"""Fresh reconstruction of the eleven-stage cross-copy hosted bit supplier (with target mixing) paired with PR #448's complex word.
usage: python -B research/e8-eleven-stage-cross-copy/verify.py /absolute/new/output [--quick] [--no-anchor] [--discover-check]
  --quick           skip only PR #443's historical regressions (as in PR #444)
  --no-anchor       skip the nine-stage regression anchors (PR #443's template, PR #448's bit template and result)
  --discover-check  recompute the frozen tape-hosting selection with scipy (HiGHS) and require equality (needs numpy, scipy)
needs: Python 3.11+, numpy, mpmath, sympy (as PR #443); a C++17 compiler (CXX, default c++) and Boost headers
(BOOST_INCLUDE, default /usr/include).  Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code."""
from pathlib import Path
import gzip, hashlib, json, os, shutil, subprocess, sys, time
from fractions import Fraction
assert __debug__
ROOT = Path(__file__).resolve().parent; R = ROOT.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = {a for a in sys.argv[1:] if a.startswith('--')}
assert len(args) == 1 and flags <= {'--quick', '--no-anchor', '--discover-check'}, __doc__
out = Path(args[0]).resolve(); assert not out.exists() and not out.is_relative_to(R)
quick = '--quick' in flags
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
CXX = os.environ.get('CXX', 'c++'); BOOST = os.environ.get('BOOST_INCLUDE', '/usr/include')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', PYTHON=PY, CXX=CXX, BOOST_INCLUDE=BOOST); env.pop('PYTHONOPTIMIZE', None)
steps = []; (out / 'logs').mkdir()
P443 = R / 'e8-r740-replica32'; P448 = R / 'cross-copy-hosting'; CODE = ROOT / 'code'
BITC = P443 / 'parent436/code/bit'; CK = BITC / 'checkers'
WORD = P443 / 'data/word.json.gz'; ISO = P443 / 'data/residual-isometries.json'; SEL = ROOT / 'data/selection.json'
K448 = '1330733966732373/1000000000000000000'                 # PR #448 (higherbeing): the frontier this package is measured against
C448 = Fraction(66625358964838932161, 5 * 10 ** 22)           # PR #448's bit lower endpoint at nine stages
C447 = Fraction(1267514693114214441041, 10 ** 24)             # PR #447's bit lower endpoint at eleven stages (single copy)
NINE434 = 'bit426-source-centres/global'; REC434 = 'bit426-source-centres/records'
def run(name, cmd, cwd=None, expect_fail=False, stdout_to=None):
    t = time.monotonic(); log = out / 'logs' / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f, (open(stdout_to, 'w') if stdout_to is not None else f) as g:
        q = subprocess.run(list(map(str, cmd)), cwd=cwd, env=env, stdout=g, stderr=f if stdout_to is not None else subprocess.STDOUT)
    if expect_fail:
        if q.returncode == 0: raise RuntimeError(('negative control accepted', name))
    elif q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-4000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 2), log_sha256=sha(log))); print(('REJECTED' if expect_fail else 'PASS'), name, flush=True)
def py(name, path, *a, **k): run(name, [PY, '-B', path, *a], **k)
def same_json(a, b, drop=('seconds',)):
    x, y = read(a), read(b)
    for d in drop: x.pop(d, None); y.pop(d, None)
    return x == y
def same_bytes(a, b): return Path(a).read_bytes() == Path(b).read_bytes()
try:
    compiler = subprocess.run([CXX, '--version'], capture_output=True, text=True).stdout.splitlines()[0]
    # ---------------- parents: PR #443 (word, local checks, C++ legality/columns) and PR #448 (cross-copy complex word, PR #434 chain)
    base = out / 'base443'
    run('parent443', ['bash', P443 / 'verify.sh', *(['--quick'] if quick else []), base])
    cand = base / 'candidate'; bindir = base / 'parent/bin'
    up = out / 'upstream448'; py('parent448', P448 / 'verify.py', up)
    ch434 = up / 'parent/changed'
    # ---------------- nine-stage regression anchors
    anchor = {}
    if '--no-anchor' not in flags:
        a = out / 'anchor'; (a / 'geo9').mkdir(parents=True); (a / 'nine').mkdir()
        py('anchor-geometry', CODE / 'geometry_k.py', '--source', P443 / 'parent436', '--out', a / 'geo9')
        assert same_json(a / 'geo9/GEOMETRY.json', base / 'parent/nine/GEOMETRY.json'), 'nine-stage geometry differs from PR #386/#443'
        shutil.copy(cand / 'nine/GEOMETRY.json', a / 'nine/GEOMETRY.json')
        py('anchor-global', CODE / 'global_k.py', '--word', WORD, '--local-check', cand, '--out', a / 'nine', '--isometries', ISO)
        assert same_bytes(a / 'nine/GLOBAL-TEMPLATE.json.gz', cand / 'nine/GLOBAL-TEMPLATE.json.gz'), 'parent template differs from PR #443'
        assert same_json(a / 'nine/GLOBAL.json', cand / 'nine/GLOBAL.json'), 'parent GLOBAL.json differs from PR #443'
        py('anchor-parent-audit', CODE / 'audit_parent_k.py', '--local-check', cand, '--out', a / 'nine', '--word', WORD)
        # PR #448's own bit template (R747 word of PR #434) reproduced by the generalised emitter
        py('anchor-cross-copy-emit', CODE / 'emit_tape_k.py', ch434 / NINE434, ch434 / 'bit426-source-centres', a / 'bit448', '--selection', P448 / 'SELECTION.json', '--key', 'bit')
        assert same_bytes(a / 'bit448/GLOBAL-TEMPLATE.json.gz', up / 'bit/GLOBAL-TEMPLATE.json.gz'), 'cross-copy bit template differs from PR #448'
        assert same_json(a / 'bit448/GLOBAL.json', up / 'bit/GLOBAL.json'), 'cross-copy GLOBAL.json differs from PR #448'
        py('anchor-cross-copy-emit-redigest', CODE / 'emit_tape_k.py', ch434 / NINE434, ch434 / 'bit426-source-centres', a / 'bit448d', '--selection', P448 / 'SELECTION.json', '--key', 'bit', '--redigest', '--depth', 2)
        py('anchor-cross-copy-audit', CODE / 'audit_tape_k.py', ch434, a / 'bit448d', a / 'bit448d/AUDIT.json', '--nine', NINE434, '--records', REC434)
        py('anchor-assembly', CODE / 'assemble_k.py', ch434, up, a / 'bit448d', a / 'bit448d/AUDIT.json', a / 'RESULT.json', '--nine', NINE434, '--residual-isometry', 0, '--route-extra', 3)
        ar = read(a / 'RESULT.json'); ex = read(P448 / 'EXPECTED.json')
        for k in ('kappa', 'kappa_decimal', 'bit_lower', 'complex_lower', 'binding_component', 'bit_template_sha256', 'complex_template_sha256'): assert ar[k] == ex[k], ('anchor differs from PR #448 EXPECTED', k, ar[k], ex[k])
        anchor = dict(kappa=ar['kappa'], bit_lower=ar['bit_lower'], emitted_program_sha256=ar['emitted_program_sha256'])
    # ---------------- eleven-stage geometry, C++ formal-column checker at K = 5 and the geometry negative control
    s11 = out / 'eleven'; (s11 / 'geo/nine').mkdir(parents=True); (s11 / 'bin').mkdir()
    py('geometry-eleven', CODE / 'geometry_k.py', '--source', P443 / 'parent436', '--out', s11 / 'geo/nine', '--stages', 11, '--no-timing')
    geo = read(s11 / 'geo/nine/GEOMETRY.json')
    assert (geo['m'], geo['stages'], geo['route_checks'], geo['max_route_factors'], geo['route_denominators'], geo['bad_prime_factors']) == (78, 11, 1320, 77, [1, 2, 4], [2])
    run('cxx-columns-k5', [CXX, '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=740', '-DKPAIRS=5', '-I' + str(P443 / 'parent436/portable-include'),
                           '-I' + str(CK), '-I' + BOOST, '-o', s11 / 'bin/columns_k5', CK / 'columns_k.cpp'])
    if '--no-anchor' not in flags:
        (s11 / 'neg/nine').mkdir(parents=True); shutil.copy(out / 'anchor/geo9/GEOMETRY.json', s11 / 'neg/nine/GEOMETRY.json')
        run('negative-control-wrong-geometry', [PY, '-B', CODE / 'global_k.py', '--word', WORD, '--local-check', cand, '--out', s11 / 'neg/nine', '--isometries', ISO,
                                                 '--stages', 11, '--replicas', 1, '--no-banks'], expect_fail=True)
    # ---------------- the word variants
    results = {}
    def local_checks(label, word, d):
        py(label + '-export', BITC / 'export_records.py', word, d / 'records')
        py(label + '-stage-cohort', BITC / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout')
        run(label + '-legality', [bindir / 'legality', d / 'cin', d / 'cout', d / 'cout/legality.json'], stdout_to=d / 'cout/legality.log')
        run(label + '-columns-h', [bindir / 'columns_h', d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns.json'], stdout_to=d / 'cout/columns.log')
        l, c = read(d / 'cout/legality.json'), read(d / 'cout/columns.json')
        assert l['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies'] == l['erasures'] == 9
        assert c['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked'] == 4 * 120 + 740
    def k5(label, d):
        run(label + '-columns-k5', [s11 / 'bin/columns_k5', d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns_k5.json'], stdout_to=d / 'cout/columns_k5.log')
        k = read(d / 'cout/columns_k5.json')
        assert k['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked'] == 10 * 120 + 740
        assert k['bridge_additions'] == 24 * 120 and len(k['stages']) == 11 and len(k['negative_controls']) == 24 and all(x['rejected'] for x in k['negative_controls'])
        py(label + '-mutate-records', BITC / 'mutate_records.py', d / 'records', d / 'cin', d / 'cout', bindir / 'legality', s11 / 'bin/columns_k5', bindir / 'legality_ncopy_h')
        return dict(columns_k5_formal=k['formal_columns_checked'], columns_k5_prefix_bits=k['payload_prefix_bits'], omitted_bridge_controls=len(k['negative_controls']))
    def eleven(label, word, local, depth=3):
        v = out / 'eleven' / label; (v / 'nine').mkdir(parents=True); shutil.copy(s11 / 'geo/nine/GEOMETRY.json', v / 'nine/GEOMETRY.json')
        (v / 'records').symlink_to(local / 'records', target_is_directory=True)
        py(label + '-global', CODE / 'global_k.py', '--word', word, '--local-check', local, '--out', v / 'nine', '--isometries', ISO, '--stages', 11, '--replicas', 1, '--no-banks')
        py(label + '-parent-audit', CODE / 'audit_parent_k.py', '--local-check', local, '--out', v / 'nine', '--word', word)
        if '--discover-check' in flags:
            sel = v / 'selection-recomputed.json'
            py(label + '-discover', CODE / 'emit_tape_k.py', v / 'nine', local, v / 'hosted-discover', '--selection', sel, '--key', 'bit11_tape', '--discover', '--host-all', '--depth', depth,
               '--redigest', '--version-tag', 'e8-eleven-stage-idle-hosting-cross-copy-v1')
            assert read(sel)['bit11_tape'] == read(SEL)['bit11_tape'], 'frozen hosting selection differs from the recomputed optimum'
        py(label + '-emit', CODE / 'emit_tape_k.py', v / 'nine', local, v / 'hosted', '--selection', SEL, '--key', 'bit11_tape', '--host-all', '--depth', depth, '--redigest',
           '--version-tag', 'e8-eleven-stage-idle-hosting-cross-copy-v1')
        py(label + '-hosted-audit', CODE / 'audit_tape_k.py', v, v / 'hosted', v / 'hosted/AUDIT.json')
        py(label + '-assembly', CODE / 'assemble_k.py', v, up, v / 'hosted', v / 'hosted/AUDIT.json', v / 'RESULT.json', '--route-extra', 3, '--parent-kappa', K448, '--label', '#448')
        res = read(v / 'RESULT.json'); res['parent_global'] = read(v / 'nine/GLOBAL.json')
        res['parent_audit'] = read(v / 'nine/AUDIT.json'); res['hosted_audit'] = read(v / 'hosted/AUDIT.json'); res['hosted_global'] = read(v / 'hosted/GLOBAL.json')
        return res
    info_u = k5('unmixed', cand)
    results['stacked_unmixed'] = eleven('stacked_unmixed', WORD, cand)
    mx = out / 'mixed'; mx.mkdir()
    py('mix-generate', CODE / 'mix_target.py', WORD, mx / 'word-mixed.json')
    local_checks('mixed', mx / 'word-mixed.json', mx)
    info_m = k5('mixed', mx)
    py('mix-check', CODE / 'mix_check.py', mx / 'word-mixed.json', mx / 'records', '--controls', WORD, stdout_to=mx / 'mix-check.json')
    mc = read(mx / 'mix-check.json'); assert mc['status'] == 'PASS' and set(mc['mutation_controls'].values()) == {'REJECTED'} and len(mc['mutation_controls']) == 4
    run('mixed-gram', [PY, '-I', '-B', CK / 'gram_frames.py', mx / 'records', '--gram', 'e8ham', '--h', 8, '--positive'])
    results['stacked_mixed'] = eleven('stacked_mixed', mx / 'word-mixed.json', mx)
    # ---------------- compare with EXPECTED.json
    record = bool(os.environ.get('E8ELEVEN_RECORD')); actual = {}
    expected = {} if record else read(ROOT / 'EXPECTED.json')
    for name, res in results.items():
        e = {} if record else expected['variants'][name]
        got = dict(kappa=res['kappa'], bit_lower=res['bit_lower'], complex_lower=res['complex_lower'], binding_component=res['binding_component'],
                   bit_template_sha256=res['bit_template_sha256'], parent_template_sha256=res['parent_global']['template_sha256'],
                   complex_template_sha256=res['complex_template_sha256'], emitted_program_sha256=res['emitted_program_sha256'],
                   word_sha256=res['parent_global']['word_sha256'], live=res['bit']['live'], maxchild=res['bit']['maxchild'],
                   hosted_residuals=res['bit']['hosted_residuals'], split_residuals=res['hosted_audit']['split_residuals'], halving_depth=res['halving_depth'],
                   external_row_allowance=res['external_row_allowance'], bit=res['bit'], bit_profile=res['bit_profile'], complex=res['complex'],
                   omitted_bridge_shears_rejected=len(res['parent_global']['omitted_bridge_shears_rejected']),
                   parent_mutations_rejected=len(res['parent_audit']['mutations_rejected']), hosted_mutations_rejected=len(res['hosted_audit']['mutations_rejected']),
                   outer_controls=res['outer_controls'], strict_constraints=len(res['strict_outer_constraints']), bit_only_kappa=res['bit_only_kappa'],
                   gain_over_pr448_percent=res['gain_over_reference_percent'],
                   bit_c_gain_over_pr448_percent=float(100 * (Fraction(res['bit_lower']) / C448 - 1)),
                   bit_c_gain_over_pr447_percent=float(100 * (Fraction(res['bit_lower']) / C447 - 1)))
        for k, v in e.items(): assert got[k] == v, (name, k, got[k], v)
        actual[name] = got
    checks = dict(unmixed_k5=info_u, mixed_k5=info_m, mixed_word_sha256=sha(mx / 'word-mixed.json'), mixed_local_profile=mc['profile'], mixed_local_cost_per_call=mc['local_cost_per_call'])
    if record:
        (out / 'EXPECTED.recorded.json').write_text(json.dumps(dict(status='PASS_ELEVEN_STAGE_CROSS_COPY_COMPOSITION', variants=actual, checks=checks, anchor=anchor), indent=2, sort_keys=True) + '\n')
    else:
        assert checks == expected['checks'], (checks, expected['checks'])
        if anchor: assert anchor == expected['anchor'], anchor
    integrity()
    head = results['stacked_mixed']
    receipt = dict(status='PASS_ELEVEN_STAGE_CROSS_COPY_COMPOSITION', mode='quick' if quick else 'full', kappa=head['kappa'], kappa_decimal=head['kappa_decimal'],
                   binding_component=head['binding_component'], gain_over_pr448_percent=head['gain_over_reference_percent'],
                   variants={n: dict(kappa=r['kappa'], kappa_decimal=r['kappa_decimal'], binding=r['binding_component'], bit_c=r['bit_lower'],
                                    gain_over_pr448_percent=r['gain_over_reference_percent'], halving_depth=r['halving_depth'], maxchild=r['bit']['maxchild'])
                             for n, r in results.items()},
                   anchor=anchor or 'skipped', manifest_sha256=sha(ROOT / 'MANIFEST.json'), source_sha256=sha(ROOT / 'SOURCE.json'),
                   compiler=compiler, python=sys.version.split()[0], checks=steps)
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps({k: receipt[k] for k in ('status', 'kappa', 'kappa_decimal', 'binding_component', 'gain_over_pr448_percent', 'compiler')}, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
