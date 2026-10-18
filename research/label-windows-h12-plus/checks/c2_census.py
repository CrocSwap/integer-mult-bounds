"""c2: the census min omega(R cap A) = 5 over all 47 x 440,880 = 20,721,360 (rep, section) pairs, by TWO independent exact implementations (C++).
  cen.cpp  decision DFS for a 7-clique, exact omega only below 7                (always run in full, about 1-2 min)
  mc.cpp   exact maximum clique, greedy-colouring branch and bound              (default: reps 43-46 in full + every 211th section of every rep;  FULL=1: all pairs, two chunks)
Both read the data rebuilt here by lib/common.py.  Compared with the recorded runs (evidence/cen_full.out.txt, evidence/mc.out.txt) and data/exceptional_pairs.json.
env: WORK (scratch dir), CXX (default c++), FULL=1.  Needs a C++ compiler; without one the lines are SKIP, never PASS.  <= 2 processes, nice 10, timeout 1200."""
import json, os, re, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); PKG = os.path.dirname(HERE); sys.path.insert(0, os.path.join(PKG, 'lib'))
WORK = os.environ.get('WORK') or os.path.join(os.environ.get('TMPDIR', '/tmp'), 'h12plus_c2'); os.makedirs(WORK, exist_ok=True)
FULL = os.environ.get('FULL') == '1'; CXX = os.environ.get('CXX') or shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
if not CXX:
    print('SKIP c2.a  no C++ compiler (cen.cpp census not run)'); print('SKIP c2.b  no C++ compiler (mc.cpp census not run)'); print('SKIP c2.c  no C++ compiler'); sys.exit(0)
import common
D = common.load(); common.write_graph(D, os.path.join(WORK, 'graph.txt')); common.write_mcdata(D, os.path.join(WORK, 'data.txt'))
for n in ('cen', 'mc'):
    subprocess.run([CXX, '-O2', '-o', os.path.join(WORK, n), os.path.join(HERE, '..', 'census', n + '.cpp')], check=True, capture_output=True)
def run(args, out):
    with open(out, 'w') as f:
        return subprocess.run(['nice', '-n', '10', 'timeout', '1200'] + args, cwd=WORK, stdout=f).returncode
def hist_cen(path):
    H = {}
    for l in open(path):
        m = re.match(r'rep (\d+) \|H\|=\d+ \|R\|=\d+:(.*)', l)
        if m:
            h = {(g + n): int(c) for g, n, c in re.findall(r'w(>=)?(\d+):(\d+)', m.group(2))}
            H[int(m.group(1))] = h
    return H
def hist_mc(path):
    H = {}
    for l in open(path):
        m = re.match(r'rep (\d+) \|R\|=\d+:(.*)', l)
        if m: H[int(m.group(1))] = {int(k): int(v) for k, v in re.findall(r'w(\d+):(\d+)', m.group(2))}
    return H
fail = 0
t = time.time(); rc = run([os.path.join(WORK, 'cen')], os.path.join(WORK, 'cen.out')); ex = []
H = hist_cen(os.path.join(WORK, 'cen.out'))
ex = [list(map(int, l.split()[1:4])) for l in open(os.path.join(WORK, 'cen.out')) if l.startswith('EX')]
rec = json.load(open(os.path.join(PKG, 'data', 'exceptional_pairs.json')))
tot = sum(sum(h.values()) for h in H.values()); w5 = sum(h.get('5', 0) for h in H.values()); w6 = sum(h.get('6', 0) for h in H.values())
ok = rc == 0 and len(H) == 47 and tot == 20721360 and sorted(ex) == sorted(rec) and (w5, w6) == (3, 141) and H == hist_cen(os.path.join(PKG, 'evidence', 'cen_full.out.txt'))
min_w = min(e[2] for e in ex)
print(('PASS' if ok and min_w == 5 else 'FAIL') + ' c2.a  cen.cpp (own run, %ds): %d pairs; omega 5 on %d, omega 6 on %d, omega >= 7 on all other %d; min omega = %d; exceptional list = data/exceptional_pairs.json = recorded cen_full.out.txt'
      % (time.time() - t, tot, w5, w6, tot - w5 - w6, min_w)); fail += not (ok and min_w == 5)
jobs = [(43, 47, 1), (0, 43, 211)] if not FULL else [(0, 23, 1), (23, 47, 1)]
procs = []; t = time.time()
if FULL:
    for k, (a, b, s) in enumerate(jobs):          # two chunks at once (two processes), each under the 1200 s timeout
        procs.append(subprocess.Popen(['nice', '-n', '10', 'timeout', '1200', os.path.join(WORK, 'mc'), str(a), str(b), str(s)], cwd=WORK, stdout=open(os.path.join(WORK, 'mc%d.out' % k), 'w')))
    rcs = [p.wait() for p in procs]
else:
    rcs = [run([os.path.join(WORK, 'mc'), str(a), str(b), str(s)], os.path.join(WORK, 'mc%d.out' % k)) for k, (a, b, s) in enumerate(jobs)]
M = {}
for k in range(len(jobs)): M.update(hist_mc(os.path.join(WORK, 'mc%d.out' % k)))
R = hist_mc(os.path.join(PKG, 'evidence', 'mc.out.txt'))
Hn = hist_cen(os.path.join(PKG, 'evidence', 'cen_full.out.txt'))
good = all(r == 0 for r in rcs) and len(M) == 47
for r, h in M.items():
    if r in (43, 44, 45, 46) or FULL:                                  # full rows: must equal the recorded mc.out.txt and cen.cpp exactly
        good &= h == R[r] and {5: Hn[r].get('5', 0), 6: Hn[r].get('6', 0)} == {5: h.get(5, 0), 6: h.get(6, 0)} and sum(h.get(k, 0) for k in (7, 8)) == Hn[r]['>=7']
    else:                                                                # strided sample: exact omega >= 7 everywhere (the exceptional sections are only in reps 43, 45, 46)
        good &= min(h) >= 7
mn = min(min(h) for h in M.values())
print(('PASS' if good and mn == 5 else 'FAIL') + ' c2.b  mc.cpp (own run, %ds, %s): exact omega histogram equals the recorded mc.out.txt %s; min omega = %d; agrees with cen.cpp on w5/w6/(>=7) counts'
      % (time.time() - t, 'ALL pairs' if FULL else 'reps 43-46 in full, other reps sampled every 211th section', 'rows' if FULL else 'rows for reps 43-46', mn)); fail += not (good and mn == 5)
ok = min(min(h) for h in R.values()) == 5 and sum(h.get(5, 0) for h in R.values()) == 3 and sum(h.get(6, 0) for h in R.values()) == 141
print(('PASS' if ok else 'FAIL') + ' c2.c  recorded mc.out.txt (Oct 15, ~25 min): min omega 5; 3 pairs omega 5, 141 omega 6, rep 43/45/46 only'); fail += not ok
sys.exit(1 if fail else 0)
