"""Adversarial controls for semantic, geometric, pricing, and certificate layers."""
from copy import deepcopy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


v = module("verify")


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        constructor = module("construct")
        cls.source = v.pinned_source()
        cls.candidate, cls.recipe = constructor.construct(cls.source)
        cls.kernels = v.kernel(cls.source)
        cls.geom = v.geometry(cls.source)

    def test_positive_full_certificate(self):
        self.assertEqual(v.verify(self.source, self.candidate, self.recipe)["status"], "PASS")

    def test_selected_budget_optimum(self):
        word, recipe = module("construct").construct(self.source, cuts=[5, 34, 39, 57, 78])
        receipt = v.verify(self.source, word, recipe)
        self.assertEqual(receipt["D_additions"]["candidate"], 15025)
        self.assertEqual(receipt["positive_prefix"]["candidate"]["reverse"], 9800790)
        self.assertTrue(receipt["cut_budget"]["selected_attains_cut_class_optimum"])

    def test_feasible_nonoptimal_cut_not_claimed_optimal(self):
        cuts = [i for i, p in enumerate(self.recipe["mst_parents"]) if p != 120]
        word, recipe = module("construct").construct(self.source, cuts=cuts)
        receipt = v.verify(self.source, word, recipe)
        self.assertTrue(receipt["cut_budget"]["selected_feasible"])
        self.assertFalse(receipt["cut_budget"]["selected_attains_cut_class_optimum"])

    def test_missing_prepare(self):
        word = deepcopy(self.candidate)
        del word["D"][0]
        with self.assertRaisesRegex(v.Reject, "D endpoint"):
            v.check_d(word, self.kernels)
        with self.assertRaisesRegex(v.Reject, "full endpoint"):
            v.whole_word(word, self.geom)

    def test_missing_unprepare(self):
        word = deepcopy(self.candidate)
        del word["D"][-1]
        with self.assertRaisesRegex(v.Reject, "D endpoint"):
            v.check_d(word, self.kernels)

    def test_missing_helper_term(self):
        word = deepcopy(self.candidate)
        index = self.recipe["D_boundaries"]["inject"][0]
        word["D"][index][2].pop()
        with self.assertRaisesRegex(v.Reject, "D endpoint"):
            v.check_d(word, self.kernels)

    def test_source_dependent_D(self):
        word = deepcopy(self.candidate)
        word["D"].append([0, 120, [0]])
        with self.assertRaisesRegex(v.Reject, "read targets/helpers"):
            v.check_d(word, self.kernels)

    def test_invalid_parent(self):
        recipe = deepcopy(self.recipe)
        recipe["parents"][0] = 121
        with self.assertRaisesRegex(v.Reject, "invalid parent"):
            v.check_tree(recipe, self.kernels)

    def test_parent_cycle(self):
        recipe = deepcopy(self.recipe)
        recipe["parents"][:3] = [1, 2, 0]
        with self.assertRaises(v.Reject):
            v.check_tree(recipe, self.kernels)

    def test_underpriced_edge(self):
        recipe = deepcopy(self.recipe)
        recipe["mst_edges"][0]["weight"] -= 1
        with self.assertRaisesRegex(v.Reject, "mispriced edge"):
            v.check_tree(recipe, self.kernels)

    def test_underpriced_total(self):
        recipe = deepcopy(self.recipe)
        recipe["metrics"]["tree_weight"] -= 1
        with self.assertRaisesRegex(v.Reject, "mispriced selected tree cost"):
            v.check_recipe(self.source, self.candidate, recipe, self.kernels)

    def test_malformed_source_pin(self):
        recipe = deepcopy(self.recipe)
        recipe["source"]["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(v.Reject, "malformed source pin"):
            v.check_recipe(self.source, self.candidate, recipe, self.kernels)

    def test_misleading_metadata(self):
        for field, value in (("seed", 7), ("algorithm", "oracle"), ("optimality_scope", "globally optimal")):
            with self.subTest(field=field):
                recipe = deepcopy(self.recipe)
                recipe[field] = value
                with self.assertRaises(v.Reject):
                    v.check_recipe(self.source, self.candidate, recipe, self.kernels)
        for field in ("path", "base_commit"):
            with self.subTest(field=field):
                recipe = deepcopy(self.recipe)
                recipe["source"][field] = "not-the-source"
                with self.assertRaisesRegex(v.Reject, "source provenance"):
                    v.check_recipe(self.source, self.candidate, recipe, self.kernels)

    def test_different_tied_MST_cannot_claim_seed6(self):
        word, recipe = module("construct").construct(self.source, seed=0)
        recipe["seed"] = 6
        with self.assertRaisesRegex(v.Reject, "tie certificate"):
            v.check_recipe(self.source, word, recipe, self.kernels)

    def test_nonminimal_honestly_priced_spanning_tree(self):
        recipe = {"parents": [120] * 120,
                  "mst_edges": [{"u": i, "v": 120, "weight": self.kernels[i].bit_count()} for i in range(120)]}
        self.assertEqual(v.check_tree(recipe, self.kernels, minimal=False)["total_weight"], 19922)
        with self.assertRaisesRegex(v.Reject, "cycle property"):
            v.check_tree(recipe, self.kernels)

    def test_neutral_paid_pair_semantically_valid_but_costs_two(self):
        word = deepcopy(self.candidate)
        word["D"].extend([[0, 120, [121]], [0, 120, [121]]])
        self.assertEqual(v.check_d(word, self.kernels), 14923)
        original = v.whole_word(self.candidate, self.geom)
        neutral = v.whole_word(word, self.geom)
        self.assertEqual(neutral["path"], original["path"])
        self.assertEqual(neutral["additions"], original["additions"] + 2)
        recipe = deepcopy(self.recipe)
        recipe["candidate_canonical_sha256"] = v.digest(word)
        with self.assertRaisesRegex(v.Reject, "claimed recipe"):
            v.check_recipe(self.source, word, recipe, self.kernels)

    def test_changed_nonD_even_if_semantically_neutral(self):
        word = deepcopy(self.candidate)
        full = self.geom[0].index(8)
        word["C"].extend([[full, 0, [1]], [full, 0, [1]]])
        v.whole_word(word, self.geom)
        with self.assertRaisesRegex(v.Reject, "outside D"):
            v.verify(self.source, word, self.recipe)

    def test_numerically_equal_nonD_type_changes_rejected(self):
        for field in ("v", "start"):
            with self.subTest(field=field):
                word, recipe = deepcopy(self.candidate), deepcopy(self.recipe)
                if field == "v":
                    word["v"] = 120.0
                else:
                    word["start"][120] = False
                recipe["candidate_canonical_sha256"] = v.digest(word)
                with self.assertRaisesRegex(v.Reject, "outside D"):
                    v.verify(self.source, word, recipe)

    def test_wrong_D_frame(self):
        word = deepcopy(self.candidate)
        word["D"][0][0] = self.source["start"][0]
        with self.assertRaisesRegex(v.Reject, "frame zero"):
            v.check_d(word, self.kernels)
        with self.assertRaisesRegex(v.Reject, "illegal frame climb"):
            v.whole_word(word, self.geom)

    def test_recompression_preserves_source_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.json.gz"
            with gzip.open(path, "wt", compresslevel=1) as stream:
                json.dump(self.source, stream, indent=1)
            self.assertEqual(v.pinned_source(path), self.source)
            damaged = deepcopy(self.source)
            damaged["D"][0][2].pop()
            with gzip.open(path, "wt") as stream:
                json.dump(damaged, stream)
            with self.assertRaisesRegex(v.Reject, "canonical SHA256"):
                v.pinned_source(path)

    def test_prefix_cap_exposes_unconstrained_optimum_failure(self):
        baseline = v.positive_prefix(v.whole_word(self.source, self.geom)["events"])
        optimum = v.positive_prefix(v.whole_word(self.candidate, self.geom)["events"])
        self.assertEqual((baseline["forward"], baseline["reverse"], baseline["payload_bits"]), (144651, 2270064, 100))
        self.assertEqual((optimum["forward"], optimum["reverse"], optimum["payload_bits"]), (144651, 20395400, 106))
        self.assertFalse(optimum["below_2_pow_104"])

    def test_forest_optimality_does_not_mean_global_linear_optimality(self):
        a, b, c = 0b111, 0b111000, 0b111000000
        rows = [a ^ b, b ^ c, a ^ c]
        self.assertEqual([x.bit_count() for x in rows], [6, 6, 6])
        self.assertEqual([(rows[i] ^ rows[j]).bit_count() + 2 for i in range(3) for j in range(i)], [8, 8, 8])
        self.assertEqual(rows[2] ^ rows[0] ^ rows[1], 0)
        self.assertLess(2 + 6 + 6 + 2, 6 + 6 + 6)
        targets = [1 << (9 + i) for i in range(3)]
        targets[2] ^= targets[0]
        targets[2] ^= targets[1]
        targets[0] ^= rows[0]
        targets[1] ^= rows[1]
        targets[2] ^= targets[1]
        targets[2] ^= targets[0]
        self.assertEqual(targets, [(1 << (9 + i)) ^ rows[i] for i in range(3)])

    def test_feasible_R420_rewire_beats_selected_cut_outside_certified_class(self):
        word, recipe = module("construct").construct(self.source, cuts=[5, 34, 39, 57, 78])
        parent = list(recipe["parents"])
        self.assertEqual(parent[32], 37)
        parent[32] = 34
        levels = []
        for target in range(120):
            node, level = target, 0
            for _ in range(121):
                if node == 120:
                    break
                node, level = parent[node], level + 1
            self.assertEqual(node, 120, "rewired parent chain must reach dummy")
            levels.append(level)
        order = sorted(range(120), key=lambda i: (-levels[i], i))
        prepare = [[0, 120 + i, [120 + parent[i]]] for i in order if parent[i] != 120]
        inject = []
        for i, p in enumerate(parent):
            residual = self.kernels[i] ^ (self.kernels[p] if p != 120 else 0)
            helpers = [r for r in range(240, 660) if residual >> r & 1]
            if helpers:
                inject.append([0, 120 + i, helpers])
        word["D"] = prepare + inject + list(reversed(prepare))
        self.assertEqual(v.check_d(word, self.kernels), 15023)
        replay = v.whole_word(word, self.geom)
        self.assertEqual((replay["columns"], replay["additions"]), (660, 22017))
        self.assertEqual(replay["path"], v.whole_word(self.source, self.geom)["path"])
        prefix = v.positive_prefix(replay["events"])
        self.assertEqual((prefix["forward"], prefix["reverse"], prefix["payload_bits"]), (144651, 9800790, 104))
        self.assertTrue(prefix["below_2_pow_104"])
        recipe["candidate_canonical_sha256"] = v.digest(word)
        recipe["parents"] = parent
        recipe["tree_edges"] = [{"u": min(i, p), "v": max(i, p),
                                 "weight": self.kernels[i].bit_count() if p == 120 else
                                 (self.kernels[i] ^ self.kernels[p]).bit_count() + 2}
                                for i, p in enumerate(parent)]
        with self.assertRaisesRegex(v.Reject, "not declared cut"):
            v.check_recipe(self.source, word, recipe, self.kernels)


if __name__ == "__main__":
    unittest.main()
