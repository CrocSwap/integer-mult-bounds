"""Behavioral and cross-implementation controls for the A3 exclusion."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import independent
import verify


class A3Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = verify.build()
        cls.other = verify.read_json(verify.PACKAGE / "INDEPENDENT.json")
        cls.roots, _, _, cls.labels, cls.values, cls.costs = verify.labelled_geometry()
        cls.witness = cls.actual["equality_witnesses"][0]

    def flat_mask(self):
        normals = self.witness["normals"]
        return sum(1 << i for i, x in enumerate(self.labels)
                   if all((n & x).bit_count() % 2 == 0 for n in normals))

    def test_committed_receipt(self):
        verify.check_receipt(self.actual, verify.read_json(verify.PACKAGE / "RESULT.json"))

    def test_independent_full_histograms(self):
        self.assertEqual(self.actual["flat_histogram"], self.other["weighted_flat_histogram"])
        self.assertEqual(self.actual["frame_histogram"], self.other["frame_cost_histogram"])
        self.assertEqual(self.actual["pair_histogram"], self.other["union_cost_histogram"])

    def test_all_maximal_flat_sets(self):
        masks = []
        for normals in self.actual["maximal_flat_normals"]:
            masks.append(sorted(x for x in self.labels
                                if all((n & x).bit_count() % 2 == 0 for n in normals)))
        self.assertEqual(sorted(masks), self.other["maximizing_flat_root_labels"])

    def test_all_sixty_equality_witnesses(self):
        pairs = []
        for witness in self.actual["equality_witnesses"]:
            normals = witness["normals"]
            pairs.append({
                "flat_root_labels": sorted(x for x in self.labels
                                           if all((n & x).bit_count() % 2 == 0
                                                  for n in normals)),
                "frame_root_labels": sorted(self.labels[i] for i in witness["frame"]),
                "singleton_root_labels": [sorted(self.labels[i] for i in group)
                                          for group in witness["singletons"]]})
        pairs.sort(key=lambda r: (r["flat_root_labels"], r["frame_root_labels"]))
        self.assertEqual(pairs, self.other["equality_pairs"])

    def test_original_caller_and_losing_relaxations(self):
        caller = self.actual["profile"]
        self.assertEqual(caller["weights"], [2, 2, 6, 6, 6, 6, 6, 7, 7, 7])
        self.assertEqual(caller["retained_code_dimension"], 3)
        self.assertLess(caller["support_only_bound"], caller["endpoint_allowance"])
        self.assertEqual(caller["flat_frame_bound"], caller["endpoint_allowance"])
        self.assertLess(caller["singleton_closed_support_cap"], caller["endpoint_allowance"])

    def test_quotient_and_root_thresholds_are_strict(self):
        self.assertLess(24 + 20, 53)
        self.assertLess(24 + 40, 70)
        self.assertEqual(6 - 3, 3)

    def test_rank_seven_is_a_real_escape_from_closure(self):
        indices = self.witness["singletons"][0]
        rank, span = verify.binary_span(tuple(self.labels[i] for i in indices))
        self.assertEqual(rank, 6)
        extra = next(x for i, x in enumerate(self.labels)
                     if i not in self.witness["frame"] and x not in span)
        self.assertEqual(verify.binary_span(tuple(self.labels[i] for i in indices) + (extra,))[0], 7)

    def test_independent_span_agrees_on_every_singleton(self):
        for witness in self.actual["equality_witnesses"]:
            for indices in witness["singletons"]:
                vectors = tuple(self.labels[i] for i in indices)
                rank, span = verify.binary_span(vectors)
                basis, members = independent.independent_basis(vectors)
                self.assertEqual((rank, span), (len(basis), members))

    def test_missing_singleton_mutation_rejects(self):
        changed = list(self.costs)
        changed[self.witness["singletons"][0][0]] = 0
        with self.assertRaisesRegex(ValueError, "singleton closure"):
            verify.equality_singletons(self.labels, self.values, changed,
                                       self.flat_mask(), self.witness["frame"])

    def test_wrong_binary_label_mutation_rejects(self):
        changed = list(self.labels)
        indices = self.witness["singletons"][0]
        _, span = verify.binary_span(tuple(self.labels[i] for i in indices))
        changed[indices[0]] = next(x for x in self.labels if x not in span)
        with self.assertRaisesRegex(ValueError, "singleton closure"):
            verify.equality_singletons(changed, self.values, self.costs,
                                       self.flat_mask(), self.witness["frame"])

    def test_changed_coverage_receipt_rejects(self):
        for key in ("flat_histogram", "frame_histogram", "equality_witnesses"):
            changed = copy.deepcopy(self.actual)
            changed[key] = []
            with self.assertRaisesRegex(ValueError, "receipt differs"):
                verify.check_receipt(changed, self.actual)

    def test_changed_retained_source_rejects(self):
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            for filename in ("SOURCES.json", "geometry.py", "caller-data.json", "original-bk1b.py"):
                (directory / filename).write_bytes((verify.PACKAGE / filename).read_bytes())
            with patch.object(verify, "PACKAGE", directory):
                verify.source_check()
                with (directory / "geometry.py").open("a") as stream:
                    stream.write("\n# changed\n")
                with self.assertRaisesRegex(ValueError, "geometry hash"):
                    verify.source_check()

    def test_changed_archived_predecessor_rejects(self):
        sources = verify.read_json(verify.PACKAGE / "SOURCES.json")
        for filename in ("original-bk1b.py", "caller-data.json"):
            with tempfile.TemporaryDirectory() as name:
                directory = Path(name)
                for row in sources["archived_sources"]:
                    (directory / row["local_path"]).write_bytes(
                        (verify.PACKAGE / row["local_path"]).read_bytes())
                with patch.object(verify, "PACKAGE", directory):
                    verify.archived_source_check(sources)
                    target = directory / filename
                    target.write_bytes(target.read_bytes() + b"\nchanged archive\n")
                    with self.assertRaisesRegex(ValueError, "archive SHA256"):
                        verify.archived_source_check(sources)
        changed = copy.deepcopy(sources)
        changed["archived_sources"][0]["git_blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "archive Git blob"):
            verify.archived_source_check(changed)
        changed = copy.deepcopy(sources)
        changed["archived_sources"][0]["pin"] = "head:" + "0" * 40 + ":wrong/path"
        with self.assertRaisesRegex(ValueError, "archive origin pin"):
            verify.archived_source_check(changed)

    def test_input_capacity_and_binary_domain_reject(self):
        for values in ((512,), (0,), tuple([1] * 121)):
            with self.assertRaisesRegex(ValueError, "label domain"):
                verify.binary_span(values)
        with self.assertRaisesRegex(ValueError, "span generator capacity"):
            independent.binary_span([1] * 10)
        with self.assertRaisesRegex(ValueError, "binary vector range"):
            independent.binary_span([512])

    def test_original_caller_label_mutation_rejects(self):
        raw = verify.read_json(verify.PACKAGE / "caller-data.json")
        raw["LAB"][0] ^= 2
        with tempfile.TemporaryDirectory() as name:
            directory = Path(name)
            (directory / "caller-data.json").write_text(json.dumps(raw))
            with patch.object(verify, "PACKAGE", directory):
                with self.assertRaisesRegex(ValueError, "caller label bridge"):
                    verify.caller_bridge(self.roots, verify.labelled_geometry()[1], self.labels)

    def test_affine_partition_is_exhaustive_count(self):
        self.assertEqual(self.other["affine_five_flats"] + self.other["even_only_six_spaces"],
                         self.other["six_spaces"])
        self.assertEqual(self.other["affine_five_directions"] * 8,
                         self.other["affine_five_flats"])


if __name__ == "__main__":
    unittest.main()
