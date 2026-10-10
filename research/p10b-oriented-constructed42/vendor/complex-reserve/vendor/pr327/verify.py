#!/usr/bin/env python3
"""The complex supplier at cube size p = 10 (h = 20), as explicit numbered programs (gcert/1). No new κ.

PR #304 compiled the source-assisted complex word of PR #184 / #194 at p = 11 (h = 22) on re-annealed query modules.
This package compiles the same word at p = 10 (h = 20, v = 960 ports) with the same frozen recipe, on modules cut
from p = 11 module files by zero restriction and then re-annealed at p = 10 (modules/), in three module sets:
  pr168-v4-cut  the control: PR #168 v4's three modules cut to p = 10 (re-derived here from the rebuilt tree);
  anneal        the result with PR #304's recipe: annealed triple, pair and all-but-one modules;
  centre        the centre-sharing variant: the same triple and all-but-one modules, and a pair module whose 37th
                root (the sum of all its inputs) is the star centre (centre46.py, the effect of PR #315's
                10-line Graph.finish patch, which this script re-applies and compares);
and two pair recipes each (PR #193's parity-avoiding pairs, PR #233's maximum-weight pairs). Each of the six words is
lowered to Jacob Sussman's gcert/1 by PR #256's emitter and checked by his reference checker gx.check1 and his gxcore
mirror (both vendored unchanged).

This script (Python 3.11+; numpy/scipy for the pinned regeneration and the checkers; -O refused)
  1. checks every pin of SOURCE.json;
  2. rebuilds the 308 pinned files of PR #202 from the vendored PR #233 package and regenerates the PR #168 v4
     producer word and the source-aligned word at p = 11 (PR #194's pipeline, as PR #304's verify.py does);
  3. anchors: (a) aligned_word_p.py at its default p = 11, given PR #168 v4's modules and the source-aligned word's
     own arcs, frames and pairs, reproduces the seven output files of source_aligned_local_v4.py byte for byte;
     (b) with PR #194's frozen pairs the chain of step 4 reproduces PR #256's certificate of PR #194's word and
     Sussman's block histogram of #193; (c) the control modules are the fewest-additions zero restrictions of PR
     #168 v4's module files in the rebuilt tree, byte for byte (module_cut.py); (d) PR #315's Graph.finish patch
     (references/centre46_graph.diff), applied to the rebuilt tree's graph.py, builds the same graph as
     centre46.finish_centre46 on the centre modules (every field but the status string) and leaves the graph of a
     36-root pair module unchanged;
  4. for each module set and pair recipe: installs the module files, builds the word on the frozen layer with
     aligned_word_p.py --p 10 (arcs through compile_closure, frames through the script's forward closure, pairs
     through the script's candidate rule, exact physical checks), re-checks the pairs with paircheck.py (five mutation
     controls), admits the layer with PR #200's complete complex checker after recomputing PR #168's physical()
     profile in-process, runs PR #184's frame flow with the frozen kernel pairs, the exact lift and PR #194's contract,
     emits gcert/1 with gcert_emit.py, runs gx.check1 (labels, blocks, N, exact scalar identity) and Sussman's gxcore
     mirror on the emitted program, checks the ledger 3 (x + y + s + c) + 2v e_2 = the flow's child histogram, writes
     the star scatter with normalize_scatter.py and runs gx.check1 and gxcore again on that program, rejects a
     flipped scalar sign in both checkers (E5), and prices the five-stage word at h = 20 with the GENERIC bridged
     layout H5 = 5 H_inv + 2v (e_{2h-2} + e_{h-1} + e_{2h+2} + e_4) = 5 H_inv + 2v (e38 + e19 + e42 + e4), m = 5h = 100,
     W = 4v + R, deficit 4v - 5 cst = 2040: the claim of SOURCE.json on the 10^-7 grid with PR #225's exact upper
     bound (PR #304's convention) and with the 10^-16 fallback envelope added, the next 10^-7 grid point rejected by
     an exact lower bound; and the coarse saving on the 10^-18 grid with the fallback by the two rational engines of
     the five-stage packages (source527 moment.py and base_two_moment.py), the next 10^-18 point rejected;
  5. compares the six committed (star-form) programs byte for byte (uncompressed JSON) with certificates/, and the
     run with certificate/expected.json.
The bridged layout at h = 20 is the generic formula: PR #304's price (and Sussman's Lean build of #193) used it at
h = 22 only. Sussman's Lean theorem bridge2_gcert is stated for every h, but no h = 20 program is kernel-checked here.
usage: python3 -B research/complex-p10/verify.py [--write] [--temp-root DIR]
--write re-pins the package's own inputs (modules/, layers/) in SOURCE.json, sets each claim to the largest 10^-7 grid
point the exact bounds certify, and rewrites certificates/ and certificate/expected.json (see README, re-pinning).
Prepared by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0), from PR #304's verify.py.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from fractions import Fraction as Q
from math import comb
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'gx'))
sys.path.insert(0, str(HERE / 'scripts'))
sys.path.insert(0, str(HERE))
import gx                      # noqa: E402  (Jacob Sussman's reference checker, unchanged)
import gxcore                  # noqa: E402  (Jacob Sussman's Python mirror of the two Lean checks, unchanged)
import normalize_scatter       # noqa: E402
import module_cut              # noqa: E402
from moment import moment_margin  # noqa: E402  (PR #225's exact upper bound, as PR #304 prices)
T0 = time.monotonic()
P = 10
SETS = ('pr168-v4-cut', 'anneal', 'centre')
RECIPES = ('parity', 'mw')
OWN = ('modules/', 'layers/')          # package inputs that --write re-pins; every other pin is vendored and fixed
SEVEN = ('cache/graph.json', 'cache/frames.json', 'cache/selection.json', 'cache/record.json',
         'references/paired-cube/physical/frames.json', 'references/paired-cube/physical/pairs.json',
         'certificates/paired-cube-sinks-input.json')
PR168 = dict(tmod='tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json', pmod='pmod_J0_full_6.0666810e-4.json',
             qmod='qmod_climb3u_best.json')
NAMES = {'pr168-v4-cut': 'PR168 v4 modules cut to p = 10', 'anneal': 'annealed p = 10 modules',
         'centre': 'annealed p = 10 modules, centre-sharing pair module',
         'parity': 'PR193 parity-avoiding pairs', 'mw': 'PR233 maximum-weight pairs'}
GRID7, GRID18, FALLBACK_WEIGHT = Q(1, 10**7), Q(1, 10**18), Q(1, 10**16)


def log(msg):
    print('[%6.1fs] %s' % (time.monotonic() - T0, msg), flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(p):
    p = Path(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


def write_gz(p, data):
    with open(p, 'wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as f:
        f.write((json.dumps(data, separators=(',', ':')) + '\n').encode())


def run(root, *args):
    r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: ' + ' '.join(map(str, args)) + '\n' + r.stdout[-3000:] + r.stderr[-3000:])
    return r.stdout


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S527 = load_module('source527_moment', HERE / 'scripts/source527/moment.py')          # eumemic, unchanged
B2M = load_module('source527_base_two_moment', HERE / 'scripts/source527/base_two_moment.py')   # unchanged


def canonical(cert):
    return (json.dumps(cert, separators=(',', ':'), sort_keys=True) + '\n').encode()


def grid(a):
    return '%d/10^7' % (a * 10**7)


def grid18(a):
    return '%d/10^18' % (a * 10**18)


def parse_grid(s):
    num, den = s.split('/')
    assert den == '10^7'
    return Q(int(num), 10**7)


def idle_ranks(h):
    """the idle climbs of Sussman's bridged word B_2 per port: 2 blocks each of rank 2h-2, h-1, 2h+2, 4 (his
    tools/gx/gxunit.py, BANK['B2']); at h = 22 these are PR #304's literals (42, 21, 46, 4)"""
    return (2 * h - 2, h - 1, 2 * h + 2, 4)


def five_stage(blocks, v, h, R):
    """Sussman's bridged five-stage word on one invocation ledger H_inv (the gcert block histogram over all
    classes): per cover vertex H5 = 5 H_inv + 2v (e_{2h-2} + e_{h-1} + e_{2h+2} + e_4), width m = 5h, stock W = 4v + R."""
    Hinv = Counter()
    for w in blocks.values():
        for r, n in w.items():
            Hinv[int(r)] += n
    H5 = {r: 5 * n for r, n in Hinv.items()}
    for r in idle_ranks(h):
        H5[r] = H5.get(r, 0) + 2 * v
    return 5 * h, 4 * v + R, H5


def certify(name, cert, v, h, expected_blocks=None):
    st = {}
    gx.check1(cert, scalar=True, stats=st)
    if expected_blocks is not None:
        assert cert['blocks'] == expected_blocks, '%s: block histogram differs from the expectation' % name
    R, N, cst = cert['R'], cert['N'], cert['cst']
    assert N == R * h + 2 * v * (h - 1) + cst and not cert['ext']
    m, W, H5 = five_stage(cert['blocks'], v, h, R)
    rank = sum(r * n for r, n in H5.items())
    assert W * m - rank == 4 * v - 5 * cst, '%s: five-stage deficit is not 4v - 5 cst' % name
    return dict(R=R, N=N, cst=cst, gates_A=len(cert['A']), gates_B=len(cert['B']), frames=len(cert['frames']),
                registers=2 * v + R, blocks_total=sum(sum(w.values()) for w in cert['blocks'].values()),
                scalar_denominators=st['den'], scalar_max_abs=st['maxabs'], distinct_frame_steps=st['steps'],
                five_stage=dict(h=h, m=m, W=W, idle_ranks=list(idle_ranks(h)), rank=rank, deficit=W * m - rank,
                                child_histogram={str(r): n for r, n in sorted(H5.items())}))


def best_claim(five):
    """the largest 10^-7 grid point at which the exact moment bound is below W (used by --write only)"""
    hist = {int(r): n for r, n in five['child_histogram'].items()}
    m, W = five['m'], five['W']
    lo, hi = 0., .01
    for _ in range(80):
        a = (lo + hi) / 2
        if math.fsum(n * r * math.exp(a * math.log(m / r)) for r, n in hist.items()) < m * W:
            lo = a
        else:
            hi = a
    k = int(lo * 10**7)
    while moment_margin(m, W, hist, Q(k, 10**7))[0] <= 0:
        k -= 1
    while moment_margin(m, W, hist, Q(k + 1, 10**7))[0] > 0:
        k += 1
    return Q(k, 10**7)


def price(name, five, a):
    """the 10^-7 claim: PR #225's exact upper bound below W at a, without (PR #304's convention) and with the 10^-16
    fallback envelope of the five-stage packages (32 m^2 rank-one calls per paid child, weight 10^-16); the next grid
    point fails PR #225's upper bound and is rejected by source527's exact LOWER bound even without the fallback."""
    hist = {int(r): n for r, n in five['child_histogram'].items()}
    m, W = five['m'], five['W']
    margin, total = moment_margin(m, W, hist, a)
    assert margin > 0, '%s: five-stage moment not below W at a = %s' % (name, grid(a))
    calls = sum(hist.values())
    with_fallback = dict(hist)
    with_fallback[1] = with_fallback.get(1, 0) + Q(32 * m * m * calls) * FALLBACK_WEIGHT
    margin_fb, total_fb = moment_margin(m, W, with_fallback, a)
    assert margin_fb > 0, '%s: five-stage moment with the 10^-16 fallback not below W at a = %s' % (name, grid(a))
    nxt = a + GRID7
    margin_next, _ = moment_margin(m, W, hist, nxt)
    assert margin_next <= 0, '%s: the next grid point %s also passes; raise the claim' % (name, grid(nxt))
    lower_next, _ = S527.moment(hist, m, W, nxt, False)
    assert lower_next > 1, '%s: the next grid point %s is not excluded by an exact lower bound' % (name, grid(nxt))
    scale = 10**30
    up = lambda t: -((-t.numerator * scale) // t.denominator)
    return dict(a=grid(a), moment_upper_bound='%d/10^30' % up(total), margin_lower_bound='%d/10^30' % (W * scale - up(total)),
                with_fallback=dict(moment_upper_bound='%d/10^30' % up(total_fb), margin_lower_bound='%d/10^30' % (W * scale - up(total_fb)),
                                   fallback_rank_one_calls='32 m^2 x %d x 10^-16' % calls),
                next_grid_point=grid(nxt), next_grid_point_rejected=True,
                next_grid_point_normalized_moment_lower_bound=str(lower_next))


def coarse(name, five, a):
    """the coarse saving b as the five-stage packages certify a complex supplier (PR #315's math_check): the largest
    10^-18 grid point at which the normalized moment WITH the 10^-16 fallback envelope is below 1, by both exact
    engines (source527 moment.py and base_two_moment.py), the next 10^-18 point excluded by both; the root without
    the fallback (PR #304's convention) is certified the same way and recorded."""
    H = {int(r): n for r, n in five['child_histogram'].items()}
    m, W = five['m'], five['W']
    fallback = 32 * m * m * sum(H.values())
    out = {}
    for label, bad in (('with_fallback', True), ('without_fallback', False)):
        root = S527.certify(H, m, W, bad)
        b = Q(int(Q(root['lower']) * 10**18), 10**18)
        cm = S527.moment(H, m, W, b, bad)
        nextcm = S527.moment(H, m, W, b + GRID18, bad)
        assert cm[1] < 1 < nextcm[0], '%s: coarse %s not certified by moment.py' % (name, label)
        _, upper = B2M.moment(m, W, list(H.items()), b)
        lower, _ = B2M.moment(m, W, list(H.items()), b + GRID18)
        if bad:
            _, badupper = B2M.moment(m, W, [(1, fallback)], b)
            badlower, _ = B2M.moment(m, W, [(1, fallback)], b + GRID18)
            upper, lower = upper + FALLBACK_WEIGHT * badupper, lower + FALLBACK_WEIGHT * badlower
        assert upper < 1 < lower, '%s: coarse %s not certified by base_two_moment.py' % (name, label)
        out[label] = dict(b=grid18(b), b_decimal=S527.decimal(b), moment_interval=[str(cm[0]), str(cm[1])],
                          next_grid_point=grid18(b + GRID18), next_moment_lower_bound=str(nextcm[0]),
                          base_two_upper=str(upper), base_two_next_lower=str(lower))
    b = Q(out['with_fallback']['b'].split('/')[0]) / 10**18
    b0 = Q(out['without_fallback']['b'].split('/')[0]) / 10**18
    assert a <= b < b0 < a + GRID7, '%s: the coarse savings do not bracket the 10^-7 claim' % name
    out['fallback_cost'] = grid18(b0 - b)
    out['scope'] = ('10^-16 and 32 m^2 rank-one fallback calls per paid child are the five-stage packages\' inherited '
                    'envelope, applied here at m = 5h = 100; not a new m = 5h admission')
    return out


def admit(root, tree, cand):
    """PR #233's step 3: admit the word's physical layer with PR #200's complete complex checker."""
    from paired_cube.closure import compile_closure            # noqa: E402  (the rebuilt tree's scripts/)
    from paired_cube_physical import physical                  # noqa: E402
    cache = tree / 'cache'
    g, w, word, row = (read(cache / n) for n in ('graph.json', 'frames.json', 'selection.json', 'record.json'))
    frames = read(tree / 'references/paired-cube/physical/frames.json')['frames']
    pairs = read(tree / 'references/paired-cube/physical/pairs.json')['pairs']
    baseline, _ = compile_closure(g, [[x, c] for x, c in w['matching_arcs']])
    profile = physical(g, w, word, row, frames, pairs)
    assert json.loads(json.dumps(profile)) == read(tree / 'certificates/paired-cube-sinks-input.json'), 'physical profile differs from the sinks certificate'
    cand.mkdir()
    for name, data in [('graph', g), ('baseline', baseline), ('frames', w), ('word', word), ('profile-before', row),
                       ('physical-frames', frames), ('physical-pairs', pairs), ('profile', profile)]:
        write_gz(cand / (name + '.json.gz'), data)
    pins = {p.name: sha(p.read_bytes()) for p in cand.glob('*.json.gz')}
    (cand / 'result.json').write_text(json.dumps(dict(tag='complex-p10', pins=pins)) + '\n')
    out = cand.with_suffix('.audit.json')
    run(root, root / 'research/paired-cube-diagonal-bit-168/complex/physical.py', '--candidate', cand, '--source', root, '--out', out)
    audit = read(out)
    assert audit['status'].startswith('PASS'), audit['status']
    # the checker keys its source hashes by absolute path; record them relative to the rebuilt tree
    return dict(status=audit['status'], formal=json.loads(json.dumps(audit.get('formal'))), mutations=audit.get('mutations'),
                source_sha256={Path(k).resolve().relative_to(root).as_posix(): x for k, x in audit['source_sha256'].items()})


def flip_one_sign(cert):
    """negate the first coefficient of the first phase-A add gate with a coefficient list (PR #315's control)"""
    gate = next(g for g in cert['A'] if g[0] in ('out', 'in') and g[3])
    t, a, b = gate[3][0]
    gate[3][0] = [t, -a, b]
    return cert


def mirror(name, cert, hinv):
    m = gxcore.mirror(gxcore.normal(copy.deepcopy(cert)))
    assert m['hist'] == dict(hinv), '%s: gxcore histogram differs from the blocks' % name


def controls(name, cert):
    """a flipped scalar sign must be rejected by gx.check1 and by the gxcore mirror on the scalar identity (E5)"""
    out = []
    try:
        gx.check1(flip_one_sign(copy.deepcopy(cert)), scalar=True)
    except AssertionError as error:
        assert str(error).startswith('E5'), ('%s: flipped sign rejected for the wrong reason' % name, str(error))
        out.append('gx.check1: REJECTED (%s)' % str(error)[:2])
    else:
        raise AssertionError('%s: gx.check1 accepted a flipped scalar sign' % name)
    try:
        gxcore.mirror(gxcore.normal(flip_one_sign(copy.deepcopy(cert))))
    except gxcore.Reject as error:
        assert str(error).startswith('E5'), ('%s: flipped sign rejected for the wrong reason' % name, str(error))
        out.append('gxcore.mirror: REJECTED (%s)' % str(error)[:2])
    else:
        raise AssertionError('%s: gxcore mirror accepted a flipped scalar sign' % name)
    return dict(flipped_scalar_sign=out)


def chain(root, work, name, tree, kernel, title, contract=True, admission=True, p=P):
    """flow, exact lift, contract, gcert/1 emission, gx.check1 and gxcore on one aligned tree"""
    PKG, SA = root / 'research/source-assisted-v4', root / 'research/source-assisted'
    cache = tree / 'cache'
    g = read(cache / 'graph.json')
    v, h = g['v'], g['h']
    assert (g['p'], h, v) == (p, 2 * p, 8 * comb(p, 3)), '%s: not a p = %d graph' % (name, p)
    rec = {}
    if admission:
        rec['admission'] = admit(root, tree, work / (name + '.candidate'))
        log('%s: PR #168\'s physical() profile recomputed; layer admitted by PR #200\'s complex checker: %s'
            % (name, rec['admission']['status'][:60]))
    flow = work / (name + '.flow.json')
    run(root, SA / 'decision/complex_frame_flow.py', '--tree', tree, '--cache', cache, '--out', flow, '--witness',
        '--purify-source-donors', '--recycle-kernels', '--kernel-pairs', kernel)
    witness = flow.with_suffix('.witness.json')
    fd = read(flow)
    lift = work / (name + '.lift.json')
    run(root, SA / 'decision/exact_complex_flow_lift.py', '--witness', witness, '--profile', flow, '--out', lift)
    lift_data = read(lift)
    log('%s: flow new_R %d, deficit %d, numerical three-stage root %.7e; lift: %s' % (
        name, fd['new_R'], fd['deficit'], fd['numerical_local_root'], lift_data['status'][:60]))
    rec['flow'] = dict(new_R=fd['new_R'], new_W=fd['new_W'], deficit=fd['deficit'], loss=fd['loss'], kernel_reuses=fd['kernel_reuses'],
                       source_control_erasures=fd['source_control_erasures'], original_physical_roles=fd['original_physical_roles'],
                       child_histogram=fd['child_histogram'])
    rec['lift'] = {k: lift_data[k] for k in ('status', 'nodes', 'physical_R', 'inverse_elementary_gates', 'all_actual_coefficients_dyadic', 'max_denominator')}
    if contract:
        # PR #233's step 4: the contract reads the frozen pairs and kernel pairs from the v4 package's data/
        (PKG / 'data/physical-pairs.json').write_bytes((tree / 'references/paired-cube/physical/pairs.json').read_bytes())
        shutil.copyfile(kernel, PKG / 'data/kernel-pairs.json')
        cprof = work / (name + '.complex-profile.json')
        run(root, PKG / 'contract_v4.py', '--tree', tree, '--cache', cache, '--witness', witness, '--flow-profile', flow,
            '--lift-profile', lift, '--out', cprof)
        cdata = read(cprof)
        for k, check in cdata['contract_checks'].items():
            assert check not in (False, 'FAIL'), '%s: contract check %s failed' % (name, k)
        assert cdata['physical_R'] == fd['new_R'] and cdata['child_histogram'] == fd['child_histogram']
        rec['contract_checks'] = cdata['contract_checks']
        log('%s: PR #194 contract: %d checks pass' % (name, len(cdata['contract_checks'])))
    out = work / ('gcert1-p%d-%s-flow.json' % (p, name))
    run(root, HERE / 'gcert_emit.py', '--cache', cache, '--flow', flow, '--witness', witness, '--lift', lift_data['certificate_path'],
        '--out', out, '--name', title)
    raw = read(out)
    rec.update(certify(name, raw, v, h))
    Hinv = Counter()
    for w in raw['blocks'].values():
        for r, n in w.items():
            Hinv[int(r)] += n
    mirror(name, raw, Hinv)
    log('%s: emitted program: gx.check1 ACCEPTED (labels, blocks, N = %d, exact scalar identity) and gxcore mirror ACCEPTED; %d gates, %d registers'
        % (name, rec['N'], rec['gates_A'] + rec['gates_B'], rec['registers']))
    # the gcert ledger is the flow's certified child histogram: 3 (x + y + s + c) + 2v e_2
    child = Counter({r: 3 * n for r, n in Hinv.items()})
    child[2] += 2 * v
    assert {int(r): n for r, n in fd['child_histogram'].items()} == dict(child), '%s: ledger differs from the flow profile' % name
    # the committed program: the scatter as the star rule (normalize_scatter.py), checked again by gx.check1 and by
    # Sussman's gxcore mirror; registers, frames, gates, labels, retained totals, blocks and N are unchanged
    cert, norm = normalize_scatter.normalize(raw)
    st = {}
    gx.check1(cert, scalar=True, stats=st)
    assert cert['scat'] == normalize_scatter.STAR and normalize_scatter.same_shape(raw, cert), '%s: normalization changed more than signs' % name
    assert (cert['blocks'], cert['N'], cert['frames'], len(cert['A']), len(cert['B'])) == (raw['blocks'], raw['N'], raw['frames'], len(raw['A']), len(raw['B']))
    assert (st['den'], st['maxabs'], st['steps']) == (rec['scalar_denominators'], rec['scalar_max_abs'], rec['distinct_frame_steps'])
    mirror(name, cert, Hinv)
    rec['controls'] = controls(name, cert)
    norm.update(raw_certificate_sha256=sha(canonical(raw)), gx_check1='ACCEPTED (raw and committed program)',
                gxcore_mirror='ACCEPTED (raw and committed program; label and scalar checks)')
    rec['scatter'] = norm
    log('%s: committed program in star form (%s): gx.check1 and gxcore ACCEPTED, blocks and N unchanged; flipped sign rejected by both (E5)'
        % (name, 'registers %s re-signed, %d coefficients' % (norm['flipped_registers'], norm['changed_coefficients'])
           if norm['flipped_registers'] else 'emitted in star form, normalization not needed'))
    rec['blocks'] = cert['blocks']
    rec['certificate_sha256'] = sha(canonical(cert))
    return rec, cert


def module_paths(src, root, name):
    paths = {}
    for kind, rel in src['module_sets'][name].items():
        if kind == 'centre46':
            continue
        # install the package's module file next to PR #168 v4's in the rebuilt tree
        dest = root / 'references/paired-cube/sources' / Path(rel).name
        if dest.exists():
            assert dest.read_bytes() == (HERE / rel).read_bytes(), 'module file name collides with a different tree file: ' + rel
        else:
            shutil.copyfile(HERE / rel, dest)
        paths[kind] = dest
    return paths


def module_record(path, kind, centre):
    """the module's contract (the rebuilt tree's loaders; centre46.load_pmod46 for the 37-root pair module), its
    additions and outputs"""
    from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from  # noqa: E402
    from centre46 import load_pmod46                                                        # noqa: E402
    if kind == 'tmod':
        triple_module_from(path, P)
    elif kind == 'pmod':
        (load_pmod46 if centre else pair_module_from)(path, P - 1)
    else:
        all_but_one_from(path, P - 2)
    d = read(path)
    outputs = {'tmod': comb(P, 3), 'pmod': comb(P - 1, 2) + (1 if centre else 0), 'qmod': P - 2}[kind]
    assert len(d['roots']) == outputs, (path, len(d['roots']))
    return dict(sha256=sha(Path(path).read_bytes()), additions=module_cut.additions(d), outputs=outputs)


def apply_diff(text, diff):
    """apply a unified diff (exact context, every hunk once) to text"""
    lines = text.split('\n')
    hunks, cur = [], None
    for ln in diff.split('\n'):
        if ln.startswith('@@'):
            cur = ([], [])
            hunks.append(cur)
        elif cur is not None and ln[:1] in (' ', '-', '+'):
            if ln[0] in ' -':
                cur[0].append(ln[1:])
            if ln[0] in ' +':
                cur[1].append(ln[1:])
    for old, new in hunks:
        hits = [i for i in range(len(lines)) if lines[i:i + len(old)] == old]
        assert len(hits) == 1, 'patch hunk does not apply exactly once'
        lines[hits[0]:hits[0] + len(old)] = new
    return '\n'.join(lines), len(hunks)


def centre_anchor(root, src):
    """PR #315's Graph.finish patch applied to the rebuilt graph.py builds centre46.finish_centre46's graph"""
    graph_py = root / 'scripts/paired_cube/graph.py'
    diff = (HERE / 'references/centre46_graph.diff').read_text()
    patched, hunks = apply_diff(graph_py.read_text(), diff)
    (root / 'scripts/paired_cube/graph_centre46_patch.py').write_text(patched)
    import paired_cube.graph as G0                                                  # noqa: E402
    import paired_cube.graph_centre46_patch as G1                                   # noqa: E402
    (root / 'scripts/paired_cube/graph_centre46_patch.py').unlink()                # leave the rebuilt tree as pinned
    from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from  # noqa: E402
    from centre46 import load_pmod46, finish_centre46                               # noqa: E402
    local = json.loads((root / 'references/paired-cube/sources/local_L1.json').read_text())
    local['G'] = {k: 's' for k in local['G']}
    local['A'] = {k: 'fd' for k in local['A']}
    mods = {k: HERE / src['module_sets']['centre'][k] for k in ('tmod', 'pmod', 'qmod')}
    t, q = triple_module_from(mods['tmod'], P), all_but_one_from(mods['qmod'], P - 2)
    pm46 = load_pmod46(mods['pmod'], P - 1)
    a = finish_centre46(G0.Graph(P, local=copy.deepcopy(local)), t, pm46, q)
    b = G1.Graph(P, local=copy.deepcopy(local)).finish(t, pm46, q)
    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    assert differ == ['status'], 'centre46.py and the patched Graph.finish differ in %s' % differ
    # with a 36-root pair module the patch changes nothing
    pm = pair_module_from(HERE / src['module_sets']['anneal']['pmod'], P - 1)
    ta = triple_module_from(HERE / src['module_sets']['anneal']['tmod'], P)
    c = G0.Graph(P, local=copy.deepcopy(local)).finish(ta, pm, q)
    d = G1.Graph(P, local=copy.deepcopy(local)).finish(ta, pm, q)
    assert c == d, 'the patch changes the graph of an ordinary pair module'
    return dict(patch_sha256=sha(diff.encode()), hunks=hunks, centres_from_pair_module=len(a['centers']),
                fields_compared=len(a), differing_fields=differ, center_additions=a['counts']['center_additions'],
                ordinary_pair_module_unchanged=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='re-pin modules/ and layers/, set the claims, rewrite certificates/ and certificate/expected.json')
    ap.add_argument('--temp-root', type=Path, default=None)
    a = ap.parse_args()
    src = read(HERE / 'SOURCE.json')
    if a.write:
        own = sorted(p.relative_to(HERE).as_posix() for d in OWN for p in (HERE / d).rglob('*') if p.is_file())
        files = {k: x for k, x in src['files'].items() if not k.startswith(OWN)}
        files.update({k: sha((HERE / k).read_bytes()) for k in own})
        changed = sorted(k for k in set(files) | set(src['files']) if files.get(k) != src['files'].get(k))
        src['files'] = dict(sorted(files.items()))
        log('--write: re-pinned %d package inputs (%d changed: %s)' % (len(own), len(changed), ', '.join(changed) or 'none'))
    for rel, digest in src['files'].items():
        assert sha((HERE / rel).read_bytes()) == digest, 'pinned file differs from SOURCE.json: ' + rel
    for name in SETS:
        for kind, rel in src['module_sets'][name].items():
            assert kind == 'centre46' or rel in src['files'], 'module file not pinned: ' + rel
        for part in ['matching-arcs', 'physical-frames'] + ['%s-%s' % (k, r) for k in ('physical-pairs', 'kernel-pairs') for r in RECIPES]:
            assert 'layers/%s/%s.json' % (name, part) in src['files'], 'layer file not pinned: %s/%s' % (name, part)
    log('checked %d pins of SOURCE.json' % len(src['files']))
    sussman = read(HERE / 'references/sussman/pr193-blocks.json')
    layer = load_module('pr233_layer_verify', HERE / 'references/pr233-layer/verify.py')
    emitted, result = {}, {}
    with tempfile.TemporaryDirectory(prefix='complex-p10-', dir=a.temp_root) as d:
        root = Path(d).resolve()
        pins = layer.rebuild(root)
        log('rebuilt %d pinned files of PR #202 (commit %s) from the vendored PR #233 package' % (len(pins['files']), pins['commit'][:7]))
        sys.path.insert(0, str(root / 'scripts'))
        PKG = root / 'research/source-assisted-v4'
        work = root / '.work'
        work.mkdir()
        base, aligned = work / 'base', work / 'aligned'
        run(root, root / 'scripts/paired_cube_producer.py', '--work-dir', base, '--output', work / 'producer.json')
        run(root, PKG / 'source_aligned_local_v4.py', '--tree', root, '--cache', base, '--out', aligned)
        log('regenerated the PR #168 v4 producer word and the source-aligned word at p = 11 (PR #194\'s pipeline)')
        # 3. anchors
        src_dir = root / 'references/paired-cube/sources'
        pr168 = {k: src_dir / f for k, f in PR168.items()}
        mods = ['--tmod', pr168['tmod'], '--pmod', pr168['pmod'], '--qmod', pr168['qmod']]
        anchor = work / 'anchor'
        phys = aligned / 'references/paired-cube/physical'
        run(root, HERE / 'aligned_word_p.py', '--tree', root, *mods, '--arcs', aligned / 'cache/frames.json',
            '--frames', phys / 'frames.json', '--pairs', phys / 'pairs.json', '--out', anchor)
        for f in SEVEN:
            assert (anchor / f).read_bytes() == (aligned / f).read_bytes(), 'aligned_word_p.py differs from source_aligned_local_v4.py: ' + f
        log('anchor (a): aligned_word_p.py at p = 11 reproduces the 7 output files of source_aligned_local_v4.py byte for byte')
        tree = work / 'pr194'
        run(root, HERE / 'aligned_word_p.py', '--tree', root, *mods, '--arcs', aligned / 'cache/frames.json',
            '--frames', phys / 'frames.json', '--pairs', PKG / 'data/physical-pairs.json', '--out', tree)
        rec, _ = chain(root, work, 'pr194', tree, PKG / 'data/kernel-pairs.json', 'pr194 flow word (PR168 frames, PR193 pairs)',
                       contract=False, admission=False, p=11)
        assert rec['blocks'] == sussman['blocks'] and rec['N'] == sussman['N'], 'pr194: not the histogram of Sussman\'s certificate of #193'
        assert rec['certificate_sha256'] == src['prerequisites']['pr256']['pr194_certificate_sha256'], 'pr194: differs from PR #256\'s certificate'
        assert rec['five_stage']['idle_ranks'] == [42, 21, 46, 4]
        result['anchor_pr194'] = dict(N=rec['N'], R=rec['R'], blocks_total=rec['blocks_total'], certificate_sha256=rec['certificate_sha256'],
                                      equals_pr256_certificate=True, equals_sussman_pr193_blocks=True,
                                      generic_idle_ranks_at_h22=rec['five_stage']['idle_ranks'])
        log('anchor (b): PR #194\'s word through this chain is PR #256\'s certificate (sha256 %s...) with Sussman\'s #193 histogram' % rec['certificate_sha256'][:12])
        cuts = {}
        for kind, n in (('tmod', P + 1), ('pmod', P), ('qmod', P - 1)):
            adds, drop, e = module_cut.min_cut(kind, read(pr168[kind]), n)
            assert module_cut.encode(e) == (HERE / src['module_sets']['pr168-v4-cut'][kind]).read_bytes(), \
                'control %s is not the fewest-additions cut of PR #168 v4\'s module' % kind
            cuts[kind] = dict(source=PR168[kind], dropped_point=list(drop), additions=adds)
        result['anchor_control_modules'] = cuts
        log('anchor (c): the control modules are the fewest-additions zero restrictions of PR #168 v4\'s modules (dropped points %s)'
            % {k: c['dropped_point'] for k, c in cuts.items()})
        result['anchor_centre_patch'] = centre_anchor(root, src)
        log('anchor (d): PR #315\'s Graph.finish patch builds centre46.py\'s graph (all %d fields but the status string); ordinary pair module unchanged'
            % (result['anchor_centre_patch']['fields_compared'] - 1))
        # 4. the six words
        modules = {}
        for name in SETS:
            centre = bool(src['module_sets'][name].get('centre46'))
            paths = module_paths(src, root, name)
            modules[name] = {kind: module_record(paths[kind], kind, centre) for kind in ('pmod', 'qmod', 'tmod')}
            L = HERE / 'layers' / name
            for recipe in RECIPES:
                key = '%s-%s' % (name, recipe)
                tree = work / key
                built = run(root, HERE / 'aligned_word_p.py', '--p', P, *(['--centre46'] if centre else []), '--tree', root,
                            '--tmod', paths['tmod'], '--pmod', paths['pmod'], '--qmod', paths['qmod'],
                            '--arcs', L / 'matching-arcs.json', '--frames', L / 'physical-frames.json',
                            '--pairs', L / ('physical-pairs-%s.json' % recipe), '--out', tree)
                dropped = [json.loads(x) for x in built.splitlines() if x.startswith('{')]
                dropped = next(x for x in dropped if x.get('stage') == 'physical')['dropped_gauges']
                # select() gauges that the script drops (rank != h - 4): only on the control's cut modules
                assert name == 'pr168-v4-cut' or not dropped, '%s: gauges dropped %s' % (key, dropped)
                sinks = read(tree / 'certificates/paired-cube-sinks-input.json')
                log('%s: word on the frozen layer (%d arcs, %d moved frames, %d pairs), physical checks pass, physical R %d'
                    % (key, len(read(L / 'matching-arcs.json')['matching_arcs']), len(read(L / 'physical-frames.json')['frames']),
                       len(read(L / ('physical-pairs-%s.json' % recipe))['pairs']), sinks['physical_R']))
                # independent re-check of the pairs from the written word, with five mutation controls
                pc = json.loads(run(root, HERE / 'paircheck.py', '--root', root, tree))
                assert pc['status'] == 'PASS' and not pc['violations'] and not pc['erasable'], '%s: paircheck %s' % (key, pc)
                assert all(x.startswith('REJECTED') for x in pc['controls'].values()), '%s: a paircheck control was not rejected: %s' % (key, pc['controls'])
                assert pc['controls']['donor_frame_outside_gauge'] == 'REJECTED (donor frame outside gauge)' and \
                    pc['controls']['parity_erasable_donor'] == 'REJECTED (erasable)', '%s: a paircheck control is not isolated: %s' % (key, pc['controls'])
                log('%s: paircheck PASS (%d early, %d late pairs, none parity-erasable); %d mutation controls rejected'
                    % (key, pc['early'], pc['late'], len(pc['controls'])))
                rec, cert = chain(root, work, key, tree, L / ('kernel-pairs-%s.json' % recipe),
                                  '%s flow word (p = 10, %s, descended frames, %s)' % (key, NAMES[name], NAMES[recipe]))
                assert rec['cst'] == 20 * 18 and rec['five_stage']['deficit'] == 4 * 960 - 5 * 360 == 2040
                rec['paircheck'] = pc
                rec['layer'] = dict(R=read(tree / 'cache/record.json')['R'], physical_R=sinks['physical_R'],
                                    arcs=len(read(L / 'matching-arcs.json')['matching_arcs']),
                                    moved_frames=len(read(L / 'physical-frames.json')['frames']),
                                    pairs=len(read(L / ('physical-pairs-%s.json' % recipe))['pairs']),
                                    kernel_pairs=len(read(L / ('kernel-pairs-%s.json' % recipe))['kernel_pairs']),
                                    gauges_dropped_by_the_script=dropped)
                five = rec['five_stage']
                claim = best_claim(five) if a.write else parse_grid(src['claims'][key])
                if a.write:
                    src['claims'][key] = grid(claim)
                five.update(price(key, five, claim))
                five['coarse'] = coarse(key, five, claim)
                log('%s: five-stage word at h = 20 (m = %d, W = %d, deficit %d) certified at a = %s with and without the 10^-16 fallback, %s rejected; coarse b = %s with the fallback (both engines)'
                    % (key, five['m'], five['W'], five['deficit'], five['a'], five['next_grid_point'], five['coarse']['with_fallback']['b']))
                result[key] = rec
                emitted[key] = cert
        log('regenerated the six certificates')
    for key, cert in emitted.items():
        path = HERE / 'certificates' / ('gcert1-p10-%s-flow.json.gz' % key)
        if a.write:
            with open(path, 'wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as f:
                f.write(canonical(cert))
        assert sha(gzip.decompress(path.read_bytes())) == result[key]['certificate_sha256'], '%s: committed certificate differs from the regenerated one' % key
    log('committed certificates reproduced byte for byte (uncompressed JSON)')
    claims = {k: parse_grid(src['claims'][k]) for k in emitted}
    comparison = {}
    for recipe in RECIPES:
        r = claims['pr168-v4-cut-' + recipe]
        for name in ('anneal', 'centre'):
            c = claims['%s-%s' % (name, recipe)]
            comparison['%s-%s' % (name, recipe)] = dict(result=grid(c), control=grid(r), gain_over_control=str(c / r - 1),
                                                       gain_over_control_percent='%.3f' % float(100 * (c / r - 1)))
    for k, (label, ref) in src['official'].items():
        for key in ('anneal-mw', 'centre-mw'):
            c = claims[key]
            comparison['%s_vs_%s' % (key, k)] = dict(official=label, gain=str(c / Q(ref) - 1), gain_percent='%.3f' % float(100 * (c / Q(ref) - 1)))
    canon = json.loads(json.dumps(dict(
        status='PASS: six flow words at p = 10 (h = 20) exported as gcert/1 programs accepted by gx.check1 and gxcore; five-stage '
               'saving (generic bridged layout at h = 20, with and without the 10^-16 fallback): centre-sharing %s, annealed %s '
               '(PR233 pairs; parity %s and %s), same-recipe control %s and %s'
               % (grid(claims['centre-mw']), grid(claims['anneal-mw']), grid(claims['centre-parity']), grid(claims['anneal-parity']),
                  grid(claims['pr168-v4-cut-mw']), grid(claims['pr168-v4-cut-parity'])),
        anchor_pr194=result['anchor_pr194'], anchor_control_modules=result['anchor_control_modules'],
        anchor_centre_patch=result['anchor_centre_patch'], comparison=comparison, modules=modules,
        **{k: result[k] for k in emitted},
        prerequisites=dict(pr202=pins['commit'], pr233=src['prerequisites']['pr233'], pr256=src['prerequisites']['pr256'],
                           pr304=src['prerequisites']['pr304'], pr315=src['prerequisites']['pr315'],
                           source527=src['prerequisites']['source527'], sussman=src['prerequisites']['sussman'])), sort_keys=True))
    if a.write:
        (HERE / 'SOURCE.json').write_text(json.dumps(src, indent=1) + '\n')
        (HERE / 'certificate/expected.json').write_text(json.dumps(canon, indent=1, sort_keys=True) + '\n')
        log('wrote SOURCE.json, certificates/ and certificate/expected.json')
    committed = read(HERE / 'certificate/expected.json')
    if committed != canon:
        for k in sorted(set(committed) | set(canon)):
            if committed.get(k) != canon.get(k):
                log('DIFFERS: %s' % k)
    assert committed == canon, 'result differs from certificate/expected.json'
    log('PASS expected.json reproduced: at p = 10 (h = 20, generic five-stage layout) centre-sharing %s and annealed %s (PR233 pairs; '
        'PR193 pairs %s and %s), control %s and %s'
        % (grid(claims['centre-mw']), grid(claims['anneal-mw']), grid(claims['centre-parity']), grid(claims['anneal-parity']),
           grid(claims['pr168-v4-cut-mw']), grid(claims['pr168-v4-cut-parity'])))


if __name__ == '__main__':
    main()
