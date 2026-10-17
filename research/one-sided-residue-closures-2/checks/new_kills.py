# Re-derives every NEW kill of this package from rows_input.csv and writes the consolidated ledger.
#  (a) Lemma Q4 (G777): ClassI (slack 7), P = pieces of weight 7, S = the other pieces, c_S = sum g(S) <= 13, |P|-2 <= d-1,
#      C(|P|,2) > bound(c_S) with bound = c_S (c_S<=7), c_S+4 (<=11), c_S+20 (<=13).  The derived set is compared with data/g777_kills.json.
#  (b) count lemma / E6 dim-cover: output of e6/asm.py parsed; rows 448,449 by the count lemma alone; rows 168,324,325,328,457: every scenario is
#      killed by IMM/COUNT/RRC except the ones needing the cover (6,6,5,5,5,4) of the 84 lines outside E6, which e6/tight.py and e6/verify_e6.py both find impossible.
#  (c) span passes: data/sc/killed_sc_ok.csv, accepted only for configs whose pass is re-checked by sc_check.py (arg: file with the passing configs).
import csv, ast, json, os, sys, re, subprocess
from math import comb
from paths import DATA
g = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36, 8: 64}
rows = list(csv.DictReader(open(os.path.join(DATA, 'rows_input.csv'))))
base = list(csv.DictReader(open(os.path.join(DATA, 'ledger_consolidated.csv'))))
assert len(rows) == len(base) == 603
def q4(i):
    r = rows[i]; d = int(r['d']); s = int(r['slack']); ws = ast.literal_eval(r['weights'])
    if s != 7: return None
    P = [w for w in ws if w == 7]; S = [w for w in ws if w != 7]; cS = sum(g[w] for w in S)
    if len(P) < 2 or cS > 13 or len(P) - 2 > d - 1: return None
    bound = cS if cS <= 7 else (cS + 4 if cS <= 11 else cS + 20)
    return dict(row=i, P=len(P), pairs=comb(len(P), 2), S=S, c_S=cS, bound=bound) if comb(len(P), 2) > bound else None
Q4 = {i: q4(i) for i in range(603) if q4(i)}
ship = {k['row']: k for k in json.load(open(os.path.join(DATA, 'g777_kills.json')))}
assert set(ship) <= set(Q4), (sorted(Q4), sorted(ship))
EXTRA = sorted(set(Q4) - set(ship)); Q4 = {i: Q4[i] for i in ship}   # criterion also holds for EXTRA rows; not audited, so NOT claimed
for i, k in ship.items(): assert (k['P'], k['pairs'], k['S'], k['c_S']) == (Q4[i]['P'], Q4[i]['pairs'], Q4[i]['S'], Q4[i]['c_S']), i
print('PASS Lemma Q4 criterion holds for all 15 shipped rows', sorted(Q4)); print('NOTE the criterion also holds for %d further rows %s: not in the audited kill list, NOT claimed' % (len(EXTRA), EXTRA))
asm = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(DATA), 'checks', 'e6', 'asm.py')], capture_output=True, text=True, timeout=600).stdout
cur = None; sc = {}
for l in asm.splitlines():
    m = re.match(r'ROW (\d+) ', l)
    if m: cur = int(m.group(1)); sc[cur] = []; continue
    sc[cur].append('KILLED' if 'KILLED by' in l else ('COVER' + re.search(r'comp \(([\d, ]+)\)', l).group(1).replace(' ', '') if 'needs DimCover' in l else '?'))
count_only = [r for r in (448, 449) if sc[r] and all(x == 'KILLED' for x in sc[r]) and 'COUNT' in asm.split('ROW %d ' % r)[1].split('ROW')[0]]
cover = [r for r in (168, 324, 325, 328, 457) if sc[r] and all(x in ('KILLED', 'COVER6,6,5,5,5,4') for x in sc[r]) and 'COVER6,6,5,5,5,4' in sc[r]]
assert count_only == [448, 449] and cover == [168, 324, 325, 328, 457], (count_only, cover)
print('PASS asm.py: rows 448,449 killed by the count lemma in every scenario; rows 168,324,325,328,457 killed in every scenario except a (6,6,5,5,5,4) cover requirement')
E_ONLY = {r: ('count lemma (asm.py, class I)' if r in (448, 449) else 'RRC/count + Dim-Cover E6 (6,6,5,5,5,4) not coverable') for r in (448, 449, 168, 324, 325, 328, 457)}
accepted = set(); scconf = {}
if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
    good = set(open(sys.argv[1]).read().split())
    for r in csv.DictReader(open(os.path.join(DATA, 'sc', 'killed_sc_ok.csv'))):
        cfg, T = r['killed_by'].split('@T'); i = int(r['row'])
        assert rows[i]['weights'] == r['weights'] and rows[i]['d'] == r['d'], i
        assert int(r['d']) >= int(T), ('pass at T gives span <= T-1 <= d-1 only if d >= T', r)
        if cfg in good: accepted.add(i); scconf[i] = r['killed_by']
out = []; cnt = {}
for i, b in enumerate(base):
    st, how = b['audit_status'], b['killed_by']
    if i in Q4: new = ('KILLED(new)', 'Lemma Q4 (G777), 2 implementations + audit')
    elif i in E_ONLY: new = ('KILLED(new)', E_ONLY[i] + ', 2 implementations')
    elif i in accepted: new = ('KILLED(new)', 'span pass ' + scconf[i] + ' (s3z.c, rerunnable)')
    else: new = None
    if new and st == 'OPEN': st, how = new
    elif new and st != 'OPEN': how = how + ' | also: ' + new[1]
    out.append([i, b['d'], b['slack'], b['weights'], b['e'], b['earlier_status'], st, how]); cnt[st] = cnt.get(st, 0) + 1
with open('ledger2_recomputed.csv', 'w', newline='') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(['row', 'd', 'slack', 'weights', 'e', 'earlier_status', 'status', 'killed_by']); w.writerows(out)
newrows = {'Q4': sorted(i for i in Q4 if base[i]['audit_status'] == 'OPEN'), 'E6': sorted(i for i in E_ONLY if base[i]['audit_status'] == 'OPEN'), 'SC': sorted(i for i in accepted if base[i]['audit_status'] == 'OPEN')}
print('NEWLY CLOSED (previously OPEN):', {k: len(v) for k, v in newrows.items()}, 'ledger:', cnt)
print('NEWLY CLOSED rows', json.dumps(newrows))
