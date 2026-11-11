"""Read-only replay of the fixed-catalogue joint BIT descent bound."""
import contextlib
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
sys.path.insert(0, str(HERE))
import five_cover
import joint
import transport

if not __debug__:
    raise RuntimeError("Run with assertions enabled")
root = HERE.parents[1]
out = io.StringIO()
with contextlib.redirect_stdout(out):
    transport.main(root / SOURCE)
assert out.getvalue() == (HERE / "TRANSPORT.json").read_text(), "Literal rows, code and catalogue receipt"
receipt = json.loads(out.getvalue())
result = joint.check(receipt)
assert json.dumps(result, sort_keys=True, indent=2) + "\n" == (HERE / "JOINT.json").read_text()
bad = json.loads(out.getvalue())
bad["max_catalogue_lines_by_rank"]["6"] = 48
try:
    joint.check(bad)
except AssertionError:
    pass
else:
    raise AssertionError("Corrupt chart capacity accepted")
target = five_cover.scan(root / SOURCE, extra_line=True)
assert not target["capped"] and target["first_survivor"] is None
assert json.dumps(target, sort_keys=True, indent=2) + "\n" == (HERE / "TARGET-COVER.json").read_text()
print("PASS_JOINT_MONOTONE_BIT_DESCENT_BOUND k=1..4 plus k=5 target exclusion")
