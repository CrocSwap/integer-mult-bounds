#!/usr/bin/env python3
"""A stronger complex supplier: our physical layer on the source-assisted v4 complex word.

The source-assisted complex word of PR #184 (icekylinx) on the PR #168 v4 modules (PR #193/#194, ikeboy) is
compiled by a frame flow whose child histogram depends on the physical layer (operation frames and reuse pairs)
that the flow receives. PR #194 uses PR #168's physical layer and certifies the complex saving 7.00918e-4. This
package keeps every other input fixed and supplies the physical layer of PR #200's descent (endpoint moves of
single operations, equal-frame components and connected bundles, seeded from PR #168's frames); the certified
complex saving becomes 3543063/5000000000 = 7.0861e-4.

verify.py (Python 3.11+, numpy/scipy for the regeneration steps; -O refused):
  1. checks baseline-pr202.tar.gz and every file in it against SOURCE.json (bytes of PR #202 at 8d8d67b, which
     carries PR #194's pipeline, the PR #168 v4 scripts and references, and PR #200's certificate and checker),
     and the three witness files;
  2. in a temporary directory: regenerates the PR #168 v4 complex cache (scripts/paired_cube_producer.py) and the
     source-aligned word (source_aligned_local_v4.py, with its own physical layer and checks);
  3. installs this package's physical frames and reuse pairs as the word's physical layer and admits that layer
     with PR #200's complete complex checker (complex/physical.py: all descended frames, nested chains, aliases,
     target read chronology, exact adjoint, every formal source/target/dirty column in both shear signs);
  4. runs PR #184's frame flow (complex_frame_flow.py), exact lift (exact_complex_flow_lift.py) and contract
     (contract_v4.py) on that layer, with the package's kernel pairs and physical pairs as the frozen witnesses;
  5. runs PR #194's assembly (assemble.py) against PR #200's bit certificate and compares the canonical result
     with certificate.json (--write regenerates it).
Nothing outside the temporary directory is read or written, except certificate.json with --write.
"""
import argparse
import gzip
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
sys.set_int_max_str_digits(0)
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
T0 = time.time()


def log(*a):
    print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def write_gz(p, data):
    with gzip.GzipFile(filename='', fileobj=open(p, 'wb'), mode='wb', mtime=0) as f:
        f.write((json.dumps(data, separators=(',', ':')) + '\n').encode())


def rebuild(dest):
    src = read(HERE / 'SOURCE.json')
    data = (HERE / src['archive']).read_bytes()
    assert sha(data) == src['archive_sha256'], 'baseline archive differs from SOURCE.json'
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = [x for x in archive.getmembers() if x.isfile()]
        assert sorted(x.name for x in members) == sorted(src['files']), 'archive lists other files than SOURCE.json'
        for x in members:
            part = Path(x.name)
            assert not part.is_absolute() and '..' not in part.parts, 'unsafe path in archive: ' + x.name
            body = archive.extractfile(x).read()
            assert sha(body) == src['files'][x.name], 'baseline file differs from SOURCE.json: ' + x.name
            (dest / part).parent.mkdir(parents=True, exist_ok=True)
            (dest / part).write_bytes(body)
    for name, digest in src['witness'].items():
        assert sha((HERE / 'witness' / name).read_bytes()) == digest, 'witness differs from SOURCE.json: ' + name
    return src


def run(root, *args):
    r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit('FAILED: ' + ' '.join(map(str, args)) + '\n' + r.stdout[-3000:] + r.stderr[-3000:])
    return r.stdout


def strip_seconds(d):
    if isinstance(d, dict):
        return {k: strip_seconds(v) for k, v in d.items() if k not in ('seconds', 'maxrss')}
    if isinstance(d, list):
        return [strip_seconds(v) for v in d]
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--write', action='store_true', help='rewrite certificate.json from this run')
    ap.add_argument('--temp-root', type=Path, default=None)
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='sa-v4-layer-', dir=a.temp_root) as d:
        root = Path(d).resolve()
        src = rebuild(root)
        log('rebuilt %d pinned files of PR #202 (commit %s) and checked the witnesses' % (len(src['files']), src['commit'][:7]))
        PKG = root / 'research/source-assisted-v4'
        SA = root / 'research/source-assisted'
        BIT = root / 'research/paired-cube-diagonal-bit-168'
        work = root / '.work'
        work.mkdir()
        base, aligned = work / 'base', work / 'aligned'
        run(root, root / 'scripts/paired_cube_producer.py', '--work-dir', base, '--output', work / 'producer.json')
        log('regenerated the PR #168 v4 complex cache')
        run(root, PKG / 'source_aligned_local_v4.py', '--tree', root, '--cache', base, '--out', aligned)
        log('regenerated the source-aligned word with its own physical layer and checks')
        # 3. install this package's physical layer and admit it with PR #200's complete complex checker
        phys = aligned / 'references/paired-cube/physical'
        frames = read(HERE / 'witness/physical-frames.json')['frames']
        pairs = read(HERE / 'witness/physical-pairs.json')['pairs']
        theirs = read(phys / 'frames.json')['frames']
        (phys / 'frames.json').write_text(json.dumps(dict(frames=frames), separators=(',', ':')) + '\n')
        (phys / 'pairs.json').write_text(json.dumps(dict(pairs=pairs), separators=(',', ':')) + '\n')
        sys.path.insert(0, str(root / 'scripts'))
        from paired_cube.closure import compile_closure            # noqa: E402
        from paired_cube_physical import physical                  # noqa: E402
        cache = aligned / 'cache'
        g, w, word, row = (read(cache / n) for n in ('graph.json', 'frames.json', 'selection.json', 'record.json'))
        baseline, _ = compile_closure(g, [[x, c] for x, c in w['matching_arcs']])
        profile = physical(g, w, word, row, frames, pairs)
        cand = work / 'candidate'
        cand.mkdir()
        for name, data in [('graph', g), ('baseline', baseline), ('frames', w), ('word', word), ('profile-before', row),
                           ('physical-frames', frames), ('physical-pairs', pairs), ('profile', profile)]:
            write_gz(cand / (name + '.json.gz'), data)
        pins = {p.name: sha(p.read_bytes()) for p in cand.glob('*.json.gz')}
        (cand / 'result.json').write_text(json.dumps(dict(tag='source-assisted-v4-layer', pins=pins)) + '\n')
        run(root, BIT / 'complex/physical.py', '--candidate', cand, '--source', root, '--out', work / 'audit.json')
        audit = read(work / 'audit.json')
        assert audit['status'].startswith('PASS'), audit['status']
        # the checker keys its source hashes by absolute path; record them relative to the rebuilt tree
        audit['source_sha256'] = {Path(k).resolve().relative_to(root).as_posix(): v for k, v in audit['source_sha256'].items()}
        log('admitted this package\'s physical layer with PR #200\'s complex checker: %s; %d frames, %d pairs, %d of PR #168\'s %d frames changed'
            % (audit['status'][:60], len(frames), len(pairs), sum(1 for (i, F), (j, G) in zip(sorted(frames), sorted(theirs)) if tuple(F) != tuple(G)), len(theirs)))
        # 4. frame flow, exact lift and contract on this layer
        flow = work / 'flow.json'
        run(root, SA / 'decision/complex_frame_flow.py', '--tree', aligned, '--cache', cache, '--out', flow, '--witness',
            '--purify-source-donors', '--recycle-kernels', '--kernel-pairs', HERE / 'witness/kernel-pairs.json')
        flow_data = read(flow)
        witness = flow.with_suffix('.witness.json')
        log('frame flow: new_R %d, new_W %d, deficit %d, numerical root %.7e' % (flow_data['new_R'], flow_data['new_W'], flow_data['deficit'], flow_data['numerical_local_root']))
        lift = work / 'lift.json'
        run(root, SA / 'decision/exact_complex_flow_lift.py', '--witness', witness, '--profile', flow, '--out', lift)
        lift_data = read(lift)
        lift_data.update(certificate_path=(work / 'lift.certificate.json.gz').relative_to(root).as_posix(),
                         witness_path=witness.relative_to(root).as_posix())
        lift.write_text(json.dumps(lift_data) + '\n')
        log('exact lift: %s' % lift_data['status'][:80])
        shutil.copy2(HERE / 'witness/physical-pairs.json', PKG / 'data/physical-pairs.json')
        shutil.copy2(HERE / 'witness/kernel-pairs.json', PKG / 'data/kernel-pairs.json')
        cprof = work / 'complex-profile.json'
        run(root, PKG / 'contract_v4.py', '--tree', aligned, '--cache', cache, '--witness', witness,
            '--flow-profile', flow, '--lift-profile', lift, '--out', cprof)
        cdata = read(cprof)
        for name, check in cdata['contract_checks'].items():
            assert check not in (False, 'FAIL'), 'contract check %s failed' % name
        log('contract: %d checks, W %d, rank %d, deficit %d' % (len(cdata['contract_checks']), cdata['W_per_vertex'], cdata['rank_per_vertex'], cdata['deficit_per_vertex']))
        # 5. assembly against PR #200's bit certificate
        final = work / 'global.json'
        run(root, PKG / 'assemble.py', '--complex', cprof, '--output', final)
        fdata = read(final)
        for branch in ('complex', 'bit'):
            fdata[branch].pop('numerical_root_for_discovery_only', None)
        complex_saving = Q(fdata['complex']['saving'])
        kappa = Q(fdata['kappa'])
        log('assembly: complex saving %s = %.7e, bit effective %.7e, kappa %s = %.7e' % (
            complex_saving, float(complex_saving), float(Q(fdata['bit']['effective_saving'])), kappa, float(kappa)))
        result = dict(status='PASS source-assisted v4 word with this package\'s physical layer',
                      complex_saving=str(complex_saving), complex_saving_float=float(complex_saving),
                      kappa=str(kappa), kappa_float=float(kappa), binding='bit' if Q(fdata['bit']['effective_saving']) < complex_saving else 'complex',
                      complex_profile=dict(m=cdata['m'], W_per_vertex=cdata['W_per_vertex'], rank_per_vertex=cdata['rank_per_vertex'],
                                           deficit_per_vertex=cdata['deficit_per_vertex'], child_histogram=cdata['child_histogram']),
                      layer=dict(frames=len(frames), pairs=len(pairs), audit=strip_seconds(audit)),
                      flow=strip_seconds({k: v for k, v in flow_data.items() if k not in ('source_sha256', 'cache_sha256')}),
                      lift={k: lift_data[k] for k in ('status', 'nodes', 'physical_R', 'all_actual_coefficients_dyadic', 'max_denominator', 'exact_scalar_program_sha256')},
                      contract_checks=cdata['contract_checks'], assembly=strip_seconds(fdata),
                      prerequisites=dict(pr202=src['commit'], pr194_complex_saving='219037/312500000', pr200_bit='research/paired-cube-diagonal-bit-168/certificate.json'))
        # certificate.json holds exact, platform-independent fields only (no floats, no hashes of generated gzip
        # artifacts); the full run record goes to report.json (informational, written only with --write)
        canon = dict(status=result['status'], complex_saving=result['complex_saving'], kappa=result['kappa'], binding=result['binding'],
                     complex_profile=result['complex_profile'],
                     layer=dict(frames=len(frames), pairs=len(pairs), frames_changed_from_pr168=sum(1 for (i, F), (j, G) in zip(sorted(frames), sorted(theirs)) if tuple(F) != tuple(G)),
                                audit_status=audit['status'], audit_input_sha256=audit['input_sha256'], audit_source_sha256=audit['source_sha256'],
                                formal=audit.get('formal'), mutations=audit.get('mutations')),
                     flow=dict(new_R=flow_data['new_R'], new_W=flow_data['new_W'], deficit=flow_data['deficit'], loss=flow_data['loss'],
                               original_physical_roles=flow_data['original_physical_roles'], child_histogram=flow_data['child_histogram']),
                     lift=dict(status=lift_data['status'], nodes=lift_data['nodes'], physical_R=lift_data['physical_R'],
                               all_actual_coefficients_dyadic=lift_data['all_actual_coefficients_dyadic'], max_denominator=lift_data['max_denominator']),
                     contract_checks=cdata['contract_checks'],
                     assembly=dict(kappa=fdata['kappa'], complex_saving=fdata['complex']['saving'], bit_effective_saving=fdata['bit']['effective_saving'], status=fdata.get('status')),
                     prerequisites=result['prerequisites'])
        canon = json.loads(json.dumps(canon, sort_keys=True))
        if a.write:
            (HERE / 'certificate.json').write_text(json.dumps(canon, indent=1, sort_keys=True) + '\n')
            (HERE / 'report.json').write_text(json.dumps(json.loads(json.dumps(result, sort_keys=True)), indent=1, sort_keys=True) + '\n')
            log('wrote certificate.json and report.json')
        committed = read(HERE / 'certificate.json')
        if committed != canon:
            for k in sorted(set(committed) | set(canon)):
                if committed.get(k) != canon.get(k):
                    log('DIFFERS: %s' % k)
        assert committed == canon, 'result differs from certificate.json'
        log('PASS certificate.json reproduced: complex saving %s (PR #194: 219037/312500000), kappa %s' % (complex_saving, kappa))


if __name__ == '__main__':
    main()
