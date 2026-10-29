# Re-checks the span passes from the raw s3z outputs: for each config every chunk (M mod x r x JMOD x j) must exist, carry an OVERALL line with
# target == passT, the right dims/s/lim, mod/rem and "max span" < passT, and no CRACK line.  Pass at T => span <= T-1.
# usage: sc_check.py GOODFILE [rerun_dir]   (rerun_dir: fresh outputs named like the shipped ones; they take precedence)
import json, glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
dirs = ([sys.argv[2]] if len(sys.argv) > 2 else []) + [os.path.join(ROOT, 'evidence', d) for d in ('sc_rerun751', 'sc_rerun752', 'sc_runs')]
good = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'sc', 'state', '*.json'))):
    v = json.load(open(f)); k = os.path.basename(f)[:-5]; T = v['passT']; arr = v['arr']; M, _, J, _ = v['chunks'][0]
    s = int(k[-1]); bad = []; nfile = 0
    for r in range(M):
        for j in range(J):
            name = '%s_M%dr%dJ%dj%d.out' % (k, M, r, J, j)
            p = next((os.path.join(d, name) for d in dirs if os.path.exists(os.path.join(d, name))), None)
            if not p: bad.append(name + ' MISSING'); continue
            t = open(p).read(); nfile += 1
            m = re.search(r'OVERALL \S+ dims (\d+) (\d+) (\d+) s (\d+) lim (\d+) target (\d+) mod (\d+) rem (\d+): pairs (\d+) surviving (\d+) leaves (\d+) overflow (\d+) max span (\d+)', t)
            if 'CRACK' in t or not m: bad.append(name + ' no OVERALL/CRACK'); continue
            g = [int(x) for x in m.groups()]
            if g[:3] != arr or g[3] != s or g[4] != (80 if k.startswith('6-6-2') else 88) or g[5] > T or g[6] != M or g[7] != r or g[12] >= g[5] or g[11] != 0: bad.append(name + ' fields %s' % g)
    print(('PASS' if not bad else 'FAIL') + ' span pass %s at T=%d: %d chunks (mod %d x JMOD %d), every chunk target <= T, max span < T, no CRACK, overflow 0 %s' % (k, T, nfile, M, J, bad[:2]))
    if not bad: good.append(k)
open(sys.argv[1], 'w').write('\n'.join(good) + '\n')
