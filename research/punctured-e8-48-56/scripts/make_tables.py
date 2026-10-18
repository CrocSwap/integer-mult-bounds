"""Author script: per-leaf result tables data/tables/T{t}_P{P}_k{k}.tsv from data/states (name, |T|, live, result, clauses, options, md5 of the leaf CNF, kissat s, total s)."""
import json, os, glob
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f'{PKG}/data/tables', exist_ok=True)
for f in sorted(glob.glob(f'{PKG}/data/states/*.json')):
    d = json.load(open(f)); out = open(f'{PKG}/data/tables/' + os.path.basename(f)[:-5] + '.tsv', 'w')
    out.write('leaf\t|T|\tlive\tresult\tclauses\toptions\tcnf_md5\tkissat_s\ttotal_s\n')
    for n in sorted(d):
        v = d[n]; out.write('\t'.join(str(x) for x in (n, (len(v['T']) if 'T' in v else ''), ','.join(map(str, v.get('live', []))), v['res'] + ('(split)' if v.get('split') else ''), v.get('clauses', ''), v.get('nopt', ''), v.get('md5', ''), v.get('kissat_s', ''), v.get('s', ''))) + '\n')
