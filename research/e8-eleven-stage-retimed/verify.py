"""Gate-frame retiming of PR #450's eleven-stage cross-copy hosted bit word, priced by PR #450's own pipeline.
usage: python -B research/e8-eleven-stage-retimed/verify.py /absolute/new/output [--quick] [--no-anchor]
  The flags are passed to PR #450's verify.py, which runs first and unchanged into <output>/parent450.
needs: everything PR #450's verify.py needs (Python 3.11+, numpy, mpmath, sympy, a C++17 compiler via CXX, Boost headers via BOOST_INCLUDE).
Apache-2.0."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, time
from fractions import Fraction
assert __debug__
ROOT = Path(__file__).resolve().parent; R = ROOT.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = {a for a in sys.argv[1:] if a.startswith('--')}
assert len(args) == 1 and flags <= {'--quick', '--no-anchor'}, __doc__
out = Path(args[0]).resolve(); assert not out.exists() and not out.is_relative_to(R)
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(p):
    return {f.relative_to(p).as_posix(): sha(f) for f in sorted(Path(p).rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
def integrity():
    actual = inventory(ROOT); actual.pop('MANIFEST.json')
    assert actual == read(ROOT / 'MANIFEST.json'), 'package manifest differs'
    for name, expected in read(ROOT / 'SOURCE.json')['packages'].items():
        assert inventory(R / name) == expected['files'], ('upstream package differs', name)
integrity(); out.mkdir(parents=True)
PY = sys.executable
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None)
steps = []; (out / 'logs').mkdir()
PARENT = R / 'e8-eleven-stage-cross-copy'; P443 = R / 'e8-r740-replica32'; CODE = PARENT / 'code'
BITC = P443 / 'parent436/code/bit'; CK = BITC / 'checkers'
WORD = P443 / 'data/word.json.gz'; ISO = P443 / 'data/residual-isometries.json'; SEL = PARENT / 'data/selection.json'
APPLY = ROOT / 'code/retime_apply.py'; DATA = ROOT / 'data'
K450 = '269548909542967/200000000000000000'                   # PR #450: the frontier this package is measured against
K448 = '1330733966732373/1000000000000000000'
MIXED450 = '8faf6b8438d4360df161798e1029ccfd6554f9e8a6d2686c08c743e388f74b33'   # PR #450's mixed word (file sha256, as in its EXPECTED.json)
def run(name, cmd, cwd=None, expect_fail=False, stdout_to=None):
    t = time.monotonic(); log = out / 'logs' / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f, (open(stdout_to, 'w') if stdout_to is not None else f) as g:
        q = subprocess.run(list(map(str, cmd)), cwd=cwd, env=env, stdout=g, stderr=f if stdout_to is not None else subprocess.STDOUT)
    if expect_fail:
        if q.returncode == 0: raise RuntimeError(('negative control accepted', name))
    elif q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-4000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 2), log_sha256=sha(log))); print(('REJECTED' if expect_fail else 'PASS'), name, flush=True)
def py(name, path, *a, **k): run(name, [PY, '-B', path, *a], **k)
try:
    # ---------------- PR #450 first, unchanged: its word, checkers, binaries, geometry, complex side and published kappa
    par = out / 'parent450'
    run('parent450', [PY, '-B', PARENT / 'verify.py', par, *sorted(flags)])
    pr = read(par / 'RECEIPT.json'); assert pr['status'] == 'PASS_ELEVEN_STAGE_CROSS_COPY_COMPOSITION' and pr['kappa'] == K450, pr
    bindir = par / 'base443/parent/bin'; k5bin = par / 'eleven/bin/columns_k5'; geo = par / 'eleven/geo/nine/GEOMETRY.json'; up = par / 'upstream448'
    mixed450 = par / 'mixed/word-mixed.json'; assert sha(mixed450) == MIXED450
    # ---------------- the retimed word: witness on the parent word, PR #450's target mixing unchanged, witness on the mixed word
    ret = out / 'retimed'; ret.mkdir()
    py('retime-unmixed', APPLY, WORD, DATA / 'witness-unmixed.json', ret / 'word-unmixed-retimed.json')
    py('remix', CODE / 'mix_target.py', ret / 'word-unmixed-retimed.json', ret / 'remix.json')
    py('retime-mixed', APPLY, ret / 'remix.json', DATA / 'witness-mixed.json', ret / 'word-retimed.json')   # pins the content hashes of remix.json and of the result
    word = ret / 'word-retimed.json'
    def local_checks(label, word, d):
        py(label + '-export', BITC / 'export_records.py', word, d / 'records')
        py(label + '-stage-cohort', BITC / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout')
        run(label + '-legality', [bindir / 'legality', d / 'cin', d / 'cout', d / 'cout/legality.json'], stdout_to=d / 'cout/legality.log')
        run(label + '-columns-h', [bindir / 'columns_h', d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns.json'], stdout_to=d / 'cout/columns.log')
        l, c = read(d / 'cout/legality.json'), read(d / 'cout/columns.json')
        assert l['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies'] == l['erasures'] == 9
        assert c['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked'] == 4 * 120 + 740
    def k5(label, d):
        run(label + '-columns-k5', [k5bin, d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns_k5.json'], stdout_to=d / 'cout/columns_k5.log')
        k = read(d / 'cout/columns_k5.json')
        assert k['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked'] == 10 * 120 + 740
        assert k['bridge_additions'] == 24 * 120 and len(k['stages']) == 11 and len(k['negative_controls']) == 24 and all(x['rejected'] for x in k['negative_controls'])
        py(label + '-mutate-records', BITC / 'mutate_records.py', d / 'records', d / 'cin', d / 'cout', bindir / 'legality', k5bin, bindir / 'legality_ncopy_h')
        return dict(columns_k5_formal=k['formal_columns_checked'], columns_k5_prefix_bits=k['payload_prefix_bits'], omitted_bridge_controls=len(k['negative_controls']))
    def eleven(label, word, local, depth=3):
        v = out / 'eleven' / label; (v / 'nine').mkdir(parents=True); shutil.copy(geo, v / 'nine/GEOMETRY.json')
        (v / 'records').symlink_to(local / 'records', target_is_directory=True)
        py(label + '-global', CODE / 'global_k.py', '--word', word, '--local-check', local, '--out', v / 'nine', '--isometries', ISO, '--stages', 11, '--replicas', 1, '--no-banks')
        py(label + '-parent-audit', CODE / 'audit_parent_k.py', '--local-check', local, '--out', v / 'nine', '--word', word)
        py(label + '-emit', CODE / 'emit_tape_k.py', v / 'nine', local, v / 'hosted', '--selection', SEL, '--key', 'bit11_tape', '--host-all', '--depth', depth, '--redigest',
           '--version-tag', 'e8-eleven-stage-idle-hosting-cross-copy-v1')
        py(label + '-hosted-audit', CODE / 'audit_tape_k.py', v, v / 'hosted', v / 'hosted/AUDIT.json')
        py(label + '-assembly', CODE / 'assemble_k.py', v, up, v / 'hosted', v / 'hosted/AUDIT.json', v / 'RESULT.json', '--route-extra', 3, '--parent-kappa', K450, '--label', '#450')
        res = read(v / 'RESULT.json'); res['parent_global'] = read(v / 'nine/GLOBAL.json')
        res['parent_audit'] = read(v / 'nine/AUDIT.json'); res['hosted_audit'] = read(v / 'hosted/AUDIT.json'); res['hosted_global'] = read(v / 'hosted/GLOBAL.json')
        return res
    local_checks('retimed', word, ret)
    info = k5('retimed', ret)
    py('retimed-mix-check', CODE / 'mix_check.py', word, ret / 'records', '--controls', WORD, stdout_to=ret / 'mix-check.json')
    mc = read(ret / 'mix-check.json'); assert mc['status'] == 'PASS' and set(mc['mutation_controls'].values()) == {'REJECTED'} and len(mc['mutation_controls']) == 4
    run('retimed-gram', [PY, '-I', '-B', CK / 'gram_frames.py', ret / 'records', '--gram', 'e8ham', '--h', 8, '--positive'])
    res = eleven('retimed', word, ret)
    # ---------------- negative controls on the witness format
    neg = out / 'controls'; neg.mkdir()
    py('control-wrong-word', APPLY, WORD, DATA / 'witness-mixed.json', neg / 'wrong-word.json', expect_fail=True)                      # witness input hash mismatch
    py('control-wrong-frame-apply', APPLY, ret / 'remix.json', DATA / 'control-wrong-frame.json', neg / 'wrong-frame.json', '--unchecked')
    d = neg / 'wrong-frame'; d.mkdir()
    py('control-wrong-frame-export', BITC / 'export_records.py', neg / 'wrong-frame.json', d / 'records')
    py('control-wrong-frame-stage-cohort', BITC / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout')
    run('control-wrong-frame-legality', [bindir / 'legality', d / 'cin', d / 'cout', d / 'cout/legality.json'], stdout_to=d / 'cout/legality.log', expect_fail=True)
    py('control-mix-crossing-apply', APPLY, mixed450, DATA / 'control-mix-crossing.json', neg / 'mix-crossing.json', '--unchecked')
    d = neg / 'mix-crossing'; d.mkdir()
    py('control-mix-crossing-export', BITC / 'export_records.py', neg / 'mix-crossing.json', d / 'records')
    py('control-mix-crossing-stage-cohort', BITC / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout')
    run('control-mix-crossing-legality', [bindir / 'legality', d / 'cin', d / 'cout', d / 'cout/legality.json'], stdout_to=d / 'cout/legality.log')   # frames are legal ...
    run('control-mix-crossing-columns-h', [bindir / 'columns_h', d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns.json'], stdout_to=d / 'cout/columns.log', expect_fail=True)   # ... but a target column breaks
    # ---------------- compare with EXPECTED.json
    record = bool(os.environ.get('E8RETIMED_RECORD'))
    got = dict(kappa=res['kappa'], kappa_decimal=res['kappa_decimal'], bit_lower=res['bit_lower'], complex_lower=res['complex_lower'], binding_component=res['binding_component'],
               bit_template_sha256=res['bit_template_sha256'], parent_template_sha256=res['parent_global']['template_sha256'],
               complex_template_sha256=res['complex_template_sha256'], emitted_program_sha256=res['emitted_program_sha256'],
               word_sha256=res['parent_global']['word_sha256'], live=res['bit']['live'], maxchild=res['bit']['maxchild'],
               hosted_residuals=res['bit']['hosted_residuals'], split_residuals=res['hosted_audit']['split_residuals'], halving_depth=res['halving_depth'],
               external_row_allowance=res['external_row_allowance'], bit=res['bit'], bit_profile=res['bit_profile'], complex=res['complex'],
               omitted_bridge_shears_rejected=len(res['parent_global']['omitted_bridge_shears_rejected']),
               parent_mutations_rejected=len(res['parent_audit']['mutations_rejected']), hosted_mutations_rejected=len(res['hosted_audit']['mutations_rejected']),
               outer_controls=res['outer_controls'], strict_constraints=len(res['strict_outer_constraints']), bit_only_kappa=res['bit_only_kappa'],
               gain_over_pr450_percent=res['gain_over_reference_percent'], gain_over_pr450_percent_exact=str(100 * (Fraction(res['kappa']) / Fraction(K450) - 1)))
    checks = dict(retimed_k5=info, retimed_word_file_sha256=sha(word), retimed_word_content_sha256=read(DATA / 'witness-mixed.json')['output_sha256'],
                  remix_content_sha256=read(DATA / 'witness-mixed.json')['input_sha256'], unmixed_retimed_content_sha256=read(DATA / 'witness-unmixed.json')['output_sha256'],
                  frame_changes=dict(unmixed=read(DATA / 'witness-unmixed.json')['count'], mixed=read(DATA / 'witness-mixed.json')['count']),
                  retimed_local_profile=mc['profile'], retimed_local_cost_per_call=mc['local_cost_per_call'], parent450_kappa=pr['kappa'], parent450_mixed_word_sha256=MIXED450)
    assert Fraction(res['kappa']) > Fraction(K450) and res['binding_component'] == 'bit'
    if record:
        (out / 'EXPECTED.recorded.json').write_text(json.dumps(dict(status='PASS_ELEVEN_STAGE_RETIMED_COMPOSITION', result=got, checks=checks), indent=2, sort_keys=True) + '\n')
    else:
        expected = read(ROOT / 'EXPECTED.json')
        for k, v in expected['result'].items(): assert got[k] == v, (k, got[k], v)
        assert checks == expected['checks'], (checks, expected['checks'])
    integrity()
    receipt = dict(status='PASS_ELEVEN_STAGE_RETIMED_COMPOSITION', mode='quick' if '--quick' in flags else 'full', kappa=res['kappa'], kappa_decimal=res['kappa_decimal'],
                   binding_component=res['binding_component'], gain_over_pr450_percent=res['gain_over_reference_percent'], bit_c=res['bit_lower'],
                   parent450=dict(kappa=pr['kappa'], mode=pr['mode'], anchor=pr['anchor']), manifest_sha256=sha(ROOT / 'MANIFEST.json'), source_sha256=sha(ROOT / 'SOURCE.json'),
                   compiler=pr['compiler'], python=sys.version.split()[0], checks=steps)
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps({k: receipt[k] for k in ('status', 'kappa', 'kappa_decimal', 'binding_component', 'gain_over_pr450_percent')}, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
