"""Executable synthetic integration and CLI boundary, not a live executor."""

import io
import json
import unittest
from contextlib import redirect_stdout

from eup.canonical import canonical_json, sha256_hex
from eup.cli import main
from eup.selection_demo import build_selection_demo_receipt


class SelectionDemoTests(unittest.TestCase):
    def test_integration_outcomes_and_receipt_hash(self) -> None:
        receipt = build_selection_demo_receipt()
        self.assertEqual(receipt["schema"], "EUP-SELECTION-DEMO/0.1")
        selection = receipt["selection"]
        self.assertEqual(selection["selected_id"], "candidate-c")
        self.assertEqual([item["stage"] for item in selection["candidates"]],
                         ["PRIVACY", "RISK", "ELIGIBLE", "ELIGIBLE"])
        self.assertEqual(receipt["vault_integration"], {
            "separate_grant_check_at_open": True,
            "synthetic_plaintext_matched": True,
            "subsequent_open_denied_after_revocation": True,
            "private_content_or_grant_in_receipt": False,
        })
        body = {key: value for key, value in receipt.items() if key != "receipt_hash"}
        self.assertEqual(receipt["receipt_hash"], sha256_hex(canonical_json(body)))

    def test_cli_stdout_is_the_same_public_synthetic_receipt(self) -> None:
        capture = io.StringIO()
        with redirect_stdout(capture):
            status = main(["selection-demo"])
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(capture.getvalue()), build_selection_demo_receipt())
        for forbidden in ("SYNTHETIC-PRIVATE-SELECTION-FIXTURE", "synthetic-selection-grant"):
            self.assertNotIn(forbidden, capture.getvalue())


if __name__ == "__main__":
    unittest.main()
