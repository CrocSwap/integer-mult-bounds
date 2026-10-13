"""Failure-mode checks for the independently rebuilt 48-frame experiment."""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import contextlib
import gzip
import io
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("roadmap48", ROOT / "research/roadmap48/experiment.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)
sys.modules["experiment"] = E
MODEL_SPEC = importlib.util.spec_from_file_location("roadmap_cost_model", ROOT / "research/roadmap48/cost_model.py")
MODEL = importlib.util.module_from_spec(MODEL_SPEC)
MODEL_SPEC.loader.exec_module(MODEL)
R = E.load_module(ROOT / "research/roadmap48/retiming.py", "roadmap_retiming")
sys.modules["retiming"] = R
OPT = E.load_module(ROOT / "research/roadmap48/optimizations.py", "roadmap_optimizations")


class FrameConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.plan, cls.owner_receipt = E.read_source()
        cls.word, cls.recipe = E.build_word(cls.source)

    def test_original_promotion_and_center_fee_are_separate(self):
        # The inherited builder alone keeps eight old rank-8 descent charges.
        partial = E.PROMOTION.apply(self.source, self.recipe)
        self.assertEqual(E.ints(partial["report"]["local_profile"]),
                         {1:2492, 2:338, 3:430, 4:138, 5:112, 8:8})
        checked = E.check_report(self.word)
        self.assertEqual(checked["profile"], E.NEW_PROFILE)
        self.assertEqual(checked["mass"]-E.rank_mass(E.OLD_PROFILE), 8)

    def test_edit_preserves_entire_scalar_program_and_other_sections(self):
        self.assertEqual([g[:-1] for g in self.source["A"]], [g[:-1] for g in self.word["A"]])
        changed = [i for i, (a, b) in enumerate(zip(self.source["A"], self.word["A"])) if a != b]
        self.assertEqual(changed, list(range(4235, 4283)))
        for section in ("B", "cut", "cleanup", "precondition", "early_cleanup",
                        "helper_final", "start_extra", "target_levels"):
            self.assertEqual(self.source[section], self.word[section], section)

    def test_wrong_base_scalar_is_rejected(self):
        word = deepcopy(self.source)
        word["A"][4235][3] = -1
        with self.assertRaisesRegex(ValueError, "scalar pin"):
            E.build_word(word)

    def test_wrong_base_frame_is_rejected(self):
        word = deepcopy(self.source)
        word["A"][4235][-1] = list(E.FULL)
        with self.assertRaisesRegex(ValueError, "frame pin"):
            E.build_word(word)

    def test_other_source_changes_cannot_bypass_word_pin(self):
        word = deepcopy(self.source)
        word["B"][0][3] *= -1
        with self.assertRaisesRegex(ValueError, "full X4 source content pin"):
            E.build_word(word)

    def test_unsynchronized_center_is_rejected(self):
        word = deepcopy(self.word)
        word["center_frames"] = self.source["center_frames"]
        with self.assertRaisesRegex(ValueError, "center declaration"):
            E.check_report(word)

    def test_stale_center_metadata_is_rejected(self):
        word = deepcopy(self.word)
        word["report"]["centre_ranks"] = [8]*8
        word["report"]["cst"] = 64
        with self.assertRaisesRegex(ValueError, "stale center"):
            E.check_report(word)

    def test_stale_paid_profile_is_rejected(self):
        word = deepcopy(self.word)
        word["report"]["local_profile"] = self.source["report"]["local_profile"]
        with self.assertRaisesRegex(ValueError, "paid profile"):
            E.check_report(word)

    def test_nonmonotone_gate_is_rejected(self):
        word = deepcopy(self.word)
        word["A"][4236][-1] = self.source["A"][4236][-1]
        with self.assertRaisesRegex(ValueError, "nonmonotone"):
            E.check_report(word)

    def test_mixed_frame_bases_have_same_span(self):
        self.assertEqual(E.basis((1,2,3)), E.basis((1,2)))
        for f in self.source["center_frames"]:
            self.assertEqual(E.join(E.basis(tuple(f)), E.FULL), E.FULL)

    def test_invalid_ambient_vector_is_rejected(self):
        for f in ((512,), (-1,), (0,), (True,)):
            with self.subTest(f=f), self.assertRaisesRegex(ValueError, "invalid F2"):
                E.basis(f)

    def test_parent_contract_diagnostic_is_precise(self):
        E.AUDIT.check_parent_interface(self.source, ROOT)
        with self.assertRaisesRegex(RuntimeError, "ordered centre frame interface"):
            E.AUDIT.check_parent_interface(self.word, ROOT)

    def test_exact_cut_collision_not_rank_heuristic(self):
        # Inverse certificate proves rank over the original all-column domain.
        for c in E.CENTERS:
            witness = E.cut_collision(self.word, c)
            self.assertEqual(witness["cut_difference"], {str(c): "1"})
            self.assertTrue(witness["all_other_cut_registers_equal"])

    def test_scalar_mutation_fails_independent_endpoint_audit(self):
        word = deepcopy(self.word)
        word["A"][4235][3] = -1
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"bad.json.gz"
            path.write_bytes(gzip.compress(E.encode(word), mtime=0))
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "endpoint failure"):
                E.AUDIT.run(path, Path(tmp)/"audit.json")

    def test_duplicate_early_cleanup_is_rejected_by_oracle(self):
        word = deepcopy(self.word)
        word["early_cleanup"].append(word["early_cleanup"][0])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"bad.json.gz"
            path.write_bytes(gzip.compress(E.encode(word), mtime=0))
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, "duplicate early cleanup"):
                E.AUDIT.run(path, Path(tmp)/"audit.json")


class PhysicalAccounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import gzip, json
        cls.source, cls.plan, _ = E.read_source()
        cls.word, _ = E.build_word(cls.source)
        path = ROOT / "research/gauge44-frames-x/data/OWNERS.json.gz"
        cls.owners = json.loads(gzip.decompress(path.read_bytes()))

    def test_occupied_cells_leave_same_idle(self):
        before = E.recount_idle(self.plan, self.owners, self.source)
        after = E.recount_idle(self.plan, self.owners, self.word)
        self.assertEqual(before, after)
        self.assertEqual(after, {1:1, 3:1, 44:1, 48:2396})
        E.validate_global(self.plan["profile"], E.OLD_PROFILE, before)

    def test_dropping_twelve_idle_children_cannot_pass_accounting(self):
        idle = E.recount_idle(self.plan, self.owners, self.word)
        actual = E.global_profile(E.NEW_PROFILE, idle)
        self.assertEqual(E.rank_mass(actual), 521280)
        self.assertEqual(73*7168-E.rank_mass(actual), 1984)
        self.assertEqual(E.rank_mass(actual)-E.rank_mass(E.ROADMAP_PROFILE), 576)
        with self.assertRaisesRegex(ValueError, "not supported"):
            E.validate_global(E.ROADMAP_PROFILE, E.NEW_PROFILE, idle)

    def test_missing_helper_role_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "all physical helper roles"):
            E.recount_idle(self.plan, self.owners[:-1], self.word)

    def test_changed_width_or_moved_time_is_rejected(self):
        for key in ("width", "time"):
            owners = deepcopy(self.owners)
            owners[0][key] += 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                E.recount_idle(self.plan, owners, self.word)


class ExactPricing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engines, cls.bit, _ = E.pricing_engines()

    def test_target_number_is_reproduced_as_profile_arithmetic(self):
        row = E.price(E.ROADMAP_PROFILE, self.engines, self.bit)
        self.assertEqual(Q(row["outer"]["kappa"]), E.ROADMAP_KAPPA)
        self.assertEqual(row["outer"]["strict_constraints_passed"], 47)
        self.assertEqual(len(row["outer"]["controls_rejected"]), 4)

    def test_actual_accounted_profile_has_its_own_price(self):
        row = E.price(E.global_profile(E.NEW_PROFILE, {1:1,3:1,44:1,48:2396}), self.engines, self.bit)
        self.assertEqual(row["outer"]["kappa_decimal"], "0.001297089685005627")
        self.assertEqual(row["deficit"], 1984)

    def test_stated_lower_endpoint_is_actually_above_root(self):
        candidate = Q("0.001674954374355989549644")
        for engine in self.engines[1:3]:
            if engine is self.engines[1]:
                lo, hi = engine.moment(E.ROADMAP_PROFILE, 73, 7168, candidate)
            else:
                lo, hi = engine.moment(73, 7168, list(E.ROADMAP_PROFILE.items()), candidate)
            self.assertGreater(lo, 1)
            self.assertGreater(hi, 1)

    def test_mass_and_capacity_scaling_preserve_moment(self):
        engine = self.engines[1]
        b = Q("0.001")
        lo, hi = engine.moment(E.ROADMAP_PROFILE, 73, 7168, b)
        large = {r: 3*n for r, n in E.ROADMAP_PROFILE.items()}
        self.assertEqual(engine.moment(large, 73, 3*7168, b), (lo, hi))

    def test_reported_mass_elasticity_has_correct_scale(self):
        engine = self.engines[1]
        root = engine.certify(E.ROADMAP_PROFILE, 73, 7168)["lower"]
        diagnostic = E.analysis(E.ROADMAP_PROFILE, root)
        self.assertGreater(float(diagnostic["relative_mass_elasticity"]), 203)
        self.assertLess(float(diagnostic["relative_mass_elasticity"]), 204)

    def test_direct_model_agrees_without_parent_interface(self):
        actual = E.global_profile(E.NEW_PROFILE, {1:1,3:1,44:1,48:2396})
        result = MODEL.evaluate(actual)
        self.assertEqual(result["outer"]["kappa_decimal"], "0.001297089685005627")
        self.assertEqual(result["deficit"], "1984")

    def test_capacity_price_with_actual_finite_difference(self):
        from decimal import Decimal, localcontext
        engine = self.engines[1]
        base = MODEL.certify(engine, E.ROADMAP_PROFILE, 73, Q(7168))
        expanded = MODEL.certify(engine, E.ROADMAP_PROFILE, 73, Q(7168)+Q(1,73))
        with localcontext() as ctx:
            ctx.prec = 60
            b0 = MODEL.decimal(Q(base["lower"])); b1 = MODEL.decimal(Q(expanded["lower"]))
            difference = b1/(1+b1)-b0/(1+b0)
            predicted = Decimal(E.analysis(E.ROADMAP_PROFILE, str(b0))["kappa_per_capacity_unit"])
            self.assertLess(abs(difference/predicted-1), Decimal("0.00001"))

    def test_range_reduced_engine_matches_retained_small_moment(self):
        engine = self.engines[1]
        self.assertEqual(MODEL.moment(engine, E.ROADMAP_PROFILE, 73, Q(7168), Q(".001")),
                         engine.moment(E.ROADMAP_PROFILE, 73, 7168, Q(".001")))

    def test_large_volume_root_is_arithmetic_outside_outer_domain(self):
        row = MODEL.evaluate(E.ROADMAP_PROFILE, live=Q(8192))
        self.assertGreater(Q(row["complex_root"]["lower"]), Q(1,32))
        self.assertIsNone(row["outer"])
        self.assertTrue(row["complex_root"]["strict_rational_signs"])

    def test_changed_scale_can_bind_on_bit_in_explicit_model(self):
        actual = E.global_profile(E.NEW_PROFILE, {1:1,3:1,44:1,48:2396})
        row = MODEL.evaluate(actual, m=74)
        self.assertEqual(row["outer"]["binding"], "bit")
        self.assertEqual(row["outer"]["strict_constraints_passed"], 47)

    def test_zero_deficit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "positive mass deficit"):
            MODEL.certify(self.engines[1], {1:73}, 73, Q(1))


class ScalarRetiming(unittest.TestCase):
    def test_commutation_criterion_against_exact_matrices(self):
        # Compare every matrix column independently of the symbolic criterion.
        gates = [["add", t, s, q.numerator, q.denominator]
                 for t in range(3) for s in range(3) if t != s
                 for q in (Q(-1), Q(0), Q(1,2), Q(1), Q(2))]
        gates += [["scale", r, q.numerator, q.denominator]
                  for r in range(3) for q in (Q(-1), Q(1,2), Q(1), Q(2))]

        def apply(g, v):
            result = v.copy()
            if g[0] == "add":
                result[g[1]] += Q(g[3], g[4])*v[g[2]]
            else:
                result[g[1]] *= Q(g[2], g[3])
            return result

        columns = [[Q(i == j) for i in range(3)] for j in range(3)]
        for a in gates:
            for b in gates:
                equal = all(apply(a, apply(b, v)) == apply(b, apply(a, v)) for v in columns)
                self.assertEqual(R.commute(a, b), equal, (a, b))

    def test_unsupported_or_noninvertible_primitives_are_rejected(self):
        for bad in (["add", 0, 0, 1, 1], ["scale", 0, 0, 1], ["swap", 0, 1]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                R.commute(bad, ["scale", 1, 1, 1])

    def test_pool_ignores_early_gates_but_respects_ordinary_prefix(self):
        word = dict(cleanup=[["add", 0, 1, 1, 1], ["add", 1, 2, 1, 1],
                             ["add", 3, 4, 1, 1], ["add", 2, 5, 1, 1]],
                    early_cleanup=[[0, [1]]])
        self.assertEqual(R.movable_pool(word), [1,2])

    def test_frame_repair_cannot_exceed_fixed_final_cap(self):
        word = dict(cleanup=[["add", 0, 1, 1, 1]])
        result = R.replay_tail(word, [(1,), (2,)], [(2,1), (2,)], [[0, [1]]], True)
        self.assertEqual(result["status"], "FINAL_FRAME_CAP")
        self.assertEqual(result["register"], 1)

    def test_minimal_frame_repair_and_exact_paid_mass(self):
        word = dict(cleanup=[["add", 0, 1, 1, 1]])
        cur, end = [(1,), (2,)], [(2,1), (2,1)]
        self.assertEqual(R.replay_tail(word, cur, end, [[0, [1]]], False)["status"], "NONMONOTONE")
        fixed = R.replay_tail(word, cur, end, [[0, [1]]], True)
        self.assertEqual(fixed["status"], "PASS")
        self.assertEqual(fixed["fitted"], [[0, [2,1]]])
        self.assertEqual(E.rank_mass(fixed["profile"]), sum(map(len,end))-sum(map(len,cur)))


class CompositionFailures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, _, _ = E.read_source()
        cls.promoted, _ = E.build_word(cls.source)
        cls.tri, cls.recipe, _ = OPT.source_inputs()

    def test_order_equality_includes_scalar_and_frame_data(self):
        u8, word = OPT.compose(self.source, self.promoted, self.tri, self.recipe)
        self.assertEqual(E.ints(word["report"]["local_profile"]), OPT.COMBINED_PROFILE)
        self.assertEqual(word["report"]["local_rank_mass"], self.promoted["report"]["local_rank_mass"])
        self.assertEqual(word["report"]["width_inventory"], u8["report"]["width_inventory"])
        self.assertEqual(word["A"], self.promoted["A"])
        self.assertEqual(word["B"], u8["B"])

    def test_corrupt_recipe_or_word_pin_is_rejected(self):
        bad = deepcopy(self.recipe)
        bad["base_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "U8 base word pin"):
            OPT.compose(self.source, self.promoted, self.tri, bad)
        bad = deepcopy(self.recipe)
        bad["expect_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError, "exact source pin"):
            OPT.compose(self.source, self.promoted, self.tri, bad)

    def test_modified_vendor_fails_before_module_execution(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            vendor = Path(tmp)/"vendor"
            shutil.copytree(OPT.VENDOR, vendor)
            with (vendor/"build_tri.py").open("a", encoding="utf-8") as f:
                f.write("\nraise AssertionError('must not execute unpinned code')\n")
            with self.assertRaisesRegex(ValueError, "vendored input SHA256"):
                OPT.source_inputs(vendor)

    def test_missing_pin_inventory_cannot_bypass_source_check(self):
        import json, shutil
        with tempfile.TemporaryDirectory() as tmp:
            vendor = Path(tmp)/"vendor"
            shutil.copytree(OPT.VENDOR, vendor)
            metadata = json.loads((vendor/"SOURCE.json").read_bytes())
            metadata["files"] = []
            E.dump(vendor/"SOURCE.json", metadata)
            with self.assertRaisesRegex(ValueError, "pinned source inventory"):
                OPT.source_inputs(vendor)

    def test_missing_restore_fails_combined_independent_endpoint_audit(self):
        word = self.tri.apply(self.promoted, self.recipe, "drop_restore@231")
        E.refresh_report(word)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "all-column endpoint failure"):
                OPT.audit_word(word, Path(tmp)/"bad.json.gz", Path(tmp)/"audit.json")


class ReproductionBindings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.modules["cost_model"] = MODEL
        sys.modules["optimizations"] = OPT
        cls.verifier = E.load_module(ROOT / "research/roadmap48/verify.py", "roadmap_release_verifier")

    def test_gzip_recompression_preserves_semantic_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.json.gz", Path(tmp)/"b.json.gz"
            a.write_bytes(gzip.compress(b'{"profile":{"1":7}}', compresslevel=1, mtime=17))
            b.write_bytes(gzip.compress(b'{"profile":{"1":7}}', compresslevel=9, mtime=99))
            self.assertNotEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(self.verifier.content_hash(a), self.verifier.content_hash(b))
            b.write_bytes(gzip.compress(b'{"profile":{"1":8}}', mtime=99))
            self.assertNotEqual(self.verifier.content_hash(a), self.verifier.content_hash(b))

    def test_changed_retained_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            committed = Path(tmp)
            E.dump(committed/"result.json", {"kappa": "1/10"})
            receipt = dict(sources={"source.py":"pinned"}, immutable_inputs={},
                           artifacts={"result.json":self.verifier.content_hash(committed/"result.json")})
            for key in ("status", "local_audit", "tests", "actual_kappa", "combined_kappa",
                        "hypothetical_kappa", "output_content_sha256", "artifact_hash_policy", "source_hash_policy"):
                receipt[key] = "original"
            E.dump(committed/"VERIFICATION.json", receipt)
            self.verifier.check_committed(receipt, committed)
            E.dump(committed/"result.json", {"kappa":"1/9"})
            with self.assertRaisesRegex(ValueError, "committed payload changed"):
                self.verifier.check_committed(receipt, committed)


if __name__ == "__main__":
    unittest.main()
