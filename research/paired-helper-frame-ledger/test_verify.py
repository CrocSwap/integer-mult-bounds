# SPDX-License-Identifier: Apache-2.0
"""Adversarial controls for the finite frame/cleanup ledger only.

These tests load the new ledger, not a predecessor producer or checker. The
small-space oracle uses row rank, independently of the ledger set expansion.
They do not check native operator identities or the multiplication theorem.
"""
from collections import Counter
from copy import deepcopy
import gzip
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("paired_frame_ledger", HERE / "ledger.py")
ledger = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ledger
SPEC.loader.exec_module(ledger)
HELPERS = (424, 428, 412, 331, 299, 320, 511, 304, 499)


def naive_span(vectors):
    """Enumerate each coefficient mask independently, without span extension."""
    values = set()
    for mask in range(1 << len(vectors)):
        value = 0
        for index, vector in enumerate(vectors):
            if mask >> index & 1:
                value ^= vector
        values.add(value)
    return frozenset(values)


def binary_rank(vectors):
    """Independent oracle using XOR pivot elimination, not span expansion."""
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def shape_counts(word):
    """The dimension-only gate counts cannot distinguish several controls."""
    return Counter((section, gate[0], len(gate[-1]))
                   for section in ("A", "B", "restore", "cleanup")
                   for gate in word[section])


class FrameLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = {}
        for kind in ("PARENT", "WORD"):
            for variant in ("base", "extra"):
                name = f"{kind}-{variant}"
                with gzip.open(HERE / "data" / f"{name}.json.gz", "rt") as source:
                    cls.words[name] = json.load(source)
        cls.transforms = []
        for helper in HELPERS:
            with (HERE / "data" / f"TRANSFORM-{helper}.json").open() as source:
                cls.transforms.append(json.load(source))

    def reject_word(self, word):
        with self.assertRaises(ValueError):
            ledger.audit_word(word)

    def test_finite_span_oracle(self):
        subspaces = {}
        # All 128 generating subsets of the seven nonzero 3-bit vectors.
        for mask in range(128):
            generators = [v for v in range(1, 8) if mask >> (v - 1) & 1]
            rank = binary_rank(generators)
            expected = frozenset(v for v in range(8)
                                 if binary_rank(generators + [v]) == rank)
            actual = ledger.span(generators)
            self.assertEqual(actual, expected)
            self.assertEqual(ledger.dimension(actual), rank)
            if rank == len(generators):
                self.assertEqual(ledger.frame_basis(generators), expected)
            else:
                with self.assertRaises(ValueError):
                    ledger.frame_basis(generators)
            subspaces[actual] = generators
        self.assertEqual(len(subspaces), 16)
        # Every ordered pair, including equal-rank unequal planes. Containment
        # is independently checked by rank of the concatenated generators.
        for a, generators_a in subspaces.items():
            for b, generators_b in subspaces.items():
                self.assertEqual(a <= b, binary_rank(generators_a + generators_b)
                                 == binary_rank(generators_b))

    def test_all_frozen_words_and_chains(self):
        for name, word in self.words.items():
            with self.subTest(word=name):
                receipt = ledger.audit_word(word)
                self.assertEqual(receipt["profile"], word["report"]["local_profile"])
                self.assertEqual(receipt["width_inventory"], word["report"]["width_inventory"])
                self.assertEqual(receipt["independent_roles"], 632)
                self.assertEqual(receipt["buffer_count"], 73 if name.startswith("PARENT") else 82)
        for variant in ("base", "extra"):
            with self.subTest(chain=variant):
                receipt = ledger.audit_chain(self.words[f"PARENT-{variant}"],
                                             self.words[f"WORD-{variant}"], self.transforms)
                self.assertEqual(len(receipt["stages"]), 9)
                self.assertEqual(len(receipt["frame_edits"]), 13)
                self.assertEqual(receipt["rank_mass_delta"], -9)
                self.assertEqual(receipt["changed_helpers"], sorted(HELPERS))

    def test_equal_rank_wrong_subspace_and_chronology(self):
        original = self.words["WORD-base"]
        wrong = deepcopy(original)
        self.assertEqual(wrong["A"][13][-1], [45])
        wrong["A"][13][-1] = [43]
        self.assertEqual(len(naive_span([45])), len(naive_span([43])))
        self.assertNotEqual(naive_span([45]), naive_span([43]))
        self.assertEqual(shape_counts(wrong), shape_counts(original))
        self.reject_word(wrong)
        early = deepcopy(original)
        # Read the source at frame [45] before the warp from [382]. Same gates.
        early["A"][12], early["A"][13] = early["A"][13], early["A"][12]
        self.assertEqual(shape_counts(early), shape_counts(original))
        self.reject_word(early)

    def test_wrong_warp_preimage_and_rank_preserving_map(self):
        original = self.words["WORD-base"]
        wrong = deepcopy(original)
        self.assertEqual(wrong["A"][12][3], [382])
        wrong["A"][12][3] = [383]
        self.assertEqual(shape_counts(wrong), shape_counts(original))
        self.reject_word(wrong)
        shifted = deepcopy(original)
        columns = shifted["warps"][0][2]
        before = tuple(columns)
        # An elementary column operation preserves matrix rank, but need not
        # carry the declared source subspace to the declared destination.
        columns[0] ^= columns[1]
        self.assertEqual(len(naive_span(before)), len(naive_span(columns)))
        self.assertEqual(shape_counts(shifted), shape_counts(original))
        self.reject_word(shifted)

    def test_report_cannot_omit_paid_transition(self):
        original = self.words["WORD-base"]
        receipt = ledger.audit_word(original)
        endpoint = receipt["section_profiles"]["endpoint"]
        self.assertGreater(sum(endpoint.values()), 0)
        wrong = deepcopy(original)
        # Simulate the ledger obtained by stopping before the terminal climbs.
        for rank, count in endpoint.items():
            wrong["report"]["local_profile"][rank] -= count
            if wrong["report"]["local_profile"][rank] == 0:
                del wrong["report"]["local_profile"][rank]
        self.reject_word(wrong)
        wrong = deepcopy(original)
        wrong["report"]["width_inventory"]["8"] -= 1
        wrong["report"]["width_inventory"]["9"] += 1
        self.reject_word(wrong)

    def test_helper499_scale_must_use_lowered_frame(self):
        wrong = deepcopy(self.words["WORD-base"])
        self.assertEqual(wrong["restore"][40][:4], ["scale", 499, -1, 1])
        self.assertEqual(len(naive_span(wrong["restore"][40][-1])), 256)
        wrong["restore"][40][-1] = [256, 128, 64, 32, 16, 8, 4, 2, 1]
        self.reject_word(wrong)

    def test_cleanup_buffer_alias_and_wrong_inverse(self):
        original = self.words["WORD-base"]
        alias = deepcopy(original)
        self.assertEqual(alias["cleanup"][0][2], 1203)
        alias["cleanup"][0][2] = 499  # 1203 = 704 + 499 is the saved copy.
        self.assertEqual(shape_counts(alias), shape_counts(original))
        self.reject_word(alias)
        reciprocal = deepcopy(original)
        self.assertEqual(reciprocal["cleanup"][603][:4], ["scale", 68, 2, 1])
        reciprocal["cleanup"][603][2:4] = [1, 2]
        self.assertEqual(shape_counts(reciprocal), shape_counts(original))
        self.reject_word(reciprocal)
        for alias_value in (True, 1.0):
            wrong_type = deepcopy(original)
            self.assertEqual(wrong_type["cleanup"][0][3], 1)
            wrong_type["cleanup"][0][3] = alias_value
            with self.subTest(coefficient_type=type(alias_value).__name__):
                self.reject_word(wrong_type)

    def test_transform_old_frame_index_and_lowered_scale_binding(self):
        parent, final = self.words["PARENT-base"], self.words["WORD-base"]
        for control in ("old_frame", "candidate_index", "omitted_scale"):
            transforms = deepcopy(self.transforms)
            changes = transforms[-1]["frame_changes"]
            if control == "old_frame":
                # Keep rank eight but change the exact parent subspace.
                changes[0]["old_frame"][2] ^= 1
            elif control == "candidate_index":
                changes[0]["candidate_index"] += 1
            else:
                changes.pop()  # The helper499 scale refit is a separate edit.
            with self.subTest(control=control), self.assertRaises(ValueError):
                ledger.audit_chain(parent, final, transforms)


class InputBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("paired_frame_wrapper_tests", HERE / "verify.py")
        cls.wrapper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.wrapper)

    def test_source_inventory_and_byte_pins(self):
        # Copies are confined to a disposable system temporary directory;
        # committed fixtures and predecessor programs are never modified.
        with tempfile.TemporaryDirectory(prefix="paired-frame-io-") as temporary:
            directory = Path(temporary)
            shutil.copytree(HERE / "data", directory / "data")
            for name in ("INPUTS.json", "SOURCE-CREDITS.md"):
                shutil.copyfile(HERE / name, directory / name)
            inputs = self.wrapper.load_inputs(directory)
            self.assertEqual(set(inputs),
                             {f"{kind}-{variant}" for kind in ("PARENT", "WORD")
                              for variant in ("base", "extra")}
                             | {f"TRANSFORM-{helper}" for helper in HELPERS})
            self.assertEqual(len(inputs["WORD-base"]["helper_final"]), 82)
            source = directory / "data" / "WORD-base.json.gz"
            original = source.read_bytes()
            source.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaisesRegex(ValueError, "source bytes changed"):
                self.wrapper.load_inputs(directory)
            source.write_bytes(original)
            saved = directory / "saved-source.gz"
            source.rename(saved)
            with self.assertRaisesRegex(ValueError, "unexpected data file"):
                self.wrapper.load_inputs(directory)
            saved.rename(source)
            extra = directory / "data" / "unlisted.json"
            extra.write_text("{}")
            with self.assertRaisesRegex(ValueError, "unexpected data file"):
                self.wrapper.load_inputs(directory)
            extra.unlink()
            manifest = directory / "INPUTS.json"
            original_manifest = manifest.read_bytes()
            manifest.write_bytes(original_manifest + b"\n")
            with self.assertRaisesRegex(ValueError, "source manifest pin mismatch"):
                self.wrapper.load_inputs(directory)
            manifest.write_bytes(original_manifest)
            # Every mutation was repaired; the same copy must pass again.
            self.assertEqual(self.wrapper.canonical(self.wrapper.load_inputs(directory)),
                             self.wrapper.canonical(inputs))

    def test_strict_json_and_receipt_type_distinctions(self):
        for raw in ('{"a":1,"a":2}', '{"outer":{"a":1,"a":2}}',
                    '{"value":NaN}', '{"value":Infinity}', '{"value":-Infinity}',
                    '{"value":1e999}', '{"value":-1e999}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.wrapper.strict_json(raw)
        values = self.wrapper.strict_json('{"values":[true,1,1.0]}')["values"]
        self.assertEqual([type(value) for value in values], [bool, int, float])
        serialized = [self.wrapper.canonical({"value": value}) for value in values]
        self.assertEqual(serialized, ['{"value":true}', '{"value":1}', '{"value":1.0}'])
        self.assertEqual(len(set(serialized)), 3)
        for nonfinite in (float("nan"), float("inf"), -float("inf")):
            with self.assertRaises(ValueError):
                self.wrapper.canonical({"value": nonfinite})


if __name__ == "__main__":
    unittest.main()
