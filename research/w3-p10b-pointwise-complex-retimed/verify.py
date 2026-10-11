#!/usr/bin/env python3
"""PR #346's w3 bit word with a per-point p = 10 complex supplier (7940/10^7): conditional κ = 793392809291691/10^18.

PR #346 (LJH-217) composes PR #310's w3 Design T and twin condensation on PR #325's p10b bit word (bit coarse
c = 32069035133443/(4·10^16) ≈ 8.01726e-4) with a p = 10 complex supplier of coarse saving
b = 396604388013523/(5·10^17) ≈ 7.93209e-4; the complex side binds, κ = 396290046684973/(5·10^17). This package keeps
PR #346's bit word (vendored) and replaces the complex supplier by a stronger p = 10 program of the same recipe
(PR #327's chain at 40ed045): PR #325's modules with a separate pair module for each point i (shared by both bits),
claim 7940/10^7, b = 794022782431403/10^18. The complex side still binds and κ rises to 793392809291691/10^18.

This script (Python 3.11+; numpy/scipy for the pinned regeneration and the checkers; -O refused)
  1. checks MANIFEST.json (every package file, nothing missing or extra) and SOURCE.json (sha256 and git blob id of
     every vendored file at its origin commit: PR #327 40ed045, PR #325 c4f1b74, PR #346 11b4de5, PR #329 c6b1a28);
  2. bit side (PR #346's word, not re-derived): decodes PR #346's final records (FINAL-RECORDS.bin.gz, hash pinned by
     its RECORD-SHA256SUMS), recounts the paid child histogram (MOVE and COPY ranks) independently, requires PR #346's
     normalized five-stage histogram to be 60·H + 12·2v·(e38 + e19 + e42 + e4), takes its normalized stock W = 125,712
     from PR #346's receipt, and certifies the bit coarse saving c with both rational engines and the 10^-16
     fallback (adjacent 10^-18 point excluded), equal to PR #346's;
  3. complex side: the committed program (canonical sha256 ff2d7307...): gx.check1 (labels, blocks, N, exact scalar
     identity), Sussman's gxcore mirror, a flipped scalar sign rejected by both (E5), the exact five-stage price at
     h = 20 (7940/10^7 with and without the fallback, 7941/10^7 rejected, coarse b by both engines);
  4. κ: the complex-bound outer assembly of PR #315 / PR #329 (the bit saving capped one grid point below the leaf
     cap (1 - β) b, β = 10^-9; three bootstrap steps from 384599/10^10; η = 10^-12; κ the last 10^-18 grid point below
     the minimum margin; PR #315's outer.assembly with its 47 strict constraints and the finite bridge; the adjacent
     κ and the cap itself rejected). It first reproduces PR #346's κ exactly from PR #346's b, then computes κ with
     this package's b;
  5. (full run, not --quick) regenerates the complex program: rebuilds PR #202's 308 files from the vendored PR #233
     package, PR #327's anchors (a) and (b), anchors (d) and (e) on the one-module-per-kind spec (e: spec_graph.
     finish_spec = centre46.finish_centre46 in every field), a builder anchor (f): on that spec's frozen layer
     (layers/uniform/, the Lean-checked 7932/10^7 companion), aligned_word_spec.py --spec writes the same seven files
     as PR #327's aligned_word_p.py --centre46; then builds the per-point word with aligned_word_spec.py --spec
     spec/c2.json on the frozen layer,
     paircheck.py, PR #200's checker, PR #184's flow and exact lift, PR #194's contract, PR #256's emitter, gx.check1
     and gxcore, and requires the committed program byte for byte;
  6. compares the run with certificate/expected.json (--quick: without the regeneration entries).
The 7940/10^7 program has NOT been built in Lean (the Lean host was unavailable); the companion 7932/10^7 program of
the same recipe with one pair module (spec/uniform.json; PR #346's supplier has the same b) was built in Lean.
usage: python3 -B research/w3-p10b-pointwise-complex/verify.py [--quick] [--write] [--temp-root DIR]
--write rewrites certificate/expected.json and then MANIFEST.json; it never rewrites the program, modules, layer or
bit data (a different regenerated program is an error).
Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance (Apache-2.0), from PR #327's verify.py
(DreamingOfClouds with Anthropic Claude assistance) and PR #329's math_check.py.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import shutil
import struct
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
import spec_graph              # noqa: E402
from moment import moment_margin  # noqa: E402  (PR #225's exact upper bound, as PR #304 and #327 price)
T0 = time.monotonic()
P = 10
BASE_PROGRAM_SHA256 = 'ff2d7307b09aceb8776654f21099b10a68be547b562b7f4a7fc918f6c5f51112'   # PR #348's program (regenerated)
PROGRAM_SHA256 = 'ff0fd6786550a9afeae762431fd2c95bd5f2a0e8ffe162e9bc6ef8581172f037'   # committed: PR #348's program after retime/retime_gcert.py
SEVEN = ('cache/graph.json', 'cache/frames.json', 'cache/selection.json', 'cache/record.json',
         'references/paired-cube/physical/frames.json', 'references/paired-cube/physical/pairs.json',
         'certificates/paired-cube-sinks-input.json')
PR168 = dict(tmod='tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json', pmod='pmod_J0_full_6.0666810e-4.json',
             qmod='qmod_climb3u_best.json')
GRID7, GRID18, FALLBACK_WEIGHT = Q(1, 10**7), Q(1, 10**18), Q(1, 10**16)
SKIP = ('__pycache__',)


def log(msg):
    print('[%6.1fs] %s' % (time.monotonic() - T0, msg), flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


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


# ---------------------------------------------------------------------------------------------------- 1. pins
def package_files():
    return sorted(p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
                  if p.is_file() and not any(part in SKIP for part in p.relative_to(HERE).parts))


def manifest(write=False):
    files = {rel: sha((HERE / rel).read_bytes()) for rel in package_files() if rel != 'MANIFEST.json'}
    for rel in files:
        data = (HERE / rel).read_bytes()
        assert b'\r\n' not in data or rel.endswith('.gz'), 'CRLF line ending in ' + rel
    if write:
        (HERE / 'MANIFEST.json').write_text(json.dumps(dict(
            description='sha256 of every file of research/w3-p10b-pointwise-complex except this one; verify.py '
                        'requires the package to be exactly these files', files=files), indent=1, sort_keys=True) + '\n')
    pinned = read(HERE / 'MANIFEST.json')['files']
    missing = sorted(set(pinned) - set(files))
    extra = sorted(set(files) - set(pinned))
    changed = sorted(k for k in set(pinned) & set(files) if pinned[k] != files[k])
    assert not (missing or extra or changed), 'MANIFEST.json: missing %s, unpinned %s, changed %s' % (missing, extra, changed)
    return len(files)


def check_source(src):
    n = Counter()
    for key, origin in src['origins'].items():
        for rel, pin in origin['files'].items():
            data = (HERE / rel).read_bytes()
            assert sha(data) == pin['sha256'] and git_blob(data) == pin['git_blob'], \
                '%s differs from %s at %s (%s)' % (rel, origin['repository'], origin['commit'][:7], pin['path'])
            n[key] += 1
    return n


# ------------------------------------------------------------------------------------------ 2. the bit side
def bit_side(src):
    """PR #346's final bit word: recount the paid children from its records, check its normalized five-stage
    histogram against them, and certify the bit coarse saving c from it"""
    B = HERE / 'bit/pr346'
    raw = gzip.decompress((B / 'FINAL-RECORDS.bin.gz').read_bytes())
    sums = dict(reversed(line.split()) for line in (B / 'RECORD-SHA256SUMS').read_text().splitlines() if line.strip())
    assert sha(raw) == sums['TT/249-records.bin'], 'final records differ from PR #346\'s RECORD-SHA256SUMS'
    assert len(raw) % 24 == 0
    kinds, H = Counter(), Counter()
    for t, a, b, c, rank5, rank6 in struct.iter_unpack('<6i', raw):
        kinds[t] += 1
        if t == 0 and rank5 > 0:        # MOVE (0, role, old frame, new frame, rank, z): a paid child of that rank
            H[rank5] += 1
        elif t == 2 and rank6 > 0:      # COPY (2, centre, temp, copy frame, target frame, rank): a paid copy
            H[rank6] += 1
    receipt = read(B / 'kappa-L10f.json')
    h, v, m, T = 20, 960, 100, 12      # T: PR #346's normalization (60 replicas / 5)
    norm = {int(r): n for r, n in receipt['normalized_histogram'].items()}
    idle = (2 * h - 2, h - 1, 2 * h + 2, 4)
    expect = Counter({r: 5 * T * n for r, n in H.items()})
    for r in idle:
        expect[r] += T * 2 * v
    assert norm == dict(expect), 'PR #346\'s normalized histogram is not 60 H + 12 * 2v * idle on its own records'
    W = receipt['W']
    assert receipt['m'] == m and W % T == 0 and (W // T - 4 * v) * h == 132720, 'unexpected stock'
    mass = sum(r * n for r, n in norm.items())
    root = S527.certify(norm, m, W, True)
    c = Q(int(Q(root['lower']) * 10**18), 10**18)
    bm, nextbm = S527.moment(norm, m, W, c, True), S527.moment(norm, m, W, c + GRID18, True)
    assert bm[1] < 1 < nextbm[0], 'bit coarse saving not certified by moment.py'
    fallback = 32 * m * m * sum(norm.values())
    _, upper = B2M.moment(m, W, list(norm.items()), c)
    _, bad = B2M.moment(m, W, [(1, fallback)], c)
    lower, _ = B2M.moment(m, W, list(norm.items()), c + GRID18)
    badlower, _ = B2M.moment(m, W, [(1, fallback)], c + GRID18)
    assert upper + FALLBACK_WEIGHT * bad < 1 < lower + FALLBACK_WEIGHT * badlower, 'bit coarse saving not certified by base_two_moment.py'
    assert c == Q(receipt['bit_coarse']), 'bit coarse saving differs from PR #346\'s'
    log('bit side (PR #346): %d records (%s), paid children recounted (%d, rank mass %d); normalized m = %d, W = %d, '
        'calls %d, rank mass %d, deficit %d; bit coarse c = %s ≈ %.12e (both engines, 10^-16 fallback, next point excluded) = PR #346\'s'
        % (len(raw) // 24, dict(sorted(kinds.items())), sum(H.values()), sum(r * n for r, n in H.items()), m, W,
           sum(norm.values()), mass, m * W - mass, c, float(c)))
    return dict(records=len(raw) // 24, record_kinds={str(k): n for k, n in sorted(kinds.items())},
                records_sha256=sha(raw), paid_children={str(r): n for r, n in sorted(H.items())},
                normalization=T, m=m, W=W, calls=sum(norm.values()), rank_mass=mass, deficit=m * W - mass,
                stock_from='PR #346 receipts/kappa-L10f.json (W = 125712 = 12 (4v + 132720/20)); not re-derived here',
                coarse=c, coarse_decimal=S527.decimal(c), moment_interval=[str(x) for x in bm],
                next_moment_lower_bound=str(nextbm[0]), equals_pr346=True)


# ------------------------------------------------------------------------------------------- 2. the program
def idle_ranks(h):
    """the idle climbs of Sussman's bridged word B_2 per port: 2 blocks each of rank 2h-2, h-1, 2h+2, 4"""
    return (2 * h - 2, h - 1, 2 * h + 2, 4)


def five_stage(blocks, v, h, R):
    Hinv = Counter()
    for w in blocks.values():
        for r, n in w.items():
            Hinv[int(r)] += n
    H5 = {r: 5 * n for r, n in Hinv.items()}
    for r in idle_ranks(h):
        H5[r] = H5.get(r, 0) + 2 * v
    return 5 * h, 4 * v + R, H5


def certify(name, cert, v, h):
    st = {}
    gx.check1(cert, scalar=True, stats=st)
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


def price(name, five, a):
    """PR #327's price(): PR #225's exact upper bound below W at a, with and without the 10^-16 fallback envelope;
    the next 10^-7 grid point fails the upper bound and is rejected by source527's exact lower bound"""
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
    """PR #327's coarse(): the largest 10^-18 grid point at which the normalized moment with the 10^-16 fallback
    envelope is below 1, by both exact engines, the next point excluded by both; likewise without the fallback"""
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


def flip_one_sign(cert):
    """negate the first coefficient of the first phase-A add gate with a coefficient list (PR #315's control)"""
    gate = next(g for g in cert['A'] if g[0] in ('out', 'in') and g[3])
    t, a, b = gate[3][0]
    gate[3][0] = [t, -a, b]
    return cert


def histogram(cert):
    Hinv = Counter()
    for w in cert['blocks'].values():
        for r, n in w.items():
            Hinv[int(r)] += n
    return Hinv


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


# -------------------------------------------------------------------------------------- 3./4. regeneration
def admit(root, tree, cand):
    """PR #233's step 3: admit the word's physical layer with PR #200's complete complex checker (PR #327's admit)"""
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
    return dict(status=audit['status'], formal=json.loads(json.dumps(audit.get('formal'))), mutations=audit.get('mutations'),
                source_sha256={Path(k).resolve().relative_to(root).as_posix(): x for k, x in audit['source_sha256'].items()})


def chain(root, work, name, tree, kernel, title, contract=True, admission=True, p=P):
    """PR #327's chain(): flow, exact lift, contract, gcert/1 emission, gx.check1 and gxcore on one aligned tree"""
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
    Hinv = histogram(raw)
    mirror(name, raw, Hinv)
    log('%s: emitted program: gx.check1 ACCEPTED (labels, blocks, N = %d, exact scalar identity) and gxcore mirror ACCEPTED; %d gates, %d registers'
        % (name, rec['N'], rec['gates_A'] + rec['gates_B'], rec['registers']))
    child = Counter({r: 3 * n for r, n in Hinv.items()})
    child[2] += 2 * v
    assert {int(r): n for r, n in fd['child_histogram'].items()} == dict(child), '%s: ledger differs from the flow profile' % name
    cert, norm = normalize_scatter.normalize(raw)
    st = {}
    gx.check1(cert, scalar=True, stats=st)
    assert cert['scat'] == normalize_scatter.STAR and normalize_scatter.same_shape(raw, cert), '%s: normalization changed more than signs' % name
    assert (cert['blocks'], cert['N'], cert['frames'], len(cert['A']), len(cert['B'])) == (raw['blocks'], raw['N'], raw['frames'], len(raw['A']), len(raw['B']))
    assert (st['den'], st['maxabs'], st['steps']) == (rec['scalar_denominators'], rec['scalar_max_abs'], rec['distinct_frame_steps'])
    mirror(name, cert, Hinv)
    norm.update(raw_certificate_sha256=sha(canonical(raw)), gx_check1='ACCEPTED (raw and committed program)',
                gxcore_mirror='ACCEPTED (raw and committed program; label and scalar checks)')
    rec['scatter'] = norm
    log('%s: star form (%s): gx.check1 and gxcore ACCEPTED, blocks and N unchanged'
        % (name, 'registers %s re-signed, %d coefficients' % (norm['flipped_registers'], norm['changed_coefficients'])
           if norm['flipped_registers'] else 'emitted in star form, normalization not needed'))
    rec['blocks'] = cert['blocks']
    rec['certificate_sha256'] = sha(canonical(cert))
    return rec, cert


def install(root, rel):
    """install a package module file next to PR #168 v4's in the rebuilt tree"""
    dest = root / 'references/paired-cube/sources' / Path(rel).name
    if dest.exists():
        assert dest.read_bytes() == (HERE / rel).read_bytes(), 'module file name collides with a different tree file: ' + rel
    else:
        shutil.copyfile(HERE / rel, dest)
    return dest


def module_record(path, kind):
    """the module's contract (the rebuilt tree's loaders; centre46.load_pmod46 for the 37-root pair module)"""
    from paired_cube.modules import triple_module_from, all_but_one_from  # noqa: E402
    from centre46 import load_pmod46                                     # noqa: E402
    if kind == 'tmod':
        triple_module_from(path, P)
    elif kind == 'pmod':
        load_pmod46(path, P - 1)
    else:
        all_but_one_from(path, P - 2)
    d = read(path)
    outputs = {'tmod': comb(P, 3), 'pmod': comb(P - 1, 2) + 1, 'qmod': P - 2}[kind]
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


def local_design(root):
    local = json.loads((root / 'references/paired-cube/sources/local_L1.json').read_text())
    local['G'] = {k: 's' for k in local['G']}
    local['A'] = {k: 'fd' for k in local['A']}
    return local


def graph_anchors(root, spec, table, files):
    """anchor (d): PR #315's Graph.finish patch builds centre46.finish_centre46's graph on these modules; anchor (e):
    spec_graph.finish_spec with the spec's per-invocation tables builds the same graph"""
    graph_py = root / 'scripts/paired_cube/graph.py'
    diff = (HERE / 'references/centre46_graph.diff').read_text()
    patched, hunks = apply_diff(graph_py.read_text(), diff)
    (root / 'scripts/paired_cube/graph_centre46_patch.py').write_text(patched)
    import paired_cube.graph as G0                                                  # noqa: E402
    import paired_cube.graph_centre46_patch as G1                                   # noqa: E402
    (root / 'scripts/paired_cube/graph_centre46_patch.py').unlink()                # leave the rebuilt tree as pinned
    from paired_cube.modules import triple_module_from, all_but_one_from            # noqa: E402
    from centre46 import load_pmod46, finish_centre46                               # noqa: E402
    local = local_design(root)
    t = triple_module_from(HERE / spec['tmod'], P)
    pm46, q = load_pmod46(files['pmod'], P - 1), all_but_one_from(files['qmod'], P - 2)
    a = finish_centre46(G0.Graph(P, local=copy.deepcopy(local)), t, pm46, q)
    b = G1.Graph(P, local=copy.deepcopy(local)).finish(t, pm46, q)
    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    assert differ == ['status'], 'centre46.py and the patched Graph.finish differ in %s' % differ
    cache = {}

    def get(path, loader, n):
        if path not in cache:
            cache[path] = loader(path, n)
        return cache[path]
    c = spec_graph.finish_spec(G0.Graph(P, local=copy.deepcopy(local)), t,
                               lambda i, bit: get(table['p', i, bit], load_pmod46, P - 1),
                               lambda i, j, mode: get(table['q', i, j, mode], all_but_one_from, P - 2))
    differ_e = sorted(k for k in set(a) | set(c) if a.get(k) != c.get(k))
    assert differ_e == [], 'spec_graph.finish_spec and centre46.finish_centre46 differ in %s' % differ_e
    return dict(d=dict(patch_sha256=sha(diff.encode()), hunks=hunks, centres_from_pair_module=len(a['centers']),
                       fields_compared=len(a), differing_fields=differ, center_additions=a['counts']['center_additions']),
                e=dict(invocations=dict(pair=sum(k[0] == 'p' for k in table), all_but_one=sum(k[0] == 'q' for k in table)),
                       distinct_module_files=dict(pair=len({f for k, f in table.items() if k[0] == 'p'}),
                                                  all_but_one=len({f for k, f in table.items() if k[0] == 'q'})),
                       fields_compared=len(a), differing_fields=differ_e,
                       query_additions=c['counts']['query_additions']))


def program(spec, cert):
    """step 3: the committed complex program on its own"""
    name = spec['name']
    assert sha(canonical(cert)) == PROGRAM_SHA256, 'the committed program is not the pinned one'
    assert (cert['format'], cert['p'], cert['h'], cert['v']) == ('gcert/1', P, 2 * P, 8 * comb(P, 3))
    assert cert['scat'] == normalize_scatter.STAR, 'the committed program is not in star form'
    rec = certify(name, cert, cert['v'], cert['h'])
    mirror(name, cert, histogram(cert))
    log('complex %s: gx.check1 ACCEPTED (labels, blocks, N = %d, exact scalar identity) and gxcore mirror ACCEPTED; R %d, %d gates, %d blocks'
        % (name, rec['N'], rec['R'], rec['gates_A'] + rec['gates_B'], rec['blocks_total']))
    rec['controls'] = controls(name, cert)
    log('complex %s: flipped scalar sign rejected by gx.check1 and gxcore (E5)' % name)
    assert rec['cst'] == 20 * 18 and rec['five_stage']['deficit'] == 4 * 960 - 5 * 360 == 2040
    five = rec['five_stage']
    claim = parse_grid(spec['claim'])
    five.update(price(name, five, claim))
    five['coarse'] = coarse(name, five, claim)
    log('complex %s: five-stage word at h = 20 (m = %d, W = %d, deficit %d) certified at a = %s with and without the 10^-16 fallback, '
        '%s rejected; coarse b = %s with the fallback, %s without (both engines)'
        % (name, five['m'], five['W'], five['deficit'], five['a'], five['next_grid_point'],
           five['coarse']['with_fallback']['b'], five['coarse']['without_fallback']['b']))
    rec['blocks'] = cert['blocks']
    rec['certificate_sha256'] = sha(canonical(cert))
    return rec


# ------------------------------------------------------------------------------------------------ 4. kappa
OUTER = load_module('pr315_outer', HERE / 'pricing/outer.py')      # PR #315's outer assembly, unchanged
BRIDGE = dict(proof='PROOF.md', representation='Exact powers with source-bound finite overcharges',
              semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000),
                            B_upper=dict(base=2, exponent=100001), C0=dict(base=2, exponent=210000), C1=1,
                            strict_literal_gap=1, induction_gap_lower=1),
              rows=dict(coefficient=20161, degree=10**6, suffix_slope=4 * 10**6, degree_gap=Q(10**6) - Q(51 * 20161, 25)))


def kappa(bit, b):
    """the outer assembly of PR #315's math_check (as in PR #329): bit saving c capped below the complex leaf cap"""
    c = bit['coarse']
    hist = {int(r): n for r, n in bit['histogram'].items()}
    m, W = bit['m'], bit['W']
    grid, eta, beta = GRID18, Q(1, 10**12), Q(1, 10**9)
    cap = (1 - beta) * b
    s = min(c, Q(((cap - grid) * 10**18).__floor__(), 10**18))
    binding = 'bit' if s == c else 'complex'
    sm = S527.moment(hist, m, W, s, True)
    assert 0 < s <= c and sm[1] < 1
    if binding == 'complex':
        assert s + grid > cap - grid
    chain = [Q(384599, 10**10)]
    for _ in range(3):
        a = (1 - s) * s + s * chain[-1]
        assert chain[-1] < a < s < 1 - a
        chain.append(a)
    a_bit = chain[-1]
    assert a_bit < s <= cap - grid < cap and BRIDGE['rows']['degree_gap'] > 0
    q = a_bit * (1 - 2 * eta)
    minimum = (1 - eta) * q / (1 + q)
    ticks = minimum * 10**18
    k = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    asm = OUTER.assembly(a_bit, b, BRIDGE, k, eta=eta, beta=beta)
    assert len(asm['strict_constraints']) == 47 and len(asm['margins']) == 7 and min(asm['strict_constraints'].values()) > 0
    try:
        OUTER.assembly(a_bit, b, BRIDGE, k + grid, eta=eta, beta=beta)
    except AssertionError:
        pass
    else:
        raise AssertionError('adjacent kappa admitted')
    if binding == 'complex':
        try:
            OUTER.assembly(cap, b, BRIDGE, k, eta=eta, beta=beta)
        except AssertionError as error:
            assert 'leaf_saving_above_bit' in str(error)
        else:
            raise AssertionError('complex leaf cap admitted')
    tight = min(asm['strict_constraints'], key=lambda n: asm['strict_constraints'][n])
    return dict(complex_coarse=b, complex_leaf_cap=cap, bit_coarse=c, bit_saving_used=s, binding=binding,
                bit_moment_interval=[str(x) for x in sm], bootstrap_chain=[str(x) for x in chain], minimum_margin=minimum,
                kappa=k, kappa_decimal=S527.decimal(k), kappa_scientific=format(float(k), '.15e'),
                strict_constraints=47, smallest_constraint=tight, adjacent_kappa_rejected=True,
                leaf_cap_itself_rejected=binding == 'complex')


# -------------------------------------------------------------------------------------- 5. regeneration
def regenerate(src, spec, uniform, temp_root):
    result = {}
    sussman = read(HERE / 'references/sussman/pr193-blocks.json')
    layer = load_module('pr233_layer_verify', HERE / 'references/pr233-layer/verify.py')
    utable = spec_graph.expand(uniform, HERE)
    one = spec_graph.shared(utable)
    assert one['p'] and one['q']
    table = spec_graph.expand(spec, HERE)
    with tempfile.TemporaryDirectory(prefix='w3-p10b-pointwise-', dir=temp_root) as d:
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
        assert rec['certificate_sha256'] == src['anchors']['pr194_certificate_sha256'], 'pr194: differs from PR #256\'s certificate'
        result['anchor_pr194'] = dict(N=rec['N'], R=rec['R'], blocks_total=rec['blocks_total'], certificate_sha256=rec['certificate_sha256'],
                                      equals_pr256_certificate=True, equals_sussman_pr193_blocks=True)
        log('anchor (b): PR #194\'s word through this chain is PR #256\'s certificate (sha256 %s...) with Sussman\'s #193 histogram' % rec['certificate_sha256'][:12])
        files = dict(tmod=HERE / uniform['tmod'], pmod=one['p'], qmod=one['q'])
        installed = {k: install(root, Path(f).relative_to(HERE).as_posix()) for k, f in files.items()}
        anchors = graph_anchors(root, uniform, utable, installed)
        result['anchor_centre_patch'], result['anchor_spec_graph'] = anchors['d'], anchors['e']
        log('anchor (d): PR #315\'s Graph.finish patch builds centre46.py\'s graph on PR #325\'s modules; anchor (e): spec_graph.finish_spec '
            'on spec/uniform.json builds the same graph (every field)')
        U = HERE / uniform['layer']
        uargs = ['--arcs', U / 'matching-arcs.json', '--frames', U / 'physical-frames.json', '--pairs', U / 'physical-pairs-mw.json']
        fa, fb = work / 'builder-p', work / 'builder-spec'
        run(root, HERE / 'aligned_word_p.py', '--p', P, '--centre46', '--tree', root, '--tmod', installed['tmod'],
            '--pmod', installed['pmod'], '--qmod', installed['qmod'], *uargs, '--out', fa)
        run(root, HERE / 'aligned_word_spec.py', '--p', P, '--spec', HERE / 'spec/uniform.json', '--spec-root', HERE, '--tree', root,
            '--tmod', 'x', '--pmod', 'x', '--qmod', 'x', *uargs, '--out', fb)
        for f in SEVEN:
            assert (fa / f).read_bytes() == (fb / f).read_bytes(), 'aligned_word_spec.py --spec differs from aligned_word_p.py --centre46: ' + f
        result['anchor_spec_builder'] = dict(spec='spec/uniform.json', layer=uniform['layer'], files_compared=len(SEVEN), identical=True,
                                             physical_R=read(fa / 'certificates/paired-cube-sinks-input.json')['physical_R'])
        L = HERE / spec['layer']
        layer_args = ['--arcs', L / 'matching-arcs.json', '--frames', L / 'physical-frames.json', '--pairs', L / 'physical-pairs-mw.json']
        log('anchor (f): on the companion layer, aligned_word_spec.py --spec spec/uniform.json writes the 7 files of aligned_word_p.py --centre46 byte for byte')
        result['modules'] = {kind: module_record(installed[kind], kind) for kind in ('pmod', 'qmod', 'tmod')}
        result['pointwise_pair_modules'] = {}
        for i in range(P):
            assert table['p', i, 0] == table['p', i, 1], 'pair module of point %d differs between the two bits' % i
            result['pointwise_pair_modules'][str(i)] = dict(file=table['p', i, 0].relative_to(HERE).as_posix(),
                                                            **module_record(table['p', i, 0], 'pmod'))
        assert spec_graph.shared(table)['q'] == one['q']
        key = spec['name']
        tree = work / key
        built = run(root, HERE / 'aligned_word_spec.py', '--p', P, '--spec', HERE / 'spec/c2.json', '--spec-root', HERE, '--tree', root,
                    '--tmod', 'x', '--pmod', 'x', '--qmod', 'x', *layer_args, '--out', tree)
        dropped = [json.loads(x) for x in built.splitlines() if x.startswith('{')]
        dropped = next(x for x in dropped if x.get('stage') == 'physical')['dropped_gauges']
        assert not dropped, '%s: gauges dropped %s' % (key, dropped)
        sinks = read(tree / 'certificates/paired-cube-sinks-input.json')
        log('%s: word on the frozen layer (%d arcs, %d moved frames, %d pairs), physical checks pass, physical R %d'
            % (key, len(read(L / 'matching-arcs.json')['matching_arcs']), len(read(L / 'physical-frames.json')['frames']),
               len(read(L / 'physical-pairs-mw.json')['pairs']), sinks['physical_R']))
        pc = json.loads(run(root, HERE / 'paircheck.py', '--root', root, tree))
        assert pc['status'] == 'PASS' and not pc['violations'] and not pc['erasable'], '%s: paircheck %s' % (key, pc)
        assert all(x.startswith('REJECTED') for x in pc['controls'].values()), '%s: a paircheck control was not rejected: %s' % (key, pc['controls'])
        assert pc['controls']['donor_frame_outside_gauge'] == 'REJECTED (donor frame outside gauge)' and \
            pc['controls']['parity_erasable_donor'] == 'REJECTED (erasable)', '%s: a paircheck control is not isolated: %s' % (key, pc['controls'])
        log('%s: paircheck PASS (%d early, %d late pairs, none parity-erasable); %d mutation controls rejected'
            % (key, pc['early'], pc['late'], len(pc['controls'])))
        rec, cert = chain(root, work, key, tree, L / 'kernel-pairs-mw.json', key)
        rec['paircheck'] = pc
        rec['layer'] = dict(R=read(tree / 'cache/record.json')['R'], physical_R=sinks['physical_R'],
                            arcs=len(read(L / 'matching-arcs.json')['matching_arcs']),
                            moved_frames=len(read(L / 'physical-frames.json')['frames']),
                            pairs=len(read(L / 'physical-pairs-mw.json')['pairs']),
                            kernel_pairs=len(read(L / 'kernel-pairs-mw.json')['kernel_pairs']))
        result['regenerated'] = rec
    return result, cert


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--quick', action='store_true', help='steps 1-4 and 6 only: no regeneration of the complex program (about two minutes)')
    ap.add_argument('--write', action='store_true', help='rewrite certificate/expected.json, then MANIFEST.json')
    ap.add_argument('--temp-root', type=Path, default=None)
    a = ap.parse_args()
    assert not (a.quick and a.write), '--write needs the full run'
    src = read(HERE / 'SOURCE.json')
    spec, uniform = read(HERE / 'spec/c2.json'), read(HERE / 'spec/uniform.json')
    if not a.write:
        log('MANIFEST.json: %d package files present and unchanged' % manifest())
    log('SOURCE.json: vendored files equal their git blobs at their origin commits: %s' % dict(check_source(src)))
    bit = bit_side(src)
    committed_path = HERE / spec['certificate']
    committed = read(committed_path)
    rec = program(spec, committed)
    b = Q(rec['five_stage']['coarse']['with_fallback']['b'].split('/')[0]) / 10**18
    bitk = dict(coarse=bit['coarse'], m=bit['m'], W=bit['W'],
                histogram=read(HERE / 'bit/pr346/kappa-L10f.json')['normalized_histogram'])
    ref = src['pr346']
    k346 = kappa(bitk, Q(ref['complex_coarse']))
    assert k346['binding'] == ref['binding'] and k346['kappa'] == Q(ref['kappa']), 'PR #346\'s kappa not reproduced'
    log('PR #346 reproduced: complex b = %s binds, kappa = %s = %s' % (ref['complex_coarse'], ref['kappa'], k346['kappa_scientific']))
    k = kappa(bitk, b)
    assert k['binding'] == 'complex'
    gain = k['kappa'] / k346['kappa'] - 1
    log('this package: complex b = %s binds (bit c = %s above the leaf cap); kappa = %s = %s, %+.4f%% over PR #346; 47 strict constraints, '
        'adjacent kappa and the leaf cap itself rejected' % (grid18(b), grid18(bit['coarse']),
                                                            k['kappa'], k['kappa_scientific'], 100 * float(gain)))
    canon = dict(bit=bit, program=rec, kappa_pr346_reproduced=k346, kappa=k,
                 comparison=dict(pr346_kappa=str(k346['kappa']), kappa=str(k['kappa']), gain=str(k['kappa'] - k346['kappa']),
                                 gain_percent='%.6f' % float(100 * gain),
                                 pr346_complex_coarse=str(Q(ref['complex_coarse'])), complex_coarse=str(b)))
    if not a.quick:
        result, cert = regenerate(src, spec, uniform, a.temp_root)
        assert sha(canonical(cert)) == BASE_PROGRAM_SHA256, 'the regenerated program differs from PR #348\'s program'
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as td:
            src_gz, out_gz = Path(td) / 'base.json.gz', Path(td) / 'retimed.json.gz'
            src_gz.write_bytes(gzip.compress(canonical(cert), mtime=0))
            subprocess.run([sys.executable, '-B', str(HERE / 'retime/retime_gcert.py'), str(src_gz), str(out_gz), '--rounds', '20'],
                           check=True, stdout=subprocess.DEVNULL)
            cert = json.loads(gzip.decompress(out_gz.read_bytes()))
        assert sha(canonical(cert)) == rec['certificate_sha256'] == PROGRAM_SHA256, 'the retimed regenerated program differs from the committed one'
        assert canonical(cert) == gzip.decompress(committed_path.read_bytes()), 'committed program differs from the retimed regenerated one'
        log('regenerated PR #348 program retimed by retime/retime_gcert.py = committed program byte for byte')
        reg = result.pop('regenerated')
        for key in ('R', 'N', 'cst', 'gates_A', 'gates_B', 'registers', 'scalar_denominators',
                    'scalar_max_abs'):
            assert reg[key] == rec[key], key
        log('regenerated chain consistent with the committed program (sha256 %s...)' % PROGRAM_SHA256[:12])
        canon['regeneration'] = dict(result, chain={key: reg[key] for key in ('admission', 'flow', 'lift', 'contract_checks', 'scatter', 'paircheck', 'layer')})
    canon['status'] = ('PASS: conditional kappa = %s (complex-bound) with PR #346\'s w3 bit word and the per-point p = 10 complex program '
                       '(%s, b = %s); PR #346\'s kappa %s reproduced' % (k['kappa'], rec['five_stage']['a'], grid18(b), k346['kappa']))
    canon = json.loads(json.dumps(canon, sort_keys=True, default=str))
    if a.write:
        (HERE / 'certificate/expected.json').write_text(json.dumps(canon, indent=1, sort_keys=True) + '\n')
        log('wrote certificate/expected.json; MANIFEST.json: %d files pinned' % manifest(write=True))
    expected = read(HERE / 'certificate/expected.json')
    if a.quick:
        expected = {key: x for key, x in expected.items() if key != 'regeneration'}
    if expected != canon:
        for key in sorted(set(expected) | set(canon)):
            if expected.get(key) != canon.get(key):
                log('DIFFERS: %s' % key)
    assert expected == canon, 'result differs from certificate/expected.json'
    log('PASS %s: conditional kappa = %s ≈ %s (complex-bound; PR #346: %s, %+.4f%%)'
        % ('certificate/expected.json reproduced' + (' (without the regeneration entry)' if a.quick else ''),
           k['kappa'], k['kappa_scientific'], k346['kappa'], 100 * float(gain)))


if __name__ == '__main__':
    main()
