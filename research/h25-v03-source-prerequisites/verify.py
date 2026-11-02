"""Passive fixed-source AST/byte audit; no archived code execution or imports."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ARCHIVE = 'research/h25-cache-source-handoff/snapshot/stages/combined-finite-v8/integration/'
DRIVER = 'areas/field-variant-producer-v2/variant_driver_v1.py'
NATIVE = 'stages/combined-finite-v8/integration/native_packet.py'
PROFILE = 'stages/combined-finite-v8/integration/RUNTIME-PROFILE.json'
CONDITIONS = 'areas/field-variant-producer-v2/CONDITIONS.json'
PARENT = 'areas/field-parent-completion-v2/parent_completion_v1.py'


def need(condition, message):
    if condition is not True:
        raise RuntimeError(message)


def function(tree, name):
    return next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)


def assignment(tree, name):
    return next(node.value for node in tree.body if isinstance(node, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == name for target in node.targets))


def shape(node):
    return ast.dump(node, include_attributes=False)


def analyse(blobs):
    root = ast.parse(blobs['root'])
    provider = ast.parse(blobs['provider'])
    native = ast.parse(blobs[NATIVE])
    driver = ast.parse(blobs[DRIVER])
    profile = json.loads(blobs[PROFILE])
    conditions = json.loads(blobs[CONDITIONS])
    parent = ast.parse(blobs[PARENT])
    entry = function(root, '_entry')
    entry_text = ast.unparse(entry)
    need('driver_sha' in entry_text and 'digest == driver_sha' in entry_text and
         "'bootstrap_root': _ROOT_MODULE" in entry_text and
         "'bootstrap_capability': capability" in entry_text and
         "'bootstrap_api': api" in entry_text,
         'source-selected genuine Root entry differs')
    delegation = next(n for n in function(root, 'preflight').body if isinstance(n, ast.Return))
    need(shape(delegation.value) == shape(ast.parse('state[1].preflight_runtime()', mode='eval').body),
         'Root preflight delegation differs')
    runtime_files = ast.literal_eval(assignment(provider, '_RUNTIME_FILES'))
    need(type(runtime_files) is tuple and len(runtime_files) == 216 and
         all(type(row) is tuple and len(row) == 3 for row in runtime_files),
         'literal runtime-file census differs')
    extra = next(n.value for n in function(provider, '_profile_files').body if isinstance(n, ast.Return))
    need(shape(extra) == shape(ast.parse('_RUNTIME_FILES + ((path, digest, count),)', mode='eval').body),
         'profile-file append differs')
    result = next(n.value for n in function(provider, 'preflight_runtime').body if isinstance(n, ast.Return))
    expected_result = ast.parse("{'schema':'h25-public-runtime-preflight-v2','authenticated_files':_LEN(files),'native_private_access':False,'cached_admission':False}", mode='eval').body
    need(shape(result) == shape(expected_result), 'preflight return semantics differ')
    need(len(profile['headers']) == 215, 'profile header count differs')
    contract = ast.literal_eval(assignment(native, 'BUILD_CONTRACT'))
    need(len(contract['dependencies']) == 29 and
         all(type(row) is tuple and len(row) == 3 for row in contract['dependencies']),
         'dependency triples differ')
    for name in ('_fresh', '_preflight', '_dependencies', '_file'):
        direct = function(native, name)
        called = [ast.unparse(n.func) for n in ast.walk(direct) if isinstance(n, ast.Call)]
        need(not any('prepare' in call or 'Popen' in call or 'cold_build' in call or 'subprocess' in call for call in called),
             'compiler/build invocation entered the direct audited branch')
    dependencies = ast.unparse(function(native, '_dependencies'))
    need('for path, expected_sha, expected_size' in dependencies and 'row = _file(path)' in dependencies and
         "row['sha256'] == expected_sha" in dependencies and "row['bytes'] == expected_size" in dependencies,
         'independent dependency authentication differs')
    need('return rows' in dependencies, 'dependency observations no longer returned')
    need(any(row['id'] == 'C05' and 'include search, macro, compiler, specs, linker' in row['required'] and
             'Original dependency scan alone is insufficient.' in row['required']
             for row in conditions['conditions']), 'original C05 meaning lost')
    service_pins = ast.literal_eval(assignment(driver, '_VARIANT_SOURCE_PINS'))
    pin_dict = next(n.value for n in ast.walk(function(driver, '_vcheck_literal_sources'))
                    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'expected' for t in n.targets))
    pins = {}
    for key, value in zip(pin_dict.keys, pin_dict.values):
        if not isinstance(value, ast.Name):
            pins[ast.literal_eval(key)] = ast.literal_eval(value)
    for role in ('pyinit_failure', 'exec_failure'):
        for name in ('dict_probe_fields_v1.c', 'field_service_v1.h', 'field_loader_snapshot_v1.h'):
            raw = blobs['areas/field-negative-variants-v1/' + role + '/' + name]
            digest, size = service_pins[role] if name == 'field_service_v1.h' else pins[name]
            need(len(raw) == size and hashlib.sha256(raw).hexdigest() == digest,
                 'literal role C/header fixture pin differs')
    for name in ('dict_probe_fields_v1.c', 'field_loader_snapshot_v1.h'):
        need(blobs['areas/field-negative-variants-v1/pyinit_failure/' + name] ==
             blobs['areas/field-negative-variants-v1/exec_failure/' + name],
             'claimed equal-content swap is not a no-op')
    need(blobs['areas/field-negative-variants-v1/pyinit_failure/field_service_v1.h'] !=
         blobs['areas/field-negative-variants-v1/exec_failure/field_service_v1.h'],
         'service headers are no longer distinct')
    permission_rows = [n for n in ast.walk(function(driver, '_vcheck_literal_sources'))
                       if isinstance(n, ast.Dict) and any(isinstance(k, ast.Constant) and k.value == 'mode' for k in n.keys)]
    need(any(any(isinstance(k, ast.Constant) and k.value == 'mode' and isinstance(v, ast.Constant) and v.value == 292
                 for k, v in zip(row.keys, row.values)) for row in permission_rows),
         'declared permission-mode pin differs')
    for name in ('VARIANT_CONFIGURATION', 'VARIANT_SOURCE_REVIEW', 'VARIANT_STAGE_ADMISSION',
                 'VARIANT_NATIVE_PROFILE', 'VARIANT_HEADER_ADMISSION', 'VARIANT_COMMAND_ADMISSION',
                 'VARIANT_FUNDING', 'VARIANT_EXECUTION'):
        need(ast.literal_eval(assignment(driver, name)) is None, 'original selection changed')
    category_call = next(n for n in ast.walk(function(parent, '_snapshot_sources'))
                         if isinstance(n, ast.Call) and ast.unparse(n.func) == 'schema.choice' and
                         ast.unparse(n.args[0]) == "expected['category']")
    categories = ast.literal_eval(category_call.args[1])
    need(type(categories) is tuple and len(categories) == len(set(categories)) == 9,
         'parent source category domain differs')
    return {'authenticated_files': len(runtime_files) + len(extra.right.elts),
            'dependency_triples': len(contract['dependencies']), 'profile_headers': len(profile['headers']),
            'categories': categories}


def rejected(blobs, label):
    try:
        analyse(blobs)
    except (RuntimeError, KeyError, StopIteration):
        return
    raise RuntimeError('source mutation accepted: ' + label)


def main():
    blobs = {}
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'canonical input hash differs')
        blobs['root' if row['path'].endswith('/full_driver.py.txt') else 'provider'] = raw
    copies = json.loads((HERE / 'SOURCE-COPIES.json').read_text())['files']
    for row in copies:
        raw = (HERE / row['path']).read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
             'inert source copy differs')
        blobs[row['origin']] = raw
    result = analyse(blobs)
    claims = json.loads((HERE / 'CLAIMS.json').read_text())
    need(claims['expected_successful_preflight'] == {
        'schema': 'h25-public-runtime-preflight-v2', 'authenticated_files': result['authenticated_files'],
        'native_private_access': False, 'cached_admission': False}, 'unbound expected preflight')
    need(claims['V03_complete_family'] is False and claims['runtime_qualified'] is False and
         claims['C05_complete_domain_supplied'] is False and claims['original_activity_credit_added'] == 0,
         'unearned family/runtime/activity credit')
    need(claims['literal_runtime_files'] == result['authenticated_files'] - 1 and
         claims['profile_python_headers'] == result['profile_headers'] and
         claims['literal_dependency_triples'] == result['dependency_triples'] and
         claims['root_selected_driver_entry_available'] is True and
         claims['direct_dependency_branch_launches_compiler'] is False and
         claims['module_import_closure_declared_inert'] is False and
         claims['equal_declared_permission_mode'] == 292 and
         claims['distinct_service_headers'] is True and
         claims['equal_content_swaps'] == ['dict_probe_fields_v1.c', 'field_loader_snapshot_v1.h'] and
         claims['original_weighted_activity_percent'] == 43.5 and claims['costs'] == 'OPEN_NOT_ZERO',
         'source resolution/report boundary differs')
    count = 0
    mutations = []
    bad = copy.copy(blobs)
    tree = ast.parse(bad['provider'])
    assignment(tree, '_RUNTIME_FILES').elts.pop()
    bad['provider'] = ast.unparse(tree).encode()
    mutations.append(('removed runtime entry', bad))
    for key, before, after, label in [
        ('provider', b'"native_private_access": False', b'"native_private_access": True', 'preflight flag'),
        (NATIVE, b'def _dependencies():', b'def _dependencies():\n    cold_build_evidence.run()', 'direct build call'),
        (NATIVE, b"row['sha256'] == expected_sha", b'True', 'dependency digest guard'),
        (DRIVER, b"'mode': 292", b"'mode': 384", 'permission-mode oracle'),
    ]:
        bad = copy.copy(blobs)
        need(before in bad[key], 'source mutation placement missing: ' + label)
        bad[key] = bad[key].replace(before, after, 1)
        mutations.append((label, bad))
    bad = copy.copy(blobs)
    target = 'areas/field-negative-variants-v1/exec_failure/dict_probe_fields_v1.c'
    bad[target] = bytes([bad[target][0] ^ 1]) + bad[target][1:]
    mutations.append(('equal-content fixture drift', bad))
    bad = copy.copy(blobs)
    conditions = json.loads(bad[CONDITIONS])
    conditions['conditions'] = [row for row in conditions['conditions'] if row['id'] != 'C05']
    bad[CONDITIONS] = json.dumps(conditions).encode()
    mutations.append(('omitted C05', bad))
    for label, bad in mutations:
        rejected(bad, label)
        count += 1
    # Finite logical counterexample only: all declared entries/labels can be
    # correct while an independent required witness is absent. This does not
    # implement or execute any original parent control.
    categories = set(result['categories'])
    selected = {(label, 'listed') for label in categories}
    witness = ('system_headers', 'required-but-not-listed')
    required = selected | {witness}
    need({label for label, _ in selected} == categories and selected != required and witness not in selected,
         'inventory completeness counterexample failed')
    print('PASS_V03_SOURCE_PREREQUISITES authenticated_files=217 dependency_triples=29 source_mutants=' +
          str(count) + ' logical_counterexamples=1 full_family=false runtime_qualified=false')


if __name__ == '__main__':
    main()
