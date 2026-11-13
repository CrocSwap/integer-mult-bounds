"""Verify the stronger R262 exact separator against the retained product."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import alarm
import sys

PIN = "40b51b7a7c980fccafb349f7c76f41fb8ee53b131980ee1317ac908d6bf87c20"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--word", required=True, type=Path)
parser.add_argument("--probe", required=True, type=Path)
args = parser.parse_args()
alarm(30)
source = Path(__file__).resolve().parent.parent / "product35452_forward.py"
assert sha256(source.read_bytes()).hexdigest() == PIN
probe = json.loads(args.probe.read_bytes())
assert set(probe) == {"883", "368", "88", "80", "67", "34", "26", "8"}
sys.argv = [str(source), "--word", str(args.word), "--probe", str(args.probe)]
# The underlying verifier checks bank annihilation, source and exact
# return/control. This wrapper adds the exact zero-product decision.
from contextlib import redirect_stdout
from io import StringIO
stdout = StringIO()
with redirect_stdout(stdout):
    run_path(str(source), run_name="__main__")
receipt = json.loads(stdout.getvalue())
assert F(receipt["old_source_1137"]) == -F(1, 2)
assert F(receipt["old_product_1545"]) == 0
assert F(receipt["old_return_1544"]) == -F(1, 2)
assert F(receipt["control_drop_ADD34379"]["return_1544"]) == 0
receipt["status"] = "PASS_BANK_AND_RETAINED_PRODUCT_SEPARATOR"
receipt["underlying_verifier_sha256"] = PIN
receipt["probe_sha256"] = sha256(args.probe.read_bytes()).hexdigest()
print(json.dumps(receipt, sort_keys=True, indent=2))
