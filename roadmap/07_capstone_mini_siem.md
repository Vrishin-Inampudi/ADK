# Phase 7: Capstone, Mini-SIEM (4+ weeks)

Goal: integrate everything into one project you can show.

## Architecture
```
sources (auth.log, web logs, pcap/Zeek) -> ingest/parsers -> normalized events (SQLite)
   -> detection rules (Sigma-style, ATT&CK-tagged) -> alerts table
   -> dashboard (FastAPI + simple HTML) -> optional LLM "explain this alert" layer
```

## Milestones
- [ ] Define a normalized event schema (timestamp, source, user, src_ip, action, outcome, raw)
- [ ] Ingest from at least 3 sources (auth.log, web access log, Zeek/pcap output)
- [ ] Store events + alerts in SQLite (learn indexes; query by time range and IP)
- [ ] Rule engine: load rules from YAML, evaluate against stored events
- [ ] Alert dedup + severity + ATT&CK technique tags
- [ ] Web dashboard: alert list, filter by IP/user/time, event drilldown
- [ ] LLM layer (ADK agent) that only *explains* alerts; redaction before any data leaves
- [ ] Docker Compose to run everything; one-command demo with sample data
- [ ] CI with tests + lint + secret scan
- [ ] README with architecture diagram, threat model, and demo GIF
- [ ] Write a blog post or README section: what you learned

## Resources
- SQLite docs: https://www.sqlite.org/docs.html
- FastAPI: https://fastapi.tiangolo.com
- Docker getting started: https://docs.docker.com/get-started/
- Study architecture of real tools: Wazuh (https://wazuh.com), Security Onion (https://securityonionsolutions.com), Elastic Security
- Book: *Designing Data-Intensive Applications* (Kleppmann), for the data-handling concepts

## Done when
A stranger can clone the repo, run one command, and see detections fire on sample attack data.
