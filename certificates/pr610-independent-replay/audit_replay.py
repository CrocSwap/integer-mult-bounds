"""Audit one fresh pinned PR610 replay; all claims remain conditional.
Prepared with OpenAI Codex assistance. No upstream code is modified.
"""
import hashlib, json
from pathlib import Path

import argparse
ap = argparse.ArgumentParser()
ap.add_argument('--source', type=Path, required=True)
ap.add_argument('--work', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
SOURCE = a.source.resolve()
WORK = a.work.resolve()
HEAD = 'd9dc50b46b20cb8f769dd85a851f8b31b0f8f695'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())

manifest = read(SOURCE / 'MANIFEST.json')
actual = {p.relative_to(SOURCE).as_posix(): sha(p) for p in SOURCE.rglob('*')
          if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts}
assert actual == manifest
tree = read(Path(__file__).with_name('SOURCE-BLOBS.json'))
assert tree['sha'] == HEAD and not tree['truncated']
prefix = 'research/complex-571-cold14/'
blobs = {x['path'][len(prefix):]: x['sha'] for x in tree['tree']
         if x['type'] == 'blob' and x['path'].startswith(prefix)}
assert set(blobs) == set(actual) | {'MANIFEST.json'}
for rel, expected in blobs.items():
    data = (SOURCE / rel).read_bytes()
    assert hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == expected

def receipt(root):
    r = read(root / 'RECEIPT.json')
    assert r['status'].startswith('PASS_')
    assert len({s['name'] for s in r['steps']}) == len(r['steps'])
    for s in r['steps']:
        assert s['exit_code'] == 0
        assert sha(root / (s['name'] + '.log')) == s['log_sha256']
    for name, expected in r['artifacts'].items():
        assert sha(root / name) == expected
    return r

r = receipt(WORK)
nested = receipt(WORK / 'baseline558')
assert len(r['steps']) == 41 and len(nested['steps']) == 9
assert r['manifest_sha256'] == sha(SOURCE / 'MANIFEST.json')
assert r['spec_sha256'] == sha(SOURCE / 'data/SPEC.json')
result = read(WORK / 'RESULT.json')
assembly = read(WORK / 'ASSEMBLY.json')
assert result['reused'] == {'baseline': False, 'locals': []}
assert result['kappa_decimal'] == assembly['kappa_decimal'] == '0.00162536523418317'
assert result['conservative_kappa_decimal'] == assembly['conservative_kappa_decimal'] == '0.001625365231365566'
assert result['provider_counts'] == {'jp8': 71, 'ck': 1}
assert result['global_profile'] == assembly['complex_profile']
assert assembly['complex_lower'] == '814005673613905131117/500000000000000000000000'
assert len(assembly['outer']) == len(assembly['conservative_outer']) == 47
from fractions import Fraction
assert all(Fraction(v) > 0 for v in assembly['outer'].values())
assert all(Fraction(v) > 0 for v in assembly['conservative_outer'].values())
spec = read(SOURCE / 'data/SPEC.json')
providers = {}
for pid in ('ck', 'jp8'):
    p = WORK / (pid + '-local')
    scalar = read(p / 'SCALAR-FRAME-AUDIT.json')
    local = read(p / 'INDEPENDENT-LOCAL-REPLAY.json')
    phases = read(p / 'CLIFFORD-REVIEW.json')
    wrappers = read(p / 'WRAPPER-CHECKS.json')
    assert scalar['status'] == 'PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES'
    assert local['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
    assert local['paid_profiles']['forward'] == local['paid_profiles']['backward']
    assert phases['all_child_equalities_include_global_phase'] is True
    assert phases['directed_edges'] == spec['providers'][pid]['phase_edges']
    assert wrappers['status'] == 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT'
    providers[pid] = {name: sha(p / name) for name in (
        'SCALAR-FRAME-AUDIT.json', 'INDEPENDENT-LOCAL-REPLAY.json',
        'CLIFFORD-REVIEW.json', 'WRAPPER-CHECKS.json')}
controls = read(WORK / 'ASSEMBLY-CONTROLS.json')
assert len(controls['rejected_controls']) == spec['expected']['assembly_controls_rejected']
owners = read(WORK / 'mixed-global/audit/OWNERS-AND-PROFILE.json')
invoice = read(WORK / 'mixed-global/audit/PREFIX-AND-INVOICE.json')
assert owners['paid_profile'] == result['global_profile']
assert owners['deficit'] == 2560
assert invoice['owner_audit_sha256'] == sha(WORK / 'mixed-global/audit/OWNERS-AND-PROFILE.json')
assert invoice['provider_counts'] == result['provider_counts']
assert all(invoice['strict_checks'].values())
out = dict(status='ROOT_INDEPENDENT_PR610_SOURCE_AND_FRESH_REPLAY_AUDIT_PASS',
    pr=610, head=HEAD, package='research/complex-571-cold14',
    package_blobs_checked=len(blobs), package_manifest_sha256=sha(SOURCE / 'MANIFEST.json'),
    top_level_stages=len(r['steps']), nested_baseline_stages=len(nested['steps']),
    verified_top_level_artifact_hashes=len(r['artifacts']),
    verified_nested_artifact_hashes=len(nested['artifacts']),
    fresh_run_seconds=result['seconds'], kappa=result['kappa_decimal'],
    conservative_kappa=result['conservative_kappa_decimal'],
    complex_lower=result['complex_lower'], global_profile=result['global_profile'],
    provider_counts=result['provider_counts'], provider_audit_hashes=providers,
    assembly_controls_rejected=len(controls['rejected_controls']),
    receipt_sha256=sha(WORK / 'RECEIPT.json'), result_sha256=sha(WORK / 'RESULT.json'),
    assembly_sha256=sha(WORK / 'ASSEMBLY.json'), source_manifest_sha256=r['source_manifest_sha256'],
    scope='Fresh exact-head replay of both provider words and the inherited558 baseline. '
          'Actual scalar columns, arbitrary dirty restoration, both native reflected ledgers, '
          'global phases, wrappers, owners, fresh invoice, both moment engines and exact assembly. '
          'PR543 bit circuit is cited/repriced, not freshly rebuilt; ck uses pinned571 ancestry. '
          'All-size compiler, common-label/mutable-source realization, whole-call hosting, '
          'precision/tape/recovery, analytic transfer and bit H1-H5 remain assumptions. '
          'No Lean replay, unconditional theorem or practical speedup claim.',
    AI_disclosure='Independent audit prepared with OpenAI Codex assistance. '
                  'PR610/604 construction credited to DreamingOfClouds with Claude Opus5.5 '
                  'and the inherited contributor lineage.')
a.out.write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps({k: v for k, v in out.items() if k not in ('provider_audit_hashes', 'source_manifest_sha256', 'scope', 'global_profile')}, indent=2))
