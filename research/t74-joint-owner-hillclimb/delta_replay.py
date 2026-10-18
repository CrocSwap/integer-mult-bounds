"""Admit an actual changed T74 candidate against the pinned PR2288 baseline.

Inputs are a complete candidate data directory and full native directories.
The inherited parent chain is reused only after its fresh baseline admission.
All changed owner/provider/invoice fields are recomputed by discovery and then
checked again in strict mode. The final ledger is PR2288's fine-prime outer.
This driver writes only a new work directory and a derivative packing runtime.
"""
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
from fractions import Fraction as Q
from pathlib import Path
from baseline_cache import validate_baseline
from native_evidence import validate_manifest

sys.set_int_max_str_digits(0)
HERE = Path(__file__).resolve().parent
PACKAGE_RELATIVE = Path('research/gmx-t74-borrow43-refit')
UPSTREAM_HEAD = '614c74a63b0f6d4a24c7740d7ddb90d37861b3c7'
UPSTREAM_MANIFEST = '557d8d6cfe0768c427e564beed37fbdfe3f65d10367f4c3a3dc36359c89cc62b'
ADOPTED_HEAD = 'fb76f799ccf078f51780076ebed3fd26b1db11c0'
ADOPTED_MANIFEST = 'c545968fb8cf6e550b82ba631e92fd756484db75e621aee211347749cff55313'
ADOPTED_PACKAGE_RELATIVE = Path('research/gmx-t74-borrow43-width-exchange')
PACKAGE = None
DATA_FILES = ('PLAN.json', 'SPEC.json', 'PROFILE.json', 'OWNERS.json.gz',
              'DISPATCH.json', 'CONSTRUCTION.json', 'GLOBAL-TEMPLATE.json.gz')


def read(p):
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def require_native(path, word, manifest_path=None):
    result = {'directory':str(path), 'steps_sha256':sha(path/'STEPS.json'),
            'full_word_sha256':sha(path/'local/FULL-WORD.json.gz'),
            'input_word_sha256':sha(word),
            'all_exact_native_steps_passed':True}
    assert read(path/'local/FULL-WORD.json.gz') == read(word)
    if manifest_path is not None:
        manifest = validate_manifest(path, PACKAGE, word, read(manifest_path))
        result.update(evidence_manifest_sha256=sha(manifest_path),
                      evidence_schema=manifest['schema'],
                      complete_native_file_count=manifest['file_count'],
                      canonical_artifacts=manifest['artifacts'])
    else:
        # Every unchanged baseline file and all four full native chains have
        # already been checked by validate_baseline before this function.
        result['evidence_source'] = 'complete-source-bound-baseline-cache'
    return result


def main():
    global PACKAGE
    if not __debug__:
        raise RuntimeError('Assertions must be enabled for source-bound admission')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-root', type=Path, required=True,
                    help='Repository root containing the immutable PR2288 package')
    ap.add_argument('--candidate-source-root', type=Path, required=True,
                    help='Repository root containing immutable PR2312 native and verifier code')
    ap.add_argument('--baseline', type=Path, required=True,
                    help='A completed source-bound cold replay verify directory')
    ap.add_argument('--data', type=Path, required=True)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--base-native', type=Path)
    ap.add_argument('--extra-native', type=Path)
    ap.add_argument('--base-word', type=Path)
    ap.add_argument('--extra-word', type=Path)
    ap.add_argument('--endpoint-digits', type=int, default=24,
                    help='24 uses the retained exact coarse certificate; '
                         'higher precision needs a separately frozen endpoint')
    ap.add_argument('--preflight-only',action='store_true',
                    help='Check immutable source and cached native bindings without replaying')
    a = ap.parse_args()
    baseline_package = a.source_root.resolve()/PACKAGE_RELATIVE
    PACKAGE = a.candidate_source_root.resolve()/ADOPTED_PACKAGE_RELATIVE
    for package,wanted_manifest in [(baseline_package,UPSTREAM_MANIFEST),
                                     (PACKAGE,ADOPTED_MANIFEST)]:
        assert sha(package/'MANIFEST.json') == wanted_manifest
        inventory = read(package/'MANIFEST.json')
        actual_files = {p.relative_to(package).as_posix() for p in package.rglob('*')
                        if p.is_file() and '__pycache__' not in p.parts
                        and p != package/'MANIFEST.json'}
        assert actual_files == set(inventory), 'Immutable upstream file set changed'
        for relative,digest in inventory.items():
            assert sha(package/relative)==digest, ('Immutable upstream file changed',relative)
    assert a.endpoint_digits == 24, 'Discovery engine returns a 24-digit endpoint'
    baseline, data, work = [p.resolve() for p in (a.baseline,a.data,a.work)]
    baseline_receipt = baseline/'PORTABLE-RESULT.json'
    assert baseline_receipt.is_file(), 'A complete portable cold baseline is required'
    admitted = read(baseline_receipt)
    assert admitted['status'] == 'PASS_PORTABLE_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
    assert admitted['manifest_sha256'] == sha(baseline_package/'MANIFEST.json')
    baseline_validation = validate_baseline(baseline,baseline_package,admitted)
    assert not work.exists()
    for name in DATA_FILES:
        assert (data/name).is_file(), name
    natives = {'base':(a.base_native or baseline/'native-new-base').resolve(),
               'extra':(a.extra_native or baseline/'native-new-extra').resolve()}
    native_binding = {}
    source_spec = read(baseline_package/'new/SPEC.json')
    ids_path = PACKAGE/'code/generated_identity.py'
    module_spec = importlib.util.spec_from_file_location('pinned_artifact_identity',ids_path)
    identities = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(identities)
    for key,provider in [('base','gauge44'),('extra','extra')]:
        word = getattr(a,key+'_word')
        if not getattr(a,key+'_native'):
            word = baseline_package/('new/borrow/words/BORROW-WORD-43'+key+'.json.gz')
        changed = bool(getattr(a,key+'_native'))
        if changed:
            assert word is not None, 'A changed native cache requires its exact input word'
        manifest_path = HERE/'evidence/native-bindings'/(key+'.json') if changed else None
        native_binding[key] = require_native(natives[key],word,manifest_path)
        if not getattr(a,key+'_native'):
            assert identities.artifact_identities(natives[key]/'local') == (
                source_spec['providers'][provider]['artifact_semantic_sha256']), (
                'Cached native artifacts differ from admitted supplier',provider)
    if a.preflight_only:
        print('PASS_PINNED_SOURCE_AND_CACHED_NATIVE_PREFLIGHT',flush=True)
        return
    work.mkdir(parents=True)
    layout = baseline/'parent/layout'
    runtime = layout/('delta-'+hashlib.sha256(str(work).encode()).hexdigest()[:16])
    assert not runtime.exists()
    # Use the exact PR2312 verifier runtime. Its source-bound negative controls
    # handle identical base/extra programs, and it binds all pooled row times.
    # All retained parent construction inputs still come from the fully checked
    # PR2288 baseline directories next to this derivative runtime.
    shutil.copytree(PACKAGE,runtime,
                    ignore=shutil.ignore_patterns('candidate','native-extra','__pycache__'))
    runtime_hashes = {p.relative_to(runtime).as_posix():sha(p)
                      for p in sorted(runtime.rglob('*')) if p.is_file()}
    for relative,digest in runtime_hashes.items():
        assert (PACKAGE/relative).is_file() and sha(PACKAGE/relative)==digest, (
            'Baseline runtime code differs from immutable upstream',relative)
    (runtime/'native-extra').symlink_to(natives['extra'],target_is_directory=True)
    candidate = work/'data'
    shutil.copytree(data,candidate)
    spec = read(candidate/'SPEC.json')
    spec['outer_refinement'] = dict(endpoint_digits=24,grid_digits=20,
                                  margin_digits=32,bootstrap_steps=16)
    # The sole non-expectation value read directly from expected during
    # discovery is the historical percentage denominator. Every other field
    # is independently reconstructed and then frozen by replay.py.
    spec['expected'] = {'gain_baseline_kappa':spec['expected']['gain_baseline_kappa']}
    spec['providers'] = {}
    # These two provenance checks run directly even during discovery.
    spec['data'] = dict(plan_sha256=sha(candidate/'PLAN.json'),
                        owners_sha256=sha(candidate/'OWNERS.json.gz'))
    (candidate/'SPEC.json').write_text(json.dumps(spec,indent=2)+'\n')
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',
               FINE_ENGINE_CACHE=str(work/'fine-cache'),OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1')
    stages = []

    def run(name,script,*args):
        t = time.monotonic()
        log = work/(name+'.log')
        with log.open('w') as f:
            r = subprocess.run([sys.executable,'-B',str(script),*map(str,args)],
                               env=env,stdout=f,stderr=subprocess.STDOUT)
        stages.append(dict(name=name,returncode=r.returncode,
                           seconds=round(time.monotonic()-t,3),log_sha256=sha(log)))
        (work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
        assert r.returncode == 0, (name,log.read_text()[-2500:])
        print('PASS',name,flush=True)

    # Adapter-label legality is a separate native obligation, beyond the five
    # frame/scalar/phase stages. Reuse it only for unchanged baseline natives.
    if a.base_native or a.extra_native:
        run('lemmag-labels',PACKAGE/'code/lemmag_stage.py',
            work/'LEMMAG-LABELS.json',natives['base'],natives['extra'])
        label_binding = {'reused':False,
                         'sha256':sha(work/'LEMMAG-LABELS.json')}
    else:
        label_binding = {'reused':True,
                         'sha256':sha(baseline/'LEMMAG-LABELS.json')}
    run('discovery',runtime/'replay.py','--data',candidate,'--work',work/'discovery',
        '--discover','--local',natives['base']/'local')
    run('discovery-owner-binding',HERE/'owner_binding.py',
        '--template',work/'discovery/global/hosted/GLOBAL-TEMPLATE.json.gz',
        '--owners',candidate/'OWNERS.json.gz',
        '--out',work/'DISCOVERY-OWNER-BINDING.json')
    # replay.py's discovery freezer has already written its full recomputed
    # candidate SPEC. Read that fully frozen spec, preserving all new fields.
    frozen = read(work/'discovery/runtime/data/SPEC.json')
    (candidate/'SPEC.json').write_text(json.dumps(frozen,indent=2)+'\n')
    run('strict',runtime/'replay.py','--data',candidate,'--work',work/'strict',
        '--local',natives['base']/'local')
    run('strict-owner-binding',HERE/'owner_binding.py',
        '--template',work/'strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
        '--owners',candidate/'OWNERS.json.gz',
        '--out',work/'STRICT-OWNER-BINDING.json')
    run('owner-binding-controls',HERE/'owner_binding.py',
        '--template',work/'strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
        '--owners',candidate/'OWNERS.json.gz','--mutation-controls',
        '--out',work/'OWNER-BINDING-CONTROLS.json')
    strict, assembly = read(work/'strict/RESULT.json'),read(work/'strict/ASSEMBLY.json')
    assert strict['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL'
    assert assembly['status'] == 'PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY'
    assert Q(assembly['bit_lower']) == Q('.001733427039589844234749')
    run('geometry-controls',runtime/'geometry_controls.py',
        '--source',layout/'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold',
        '--strict',work/'strict','--out',work/'GEOMETRY-CONTROLS.json')
    assert len(read(work/'GEOMETRY-CONTROLS.json')['rejected']) == 6
    outer_root = work/'fine-padding'
    (outer_root/'new').mkdir(parents=True)
    shutil.copy2(candidate/'SPEC.json',outer_root/'new/SPEC.json')
    (outer_root/'CLAIM.json').write_text(json.dumps({
        'kappa':assembly['kappa'],'kappa_decimal':assembly['kappa_decimal']})+'\n')
    shutil.copytree(PACKAGE/'outer',outer_root/'outer')
    b = Q(assembly['complex_lower']); digits = 24
    bj = {'b':str(b-Q(1,10**(digits+80))),
          'b_above_endpoint':str(b+Q(1,10**digits)),
          'profile':assembly['complex_profile'],
          'live':frozen['expected']['live'],
          'note':'Candidate exact endpoint; unchanged PR2288 fine-padding formulas'}
    (outer_root/'outer/B.json').write_text(json.dumps(bj,indent=2)+'\n')
    run('fine-padding-ledger',outer_root/'outer/check_ledger.py')
    run('independent-fine-padding',outer_root/'outer/independent_check.py')
    ledger = read(outer_root/'outer/LEDGER.json')
    k = Q(ledger['rows']['struct_boundary_radix_union']['kappa']['rational'])
    old = Q(read(PACKAGE/'outer/OUTER-CLAIM.json')['kappa'])
    result = dict(status='PASS_CHANGED_T74_FULL_DELTA_ADMISSION',
                  baseline_head=UPSTREAM_HEAD,
                  source_manifest_sha256=ADOPTED_MANIFEST,
                  adopted_supplier_head=ADOPTED_HEAD,
                  parent_baseline_manifest_sha256=UPSTREAM_MANIFEST,
                  baseline_result_sha256=sha(baseline_receipt),
                  baseline_receipt_name=baseline_receipt.name,
                  baseline_cache_validation=baseline_validation,
                  driver_sha256=sha(Path(__file__)),
                  derivative_runtime_sha256=runtime_hashes,
                  input_data_sha256={n:sha(data/n) for n in DATA_FILES},
                  frozen_data_sha256={n:sha(candidate/n) for n in DATA_FILES},
                  native_bindings=native_binding,stages=stages,
                  adapter_label_binding=label_binding,
                  hosted_owner_bindings={name:sha(work/name) for name in
                      ['DISCOVERY-OWNER-BINDING.json','STRICT-OWNER-BINDING.json',
                       'OWNER-BINDING-CONTROLS.json']},
                  final_kappa=str(k),baseline_kappa=str(old),gain=str(k-old),
                  comparison_supplier='PR2312 canonical outer/OUTER-CLAIM.json',
                  genuine_improvement_over_pr2312=k>old,
                  genuine_improvement_over_pr2288=k>Q(read(baseline_package/'outer/OUTER-CLAIM.json')['kappa']),
                  strict_assembly_sha256=sha(work/'strict/ASSEMBLY.json'),
                  ledger_sha256=sha(outer_root/'outer/LEDGER.json'),
                  independent_sha256=sha(outer_root/'outer/INDEPENDENT.json'),
                  scope='Exact changed supplier/owner finite admission with '
                        'the retained PR2288 fine-prime outer; inherited '
                        'all-size assumptions remain. No publication claim.')
    (work/'DELTA-ADMISSION.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_CHANGED_T74_FULL_DELTA_ADMISSION',str(float(k)),
          'gain',str(float(k-old)),flush=True)


if __name__ == '__main__':
    main()
