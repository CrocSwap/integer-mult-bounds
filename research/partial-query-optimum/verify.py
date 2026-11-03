"""Bounded exact corroboration; no predecessor implementation is executed."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from itertools import product

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from optimizer import check, solve, subspaces_by_extension, subspaces_by_rref


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def authenticate() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for source in sources["files"]:
        if source["usage"] == "input":
            digest = hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
            require(digest == source["sha256"], "source bytes changed")


def literal_span(vectors: list[int]) -> int:
    """Truth-set doubling, independent of Gaussian elimination."""
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in values}
    return sum(1 << value for value in values)


def literal_spaces(width: int) -> list[int]:
    """Scan every subset of the vector set and test XOR closure."""
    spaces = []
    for mask in range(1, 1 << (1 << width), 2):
        values = [value for value in range(1 << width) if mask & (1 << value)]
        if all(mask & (1 << (left ^ right)) for left in values for right in values):
            spaces.append(mask)
    return spaces


def subset_inventory(vectors: list[int]) -> list[tuple[int, int]]:
    return [(mask, literal_span([vector for index, vector in enumerate(vectors)
                                if mask & (1 << index)]))
            for mask in range(1 << len(vectors))]


def oracle(inventory: list[tuple[int, int]], costs: list[int], target_space: int) -> int:
    return min(sum(cost for index, cost in enumerate(costs) if mask & (1 << index))
               for mask, space in inventory if space & target_space == target_space)


def exhaustive() -> dict[str, int]:
    comparisons = 0
    entries = 0
    for vectors, width in [(list(range(1, 8)), 3), ([0, 1, 1, 2, 3], 2)]:
        inventory = subset_inventory(vectors)
        spaces = literal_spaces(width)
        for costs in product(range(3), repeat=len(vectors)):
            costs = list(costs)
            for space in spaces:
                targets = [value for value in range(1 << width) if space & (1 << value)]
                problem = {"width": width, "vectors": vectors,
                           "costs": costs, "targets": targets}
                certificate = solve(problem)
                actual = check(problem, certificate)
                require(actual == oracle(inventory, costs, space), "partial optimum mismatch")
                comparisons += 1
                entries += len(certificate["entries"])
    return {"exhaustive_optima": comparisons, "checked_candidate_bases": entries}


def rejection(problem: dict, certificate: dict) -> None:
    try:
        check(problem, certificate)
    except (ValueError, TypeError, KeyError):
        return
    raise ValueError("corrupted certificate accepted")


def certificate_controls() -> int:
    problem = {"width": 3, "vectors": [1, 2, 3, 4, 7],
               "costs": [8, 2, 2, 1, 2], "targets": [1]}
    certificate = solve(problem)
    require(check(problem, certificate) == 4, "intermediate-space optimum")
    feasible = [(entry["space"], sum(problem["costs"][i] for i in entry["selected"]))
                for entry in certificate["entries"] if entry["missing_target"] is None]
    require(feasible[0][1] == 8 and feasible[-1][1] == 5, "endpoint prices")
    mutants = []
    mutant = copy.deepcopy(certificate)
    mutant["entries"].pop(1)
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["quotient_forms"] = [0, 0]
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["entries"][0]["duals"][0] = 0
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["cost"] += 1
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["cost"], mutant["winner"] = 5, feasible[-1][0]
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["entries"][0]["selected"] = [1]
    mutants.append(mutant)
    mutant = copy.deepcopy(certificate)
    mutant["cost"] = True
    mutants.append(mutant)
    for mutant in mutants:
        rejection(problem, mutant)
    absent = {"width": 3, "vectors": [3, 2, 4], "costs": [2, 2, 1], "targets": [1]}
    missing_certificate = solve(absent)
    require(missing_certificate["entries"][0]["missing_target"] == 0, "separator fixture")
    mutant = copy.deepcopy(missing_certificate)
    mutant["entries"][0]["separator"] = 4
    rejection(absent, mutant)
    expensive = {"width": 2, "vectors": [1, 2, 3], "costs": [9, 1, 1], "targets": [1, 2]}
    mutant = solve(expensive)
    mutant["entries"][0]["selected"] = [0, 1]
    mutant["entries"][0]["duals"] = [1, 2]
    mutant["cost"] = 10
    rejection(expensive, mutant)
    return len(mutants) + 2


def boundary_and_invalid() -> dict:
    counts = []
    for dimension in range(5):
        direct = literal_spaces(dimension)
        require(direct == subspaces_by_extension(dimension) == subspaces_by_rref(dimension),
                "incomplete quotient enumeration")
        counts.append(len(direct))
    require(counts == [1, 2, 5, 16, 67], "Gaussian subspace counts")
    wide = {"width": 256, "vectors": [1 << i for i in range(256)] * 16,
            "costs": list(range(256)) * 16, "targets": [1 << i for i in range(255)]}
    require(check(wide, solve(wide)) == sum(range(255)), "wide boundary")
    codimension_four = {"width": 6, "vectors": list(range(64)),
                       "costs": [value.bit_count() for value in range(64)], "targets": [1, 2]}
    require(check(codimension_four, solve(codimension_four)) == 2, "codimension four boundary")
    empty = {"width": 1, "vectors": [], "costs": [], "targets": []}
    require(check(empty, solve(empty)) == 0, "empty problem")
    invalid = []
    for field, value in [("width", True), ("width", 257), ("vectors", [2]),
                         ("costs", [True]), ("costs", [-1]), ("costs", []),
                         ("targets", [2])]:
        problem = {"width": 1, "vectors": [1], "costs": [1], "targets": [1]}
        problem[field] = value
        invalid.append(problem)
    invalid.append({"width": 2, "vectors": [1], "costs": [1], "targets": [2]})
    invalid.append({"width": 5, "vectors": [1, 2, 4, 8, 16], "costs": [1] * 5,
                    "targets": []})
    invalid.append({"width": 1, "vectors": [1] * 4097, "costs": [1] * 4097,
                    "targets": [1]})
    for problem in invalid:
        try:
            solve(problem)
        except ValueError:
            continue
        raise ValueError("invalid problem accepted")
    return {"quotient_space_counts": counts, "boundary_cases": 3,
            "invalid_problem_rejections": len(invalid)}


def cli_control() -> int:
    problem = {"width": 2, "vectors": [1, 2, 3], "costs": [3, 2, 2], "targets": [1]}
    with tempfile.TemporaryDirectory(prefix="partial-query-") as directory:
        problem_path, certificate_path = (Path(directory) / name for name in ("input.json", "cert.json"))
        problem_path.write_text(json.dumps(problem), encoding="utf-8")
        command = [sys.executable, "-I", "-W", "error", "-B", str(PACKAGE / "optimizer.py")]
        result = subprocess.run(command + [str(problem_path)], check=True, capture_output=True,
                                text=True, timeout=30)
        certificate_path.write_text(result.stdout, encoding="utf-8")
        checked = subprocess.run(command + [str(problem_path), "--check", str(certificate_path)],
                                 check=True, capture_output=True, text=True, timeout=30)
        require(json.loads(checked.stdout)["cost"] == 3, "CLI optimum")
        certificate_path.write_text('{"schema": "wrong"}', encoding="utf-8")
        rejected = subprocess.run(command + [str(problem_path), "--check", str(certificate_path)],
                                  capture_output=True, text=True, timeout=30)
        require(rejected.returncode != 0, "CLI corrupted certificate accepted")
    return 3


def main() -> None:
    authenticate()
    counts = exhaustive()
    counts.update(boundary_and_invalid())
    counts["certificate_rejections"] = certificate_controls()
    counts["cli_runs"] = cli_control()
    files = ["README.md", "PROOF.md", "ENGINEERING.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "optimizer.py", "verify.py"]
    receipt = {"status": "PASS_PARTIAL_QUERY_OPTIMUM", "python": sys.version,
               "counts": counts, "sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                                            for name in files}}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
