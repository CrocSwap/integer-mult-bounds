"""replay_full.py: complete finite admission of the pivot-566 kernel on PR1319's T74 exact-fill construction.

Not part of the bounded registered hook (it takes about 10-20 minutes and needs Python 3.14 with SymPy, like PR1319).
Stages, all with unchanged predecessor code:
  parent        PR1297's own verify.py (retained provider and parent admission; extracts the upstream layout). Optional
                --orig-base-native-from/--orig-extra-native-from reuse completed natives of PR1297's ORIGINAL words.
  native-*      the lineage native chain (layout/joint1148-round45/source/research/k8-eight-ends/replay_native.py, as in
                PR1297) on both shipped words, unless --new-*-native-from gives completed directories (bound by FULL-WORD).
  rebind        rebind.py regenerates PLAN/PROFILE from those natives; PLAN must equal data/PLAN.json except the receipt hashes
                that PR1319's bind step itself rebinds (timing-bearing phase receipts; their content is semantically pinned).
  strict-t74    PR1319's replay.py (bind, emit, audit + 15 mutations, invoice, assembly, 114 admission and 12 bit
                controls, independent owner audit) with data/SPEC.json; kappa must equal SPEC.expected.kappa.
  geometry      PR1319's geometry_controls.py: 6 geometry/charge mutations rejected.
  refined       (--refined) the same strict replay with PR1549's refined assembler overlaid (vendor/pr1549/code, its fine
                engines with the PR1519 parity repair) and data/SPEC-R200.json: 1e-200 certified endpoints, 200-digit grid,
                90 bootstrap steps; plus PR1549's fine-engine 2*atanh oracle check.
usage: python3 -B replay_full.py --work /abs/new/dir [--refined] [--orig-base-native-from D --orig-extra-native-from D]
                                 [--new-gauge44-native-from D --new-extra-native-from D]"""
import argparse, gzip, hashlib, json, os, shutil, subprocess, sys, time
from pathlib import Path
assert __debug__, 'assertions required'
PKG = Path(__file__).resolve().parent; ROOT = PKG.parents[1]; P1319 = ROOT / 'research/global-mixed-t74-exact-fill'; V1297 = P1319 / 'vendor/pr1297'
ap = argparse.ArgumentParser(); ap.add_argument('--work', type=Path, required=True); ap.add_argument('--refined', action='store_true')
for k in ('orig-base', 'orig-extra', 'new-gauge44', 'new-extra'): ap.add_argument('--%s-native-from' % k, type=Path)
a = ap.parse_args(); work = a.work.resolve(); assert not work.exists() and not work.is_relative_to(PKG); work.mkdir()
def rd(p): p = Path(p); return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
env = dict(os.environ, TMPDIR=str(work), PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
for k in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'): env.pop(k, None)
stages = []
def run(name, script, *args, cwd=None):
    t = time.monotonic(); log = work / (name + '.log')
    with log.open('w') as f: r = subprocess.run([sys.executable, '-B', str(script), *map(str, args)], cwd=cwd or work, env=env, stdout=f, stderr=subprocess.STDOUT)
    stages.append(dict(name=name, exit_code=r.returncode, seconds=round(time.monotonic() - t, 1), log_sha256=sha(log))); (work / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
    assert r.returncode == 0, (name, log.read_text()[-5000:]); print('PASS', name, stages[-1]['seconds'], flush=True)
opts = []
if a.orig_base_native_from: opts += ['--base-native-from', a.orig_base_native_from.resolve()]
if a.orig_extra_native_from: opts += ['--extra-native-from', a.orig_extra_native_from.resolve()]
run('parent', V1297 / 'verify.py', '--work', work / 'parent', *opts)
assert rd(work / 'parent/RESULT.json')['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
layout = work / 'parent/layout'; native = {}
words = {'gauge44': PKG / 'inputs/gauge44-word-566.json.gz', 'extra': PKG / 'inputs/extra-word-566.json.gz'}
for pid, w in words.items():
    reuse = getattr(a, 'new_%s_native_from' % pid)
    d = reuse.resolve() if reuse else work / ('native-' + pid)
    if not reuse: run('native-' + pid, layout / 'joint1148-round45/source/research/k8-eight-ends/replay_native.py', w, d, cwd=layout)
    assert gzip.decompress((d / 'local/FULL-WORD.json.gz').read_bytes()) == gzip.decompress(w.read_bytes()), (pid, 'native directory is not bound to the shipped word')
    steps = rd(d / 'STEPS.json'); assert [x['step'] for x in steps] == ['native', 'ledgers', 'local-replay', 'wrappers', 'phases'] and all(x['exit_code'] == 0 for x in steps)
    native[pid] = d
run('rebind', PKG / 'rebind.py', P1319, native['gauge44'] / 'local', native['extra'] / 'local', work / 'data')
# PR1319's bind_providers_portable.py byte-pins only LOCAL-CHECKS / CLIFFORD-RECIPES / RESIDUAL-ADAPTERS and rebinds every other
# artifact_sha256 (phase receipts carry timing fields; their content is pinned through artifact_semantic_sha256).
STABLE = ('LOCAL-CHECKS.json', 'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')
def bind_view(plan):
    plan = json.loads(json.dumps(plan))
    for desc in plan['provider_registry'].values(): desc['artifact_sha256'] = {n: h for n, h in desc['artifact_sha256'].items() if n in STABLE}
    return plan
assert bind_view(rd(work / 'data/PLAN.json')) == bind_view(rd(PKG / 'data/PLAN.json')), 'regenerated PLAN differs from data/PLAN.json beyond bind-rebound receipt hashes'
assert rd(work / 'data/PROFILE.json') == rd(PKG / 'data/PROFILE.json')
shutil.copy2(PKG / 'data/PLAN.json', work / 'data/PLAN.json')   # the strict chain runs on the shipped, SPEC-pinned PLAN (bind rebinds receipt hashes)
def runtime(name, overlay=None):
    R = layout / name; (R / 'inputs').mkdir(parents=True)
    for n in ('replay.py', 'freeze_spec.py', 'audit_mixed.py', 'independent_core.py', 'geometry_controls.py'): shutil.copy2(P1319 / n, R / n)
    for n in ('code', 'construction'): shutil.copytree(P1319 / n, R / n)
    shutil.copy2(P1319 / 'inputs/PR589-EXPECTED.json', R / 'inputs/PR589-EXPECTED.json'); shutil.copytree(native['extra'], R / 'native-extra')
    for f in (overlay or []): shutil.copy2(f, R / 'code' / f.name)
    return R
def strict(tag, R, spec):
    data = work / ('data-' + tag); shutil.copytree(work / 'data', data); shutil.copy2(spec, data / 'SPEC.json')
    run('strict-' + tag, R / 'replay.py', '--data', data, '--work', work / ('strict-' + tag), '--local', native['gauge44'] / 'local')
    r = rd(work / ('strict-' + tag) / 'RESULT.json'); s = rd(spec)
    assert r['status'] == 'PASS_STRICT_MIXED_T74_EXACT_FILL' and r['kappa'] == s['expected']['kappa'], (tag, r['status'], r['kappa'])
    return r
R74 = runtime('packing74-pivot566'); r74 = strict('t74', R74, PKG / 'data/SPEC.json')
run('geometry', R74 / 'geometry_controls.py', '--source', layout / 'joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold', '--strict', work / 'strict-t74', '--out', work / 'GEOMETRY-CONTROLS.json')
assert len(rd(work / 'GEOMETRY-CONTROLS.json')['rejected']) == 6
res = dict(status='PASS_T74_PIVOT566_KERNEL_COMPLETE_FINITE_ADMISSION', kappa=r74['kappa'], kappa_decimal=r74['kappa_decimal'], independent=dict((k, r74['independent'][k]) for k in ('roles', 'prefix_bits', 'charged_prefix_bits', 'physical_row_coefficient', 'row_limit')))
if a.refined:
    run('fine-engine-oracle', PKG / 'vendor/pr1549/code/oracle_check.py')
    R200 = runtime('packing74-pivot566-r200', overlay=sorted((PKG / 'vendor/pr1549/code').glob('*.py')))
    r200 = strict('r200', R200, PKG / 'data/SPEC-R200.json'); res.update(refined_kappa=r200['kappa'], refined_kappa_decimal=r200['kappa_decimal'])
res['stages'] = stages; (work / 'RESULT.json').write_text(json.dumps(res, indent=2) + '\n'); print(res['status'], res['kappa_decimal'], res.get('refined_kappa_decimal', '')[:60], flush=True)
