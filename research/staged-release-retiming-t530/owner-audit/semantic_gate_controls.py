#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the preserved auditor and test its exact production semantic gate nodes.

The auditor and frozen inputs remain byte-identical. These are five isolated
in-memory gate tests, not five end-to-end corrupted-artifact replays. Historical
reject() lambdas in the preserved auditor are not counted as negative coverage.
Prepared with substantial OpenAI Codex assistance.
"""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'independent_literal.py'
GATES = {
    'helper_identity': 'complete literal ordered helper identities',
    'window': 'strict/closed actual source windows',
    'family': 'same-call physical family uniqueness',
    'prefix': 'every chronological pending mask is a compact prefix',
    'histogram': 'independent complete histogram',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(path):
    """Select unconditional production statements, failing closed on ambiguity."""
    found = {}
    assignments = {}
    for statement in ast.parse(path.read_text()).body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, ast.Name) and target.id in ('family', 'key', 'sort'):
                need(target.id not in assignments, 'Repeated family computation')
                assignments[target.id] = statement
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if (isinstance(call.func, ast.Name) and call.func.id == 'need'
                and len(call.args) == 2 and isinstance(call.args[1], ast.Constant)
                and call.args[1].value in GATES.values()):
            message = call.args[1].value
            need(message not in found, 'Repeated production gate: ' + message)
            found[message] = statement
    need(set(found) == set(GATES.values()), 'Exact five unconditional production gates')
    need(set(assignments) == {'family', 'key', 'sort'}, 'Exact family recomputation')
    computation = [assignments[name] for name in ('family', 'key', 'sort')]
    need([node.lineno for node in computation] == sorted(node.lineno for node in computation)
         and computation[-1].lineno <= found[GATES['family']].lineno,
         'Family computation precedes its production gate')
    return found, computation


def execute(nodes, context):
    module = ast.Module(body=copy.deepcopy(nodes), type_ignores=[])
    exec(compile(module, str(SOURCE), 'exec'), context)


def rejected(node, context, message):
    try:
        execute([node], context)
    except ValueError as error:
        need(str(error) == message, 'Rejected at an unintended condition: ' + str(error))
        return True
    return False


def mutation(label, context, family_computation):
    # Namespace copies retain baseline storage; only modified arrays are copied.
    changed = dict(context)
    np = context['np']
    if label == 'helper_identity':
        changed['rows'] = context['rows'].copy()
        changed['rows'][1, 1] = changed['rows'][0, 1]
        details = {'row': 1, 'column': 'helper', 'old': int(context['rows'][1, 1]),
                   'new': int(changed['rows'][1, 1])}
    elif label == 'window':
        candidates = np.flatnonzero(context['lo'][context['o'], context['c']] >= 0)
        need(len(candidates) > 0, 'Nonnegative strict endpoint fixture exists')
        row = int(candidates[0])
        changed['t'] = context['t'].copy()
        changed['t'][row] = context['lo'][context['o'][row], context['c'][row]]
        details = {'row': row, 'column': 'time', 'old': int(context['t'][row]),
                   'new': int(changed['t'][row]), 'meaning': 'exact strict lower endpoint'}
    elif label == 'family':
        need(context['t'][0] == context['t'][1], 'Same-call family fixture')
        for name in ('o', 'c', 'p'):
            changed[name] = context[name].copy()
            changed[name][1] = changed[name][0]
        # Recompute the family keys with the production assignments, not a
        # duplicated implementation of the uniqueness predicate or key formula.
        execute(family_computation, changed)
        details = {'row': 1, 'columns': ['owner_replica', 'child', 'port'],
                   'copied_from_row': 0,
                   'meaning': 'two helpers of the same call share a physical family'}
    elif label == 'prefix':
        row = int(context['idx'][0])
        changed['z'] = context['z'].copy()
        changed['z'][row] += 1
        details = {'row': row, 'column': 'offset', 'old': int(context['z'][row]),
                   'new': int(changed['z'][row])}
    elif label == 'histogram':
        changed['profile'] = dict(context['profile'])
        changed['profile'][1] += 1
        details = {'rank': 1, 'old': context['profile'][1], 'new': changed['profile'][1]}
    else:
        raise ValueError('Unknown semantic mutation: ' + label)
    return changed, details


def main():
    need(__debug__ and not sys.flags.optimize, 'Assertions-enabled Python is required')
    started = time.monotonic()
    derivation = json.loads((HERE / 'DERIVATION.json').read_text())
    source_pin = derivation['derived_script_sha256']
    need(sha(SOURCE) == source_pin, 'Authenticated preserved auditor')
    output = Path(os.environ['OWNER_AUDIT_OUTPUT']).resolve()
    semantic_output = output.with_name('SEMANTIC-GATES.json')
    need(not semantic_output.exists(), 'Fresh semantic-gate receipt')
    # Authentication, the complete positive audit, and its original RESULT.json
    # execute once. No producer or validator predicate is replaced or bypassed.
    context = runpy.run_path(str(SOURCE), run_name='__main__')
    gates, family_computation = inventory(SOURCE)
    inherited = HERE / 'upstream/independent_literal.py'
    need(sha(inherited) == derivation['predecessor_script_sha256'], 'Frozen predecessor auditor')
    inherited_gates, inherited_family = inventory(inherited)
    for message in GATES.values():
        need(ast.dump(gates[message], include_attributes=False)
             == ast.dump(inherited_gates[message], include_attributes=False),
             'Same inherited production gate: ' + message)
    need([ast.dump(node, include_attributes=False) for node in family_computation]
         == [ast.dump(node, include_attributes=False) for node in inherited_family],
         'Same inherited family computation')
    baseline_rows = hashlib.sha256(context['rows']).hexdigest()
    baseline_profile = dict(context['profile'])
    tests = []
    for label, message in GATES.items():
        node = gates[message]
        execute([node], dict(context))
        bad, details = mutation(label, context, family_computation)
        need(rejected(node, bad, message), 'Semantic mutation accepted: ' + label)
        disabled = copy.deepcopy(node)
        disabled.value.args[0] = ast.copy_location(ast.Constant(True), disabled.value.args[0])
        ast.fix_missing_locations(disabled)
        need(not rejected(disabled, bad, message),
             'Disabling the gate did not break the negative test: ' + label)
        execute([node], dict(context))
        tests.append({'gate': label, 'source_line': node.lineno, 'message': message,
                      'predicate_sha256': hashlib.sha256(
                          ast.dump(node, include_attributes=False).encode()).hexdigest(),
                      'baseline_passed': True, 'mutation': details,
                      'mutant_rejected_at_expected_gate': True,
                      'disabling_gate_makes_control_fail': True,
                      'restored_baseline_passed': True})
        del bad
    need(hashlib.sha256(context['rows']).hexdigest() == baseline_rows
         and context['profile'] == baseline_profile, 'Baseline semantic inputs unchanged')
    need(sha(SOURCE) == source_pin, 'Preserved auditor unchanged')
    receipt = {
        'status': 'PASS_FIVE_EXACT_PRODUCTION_GATE_MUTATIONS_AND_FIVE_DISABLE_SENSITIVITIES',
        'source_sha256': source_pin, 'predecessor_source_sha256': sha(inherited),
        'checker_sha256': sha(Path(__file__)), 'positive_receipt_sha256': sha(output),
        'roles': len(context['rows']), 'tests': tests, 'seconds': time.monotonic() - started,
        'semantic_mutants_rejected': len(tests), 'gate_disable_sensitivities': len(tests),
        'historical_reject_lambdas_counted': False,
        'scope': 'Fresh authenticated complete positive owner audit followed by five isolated '
                 'production AST gate tests on changed in-memory inputs, each sensitive to disabling '
                 'its gate. Not five end-to-end corrupted-artifact replays. Frozen auditor and '
                 'source manifests are unchanged; historical reject lambdas provide no negative coverage.'}
    semantic_output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': receipt['status'], 'semantic_mutants_rejected': len(tests),
                      'gate_disable_sensitivities': len(tests)}, indent=2))


if __name__ == '__main__':
    main()
