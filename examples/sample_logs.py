"""Sample authentication logs used by the tests and for manual experiments."""

BRUTE_FORCE = """
timestamp=2026-03-24T14:00:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
timestamp=2026-03-24T14:02:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
timestamp=2026-03-24T14:04:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
timestamp=2026-03-24T14:06:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
timestamp=2026-03-24T14:08:00 username=alice ip=1.2.3.4 event=login status=failure session_id=abc123
timestamp=2026-03-24T14:10:00 username=alice ip=1.2.3.4 event=login status=success session_id=abc123
"""

CREDENTIAL_STUFFING = "\n".join(
    f"timestamp=2026-03-24T15:{i:02d}:00 username={u} ip=9.9.9.9 event=login status=failure session_id=s{i}"
    for i, u in enumerate(
        ["alice", "bob", "charlie", "diana", "eva", "frank", "grace", "henry", "ivy", "jack"]
    )
)

REPLAY = """
timestamp=2026-03-24T16:00:00 username=alice ip=5.5.5.5 event=verify status=failure session_id=replay777
timestamp=2026-03-24T16:01:00 username=alice ip=5.5.5.5 event=verify status=failure session_id=replay777
timestamp=2026-03-24T16:02:00 username=alice ip=5.5.5.5 event=verify status=success session_id=replay777
timestamp=2026-03-24T16:03:00 username=alice ip=5.5.5.5 event=verify status=success session_id=replay777
"""

JSON_LINES = (
    '{"timestamp": "2026-03-24T14:00:00Z", "username": "bob", "ip": "8.8.8.8", '
    '"event": "login", "status": "success"}'
)
