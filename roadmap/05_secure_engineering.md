# Phase 5: Secure Engineering (ongoing)

Goal: build things securely, then attack your own work.

## Milestones
- [ ] Small login API (FastAPI or Flask): registration, login, sessions/JWT
  - [ ] Hash passwords with argon2 (`argon2-cffi`), never roll your own
  - [ ] Rate limiting + account lockout
  - [ ] Structured auth logs that your Phase 2 tool can parse
  - [ ] Input validation, parameterized SQL, secure cookies, CSRF protection
- [ ] Attack your API with a script you write (brute force, spraying); confirm your tool detects it
- [ ] Threat model the ADK agents (STRIDE): assets, trust boundaries, abuse cases
- [ ] Prompt injection test: put "ignore previous instructions..." inside a log line; document what happens and harden
- [ ] Don't send secrets to the model: add redaction of passwords/tokens before logs reach an LLM
- [ ] Dependency scanning: `pip-audit`, Dependabot
- [ ] Learn the basics of crypto by breaking it (Cryptopals sets 1-2)

## Concepts to understand
- Authentication vs authorization; sessions vs tokens
- Hashing vs encryption vs encoding; salts; why fast hashes are bad for passwords
- OWASP Top 10 categories; injection; broken access control
- Least privilege; defense in depth

## Resources
- OWASP Top 10: https://owasp.org/Top10/
- OWASP LLM Top 10: https://genai.owasp.org/llm-top-10/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org
- Cryptopals: https://cryptopals.com
- PortSwigger Web Security Academy (free): https://portswigger.net/web-security
- FastAPI docs: https://fastapi.tiangolo.com
- pip-audit: https://github.com/pypa/pip-audit
- Threat modeling: *Threat Modeling* by Adam Shostack, or https://owasp.org/www-community/Threat_Modeling

## Done when
You can explain how each part of your API could be attacked and show the test proving the defense.
