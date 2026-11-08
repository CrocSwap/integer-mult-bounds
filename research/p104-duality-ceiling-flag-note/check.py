#!/usr/bin/env python3
"""Single driver: one PASS line per claim of THEOREM.md; ends with PASS_P104_DUALITY_CEILING_FLAG_NOTE (exit 1 on any FAIL).
Run from anywhere:  python3.12 -I -B research/p104-duality-ceiling-flag-note/check.py   (writes nothing).
Standard library only. The quote checks read the repository files named in data/quotes.json (root is two levels above this
package); a missing file or a changed line is a FAIL, never a skip. Each check script prints 'ok' or 'FAIL' lines and a
PASS_* marker; the driver requires the marker, the exact number of ok lines, and no FAIL."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, 'checks')
ROOT = os.path.dirname(os.path.dirname(HERE))
fails = []
def PASS(tag, msg): print(f'PASS [{tag}] {msg}', flush=True)
def FAIL(tag, msg): fails.append(tag); print(f'FAIL [{tag}] {msg}', flush=True)
def ck(tag, cond, msg): (PASS if cond else FAIL)(tag, msg)

quotes = json.load(open(os.path.join(HERE, 'data', 'quotes.json')))
for rel, ln, sub in quotes['pkg']:
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        FAIL('Q', f'{rel}:{ln} (file absent)'); continue
    lines = open(path, encoding='utf-8', errors='replace').read().split('\n')
    ck('Q', ln <= len(lines) and sub in lines[ln - 1], f'{rel}:{ln} contains {sub[:60]!r}')

# (script, tag, marker, expected number of ok lines)
SCRIPTS = [
    ('duality.py', 'G-duality', 'PASS_DUALITY', 22),
    ('omega_floor.py', 'omega-floor', 'PASS_OMEGA_FLOOR', 19),
    ('flatten.py', 'flag-flatten', 'PASS_FLATTEN', 4),
    ('a2.py', 'A2-toy', 'PASS_A2', 5),
    ('lagr.py', 'lagrangian', 'PASS_LAGR', 36),
    ('caps.py', 'tile-caps', 'PASS_CAPS', 3),
    ('schur_leak.py', 'schur-leak', 'PASS_SCHUR_LEAK', 5),
]
for script, tag, marker, nok in SCRIPTS:
    p = subprocess.run([sys.executable, '-I', '-B', os.path.join(CH, script)], cwd=CH, capture_output=True, text=True, timeout=500)
    out = p.stdout + p.stderr
    oks = [l[5:].strip() for l in out.splitlines() if l.startswith('ok   ')]
    bad = [l for l in out.splitlines() if l.startswith('FAIL')]
    for m in oks: PASS(tag, m)
    for b in bad: FAIL(tag, b)
    ck(tag, marker in out and p.returncode == 0 and not bad and len(oks) == nok, f'{script}: marker {marker}, {len(oks)} ok lines (expected {nok}), exit {p.returncode}')
print('PASS_P104_DUALITY_CEILING_FLAG_NOTE' if not fails else f'FAILED: {sorted(set(fails))}')
sys.exit(1 if fails else 0)
