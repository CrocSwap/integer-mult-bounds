"""Exact bounded verification; normal replay is read-only. Apache-2.0."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
from types import ModuleType

ROOT = Path(__file__).resolve().parent


def load(name, path, raw=None):
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes() if raw is None else raw, str(path), 'exec'), module.__dict__)
    return module


b = load('blockwise', ROOT/'blockwise.py')


def sources():
    code = None
    for item in json.loads((ROOT/'PREDECESSOR.json').read_text()):
        raw = (ROOT/item['file']).read_bytes()
        b.need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'source SHA256')
        b.need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
               == item['git_blob'], 'source Git blob')
        if item['file'] == 'vendor/lifting.py':
            code = raw
    b.need(code is not None, 'missing source implementation pin')
    return load('pinned_lifting', ROOT/'vendor/lifting.py', code)


def compositions(r):
    for mask in range(1 << (r-1)):
        result, start = [], 0
        for end in range(1, r):
            if mask & (1 << (end-1)):
                result.append(end-start)
                start = end
        yield tuple(result+[r-start])


def fail(call, contains):
    try:
        call()
    except ValueError as e:
        b.need(contains in str(e), 'wrong rejection: '+str(e))
        return
    raise ValueError('control did not reject: '+contains)


def verify():
    predecessor = sources()
    counts = Counter()
    rng = random.Random(170101)
    for r in range(1, 8):
        for inactive in (0, 1):
            N = 1 << (r+inactive)
            v = [(rng.randrange(-1000, 1001), rng.randrange(-1000, 1001)) for _ in range(N)]
            identity = [(x, 0) for x in range(N)]
            for inverse in (False, True):
                want = predecessor.kernel(v[:], r, identity, identity, inverse=inverse)
                b.need(b.literal(v, tuple(range(r)), inverse) == want, 'pinned floor word')
                for parts in compositions(r):
                    b.need(b.blocked(v, parts, inverse) == want, 'all partition equality')
                    counts['partition_directions'] += 1
                for h in range(1, r+1):
                    meter = Counter()
                    parts = b.partition(r, h)
                    fresh = v[:]
                    got = b.blocked(fresh, parts, inverse, width=32, meter=meter, inplace=True)
                    b.need(got == want, 'clean macro permutation')
                    b.need(got is fresh, 'in-place dispatcher returned a snapshot')
                    b.need(dict(meter) == b.invoice(r+inactive, parts), 'complete macro counts')
                    counts['clean_partition_invoice_directions'] += 1
            for h in range(1, r+1):
                parts = b.partition(r, h)
                sent = b.blocked(v, parts, width=32)
                b.need(b.blocked(sent, parts, True, width=32) == v, 'paired blocked return')
                counts['paired_clean_returns'] += 1
    for r in range(1, 6):
        N = 1 << r
        for width in (16, 33, 128):
            v = [(rng.randrange(-11, 12), rng.randrange(-11, 12)) for _ in range(N)]
            for inverse in (False, True):
                target = [(rng.randrange(-(1 << (width-1)), 1 << (width-1)),
                           rng.randrange(-(1 << (width-1)), 1 << (width-1))) for _ in range(N)]
                before = v[:]
                want = b.literal(v, tuple(range(r)), inverse)
                expected = [tuple(b.signed_xor(x, y, width) for x, y in zip(a, c))
                            for a, c in zip(target, want)]
                work = [[(0, 0)]*N for _ in range(3)]
                b.clean_oracle(v, target, width, inverse, work)
                b.need(target == expected and v == before and all(z == (0, 0) for a in work for z in a),
                       'arbitrary dirty XOR target/clean work')
                counts['dirty_target_oracles'] += 1
    for n in range(1, 9):
        for _ in range(8):
            # Build an invertible binary matrix by row additions and swaps.
            rows = [1 << j for j in range(n)]
            for _ in range(4*n):
                i, j = rng.randrange(n), rng.randrange(n)
                if i != j:
                    rows[i] ^= rows[j]
            offset, phase = rng.randrange(1 << n), rng.randrange(4)
            linear = [rng.randrange(4) for _ in range(n)]
            quadratic = [rng.randrange(1 << n) & ~((1 << (j+1))-1) for j in range(n)]
            got = b.gray_plan(rows, offset, linear, quadratic, phase)
            for x in range(1 << n):
                y = offset ^ sum((((row & x).bit_count() % 2) << j) for j, row in enumerate(rows))
                f = phase + sum(((x >> j) & 1)*linear[j] for j in range(n))
                f += 2*sum(((x >> j) & 1)*((x >> k) & 1)*((quadratic[j] >> k) & 1)
                           for j in range(n) for k in range(j+1, n))
                b.need(got[x] == (y, f % 4), 'Gray compiler versus direct formula')
                counts['wrapper_entries'] += 1
            counts['wrapper_plans'] += 1
    # All bounded two's-complement XOR target states at the smallest pair.
    source = [(-1, 2), (3, -2)]
    want = b.literal(source, (0,))
    for flat in itertools.product(range(-4, 4), repeat=4):
        target = list(zip(flat[::2], flat[1::2]))
        expected = [tuple(b.signed_xor(x, y, 5) for x, y in zip(a, c)) for a, c in zip(target, want)]
        b.clean_oracle(source, target, 5)
        b.need(target == expected, 'exhaustive arbitrary target')
        counts['rank1_targets'] += 1
    fail(lambda: b.clean_oracle(source, [(0, 0)]*2, 8,
                               work=[[(1, 0), (0, 0)], [(0, 0)]*2, [(0, 0)]*2]), 'clean work')
    fail(lambda: b.clean_oracle(source, source, 8), 'alias')
    fail(lambda: b.clean_oracle([(15, 15), (15, -15)], [(0, 0)]*2, 5), 'headroom')
    fail(lambda: b.clean_oracle([(-1, 0)]+[(0, 0)]*63, [(0, 0)]*64, 4),
         'narrow signed headroom')
    work = [[(0, 0)]*2 for _ in range(3)]
    b.clean_oracle(source, [(0, 0)]*2, 8, work=work, clean_return=False)
    b.need(any(z != (0, 0) for a in work for z in a), 'missing cleanup control')
    meter = Counter()
    b.blocked([(j-9, 3-j) for j in range(128)], b.partition(7, 3), width=32, meter=meter)
    wrong = b.invoice(7, b.partition(7, 3))
    wrong['backend_xor_calls'] //= 2
    b.need(dict(meter) != wrong, 'missing inverse backend tariff control')
    return dict(status='PASS_P104_BLOCKWISE_LIFTING', coverage=dict(counts),
                controls=['dirty_work', 'aliased_source_target', 'insufficient_headroom',
                          'signed_residue_bank_width', 'omitted_cleanup', 'omitted_inverse_backend_calls'],
                rank7_cap3_invoice=b.invoice(7, b.partition(7, 3)),
                source_commit='b12bbaeb5ca2e83f15433fc2dd0ba3b766595281',
                proof_level='finite exact macros plus separate written conditional proof',
                no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    raw = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.out:
        with args.out.open('x') as f:
            f.write(raw)
    else:
        expected = json.loads((ROOT/'RESULT.json').read_text())
        b.need(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True), 'typed receipt mismatch')
    print(raw, end='')


if __name__ == '__main__':
    main()
