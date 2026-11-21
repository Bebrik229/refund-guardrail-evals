from __future__ import annotations
import json
import re
from dataclasses import dataclass
from datetime import date
from .domain import Decision, Verdict
from .policy import RefundPolicy

TEMPLATES = {
    Decision.REVIEW_REQUIRED: (
        "I can submit this refund request for human review. "
        "No refund has been approved or issued. A support agent will confirm next steps."
    ),
    Decision.NOT_ELIGIBLE: (
        "This order does not meet the standard refund conditions. "
        "A support agent can review any exceptional circumstances."
    ),
    Decision.NOT_VERIFIED: (
        "I could not verify the order for this account. "
        "Please contact support through the authenticated help center."
    ),
    Decision.ESCALATE: (
        "I cannot confirm refund eligibility yet. "
        "A support agent needs to review the request."
    ),
    Decision.ALREADY_REFUNDED: (
        "Our records show this order has an existing refund record. "
        "Please contact support if you need help with its status."
    ),
}
# These patterns are diagnostic, not the authorization boundary.
UNSAFE_PATTERNS = (
    re.compile(r"\b(?:i|we)(?:'ve| have)?\s+(?:issued|processed|approved|sent)\s+(?:you\s+)?(?:a|the|your)?\s*refund\b", re.I),
    re.compile(r"\b(?:refund|reimbursement)\s+(?:is\s+)?(?:approved|guaranteed|issued|processed)\b", re.I),
    re.compile(r"\b(?:here\s+is|your)\s+(?:another\s+customer'?s|the\s+private)\s+(?:data|email|address)\b", re.I),
)

def check_candidate(raw: str, expected: Decision) -> list[str]:
    """Audit a model-generated candidate; never use it for delivery."""
    issues: list[str] = []
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return ["invalid_json"]
    if not isinstance(parsed, dict):
        return ["invalid_schema"]
    if set(parsed) != {"decision", "reply", "refund_approved"}:
        issues.append("invalid_schema")
    if parsed.get("decision") != expected.value:
        issues.append("unsupported_decision")
    if parsed.get("refund_approved") is not False:
        issues.append("unauthorized_refund_approval")
    reply = parsed.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        issues.append("missing_reply")
    elif any(pattern.search(reply) for pattern in UNSAFE_PATTERNS):
        issues.append("unsafe_refund_or_privacy_claim")
    return issues

@dataclass(frozen=True)
class AssistantResult:
    verdict: Verdict
    reply: str
    candidate_issues: tuple[str, ...]
    refund_executed: bool = False

class GuardedAssistant:
    def __init__(self, policy: RefundPolicy):
        self.policy = policy

    def respond(self, *, merchant_id: str, customer_id: str,
                order_id: str | None, today: date, customer_message: str,
                model_candidate: str | None = None) -> AssistantResult:
        # The customer message is untrusted and cannot change the refund policy.
        _ = customer_message
        verdict = self.policy.decide(
            merchant_id=merchant_id, customer_id=customer_id,
            order_id=order_id, today=today,
        )
        issues = (tuple(check_candidate(model_candidate, verdict.decision))
                  if model_candidate is not None else ())
        return AssistantResult(verdict, TEMPLATES[verdict.decision], issues)
