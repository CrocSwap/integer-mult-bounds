#!/usr/bin/env python3
"""Full focused replay in a temporary copy; submitted evidence stays read-only."""
from pathlib import Path
from fractions import Fraction
from itertools import combinations
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def run(script, *args, reject=False, reason=None):
    start = time.monotonic()
    result = subprocess.run([sys.executable, str(script), *map(str, args)],
                            text=True, capture_output=True, timeout=900)
    if reject:
        require(result.returncode != 0, f'Corruption accepted: {script.name}')
        if reason:
            require(reason in result.stderr, f'Wrong rejection: {script.name}')
    elif result.returncode:
        raise RuntimeError(f'{script.name} failed:\n{result.stdout[-6000:]}\n{result.stderr[-6000:]}')
    print(f'{"REJECT" if reject else "PASS"} {script.name} ({time.monotonic()-start:.1f}s)', flush=True)


def primary_certificate(data):
    row = data['results'][0]
    final = row['assemblies'][-1]
    return dict(kappa=final['kappa'], kappa_decimal=final['kappa_decimal'],
                status='Conditional on the inherited interfaces stated in PROOF.md',
                coarse_bit=data['opposite_coarse'], ordinary_bit=data['actual_stopped_bit'],
                ordinary_leaf=data['ordinary_leaf'], theta=data['theta'],
                complex_moment=row['complex_moment'], complex_profile=row['profile'],
                bridge=row['bridge'], assembly=final)


def controls(work, expected):
    # Preserve coverage and group sizes but introduce a nonorthogonal pair.
    source = work / 'pr-network-mrp24-signed.json'
    bad = read(source)
    triples = list(combinations(range(24), 3))
    masks = [sum(1 << i for i in t) for t in triples]
    groups = bad['groups']
    anchor = masks[groups[0][0]]
    found = False
    for j in range(1, len(groups)):
        for k, index in enumerate(groups[j]):
            if (anchor & masks[index]).bit_count() % 2:
                groups[0][1], groups[j][k] = groups[j][k], groups[0][1]
                found = True
                break
        if found:
            break
    require(found, 'No partition control selected')
    corrupted = work / 'bad-partition.json'
    corrupted.write_text(json.dumps(bad))
    run(work / 'pr-foundations-mrp-phase.py', corrupted, reject=True,
        reason='non-orthonormal completed group basis')

    # Remove a real source-to-target scatter, without changing its saved profile.
    candidate = work / 'round8-foundations-minimal-v-word.json.gz'
    word = json.loads(gzip.decompress(candidate.read_bytes()))
    index = next(i for i, event in enumerate(word['events']) if event[0] == 'out')
    del word['events'][index]
    damaged = work / 'bad-word.json.gz'
    damaged.write_bytes(gzip.compress(json.dumps(word).encode(), mtime=0))
    run(work / 'round8-network-physical-ledger.py', '--candidate', damaged,
        '--output', work / 'bad-ledger', reject=True)

    # One omitted paid child violates the independently fixed rank deficit.
    profile = expected['results'][0]['profile']
    hist = {int(t): n for t, n in profile['child_multiplicities'].items()}
    hist[23] -= 1
    require(sum(t*n for t, n in hist.items()) != profile['m']*profile['W']-1862080,
            'Unpaid child was accepted')
    # Reconstruct the limiting saving rather than trust a rounded decimal.
    final = expected['results'][0]['assemblies'][-1]
    p = final['certificate']['parameters']
    a, eta = Fraction(p['a_bit']), Fraction(p['eta'])
    q = a*(1-2*eta)
    limit = (1-eta)*q/(1+q+q*(1+eta))
    require(Fraction(final['kappa']) < limit < Fraction(final['kappa'])+Fraction(1, 10**17),
            'Next kappa grid was accepted')
    print('REJECT unpaid child and next kappa grid; all four controls passed', flush=True)


def main():
    require(not sys.flags.optimize, 'Run without -O; source assertions are required')
    manifest = read(HERE / 'MANIFEST.json')
    for name, digest in manifest['sha256'].items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest,
                f'Frozen file changed: {name}')
    print(f'PASS {len(manifest["sha256"])} frozen file hashes', flush=True)
    frozen = HERE / 'inputs/research'
    public_tree = frozen / 'pr117-public/tree'
    pinned_tree = read(frozen / 'pr117-public/TREE.json')
    require(pinned_tree['sha'] == 'cbb05ce504d571546d9b7794c186a613c659c3bf'
            and not pinned_tree['truncated'], 'PR117 source pin differs')
    public_pins = {item['path']: item['sha'] for item in pinned_tree['tree'] if item['type'] == 'blob'}
    for path in public_tree.rglob('*'):
        if path.is_file():
            data = path.read_bytes()
            git_blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            require(git_blob == public_pins[str(path.relative_to(public_tree))],
                    f'PR117 Git blob differs: {path.name}')
    print('PASS every included PR117 Git blob pin', flush=True)
    expected = read(frozen / 'round8-optimize-reuse117-mrp.json')
    require(read(HERE/'certificate.json') == primary_certificate(expected), 'Primary certificate differs')

    with tempfile.TemporaryDirectory(prefix='completed-core-sharing-') as temporary:
        work = Path(temporary) / 'research'
        shutil.copytree(frozen, work)
        # The independent reviewer verifies the original frozen hashes first.
        run(work / 'round8-optimize-reuse117-mrp-independent.py')
        run(work / 'round8-optimize-reuse117-producer.py')
        old_complex_ledger = read(work / 'round8-foundations-reuse117-ledger.json')
        run(work / 'round8-foundations-reuse117-ledger.py')
        new_complex_ledger = read(work / 'round8-foundations-reuse117-ledger.json')
        for key in old_complex_ledger:
            if key != 'elapsed_seconds':
                require(new_complex_ledger[key] == old_complex_ledger[key], f'Complex ledger differs: {key}')
        run(work / 'round8-foundations-reuse117-interface.py')
        partition_hash = hashlib.sha256((work/'pr-network-mrp24-signed.json').read_bytes()).hexdigest()
        run(work / 'pr-network-mrp24.py')
        require(hashlib.sha256((work/'pr-network-mrp24-signed.json').read_bytes()).hexdigest() == partition_hash,
                'Regenerated signed partition differs')
        run(work / 'round8-network-final-geometry.py', '--output', work / 'fresh-geometry.json')
        fresh_geometry = read(work / 'fresh-geometry.json')
        old_geometry = read(work / 'pr-review-network-geometry.json')
        for key in old_geometry:
            if key != 'elapsed':
                require(fresh_geometry[key] == old_geometry[key], f'Geometry differs: {key}')
        candidate = work / 'round8-foundations-minimal-v-word.json.gz'
        ledger = work / 'fresh-ledger'
        run(work / 'round8-network-physical-ledger.py', '--candidate', candidate, '--output', ledger)
        old = read(work / 'round8-network-minimal-v-ledger/result.json')
        fresh = read(ledger / 'result.json')
        for key in old:
            if key != 'elapsed':
                require(fresh[key] == old[key], f'Literal ledger differs: {key}')
        require(gzip.decompress((ledger/'forward-events.i32.gz').read_bytes()) ==
                gzip.decompress((work/'round8-network-minimal-v-ledger/forward-events.i32.gz').read_bytes()),
                'Decompressed physical event stream differs')
        partition = work / 'pr-network-mrp24-signed.json'
        run(work / 'pr-foundations-mrp-phase.py', partition)
        run(work / 'pr-foundations-mrp-interface.py')
        run(work / 'round8-network-pr104-check.py')
        run(work / 'round8-network-opposite-profile.py')
        run(work / 'round8-optimize-reuse117-mrp.py')
        actual = read(work / 'round8-optimize-reuse117-mrp.json')
        for key in ('public', 'opposite_coarse', 'coarse_rank_moment', 'theta',
                    'ordinary_leaf', 'actual_stopped_bit', 'results'):
            require(actual[key] == expected[key], f'Exact mathematical output differs: {key}')
        controls(work, expected)
    print('PASS conditional kappa = 12310001053253/100000000000000000 > 1/8192')
    print('Inherited analytic/tape interfaces remain; no expanded Gaussian tape execution is claimed.')


if __name__ == '__main__':
    main()
