"""Exact arithmetic, rank-one laws, witnesses and package failure controls.

@Scratch-net with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT)


def load(name):
    spec = importlib.util.spec_from_file_location("r480_center_test_" + name, HERE / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class PackageTests(unittest.TestCase):
    def test_local_adjoint_and_rank_one_laws(self):
        v = load("verify")
        # COPY and CLEAR are singular: pulling a COPY back as a swap is wrong.
        copy = [(0, "copy", 0, 1, Q(1))]
        matrix = v.pullback(copy)
        self.assertEqual(matrix[0], {})
        self.assertEqual(matrix[1], {0: Q(1), 1: Q(1)})
        circuits = [
            [(0, "add", 0, 1, Q(-3, 8)), (1, "clear", 0, None, Q(1)),
             (2, "add", 1, 0, Q(2))],
            [(0, "copy", 0, 1, Q(1)), (1, "scale", 0, None, Q(-2)),
             (2, "copy", 1, 0, Q(1))],
            [(0, "clear", 0, None, Q(1)), (1, "copy", 0, 1, Q(1)),
             (2, "clear", 0, None, Q(1))],
        ]
        for ops in circuits:
            baseline = v.pullback(ops)
            for position, (index, kind, target, source, _) in enumerate(ops):
                if kind not in ("clear", "copy"):
                    continue
                u = v.evaluate(ops[position + 1:], {target: Q(1)})
                f = {target: Q(1)} if kind == "clear" else {target: Q(1), source: Q(-1)}
                sensitivity = v.prefix_functional(ops[:position], f)
                factor = [{out: coef * sensitivity[i] for out, coef in u.items()}
                          if i in sensitivity else {} for i in range(v.SIZE)]
                self.assertEqual(v.delta(v.pullback(ops, index), baseline), factor)

    def test_integer_dyadic_arithmetic(self):
        f = load("forward_check")
        rng = random.Random(80)
        for _ in range(2000):
            left = f.normalize({i: rng.randint(-32, 32) for i in range(5)}, rng.randrange(28))
            right = f.normalize({i: rng.randint(-32, 32) for i in range(5)}, rng.randrange(28))
            left = ({i: n for i, n in left[0].items() if n}, left[1])
            right = ({i: n for i, n in right[0].items() if n}, right[1])
            n, d = rng.choice((-7, -3, -1, 1, 3, 7)), rng.randrange(8)
            actual = f.sum_rows(left, f.multiply(right, n, d))
            expected = {i: Q(left[0].get(i, 0), 1 << left[1]) +
                        Q(right[0].get(i, 0) * n, 1 << (right[1] + d)) for i in range(5)}
            self.assertEqual({i: Q(value, 1 << actual[1]) for i, value in actual[0].items()},
                             {i: value for i, value in expected.items() if value})

    def test_all_private_only_basis_witnesses(self):
        v = load("verify")
        _, programs = v.sources()
        certificate = v.read(HERE / "CERTIFICATE.json")
        ops = v.operations(programs["backward"])
        covered = []
        for fault in certificate["programs"]["backward"]["faults"]:
            if fault["classification"] != "private_input_only":
                continue
            c = v.PERSISTENT + fault["center"]
            self.assertEqual(fault["sensitivity"], [[c, "1"]])
            self.assertFalse(fault["ordinary_inputs_detect"])
            self.assertEqual(v.evaluate(ops, {c: Q(1)}), {})
            actual = v.evaluate(ops, {c: Q(1)}, fault["event_index"])
            self.assertEqual(v.vector(actual), fault["witness"]["output_difference"])
            self.assertEqual(len(actual), [111, 106, 110, 107, 104, 105, 103, 106][fault["center"]])
            self.assertTrue(all(output < v.PERSISTENT for output in actual))
            covered.append(fault["center"])
        self.assertEqual(covered, list(range(8)))

    def test_minimal_optimized_relocation_and_corruption(self):
        v = load("verify")
        pins = v.read(HERE / "SOURCE-PINS.json")
        with tempfile.TemporaryDirectory(prefix="r480 center audit ") as tmp:
            target = Path(tmp)
            for path in HERE.iterdir():
                if path.is_file():
                    dst = target / REL / path.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(path, dst)
            for name in pins["files"]:
                dst = target / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, dst)

            def run(script):
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / REL / script)],
                                      cwd=target, text=True, capture_output=True, timeout=240)

            result = run("check.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("private_only=8", result.stdout)
            cert_path = target / REL / "CERTIFICATE.json"
            original = cert_path.read_text()
            for mutate in (
                lambda x: x["programs"]["backward"]["faults"][0].__setitem__("defect_rank", 0),
                lambda x: x["programs"]["backward"]["faults"][0]["response"][0].__setitem__(1, "99"),
                lambda x: x["programs"]["forward"]["faults"].pop(),
                lambda x: x["programs"].pop("backward"),
            ):
                data = json.loads(original)
                mutate(data)
                cert_path.write_text(json.dumps(data))
                bad = run("forward_check.py")
                self.assertNotEqual(bad.returncode, 0)
                self.assertIn("ValueError", bad.stderr)
            cert_path.write_text(original)
            archive = target / v.ARCHIVE
            archive.write_bytes(archive.read_bytes() + b"deliberate source mutation")
            bad = run("check.py")
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("source pin differs", bad.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
