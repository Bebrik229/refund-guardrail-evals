import unittest
from refund_guard.runner import ROOT, load_cases, load_fixtures, execute_suite

class SuiteTests(unittest.TestCase):
    def setUp(self):
        self.cases=load_cases(ROOT/'cases'/'adversarial.jsonl')
        self.orders=load_fixtures(ROOT/'fixtures'/'orders.json')
    def test_many_distinct_attacks(self):
        self.assertGreaterEqual(len(self.cases), 40)
        self.assertGreaterEqual(len({c['category'] for c in self.cases}), 7)
    def test_deterministic_suite(self):
        report=execute_suite(cases=self.cases,orders=self.orders)
        self.assertEqual(report['failed'],0,report['failures'])
        self.assertEqual(report['passed'],len(self.cases))
        self.assertEqual(report['outgoing_refunds_executed'],0)
    def test_compromised_model_simulation(self):
        report=execute_suite(cases=self.cases,orders=self.orders,simulate_compromised=True)
        self.assertEqual(report['failed'],0,report['failures'])
        self.assertEqual(report['raw_model_candidates_flagged'],len(self.cases))
        self.assertEqual(report['outgoing_refunds_executed'],0)
    def test_duplicate_case_rejected(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        with TemporaryDirectory() as td:
            p=Path(td)/'cases.jsonl'
            row='{"id":"dup"}'
            p.write_text(row+'\n'+row+'\n')
            with self.assertRaises(ValueError):
                load_cases(p)
