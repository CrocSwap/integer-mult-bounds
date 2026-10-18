"""Part B: tape-model count for the tensor-diagonal scan of TENSOR-COMPILER.md sec. 6 / note line 120.

Model: fixed number of tapes. Coefficient tape holds g one-axis tables (N cells each) in axis order; a suffix-product
tape holds P_1..P_{g-1}. A head move is one cell. The data stream is read once sequentially (not counted below).
The record layout is a list of fields, fastest first: group axes ('a',k) appear in order k=0..g-1, spectator fields
('s',M) may be interleaved anywhere (inner, between, outer). The diagonal is d(x)=prod_k d_k(x_k) (exact integers),
checked against the naive product for every record. We report coefficient/suffix head moves and multiplications
per record, and compare with the naive method (g reads + g-1 products per record).
"""
import json, math, random, sys

def run(N, g, layout, seed=0):
    rng = random.Random(seed)
    tables = [[rng.randint(2, 9) for _ in range(N)] for _ in range(g)]
    sizes = [N if f[0] == 'a' else f[1] for f in layout]
    V = math.prod(sizes)
    pos = {f[1]: i for i, f in enumerate(layout) if f[0] == 'a'}
    hc = 0; hs = 0; cm = 0; sm = 0; mults = 0
    def readc(k, i):
        nonlocal hc, cm
        c = k * N + i; cm += abs(hc - c); hc = c; return tables[k][i]
    def touchs(j):           # suffix cell j (1..g-1) stored at cell j-1
        nonlocal hs, sm
        c = j - 1; sm += abs(hs - c); hs = c
    x = [0] * len(layout)
    # initial suffix products
    P = [1] * (g + 1)
    for j in range(g - 1, 0, -1):
        P[j] = readc(j, 0) * P[j + 1]; mults += 1; touchs(j)
    maxd = 0
    for r in range(V):
        # record value
        i0 = x[pos[0]]
        d0 = readc(0, i0)
        val = d0 * P[1] if g > 1 else d0; mults += 1
        if g > 1: touchs(1)
        naive = math.prod(tables[k][x[pos[k]]] for k in range(g))
        assert val == naive
        # odometer increment over all fields
        f = 0
        while f < len(layout):
            x[f] += 1
            if x[f] < sizes[f]: break
            x[f] = 0; f += 1
        if f == len(layout): break
        # field f incremented, fields < f wrapped. Lowest group axis whose value changed from the top:
        changed = [layout[i][1] for i in range(f + 1) if layout[i][0] == 'a']
        if not changed: continue
        top = max(changed)            # highest group axis changed (incremented or wrapped)
        if top == 0: continue          # only axis 0 changed: next record reads table 0 sequentially
        for j in range(top, 0, -1):    # recompute P_top..P_1
            P[j] = readc(j, x[pos[j]]) * P[j + 1]; mults += 1; touchs(j)
            maxd = max(maxd, top)
    return dict(N=N, g=g, layout=[f"{f[0]}{f[1]}" for f in layout], V=V,
                coef_moves_per_record=cm / V, suffix_moves_per_record=sm / V, mults_per_record=mults / V,
                naive_mults_per_record=g - 1, naive_table_reads_per_record=g,
                bound_2sum_kN_over_Nk=2 * sum(k * N / N**k for k in range(1, g)) + 1)

res = []
for N in (2, 4, 8):
    for g in range(2, 21):
        if N**g > 1 << 18: break
        res.append(run(N, g, [('a', k) for k in range(g)]))
# spectators interleaved (inner, between, outer)
res.append(run(2, 10, [('s', 3)] + [('a', k) for k in range(10)]))
res.append(run(2, 10, [('a', 0), ('a', 1), ('s', 5)] + [('a', k) for k in range(2, 10)] + [('s', 2)]))
res.append(run(4, 6, [('a', 0), ('s', 2), ('a', 1), ('a', 2), ('s', 3), ('a', 3), ('a', 4), ('a', 5)]))
for r in res: print(json.dumps(r))
json.dump(res, open(sys.argv[1], 'w'), indent=1)
