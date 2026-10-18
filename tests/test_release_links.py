"""Regression checks for the release checker's local-link classification."""

import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools/local_links.py"
SPEC = importlib.util.spec_from_file_location("release_local_links", MODULE)
LINKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LINKS)


class LocalLinkTests(unittest.TestCase):
    def test_remote_destinations_with_or_without_angle_brackets_are_not_files(self) -> None:
        source = (
            "[remote](https://example.org/a) [remote](<https://example.org/a>) "
            "[mail](mailto:a@example.org) [mail](<mailto:a@example.org>) "
            "[anchor](#local) [anchor](<#local>) "
            '<a href="https://example.org/a">remote</a>'
        )
        self.assertEqual(LINKS.local_targets(source), [])

    def test_relative_destinations_preserve_paths_and_decode_spaces(self) -> None:
        source = (
            "[a](docs/a.md) [b](<docs/My%20File.md>) [c](docs/c.md#anchor) "
            '<a href="docs/d.md#anchor">d</a>'
        )
        self.assertEqual(LINKS.local_targets(source),
                         ["docs/a.md", "docs/My File.md", "docs/c.md", "docs/d.md"])


if __name__ == "__main__":
    unittest.main()
