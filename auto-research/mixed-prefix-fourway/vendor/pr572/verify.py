#!/usr/bin/env python3
"""Cold, standard-library replay of the composed eight-cold / width-seven witness.
Prepared with OpenAI Codex assistance. Apache-2.0; source notices retained.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time

if not __debug__:
    raise SystemExit('Assertions must remain enabled')
P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    work = args.work.resolve()
    assert not work.exists() and not work.is_relative_to(P), 'Use a new work directory outside the source package'
    manifest = read(P / 'MANIFEST.json')
    actual = {p.relative_to(P).as_posix(): sha(p) for p in P.rglob('*')
              if p.is_file() and p != P / 'MANIFEST.json' and '__pycache__' not in p.parts}
    assert actual == manifest, 'Source inventory differs'
    for vendor, source in read(P / 'SOURCE-PINS.json').items():
        for name, pin in source['files'].items():
            raw = (P / 'vendor' / vendor / name).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == pin['sha256']
            assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == pin['git_blob']
    expected = read(P / 'EXPECTED.json')
    upstream = P / 'vendor/pr568'
    assert sha(upstream / 'MANIFEST.json') == expected['source_manifest_sha256']
    work.mkdir(parents=True)
    (work / 'logs').mkdir()
    steps = []
    start = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

    def run(name, script, *arguments, portable=True, optimized=False):
        command = [sys.executable, '-B']
        if optimized:
            assert not portable
            command.append('-O')
        if portable:
            command.append(str(upstream / 'code/run_portable.py'))
        command += [str(script), *map(str, arguments)]
        print('RUN', name, flush=True)
        began = time.monotonic()
        log = work / 'logs' / (name + '.log')
        with log.open('w', encoding='utf-8', newline='\n') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, env=env)
        row = dict(name=name, command=command, exit_code=result.returncode,
                   script_sha256=sha(script), seconds=time.monotonic() - began, log_sha256=sha(log))
        steps.append(row)
        dump(work / 'STAGES.json', steps)
        if result.returncode:
            raise RuntimeError(name + ' failed\n' + log.read_text()[-6000:])
        print('PASS', name, flush=True)

    baseline = work / 'baseline568'
    run('pinned568-full-replay', upstream / 'verify.py', '--work', baseline, portable=False)
    assert read(baseline / 'RESULT.json')['kappa_decimal'] == '0.001596133352130093'
    original = baseline / 'eight-multicold-word/FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(original.read_bytes())).hexdigest() == expected['source_content_sha256']
    raw = work / 'width7-word'
    local = work / 'width7-local'
    recipes = P / 'vendor/pr569/providers/width7/eight/RECIPES.json'
    b = upstream / 'vendor/pr558'
    f = b / 'vendor/pr552'
    v = f / 'complex-global/vendor531'
    run('compose-32-entrance-promotions', P / 'vendor/pr569/providers/build_entrance_promotions.py',
        '--word', original, '--recipes', recipes, '--gk-dir', f / 'complex-local/static44/gk', '--out', raw)
    construction = read(raw / 'CONSTRUCTION.json')
    assert construction['profile_delta'] == {'1': 32, '2': 160, '3': -128}
    assert construction['changed_gates'] == 96 and construction['promotions'] == 32
    assert construction['scalar_operations_unchanged'] is True
    word = raw / 'FULL-WORD.json.gz'
    assert hashlib.sha256(gzip.decompress(word.read_bytes())).hexdigest() == expected['local_content_sha256']
    run('independent-scalar-omission-transfer', P / 'code/audit_scalar_transfer.py',
        '--source', original, '--word', word, '--recipes', recipes,
        '--controls', baseline / 'eight-multicold-word', '--promotions', 8,
        '--out', raw / 'SCALAR-TRANSFER.json', portable=False, optimized=True)
    assert len(read(raw / 'SCALAR-TRANSFER.json')['negative_controls_rejected']) == 3
    run('first-cold-kernel-omissions', upstream / 'code/audit_kernel_controls.py',
        '--word', word, '--recipe', upstream / 'data/EIGHT-COLD.json', '--out', raw / 'FIRST-COLD-OMISSIONS.json')
    assert len(read(raw / 'FIRST-COLD-OMISSIONS.json')['controls']) == 6
    run('seven-multicut-kernel-omissions', upstream / 'code/audit_multicold_controls.py',
        '--word', word, '--recipe', upstream / 'data/EIGHT-MULTICOLD.json', '--out', raw / 'MULTICOLD-OMISSIONS.json')
    assert len(read(raw / 'MULTICOLD-OMISSIONS.json')['controls']) == 32
    run('all-columns-and-native-frames', v / 'code/audit_and_transport.py', '--raw', word,
        '--routing', f / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', local)
    run('both-reflected-ledgers', v / 'code/emit_local.py', local)
    run('independent-local-controls', v / 'code/audit_local.py', local)
    assert len(read(local / 'INDEPENDENT-LOCAL-REPLAY.json')['negative_controls_rejected']) == 11
    run('normalized-wrappers', v / 'code/adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json')
    run('every-phase-edge-and-endpoint', b / 'code/phases_full.py', local, v / 'vendor/clifford')
    phase = read(local / 'CLIFFORD-REVIEW.json')
    assert phase['directed_edges'] == 3005 and phase['endpoint_adapters'] == 224
    assert phase['all_child_equalities_include_global_phase'] is True
    global_root = work / 'global'
    code = P / 'code'
    run('bind-two-actual-providers', code / 'bind_providers_portable.py',
        '--baseline', baseline / 'baseline558', '--plain', baseline / 'eight-cold-local',
        '--width7', local, '--plan', P / 'data/PLAN.json', '--out', global_root)
    run('emit-literal-owner-controller', code / 'emit_allcold.py', '--base', global_root / 'base',
        '--owners', P / 'data/OWNERS.json.gz', '--plan', global_root / 'PLAN.json', '--out', global_root / 'hosted')
    run('independent-owners-and-controls', code / 'audit_allcold.py', global_root / 'base',
        global_root / 'hosted', global_root / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
    assert len(read(global_root / 'audit/ASYNC-AUDIT.json')['mutations_rejected']) == 16
    run('fresh-complete-invoice', code / 'invoice_allcold.py', '--base', global_root / 'base',
        '--hosted', global_root / 'hosted', '--audit', global_root / 'audit', '--out', global_root / 'audit',
        '--retained-invoice', v / 'evidence/audit/PREFIX-AND-INVOICE.json')
    run('both-exact-assembly-models', code / 'assemble.py', upstream, global_root, global_root / 'ASSEMBLY.json')
    run('ninety-three-admission-controls', code / 'assembly_controls.py', '--source-package', upstream,
        '--owner', global_root / 'audit/OWNERS-AND-PROFILE.json', '--invoice', global_root / 'audit/PREFIX-AND-INVOICE.json',
        '--out', global_root / 'ASSEMBLY-CONTROLS.json')
    assert len(read(global_root / 'ASSEMBLY-CONTROLS.json')['rejected_controls']) == 93
    run('phase-timing-and-semantic-controls', code / 'phase_timing_controls.py', upstream,
        global_root / 'base', global_root / 'audit', global_root / 'PHASE-TIMING-CONTROLS.json')
    run('actual-recompression-and-semantic-controls', code / 'generated_identity_controls.py',
        '--base', global_root / 'base', '--audit', global_root / 'audit',
        '--out', global_root / 'GENERATED-IDENTITY-CONTROLS.json')
    assert read(global_root / 'GENERATED-IDENTITY-CONTROLS.json')['counts'] == dict(
        recompression_accepted=2, semantic_rejected=18, reference_or_metadata_rejected=18)
    result = read(global_root / 'ASSEMBLY.json')
    keys = ('kappa', 'kappa_decimal', 'complex_lower', 'bit_lower', 'complex_profile',
            'provider_counts', 'conservative_kappa', 'conservative_complex_lower')
    assert all(result[k] == expected[k] for k in keys)
    stable = dict(status='PASS_COMPOSED_MULTICOLD_WIDTH7_FULL_ADMISSION', **{k: result[k] for k in keys},
                  directed_phase_edges=3005, endpoint_adapters=224, scalar_transfer_controls=3,
                  new_kernel_omission_controls=38, controller_controls=16, assembly_controls=93, recompression_controls=2,
                  generated_semantic_controls=18, generated_reference_controls=18,
                  scope=result['scope'])
    dump(work / 'RESULT.json', stable)
    files = ['RESULT.json', 'width7-word/CONSTRUCTION.json', 'width7-word/SCALAR-TRANSFER.json',
             'width7-word/FIRST-COLD-OMISSIONS.json', 'width7-word/MULTICOLD-OMISSIONS.json',
             'width7-local/INDEPENDENT-LOCAL-REPLAY.json', 'width7-local/CLIFFORD-REVIEW.json',
             'global/BINDING.json', 'global/audit/ASYNC-AUDIT.json', 'global/audit/OWNERS-AND-PROFILE.json',
             'global/audit/PREFIX-AND-INVOICE.json', 'global/ASSEMBLY.json',
             'global/ASSEMBLY-CONTROLS.json', 'global/PHASE-TIMING-CONTROLS.json',
             'global/GENERATED-IDENTITY-CONTROLS.json']
    dump(work / 'RECEIPT.json', dict(status=stable['status'], source_manifest_sha256=sha(P / 'MANIFEST.json'),
                                   upstream_receipt_sha256=sha(baseline / 'RECEIPT.json'), steps=steps,
                                   artifacts={name: sha(work / name) for name in files}, seconds=time.monotonic() - start))
    print(json.dumps(stable, indent=2), flush=True)


if __name__ == '__main__':
    main()
