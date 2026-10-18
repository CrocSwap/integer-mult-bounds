"""Exact rank-two obstructions to fusing repeated CK cleanup additions.

Apache-2.0. Prepared for @thakrarsagar with substantial OpenAI Codex assistance.
The supplier sources and contributors are credited in README.md.
"""

import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_word():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, expected in pins["files"].items():
        data = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        require(hashlib.sha256(data).hexdigest() == expected, "source pin: " + name)
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    require(selected["audited_source_head"] == pins["selected_pr626_head"], "selected head binding")
    require(selected["reviewed_dependency_heads"]["622"] == pins["reviewed_pr622_head"], "PR622 head binding")
    require(selected["reviewed_dependency_heads"]["543"] == pins["retained_pr543_head"], "PR543 head binding")
    spec = json.loads((ROOT / "research/complex-k492-owner-repair/data/SPEC.json").read_text())
    require(spec["providers"]["ck"]["artifact_semantic_sha256"]["CANONICAL-WORD.json.gz"]
            == pins["files"][WORD], "CK SPEC binding")
    n = 2 * word["v"] + word["R"]
    for op in word["cleanup"]:
        require(op[0] in ("add", "scale"), "unexpected cleanup operation")
        require(len(op) == (6 if op[0] == "add" else 5), "operation shape")
        regs = op[1:3] if op[0] == "add" else op[1:2]
        require(all(isinstance(r, int) and 0 <= r < n for r in regs), "register range")
        require(op[-1] == 1 and all(word["final"][r] == 1 for r in regs), "full-frame cleanup")
        require(op[0] != "add" or op[1] != op[2], "aliased addition")
        q = Q(*op[3:5]) if op[0] == "add" else Q(*op[2:4])
        require(q != 0, "zero addition or singular scale")
    return word


def put(vector, index, value):
    if value:
        vector[index] = value
    else:
        vector.pop(index, None)


def conjugate(middle, target, source):
    """Return M e_target and e_source^T M^-1 without constructing M."""
    u, v = {target: Q(1)}, {source: Q(1)}
    for op in middle:
        x = op[1]
        if op[0] == "add":
            y, q = op[2], Q(*op[3:5])
            put(u, x, u.get(x, 0) + q * u.get(y, 0))
            put(v, y, v.get(y, 0) - q * v.get(x, 0))
        else:
            q = Q(*op[2:4])
            put(u, x, q * u.get(x, 0))
            put(v, x, v.get(x, 0) / q)
    return u, v


def dual(op):
    if op[0] == "add":
        return ["add", op[2], op[1], -op[3], op[4], op[5]]
    return ["scale", op[1], op[3], op[2], op[4]]


def rank_two_witness(middle, t, s, a, b):
    u, v = conjugate(middle, t, s)
    rows = sorted(set(u) - {t})
    columns = sorted(set(v) - {s})
    if not rows or not columns:
        return None
    r, c = rows[0], columns[0]

    def entry(x, y):
        shifted = u.get(x, 0) + (b * u.get(s, 0) if x == t else 0)
        return a * shifted * v.get(y, 0) + (b if (x, y) == (t, s) else 0)

    minor = [[entry(x, y) for y in (s, c)] for x in (t, r)]
    determinant = minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]
    require(determinant == a * b * u[r] * v[c] != 0, "rank-two determinant")
    return {
        "rows": [t, r], "columns": [s, c],
        "minor": [[str(x) for x in row] for row in minor],
        "determinant": str(determinant),
        "u_support": len(u), "v_support": len(v),
        "u_r": str(u[r]), "v_c": str(v[c]),
    }


def census(word):
    ops = word["cleanup"]
    seen, pairs = {}, []
    for j, last in enumerate(ops):
        if last[0] != "add":
            continue
        t, s = last[1:3]
        for i in seen.get((t, s), []):
            a, b = Q(*ops[i][3:5]), Q(*last[3:5])
            witness = rank_two_witness(ops[i + 1:j], t, s, a, b)
            require(witness is not None, f"unresolved pair: {i},{j}")
            reflected = rank_two_witness([dual(op) for op in ops[i + 1:j]], s, t, -a, -b)
            require(reflected is not None, f"unresolved dual pair: {i},{j}")
            pairs.append({"i": i, "j": j, "t": t, "s": s,
                          "a": str(a), "b": str(b), **witness,
                          "dual": {"t": s, "s": t, "a": str(-a), "b": str(-b), **reflected}})
        seen.setdefault((t, s), []).append(j)
    return {
        "schema": "ck-cleanup-rank-two-v1",
        "assignment_seed": 20,
        "word": WORD,
        "registers": 2 * word["v"] + word["R"],
        "cleanup_operations": len(ops),
        "cleanup_counts": dict(sorted(Counter(op[0] for op in ops).items())),
        "same_endpoint_pairs": len(pairs),
        "rank_two_pairs": len(pairs),
        "pairs": pairs,
    }


def controls():
    # A noncommuting middle gate alone does not imply a rank-two obstruction.
    require(rank_two_witness([["add", 0, 2, 3, 1, 1]], 0, 1, Q(1), Q(1)) is None,
            "commuting positive control")
    scaled = [["scale", 1, 2, 1, 1]]
    require(rank_two_witness(scaled, 0, 1, Q(1), Q(1)) is None,
            "scaled-conjugation positive control")
    u, v = conjugate(scaled, 0, 1)
    require(u[0] * v[1] + 1 == Q(3, 2), "transported coefficient")
    middle = [["add", 1, 0, 1, 1, 1]]
    witness = rank_two_witness(middle, 0, 1, Q(1), Q(1))
    require(witness["minor"] == [["3", "-2"], ["1", "-1"]]
            and witness["determinant"] == "-1", "rank-two control")
    # Opposite endpoint coefficients do not suffice for cancellation.
    require(rank_two_witness(middle, 0, 1, Q(1), Q(-1)) is not None,
            "false cancellation control")
    # If the whole middle is identity, local blockers must cancel collectively.
    identity_middle = middle + [["add", 1, 0, -1, 1, 1]]
    require(rank_two_witness(identity_middle, 0, 1, Q(1), Q(1)) is None,
            "collective cancellation positive control")
    return 5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print regenerated certificate without writing files")
    args = parser.parse_args()
    result = census(load_word())
    count = controls()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(result == expected, "certificate differs from exact recomputation")
    from check_columns import verify
    checked = verify(ROOT, result)
    for label in ("minor", "dual coefficient", "coverage"):
        mutant = copy.deepcopy(result)
        if label == "minor":
            mutant["pairs"][0]["minor"][0][0] = str(Q(mutant["pairs"][0]["minor"][0][0]) + 1)
        elif label == "dual coefficient":
            mutant["pairs"][0]["dual"]["a"] = str(-Q(mutant["pairs"][0]["dual"]["a"]))
        else:
            mutant["pairs"].pop()
        try:
            verify(ROOT, mutant)
        except ValueError:
            count += 1
        else:
            raise ValueError("accepted invalid certificate: " + label)
    print(f"PASS_CK_CLEANUP_RANK_TWO pairs={len(result['pairs'])} "
          f"rank=2 columns={checked} controls={count}")


if __name__ == "__main__":
    main()
