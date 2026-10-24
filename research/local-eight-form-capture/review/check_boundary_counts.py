"""Check the local scalar bill and the selected columns of D."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--package", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
p = args.package.resolve()
script = p / "historical/work/doubling-architecture/rank-independent/live-capture/check.py"
spec = importlib.util.spec_from_file_location("capture_audit", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
word_path = p / "historical/work/next-track/complex/pipeline/retimed-4/split-centres/CANONICAL-WORD.json.gz"
w = json.loads(gzip.decompress(word_path.read_bytes()))
ops = module.compile_ops(w["precondition"] + w["compensation"] + w["A"] + w["B"] + w["cleanup"])
prefix = module.compile_ops(w["precondition"] + w["A"])
n = 240 + w["R"]
centres = [[Q() for _ in range(120)] for _ in range(8)]
helpers = list(range(758, 750, -1))
for column in range(120):
    vector = [0] * n
    vector[column] = 1
    module.apply(vector, prefix)
    for i, centre in enumerate(w["centers"][:8]):
        centres[i][column] = vector[centre]

selected_d = []
for helper in helpers:
    vector = [0] * n
    vector[helper] = 1
    module.apply(vector, ops)
    selected_d.append(sum(bool(x) for x in vector[120:240]))
if selected_d != [0] * 8:
    raise RuntimeError("Selected D columns are not zero")
supports = [sum(bool(x) for x in row) for row in centres]
if supports != [56] * 8 or not all(x in (-1, 0, 1) for row in centres for x in row):
    raise RuntimeError("The centre support changed")
if (w["frames"][0] != [] or set(w["frames"][1]) != {1 << i for i in range(9)}
        or set(w["start"][120:240]) != {0}):
    raise RuntimeError("The boundary frames changed")

receipt = {
    "status": "PASS_BOUNDARY_COUNTS_AND_SELECTED_HELPER_D_COLUMN_CHECK",
    "centre_row_support": supports,
    "centre_coefficients": [-1, 0, 1],
    "base_scalar_operations": len(ops),
    "dirt_correction_operations": 11326,
    "dirt_correction_count_source": "Reproduced complete historical receipts",
    "preload_operations": sum(supports),
    "postload_operations": sum(supports),
    "total_scalar_operations": len(ops) + 11326 + 2 * sum(supports),
    "all_Y_start_at_zero_frame": True,
    "zero_and_full_frame_ids_verified": True,
    "selected_helper_D_nonzero_counts": selected_d,
    "DP_zero": True,
    "clarification": "For these selected helpers D has zero columns. Using their old values does not add a nonzero DPY error. The implemented updated-helper order is valid.",
    "scope": "Scalar operation count and order clarification only; no native or recursive cost invoice.",
    "method": "Use the retained column interpreter on 120 centre-prefix and eight helper basis columns.",
    "source_sha256": {
        str(script.relative_to(p)): hashlib.sha256(script.read_bytes()).hexdigest(),
        str(word_path.relative_to(p)): hashlib.sha256(word_path.read_bytes()).hexdigest(),
    },
}
args.output.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"])
