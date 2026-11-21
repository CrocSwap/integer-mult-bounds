import os, gzip, collections, pickle
os.chdir('code/drat55')
rows = {}
for l in open('results.tsv'):
    f = l.rstrip('\n').split('\t')
    if len(f) < 9: continue
    if f[0] in rows and rows[f[0]][6]=='VERIFIED': continue
    rows[f[0]] = f
def verdict(b, f):
    v = f[6]
    if v == '' and f[1] == 'UNSATISFIABLE':
        try:
            t = gzip.open(f'logs/{b}.dlog.gz', 'rt', errors='ignore').read()
            v = 'NOT_VERIFIED' if 's NOT VERIFIED' in t else ('VERIFIED' if 's VERIFIED' in t else 'NO_VERDICT')
        except Exception as e: v = 'NOLOG'
    return v
split = ['i1_d1le5', 'i1_d1_6', 'i1_d1_7', 'i1_d1_8', 'i0_d0_le6', 'i0_d0_7', 'j8_le5', 'j8_6', 'j8_7', 'j8_8']
reps = pickle.load(open('code/tight55/reps.pkl', 'rb'))
orig = split + [f'i{m}' for m in reps if m != 1]
F = pickle.load(open('F_masks.pkl', 'rb')); gap = [f'f{m}' for m in F]
def rep(name, names):
    c = collections.Counter(); tm = 0; kt = 0
    for b in names:
        if b not in rows: c['pending'] += 1; continue
        v = verdict(b, rows[b]); s = rows[b][1]
        c[(s, v)] += 1; tm += float(rows[b][7] or 0); kt += float(rows[b][2])
    print(f'{name}: {len(names)} cubes; ' + ', '.join(f'{k}={v}' for k, v in c.items()) + f'; kissat {kt:.0f}s drat-trim {tm:.0f}s')
rep('ORIGINAL decisive cubes (10 split + 400 ic, i1/i0_d0_8 parents excluded)', orig)
rep('GAP cubes (I with a G-lexmax d but not indicator-lexmax)', gap)
print('proof bytes checked:', sum(int(r[3]) for r in rows.values()))
bad = [b for b, f in rows.items() if f[1] != 'UNSATISFIABLE' or not verdict(b, f).startswith('VERIFIED') or 'MISMATCH' in verdict(b, f)]
print('non-UNSAT or not-VERIFIED:', bad)
