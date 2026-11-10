#!/usr/bin/env python3
"""Driver for the exact checks of THEOREM.md (a few seconds, standard library only, writes nothing).
Run from anywhere:  python3.12 -I -B research/p104-root-cut-laws/check.py
Each script in checks/ prints 'ok' or 'FAIL' lines and a PASS_* marker; the driver requires the marker, the exact number of ok lines,
exit status 0 and no FAIL."""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'checks')
fails = []
def PASS(tag, msg): print('PASS [%s] %s' % (tag, msg), flush=True)
def FAIL(tag, msg): fails.append(tag); print('FAIL [%s] %s' % (tag, msg), flush=True)

SCRIPTS = [
    ('rect_s.py', 'rectangle-and-S', 'PASS_RECT_S', 23),
    ('hubs.py', 'hub-laws', 'PASS_HUBS', 65),
    ('rootcut.py', 'root-cut-arithmetic', 'PASS_ROOTCUT', 13),
    ('cutc.py', 'crossing-bounds', 'PASS_CUTC', 14),
]
for script, tag, marker, nok in SCRIPTS:
    p = subprocess.run([sys.executable, '-I', '-B', os.path.join(CH, script)], cwd=CH, capture_output=True, text=True, timeout=500)
    out = p.stdout + p.stderr
    oks = [l[5:].strip() for l in out.splitlines() if l.startswith('ok   ')]
    bad = [l for l in out.splitlines() if l.startswith('FAIL') or 'Traceback' in l]
    for m in oks: PASS(tag, m)
    for b in bad: FAIL(tag, b)
    good = marker in out and p.returncode == 0 and not bad and len(oks) == nok
    (PASS if good else FAIL)(tag, '%s: marker %s, %d ok lines (expected %d), exit %d' % (script, marker, len(oks), nok, p.returncode))
print('PASS_P104_ROOT_CUT_LAWS' if not fails else 'FAILED: %s' % sorted(set(fails)))
sys.exit(1 if fails else 0)
