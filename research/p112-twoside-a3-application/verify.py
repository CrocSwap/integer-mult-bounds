"""Check one literal TWOSIDE application of the inherited A3 theorem."""

import argparse
import hashlib
import json
from itertools import combinations_with_replacement, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PROFILE = (2, 3) + (6,) * 5 + (7,) * 4
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
DISTANCE = (0, 53, 78, 92, 100, 106, 109, 111, 112)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_profile(weights, dimension, allowance):
    require(type(dimension) is int and 5 <= dimension <= 8, "code dimension")
    require(type(allowance) is int and 1 <= allowance <= 6, "piece allowance")
    require(
        isinstance(weights, tuple)
        and dimension <= len(weights) <= dimension + allowance,
        "profile length",
    )
    require(all(type(w) is int and w in CAP for w in weights), "weight domain")
    require(tuple(sorted(weights)) == weights, "profile ordering")


def historical_survivor(weights, dimension=7, allowance=4):
    """Transcribe PR3154's bk2b predicate with bounded exhaustive bin packing."""
    validate_profile(weights, dimension, allowance)
    if sum(w - 2 for w in weights) >= 6 * dimension:
        return False
    for level in range(1, dimension + 1):
        retained = weights[: len(weights) - dimension + level]
        global_cap = sum(CAP[w] for w in retained)
        target_cap = sum(32 if w == 7 else CAP[w] for w in retained)
        if level == 1 and target_cap < 53 and global_cap < 73:
            return False
        if level == 2 and target_cap < 78 and global_cap < 82:
            return False
        if level >= 3 and global_cap < DISTANCE[level]:
            return False
    small = weights[: len(weights) - dimension]
    if sum(CAP[w] for w in small) >= 53:
        return True
    if sum(small) <= 7:
        return False
    return not any(
        all(
            sum(w for w, side in zip(small, assignment) if side == k) <= 6
            for k in (0, 1)
        )
        for assignment in product((0, 1), repeat=len(small))
    )


def application(weights=PROFILE, dimension=7, deleted=4):
    """Check transfer hypotheses; A3 and geometric caps remain dependencies."""
    validate_profile(weights, dimension, 4)
    require(type(deleted) is int and 0 <= deleted <= len(weights) - 4, "deletion count")
    retained = weights[: len(weights) - deleted] if deleted else weights
    small, endpoints = retained[:-4], retained[-4:]
    remaining_dimension = dimension - deleted
    require(remaining_dimension >= 3, "insufficient retained code dimension")
    require(all(w <= 6 for w in endpoints), "A3 endpoint rank exceeded")
    support_cap = sum(CAP[w] for w in small)
    require(support_cap <= 29, "A3 common support exceeded")
    require(support_cap + 20 < 53, "small-plus-one quotient independence")
    require(support_cap + 40 < 70, "all six edges in root-support range")
    return {
        "profile": list(weights),
        "original_piece_count": len(weights),
        "original_code_dimension_lower_bound": dimension,
        "deleted_pieces": deleted,
        "retained_weights": list(retained),
        "small_weights": list(small),
        "endpoint_weights": list(endpoints),
        "common_support_cap": support_cap,
        "retained_code_dimension_lower_bound": remaining_dimension,
        "a3_code_dimension_upper_bound": 2,
        "small_plus_one_cap": support_cap + 20,
        "edge_support_cap": support_cap + 40,
        "older_support22_applies": support_cap <= 22,
    }


def authenticate(package=PACKAGE, root=ROOT):
    require((package / "SOURCES.json").stat().st_size <= 100_000, "manifest capacity")
    manifest = json.loads((package / "SOURCES.json").read_text())
    require(
        len(manifest["files"]) <= 8 and len(manifest["retained_files"]) <= 6,
        "source inventory capacity",
    )
    for row in manifest["files"]:
        if row["usage"] == "input":
            require((root / row["path"]).stat().st_size <= 2_000_000, "input capacity")
            require(
                hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
                == row["sha256"],
                "changed input source",
            )
    for row in manifest["retained_files"]:
        require(
            (package / row["local_path"]).stat().st_size <= 100_000,
            "retained source capacity",
        )
        require(
            hashlib.sha256((package / row["local_path"]).read_bytes()).hexdigest()
            == row["sha256"],
            "changed retained source",
        )


def build():
    authenticate()
    survivors = []
    for count in range(7, 12):
        for weights in combinations_with_replacement(range(2, 8), count):
            if historical_survivor(weights):
                survivors.append(weights)
    require(
        len(survivors) == 154 and PROFILE in survivors,
        "literal original (7,4) survivor binding",
    )
    labels = tuple(
        map(
            int,
            (ROOT / "research/one-sided-six-multisets/data/data.txt")
            .read_text()
            .splitlines()[0]
            .split(),
        )
    )
    require(
        len(labels) == len(set(labels)) == 112 and all(x & 1 for x in labels),
        "P112 odd-label convention",
    )
    result = application()
    result.update(
        {
            "schema": "p112-twoside-a3-application/v1",
            "errors": 0,
            "original_cell": [7, 4],
            "original_cell_survivors": len(survivors),
            "sigma_sum": sum(w - 2 for w in PROFILE),
            "sigma_strict_ceiling": 42,
            "inherited_a3_source": "bd90899d5a45806288f7f3c9f177172a0ef5fa59",
            "source_theorem_replayed": False,
        }
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build()
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(ROOT), "external output required")
        with output.open("x", encoding="utf-8") as stream:
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            require(stream.write(encoded) == len(encoded), "receipt write")
    else:
        require(
            result == json.loads((PACKAGE / "RESULT.json").read_text()),
            "changed application receipt",
        )
    print(
        "PASS_P112_TWOSIDE_A3_APPLICATION survivors=154 support=26 dimensions=3>2 errors=0"
    )


if __name__ == "__main__":
    main()
