#!/usr/bin/env python3
"""Opt-in paired traversal preserving PR2040 strict comparison semantics.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
The source comparator by commdata2338 supplies all parsing, policies, inventory,
CLI and negative diagnostics. This private adapter never changes its source.
"""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/strict-replay-payload-comparison/compare.py'


def load_source(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    rows = [r for r in manifest['files'] if r['path'] == SOURCE and r['usage'] == 'input']
    if len(rows) != 1:
        raise ValueError('source comparator inventory differs')
    raw = (root / SOURCE).read_bytes()
    if hashlib.sha256(raw).hexdigest() != rows[0]['sha256']:
        raise ValueError('source comparator SHA256 differs')
    module = types.ModuleType('source_strict_payload')
    module.__file__ = str(root / SOURCE)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


source = load_source()
original_classify = source.classify
EMPTY = source.EMPTY_ROOTS


def paired(a, b, ra=EMPTY, rb=EMPTY, ta=frozenset(), tb=frozenset(), pa=(), pb=()):
    """True only for equal complete tagged trees; allocate no complete tree.

    Timing paths on the two sides retain their original object keys. A mismatch
    need not search the remaining branches: classify delegates that case to the
    original full-tree routine, including its error precedence and diagnostics.
    """
    if pa in ta or pb in tb:
        return pa in ta and pb in tb
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        if not ra.pairs and not rb.pairs:
            if a.keys() != b.keys():
                return False
            return all(paired(v, b[k], ra, rb, ta, tb,
                              pa + (k,) if ta else (), pb + (k,) if tb else ())
                       for k, v in a.items())
        left = {ra.string(k): (k, v) for k, v in a.items()}
        right = {rb.string(k): (k, v) for k, v in b.items()}
        source.require(len(left) == len(a) and len(right) == len(b),
                       'relocation key collision')
        if left.keys() != right.keys():
            return False
        return all(paired(v, right[k][1], ra, rb, ta, tb,
                          pa + (original,) if ta else (),
                          pb + (right[k][0],) if tb else ())
                   for k, (original, v) in left.items())
    if type(a) is list:
        return len(a) == len(b) and all(
            paired(x, y, ra, rb, ta, tb,
                   pa + (i,) if ta else (), pb + (i,) if tb else ())
            for i, (x, y) in enumerate(zip(a, b)))
    if type(a) is str:
        return ra.string(a) == rb.string(b)
    if type(a) is source.Decimal:
        source.require(a.is_finite() and b.is_finite(), 'nonfinite decimal')
    elif type(a) not in (bool, int, type(None)):
        raise source.InvalidPayload('unsupported JSON type: ' + type(a).__name__)
    return a == b


def classify(name, reference, run, ref_roots=EMPTY, run_roots=EMPTY, timing_paths=()):
    source.require(ref_roots.tokens == run_roots.tokens, 'root-token sets must agree')
    compressed = name.endswith('.gz')
    json_name = name[:-3] if compressed else name
    if json_name.endswith('.json'):
        try:
            a = source.gzip.decompress(reference) if compressed else reference
            b = source.gzip.decompress(run) if compressed else run
            ja, jb = source.read_json(a), source.read_json(b)
            ta = source.validate_timings(ja, timing_paths)
            tb = source.validate_timings(jb, timing_paths)
            if a == b and ref_roots.pairs == run_roots.pairs:
                return {'cls': 'bytes' if reference == run else 'gzip-container'}
            if paired(ja, jb, ref_roots, run_roots):
                if reference == run:
                    return {'cls': 'bytes'}
                if a == b:
                    return {'cls': 'gzip-container'}
                if (not ref_roots.pairs and not run_roots.pairs) or paired(ja, jb):
                    return {'cls': 'json-format'}
                return {'cls': 'json-relocated'}
            if (ta or tb) and paired(ja, jb, ref_roots, run_roots, ta, tb):
                return {'cls': 'json-diff', 'verdict': 'declared-timing'}
        except (ValueError, UnicodeError, OSError, EOFError,
                source.zlib.error, source.InvalidOperation):
            # Preserve the original diagnostic and which invalid branch wins.
            pass
    return original_classify(name, reference, run, ref_roots, run_roots, timing_paths)


# Only this authenticated private module is adapted. Its API and CLI are reused.
source.classify = classify
Roots = source.Roots
read_json = source.read_json
accepted = source.accepted
compare = source.compare
InvalidPayload = source.InvalidPayload


if __name__ == '__main__':
    sys.exit(source.main())
