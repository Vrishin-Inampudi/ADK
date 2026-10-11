import json
import logging
import math
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from google.adk.agents import Agent

logger = logging.getLogger(__name__)

MODEL = os.getenv("ADK_MODEL", "gemini-3-flash-preview")


def _parse_line(line: str) -> Dict[str, Any]:
    """
    EX: timestamp=2026-03-24T14:22:00 username=alice event=login status=failure

    This works by taking the raw text and converts it into a dictionary.
    Since most modern logs are written in JSON, we use the try and except clause to see if our log is json compatible.
    If this doesn't work we use a legacy version that parses a line till it finds a word with an = sign
    and returns the next characters till a space.
    Worst case if the legacy and json method don't work just do raw and the information.
    All of these return dicts
    """
    line = line.strip()
    if not line:
        return {}

    try:  # json
        data = json.loads(line)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    pairs = re.findall(r"(\w+)=([^\s]+)", line)  # legacy
    if not pairs:  # neither
        return {"raw (error)": line}

    return {k: v for k, v in pairs}


def _parse_timestamps(value: str):
    """
    EX: 2023-10-01 vs 10/01/2023

    If the value is empty return nothing.
    We try date time with ISO 8601 since this is the most modern way now.
        - This returns a proper datetime object for python.
    If that fails we have a simple dict with formats of templates that it loops through.
    if that doesn't work and we hit the error just return none and we know too look back.
    returning datetime objects because it's more useful for logs:
        ex: did success happen after a failure
        ex: how many failures in x amount of time
    """
    if not value:
        return None

    value = value.replace("Z", "+00:00")  # swaps to zulu time
    try:
        parsed = datetime.fromisoformat(value)  # use datetime first
        if parsed.tzinfo is not None:
            # normalise to naive UTC so naive and aware logs can be compared
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        for fmt in (  # unless in this format
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt)  # then try datetime with the formats
            except ValueError:  # if we have an error continue and return nothing
                continue
    return None  # if broken return None


def _load_logs(log_text: str) -> List[Dict[str, Any]]:
    """
    Takes a block of logs and turns each line into a parsed dictionary.
    This is what the agent uses to break multiline logs into interpretable logs for the agent.
    """
    entries: List[Dict[str, Any]] = []
    for raw_line in log_text.splitlines(): #splits where there are new lines
        parsed = _parse_line(raw_line) #this returns the value from the _parse (either JSON, Legacy, or empty)
        if parsed: #if we have data add it to entries 
            entries.append(parsed)
    return entries #this will also return empty dict if we have that 


def summarize_auth_logs(log_text: str) -> Dict[str, Any]:
    """
    This gives us a quick summary of what is inside the logs.

    It tells us:
    - how many events are there
    - how many unique users and ips
    - what event types show up
    - how many successes/failures show up

    This is useful because before doing deep detection we want a quick picture of what the logs contain.

    Args:
        log_text: Raw log lines, one event per line, as JSON objects or key=value pairs.
    """
    logger.info("summarize_auth_logs tool called")

    entries = _load_logs(log_text) #get entries 
    if not entries: #if nothing in entries return an error
        return {
            "status": "error",
            "report": None,
            "error_message": "No parseable log entries were found."
        }

    total = len(entries) 
    by_event = Counter()
    by_status = Counter() #tracks the events and status evry time 
    users = set()
    ips = set() #to ensure no dupes use a set 

    for entry in entries: 
        by_event[entry.get("event", "unknown")] += 1
        by_status[entry.get("status", "unknown")] += 1

        if entry.get("username"):
            users.add(entry["username"])

        if entry.get("ip"):
            ips.add(entry["ip"])

    return {
        "status": "success",
        "report": {
            "total_entries": total,
            "unique_users": len(users),
            "unique_ips": len(ips),
            "events": dict(by_event),
            "statuses": dict(by_status),
        },
        "error_message": None,
    }


def detect_auth_anomalies(
    log_text: str,
    failure_threshold: int = 5, #these are our parameters:
    window_minutes: int = 15
) -> Dict[str, Any]:
    """
    This is the main detector to flag any suspicious behavior.

    What we are looking for:
    - lots of failed login attempts from the same user and ip in a short time (15 minutes)
    - lots of failures from one ip overall
    - repeated session ids which may mean a attacker maybe trying to replay or attempt token reuse.
    - success after a lot of failures, which may mean the attacker finally got in after credential stuffing.

    Args:
        log_text: Raw log lines, one event per line, as JSON objects or key=value pairs.
        failure_threshold: Failures that trigger a finding (default 5).
        window_minutes: Window for the brute-force burst check (default 15).
    """
    logger.info("detect_auth_anomalies tool called")

    entries = _load_logs(log_text)
    if not entries: # if nothing comes from _load_logs
        return {
            "status": "error",
            "report": None,
            "error_message": "No parseable log entries were found."
        }
    #init all of our dicts and lists 
    failures_by_user_ip = defaultdict(list)
    failures_by_ip = defaultdict(list)
    successes_after_failures = []
    repeated_session_ids = Counter()
    suspicious_findings = []

    for entry in entries: #loops through every log entry and sorts out the who,what, and where.
        ts = _parse_timestamps(entry.get("timestamp", ""))
        username = entry.get("username", "unknown")
        ip = entry.get("ip", "unknown")
        status = str(entry.get("status", "unknown")).lower()
        session_id = entry.get("session_id")
        event = str(entry.get("event", "unknown")).lower()

        if session_id:
            repeated_session_ids[session_id] += 1

        if event in {"login", "authenticate", "verify", "mfa", "otp"}: 
            if status in {"failure", "failed", "denied", "invalid"}: #if the user fails we want to note that 
                failures_by_user_ip[(username, ip)].append(ts) #add the timestamp for the user,ip
                failures_by_ip[ip].append(ts) #add into failures by ip

            if status in {"success", "passed", "ok"}: 
                prior_failures = failures_by_user_ip.get((username, ip), [])
                if len(prior_failures) >= failure_threshold - 1: #this checks if password stuffing happened  
                    successes_after_failures.append({
                        "username": username,
                        "ip": ip,
                        "success_timestamp": entry.get("timestamp"),
                        "prior_failures": len(prior_failures), #flags
                    })

    window = timedelta(minutes=window_minutes)

    """
    Sliding window logic:
    We sort timestamps and move left/right pointers through them.
    This lets us check whether we have x failures inside y minutes efficiently.
    """
    for (username, ip), timestamps in failures_by_user_ip.items():
        clean_times = sorted(t for t in timestamps if t is not None) #sorts from oldest to newest
        if len(clean_times) < failure_threshold:
            continue

        left = 0
        for right in range(len(clean_times)):
            while clean_times[right] - clean_times[left] > window:
                left += 1
        

            burst = right - left + 1
            if burst >= failure_threshold:
                suspicious_findings.append({
                    "type": "possible_brute_force",
                    "username": username,
                    "ip": ip,
                    "failures_in_window": burst,
                    "window_minutes": window_minutes,
                })
                break
        #this uses the two pointer method to scan for if we hit 5 attempts in 15 minutes

    """
    This is a simple credential stuffing style rule.
    If one ip generates a lot of failures overall, flag it.
    Future: Try to also check how many different usernames were targeted. 
    """
    for ip, timestamps in failures_by_ip.items():
        clean_times = sorted(t for t in timestamps if t is not None)
        if len(clean_times) >= failure_threshold * 2:
            suspicious_findings.append({
                "type": "possible_credential_stuffing",
                "ip": ip,
                "failure_count": len(clean_times),
            })

    """
    Replay / token reuse style rule:
    If the same session id appears a lot, flag. 
    This is not always malicious, but wouldn't hurt to flag.
    -Ex: Someone might be spamming refresh on their keyboard.
    """
    for session_id, count in repeated_session_ids.items():
        if count >= 3:
            suspicious_findings.append({
                "type": "possible_replay_or_token_reuse",
                "session_id": session_id,
                "occurrences": count,
            })

    return {
        "status": "success",
        "report": {
            "finding_count": len(suspicious_findings),
            "findings": suspicious_findings,
            "successes_after_repeated_failures": successes_after_failures,
            "recommendations": [
                "Rate-limit repeated login and verification attempts.",
                "Use constant-time credential comparisons and avoid verbose auth errors.",
                "Require MFA or step-up verification after repeated failures.",
                "Invalidate reused session or verification tokens immediately.",
                "Alert on high failure volume from one IP across many accounts.",
            ],
        },
        "error_message": None,
    }


def explain_auth_security(log_text: str) -> Dict[str, Any]:
    """
    This is the plain english explanation layer.

    Instead of only giving raw findings, this tool explains what the logs mean from a security perspective.
    It reuses the summary tool and anomaly tool instead of rewriting the logic.

    Args:
        log_text: Raw log lines, one event per line, as JSON objects or key=value pairs.
    """
    logger.info("explain_auth_security tool called")

    summary = summarize_auth_logs(log_text)
    anomalies = detect_auth_anomalies(log_text)

    if summary["status"] == "error":
        return summary
    if anomalies["status"] == "error":
        return anomalies

    findings = anomalies["report"]["findings"]
    finding_count = anomalies["report"]["finding_count"]

    if finding_count == 0:
        interpretation = (
            "The log sample does not show obvious brute-force bursts, token reuse, or high-volume "
            "credential-stuffing patterns based on the implemented heuristics."
        )
    else:
        interpretation = (
            f"The log sample contains {finding_count} suspicious pattern(s) that may indicate brute-force, "
            "credential stuffing, or replay-style behavior. These events should be reviewed alongside "
            "attempt-limiting, MFA, and token lifecycle controls."
        )

    return {
        "status": "success",
        "report": {
            "security_interpretation": interpretation,
            "summary": summary["report"],
            "anomalies": findings,
        },
        "error_message": None,
    }


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    This is a simple password checker.

    Rules:
    - minimum 12 chars
    - at least one number
    - at least one symbol

    For the math:
    We assume a random 12-character password chosen from printable ASCII.
    There are about 94 printable ASCII chars.

    All possible 12-char strings:
    94^12

    Subtract the bad sets:
    - no digits -> 84^12
    - no symbols -> 62^12

    Then add back the overlap because we subtracted it twice:
    - neither digits nor symbols -> 52^12

    So the total valid policy-compliant random password space is:
    94^12 - 84^12 - 62^12 + 52^12
    """
    logger.info("check_password_strength tool called")

    if password is None:
        return {
            "status": "error",
            "report": None,
            "error_message": "No password was provided."
        }

    length_ok = len(password) >= 12
    has_number = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[^A-Za-z0-9]", password))

    passed = length_ok and has_number and has_symbol

    missing_requirements = []
    if not length_ok:
        missing_requirements.append("at least 12 characters")
    if not has_number:
        missing_requirements.append("at least one number")
    if not has_symbol:
        missing_requirements.append("at least one symbol")

    valid_space = (94 ** 12) - (84 ** 12) - (62 ** 12) + (52 ** 12)
    entropy_bits = math.log2(valid_space)

    return {
        "status": "success",
        "report": {
            "password_policy_passed": passed,
            "length": len(password),
            "has_number": has_number,
            "has_symbol": has_symbol,
            "missing_requirements": missing_requirements,
            "math": {
                "formula": "94^12 - 84^12 - 62^12 + 52^12",
                "valid_password_space_estimate": valid_space,
                "approx_entropy_bits": round(entropy_bits, 2),
                "explanation": (
                    "This estimates the number of 12-character printable ASCII passwords "
                    "that include at least one digit and at least one symbol."
                ),
            },
            "security_interpretation": (
                "This policy creates a large brute-force search space if the password is random, "
                "but predictable passwords can still be weak even if they satisfy the rule."
            ),
        },
        "error_message": None,
    }


# Tells the model when to use each tool.
INSTRUCTION = """
You are a security log analysis assistant focused on authentication and verification workflows.

Rules:
- If the user asks for an overview or counts, call summarize_auth_logs.
- If the user asks about suspicious behavior, brute-force activity, replay risks, or anomalies, call detect_auth_anomalies.
- If the user asks for an interpretation or security assessment, call explain_auth_security.
- If the user asks whether a password meets the basic password policy, call check_password_strength.
- Always use tools instead of guessing.
- Keep conclusions grounded in the log data or password provided.
- If a tool returns an error, explain it clearly.
- Recommend defensive controls such as salted password hashing, attempt limiting, MFA, secure comparisons, and structured errors when relevant.
- Interpret the data and make it easy to read in plain text.
- If the user goes beyond the scope of the log analyzer don't follow the request and return a simple message that say's "Sorry, I can't do that"
"""

# ADK discovers the agent through the `root_agent` name.
root_agent = Agent(
    name="auth_log_analysis_agent",
    model=MODEL,
    description="Analyzes authentication logs for suspicious activity, security patterns, operational summaries, and basic password policy compliance.",
    instruction=INSTRUCTION,
    tools=[
        summarize_auth_logs,
        detect_auth_anomalies,
        explain_auth_security,
        check_password_strength,
    ],
)

