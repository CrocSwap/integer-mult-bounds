# Step 2 of verify.sh: every number the README quotes from a script, as PASS/FAIL lines.  usage: python check_logs.py LOGDIR
import os, sys
D = sys.argv[1]; ok = True
def log(n):
    p = os.path.join(D, n + '.log'); return open(p).read() if os.path.exists(p) else ''
def chk(name, cond):
    global ok; print(('PASS ' if cond else 'FAIL ') + name); ok &= bool(cond)
c1 = log('cat1')
chk('cat1: 1200 directions, |Off| distribution 73:896 70:128 53:112 76:56 56:8', "directions 1200 Counter({73: 896, 70: 128, 53: 112, 76: 56, 56: 8})" in c1)
chk('cat1: |O_z| >= 48', "|O_phi| range 48 112" in c1)
chk('cat1: min 0 only frame roots at frame classes (8)', "(0, 'r', 56, 'frame') 8" in c1)
chk('cat1: min 1 only P112 roots at line classes (112)', "(1, 'r', 53, 'line') 112" in c1)
chk('cat1: min 12 only norm-4 |Off|=76 at non-line classes (56)', "(12, 'n4', 76, 'other') 56" in c1)
rows = [l for l in c1.splitlines() if l.startswith('(')]
chk('cat1: no other (value <= 12) entries', len(rows) == 3)
c2 = log('cat2')
for t in ["('r', 56) [((0, 24, 24), 8)]", "('r', 53) [((1, 20, 20), 112)]", "('n4', 76) [((12, 32, 32), 56)]", "('n4', 73) [((13, 29, 30), 896)]", "('n4', 70) [((14, 30, 30), 128)]"]:
    chk('cat2: smallest three intersections ' + t, t in c2)
chk('gtab: g(8,7,6) = 64, 36, 20', "{8: 64, 7: 36, 6: 20}" in log('gtab'))
p2 = log('pair2')
chk('pair2: all 1200 directions tested', "directions tested: 1200" in p2)
chk('pair2: two deficiency>=2 columns share a coset only along frame roots', "direction types admitting two deficiency>=2 columns: [('r', 56)]" in p2)
f = log('fold')
chk('fold: (0,0) lam=-1 folds 64+64, shared term vanishes, batch 136', "(i,j)=(0,0) lam=-1: batch 136, fold0 64, fold1 64, fold0+fold1 128, shared-term charges 0+0 (batch 8)" in f)
chk('fold: (0,1),(0,5) folds 72+72, shared 8+8 vs batch 9 (all lam)', all(f"(i,j)=({a},{b}) lam={l:2d}: batch 137, fold0 72, fold1 72, fold0+fold1 144, shared-term charges 8+8 (batch 9)" in f for a, b in [(0, 1), (0, 5)] for l in (1, -1, 2)))
chk('fold: 9 fold cases ran (assertions inside)', f.count('(i,j)=') == 9)
chk('transport: dim span lab(R_t) = 8 for all t, 2 transportable labels', "dim span lab(R_t): {8}  #labels y transportable onto t: {2}" in log('transport'))
pp = log('p104prem')
chk('p104prem: P112 8 avoidable hyperplane classes, pair ranks {8: 64}', "P112: label dim h=9; avoidable hyperplane classes=8; avoidable codim-2 subspaces=0; within-call out/in hyperplane pair ranks {8: 64}" in pp)
chk('p104prem: P104 (4 variants) 16 classes, pair ranks {8: 192, 7: 64}', pp.count("avoidable hyperplane classes=16; avoidable codim-2 subspaces=0; within-call out/in hyperplane pair ranks {8: 192, 7: 64}") == 4)
for n, k in (('c_batch_arith', 5), ('c_clique_lemmaE', 4)):
    L = log(n); chk(f'{n}: {k} PASS, 0 FAIL', L.count('PASS ') == k and 'FAIL' not in L)
tb = log('twinblk')
chk('twinblk: ran (28 twin pairs per coordinate asserted), Phi=I: 56 cases with a twin block', "trial 0 Phi=I (any block, induced family LB): {(False, 0): 8, (True, 4): 56}" in tb)
s1 = log('s1close')
chk('s1close: closed 277/512; open = saving 8: 11, saving 7: 224, none with a twin block', "trial 7: closed 277/512; open (saving, n01, n10): {(8, 0, 0): 11, (7, 0, 0): 224}" in s1)
d4 = log('d4')
chk('d4: 56 twelve-overlap (h,z) pairs, 56 distinct sets, all of label span dim 7', "12-overlap (h,z) total 56 distinct sets 56" in d4 and "label span dims of 12-sets Counter({7: 56})" in d4)
om = log('omega')
chk('omega: Omega solved uniquely, symmetric, rank 9', "free vars 0" in om and "sym True" in om and "rank G 9" in om)
chk('omega: Omega(z_i, z_j) = 1 for all frame classes', "Om(x_i,x_j) all ==1? True" in om)
chk('omega: 119616 non-orthogonal-clique cases, z_j never in span', "tested 119616 bad 0" in om)
gl = log('glclique')
chk('glclique: 72 arcs of the 9-term digon clique realised by explicit GL(9,F2) charts, slot normals and h.g = 1 verified', "glclique: 72 arcs of the 9-term digon clique realised by" in gl and "arcs covered 72" in gl)
p56 = log('p104dec56')
chk('p104dec56: exact P104 decoder, 104 live lines, ranks 7^8, cost 56', 'P104 coordinate decoder cost 56: True' in p56)
pr = log('price')
chk('price: K6 break-even prices 55 / 51 / 46 / 42 at h = 11 / 12 / 13 / 14', all(f"h {h} break-even (both >= 1): {c}" in pr for h, c in ((11, 55), (12, 51), (13, 46), (14, 42))))
raise SystemExit(0 if ok else 1)
