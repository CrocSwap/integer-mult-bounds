#!/usr/bin/env python3
"""Independent depth oracle and public-CLI failure controls."""

from array import array
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SPEC = importlib.util.spec_from_file_location("stock_fit", PACKAGE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix="stock-fit-") as directory:
        root = Path(directory)
        package = root / "research" / PACKAGE.name
        package.mkdir(parents=True)
        for name in ("verify.py", "SOURCES.json", "RESULT.json"):
            shutil.copyfile(PACKAGE / name, package / name)
        for name in VERIFY.INPUTS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        yield root, package


def cli(package, optimized=False, extra=()):
    command = [sys.executable, "-I", "-B", "-Werror"]
    if optimized:
        command.append("-O")
    command.extend([str(package / "verify.py"), *extra])
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    return subprocess.run(command, cwd=package, env=env, capture_output=True,
                          text=True, timeout=30, check=False)


class StockFitTests(unittest.TestCase):
    def test_public_success_normal_and_optimized(self):
        with fixture() as (_, package):
            for optimized in (False, True):
                result = cli(package, optimized)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(),
                                 "PASS_SELECTED_BIT_STOCK_FIT uniform_cutoff=311305 "
                                 "failure=311304 no_new_kappa")

    def test_independent_all_child_depth_oracle(self):
        # Bottom-up all-rank DP, independent of the inverse-threshold generator.
        ranks = (1, 2, 3, 4, 5, 6, 7, 42)
        dp = array("B", [0]) * (VERIFY.TAIL + 1)
        thresholds = VERIFY.thresholds()
        index = 0
        for n in range(VERIFY.TAIL + 1):
            if n >= 64:
                f = n // 64
                dp[n] = 1 + max(dp[r * f] for r in ranks)
            if index < len(thresholds) and n >= thresholds[index]:
                index += 1
            if dp[n] != index:
                self.fail(f"independent depth mismatch at {n}")
        self.assertEqual((dp[63], dp[64], dp[311304], dp[405312], dp[-1]),
                         (0, 1, 19, 20, 22))
        for threshold in thresholds:
            for n in (threshold - 1, threshold):
                self.assertEqual(VERIFY.depth(n), sum(b <= n for b in thresholds))

    def test_strict_half_width_boundary(self):
        rows = VERIFY.staircase(311305)["intervals"]
        self.assertEqual(rows[0], {"depth": 19, "first": 311305, "last": 405311,
                                   "k_upper": 155652})
        self.assertEqual(rows[-1]["last"], 1048575)
        with self.assertRaisesRegex(ValueError, "strict fit"):
            VERIFY.staircase(311304)
        self.assertEqual(VERIFY.sharpness()["k"], 155652)
        self.assertEqual(VERIFY.sharpness()["failing_width"], 311304)

    def test_sharpness_against_full_exact_gl_product(self):
        failure = VERIFY.sharpness()
        q = int(failure["q"])
        numerator = 28425
        for i in range(1, 65):
            numerator *= q**i - 1
        # Strip the known integral q-power, but retain all 64 exact GL factors.
        # This does not use the production certificate's Bernoulli relaxation.
        actual = numerator**19
        offset = failure["k"] - 8192 * 19
        lower = q**(2080 * 19 + offset - 1)
        upper = lower * q
        self.assertEqual((offset, lower < actual, actual < upper), (4, True, True))

    def test_prime_certificate_and_composite_control(self):
        self.assertEqual(VERIFY.proth_prime(), 4533471823554859405148161)
        with self.assertRaisesRegex(ValueError, "prime (Fermat|order) condition"):
            VERIFY.proth_prime(k=1, exponent=81, witness=11)
        with self.assertRaisesRegex(ValueError, "insufficient known"):
            VERIFY.proth_prime(k=15, exponent=1, witness=11)
        with self.assertRaisesRegex(ValueError, "types"):
            VERIFY.proth_prime(k=True)

    def test_source_bound_producer_and_exponent_controls(self):
        data, pin = VERIFY.load_sources()
        assembler = VERIFY.assembler_bytes(ROOT, pin)
        actual = VERIFY.selected_parameters(data, assembler)
        self.assertEqual(set(actual), {"native", "conservative"})
        expected = json.loads(data[VERIFY.INPUTS[2]])
        expected["nine"]["bit"]["physical"] = 28416
        altered = dict(data)
        altered[VERIFY.INPUTS[2]] = json.dumps(expected).encode()
        # Rebind the citation in this in-memory adversarial model, so the
        # physical-packet condition, not just a hash, must reject it.
        raw = altered[VERIFY.INPUTS[2]]
        assembly = json.loads(data[VERIFY.INPUTS[1]])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        assembly["bit_supplier"]["git_blob_sha1"] = VERIFY.hashlib.sha1(blob).hexdigest()
        altered[VERIFY.INPUTS[1]] = json.dumps(assembly).encode()
        selected = json.loads(data[VERIFY.INPUTS[0]])
        selected["certificate_sha256"] = VERIFY.hashlib.sha256(altered[VERIFY.INPUTS[1]]).hexdigest()
        altered[VERIFY.INPUTS[0]] = json.dumps(selected).encode()
        with self.assertRaisesRegex(ValueError, "physical packet"):
            VERIFY.selected_parameters(altered, assembler)
        high_data = dict(data)
        assembly = json.loads(data[VERIFY.INPUTS[1]])
        for key in ("bit_lower", "complex_lower", "conservative_complex_lower"):
            assembly[key] = "3/1000"
        high_data[VERIFY.INPUTS[1]] = json.dumps(assembly).encode()
        selected = json.loads(data[VERIFY.INPUTS[0]])
        selected["certificate_sha256"] = VERIFY.hashlib.sha256(high_data[VERIFY.INPUTS[1]]).hexdigest()
        high_data[VERIFY.INPUTS[0]] = json.dumps(selected).encode()
        with self.assertRaisesRegex(ValueError, "atom exponent outside proved domain"):
            VERIFY.selected_parameters(high_data, assembler)
        # Direct formula mutation is checked separately from source integrity.
        with self.assertRaisesRegex(ValueError, "atom exponent formula"):
            VERIFY.selected_parameters(data, assembler.replace("s=min(c,", "s=max(c,"))

    def test_every_live_source_corruption_fails_cli(self):
        for name in VERIFY.INPUTS:
            with self.subTest(source=name), fixture() as (root, package):
                path = root / name
                with path.open("ab") as stream:
                    stream.write(b"\n")
                result = cli(package, optimized=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source SHA256", result.stderr)

    def test_required_result_missing_tampered_and_type_drift(self):
        for mode in ("missing", "number", "type"):
            with self.subTest(mode=mode), fixture() as (_, package):
                path = package / "RESULT.json"
                if mode == "missing":
                    path.unlink()
                else:
                    result = json.loads(path.read_text(encoding="utf-8"))
                    result["uniform_cutoff"] = 311304 if mode == "number" else True
                    path.write_text(json.dumps(result), encoding="utf-8")
                run = cli(package, optimized=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("FAIL_SELECTED_BIT_STOCK_FIT", run.stderr)

    def test_explicit_regeneration_never_overwrites(self):
        with fixture() as (_, package):
            path = package / "external.json"
            first = cli(package, extra=("--write-result", str(path)))
            self.assertEqual(first.returncode, 0, first.stderr)
            payload = path.read_bytes()
            self.assertEqual(json.loads(payload)["uniform_cutoff"], 311305)
            second = cli(package, extra=("--write-result", str(path)))
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(path.read_bytes(), payload)

    def test_depth_domain_controls(self):
        self.assertEqual(VERIFY.depth((1 << 1023) - 1), 1672)
        for invalid in (-1, True, 1 << 1024):
            with self.subTest(invalid=str(invalid)[:20]):
                with self.assertRaisesRegex(ValueError, "depth domain"):
                    VERIFY.depth(invalid)


if __name__ == "__main__":
    unittest.main()
