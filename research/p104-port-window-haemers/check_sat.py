#!/usr/bin/env python3
"""Driver for the solver-side data (a few seconds, standard library only, writes nothing): regenerates the DIMACS instances and compares
counts and sha256 with data/sat_results.json, evaluates explicit labellings on them, and checks the shipped DRAT proof file's sha256.
Run from anywhere:  python3.12 -I -B research/p104-port-window-haemers/check_sat.py   (no solver is run)."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'checks')
p = subprocess.run([sys.executable, '-I', '-B', os.path.join(CH, 'sat.py')], cwd=CH, capture_output=True, text=True, timeout=500)
out = p.stdout + p.stderr
oks = [l[5:].strip() for l in out.splitlines() if l.startswith('ok   ')]
bad = [l for l in out.splitlines() if l.startswith('FAIL') or 'Traceback' in l]
for m in oks: print('PASS [sat] ' + m, flush=True)
for b in bad: print('FAIL [sat] ' + b, flush=True)
good = 'PASS_SAT' in out and p.returncode == 0 and not bad and len(oks) == 13
print('PASS_P104_PORT_WINDOW_SAT' if good else 'FAILED: sat.py (%d ok lines, expected 13, exit %d)' % (len(oks), p.returncode))
sys.exit(0 if good else 1)
