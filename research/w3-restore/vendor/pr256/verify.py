#!/usr/bin/env python3
"""The source-assisted complex words of PR #194 and PR #233 as explicit numbered programs (gcert/1).

PR #194's contract says of its flow word: "A literal globally renumbered operation program is not exported."
This package exports it. `gcert_emit.py` lowers the flow witness of PR #184's complex_frame_flow.py and the local
invertible completions of exact_complex_flow_lift.py to Jacob Sussman's certificate format gcert/1
(jacobalansussman/wht-power-saving-lean, tools/gx): 12,052 numbered registers (1,320 sources, 1,320 targets,
9,412 slots), one frame per gate, every addition explicit, and the star scatter.  His reference checker
`gx.check1` (vendored unchanged in gx/gx.py) then checks the nested frames of every register, the block
histogram and the unit-move count N, and replays the exact scalar identity: every target receives exactly its
source and every source is restored.

This script (Python 3.11+; numpy/scipy only for the pinned regeneration of PR #202's word; -O refused)
  1. checks every pin of SOURCE.json;
  2. rebuilds the 308 pinned files of PR #202 from the vendored PR #233 package, regenerates the PR #168 v4
     cache and the source-aligned word (PR #194's pipeline, as PR #233's verify.py does);
  3. control: on the aligned tree's own physical layer (PR #168's frames, PR #193's pairs: the word of PR #194)
     runs flow (--witness), exact lift, emits gcert1-p11-pr194-flow and checks it with gx.check1; its block
     histogram must equal the one of Sussman's published certificate of #193 (tools/certificate/
     gcert1-p11-pr193.json.gz at f010392, embedded in certificate/expected.json) and N = 262,944;
  4. result: installs PR #233's physical layer (witness/), runs flow with PR #233's frozen kernel pairs, exact
     lift, emits gcert1-p11-pr233-flow and checks it; its per-invocation ledger must reproduce PR #233's
     certified child histogram (3 (x + y + s + c) + 2v e_2), and the five-stage price of the word
     (H5 = 5 H_inv + 2v (e42 + e21 + e46 + e4), m = 110, W = 14,692) is certified at a = 7547/10^7 with exact
     rational bounds, 7548/10^7 rejected;
  5. compares the two emitted certificates byte for byte (uncompressed JSON) with certificates/, and the run
     with certificate/expected.json.
usage: python3 -B research/gcert-program-233/verify.py [--write] [--temp-root DIR]"""
import argparse
import gzip
import hashlib
import importlib.util
import json
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
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE / 'gx'))
sys.path.insert(0, str(HERE / 'scripts'))
import gx                      # noqa: E402  (Jacob Sussman's reference checker, unchanged)
from moment import moment_margin  # noqa: E402
T0 = time.monotonic()


def log(msg):
    print('[%6.1fs] %s' % (time.monotonic() - T0, msg), flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(p):
    p = Path(p)
    return json.loads(gzip.decompress(p.read_bytes()) if p.suffix == '.gz' else p.read_bytes())


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


def certify(name, cert, expected_blocks, v, h):
    st = {}
    gx.check1(cert, scalar=True, stats=st)
    assert cert['blocks'] == expected_blocks, '%s: block histogram differs from the expectation' % name
    R, N, cst = cert['R'], cert['N'], cert['cst']
    assert N == R * h + 2 * v * (h - 1) + cst and not cert['ext']
    m, W, H5 = five_stage(cert['blocks'], v, h, R)
    rank = sum(r * n for r, n in H5.items())
    return dict(R=R, N=N, cst=cst, gates_A=len(cert['A']), gates_B=len(cert['B']), frames=len(cert['frames']),
                registers=2 * v + R, blocks_total=sum(sum(w.values()) for w in cert['blocks'].values()),
                scalar_denominators=st['den'], scalar_max_abs=st['maxabs'], distinct_frame_steps=st['steps'],
                five_stage=dict(m=m, W=W, rank=rank, deficit=W * m - rank, child_histogram={str(r): n for r, n in sorted(H5.items())}))


def price(name, five, a):
    hist = {int(r): n for r, n in five['child_histogram'].items()}
    margin, total = moment_margin(five['m'], five['W'], hist, a)
    assert margin > 0, '%s: five-stage moment not below W at a = %s' % (name, a)
    nxt = a + Q(1, 10**7)
    margin_next, _ = moment_margin(five['m'], five['W'], hist, nxt)
    assert margin_next <= 0, '%s: the next grid point %d/10^7 also passes; raise the claim' % (name, nxt * 10**7)
    scale = 10**30
    upper = -((-total.numerator * scale) // total.denominator)
    return dict(a='%d/10^7' % (a * 10**7), moment_upper_bound='%d/10^30' % upper, margin_lower_bound='%d/10^30' % (five['W'] * scale - upper),
                next_grid_point='%d/10^7' % (nxt * 10**7), next_grid_point_rejected=True)


def canonical(cert):
    return (json.dumps(cert, separators=(',', ':'), sort_keys=True) + '\n').encode()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='rewrite certificates/*.json.gz and certificate/expected.json')
    ap.add_argument('--temp-root', type=Path, default=None)
    a = ap.parse_args()
    src = read(HERE / 'SOURCE.json')
    for rel, digest in src['files'].items():
        assert sha((HERE / rel).read_bytes()) == digest, 'pinned file differs from SOURCE.json: ' + rel
    log('checked %d pins of SOURCE.json' % len(src['files']))
    expected = read(HERE / 'certificate/expected.json') if (HERE / 'certificate/expected.json').exists() else None
    sussman = read(HERE / 'references/sussman/pr193-blocks.json')
    layer = load_module('pr233_layer_verify', HERE / 'references/pr233-layer/verify.py')
    pr233 = read(HERE / 'references/pr233-layer/certificate.json')
    with tempfile.TemporaryDirectory(prefix='gcert-233-', dir=a.temp_root) as d:
        root = Path(d).resolve()
        pins = layer.rebuild(root)
        log('rebuilt %d pinned files of PR #202 (commit %s) from the vendored PR #233 package' % (len(pins['files']), pins['commit'][:7]))
        PKG, SA = root / 'research/source-assisted-v4', root / 'research/source-assisted'
        work = root / '.work'; work.mkdir()
        base, aligned = work / 'base', work / 'aligned'
        run(root, root / 'scripts/paired_cube_producer.py', '--work-dir', base, '--output', work / 'producer.json')
        run(root, PKG / 'source_aligned_local_v4.py', '--tree', root, '--cache', base, '--out', aligned)
        cache = aligned / 'cache'
        g = read(cache / 'graph.json'); v, h = g['v'], g['h']
        log('regenerated the source-aligned word (h = %d, v = %d)' % (h, v))
        emitted, result = {}, {}
        for name, a_claim in (('pr194', None), ('pr233', Q(7547, 10**7))):
            phys = aligned / 'references/paired-cube/physical'
            flow_args = ['--purify-source-donors', '--recycle-kernels']
            if name == 'pr194':
                # PR #194's layer: the aligned tree's own frames (PR #168's) and PR #193's pairs, as pinned by PR #194
                data = read(PKG / 'data/physical-pairs.json')
                (phys / 'pairs.json').write_text(json.dumps(dict(pairs=data['pairs']), separators=(',', ':')) + '\n')
                flow_args += ['--kernel-pairs', PKG / 'data/kernel-pairs.json']
                own_frames = read(phys / 'frames.json')['frames']
                assert own_frames == read(HERE / 'references/pr233-layer/witness/physical-frames.json')['frames'], 'PR #233 keeps the aligned tree\'s frames'
            if name == 'pr233':
                for part in ('frames', 'pairs'):
                    data = read(HERE / ('references/pr233-layer/witness/physical-%s.json' % part))
                    (phys / (part + '.json')).write_text(json.dumps({part: data[part]}, separators=(',', ':')) + '\n')
                flow_args += ['--kernel-pairs', HERE / 'references/pr233-layer/witness/kernel-pairs.json']
            flow = work / (name + '.flow.json')
            run(root, SA / 'decision/complex_frame_flow.py', '--tree', aligned, '--cache', cache, '--out', flow, '--witness', *flow_args)
            witness = flow.with_suffix('.witness.json')
            lift = work / (name + '.lift.json')
            run(root, SA / 'decision/exact_complex_flow_lift.py', '--witness', witness, '--profile', flow, '--out', lift)
            lift_data = read(lift)
            fd = read(flow)
            log('%s: flow new_R %d, deficit %d, numerical root %.7e; lift: %s' % (name, fd['new_R'], fd['deficit'], fd['numerical_local_root'], lift_data['status'][:60]))
            out = work / ('gcert1-p11-%s-flow.json' % name)
            run(root, HERE / 'gcert_emit.py', '--cache', cache, '--flow', flow, '--witness', witness, '--lift', lift_data['certificate_path'],
                '--out', out, '--name', 'pr194 flow word (PR168 frames, PR193 pairs)' if name == 'pr194' else 'pr233 flow word (PR168 frames, PR200 maximum-weight pairs)')
            cert = read(out)
            exp_blocks = sussman['blocks'] if name == 'pr194' else expected['pr233']['blocks'] if expected else cert['blocks']
            rec = certify(name, cert, exp_blocks, v, h)
            log('%s: gx.check1 ACCEPTED (labels, blocks, N = %d, exact scalar identity); %d gates' % (name, rec['N'], rec['gates_A'] + rec['gates_B']))
            # the gcert ledger is PR #233's / PR #194's certified child histogram: 3 (x + y + s + c) + 2v e_2
            child = Counter()
            for w in cert['blocks'].values():
                for r, n in w.items():
                    child[int(r)] += 3 * n
            child[2] += 2 * v
            if name == 'pr233':
                assert {int(r): n for r, n in pr233['flow']['child_histogram'].items()} == dict(child), 'pr233: ledger differs from PR #233 certificate.json'
                assert pr233['complex_saving'] == '3549537/5000000000'
            assert {int(r): n for r, n in fd['child_histogram'].items()} == dict(child), '%s: ledger differs from the flow profile' % name
            if a_claim is not None:
                rec['five_stage'].update(price(name, rec['five_stage'], a_claim))
                log('%s: five-stage word (m = %d, W = %d) certified at a = %s, %s rejected' % (name, rec['five_stage']['m'], rec['five_stage']['W'], a_claim, rec['five_stage']['next_grid_point']))
            rec['blocks'] = cert['blocks']
            rec['certificate_sha256'] = sha(canonical(cert))
            result[name] = rec
            emitted[name] = cert
        log('regenerated both certificates')
    for name, cert in emitted.items():
        path = HERE / 'certificates' / ('gcert1-p11-%s-flow.json.gz' % name)
        if a.write:
            with gzip.GzipFile(filename='', fileobj=open(path, 'wb'), mode='wb', mtime=0) as f:
                f.write(canonical(cert))
        assert sha(gzip.decompress(path.read_bytes())) == result[name]['certificate_sha256'], '%s: committed certificate differs from the regenerated one' % name
    log('committed certificates reproduced byte for byte (uncompressed JSON)')
    canon = json.loads(json.dumps(dict(status='PASS: both flow words exported as gcert/1 programs accepted by gx.check1; PR #233 word priced at 7547/10^7 in the five-stage layout',
                                       pr194=result['pr194'], pr233=result['pr233'],
                                       sussman_pr193=dict(blocks=sussman['blocks'], N=sussman['N'], file_sha256=sussman['file_sha256']),
                                       prerequisites=dict(pr233=src['prerequisites']['pr233'], pr202=pins['commit'], sussman=src['prerequisites']['sussman'])), sort_keys=True))
    if a.write:
        (HERE / 'certificate/expected.json').write_text(json.dumps(canon, indent=1, sort_keys=True) + '\n')
        log('wrote certificate/expected.json')
    committed = read(HERE / 'certificate/expected.json')
    if committed != canon:
        for k in sorted(set(committed) | set(canon)):
            if committed.get(k) != canon.get(k):
                log('DIFFERS: %s' % k)
    assert committed == canon, 'result differs from certificate/expected.json'
    log('PASS expected.json reproduced: N = %d, PR #233 word at a = %s in the five-stage layout' % (result['pr233']['N'], result['pr233']['five_stage']['a']))


if __name__ == '__main__':
    main()
