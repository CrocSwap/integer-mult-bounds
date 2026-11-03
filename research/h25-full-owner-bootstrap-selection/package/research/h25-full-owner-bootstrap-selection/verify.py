#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Non-admitting DATA/source verifier, adapted from PR6370 e144f3b0.

Only this new verifier is executable. Retained originals are bytes/AST only.
No imports, compilation or extracted calls of retained originals are permitted.
"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
FROZEN_SOURCE_PINS_SHA256 = '4b93f3e9b89dfce0743c187723414c7fc8e096e8797be61e8ea2f69d3cbfb0d3'
FROZEN_GRAPH_SHA256 = '388f1c2c379a718b98c1831d56796527fb9f14d85107971eb56650145415049f'

def bounded_read(name, maximum=8 * 1024 * 1024):
    path = ROOT / name
    need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'bounded local name')
    need(not any(x.is_symlink() for x in (path, *path.parents) if x.is_relative_to(ROOT)), 'archive symlink')
    need(path.stat().st_size <= maximum, 'bounded source/document size')
    return path.read_bytes()
FALSE_FIELDS = ('runtime_admission', 'C07', 'full_C05', 'full_V03',
                'original_activity_complete', 'prefix_substitutes_full_completion')
KEY_PINS = {'full_driver': 'f5a2d33f2b4d3651f214156a0e7094c2bb516ce2d5ab7698d18c11f98f35dee0',
 'probe_binding_v3': '9cbb7368f89e71d1e6cc46db5dc77efed3e03ed2a801c98c88fe316e4d9f3ef2',
 'variant_driver_v1': 'cdb1479253358508088f8aa0e1e92e6c75ffcc127e54552698598a02de061254',
 'parent_completion_v1': 'd4ee1b7ce4a42b73261984ffb1b9ceb5bb0165223e04a253588f83b99f6981a5',
 'parent_domain_v1': 'a51264289803b4b17bb262f2460ddd4ed72500aaa21e5eb80fa2db4583689361',
 'parent_closure_v1': 'a15424f14baa3d484fe04bfbe7e449c32561c866dbaca2c1b5f646dfb377ed1f'}


def need(value, message):
    if value is not True:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def import_rows(tree):
    # Retained PR6370 method; no original functions are extracted or called.
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                rows.append((node.lineno, item.name, None, item.asname or item.name.split('.')[0], node not in tree.body))
        elif isinstance(node, ast.ImportFrom):
            need(node.level == 0 and node.module is not None, 'unsupported relative import')
            for item in node.names:
                rows.append((node.lineno, node.module, item.name, item.asname or item.name, node not in tree.body))
    return [list(r) for r in sorted(rows, key=repr)]


def init_rows(tree, text):
    return [{'line': n.lineno, 'kind': type(n).__name__,
             'source_sha256': sha(ast.get_source_segment(text, n).encode())}
            for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def call_rows(tree, text):
    rows = []
    class Visitor(ast.NodeVisitor):
        scope = 'module'
        def visit_FunctionDef(self, node):
            prior = self.scope
            self.scope = node.name
            self.generic_visit(node)
            self.scope = prior
        visit_AsyncFunctionDef = visit_FunctionDef
        def visit_Call(self, node):
            callee = ast.unparse(node.func)
            tokens = ('_COMPILE', '_EXEC', '_hash_regular', 'import_module', 'run_module',
                      'run_path', 'read_verified', 'bind_receivers', '.receiver',
                      'capture_authority', 'load_probe', '._dependencies', '_vinvoke',
                      '_ca_dispatch', '_vdispatch', 'adapters.load', 'load_control_module',
                      '_CREATE_DYNAMIC', '_EXEC_DYNAMIC',
                      '_EPOCH_', 'make_parent', 'run_producer', 'accept_producer',
                      'commit_exports', 'stop_evidence', 'CDLL', 'Popen', '_POPEN')
            if any(token in callee for token in tokens) or callee in ('compile', 'exec', 'eval', '__import__'):
                rows.append({'caller': self.scope, 'line': node.lineno, 'callee': callee,
                             'source': ast.get_source_segment(text, node)})
            self.generic_visit(node)
    Visitor().visit(tree)
    return sorted(rows, key=lambda r: (r['line'], r['callee'], r['source']))


def validate_data(selection, graph):
    need(selection['kind'] == 'PROPOSED_SOURCE_SELECTION_ONLY', 'proposal cannot be admission')
    context = selection['context']
    stage, session = context['stage'], context['session_directory']
    need(stage.startswith('/') and session.startswith('/') and stage != session, 'independent absolute paths')
    need(context['output'] == session + '/failure_variants/producer-output', 'output relation')
    need(selection['variant_relative_path'] == 'integration/variant_driver_v1.py', 'variant basename')
    need(selection['producer_order'] == ['group01', 'failure_variants'], 'both parent producers')
    need(selection['creation_ownership'] == {'session_directory': 'make_parent',
        'role_evidence_directory': 'run_producer', 'producer-output': 'original producer initial TCB'}, 'creation ownership')
    need(selection['precreated_runtime_owned_objects'] == [], 'runtime-owned objects precreated')
    need(selection['group01']['status'] == 'UNRESOLVED_FULL_SOURCE_AND_SELECTION', 'Group01 obligation')
    need(selection['handles'] == {k: {'kind': 'UNRESOLVED', 'issued': False}
        for k in ('epoch', 'authority', 'receivers', 'generation', 'launch_nonce', 'group01_generation', 'group01_launch_nonce')}, 'DATA is not capability authority')
    for doc in (selection, graph):
        need(all(doc['claims'][key] is False for key in FALSE_FIELDS), 'scope flag elevated')
        need(doc['claims']['original_credit'] == 0 and type(doc['claims']['original_credit']) is int, 'original credit')
        need(doc['claims']['costs'] == 'OPEN_NOT_ZERO' and doc['claims']['goal_stagnation'] == 'UNKNOWN_NOT_RESET', 'cost/progress boundary')
    projections = selection['command_projections']
    need(set(projections) == {'normal', 'optimized'}, 'both command modes')
    for mode, row in projections.items():
        prefix = ['/usr/bin/python3.12', '-S', '-s', '-P', '-B'] + (['-O'] if mode == 'optimized' else [])
        expected = prefix + [stage + '/integration/full_driver.py', '--root-sha256', KEY_PINS['full_driver'],
            '--provider', stage + '/integration/probe_binding_v3.py', KEY_PINS['probe_binding_v3'],
            '--driver', stage + '/integration/variant_driver_v1.py', KEY_PINS['variant_driver_v1'],
            '--integration', stage + '/integration', '--', '--output', context['output'],
            '--generation', {'unresolved': 'generation'}, '--launch-nonce', {'unresolved': 'launch_nonce'}]
        need(row['failure_variants'] == expected, 'variant command projection ' + mode)
        need(row['group01']['status'] == 'UNRESOLVED_FULL_SOURCE_AND_SELECTION', 'Group01 command obligation')
        need(row['gcc_argv'] == selection['direct_variant_domain']['gcc_argv'], 'GCC argv mode drift')
    domain = selection['direct_variant_domain']
    need(domain['ordered_roles'] == ['pyinit_failure', 'exec_failure'] and domain['build_count_per_mode'] == 2, 'two-build domain')
    need(len(domain['gcc_argv']) == 2 and len(domain['six_role_occurrences']) == 6, 'direct fixed denominator')
    for role, argv in zip(domain['ordered_roles'], domain['gcc_argv']):
        expected = ['/usr/bin/x86_64-linux-gnu-gcc-13', '-nostartfiles', '-shared', '-fPIC', '-O3',
            '-std=c11', '-Wall', '-Wextra', '-Werror', '-I/usr/include/python3.12',
            stage + '/areas/field-negative-variants-v1/' + role + '/dict_probe_fields_v1.c', '-o',
            context['output'] + '/' + role + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so']
        need(argv == expected, 'literal GCC projection')
    names = {n['module']: n for n in graph['nodes']}
    for name, pin in KEY_PINS.items():
        need(names[name]['sha256'] == pin, 'selected body identity ' + name)
    need(graph['complete_entry_graph'] is False and graph['coverage'] == 'FINITE_KNOWN_SOURCE_AUDIT_INCOMPLETE', 'unknown selector hidden as complete')
    need(graph['external_caller'] == {'status': 'MISSING_CALLER_BODY', 'source_identity': None,
        'api_signature_is_caller_body': False}, 'API signature is not caller body')
    need(len(graph['required_receivers']) == 33 and len(set(graph['required_receivers'])) == 33, 'receiver count')
    edges = graph['edges']
    need(any(e['class'] == 'source_load_compile_exec_injected_namespace' and
        e['source'] == 'full_driver' and e['destination'] == 'probe_binding_v3' and
        e['selector'] == 'selected_provider' for e in edges), 'provider execution edge missing')
    need({e['destination'] for e in edges if e['class'] == 'receiver_requirement'} == set(graph['required_receivers']), 'receiver edge omitted')
    need(any(f['kind'] == 'MISSING_CALLER_BODY' for f in graph['frontiers']), 'missing caller frontier')
    need(any(f['kind'] == 'UNCLASSIFIED_SOURCE_SELECTOR' for f in graph['frontiers']), 'unknown selector frontier')
    return True


def verify_sources(selection, graph):
    pin_raw = bounded_read('SOURCE-PINS-v1.json')
    need(sha(pin_raw) == FROZEN_SOURCE_PINS_SHA256, 'independently frozen source pool')
    pins = json.loads(pin_raw)
    need(len(pins['sources']) == 21 and sum(r['bytes'] for r in pins['sources']) <= 4 * 1024 * 1024, 'finite pool bounds')
    need({r['module'] for r in pins['sources']} == {n['module'] for n in graph['nodes']}, 'source pool membership')
    trees = {}
    for row, node in zip(sorted(pins['sources'], key=lambda n: n['module']), sorted(graph['nodes'], key=lambda n: n['module'])):
        target = ROOT / row['local_path']
        need(row['local_path'].startswith('source/') and '..' not in Path(row['local_path']).parts and not target.is_symlink(), 'local inert source path')
        need(row['local_path'] == 'source/' + row['module'] + '.py.txt', 'exact source path')
        raw = bounded_read(row['local_path'], 1024 * 1024)
        need(len(raw) == row['bytes'] == node['bytes'] and sha(raw) == row['sha256'] == node['sha256'], 'source identity ' + row['module'])
        text = raw.decode()
        tree = ast.parse(text)
        trees[row['module']] = tree
        need(import_rows(tree) == node['imports'], 'import inventory ' + row['module'])
        need(init_rows(tree, text) == node['initialization_anchors'], 'initialization anchors ' + row['module'])
        need(call_rows(tree, text) == node['interface_loader_sites'], 'loader/interface AST coverage ' + row['module'])
    parent = trees['parent_completion_v1']
    receivers = [ast.literal_eval(n.value) for n in parent.body if isinstance(n, ast.Assign)
                 and any(isinstance(x, ast.Name) and x.id == 'REQUIRED_MODULES' for x in n.targets)]
    need(len(receivers) == 1 and list(receivers[0]) == graph['required_receivers'], 'literal receiver requirements')
    node_index = {n['module']: n for n in graph['nodes']}
    for edge in graph['edges']:
        if edge['source'] in trees:
            text = bounded_read(node_index[edge['source']]['retained_local_path'], 1024 * 1024).decode()
            anchor = edge['anchor']
            need(any(getattr(n, 'lineno', None) == anchor['line'] and
                     ast.get_source_segment(text, n) == anchor['source'] for n in ast.walk(trees[edge['source']])), 'edge source anchor')
    for module in node_index:
        expected = len(node_index[module]['imports'])
        need(sum(e['source'] == module and e['class'] in ('eager_project_or_stdlib_import', 'deferred_project_or_stdlib_import') for e in graph['edges']) == expected, 'import edges inventory')
    return True


def controls(selection, graph):
    cases = json.loads(bounded_read('CONTROL-PLAN-v1.json'))['cases']
    need(len(cases) == 15, 'reviewed control count')
    outcomes = []
    for case in cases:
        s, g = copy.deepcopy(selection), copy.deepcopy(graph)
        key = case['id']
        if key == 'old_basename': s['variant_relative_path'] = 'integration/v03_control_driver_v1.py'
        elif key == 'arbitrary_output': s['context']['output'] += '-arbitrary'
        elif key == 'omit_group01': s['producer_order'] = ['failure_variants']
        elif key == 'precreated_output': s['precreated_runtime_owned_objects'] = [s['context']['output']]
        elif key == 'old_domain': next(n for n in g['nodes'] if n['module'] == 'parent_domain_v1')['sha256'] = 'old-domain-body'
        elif key == 'omit_provider': g['edges'] = [e for e in g['edges'] if not (e['source'] == 'full_driver' and e['destination'] == 'probe_binding_v3' and e['class'] == 'source_load_compile_exec_injected_namespace')]
        elif key == 'omit_receiver': g['edges'] = [e for e in g['edges'] if not (e['class'] == 'receiver_requirement' and e['destination'] == 'receipt_contract_v1')]
        elif key == 'unknown_claim_complete': g['complete_entry_graph'] = True
        elif key == 'signature_as_caller': g['external_caller'] = {'status': 'AVAILABLE', 'source_identity': 'make_parent(epoch,authority,receivers)', 'api_signature_is_caller_body': True}
        elif key == 'fake_authority': s['handles']['authority'] = {'kind': 'DATA_DIGEST', 'issued': True}
        elif key == 'prefix_as_full': g['claims']['prefix_substitutes_full_completion'] = True
        elif key == 'graph_pass_runtime': g['claims']['runtime_admission'] = True
        elif key == 'graph_pass_c07': g['claims']['C07'] = True
        elif key == 'graph_pass_credit': g['claims']['original_credit'] = 1
        elif key != 'corrected_positive': raise ValueError('unreviewed control')
        try:
            validate_data(s, g)
            outcome = 'ACCEPT_SOURCE_PROPOSAL_ONLY'
        except ValueError:
            outcome = 'REJECT'
        need(outcome == case['expected'], 'control oracle ' + key)
        outcomes.append({'id': key, 'outcome': outcome})
    return outcomes


def main():
    selection = json.loads(bounded_read('SELECTION-DELTA-v1.json'))
    graph_raw = bounded_read('FULL-ENTRY-GRAPH-v1.json')
    need(sha(graph_raw) == FROZEN_GRAPH_SHA256, 'frozen exact incomplete graph identity')
    graph = json.loads(graph_raw)
    validate_data(selection, graph)
    verify_sources(selection, graph)
    result = {'status': 'PASS_FINITE_SOURCE_AUDIT_ONLY_GRAPH_INCOMPLETE', 'original_credit': 0,
              'runtime_admission': False, 'C07': False, 'full_C05': False, 'full_V03': False}
    need(sys.argv[1:] in ([], ['--controls']), 'only optional --controls is supported')
    if sys.argv[1:] == ['--controls']:
        result['controls'] = controls(selection, graph)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
