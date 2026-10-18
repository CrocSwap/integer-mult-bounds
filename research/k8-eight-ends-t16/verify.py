"""Rebuild the endpoint word, then replay the frozen T16 witness without optimization."""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PRE = ROOT / 'research/k8-eight-ends'
UP = ROOT / 'research/gauge44-slots'


def read(path):
    path = Path(path)
    b = path.read_bytes()
    return json.loads(gzip.decompress(b) if path.suffix == '.gz' else b)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def payload(path):
    return hashlib.sha256(gzip.decompress(Path(path).read_bytes())).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert __debug__, 'Assertions required'
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--native-from', type=Path)
    a = ap.parse_args()
    work = a.work.resolve()
    assert not work.exists() and not work.is_relative_to(ROOT)
    for name, h in read(P / 'MANIFEST.json').items():
        assert sha(P / name) == h, ('package drift', name)
    for name, h in read(P / 'SOURCE-PINS.json').items():
        assert sha(ROOT / name) == h, ('source drift', name)
    for name, pins in read(P / 'UPSTREAM.json')['files'].items():
        b = (P / 'vendor/pr1074' / name).read_bytes()
        assert hashlib.sha256(b).hexdigest() == pins['sha256'], name
        assert hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest() == pins['git_blob'], name
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    for name in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(name, None)
    steps = []

    def run(name, script, *args):
        t = time.monotonic()
        log = work / (name + '.log')
        with log.open('w') as f:
            result = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                                    cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT)
        steps.append(dict(step=name, exit_code=result.returncode, seconds=time.monotonic()-t,
                          log_sha256=sha(log)))
        dump(work / 'STEPS.json', steps)
        assert result.returncode == 0, (name, log.read_text()[-6000:])
        print('PASS', name, flush=True)

    raw = work / 'FULL-WORD.json.gz'
    run('build', PRE / 'build_word.py', '--base', a.base.resolve(), '--out', raw)
    assert payload(raw) == read(PRE / 'RECIPE.json')['output_content_sha256'] == payload(PRE / 'FULL-WORD.json.gz')
    run('independent-local', UP / 'independent/audit_local.py', '--word', raw, '--main', ROOT,
        '--output', work / 'AUDIT-LOCAL.json')
    run('end-controls', PRE / 'end_controls.py', work / 'END-CONTROLS.json')
    assert len(read(work / 'END-CONTROLS.json')['rejected']) == 32
    if a.native_from:
        native = a.native_from.resolve()
    else:
        native = work / 'native'
        run('native', PRE / 'replay_native.py', raw, native)
    ns = read(native / 'STEPS.json')
    assert [s['step'] for s in ns] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
    assert all(s['exit_code'] == 0 for s in ns)
    for s in ns:
        if 'log_sha256' in s:
            assert sha(native / (s['step'] + '.log')) == s['log_sha256'], s['step']
    native_logs = {s['step']: sha(native / (s['step'] + '.log')) for s in ns}
    local = native / 'local'
    assert payload(local / 'FULL-WORD.json.gz') == payload(raw)
    spec = importlib.util.spec_from_file_location('native_identity', UP / 'code/generated_identity.py')
    ident = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ident)
    identities = ident.artifact_identities(local)
    assert identities == read(PRE / 'PLAN.json.gz')['provider_registry']['gauge44']['artifact_semantic_sha256']
    assert identities == read(P / 'PLAN.json.gz')['provider_registry']['gauge44']['artifact_semantic_sha256']

    runtime = work / 'runtime'
    shutil.copytree(P / 'vendor/pr1074', runtime, ignore=shutil.ignore_patterns('__pycache__'))
    data = runtime / 'data'
    (data / 'T8').mkdir()
    (data / 'T8/PLAN.json').write_bytes(gzip.decompress((PRE / 'PLAN.json.gz').read_bytes()))
    shutil.copy2(PRE / 'OWNERS.json.gz', data / 'T8/OWNERS.json.gz')
    shutil.copy2(PRE / 'SPEC.json', data / 'SPEC-T8.json')
    (data / 'PLAN.json').write_bytes(gzip.decompress((P / 'PLAN.json.gz').read_bytes()))
    for name in ('OWNERS.json.gz', 'SPEC.json'):
        shutil.copy2(P / name, data / name)
    run('strict-t16', runtime / 'verify_t16.py', '--main', ROOT, '--local', local, '--work', work / 't16')
    result = read(work / 't16/REPLAY.json')
    claim = read(P / 'CLAIM.json')
    assert result['kappa_decimal'] == claim['kappa_decimal']
    assert result['complex_profile'] == read(P / 'PLAN.json.gz')['profile'] == claim['global_profile']
    assert Fraction(result['kappa']) > Fraction(claim['previous_kappa'])
    run('all-replica-bound', P / 'independent/all_t_bound.py', '--out', work / 'ALL-T-BOUND.json')
    bound = read(work / 'ALL-T-BOUND.json')
    assert bound == read(P / 'evidence/ALL-T-BOUND.json')
    assert Fraction(result['kappa']) < Fraction(bound['kappa_strict_rational_upper'])
    receipt = dict(status='PASS_K8_EIGHT_ENDS_T16_COMPLETE_ADMISSION',
                   kappa_decimal=result['kappa_decimal'], complex_lower=result['complex_lower'],
                   bit_lower=result['bit_lower'], previous_kappa=claim['previous_kappa'],
                   end_controls=32, controls=result['controls'], outer_strict_inequalities=47,
                   native_steps=ns, native_log_sha256=native_logs, native_reuse=bool(a.native_from), native_semantic_artifacts=identities,
                   fixed_family_all_replica_grid_upper=bound['all_T_grid_upper_decimal'],
                   replay_sha256=sha(work / 't16/REPLAY.json'), scope=claim['scope'], steps=steps)
    dump(work / 'RESULT.json', receipt)
    print(receipt['status'], receipt['kappa_decimal'])


if __name__ == '__main__':
    main()
