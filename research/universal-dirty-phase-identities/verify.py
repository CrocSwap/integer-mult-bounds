#!/usr/bin/env python3
"""Universal typed block-polynomial check of PR1278's phase identities.

Philipp / mightyOil, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported. A word is NEVER sorted or deduplicated.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TYPES = ("D", "D", "D", "S")  # x, y, z, all shared deeper scratch
SYMBOLS = {}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b, sign=1):
    out = dict(a)
    for word, coeff in b.items():
        out[word] = out.get(word, 0) + sign * coeff
        if not out[word]:
            del out[word]
    return out


def times(a, b):
    out = {}
    for u, c in a.items():
        for v, d in b.items():
            if u and v:
                require(SYMBOLS[u[-1]][1] == SYMBOLS[v[0]][0], "ill-typed product")
            w = u + v
            out[w] = out.get(w, 0) + c * d
            if not out[w]:
                del out[w]
    return out


def zero():
    return [[{} for _ in range(4)] for _ in range(4)]


def identity():
    m = zero()
    for i in range(4):
        m[i][i] = {(): 1}
    return m


def plus(a, b, sign=1):
    return [[add(a[i][j], b[i][j], sign) for j in range(4)] for i in range(4)]


def product(*matrices):
    out = identity()
    for b in matrices:
        c = zero()
        for i in range(4):
            for j in range(4):
                for k in range(4):
                    c[i][j] = add(c[i][j], times(out[i][k], b[k][j]))
        out = c
    return out


def variable(name, i, j):
    kind = (TYPES[i], TYPES[j])
    require(name not in SYMBOLS or SYMBOLS[name] == kind, "symbol changed type")
    SYMBOLS[name] = kind
    return {(name,): 1}


def atom(name, i, j):
    m = zero()
    m[i][j] = variable(name, i, j)
    return m


def child(name, source, target):
    m = identity()
    # This is the complete generic block shape, not a product of chosen shears.
    for i, j, label in [(target, source, "a"), (target, 3, "b"),
                         (3, source, "c"), (3, 3, "d")]:
        m[i][j] = variable(name + "_" + label, i, j)
    return m


def weak_block(name, fixed_column=None, fixed_row=None):
    m = zero()
    for i in range(4):
        for j in range(4):
            if j == fixed_column or i == fixed_row:
                m[i][j] = {(): 1} if i == j else {}
            else:
                m[i][j] = variable(f"{name}_{i}{j}", i, j)
    return m


def equations(mutation=None, weak=False):
    if weak:
        p, q = weak_block("P", fixed_column=1), weak_block("Q", fixed_column=1)
        r, s = weak_block("R", fixed_row=0), weak_block("S", fixed_row=0)
    else:
        p, r = child("P", 0, 2), child("R", 0, 2)
        q, s = child("Q", 2, 1), child("S", 2, 1)
    mats = {"P": p, "R": r, "Q": q, "S": s}
    if mutation:
        name, i, j = mutation
        mats[name][i][j] = add(mats[name][i][j], variable("FAULT", i, j))
    I = identity()
    H, E = atom("B", 2, 0), atom("A", 1, 2)
    U, Ui, V, Vi = plus(I, H), plus(I, H, -1), plus(I, E), plus(I, E, -1)
    G = product(E, H)
    F, Fi = plus(I, G), plus(I, G, -1)
    ends = [p, product(q, U), product(p, Ui, V, U), product(q, F)]
    # R and S stand for inverse prefixes. They are independent generic blocks;
    # not a single cancellation P*R=I or Q*S=I is available to the checker.
    starts_inverse = [r, product(Ui, s), product(Ui, Vi, U, r), product(Fi, s)]
    expected = {
        (0, 0): product(p, r), (1, 1): product(q, s),
        (2, 2): product(p, r), (3, 3): product(q, s),
        (1, 0): product(q, U, r), (2, 1): product(p, Ui, V, s),
        (3, 2): product(q, Vi, r),
        (0, 1): product(p, Ui, s), (1, 2): product(q, Vi, U, r),
        (2, 3): product(p, V, s),
        (2, 0): plus(product(p, r), product(E, U, r)),
        (0, 2): plus(product(p, r), product(E, U, r), -1),
        (3, 1): plus(product(q, s), product(q, Vi, H), -1),
        (1, 3): plus(product(q, s), product(q, Vi, H)),
        (3, 0): plus(product(q, r), G),
        (0, 3): plus(product(p, s), G, -1),
    }
    eqs = {f"phase_{start}_to_{end}": (product(ends[end], starts_inverse[start]), rhs)
           for (end, start), rhs in expected.items()}
    eqs["completed_parent"] = (product(Vi, Ui, V, U), F)
    eqs["completed_parent_inverse"] = (product(Ui, Vi, U, V), Fi)
    return eqs


def encode(m):
    return [{"row": i, "column": j, "terms":
             [{"word": list(w), "coefficient": c} for w, c in sorted(m[i][j].items())]}
            for i in range(4) for j in range(4) if m[i][j]]


def check_types(m):
    for i in range(4):
        for j in range(4):
            for w in m[i][j]:
                if w:
                    require(SYMBOLS[w[0]][0] == TYPES[i] and SYMBOLS[w[-1]][1] == TYPES[j],
                            "wrong rectangular block endpoints")
                else:
                    require(i == j, "identity off diagonal")


def source_check():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["vendor_inputs"]:
        raw = (HERE / row["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash mismatch")
        obj = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(hashlib.sha1(obj).hexdigest() == row["git_blob"], "source Git blob mismatch")
    return len(sources["vendor_inputs"])


def run():
    source_count = source_check()
    SYMBOLS.clear()
    eqs = equations(weak=True)
    records = {}
    for name, (lhs, rhs) in eqs.items():
        check_types(lhs)
        check_types(rhs)
        require(lhs == rhs, "universal identity fails: " + name)
        records[name] = {"normal_form": encode(lhs), "residual": []}
    symbols = {k: list(v) for k, v in sorted(SYMBOLS.items())}
    controls = {}
    for label, mutation in {
        "P_does_not_fix_y": ("P", 3, 1),
        "Q_does_not_fix_y": ("Q", 3, 1),
        "R_does_not_preserve_x": ("R", 0, 3),
        "S_does_not_preserve_x": ("S", 0, 3),
    }.items():
        SYMBOLS.clear()
        bad = equations(mutation, weak=True)
        residuals = {n: encode(plus(a, b, -1)) for n, (a, b) in bad.items() if a != b}
        require(residuals, "invariant-removal control did not fail")
        controls[label] = {"mutation": list(mutation), "failed_identities": residuals}
    SYMBOLS.clear()
    strong_eqs = equations()
    require(all(a == b for a, b in strong_eqs.values()), "source child-shape check fails")
    a, b = {("A",): 1}, {("B",): 1}
    require(times(a, b) != times(b, a), "commuting normalization hid order")
    require(times(a, a) == {("A", "A"): 1}, "repetition discarded")
    # An intentionally incorrect parent shear sign must not normalize to zero.
    require(eqs["completed_parent"][0] != plus(identity(), product(atom("A", 1, 2), atom("B", 2, 0)), -1),
            "wrong parent sign accepted")
    return {"status": "PASS_UNIVERSAL_DIRTY_PHASE_IDENTITIES", "identities": records,
            "block_types": list(TYPES), "symbol_types": symbols, "source_inputs": source_count,
            "strong_child_shape_identities": len(strong_eqs),
            "interface_controls": controls, "arithmetic_controls": ["order_retained", "repetitions_retained", "wrong_parent_sign_rejected"],
            "scope": "Universal rectangular-block polynomial identities only; no full induction or supplier verification."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", type=Path)
    args = ap.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as out:
            json.dump(result, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
    print(result["status"] + " identities=" + str(len(result["identities"])) + " sources=" + str(result["source_inputs"]))


if __name__ == "__main__":
    main()
