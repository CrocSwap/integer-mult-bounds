#!/usr/bin/env python3
"""Source-bound comparison audit; no supplier execution or network.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compare as strict

ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
LEGACY = 'research/selected-final-stage-portability/compare_payloads.py'
INPUTS = frozenset((ARCHIVE, LEGACY,
    'research/selected-final-stage-portability/README.md',
    'research/community-frontier1094-audit/RESULT.json',
    'research/community-frontier1094-audit/REPLAY.json',
    'research/community-frontier1094-audit/ASSEMBLY.json'))
REF_PAIRS = (('<WORK>', '/private/tmp/batch1099-selected/candidate'),
             ('<LOCAL>', '/private/tmp/batch1047-selected/slots/local'))
RUN_PAIRS = (('<WORK>', '/relocated/replay'), ('<LOCAL>', '/relocated/local'))
RECEIPTS = ('INDEPENDENT-T16.json', 'REPLAY.json', 'STAGES.json')


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def bound_inputs(root=ROOT):
    manifest = strict.read_json((HERE / 'SOURCES.json').read_bytes())
    rows = [r for r in manifest['files'] if r['usage'] == 'input']
    check(len(rows) == len(INPUTS) and {r['path'] for r in rows} == INPUTS,
          'source input inventory differs')
    result = {}
    for row in rows:
        raw = (root / row['path']).read_bytes()
        check(sha(raw) == row['sha256'], 'source SHA256 mismatch: ' + row['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        check(blob == row['git_blob'], 'source Git blob mismatch: ' + row['path'])
        result[row['path']] = raw
    return result


def corpus(inputs):
    result = {}
    with tarfile.open(fileobj=io.BytesIO(inputs[ARCHIVE])) as archive:
        names = [m.name for m in archive.getmembers()]
        check(len(names) == len(set(names)), 'duplicate archive member')
        prefix = 'candidate/strict/'
        for member in archive.getmembers():
            if not member.name.startswith(prefix) or member.isdir():
                continue
            check(member.isfile(), 'nonregular corpus member')
            name = member.name[len(prefix):]
            check(name and not name.startswith('/') and '..' not in name.split('/'),
                  'invalid corpus member name')
            result[name] = archive.extractfile(member).read()
        check(archive.extractfile('RESULT.json').read() ==
              inputs['research/community-frontier1094-audit/RESULT.json'],
              'archived review receipt differs')
    check(len(result) == 105, 'reviewed corpus must contain 105 files')
    for name in ('ASSEMBLY.json', 'REPLAY.json'):
        check(result[name] == inputs['research/community-frontier1094-audit/' + name],
              'archived ' + name + ' differs')
    receipt = strict.read_json(inputs['research/community-frontier1094-audit/RESULT.json'])
    check(sha(result['ASSEMBLY.json']) == receipt['assembly_sha256'], 'assembly receipt binding')
    return result


def legacy_module():
    spec = importlib.util.spec_from_file_location('pinned_pr1824_comparator', ROOT / LEGACY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def leaves(node, path=()):
    if type(node) is dict:
        for key, value in sorted(node.items()):
            yield from leaves(value, path + (key,))
    elif type(node) is list:
        for i, value in enumerate(node):
            yield from leaves(value, path + (i,))
    else:
        yield path, node


def replace(node, path, value):
    result = copy.deepcopy(node)
    parent = result
    for component in path[:-1]:
        parent = parent[component]
    parent[path[-1]] = value
    return result


def label(result):
    return result['cls'] + (':' + result['verdict'] if 'verdict' in result else '')


def audit(inputs, data):
    legacy = legacy_module()  # only after exact source admission
    ref_roots, run_roots = strict.Roots(REF_PAIRS), strict.Roots(RUN_PAIRS)
    expected_policy = {'REPLAY.json': [['stages', i, 'seconds'] for i in range(11)],
                       'STAGES.json': [[i, 'seconds'] for i in range(11)]}
    policy = strict.read_json((HERE / 'TIMINGS.json').read_bytes())
    check(encoded(policy) == encoded(expected_policy), 'timing policy differs from exact 22 paths')
    positive = Counter()
    for name, raw in sorted(data.items()):
        result = strict.classify(name, raw, raw, timing_paths=policy.get(name, ()))
        check(label(result) == 'bytes', 'unchanged corpus rejected: ' + name)
        positive['unchanged_files'] += 1
        if name.endswith('.gz'):
            altered = gzip.compress(gzip.decompress(raw), compresslevel=1, mtime=12345)
            result = strict.classify(name, raw, altered)
            check(label(result) == 'gzip-container', 'valid recompression rejected: ' + name)
            positive['recompressed_files'] += 1
        elif name.endswith('.json'):
            # Independent fixture producer; acceptance still uses exact Decimal
            # parsing and complete trees, not this ordinary parser's equality.
            altered = json.dumps(json.loads(raw), sort_keys=True, indent=3).encode()
            result = strict.classify(name, raw, altered, timing_paths=policy.get(name, ()))
            check(label(result) == 'json-format', 'valid reformat rejected: ' + name)
            positive['reformatted_files'] += 1

    # Construct a complete relocation/time fixture without executing a supplier.
    relocated = dict(data)
    value = json.loads(data['INDEPENDENT-T16.json'])
    relocated_keys = {}
    for key, digest in value['input_sha256'].items():
        matches = [(old, new) for (_, old), (_, new) in zip(REF_PAIRS, RUN_PAIRS)
                   if key.startswith(old + '/')]
        check(len(matches) == 1, 'fixture path must match exactly one source root')
        old, new = matches[0]
        relocated_keys[new + key[len(old):]] = digest
    check(len(relocated_keys) == 6, 'six distinct input roles required')
    value['input_sha256'] = relocated_keys
    relocated['INDEPENDENT-T16.json'] = encoded(value)
    for name in ('REPLAY.json', 'STAGES.json'):
        value = json.loads(data[name])
        stages = value['stages'] if type(value) is dict else value
        for i, stage in enumerate(stages):
            stage['seconds'] = 1000 + i
        relocated[name] = encoded(value)
    classes = Counter(label(strict.classify(name, raw, relocated[name], ref_roots, run_roots,
                                            policy.get(name, ())))
                      for name, raw in sorted(data.items()))
    check(dict(classes) == {'bytes': 102, 'json-relocated': 1, 'json-diff:declared-timing': 2},
          'complete relocation/timing fixture differs')

    witnesses = []
    with tempfile.TemporaryDirectory(prefix='strict-payload-audit-') as temporary:
        reference, candidate = Path(temporary) / 'reference.json', Path(temporary) / 'candidate.json'

        def witness(kind, name, changed, path, old_expected, roots=False):
            reference.write_bytes(data[name])
            candidate.write_bytes(changed)
            mappings = REF_PAIRS if roots else ()
            old = legacy.classify(reference, candidate, mappings, mappings)
            new = strict.classify(name, data[name], changed,
                                  ref_roots if roots else strict.EMPTY_ROOTS,
                                  ref_roots if roots else strict.EMPTY_ROOTS,
                                  policy.get(name, ()))
            check(label(old) == old_expected, 'legacy witness not reproduced: ' + kind)
            check(not strict.accepted(new), 'strict comparison missed: ' + kind)
            witnesses.append({'kind': kind, 'file': name, 'path': list(path),
                              'candidate_sha256': sha(changed), 'legacy': label(old),
                              'strict': label(new)})

        # Exhaustive for Boolean and integer 0/1 leaves of these three receipts,
        # not for the large generated word arrays in the other corpus files.
        for name in RECEIPTS:
            original = json.loads(data[name])
            for path, value in leaves(original):
                if type(value) is bool:
                    changed = int(value)
                elif type(value) is int and value in (0, 1):
                    changed = bool(value)
                else:
                    continue
                witness('boolean-integer', name, encoded(replace(original, path, changed)),
                        path, 'json-format')

        name = 'INDEPENDENT-T16.json'
        original = json.loads(data[name])
        for key, digest in sorted(original['input_sha256'].items()):
            tokenized = legacy.relocate(key, REF_PAIRS)
            check(tokenized != key, 'fixture input is outside the known roots')
            changed = copy.deepcopy(original)
            del changed['input_sha256'][key]
            changed['input_sha256'][tokenized] = digest
            witness('literal-placeholder-replacement', name, encoded(changed),
                    ('input_sha256', key), 'json-relocated', roots=True)
            changed = copy.deepcopy(original)
            changed['input_sha256'] = {tokenized: '0' * 64, **original['input_sha256']}
            # Preserve order so the path overwrites the conflicting literal key.
            raw = json.dumps(changed, separators=(',', ':')).encode()
            witness('relocation-key-collapse', name, raw, ('input_sha256', key),
                    'json-relocated', roots=True)

        raw = data[name]
        needle = b'"local_profile_recounted": true'
        check(raw.count(needle) == 1, 'duplicate-key fixture source shape')
        changed = raw.replace(needle, b'"local_profile_recounted": false, ' + needle)
        witness('duplicate-key', name, changed, ('local_profile_recounted',), 'json-format')
        needle = b'"local_prefix_bits": 68'
        check(raw.count(needle) == 1, 'decimal fixture source shape')
        changed = raw.replace(needle, b'"local_prefix_bits": 68.000000000000000000000001')
        witness('exact-decimal-perturbation', name, changed, ('local_prefix_bits',), 'json-format')

    timing_rejections = 0
    for name, paths in policy.items():
        original = json.loads(data[name])
        for path in paths:
            changed = copy.deepcopy(original)
            parent = changed
            for component in path[:-1]:
                parent = parent[component]
            del parent[path[-1]]
            result = strict.classify(name, data[name], encoded(changed), timing_paths=paths)
            check(result['cls'] == 'invalid', 'missing declared timing was accepted')
            timing_rejections += 1

    kinds = Counter(w['kind'] for w in witnesses)
    check(dict(kinds) == {'boolean-integer': 25, 'literal-placeholder-replacement': 6,
                         'relocation-key-collapse': 6, 'duplicate-key': 1,
                         'exact-decimal-perturbation': 1}, 'mutation coverage changed')
    return {'schema_version': 1, 'result_kind': 'scoped-audit-and-opt-in-tool',
            'base_commit': 'c676548106012571fefa1dce0ec16f1bcfe11dce',
            'archive_sha256': sha(inputs[ARCHIVE]), 'legacy_sha256': sha(inputs[LEGACY]),
            'corpus_files': len(data), 'positive_controls': dict(sorted(positive.items())),
            'relocation_timing_classes': dict(sorted(classes.items())),
            'legacy_false_equivalence_counts': dict(sorted(kinds.items())),
            'legacy_false_equivalences': witnesses,
            'missing_timing_fields_rejected': timing_rejections,
            'scope': 'Comparison audit only; no cold replay, supplier admission or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--write-result', action='store_true', help='create RESULT.json exclusively')
    args = parser.parse_args()
    inputs = bound_inputs()
    result = audit(inputs, corpus(inputs))
    if args.write_result:
        with (HERE / 'RESULT.json').open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write('\n')
    else:
        stored = strict.read_json((HERE / 'RESULT.json').read_bytes())
        check(encoded(result) == encoded(stored), 'complete audit receipt differs')
    print('PASS_STRICT_REPLAY_PAYLOAD_COMPARISON files=105 false_equivalences=39 '
          'type_cases=25 path_cases=12 timing_rejections=22 no_new_kappa')


if __name__ == '__main__':
    main()
