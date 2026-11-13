#!/usr/bin/env python3
"""Generate CERTIFICATES.json for research/cubic-odd-s-shift-floor.

    python3.12 -B research/cubic-odd-s-shift-floor/build.py           # write
    python3.12 -B research/cubic-odd-s-shift-floor/build.py --check   # compare

Deterministic.  It reuses verify.py's complete integer-shift search, takes
the lexicographically first four-node integer certificate with nodes in
[-12, 12] at each arity that needs four queries, and compiles the twenty
general-frame rows/weights below into explicit integer-shear programs.
The twenty rows and weights came from an external search that is not part
of acceptance; every certificate is accepted only by the exact checks.
Prepared by ahrazzle with substantial AI assistance. Apache-2.0.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import pathlib
import sys
from fractions import Fraction

PKG = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cubic_floor_verify", PKG / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

GENERAL = {
    48: ([(13, 184), (1, -40), (1, 24)], ["-47/1024", "-1081/512", "105421/1024"]),
    49: ([(5, -1217), (1, -141), (1, 115)], ["245/16384", "-118139/16384", "43757/8192"]),
    57: ([(5, -4), (1, 12), (1, 44)], ["-209/512", "11039/512", "7543/256"]),
    60: ([(5, 242), (1, -6), (1, 74)], ["295/1024", "-4307/128", "-2419/1024"]),
    69: ([(31, 963), (1, -35), (1, 29)], ["1955/65536", "-523549/65536", "-1803683/2048"]),
    84: ([(11, -1235), (1, 295), (7, 2193)], ["-17513/2097152", "557345/8192", "-348019/2097152"]),
    88: ([(5, 272), (1, -16), (1, 36)], ["29/32", "-1073/32", "-319/4"]),
    96: ([(5, -208), (1, -48), (1, 80)], ["-95/64", "36005/256", "11495/256"]),
    105: ([(13, 1396), (1, 68), (7, -36)], ["1001/262144", "4046315/65536", "-53599/262144"]),
    112: ([(19, -120), (1, 56), (1, 88)], ["-11/1024", "2933/128", "51985/1024"]),
    120: ([(5, 2781), (1, -263), (1, 761)], ["149345/1048576", "-11044985/1048576", "-1905785/262144"]),
    121: ([(37, 5067), (1, 47), (7, 73)], ["605/2097152", "2424235/16384", "-994015/2097152"]),
    124: ([(1, 259), (1, -765), (1, -253)], ["4195571/262144", "291059/262144", "-2243315/131072"]),
    132: ([(19, -20806), (1, 670), (7, -9390)], ["-9229/4194304", "201427/32768", "109385/4194304"]),
    133: ([(11, 1106), (1, -10), (1, 102)], ["77/512", "-41459/512", "-15257/128"]),
    148: ([(19, -635), (1, -249), (11, 1357)], ["-705257/67108864", "9538193/8388608", "3577049/67108864"]),
    169: ([(1, 340), (1, -52), (1, 204)], ["-169/16", "-31265/512", "36673/512"]),
    177: ([(1, -2765), (1, -2253), (1, 1331)], ["2024231/262144", "-431585/32768", "1428449/262144"]),
    184: ([(1, 84), (1, -160), (1, 64)], ["3013/4", "-253/32", "-23851/32"]),
    192: ([(7, 160), (1, 96), (1, 608)], ["-47177/65536", "2018297/8192", "35335/65536"]),
}


def fstr(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


# --------------------------------------------------- SL2(Z) shear words

def mat_mul(X, Y):
    return ((X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]),
            (X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]))


def op_matrix(kind: str, k: int):
    return ((1, k), (0, 1)) if kind == "a" else ((1, 0), (k, 1))


def _greedy(G):
    """Nearest-integer Euclid on the first column; -I is cleared with
    S^2, S = U_-1 L_1 U_-1.  Returns reduction ops E_1..E_m (E_m...E_1 G = I)."""
    red, M = [], G
    while M[1][0] != 0:
        (p, _), (r, _) = M
        if p == 0:
            o = ("a", r)
        elif abs(p) > abs(r):
            o = ("a", -round(Fraction(p, r)))
        else:
            o = ("b", -round(Fraction(r, p)))
        red.append(o)
        M = mat_mul(op_matrix(*o), M)
    if M[0][0] == -1:
        for o in [("a", -1), ("b", 1), ("a", -1)] * 2:
            red.append(o)
            M = mat_mul(op_matrix(*o), M)
    if M[0][1]:
        red.append(("a", -M[0][1]))
    return red


def _dfs(G, budget):
    best, stack = None, [(G, [])]
    while stack and budget > 0:
        budget -= 1
        M, red = stack.pop()
        (p, q), (r, s) = M
        if r == 0:
            if p == 1:
                red = red + ([("a", -q)] if q else [])
                if best is None or len(red) < len(best):
                    best = red
            continue
        if best is not None and len(red) + 1 >= len(best):
            continue
        cand = []
        if p == 0:
            cand.append(("a", r))
        elif abs(p) > abs(r):
            lo = -(p // r)
            cand += [("a", lo), ("a", lo - 1)] if p % r else [("a", lo)]
        else:
            lo = -(r // p)
            cand += [("b", lo), ("b", lo - 1)] if r % p else [("b", lo)]
        cand.sort(key=lambda o: abs(M[0][0] + o[1] * M[1][0]) if o[0] == "a"
                  else abs(M[1][0] + o[1] * M[0][0]), reverse=True)
        for o in cand:
            if o[1] != 0:
                stack.append((mat_mul(op_matrix(*o), M), red + [o]))
    return best


def word(G, budget: int = 300):
    """Shear ops o_1..o_n (('a', k): a += k*b, ('b', k): b += k*a) with
    O_n...O_1 = G: the shorter of a bounded rounding search and a greedy
    Euclid word, checked by multiplication."""
    red = _greedy(G)
    alt = _dfs(G, budget)
    if alt is not None and len(alt) < len(red):
        red = alt
    out = [(kind, -k) for kind, k in reversed(red)]
    acc = ((1, 0), (0, 1))
    for kind, k in out:
        acc = mat_mul(op_matrix(kind, k), acc)
    if acc != G:
        raise SystemExit("shear word does not multiply to G")
    return out


def inv(F):
    (a1, a2), (b1, b2) = F
    return ((b2, -a2), (-b1, a1))


def egcd(x: int, y: int):
    if y == 0:
        return (x, 1, 0) if x >= 0 else (-x, -1, 0)
    g, s, t = egcd(y, x % y)
    return g, t, s - (x // y) * t


def transitions(F, row, reg: str, T: int = 2):
    """All G in SL2(Z) (bounded completions) with (G F) having `row` in reg."""
    Fi = inv(F)
    g = row[0] * Fi[0][0] + row[1] * Fi[1][0]
    h = row[0] * Fi[0][1] + row[1] * Fi[1][1]
    d, s, t = egcd(g, h)
    if d != 1:
        raise SystemExit("non-primitive row")
    for k in range(-T, T + 1):
        if reg == "a":            # det [[g,h],[x,y]] = g y - h x = 1
            x, y = -t + k * g, s + k * h
            yield ((g, h), (x, y))
        else:                     # det [[x,y],[g,h]] = x h - y g = 1
            x, y = t + k * g, -s + k * h
            yield ((x, y), (g, h))


def compile_general(r: int, rows, weights):
    """Search query order, register, sign and completions for few shears."""
    best = None
    start = ((1, r), (0, 1))
    for order in itertools.permutations(range(3)):
        for regs in itertools.product("ab", repeat=3):
            for signs in itertools.product((1, -1), repeat=3):
                partial = [(start, [], 0)]
                for j, reg, sg in zip(order, regs, signs):
                    row = (sg * rows[j][0], sg * rows[j][1])
                    nxt = []
                    for F, ev, cost in partial:
                        if (F[0] if reg == "a" else F[1]) == row:
                            Gs = [((1, 0), (0, 1))]
                        else:
                            Gs = list(transitions(F, row, reg))
                        for G in Gs:
                            w = word(G) if G != ((1, 0), (0, 1)) else []
                            F2 = mat_mul(G, F)
                            q = -Fraction(weights[j]) * sg
                            e2 = ev + [("a+=b" if kd == "a" else "b+=a", k) for kd, k in w]
                            e2 = e2 + [("y+=a^3" if reg == "a" else "y+=b^3", q)]
                            nxt.append((F2, e2, cost + len(w)))
                    nxt.sort(key=lambda z: z[2])
                    partial = nxt[:12]
                for F, ev, cost in partial:
                    w = word(inv(F)) if F != ((1, 0), (0, 1)) else []
                    total = cost + len(w)
                    ev2 = ev + [("a+=b" if kd == "a" else "b+=a", k) for kd, k in w]
                    key = (total, json.dumps([[a, fstr(Fraction(b))] for a, b in ev2]))
                    if best is None or key < best[0]:
                        best = (key, ev2)
    return best[1]


def shift_program(r: int, nodes, weights):
    """Integer-shift program visiting nodes; r first and 0 last if present."""
    order = sorted(range(len(nodes)), key=lambda j: (nodes[j] != r, nodes[j] == 0, j))
    ev, cur = [], r
    for j in order:
        if nodes[j] != cur:
            ev.append(("a+=b", nodes[j] - cur))
            cur = nodes[j]
        ev.append(("y+=a^3", -weights[j]))
    if cur != 0:
        ev.append(("a+=b", -cur))
    return ev


def four_node_certificate(r: int, box: int = 12):
    S1 = Fraction(sum(range(r)))
    m = [Fraction(0), S1, Fraction(sum(i * i for i in range(r))), S1 * S1]
    for c in itertools.combinations(range(-box, box + 1), 4):
        A = [[Fraction(x) ** k for x in c] + [m[k]] for k in range(4)]
        for col in range(4):
            piv = next(i for i in range(col, 4) if A[i][col] != 0)
            A[col], A[piv] = A[piv], A[col]
            for i in range(4):
                if i != col and A[i][col] != 0:
                    f = A[i][col] / A[col][col]
                    A[i] = [x - f * y for x, y in zip(A[i], A[col])]
        q = [A[i][4] / A[i][i] for i in range(4)]
        if all(x != 0 and V.is_dyadic(x) for x in q):
            return list(c), q
    raise SystemExit(f"no four-node certificate at r={r}")


def ev_json(ev):
    return [[k, fstr(Fraction(x))] for k, x in ev]


def build() -> str:
    primes = V.primes_upto(70000)
    odd_s = [r for r in range(3, V.R_MAX + 1) if (r * (r - 1) // 2) % 2]
    table = {r: V.integer_shift_triples(r, primes) for r in odd_s}
    solvable = [r for r in odd_s if table[r]]
    impossible = [r for r in odd_s if not table[r]]
    certs = []
    for r in solvable:
        nodes = list(min(table[r], key=lambda t: (max(map(abs, t)), t)))
        w = V.node_weights(r, nodes)
        ev = shift_program(r, nodes, w)
        certs.append({"r": r, "kind": "three-shift", "rows": [[1, c] for c in nodes],
                      "weights": [fstr(x) for x in w], "shears": V.shear_count(ev),
                      "program": ev_json(ev)})
    for r in impossible:
        nodes, w = four_node_certificate(r)
        ev = shift_program(r, nodes, w)
        certs.append({"r": r, "kind": "four-shift", "rows": [[1, c] for c in nodes],
                      "weights": [fstr(x) for x in w], "shears": V.shear_count(ev),
                      "program": ev_json(ev)})
    for r, (rows, ws) in GENERAL.items():
        ev = compile_general(r, rows, ws)
        certs.append({"r": r, "kind": "general", "rows": [list(x) for x in rows],
                      "weights": ws, "shears": V.shear_count(ev), "program": ev_json(ev)})
    c6653 = json.loads((V.ROOT / V.PR6653_CERTS).read_text(encoding="utf-8"))
    p6653 = {c["r"] for c in c6653["certificates"]}
    pell = V.pell_arities(V.R_MAX)
    known = {r for r in range(3, V.R_MAX + 1)
             if V.covered_6653(r) or r in p6653 or r == V.PR7475_R24 or r in pell}
    after = known | set(GENERAL)
    data = {
        "schema_version": 1,
        "r_max": V.R_MAX,
        "conventions": {
            "defect": "D_r(A,B) = sum_{i<r} (A+iB)^3 - r A^3; each certificate states D_r = sum_j weights[j] * (rows[j][0] A + rows[j][1] B)^3",
            "program": "events appended after the r retained children y += a^3; a += b. a+=b k: a += k*b; b+=a k: b += k*a; y+=a^3 w: y += w*a^3; y+=b^3 w: y += w*b^3",
            "integer-shift": "PR6653 alphabet without reads of b: integer a += k*b only, queries y += q*a^3, q in Z[1/2]",
            "general": "determinant-one integer shears on a and b, dyadic queries on either named source (PR6212/PR7475 contract)",
        },
        "integer_shift_odd_s": {
            "arities": odd_s,
            "three_query_node_sets": {str(r): [list(t) for t in table[r]] for r in solvable},
            "three_query_impossible": impossible,
        },
        "open_after_package": {
            "odd_s": [r for r in impossible if r not in after],
            "even_s": [r for r in range(3, V.R_MAX + 1)
                       if (r * (r - 1) // 2) % 2 == 0 and r not in after],
        },
        "certificates": certs,
    }
    return json.dumps(data, indent=1) + "\n"


def main() -> None:
    text = build()
    out = PKG / "CERTIFICATES.json"
    if "--check" in sys.argv[1:]:
        if out.read_text(encoding="utf-8") != text:
            raise SystemExit("FAIL: CERTIFICATES.json differs from regeneration")
        print("PASS CERTIFICATES.json regenerates byte for byte")
    else:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
