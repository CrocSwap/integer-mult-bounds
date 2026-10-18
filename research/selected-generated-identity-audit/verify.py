#!/usr/bin/env python3
"""Audit the selected-lineage seven-artifact projection, not supplier mathematics.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODE = 'research/gauge44-slots-t16/code/generated_identity.py'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
RECEIPT = 'research/community-frontier1042-audit/RESULT.json'
MANIFEST = 'research/community-frontier1094-audit/SELECTED-SOURCE.json'
FILES = ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json',
         'INDEPENDENT-LOCAL-REPLAY.json', 'CLIFFORD-RECIPES.json',
         'CLIFFORD-REVIEW.json', 'RESIDUAL-ADAPTERS.json')
NATIVE, PHASE = FILES[3], FILES[5]
REFERENCES = {NATIVE: {'canonical_word_sha256': FILES[0], 'local_programs_sha256': FILES[1]},
              PHASE: {'canonical_word_sha256': FILES[0], 'recipe_sha256': FILES[4]}}
INPUTS = {CODE, ARCHIVE, RECEIPT, MANIFEST}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def quoted(value):
    """Independent ASCII JSON string encoder, including UTF-16 surrogate pairs."""
    escapes = {'"': '\\"', '\\': '\\\\', '\b': '\\b', '\f': '\\f',
               '\n': '\\n', '\r': '\\r', '\t': '\\t'}
    yield b'"'
    for char in value:
        code = ord(char)
        if char in escapes:
            yield escapes[char].encode('ascii')
        elif 32 <= code < 127:
            yield char.encode('ascii')
        elif code <= 0xffff:
            yield ('\\u%04x' % code).encode('ascii')
        else:
            code -= 0x10000
            yield ('\\u%04x\\u%04x' % (0xd800 + (code >> 10), 0xdc00 + (code & 1023))).encode('ascii')
    yield b'"'


def encode(value):
    """All-field canonical encoder for the actual retained scalar domain.

    This does not call json.dumps or any function from the audited module.
    The only float in the input trees is the explicitly excluded phase time.
    """
    if value is None:
        yield b'null'
    elif type(value) is bool:
        yield b'true' if value else b'false'
    elif type(value) is int:
        yield str(value).encode('ascii')
    elif type(value) is str:
        yield from quoted(value)
    elif type(value) is list:
        yield b'['
        for index, child in enumerate(value):
            if index:
                yield b','
            yield from encode(child)
        yield b']'
    elif type(value) is dict:
        need(all(type(key) is str for key in value), 'non-string object key')
        yield b'{'
        for index, key in enumerate(sorted(value)):
            if index:
                yield b','
            yield from quoted(key)
            yield b':'
            yield from encode(value[key])
        yield b'}'
    else:
        raise ValueError('outside audited scalar domain: ' + type(value).__name__)


def identity(value):
    result = hashlib.sha256()
    for chunk in encode(value):
        result.update(chunk)
    return result.hexdigest()


def walk(value, path=()):
    """Visit every node, including containers, keys and list positions."""
    yield path, value
    if type(value) is dict:
        for key in sorted(value):
            yield from walk(value[key], path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from walk(child, path + (index,))


def tree(value):
    """Independent typed-path census; distinguishes true, 1 and container shapes."""
    transcript = hashlib.sha256()
    kinds = Counter()
    for path, node in walk(value):
        kind = type(node).__name__
        kinds[kind] += 1
        content = sorted(node) if kind == 'dict' else len(node) if kind == 'list' else node
        for chunk in encode([list(path), kind, content]):
            transcript.update(chunk)
        transcript.update(b'\n')
    return {'nodes': sum(kinds.values()), 'types': dict(sorted(kinds.items())),
            'typed_path_sha256': transcript.hexdigest()}


def expected_value(name, objects, raw):
    value = copy.deepcopy(objects[name])
    if name == PHASE:
        del value['seconds']
    for field, target in REFERENCES.get(name, {}).items():
        need(value[field] == digest(raw[target]), 'reference fixture mismatch: ' + field)
        value[field] = digest(gzip.decompress(raw[target])) if target.endswith('.gz') else identity(objects[target])
    return value


def bind_sources(root=ROOT):
    sources = load((HERE / 'SOURCES.json').read_bytes())
    inputs = {row['path']: row['sha256'] for row in sources['files'] if row['usage'] == 'input'}
    need(set(inputs) == INPUTS, 'mandatory input inventory')
    for name, expected in inputs.items():
        need(digest((root / name).read_bytes()) == expected, 'immutable source pin: ' + name)
    manifest = load((root / MANIFEST).read_bytes())
    need(manifest['files'][CODE] == inputs[CODE], 'selected-lineage implementation binding')


def materialize(directory):
    receipt = load((ROOT / RECEIPT).read_bytes())
    raw = {}
    with tarfile.open(ROOT / ARCHIVE) as archive:
        for member in archive:
            if member.name not in {'slots/local/' + name for name in FILES}:
                continue
            name = member.name.removeprefix('slots/local/')
            need(member.isfile() and name not in raw, 'regular unique chosen archive member')
            raw[name] = archive.extractfile(member).read()
            need(digest(raw[name]) == receipt['artifacts'][member.name], 'archived artifact pin: ' + name)
    need(set(raw) == set(FILES), 'complete seven-artifact input')
    for name, data in raw.items():
        (directory / name).write_bytes(data)
    return raw


def audit():
    need(__debug__, 'audited implementation requires enabled assertions')
    bind_sources()
    source = runpy.run_path(str(ROOT / CODE))
    need(tuple(source['FILES']) == FILES, 'artifact inventory changed')
    controls = []
    positives = []
    with tempfile.TemporaryDirectory(prefix='selected-generated-identity-') as temporary:
        directory = Path(temporary)
        raw = materialize(directory)
        objects = {name: load(gzip.decompress(data) if name.endswith('.gz') else data)
                   for name, data in raw.items()}
        baseline = source['artifact_identities'](directory)
        coverage = {}
        for name in FILES:
            value = expected_value(name, objects, raw)
            # Payloads intentionally bind byte serialization, not parsed JSON.
            expected = digest(gzip.decompress(raw[name])) if name.endswith('.gz') else identity(value)
            need(baseline[name] == expected, 'independent complete-tree identity: ' + name)
            if name in REFERENCES:
                actual = source['phase_value' if name == PHASE else 'native_value'](directory)
                need(tree(actual) == tree(value), 'typed-path projection coverage: ' + name)
            coverage[name] = {**tree(value), 'identity_sha256': expected,
                              'comparison_domain': 'complete decompressed bytes' if name.endswith('.gz') else 'complete canonical JSON tree',
                              'payload_bytes': len(gzip.decompress(raw[name])) if name.endswith('.gz') else None}
        positives.append('independent_all_field_identity_and_typed_path_projection')

        def rejected(label, action):
            try:
                action()
            except (AssertionError, KeyError, ValueError):
                controls.append(label)
            else:
                raise ValueError('accepted negative control: ' + label)

        def receipt_equal(name, value):
            projected = source['phase_value' if name == PHASE else 'native_value'](directory, value)
            need(source['json_identity'](projected) == baseline[name], 'changed receipt identity')

        census = {}
        for name in (NATIVE, PHASE):
            before = len(controls)
            for path, value in walk(objects[name]):
                if not path:
                    continue
                for operation in ('omit', 'replace'):
                    if name == PHASE and path == ('seconds',) and operation == 'replace':
                        continue  # Valid timing changes are a documented positive control.
                    changed = copy.deepcopy(objects[name])
                    parent = changed
                    for part in path[:-1]:
                        parent = parent[part]
                    if operation == 'omit':
                        del parent[path[-1]]
                    else:
                        parent[path[-1]] = 0 if value is None else None
                    label = name + ':' + operation + ':' + repr(path)
                    rejected(label, lambda n=name, v=changed: receipt_equal(n, v))
            census[name] = len(controls) - before
        for name, path in ((NATIVE, ('local', 'forward', 'private_work_erased')),
                           (PHASE, ('all_child_equalities_include_global_phase',))):
            changed = copy.deepcopy(objects[name])
            parent = changed
            for part in path[:-1]:
                parent = parent[part]
            parent[path[-1]] = 1
            rejected(name + ':boolean_to_integer', lambda n=name, v=changed: receipt_equal(n, v))
        for name in (NATIVE, PHASE):
            changed = copy.deepcopy(objects[name])
            changed['unfamiliar'] = {'seconds': 1, 'proof': True}
            rejected(name + ':unfamiliar_nested_seconds', lambda n=name, v=changed: receipt_equal(n, v))
        for value in (-1, True, '1', None, float('inf'), float('nan')):
            changed = dict(objects[PHASE], seconds=value)
            rejected('phase_invalid_seconds:' + repr(value), lambda v=changed: receipt_equal(PHASE, v))
        for value in (0, 1.25, 100000):
            receipt_equal(PHASE, dict(objects[PHASE], seconds=value))
            positives.append('phase_valid_seconds:' + repr(value))

        def restore():
            for name, data in raw.items():
                (directory / name).write_bytes(data)

        def rebind():
            for name, references in REFERENCES.items():
                value = load((directory / name).read_bytes())
                for field, target in references.items():
                    value[field] = digest((directory / target).read_bytes())
                (directory / name).write_text(json.dumps(value), encoding='utf-8')

        def equal():
            need(source['artifact_identities'](directory) == baseline, 'changed artifact identities')

        for level in (1, 9):
            for name in FILES[:2]:
                restore()
                fresh = gzip.compress(gzip.decompress(raw[name]), compresslevel=level, mtime=123)
                need(fresh != raw[name], 'recompression control must change container')
                (directory / name).write_bytes(fresh)
                rejected(name + ':stale_raw_reference:level' + str(level), equal)
                rebind()
                equal()
                positives.append(name + ':recompressed:level' + str(level))
        restore()
        for name in FILES[2:]:
            (directory / name).write_text(json.dumps(objects[name], sort_keys=True, indent=3), encoding='utf-8')
        rejected('recipe_reformatted_with_stale_raw_reference', equal)
        rebind()
        equal()
        positives.append('all_plain_JSON_reformatted_with_bound_recipe_reference')
        for name in FILES:
            restore()
            changed = copy.deepcopy(objects[name])
            key = next(iter(changed))
            del changed[key]
            data = json.dumps(changed).encode()
            (directory / name).write_bytes(gzip.compress(data, mtime=0) if name.endswith('.gz') else data)
            rebind()  # Do not let stale references substitute for detecting lost content.
            rejected(name + ':omitted_root_field_with_rebound_references:' + key, equal)
        for name in FILES[:2]:
            restore()
            # Even harmless JSON whitespace is proof-payload byte drift here.
            (directory / name).write_bytes(gzip.compress(gzip.decompress(raw[name]) + b'\n', mtime=0))
            rebind()
            rejected(name + ':decompressed_serialization_drift', equal)
            restore()
            (directory / name).write_bytes(raw[name][:-8])
            rebind()
            try:
                equal()
            except (EOFError, gzip.BadGzipFile):
                controls.append(name + ':truncated_gzip')
            else:
                raise ValueError('accepted truncated gzip')
    return {'status': 'PASS_SELECTED_GENERATED_IDENTITY_AUDIT',
            'coverage': coverage, 'receipt_mutation_census': census,
            'raw_reference_slots': REFERENCES,
            'excluded_pointer': 'CLIFFORD-REVIEW.json#/seconds',
            'positive_controls': positives, 'negative_controls': controls,
            'scope': 'Exact retained-input projection audit; no supplier rerun, cross-OS replay, full theorem or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = audit()
    target = HERE / 'RESULT.json'
    if args.write_result:
        need(not target.exists(), 'refusing to overwrite audit result')
        target.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    else:
        need(identity(result) == identity(load(target.read_bytes())), 'stored result mismatch')
    print(result['status'], 'nodes=' + str(sum(row['nodes'] for row in result['coverage'].values())),
          'receipt_mutations=' + str(sum(result['receipt_mutation_census'].values())),
          'positives=' + str(len(result['positive_controls'])),
          'negatives=' + str(len(result['negative_controls'])))


if __name__ == '__main__':
    main()
