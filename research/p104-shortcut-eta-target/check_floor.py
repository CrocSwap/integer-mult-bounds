"""Replay the original ordinary stock hypotheses and two finite signed tapes at the installed floor."""

from pathlib import Path
import json
import runpy
import sys

if not __debug__:
    raise ValueError("Enable assertions")

tree = Path(sys.argv[1]).resolve()
runtime = tree / "runtime"
peer = tree / "research/frequency-weighted-native-multiplier"
sys.argv = [__file__, str(runtime)]
sys.path.insert(0, str(runtime))
from upstream import install

install()
from installations import BINARY_C
from raw_binary_stage import binary_word
from unpowered_price import intervals
from strict_moment import UNIT

original = (peer / "check_ordinary_floor.py").read_bytes()
for before, after in (
    (b"LOWER=4474", b"LOWER=18960"),
    (b"(4466,4468)", b"(18952,18954)"),
):
    assert original.count(before) == 1
    original = original.replace(before, after)
ns = {
    "__name__": "actual_target_floor",
    "__file__": str(peer / "check_ordinary_floor.py"),
}
exec(compile(original, ns["__file__"], "exec"), ns)
word = binary_word()
stock = ns["all_size_stock"](word, BINARY_C, intervals, UNIT)
fixture = ns["finite_plan"](word, BINARY_C)
seam = runpy.run_path(str(peer / "check_stage_seam.py"))
tapes = [seam["verify_tape"](1, [0, 1], [2, 1]), seam["verify_tape"](2, [1, 7], [3, 1])]
assert stock["first_two_columns"] == [18952, 18954]
assert fixture["tested_occupied_K7_grade"] == [49, 64] and fixture["native_opens"] > 0
print(
    json.dumps(
        {"stock": stock, "finite_occupied_edge": fixture, "signed_tapes": tapes},
        sort_keys=True,
    )
)
