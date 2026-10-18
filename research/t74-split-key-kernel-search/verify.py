"""Bounded replay of the split-key kernel search package (assertions must be enabled).

Stages (each one command in VERIFY.json; Python 3.11+, NumPy and OR-Tools CP-SAT, as for PR1957):
  pins       package MANIFEST and the PR1957 inputs it reads;
  results    RESULTS.json recomputed from data/ (coverage of all 3,451 A gates, search statuses);
  relax      a deterministic sample of 12 A-section deletions re-solved with exact optimal frames and compared to data/;
  control    positive control: on PR1672's pivot-566-only word, deleting B342 must yield an exact -1,850 kernel
             (the search rediscovers k554-signed-001); a coefficient-flipped copy of it must price as inexact;
  negative   two strict searches re-run from scratch (A1215, first priced here; B783): CP-SAT must prove INFEASIBLE.
usage: verify.py [--stage pins|results|relax|control|negative|all] [--work DIR]
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
PR1957 = PKG.parent / 't74-k554-local-exhaustion'
TOOLS = PKG / 'tools'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pins():
    man = json.loads((PKG / 'MANIFEST.json').read_text())
    have = {p.relative_to(PKG).as_posix() for p in PKG.rglob('*') if p.is_file() and '__pycache__' not in p.parts
            and p.name != 'MANIFEST.json'}
    assert have == set(man['files']), sorted(have ^ set(man['files']))
    for n, h in man['files'].items(): assert sha(PKG / n) == h, n
    for n, h in man['inputs'].items(): assert sha(ROOT / n) == h, n
    pr = json.loads((ROOT / man['pr1957_manifest']).read_text())  # PR1957 pins every file of its package
    for n, h in pr.items(): assert sha(PR1957 / n) == h, ('PR1957', n)
    print('PASS_PINS', len(man['files']), 'files', len(man['inputs']), 'inputs', len(pr), 'PR1957 files')


def run(args, env=None, timeout=590):
    e = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', **(env or {})); e.pop('PYTHONOPTIMIZE', None)
    r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=TOOLS, env=e, capture_output=True, text=True, timeout=timeout)
    assert r.returncode == 0, (args, r.stdout[-2000:], r.stderr[-2000:])
    return r.stdout


def results():
    out = run([TOOLS / 'summarize.py', '--check']); assert 'PASS_RESULTS_RECOMPUTED' in out
    d = json.loads((PKG / 'RESULTS.json').read_text()); s = d['strict_searches']
    assert d['a_section_relaxation']['gates'] == 3451 and not s['exact_profitable'] and not s['other']
    assert s['proven_infeasible'] + s['shape_infeasible'] == s['jobs']
    assert d['positive_control'][0]['best_exact_delta'] == -1850
    print('PASS_RESULTS', s['jobs'], 'strict searches,', s['proven_infeasible'], 'proven infeasible')


def relax():
    data = json.loads((PKG / 'data' / 'relaxation-A-rest.json').read_text())
    by = {}
    for k, v in data.items(): by.setdefault(v.get('delta'), []).append(int(k))
    pick = sorted(by[-6763])[:2] + sorted(by[-8857])[:2] + sorted(by[-9826])[:1] + sorted(by[-20839])[:1]
    zero = sorted(by[0], key=lambda i: hashlib.sha256(str(i).encode()).hexdigest())[:6]
    idx = sorted(pick + zero)
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'idx.txt').write_text(','.join(map(str, idx)))
        run([PR1957 / 'tools' / 'relaxAsec.py', PR1957 / 'inputs' / 'gauge44-word-566.json.gz', Path(td) / 'out.json', Path(td) / 'idx.txt'],
            env=dict(IMB_ROOT=str(ROOT)))
        got = json.loads((Path(td) / 'out.json').read_text())
    for i in idx:
        assert got[str(i)]['delta'] == data[str(i)]['delta'], (i, got[str(i)], data[str(i)])
        assert {str(k): v for k, v in got[str(i)]['prof'].items()} == {str(k): v for k, v in data[str(i)]['prof'].items()}, i
    print('PASS_RELAX_SAMPLE', idx)


def search(word, job, work, k=1, extra=None):
    work.mkdir(parents=True, exist_ok=True)
    out = run([TOOLS / 'skkernel.py', word, json.dumps([[job]]), 12, k, 120],
              env=dict(IMB_ROOT=str(ROOT), OUT_DIR=str(work), SK_WORKERS='4', **(extra or {})))
    return json.loads((work / ('sk-%s%d.json' % tuple(job))).read_text()), out


def control(work):
    d, _ = search(PR1957 / 'inputs' / 'step0-gauge44.json.gz', ['B', 342], work / 'control')
    ok = [r for r in d['res'] if r['status'] == 'ok']
    assert ok and ok[0]['delta'] == -1850, d['res']
    ref = json.loads((PR1957 / 'inputs' / 'EDITS-k554.json').read_text())['edit']
    gates = sorted(tuple(g[1:5]) for _, g in ref['insert']) + sorted(tuple(g[1:5]) for _, g in ref['tail'])
    found = sorted(tuple(g[1:5]) for s, _, g in ok[0]['ed']['insert']) + sorted(tuple(g[1:5]) for _, g in ok[0]['ed']['tail'])
    assert sorted(found) == sorted(gates), ('expected k554-signed-001 gates', found, gates)
    # failure control: flip one inserted coefficient; the exact pricer must reject the result as inexact
    sys.path.insert(0, str(TOOLS)); os.environ['IMB_ROOT'] = str(ROOT)
    import skkernel as K
    P = K.H.Pricer(str(PR1957 / 'inputs' / 'step0-gauge44.json.gz'))
    ed = json.loads(json.dumps(ok[0]['ed'])); ed['delete'] = [tuple(x) for x in ed['delete']]
    ed['insert'] = [tuple(x) for x in ed['insert']]; ed['tail'] = [tuple(x) for x in ed['tail']]
    good = K.price(P, ed, K.amap(K.fullseq(P.base))); assert good['status'] == 'ok' and good['delta'] == -1850, good
    s, p, g = ed['insert'][0]; g = list(g); g[3] = -g[3]; ed['insert'][0] = (s, p, g)
    bad = K.price(P, ed, K.amap(K.fullseq(P.base))); assert bad['status'] == 'inexact', bad
    print('PASS_CONTROL rediscovered k554-signed-001 (-1850); flipped coefficient rejected as inexact')


def negative(work, job):
    d, _ = search(PR1957 / 'inputs' / 'gauge44-word-566.json.gz', job, work / 'negative', k=3)
    assert d['cp_status'] == 'INFEASIBLE' and not d['res'], (job, d['cp_status'], d['res'])
    print('PASS_NEGATIVE', job, d['ddel'], 'candidates', d['ncand'], 'keys', len(d['keys']))


def main():
    if not __debug__: raise RuntimeError('Assertions required')
    ap = argparse.ArgumentParser(); ap.add_argument('--stage', default='all'); ap.add_argument('--work', type=Path)
    a = ap.parse_args()
    td = None
    if a.work is None: td = tempfile.TemporaryDirectory(); work = Path(td.name)
    else: work = a.work.resolve()
    st = a.stage
    if st in ('pins', 'all'): pins()
    if st in ('results', 'all'): results()
    if st in ('relax', 'all'): relax()
    if st in ('control', 'all'): control(work)
    if st in ('negative-a', 'negative', 'all'): negative(work, ['A', 1215])
    if st in ('negative-b', 'negative', 'all'): negative(work, ['B', 783])
    print('PASS_SPLIT_KEY_PACKAGE', st)


if __name__ == '__main__':
    main()
