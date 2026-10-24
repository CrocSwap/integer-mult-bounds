"""Check ordered matched bridges with exact rational matrices."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
N = 2
I = [[F(i == j) for j in range(N)] for i in range(N)]
ZERO = [[F(0) for _ in range(N)] for _ in range(N)]


def need(value, label):
    if not value:
        raise ValueError(label)


def add(a, b, c=1):
    return [[x + c*y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def mul(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def inv(a):
    n = len(a)
    rows = [list(row) + [F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        value = rows[j][j]
        rows[j] = [v/value for v in rows[j]]
        for i in range(n):
            if i != j:
                value = rows[i][j]
                rows[i] = [v-value*w for v, w in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def unit(k):
    return [[F(1+k*k), F(k)], [F(k), F(1)]]


def projection(k):
    q = [[F(1), F(k)], [F(k+1), F(1+k*(k+1))]]
    return mul(mul(q, [[F(1), F(0)], [F(0), F(0)]]), inv(q))


def identity_blocks(m):
    return [[I if i == j else ZERO for j in range(2*m)] for i in range(2*m)]


def row_add(state, dst, src, op=I, c=1):
    state[dst] = [add(a, mul(op, b), c) for a, b in zip(state[dst], state[src])]


def row_map(state, row, op):
    state[row] = [mul(op, b) for b in state[row]]


def block_product(a, b):
    n = len(a)
    out = [[ZERO for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] = add(out[i][j], mul(a[i][k], b[k][j]))
    return out


def run(a, g, p, w, t, c, v, mutation=None):
    m = len(a)
    state = identity_blocks(m)
    for i in range(m-2, -1, -1):
        row_add(state, 2*i, 2*i+2, c=-1)
    row_map(state, 1, c)
    row_add(state, 1, 0, v)
    for i in range(m):
        x, y = 2*i, 2*i+1
        ax = [mul(a[i], block) for block in state[x]]
        old_y = state[y]
        state[x] = [add(mul(add(I, p[i], -1), b), e, -1) for b, e in zip(ax, old_y)]
        state[y] = [add(e, mul(p[i], b)) for b, e in zip(ax, old_y)]
        if i+1 < m:
            row_map(state, x+2, a[i])
            row_add(state, x, x+2)
            row_add(state, y+2, y, w[i], -1)
        state[y] = [mul(g[i], add(b, e)) for b, e in zip(state[x], state[y])]
        if i+1 < m:
            if mutation == "early_reset":
                row_map(state, x+2, inv(a[i]))
            row_add(state, x, x+2, c=-1)
            row_add(state, y+2, y, t[i])
            if mutation != "early_reset":
                row_map(state, x+2, inv(a[i]))
    for i in range(m-1, 0, -1):
        row_add(state, 2*i, 2*i-2, add(I, p[i-1], -1) if mutation == "old_tail" else w[i-1])
    row_map(state, 0, inv(c))
    return state


def formulas(a, g, p, w, t, c, v):
    m = len(a)
    e = [mul(gg, aa) for aa, gg in zip(a, g)]
    h = []
    for i in range(m):
        row = []
        for j in range(m):
            if not i:
                block = mul(inv(c), add(mul(add(I, p[0], -1), a[0]), v, -1))
                block = [[(-1)**j*x for x in r] for r in block]
            else:
                block = ZERO
                if j >= i:
                    block = add(block, mul(add(I, p[i], -1), a[i]), (-1)**(j-i))
                if j >= i-1:
                    block = add(block, mul(w[i-1], a[i-1]), (-1)**(j-i+1))
                if j == i-1:
                    block = add(block, mul(t[i-1], e[i-1]), -1)
            row.append(block)
        h.append(row)
    return e, h


def check_case(m, kind):
    a, g = [unit(i+1) for i in range(m)], [unit(-i-2) for i in range(m)]
    p = [projection(i+1) if kind != "non_idempotent" else add(projection(i+1), I) for i in range(m)]
    w = [unit(i+3) if kind in ("general", "non_idempotent") else add(I, p[i+1], -1) for i in range(m-1)]
    t = [unit(-i-4) if kind in ("general", "non_idempotent") else (ZERO if kind == "future_zero" else w[i]) for i in range(m-1)]
    c, v = unit(3), [[F(2), F(-3)], [F(5), F(7)]]
    state = run(a, g, p, w, t, c, v)
    e, h = formulas(a, g, p, w, t, c, v)
    terminal, inverse = identity_blocks(m), identity_blocks(m)
    for i in range(m):
        for j in range(2*m):
            need(state[2*i+1][j] == (e[i] if j == 2*i else ZERO), "Retired output")
            expected = h[i][j//2] if j % 2 == 0 else (add(ZERO, I, -1) if j == 2*i+1 else ZERO)
            need(state[2*i][j] == expected, "Completed output")
        terminal[2*i][2*i], inverse[2*i][2*i] = e[i], inv(e[i])
        for j in range(m):
            terminal[2*i+1][2*j] = add(ZERO, h[i][j], -1)
            inverse[2*i+1][2*j] = mul(h[i][j], inv(e[j]))
            if i and kind.startswith("future"):
                need(mul(p[i], h[i][j]) == ZERO, "Future projection removes selected response")
    need(block_product(terminal, inverse) == identity_blocks(m), "Right inverse")
    need(block_product(inverse, terminal) == identity_blocks(m), "Left inverse")
    if m > 1:
        need(run(a, g, p, w, t, c, v, "early_reset") != state, "Early reset control")
        need(run(a, g, p, w, t, c, v, "old_tail") != state, "Unmatched tail control")
    return {"pairs": m, "family": kind, "endpoint_blocks": (2*m)**2}


def signed_checks():
    pi = [[F(1), F(0)], [F(0), F(0)]]
    for i in range(1, 6):
        bs, ds, bt, dt = F(13*i), F(1, i), F(13*(i+1)), F(1, i+1)
        a = [[F(12), -bs], [-ds, F(1)]]
        s = [[F(-1), -bs], [-ds, F(1)-ds*bs]]
        st = [[F(-1), -bt], [-dt, F(1)-dt*bt]]
        p = [[F(1), bs], [F(0), F(0)]]
        pt = [[F(1), bt], [F(0), F(0)]]
        need(mul(s, a) == I and mul(a, s) == I, "Signed inverse")
        need(mul(p, a) == add(ZERO, pi, -1), "Original selected return")
        need(mul(p, p) == p, "Oblique projection")
        need(mul(add(I, p, -1), a) == add(a, pi), "Cheap return factor")
        e = mul(st, a)
        need(e[1] == [F(0)-ds+dt*e[0][0], F(1)+dt*e[0][1]], "Ordinary E graph")
        need(mul(pt, a) == add(ZERO, mul(pi, e), -1), "Productive query quotient")
    return 5


def main():
    tests = [check_case(m, kind) for kind in ("general", "non_idempotent", "future_zero", "future_matched") for m in range(1, 7)]
    signed = signed_checks()
    root = HERE.parent
    sources = [root / "encoded-controller/PROJECTION-RETIREMENT.md", root / "interface-proof/projection-retirement-review/REVIEW.md", root / "encoded-controller/SELECTED-SOURCE-RETIREMENT.md", root / "interface-proof/selected-source-retirement-review/REVIEW.md"]
    receipt = {
        "status": "PASS_GENERAL_MATCHED_BRIDGES",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_sha256": sha256((HERE / "GENERAL-BRIDGES.md").read_bytes()).hexdigest(),
        "source_pins": {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in sources},
        "tests": tests,
        "signed_specializations": signed,
        "method": "Exact Fraction matrices; direct event replay and independent endpoint formula; no producer imports.",
        "controls": ["Wrong final bridge coefficient", "Early idle-X reset"],
        "scope": "Ordered algebra only. The proof covers all positive pair counts. Separate native bridge and local-word contracts are required. No complete decoder or kappa claim."
    }
    (HERE / "CHECKS.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
