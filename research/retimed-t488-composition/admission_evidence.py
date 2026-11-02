#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind recorded full admission to fresh bounded results; never run a scientific gate.

Export only after terminal success:
  python3.12 -B admission_evidence.py --package PACKAGE --run FULL_RUN \
      --source RETIMED_SOURCE --export FRESH_EVIDENCE_DIRECTORY
The directory contains COMPLETE-ADMISSION.json and byte-exact upstream receipts.
Integrate with check(package, summary_path, owner_profile, kappa, literal_dir).
Receipt consistency is not independent attestation or a fresh full admission.
"""
from pathlib import Path, PurePosixPath
from fractions import Fraction as Q
import argparse, gzip, hashlib, json

STAGES = ('owners', 'parent-lift', 'rebind', 'discovery',
          'outer-check_ledger.py', 'outer-independent_check.py', 'release')
FILES = {
    'admission': 'admission/RESULT.json',
    'stages': 'admission/STAGES.json',
    'release': 'admission/release/RELEASE-RECEIPT.json',
    'manifest': 'admission/package/MANIFEST.json',
    'spec': 'admission/package/new/SPEC.json',
    'profile': 'admission/package/new/PROFILE.json',
    'outer_claim': 'admission/package/outer/OUTER-CLAIM.json',
    'native': 'native/NATIVE-RECEIPT.json',
    'fill': 'FILL-legacy.json.gz',
    'order': 'allocation/ORDER.json',
    'dispatch': 'allocation/DISPATCH.json',
}

def need(ok, why):
    if not ok:
        raise ValueError(why)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(Path(path).read_bytes())

def profile(value):
    need(isinstance(value, dict) and value, 'nonempty profile required')
    need(all(isinstance(k, str) and k.isdigit() and str(int(k)) == k
             and type(v) is int and v >= 0 for k, v in value.items()), 'profile integer schema')
    return value

def check(package, summary_path, owner_profile, kappa, literal_dir):
    """Read-only check. The caller must supply freshly verified bounded outputs.

    ARTIFACTS authenticates this module and all exported evidence in aggregate use.
    No command or absolute path in an upstream receipt is ever executed/resolved.
    """
    package, summary_path, literal_dir = map(Path, (package, summary_path, literal_dir))
    summary = read(summary_path)
    need(summary['schema'] == 'retimed-t488-recorded-admission/v1', 'recorded schema')
    need(summary['status'] == 'PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE', 'summary terminal status')
    need(set(summary['files']) == set(FILES) | {'source_manifest'}, 'complete evidence inventory')
    blobs = {}
    for key, entry in summary['files'].items():
        rel = PurePosixPath(entry['path'])
        need(not rel.is_absolute() and '..' not in rel.parts and rel.parts, 'unsafe evidence path')
        p = summary_path.parent.joinpath(*rel.parts)
        need(p.is_file() and not p.is_symlink() and summary_path.parent.resolve() in p.resolve().parents,
             'evidence must be a regular file within bundle')
        blobs[key] = p.read_bytes()
        need(digest(blobs[key]) == entry['sha256'], 'recorded bytes changed: ' + key)
    data = {k: json.loads(v) for k, v in blobs.items() if k != 'fill'}
    a, release, manifest, native = (data[k] for k in ('admission', 'release', 'manifest', 'native'))
    deps = read(package/'full-replay/DEPENDENCIES.json')
    spec = read(package/'full-replay/SPEC.json')
    C = Q(spec['expected_complex_lower'])
    K = Q(kappa)
    need(profile(owner_profile) == profile(spec['expected_complete_profile']) == profile(a['profile'])
         == profile(summary['profile']) == profile(data['profile'])
         == profile(data['spec']['expected']['global_profile']), 'exact complete profile binding')
    need(K == C-Q(spec['outer_margin'])-Q(spec['grid_margin']), 'fixed transfer expression')
    need(Q(summary['kappa']) == Q(a['kappa']) == Q(a['kappa_decimal'])
         == Q(release['kappa_decimal']) == Q(data['outer_claim']['kappa_rational'])
         == Q(data['outer_claim']['kappa']) == K, 'full modern endpoint binding')
    need(Q(a['complex_lower']) == Q(data['spec']['expected']['complex_lower']) == C,
         'complex endpoint binding')
    need(a['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'raw terminal admission/release required')
    need(a['release_receipt_sha256'] == digest(blobs['release']), 'release receipt link')
    need(a['package_manifest_sha256'] == release['manifest_sha256'] == digest(blobs['manifest']),
         'final package manifest link')
    need(a['source_manifest_sha256'] == native['manifest_sha256']
         == deps['source_manifest_sha256'] == digest(blobs['source_manifest']), 'retimed source manifest link')
    need(len(data['source_manifest']) == a['source_file_count'] == deps['source_file_count'],
         'complete source inventory')
    need(a['native_receipt_sha256'] == digest(blobs['native']), 'native receipt link')
    need(native['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
         and native['fresh_current_provider_count'] == 2, 'both current suppliers freshly replayed')
    claim_bytes = (package/'full-replay/comparator/PR3642-CLAIM.json').read_bytes()
    claim_pin = deps['files']['comparator/PR3642-CLAIM.json']
    need(digest(claim_bytes) == claim_pin['sha256'] == summary['comparison_claim_sha256'],
         'authenticated PR3642 comparator')
    prior = Q(json.loads(claim_bytes)['kappa'])
    need(prior == Q(spec['comparison_kappa']) == Q(summary['prior_PR3642']) and K > prior,
         'strict improvement over modern PR3642 claim')
    need(Q(summary['absolute_gain']) == K-prior, 'exact headline gain')
    stages = data['stages']
    need(stages == a['stages'] == summary['admission_stages'], 'raw stage list link')
    need(tuple(s['name'] for s in stages) == STAGES and all(type(s['exit_code']) is int
         and s['exit_code'] == 0 for s in stages), 'seven distinct ordered scientific stages')
    script_paths = {'owners':'reconstruct.py', 'parent-lift':'lift_parent.py',
        'rebind':'new/rebind.py', 'discovery':'replay.py',
        'outer-check_ledger.py':'outer/check_ledger.py',
        'outer-independent_check.py':'outer/independent_check.py', 'release':'verify_release.py'}
    for s in stages:
        need(s['script_sha256'] == manifest[script_paths[s['name']]], 'stage script/package link: '+s['name'])
    for key, rel in [('spec','new/SPEC.json'), ('profile','new/PROFILE.json'),
                     ('outer_claim','outer/OUTER-CLAIM.json'), ('fill','new/borrow-fill/FILL.json.gz'),
                     ('order','new/borrow-fill/ORDER.json'), ('dispatch','new/borrow-fill/DISPATCH.json')]:
        need(manifest[rel] == digest(blobs[key]), 'package payload link: ' + key)
    expected = read(package/'owners/upstream/EXPECTED.json')
    literal = gzip.decompress((literal_dir/'FILL.json.gz').read_bytes())
    need(digest(literal) == expected['payload_sha256'], 'fresh literal owner payload pin')
    need(json.loads(gzip.decompress(blobs['fill'])) == json.loads(literal),
         'admitted fill must equal every fresh literal owner row')
    need(a['fill_sha256'] == digest(blobs['fill']), 'admitted fill hash')
    for key in ('order', 'dispatch'):
        name = key.upper()+'.json'
        need(a[key+'_sha256'] == digest(blobs[key]) == expected['literal_files'][name]
             == digest((literal_dir/name).read_bytes()), 'exact owner '+key+' binding')
    geometry, expectation = data['spec']['geometry'], data['spec']['expected']
    need(a['replicas'] == geometry['replicas'] == spec['replicas'] == expected['replicas']
         and expectation['hosted_residuals'] == spec['roles'] == expected['rows']
         and expectation['physical'] == expected['physical']
         and expectation['live'] == 896*spec['replicas'], 'geometry/roles/physical binding')
    pins = read(package/'owners/NATIVE-BINDING.json')
    need(set(native['providers']) == set(pins), 'exact provider set')
    for tag, pin in pins.items():
        p = native['providers'][tag]
        word = digest((package/('local-audit/words/RETIMED644-660-'+tag+'.json.gz')).read_bytes())
        canonical = (package/('owners/native/checked-'+tag+'/CANONICAL-WORD.json.gz')).read_bytes()
        need(p['word_sha256'] == word, 'native raw supplier word: '+tag)
        need(digest(canonical) == pin['canonical_sha256']
             == p['complete_native_files']['local/CANONICAL-WORD.json.gz']
             == native['cache_files'][word+'/local/CANONICAL-WORD.json.gz'], 'canonical native receipt link: '+tag)
        need(digest(gzip.decompress(canonical)) == pin['payload_sha256'], 'canonical native payload: '+tag)
        need(p['complete_native_files']['local/FULL-WORD.json.gz'] == word,
             'full native input: '+tag)
        for rel, sha in p['complete_native_files'].items():
            need(native['cache_files'][word+'/'+rel] == sha, 'native provider/cache inventory: '+tag)
    return {'status':'PASS_RECORDED_ADMISSION_CROSS_BINDING', 'kappa':str(K),
            'source_manifest_sha256':digest(blobs['source_manifest']),
            'package_manifest_sha256':digest(blobs['manifest']),
            'scope':'Byte-exact recorded receipt consistency with fresh bounded construction. Not independent attestation or a fresh native/controller/full admission; inherited conditional hypotheses remain.'}


def export(package, run, source, destination):
    """Preserve originals byte-for-byte. Refuse incomplete runs before creating output."""
    package, run, source, destination = map(Path, (package, run, source, destination))
    need(not destination.exists(), 'fresh export destination required')
    blobs = {k:(run/rel).read_bytes() for k, rel in FILES.items()}
    blobs['source_manifest'] = (source/'MANIFEST.json').read_bytes()
    a = json.loads(blobs['admission'])
    need(a['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'cannot export a pending admission')
    prior = Q(read(package/'full-replay/comparator/PR3642-CLAIM.json')['kappa'])
    summary = {'schema':'retimed-t488-recorded-admission/v1',
        'status':'PASS_T488_RETIMER_COMPLETE_CONDITIONAL_RELEASE', 'profile':a['profile'],
        'kappa':a['kappa'], 'prior_PR3642':str(prior), 'absolute_gain':str(Q(a['kappa'])-prior),
        'comparison_claim_sha256':digest((package/'full-replay/comparator/PR3642-CLAIM.json').read_bytes()),
        'admission_stages':json.loads(blobs['stages']), 'files':{},
        'scope':'Recorded complete conditional release; fresh bounded cross-check is separate. This export does not replay native/controller/full scientific gates.'}
    destination.mkdir(parents=True)
    for key, blob in blobs.items():
        name = key+('.json.gz' if key == 'fill' else '.json')
        (destination/name).write_bytes(blob)
        summary['files'][key] = {'path':name, 'sha256':digest(blob)}
    summary_path = destination/'CANDIDATE-ADMISSION.json'
    summary_path.write_text(json.dumps(summary, indent=2)+'\n')
    check(package, summary_path, a['profile'], a['kappa'], run/'allocation')
    complete = destination/'COMPLETE-ADMISSION.json'
    summary_path.rename(complete)
    return complete

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    for flag in ('package','run','source','export'): ap.add_argument('--'+flag, required=True, type=Path)
    args=ap.parse_args()
    print(export(args.package, args.run, args.source, args.export))
