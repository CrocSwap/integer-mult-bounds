"""Fresh replay: PR #442 in full, regression anchor, the gauge + kernel complex word through the extended pipeline, mutation controls,
independent hosting audit, certified complex saving b and the strict outer assembly for the listed bit suppliers.
usage: python -B research/e8-complex-gauge-kernel/verify.py /absolute/new/output [--all] [--discover-check]
  --all             also run the kernel-only and gauge-only words (per-tool numbers)
  (always) the independent Lemma G check stage (code/lemmaG) runs on the headline word and the anchor, and with --all on the per-tool words
  --discover-check  recompute the frozen hosting selections with scipy/HiGHS and require byte equality (needs numpy, scipy)
needs: Python 3.11+ (standard library; numpy for the Lemma G check stage, numpy and scipy for --discover-check); the repository tree of PR #442 (this package lives in it).
Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT = Path(__file__).resolve().parent; R = ROOT.parent; CODE = ROOT / 'code'
args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = {a for a in sys.argv[1:] if a.startswith('--')}
assert len(args) == 1 and flags <= {'--all', '--discover-check', '--write-expected'}, __doc__
out = Path(args[0]).resolve(); assert not out.exists() and not out.is_relative_to(R)
read = lambda p: json.loads(Path(p).read_text()); sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(p): return {f.relative_to(p).as_posix(): sha(f) for f in sorted(Path(p).rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
def integrity():
    actual = inventory(ROOT); actual.pop('MANIFEST.json'); assert actual == read(ROOT / 'MANIFEST.json')['files'], 'package manifest differs'
    for name, exp in read(ROOT / 'SOURCE.json')['packages'].items(): assert inventory(R / name) == exp['files'], ('upstream package differs', name)
integrity(); out.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None)
PY = sys.executable; steps = []
def run(name, cmd, cwd=None):
    t = time.monotonic(); log = out / (name.replace(' ', '_') + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f: q = subprocess.run([PY, '-B', *map(str, cmd)], cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-3000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 1), log_sha256=sha(log))); print('PASS', name, flush=True)
try:
    p442 = out / 'p442'
    run('parent-442-full', [R / 'idle-axis-hosting/verify.py', p442])
    assert read(p442 / 'RECEIPT.json')['status'] == 'PASS_FULL_IDLE_AXIS_HOSTING_COMPOSITION'
    changed = p442 / 'parent/changed'
    # ---- regression anchor: empty selection reproduces PR #433/#442 byte for byte
    run('anchor', [CODE / 'run_variant.py', 'anchor', ROOT / 'data/selections/empty.json', 'complex', changed, out / 'anchor', '--anchor'])
    a, b = out / 'anchor/hosted', p442 / 'complex'
    assert (a / 'GLOBAL-TEMPLATE.json.gz').read_bytes() == (b / 'GLOBAL-TEMPLATE.json.gz').read_bytes(), 'anchor: hosted template differs from PR #442'
    ha, hb = read(a / 'HOSTED.json'), read(b / 'HOSTED.json'); ha.pop('seconds'); hb.pop('seconds'); assert ha == hb
    # ---- the words
    words = [('gauge80-kernel42', 'complex-gauge80-kernel42')] + ([('kernel79', 'complex-kernel79'), ('gauge80', 'complex-gauge80')] if '--all' in flags else [])
    procs = []
    for i, (w, key) in enumerate(words):
        extra = (['--controls'] if w == 'gauge80-kernel42' else []) + (['--discover-check'] if '--discover-check' in flags else [])
        t = time.monotonic(); log = (out / ('variant-' + w + '.log')).open('w'); print('RUN variant', w, flush=True)
        procs.append((w, t, log, subprocess.Popen([PY, '-B', str(CODE / 'run_variant.py'), w, str(ROOT / 'data/selections' / (w + '.json')), key, str(changed), str(out / w), *extra],
                                                   cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)))
    for w, t, log, p in procs:
        rc = p.wait(); log.close()
        if rc: raise RuntimeError((w, rc, (out / ('variant-' + w + '.log')).read_text()[-3000:]))
        steps.append(dict(name='variant ' + w, seconds=round(time.monotonic() - t, 1), log_sha256=sha(out / ('variant-' + w + '.log')))); print('PASS variant', w, flush=True)
    # ---- independent check stage for Lemma G (code/lemmaG: imports no package script): labels, exhaustive instance identities, end-to-end identity, necessity mutants
    lgw = [(w, ['--mutants'] if w == 'gauge80-kernel42' else []) for w, key in words] + [('anchor', [])]
    procs = []
    for w, extra in lgw:
        t = time.monotonic(); log = (out / ('lemmaG-' + w + '.log')).open('w'); print('RUN lemma G checks', w, flush=True)
        procs.append((w, t, log, subprocess.Popen([PY, '-B', str(CODE / 'lemmaG/check.py'), str(out), w, str(out / 'lemmaG' / w), *extra], cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)))
    for w, t, log, p in procs:
        rc = p.wait(); log.close()
        if rc: raise RuntimeError(('lemma G checks', w, rc, (out / ('lemmaG-' + w + '.log')).read_text()[-3000:]))
        steps.append(dict(name='lemma G checks ' + w, seconds=round(time.monotonic() - t, 1), log_sha256=sha(out / ('lemmaG-' + w + '.log')))); print('PASS lemma G checks', w, flush=True)
    lemmaG = {w: read(out / 'lemmaG' / w / 'LEMMA-G-CHECK.json') for w, extra in lgw}
    # ---- certification and outer assembly
    r442 = read(p442 / 'RESULT.json')
    bits = [dict(label='#442 bit word (R747, nine stages)', c=r442['bit_lower'], charged_two_level_coefficient_bits=r442['bit']['charged_two_level_coefficient_bits'],
                 row_coefficient=r442['bit']['row_coefficient'], source='run by this package inside the PR #442 replay')] + read(ROOT / 'data/bit-suppliers-pinned.json')
    (out / 'BITS.json').write_text(json.dumps(bits, indent=1) + '\n')
    results = {}
    for w, key in words:
        wd = out / w
        run('assemble ' + w, [CODE / 'assemble_gk.py', changed, wd / 'split-centres', wd / 'hosted', wd / 'HOSTING-AUDIT.json', out / 'BITS.json', out / ('RESULT-' + w + '.json')])
        results[w] = read(out / ('RESULT-' + w + '.json'))
        assert results[w]['complex_template_sha256'] == read(wd / 'hosted/HOSTED.json')['template_sha256']
    head = results['gauge80-kernel42']
    summary = dict(status='PASS_FULL_COMPLEX_GAUGE_KERNEL_COMPOSITION', complex_lower=head['complex_lower'], complex_decimal=head['complex_decimal'],
                   complex_cap_kappa_decimal=head['complex_cap_kappa_decimal'], baseline_442_complex=str(read(p442 / 'RESULT.json')['complex_lower']),
                   suppliers={r['label']: dict(kappa=r['kappa'], kappa_decimal=r['kappa_decimal'], binding=r['binding_component']) for r in head['suppliers']},
                   words={w: dict(complex_lower=r['complex_lower'], hosted_template_sha256=r['complex_template_sha256'], live=r['complex']['live']) for w, r in results.items()},
                   mutation_controls_word=read(out / 'gauge80-kernel42/CONTROLS-WORD.json')['rejected'], mutation_controls_selection=read(out / 'gauge80-kernel42/CONTROLS-SELECTION.json')['refused'],
                   mutation_controls_certifying_pipeline=[c['control'] for c in read(out / 'gauge80-kernel42/CONTROLS-PIPELINE.json')['controls']],
                   mutation_controls_one_owner_rule=[c['control'] for c in read(out / 'gauge80-kernel42/CONTROLS-HOSTING.json')['controls']],
                   replay_controls=read(out / 'gauge80-kernel42/split-centres/INDEPENDENT-REPLAY.json')['mutation_controls_rejected'],
                   wrapper_check={k: read(out / 'gauge80-kernel42/LEMMA-A.json')[k] for k in ('frames', 'wrappers_reject', 'all_even_weight', 'all_totally_isotropic')},
                   hosting_audit_controls=read(out / 'gauge80-kernel42/HOSTING-AUDIT.json')['mutations_rejected'],
                   hosting_audit_controls_not_applicable=read(out / 'gauge80-kernel42/HOSTING-AUDIT.json')['controls_not_applicable'],
                   hosting_rule=read(out / 'gauge80-kernel42/HOSTING-AUDIT.json')['one_helper_per_family'], lemma_G_independent_checks=lemmaG)
    if '--write-expected' in flags: (out / 'EXPECTED.candidate.json').write_text(json.dumps(summary, indent=1, sort_keys=True) + '\n')   # development: review, then copy to EXPECTED.json
    exp = read(ROOT / 'EXPECTED.json') if (ROOT / 'EXPECTED.json').exists() else None
    if exp is not None and '--all' in flags:
        for k, v in exp.items(): assert summary[k] == v, (k, summary[k], v)
    elif exp is not None:
        for k in ('complex_lower', 'complex_decimal', 'complex_cap_kappa_decimal', 'baseline_442_complex', 'suppliers', 'mutation_controls_word', 'mutation_controls_selection', 'mutation_controls_certifying_pipeline', 'mutation_controls_one_owner_rule', 'replay_controls', 'wrapper_check', 'hosting_audit_controls', 'hosting_audit_controls_not_applicable', 'hosting_rule'):
            assert summary[k] == exp[k], (k, summary[k], exp[k])
        assert summary['words']['gauge80-kernel42'] == exp['words']['gauge80-kernel42']
        for w_, v_ in summary['lemma_G_independent_checks'].items(): assert v_ == exp['lemma_G_independent_checks'][w_], ('lemma G checks', w_)
    assert inventory(ROOT).get('MANIFEST.json') is not None and (lambda a: (a.pop('MANIFEST.json'), a)[1] == read(ROOT / 'MANIFEST.json')['files'])(inventory(ROOT)), 'package modified during verification'
    receipt = dict(summary, steps=steps, python=sys.version.split()[0], manifest_sha256=sha(ROOT / 'MANIFEST.json'))
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps({k: v for k, v in summary.items() if not k.startswith('mutation_controls') and k not in ('hosting_audit_controls', 'replay_controls')}, indent=1))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
