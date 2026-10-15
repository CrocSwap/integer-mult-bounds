"""Focused mathematical and fail-closed tests for this package (Apache-2.0)."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("intervention_check", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class InterventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        packet, members, _ = v.load_sources(v.ROOT)
        cls.model = v.Model(packet, members[v.PHASES])
        cls.template = members[v.TEMPLATE]

    def test_factored_backward_matches_literal_rows(self):
        # Nonconstant owner functions exercise ordered routes, including
        # products with the future chart. This is a regression, not a census.
        x = [{1 << (p % 73): v.Q((p % 5) - 2), 0: v.Q(1, 2)} for p in range(112)]
        y = [{1 << ((p + 9) % 73): v.Q((p % 7) - 3), 0: v.Q(-2)} for p in range(112)]
        for stage, future in ((1, 2), (2, 8)):
            with self.subTest(stage=stage, future=future):
                m = self.model
                ua = m.inject(future, v.A, m.query(future, y))
                u = [ua[p] if p in v.A else y[p] for p in range(112)]
                a, b = m.query(stage, x, v.T), m.query(stage, u)
                response = m.inject(stage, v.U, a)
                xt = m.inject(stage, v.T, [v.linear((1, b[k]), (12, a[k])) for k in range(8)])
                yt_sub = m.inject(stage, v.T, [v.linear((1, b[k]), (11, a[k])) for k in range(8)])
                xx, yy = v.zero_ports(), v.zero_ports()
                for p in v.U:
                    xx[p] = v.linear((1, x[p]), (-1, y[p]))
                    yy[p] = v.linear((1, y[p]), (1, response[p]))
                for p in v.A:
                    xx[p] = v.linear((1, x[p]), (1, y[p]), (-1, u[p]))
                    yy[p] = u[p]
                for p in v.T:
                    xx[p], yy[p] = xt[p], v.linear((1, u[p]), (-1, yt_sub[p]))
                self.assertEqual(m.backward(stage, future, x, y), [xx, yy])

    def test_nonlinear_fixture_is_reversible_and_keeps_dirty_helper(self):
        banks = v.zero_banks()
        helper = {0: v.Q(3), 37: v.Q(-2)}
        for j, p in enumerate(v.A):
            banks[0][0][p] = {0: v.Q(j + 1), 38: v.Q(-1)}
        before = deepcopy(banks)
        helper_before = deepcopy(helper)
        v.intervention(banks, helper, "nonlinear", 2)
        self.assertNotEqual(banks, before)
        self.assertEqual(helper, helper_before)
        for j, (a, t) in enumerate(zip(v.A, v.T)):
            x, y = banks[0]
            amount = v.linear((1, v.multiply(x[a], x[a])), (j + 3, helper))
            x[t] = v.linear((1, x[t]), (-1, amount))
            y[t] = v.linear((1, y[t]), (1, amount))
        self.assertEqual(banks, before)
        self.assertEqual(v.multiply({37: v.Q(1)}, {37: v.Q(1)}), {0: v.Q(1)})

    def test_wrong_pair_requires_source_binding_not_zero_witness(self):
        initial, _ = v.witness(self.model)
        wrong = deepcopy(self.template)
        wrong["recipe"][3]["pair"] = 1
        correct = v.replay(self.model, self.template["recipe"], initial)[1]
        self.assertEqual(v.replay(self.model, wrong["recipe"], initial)[1], correct)
        with self.assertRaisesRegex(ValueError, "schedule/pair binding"):
            v.bind_schedule(wrong)

    def test_ordinary_read_crosses_the_observation_boundary(self):
        initial, _ = v.witness(self.model)
        state, _ = self.model.forward(0, *initial[0])
        banks = v.zero_banks()
        banks[0] = state
        v.intervention(banks, {}, "pr2216", 0)
        self.assertFalse(any(banks[0][0][p] for p in v.S))
        v.intervention(banks, {}, "ordinary_read", 0)
        self.assertTrue(any(v.at_identity(banks[0][0][p]) for p in v.T))

    def test_mutated_source_rejected_by_optimized_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = json.loads((HERE / "SOURCES.json").read_text())
            for entry in manifest["files"]:
                if entry["usage"] != "input":
                    continue
                path = root / entry["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                if entry["path"] == v.PACKET:
                    path.write_bytes((v.ROOT / v.PACKET).read_bytes() + b"changed")
                else:
                    path.symlink_to(v.ROOT / entry["path"])
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--root", str(root)], capture_output=True, text=True, timeout=60)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source digest mismatch", result.stderr)
            self.assertNotIn(v.MARKER, result.stdout)

    def test_changed_receipt_rejected_by_optimized_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "research" / "package"
            shutil.copytree(HERE, package)
            result_path = package / "RESULT.json"
            result = json.loads(result_path.read_text())
            result["witness"]["initial_X_A_at_identity"] = ["0"] * 8
            result_path.write_text(json.dumps(result))
            replay = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                     "--root", str(v.ROOT)], capture_output=True, text=True, timeout=60)
            self.assertNotEqual(replay.returncode, 0)
            self.assertIn("complete result mismatch", replay.stderr)
            self.assertNotIn(v.MARKER, replay.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
