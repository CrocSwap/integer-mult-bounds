"""Independent pure controls. Archived sources are data and AST only."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import re
import types

HERE = Path(__file__).resolve().parent
ROLES = ('pyinit_failure', 'exec_failure')
FILES = ('dict_probe_fields_v1.c', 'field_loader_snapshot_v1.h', 'field_service_v1.h')
CODE_SHA = '438cdc6c8b003d9a1b6a41889d6ac2f3d5bed25f77b430cf3b5f63c36c4e4612'
CHECKS = 0


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def check(value, message):
    global CHECKS
    need(value, message)
    CHECKS += 1


def opened(impl, action, message):
    try:
        action()
    except impl.ConstructionOpen:
        check(True, message)
        return
    raise RuntimeError('unexpected acceptance: ' + message)


def snapshot_inputs():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    data = {}
    for row in pins['snapshots']:
        raw = (HERE / row['path']).read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
             'inert source identity differs')
        data[row['origin']] = raw
    return data


def independent_sites(payloads, stage):
    # This enumerates the known whole-source-pinned literal lines; it is not
    # a general preprocessor or a claim about transitive/implicit includes.
    result = []
    for role in ROLES:
        for name in FILES:
            path = stage + '/areas/field-negative-variants-v1/' + role + '/' + name
            for number, line in enumerate(payloads[(role, name)].decode('ascii').splitlines(), 1):
                if not line.lstrip().startswith('#include'):
                    continue
                match = re.fullmatch(r'\s*#\s*include\s+([<"][^>"]+[>"])\s*', line)
                need(match is not None, 'unexpected nonliteral directive in fixed source')
                result.append((role, path, number, match.group(1)))
    return tuple(result)


def independent_argv(driver_source, stage, output):
    tree = ast.parse(driver_source)
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_variant_main')
    node = next(n.value for n in ast.walk(main) if isinstance(n, ast.Assign) and
                any(isinstance(t, ast.Name) and t.id == 'command' for t in n.targets))
    need(isinstance(node, ast.List) and len(node.elts) == 13, 'original command shape differs')
    prefix = [ast.literal_eval(n) for n in node.elts[:9]]
    need(ast.unparse(node.elts[9]) == "'-I' + plan['include']" and
         ast.unparse(node.elts[10]) == "row['source_path']" and
         ast.literal_eval(node.elts[11]) == '-o' and ast.unparse(node.elts[12]) == 'target',
         'original command binding differs')
    return tuple((role, prefix + ['-I/usr/include/python3.12',
                 stage + '/areas/field-negative-variants-v1/' + role + '/' + FILES[0],
                 '-o', output + '/' + role + '/_h25_dict_probe.cpython-312-x86_64-linux-gnu.so'])
                 for role in ROLES)


def main():
    data = snapshot_inputs()
    raw = (HERE / 'source_roots_v1.py').read_bytes()
    need(len(raw) == 6365 and hashlib.sha256(raw).hexdigest() == CODE_SHA,
         'frozen new pure source differs')
    tree = ast.parse(raw)
    need([ast.unparse(n) for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))] == ['import hashlib'],
         'unexpected pure-component import')
    # Only this new reviewed pure implementation executes. None of the
    # original archived .txt/JSON/C/header inputs is compiled or executed.
    impl = types.ModuleType('c05_pure_component')
    exec(compile(raw, str(HERE / 'source_roots_v1.py'), 'exec', dont_inherit=True), impl.__dict__)
    payloads = {(role, name): data['areas/field-negative-variants-v1/' + role + '/' + name]
                for role in ROLES for name in FILES}
    stage, output = '/owned-stage', '/owned-evidence'
    expected_sites = independent_sites(payloads, stage)
    check(len(expected_sites) == 20, 'twenty independently enumerated literal sites')
    driver = data['areas/field-variant-producer-v2/variant_driver_v1.py']
    expected_argv = independent_argv(driver, stage, output)
    original = copy.copy(payloads)
    normal = impl.source_roots(payloads, stage, output, 'normal')
    optimized = impl.source_roots(payloads, stage, output, 'optimized')
    check(normal['literal_include_obligations'] == expected_sites, 'full fixed site list')
    check(normal['commands'] == expected_argv and all(type(x[1]) is list for x in normal['commands']),
          'unchanged original list-valued argv')
    check(normal['commands'] == optimized['commands'] and normal['mode'] != optimized['mode'],
          'supplied Python-mode binding preserves GCC flags')
    expected_rows = [{'path': stage + '/areas/field-negative-variants-v1/' + role + '/' + name,
                      'sha256': hashlib.sha256(payloads[(role, name)]).hexdigest(),
                      'bytes': len(payloads[(role, name)]), 'mode': 0o444}
                     for role in ROLES for name in FILES]
    check(normal['project_files'] == expected_rows and len(normal['project_files']) == 6,
          'six path occurrences retained; permissions are requirements')
    check(normal['full_c05'] is False and normal['runtime_qualified'] is False,
          'no completeness or runtime authority')
    check(payloads == original, 'constructor leaves input payload mapping unchanged')
    check(sum(len(x) for x in payloads.values()) == 108996, 'project bytes')
    for key in payloads:
        bad = copy.copy(payloads)
        bad[key] = bytes([bad[key][0] ^ 1]) + bad[key][1:]
        opened(impl, lambda: impl.source_roots(bad, stage, output, 'normal'), 'each payload corruption')
    bad = copy.copy(payloads)
    a, b = (ROLES[0], FILES[2]), (ROLES[1], FILES[2])
    bad[a], bad[b] = bad[b], bad[a]
    opened(impl, lambda: impl.source_roots(bad, stage, output, 'normal'), 'distinct service swap')
    for name in FILES[:2]:
        bad = copy.copy(payloads)
        a, b = (ROLES[0], name), (ROLES[1], name)
        bad[a], bad[b] = bad[b], bad[a]
        check(impl.source_roots(bad, stage, output, 'normal') == normal,
              'equal-content swap positive')
    for bad_mode in (False, 0, 'release'):
        opened(impl, lambda: impl.source_roots(payloads, stage, output, bad_mode), 'invalid mode')
    for bad_stage, bad_output in [('/bad/../stage', output), ('relative', output),
                                  (stage, stage + '/nested'), (stage, stage),
                                  (stage, '/bad//output'), (stage, '/')]:
        opened(impl, lambda: impl.source_roots(payloads, bad_stage, bad_output, 'normal'),
               'path/domain refusal')
    for bad in ({}, {**payloads, ('extra', 'key'): b''}, list(payloads.values())):
        opened(impl, lambda: impl.source_roots(bad, stage, output, 'normal'), 'exact bounded payload domain')

    # Explicitly inert namespace DATA; these do not stand for a real Root,
    # owner, syscall result, mount, compiler trace or admitted observer.
    missing = ('MISSING', b'')
    facts = {'/a/x.h.gch': missing, '/a/x.h': missing,
             '/b/x.h.gch': missing, '/b/x.h': ('REGULAR', b'B')}
    chain = ('/a', '/b')
    result = impl.no_pch_prefix('x.h', chain, facts)
    expected = (('/a/x.h.gch', 'MISSING'), ('/a/x.h', 'MISSING'),
                ('/b/x.h.gch', 'MISSING'),
                ('/b/x.h', 'REGULAR', hashlib.sha256(b'B').hexdigest(), 1))
    check(result == (expected, '/b/x.h'), 'conditional first-match prefix')
    for key in ('/a/x.h.gch', '/a/x.h'):
        bad = dict(facts)
        del bad[key]
        opened(impl, lambda: impl.no_pch_prefix('x.h', chain, bad), 'missing preceding observation')
    early = {**facts, '/a/x.h': ('REGULAR', b'A')}
    changed = impl.no_pch_prefix('x.h', chain, early)
    check(changed[1] == '/a/x.h' and changed != result, 'earlier header changes winner')
    reversed_result = impl.no_pch_prefix('x.h', tuple(reversed(chain)), facts)
    check(reversed_result[1] == '/b/x.h' and reversed_result[0] != result[0],
          'search order changes ordered certificate')
    prefix_only = {'/a/x.h.gch': missing, '/a/x.h': ('REGULAR', b'A')}
    check(impl.no_pch_prefix('x.h', chain, prefix_only) == changed,
          'unused lookup suffix not necessary after first winner')
    opened(impl, lambda: impl.no_pch_prefix('x.h', ('/a', '/bad/../suffix'), prefix_only),
           'unused chain paths still validated')
    for disposition, raw_value in [('REGULAR', b'PCH'), ('DIRECTORY', b''), ('SYMLINK', b'alias'), ('ERROR', b'')]:
        bad = dict(facts)
        bad['/a/x.h.gch'] = (disposition, raw_value)
        opened(impl, lambda: impl.no_pch_prefix('x.h', chain, bad), 'unsupported PCH/namespace subcase')
    for bad_name in ('/absolute.h', '../x.h', 'x//y.h', 'x.h\x00'):
        opened(impl, lambda: impl.no_pch_prefix(bad_name, chain, facts), 'unsupported include domain')
    opened(impl, lambda: impl.no_pch_prefix('x.h', ['/a', '/b'], facts), 'exact tuple chain')
    opened(impl, lambda: impl.no_pch_prefix('x.h', ('/a',) * 513, facts), 'chain bound')
    bad = {**facts, '/unused': ('MISSING', b'invented absence bytes')}
    opened(impl, lambda: impl.no_pch_prefix('x.h', chain, bad), 'absence is not a byte input')
    bad = {**facts, '/unused': (True, b'')}
    opened(impl, lambda: impl.no_pch_prefix('x.h', chain, bad), 'exact disposition type')
    # Retain a limitation, not a fabricated stale-namespace rejection: this
    # pure function cannot tell whether its supplied MISSING assertion is true.
    latent_changed_namespace = early
    check(impl.no_pch_prefix('x.h', chain, facts) == result and
          impl.no_pch_prefix('x.h', chain, latent_changed_namespace) != result,
          'stale-data counterexample preserves external authenticity premise')
    check(facts['/a/x.h'] == missing, 'prefix constructor leaves observations unchanged')
    check(impl.CONFIGURATION is None and impl.SOURCE_REVIEW is None and impl.EXECUTION is None,
          'selection markers remain None')

    helper = ast.parse(data['stages/combined-finite-v8/integration/cold_build_evidence.py'])
    launches = [n for n in ast.walk(helper) if isinstance(n, ast.Call) and
                isinstance(n.func, ast.Attribute) and n.func.attr == 'Popen']
    check(len(launches) == 1 and not {'env', 'cwd'} & {kw.arg for kw in launches[0].keywords},
          'original helper Popen has no explicit env/cwd keyword; caller remains open')
    conditions = json.loads(data['areas/field-variant-producer-v2/CONDITIONS.json'])
    check(any(row['id'] == 'C05' and 'Original dependency scan alone is insufficient.' in row['required']
              for row in conditions['conditions']), 'original C05 preserved')
    print('PASS_C05_PURE_SOURCE_ROOTS controls=' + str(CHECKS) +
          ' project_paths=6 literal_sites=20 stale_facts_counterexample=1 full_C05=false runtime_qualified=false')


if __name__ == '__main__':
    main()
