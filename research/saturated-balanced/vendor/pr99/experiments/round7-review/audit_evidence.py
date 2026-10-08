"""Bind successful finite checks to their exact inputs and checking code."""
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def snapshot(kind, candidate):
    inputs = {'candidate': digest(candidate)}
    sources = [Path(__file__)]
    if kind == 'frames':
        sources += [HERE / 'check_candidate_frames.py']
        sources += list((HERE / 'vendor').rglob('*.py'))
        for name in ('witness_23.json.gz', 'deferred_23.json.gz'):
            inputs[name] = digest(HERE / 'vendor/certificates/round7' / name)
    elif kind == 'scalar':
        sources += [HERE / 'scalar_engine.py']
    else:
        raise ValueError('unknown audit kind: ' + kind)
    return dict(input_sha256=inputs, checker_sha256={
        str(p.relative_to(ROOT)): digest(p) for p in sorted(set(sources))})


def receipt_path(kind):
    return HERE / ('candidate-' + kind + '-receipt.json')


def record(kind, candidate, before, checks, artifacts=None):
    assert before == snapshot(kind, candidate), 'audit inputs/checker changed during execution'
    assert checks and all(checks.values()), 'audit did not pass every required check'
    row = dict(schema=1, kind=kind, status='PASS', **before, checks=checks,
               python_version=sys.version, artifacts={str(Path(p).resolve()): digest(p)
                   for p in (artifacts or [])})
    path = receipt_path(kind)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(row, indent=2) + '\n')
    temp.replace(path)
    return path


def verify(kind, candidate, path=None):
    path = Path(path) if path is not None else receipt_path(kind)
    row = json.loads(path.read_text())
    assert row['schema'] == 1 and row['kind'] == kind and row['status'] == 'PASS'
    actual = snapshot(kind, candidate)
    assert row['input_sha256'] == actual['input_sha256'], 'stale candidate/input evidence'
    assert row['checker_sha256'] == actual['checker_sha256'], 'stale checking-code evidence'
    assert row['checks'] and all(row['checks'].values())
    if kind == 'frames':
        assert len(row['checks']) >= 19, 'incomplete frame check set'
        for prefix in ('X.', 'Q.', 'S.', 'F.', 'N.'):
            assert any(k.startswith(prefix) for k in row['checks']), 'missing check class: ' + prefix
    else:
        assert set(row['checks']) == {'full_basis', 'scratch_restored', 'outputs_exact',
                                     'negative_controls_detected', 'integer_samples'}
    for p, h in row['artifacts'].items():
        assert digest(p) == h, 'stale audit result: ' + p
    return row
