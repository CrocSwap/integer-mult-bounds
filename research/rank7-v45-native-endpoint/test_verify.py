# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the native/covector research check."""

import copy
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load(name):
    module = types.ModuleType(name)
    module.__file__ = str(PACKAGE / (name + ".py"))
    exec(
        compile(Path(module.__file__).read_bytes(), module.__file__, "exec"),
        module.__dict__,
    )
    return module


V = load("verify")
E = load("endpoints")


def word(tag="base"):
    raw = (ROOT / (V.WORD_PREFIX + tag + ".json.gz")).read_bytes()
    return json.loads(gzip.decompress(raw))


def cli(path, *args):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-Werror", "-B", str(path), *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


class NativeEndpointTests(unittest.TestCase):
    def test_actual_cli_and_receipt(self):
        result = cli(PACKAGE / "verify.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "PASS_RANK7_V45_NATIVE_ENDPOINT helper=249 "
            "private=953 providers=2 columns=512 no_new_kappa\n",
        )
        emitted = cli(PACKAGE / "verify.py", "--emit")
        self.assertEqual(emitted.returncode, 0, emitted.stderr)
        payload = json.loads(emitted.stdout)
        self.assertEqual(
            [r["rank"] for r in payload["native_recipes"]], [1, 1, 1, 1, 2, 1, 7]
        )
        self.assertEqual(
            payload["providers"]["base"]["normalized_endpoint"]["gates"], 17575
        )
        self.assertEqual(payload, json.loads((PACKAGE / "RESULT.json").read_text()))

    def test_noncommuting_covector_order(self):
        gates = [
            ["add", 0, 1, 2, 1],
            ["warp", 0, 1],
            ["warp", 0, 2],
            ["corr", 2, 0, 3, 1, [3, -1]],
        ]
        self.assertEqual(
            E.endpoint(gates, 2, False, {0, 1, 2}, set()),
            [(0, (3, -1, 2, 1), "3"), (1, (3, -1, 2, 1), "6"), (2, (), "1")],
        )
        self.assertEqual(E.append_word((1, 2), (-2, -1, 3)), (3,))
        self.assertEqual(
            E.endpoint([["corr", 2, 0, 3, 1, [1, 2]]], 0, True, {0, 2}, set()),
            [(0, (), "1"), (2, (-1000002, -1000001), "-3")],
        )

    def test_dyadic_scaling_and_input_failures(self):
        gates = [["scale", 0, 3, 2], ["add", 1, 0, 2, 1]]
        self.assertEqual(
            E.endpoint(gates, 1, False, {0, 1}, set()), [(0, (), "3"), (1, (), "1")]
        )
        self.assertEqual(
            E.endpoint(gates, 0, True, {0, 1}, set()), [(0, (), "2/3"), (1, (), "-2")]
        )
        with self.assertRaisesRegex(ValueError, "nonzero scale"):
            E.pull_gate([{(): Fraction(1)}], ["scale", 0, 0, 1], False)
        with self.assertRaisesRegex(ValueError, "operator word bound"):
            E.append_word((1,) * 64, (2,))
        with self.assertRaisesRegex(ValueError, "legal register"):
            E.endpoint([["add", 0, 3, 1, 1]], 0, False, {0}, set())

    def test_actual_endpoints_and_omitted_cleanup(self):
        for tag in ("base", "extra"):
            actual = word(tag)
            result = E.check(actual)
            expected = {
                "helper_full_input_terms": [(249, (), "1")],
                "private_full_input_terms": [(953, (), "1")],
            }
            self.assertEqual(result["endpoints"]["forward"], expected)
            self.assertEqual(result["endpoints"]["inverse_transpose"], expected)
            control = E.omission_control(actual)
            self.assertEqual(control["private_original_input_terms"]["forward"], [])
            self.assertIn(
                (11, (), "-1/2"),
                control["private_original_input_terms"]["inverse_transpose"],
            )
            broken = copy.deepcopy(actual)
            del broken["cleanup"][72]
            with self.assertRaisesRegex(ValueError, "endpoint"):
                E.check(broken)

    def test_actual_frame_paths_and_changed_end(self):
        path = V.helper_path(word())
        self.assertEqual(
            [(p["section"], p["index"]) for p in path],
            [
                ("A", 2036),
                ("A", 2046),
                ("B", 459),
                ("B", 461),
                ("B", 470),
                ("restore", 124),
            ],
        )
        broken = word()
        broken["helper_final"]["249"] = [256, 128, 64, 32, 16, 8, 4]
        with self.assertRaisesRegex(ValueError, "V45 endpoint"):
            V.helper_path(broken)
        broken = word()
        broken["A"][2036][-1] = [1]
        with self.assertRaisesRegex(ValueError, "monotone helper frame"):
            V.helper_path(broken)

    def test_native_dual_is_not_adjoint(self):
        raw = V.inputs()
        kernel = V.load_source(raw[V.KERNEL], "independent_kernel")
        circuit = kernel.canonical_frame(V.W)
        self.assertTrue(
            kernel.same_operator(
                V.inverse_transpose(kernel.fourier(1)), kernel.fourier(1, -1)
            )
        )
        self.assertFalse(
            kernel.same_operator(V.inverse_transpose(circuit), kernel.adjoint(circuit))
        )
        compiler = V.load_source(raw[V.COMPILER], "native_compiler")
        record = V.native_identity(compiler, kernel, [], V.W)
        self.assertEqual(record["rank"], 7)
        self.assertEqual(record["recipe"]["right"]["phase"], 2)

    def test_git_free_export_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix="v45-export-") as temporary:
            root = Path(temporary)
            exported = root / "research" / PACKAGE.name
            shutil.copytree(
                PACKAGE, exported, ignore=shutil.ignore_patterns("__pycache__")
            )
            for name in sorted(V.INPUTS):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            result = cli(exported / "verify.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            (root / V.COMPILER).write_text("raise RuntimeError('must not execute')\n")
            result = cli(exported / "verify.py")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input SHA256", result.stderr)
            self.assertNotIn("RuntimeError", result.stderr)

    def test_duplicate_json_and_boolean_frame(self):
        self.assertEqual(V.read_json('{"sample":7}'), {"sample": 7})
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            V.read_json('{"sample":7,"sample":8}')
        self.assertEqual(V.span([1, 2]), {0, 1, 2, 3})
        with self.assertRaisesRegex(ValueError, "independent frame generator"):
            V.span([True])


if __name__ == "__main__":
    unittest.main()
