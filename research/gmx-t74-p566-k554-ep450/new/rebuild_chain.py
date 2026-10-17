"""Package stage: re-verifies every kernel step of new/CHAIN.json with the retained exactness checker (rebuild.py of PR1625), generalised soundly.

For each step: apply the step's edit to the step's BASE words and compare with the step's NEW words (scalar program, interfaces, the
complete B + early-cleanup map over every register in exact Fractions, remaining cleanup). Inserted reads of the pivot must see q's row = s*I with
s in {+1,-1} (rebuild.py required s=+1 and exactly two writes of q; pivots restored by a sign-flipping cleanup gate, e.g. 554, read -q after the
restore, with the coefficient taken with that sign; exactness is proven by the unchanged map check). Tamper controls (sign not accounted on all new gates / on tail gates, and each new coefficient moved by one dyadic step) must all FAIL the map check. See pivotcheck.py.
Step 0 starts from PR1297's pinned words (vendor/pr1297); later steps start from the previous step's words.
"""
import json, sys
from pathlib import Path
PKG = Path(__file__).resolve().parent
ROOT = PKG.parent
sys.path.insert(0, str(PKG))
import rebuild as RB
import pivotcheck as PC
chain = json.loads((PKG / 'CHAIN.json').read_text())
ok = True
for i, st in enumerate(chain['steps']):
    E = json.loads((PKG / st['edits']).read_text())
    assert E['pivot'] == st['pivot'], (i, 'pivot mismatch')
    for key in ('gauge44', 'extra'):
        base = RB.load(ROOT / st['base'][key])
        r = PC.check_signed(RB, '%s step %d' % (key, i), base, RB.load(ROOT / st['new'][key]), E['edit'], E['pivot'])
        c = PC.tamper_controls(RB, base, E['edit'], E['pivot'])
        r['tamper_controls_all_fail'] = all(c.values()); r['tamper_controls'] = c
        print('step', i, key, 'PASS' if r['pass'] else 'FAIL', {k: v for k, v in r.items() if k not in ('word', 'new_read_positions')}, flush=True)
        ok = ok and r['pass'] and all(c.values())
sys.exit(0 if ok else 1)
