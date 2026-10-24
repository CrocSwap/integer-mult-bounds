"""Check the stated scope arithmetic without package checker imports."""

from collections import Counter
from fractions import Fraction
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "cold" / "package"


def check(condition, label):
    if not condition:
        raise ValueError(label)


def span(rows):
    values = {0}
    for row in rows:
        values |= {value ^ row for value in values}
    return values


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


word = json.loads(gzip.decompress((PACKAGE / "data/CANONICAL-WORD.json.gz").read_bytes()))
programs = json.loads(gzip.decompress((PACKAGE / "data/LOCAL-PROGRAMS.json.gz").read_bytes()))
profiles = {}
for orientation, program in programs.items():
    profile = Counter()
    for event in program:
        if event[0] in ("center", "climb"):
            profile[event[-1]] += 1
        elif event[0] in ("adapter", "residual_adapter"):
            profile[0] += 1
    check(profile == {0: 1570, 1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "source profile")
    check(sum(profile.values()) == 5064, "event count")
    check(sum(r * n for r, n in profile.items()) == 5586, "rank mass")
    profiles[orientation] = dict(profile)

basis = [30, 45, 75, 128, 256]
centres = [span(word["frames"][f]) for f in word["center_frames"]]
common = set.intersection(*centres)
check(common == span(basis) and len(common) == 32, "common intersection")
gram = [sum(((u & v).bit_count() % 2) << j for j, v in enumerate(basis)) for u in basis]
check(gram == [0, 0, 0, 8, 16] and rank(gram) == 2, "Gram rank")
sharp_ranks = []
twisted_zero = [((1 << j) << 9) | ((1 << j) & 384) for j in range(9)]
for frame_id, values in zip(word["center_frames"], centres):
    frame = word["frames"][frame_id]
    perpendicular = [v for v in range(512) if all((v & u).bit_count() % 2 == 0 for u in frame)]
    label = [u | (u << 9) for u in frame] + [v << 9 for v in perpendicular]
    check(rank(label) == 9 and len(values) == 256, "centre dimensions")
    fixed = {u for u in values if u == (u & 384)}
    check(fixed == {0, 128, 256, 384}, "fixed space")
    result = rank(label + twisted_zero) - 9
    check(result == 6, "sharp descent rank")
    sharp_ranks.append(result)

replay = json.loads((HERE / "cold-output/REPLAY.json").read_text())
changed = {int(k): v for k, v in replay["frame415_counterexample"]["profile"].items()}
baseline = profiles["forward"]
check(sum(changed.values()) == 5064, "counterexample event count")
rank_delta = sum(r * n for r, n in changed.items()) - 5586
child_delta = sum(n for r, n in changed.items() if r > 0) - sum(n for r, n in baseline.items() if r > 0)
check((rank_delta, child_delta) == (48, -1), "counterexample costs")
check(49**5 > 81 * 20**5, "first strict fifth-power bound")
check(303**5 < 8 * 200**5, "second strict fifth-power bound")
check(Fraction(24, 49) - Fraction(97, 200) == Fraction(47, 9800), "strict gap")
result = {
    "status": "PASS_INDEPENDENT_SCOPE_ARITHMETIC",
    "imports_package_checkers": False,
    "source_profiles": profiles,
    "source_native_events": 5064,
    "source_rank_mass": 5586,
    "all_nonzero_lines": 511,
    "odd_lines": sum(a.bit_count() % 2 for a in range(1, 512)),
    "common_odd_lines": sorted(a for a in common if a.bit_count() % 2),
    "common_gram_rows": gram,
    "common_gram_rank": 2,
    "sharp_centre_ranks": sharp_ranks,
    "frame415_counterexample_rank_delta": rank_delta,
    "frame415_counterexample_paid_child_delta": child_delta,
    "strict_moment_gap": "47/9800",
    "scope": "Arithmetic checks for existing claims. The proof review supplies the general statements.",
}
(HERE / "SCOPE-CHECK.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(result["status"])
