#!/usr/bin/env python3
"""Exact six-role path adapter to PR2101's unchanged complete comparator.

AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
The underlying comparison is Adam Gall's PR2101, retaining the credited
PR2040/PR2059 predicates. This adapter does not execute a supplier.
"""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

HERE = Path(__file__).resolve().parent
RESERVED = {'work': '/__selected_roles__/work', 'local': '/__selected_roles__/local'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_bytes(raw, expected, name):
    require(hashlib.sha256(raw).hexdigest() == expected, 'source drift: ' + name)


def load_predecessor():
    records = json.loads((HERE / 'SOURCES.json').read_bytes())['vendored_sources']
    expected = {'vendor/pr2101/' + name for name in (
        'compare_outputs.py', 'POLICY.json', 'SOURCES.json',
        'vendor/strict_compare.py', 'vendor/invoice_compare.py')}
    require(len(records) == 5 and {r['path'] for r in records} == expected,
            'vendored source inventory differs')
    for row in records:
        check_bytes((HERE / row['path']).read_bytes(), row['sha256'], row['path'])
    spec = importlib.util.spec_from_file_location(
        'pr2101_closed_comparison', HERE / 'vendor/pr2101/compare_outputs.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


predecessor = load_predecessor()


def role_path(root, suffix):
    """Join trusted role suffixes; never normalize a key supplied by a receipt.

    Deliberately narrow spelling policy: canonical POSIX roots or ordinary
    absolute Windows drive roots with backslashes. UNC/device/extended-length
    roots and alternative spelling are unsupported and reject.
    """
    require(type(root) is dict and set(root) == {'style', 'path'}, 'invalid typed root')
    style, value = root['style'], root['path']
    require(type(value) is str and value and '\x00' not in value, 'invalid root path')
    part = PurePosixPath(suffix)
    require(suffix and part.as_posix() == suffix and not part.is_absolute()
            and '..' not in part.parts and '\\' not in suffix and ':' not in suffix,
            'noncanonical role suffix')
    if style == 'posix':
        predecessor.strict.Roots([('root', value)])
        return str(PurePosixPath(value).joinpath(*part.parts))
    require(style == 'windows-drive', 'unsupported root style')
    path = PureWindowsPath(value)
    require(re.fullmatch(r'[A-Za-z]:', path.drive) is not None and path.is_absolute()
            and str(path) == value and '/' not in value and '..' not in path.parts,
            'root must be a canonical absolute Windows drive path')
    # Windows normalizes these lexical aliases. Do not silently identify them.
    for component in path.parts[1:]:
        require(not component.endswith((' ', '.'))
                and not any(c in component for c in '<>:"|?*')
                and all(ord(c) >= 32 for c in component)
                and not PureWindowsPath(component).is_reserved(),
                'unsupported Windows root component')
    return str(path.joinpath(*part.parts))


def adapt(files, context):
    """Authenticate exactly six native role edges, then translate only their keys.

    Caller-supplied roots describe the executed run, not filesystem access:
    this function never opens a receipt path. Literal strings elsewhere and
    all other keys/values remain untouched. PR2101 rechecks the six edges.
    """
    require(type(context) is dict and set(context) == {'work', 'local', 'external'},
            'invalid comparison context')
    require(set(files) == predecessor.NAMES, 'complete 105-file inventory differs')
    external = context['external']
    require(type(external) is dict and set(external) == {'local-word', 'local-replay', 'owners'}
            and all(type(raw) is bytes for raw in external.values()), 'invalid external inputs')
    independent = predecessor.strict.read_json(files['INDEPENDENT-T16.json'])
    require(type(independent) is dict and type(independent.get('input_sha256')) is dict,
            'missing independent input roles')
    expected, translated, identities = {}, {}, set()
    for role in predecessor.POLICY['input_roles']:
        root = context[role['root']]
        native = role_path(root, role['suffix'])
        identity = (root['style'], native.casefold() if root['style'] == 'windows-drive' else native)
        require(identity not in identities and native not in expected, 'colliding input roles')
        identities.add(identity)
        raw = files[role['target']] if 'target' in role else external[role['external']]
        expected[native] = predecessor.digest(raw)
        translated[RESERVED[role['root']] + '/' + role['suffix']] = predecessor.digest(raw)
    require(len(expected) == len(translated) == 6 and
            predecessor.strict.tree(independent['input_sha256']) == predecessor.strict.tree(expected),
            'stale, missing, aliased, or misbound native input role')
    independent['input_sha256'] = translated
    updated = dict(files)
    updated['INDEPENDENT-T16.json'] = predecessor.invoice.canonical(independent)
    return updated, {**RESERVED, 'external': external}


def compare(reference, candidate, reference_context, candidate_context):
    left, left_context = adapt(reference, reference_context)
    right, right_context = adapt(candidate, candidate_context)
    return predecessor.compare(left, right, left_context, right_context)


outer_log = predecessor.outer_log
read_files = predecessor.read_files
