# Roadmap Overview

Goal: build network security + engineering skill with minimal AI assistance.

## Rules of engagement
1. Write the code yourself first. Run tests. Read docs and error messages.
2. Only after a real attempt, use AI for *review* ("what would you critique?"), never to write the solution.
3. Commit small and often. One milestone = one or more commits.
4. Only scan/attack machines you own (VMs, home lab). Never third-party systems.
5. Keep a `NOTES.md` per phase: what you learned, what confused you, what you'd do differently.

## Order
| # | Phase | Time | File |
|---|-------|------|------|
| 1 | Engineering foundations | 1-2 wks | 01_engineering_foundations.md |
| 2 | AI-free log analysis tool | 2-3 wks | 02_log_analysis_tool.md |
| 3 | Network fundamentals | 3-4 wks | 03_network_fundamentals.md |
| 4 | Detection engineering | 3-4 wks | 04_detection_engineering.md |
| 5 | Secure engineering | ongoing | 05_secure_engineering.md |
| 6 | Practice platforms | parallel | 06_practice_platforms.md |
| 7 | Capstone: mini-SIEM | 4+ wks | 07_capstone_mini_siem.md |

Do Phase 1 first (CI + secret scanning protect everything after).
Alternate 2 and 3 (they feed each other). Run 6 alongside everything.

Note: links were written from memory. If one is dead, search the resource name.
