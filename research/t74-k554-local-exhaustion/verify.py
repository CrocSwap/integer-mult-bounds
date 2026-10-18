"""Replay of the local-exhaustion research package (assertions must be enabled).

Default (about 10 minutes, 2 cores):
  1. package MANIFEST and input pins;
  2. exact frame optimum of both current words equals their published local profiles;
  3. oracle calibration on the pivot-554 kernel (tools/validate554.py);
  4. a deterministic sample of 32 single-read deletion relaxations and 32 commuting-move prices re-solved exactly and compared
     with data/relaxation-B.json and data/move-sweep.json;
  5. the cost-aware compensation search re-run on all 16 one-split reads (budget 4912: no solution);
  6. the aggregate T74 packing ILPs (tools/aggT74.py for k = 0, 12, 24; tools/aggmix.py);
  7. RESULTS.json recomputed from the data files.
--full additionally re-solves every relaxation and every move position (several CPU hours)."""
import argparse, gzip, hashlib, json, os, subprocess, sys, time
from pathlib import Path
P = Path(__file__).resolve().parent; T = P / 'tools'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    if not __debug__: raise RuntimeError('Assertions required')
    ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--full', action='store_true'); a = ap.parse_args()
    work = a.work.resolve(); assert not work.exists(); work.mkdir(parents=True)
    pins = json.loads((P / 'MANIFEST.json').read_text())
    have = {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p != P / 'MANIFEST.json'}
    assert have == set(pins), sorted(have ^ set(pins))
    for n, h in pins.items(): assert sha(P / n) == h, n
    ip = json.loads((P / 'inputs/PINS.json').read_text())
    for n, v in ip.items():
        if n.startswith('vendor'): continue
        assert sha(P / 'inputs' / n) == v['sha256'], n
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OUT_DIR=str(work)); env.setdefault('IMB_ROOT', str(P.parents[1])); stages = []
    def run(name, *args, timeout=7200):
        t = time.monotonic(); log = work / (name + '.log')
        with log.open('w') as f: r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=T, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
        stages.append(dict(name=name, exit_code=r.returncode, seconds=round(time.monotonic() - t, 1))); (work / 'STAGES.json').write_text(json.dumps(stages, indent=2))
        assert r.returncode == 0, (name, log.read_text()[-2000:]); print('PASS', name, flush=True); return log.read_text()
    run('profiles', T / 'check_profiles.py')
    out = run('oracle-calibration', T / 'validate554.py'); assert 'PASS_ORACLE_CALIBRATION_K554' in out
    run('sample-replay', T / 'sample_replay.py', P / 'data', 32 if not a.full else 0)
    out = run('one-split-searches', T / 'gencomp2.py', P / 'inputs/gauge44-word-566.json.gz', json.dumps([[r['gate']] for r in json.loads((P / 'RESULTS.json').read_text())['b_deletion_relaxation']['one_split_reads']]), 12, 4, 30)
    summ = [l for l in out.splitlines() if l.startswith('SUMMARY')]
    assert len(summ) == 16 and all(' nsol 0 ' in l for l in summ), summ
    for k in (0, 12, 24):
        out = run('pack-k%d' % k, T / 'aggT74.py', k); assert ('OPTIMAL' in out) == (k == 0) and ('INFEASIBLE' in out) == (k > 0), out
    out = run('pack-mix', T / 'aggmix.py'); assert 'OPTIMAL empty48 22748' in out and 'bound 22748' in out, out
    run('results', T / 'summarize.py', P)
    (work / 'RESULT.json').write_text(json.dumps(dict(status='PASS_LOCAL_EXHAUSTION_REPLAY', full=a.full, package_manifest=sha(P / 'MANIFEST.json'), stages=stages), indent=2) + '\n')
    print('PASS_LOCAL_EXHAUSTION_REPLAY', flush=True)
if __name__ == '__main__': main()
