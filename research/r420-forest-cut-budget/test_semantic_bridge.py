"""Source-bound application of the conditional semantic-D chronology bridge.

Credits: woklerx, PR1194 at 2e39c98238f543d988f9efc1b076590a4b780dca
(research/r439-semantic-d-contract-seed10/PROOF.md), and Arham Tahir,
PR1311 at a2875c1834b9c9ef42a84eda4890d5462cc98fa5
(research/r439-abc-semantic-bridge). Their argument substitutes equal zero-frame
prefixes before an identical continuation, retaining the realization premises.
This checks that application's concrete premises; it proves no new theorem or
full hosted admission. The package reproduce.py runs this suite with a timeout.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_PATH = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
CHECKER_PATH = "research/e8-bit-r420/code/xcheck.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load_module("forest_verify", HERE / "verify.py")


class SemanticBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for relative in (SOURCE_PATH, CHECKER_PATH):
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            v.need(actual == pins["repository_inputs_sha256"][relative],
                   "bridge pinned input changed: " + relative)
        cls.source = v.pinned_source(ROOT / SOURCE_PATH)
        cls.candidate = v.read_word(HERE / "data/word.json.gz")
        cls.recipe = json.loads((HERE / "data/recipe.json").read_text())
        v.need(v.digest(cls.source) == pins["source_word_canonical_sha256"] ==
               cls.recipe["source"]["canonical_sha256"], "bridge source identity")
        v.need(v.digest(cls.candidate) == cls.recipe["candidate_canonical_sha256"],
               "bridge candidate identity")
        cls.checker = load_module("pinned_r420_xcheck", ROOT / CHECKER_PATH)
        cls.source_check = cls.checker.check(cls.source)
        cls.candidate_check = cls.checker.check(cls.candidate)
        cls.kernels = v.kernel(cls.source)
        cls.geom = v.geometry(cls.source)

    def test_original_interface_and_exact_legacy_rejections(self):
        _, _, source_flow, source_h, source_c, _ = self.source_check
        _, _, candidate_flow, candidate_h, candidate_c, _ = self.candidate_check
        self.assertEqual(source_flow["columns"], 660)
        self.assertEqual(candidate_flow["columns"], 660)
        self.assertEqual(len(source_h), 5)
        self.assertEqual(len(source_c), 4)
        self.assertTrue(all(source_h.values()), source_h)
        self.assertTrue(all(source_c.values()), source_c)
        self.assertEqual(candidate_h.keys(), source_h.keys())
        self.assertEqual(candidate_c.keys(), source_c.keys())
        self.assertEqual({name for name, ok in candidate_h.items() if not ok},
                         {"H2_D_frame0_targets_from_helpers"})
        self.assertEqual({name for name, ok in candidate_c.items() if not ok},
                         {"K_equals_D"})

    def test_original_d_splice_is_the_original_checked_word(self):
        virtual = deepcopy(self.candidate)
        virtual["D"] = deepcopy(self.source["D"])
        self.assertEqual(v.digest(virtual), v.digest(self.source))
        self.assertEqual(virtual, self.source)
        # Exact equality transfers the already executed original interface
        # check; the proof-only D is never charged as the candidate's circuit.
        self.assertTrue(all(self.source_check[3].values()))
        self.assertTrue(all(self.source_check[4].values()))

    def test_equal_dirty_prefix_values_frames_and_complete_paths(self):
        self.assertEqual(v.check_d(self.source, self.kernels), 19922)
        self.assertEqual(v.check_d(self.candidate, self.kernels), 15025)
        source_values, source_frames, _ = self.source_check[0].replay(sections=("D",))
        candidate_values, candidate_frames, _ = self.candidate_check[0].replay(sections=("D",))
        self.assertEqual(len(source_values), 660)
        self.assertEqual(candidate_values, source_values)
        self.assertEqual(candidate_frames, source_frames)
        self.assertEqual(source_frames, self.source["start"])
        zero = self.source["frames"].index([])
        self.assertTrue(all(f == zero for f in candidate_frames[v.V:]))
        source = v.whole_word(self.source, self.geom)
        candidate = v.whole_word(self.candidate, self.geom)
        self.assertEqual(source["columns"], candidate["columns"])
        self.assertEqual(source["columns"], 660)
        self.assertEqual(source["path"], candidate["path"])
        self.assertEqual(source["paid_histogram"], candidate["paid_histogram"])
        self.assertEqual(source["rank_mass"], candidate["rank_mass"])
        self.assertEqual(candidate["rank_mass"], 5112)

    def test_missing_restoration_breaks_the_dirty_boundary(self):
        bad = deepcopy(self.candidate)
        del bad["D"][-1]
        with self.assertRaisesRegex(v.Reject, "D endpoint mismatch"):
            v.check_d(bad, self.kernels)
        with self.assertRaisesRegex(v.Reject, "full endpoint mismatch"):
            v.whole_word(bad, self.geom)

    def test_neutral_frame_change_is_not_a_valid_prefix_substitution(self):
        bad = deepcopy(self.candidate)
        full = self.candidate_check[0].FULL
        gate = [full, v.V, [v.V + 1]]
        bad["D"] = [deepcopy(gate), deepcopy(gate)] + bad["D"]
        # Cancelling XORs preserve scalar columns but cannot undo frame climbs.
        self.assertEqual(v.scalar_replay(bad, ("D",)),
                         v.scalar_replay(self.candidate, ("D",)))
        with self.assertRaisesRegex(v.Reject, "frame zero"):
            v.check_d(bad, self.kernels)
        with self.assertRaisesRegex(v.Reject, "illegal frame climb"):
            v.whole_word(bad, self.geom)

    def test_neutral_target_feedback_still_violates_retained_h1(self):
        bad = deepcopy(self.candidate)
        zero = bad["frames"].index([])
        gate = [zero, 2 * v.V, [v.V]]
        bad["D"] = [deepcopy(gate), deepcopy(gate)] + bad["D"]
        self.assertEqual(v.scalar_replay(bad, ("D",)),
                         v.scalar_replay(self.candidate, ("D",)))
        # Endpoint and frames alone would accept this neutral helper write.
        replay = v.whole_word(bad, self.geom)
        self.assertEqual(replay["columns"], 660)
        self.assertEqual(replay["rank_mass"], 5112)
        with self.assertRaisesRegex(v.Reject, "write targets"):
            v.check_d(bad, self.kernels)
        hypotheses, _, _ = self.checker.Word(bad).interface()
        self.assertFalse(hypotheses["H1_no_target_feeds_z"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
