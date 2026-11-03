"""New v26 discriminators only; predecessor17 retained solely by reference.

The parent executes once per mode only after independent exact-source review.
Original and opaque payloads remain bytes, never imported, extracted or decoded.
"""
import copy
import json
import os
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / 'constructor'))
sys.path.insert(0, str(SOURCE / 'validation'))
import fresh_sc as new
import plan_validator as plans
import full_prepare_child as child
import run_reviewed_constructor as wrapper

PRE = 'REFUSAL_BEFORE_DESTINATION_ACQUISITION'
SEMANTIC = 'SEMANTIC_PLAN_REFUSAL'
INCOMPLETE = 'INCOMPLETE_NO_PASS'
IDS = ('old_binding', 'hold_cleared_alone', 'missing_v1', 'wrong_v1', 'v5_substitution',
       'missing_opaque', 'wrong_opaque', 'extra_occurrence', 'extra_body_pool',
       'mode_collision', 'session_collision', 'export_collision', 'output_collision',
       'inconsistent_command', 'parent_mismatch', 'stage_name_mismatch',
       'claim_elevation', 'nonce_issued', 'final_close_failure',
       'external_inventory_failure', 'ledger_failure')
SEMANTIC_IDS = {'mode_collision', 'session_collision', 'export_collision',
                'output_collision', 'inconsistent_command', 'nonce_issued'}
OLD = {'manifest_sha256': 'd1241f4c69bea51364463f65086fae5297be8f5e65d6f1c002919cdf2cd7405d',
       'compatibility_sha256': 'c45bb20c5d61c86044072d53fc9b9853eeee5d7739287329513e6078b76a979e',
       'selection_sha256': '1d1b19a92e610d411ffcc2bd44e1a8272a197d1f7f69bc303fda0090256ba0b9'}


class Marker(RuntimeError):
    pass


def reject_semantic(key, original, rows):
    selection = copy.deepcopy(original)
    normal, optimized = selection['modes']['normal'], selection['modes']['optimized']
    if key == 'mode_collision':
        optimized['mode'] = 'normal'
    elif key == 'session_collision':
        optimized['session_directory'] = normal['session_directory']
    elif key == 'export_collision':
        optimized['export_directory'] = normal['export_directory']
    elif key == 'output_collision':
        optimized['producers']['failure_variants']['output_directory'] = normal['producers']['group01']['output_directory']
    elif key == 'inconsistent_command':
        producer = optimized['producers']['failure_variants']
        producer['command'][0] = '/usr/bin/python3.11'
        producer['command_sha256'] = plans.digest(producer['command'])
        producer['plan_sha256'] = plans.digest({k: v for k, v in producer.items() if k != 'plan_sha256'})
    elif key == 'nonce_issued':
        optimized['producers']['failure_variants']['issued'] = True
    caught = None
    try:
        # Deliberately no file-hash comparison: test the actual semantic gate.
        plans.validate_source_plans(selection, rows)
    except ValueError as error:
        caught = error
    new.need(caught is not None, 'semantic mutation must be refused: ' + key)
    if key == 'inconsistent_command':
        new.need(str(caught) == 'inconsistent derived command', 'semantic command refusal independent of hash')
        # Also protect all three separate Group01 compiler commands, with the
        # same reviewed discriminator rather than adding an unreviewed case.
        for i in range(3):
            mutation = copy.deepcopy(original)
            mutation['modes']['normal']['group01_positive_argv'][i][0] = '/bin/false'
            try:
                plans.validate_source_plans(mutation, rows)
            except ValueError as error:
                new.need(str(error) == 'separate ordered group01 three compiler commands', 'positive compiler semantic oracle')
            else:
                raise Marker('mutated group01 compiler plan accepted')
    if key == 'nonce_issued':
        # Generation shares the same explicit DATA envelope. Reserved values
        # and elevated top-level issuance are independently forbidden.
        for which in ('reserved', 'top'):
            mutation = copy.deepcopy(original)
            target = mutation['generation_and_nonce'] if which == 'top' else mutation['modes']['normal']['producers']['group01']
            target['issued' if which == 'top' else 'reserved'] = True
            try:
                plans.validate_source_plans(mutation, rows)
            except ValueError:
                pass
            else:
                raise Marker('issued/reserved DATA accepted')
    return SEMANTIC


def terminal_control(key, root):
    """New final-success gate fixture; no old fault harness is imported/run."""
    raw = b'new v26 terminal fixture\n'
    pin = new.digest(raw)
    rows = [{'occurrence_id': 'terminal', 'logical_name': 'literal terminal fixture',
             'recovered_path': None, 'installed_relative_path': 'body.txt', 'sha256': pin,
             'bytes': len(raw), 'mode': 0o444, 'producer_role': 'OWNED_FIXTURE',
             'pin_provenance': 'new literal fixture', 'availability': 'OWNED_FIXTURE_BYTES', 'required': True}]
    request = {'schema': 'fresh-sc-request-v1', 'subject_kind': 'OWNED_FIXTURE',
               'stage_name': 'fixture-stage', 'manifest': rows, 'manifest_sha256': new.digest(new.canonical(rows)),
               'compatibility_sha256': '0' * 64, 'selection_sha256': '1' * 64,
               'forbidden_runtime_names': list(new.RUNTIME_NAMES), 'claims': dict(new.CLAIMS)}
    owner = new.PreparationOwner(os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
    result = new.prepare_full_stage(request, {pin: raw}, owner)
    new.need(result['status'] == 'INERT_FRESH_STAGE_PREPARED_ONLY', 'intermediate fixture preparation')
    marker = Marker(key)
    if key == 'final_close_failure':
        class FinalClose:
            def close(self, fd):
                os.close(fd)
                raise marker
        # Only still-held root/stage descriptors: installation already returned.
        owner.ops = FinalClose()
    def finish(state):
        new.finish_preparation(owner)
    def capture(state):
        state['partial_inventory'] = wrapper.inventory(root)
        if key == 'external_inventory_failure':
            raise marker
    def ledger(state):
        wrapper.retained_write(root / 'retained-incomplete-ledger.json', state)
        if key == 'ledger_failure':
            raise marker
    state = wrapper.finalize_attempt(True, finish, capture, ledger)
    new.need(state['status'] == 'INCOMPLETE' and state['errors']
             and all(fd is None for fd in owner.fds), 'failed finalization remains incomplete')
    expected_stage = {'final_close_failure': 'finish', 'external_inventory_failure': 'external_inventory',
                      'ledger_failure': 'ledger'}[key]
    new.need(state['errors'][0]['stage'] == expected_stage
             and 'partial_inventory' in state
             and (root / 'retained-incomplete-ledger.json').is_file(), 'external failure partials retained')
    return INCOMPLETE


def main():
    new.need(len(sys.argv) == 3 and sys.argv[2] in ('normal', 'optimized'), 'fresh fixture root and mode')
    base, mode = Path(sys.argv[1]), sys.argv[2]
    new.need(bool(sys.flags.optimize) == (mode == 'optimized'), 'actual controls mode')
    base.mkdir(mode=0o700, parents=False, exist_ok=False)
    pristine, original_pool, compatibility_raw, selection_raw = child.load_source()
    selection = json.loads(selection_raw)
    plans.validate_source_plans(selection, pristine['manifest'])
    v1 = next(r['sha256'] for r in pristine['manifest'] if r['installed_relative_path'] == 'owner/run_controls_v1.py')
    v5 = next(r['sha256'] for r in pristine['manifest'] if r['installed_relative_path'] == 'owner/run_controls_v5.py')
    opaque = next(r['sha256'] for r in pristine['manifest'] if r['installed_relative_path'].endswith('.gz'))
    outcomes = []
    for key in IDS:
        if key in SEMANTIC_IDS:
            outcome = reject_semantic(key, selection, pristine['manifest'])
        else:
            root = base / key
            root.mkdir(mode=0o700)
            if key.endswith('_failure'):
                outcome = terminal_control(key, root)
            else:
                request, pool = copy.deepcopy(pristine), dict(original_pool)
                owner = new.PreparationOwner(os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
                new.bind_full_preparation(owner, pristine, compatibility_raw, selection_raw, mode)
                if key == 'old_binding':
                    request.update(OLD)
                elif key == 'hold_cleared_alone':
                    new.need(new.FULL_SOURCE_HOLD == (), 'isolated-clear scenario requires clear successor HOLD')
                    request = json.loads((SOURCE / 'controls/PREDECESSOR-REQUEST-v1.json').read_bytes())['constructor_request']
                elif key == 'missing_v1':
                    del pool[v1]
                elif key == 'wrong_v1':
                    pool[v1] = original_pool[v1] + b'wrong'
                elif key == 'v5_substitution':
                    pool[v1] = original_pool[v5]
                elif key == 'missing_opaque':
                    del pool[opaque]
                elif key == 'wrong_opaque':
                    pool[opaque] = original_pool[opaque][:-1] + bytes([original_pool[opaque][-1] ^ 1])
                elif key == 'extra_occurrence':
                    row = copy.deepcopy(request['manifest'][-1])
                    row['occurrence_id'] += ':unreviewed-extra'
                    row['installed_relative_path'] = 'owner/unreviewed-extra.py'
                    request['manifest'].append(row)
                    request['manifest_sha256'] = new.digest(new.canonical(request['manifest']))
                elif key == 'extra_body_pool':
                    extra = b'unreferenced new v26 fixture\n'
                    pool[new.digest(extra)] = extra
                elif key == 'stage_name_mismatch':
                    request['stage_name'] = 'wrong-stage'
                elif key == 'claim_elevation':
                    request['claims']['runtime_admission'] = True
                elif key != 'parent_mismatch':
                    raise Marker('unknown pre-I/O case')
                caught = None
                try:
                    new.prepare_full_stage(request, pool, owner)
                except BaseException as error:
                    caught = error
                new.need(caught is not None and caught is owner.primary[0]
                         and owner.next_slot[0] == 1 and not any(root.iterdir())
                         and (owner.creation_lineage is None or not any(r['attempted'] for r in owner.creation_lineage)),
                         'no destination acquisition: ' + key)
                if key == 'parent_mismatch':
                    new.need(str(caught) == 'actual held preparation parent mismatch', 'parent identity decisive predicate')
                try:
                    new.finish_preparation(owner)
                except BaseException as terminal:
                    new.need(terminal is caught, 'pre-I/O direct primary preserved')
                new.need(all(fd is None for fd in owner.fds), 'ordinary owner closed once')
                outcome = PRE
        outcomes.append({'id': key, 'outcome': outcome})
    print(json.dumps({'status': 'NEW_CONTROL_OBSERVATIONS_ONLY', 'controls': outcomes,
                      'claims': new.CLAIMS, 'original_definitions_executed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
