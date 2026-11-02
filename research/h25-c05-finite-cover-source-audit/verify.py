#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Static archive/anchor checks. Never import or execute archived source."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if condition is not True:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(spelling):
    path = PurePosixPath(spelling)
    need(type(spelling) is str and path.as_posix() == spelling and not path.is_absolute()
         and all(part not in ('', '.', '..') for part in path.parts), 'invalid archive path')
    target = ROOT / spelling
    need(not any(p.is_symlink() for p in (target, *target.parents) if p.is_relative_to(ROOT)), 'archive link')
    return target


def function(tree, name):
    current = tree
    for part in name.split('.'):
        nodes = [n for n in current.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == part]
        need(len(nodes) == 1, 'missing/ambiguous source function: ' + name)
        current = nodes[0]
    return current


def main():
    manifest = json.loads((ROOT / 'ARTIFACTS.json').read_text())
    expected = set()
    for row in manifest['files']:
        need(row['path'] not in expected, 'duplicate archive path')
        expected.add(row['path'])
        raw = local(row['path']).read_bytes()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'archive identity: ' + row['path'])
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == expected | {'ARTIFACTS.json'}, 'archive file set changed')
    findings = json.loads(local('SOURCE-FINDINGS.json').read_text())
    for row in findings['function_anchors']:
        text = local(row['path']).read_text()
        node = function(ast.parse(text), row['qualified_name'])
        need((node.lineno, node.end_lineno) == (row['first_line'], row['last_line']), 'source location changed')
        need(digest(ast.get_source_segment(text, node).encode()) == row['source_segment_sha256'], 'source segment changed')
        need(digest(ast.dump(node, include_attributes=False).encode()) == row['ast_sha256'], 'source AST changed')
    for row in findings['text_anchors']:
        text = '\n'.join(local(row['path']).read_text().splitlines()[row['first_line']-1:row['last_line']])
        need(text == row['literal'], 'source text anchor changed')
    for row in findings['literal_constants']:
        tree = ast.parse(local(row['path']).read_text())
        nodes = [n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == row['name'] for t in n.targets)]
        need(len(nodes) == 1, 'literal gate missing/ambiguous')
        value = ast.literal_eval(nodes[0])
        need(type(value) is type(row['expected']) and value == row['expected'], 'literal gate/cap changed')
    for row in findings['json_anchors']:
        value = json.loads(local(row['path']).read_text())
        for part in row['pointer']:
            value = value[part]
        need(type(value) is type(row['expected']) and value == row['expected'], 'decision metadata changed')
    tree = ast.parse(local('snapshot/cold_build_evidence.py.txt').read_text())
    node = function(tree, 'run')
    calls = [n for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and isinstance(n.func.value, ast.Name) and n.func.value.id == 'subprocess' and n.func.attr == 'Popen']
    need(len(calls) == 1 and len(calls[0].args) == 1 and isinstance(calls[0].args[0], ast.Name)
         and calls[0].args[0].id == 'command', 'original helper call shape changed')
    need([kw.arg for kw in calls[0].keywords] == findings['helper_Popen_keywords'], 'original helper keyword shape changed')
    need(findings['full_C05'] is False and findings['full_V03'] is False
         and findings['runtime_qualification'] is False and findings['source_clock_reopened'] is False
         and findings['outside_costs'] == 'OPEN_NOT_ZERO', 'scope changed')
    print('PASS_FINITE_COVER_SOURCE_ARCHIVE_ONLY files=' + str(len(expected))
          + ' functions=' + str(len(findings['function_anchors']))
          + ' text=' + str(len(findings['text_anchors']))
          + ' metadata=' + str(len(findings['json_anchors'])))


if __name__ == '__main__':
    main()
