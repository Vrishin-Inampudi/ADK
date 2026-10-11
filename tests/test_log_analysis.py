from examples import sample_logs as logs
from log_analysis_agent.agent import (
    check_password_strength,
    detect_auth_anomalies,
    explain_auth_security,
    summarize_auth_logs,
)


def _types(text):
    return {f["type"] for f in detect_auth_anomalies(text)["report"]["findings"]}


def test_summary_counts():
    report = summarize_auth_logs(logs.BRUTE_FORCE)["report"]
    assert report["total_entries"] == 6
    assert report["unique_users"] == 1
    assert report["statuses"] == {"failure": 5, "success": 1}


def test_json_lines_and_zulu_timestamps():
    assert summarize_auth_logs(logs.JSON_LINES)["report"]["unique_ips"] == 1


def test_brute_force_detected():
    result = detect_auth_anomalies(logs.BRUTE_FORCE)["report"]
    assert "possible_brute_force" in _types(logs.BRUTE_FORCE)
    assert result["successes_after_repeated_failures"]


def test_credential_stuffing_detected():
    assert "possible_credential_stuffing" in _types(logs.CREDENTIAL_STUFFING)


def test_replay_detected():
    assert "possible_replay_or_token_reuse" in _types(logs.REPLAY)


def test_mixed_naive_and_aware_timestamps_do_not_crash():
    text = (
        "timestamp=2026-03-24T14:00:00Z username=a ip=1.1.1.1 event=login status=failure\n"
        "timestamp=2026-03-24T14:01:00 username=a ip=1.1.1.1 event=login status=failure\n"
    )
    assert detect_auth_anomalies(text, failure_threshold=2)["status"] == "success"


def test_empty_logs_error():
    assert summarize_auth_logs("")["status"] == "error"
    assert explain_auth_security("")["status"] == "error"


def test_password_policy():
    assert not check_password_strength("short")["report"]["password_policy_passed"]
    assert not check_password_strength("LongPassword12")["report"]["password_policy_passed"]
    assert not check_password_strength("LongPassword!")["report"]["password_policy_passed"]
    assert check_password_strength("LongPassword12!")["report"]["password_policy_passed"]
