#!/usr/bin/env python3
"""Bind a complete native replay to its word, artifacts, logs and source.

All native files are included. Only the enumerated timing fields are removed;
known receipt hash references are first checked against their actual targets,
then represented by canonical JSON identities for compression portability.
Predecessor credit: PR2288 and its retained notices. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = 't74-native-evidence/1'
SOURCE_HEAD = 'fb76f799ccf078f51780076ebed3fd26b1db11c0'
SOURCE_MANIFEST = 'c545968fb8cf6e550b82ba631e92fd756484db75e621aee211347749cff55313'
LOCAL_FILES = (
    'CANONICAL-WORD.json.gz', 'FULL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz',
    'SCALAR-FRAME-AUDIT.json', 'LOCAL-CHECKS.json',
    'INDEPENDENT-LOCAL-REPLAY.json', 'RESIDUAL-ADAPTERS.json',
    'WRAPPER-CHECKS.json', 'CLIFFORD-RECIPES.json', 'CLIFFORD-REVIEW.json',
    'WARP-RECIPE-CHECKS.json',
)
STEPS = ('native', 'ledgers', 'local-replay', 'wrappers', 'phases')
LOG_FILES = tuple(name + '.log' for name in STEPS)
INVENTORY = tuple(sorted(('STEPS.json',) + LOG_FILES +
                         tuple('local/' + name for name in LOCAL_FILES)))
JSON_TIMINGS = {
    'local/SCALAR-FRAME-AUDIT.json': ('seconds',),
    'local/CLIFFORD-REVIEW.json': ('seconds',),
    'native.log': ('seconds',),
}
REFERENCE_TARGETS = {
    'local/SCALAR-FRAME-AUDIT.json': {
        'input_content_sha256': ('local/FULL-WORD.json.gz', 'payload'),
        'canonical_content_sha256': ('local/CANONICAL-WORD.json.gz', 'payload'),
    },
    'native.log': {
        'input_content_sha256': ('local/FULL-WORD.json.gz', 'payload'),
        'canonical_content_sha256': ('local/CANONICAL-WORD.json.gz', 'payload'),
    },
    'local/INDEPENDENT-LOCAL-REPLAY.json': {
        'canonical_word_sha256': ('local/CANONICAL-WORD.json.gz', 'raw'),
        'local_programs_sha256': ('local/LOCAL-PROGRAMS.json.gz', 'raw'),
    },
    'local/CLIFFORD-REVIEW.json': {
        'canonical_word_sha256': ('local/CANONICAL-WORD.json.gz', 'raw'),
        'recipe_sha256': ('local/CLIFFORD-RECIPES.json', 'raw'),
    },
    'local/WARP-RECIPE-CHECKS.json': {
        'canonical_word_sha256': ('local/CANONICAL-WORD.json.gz', 'raw'),
        'recipe_sha256': ('local/CLIFFORD-RECIPES.json', 'raw'),
    },
}
POLICY = {
    'json': 'UTF-8 JSON, sorted object keys, compact separators; all values retained',
    'compression': 'Gzip headers and encoding are replaced by parsed JSON identity',
    'reference_portability': ('Each reference must match its current target bytes or its pinned '
                              'original target bytes, and the target canonical JSON identity must '
                              'match the pinned target; no other stale references are accepted'),
    'timing_fields': {
        'STEPS.json': ['[0].seconds', '[1].seconds', '[2].seconds',
                       '[3].seconds', '[4].seconds'],
        **{name: ['$.seconds'] for name in JSON_TIMINGS},
    },
    'phase_log_timing': [
        'exact phase edges I / N seconds T: only T',
        'PASS exact local phases T seconds: only T',
    ],
    'paths_ignored': [],
    'hash_references': {
        name: {field: {'target': target, 'checked_encoding': encoding,
                       'replacement': 'canonical-json-sha256'}
               for field, (target, encoding) in fields.items()}
        for name, fields in REFERENCE_TARGETS.items()
    },
    'other_logs': 'Only CRLF versus LF is normalized; every other character is retained',
    'inventory': 'Exact complete file inventory; missing, extra or symlinked entries reject',
}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        _require(key not in result, 'Duplicate JSON object key: ' + key)
        result[key] = value
    return result


def _bad_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def _json(data):
    return json.loads(data, object_pairs_hook=_pairs, parse_constant=_bad_constant)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def canonical_json_sha256(value):
    return _sha(canonical_json(value))


def _payload(path):
    data = path.read_bytes()
    return gzip.decompress(data) if path.suffix == '.gz' else data


def _timing(value, label):
    _require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
             'Invalid timing metadata: ' + label)


def _text(data):
    text = data.decode('utf-8').replace('\r\n', '\n')
    _require('\r' not in text, 'Unexpected bare carriage return in a native log')
    return text


def _source_binding(source_package):
    package = Path(source_package).resolve()
    path = package / 'MANIFEST.json'
    _require(_sha(path.read_bytes()) == SOURCE_MANIFEST,
             'Native source package is not the pinned immutable package')
    inventory = _json(path.read_bytes())
    entries = list(package.rglob('*'))
    _require(all(not entry.is_symlink() for entry in entries),
             'Symlinked source package entries are not accepted')
    actual = {entry.relative_to(package).as_posix(): entry
              for entry in entries if entry.is_file()}
    expected = set(inventory) | {'MANIFEST.json'}
    _require(set(actual) == expected,
             'Source package file inventory differs: missing=%s extra=%s' % (
                 sorted(expected - set(actual)), sorted(set(actual) - expected)))
    for name, digest in inventory.items():
        _require(_sha(actual[name].read_bytes()) == digest,
                 'Immutable package source changed: ' + name)
    paths = sorted(name for name in inventory if name.startswith('new/code/borrow/'))
    paths.append('new/run_native_borrow.py')
    _require(paths and all(name in inventory for name in paths),
             'Missing native pipeline source pins')
    return {'head': SOURCE_HEAD, 'package_manifest_sha256': SOURCE_MANIFEST,
            'complete_package_files': len(expected),
            'complete_package_inventory_verified': True,
            'native_source_sha256': {name: inventory[name] for name in sorted(paths)}}


def _pipeline():
    root = 'new/code/borrow/'
    return {'launcher': 'new/run_native_borrow.py', 'python_flags': ['-B'],
        'working_directory': 'new/code/borrow',
        'steps': [
            {'step': 'native', 'commands': [[root + 'bw_transport.py', '<input-word>', '<native>/local']]},
            {'step': 'ledgers', 'commands': [[root + 'bw_emit.py', '<native>/local']]},
            {'step': 'local-replay', 'commands': [[root + 'bw_audit_local.py', '<native>/local']]},
            {'step': 'wrappers', 'commands': [[root + 'bw_adapters.py',
                '<native>/local/CANONICAL-WORD.json.gz',
                '<native>/local/RESIDUAL-ADAPTERS.json',
                '<native>/local/WRAPPER-CHECKS.json']]},
            {'step': 'phases', 'commands': [[root + 'bw_phases.py', '<native>/local'],
                                          [root + 'bw_check_recipes.py', '<native>/local']]},
        ]}


def _normalized_json(name, value, raw, payloads, documents, reference_targets):
    result = copy.deepcopy(value)
    for field in JSON_TIMINGS.get(name, ()):
        _require(field in result, 'Missing expected timing field: ' + name + '/' + field)
        _timing(result.pop(field), name + '/' + field)
    for field, (target, encoding) in REFERENCE_TARGETS.get(name, {}).items():
        actual = _sha(raw[target] if encoding == 'raw' else payloads[target])
        original = reference_targets[target][encoding + '_sha256']
        _require(result.get(field) in (actual, original),
                 'Stale native artifact reference: ' + name + '/' + field)
        result[field] = canonical_json_sha256(documents[target])
    return result


def _phase_log(text, documents):
    phase = documents['local/CLIFFORD-REVIEW.json']
    warp = documents['local/WARP-RECIPE-CHECKS.json']
    _require(text.endswith('\n') and not text.endswith('\n\n'),
             'Unexpected phase transcript termination')
    lines = text[:-1].split('\n')
    expected_indices = list(range(0, phase['directed_edges'], 200))
    _require(len(lines) == len(expected_indices) + 2,
             'Missing or extra phase transcript lines')
    result = []
    previous = 0.0
    number = r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    for line, index in zip(lines, expected_indices):
        prefix = 'exact phase edges %d / %d seconds ' % (index, phase['directed_edges'])
        match = re.fullmatch(re.escape(prefix) + '(' + number + ')', line)
        _require(match is not None, 'Unrecognized phase progress transcript')
        seconds = float(match[1]); _timing(seconds, 'phases.log/progress')
        _require(seconds >= previous,
                 'Phase progress counts, ordering or timing are inconsistent')
        previous = seconds
        result.append(prefix + '<seconds>')
    match = re.fullmatch(r'PASS exact local phases (' + number + ') seconds', lines[-2])
    _require(match is not None, 'Missing exact local phase completion transcript')
    seconds = float(match[1]); _timing(seconds, 'phases.log/completion')
    _require(seconds >= previous, 'Phase completion precedes its progress transcript')
    result.append('PASS exact local phases <seconds> seconds')
    expected = '%s %d classes %d controls rejected' % (
        warp['status'], warp['warp_classes'], len(warp['controls_rejected']))
    _require(lines[-1] == expected, 'Warp recipe transcript does not match its receipt')
    result.append(lines[-1])
    return '\n'.join(result) + '\n'


def _check_documents(documents):
    c = documents['local/CANONICAL-WORD.json.gz']
    scalar = documents['local/SCALAR-FRAME-AUDIT.json']
    checks = documents['local/LOCAL-CHECKS.json']
    programs = documents['local/LOCAL-PROGRAMS.json.gz']
    independent = documents['local/INDEPENDENT-LOCAL-REPLAY.json']
    phase = documents['local/CLIFFORD-REVIEW.json']
    recipes = documents['local/CLIFFORD-RECIPES.json']
    warp = documents['local/WARP-RECIPE-CHECKS.json']
    wrappers = documents['local/WRAPPER-CHECKS.json']
    _require(scalar['status'] == 'PASS_BORROW_WORD_FREE_ALGEBRA_ALL_COLUMNS_AND_NATIVE_FRAMES',
             'Scalar/frame replay did not pass')
    _require(scalar['helpers'] == c['R'] and scalar['live_columns_each_orientation'] == 2*c['v'] + c['R']
             and scalar['local_profile'] == c['local_profile']
             and scalar['local_rank_mass'] == sum(int(k)*v for k,v in c['local_profile'].items()),
             'Scalar/frame receipt differs from its canonical word')
    _require(set(programs) == set(checks) == {'forward', 'backward'},
             'Both emitted orientations are required')
    for orientation in ('forward', 'backward'):
        _require(checks[orientation]['sha256'] == canonical_json_sha256(programs[orientation]),
                 'Emitted orientation program hash differs')
        _require(checks[orientation]['events'] == len(programs[orientation]) and
                 checks[orientation]['paid_profile'] == c['local_profile'],
                 'Emitted orientation profile or event count differs')
    _require(independent['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY' and
             independent['warp_replay']['status'] == 'PASS_EXACT_MONOMIAL_WARP_COLUMNS_ALL_512_BOTH_ORIENTATIONS' and
             set(independent['local']) == {'forward', 'backward'} and
             all(value == c['local_profile'] for value in independent['paid_profiles'].values()),
             'Independent local replay did not pass both orientations')
    _require(wrappers['status'] == 'PASS_RESIDUAL_WRAPPERS_ARE_EXACT' and
             documents['local/RESIDUAL-ADAPTERS.json']['status'] == 'RESIDUAL_ADAPTER_RECIPES',
             'Exact wrapper evidence is missing')
    _require(phase['status'] == 'PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES' and
             phase['all_child_equalities_include_global_phase'] is True and
             phase['warp_recipes_rank_zero'] is True and
             phase['warp_recipes_equal_exact_512_column_product'] is True and
             phase['endpoint_adapters'] == len(recipes['endpoint_adapters']) == 2*c['v'] and
             phase['directed_edges'] == len(recipes['children']) and
             phase['warp_recipes'] == len(recipes['warps']),
             'Exact phase recipe evidence is missing')
    _require(warp['status'] == 'PASS_WARP_RECIPES_EXACT_ON_ALL_512_COLUMNS' and
             warp['warp_classes'] == len(recipes['warps']) and
             warp['operators'] == len(c['warps']) and warp['columns_each'] == 1 << c['h'],
             'Independent warp recipe evidence is missing')


def _build_manifest(native_dir, source_package, word_path, pinned_targets=None):
    """Return a portable manifest after validating all cached native bindings.

    source_package is the immutable package directory, not its repository root.
    The returned object contains no machine paths or measured timings.
    """
    directory = Path(native_dir).resolve()
    source = _source_binding(source_package)
    entries = list(directory.rglob('*'))
    _require(all(not path.is_symlink() for path in entries), 'Symlinked native evidence is not accepted')
    files = {p.relative_to(directory).as_posix(): p for p in entries if p.is_file()}
    _require(set(files) == set(INVENTORY),
             'Native file inventory differs: missing=%s extra=%s' % (
                 sorted(set(INVENTORY)-set(files)), sorted(set(files)-set(INVENTORY))))
    raw = {name: path.read_bytes() for name, path in files.items()}
    payloads = {name: gzip.decompress(data) if name.endswith('.gz') else data
                for name, data in raw.items()}
    documents = {name: _json(payloads[name])
                 for name in INVENTORY if name.endswith(('.json', '.json.gz'))}
    target_names = {target for fields in REFERENCE_TARGETS.values()
                    for target, encoding in fields.values()}
    reference_targets = {name: {
        'raw_sha256': _sha(raw[name]),
        'payload_sha256': _sha(payloads[name]),
        'canonical_sha256': canonical_json_sha256(documents[name]),
    } for name in sorted(target_names)}
    if pinned_targets is not None:
        _require(isinstance(pinned_targets, dict) and set(pinned_targets) == target_names,
                 'Pinned native reference target inventory differs')
        for name, current in reference_targets.items():
            original = pinned_targets[name]
            _require(isinstance(original, dict) and set(original) == set(current) and
                     all(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
                         for value in original.values()),
                     'Invalid pinned native reference target: ' + name)
            _require(current['canonical_sha256'] == original['canonical_sha256'],
                     'Native reference target semantic identity changed: ' + name)
        reference_targets = copy.deepcopy(pinned_targets)
    input_word = _json(_payload(Path(word_path)))
    _require(documents['local/FULL-WORD.json.gz'] == input_word,
             'Native FULL-WORD differs from the supplied input word')
    steps = documents['STEPS.json']
    _require(isinstance(steps, list) and [row.get('step') for row in steps] == list(STEPS),
             'Native pipeline order differs')
    normalized_steps = copy.deepcopy(steps)
    for row in normalized_steps:
        _require(set(row) == {'step', 'exit_code', 'seconds'} and row['exit_code'] == 0,
                 'A native pipeline step failed or has unexpected metadata')
        _timing(row.pop('seconds'), 'STEPS.json/' + row['step'])
    _check_documents(documents)
    values = {'STEPS.json': normalized_steps}
    for name in documents:
        if name != 'STEPS.json':
            values[name] = _normalized_json(name, documents[name], raw, payloads, documents,
                                           reference_targets)
    native_log = _json(raw['native.log'])
    values['native.log'] = _normalized_json('native.log', native_log, raw, payloads, documents,
                                          reference_targets)
    printed = copy.deepcopy(values['local/SCALAR-FRAME-AUDIT.json'])
    printed.pop('widths')
    _require(values['native.log'] == printed, 'Native transcript differs from its scalar/frame receipt')
    checks = documents['local/LOCAL-CHECKS.json']
    expected = ''.join('PASS emitted %s %d events\n' % (o, checks[o]['events'])
                       for o in ('forward', 'backward'))
    _require(_text(raw['ledgers.log']) == expected, 'Emitted-program transcript differs')
    values['ledgers.log'] = expected
    independent = documents['local/INDEPENDENT-LOCAL-REPLAY.json']
    expected = ('independent emitted replay PASS forward\n'
        'independent emitted replay PASS backward\n%s %s %d controls rejected\n' % (
            independent['status'], independent['warp_replay']['status'],
            len(independent['negative_controls_rejected'])))
    _require(_text(raw['local-replay.log']) == expected, 'Independent replay transcript differs')
    values['local-replay.log'] = expected
    wrappers = documents['local/WRAPPER-CHECKS.json']
    expected = ('Lemma A (exact): L^-1 S_E R^-1 = C_[w] x I for %d entrance frames, '
        'global phase included; %d wrapper mutations rejected; all-even-weight: %s\n' % (
            wrappers['frames'], len(wrappers['wrappers_reject']), wrappers['all_even_weight']))
    _require(_text(raw['wrappers.log']) == expected, 'Wrapper transcript differs')
    values['wrappers.log'] = expected
    values['phases.log'] = _phase_log(_text(raw['phases.log']), documents)
    artifacts = {}
    for name in INVENTORY:
        value = values[name]
        encoded = value.encode('utf-8') if isinstance(value, str) else canonical_json(value)
        artifacts[name] = {'canonical_sha256': _sha(encoded),
                           'encoding': 'normalized-transcript' if isinstance(value, str) else 'canonical-json'}
    return {'schema': SCHEMA, 'source': source, 'pipeline': _pipeline(),
        'input_word_canonical_sha256': canonical_json_sha256(input_word),
        'inventory': list(INVENTORY), 'file_count': len(INVENTORY),
        'reference_targets': reference_targets,
        'artifacts': artifacts, 'normalization_policy': copy.deepcopy(POLICY)}


def build_manifest(native_dir, source_package, word_path):
    """Return all validated portable bindings, including original reference targets."""
    return _build_manifest(native_dir, source_package, word_path)


def validate_manifest(native_dir, source_package, word_path, manifest):
    """Rebuild and compare every binding; return the validated manifest.

    A changed proof field, source file, program, recipe, log, status, inventory
    or hash reference rejects. Only the documented metadata differences pass.
    """
    _require(isinstance(manifest, dict) and manifest.get('schema') == SCHEMA,
             'Unknown native evidence manifest schema')
    actual = _build_manifest(native_dir, source_package, word_path,
                             manifest.get('reference_targets'))
    _require(actual == manifest, 'Native evidence differs from its pinned manifest')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('build', 'validate'))
    parser.add_argument('--native-dir', type=Path, required=True)
    parser.add_argument('--source-package', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    if args.operation == 'build':
        result = build_manifest(args.native_dir, args.source_package, args.word)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_bytes(canonical_json(result) + b'\n')
    else:
        validate_manifest(args.native_dir, args.source_package, args.word,
                          _json(args.manifest.read_bytes()))
    print('PASS_NATIVE_EVIDENCE_MANIFEST', args.operation)


if __name__ == '__main__':
    main()
