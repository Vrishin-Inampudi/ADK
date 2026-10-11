# Phase 4: Detection Engineering (3-4 weeks)

Goal: think like a SOC analyst/detection engineer; write detections other people could use.

## Milestones
- [ ] Learn MITRE ATT&CK; map each detection you've built to a technique ID (e.g. T1110 Brute Force)
- [ ] Write 5 Sigma rules (brute force, password spray, suspicious process, etc.)
- [ ] Build a small converter: Sigma rule (YAML) -> your tool's rule format
- [ ] Run Suricata on a pcap from Phase 3; read the alerts; write 3 custom Suricata rules
- [ ] Run Zeek on the same pcap; read `conn.log`, `dns.log`, `http.log`; feed them to your tool
- [ ] Deploy a honeypot (Cowrie SSH honeypot) on a VM; collect logs for a week
- [ ] Analyze real honeypot attacks with your own tool; write up top usernames, IPs, commands tried
- [ ] Tune: document false positive rate per rule

## Concepts to understand
- Detection pipeline: log source -> normalization -> rule -> alert -> triage
- Signature vs behavioral vs anomaly detection
- The Pyramid of Pain
- Alert fatigue and tuning

## Resources
- MITRE ATT&CK: https://attack.mitre.org
- Sigma rules: https://github.com/SigmaHQ/sigma
- Zeek: https://docs.zeek.org
- Suricata: https://docs.suricata.io
- Cowrie honeypot: https://github.com/cowrie/cowrie
- Blue Team Labs Online: https://blueteamlabs.online
- Pyramid of Pain (David Bianco): search the title
- Atomic Red Team (test your detections): https://github.com/redcanaryco/atomic-red-team

## Done when
You have a rule set with ATT&CK mappings, tests, and measured false positives, run against real data.
