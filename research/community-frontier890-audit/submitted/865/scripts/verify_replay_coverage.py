#!/usr/bin/env python3
"""Versioned evidence coverage, supplementary to immutable frontier bindings.

Credit Lucas (@ljste), PR838, for the ancestor-coverage audit. Prepared for
nightangelflowerwin-ops with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'certificates/replay-coverage/pr741-sw4-v1.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def artifact_path(directory, name):
    require(type(name) is str and name and '\\' not in name, 'Invalid evidence path')
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and '..' not in relative.parts and
            relative.as_posix() == name and ':' not in name, 'Invalid evidence path')
    path = (directory / name).resolve()
    require(path.is_relative_to(directory.resolve()), 'Evidence escapes replay directory')
    return path


def contract():
    value = read(CONTRACT)
    require(value['schema'] == 'integer-mult-replay-coverage-v1' and
            value['id'] == 'pr741-sw4-v1', 'Unsupported replay coverage version')
    producer = ROOT / value['producer']
    require(value['producer'] == 'research/complex-sw4-frame8/verify.py' and
            digest(producer) == value['producer_sha256'], 'Coverage producer version differs')
    require(digest(producer.parent / 'MANIFEST.json') == value['manifest_sha256'] and
            digest(producer.parent / 'data/SPEC.json') == value['spec_sha256'], 'Coverage package version differs')
    tree = ast.parse(producer.read_bytes())
    calls = [n.value for n in tree.body if isinstance(n, ast.Expr) and
             isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'run']
    require([ast.literal_eval(call.args[0]) for call in calls] == value['stages'], 'Contract stages differ from producer')
    lists = [n.value for n in tree.body if isinstance(n, ast.Assign) and
             any(isinstance(t, ast.Name) and t.id == 'files' for t in n.targets)]
    require(len(lists) == 1, 'Producer artifact declaration differs')
    fixed = ast.literal_eval(lists[0])
    require(type(value['artifacts']) is list and len(value['artifacts']) == 44 and
            len(set(value['artifacts'])) == 44 and set(fixed) <= set(value['artifacts']), 'Contract artifact inventory differs')
    dynamic = set(value['artifacts']) - set(fixed)
    require(len(fixed) == 34 and len(dynamic) == 10 and
            all(name.startswith('local/') for name in dynamic), 'Contract local artifact inventory differs')
    for name in value['stages']:
        require(type(name) is str and '/' not in name and '\\' not in name and ':' not in name, 'Invalid stage name')
    return value


def check_ancestor(bit, complex_dir):
    """Require source-versioned complete coverage, then all original checks."""
    value = contract()
    receipt = read(complex_dir / 'RECEIPT.json')
    stages = receipt['stages']
    require(type(stages) is list and [s['name'] for s in stages] == value['stages'], 'Required ancestry stage sequence differs')
    require(all(type(s['exit_code']) is int and s['exit_code'] == 0 for s in stages), 'Required ancestry stage failed')
    artifacts = receipt['artifacts']
    require(type(artifacts) is dict and set(artifacts) == set(value['artifacts']), 'Required ancestry artifact inventory differs')
    require(read(complex_dir / 'STAGES.json') == stages, 'Ancestry execution record differs from receipt')
    for name, expected in artifacts.items():
        require(type(expected) is str and digest(artifact_path(complex_dir, name)) == expected, 'Required ancestry artifact hash differs: ' + name)
    for stage in stages:
        require(type(stage['log_sha256']) is str and
                digest(artifact_path(complex_dir, stage['name'] + '.log')) == stage['log_sha256'], 'Required ancestry log differs')
    from verify_frontier741_bindings import check
    return check(bit, complex_dir)


def check_selected(work, ancestor=None):
    """Enforce coverage in the complete selected PR799 replay, without reuse guesses."""
    ancestry_record = read(work / 'ANCESTRY.json')
    require(type(ancestry_record['reused']) is bool, 'Invalid ancestry reuse flag')
    require(ancestor is not None or ancestry_record['reused'] is False,
            'Explicit ancestor path required for reused evidence')
    parent = ancestor if ancestor is not None else work / 'ancestor'
    ancestry = check_ancestor(parent / 'bit', parent / 'complex')
    selected = contract()['selected']
    require(selected['id'] == 'pr799-x4-v1', 'Unsupported selected coverage version')
    for name, expected_hash in selected['source_sha256'].items():
        require(digest(artifact_path(ROOT, name)) == expected_hash, 'Selected coverage producer version differs: ' + name)
    require(ancestry_record['binding'] == ancestry, 'Ancestry receipt binding differs')
    expected = ([] if ancestry_record['reused'] else ['ancestor']) + selected['stages']
    stages = read(work / 'STEPS.json')
    require(type(stages) is list and [s['name'] for s in stages] == expected and
            all(type(s['exit_code']) is int and s['exit_code'] == 0 for s in stages), 'Required selected stage sequence differs')
    for stage in stages:
        require(digest(artifact_path(work, stage['name'] + '.log')) == stage['log_sha256'], 'Selected stage log differs')
    # The original binding independently validates the named native stages.
    # Also require each corresponding native log to exist. Native STEPS.json
    # does not contain log digests, so no authentication claim is made here.
    for stage in read(work / 'native/STEPS.json'):
        require(type(stage['exit_code']) is int and stage['exit_code'] == 0, 'Required native stage failed')
        require(artifact_path(work / 'native', stage['step'] + '.log').is_file(), 'Required native stage log missing')
    from verify_frontier799_bindings import check
    result = check(parent, work / 'native', work / 'global',
                   work / 'INDEPENDENT-LOCAL.json', work / 'INDEPENDENT-PRICE.json')
    recorded = read(work / 'RESULT.json')
    require(recorded['status'] == result['status'] and recorded['kappa'] == result['kappa'] and
            recorded['ancestry'] == result['ancestry'] and
            recorded['reused_ancestry'] is ancestry_record['reused'], 'Selected result binding differs')
    return dict(status='PASS_COMPLETE_PR799_REPLAY_COVERAGE', kappa=result['kappa'],
                decimal=result['decimal'],
                coverage_contract=value_id(), contract_sha256=digest(CONTRACT),
                selected_binding=result, reused_ancestry=ancestry_record['reused'],
                scope='Required evidence presence, ordered stages and existing hash/mathematical bindings. Not execution authentication or a full multiplication proof.')


def value_id():
    return 'pr741-sw4-v1'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frontier', choices=['741', '799'], required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--ancestor', type=Path)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    if a.frontier == '741':
        require(a.ancestor is None, 'Ancestor flag is only for PR799')
        result = check_ancestor(a.work / 'bit', a.work / 'complex')
        result = dict(status='PASS_COMPLETE_PR741_REPLAY_COVERAGE', binding=result,
                      coverage_contract=value_id(), contract_sha256=digest(CONTRACT))
    else:
        result = check_selected(a.work, a.ancestor)
    if a.out:
        a.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(result['status'])


if __name__ == '__main__':
    main()
