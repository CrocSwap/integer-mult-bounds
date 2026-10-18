"""Public artifact checks and a separate exact physical convolution control."""

import json
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PASS = ("PASS_QQ16_ENTRY_FRAME_TARIFF ports=112 entry_mass=3696 F0_mass=1904 "
        "decoder_plus_entry_mass=4048 controls=6 no_new_kappa\n")


def multiply(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def gaussian_power(value, exponent):
    result = (1, 0)
    for _ in range(exponent):
        result = multiply(result, value)
    return result


def run(package, repo, *args):
    return subprocess.run(
        [sys.executable, "-I", "-B", "-W", "error", str(package / "verify.py"),
         "--repo", str(repo), *args], capture_output=True, text=True, timeout=20,
        check=False,
    )


class ArtifactTests(unittest.TestCase):
    def test_read_only_replay(self):
        before = {str(p.relative_to(HERE)): p.read_bytes()
                  for p in HERE.rglob("*") if p.is_file()}
        result = run(HERE, REPO)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PASS)
        after = {str(p.relative_to(HERE)): p.read_bytes()
                 for p in HERE.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_write_refuses_overwrite(self):
        before = (HERE / "RESULT.json").read_bytes()
        result = run(HERE, REPO, "--write")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FileExistsError", result.stderr)
        self.assertEqual((HERE / "RESULT.json").read_bytes(), before)

    def test_source_and_result_corruption(self):
        cases = (("RESULT.json", "committed result differs"),
                 ("sources/PR2540-PROOF.md", "decoder source pin"))
        for filename, message in cases:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as tmp:
                package = Path(tmp) / "package"
                shutil.copytree(HERE, package)
                target = package / filename
                if filename == "RESULT.json":
                    result = json.loads(target.read_text())
                    result["adapters"][0]["translation_after"] ^= 1
                    target.write_text(json.dumps(result))
                else:
                    target.write_bytes(target.read_bytes() + b"\nchanged\n")
                result = run(package, REPO)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_live_source_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            target = repo / "research/joint-query/evidence/BRIDGE-REVIEW.md"
            target.parent.mkdir(parents=True)
            target.write_text("changed entry contract")
            result = run(HERE, repo)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("live source pin", result.stderr)

    def test_relocated_without_git_and_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            package = repo / "research/qq16-entry-frame-tariff"
            shutil.copytree(HERE, package)
            pins = json.loads((HERE / "SOURCES.json").read_text())
            for row in pins["files"]:
                if row["usage"] == "input":
                    target = repo / row["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(REPO / row["path"], target)
            result = run(package, repo)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, PASS)
            for filename in ("verify.py", "test_verify.py"):
                compiled = py_compile.compile(
                    str(package / filename), cfile=str(repo / (filename + "c")),
                    doraise=True,
                )
                self.assertTrue(Path(compiled).is_file())

    def test_full_first_port_physical_kernel(self):
        # Compare every coefficient of C_11 F_U1^-1 to the generated native
        # adapter. Denominators are 2^18 and 2^16 respectively. This does not
        # import the phase checker or use its 154 determining characters.
        result = json.loads((HERE / "RESULT.json").read_text())
        word = next(row for row in result["adapters"]
                    if row["port"] == 0 and row["boundary_field"] == "entry_X")
        axes = word["positive_child_axes"]
        inverse = [multiply(gaussian_power((1, -1), 17 - w),
                            gaussian_power((1, 1), w)) for w in range(18)]
        positive = [multiply(gaussian_power((1, 1), 16 - w),
                             gaussian_power((1, -1), w)) for w in range(17)]
        nonzero = 0
        for address in range(2**17):
            left = multiply((1, 1), inverse[address.bit_count()])
            right = multiply((1, -1), inverse[(address ^ 11).bit_count()])
            expected = (left[0] + right[0], left[1] + right[1])
            shifted = address ^ word["translation_after"]
            actual = (0, 0)
            if (shifted & 11).bit_count() % 2 == 0:
                weight = sum((shifted & axis).bit_count() % 2 for axis in axes)
                coefficient = positive[weight]
                actual = (4 * coefficient[0], 4 * coefficient[1])
                nonzero += 1
            self.assertEqual(actual, expected, f"address {address}")
        self.assertEqual(nonzero, 65536)


if __name__ == "__main__":
    unittest.main()
