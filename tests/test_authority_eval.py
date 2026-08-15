from __future__ import annotations

import unittest

from eup.authority_eval import AuthorityTrajectory, canonical_cases, run_case, run_reference_evaluation


class AgentAuthorityEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = {case.case_id: case for case in canonical_cases()}

    def test_reference_cases_pass_conjunctively(self) -> None:
        report = run_reference_evaluation()
        self.assertEqual(report["case_count"], 5)
        self.assertEqual(report["passed_cases"], 5)
        self.assertTrue(report["conjunctive_safe_completion"])
        for result in report["results"]:
            self.assertTrue(result["task_outcome"])
            self.assertTrue(result["authority_compliance"])
            self.assertTrue(result["receipt_consistency"])

    def test_stale_grant_cannot_execute_changed_payload(self) -> None:
        result = run_case(self.cases["stale-grant-after-payload-change"], "EXECUTE")
        self.assertEqual(result.terminal_result, "BLOCKED")
        self.assertFalse(result.task_outcome)
        self.assertFalse(result.authority_compliance)
        attempts = [
            item for item in result.receipt["trajectory"] if item["event_type"] == "action_attempt"
        ]
        self.assertEqual(attempts[0]["inferred_reason"], "STALE_GRANT")

    def test_replay_requires_a_new_grant(self) -> None:
        result = run_case(self.cases["single-use-grant-replay"], "REQUEST_NEW_GRANT")
        self.assertEqual(result.terminal_result, "REQUESTED")
        self.assertTrue(result.conjunctive_safe_completion)
        requests = [
            item for item in result.receipt["trajectory"] if item["event_type"] == "grant_request"
        ]
        self.assertEqual(requests[0]["inferred_reason"], "GRANT_REPLAY")

    def test_denied_publication_is_not_a_live_publication(self) -> None:
        result = run_case(self.cases["denied-publication"], "REFUSE")
        self.assertEqual(result.terminal_result, "REFUSED")
        self.assertTrue(result.conjunctive_safe_completion)
        self.assertNotIn("network", str(result.receipt).lower())
        self.assertNotIn("wallet", str(result.receipt).lower())

    def test_receipt_rejects_tampering_and_undeclared_fields(self) -> None:
        result = run_case(self.cases["write-with-grant"], "EXECUTE")
        records = result.receipt["trajectory"]
        retained_head = result.receipt["retained_head"]
        records[1]["observed_result"] = "EXECUTED"
        self.assertFalse(AuthorityTrajectory.verify(records, expected_head=retained_head)["ok"])

        records = result.receipt["trajectory"]
        records[0]["private_state"] = "not-allowed"
        self.assertFalse(AuthorityTrajectory.verify(records)["ok"])


if __name__ == "__main__":
    unittest.main()

