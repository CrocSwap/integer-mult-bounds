#!/usr/bin/env python3
"""Strict, opt-in comparison of generated replay payloads (standard library).

This does not authenticate a replay or replace immutable source hashes.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from decimal import Decimal, InvalidOperation
import gzip
import json
from pathlib import Path, PurePosixPath
import sys
import zlib


class InvalidPayload(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidPayload(message)


def read_json(raw):
    """Reject ambiguous objects; preserve every JSON number exactly."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key: ' + repr(key))
            result[key] = value
        return result

    def constant(value):
        raise InvalidPayload('nonfinite JSON constant: ' + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_float=Decimal,
                      parse_constant=constant)


class Roots:
    """Injective lexical POSIX path map; path tags cannot equal literal text."""
    def __init__(self, pairs=()):
        self.pairs = []
        tokens, prefixes = set(), set()
        for token, prefix in pairs:
            require(type(token) is str and bool(token), 'empty root token')
            require(type(prefix) is str and prefix.startswith('/'),
                    'root must be an absolute POSIX path')
            require(str(PurePosixPath(prefix)) == prefix and
                    not prefix.startswith('//') and '..' not in prefix.split('/'),
                    'root must be lexically canonical')
            require(token not in tokens, 'duplicate root token: ' + token)
            require(prefix not in prefixes, 'duplicate root prefix: ' + prefix)
            tokens.add(token)
            prefixes.add(prefix)
            self.pairs.append((token, prefix))
        self.tokens = frozenset(tokens)
        self.pairs.sort(key=lambda pair: -len(pair[1]))

    def string(self, value):
        for token, prefix in self.pairs:
            if value == prefix:
                return ('path', token, '')
            if prefix == '/' and value.startswith('/'):
                return ('path', token, value)
            if value.startswith(prefix + '/'):
                return ('path', token, value[len(prefix):])
        return ('string', value)


EMPTY_ROOTS = Roots()


def validate_timings(value, paths):
    require(type(paths) in (list, tuple), 'timing paths must be an array')
    seen = set()
    for path in paths:
        require(type(path) in (tuple, list), 'timing path must be an array')
        require(all(type(p) in (str, int) for p in path), 'invalid timing path component')
        path = tuple(path)
        require(path not in seen, 'duplicate timing path')
        seen.add(path)
        node = value
        for component in path:
            if type(node) is dict and type(component) is str:
                require(component in node, 'missing timing field: ' + repr(path))
            elif type(node) is list and type(component) is int:
                require(0 <= component < len(node), 'missing timing index: ' + repr(path))
            else:
                raise InvalidPayload('timing path has wrong shape: ' + repr(path))
            node = node[component]
        require(type(node) in (int, Decimal), 'timing must be numeric, not Boolean/string')
        require(node >= 0 and (type(node) is int or node.is_finite()),
                'timing must be finite and nonnegative')
    return frozenset(seen)


def tree(value, roots=EMPTY_ROOTS, timings=frozenset(), path=()):
    """A tagged, lossless tree, except for explicitly declared path/time quotients."""
    if path in timings:
        return ('timing',)
    if type(value) is dict:
        items = [(roots.string(k), tree(v, roots, timings, path + (k,)))
                 for k, v in value.items()]
        require(len({k for k, _ in items}) == len(items), 'relocation key collision')
        return ('object', tuple(sorted(items)))
    if type(value) is list:
        return ('array', tuple(tree(v, roots, timings, path + (i,))
                               for i, v in enumerate(value)))
    if type(value) is str:
        return roots.string(value)
    if type(value) is bool:
        return ('boolean', value)
    if value is None:
        return ('null',)
    if type(value) is int:
        return ('integer', value)
    if type(value) is Decimal:
        require(value.is_finite(), 'nonfinite decimal')
        return ('decimal', value)
    raise InvalidPayload('unsupported JSON type: ' + type(value).__name__)


def first_difference(a, b, path=()):
    """Diagnostic typed path; equality is checked on the entire tagged trees."""
    if a == b:
        return None
    if a[0] == b[0] == 'object':
        left, right = dict(a[1]), dict(b[1])
        for key in sorted(left.keys() | right.keys()):
            if key not in left or key not in right:
                return {'path': [*path, list(key)], 'kind': 'missing-or-extra-key'}
            diff = first_difference(left[key], right[key], (*path, list(key)))
            if diff:
                return diff
    elif a[0] == b[0] == 'array':
        if len(a[1]) != len(b[1]):
            return {'path': list(path), 'kind': 'array-length'}
        for i, (x, y) in enumerate(zip(a[1], b[1])):
            diff = first_difference(x, y, (*path, i))
            if diff:
                return diff
    return {'path': list(path), 'kind': 'value-or-type',
            'reference': repr(a)[:160], 'run': repr(b)[:160]}


def classify(name, reference, run, ref_roots=EMPTY_ROOTS, run_roots=EMPTY_ROOTS,
             timing_paths=()):
    require(ref_roots.tokens == run_roots.tokens, 'root-token sets must agree')
    compressed = name.endswith('.gz')
    json_name = name[:-3] if compressed else name
    try:
        a = gzip.decompress(reference) if compressed else reference
        b = gzip.decompress(run) if compressed else run
        if not json_name.endswith('.json'):
            require(not timing_paths, 'timing policy on a non-JSON file')
            if reference == run:
                return {'cls': 'bytes'}
            return {'cls': 'gzip-container' if a == b else 'binary-diff'}
        ja, jb = read_json(a), read_json(b)
        # Validate even byte-identical inputs: identical malformed JSON is not
        # positive evidence, nor is a missing/invalid declared time field.
        ta, tb = validate_timings(ja, timing_paths), validate_timings(jb, timing_paths)
        # Equal payload bytes with the same path interpretation need no tree
        # allocation. Parsing and time validation above still run in full.
        if a == b and ref_roots.pairs == run_roots.pairs:
            return {'cls': 'bytes' if reference == run else 'gzip-container'}
        relocated_a, relocated_b = tree(ja, ref_roots), tree(jb, run_roots)
        if relocated_a == relocated_b:
            if reference == run:
                return {'cls': 'bytes'}
            if a == b:
                return {'cls': 'gzip-container'}
            if not ref_roots.pairs and not run_roots.pairs:
                return {'cls': 'json-format'}
            if tree(ja) == tree(jb):
                return {'cls': 'json-format'}
            return {'cls': 'json-relocated'}
        timed_a = tree(ja, ref_roots, ta) if ta else relocated_a
        timed_b = tree(jb, run_roots, tb) if tb else relocated_b
        if timed_a == timed_b:
            return {'cls': 'json-diff', 'verdict': 'declared-timing'}
        return {'cls': 'json-diff', 'verdict': 'proof-relevant-candidate',
                'first_difference': first_difference(timed_a, timed_b)}
    except (ValueError, UnicodeError, OSError, EOFError, zlib.error, InvalidOperation) as exc:
        return {'cls': 'invalid', 'reason': str(exc)}


def accepted(result):
    return result['cls'] in {'bytes', 'gzip-container', 'json-format', 'json-relocated'} or (
        result['cls'] == 'json-diff' and result['verdict'] == 'declared-timing')


def inventory(root):
    require(root.is_dir(), 'comparison root is not a directory: ' + str(root))
    require(not root.is_symlink(), 'comparison root must not be a symlink')
    result = {}
    for path in sorted(root.rglob('*')):
        require(not path.is_symlink(), 'symlink outside the file-comparison contract')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path
    return result


def compare(reference, run, ref_roots=EMPTY_ROOTS, run_roots=EMPTY_ROOTS, timings=None):
    require(ref_roots.tokens == run_roots.tokens, 'root-token sets must agree')
    timings = timings or {}
    left, right = inventory(reference), inventory(run)
    require(set(timings) <= left.keys() & right.keys(), 'timing policy names absent files')
    result = {}
    for name in sorted(left.keys() | right.keys()):
        if name not in right:
            result[name] = {'cls': 'missing'}
        elif name not in left:
            result[name] = {'cls': 'extra'}
        else:
            result[name] = classify(name, left[name].read_bytes(), right[name].read_bytes(),
                                    ref_roots, run_roots, timings.get(name, ()))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('reference', type=Path)
    parser.add_argument('run', type=Path)
    parser.add_argument('--ref-root', action='append', default=[], metavar='TOKEN=/absolute/path')
    parser.add_argument('--run-root', action='append', default=[], metavar='TOKEN=/absolute/path')
    parser.add_argument('--timings', type=Path, help='JSON object: filename -> exact typed path arrays')
    parser.add_argument('--out', type=Path, help='write detailed JSON to a new file')
    args = parser.parse_args()
    try:
        def roots(values):
            pairs = []
            for value in values:
                token, sep, prefix = value.partition('=')
                require(bool(sep), 'expected TOKEN=/absolute/path')
                pairs.append((token, prefix))
            return Roots(pairs)
        policy = read_json(args.timings.read_bytes()) if args.timings else {}
        require(type(policy) is dict, 'timing policy must be an object')
        result = compare(args.reference, args.run, roots(args.ref_root), roots(args.run_root), policy)
        counts = {}
        for value in result.values():
            key = value['cls'] + (':' + value['verdict'] if 'verdict' in value else '')
            counts[key] = counts.get(key, 0) + 1
        report = {'equivalent': all(map(accepted, result.values())), 'counts': counts, 'files': result}
        if args.out:
            with args.out.open('x', encoding='utf-8') as stream:
                json.dump(report, stream, indent=2, sort_keys=True)
                stream.write('\n')
        print(json.dumps({'equivalent': report['equivalent'], 'counts': counts}, sort_keys=True))
        return 0 if report['equivalent'] else 1
    except (ValueError, OSError) as exc:
        print('INVALID_COMPARISON: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
