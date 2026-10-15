"""Current status and CI navigation must agree with the selected record."""

import ast
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/research/current-status.md"
SELECTED = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))


def headings(text):
    """ATX headings outside fenced code blocks, as (line index, text)."""
    out, fenced = [], False
    for i, line in enumerate(text.splitlines()):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(r"#{1,6} ", line):
            out.append((i, line))
    return out


class CurrentStatusTests(unittest.TestCase):
    def setUp(self):
        self.text = STATUS.read_text(encoding="utf-8")
        self.lines = self.text.splitlines()
        self.heads = headings(self.text)

    def test_only_the_first_heading_claims_current_or_selected(self):
        self.assertEqual(self.heads[0], (0, "# Current reviewed status"))
        stale = [h for _, h in self.heads[1:]
                 if re.search(r"\b(current|selected|next research)\b", h, re.IGNORECASE)]
        self.assertEqual(stale, [], "rename superseded headings to name their checkpoint")

    def test_current_section_matches_selected_record(self):
        end = self.heads[1][0]
        current = "\n".join(self.lines[:end])
        self.assertIn(f"**{SELECTED['decimal']}**", current)
        self.assertIn(Path(SELECTED["review"]).name, current)
        self.assertIn(f"`{SELECTED['reproduce']}`", current)

    def test_history_banner_precedes_historical_sections(self):
        end = self.heads[1][0]
        self.assertIn("historical snapshot", "\n".join(self.lines[:end]))
        self.assertIn("selected-result.json", "\n".join(self.lines[:end]))


class CurrentCiNavigationTests(unittest.TestCase):
    def test_current_ci_section_matches_selected_record(self):
        text = (ROOT / "docs/ci-verification.md").read_text(encoding="utf-8")
        current, _ = text.split("\n## Historical", 1)
        links = {(ROOT / "docs" / target).resolve()
                 for target in re.findall(r"\]\(([^)]+)\)", current)
                 if not target.startswith("https://")}
        self.assertIn(ROOT / "certificates/selected-result.json", links)
        self.assertIn(f"`{SELECTED['reproduce']}`", current)
        for field in ("review", "validation", "source_manifest"):
            with self.subTest(field=field):
                target = ROOT / SELECTED[field]
                self.assertIn(target, links)
                self.assertTrue(target.is_file())


class LocaleIndependenceTests(unittest.TestCase):
    def test_this_modules_text_io_does_not_depend_on_host_locale(self):
        # A UTF-8 CI host cannot observe locale-codec bugs, so check the calls
        # statically (the approach of test_research_onboarding.TextEncodingTests).
        source = Path(__file__).read_text(encoding="utf-8")
        missing = []
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Call):
                continue
            func = getattr(node.func, "attr", getattr(node.func, "id", None))
            keywords = {k.arg: k.value for k in node.keywords}
            if func in ("read_text", "write_text", "open") and "encoding" not in keywords:
                missing.append(node.lineno)
        self.assertEqual(missing, [], "pass encoding= to every text read/write in this module")

    def test_status_document_carries_the_load_bearing_byte(self):
        # Byte 0x9d (in U+201D) is undefined in cp1252, the default Windows
        # locale codec, so a bare locale read of this document fails there.
        raw = STATUS.read_bytes()
        self.assertIn(b"\xe2\x80\x9d", raw)
        with self.assertRaises(UnicodeDecodeError):
            STATUS.read_text(encoding="cp1252")


if __name__ == "__main__":
    unittest.main()
