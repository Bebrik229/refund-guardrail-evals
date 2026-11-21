from __future__ import annotations
from datetime import date
from typing import Mapping
from .domain import Decision, Order, Verdict

class RefundPolicy:
    """Authoritative eligibility. Untrusted message text cannot modify this decision."""
    def __init__(self, orders: Mapping[str, Order], *, window_days: int = 30):
        if window_days <= 0:
            raise ValueError("window_days must be positive")
        self._orders = dict(orders)
        self._window = window_days

    def decide(self, *, merchant_id: str, customer_id: str,
               order_id: str | None, today: date) -> Verdict:
        if not merchant_id or not customer_id or not order_id:
            return Verdict(Decision.NOT_VERIFIED, "missing_verified_identity_or_order")
        order = self._orders.get(order_id)
        if order is None or order.customer_id != customer_id or order.merchant_id != merchant_id:
            return Verdict(Decision.NOT_VERIFIED, "not_verified")
        if order.status == "refunded":
            return Verdict(Decision.ALREADY_REFUNDED, "refund_already_recorded")
        if order.status in ("cancelled", "rejected"):
            return Verdict(Decision.NOT_ELIGIBLE, "order_status_ineligible")
        if order.status != "delivered" or order.delivered_on is None:
            return Verdict(Decision.ESCALATE, "delivery_not_confirmed")
        elapsed = (today - order.delivered_on).days
        if elapsed < 0:
            return Verdict(Decision.ESCALATE, "invalid_delivery_timestamp")
        if elapsed > self._window:
            return Verdict(Decision.NOT_ELIGIBLE, "outside_standard_window")
        return Verdict(Decision.REVIEW_REQUIRED, "eligible_for_human_review_only")
