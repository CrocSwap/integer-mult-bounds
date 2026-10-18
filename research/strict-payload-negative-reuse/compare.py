#!/usr/bin/env python3
"""Opt-in PR2693 mismatch diagnostics without repeated JSON parsing.

Nick Petalas. Apache-2.0. Substantial automated assistance was used.
PR2040 by commdata2338 supplies strict semantics; ywz65 supplies paired traversal.
"""
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = 'research/strict-payload-paired-walk/compare.py'


def load_parent(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    expected = {PARENT, 'research/strict-payload-paired-walk/SOURCES.json'}
    rows = [r for r in manifest['files'] if r['path'] in expected and r['usage'] == 'input']
    if len(rows) != len(expected) or {r['path'] for r in rows} != expected:
        raise ValueError('parent comparator inventory differs')
    sources = {}
    for row in rows:
        raw = (root / row['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('parent comparator SHA256 differs: ' + row['path'])
        sources[row['path']] = raw
    module = types.ModuleType('private_paired_payload')
    module.__file__ = str(root / PARENT)
    exec(compile(sources[PARENT], module.__file__, 'exec'), module.__dict__)
    return module


parent = load_parent()
source = parent.source
original_classify = parent.original_classify
EMPTY = parent.EMPTY


def parsed_result(ja, jb, ref_roots, run_roots, ta, tb, reference, run, a, b):
    """The original classifier's tree phase, with its original evaluation order."""
    relocated_a = source.tree(ja, ref_roots)
    relocated_b = source.tree(jb, run_roots)
    if relocated_a == relocated_b:
        if reference == run:
            return {'cls': 'bytes'}
        if a == b:
            return {'cls': 'gzip-container'}
        if not ref_roots.pairs and not run_roots.pairs:
            return {'cls': 'json-format'}
        if source.tree(ja) == source.tree(jb):
            return {'cls': 'json-format'}
        return {'cls': 'json-relocated'}
    timed_a = source.tree(ja, ref_roots, ta) if ta else relocated_a
    timed_b = source.tree(jb, run_roots, tb) if tb else relocated_b
    if timed_a == timed_b:
        return {'cls': 'json-diff', 'verdict': 'declared-timing'}
    return {'cls': 'json-diff', 'verdict': 'proof-relevant-candidate',
            'first_difference': source.first_difference(timed_a, timed_b)}


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
            if parent.paired(ja, jb, ref_roots, run_roots):
                if reference == run:
                    return {'cls': 'bytes'}
                if a == b:
                    return {'cls': 'gzip-container'}
                if (not ref_roots.pairs and not run_roots.pairs) or parent.paired(ja, jb):
                    return {'cls': 'json-format'}
                return {'cls': 'json-relocated'}
            if (ta or tb) and parent.paired(ja, jb, ref_roots, run_roots, ta, tb):
                return {'cls': 'json-diff', 'verdict': 'declared-timing'}
            return parsed_result(ja, jb, ref_roots, run_roots, ta, tb, reference, run, a, b)
        except (ValueError, UnicodeError, OSError, EOFError,
                source.zlib.error, source.InvalidOperation):
            # Speculative failures still use the original error precedence.
            pass
    return original_classify(name, reference, run, ref_roots, run_roots, timing_paths)


# Adapt only the authenticated private instance, including its original CLI.
source.classify = classify
Roots = source.Roots
read_json = source.read_json
accepted = source.accepted
compare = source.compare
InvalidPayload = source.InvalidPayload


if __name__ == '__main__':
    sys.exit(source.main())
