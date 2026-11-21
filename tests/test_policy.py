import unittest
from datetime import date
from refund_guard.domain import Decision, Order
from refund_guard.policy import RefundPolicy

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 21)
        self.orders = {
            'o1': Order('o1', 'alice', 'm1', date(2026, 11, 1), 'delivered'),
            'o2': Order('o2', 'bob', 'm1', date(2026, 11, 2), 'delivered'),
            'o3': Order('o3', 'alice', 'm2', date(2026, 11, 3), 'delivered'),
            'o4': Order('o4', 'alice', 'm1', date(2026, 10, 21), 'delivered'),
            'o5': Order('o5', 'alice', 'm1', date(2026, 10, 22), 'delivered'),
            'o6': Order('o6', 'alice', 'm1', None, 'in_transit'),
            'o7': Order('o7', 'alice', 'm1', None, 'cancelled'),
            'o8': Order('o8', 'alice', 'm1', date(2026, 11, 2), 'refunded'),
            'o9': Order('o9', 'alice', 'm1', date(2026, 12, 2), 'delivered'),
        }
        self.policy = RefundPolicy(self.orders)

    def decide(self, order, customer='alice', merchant='m1'):
        return self.policy.decide(merchant_id=merchant, customer_id=customer, order_id=order, today=self.today).decision

    def test_human_review_only(self):
        self.assertEqual(self.decide('o1'), Decision.REVIEW_REQUIRED)
    def test_other_customer_not_verified(self):
        self.assertEqual(self.decide('o2'), Decision.NOT_VERIFIED)
    def test_cross_merchant_not_verified(self):
        self.assertEqual(self.decide('o3'), Decision.NOT_VERIFIED)
    def test_nonexistent_indistinguishable(self):
        a=self.policy.decide(merchant_id='m1', customer_id='alice', order_id='o2', today=self.today)
        b=self.policy.decide(merchant_id='m1', customer_id='alice', order_id='nope', today=self.today)
        self.assertEqual(a,b)
    def test_day_31_ineligible(self):
        self.assertEqual(self.decide('o4'), Decision.NOT_ELIGIBLE)
    def test_day_30_eligible(self):
        self.assertEqual(self.decide('o5'), Decision.REVIEW_REQUIRED)
    def test_in_transit_escalates(self):
        self.assertEqual(self.decide('o6'), Decision.ESCALATE)
    def test_cancelled_ineligible(self):
        self.assertEqual(self.decide('o7'), Decision.NOT_ELIGIBLE)
    def test_already_refunded(self):
        self.assertEqual(self.decide('o8'), Decision.ALREADY_REFUNDED)
    def test_future_delivery_escalates(self):
        self.assertEqual(self.decide('o9'), Decision.ESCALATE)
    def test_missing_identity(self):
        self.assertEqual(self.decide('o1', customer=''), Decision.NOT_VERIFIED)
    def test_invalid_window_rejected(self):
        with self.assertRaises(ValueError):
            RefundPolicy({}, window_days=0)
