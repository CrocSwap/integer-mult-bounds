"""Build the 26-stage frame certificate FRAMES.json (standard library only).

Each frame block is an integer 112x4 matrix V_j with M^T V_j = 0 and V_j
zero on the coordinates E = (0, 1, 2, 4). The cumulative inverse frames are
W_j = I + V_j E (W_1 = I). Usage: build_frames.py OUTPUT.json
"""
import itertools
import json
import pathlib
import sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
E_COORDS = (0, 1, 2, 4)
N, MODES, STAGES = 112, 8, 26


def load_rows():
    cols = json.loads(FIXTURE.read_text())["mode_columns"]
    return [tuple(cols[j][i] for j in range(MODES)) for i in range(N)]


def det(rows):
    a = [[Fraction(x) for x in r] for r in rows]
    d = Fraction(1)
    for c in range(len(a)):
        p = next((r for r in range(c, len(a)) if a[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            a[c], a[p] = a[p], a[c]
            d = -d
        d *= a[c][c]
        for r in range(c + 1, len(a)):
            f = a[r][c] / a[c][c]
            a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return d


def solve(rows_t, rhs):
    """Solve B c = rhs for square B given as list of columns' transpose rows."""
    n = len(rhs)
    a = [[Fraction(rows_t[k][i]) for k in range(n)] + [Fraction(rhs[i])] for i in range(n)]
    for c in range(n):
        p = next(r for r in range(c, n) if a[r][c] != 0)
        a[c], a[p] = a[p], a[c]
        a[c] = [x / a[c][c] for x in a[c]]
        for r in range(n):
            if r != c and a[r][c] != 0:
                f = a[r][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return [a[i][n] for i in range(n)]


def main(out_path):
    rho = load_rows()
    free = [i for i in range(N) if i not in E_COORDS]
    # Lattice Lambda = M^T Z^112 has index 16; find 8 free rows forming a basis.
    basis = None
    for combo in itertools.combinations(free[:40], MODES):
        if abs(det([rho[i] for i in combo])) == 16:
            basis = combo
            break
    assert basis is not None
    brows = [rho[i] for i in basis]

    def coords(vec):
        c = solve(brows, vec)
        assert all(x.denominator == 1 for x in c)
        return [int(x) for x in c]

    phi = {i: sum((coords(rho[i])[k] & 1) << k for k in range(MODES)) for i in free}
    # F2 kernel of phi on free coordinates (red K restricted to free coords).
    piv, kern = {}, []
    for i in free:
        v, u = phi[i], 1 << i
        while v:
            p = v.bit_length() - 1
            if p not in piv:
                piv[p] = (v, u)
                break
            v ^= piv[p][0]
            u ^= piv[p][1]
        if v == 0:
            kern.append(u)
    # Integer lifts supported on free coordinates.
    lifts = []
    for u in kern:
        supp = [i for i in range(N) if (u >> i) & 1]
        tot = [sum(rho[i][k] for i in supp) for k in range(MODES)]
        assert all(x % 2 == 0 for x in tot)
        c = coords([x // 2 for x in tot])
        vec = {i: 1 for i in supp}
        for k, i in enumerate(basis):
            vec[i] = vec.get(i, 0) - 2 * c[k]
        vec = {i: x for i, x in vec.items() if x}
        assert all(sum(x * rho[i][m] for i, x in vec.items()) == 0 for m in range(MODES))
        lifts.append(vec)
    # Keep lifts independent from im(M mod 2).
    span = {}

    def add(x):
        while x:
            p = x.bit_length() - 1
            if p not in span:
                span[p] = x
                return True
            x ^= span[p]
        return False

    for j in range(MODES):
        add(sum((rho[i][j] & 1) << i for i in range(N)))
    chosen = [v for v in lifts if add(sum(1 << i for i, x in v.items() if x & 1))]
    assert len(chosen) == 4 * (STAGES - 1), len(chosen)
    blocks = [chosen[4 * b:4 * b + 4] for b in range(STAGES - 1)]
    payload = {
        "schema": "refined-recovery-longer-chains-frames-v1",
        "E_coords": list(E_COORDS),
        "stages": STAGES,
        "lattice_basis_rows": list(basis),
        "V_blocks": [[sorted([int(i), int(x)] for i, x in col.items()) for col in blk] for blk in blocks],
    }
    pathlib.Path(out_path).write_text(json.dumps(payload, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: build_frames.py OUTPUT.json")
    main(sys.argv[1])
