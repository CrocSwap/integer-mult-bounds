# Finite inputs of the kappa <= 3 Carrier Lemma (README section 4) and of the Parity Lemma.   usage: python carrier3.py data80.txt
# Reads the 112 labels, the 8 frame labels and the 112 line vectors (doubled E8 coordinates, true inner product = dot // 4) from the data file written by gen.py.
import sys, itertools
L = open(sys.argv[1]).read().split('\n')
LAB = list(map(int, L[0].split())); ZL = list(map(int, L[1].split()))
P = [tuple(map(int, L[2 + i].split())) for i in range(112)]
dot = lambda a, b: sum(x * y for x, y in zip(a, b)) // 4
par = lambda x: bin(x).count('1') & 1
frame = []
for k in range(4):
    for sg in (2, -2):
        v = [0] * 8; v[2 * k] = 2; v[2 * k + 1] = sg; frame.append(tuple(v))
assert len(LAB) == 112 and len(set(LAB)) == 112 and len(ZL) == 8 and len(set(ZL)) == 8
# the form beta on F2^9 = F2 + E8/2E8, given by the Gram matrix of the Z-basis (simple roots of gen.py) mod 2
simple = [(1,-1,-1,-1,-1,-1,-1,1),(2,2,0,0,0,0,0,0),(-2,2,0,0,0,0,0,0),(0,-2,2,0,0,0,0,0),(0,0,-2,2,0,0,0,0),(0,0,0,-2,2,0,0,0),(0,0,0,0,-2,2,0,0),(0,0,0,0,0,-2,2,0)]
G = [[dot(a, b) % 2 for b in simple] for a in simple]
def beta(u, v):
    r = (u & 1) * (v & 1)
    for i in range(8):
        for j in range(8):
            r ^= ((u >> (i + 1)) & 1) & ((v >> (j + 1)) & 1) & G[i][j]
    return r & 1
bad = 0
ip = [[dot(P[s], P[t]) for t in range(112)] for s in range(112)]
# (1) beta(l_s, l_t) = 1 + <r_s, r_t> mod 2 for every pair (including s = t); distinct lines have <r_s, r_t> in {0, +-1}
ok1 = all(beta(LAB[s], LAB[t]) == (1 + ip[s][t]) % 2 for s in range(112) for t in range(112))
ok2 = all(ip[s][t] in (0, 1, -1) for s in range(112) for t in range(112) if s != t) and all(ip[s][s] == 2 for s in range(112))
print(('PASS' if ok1 and ok2 else 'FAIL') + ' beta(l_s,l_t) = 1 + <r_s,r_t> mod 2 on all 112x112 pairs; distinct lines have inner product 0, +-1'); bad += not (ok1 and ok2)
# (2) frame labels
okz = all(beta(ZL[i], ZL[j]) == 1 for i in range(8) for j in range(8)) and not set(ZL) & set(LAB)
print(('PASS' if okz else 'FAIL') + ' frame labels z_i: beta(z_i,z_j) = 1 for all i,j (so z_i is not in the flat W_j = z_j^perp), and no z_i is the label of a P112 line'); bad += not okz
# (3) cocircuit sizes
def span_rank(vs):
    bs = []
    for x in vs:
        for b in bs: x = min(x, x ^ b)
        if x: bs.append(x)
    return len(bs)
def min_cocircuit(labs):
    # smallest positive number of lines of `labs` outside a hyperplane (functional phi != 0 on F2^9): deleting fewer lines never lowers the rank
    best = 10 ** 9
    for phi in range(1, 512):
        c = sum(par(phi & x) for x in labs)
        if 0 < c < best: best = c
    return best
rt = []
for t in range(112):
    off = [s for s in range(112) if ip[s][t] != 0]
    offt = [LAB[s] for s in off if s != t]
    assert len(off) == 53 and span_rank([LAB[s] for s in off]) == 9 and span_rank(offt) == 8
    assert all(beta(LAB[t], x) == 0 for x in offt)                       # span(Off(r_t) minus t) = l_t^perp = W_t
    assert [s for s in range(112) if beta(LAB[t], LAB[s]) == 0] == [s for s in off if s != t]   # l_s in W_t  <=>  s in Off(r_t), s != t
    rt.append(min_cocircuit(offt))
okr = min(rt) >= 5
print(('PASS' if okr else 'FAIL') + ' root r_t (all 112): |Off| = 53, label rank 9, t is a coloop, span(Off minus t) = W_t = l_t^perp contains exactly the labels of Off minus t; every cocircuit of the 52 other lines has size >= 5 (minimum %d): deleting <= 4 lines never lowers the rank' % min(rt)); bad += not okr
ft = []
for j in range(8):
    off = [s for s in range(112) if dot(P[s], frame[j]) != 0]
    labs = [LAB[s] for s in off]
    assert len(off) == 56 and span_rank(labs) == 8 and all(beta(ZL[j], x) == 0 for x in labs)
    ft.append(min_cocircuit(labs))
okf = min(ft) >= 5
print(('PASS' if okf else 'FAIL') + ' frame direction f_j (all 8): |Off| = 56, label rank 8 = W_j; every cocircuit has size >= 5 (minimum %d)' % min(ft)); bad += not okf
# (4) Parity Lemma: pairwise non-orthogonal lines
adj = [sum(1 << t for t in range(112) if t != s and ip[s][t] != 0) for s in range(112)]
tri = quad = 0; tri_z = quad_0 = 0
for a in range(112):
    for b in range(a + 1, 112):
        if not (adj[a] >> b) & 1: continue
        cab = adj[a] & adj[b]
        for c in range(b + 1, 112):
            if not (cab >> c) & 1: continue
            tri += 1; sm = LAB[a] ^ LAB[b] ^ LAB[c]
            if sm in ZL: tri_z += 1
            cabc = cab & adj[c]
            for d in range(c + 1, 112):
                if (cabc >> d) & 1:
                    quad += 1
                    if sm ^ LAB[d] == 0: quad_0 += 1
okp = tri_z == 0 and quad_0 == 0 and tri > 0 and quad > 0
print(('PASS' if okp else 'FAIL') + ' Parity Lemma: %d pairwise non-orthogonal triples, none with label sum in {z_i}; %d pairwise non-orthogonal quadruples, none with label sum 0' % (tri, quad)); bad += not okp
# Parity (ii), form used in the Carrier Lemma: no four lines with label sum 0 has a line non-orthogonal to the other three
from collections import defaultdict
px = defaultdict(list)
for a in range(112):
    for b in range(a + 1, 112): px[LAB[a] ^ LAB[b]].append((a, b))
quads = set()
for x, prs in px.items():
    for (a, b), (c, d) in itertools.combinations(prs, 2):
        if len({a, b, c, d}) == 4: quads.add(tuple(sorted((a, b, c, d))))
badq = [q for q in quads if any(all(ip[v][u] != 0 for u in q if u != v) for v in q)]
okq = len(quads) > 0 and not badq
print(('PASS' if okq else 'FAIL') + ' Parity (ii) as used in the Carrier Lemma: %d quadruples of lines with label sum 0, none has a line non-orthogonal to the other three' % len(quads)); bad += not okq
# control: the statement is about non-orthogonality, not vacuous: triples (not pairwise non-orthogonal) with label sum z_i exist
ctl = sum(1 for a, b, c in itertools.combinations(range(112), 3) if LAB[a] ^ LAB[b] ^ LAB[c] in ZL)
print(('PASS' if ctl > 0 else 'FAIL') + ' control: %d triples of P112 lines have label sum in {z_i} (necessarily with an orthogonal pair)' % ctl); bad += not ctl > 0
print('carrier3: %d failing' % bad); sys.exit(1 if bad else 0)
