"""Parent-only single-attempt epoch source; no execution authority is configured.

Parent authority and run tickets are identity capabilities in the trusted parent
process. They are never serialized or sent to a child. This is not a Python
sandbox against code already executing inside that trusted parent. The future
source-fixed supervisor must authenticate original compiler/terminal/raw data
before submitting a completion; a child JSON object or saved PASS is not that
call. The missing supervisor adapter is an explicit independent-review blocker.
"""
from dataclasses import dataclass
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import epoch_stop_v5 as stopping

CONFIGURATION = None
SOURCE_REVIEW = None
EXECUTION_APPROVAL = None
FUNDING = None
_RESERVED_EPOCHS = set()
_PARENT_OWNERS = []
_TYPE = type


@dataclass(frozen=True, slots=True)
class ParentCompletion:
    """In-memory result of the separately pinned parent evidence checker.

    Cannot be reconstructed from a child report as authority. All raw evidence
    remains referenced by producer_record and must be re-read by each consumer.
    Whole-domain closure is stronger than a compiler's direct-child wait.
    """
    producer_ticket: object
    checker_sha256: str
    observation_sha256: str
    generation: str
    mode: str
    producer_role: str
    process_id: int
    process_start_ticks: int
    direct_child_reaped: bool
    whole_process_domain_closed: bool
    own_in_process_obligations_authenticated: bool
    original_attempts_and_logs_authenticated: bool
    final_source_custody_authenticated: bool
    returned_groups_captured: bool


def _gate() -> None:
    schema.exact(CONFIGURATION, ('parent_checker_sha256', 'configuration_sha256'))
    schema.exact(SOURCE_REVIEW, ('review_sha256',))
    schema.exact(EXECUTION_APPROVAL, ('external_launch_policy_sha256',))
    schema.exact(FUNDING, ('reservation_sha256',))
    for record in (CONFIGURATION, SOURCE_REVIEW, EXECUTION_APPROVAL, FUNDING):
        for value in record.values():
            schema.digest(value)


_COMPLETION_FIELDS = ('producer_ticket', 'checker_sha256', 'observation_sha256', 'generation', 'mode',
    'producer_role', 'process_id', 'process_start_ticks', 'direct_child_reaped', 'whole_process_domain_closed',
    'own_in_process_obligations_authenticated', 'original_attempts_and_logs_authenticated',
    'final_source_custody_authenticated', 'returned_groups_captured')
_COMPLETION_GETTERS = tuple(ParentCompletion.__dict__[name].__get__ for name in _COMPLETION_FIELDS)


def _completion_values(observation) -> dict:
    schema.need(_TYPE(observation) is ParentCompletion, 'exact parent completion type required')
    values = {name: getter(observation, ParentCompletion)
              for name, getter in zip(_COMPLETION_FIELDS, _COMPLETION_GETTERS)}
    schema.need(_TYPE(values['producer_ticket']) is object, 'exact opaque producer ticket required')
    schema.digest(values['checker_sha256'])
    schema.digest(values['observation_sha256'])
    schema.label(values['generation'])
    schema.choice(values['mode'], ('normal', 'optimized'))
    schema.choice(values['producer_role'], schema.PRODUCERS)
    schema.integer(values['process_id'], 1, (1 << 31) - 1)
    schema.integer(values['process_start_ticks'], 1, (1 << 64) - 1)
    for name in _COMPLETION_FIELDS[8:]:
        schema.boolean(values[name])
    return values


def _clone(value: dict) -> dict:
    return schema.decode(schema.canonical(value))


def _plan(value: dict, role: str) -> None:
    schema.choice(role, schema.PRODUCERS)
    schema.exact(value, ('role', 'generation', 'stage_sha256', 'command_sha256', 'root_sha256',
                        'artifact_plans'))
    schema.choice(value['role'], schema.PRODUCERS)
    schema.need(value['role'] == role, 'planned producer role differs')
    schema.label(value['generation'])
    for key in ('stage_sha256', 'command_sha256', 'root_sha256'):
        schema.digest(value[key])
    roles = schema.ROLES[:3] if role == 'group01' else schema.ROLES[3:]
    schema.need(type(value['artifact_plans']) is list and len(value['artifact_plans']) == len(roles),
                'planned build count differs')
    for artifact_role, row in zip(roles, value['artifact_plans']):
        schema.exact(row, ('role', 'command_sha256', 'profile', 'original_output_path'))
        schema.choice(row['role'], schema.ROLES)
        schema.need(row['role'] == artifact_role, 'planned artifact role differs')
        schema.digest(row['command_sha256'])
        schema.profile(row['profile'])
        schema.path(row['original_output_path'])


_STATE_KEYS = ('_authority', '_bytes', '_children', '_copies', '_directory', '_epoch_id', '_error_owner', '_failure_fallback', '_generations', '_intent_file', '_manifest', '_manifest_file', '_mode', '_occupied_inodes', '_occupied_paths', '_plans', '_processes', '_producers', '_state', '_stop', '_tickets')


def _registry() -> list:
    schema.need(_TYPE(_PARENT_OWNERS) is list and len(_PARENT_OWNERS) <= 2,
                'original parent registry shape differs')
    for record in _PARENT_OWNERS:
        schema.need(_TYPE(record) is tuple and len(record) == 2, 'original parent registry row differs')
        schema.need(_TYPE(record[0]) is ParentEpoch, 'original parent registry identity differs')
        schema.exact(record[1], _STATE_KEYS)
    return _PARENT_OWNERS


def _constructor_identity(owner) -> None:
    schema.need(_TYPE(owner) is ParentEpoch, 'exact parent owner required')
    records = _registry()
    schema.need(len(records) < 2 and not any(owner is record[0] for record in records),
                'parent constructor instance reused or finite bound exceeded')


def _registered_parent(owner) -> tuple:
    # Identity only. Never read owner.__dict__ or dispatch owner helpers.
    schema.need(_TYPE(owner) is ParentEpoch, 'exact parent owner required')
    for original in _registry():
        if owner is original[0]:
            return original  # Canonical constructor-held object and state.
    raise schema.EpochStop('parent was not original constructor instance')


def _entry_state(owner, authority) -> dict:
    canonical, state = _registered_parent(owner)
    _gate()
    schema.need(authority is state['_authority'], 'parent capability differs')
    schema.need(state['_stop'][1] is None, 'epoch has a retained terminal failure')
    schema.choice(state['_state'], ('RESERVED', 'PRODUCERS_PENDING', 'EXPORT_READY',
        'EXPORT_ATTEMPT_CONSUMED', 'COMMITTED', 'STOP', 'CLOSED'))
    schema.need(state['_state'] not in ('STOP', 'CLOSED'), 'epoch is terminal')
    return state


def _failed_state(state, operation: str, error) -> None:
    # Only a source-owned registry sidecar is used. The supplied instance's
    # _owner/_failed attributes are never looked up, even on failure paths.
    schema.need(any(state is record[1] for record in _registry()), 'failure state not owned')
    schema.text(operation, 96)
    state['_state'] = 'STOP'
    if state['_stop'][1] is error:
        try:
            schema.retain_primary(state['_error_owner'], error, operation)
        except BaseException as custody_failure:
            if state['_failure_fallback'][0] is None:
                state['_failure_fallback'][0] = custody_failure
            return
        try:
            stopping.retain_stop(state['_directory'], operation, state['_error_owner'])
        except BaseException as evidence_failure:
            if state['_failure_fallback'][1] is None:
                state['_failure_fallback'][1] = evidence_failure
            try:
                schema.retain_secondary(state['_error_owner'], evidence_failure, 'stop-capture', None)
            except BaseException as custody_failure:
                if state['_failure_fallback'][2] is None:
                    state['_failure_fallback'][2] = custody_failure


class ParentEpoch:
    """One parent instance; two producers, five exports, thirteen child attempts.

    Any caught operational failure moves state to STOP permanently. Tickets are
    burned before validation/I/O. No serialized-state restore or retry exists.
    The constructor does not create directories; the supervised parent must own
    fresh exclusive directories and charge their creation/retention separately.
    """
    def __init__(self, authority: object, epoch_id: str, mode: str,
                 export_directory: str, producer_plans: list[dict]):
        _constructor_identity(self)
        _gate()
        schema.need(_TYPE(authority) is object, 'trusted parent capability must be exact object')
        schema.label(epoch_id)
        schema.choice(mode, ('normal', 'optimized'))
        schema.path(export_directory)
        schema.need(epoch_id not in _RESERVED_EPOCHS and len(_RESERVED_EPOCHS) < 2,
                    'parent epoch reused or finite mode count exceeded')
        # Reservation precedes all further work; invalid construction burns id.
        _RESERVED_EPOCHS.add(epoch_id)
        state = {}
        state['_state'] = 'RESERVED'
        state['_authority'] = authority
        state['_epoch_id'], state['_mode'] = epoch_id, mode
        state['_directory'] = export_directory
        state['_plans'], state['_tickets'], state['_producers'] = {}, {}, {}
        state['_children'], state['_generations'], state['_processes'] = {}, set(), set()
        state['_occupied_paths'], state['_occupied_inodes'] = set(), set()
        state['_copies'], state['_bytes'] = 0, 0
        state['_manifest'] = state['_manifest_file'] = state['_intent_file'] = None
        state['_stop'] = [None, None]
        state['_failure_fallback'] = [None, None, None, None]
        state['_error_owner'] = schema.make_error_owner()
        _PARENT_OWNERS.append((self, state))
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            schema.need(type(producer_plans) is list and len(producer_plans) == 2, 'two producer plans required')
            for role, plan in zip(schema.PRODUCERS, producer_plans):
                _plan(plan, role)
                schema.need(plan['generation'] not in state['_generations'], 'producer generation reused')
                state['_generations'].add(plan['generation'])
                state['_plans'][role] = _clone(plan)
            copying.require_entries(state['_directory'], (), error_owner=state['_error_owner'])
            intent = {'schema': 'h25-negative-epoch-intent-v3', 'epoch_id': epoch_id, 'mode': mode,
                      'producer_plans': [state['_plans'][role] for role in schema.PRODUCERS],
                      'restore_or_retry_allowed': False}
            state['_intent_file'] = copying.write_once(state['_directory'] + '/epoch-intent.json', schema.canonical(intent), error_owner=state['_error_owner'])
            state['_state'] = 'PRODUCERS_PENDING'
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'constructor'
            try:
                _failed_state(state, 'constructor', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def _owner(self, authority: object) -> None:
        _entry_state(self, authority)

    def _failed(self, operation: str, error: BaseException) -> None:
        canonical, state = _registered_parent(self)
        stop_slots, fallback_slots = state['_stop'], state['_failure_fallback']
        if stop_slots[1] is None:
            stop_slots[1] = error
            stop_slots[0] = operation
        try:
            _failed_state(state, operation, error)
        except BaseException as helper_error:
            if fallback_slots[3] is None:
                fallback_slots[3] = helper_error


    def reserve_producer(self, authority: object, role: str) -> object:
        state = _entry_state(self, authority)
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            schema.choice(role, schema.PRODUCERS)
            schema.need(state['_state'] == 'PRODUCERS_PENDING' and role in schema.PRODUCERS and
                        role not in state['_tickets'], 'producer attempt already consumed/unknown')
            ticket = object()
            state['_tickets'][role] = {'ticket': ticket, 'state': 'ATTEMPT_RESERVED'}
            return ticket
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'reserve_producer'
            try:
                _failed_state(state, 'reserve_producer', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def accept_completed_producer(self, authority: object, ticket: object,
                                  observation: ParentCompletion, producer_record: dict) -> None:
        state = _entry_state(self, authority)
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            matches = [role for role, row in state['_tickets'].items() if row['ticket'] is ticket]
            schema.need(len(matches) == 1, 'unknown producer attempt capability')
            role = matches[0]
            attempt = state['_tickets'][role]
            schema.need(attempt['state'] == 'ATTEMPT_RESERVED', 'producer completion replay')
            attempt['state'] = 'COMPLETION_CONSUMED'
            observed = _completion_values(observation)
            schema.need(observed['producer_ticket'] is ticket,
                        'serialized/replayed completion is not this parent attempt')
            schema.need(observed['checker_sha256'] == CONFIGURATION['parent_checker_sha256'],
                        'parent completion checker source differs')
            schema.digest(observed['observation_sha256'])
            schema.integer(observed['process_id'], 1, (1 << 31) - 1)
            schema.integer(observed['process_start_ticks'], 1, (1 << 64) - 1)
            process_key = (observed['process_id'], observed['process_start_ticks'])
            schema.need(process_key not in state['_processes'], 'producer process generation reused')
            state['_processes'].add(process_key)
            plan = state['_plans'][role]
            schema.need(observed['generation'] == plan['generation'] and observed['mode'] == state['_mode'] and
                        observed['producer_role'] == role, 'terminal observation independent role/generation differs')
            for value in (observed['direct_child_reaped'], observed['whole_process_domain_closed'],
                          observed['own_in_process_obligations_authenticated'],
                          observed['original_attempts_and_logs_authenticated'],
                          observed['final_source_custody_authenticated'], observed['returned_groups_captured']):
                schema.need(value is True, 'parent completion obligation absent')
            schema.producer(producer_record)
            record = _clone(producer_record)
            schema.need(record['completion_checker_sha256'] == observed['checker_sha256'] and
                        record['parent_observation']['sha256'] == observed['observation_sha256'],
                        'parent observation bytes/checker binding differs')
            for key in ('role', 'generation', 'stage_sha256', 'command_sha256', 'root_sha256'):
                schema.need(record[key] == plan[key], 'producer independent plan differs')
            for item, planned in zip(record['builds'], plan['artifact_plans']):
                schema.need(item['role'] == planned['role'] and item['command_sha256'] == planned['command_sha256'] and
                            item['profile'] == planned['profile'] and
                            item['original_output']['path'] == planned['original_output_path'],
                            'build original command/source/profile/path differs')
                for key, bound in (('original_output', schema.FILE_BYTES), ('original_receipt', 65536),
                                   ('attempt', 65536), ('journal', schema.JOURNAL_BYTES),
                                   ('stdout', schema.LOG_BYTES), ('stderr', schema.LOG_BYTES)):
                    copying.verify(item[key], bound, error_owner=state['_error_owner'])
                original = item['original_output']
                schema.need(original['path'] not in state['_occupied_paths'] and
                            schema.inode(original) not in state['_occupied_inodes'], 'producer output aliases another role')
                state['_occupied_paths'].add(original['path'])
                state['_occupied_inodes'].add(schema.inode(original))
            for key in ('terminal', 'raw_result', 'raw_groups', 'final_source_custody', 'parent_observation'):
                copying.verify(record[key], schema.RAW_RESULT_BYTES, error_owner=state['_error_owner'])
            # No control/PASS/native result is returned to a child as authority.
            state['_producers'][role] = record
            attempt['state'] = 'AUTHENTICATED_COMPLETED'
            if len(state['_producers']) == 2:
                state['_state'] = 'EXPORT_READY'
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'accept_completed_producer'
            try:
                _failed_state(state, 'accept_completed_producer', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def commit_exports(self, authority: object) -> dict:
        state = _entry_state(self, authority)
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            schema.need(state['_state'] == 'EXPORT_READY', 'partial/failed producer epoch cannot export')
            state['_state'] = 'EXPORT_ATTEMPT_CONSUMED'
            copying.verify(state['_intent_file'], schema.RECORD_BYTES, error_owner=state['_error_owner'])
            copying.require_entries(state['_directory'], ('epoch-intent.json',), error_owner=state['_error_owner'])
            exports = []
            for parent in (state['_producers'][role] for role in schema.PRODUCERS):
                for item in parent['builds']:
                    destination = state['_directory'] + '/' + item['role'] + '.artifact'
                    schema.need(destination not in state['_occupied_paths'], 'export path alias')
                    copy = copying.copy_once(item['original_output'], destination, tuple(state['_occupied_inodes']), error_owner=state['_error_owner'])
                    state['_bytes'] += copy['bytes']
                    schema.need(state['_bytes'] <= schema.MAX_EPOCH_FILE_BYTES, 'aggregate copy payload bound exceeded')
                    state['_occupied_paths'].add(copy['path'])
                    state['_occupied_inodes'].add(schema.inode(copy))
                    exports.append({'role': item['role'], 'build_sha256': schema.sha(schema.canonical(item)), 'file': copy})
            manifest = {'schema': schema.SCHEMA, 'epoch_id': state['_epoch_id'], 'mode': state['_mode'],
                        'publication_state': 'COMMITTED', 'intent': state['_intent_file'],
                        'producers': [state['_producers'][role] for role in schema.PRODUCERS],
                        'exports': exports, 'not_runtime_authority': True}
            schema.epoch(manifest)
            # Recheck every source/store before the publication write.
            for producer in manifest['producers']:
                for item in producer['builds']:
                    copying.verify(item['original_output'], error_owner=state['_error_owner'])
            for row in exports:
                copying.verify(row['file'], error_owner=state['_error_owner'])
            raw = schema.canonical(manifest)
            published = copying.write_once(state['_directory'] + '/epoch.json', raw, error_owner=state['_error_owner'])
            copying.require_entries(state['_directory'], tuple(role + '.artifact' for role in schema.ROLES) + ('epoch.json', 'epoch-intent.json'), error_owner=state['_error_owner'])
            state['_manifest'], state['_manifest_file'] = manifest, published
            state['_state'] = 'COMMITTED'
            return _clone(published)
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'commit_exports'
            try:
                _failed_state(state, 'commit_exports', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def claim_child(self, authority: object, group: str, generation: str,
                    launch_binding: dict, private_directory: str) -> tuple[dict, dict]:
        state = _entry_state(self, authority)
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            schema.need(state['_state'] == 'COMMITTED', 'uncommitted epoch cannot be consumed')
            roles = schema.required_roles(group)
            schema.label(generation)
            schema.need(group not in state['_children'] and generation not in state['_generations'],
                        'child group/generation replay')
            # Burn group/generation before any caller data check or filesystem IO.
            state['_children'][group] = {'generation': generation, 'state': 'ATTEMPT_CONSUMED'}
            state['_generations'].add(generation)
            schema.launch(launch_binding)
            schema.path(private_directory)
            copying.require_entries(private_directory, (), error_owner=state['_error_owner'])
            copying.require_entries(state['_directory'], tuple(role + '.artifact' for role in schema.ROLES) + ('epoch.json', 'epoch-intent.json'), error_owner=state['_error_owner'])
            copying.verify(state['_intent_file'], schema.RECORD_BYTES, error_owner=state['_error_owner'])
            copying.verify(state['_manifest_file'], schema.RECORD_BYTES, error_owner=state['_error_owner'])
            for row in state['_manifest']['exports']:
                copying.verify(row['file'], error_owner=state['_error_owner'])
            copies = []
            for role in roles:
                source = next(row for row in state['_manifest']['exports'] if row['role'] == role)
                destination = private_directory + '/' + role + '.artifact'
                schema.need(destination not in state['_occupied_paths'] and state['_copies'] < schema.MAX_PRIVATE_COPIES,
                            'private path/copy bound differs')
                state['_copies'] += 1
                copy = copying.copy_once(source['file'], destination, tuple(state['_occupied_inodes']), error_owner=state['_error_owner'])
                state['_bytes'] += copy['bytes']
                schema.need(state['_bytes'] <= schema.MAX_EPOCH_FILE_BYTES, 'aggregate copy payload bound exceeded')
                state['_occupied_paths'].add(copy['path'])
                state['_occupied_inodes'].add(schema.inode(copy))
                copies.append({'role': role, 'build_sha256': source['build_sha256'],
                               'source': source['file'], 'destination': copy})
            claim = {'schema': schema.CLAIM_SCHEMA, 'epoch_id': state['_epoch_id'], 'mode': state['_mode'],
                     'group': group, 'generation': generation, 'manifest_sha256': state['_manifest_file']['sha256'],
                     'launch': _clone(launch_binding), 'copies': copies, 'local_compilations': 0,
                     'not_runtime_authority': True, 'admission': 'CURRENT_CHILD_CHECKS_REQUIRED'}
            schema.claim(claim, state['_manifest'], launch_binding, group, generation, private_directory)
            published = copying.write_once(private_directory + '/import-claim.json', schema.canonical(claim), error_owner=state['_error_owner'])
            copying.require_entries(private_directory, tuple(role + '.artifact' for role in roles) + ('import-claim.json',), error_owner=state['_error_owner'])
            copying.require_entries(state['_directory'], tuple(role + '.artifact' for role in schema.ROLES) + ('epoch.json', 'epoch-intent.json'), error_owner=state['_error_owner'])
            state['_children'][group]['state'] = 'CLAIM_ISSUED'
            state['_children'][group]['claim'] = published
            return _clone(claim), _clone(published)
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'claim_child'
            try:
                _failed_state(state, 'claim_child', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def close(self, authority: object) -> dict:
        state = _entry_state(self, authority)
        _stop_slots, _fallback_slots = state['_stop'], state['_failure_fallback']
        try:
            schema.need(state['_state'] == 'COMMITTED' and tuple(sorted(state['_children'])) == schema.GROUPS and
                        all(row['state'] == 'CLAIM_ISSUED' for row in state['_children'].values()) and
                        state['_copies'] == schema.MAX_PRIVATE_COPIES, 'core epoch claim schedule incomplete')
            state['_state'] = 'CLOSED'
            return {'schema': 'h25-negative-epoch-accounting-v3', 'epoch_id': state['_epoch_id'], 'mode': state['_mode'],
                    'exports': 5, 'private_copies': state['_copies'], 'copy_payload_bytes': state['_bytes'],
                    'child_runtime_results': 'NOT_ADMITTED_BY_THIS_API', 'complete_cost': None}
        except BaseException as error:
            if _stop_slots[1] is None:
                _stop_slots[1] = error
                _stop_slots[0] = 'close'
            try:
                _failed_state(state, 'close', error)
            except BaseException as helper_error:
                if _fallback_slots[3] is None:
                    _fallback_slots[3] = helper_error
            raise

    def stop_evidence(self, authority: object) -> tuple:
        canonical, state = _registered_parent(self)
        schema.need(authority is state['_authority'], 'parent capability differs')
        return state['_stop'], state['_error_owner'], state['_failure_fallback']
