#!/usr/bin/env python3
"""Parent-admitted source-only controls: extract exactly one authenticated pure function.

No scientific/project module is imported or executed. Only the whitelisted pure
function body from the actual pinned runner is evaluated after parent admission.
This file creates no process, native image, fixture directory or output file.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

R = Path(__file__).resolve().parent
RUNNER = R / 'snapshots/implementation/source/fresh_runner.py.txt'
FIXTURES = R / 'REFUSAL-FIXTURES-v1.json'
RUNNER_SHA = 'b04db13314675b9a51bea6bb3bb0875b1d5490b9ea44db654cb3a3d38c054675'
FIXTURES_SHA = '4ecd6a26e87aef19f832b1cdce07cb1c15843e03bd4f548eddb4902f1fd52334'
FUNCTION = 'original_optimized_refusal'
ARGUMENTS = ('exit_code','stderr_raw','stdout_bytes','positive_receipt_present','stop_present','capture_complete')


def need(value, reason):
    if value is not True:
        raise RuntimeError(reason)


def read_pinned(path, cap, expected):
    with path.open('rb') as stream:
        raw = stream.read(cap + 1)
    need(len(raw) <= cap and hashlib.sha256(raw).hexdigest() == expected,
         'fixed source/fixture digest and byte cap')
    return raw


def extracted_function(raw):
    tree = ast.parse(raw, filename=str(RUNNER), mode='exec')
    selected = [node for node in tree.body if type(node) is ast.FunctionDef and node.name == FUNCTION]
    need(len(selected) == 1, 'one authentic actual runner predicate')
    function = selected[0]
    args = function.args
    need(tuple(arg.arg for arg in args.args) == ARGUMENTS and not args.posonlyargs and
         not args.kwonlyargs and not args.defaults and not args.kw_defaults and
         args.vararg is None and args.kwarg is None and not function.decorator_list and
         function.returns is None, 'closed exact pure function signature')
    allowed = (ast.FunctionDef, ast.arguments, ast.arg, ast.Expr, ast.Constant, ast.Return,
               ast.BoolOp, ast.And, ast.Compare, ast.Is, ast.Eq, ast.Lt, ast.LtE,
               ast.In, ast.NotIn, ast.Call, ast.Name, ast.Load, ast.Attribute)
    nodes = tuple(ast.walk(function))
    need(len(nodes) <= 256 and all(type(node) in allowed for node in nodes),
         'no imports, assignment, filesystem, native or other side effect in extracted body')
    for node in nodes:
        if type(node) is ast.Name:
            need(node.id in set(ARGUMENTS) | {'type','int','bytes','len'}, 'closed builtin/argument names')
        elif type(node) is ast.Attribute:
            need(type(node.value) is ast.Name and node.value.id == 'stderr_raw' and
                 node.attr in ('startswith','endswith'), 'only exact-byte prefix/tail operations')
        elif type(node) is ast.Call:
            need(not node.keywords and ((type(node.func) is ast.Name and node.func.id in ('type','len')) or
                 (type(node.func) is ast.Attribute and node.func.attr in ('startswith','endswith'))),
                 'only approved pure builtin calls')
    mains = [node for node in tree.body if type(node) is ast.FunctionDef and node.name == 'main']
    need(len(mains) == 1 and sum(type(node) is ast.Call and type(node.func) is ast.Name and
         node.func.id == FUNCTION for node in ast.walk(mains[0])) == 1,
         'actual main calls this owning predicate exactly once; no disconnected helper')
    namespace = {'__builtins__':{'type':type,'int':int,'bytes':bytes,'len':len}}
    module = ast.Module(body=[function], type_ignores=[])
    # This is the sole candidate evaluation, separately gated by parent admission.
    exec(compile(module, str(RUNNER), 'exec', dont_inherit=True,
                 optimize=sys.flags.optimize), namespace, namespace)
    return namespace[FUNCTION]


def fixture_bytes(row):
    kind = row['stderr_kind']
    raw = row['stderr'].encode('ascii')
    if kind == 'literal':
        return raw
    if kind == 'bytearray':
        return bytearray(raw)
    if kind in ('overflow','exact_cap'):
        prefix = b'Traceback (most recent call last):\n_epoch_sc4_full_entry\n'
        tail = b'RuntimeError: SC4 fixed assertion-on fresh candidate full invocation required\n'
        amount = 2097153 if kind == 'overflow' else 2097152
        return prefix + b' ' * (amount - len(prefix) - len(tail)) + tail
    raise RuntimeError('unknown fixed fixture construction')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=('normal','optimized'))
    args = parser.parse_args()
    need(sys.flags.optimize == (1 if args.mode == 'optimized' else 0), 'actual control mode matches command')
    source = read_pinned(RUNNER, 131072, RUNNER_SHA)
    fixtures_raw = read_pinned(FIXTURES, 32768, FIXTURES_SHA)
    fixtures = json.loads(fixtures_raw)
    need(fixtures['schema'] == 'original-optimized-refusal-fixed-fixtures-v1' and
         type(fixtures['cases']) is list and len(fixtures['cases']) == 22,
         'fixed independent literal oracle denominator')
    predicate = extracted_function(source)
    results = []
    for row in fixtures['cases']:
        actual = predicate(row['exit_code'], fixture_bytes(row), row['stdout_bytes'],
                           row['positive_receipt_present'], row['stop_present'], row['capture_complete'])
        need(type(row['expected']) is bool and type(actual) is bool, 'exact boolean control result')
        results.append({'id':row['id'], 'expected':row['expected'], 'actual':actual,
                        'pass':actual is row['expected']})
    passed = sum(row['pass'] for row in results)
    report = {'schema':'source-only-original-refusal-controls-v1','mode':args.mode,
        'status':'PASS' if passed == 22 else 'FAIL','controls_passed':passed,'controls_expected':22,
        'runner_sha256':RUNNER_SHA,'fixtures_sha256':FIXTURES_SHA,'results':results,
        'scope':'Authenticated AST-extracted actual pure predicate only',
        'scientific_imports':False,'whole_runner_executed':False,'native_calls':0,'compiler_calls':0,
        'original_activity_credit':0,'runtime_qualification':False,'full_science':False}
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0 if passed == 22 else 1


if __name__ == '__main__':
    raise SystemExit(main())
