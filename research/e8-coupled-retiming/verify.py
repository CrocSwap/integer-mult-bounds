"""Check the pinned E8 frame changes and their exact recursive cost."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from reconstruct import moment, reconstruct
from retime import build
from scalar_map_comparison import compare


ROOT = Path(__file__).resolve().parent
OLD = Q(876248285600677, 10**18)
NEW = Q(876412559609473, 10**18)
GRID = Q(1, 10**18)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_bound(result, saving):
    args = result["histogram"], result["m"], result["W"]
    low, high = moment(*args, saving)
    next_low, _ = moment(*args, saving + GRID)
    assert high < 1 < next_low
    return {"saving": str(saving), "strict_upper_below_one": True,
            "next_grid_lower_above_one": True, "upper_gap_decimal": float(1 - high)}


def main():
    if sys.flags.optimize:
        raise SystemExit("Assertions must remain enabled for verification")
    pins = json.loads((ROOT / "sources.json").read_text())
    for path, expected in pins["files"].items():
        assert digest((ROOT / path).read_bytes()) == expected, path
    raw = [gzip.decompress((ROOT / "data" / name).read_bytes())
           for name in ("original.json.gz", "retimed.json.gz")]
    original, candidate = map(json.loads, raw)
    assert digest(raw[0]) == "3594f19c4d01cf11fb930c5c61baeed399620acbc5b94096b16bcacb23997dd3"
    assert digest(raw[1]) == "3191011e0cb189665c8e0a9b97137dbed50241a0704c8be01c11b1b5a9518fc2"
    rebuilt = json.dumps(build(original), separators=(",", ":")).encode()
    assert rebuilt == raw[1]
    old, new = map(reconstruct, (original, candidate))
    delta = {r: new["invocation_histogram"].get(r, 0) - old["invocation_histogram"].get(r, 0)
             for r in range(1, 10)}
    delta = {r: count for r, count in delta.items() if count}
    assert delta == {1: 2, 2: -6, 3: 4, 4: 1, 5: -6, 6: 4}
    # These positive weights prove the cost sign for every exponent in (0, 1).
    weights = [1, 4, 1, 2, 4]
    coefficients = Counter()
    for rank, weight in enumerate(weights, 1):
        assert weight > 0
        coefficients[rank - 1] += weight
        coefficients[rank] -= 2 * weight
        coefficients[rank + 1] += weight
    assert coefficients.pop(0) == 1
    assert dict(coefficients) == delta
    assert sum(delta.values()) == -1
    for key in ("helpers", "copy_cost", "invocation_mass", "rank_mass", "deficit", "m", "W"):
        assert old[key] == new[key], key

    # These damaged inputs test separate proof obligations.
    controls = []
    bad = deepcopy(candidate)
    bad["scat"]["table"][0][0][1] *= -1
    controls.append(("scatter sign", bad, "Clean-source scalar identity"))
    bad = deepcopy(candidate)
    bad["A"][0][1] = candidate["start"][1]
    controls.append(("same-rank wrong subspace", bad, "A frame path is not nested"))
    bad = deepcopy(candidate)
    bad["cst"] -= 1
    controls.append(("copy undercharge", bad, "Copy cost"))
    bad = deepcopy(candidate)
    bad["A"] += [["out", 1, 0, [[1, 1, 1]], []], ["out", 1, 0, [[1, -1, 1]], []]]
    controls.append(("forbidden phase-A cancellation", bad, "Unsupported phase-A scalar direction"))
    rejected = []
    for name, broken, expected in controls:
        try:
            reconstruct(broken)
        except ValueError as error:
            assert str(error) == expected, (name, str(error))
            rejected.append(name)
        else:
            raise AssertionError("Damaged input accepted: " + name)

    scalar = compare((original, candidate))
    assert scalar["complete_scalar_maps_equal"] and scalar["rows"] == 1023
    result = {"status": "PASS", "source_commit": pins["commit"],
              "uncompressed_sha256": list(map(digest, raw)),
              "histogram_delta": delta, "histogram": new["invocation_histogram"],
              "positive_second_difference_weights": weights,
              "baseline": check_bound(old, OLD), "candidate": check_bound(new, NEW),
              "m": new["m"], "W": new["W"], "helpers": new["helpers"],
              "copy_cost": new["copy_cost"], "rank_mass": new["rank_mass"], "deficit": new["deficit"],
              "scalar_map_rows_and_columns": scalar["rows"],
              "checks": ["frame_paths", "clean_source_identity", "complete_scalar_map", "exact_moments", "strict_concavity_identity"],
              "rejected_controls": rejected,
              "scope": "Finite E8 circuit and exact recursive moment. No new Lean build or full multiplication theorem is claimed."}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
