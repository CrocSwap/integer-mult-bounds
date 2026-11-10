"""Check the new local map and literal substitution, without replaying PR6621.

Produced by Nick Petalas. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import sys

# Isolated Python excludes the script directory. Admit this one explicit
# package directory for its fixed local rewrite module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rewrite import (HERE, TARGETS, SOURCES, TEMPORARY, construct, encoded,
                     evaluate, new_prefix, old_prefix, read_source, require)

ROLES = TARGETS + tuple(role for role, _ in SOURCES)


def expected(values):
    result = dict(values)
    combination = sum(Q(coefficient) * values[source] for source, coefficient in SOURCES)
    for target in TARGETS:
        result[target] += combination
    return result


def check_case(values):
    desired = expected(values)
    old, old_temporary, old_public = evaluate(old_prefix(), values)
    new, new_temporary, new_public = evaluate(new_prefix(), values)
    require(old == desired == new, "Exact arbitrary-input local map")
    bound = max(abs(value) for value in values.values())
    require(old_temporary == 0 and new_temporary <= Q(7, 2) * bound,
            "Temporary range bound")
    require(max(old_public, new_public) <= Q(9, 2) * bound, "Public range bound")


def reject(action, message):
    try:
        action()
    except (ValueError, KeyError):
        return
    raise ValueError("Accepted control: " + message)


def controls(word):
    values = {role: Q(i + 1) for i, role in enumerate(ROLES)}
    bad = new_prefix()
    del bad[4]
    reject(lambda: require(evaluate(bad, values)[0] == expected(values), "Missing read"),
           "deleted destination ADD")
    bad = new_prefix()
    bad[-2][3] = "1"
    reject(lambda: evaluate(bad, values), "nonzero owned CLEAR")
    bad = new_prefix()
    bad[2][3] = "1/4"
    reject(lambda: evaluate(bad, values), "wrong source coefficient")
    bad = new_prefix()
    bad[0][-1] = 127
    reject(lambda: evaluate(bad, values), "wrong local frame")
    bad = new_prefix()
    bad[1][2] = TEMPORARY
    reject(lambda: evaluate(bad, values), "aliased ADD")
    bad_word = deepcopy(word)
    bad_word["program"].insert(0, ["INIT", TEMPORARY, 3])
    reject(lambda: construct(bad_word), "occupied prefix slot")
    bad_word = deepcopy(word)
    bad_word["initial"][TARGETS[0]] = 127
    reject(lambda: construct(bad_word), "illegal initial reader frame")


def run():
    word = read_source()
    candidate = construct(word)
    require({k: v for k, v in word.items() if k != "program"} ==
            {k: v for k, v in candidate.items() if k != "program"}, "All metadata unchanged")
    require(candidate["program"][14:] == word["program"][18:], "Literal untouched suffix")
    require(len(word["program"]) - len(candidate["program"]) == 4, "Four fewer events")
    require(sum(event[0] == "ADD" for event in old_prefix()) == 18 and
            sum(event[0] == "ADD" for event in new_prefix()) == 12, "Six fewer ADDs")
    for column in range(9):
        check_case({role: Q(i == column) for i, role in enumerate(ROLES)})
    for signs in product((-1, 1), repeat=9):
        check_case(dict(zip(ROLES, map(Q, signs))))
    for case in range(17):
        check_case({role: Q((-1) ** (i + case) * ((case + 1) << (i + case)),
                           1 << (i % 4)) for i, role in enumerate(ROLES)})
    controls(word)
    return {"status": "PASS_P104_SHARED_PREPARATION", "claim_type": "scoped construction",
            "basis_columns": 9, "box_vertices": 512, "signed_dyadic_cases": 17,
            "rejection_controls": 7, "old_ADDs": 18, "new_ADDs": 12,
            "old_events": len(word["program"]), "new_events": len(candidate["program"]),
            "candidate_word_sha256": sha256(encoded(candidate)).hexdigest()}


if __name__ == "__main__":
    result = run()
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "NATIVE-SOURCE.json", "rewrite.py", "verify.py", "inputs/WORD.json.gz", "inputs/NOTICE")
    result["package_sha256"] = {name: sha256((HERE / name).read_bytes()).hexdigest()
                                for name in files}
    print(json.dumps(result, sort_keys=True, indent=2))
