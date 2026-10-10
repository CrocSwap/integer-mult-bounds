#!/usr/bin/env python3
"""A stronger complex supplier from re-annealed complex modules, as explicit numbered programs (gcert/1). No new κ.

The source-assisted complex word of PR #184 / #194 calls three query modules: PR #168 v4's pair module (n = 10),
all-but-one module (n = 9) and disjoint-triple module (p = 11). This package replaces the three module files by
re-annealed ones (modules/), compiles the word with one recipe frozen as files (layers/: carrier arcs, PR #200's
descended operation frames, reuse pairs of PR #193's parity-avoiding recipe and of PR #233's maximum-weight recipe,
kernel pairs), and runs the same recipe on PR #168 v4's own modules as the control. Each of the four words is lowered
to Jacob Sussman's gcert/1 by PR #256's emitter, checked by his reference checker gx.check1, written with the star
scatter by normalize_scatter.py and checked again by gx.check1 and by his gxcore mirror (both vendored unchanged).

This script (Python 3.11+; numpy/scipy for the pinned regeneration and the checkers; -O refused)
  1. checks every pin of SOURCE.json;
  2. rebuilds the 308 pinned files of PR #202 from the vendored PR #233 package and regenerates the PR #168 v4
     producer word and the source-aligned word (PR #194's pipeline, as PR #233's and PR #256's verify.py do);
  3. anchors the new word builder and the chain: aligned_word.py, given PR #168 v4's modules and the source-aligned
     word's own arcs, frames and pairs, reproduces the seven output files of source_aligned_local_v4.py byte for
     byte; with PR #194's frozen pairs and kernel pairs the chain of step 4 reproduces PR #256's certificate of PR
     #194's word (sha256 of the canonical JSON pinned in SOURCE.json) and Sussman's block histogram of #193;
  4. for each module set (pr168-v4 = control, cmod = result) and pair recipe (parity, mw): installs the module files
     in the rebuilt tree, builds the word on the frozen layer with aligned_word.py (arcs through compile_closure,
     frames through the script's forward closure, pairs through the script's candidate rule, exact physical
     checks), re-checks the pairs from the written word with paircheck.py (five mutation controls rejected),
     admits the layer with PR #200's complete complex checker (complex/physical.py, as PR #233 does), runs
     PR #184's frame flow with the frozen kernel pairs, the exact lift and PR #194's contract (contract_v4.py),
     emits gcert/1 with gcert_emit.py, runs gx.check1 (labels, blocks, N, exact scalar identity), checks the ledger
     3 (x + y + s + c) + 2v e_2 = the flow's child histogram, writes the scatter as the star rule with
     normalize_scatter.py (registers of retained totals with unit -1 re-signed over the whole program) and runs
     gx.check1 and Sussman's gxcore mirror on that program (blocks, N, frames and gates unchanged), and certifies the
     five-stage price (H5 = 5 H_inv + 2v (e42 + e21 + e46 + e4), m = 110, W = 4v + R) at the claim of SOURCE.json
     with exact rational bounds, the next 10^-7 grid point rejected;
  5. compares the four committed (star-form) programs byte for byte (uncompressed JSON) with certificates/, and the
     run with certificate/expected.json.
usage: python3 -B research/complex-module-anneal/verify.py [--write] [--temp-root DIR]
--write re-pins the package's own inputs (modules/, layers/) in SOURCE.json, sets each claim to the largest 10^-7
grid point the exact bounds certify, and rewrites certificates/ and certificate/expected.json (see README, re-pinning).
"""
import argparse
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
from moment import moment_margin  # noqa: E402
T0 = time.monotonic()
SETS = ('pr168-v4', 'cmod')
RECIPES = ('parity', 'mw')
OWN = ('modules/', 'layers/')          # package inputs that --write re-pins; every other pin is vendored and fixed
SEVEN = ('cache/graph.json', 'cache/frames.json', 'cache/selection.json', 'cache/record.json',
         'references/paired-cube/physical/frames.json', 'references/paired-cube/physical/pairs.json',
         'certificates/paired-cube-sinks-input.json')
NAMES = {'pr168-v4': 'PR168 v4 modules', 'cmod': 're-annealed modules',
         'parity': 'PR193 parity-avoiding pairs', 'mw': 'PR233 maximum-weight pairs'}


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


def canonical(cert):
    return (json.dumps(cert, separators=(',', ':'), sort_keys=True) + '\n').encode()


def grid(a):
    return '%d/10^7' % (a * 10**7)


def parse_grid(s):
    num, den = s.split('/')
    assert den == '10^7'
    return Q(int(num), 10**7)


def five_stage(blocks, v, h, R):
    """Sussman's bridged five-stage word on one invocation ledger H_inv (the gcert block histogram over all
    classes): per cover vertex H5 = 5 H_inv + 2v (e42 + e21 + e46 + e4), width m = 5h, stock W = 4v + R."""
    Hinv = Counter()
    for w in blocks.values():
        for r, n in w.items():
            Hinv[int(r)] += n
    H5 = {r: 5 * n for r, n in Hinv.items()}
    for r in (42, 21, 46, 4):
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
    return dict(R=R, N=N, cst=cst, gates_A=len(cert['A']), gates_B=len(cert['B']), frames=len(cert['frames']),
                registers=2 * v + R, blocks_total=sum(sum(w.values()) for w in cert['blocks'].values()),
                scalar_denominators=st['den'], scalar_max_abs=st['maxabs'], distinct_frame_steps=st['steps'],
                five_stage=dict(m=m, W=W, rank=rank, deficit=W * m - rank, child_histogram={str(r): n for r, n in sorted(H5.items())}))


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
    hist = {int(r): n for r, n in five['child_histogram'].items()}
    margin, total = moment_margin(five['m'], five['W'], hist, a)
    assert margin > 0, '%s: five-stage moment not below W at a = %s' % (name, grid(a))
    nxt = a + Q(1, 10**7)
    margin_next, _ = moment_margin(five['m'], five['W'], hist, nxt)
    assert margin_next <= 0, '%s: the next grid point %s also passes; raise the claim' % (name, grid(nxt))
    scale = 10**30
    upper = -((-total.numerator * scale) // total.denominator)
    return dict(a=grid(a), moment_upper_bound='%d/10^30' % upper, margin_lower_bound='%d/10^30' % (five['W'] * scale - upper),
                next_grid_point=grid(nxt), next_grid_point_rejected=True)


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
    (cand / 'result.json').write_text(json.dumps(dict(tag='complex-module-anneal', pins=pins)) + '\n')
    out = cand.with_suffix('.audit.json')
    run(root, root / 'research/paired-cube-diagonal-bit-168/complex/physical.py', '--candidate', cand, '--source', root, '--out', out)
    audit = read(out)
    assert audit['status'].startswith('PASS'), audit['status']
    # the checker keys its source hashes by absolute path; record them relative to the rebuilt tree
    return dict(status=audit['status'], formal=json.loads(json.dumps(audit.get('formal'))), mutations=audit.get('mutations'),
                source_sha256={Path(k).resolve().relative_to(root).as_posix(): x for k, x in audit['source_sha256'].items()})


def chain(root, work, name, tree, kernel, title, contract=True, admission=True):
    """flow, exact lift, contract, gcert/1 emission and gx.check1 on one aligned tree"""
    PKG, SA = root / 'research/source-assisted-v4', root / 'research/source-assisted'
    cache = tree / 'cache'
    g = read(cache / 'graph.json')
    v, h = g['v'], g['h']
    rec = {}
    if admission:
        rec['admission'] = admit(root, tree, work / (name + '.candidate'))
        log('%s: layer admitted by PR #200\'s complex checker: %s' % (name, rec['admission']['status'][:72]))
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
    out = work / ('gcert1-p11-%s-flow.json' % name)
    run(root, HERE / 'gcert_emit.py', '--cache', cache, '--flow', flow, '--witness', witness, '--lift', lift_data['certificate_path'],
        '--out', out, '--name', title)
    raw = read(out)
    rec.update(certify(name, raw, v, h))
    log('%s: gx.check1 ACCEPTED (labels, blocks, N = %d, exact scalar identity); %d gates, %d registers'
        % (name, rec['N'], rec['gates_A'] + rec['gates_B'], rec['registers']))
    # the gcert ledger is the flow's certified child histogram: 3 (x + y + s + c) + 2v e_2
    child = Counter()
    for w in raw['blocks'].values():
        for r, n in w.items():
            child[int(r)] += 3 * n
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
    mirror = gxcore.mirror(gxcore.normal(cert))
    Hinv = Counter()
    for w in cert['blocks'].values():
        for r, n in w.items():
            Hinv[int(r)] += n
    assert mirror['hist'] == dict(Hinv), '%s: gxcore histogram differs from the blocks' % name
    norm.update(raw_certificate_sha256=sha(canonical(raw)), gx_check1='ACCEPTED (raw and committed program)',
                gxcore_mirror='ACCEPTED (committed program; label and scalar checks)')
    rec['scatter'] = norm
    log('%s: committed program in star form (%s): gx.check1 and Sussman\'s gxcore mirror ACCEPTED, blocks and N unchanged'
        % (name, 'registers %s re-signed, %d coefficients' % (norm['flipped_registers'], norm['changed_coefficients'])
           if norm['flipped_registers'] else 'already star, unchanged'))
    rec['blocks'] = cert['blocks']
    rec['certificate_sha256'] = sha(canonical(cert))
    return rec, cert


def module_paths(src, root, name):
    paths = {}
    for kind, rel in src['module_sets'][name].items():
        if rel.startswith('tree:'):
            paths[kind] = root / rel[5:]
        else:
            # install the package's module file next to PR #168 v4's in the rebuilt tree
            dest = root / 'references/paired-cube/sources' / Path(rel).name
            assert not dest.exists(), 'module file name collides with a tree file: ' + rel
            shutil.copyfile(HERE / rel, dest)
            paths[kind] = dest
    return paths


def module_record(path, kind):
    d = read(path)
    inputs = {'tmod': 165, 'pmod': 45, 'qmod': 9}[kind]
    return dict(sha256=sha(Path(path).read_bytes()), additions=len(d['args']) - inputs - (1 if kind == 'tmod' else 0), outputs=len(d['roots']))


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
            assert rel.startswith('tree:') or rel in src['files'], 'module file not pinned: ' + rel
        for part in ['matching-arcs', 'physical-frames'] + ['%s-%s' % (k, r) for k in ('physical-pairs', 'kernel-pairs') for r in RECIPES]:
            assert 'layers/%s/%s.json' % (name, part) in src['files'], 'layer file not pinned: %s/%s' % (name, part)
    log('checked %d pins of SOURCE.json' % len(src['files']))
    sussman = read(HERE / 'references/sussman/pr193-blocks.json')
    layer = load_module('pr233_layer_verify', HERE / 'references/pr233-layer/verify.py')
    emitted, result = {}, {}
    with tempfile.TemporaryDirectory(prefix='cmod-anneal-', dir=a.temp_root) as d:
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
        log('regenerated the PR #168 v4 producer word and the source-aligned word (PR #194\'s pipeline)')
        # 3. anchors
        pr168 = module_paths(src, root, 'pr168-v4')
        mods = ['--tmod', pr168['tmod'], '--pmod', pr168['pmod'], '--qmod', pr168['qmod']]
        anchor = work / 'anchor'
        phys = aligned / 'references/paired-cube/physical'
        run(root, HERE / 'aligned_word.py', '--tree', root, *mods, '--arcs', aligned / 'cache/frames.json',
            '--frames', phys / 'frames.json', '--pairs', phys / 'pairs.json', '--out', anchor)
        for f in SEVEN:
            assert (anchor / f).read_bytes() == (aligned / f).read_bytes(), 'aligned_word.py differs from source_aligned_local_v4.py: ' + f
        log('anchor: aligned_word.py reproduces the 7 output files of source_aligned_local_v4.py byte for byte')
        tree = work / 'pr194'
        run(root, HERE / 'aligned_word.py', '--tree', root, *mods, '--arcs', aligned / 'cache/frames.json',
            '--frames', phys / 'frames.json', '--pairs', PKG / 'data/physical-pairs.json', '--out', tree)
        rec, _ = chain(root, work, 'pr194', tree, PKG / 'data/kernel-pairs.json', 'pr194 flow word (PR168 frames, PR193 pairs)',
                       contract=False, admission=False)
        assert rec['blocks'] == sussman['blocks'] and rec['N'] == sussman['N'], 'pr194: not the histogram of Sussman\'s certificate of #193'
        assert rec['certificate_sha256'] == src['prerequisites']['pr256']['pr194_certificate_sha256'], 'pr194: differs from PR #256\'s certificate'
        result['anchor_pr194'] = dict(N=rec['N'], R=rec['R'], blocks_total=rec['blocks_total'], certificate_sha256=rec['certificate_sha256'],
                                      equals_pr256_certificate=True, equals_sussman_pr193_blocks=True)
        log('anchor: PR #194\'s word through this chain is PR #256\'s certificate (sha256 %s...) with Sussman\'s #193 histogram' % rec['certificate_sha256'][:12])
        # 4. the four words
        modules = {}
        for name in SETS:
            paths = pr168 if name == 'pr168-v4' else module_paths(src, root, name)
            modules[name] = {kind: module_record(paths[kind], kind) for kind in ('pmod', 'qmod', 'tmod')}
            L = HERE / 'layers' / name
            for recipe in RECIPES:
                key = '%s-%s' % (name, recipe)
                tree = work / key
                run(root, HERE / 'aligned_word.py', '--tree', root, '--tmod', paths['tmod'], '--pmod', paths['pmod'], '--qmod', paths['qmod'],
                    '--arcs', L / 'matching-arcs.json', '--frames', L / 'physical-frames.json',
                    '--pairs', L / ('physical-pairs-%s.json' % recipe), '--out', tree)
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
                                  '%s flow word (%s, descended frames, %s)' % (key, NAMES[name], NAMES[recipe]))
                rec['paircheck'] = pc
                rec['layer'] = dict(R=read(tree / 'cache/record.json')['R'], physical_R=sinks['physical_R'],
                                    arcs=len(read(L / 'matching-arcs.json')['matching_arcs']),
                                    moved_frames=len(read(L / 'physical-frames.json')['frames']),
                                    pairs=len(read(L / ('physical-pairs-%s.json' % recipe))['pairs']),
                                    kernel_pairs=len(read(L / ('kernel-pairs-%s.json' % recipe))['kernel_pairs']))
                five = rec['five_stage']
                claim = best_claim(five) if a.write else parse_grid(src['claims'][key])
                if a.write:
                    src['claims'][key] = grid(claim)
                five.update(price(key, five, claim))
                log('%s: five-stage word (m = %d, W = %d) certified at a = %s, %s rejected'
                    % (key, five['m'], five['W'], five['a'], five['next_grid_point']))
                result[key] = rec
                emitted[key] = cert
        log('regenerated the four certificates')
    for key, cert in emitted.items():
        path = HERE / 'certificates' / ('gcert1-p11-%s-flow.json.gz' % key)
        if a.write:
            with open(path, 'wb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', mtime=0) as f:
                f.write(canonical(cert))
        assert sha(gzip.decompress(path.read_bytes())) == result[key]['certificate_sha256'], '%s: committed certificate differs from the regenerated one' % key
    log('committed certificates reproduced byte for byte (uncompressed JSON)')
    claims = {k: parse_grid(src['claims'][k]) for k in emitted}
    comparison = {}
    for recipe in RECIPES:
        c, r = claims['cmod-' + recipe], claims['pr168-v4-' + recipe]
        comparison[recipe] = dict(cmod=grid(c), control=grid(r), gain_over_control=str(c / r - 1), gain_over_control_percent='%.3f' % float(100 * (c / r - 1)))
    for k, (label, ref) in src['official'].items():
        c = claims['cmod-mw']
        comparison['cmod-mw_vs_' + k] = dict(official=label, gain=str(c / Q(ref) - 1), gain_percent='%.3f' % float(100 * (c / Q(ref) - 1)))
    canon = json.loads(json.dumps(dict(
        status='PASS: four flow words exported as gcert/1 programs accepted by gx.check1; re-annealed modules priced at %s (PR233 pairs) and %s (PR193 pairs) in the five-stage layout, same-recipe control %s and %s'
               % (grid(claims['cmod-mw']), grid(claims['cmod-parity']), grid(claims['pr168-v4-mw']), grid(claims['pr168-v4-parity'])),
        anchor_pr194=result['anchor_pr194'], comparison=comparison, modules=modules,
        **{k: result[k] for k in emitted},
        prerequisites=dict(pr202=pins['commit'], pr233=src['prerequisites']['pr233'], pr256=src['prerequisites']['pr256'],
                           sussman=src['prerequisites']['sussman'])), sort_keys=True))
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
    log('PASS expected.json reproduced: re-annealed modules at a = %s (PR233 pairs; control %s) and %s (PR193 pairs; control %s) in the five-stage layout'
        % (grid(claims['cmod-mw']), grid(claims['pr168-v4-mw']), grid(claims['cmod-parity']), grid(claims['pr168-v4-parity'])))


if __name__ == '__main__':
    main()
