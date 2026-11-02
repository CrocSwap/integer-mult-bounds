#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Static retained-source checks; never compile/import/execute original bodies."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(spelling):
    need(type(spelling) is str, 'path type')
    path = PurePosixPath(spelling)
    need(not path.is_absolute() and path.as_posix() == spelling
         and all(p not in ('', '.', '..') for p in path.parts), 'path spelling')
    target = ROOT / spelling
    need(not any(p.is_symlink() for p in (target, *target.parents) if p.is_relative_to(ROOT)), 'archive link')
    return target


def import_rows(tree):
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                rows.append((node.lineno, item.name, None, item.asname or item.name.split('.')[0], node not in tree.body))
        elif isinstance(node, ast.ImportFrom):
            need(node.level == 0 and node.module is not None, 'unsupported relative project import')
            for item in node.names:
                rows.append((node.lineno, node.module, item.name, item.asname or item.name, node not in tree.body))
    return sorted(rows, key=repr)


def main():
    manifest = json.loads(local('ARTIFACTS.json').read_text())
    seen = set()
    for row in manifest['files']:
        need(row['path'] not in seen, 'duplicate artifact')
        seen.add(row['path'])
        raw = local(row['path']).read_bytes()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'archive identity: ' + row['path'])
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == seen | {'ARTIFACTS.json'}, 'archive inventory changed')
    graph_raw = local('SOURCE-GRAPH-v1.json').read_bytes()
    pins_raw = local('prerequisites/PINS-v1.json').read_bytes()
    need(len(graph_raw) == 132763 and digest(graph_raw) == 'f999a6bfc9ac9048b248d9b029b7676ba04dea5c559228d5286e49d269ca3597', 'final graph pin')
    need(len(pins_raw) == 13934 and digest(pins_raw) == 'f20555d87ab5b0f1bed28461f2b435773607ffaf87f5c4ba21414844f44fd1d6', 'frozen input pins')
    graph, pins = json.loads(graph_raw), json.loads(pins_raw)
    modules = {row['module']: row for row in graph['modules']}
    need(len(modules) == 15 and set(modules) == {row['module'] for row in pins['inner_project']}, 'inner15 set')
    need(sum(row['bytes'] for row in modules.values()) == graph['project_source_bytes'] == 379241, 'inner source byte bill')
    trees, sources, edges = {}, {}, {}
    statement_count = call_count = 0
    for pin in pins['inner_project']:
        name = pin['module']
        raw = local('prerequisites/' + Path(pin['copy_path']).name).read_bytes()
        row = modules[name]
        need(len(raw) == pin['bytes'] == row['bytes'] and digest(raw) == pin['sha256'] == row['sha256'], 'inner input identity: ' + name)
        text = raw.decode('utf-8')
        tree = ast.parse(text, feature_version=(3, 12))
        trees[name], sources[name] = tree, text
        actual_imports = import_rows(tree)
        frozen_imports = []
        for r in row['imports']:
            if 'members' in r:
                need(r['level'] == 0, 'frozen relative import')
                frozen_imports.extend((r['line'], r['module'], member['name'], member['alias'], r['deferred']) for member in r['members'])
            else:
                frozen_imports.append((r['line'], r['module'], r['member'], r['alias'], r['deferred']))
        frozen_imports.sort(key=repr)
        need(actual_imports == frozen_imports, 'AST import inventory: ' + name)
        project = set()
        for imported in row['imports']:
            base = imported['module'].split('.')[0]
            if base in modules:
                project.add(base)
                need(imported['classification'] == 'selected_project' and imported['deferred'] is False, 'project import scope: ' + name)
            else:
                expected_class = 'deferred_stdlib_T0_or_original_native_supplement' if imported['deferred'] else 'original_trusted_stdlib_T0'
                need(base in graph['trusted_stdlib_T0_names'] and imported['classification'] == expected_class, 'undeclared import premise: ' + name)
        edges[name] = sorted(project)
        for anchor in row['module_initialization']:
            if anchor['kind'] == 'class_definition':
                nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.lineno == anchor['line'] and n.name == anchor['name']]
                need(len(nodes) == 1 and [ast.unparse(n) for n in nodes[0].bases] == anchor['bases']
                     and [ast.unparse(n) for n in nodes[0].decorator_list] == anchor['decorators'], 'class initialization anchor: ' + name)
            else:
                nodes = [n for n in tree.body if n.lineno == anchor['line'] and type(n).__name__ == anchor['kind']]
                need(len(nodes) == 1 and ast.get_source_segment(text, nodes[0]) == anchor['source'], 'module initialization anchor: ' + name + ':' + str(anchor['line']))
            statement_count += 1
        for anchor in row['initialization_calls']:
            calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and n.lineno == anchor['line']
                     and ast.get_source_segment(text, n) == anchor['source'] and ast.unparse(n.func) == anchor['callee']]
            need(len(calls) == 1, 'initialization call anchor: ' + name)
            call_count += 1
        need(row['static_namespace_name_count'] == len(row['static_namespace_names'])
             and row['static_names_plus8_import_metadata'] == row['static_namespace_name_count'] + 8
             and row['static_names_plus8_import_metadata'] <= 512
             and row['namespace_bound_actual_capture_proven'] is False, 'static/actual capture boundary')
    need(edges == graph['import_edges'], 'selected project graph differs from AST')
    order = graph['topological_initialization_order']
    need(len(order) == len(set(order)) == 15 and set(order) == set(modules), 'initialization order membership')
    positions = {name: index for index, name in enumerate(order)}
    need(all(positions[dependency] < positions[name] for name, dependencies in edges.items() for dependency in dependencies), 'initialization order violates import dependency')
    need(graph['missing_sources'] == [] and graph['module_initialization_cycles'] == [], 'frozen missing/cycle result')
    need(len(pins['outer_reference_inputs']) == 4, 'four separate outer references')
    for row in pins['outer_reference_inputs']:
        name = Path(row['copy_path']).name
        raw = local('prerequisites/' + name).read_bytes()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'] and row['part_of_inner15_project_graph'] is False, 'outer byte identity')
        if name.endswith('.py.txt'):
            text = raw.decode('utf-8')
            tree = ast.parse(text, feature_version=(3, 12))
            imports = sorted([{'line': n.lineno, 'source': ast.get_source_segment(text, n)} for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))], key=lambda r: (r['line'], r['source']))
            need(imports == sorted(row['imports_as_text'], key=lambda r: (r['line'], r['source'])), 'outer textual import anchors')
        else:
            need(type(json.loads(raw)) is dict, 'native TCB data shape')
    gate = json.loads(local('evidence/INPUT-GATE-v1.json').read_text())
    need(gate['accepted_checkpoint'] == 'U6.1' and gate['gate_passed_before_deadline'] is True, 'input checkpoint')
    for item in gate['evidence']:
        rel = item['path'] if item['path'] == 'SOURCE-GRAPH-v1.json' else 'evidence/' + item['path']
        raw = local(rel).read_bytes()
        need(len(raw) == item['bytes'] and digest(raw) == item['sha256'], 'frozen gate evidence')
    historical = json.loads(local('evidence/CALLER-INPUT-AUDIT-v1.json').read_text())
    need(historical['graph']['sha256_at_first_read'] == '83d52ab1de782590ce892984292e12b4cc73be3b4c89964550e64ae8f10b480b', 'historical graph reference changed')
    need(historical['whole_unit_input_gate_accepted_by_this_first_review'] is False, 'initial pending status rewritten')
    initial = json.loads(local('evidence/RECEIVER-INPUT-REVIEW-v1.json').read_text())
    need(initial['input_gate_complete'] is False, 'initial receiver pending status rewritten')
    for field in ['actual_receiver_capture_fit', 'actual_runtime_initialization_or_admission', 'full_C05', 'full_V03', 'old_units_reopened', 'original_modules_imported_or_executed', 'original_tests_or_native_or_Popen_or_compiler']:
        need(graph[field] is False, 'graph authority scope: ' + field)
    need(gate['full_C05'] is False and gate['full_V03'] is False and gate['runtime_execution'] is False
         and gate['original_activity_credit'] == 0 and graph['costs'] == gate['costs'] == 'OPEN_NOT_ZERO', 'original admission scope')
    print('PASS_BOOTSTRAP_SOURCE_INPUT_ARCHIVE_ONLY files=' + str(len(seen)) + ' inner=15 outer=4 bytes=379241 imports=' + str(sum(len(r['imports']) for r in modules.values())) + ' initialization_anchors=' + str(statement_count) + ' call_anchors=' + str(call_count), flush=True)


if __name__ == '__main__':
    main()
