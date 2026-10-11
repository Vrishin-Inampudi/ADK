# Phase 1: Engineering Foundations (1-2 weeks)

Goal: make the repo professional and safe. Everything later builds on it.

## Milestones
- [ ] `pyproject.toml` with project metadata, dependencies, and tool config
- [ ] Type hints on every function; run `mypy` (or `pyright`) clean
- [ ] `ruff` for lint + format; zero warnings
- [ ] `pre-commit` hooks: ruff, `gitleaks` (blocks committed secrets)
- [ ] GitHub Actions workflow: on push/PR run ruff + pytest
- [ ] Tests for edge cases: malformed lines, empty input, huge input, missing fields, mixed timezones
- [ ] Measure coverage with `pytest --cov`; aim for 90%+ on log_analysis_agent
- [ ] Refactor `detect_auth_anomalies` into small single-purpose functions (one per rule)
- [ ] Branch protection on `main` (require CI to pass)

## Concepts to understand
- Virtual environments, packaging, editable installs (`pip install -e .`)
- Why pure functions are easy to test
- Secret scanning vs. `.gitignore` (ignore prevents; scanning catches mistakes)

## Resources
- Real Python: https://realpython.com
- pytest: https://docs.pytest.org
- Ruff: https://docs.astral.sh/ruff/
- pre-commit: https://pre-commit.com
- Gitleaks: https://github.com/gitleaks/gitleaks
- GitHub Actions: https://docs.github.com/actions
- Python packaging guide: https://packaging.python.org
- Book: *Fluent Python* (Ramalho)

## Done when
A bad commit (type error, lint failure, or fake API key) is rejected locally or in CI.
