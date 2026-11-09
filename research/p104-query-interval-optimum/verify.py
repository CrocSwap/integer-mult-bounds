"""Exact forward response certificate for one pinned source interval.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
No predecessor emitter, evaluator or matrix routine is imported.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 19)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    entries = json.loads((HERE / "DEPENDENCIES.json").read_text())["files"]
    for entry in entries:
        data = (ROOT / entry["path"]).read_bytes()
        require(sha256(data).hexdigest() == entry["sha256"], "dependency SHA256")
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == entry["git_blob"], "dependency Git blob")
    return len(entries)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def evaluate(events, sign, roles=76):
    """Propagate every independent input column, at q=sign and D9=1."""
    require(sign in (-1, 1), "legal sign")
    rows = identity(roles)
    for event in events:
        require(event[0] == "A", "only A-chain operations in this interval")
        op, dest = event[1:3]
        require(0 <= dest < 38, "original A role range")
        if op in ("ADD", "QUERY"):
            source, coefficient = event[3:5]
            require(0 <= source < 38 and source != dest, "distinct original roles")
            c = F(coefficient) if op == "ADD" else F(sign if coefficient % 2 else 1)
            rows[dest] = [a + c*b for a, b in zip(rows[dest], rows[source])]
        elif op == "SWAP":
            source = event[3]
            require(0 <= source < 38, "swap source")
            rows[dest], rows[source] = rows[source], rows[dest]
        elif op == "SCALE":
            rows[dest] = [F(event[3])*a for a in rows[dest]]
        elif op == "QSELF":
            c = sign if event[3] % 2 else 1
            rows[dest] = [c*a for a in rows[dest]]
        elif op == "LAMBDA":
            require(event[3] in (-1, 1), "literal lambda sign")
            # ((1+s*i)+(1-s*i)*q^2)/2 = 1 at either q sign.
        elif op == "IDLE_ONE":
            require(event[3] == [9], "only the unconstrained formal D9 occurs")
        else:
            raise ValueError("unhandled source operation " + op)
    return rows


def difference(a, b):
    return [[x-y for x, y in zip(r, s)] for r, s in zip(a, b)]


def rank(matrix):
    rows = [row[:] for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        chosen = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        d = rows[pivot][col]
        rows[pivot] = [x/d for x in rows[pivot]]
        for i in range(pivot+1, len(rows)):
            c = rows[i][col]
            if c:
                rows[i] = [a-c*b for a, b in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def determinant3(m):
    a, b, c = m
    return (a[0]*(b[1]*c[2]-b[2]*c[1])
            - a[1]*(b[0]*c[2]-b[2]*c[0])
            + a[2]*(b[0]*c[1]-b[1]*c[0]))


def response(word):
    return difference(evaluate(word, 1), evaluate(word, -1))


def main():
    authenticated = authenticate()
    old = json.loads((HERE / "data/caller_efree.json").read_text())
    new = json.loads((HERE / "QUERY-ONLY-CALLER.json").read_text())
    require(old["roles"] == new["roles"] == 76, "independent complete role inventory")
    before, after = old["events"][457:576], new["events"][457:680]
    require(len(old["events"]) == 2991 and len(new["events"]) == 3095, "whole source sizes")
    require(len(before) == 119 and len(after) == 223, "fixed interval sizes")
    require(before[0] == ["A", "QSELF", 0, -1]
            and before[-1] == ["A", "QSELF", 19, -1], "exact source endpoints")
    require(old["events"][:457] == new["events"][:457]
            and old["events"][576:] == new["events"][680:], "unchanged enclosing event segments")
    for word in (before, after):
        require(sum(e[1] == "IDLE_ONE" for e in word) == 1, "one formal D9 operation")
    counts = [Counter(e[1] for e in word) for word in (before, after)]
    require(counts[0]["QSELF"] == 2 and counts[0]["QUERY"] == 1, "old charged sites")
    require(counts[1]["QUERY"] == 3 and counts[1]["QSELF"] == 0, "prior three-query attainment")
    delta = response(before)
    minor = [[delta[i][j] for j in PIVOTS] for i in PIVOTS]
    require(minor == [[-2, -4, 0], [0, -2, 0], [0, 0, 2]], "actual source minor")
    require(determinant3(minor) == 8 and rank(delta) == 3, "exact response rank")
    for sign in (-1, 1):
        require(evaluate(before, sign) == evaluate(after, sign), "complete two-point attainment check")
    controls = []
    for name, word, charged in (("source", before, {"QUERY", "QSELF"}),
                                ("attainment", after, {"QUERY"})):
        for index, event in enumerate(word):
            if event[1] in charged:
                r = rank(response(word[:index]+word[index+1:]))
                require(r <= 2, "deleted paid site must lose response rank three")
                controls.append({"word": name, "local_index": index, "response_rank": r})
    require(len(controls) == 6, "all charged-site controls executed")
    # These boundary examples explain why the theorem retains its premises.
    require(rank([[delta[i][j] for j in (2, 3)] for i in range(76)]) <= 2,
            "two-input restriction cannot prove a three-query bound")
    require(rank([[F(2 if i == j else 0) for j in range(3)] for i in range(3)]) == 3,
            "free odd-q diagonal would defeat the even-map premise")
    result = {
        "status": "PASS_P104_QUERY_INTERVAL_OPTIMUM",
        "dependencies_authenticated": authenticated,
        "independent_inputs": 76,
        "source_interval": [457, 576],
        "attainment_interval": [457, 680],
        "source_rows": 119,
        "attainment_rows": 223,
        "source_opcodes": dict(counts[0]),
        "attainment_opcodes": dict(counts[1]),
        "response_rank": 3,
        "minor_rows_and_columns": list(PIVOTS),
        "minor": [[str(x) for x in row] for row in minor],
        "minor_determinant": "8",
        "nonzero_response_entries": sum(bool(x) for row in delta for x in row),
        "complete_character_comparisons": 2,
        "deleted_site_controls": controls,
        "scope_controls": ["independent-input subspace restriction", "free odd-q coefficients forbidden"],
        "attainment_scope": "Full formal identity is the pinned predecessor theorem; two-point checking alone is insufficient.",
        "lower_bound_scope": "Written telescoping proof plus exact finite source minor; no physical or whole-caller optimality.",
        "no_new_kappa": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
