"""Counts the shipped working-card logs and state files and asserts the exact numbers quoted in the README.  RE-RUNS NOTHING: every line it
counts is a result the author's cards produced (kissat 4.0.4 + drat-trim); this script only checks that the README's counts are what the shipped
evidence says.  Standard library only."""
import os, re, json, sys
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, '..', 'data')
ok = True
def chk(name, cond, extra=''):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else ''), flush=True); ok &= bool(cond)
def lines(f): return open(os.path.join(D, 'logs', f)).read().splitlines()
# --- p = 46 cube leaves (PUNCT7, end-to-end drat-trim against the unreduced cube CNF, per the card)
exp46 = [16, 29, 92, 197, 148, 51, 28, 10]; got = []; allv = True
for T in range(8):
    d = json.load(open(os.path.join(D, 'states', 'st3_%d_46.json' % T))); v = [x for k, x in d.items() if k != '_md5']
    got.append(len(v)); allv &= all(x['res'] == 'UNSAT-VERIFIED' for x in v)
chk('4.1 p=46, m<=7: leaves per flat type 0..7 = %s, total %d, all res == UNSAT-VERIFIED (card statement; not re-run)' % (got, sum(got)), got == exp46 and sum(got) == 571 and allv)
# --- h = 10 term queries
ver = 0; bad = []; tot = 0
for f in ('dratT_0.txt', 'dratT_43.txt', 'dratT_86.txt', 'dratT_129.txt'):
    for l in lines(f):
        if l == 'DONE': continue
        tot += 1
        if l.endswith('drat VERIFIED'): ver += 1
        else: bad.append(l.split(' : ')[0])
chk('4.4 h=10 T-query DRATs: %d verified of %d; unverified: %s (no proof within the lane cap: kissat returned no UNSAT)' % (ver, tot, bad), (ver, tot) == (687, 688) and bad == ['hk3.py 10 1 2 pairs46.pkl 0 cnf/dT_0_12.cnf'])
fin = lines('dratT_0_12_final.txt')[0]
chk('4.4b the one missing T(10) DRAT, re-run Oct 15 with a 1200 s hard kissat cap: no verdict, still unverified (so 687/688 stands)', fin.startswith('hk3.py 10 1 2 pairs46.pkl 0 cnf/dT_0_12.cnf') and 'TIMEOUT' in fin and 'drat -' in fin)
g = [l for l in lines('dratG10.txt') if l.endswith('drat VERIFIED')]
chk('4.5 h=10 G(10,2,rep) DRATs verified: %d (46 orbits)' % len(g), len(g) == 46)
# --- h = 10: the kissat verdicts for all 688 T(10) queries (the 688th, pair 0 split 12, is only in t46a.txt: a single kissat run, not reproduced)
k10 = {}
for f in ('t46a.txt', 't46b.txt', 't46c.txt', 't46d.txt'):
    for l in lines(f):
        m = re.match(r'p46 (\d+) (\d\d) : s UNSATISFIABLE$', l)
        if m: k10.setdefault((int(m[1]), m[2]), set()).add('t46')
for f in ('dratT_0.txt', 'dratT_43.txt', 'dratT_86.txt', 'dratT_129.txt'):
    for l in lines(f):
        m = re.match(r'hk3.py 10 (\d) (\d) pairs46.pkl (\d+) .* : s UNSATISFIABLE : drat VERIFIED$', l)
        if m: k10.setdefault((int(m[3]), m[1] + m[2]), set()).add('drat')
allq = {(i, s) for i in range(172) for s in ('03', '12', '21', '30')}
only_t46 = sorted(q for q, v in k10.items() if v == {'t46'})
chk('4.4c h=10 T(10) kissat UNSAT verdicts: %d of 688 queries (t46a-d: %d, dratT lanes: %d); the only query with a kissat verdict and no DRAT is pair 0 split 12 (RECORDED, single kissat run, not reproduced)' % (len(set(k10) & allq), sum('t46' in v for v in k10.values()), sum('drat' in v for v in k10.values())),
    set(k10) == allq and only_t46 == [(0, '12')] and sum('t46' in v for v in k10.values()) == 686)
# --- h = 11
h = lines('dratH11.txt'); gv = [l for l in h if re.match(r'hk.py 11 3 \d+ .*drat VERIFIED$', l)]; gb = [l for l in h if re.match(r'hk.py 11 3 \d+ ', l) and not l.endswith('drat VERIFIED')]
chk('4.6 h=11 G(11,3) DRATs (older run): %d verified, unverified %s; reps 33..45 not attempted; no T(11) DRAT in any shipped log' % (len(gv), [l.split(' : ')[0] for l in gb]), len(gv) == 32 and len(gb) == 1)
g11 = {}
for f in ('k11.txt', 'k11a.txt', 'k11b.txt', 'k11c.txt', 'k11f.txt', 'k11g.txt'):
    for l in lines(f):
        m = re.match(r'(RREF )?h 11 K 3 rep (\d+) : s UNSATISFIABLE$', l)
        if m: g11.setdefault(int(m[2]), set()).add('RREF' if m[1] else 'plain')
chk('4.6b h=11 G(11,3) kissat UNSAT verdicts: reps %s (%d of 46); reps 40-45 on RREF CNFs (k11g.txt), rep 46 (f-perp orbit) not needed' % ('0..45' if sorted(g11) == list(range(46)) else sorted(g11), len(g11)),
    sorted(g11) == list(range(46)) and all(g11[r] == {'RREF'} for r in range(40, 46)) and all('plain' in g11[r] for r in range(40)))
hb = [l for l in lines('dratH11b.txt') if l.strip()]; hbv = sorted(int(re.match(r'hk.py 11 3 (\d+) ', l)[1]) for l in hb if re.match(r'hk.py 11 3 \d+ cnf/\S+ : s UNSATISFIABLE : drat VERIFIED$', l))
old_ok = sorted(int(re.match(r'hk.py 11 3 (\d+) ', l)[1]) for l in gv)
chk('4.6c h=11 DRAT (snapshot of the live dratH11b job, RREF CNFs): %d lines, G reps %s VERIFIED; union with the older run = %d of 46 G(11,3) drat-trim VERIFIED; T(11) DRAT: %d of 522 (only drat-trim VERIFIED proofs counted)' % (len(hb), hbv, len(set(old_ok) | set(hbv)), sum('hk3.py' in l and l.endswith('drat VERIFIED') for l in hb)),
    len(hb) == len(hbv) == 8 and hbv == [12] + list(range(33, 40)) and len(set(old_ok) | set(hbv)) == 40 and not any('hk3.py' in l for l in hb))
done = set()
for f in ('t11x.txt', 't11a.txt', 't11b.txt'):
    for l in lines(f):
        m = re.match(r'p46h11 (\d+) (\d\d) : s UNSATISFIABLE', l)
        if m: done.add((int(m[1]), m[2]))
for l in lines('h11_run1.txt'):
    m = re.search(r'h11 l(\d) k(\d) pair (\d+) : s UNSATISFIABLE', l)
    if m: done.add((int(m[3]), m[1] + m[2]))
need = {(i, s) for i in range(172) for s in ('23', '14', '05')} | {(i, s) for i in (0, 3) for s in ('32', '41', '50')}
chk('4.7 h=11 T(11) queries: %d needed (172 pair orbits x splits 23/14/05, plus pairs 0 and 3 x 32/41/50), %d UNSAT (kissat verdicts, from 4 logs; DRAT not run)' % (len(need), len(need & done)), len(need) == 522 and need <= done)
# --- Case-B census
a = lines('cB4_56_17_6.txt'); b = lines('cB4_56_17_6_b27.txt')
va = [l for l in a if re.search(r'UNSAT VERIFIED', l)]; vb = [l for l in b if re.search(r'UNSAT VERIFIED', l)]
chk('4.8 Case-B census: first log %d cubes UNSAT VERIFIED (b = 1, 2, 8, 26) + b=27 "UNSAT NOT-VERIFIED" (drat-trim timeout); split log %d leaves UNSAT VERIFIED; final line %r' % (len(va), len(vb), b[-1].strip()),
    len(va) == 4 and len(vb) == 7 and any('b 27 UNSAT NOT-VERIFIED' in l for l in a) and b[-1].strip().endswith('RESULT UNSAT-VERIFIED'))
chk('4.8 total leaves VERIFIED = 4 + 7 = 11 (cubes b=1,2,8,26 and the 7 kernel reps of b=27)', len(va) + len(vb) == 11)
raise SystemExit(0 if ok else 1)
