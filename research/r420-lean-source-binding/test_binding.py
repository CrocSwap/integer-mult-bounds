#!/usr/bin/env python3
"""Regression checks for the historical external R420 source correspondence.

Only the R420 prefix of the pinned historical Python script is executed, with
three local directory substitutions. Its assertions are retained even under -O.
These tests make no claim that mutated Lean files pass Lean kernel checking.
Run this repository code in the same restricted environment as verify.py.
"""

import copy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import warnings


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CURRENT = Path("research/lean-current-r420-boundary-interfaces")
OLD = Path("research/community-cold617-audit/pr612/lean")
WORD = Path("research/e8-bit-r420/data/bitE8mut-r420.json.gz")
HISTORICAL = Path("research/community-cold617-audit/im-cold617-formal-binding.py")
CURRENT_FILE = "CurrentR420BoundaryData.lean"
BOUNDARY_FILE = "SelectedBitCarrierBoundaryData.lean"
PHASE_FILE = "SelectedBitCarrierPhaseBData.lean"

spec = importlib.util.spec_from_file_location("r420_binding", HERE / "verify.py")
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("mutation anchor must occur exactly once: " + old)
    return text.replace(old, new, 1)


class SourceCorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        binding.audit(ROOT)  # Pin the historical code before executing it.
        cls.current = (ROOT / CURRENT / CURRENT_FILE).read_text(encoding="utf-8")
        cls.boundary = (ROOT / OLD / BOUNDARY_FILE).read_text(encoding="utf-8")
        cls.phase = (ROOT / OLD / PHASE_FILE).read_text(encoding="utf-8")
        cls.raw = (ROOT / WORD).read_bytes()
        cls.word = json.loads(gzip.decompress(cls.raw))
        source = (ROOT / HISTORICAL).read_text(encoding="utf-8")
        marker = "p=root/'research/lean-current588-native-moment';"
        if source.count(marker) != 1:
            raise ValueError("historical R420 prefix boundary changed")
        cls.prefix = source.split(marker)[0]

    def historical_check(self, current):
        """Run the actual historical checks; do not reimplement their logic."""
        with tempfile.TemporaryDirectory(prefix="r420-binding-") as dirname:
            root = Path(dirname)
            for relative in (CURRENT, OLD, WORD.parent):
                (root / relative).mkdir(parents=True, exist_ok=True)
            (root / CURRENT / CURRENT_FILE).write_text(current, encoding="utf-8")
            (root / OLD / BOUNDARY_FILE).write_text(self.boundary, encoding="utf-8")
            (root / OLD / PHASE_FILE).write_text(self.phase, encoding="utf-8")
            (root / WORD).write_bytes(self.raw)
            (root / CURRENT / "SOURCE_BINDING.json").write_bytes(
                (ROOT / CURRENT / "SOURCE_BINDING.json").read_bytes())
            program = replace_once(
                self.prefix, "'/tmp/integer-mult-family588'", repr(str(root)))
            for filename in (BOUNDARY_FILE, PHASE_FILE):
                program = replace_once(
                    program, repr("/tmp/im-cold617-replay/lean612-macos/" + filename),
                    repr(str(root / OLD / filename)))
            # optimize=0 is essential: the inherited script uses assert.
            with warnings.catch_warnings():
                # The retained historical json.load(open(...)) emits this
                # unrelated warning under unittest; its code stays unchanged.
                warnings.simplefilter("ignore", ResourceWarning)
                exec(compile(program, str(ROOT / HISTORICAL), "exec", optimize=0), {})
            receipt = json.loads((root / OLD / "SOURCE-CORRESPONDENCE.json").read_text())
            self.assertEqual(receipt["status"], "PASS_LITERAL_R420_SOURCE_CORRESPONDENCE")
            self.assertEqual(receipt["B_gates"], 837)
            self.assertEqual(len(receipt["fields"]), 7)

    def semantic_check(self, current):
        projection = binding.extract_projection(current, self.boundary, self.phase)
        binding.compare_projection(projection, self.word)

    def demonstrate_missed_change(self, old, new):
        changed = replace_once(self.current, old, new)
        self.historical_check(changed)
        # Deliberately bypass source-hash admission: expression/value checking
        # itself must reject the altered data, rather than relying on a hash.
        with self.assertRaises(binding.AuditError):
            self.semantic_check(changed)

    def test_unmodified_sources_pass_both(self):
        self.historical_check(self.current)
        self.semantic_check(self.current)

    def test_start_offset_change_is_missed_by_historical_check(self):
        self.demonstrate_missed_change("(fun r => r+2)", "(fun r => r+3)")

    def test_phase_band_order_change_is_missed_by_historical_check(self):
        self.demonstrate_missed_change(
            "def phaseB := firstTargets ++ sourceMiddle ++ lastTargets",
            "def phaseB := lastTargets ++ sourceMiddle ++ firstTargets")

    def test_lines_alias_reversal_is_missed_by_historical_check(self):
        self.assertNotEqual(self.word["lines"], self.word["lines"][::-1])
        self.demonstrate_missed_change(
            "abbrev lines := SelectedBitCarrierBoundary.Data.lines",
            "abbrev lines := SelectedBitCarrierBoundary.Data.lines.reverse")

    def test_frame_map_reversal_is_missed_by_historical_check(self):
        self.assertNotEqual(self.word["frames"], self.word["frames"][::-1])
        self.demonstrate_missed_change(
            "def frames : List (List Nat) := frameOrder.map frameAt",
            "def frames : List (List Nat) := (frameOrder.map frameAt).reverse")

    def test_scatter_alias_reversal_is_missed_by_historical_check(self):
        self.assertNotEqual(self.word["scatter"], self.word["scatter"][::-1])
        self.demonstrate_missed_change(
            "abbrev scatter := SelectedBitCarrierPhaseB.Data.scatter",
            "abbrev scatter := SelectedBitCarrierPhaseB.Data.scatter.reverse")

    def test_final_prefix_length_change_is_missed_by_historical_check(self):
        self.demonstrate_missed_change(
            "SelectedBitCarrierBoundary.Data.final.take 660",
            "SelectedBitCarrierBoundary.Data.final.take 659")

    def test_historical_assertions_are_active_even_under_optimized_python(self):
        changed = replace_once(self.current, "[603, 568, 597, 583,", "[602, 568, 597, 583,")
        with self.assertRaises(AssertionError):
            self.historical_check(changed)
        with self.assertRaises(binding.AuditError):
            self.semantic_check(changed)

    def test_source_grammar_controls(self):
        cases = [
            ("literal_suffix", "def ret : List Nat := [603, 568, 597, 583, 569, 604, 616, 596, 598]", "def ret : List Nat := [603, 568, 597, 583, 569, 604, 616, 596, 598] ++ []"),
            ("duplicate_declaration", "def R : Nat := 420", "def R : Nat := 420\ndef R : Nat := 420"),
            ("namespace_shadow", "def R : Nat := 420", "namespace Shadow\ndef R : Nat := 420\nend Shadow"),
            ("unrecognized_command", "def R : Nat := 420", "set_option maxRecDepth 3000\ndef R : Nat := 420"),
            ("malformed_fin_proof", "⟨0, by decide⟩", "⟨0, by decide extra⟩"),
            ("duplicate_frame_index", "⟨0, by decide⟩", "⟨1, by decide⟩"),
            ("frame_index_out_of_bounds", "⟨0, by decide⟩", "⟨672, by decide⟩"),
            ("bare_fin_index", "⟨0, by decide⟩", "0"),
            ("frame_lookup_alias", "SelectedBitCarrierBoundary.Data.frames[i.val]", "SelectedBitCarrierBoundary.Data.frames[0]"),
            ("phase_missing_band", "def phaseB := firstTargets ++ sourceMiddle ++ lastTargets", "def phaseB := firstTargets ++ lastTargets"),
            ("trailing_module_command", "end CurrentMain.CurrentR420Boundary.Data", "end CurrentMain.CurrentR420Boundary.Data\nopen CurrentMain"),
            ("unsupported_character", "def R : Nat := 420", "def R : Nat := 420;"),
            ("unterminated_comment", "def R : Nat := 420", "def R : Nat := 420 /-"),
            ("list_as_gate_tuple", "(143, 120, [3])", "[143, 120, [3]]"),
        ]
        for name, old, new in cases:
            with self.subTest(name=name), self.assertRaises(binding.AuditError):
                self.semantic_check(replace_once(self.current, old, new))

    def test_order_and_multiplicity_controls(self):
        original = binding.extract_projection(self.current, self.boundary, self.phase)
        for name, mutate in [
            ("B_gate_order", lambda p: p["B"].reverse()),
            ("B_operand_order", lambda p: p["B"][-1][2].reverse()),
            ("B_operand_multiplicity", lambda p: p["B"][-1][2].extend([5, 5])),
            ("scatter_order", lambda p: p["scatter"][0].reverse()),
            ("scatter_multiplicity", lambda p: p["scatter"][0].extend([0, 0])),
            ("frame_rows_order", lambda p: p["frames"].reverse()),
            ("retained_order", lambda p: p["ret"].reverse()),
        ]:
            altered = copy.deepcopy(original)
            mutate(altered)
            with self.subTest(name=name), self.assertRaises(binding.AuditError):
                binding.compare_projection(altered, self.word)

    def test_json_types_and_keys(self):
        projection = binding.extract_projection(self.current, self.boundary, self.phase)
        for field, transform in [
            ("h", lambda _: 8.0),
            ("B", lambda v: [[False, *v[0][1:]], *v[1:]]),
            ("start", lambda v: [*v[:120], False, *v[121:]]),
        ]:
            altered = copy.deepcopy(self.word)
            altered[field] = transform(altered[field])
            with self.subTest(field=field), self.assertRaises(binding.AuditError):
                binding.compare_projection(projection, altered)
        for payload in ('{"h":8,"h":8}', '{"h":NaN}'):
            with self.subTest(payload=payload), self.assertRaises(binding.AuditError):
                binding.load_word(payload)

    def test_nested_comments_are_accepted(self):
        changed = replace_once(self.current, "def R : Nat := 420",
                               "def /- nested /- def R := 999 -/ comment -/ R : Nat := 420")
        self.semantic_check(changed)

    def test_recompression_preserves_result(self):
        with tempfile.TemporaryDirectory(prefix="r420-recompress-") as directory:
            alternate = Path(directory) / "word.json.gz"
            alternate.write_bytes(gzip.compress(gzip.decompress(self.raw), compresslevel=1, mtime=75))
            self.assertNotEqual(alternate.read_bytes(), self.raw)
            self.assertEqual(binding.audit(ROOT, alternate), binding.audit(ROOT))


if __name__ == "__main__":
    unittest.main(verbosity=2)
