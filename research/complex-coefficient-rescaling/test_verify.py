"""Focused adversarial tests; run with Python's standard-library unittest."""

import copy
import gzip
import itertools
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify
from crosscheck import crosscheck
from lowering import WORK, lower_block, plans


def stream(coefficients):
    events = [["phase", "full_frame_cleanup"]]
    for target, q in enumerate(coefficients, 1):
        q = Fraction(q)
        events.append(["scalar", ["add", ["L", target], ["L", 0], q.numerator, q.denominator], 1])
    return events + [["phase", "done"]]


class RescalingTests(unittest.TestCase):
    def test_exhaustive_small_signed_domain(self):
        # Includes different odd families and both profitable and losing shifts.
        domain = [Fraction(1, 8), Fraction(-1, 2), Fraction(3, 2),
                  Fraction(-3), Fraction(2), Fraction(-8), Fraction(16)]
        for coefficients in itertools.product(domain, repeat=3):
            events = stream(coefficients)
            crosscheck(events, plans(events, "rescale"), lower_block)

    def test_exact_but_unprofitable_shift(self):
        events = stream([16, Fraction(1, 2)])
        self.assertEqual(plans(events, "rescale"), [])
        result = crosscheck(events, [], lower_block)
        self.assertEqual(result["nonpositive_transition_census"][0]["extra_real_primitives_if_merged"], 2)

    def test_equal_cost_tie_keeps_work_lifetime_short(self):
        events = stream([8, Fraction(1, 2)])
        self.assertEqual(plans(events, "rescale"), [])
        crosscheck(events, [], lower_block)

    def test_missing_profitable_block_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "dynamic-programming optimum"):
            crosscheck(stream([Fraction(3, 2), 3]), [], lower_block)

    def test_endpoint_neutral_extra_work_is_rejected(self):
        events = stream([Fraction(3, 2), 3])
        def redundant(block):
            return lower_block(block) + [("clear", WORK)]
        with self.assertRaisesRegex(ValueError, "independent cost"):
            crosscheck(events, plans(events, "rescale"), redundant)

    def test_early_ended_register_is_rejected(self):
        native, programs, _ = verify.load_inputs()
        events = programs["forward"]
        spans = plans(events, "rescale")
        native = copy.deepcopy(native)
        native["final"][events[spans[0][0]][1][2][1]] = 0
        with self.assertRaisesRegex(ValueError, "early-ended"):
            verify.replay(events, native, spans, "forward")

    def test_all_mathematical_controls(self):
        self.assertEqual(len(verify.negative_controls()), 11)

    def test_relocated_inputs_recompression_and_corruption(self):
        pins = json.loads((HERE / "SOURCE-PINS.json").read_text())
        with tempfile.TemporaryDirectory(prefix="rescaling space ") as directory:
            root = Path(directory)
            for name in pins["files"]:
                source, destination = verify.ROOT / name, root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                payload = source.read_bytes()
                if name.endswith(".gz"):
                    payload = gzip.compress(gzip.decompress(payload), compresslevel=1, mtime=123)
                destination.write_bytes(payload)
            with patch.object(verify, "ROOT", root):
                verify.load_inputs()
                target = root / verify.PROVIDER / "LOCAL-PROGRAMS.json.gz"
                programs = json.loads(gzip.decompress(target.read_bytes()))
                programs["forward"].pop()
                target.write_bytes(gzip.compress(json.dumps(programs).encode()))
                with self.assertRaisesRegex(ValueError, "source payload changed"):
                    verify.load_inputs()

    def test_corrupt_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            here = Path(directory)
            for name in ("verify.py", "lowering.py", "crosscheck.py", "SOURCE-PINS.json"):
                (here / name).write_bytes((HERE / name).read_bytes())
            receipt = json.loads((HERE / "EXPECTED.json").read_text())
            receipt["orientations"]["forward"]["incremental_real_saving"] -= 1
            (here / "EXPECTED.json").write_text(json.dumps(receipt))
            # The public entry point still runs all checks before the comparison.
            code = ("import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
                    "import verify; verify.ROOT=Path(sys.argv[2]); sys.argv=[sys.argv[0]]; verify.main()")
            run = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(here), str(verify.ROOT)],
                                 capture_output=True, text=True, check=False)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("committed receipt mismatch", run.stderr)


if __name__ == "__main__":
    unittest.main()
