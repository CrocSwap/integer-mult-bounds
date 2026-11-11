# SPDX-License-Identifier: Apache-2.0
"""Check this source archive and replay its finite, relocated JSON graphs only."""

import ast
import hashlib
import json
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def integrity():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_bytes())
    need(manifest['schema'] == 'h25-v02-source-archive-manifest-v1', 'manifest schema')
    rows = manifest['files']
    names = [row['path'] for row in rows]
    need(len(names) == len(set(names)), 'duplicate manifest entry')
    need(all(name == PurePosixPath(name).name and name not in ('.', '..', 'MANIFEST.json')
             for name in names), 'nonlocal manifest entry')
    actual = {path.name for path in ROOT.iterdir() if path.name != 'MANIFEST.json'}
    need(set(names) == actual, 'archive file set differs')
    for row in rows:
        path = ROOT / row['path']
        need(path.is_file() and not path.is_symlink(), 'nonregular archive entry')
        data = path.read_bytes()
        need(len(data) == row['bytes'], 'archive byte count differs: ' + row['path'])
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'archive hash differs: ' + row['path'])
    return len(rows)


class StaticProjection(dict):
    def __init__(self, graph, prefixes):
        super().__init__(graph)
        self.prefixes = tuple(prefixes)

    def get(self, key, default=None):
        need(not any(key == prefix or key.startswith(prefix + '/') for prefix in self.prefixes),
             'lookup enters a dynamic or writable path: ' + key)
        return super().get(key, default)


def replay():
    fixture = json.loads((ROOT / 'FIXTURE.json').read_bytes())
    provenance = json.loads((ROOT / 'SOURCE_MAP.json').read_bytes())
    need(fixture['schema'] == 'h25-v02-exported-static-input-fixture-v1', 'fixture schema')
    raw = (ROOT / 'literal_walk.py').read_bytes()
    tree = ast.parse(raw)
    need(len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)
         and tree.body[0].name == 'literal_walk', 'pure walker structure differs')
    node = tree.body[0]
    body = b''.join(raw.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])
    need(hashlib.sha256(body).hexdigest() == provenance['literal_walk_body_sha256'],
         'retained walker body differs')
    namespace = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<pinned-pure-walker>', 'exec'), namespace)
    walk = namespace['literal_walk']
    rows = fixture['compiler_rows']
    declared = {row['path'] for row in rows}
    need(len(rows) == len(declared) == 471 and len(rows) <= 512, 'candidate row count differs')
    need(sum(row['bytes'] for row in rows) == 99377921, 'candidate total bytes differ')
    need(max(row['bytes'] for row in rows) == 30487984, 'candidate largest row differs')
    required = fixture['required_auxiliary_file_from_retained_open_evidence']

    def require_auxiliary(paths):
        need(required in paths, 'retained gconv requirement missing')

    require_auxiliary(declared)
    paths = fixture['ordinary_lookup_paths']
    specs = fixture['literal_specs_first_missing']
    need(len(paths) == len(set(paths)) == 6424 and len(specs) == 12, 'frontier size differs')
    need(len(fixture['original_source_condition_assumptions']) == 56, 'assumption count differs')
    base, census = fixture['baseline_graph'], fixture['census_graph']
    need(len(base) == 749 and len(census) == 751, 'graph size differs')
    need(sum(row['kind'] == 'regular' for row in base.values()) == 638, 'baseline regular count differs')
    need(sum(row['kind'] == 'regular' for row in census.values()) == 640, 'census regular count differs')
    need(all(census.get(path) == row for path, row in base.items()), 'baseline nodes changed')
    need(census.keys() - base.keys() == {
        '/usr/lib/python3.12/lib-dynload/_json.cpython-312-x86_64-linux-gnu.so', '/v02-census.py'
    }, 'census additions differ')
    for row in rows:
        need(base.get(row['path']) == {'kind': 'regular', **{k: v for k, v in row.items() if k != 'path'}},
             'compiler row differs from graph: ' + row['path'])

    def inspect(graph):
        projected = StaticProjection(graph, fixture['writable_or_dynamic_prefixes'])
        outcomes = []
        present = absent = 0
        for path in paths:
            outcome = walk(path, projected)
            if 'resolved' in outcome:
                target = outcome['resolved']
                need(not path.endswith('.gch'), 'earlier PCH candidate present: ' + path)
                need(projected[target]['kind'] == 'regular' and target in declared,
                     'lookup reaches undeclared C05 row: ' + path)
                present += 1
            else:
                need(set(outcome) == {'first_missing'}, 'non-directory lookup outcome')
                absent += 1
            outcomes.append((path, outcome))
        need((present, absent) == (354, 6070), 'lookup partition differs')
        for path, missing in specs.items():
            outcome = walk(path, projected)
            need(outcome == {'first_missing': missing}, 'literal specs first-missing differs')
            outcomes.append((path, outcome))
        return outcomes

    baseline_outcomes = inspect(base)
    need(inspect(census) == baseline_outcomes, 'census outcomes differ')
    gch = '/usr/include/python3.12/Python.h.gch'
    shadow = next(path for path in paths if '/exec_failure/internal/pycore_dict.h' in path)
    controls = {
        'earlier_pch_regular': ({gch: {'kind': 'regular'}}, 'earlier PCH candidate present'),
        'earlier_pch_directory': ({gch: {'kind': 'directory'}}, 'earlier PCH candidate present'),
        'quote_start_shadow': ({str(PurePosixPath(shadow).parent): {'kind': 'directory'},
                                shadow: {'kind': 'regular'}}, 'lookup reaches undeclared C05 row'),
    }
    checked = []
    for name, (replacement, expected) in controls.items():
        need(not base.keys() & replacement.keys(), 'control overwrites retained node')
        need(not declared & replacement.keys(), 'control overwrites declared input')
        try:
            inspect(base | replacement)
        except RuntimeError as error:
            need(str(error).startswith(expected), 'wrong rejection: ' + name)
            checked.append(name)
        else:
            raise RuntimeError('mutated graph accepted: ' + name)
    try:
        require_auxiliary(declared - {required})
    except RuntimeError as error:
        need(str(error) == 'retained gconv requirement missing', 'wrong auxiliary rejection')
        checked.append('missing_named_gconv_row')
    else:
        raise RuntimeError('missing named gconv row accepted')
    return {'compiler_rows': len(rows), 'candidate_bytes': 99377921, 'baseline_nodes': len(base),
            'census_nodes': len(census), 'lookup_names_per_graph': len(paths),
            'declared_regular_outcomes': 354, 'first_missing_outcomes': 6070,
            'specs_paths_per_graph': len(specs), 'controls_rejected': checked,
            'original_commands_executed': 0, 'original_omission_cases_accepted': 0}


if __name__ == '__main__':
    count = integrity()
    print(json.dumps({'status': 'PASS', 'archive_files_checked': count, 'scope': 'exported finite JSON graphs only',
                      **replay()}, sort_keys=True))
