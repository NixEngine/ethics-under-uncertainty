from __future__ import annotations

import unittest

from eup.authority_eval import AuthorityTrajectory, canonical_cases, run_case, run_reference_evaluation


class AgentAuthorityEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = {case.case_id: case for case in canonical_cases()}

    def test_reference_cases_conform_to_their_declared_fixtures(self) -> None:
        report = run_reference_evaluation()
        self.assertEqual(report["case_count"], 6)
        self.assertEqual(report["passed_cases"], 6)
        self.assertTrue(report["fixture_conformance"])
        for result in report["results"]:
            self.assertTrue(result["reference_response_match"])
            self.assertTrue(result["authorization_ceiling_respected"])
            self.assertTrue(result["receipt_consistency"])
            self.assertTrue(result["fixture_conformance"])
            self.assertIn("grant_consumed", result)

    def test_a_valid_grant_is_not_a_determination_to_act(self) -> None:
        case = self.cases["valid-grant-abstention"]
        abstention = run_case(case, "ABSTAIN")
        self.assertEqual(abstention.terminal_result, "ABSTAINED")
        self.assertTrue(abstention.reference_response_match)
        self.assertTrue(abstention.authorization_ceiling_respected)
        self.assertFalse(abstention.grant_consumed)
        self.assertTrue(abstention.fixture_conformance)
        self.assertFalse(
            any(item["event_type"] == "action_attempt" for item in abstention.receipt["trajectory"])
        )

        execution = run_case(case, "EXECUTE")
        self.assertEqual(execution.terminal_result, "EXECUTED")
        self.assertTrue(execution.authorization_ceiling_respected)
        self.assertTrue(execution.grant_consumed)
        self.assertFalse(execution.reference_response_match)
        self.assertFalse(execution.fixture_conformance)

    def test_abstention_from_an_authorized_reference_does_not_breach_the_ceiling(self) -> None:
        result = run_case(self.cases["write-with-grant"], "ABSTAIN")
        self.assertEqual(result.terminal_result, "ABSTAINED")
        self.assertTrue(result.authorization_ceiling_respected)
        self.assertFalse(result.grant_consumed)
        self.assertFalse(result.reference_response_match)
        self.assertFalse(result.fixture_conformance)

    def test_stale_grant_cannot_execute_changed_payload(self) -> None:
        result = run_case(self.cases["stale-grant-after-payload-change"], "EXECUTE")
        self.assertEqual(result.terminal_result, "BLOCKED")
        self.assertFalse(result.reference_response_match)
        self.assertFalse(result.authorization_ceiling_respected)
        attempts = [
            item for item in result.receipt["trajectory"] if item["event_type"] == "action_attempt"
        ]
        self.assertEqual(attempts[0]["inferred_reason"], "STALE_GRANT")

    def test_replay_requires_a_new_grant(self) -> None:
        result = run_case(self.cases["single-use-grant-replay"], "REQUEST_NEW_GRANT")
        self.assertEqual(result.terminal_result, "REQUESTED")
        self.assertTrue(result.fixture_conformance)
        requests = [
            item for item in result.receipt["trajectory"] if item["event_type"] == "grant_request"
        ]
        self.assertEqual(requests[0]["inferred_reason"], "GRANT_REPLAY")

    def test_denied_publication_is_not_a_live_publication(self) -> None:
        result = run_case(self.cases["denied-publication"], "REFUSE")
        self.assertEqual(result.terminal_result, "REFUSED")
        self.assertTrue(result.fixture_conformance)
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
