# Phase 2: AI-Free Log Analysis Tool (2-3 weeks)

Goal: turn the analyzer into a standalone CLI tool. The LLM agent becomes an optional layer later.

## Milestones
- [ ] Package `loganalyzer/` with no ADK dependency (agent imports it, not the reverse)
- [ ] CLI with `argparse`: `loganalyzer auth.log --format syslog --threshold 5 --window 15 --json`
- [ ] Parsers: Linux `/var/log/auth.log` (syslog), Apache/nginx access logs, JSON lines, key=value
- [ ] Stream files line-by-line (generators); test on a 1 GB file without blowing memory
- [ ] Detections (write each as its own function + tests):
  - [ ] Brute force (existing, sliding window)
  - [ ] Password spraying: one IP, many usernames, few attempts each
  - [ ] Credential stuffing: many failures across many users then a success
  - [ ] Off-hours logins
  - [ ] Impossible travel (needs IP geolocation, e.g. MaxMind GeoLite2 DB)
  - [ ] Web scanner user-agents / repeated 404s / path traversal strings in access logs
- [ ] Output: human-readable report + JSON; severity levels
- [ ] Config file for thresholds (TOML)
- [ ] Benchmark with real data from Loghub; note false positives and tune

## Concepts to understand
- Regex, named groups, and the cost of bad regexes (ReDoS)
- Sliding window / two-pointer algorithms; time complexity
- Time zones and clock skew in logs
- False positive vs. false negative tradeoffs

## Resources
- Loghub datasets: https://github.com/logpai/loghub
- NIST SP 800-92 Guide to Computer Security Log Management (search the title)
- Python docs: `re`, `argparse`, `tomllib`, `ipaddress`
- Regex practice: https://regexone.com
- MaxMind GeoLite2: https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
- Algorithms: *Grokking Algorithms* or https://neetcode.io (sliding window problems)

## Done when
You can point the CLI at a real auth.log and explain every finding it reports.
