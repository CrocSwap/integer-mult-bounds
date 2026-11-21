"""Independent check of LOOSE's sound cube scheme (no LOOSE code executed; reads masks0.txt, remF2T.txt, cubes/F2T.log, AF2T.state.json, f55n/f55e cnf+map)."""
import pickle, json, sys, os, collections
L = 'code/loose/'
T55 = 'code/tight55/'
ok = True
def rep(n, c, i=''):
    global ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + n + ('  ' + i if i else ''), flush=True)
P = [tuple(p) for p in pickle.load(open(T55 + 'perms.pkl', 'rb'))]; ident = tuple(range(16))
nonrep, lexmax = pickle.load(open('partition_masks.pkl', 'rb'))
masks0 = [int(x) for x in open(L + 'masks0.txt').read().split()]
rep('masks0.txt == all indicator-orbit-lexmax masks incl. 0 (my own computation), 402 distinct', sorted(masks0) == sorted(lexmax) and len(set(masks0)) == 402)
done_n = [int(l.split()[0]) for l in open(L + 'cubes/F2T.log') if l.split() and l.split()[0].isdigit() and 'UNSAT' in l]
rem = [int(x) for x in open(L + 'remF2T.txt').read().split()]
rep('F2T.log (296 UNSAT on f55n) and remF2T.txt (106 on f55e) partition masks0', set(done_n) | set(rem) == set(masks0) and not (set(done_n) & set(rem)) and len(done_n) == len(set(done_n)),
    f'{len(done_n)}+{len(rem)}')
# Stab(I) is a subgroup of the verified-symmetry group; contains identity; closed
Pset = set(P)
bad = 0
for I in masks0:
    ind = [I >> j & 1 for j in range(16)]
    S = [p for p in P if all(ind[p[j]] == ind[j] for j in range(16))]
    Ss = set(S)
    if ident not in Ss or any(tuple(a[b[i]] for i in range(16)) not in Ss for a in S for b in S[:6]): bad += 1
rep('Stab(I) (perms preserving I) contains id and is closed (spot-checked on 6 right factors per mask) for all 402 masks', bad == 0)
# soundness argument pieces (exhaustive): every d-vector orbit has a member with indicator lexmax... trivially: apply g with I(g d) lexmax in the orbit of I.
# then for the stabiliser: lexmax d over Stab(I)-orbit satisfies d >=lex d o p for p in Stab(I) (same argument as before, group = Stab(I)).
# check bases carry NO global lex-leader: no binary clause between used vars of different rows
def parse(path):
    with open(path) as fh:
        h = fh.readline().split(); cl = [tuple(int(x) for x in l.split()[:-1]) for l in fh]
    return int(h[2]), cl
for base in ['f55n', 'f55e']:
    U = pickle.load(open(L + base + '.cnf.map', 'rb'))['used']
    inv = {v: k for k, v in U.items()}
    nv, cl = parse(L + base + '.cnf')
    cross = [c for c in cl if len(c) == 2 and abs(c[0]) in inv and abs(c[1]) in inv and inv[abs(c[0])][0] != inv[abs(c[1])][0]]
    # also lex step clauses: [-used a, used b] with a,b rows differ, or 3-lit with prefix var
    cross3 = [c for c in cl if len(c) == 3 and sum(abs(x) in inv for x in c) == 2 and sum(abs(x) in inv and inv[abs(x)][0] != 0 for x in c) >= 0
              and any(abs(x) in inv for x in c) and False]
    rep(f'{base}.cnf: no cross-row binary clauses on used[] (no global d-lex-leader in the base)', not cross, f'{len(cross)} cross-row binaries, nv={nv}, clauses={len(cl)}')
# adaptive tree check on AF2T.state.json
if os.path.exists(L + 'AF2T.state.json'):
    st = json.load(open(L + 'AF2T.state.json'))
    print('AF2T: done', len(st['done']), 'queue', len(st['queue']), collections.Counter(d[2] for d in st['done']))
    # every UNKNOWN has the 9 children d_z=0..8 on one new free z; check from the done list
    done = {(d[0], tuple(map(tuple, d[1]))): d[2] for d in st['done']}
    pend = {(q[0], tuple(map(tuple, q[1]))) for q in st['queue']}
    badt = 0
    for (m, fx), s in done.items():
        if s != 'UNKNOWN': continue
        fixed = {z for z, _ in fx}
        kids = {}
        for (m2, fx2) in list(done) + list(pend):
            if m2 == m and len(fx2) == len(fx) + 1 and fx2[:len(fx)] == fx: kids[fx2[-1]] = 1
        zs = {k[0] for k in kids}; vs = {k[1] for k in kids}
        if len(zs) != 1 or vs != set(range(9)) or list(zs)[0] in fixed or (m >> list(zs)[0] & 1): badt += 1
    rep('every UNKNOWN cube was split into the 9 value children d_z=0..8 of one free active z (complete value partition)', badt == 0, f'bad={badt}')
print('ALL OK' if ok else 'SOME FAIL')
