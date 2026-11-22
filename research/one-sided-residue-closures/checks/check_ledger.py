# Compares the recomputed ledger (ledger_recomputed.csv, from build_ledger.py) with the shipped data/ledger_consolidated.csv and asserts the headline counts.
import csv, ast, sys, os
from collections import Counter
from paths import DATA
ok = True
def chk(name, cond):
    global ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name)
new = open('ledger_recomputed.csv', 'rb').read(); old = open(os.path.join(DATA, 'ledger_consolidated.csv'), 'rb').read()
chk('recomputed ledger is byte-identical to data/ledger_consolidated.csv', new == old)
L = list(csv.DictReader(open('ledger_recomputed.csv')))
chk('603 rows', len(L) == 603)
ws = [tuple(sorted(ast.literal_eval(r['weights']), reverse=True)) for r in L]
keys = [(int(r['d']), w) for r, w in zip(L, ws)]
chk('rows are distinct (d, multiset) pairs with d in 4..8, weights in 1..7, slack = sum(w) - 8d in 4..7, e = #pieces - d', len(set(keys)) == 603 and all(
    4 <= int(r['d']) <= 8 and all(1 <= x <= 7 for x in w) and sum(w) - 8 * int(r['d']) == int(r['slack']) and 4 <= int(r['slack']) <= 7 and len(w) - int(r['d']) == int(r['e']) for r, w in zip(L, ws)))
c = Counter(r['audit_status'] for r in L)
chk('480 KILLED by audited sources, 7 KILLED(prior-only), 116 OPEN', c == {'KILLED': 480, 'KILLED(prior-only)': 7, 'OPEN': 116})
chk('every KILLED row has a certificate string; every OPEN row has none', all((r['certificates'] != '') == (r['audit_status'] == 'KILLED') for r in L if r['audit_status'] != 'KILLED(prior-only)'))
po = [r for r in L if r['audit_status'] == 'KILLED(prior-only)']
chk('the 7 prior-only rows are exactly rows with no audited certificate and the earlier span-cover tag', all('prior, not re-audited' in r['killed_by'] and '[audited' not in r['killed_by'] for r in po))
def keyset(fn): return {(int(r['d']), tuple(sorted(ast.literal_eval(r['weights']), reverse=True))) for r in csv.DictReader(open(os.path.join(DATA, fn)))}
st = {k: r['audit_status'] for k, r in zip(keys, L)}
for fn, n, nm in (('src_scB2_killed.csv', 47, 'class-B (RRC)'), ('src_s7b_killed.csv', 25, 'root-count (K0 empty)'), ('src_scA2_killed.csv', 74, 'class-A (Lemma P / P\')')):
    S = keyset(fn); chk('all %d earlier %s kills are KILLED by the audited recomputation' % (n, nm), len(S) == n and all(st[k] == 'KILLED' for k in S))
tab = Counter((int(r['d']), int(r['slack']), r['audit_status']) for r in L)
print('OPEN rows by (d, slack):', sorted((d, s, n) for (d, s, a), n in tab.items() if a == 'OPEN'))
print('PASS ledger' if ok else 'FAIL ledger'); sys.exit(0 if ok else 1)
