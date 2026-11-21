from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum

class Decision(str, Enum):
    REVIEW_REQUIRED = "review_required"
    NOT_ELIGIBLE = "not_eligible"
    NOT_VERIFIED = "not_verified"
    ESCALATE = "escalate"
    ALREADY_REFUNDED = "already_refunded"

@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    merchant_id: str
    delivered_on: date | None
    status: str

    @classmethod
    def from_dict(cls, obj: dict) -> "Order":
        delivered = obj.get("delivered_on")
        return cls(
            order_id=str(obj["order_id"]),
            customer_id=str(obj["customer_id"]),
            merchant_id=str(obj["merchant_id"]),
            delivered_on=date.fromisoformat(delivered) if delivered else None,
            status=str(obj["status"]),
        )

@dataclass(frozen=True)
class Verdict:
    decision: Decision
    reason: str
