#!/usr/bin/env python3
"""Rebuild and independently verify one finite T16 CP-SAT packing improvement."""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P = Path(__file__).resolve().parent
OLD_KAPPA = Q('0.001673614205725695')
CEILING_A_HI = Q(1690054109089, 10**15)
CONTROLS = dict(admission=69, bit_supplier=12, independent_t16=6, controller_mutations=15)


def read_json(path):
    return json.loads(Path(path).read_text())


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean_env():
    env = {k: os.environ[k] for k in ('PATH', 'SYSTEMROOT', 'WINDIR', 'TMPDIR', 'TEMP', 'TMP') if k in os.environ}
    env.update(PYTHONNOUSERSITE='1', PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    return env


def reconstruct(main, work):
    pins = read_json(P/'SOURCES.json')
    for item in pins['files']:
        if item['usage'] == 'input':
            assert digest(main/item['path']) == item['sha256'], 'Changed pinned input: '+item['path']

    # Apply the compact row delta to the immediately preceding owner map.
    prev = main/'research/complex-t16-two-stage-cycles/data/OWNERS.json.gz'
    rows = json.loads(gzip.decompress(prev.read_bytes()))
    diff = read_json(P/'DIFF-vs-predecessor.json')
    assert len(diff) == 163 and [r['index'] for r in diff] == sorted(r['index'] for r in diff)
    moved = 0
    for item in diff:
        i = item['index']
        assert 0 <= i < len(rows) and rows[i] == item['before'], ('delta base mismatch', i)
        before, after = item['before'], item['after']
        assert all(before[k] == after[k] for k in ('stage', 'replica', 'time', 'helper', 'width'))
        moved += any(before[k] != after[k] for k in ('owner_replica', 'child', 'port'))
        rows[i] = after
    assert moved == 142 and len(diff)-moved == 21
    owners = json.loads(gzip.decompress((P/'data/OWNERS.json.gz').read_bytes()))
    assert rows == owners, 'predecessor + delta does not reconstruct the candidate'

    # The existing builder derives all three shipped data files, including the actual chart count.
    rebuilt = work/'rebuilt'
    subprocess.run([sys.executable, '-B', str(main/'research/complex-t16-two-stage-cycles/search/buildcand.py'),
                    str(main/'research/complex-t16-two-stage-cycles/search'), str(P/'data/OWNERS.json.gz'),
                    str(rebuilt), '10008'], cwd=main, env=clean_env(), check=True)
    rebuilt_rows = json.loads(gzip.decompress((rebuilt/'OWNERS.json.gz').read_bytes()))
    assert rebuilt_rows == owners, 'builder changed owner rows'
    # zlib may emit different gzip bytes across Python versions. Compare the
    # complete JSON objects after removing only hashes of those compressed bytes.
    rebuilt_plan, plan = read_json(rebuilt/'PLAN.json'), read_json(P/'data/PLAN.json')
    assert digest(P/'data/OWNERS.json.gz') == plan['assignment_sha256']
    assert digest(P/'data/OWNERS.json.gz') == plan['replica_lift']['owners_file_sha256']
    assert digest(P/'data/PLAN.json') == read_json(P/'data/SPEC.json')['data']['plan_sha256']
    assert digest(P/'data/OWNERS.json.gz') == read_json(P/'data/SPEC.json')['data']['owners_sha256']
    for obj in (rebuilt_plan, plan):
        obj.pop('assignment_sha256')
        obj['replica_lift'].pop('owners_file_sha256')
    assert rebuilt_plan == plan, 'builder mismatch in semantic PLAN fields'
    rebuilt_spec, candidate_spec = read_json(rebuilt/'SPEC.json'), read_json(P/'data/SPEC.json')
    rebuilt_spec['data'] = {'owners_sha256': 'compressed-bytes-vary', 'plan_sha256': 'compressed-bytes-vary'}
    candidate_spec['data'] = {'owners_sha256': 'compressed-bytes-vary', 'plan_sha256': 'compressed-bytes-vary'}
    assert rebuilt_spec == candidate_spec, 'builder mismatch in semantic SPEC fields'


def strict_replay(main, work):
    source = work/'source'
    source.mkdir()
    archive = main/'research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz'
    with tarfile.open(archive) as tar:
        for member in tar.getmembers():
            assert member.isfile() and (source/member.name).resolve().is_relative_to(source.resolve())
        tar.extractall(source, filter='data')
    manifest = read_json(source/'MANIFEST.json')
    actual = {f.relative_to(source).as_posix(): digest(f) for f in source.rglob('*')
              if f.is_file() and f != source/'MANIFEST.json'}
    assert actual == manifest, 'frozen PR1087 source manifest mismatch'
    for name in ('OWNERS.json.gz', 'PLAN.json', 'SPEC.json'):
        shutil.copyfile(P/'data'/name, source/'data'/name)

    local = work/'local'
    local.mkdir()
    local_pins = read_json(main/'research/complex-t16-two-stage-cycles/LOCAL-PINS.json')
    provider_archive = main/'research/community-frontier1094-audit/selected-replay.tar.gz'
    prefix = 'candidate/strict/global/base/providers/gauge44/'
    with tarfile.open(provider_archive) as tar:
        for name, expected in local_pins.items():
            member = tar.getmember(prefix+name)
            assert member.isfile()
            content = tar.extractfile(member).read()
            assert hashlib.sha256(content).hexdigest() == expected, 'provider pin mismatch: '+name
            (local/name).write_bytes(content)

    replay_dir = work/'strict'
    env = clean_env()
    subprocess.run([sys.executable, '-E', '-S', '-B', str(source/'verify_t16.py'),
                    '--main', str(main), '--local', str(local), '--work', str(replay_dir)],
                   env=env, check=True)
    result = read_json(replay_dir/'REPLAY.json')
    expected = read_json(P/'data/SPEC.json')['expected']
    assert result['status'] == 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
    assert result['kappa'] == expected['kappa']
    assert Decimal(result['kappa_decimal']) == Decimal(expected['kappa_decimal'])
    assert Decimal(result['conservative_kappa_decimal']) == Decimal(expected['conservative_kappa_decimal'])
    assert result['complex_profile'] == expected['global_profile']
    assert result['idle_remainder_profile'] == expected['idle_remainder_profile']
    assert result['actual_73_axis_charts'] == expected['actual_73column_sigmas'] == 10008
    assert result['controls'] == CONTROLS
    pinned = read_json(P/'evidence/REPLAY.json')
    for key in ('status', 'kappa', 'kappa_decimal', 'conservative_kappa_decimal', 'actual_73_axis_charts', 'controls'):
        assert result[key] == pinned[key], 'strict receipt differs from packaged evidence: '+key
    return replay_dir, result


def independent_audit(main, replay_dir, work):
    check = load_module('t16_predecessor_independent_check', main/'research/complex-t16-two-stage-cycles/check.py')
    check.P = P
    out_path = work/'CHECK.json'
    check.run(main, replay_dir, out_path)
    result = read_json(out_path)
    evidence = read_json(P/'evidence/CHECK.json')
    for key in ('candidate', 'price_new', 'price_new_conservative', 'majorization', 'sweep',
                'changed_rows', 'offset_only_rows', 'all_strictly_inside', 'helper_once_per_call'):
        assert result[key] == evidence[key], 'independent receipt mismatch: '+key
    assert result['relocated_rows'] == evidence['relocated_rows']
    assert Decimal(result['price_new']['kappa_decimal']) == Decimal('0.001673618490895016')
    assert result['majorization']['candidate_majorizes_selected'] is True
    assert result['sweep']['binding'] == 'complex'
    return result


def check_word_ceiling(main, expected):
    word_path = main/'research/t16-owner-audit-seed67/inputs/k8-seven-slot-word.json.gz'
    word = json.loads(gzip.decompress(word_path.read_bytes()))
    local = {int(k): int(v) for k, v in word['report']['local_profile'].items()}
    mod = load_module('t16_word_ceiling', main/'research/complex-local-word-ceiling/ceiling.py')
    a_lo, a_hi = mod.ceiling(local, 73, 896, 9, 64)
    assert a_hi == CEILING_A_HI, (a_lo, a_hi)
    kappa_cap = a_hi/(1+a_hi)
    candidate_kappa = Q(expected['kappa'])
    selected_kappa = Q('0.001672660197076918')
    assert candidate_kappa < kappa_cap and candidate_kappa > OLD_KAPPA > selected_kappa
    realized = candidate_kappa/kappa_cap
    selected_gap_realized = (candidate_kappa-selected_kappa)/(kappa_cap-selected_kappa)
    with localcontext() as ctx:
        ctx.prec = 50
        realized_decimal = Decimal(realized.numerator)/Decimal(realized.denominator)
        gap_decimal = Decimal(selected_gap_realized.numerator)/Decimal(selected_gap_realized.denominator)
        cap_decimal = Decimal(kappa_cap.numerator)/Decimal(kappa_cap.denominator)
    return dict(a_hi=str(Decimal(a_hi.numerator)/Decimal(a_hi.denominator)),
                kappa_ceiling=str(cap_decimal), fraction_of_kappa_ceiling_realized=str(realized_decimal),
                fraction_of_selected_to_ceiling_gap_realized=str(gap_decimal))


def packing_ceiling(main, work):
    out_path = work/'CEILING.json'
    subprocess.run([sys.executable, '-I', '-B', str(main/'research/complex-t16-two-stage-cycles/ceiling_bound.py'),
                    '--data', str(P/'data'), '--out', str(out_path)], env=clean_env(), check=True)
    result = read_json(out_path)
    evidence = read_json(P/'evidence/CEILING.json')
    assert result == evidence
    assert result['theorem1']['max_empty_cap48'] == 4887
    assert result['theorem3']['bound_decimal'] == '908139.013'
    assert result['this_map']['empty_cap48'] == 4880
    return result


def run(main, work):
    reconstruct(main, work)
    replay_dir, replay = strict_replay(main, work)
    audit = independent_audit(main, replay_dir, work)
    spec = read_json(P/'data/SPEC.json')['expected']
    old_delta = Q(spec['kappa'])-OLD_KAPPA
    assert old_delta == Q(4285169321, 10**18)
    cap = check_word_ceiling(main, spec)
    packing = packing_ceiling(main, work)
    print('PASS_T16_EVACUATION_INCREMENT', replay['kappa_decimal'],
          'delta_vs_predecessor', Decimal(old_delta.numerator)/Decimal(old_delta.denominator),
          'fraction_of_word_kappa_ceiling', cap['fraction_of_kappa_ceiling_realized'],
          'changed/relocated', audit['changed_rows'], len(audit['relocated_rows']),
          'packing ceiling E<=', packing['theorem3']['bound_decimal'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--main', type=Path, default=P.parents[1])
    parser.add_argument('--work', type=Path)
    args = parser.parse_args()
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        run(args.main.resolve(), args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='t16-evacuation-increment-') as tmp:
            run(args.main.resolve(), Path(tmp))
