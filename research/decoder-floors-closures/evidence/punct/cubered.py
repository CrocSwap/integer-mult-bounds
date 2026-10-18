r"""PUNCT7 cube reducer. usage: cubered.py base.cnf P out.cnf [prefix.drat] -- u1 u2 ...   (cube literals)
F = base CNF (rkdirect.py: S vars 1..120, seqcounter |S|<=P, frames, heads S_s v OR z, binaries -z v S_t), U = cube units.
Computes an assignment A by alternating (1) unit propagation on F ∧ U and (2) card-elimination: option var z (binary clauses -z v S_t, t<=120)
gets -z when |{t : S_t true in A} ∪ set(z)| > P. Writes F' = {units of A} ∪ {C \ false-literals : C in F not satisfied by A}, same variable
numbering. Soundness (both directions): every model of F ∧ U satisfies A (UP sound; z true would put > P S-vars true, violating the
cardinality clauses of F), hence satisfies F'; conversely every model of F' contains A and so satisfies every clause of F (satisfied ones by A,
the others by their shortened copy) and U. So F' UNSAT <=> F ∧ U UNSAT.
Optional prefix.drat (route b, no trust in this script): RUP lemmas = every unit of A in derivation order, then every shortened clause, then
deletion of every original clause; prepend it to the solver's DRAT for F' and drat-trim against base+U."""
import sys, time
from collections import defaultdict
t0 = time.time()
args = sys.argv[1:]; k = args.index('--')
base, P, outf = args[0], int(args[1]), args[2]; pref = args[3] if k > 3 else None
U = [int(x) for x in args[k + 1:]]
cls = []; nv = 0
with open(base) as f:
    for ln in f:
        if ln[0] in 'pc':
            if ln[0] == 'p': nv = int(ln.split()[2])
            continue
        v = list(map(int, ln.split()));
        if v: cls.append(v[:-1])
zset = defaultdict(set)
for c in cls:
    if len(c) == 2 and c[0] < -120 and 0 < c[1] <= 120: zset[-c[0]].add(c[1])
occ = defaultdict(list)
for i, c in enumerate(cls):
    for l in c: occ[l].append(i)
val = {}          # var -> bool
order = []        # assigned literals in derivation order
nfalse = [0] * len(cls); sat = [False] * len(cls)
def assign(l, q):
    v = abs(l); b = l > 0
    if v in val:
        if val[v] != b: raise SystemExit('CONFLICT: F ∧ U refuted by unit propagation (UNSAT outright) at lit %d' % l)
        return
    val[v] = b; order.append(l); q.append(l)
def prop(q):
    while q:
        l = q.pop()
        for i in occ[l]: sat[i] = True
        for i in occ[-l]:
            if sat[i]: continue
            nfalse[i] += 1; c = cls[i]
            if nfalse[i] >= len(c) - 1:
                free = [x for x in c if abs(x) not in val]
                if any(val.get(abs(x)) == (x > 0) for x in c): sat[i] = True; continue
                if not free: raise SystemExit('CONFLICT: F ∧ U refuted by unit propagation at clause %d' % i)
                if len(free) == 1: assign(free[0], q)
q = []
for u in U: assign(u, q)
prop(q)
rounds = 0; nelim = 0
while True:
    rounds += 1
    T = {t for t in range(1, 121) if val.get(t)}
    new = [z for z, e in zset.items() if z not in val and len(T | e) > P]
    if not new: break
    for z in new: assign(-z, q); nelim += 1
    prop(q)
out = []
for i, c in enumerate(cls):
    if any(val.get(abs(x)) == (x > 0) for x in c): continue
    d = [x for x in c if abs(x) not in val]
    if not d: raise SystemExit('CONFLICT clause %d all false' % i)
    out.append(d)
units = [[l] for l in order]
with open(outf, 'w') as f:
    f.write(f'p cnf {nv} {len(units) + len(out)}\n')
    for c in units + out: f.write(' '.join(map(str, c)) + ' 0\n')
if pref:
    with open(pref, 'w') as f:
        for l in order: f.write(f'{l} 0\n')
        for c in out: f.write(' '.join(map(str, c)) + ' 0\n')
        for c in cls: f.write('d ' + ' '.join(map(str, c)) + ' 0\n')
nS = sum(1 for t in range(1, 121) if val.get(t)); nSf = sum(1 for t in range(1, 121) if val.get(t) is False)
zl = sum(1 for z in zset if z not in val)
print(f'reduced {base}+{U}: S true {nS}, S false {nSf}, assigned {len(order)}, card-elim {nelim} ({rounds} rounds), '
      f'live options {zl}/{len(zset)}, clauses {len(cls)} -> {len(units)}+{len(out)}, {time.time() - t0:.1f}s -> {outf}', flush=True)
