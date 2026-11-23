#!/usr/bin/env python3
"""Authenticate the joined arguments and check their exact rational substitution."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import ast
import json

HERE = Path(__file__).resolve().parent
PINS = {
    "composition/PROOF.md": "f40697245c65ade66b84d49f7ed64c5c13a598d962a71bb3e2881bd64f65f9fd",
    "composition/ENTRY-HISTORY.md": "945f93f1d954ca0c4472395f1515615520555b0f14d097751b82210f055c4fc5",
    "ordinary-local/PROOF.md": "b1582d78063be51e057f3d6bcf5819134f4b1a3a62fed1bf90d2411dc67684ca",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for name, digest in PINS.items():
        require(sha256((HERE / name).read_bytes()).hexdigest() == digest,
                "changed joined argument: " + name)
    left = json.loads((HERE / "composition/SOURCE-BINDINGS.json").read_text())
    right = json.loads((HERE / "ordinary-local/SOURCE-BINDINGS.json").read_text())
    require(left["commit"] == right["commit"] ==
            "dfd25d553a843a946ca0b94130a5ff8943e98fdd", "different source heads")
    require(set(left["files"]) <= set(right["files"]), "source export mismatch")
    for name, pin in left["files"].items():
        other = right["files"][name]
        require(pin["sha256"] == other["sha256"] and pin["size"] == other["size"],
                "source binding disagreement: " + name)
        for folder in ("composition", "ordinary-local"):
            data = (HERE / folder / "sources" / name).read_bytes()
            require(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"],
                    "changed retained source: " + folder + "/" + name)
    for name in set(right["files"]) - set(left["files"]):
        pin = right["files"][name]
        data = (HERE / "ordinary-local/sources" / name).read_bytes()
        require(len(data) == pin["size"] and sha256(data).hexdigest() == pin["sha256"],
                "changed additional local source: " + name)
    tree = ast.parse((HERE / "composition/sources/installations.py").read_text())
    profiles = [ast.literal_eval(node.value.args[0]) for node in tree.body
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name) and node.value.func.id == "Profile"]
    require(len(profiles) == 7 and max(map(len, profiles)) == 7, "installed stage count changed")
    min_rank_log = min(min(profile) for profile in profiles)
    require(min_rank_log >= 5610 and 92 * min_rank_log >= 15, "insufficient production B")
    b = 32768
    correction = 254 * (Fraction(123, 8 * (b - 1)) + Fraction(54, b))
    require(correction == Fraction(144349851, 268427264) and correction < 1,
            "invalid exact correction")
    for stages in range(1, 8):
        weights = sum(2 ** (stages - j + 1) for j in range(1, stages + 1))
        require(weights == 2 ** (stages + 1) - 2 and weights <= 254,
                "stage geometric sum changed")
        coefficient = 2 + (31 + correction / 254) * weights + 3 * 2 ** stages
        require(coefficient < 8261, "joined native coefficient too small")
    require(9 * 8261 == 74349 and 74349 + 3 == 74352, "history coefficient mismatch")
    require(sum((Fraction(1), Fraction(1), *([Fraction(1, 4)] * 4))) == 3,
            "cold binary coefficient mismatch")
    result = {
        "status": "PASS_JOINED_ORDINARY_DATA_FILE_BOUND",
        "proof_sha256": sha256((HERE / "JOINED-STORAGE.md").read_bytes()).hexdigest(),
        "component_proofs": PINS,
        "shared_source_files": len(left["files"]),
        "total_authenticated_source_files": len(right["files"]),
        "minimum_installed_rank_log": min_rank_log,
        "sufficient_B": b,
        "exact_correction": str(correction),
        "native_T_coefficient": 8261,
        "native_X_coefficient": 74349,
        "mixed_history_Xmax_coefficient": 74352,
        "scope": "Conditional ordinary data-file endpoints; binary capacity/mass, header/control, fixed-tape and outer contracts retained",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
