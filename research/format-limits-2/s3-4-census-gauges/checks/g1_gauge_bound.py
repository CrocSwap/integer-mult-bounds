"""G1/G2: gauge-free cold-end bound per block on the frozen #645 Gauge44 word (SYN-2 tool, adapted: inputs from ../inputs, no output file).
bound_b = |Q_b| - rank Clean[Q_b] (clean = source columns); Lfix = |Q_b| - rank M[Q_b, protected]; LK = rank of the attained cold-unit pairing (exact rationals)."""
import sys, json, gzip
from common import *
from fractions import Fraction as Q
w = load_json('pr645', 'FULL-WORD.json.gz'); v = w['report']['v']; n = 2*v + w['report']['R']
N = list(range(v)) + list(range(2*v, n)); ix = {x: i for i, x in enumerate(N)}
def basis(vs):
    d = {}
    for a in vs:
        for k in sorted(d, reverse=True):
            if a >> k & 1: a ^= d[k]
        if a:
            k = a.bit_length()-1
            for j in d:
                if d[j] >> k & 1: d[j] ^= a
            d[k] = a
    return tuple(d[k] for k in sorted(d, reverse=True))
inside = lambda a, b: basis(list(a)+list(b)) == b
regs = lambda e: e[1:3] if e[0] == 'add' else e[1:2]
def apply(e, M):
    t = ix[e[1]]
    if e[0] == 'add':
        s = ix[e[2]]; q = Q(e[3], e[4])
        for j, a in list(M[s].items()):
            x = M[t].get(j, Q(0)) + q*a
            if x: M[t][j] = x
            else: M[t].pop(j, None)
    else:
        q = Q(e[2], e[3]); M[t] = {j: q*a for j, a in M[t].items()}
def rank(rows):
    rows = [dict(r) for r in rows if r]; r = 0; piv = {}
    for row in rows:
        row = {k: x for k, x in row.items() if x}
        for c, prow in piv.items():
            if c in row:
                q = row[c]
                for k, x in prow.items():
                    y = row.get(k, Q(0)) - q*x
                    if y: row[k] = y
                    else: row.pop(k, None)
        if row:
            c = min(row); q = row[c]; row = {k: x/q for k, x in row.items()}
            for c2, prow in piv.items():
                if c in prow:
                    q2 = prow[c]
                    for k, x in row.items():
                        y = prow.get(k, Q(0)) - q2*x
                        if y: prow[k] = y
                        else: prow.pop(k, None)
            piv[c] = row; r += 1
    return r
ntail = 34
tail = [w['cleanup'][i][:-1]+[list(f)] for i, f in w.get('early_cleanup', [])][:ntail]
mainN = [e for e in w['A']+w['B'] if not v <= e[1] < 2*v]
M = [{i: Q(1)} for i in range(len(N))]
for e in mainN+tail: apply(e, M)
cur = {x: (w['ports'][x],) if x < v else basis(w.get('start_extra', {}).get(str(x), [])) for x in N}
for e in w['A']+w['B']+tail:
    for x in regs(e):
        if x in cur: cur[x] = basis(e[-1])
enter = set(map(int, w.get('start_extra', {})))
src = set(range(v)); prot = set(ix[x] for x in N if x < v or x in enter); srci = set(ix[x] for x in src)
mods = load_json('pr531', 'PACKET-PROGRAMS.json.gz'); proto = load_json('pr531', 'PROTOTYPE.json.gz')
def inverse(e):
    e=list(e)
    if e[0]=='add': e[3]=-e[3]
    else: e[2],e[3]=e[3],e[2]
    return e
MI = [{i: Q(1)} for i in range(len(N))]
for e in reversed(mainN+tail): apply(inverse(e), MI)
def nullsp(A, nc):
    # A: list of dict rows over 0..nc-1 ; return basis of right kernel as list of dict columns
    piv = {}
    for row in A:
        row = {k: x for k, x in row.items() if x}
        for c, prow in piv.items():
            if c in row:
                q = row[c]
                for k, x in prow.items():
                    y = row.get(k, Q(0)) - q*x
                    if y: row[k] = y
                    else: row.pop(k, None)
        if row:
            c = min(row); q = row[c]; row = {k: x/q for k, x in row.items()}
            for c2, prow in piv.items():
                if c in prow:
                    q2 = prow[c]
                    for k, x in row.items():
                        y = prow.get(k, Q(0)) - q2*x
                        if y: prow[k] = y
                        else: prow.pop(k, None)
            piv[c] = row
    free = [j for j in range(nc) if j not in piv]
    out = []
    for f in free:
        col = {f: Q(1)}
        for c, prow in piv.items():
            if prow.get(f): col[c] = -prow[f]
        out.append(col)
    return out
tot = dict(Q=0, Lfix=0, Lgauge=0, LK=0)
out = []
for b, mod in enumerate(mods):
    ss = mod['receipt']['source_lines']; F = basis([proto['binary_ports'][s] for s in ss])
    I = [ix[x] for x in N if inside(cur[x], F)]
    rp = rank([{j: a for j, a in M[i].items() if j in prot} for i in I])
    rs = rank([{j: a for j, a in M[i].items() if j in srci} for i in I])
    regsI = sorted(N[i] for i in I)
    pl = sorted(prot)
    Ct = [{k: M[I[k]][j] for k in range(len(I)) if M[I[k]].get(j)} for j in pl]   # C^T rows -> left kernel of C
    Lb = nullsp(Ct, len(I))
    Ab = [{k: MI[j].get(I[k]) for k in range(len(I)) if MI[j].get(I[k])} for j in pl]
    Kb = nullsp([r for r in Ab if r], len(I))
    LK = rank([{c: sum((l.get(k, Q(0))*kc.get(k, Q(0)) for k in range(len(I))), Q(0)) for c, kc in enumerate(Kb)} for l in Lb]) if Lb and Kb else 0
    tot['LK'] += LK
    LKb = LK
    # near-miss registers: end frame inside F + one extra dim
    near = sorted(x for x in N if not inside(cur[x], F) and len(basis(list(cur[x])+list(F))) == len(F)+1)
    tot['Q'] += len(I); tot['Lfix'] += len(I)-rp; tot['Lgauge'] += len(I)-rs
    out.append(dict(LK=LKb, block=b, rankF=len(F), Q=len(I), rank_prot=rp, rank_src=rs, Lfix=len(I)-rp, Lgauge=len(I)-rs, regs=regsI, near=near))
    if 0: print(b, 'dimL', len(Lb), 'dimK', len(Kb), 'rankLK', LK, 'rkF', len(F), '|Q|', len(I), 'rk prot', rp, 'rk src', rs, 'Q:', regsI, 'near(+1 dim):', near, flush=True)

sI = sorted(o['Q'] for o in out)
check('G1 14 blocks: 6 with |I| = 6, 8 with |I| = 8; sum |I| = 100 (K492 factory)', sI == [6]*6 + [8]*8 and tot['Q'] == 100, sI)
check('G1 rank of the 4 pinned totals: rank Clean[I_b] = rank M[I_b, protected] = 4 in all 14 blocks', all(o['rank_src'] == 4 and o['rank_prot'] == 4 and o['rankF'] == 4 for o in out))
check('G1 gauge-free bound N_cold <= sum_b(|I_b| - 4) = 44 (fixed-content value Lfix = gauge value = 44)', tot['Lgauge'] == 44 and tot['Lfix'] == 44 and sum(o['Q'] - 4 for o in out) == 44, tot)
check('G2 attained cold units (rank LK) = 44 = the bound: 2 in each short block, 4 in each |I| = 8 block', tot['LK'] == 44 and sorted(o['LK'] for o in out) == [2]*6 + [4]*8, [o['LK'] for o in out])
finish()
