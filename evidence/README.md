# Reproducible local evidence

- `deterministic-report.json`: execution of deterministic suite against local policy.
- `simulated-compromised-report.json`: execution of a **simulated** malicious model, not a live LLM.

Regenerate with:

```bash
python -m refund_guard.runner --json > evidence/deterministic-report.json
python -m refund_guard.runner --simulate-compromised-model --json > evidence/simulated-compromised-report.json
```

These files are local proof-of-concept evidence and must not be described as live-model performance.
