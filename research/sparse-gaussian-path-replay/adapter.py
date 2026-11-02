"""Opt-in, source-bound complete PR800 replay. Apache-2.0."""

import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sparse_product import raw_product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    """Check every declared live input before executing any retained source."""
    root = HERE.parents[1]
    sources = json.loads((HERE/'SOURCES.json').read_text())
    inputs = [row for row in sources['files'] if row['usage'] == 'input']
    require(len(inputs) == 17, 'Expected exactly seventeen source inputs')
    for row in inputs:
        path = root/row['path']
        require(path.is_file() and not path.is_symlink(), 'Missing regular input')
        require(path.stat().st_size <= 2**20, 'Input exceeds one MiB')
        require(sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'Source integrity mismatch: '+row['path'])
    return root/'research/weighted-path-valuations'


def load_source(root):
    require(__debug__, 'Run without -O: retained source assertions are required')
    loaded = {}
    for name in ('model', 'dense', 'screen', 'valuation', 'verify'):
        key = '_weighted_source_verify' if name == 'verify' else name
        require(key not in sys.modules, 'Source module already loaded: '+key)
        path = root/(name+'.py')
        module = types.ModuleType(key)
        module.__file__ = str(path)
        sys.modules[key] = module
        # Execute authenticated bytes directly; never read a bytecode cache.
        exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
        loaded[name] = module
    return loaded


def product_counts(a, b):
    """Count Gaussian product evaluations on one cache miss, not cache hits."""
    _, ar, ai = a
    _, br, bi = b
    left = [bool(x or y) for x, y in zip(ar, ai)]
    right = [sum(bool(br[8*k+j] or bi[8*k+j]) for j in range(8))
             for k in range(8)]
    baseline = 8*sum(left)
    sparse = sum(right[k] for i in range(8) for k in range(8) if left[8*i+k])
    require(0 <= sparse <= baseline <= 512, 'Product-count invariant')
    return baseline, sparse


def install(dense, engine, stats):
    reference = dense.multiply

    @lru_cache(maxsize=40_000)
    def sparse(a, b, projective=False):
        return dense.normalize(*raw_product(a, b), projective)

    digest = sha256()

    def compare(a, b, projective=False):
        before = sparse.cache_info().misses
        actual = sparse(a, b, projective)
        expected = reference(a, b, projective)
        require(actual == expected, 'Gaussian product conformance mismatch')
        if sparse.cache_info().misses != before:
            baseline, changed = product_counts(a, b)
            stats['baseline_products'] += baseline
            stats['sparse_products'] += changed
        digest.update(json.dumps([a, b, projective, actual],
                                 separators=(',', ':')).encode()+b'\n')
        stats['calls'] += 1
        return actual

    if engine == 'sparse':
        dense.multiply = sparse
    elif engine == 'compare':
        dense.multiply = compare
    else:
        require(engine == 'reference', 'Unknown engine')
    return sparse, reference, digest


def run(engine):
    source = load_source(authenticate())
    main, dense = source['verify'], source['dense']
    main.check_manifest()
    stats = {'calls': 0, 'baseline_products': 0, 'sparse_products': 0}
    sparse, reference, digest = install(dense, engine, stats)
    report = main.replay()
    expected = json.loads((Path(main.__file__).parent/'EXPECTED.json').read_text())
    require(report == expected, 'Complete source result mismatch')
    if engine == 'compare':
        require(sparse.cache_info() == reference.cache_info(), 'Cache coverage mismatch')
        stats['cache'] = sparse.cache_info()._asdict()
        stats['transcript_sha256'] = digest.hexdigest()
    return report, stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('reference', 'sparse', 'compare'),
                        default='sparse')
    args = parser.parse_args()
    report, stats = run(args.engine)
    value = {'scientific': report, 'conformance': stats} if args.engine == 'compare' else report
    print(json.dumps(value, sort_keys=True))


if __name__ == '__main__':
    main()
