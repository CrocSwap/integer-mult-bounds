# Assertions on the logs written by verify.sh.  usage: check_logs.py LOGDIR   (prints PASS/FAIL lines; exit 1 on any FAIL)
import re, sys, ast, os
D = sys.argv[1]; bad = 0
def rd(n):
    p = os.path.join(D, n + '.log')
    return open(p).read() if os.path.exists(p) else None
def ok(name, cond, extra=''):
    global bad
    print(('PASS ' if cond else 'FAIL ') + name + (' ' + extra if extra else '')); bad += (not cond)
def has(n, *subs):
    t = rd(n); return t is not None and all(s in t for s in subs)

ok('dump: data/data.json regenerated from the geometry (base.py) is byte-identical', has('dump', 'data.json regenerated: identical'))
ok('chk1: labels (1, r mod 2) of rank 9, 112 distinct, kappa formula = oscommon cost', has('chk1', 'rank lab 9 rank mylab 9 rank combined 9', 'distinct labels 112', 'kappa formula ok True'))
t = rd('w8') or ''
zs = re.findall(r'^z (\d+) flat lines 56 compl rank 7 \|Off\(h\)\| 56 Off inside flat True h~f_i \[(\d)\]', t, re.M)
ok('w8: exactly 8 label hyperplanes have complement of real rank <= 7; each is W_i with Off = N(f_i), 56 lines', len(zs) == 8 and sorted(int(b) for _, b in zs) == list(range(8)) and len(re.findall(r'^z ', t, re.M)) == 8)
ok('g78: g(8) = 64, g(7) = 36 over the 43435 seven-dimensional label subspaces', has('g78', 'g78 OK'))
ok('gsmall: g(6) = 20, g(5) = 12 (label-rank maxima {6: 20, 5: 12, 4: 8})', has('gsmall', "{6: 20, 5: 12, 4: 8}", 'g(5)= 12'))
ok('flats_classify: N_u = 1,3,6,12,20,36,63; flats with >= 36 lines are E7/D7/E6+A1/E6; every E6 flat holds >= 2 frame lines', has('flats_classify', 'flats_classify OK'))
ok('gen_targets: |Off(h)| <= 73 directions: 112 roots (53), 8 frame (56), 128 x 70, 896 x 73', has('gen_targets', "Counter({(4, 73): 896, (4, 70): 128, (2, 53): 112, (2, 56): 8})"))
ok('gen_t3: complete list of 1200 directions with |Off| <= 76; the norm-6 (E6+A1) directions have |Off| >= 77', has('gen_t3_76', '(4, 42, 76) 56', '(6, 37, 77) 2688', '\n1200\n') and min(int(x) for x in re.findall(r'\(6, 37, (\d+)\)', rd('gen_t3_76'))) == 77)
ok('cover: min cover of N(f_i) by two 7-flats = 14; Off(r) has no pair cover; best <=3-cover of Off(r) has weight 15', has('cover', 'N(f0) |T| 56 best pair cover 14', 'Off(r0) |T| 53 best pair cover 99', 'Off(r0) best <=3-cover 15'))
ok('symcheck: line symmetries are label-linear and transitive on the 112 roots and the 8 frame targets (one root target / one frame target suffice for cover facts)', has('symcheck', 'symcheck OK'))
ok('cover761: for all 112 roots the weight-14 shape (7,6,1) leaves >= 9 lines of Off(r) uncovered (so W >= 15 for any cover with >= 3 pieces)', has('cover761', 'Counter({(3, 48, 9): 112})', 'minimum uncovered lines over (7,6) pairs: 9'))
t = rd('gT') or ''
G = {n: ast.literal_eval(re.search(r"%s \d+ (\{.*\})" % re.escape(n), t).group(1)) for n in ('N(f0)', 'Off(r0)')} if t else {}
ok('gT: in-target capacities G(w) of 7-/6-flats are <= (32, 20) and G(w) <= (1,2,4,8,12,20,32) elementwise', bool(G) and all(G[n][7] == 32 and G[n][6] == 20 and all(G[n][w] <= [0, 1, 2, 4, 8, 12, 20, 32][w] for w in range(1, 8)) for n in G))
ok('d7: the 70-line Off sets of the 1080 norm-4 directions are not covered by two 7-flats', has('d7', '70-line Off sets pair-coverable: 0', 'Counter({73: 896, 70: 128, 76: 56})'))
ok('cover6: three (dim <= 6) flats cannot cover Off(r); they can cover N(f_i) (6,6,6)', has('cover6', 'Off(r0) 3-cover by dim<=6 exists: False', 'N(f0) 3-cover by dim<=6 exists: True'))
dp = [int(x) for x in re.findall(r'eps-free d \d DP \[(\d+),', rd('dp3') or '')]
ok('dp3: DP minima of cost(T) for d = 1..8 are 14,22,29,36,42,48,55,61 (need 8d = 8,..,64)', dp == [14, 22, 29, 36, 42, 48, 55, 61], str(dp))
en = {d: rd('enum_%d' % d) or '' for d in range(1, 9)}
ok('enum: multisets of cost(T) < 8d passing the DP rules: none for d <= 6, one for d = 7 ([7,6^8], 55), seven for d = 8', all(en[d].startswith('0 multisets') for d in range(1, 7)) and en[7].startswith('1 multisets') and '(55, [7, 6, 6, 6, 6, 6, 6, 6, 6])' in en[7] and en[8].startswith('7 multisets'))
lp3 = [ast.literal_eval(l.split('] ', 1)[1].replace('np.True_', 'True')) if l.startswith('[') else None for l in (rd('lp3') or '').splitlines()]
lp3d7 = [l for l in (rd('lp3') or '').splitlines() if l.startswith('d=7')]
r8 = [x for x in lp3 if x]
ok('lp3: 7 (d=8) exact INTEGER dual certificates (A^T y >= 1 in exact int arithmetic), bounds < 112', len(r8) == 7 and all(x[1] is True and x[2] < 112 for x in r8), str([round(x[2], 2) for x in r8]))
ok('lp3: d = 7 certificate, bound < 111', len(lp3d7) == 1 and 'True' in lp3d7[0] and float(lp3d7[0].split(', ')[2]) < 111)
t = rd('symlp') or ''
fr = re.findall(r'Fraction\((\d+), (\d+)\)', t)
ok('symlp (independent symmetrised LP, exact rational repaired dual): 7 d=8 bounds < 112, d=7 bound < 111; controls [8]^8 give exactly 112',
   len(fr) >= 10 and all(int(a) / int(b) < 112 for a, b in fr[:7]) and int(fr[7][0]) / int(fr[7][1]) < 111 and 'CONTROL [8]^8 d=8: (112.0, Fraction(112, 1))' in t and 'CONTROL [8]^8 d=7 (need 111): (112.0, Fraction(112, 1))' in t)
t = rd('eq') or ''
surv = [ast.literal_eval(re.search(r'(\[.*?\])', l).group(1)) for l in t.splitlines() if l.endswith('SURVIVES')]
ok('eq (Theorem U-prime inputs): cost(T) = 8d exactly: d = 6,7 fully killed by the quotient LP; d = 8 leaves exactly [7^9,1], [7^8,6,2], [7^8,6,1,1]', len(t.splitlines()) == 21 and sorted(surv) == sorted([[7]*8+[6, 1, 1], [7]*8+[6, 2], [7]*9+[1]]) and t.count('KILLED') == 18)
t = rd('eq2') or ''
ok('eq2: slack 0 survivors: none for d = 6, 7; the same 3 for d = 8', 'd 6 slack 0 multisets 1 LP-survivors 0' in t and 'd 7 slack 0 multisets 2 LP-survivors 0' in t and 'd 8 slack 0 multisets 18 LP-survivors 3' in t)
t = rd('land') or ''
sv = [(l.split()[1], l.split()[3]) for l in t.splitlines() if "'SURV': 0" not in l]
ok('land: after LP + Pencil + e=2 triple rule, slack <= 2 leaves survivors only at d = 8, slack 2 (the six multisets)', len(t.splitlines()) == 24 and sv == [('8', '2')] and "'SURV': 6" in t)
t = rd('c65') or ''
sv = [ast.literal_eval(re.search(r'(\[.*?\])', l).group(1)) for l in t.splitlines() if l.endswith('SURVIVES')]
ok('c65: cost(T) <= 8d+1: LP-survivors are the 7^k + small multisets (d = 7: 3, d = 8: 8) and [7^5,6^5]; N(r) has no coloops', len(sv) == 12 and sum(1 for s in sv if s.count(7) < 7) == 1 and [7]*5+[6]*5 in sv and 'coloops found 0' in t)
t = rd('c66') or ''
six = sorted(ast.literal_eval(re.search(r'(\[.*?\])', l).group(1)) for l in t.splitlines() if l.endswith('SURVIVES'))
want = sorted([[7]*5+[6]*5+[1], [7]*6+[6]*4, [7]*8+[5, 4, 1], [7]*8+[5, 5], [7]*8+[6, 3, 1], [7]*8+[6, 4]])
ok('c66: cost(T) <= 8d+2: after LP, Pencil, e=2 triple rule exactly the SIX d = 8 multisets survive', six == want)
ok('coloop: rank <= 8 targets = the 8 frame targets; for the 112 root targets exactly one coloop each', has('coloop', 'rank<=8 targets (frame): 8  root-coloop pairs: 112  other: 0'))
ok('coloop2: N(r) minus any <= 3 lines still has label rank 8', has('coloop2', 'N size 52', 'min rank of N(r) minus <=3 lines: 8'))
t = rd('rootswap') or ''
ok('rootswap: root-swap family, exact P Y = C: eps-free 64+k, k corrections, corrected cost 64 for k = 1..4; pair-coloop fact', 'root targets: pairs dropping rank without the coloop: 0' in t and all(('eps-free %d corrections %d corrected cost 64' % (64 + k, k)) in t for k in (1, 2, 3, 4)))
ok('rootswap_audit: independent scan: weight-<=8 carriers of a z_i are exactly the root swaps', has('rootswap_audit', 't with deviations 0', "('r', 8, True): 112"))
ok('lemmaN (independent C implementation, 1200 directions from lnprep): max 2 active directions per 7-flat, 0 violations', has('lemmaN', '7-flats 43435 dirs 1200', 'F checked 43435', 'max active per F 2, violations 0'))
ok('ncount (|L| = 1, exact): max N = 2', has('ncount', 'max N = 2'))
ok('ncount2 (|L| = 2, exact): max N2 = 2', has('ncount2', 'max N2 = 2'))
ok('mu76 (|L| <= 4, upper bound over all removal sets): max UB = 2 for k = 0..4', all(('k=%d max UB=2' % k) in (rd('mu76') or '') for k in range(5)))
sys.exit(1 if bad else 0)
