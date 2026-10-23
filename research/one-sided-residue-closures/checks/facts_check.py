# Asserts that the covering facts recomputed by anroot.py / annon.py (outputs passed as argv[1], argv[2]) support every parameter used by lemp_audit.params.
import re, sys
a = open(sys.argv[1]).read(); b = open(sys.argv[2]).read(); ok = True
def chk(name, cond):
    global ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name)
g = lambda pat, s: re.search(pat, s)
chk('F3(a): three <=6-flats cover Off(r) minus L only if |L| >= 4 (root not in L)', int(g(r'\(a\) min \|L\| = (\d+)', a).group(1)) == 4)
chk('F3(b): exactly 96 four-line leftovers per root, all of label rank 4', g(r'\(b\) #4-leftovers per root 96  ranks Counter\(\{4: 96\}\)', a) is not None)
nb = eval(g(r'by size: (\{.*?\})', a).group(1))
chk('each 4-line leftover serves <= 1 root, 5-line <= 2, 6-line <= 1', nb[4] == 1 and nb[5] <= 2 and nb[6] == 1)
chk('F3(c): a 5-line X serves <= 4 roots outside X  (sigma(s=5) <= 5+4 = 9)', int(g(r'\(c\) .*: (\d+)', a).group(1)) <= 4)
chk('F3(d): 6-line X: roots outside X <= 15*1+6*2+1 = 28 (sigma <= 6+28 = 34)', int(g(r'\(d\) .* = (\d+)', a).group(1)) <= 28)
chk('F3(e): X = 4-flat set serves <= 1 root outside X  (sigma({4}) <= 8+1 = 9)', int(g(r'\(e\) .*?: (\d+)', a).group(1)) <= 1)
chk('F3(f): X = 4-flat set + 1 line serves <= 8 roots outside X  (sigma({1,4}) <= 9+8 = 17)', int(g(r'\(f\) .*?: (\d+)', a).group(1)) <= 8)
rows = re.findall(r"^\((\d+), (\d+), (\d+), '(\w+)', '(\d+)', 'min', (\S+), 'hist', .*?'six', (\d+), 'bad6', (\d+), 'formF', (\d+)", b, re.M)
chk('annon covers all 17 orbit representatives', len(rows) == 17)
R = [dict(sz=int(r[1]), left=int(r[4]), mn=r[5], six=int(r[6]), bad6=int(r[7]), formF=int(r[8])) for r in rows]
chk('F4: every non-E8 direction (|Off| <= 89, 17 orbits) has min leftover >= 6 for four <=6-flats (so s <= 5 gives omega\'=0)', all(x['mn'] == "'>9'" or int(x['mn']) >= 6 for x in R))
chk('F4: 6-line leftovers occur only for |Off| in {79, 80} (16 six-sets each) and none contains a 4-set of label rank <= 3 (omega\'=0 for the s=6 types {1,1,3},{2,3})',
    {x['sz'] for x in R if x['six']} == {79, 80} and all(x['six'] == 16 for x in R if x['six']) and all(x['bad6'] == 0 for x in R))
chk('F4: form-F leftovers (<=9 lines, rank <=4 or +1 line) exist only for the |Off|=70 orbit; no family mask has one', [x['sz'] for x in R if x['formF']] == [70] and 'family masks with form-F leftovers (would give infinitely many directions): []' in b)
chk('F4: one 4-flat set (8 lines, D7 type) serves <= 32 directions; 4-flat set + 1 line <= 32  (omega\' in {0, 32})',
    int(g(r'X = 4-flat set: max #directions served (\d+)', b).group(1)) == 32 and int(g(r'X = 4-flat set \+ 1 line: max #directions served (\d+)', b).group(1)) == 32)
chk('no leftover of <= 9 lines at all for |Off| = 89 (four 6-flats cannot cover 80 of 89)', [x for x in R if x['sz'] == 89 and x['left'] == 0 and x['mn'] == "'>9'"] != [])
print('PASS facts' if ok else 'FAIL facts'); sys.exit(0 if ok else 1)
