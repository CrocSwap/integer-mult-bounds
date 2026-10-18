"""c7: compare a fresh chain.sh log (argv[1], produced by verify.sh step 7) with the shipped re-run logs: every fresh query regenerated a CNF with the SAME sha256 as the
shipped record (the encoder sat/hk3.py is deterministic and the CNF byte-identical), kissat said UNSAT and drat-trim said VERIFIED.  argv[2] = 'sample' or 'full'.
Standard library only."""
import os, re, sys
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); mode = sys.argv[2]
def load(p):
    d = {}
    for l in open(p):
        if l.startswith('DONE') or not l.strip(): continue
        k, _, rest = l.rstrip('\n').partition(' : '); d.setdefault(k, []).append(rest)
    return d
ship = {}
for f in ('drat_61.log.txt', 'drat_696.log.txt'): ship.update(load(os.path.join(PKG, 'evidence', f)))
new = load(sys.argv[1]); fail = 0
same = bad = 0
for k, v in new.items():
    r = v[-1]; m = re.search(r'cnf ([0-9a-f]{64})', r); s = re.search(r'cnf ([0-9a-f]{64})', ship[k][-1]) if k in ship else None
    if m and s and m.group(1) == s.group(1): same += 1
    if not ('s UNSAT' in r and 'drat VERIFIED' in r and 'NOT VERIFIED' not in r): bad += 1
n = len(new)
exp = {'sample': 14, 'full': 757}[mode]
ok1 = n == exp and same == n; ok2 = n == exp and bad == 0
print(('PASS' if ok1 else 'FAIL') + ' c7.a  %s: %d of %d regenerated CNFs have the shipped sha256 (expected %d queries)' % (mode, same, n, exp))
print(('PASS' if ok2 else 'FAIL') + ' c7.b  %s: kissat 4.0.4 UNSAT and drat-trim VERIFIED on %d of %d queries' % (mode, n - bad, n))
sys.exit(0 if ok1 and ok2 else 1)
