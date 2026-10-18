"""c6: accounting of the shipped SAT evidence (re-runs nothing; verify.sh step 7 re-runs a sample, FULL=1 all).  Standard library only.
  c6.a  sat/jobs61.txt is exactly: h=12, l+k=6, pairs 0..5, l=0..6 (42);  h=13, l+k=8, pair 4, l=0..8 (9);  h=14, l+k=9, pair 4, l=0..9 (10)
  c6.b  evidence/drat_61.log.txt (this package's re-run, CNF sha256 recorded): one line per job, each  s UNSATISFIABLE ... drat VERIFIED, 61 distinct keys = the job list
  c6.c  evidence/drat_696.log.txt: same for the 696 queries of sat/jobs696.txt (H11 item (i): T(12, l+k=7))
  c6.d  the Oct 15 logs (evidence/oct15_*.log; no CNF hashes): the same key sets, all VERIFIED (RECORDED)"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE); fail = 0
def jobs(f):
    out = []
    for l in open(os.path.join(PKG, 'sat', f)):
        if l.strip():
            e, h, a, b, i, pf = l.split(); out.append((e, int(h), int(a), int(b), int(i), pf))
    return out
def key(j): return '%s h%d l%d k%d pair %d %s' % j
def parse(path):
    d = {}; dup = 0; other = []
    for l in open(path):
        l = l.rstrip('\n')
        if l.startswith('DONE'): continue
        k, _, rest = l.partition(' : ')
        if k in d: dup += 1
        d.setdefault(k, []).append(rest)
    return d, dup
J61, J696 = jobs('jobs61.txt'), jobs('jobs696.txt')
exp = {(12, 6, p, l) for p in range(6) for l in range(7)} | {(13, 8, 4, l) for l in range(9)} | {(14, 9, 4, l) for l in range(10)}
ok = {(h, a + b, i, a) for _, h, a, b, i, _ in J61} == exp and len(J61) == 61 and all(e == 'RREF=1,ORTH=1,GAUGE=RA' and pf == 'X' for e, _, _, _, _, pf in J61)
print(('PASS' if ok else 'FAIL') + ' c6.a  jobs61.txt = 42 (h=12, l+k=6, six orbits) + 9 (h=13, l+k=8) + 10 (h=14, l+k=9) distinct queries'); fail += not ok
ok = len({key(j) for j in J696}) == 696 and all(j[1] == 12 and j[2] + j[3] == 7 and j[5] == 'P46' for j in J696)
print(('PASS' if ok else 'FAIL') + ' c6.a2 jobs696.txt = 696 distinct T(12, l+k=7) queries on pairs46.json'); fail += not ok
def audit(label, path, J, hashes):
    d, dup = parse(os.path.join(PKG, 'evidence', path)); want = {key(j) for j in J}
    good = set(d) == want
    for k, v in d.items():
        good &= any('s UNSAT' in r and 'drat VERIFIED' in r and 'NOT VERIFIED' not in r and (not hashes or re.search(r'cnf [0-9a-f]{64}', r)) for r in v)
    return good, len(d), dup
for tag, f, J, hs in (('c6.b', 'drat_61.log.txt', J61, True), ('c6.c', 'drat_696.log.txt', J696, True)):
    g, n, dup = audit(tag, f, J, hs); print(('PASS' if g else 'FAIL') + ' %s  %s: %d keys = job list, all UNSAT + drat VERIFIED, CNF sha256 recorded%s' % (tag, f, n, '' if not dup else ' (%d keys logged twice)' % dup)); fail += not g
G = [audit('', 'oct15_dratX.log.txt', J61, False), audit('', 'oct15_drat696.log.txt', J696, False)]
print(('PASS' if all(g[0] for g in G) else 'FAIL') + ' c6.d  Oct 15 logs (RECORDED): %d + %d distinct keys = the job lists, all UNSAT + drat VERIFIED (%d keys of the 696 log occur twice, see README)' % (G[0][1], G[1][1], G[1][2])); fail += not all(g[0] for g in G)
cl = [l for l in open(os.path.join(PKG, 'evidence', 'controls_sat.log.txt')) if l.strip()]
jc = jobs('jobs_controls.txt')
ok = len(cl) == 4 and {l.split(' : ')[0] for l in cl} == {key(j) for j in jc} and all('s SATISFIABLE' in l and re.search(r'cnf [0-9a-f]{64}', l) for l in cl)
print(('PASS' if ok else 'FAIL') + ' c6.e  evidence/controls_sat.log.txt: 4 SAT controls T(12, l+k=3) on pair 4 (sat/jobs_controls.txt), CNF sha256 recorded'); fail += not ok
sys.exit(1 if fail else 0)
