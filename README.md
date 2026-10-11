# ADK Agents

A collection of AI agents built with [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/) and Gemini. Each agent is a self-contained package that ADK can discover and run.

## Agents

| Agent | Package | What it does |
|-------|---------|--------------|
| **Weather & Time** | `weather_agent/` | Current weather and local time for any city. Resolves city names with the Open-Meteo geocoding API, then queries the Open-Meteo forecast API (no API key needed for either). Answers in imperial units. |
| **Auth Log Analyzer** | `log_analysis_agent/` | Security assistant for authentication logs. Parses JSON or `key=value` logs and provides summaries, brute-force / credential-stuffing / session-replay detection, a plain-English security assessment, and a password policy check. |

### Auth Log Analyzer tools

- `summarize_auth_logs` – event, status, user and IP counts
- `detect_auth_anomalies` – sliding-window brute-force detection (default 5 failures / 15 min), per-IP credential stuffing, repeated session IDs, success-after-failures
- `explain_auth_security` – human-readable interpretation of the findings
- `check_password_strength` – 12+ chars, a digit and a symbol, with the search-space/entropy math

> **Note:** `check_password_strength` sends the password to the model provider as part of the conversation. Only test throwaway passwords.

## Project structure

```
weather_agent/        # Weather & time agent (agent.py exposes root_agent)
log_analysis_agent/   # Auth log analysis agent (agent.py exposes root_agent)
examples/             # Sample logs and a ToolContext quiz-state snippet
tests/                # pytest suite (network calls are mocked)
.env.example          # Template for your credentials
requirements.txt
```

## Setup

Requires Python 3.10+ and a [Gemini API key](https://aistudio.google.com/apikey).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit .env and add your GOOGLE_API_KEY
```

`.env` is git-ignored. **Never commit it.**

## Run

From the repository root:

```bash
adk web          # browser UI; pick an agent from the dropdown
adk run weather_agent
adk run log_analysis_agent
```

Set `ADK_MODEL` in `.env` to switch models (default: `gemini-3-flash-preview`).

### Example prompts

- *Weather:* "What's the weather and local time in Tokyo?"
- *Log analyzer:* paste logs like
  ```
  timestamp=2026-03-24T14:00:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
  ```
  and ask "Is anything suspicious here?"

## Tests

```bash
pytest
```

## License

Add a license of your choice (e.g. MIT) before publishing.
