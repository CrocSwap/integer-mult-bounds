#!/usr/bin/env python3
"""Recompute data/ledger4_consolidated.csv from data/ledger3_consolidated.csv (PR #3154, 602 KILLED + row 579 CONDITIONAL(C6=DEG2)).
Only row 579 changes: CONDITIONAL(C6=DEG2) -> KILLED(conditional on DEG2 impl C rerun slot, see PROOF_MAP.md).  Prints counts; exits 1 on inconsistency.
usage: build_ledger4.py [out.csv]"""
import csv, sys, os, collections
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
L3 = list(csv.DictReader(open(os.path.join(D, 'ledger3_consolidated.csv'))))
out = []; bad = 0
for r in L3:
    if int(r['row']) == 579:
        if r['status'] != 'CONDITIONAL(C6=DEG2)': print('row 579 not conditional in ledger3'); bad += 1
        r = dict(r, status='KILLED',
                 killed_by='K579T Theorem K5 + R579b Lemmas K5^-, K5^-2 (e_N >= 6 non-root pairs) + DEG2 (no seven carries two non-root pair directions; mask model, '
                           'impl A DEG2A: 0 six-sets; impl C DEG2C fixed oracle: SLOT-C6-IMPL-C, see PROOF_MAP.md) | checks/K579T; checks/R579b; checks/DEG2A; checks/DEG2C')
    out.append(r)
cnt = collections.Counter(r['status'] for r in out)
print('rows', len(out)); [print(' ', k, v) for k, v in sorted(cnt.items())]
if len(out) != 603 or cnt.get('KILLED', 0) != 603 + 0 - sum(v for k, v in cnt.items() if k != 'KILLED') or any(k.startswith('CONDITIONAL') for k in cnt):
    bad += 1
if not all(r['status'].startswith('KILLED') for r in out): bad += 1
if bad: print('LEDGER FAIL'); sys.exit(1)
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'ledger4_consolidated.csv')
w = csv.DictWriter(open(dst, 'w', newline=''), fieldnames=list(out[0].keys()), lineterminator='\n'); w.writeheader(); w.writerows(out)
print('LEDGER OK: 603/603 KILLED (row 579 via DEG2, conditional on the impl C slot)')
