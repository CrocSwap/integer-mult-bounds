"""Kernel-cap package: width rule, pivot ceiling, exact pivot maximum (112), annealed 112-pivot kernel selection, and the R715 bit supplier rebuilt with it.
usage: python -B research/e8-r715-kernel-cap/verify.py /absolute/new/output [--light] [flags]
  --light                 quick mode (about two minutes, no C++): package integrity and pins; ceiling analysis recomputed from the pinned
                          R715 word; EXACT pivot maximum recomputed (block DP + exhaustive search, `code/exact_pivots.py`) and required to equal
                          112; selection checked against the exact kernel conditions; kernel word rebuilt (PR #443 kernel, replay,
                          interface) and compared; target mixing regenerated and compared; width rule checked on the word and on the
                          exported records; hosting re-solve (CP-SAT, needs ortools; skipped with a notice without it) priced with the exact
                          engine against the pinned endpoint; screen composition with PR #458's pinned complex endpoint (47 strict outer
                          inequalities, next-grid rejection).
  (default) FULL mode     LIGHT plus: the seeded search re-run from scratch; PR #443's regressions; relaxed all-column checker; C++ cohort
                          legality and formal columns (five and eleven stages); mixing mutants; Gram; eleven-stage geometry/template/audit;
                          hosting selection rediscovered with HiGHS and required equal; hosted audit; assembly; pivot-count scan; PR #458's
                          complex supplier from scratch and the exact composition.
  --complex-output=DIR    use an already verified PR #458 wrapper output (e8-complex-adapted-kernel/verify.py) instead of running it
  --complex-upstream=DIR  use an already verified PR #442 layout directory (parent/changed, complex/, AUDIT.json, RESULT.json, RECEIPT.json)
  --reuse-parent443=DIR   use an already built PR #443 parent output directory (parent/bin/...) instead of running its verifier
  --quick                 pass --quick to PR #443's verifier (skips its historical regressions)
  --no-scan               skip the pivot-count scan (FULL only)
  --rewrite-manifest      developer: rewrite MANIFEST.json from the tree and exit (no output argument)
  environment: E8KCAP_RECORD=1 writes EXPECTED.recorded.json instead of comparing with EXPECTED.json.
needs: Python 3.11+, numpy, mpmath, sympy, scipy (as PR #443/#450); ortools for the hosting re-solve and the scan; a C++17 compiler (CXX) and Boost
headers (BOOST_INCLUDE) in FULL mode.  Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code."""
from pathlib import Path
import gzip, hashlib, json, os, shutil, subprocess, sys, time
from fractions import Fraction
assert __debug__
ROOT = Path(__file__).resolve().parent; R = ROOT.parent
args = [a for a in sys.argv[1:] if not a.startswith('--')]; flags = {a.split('=')[0]: a.partition('=')[2] for a in sys.argv[1:] if a.startswith('--')}
assert set(flags) <= {'--light', '--complex-output', '--complex-upstream', '--reuse-parent443', '--quick', '--no-scan', '--rewrite-manifest', '--no-discover-check'}, __doc__
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csha(p):
    w = json.load(gzip.open(p, 'rt') if str(p).endswith('.gz') else open(p))
    return hashlib.sha256(json.dumps(w, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def inventory(p):
    return {f.relative_to(p).as_posix(): sha(f) for f in sorted(Path(p).rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.suffix != '.pyc'}
RECORD = bool(os.environ.get('E8KCAP_RECORD'))
def integrity():
    actual = inventory(ROOT); actual.pop('MANIFEST.json', None)
    if not RECORD: assert actual == read(ROOT / 'MANIFEST.json'), 'package manifest differs'
    for pin in read(ROOT / 'SOURCE.json').values():       # pinned upstream packages: their manifests, their sources, and everything those cite
        pkg = R / pin['package']; assert sha(pkg / 'MANIFEST.json') == pin['manifest_sha256'] and sha(pkg / 'SOURCE.json') == pin['source_sha256'], pin['package']
        a = inventory(pkg); a.pop('MANIFEST.json'); assert a == read(pkg / 'MANIFEST.json'), ('upstream package differs', pin['package'])
        s = read(pkg / 'SOURCE.json')
        for name, expected in s.get('packages', {}).items(): assert inventory(R / name) == expected['files'], ('upstream package differs', name)
        for sub in (v for v in s.values() if isinstance(v, dict) and 'manifest_sha256' in v):
            q = R / sub['package']; assert sha(q / 'MANIFEST.json') == sub['manifest_sha256'] and sha(q / 'SOURCE.json') == sub['source_sha256'], sub['package']
            b = inventory(q); b.pop('MANIFEST.json'); assert b == read(q / 'MANIFEST.json'), ('upstream package differs', sub['package'])
            for name, expected in read(q / 'SOURCE.json').get('packages', {}).items(): assert inventory(R / name) == expected['files'], ('upstream package differs', name)
if '--rewrite-manifest' in flags:
    m = inventory(ROOT); m.pop('MANIFEST.json', None); (ROOT / 'MANIFEST.json').write_text(json.dumps(m, indent=1, sort_keys=True) + '\n'); print('MANIFEST.json rewritten,', len(m), 'files'); sys.exit(0)
assert len(args) == 1, __doc__
out = Path(args[0]).resolve(); assert not out.exists() and not out.is_relative_to(R)
LIGHT = '--light' in flags
integrity(); out.mkdir(parents=True)
PY = sys.executable
CXX = os.environ.get('CXX', 'c++'); BOOST = os.environ.get('BOOST_INCLUDE', '/usr/include')
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', PYTHON=PY, CXX=CXX, BOOST_INCLUDE=BOOST); env.pop('PYTHONOPTIMIZE', None)
steps = []; (out / 'logs').mkdir()
SIB = R / 'e8-r715-eleven-stage-whole'; P443 = R / 'e8-r740-replica32'; P442 = R / 'idle-axis-hosting'; CODE = ROOT / 'code'; SC = SIB / 'code'; D = ROOT / 'data'
BITC = P443 / 'parent436/code/bit'; CK = BITC / 'checkers'; RH = 715; WORD = SIB / 'data/word-r715.json.gz'
KSEL, ISO, SEL = D / 'kernel-selection.json', D / 'residual-isometries.json', D / 'selection.json'
SEARCH = dict(seed=3, iters=150000, restarts=1)     # the pinned search that produced data/kernel-selection.json
K463 = Fraction(641739651875561, 5 * 10 ** 17)      # #463: the R715 bit word with PR #458's complex (this package's baseline)
exp = None if RECORD else read(ROOT / 'EXPECTED.json'); rec = dict(light={}, full={})
def expect(mode, key, value):
    rec[mode][key] = value
    if not RECORD: assert exp[mode][key] == value, ('differs from EXPECTED', mode, key, value, exp[mode][key])
def run(name, cmd, cwd=None, stdout_to=None):
    t = time.monotonic(); log = out / 'logs' / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f, (open(stdout_to, 'w') if stdout_to is not None else f) as g:
        q = subprocess.run(list(map(str, cmd)), cwd=cwd, env=env, stdout=g, stderr=f if stdout_to is not None else subprocess.STDOUT)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-4000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 2), log_sha256=sha(log))); print('PASS', name, flush=True)
def py(name, path, *a, **k): run(name, [PY, '-B', path, *a], **k)
def records_widths(rdir):
    """second path for the width rule: residual width of every helper from the exported PR #249 records (initial frame ids and frame dimensions)"""
    st = read(Path(rdir) / '249-states.json'); fr = read(Path(rdir) / 'frames.json')['frames']; v = st['v']
    return [8 - fr[str(st['initial'][str(r)])]['dim'] for r in range(2 * v, 2 * v + st['R'])]
def hist(xs):
    h = {}
    for x in xs: h[str(x)] = h.get(str(x), 0) + 1
    return {k: h[k] for k in sorted(h)}
try:
    compiler = subprocess.run([CXX, '--version'], capture_output=True, text=True).stdout.splitlines()[0] if not LIGHT else None
    # ---------------- LIGHT: ceiling, selection, kernel, mixing, width rule, hosting re-solve, screen composition
    w = out / 'word'; w.mkdir()
    py('ceiling-analysis', CODE / 'kernel_cap.py', R, WORD, w / 'cap-analysis.json', stdout_to=w / 'cap.txt')
    cap = read(w / 'cap-analysis.json'); assert cap == read(D / 'cap-analysis.json'); expect('light', 'cap', cap)
    assert cap['proved_ceiling'] == cap['candidates'] - cap['response_rank_of_candidates']
    py('kernel-build', CODE / 'kernel_from_selection.py', R, WORD, KSEL, w / 'kernel.json.gz', w / 'isometries.json', stdout_to=w / 'kernel.json')
    kj = read(w / 'kernel.json'); assert csha(w / 'kernel.json.gz') == csha(D / 'word-kernel.json.gz') and read(w / 'isometries.json') == read(ISO)
    sel = read(KSEL); assert len(sel) == kj['selection']['entries'] == 112 and kj['selection']['pivots_by_entrance_rank'] == {'1': 112}
    expect('light', 'kernel', kj)
    py('exact-pivots', CODE / 'exact_pivots.py', R, WORD, w / 'exact-pivots.json', stdout_to=w / 'exact-pivots.txt')       # exact maximum, not a search
    ex = read(w / 'exact-pivots.json'); expect('light', 'exact_pivots', ex)
    assert ex['exact_max_pivots'] == ex['exact_max_pivots_after_parity'] == 112 == len(sel), 'exact pivot maximum is not the shipped 112'
    assert ex['proved_ceiling'] == cap['proved_ceiling'] and ex['candidates'] == cap['candidates'] and ex['loops'] == 0
    mx = out / 'mixed'; mx.mkdir()
    py('mix-generate', SC / 'mix_target.py', D / 'word-kernel.json.gz', mx / 'word-mixed.json', stdout_to=mx / 'mix.json')
    assert csha(mx / 'word-mixed.json') == csha(D / 'word-mixed.json.gz'), 'regenerated mixed word differs'; expect('light', 'mix', read(mx / 'mix.json'))
    py('mixed-export', BITC / 'export_records.py', mx / 'word-mixed.json', mx / 'records')
    wr = records_widths(mx / 'records'); v = 120
    pivw = {p: 8 - len(E) for E, p, Dn in sel}
    assert all(wr[h - 2 * v] == pivw.get(h, 8) for h in range(2 * v, 2 * v + len(wr))), 'width rule: records disagree with 8 - entrance rank'
    assert {h for h in range(2 * v, 2 * v + len(wr)) if wr[h - 2 * v] < 8} == set(pivw), 'only kernel pivots have a nonzero entrance'
    assert hist(wr) == kj['helper_widths']; expect('light', 'widths', hist(wr))
    try:
        sys.path.insert(0, str(CODE)); import hosting_model as HM; have_model = True
    except ImportError: have_model = False
    def model_step(profile):
        """hosting re-solve at profile level (CP-SAT, whole-residual rule), priced with the exact engine; must equal the pipeline endpoint"""
        if not have_model: print('NOTE hosting re-solve skipped (ortools missing)'); return
        t = time.monotonic(); r_ = HM.solve({int(a): b for a, b in profile.items()}, {int(a): b for a, b in hist(wr).items()}, tl=300)
        assert r_['status'] == 'OPTIMAL'; c_, W_ = HM.price(R, r_)
        expect('light', 'model', dict(c='%d/%d' % (c_.numerator, c_.denominator), W=W_, remainder={str(a): b for a, b in sorted(r_['remainder'].items())}))
        steps.append(dict(name='hosting-model', seconds=round(time.monotonic() - t, 2))); print('PASS hosting-model', flush=True)
    if not RECORD:
        model_step(exp['full']['checks']['mixed_local_profile'])
        assert Fraction(exp['light']['model']['c']) == Fraction(exp['full']['bit']['bit_lower']) if have_model else True, 'model endpoint differs from the pipeline endpoint'
    if not RECORD:
        py('compose-screen', ROOT / 'compose.py', out / 'screen.json')
        sc = read(out / 'screen.json'); assert sc['status'] == 'PASS_R715_KERNEL_CAP_COMPOSITION' and sc['outer_controls'] == ['next_grid', 'zero_eta', 'zero_beta', 'unit_beta']
        expect('light', 'screen', {k: sc[k] for k in ('kappa', 'kappa_decimal', 'bit_lower', 'complex_lower', 'binding_component', 'row_allowance', 'charged_coefficient_bits')})
        assert Fraction(sc['kappa']) > K463
    if LIGHT:
        integrity()
        receipt = dict(status='PASS_R715_KERNEL_CAP_LIGHT', mode='light', manifest_sha256=sha(ROOT / 'MANIFEST.json'), python=sys.version.split()[0], checks=steps)
        (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if RECORD: (out / 'EXPECTED.recorded.json').write_text(json.dumps(rec, indent=2, sort_keys=True) + '\n')
        print(json.dumps({k: receipt[k] for k in ('status', 'mode')}))
        sys.exit(0)
    # ---------------- FULL: the search from scratch, then the complete bit supplier on the new kernel
    py('search-selection', CODE / 'select_kernel.py', R, WORD, w / 'selection.json', '--seed', SEARCH['seed'], '--iters', SEARCH['iters'], '--restarts', SEARCH['restarts'], stdout_to=w / 'search.txt')
    assert read(w / 'selection.json') == sel, 'seeded search does not reproduce the shipped selection'; expect('full', 'search', dict(SEARCH, pivots=len(sel)))
    if flags.get('--reuse-parent443'):
        base = Path(flags['--reuse-parent443']).resolve(); assert (base / 'parent/bin/legality').exists()
    else:
        base = out / 'base443'; run('parent443', ['bash', P443 / 'verify.sh', *(['--quick'] if '--quick' in flags else []), base])
    bindir = base / 'parent/bin'
    if flags.get('--complex-upstream'):
        up = Path(flags['--complex-upstream']).resolve(); assert (up / 'RESULT.json').exists() and (up / 'complex').is_dir()
    else:
        up = out / 'upstream442'; py('parent442', P442 / 'verify.py', up)
    for tag, wd in (('kernel', D / 'word-kernel.json.gz'), ('mixed', D / 'word-mixed.json.gz')):   # independent validator's relaxed all-column checker
        py('relaxed-checkword-' + tag, SC / 'checkword_relaxed.py', wd, P443 / 'parent436/code/pricing', stdout_to=w / ('checkword-relaxed-%s.txt' % tag))
        t_ = (w / ('checkword-relaxed-%s.txt' % tag)).read_text()
        assert 'legality + exact F2 on all %d columns: PASS' % (2 * 120 + RH) in t_ and 'all Gram dets > 0' in t_
    s11 = out / 'eleven'; (s11 / 'geo/nine').mkdir(parents=True); (s11 / 'bin').mkdir()
    inc = ['-I' + str(P443 / 'parent436/portable-include'), '-I' + str(CK), '-I' + BOOST]
    run('cxx-columns-h', [CXX, '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=%d' % RH, *inc, '-o', s11 / 'bin/columns_h', CK / 'columns_h.cpp'])
    run('cxx-columns-k5', [CXX, '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=%d' % RH, '-DKPAIRS=5', *inc, '-o', s11 / 'bin/columns_k5', CK / 'columns_k.cpp'])
    py('mixed-stage-cohort', BITC / 'regression/stage_cohort.py', mx / 'records', mx / 'records', mx / 'cin', mx / 'cout')
    run('mixed-legality', [bindir / 'legality', mx / 'cin', mx / 'cout', mx / 'cout/legality.json'], stdout_to=mx / 'cout/legality.log')
    run('mixed-columns-h', [s11 / 'bin/columns_h', mx / 'cout/COHORT249-RECORDS.bin', mx / 'cout/columns.json'], stdout_to=mx / 'cout/columns.log')
    l, c = read(mx / 'cout/legality.json'), read(mx / 'cout/columns.json')
    assert l['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE' and l['copies'] == l['erasures'] == 9
    assert c['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and c['formal_columns_checked'] == 4 * 120 + RH
    run('mixed-columns-k5', [s11 / 'bin/columns_k5', mx / 'cout/COHORT249-RECORDS.bin', mx / 'cout/columns_k5.json'], stdout_to=mx / 'cout/columns_k5.log')
    k = read(mx / 'cout/columns_k5.json')
    assert k['status'] == 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' and k['formal_columns_checked'] == 10 * 120 + RH
    assert k['bridge_additions'] == 24 * 120 and len(k['stages']) == 11 and all(x['rejected'] for x in k['negative_controls'])
    py('mixed-mutate-records', BITC / 'mutate_records.py', mx / 'records', mx / 'cin', mx / 'cout', bindir / 'legality', s11 / 'bin/columns_k5', bindir / 'legality_ncopy_h')
    py('mix-check', SC / 'mix_check.py', mx / 'word-mixed.json', mx / 'records', '--controls', D / 'word-kernel.json.gz', stdout_to=mx / 'mix-check.json')
    mc = read(mx / 'mix-check.json'); assert mc['status'] == 'PASS' and set(mc['mutation_controls'].values()) == {'REJECTED'} and len(mc['mutation_controls']) == 4
    run('mixed-gram', [PY, '-I', '-B', CK / 'gram_frames.py', mx / 'records', '--gram', 'e8ham', '--h', 8, '--positive'])
    assert mc['profile'] == {str(r): z for r, z in l['paid_histogram']}, 'mix_check profile differs from the cohort legality histogram'
    model_step(mc['profile'])
    py('geometry-eleven', SC / 'geometry_k.py', '--source', P443 / 'parent436', '--out', s11 / 'geo/nine', '--stages', 11, '--no-timing')
    geo = read(s11 / 'geo/nine/GEOMETRY.json')
    assert (geo['m'], geo['stages'], geo['route_checks'], geo['max_route_factors'], geo['route_denominators'], geo['bad_prime_factors']) == (78, 11, 1320, 77, [1, 2, 4], [2])
    v_ = s11 / 'mixed_d3'; (v_ / 'nine').mkdir(parents=True); shutil.copy(s11 / 'geo/nine/GEOMETRY.json', v_ / 'nine/GEOMETRY.json')
    (v_ / 'records').symlink_to(mx / 'records', target_is_directory=True)
    py('global', SC / 'global_k.py', '--word', mx / 'word-mixed.json', '--local-check', mx, '--out', v_ / 'nine', '--isometries', ISO, '--stages', 11, '--replicas', 1, '--no-banks')
    py('parent-audit', SC / 'audit_parent_k.py', '--local-check', mx, '--out', v_ / 'nine', '--word', mx / 'word-mixed.json')
    sel_path = SEL
    if '--no-discover-check' not in flags or not SEL.exists():
        rs = v_ / 'selection-recomputed.json'
        py('discover', SC / 'emit_k.py', v_ / 'nine', mx, v_ / 'hosted-discover', '--selection', rs, '--key', 'bit11_d3', '--discover', '--host-all', '--depth', 3, '--version-tag', 'e8-eleven-stage-idle-hosting-v1')
        if SEL.exists(): assert read(rs)['bit11_d3'] == read(SEL)['bit11_d3'], 'frozen hosting selection differs from the recomputed optimum'
        else: assert RECORD, 'data/selection.json missing'; sel_path = rs
    py('emit', SC / 'emit_k.py', v_ / 'nine', mx, v_ / 'hosted', '--selection', sel_path, '--key', 'bit11_d3', '--host-all', '--depth', 3, '--version-tag', 'e8-eleven-stage-idle-hosting-v1')
    py('hosted-audit', SC / 'audit_hosted_k.py', v_, v_ / 'hosted', v_ / 'hosted/AUDIT.json')
    au = read(v_ / 'hosted/AUDIT.json'); assert au['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT' and 'wrong residual width' in au['mutations_rejected']
    py('assembly', SC / 'assemble_k.py', v_, up, v_ / 'hosted', v_ / 'hosted/AUDIT.json', v_ / 'RESULT.json', '--parent-kappa', '%d/%d' % (K463.numerator, K463.denominator), '--label', '#463')
    res = read(v_ / 'RESULT.json')
    got = dict(kappa=res['kappa'], bit_lower=res['bit_lower'], complex_lower=res['complex_lower'], binding_component=res['binding_component'],
               bit_only_kappa=res['bit_only_kappa'], bit=res['bit'], bit_profile=res['bit_profile'], halving_depth=res['halving_depth'],
               external_row_allowance=res['external_row_allowance'], strict_constraints=len(res['strict_outer_constraints']), outer_controls=res['outer_controls'],
               bit_template_sha256=res['bit_template_sha256'], emitted_program_sha256=res['emitted_program_sha256'],
               bit_c_gain_over_r715_percent=float(100 * (Fraction(res['bit_lower']) / Fraction(read(SIB / 'EXPECTED.json')['variants']['pr442']['bit_lower']) - 1)))
    expect('full', 'bit', got)
    expect('full', 'checks', dict(kernel_sha256=csha(D / 'word-kernel.json.gz'), mixed_word_sha256=csha(D / 'word-mixed.json.gz'), columns_k5_formal=k['formal_columns_checked'],
                                  mixed_local_profile=mc['profile'], mixed_local_cost_per_call=mc['local_cost_per_call'], hosted_widths=hist(wr)))
    if not flags.get('--no-scan'):
        py('pivot-scan', CODE / 'scan_pivots.py', R, bindir / 'legality', out / 'scan', out / 'pivot-scan.json', stdout_to=out / 'logs/pivot-scan.txt')
        scan = read(out / 'pivot-scan.json'); expect('full', 'scan', [{kk: r_[kk] for kk in ('case', 'pivots', 'entrance_rank', 'status', 'c', 'local_profile', 'widths')} for r_ in scan])
    integrity()
    bit_receipt = dict(status='PASS_R715_KERNEL_CAP_BIT', mode='full', kappa_with_pr442_complex=res['kappa'], bit_lower=res['bit_lower'], binding_component=res['binding_component'],
                       manifest_sha256=sha(ROOT / 'MANIFEST.json'), source_sha256=sha(ROOT / 'SOURCE.json'), compiler=compiler, python=sys.version.split()[0], checks=steps)
    (out / 'BIT-RECEIPT.json').write_text(json.dumps(bit_receipt, indent=2) + '\n')
    # ---------------- PR #458's complex supplier and the exact composition
    if flags.get('--complex-output'): cxo = Path(flags['--complex-output']).resolve()
    else:
        cxo = out / 'complex458'; py('full-complex458', R / 'e8-complex-adapted-kernel/verify.py', cxo)
    py('exact-composition', ROOT / 'compose.py', out / 'RESULT.json', '--research-root', R, '--complex-output', cxo, '--bit-output', out)
    result = read(out / 'RESULT.json'); assert result['mode'] == 'FRESH_FULL_SUPPLIERS'
    expect('full', 'composition', {kk: result[kk] for kk in ('kappa', 'kappa_decimal', 'bit_lower', 'complex_lower', 'binding_component', 'row_allowance', 'charged_coefficient_bits', 'outer_controls')})
    receipt = dict(status='PASS_FULL_R715_KERNEL_CAP', python=sys.version.split()[0], kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
                   gain_over_pr463_percent=result['gain_over_pr463_percent'], gain_over_pr472_percent_quoted=result['gain_over_pr472_percent_quoted'],
                   manifest_sha256=sha(ROOT / 'MANIFEST.json'), source_sha256=sha(ROOT / 'SOURCE.json'), steps=steps)
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    if RECORD: (out / 'EXPECTED.recorded.json').write_text(json.dumps(rec, indent=2, sort_keys=True) + '\n')
    print(json.dumps({kk: receipt[kk] for kk in ('status', 'kappa', 'kappa_decimal', 'gain_over_pr463_percent', 'gain_over_pr472_percent_quoted')}, indent=2))
except BaseException as e:
    if isinstance(e, SystemExit) and e.code in (0, None): raise      # LIGHT's clean sys.exit(0) is a pass, not a failure
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
