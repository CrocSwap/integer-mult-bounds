# Step 3 of verify.sh: every number the README quotes from a script, as PASS/FAIL lines.  usage: python check_logs.py LOGDIR
import os, sys, re, itertools, ast
D = sys.argv[1]; ok = True
def log(n):
    p = os.path.join(D, n + '.log'); return open(p).read() if os.path.exists(p) else ''
def chk(name, cond):
    global ok
    print(('PASS ' if cond else 'FAIL ') + name); ok = ok and cond
# clique.py
t = log('clique')
chk('clique.py: 255 compatible non-frame classes for each i', 'compatible nonframe classes per i: [255, 255, 255, 255, 255, 255, 255, 255]' in t)
chk('clique.py: 35400 class pairs with deficient Theta-rank', 'pairs with nontrivial Theta-perp: 35400' in t)
# clique2.py 5 on all 93 sets
pat = re.compile(r'Ic \(([0-9, ]*)\) vertices (\d+) edges (\d+) max clique\(distinct i\) \d+ cliques>=5 passing joint (\d+)')
rows = []
for k in range(4): rows += pat.findall(log('c2_%d' % k))
sets = {tuple(int(x) for x in r[0].replace(' ', '').split(',') if x) for r in rows}
want = {c for k in range(4) for c in itertools.combinations(range(8), k)}
chk('clique2.py 5: all 93 sets I^c (|I^c| <= 3) were run (%d lines, %d distinct)' % (len(rows), len(sets)), len(rows) == 93 and sets == want)
chk('clique2.py 5: no 5-clique passes the joint test on any of the 93 sets', len(rows) == 93 and all(r[3] == '0' for r in rows))
VE = {0: (2040, 3584), 1: (1785, 2856), 2: (1530, 9648), 3: (1275, 16496)}
chk('clique2.py 5: vertex/edge counts 2040/3584, 1785/2856, 1530/9648, 1275/16496 by |I^c|',
    all((int(r[1]), int(r[2])) == VE[len([x for x in r[0].replace(' ', '').split(',') if x])] for r in rows))
# verify_cl.py
cl = {}
for n in ['vcl_none', 'vcl_0', 'vcl_0_1', 'vcl_0_1_2']:
    m = re.search(r'VERIFY Ic \(([0-9, ]*)\) vertices (\d+) edges (\d+) maximal clique sizes (\[.*\])', log(n))
    if m: cl[n] = (int(m.group(2)), int(m.group(3)), ast.literal_eval(m.group(4)))
for n, k, mx in [('vcl_none', 0, 2), ('vcl_0', 1, 2), ('vcl_0_1', 2, 2), ('vcl_0_1_2', 3, 4)]:
    chk('verify_cl.py |I^c| = %d: vertices/edges %s, largest clique %d' % (k, VE[k], mx), n in cl and (cl[n][0], cl[n][1]) == VE[k] and max(s for s, _ in cl[n][2]) == mx)
chk('verify_cl.py {0,1,2}: 7936 maximal 4-cliques', 'vcl_0_1_2' in cl and (4, 7936) in cl['vcl_0_1_2'][2])
# sym.py / stab.py
t = log('sym')
chk('sym.py: stabiliser of order 1344 preserves {O_z} and compat (0 failures), one orbit on 3-sets', 'group order 1344' in t and 'elements failing O-family/compat invariance: 0' in t and 'orbits on 3-sets: {(0, 1, 2)}' in t)
t = log('stab')
chk('stab.py: permutation part of order 1344; one orbit on 3-sets, two on 4-sets', 'perm group order 1344' in t and '3 orbits [(0, 1, 2)]' in t and '4 orbits [(0, 1, 2, 3), (0, 1, 2, 4)]' in t)
# witnesses
t = log('w16')
chk('witness16.py disjoint: P Q^T = N0 on all entries, m 10, cost 64, |J_P| = |J_Q| = 3, K empty, no proportional terms',
    bool(re.search(r"disjoint .* m 10 PQ\^T=N0 mismatches 0 cost 64 \|J_P\| 3 \|J_Q\| 3 K \[\] proportional pairs \[\]", t)))
chk('witness16.py shared: exact, m 10, cost 64, |J_P| 4, |J_Q| 3, |K| = 2, no proportional terms',
    bool(re.search(r"shared .* m 10 PQ\^T=N0 mismatches 0 cost 64 \|J_P\| 4 \|J_Q\| 3 K \[3, 4\] proportional pairs \[\]", t)))
# Case B
t = log('d9')
chk('diag9.py: 280 pairs (J, m), none has candidates for all five columns', "{'us': 0, 'nonorth': 0, 'sol': 0, 'vl': 0} {'nocand': 280}" in t)
tot = {'rows_ok': 0, 'lin': 0, 'lin_s2': 0, 'full': 0, 'full_s2': 0}; good = True
for k in range(3):
    t = log('cb4_%d' % k)
    m = re.search(r'chunk %d of 3 (\{.*\})' % k, t)
    good = good and ('#blocks 14 S(3,4,8): True' in t) and bool(m)
    if m:
        for a, b in ast.literal_eval(m.group(1)).items(): tot[a] += b
chk('caseb4.py: 14 blocks form S(3,4,8) (each chunk)', good)
chk('caseb4.py: 917504 row patterns, 22020096 linear-core solutions, none with s = 2 at both repeated terms, none valid (lin_s2 = full = full_s2 = 0)',
    tot == {'rows_ok': 917504, 'lin': 22020096, 'lin_s2': 0, 'full': 0, 'full_s2': 0})
# Case A chain
t = log('c24')
chk('clique2.py 4 on I^c = {0,1,2,4}: 1020 vertices, 15936 edges, 16128 joint-feasible 4-cliques', 'Ic (0, 1, 2, 4) vertices 1020 edges 15936 max clique(distinct i) 4 cliques>=4 passing joint 16128' in t)
t = log('d4A')
chk('d4A.py: 16128 cliques, 128 column-swap configurations, 128 survive non-orthogonality + joint beta system', 'cliques 16128 all-line-class 5248 column-swap-compatible 128' in t and 'survive (non-orth swap lines + joint beta system): 128' in t)
t = log('d4A2')
chk('d4A2.py: {0,1,2,3} is a block; every configuration has 10 roots orthogonal to the four swap roots', '(0,1,2,3) is a block: True' in t and '[((10, 4), 128)]' in t)
t = log('d4A3')
chk('d4A3.py: 0 of 128 configurations admit a frame row for term a', 'configs 128 with an admissible frame row for term a: 0' in t)
print('ALL PASS' if ok else 'SOME FAIL'); sys.exit(0 if ok else 1)
