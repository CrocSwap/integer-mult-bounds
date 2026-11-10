#!/usr/bin/env python3
"""Independent full finite replay and direct 256-entry tensor witness check.

No author kernel import. Reconstructs with descending-column coset lifts,
then compares with the existing largest-section independent finite checker.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
M = runpy.run_path(str(HERE / "independent_square.py"))
need = M["need"]
E = lambda j: tuple(int(i == j) for i in range(16))


def main():
    path = HERE / "CERTIFICATE.json"
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == "44a950a62abec947b4c094c2c1f290bec2f8d7f41d3a108ab4c58b5bdfc46b56", "Frozen candidate")
    finite = M["replay"](path)
    data = json.loads(raw)
    basis = M["basis"]()
    sections = {0: 0}
    for j in range(15, -1, -1):
        column = M["synd"](E(j))
        if column not in sections:
            sections.update({label ^ column: mask ^ (1 << j)
                             for label, mask in list(sections.items())})
    need(len(sections) == 64, "Descending section surjective")
    lifts = [tuple(sum(basis[j][i] for j in range(16) if sections[s] & (1 << j))
                   for i in range(16)) for s in range(64)]
    reps = [M["add"](M["base"](q), lifts[s]) for q in range(64) for s in range(64)]
    need([M["label"](z) for z in reps] == list(range(4096)), "Every class represented")
    table = {}
    for source, values in data["cycles"]:
        z, c = reps[source], tuple(values)
        y = M["quarter"](M["add"](M["sw"](z), c))
        d = M["neg"](M["b"](c))
        for u, correction in ((z,c), (y,d), (M["k"](z),M["k"](c)), (M["k"](y),M["k"](d))):
            for v, f in ((u,correction), (M["neg"](u),M["neg"](correction))):
                label = M["label"](v)
                need(label not in table or table[label] == f, "No reconstruction collision")
                table[label] = f
    need(len(table) == 4096, "Full reconstructed table")
    packed = json.dumps([list(table[j]) for j in range(4096)], separators=(",",":")).encode()
    need(sha256(packed).hexdigest() == finite["table_sha256"], "Table digest agrees with full independent check")
    need(all(not any(table[j]) for j in range(64)), "Every integral-image fiber exact")

    def t(z):
        return M["quarter"](M["add"](M["sw"](z), table[M["label"](z)]))

    re = tuple((1,0,-1,0)[i.bit_count()%4] for i in range(16))
    im = tuple((0,-1,0,1)[i.bit_count()%4] for i in range(16))
    cycle, signed_labels, local = (0,3,15,12), set(), []
    for k, j in enumerate(cycle):
        z, y = E(j), E(cycle[(k+1)%4])
        c = tuple(4*a-b for a,b in zip(y,M["sw"](z)))
        need(table[M["label"](z)] == c and t(z) == y, "Forced transition in full table")
        need(sum(x*x for x in c) == 24, "Forced energy24")
        need(sum(a*b for a,b in zip(re,c)) == 0 and sum(a*b for a,b in zip(im,c)) == 0, "Both weighted sums zero")
        need(t(y) == M["k"](z), "Forced square")
        labels = [M["label"](z), M["label"](M["neg"](z))]
        signed_labels.update(labels)
        local.append({"basis":j,"next":cycle[(k+1)%4],"labels":labels,"energy":24})
    need(len(signed_labels) == 8 and all(j >= 64 for j in signed_labels), "No odd/K/zero-fiber collision")

    def d_phase(z):
        return tuple(((a,b),(b,-a),(-a,-b),(-b,a))[j.bit_count()%4] for j,(a,b) in enumerate(z))

    def f(z):
        inner = d_phase(z)
        r, i = t(tuple(a for a,_ in inner)), t(tuple(b for _,b in inner))
        middle = tuple((M["SIGNS"][j]*r[j], M["SIGNS"][j]*i[j]) for j in range(16))
        return tuple((-a,-b) for a,b in d_phase(middle))

    zero = ((0,0),)*16
    e0 = tuple((int(j == 0),0) for j in range(16))
    e3 = tuple((int(j == 3),0) for j in range(16))
    need(f(zero) == zero and f(e0) == e3, "F(e0)=e3 and F(0)=0")
    lam = tuple(((1,0),(0,1),(-1,0),(0,-1))[j.bit_count()%4] for j in range(16))
    x = tuple(tuple(lam[r] if c == 0 else (0,0) for c in range(16)) for r in range(16))

    def rows(a):
        return tuple(f(row) for row in a)

    def columns(a):
        images = tuple(f(tuple(a[r][c] for r in range(16))) for c in range(16))
        return tuple(tuple(images[c][r] for c in range(16)) for r in range(16))

    rc, cr = rows(columns(x)), columns(rows(x))
    delta = tuple(tuple((rc[r][c][0]-cr[r][c][0], rc[r][c][1]-cr[r][c][1]) for c in range(16)) for r in range(16))
    expected_row = list(d_phase(((1,0),)*16))
    expected_row[3] = (expected_row[3][0]+4, expected_row[3][1])
    need(delta == (tuple(expected_row),)+(zero,)*15, "All256 tensor defect entries")
    energy = sum(a*a+b*b for row in delta for a,b in row)
    need(energy == 24, "Sharp stronger fixed-witness floor")
    need(rc[0] == d_phase(((1,0),)*16), "Row-after-column output")
    need(cr[0] == tuple((-4*int(j == 3),0) for j in range(16)), "Column-after-row output")
    print(json.dumps({"status":"PASS_INDEPENDENT_SHARP_TENSOR_COMPOSITION", "finite_check":finite,
                      "forced_cycle":local,"F_e0":"e3","tensor_defect_squared":energy,
                      "tensor_entries_checked":256,"nonzero_defect_rows":[0],
                      "scope":"Fixed witness only; no worst-case tensor-discrepancy claim"},indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
