#!/usr/bin/env python3
"""Recompute data/ledger3_consolidated.csv from data/ledger2_consolidated.csv (the 38-open ledger of the part-2 closures)
and data/new_kills.csv.  Prints counts; exits 1 on any inconsistency.  usage: build_ledger3.py [out.csv]"""
import csv, sys, os, collections
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, '..', 'data')
L2 = list(csv.DictReader(open(os.path.join(D, 'ledger2_consolidated.csv'))))
NK = {int(r['row']): r for r in csv.DictReader(open(os.path.join(D, 'new_kills.csv')))}
PRIOR7 = {381, 384, 576, 577, 578, 580, 581}
out = []; bad = 0
for r in L2:
    n = int(r['row']); st = r['status']; kb = r['killed_by']
    if st == 'OPEN':
        if n not in NK: print('OPEN row without a closing entry', n); bad += 1; continue
        st, kb = NK[n]['status'], NK[n]['by'] + ' | ' + NK[n]['checks']
    elif n in NK: print('row already closed but in new_kills', n); bad += 1
    if st == 'KILLED(prior-only)':
        if n not in PRIOR7: print('unexpected prior-only', n); bad += 1
        st = 'KILLED'
        kb = ('(6,6,5) s0 span at target 7, span <= 6 <= d-1, two implementations: original s3y run + independent s3z rerun '
              '(192/192 slices, 0 cracks) | checks/PRIOR7/rerun.sh, evidence/prior7/ | Lemma P at T-level [audited lemma, new application]')
    out.append(dict(r, status=st, killed_by=kb))
if set(NK) - {int(r['row']) for r in L2 if r['status'] == 'OPEN'}: print('new_kills rows not open in ledger2'); bad += 1
cnt = collections.Counter(r['status'] for r in out)
print('rows', len(out)); [print(' ', k, v) for k, v in sorted(cnt.items())]
if sum(v for k, v in cnt.items() if k.startswith('KILLED')) != 602 or cnt.get('CONDITIONAL(C6=DEG2)', 0) != 1: print('unexpected counts'); bad += 1
if len(out) != 603 or bad: print('LEDGER FAIL'); sys.exit(1)
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'ledger3_consolidated.csv')
w = csv.DictWriter(open(dst, 'w', newline=''), fieldnames=list(out[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(out)
print('LEDGER OK')
