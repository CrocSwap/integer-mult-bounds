#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the narrow derivation of the T248 admission adapter without executing it.

The immutable baseline is Tekalign's PR2839 admission driver. This checker
allows only the declared immutable source/comparison records, two CLI defaults,
and the module docstring to differ in the parsed program. Comments and formatting
have no AST representation. It does not prove the inherited admission theorem.
Prepared with OpenAI Codex assistance for Yiyang Lu.
"""
import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path


BASELINE_SHA256 = '57630311eb90be3d417e7bdeaae03965fef46a97b4b38389ff66805c75276f80'
ADDITIONS = {
    'SOURCE_PROFILES': {
        'pr2833': {
            'commit': 'pr2833-dirtentry',
            'manifest': 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f',
            'helpers': 408,
            'source_file_count': 541,
            'upstream_head': 'e9307b48d7d1b690939935ecef0f8e524e6d92f4',
        },
    },
    'COMPARISONS': {
        'pr2843': {
            'pr': 2843,
            'head': '47a7227c044cd0cabb1432a06c61dd5d60c07f5a',
            'sha256': '0adc0edfade0260c65e79867b6c8b96f58dfe29d38aa30cfb8f3d5e9c7e828d9',
            'field': 'kappa',
        },
        'pr2833': {
            'pr': 2833,
            'head': 'e9307b48d7d1b690939935ecef0f8e524e6d92f4',
            'sha256': '6f2c4195f0226c5a7f9ba604bc038cfd4100ba3caeeac8ed2defb6fb00632b70',
            'field': 'kappa_rational',
        },
    },
}
DEFAULTS = {'--source-profile': 'pr2833', '--comparison-profile': 'pr2843'}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def profile_assignment(tree, name):
    nodes = [node for node in tree.body if isinstance(node, ast.Assign)
             and len(node.targets) == 1
             and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id == name]
    require(len(nodes) == 1, 'exactly one module assignment required: ' + name)
    require(isinstance(nodes[0].value, ast.Dict), 'literal profile dictionary: ' + name)
    keys = [ast.literal_eval(key) for key in nodes[0].value.keys]
    require(all(type(key) is str for key in keys) and len(keys) == len(set(keys)),
            'distinct literal profile keys: ' + name)
    return nodes[0]


def literal_profile(node):
    """Accept the inherited dict(keyword=literal, ...) spelling without execution."""
    values = {}
    for key, value in zip(node.value.keys, node.value.values):
        require(isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                and value.func.id == 'dict' and not value.args,
                'profile record must be dict with literal keyword arguments')
        names = [keyword.arg for keyword in value.keywords]
        require(None not in names and len(names) == len(set(names)),
                'distinct explicit profile fields')
        values[ast.literal_eval(key)] = {
            keyword.arg: ast.literal_eval(keyword.value) for keyword in value.keywords
        }
    return values


def default_keyword(tree, flag):
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument'
             and node.args and isinstance(node.args[0], ast.Constant)
             and node.args[0].value == flag]
    require(len(calls) == 1, 'exactly one CLI declaration: ' + flag)
    defaults = [keyword for keyword in calls[0].keywords if keyword.arg == 'default']
    require(len(defaults) == 1, 'exactly one CLI default: ' + flag)
    return defaults[0]


def remove_module_docstring(tree):
    require(tree.body and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str), 'module docstring required')
    tree.body.pop(0)


def verify(baseline, adapter):
    require(hashlib.sha256(baseline).hexdigest() == BASELINE_SHA256,
            'immutable PR2839 baseline SHA256 mismatch')
    old = ast.parse(baseline)
    new = ast.parse(adapter)
    for name, added in ADDITIONS.items():
        old_assignment = profile_assignment(old, name)
        new_assignment = profile_assignment(new, name)
        old_values = literal_profile(old_assignment)
        require(not (old_values.keys() & added.keys()), 'addition overwrites baseline profile')
        require(json.dumps(literal_profile(new_assignment), sort_keys=True)
                == json.dumps(old_values | added, sort_keys=True),
                'profile records differ from the exact declared extension: ' + name)
        # Replace only the approved dictionary. Every other program node stays.
        new_assignment.value = copy.deepcopy(old_assignment.value)
    for flag, new_default in DEFAULTS.items():
        old_keyword = default_keyword(old, flag)
        new_keyword = default_keyword(new, flag)
        require(ast.literal_eval(old_keyword.value) == 'pr2802', 'baseline default changed')
        require(ast.literal_eval(new_keyword.value) == new_default, 'adapter default changed')
        new_keyword.value = copy.deepcopy(old_keyword.value)
    remove_module_docstring(old)
    remove_module_docstring(new)
    require(ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False),
            'unexpected executable AST change outside the exact allowlist')


def controls(baseline, adapter):
    text = adapter.decode('utf-8')
    substitutions = {
        'weakened_stage_exit_guard': ('need(result.returncode == 0,', 'need(True,'),
        'altered_source_hash': (ADDITIONS['SOURCE_PROFILES']['pr2833']['manifest'], '0' * 64),
        'altered_helper_value_type': ('helpers=408, source_file_count=541',
                                     'helpers=408.0, source_file_count=541'),
        'altered_comparison_field': ("field='kappa'),", "field='kappa_decimal'),"),
        'wrong_default': ("default='pr2843')", "default='pr2802')"),
        'weakened_final_source_guard': (
            "need(sha(source / 'MANIFEST.json') == SOURCE_MANIFEST\n",
            "need(True\n"),
    }
    rejected = []
    for name, (old, new) in substitutions.items():
        require(old in text and old != new, 'control does not alter adapter: ' + name)
        mutant = text.replace(old, new, 1).encode('utf-8')
        try:
            verify(baseline, mutant)
        except (RuntimeError, ValueError, SyntaxError):
            rejected.append(name)
        else:
            raise RuntimeError('control accepted: ' + name)
    try:
        verify(baseline + b'\n', adapter)
    except RuntimeError:
        rejected.append('altered_baseline_bytes')
    else:
        raise RuntimeError('altered immutable baseline accepted')
    # Positive control: comments and the module docstring are permitted metadata.
    tree = ast.parse(adapter)
    tree.body[0].value.value += '\nPositive metadata-only control.'
    verify(baseline, ast.unparse(tree).encode('utf-8'))
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--adapter', type=Path, required=True)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    baseline, adapter = args.baseline.read_bytes(), args.adapter.read_bytes()
    verify(baseline, adapter)
    rejected = controls(baseline, adapter) if args.controls else []
    print(json.dumps({
        'status': 'PASS_ADMISSION_DERIVATION',
        'baseline_sha256': BASELINE_SHA256,
        'adapter_sha256': hashlib.sha256(adapter).hexdigest(),
        'allowed_changes': ['module docstring', 'exact immutable profile additions',
                            'two declared CLI defaults'],
        'rejected_controls': rejected,
        'candidate_code_executed': False,
        'scope': 'Exact parsed-program derivation; inherited theorem and full runtime evidence remain separate.',
    }, sort_keys=True))


if __name__ == '__main__':
    main()
