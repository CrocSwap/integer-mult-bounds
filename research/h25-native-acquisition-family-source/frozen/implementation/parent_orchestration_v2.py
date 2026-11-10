"""One live two-mode source-bound parent, concrete receivers, no restored PASS.

All runtime/configuration gates intentionally remain None. The authenticated
bootstrap must bind exact independently admitted sources before importing this
module. Public APIs accept only this source's opaque owner and fixed role names;
no callback, child result, restored token or replacement schedule is accepted.
"""
import os
import sys
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import epoch_parent_v5 as epoch
import parent_completion_v1 as parent
import family_batching_v1 as families
import parent_domain_v1 as domain
import group01_evidence_v1 as evidence
import persistent_replay_v1 as replay
import policy_parent_domain_v1 as policy
import negative_parent_v2 as negative
import observation_codec_v2 as codec
import owned_root_v2 as owned
import full_caller_receiver_v2 as full
import supplemental_receivers_v2 as supplemental
import fixture_parent_v2 as fixtures
import orchestration_closure_v2 as closure
import bootstrap_bindings_v2 as bindings

CONFIGURATION = None
SOURCE_REVIEW = None
RUNTIME_CONFIGURATION = None
NATIVE_PROFILE_CONFIGURATION = None
FULL_UNION_CONFIGURATION = None
FULL_CALLER_CONFIGURATION = None
BOOTSTRAP_CONFIGURATION = None
STAGE_APPROVAL = None
COMMAND_APPROVAL = None
FUNDING = None
EXECUTION_APPROVAL = None
_ORCHESTRATORS = []
_SHARED = parent._UNKNOWN_OWNER
_TYPE, _LEN = type, len
_MKDIR, _GETPID = os.mkdir, os.getpid
MODES = ('normal', 'optimized')
NEGATIVE_GROUPS = ('02', '03', '04', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16')
CONTROL_FAMILIES = ('epoch-old7', 'epoch-v4-12', 'epoch-v5-5', 'parent-old18', 'parent-additive20',
                    'variant33', 'policy-old36', 'policy-additive20', 'policy-B01-7', 'replay32',
                    'orchestration-v2', 'elf-model50', 'elf-old33', 'elf-v3-5')
RUNTIME_MODULES = parent.REQUIRED_MODULES + ('persistent_replay_v1', 'replay_receiver_closure_v1',
 'policy_parent_domain_v1', 'policy_process_domain_v1', 'policy_receiver_closure_v1',
 'negative_parent_v2', 'negative_receiver_closure_v2', 'negative_process_domain_v2',
 'negative_observation_v2', 'typed_codec_v2', 'negative_wide_codec_v2', 'run_controls_v1', 'inert_byte_v2', 'parent_orchestration_v2', 'observation_codec_v2',
 'owned_root_v2', 'full_caller_receiver_v2', 'supplemental_receivers_v2', 'fixture_parent_v2',
 'orchestration_closure_v2', 'configured_inverse_v2', 'bootstrap_bindings_v2', 'fixture_elf_v2', 'component_control_validation_v1',
 'family_batching_v1', 'requirement_anchor_v1', 'offline_replay_v2', 'source_bindings_v3',
 'h25_original_queue_v4', 'h25_queue4_wrapper')


def _gate():
    schema.exact(CONFIGURATION, ('schedule', 'receiver_policy', 'policy_configuration_profile', 'configured_sources',
        'schedule_projection_sha256', 'family_source_manifest', 'publication_admission'))
    schema.digest(CONFIGURATION['schedule_projection_sha256'])
    schema.blob(CONFIGURATION['schedule'], schema.RECORD_BYTES)
    schema.blob(CONFIGURATION['receiver_policy'], schema.RECORD_BYTES)
    schema.blob(CONFIGURATION['configured_sources'], schema.RECORD_BYTES)
    schema.blob(CONFIGURATION['family_source_manifest'], schema.RECORD_BYTES)
    schema.blob(CONFIGURATION['publication_admission'], schema.RECORD_BYTES)
    closure._configuration_profile(CONFIGURATION['policy_configuration_profile'])
    for value, label in ((SOURCE_REVIEW, 'SOURCE_REVIEW'), (RUNTIME_CONFIGURATION, 'RUNTIME_CONFIGURATION'),
        (NATIVE_PROFILE_CONFIGURATION, 'NATIVE_PROFILE_CONFIGURATION'), (FULL_UNION_CONFIGURATION, 'FULL_UNION_CONFIGURATION'),
        (FULL_CALLER_CONFIGURATION, 'FULL_CALLER_CONFIGURATION'), (BOOTSTRAP_CONFIGURATION, 'BOOTSTRAP_CONFIGURATION'),
        (STAGE_APPROVAL, 'STAGE_APPROVAL'), (COMMAND_APPROVAL, 'COMMAND_APPROVAL'),
        (FUNDING, 'FUNDING'), (EXECUTION_APPROVAL, 'EXECUTION_APPROVAL')):
        schema.need(_TYPE(value) is tuple and _LEN(value) == 2 and _TYPE(value[0]) is str and value[0] == label,
                    'exact complete-parent gate absent')
        schema.digest(value[1])


def _state(token):
    schema.need(_TYPE(token) is object, 'exact same-process orchestration owner required')
    for known, state in _ORCHESTRATORS:
        if known is token:
            return state
    raise schema.EpochStop('unknown orchestration owner; serialized data cannot restore authority')


def _fresh(state):
    schema.need(parent._UNKNOWN_OWNER is _SHARED, 'original UNKNOWN_OWNER changed')
    domain.refresh_unknown_owner(_SHARED)
    native = state['native']
    io = native[7]
    if (io[0] or io[1] or io[2] or io[4] or io[6] or io[10] or io[11] or
            io[5] is not None or native[5][1] or io[7][4] == 1):
        _SHARED['quarantine'][0] = True
        if io[5] is not None:
            _SHARED['iterator_uncertain'][0] = True
    schema.need(state['phase'] != 'STOP' and _SHARED['primary'][0] is None and
                _SHARED['quarantine'][0] is False and _SHARED['pending'][0] is False and
                _SHARED['iterator_uncertain'][0] is False, 'common unknown ownership prohibits new work')
    schema.need(_GETPID is os.getpid and _MKDIR is os.mkdir and _GETPID() == state['pid'], 'live parent process changed')


def _guard(state):
    _fresh(state)
    _gate()
    bindings.verify_bindings(state['binding_context'])
    schema.need(families.supervisor._publication_binding() is state['publication'],
                'actual original native publication owner changed')
    schema.need(evidence.encode(CONFIGURATION) == state['configuration_raw'], 'orchestrator configuration changed')
    closure.check_receivers(state['receivers'])
    _fresh(state)
    for key in ('schedule', 'receiver_policy', 'configured_sources', 'family_source_manifest', 'publication_admission'):
        copying.verify(CONFIGURATION[key], schema.RECORD_BYTES, error_owner=state['errors'])
        _fresh(state)
    schema.need(evidence.encode(state['schedule']) == state['schedule_raw'], 'private whole schedule changed')
    replay._guard(replay._entry(state['replay']))
    _fresh(state)
    # Keep the repeated full source and complete prior-chain reads in the bill.
    for pin in state['schedule']['source_files']:
        copying.verify(pin, error_owner=state['errors'])
        _fresh(state)
    for result in state['observations']:
        copying.verify(result['wire'], codec.MAX_BYTES, error_owner=state['errors'])
        for pin in result['raw_pins']:
            copying.verify(pin, error_owner=state['errors'])
        _fresh(state)
    if state['family_sources_sealed']:
        # This check does not call the orchestration guard recursively.
        families._check_source_bindings()


def _fail(state, error):
    # No formatting or fallible helper before first delivered primary retention.
    if _SHARED['primary'][0] is None:
        _SHARED['primary'][0] = error
    _SHARED['quarantine'][0] = True
    if state is not None:
        if state['primary'][0] is None:
            state['primary'][0] = error
        state['phase'] = 'STOP'


def _read(state, pin):
    _fresh(state)
    raw = copying.read_verified_complete_v3(pin, schema.RECORD_BYTES, error_owner=state['errors'])
    _fresh(state)
    return evidence.decode(raw)


def schedule_projection_v3(plan):
    """Upstream structural action projection; no action digest/descendant pin.

    Full plan/source/Root/fixture/execution pins remain authenticated by the full
    schedule in replay and wire. They are excluded ONLY from this preimage.
    """
    return {'schema': 'h25-orchestration-acyclic-action-projection-v3',
        'order': plan['order'], 'required_control_families': plan['required_control_families'],
        'full_arm_order': plan['full_arm_order'], 'all_six_areas': plan['all_six_areas'],
        'original_requirements': plan['original_requirements'],
        'modes': {mode: {'epoch_id': plan['modes'][mode]['epoch_id'],
            'parent_plan_sha256': plan['modes'][mode]['parent_plan']['sha256'],
            'actions': [{k: a[k] for k in ('action_id', 'generation', 'source_role', 'receiver_sha256',
                'receiver_module', 'receiver_function', 'kind', 'role', 'phase', 'wire_path', 'obligations')}
                for a in plan['modes'][mode]['actions']]} for mode in MODES}}


def _validate_schedule(state):
    plan = state['schedule']
    schema.exact(plan, ('schema', 'modes', 'order', 'source_files', 'required_control_families',
        'full_arm_order', 'all_six_areas', 'original_requirements', 'measurement_protocol', 'execution_contract'))
    schema.need(plan['schema'] == 'h25-orchestration-schedule-v3' and plan['all_six_areas'] is True,
                'complete six-area schedule absent')
    schema.exact(plan['modes'], MODES)
    schema.need(plan['required_control_families'] == list(CONTROL_FAMILIES) and
                plan['original_requirements'] == ['original24', 'R01-R10', 'C01-C10-G0', 'full202', 'native24',
                'all-six-areas', 'independent-Fraction', 'all-source-current', 'ELF41-66-76'],
                'retained old/new requirement union differs')
    schema.need(plan['full_arm_order'] == ['baseline-full', 'candidate-full'],
                'only declared first pair; qualified samples require a separately admitted schedule version')
    schema.blob(plan['measurement_protocol'], schema.RECORD_BYTES)
    schema.need(plan['measurement_protocol']['sha256'] ==
                '883c4b51c2d07413bc8ed600b48780cd4617ac1dd1e09681de9c03b84332f390', 'frozen protocol differs')
    schema.blob(plan['execution_contract'], schema.RECORD_BYTES)
    schema.need(_TYPE(plan['order']) is list and 1 <= _LEN(plan['order']) <= 512, 'complete global schedule missing')
    seen, actions, modes_for_order = set(), {}, {}
    for mode in MODES:
        item = plan['modes'][mode]
        schema.exact(item, ('epoch_id', 'parent_plan', 'policy_plan', 'negative_plan', 'root_plan', 'fixture_plan',
                           'export_directory', 'actions'))
        schema.label(item['epoch_id']); schema.path(item['export_directory'])
        for key in ('parent_plan', 'policy_plan', 'negative_plan', 'root_plan', 'fixture_plan'):
            schema.blob(item[key], schema.RECORD_BYTES)
        schema.need(item['parent_plan'] == parent.CONFIGURATION['plans'][mode] and
                    item['policy_plan'] == policy.CONFIGURATION[mode] and
                    item['negative_plan'] == negative.CONFIGURATION[mode] and
                    item['root_plan'] == owned.CONFIGURATION[mode] and
                    item['fixture_plan'] == fixtures.CONFIGURATION[mode], 'actual selected dependency plan differs')
        actual_parent = _read(state, item['parent_plan'])
        parent._validate_plan(actual_parent)
        schema.need(actual_parent['epoch_id'] == item['epoch_id'] and actual_parent['mode'] == mode,
                    'actual ParentEpoch/full parent plan binding differs')
        descendants = {item[k]['path'] for k in ('policy_plan', 'negative_plan', 'root_plan', 'fixture_plan')}
        descendants.update((CONFIGURATION['schedule']['path'], replay.CONFIGURATION['plan']['path']))
        schema.need(not descendants.intersection(x['path'] for x in actual_parent['source_files']),
                    'parent source inventory contains a reciprocal descendant configuration hash')
        schema.need(_TYPE(item['actions']) is list and 1 <= _LEN(item['actions']) <= 256, 'complete mode actions absent')
        for action in item['actions']:
            schema.exact(action, ('action_id', 'generation', 'source_role', 'binding_sha256', 'receiver_sha256',
                'receiver_module', 'receiver_function', 'kind', 'role', 'phase', 'wire_path', 'obligations'))
            for key in ('action_id', 'generation', 'source_role', 'role', 'kind'):
                schema.label(action[key])
            for key in ('binding_sha256', 'receiver_sha256'):
                schema.digest(action[key])
            schema.path(action['wire_path'])
            schema.need(action['wire_path'].startswith(actual_parent['session_directory'] + '/'),
                        'captured wire outside actual owned parent session')
            schema.choice(action['phase'], ('finite', 'full'))
            key = (mode, action['action_id'])
            schema.need(key not in actions and action['generation'] not in seen, 'declared action/generation reused')
            seen.add(action['generation']); actions[key] = action
        modes_for_order[mode] = [a for a in item['actions'] if a['phase'] == 'finite']
        # Exact source-role census: extra control Roots add work, never replace originals.
        kinds = [(a['kind'], a['role']) for a in modes_for_order[mode]]
        for required in [('producer', 'group01'), ('producer', 'failure_variants'), ('exports', 'five-original'),
            ('group05', '05'), ('elf-gap', 'elf41'), ('history-fixtures', 'history_fixtures_v1'),
            ('fixture-exports', 'nine-fixtures'), ('soname', '09-soname'), ('epoch-close', 'all13'),
            ('finite-complete', mode)] + [('policy', r) for r in policy.ROLES] + [('negative', g) for g in NEGATIVE_GROUPS]:
            schema.need(kinds.count(required) == 1, 'complete exact required action omitted/repeated')
        for family in CONTROL_FAMILIES:
            schema.need(kinds.count(('component-controls', family)) >= 1,
                        'required component family has no declared actual unit Roots')
        schema.need(any(kind == 'component-envelope' for kind, role in kinds),
                    'actual complete-family envelope schedule absent')
    order = []
    for pair in plan['order']:
        schema.need(_TYPE(pair) is list and _LEN(pair) == 2 and all(_TYPE(x) is str for x in pair), 'schedule key shape')
        key = tuple(pair)
        schema.need(key in actions and key not in order, 'global action absent/repeated')
        order.append(key)
    schema.need(set(order) == set(actions), 'global whole schedule has an omitted tail')
    normal_end = next(i for i, k in enumerate(order) if actions[k]['kind'] == 'finite-complete' and k[0] == 'normal')
    optimized_end = next(i for i, k in enumerate(order) if actions[k]['kind'] == 'finite-complete' and k[0] == 'optimized')
    schema.need(normal_end < optimized_end and all(k[0] == 'normal' and actions[k]['phase'] == 'finite' for k in order[:normal_end + 1]) and
                all(k[0] == 'optimized' and actions[k]['phase'] == 'finite' for k in order[normal_end + 1:optimized_end + 1]) and
                [actions[k]['role'] for k in order[optimized_end + 1:]] == plan['full_arm_order'] and
                all(actions[k]['phase'] == 'full' and k[0] == 'normal' for k in order[optimized_end + 1:]),
                'both complete finite modes must precede either assertions-on full arm')
    reservation = replay._entry(state['replay'])['plan']
    schema.need(reservation['full_schedule_sha256'] == CONFIGURATION['schedule']['sha256'], 'replay full schedule binding differs')
    for mode in MODES:
        reserved = reservation[mode]; selected = plan['modes'][mode]
        schema.need(reserved['epoch_id'] == selected['epoch_id'] and
                    reserved['parent_plan_sha256'] == selected['parent_plan']['sha256'] and
                    reserved['actions'] == [{k: a[k] for k in ('action_id', 'generation', 'source_role', 'binding_sha256')}
                        for a in selected['actions']], 'real caller replay identity/action binding differs')
    projection_sha256 = schema.sha(evidence.encode(schedule_projection_v3(plan)))
    schema.need(projection_sha256 == CONFIGURATION['schedule_projection_sha256'],
                'externally authenticated acyclic schedule projection differs')
    state['schedule_projection_sha256'] = projection_sha256
    state['actions'], state['order'] = actions, order


def make_orchestrator(original_receivers, binding_context):
    state = None
    try:
        bindings.verify_bindings(binding_context)
        _gate()
        schema.need(not _ORCHESTRATORS and _SHARED['primary'][0] is None and _SHARED['quarantine'][0] is False,
                    'one live complete attempt; no reconstruction or new IDs after failure')
        errors = schema.make_error_owner()
        state = {'pid': _GETPID(), 'phase': 'CONSTRUCTING', 'errors': errors, 'native': schema.owner_state(errors),
            'configuration_raw': evidence.encode(CONFIGURATION), 'binding_context': binding_context, 'receivers': None, 'modules': original_receivers,
            'replay': None, 'schedule': None, 'schedule_raw': None, 'actions': {}, 'order': [], 'next': 0,
            'mode_states': {}, 'observations': [], 'native_actuals': [], 'pending': [None], 'primary': [None],
            'normal_authority': None, 'optimized_consumed': False, 'finite_complete': {}, 'full_results': [],
            'family_sources_sealed': False, 'publication': None, 'owner': None}
        token = object(); _ORCHESTRATORS.append((token, state))
        state['owner'] = token
        _fresh(state)
        source_policy = _read(state, CONFIGURATION['receiver_policy'])
        schema.exact(original_receivers, RUNTIME_MODULES); schema.exact(source_policy, RUNTIME_MODULES)
        schema.need(original_receivers['parent_orchestration_v2'] is sys.modules[__name__] and
                    original_receivers['parent_completion_v1'] is parent and
                    original_receivers['persistent_replay_v1'] is replay and
                    original_receivers['epoch_parent_v5'] is epoch and
                    original_receivers['family_batching_v1'] is families and
                    original_receivers['requirement_anchor_v1'] is families.anchor and
                    original_receivers['offline_replay_v2'] is families.offline and
                    original_receivers['source_bindings_v3'] is families.bindings and
                    original_receivers['h25_original_queue_v4'] is families.original_queue and
                    original_receivers['h25_queue4_wrapper'] is families.queue_wrapper,
                    'actual original and family module identity differs')
        schema.need(original_receivers['h25_parent_supervisor'] is families.supervisor,
                    'family supervisor is not the original source-bound native owner')
        admission = _read(state, CONFIGURATION['publication_admission'])
        schema.need(admission['source_sha256'] == source_policy['h25_parent_supervisor']['sha256'] and
            admission['source_review_sha256'] == families.SOURCE_REVIEW[1] and
            admission['command_approval_sha256'] == COMMAND_APPROVAL[1] and
            admission['funding_sha256'] == FUNDING[1] == families.FUNDING[1],
            'original publication source, command or same-operation funding differs')
        # Actual one-shot native initialization precedes every receiver capture.
        families.supervisor.prepare_atomic_publication(families.original_queue.ROOT, admission)
        state['publication'] = families.supervisor._publication_binding()
        state['receivers'] = closure.bind_receivers(original_receivers, source_policy, errors,
                                                  CONFIGURATION['policy_configuration_profile'],
                                                  _read(state, CONFIGURATION['configured_sources']))
        state['schedule'] = _read(state, CONFIGURATION['schedule'])
        state['schedule_raw'] = evidence.encode(state['schedule'])
        # C06: both epochs/every declared generation durably reserved before ANY epoch constructor.
        replay_modules = {name: original_receivers[name] for name in replay._REQUIRED}
        state['replay'] = replay.reserve_batch(replay_modules)
        _validate_schedule(state)
        state['phase'] = 'RESERVED'
        _guard(state)
        return token
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error)
        raise


def _begin(state, mode):
    _guard(state)
    schema.need(mode not in state['mode_states'], 'actual epoch already constructed')
    selected = state['schedule']['modes'][mode]
    actual_plan = _read(state, selected['parent_plan'])
    # Original ParentEpoch requires a new owned export directory; creation is paid.
    authority = object()
    slot = {'authority': authority, 'epoch': None, 'parent': None, 'policy': None, 'negative': None,
            'roots': None, 'fixtures': None, 'accepted': [], 'exports': None, 'epoch_close': None,
            'family_owner': None, 'family_union_pin': None}
    state['mode_states'][mode] = slot
    _MKDIR(selected['export_directory'], 0o700)
    slot['epoch'] = epoch.ParentEpoch(authority, selected['epoch_id'], mode, selected['export_directory'],
        [actual_plan['producers'][r]['epoch_plan'] for r in schema.PRODUCERS])
    _fresh(state)
    slot['parent'] = parent.make_parent(slot['epoch'], authority,
        {name: state['modules'][name] for name in parent.REQUIRED_MODULES})
    slot['policy'] = policy.make_policy_parent(slot['parent'],
        {name: state['modules'][name] for name in policy.REQUIRED_POLICY_MODULES})
    slot['roots'] = owned.make_root_parent(slot['parent'])
    slot['fixtures'] = fixtures.make_fixture_parent(slot['parent'])
    state['phase'] = mode
    _guard(state)
    if not state['family_sources_sealed']:
        schema.need(mode == 'normal', 'family source admission must precede the first mode')
        families.seal_source_bindings(slot['parent'], state['owner'], CONFIGURATION['family_source_manifest'])
        state['family_sources_sealed'] = True
    slot['family_owner'] = families.make_family_owner(slot['parent'], state['replay'], state['owner'])
    _guard(state)


def begin_normal(owner):
    state = _state(owner)
    try:
        schema.need(state['phase'] == 'RESERVED' and state['next'] == 0, 'normal already consumed')
        _begin(state, 'normal')
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def begin_optimized(owner):
    state = _state(owner)
    try:
        _guard(state)
        schema.need(state['phase'] == 'NORMAL_COMPLETE' and _TYPE(state['normal_authority']) is object and
                    'normal' in state['finite_complete'] and not state['optimized_consumed'],
                    'actual complete normal finite receiver PASS required')
        _refresh_mode(state, 'normal')
        state['optimized_consumed'] = True
        # Consume live authority BEFORE constructor; it is never serialized/restored.
        state['normal_authority'] = None
        _begin(state, 'optimized')
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def _next(state, kind, role):
    _guard(state)
    schema.need(state['next'] < len(state['order']), 'fixed schedule exhausted')
    key = state['order'][state['next']]
    mode, unused = key
    action = state['actions'][key]
    schema.need(action['kind'] == kind and action['role'] == role and action['source_role'] == role and mode in state['mode_states'],
                'fixed whole schedule order differs')
    if action['phase'] == 'finite':
        schema.need(state['phase'] == mode, 'finite mode authority differs')
    else:
        schema.need(set(state['finite_complete']) == set(MODES) and state['phase'] == 'BOTH_FINITE_COMPLETE',
                    'both actual complete finite unions required before full arm')
    return mode, action, state['mode_states'][mode]


def _burn(state, mode, action, actual_binding, module_name, function_name):
    schema.need(action['receiver_module'] == module_name and action['receiver_function'] == function_name,
                'source-fixed receiver role differs')
    captured = closure.receiver(state['receivers'], module_name, function_name)
    schema.need(captured is getattr(state['modules'][module_name], function_name), 'actual receiver function identity differs')
    receiver_pin = next(row[3] for row in closure._packet(state['receivers'])[1] if row[0] == module_name)
    schema.need(receiver_pin['sha256'] == action['receiver_sha256'], 'actual receiver source image differs')
    # Binds complete actual source/config/argv/profile row, not just digest syntax.
    binding = {'mode': mode, 'epoch_id': state['schedule']['modes'][mode]['epoch_id'],
        'parent_plan_sha256': state['schedule']['modes'][mode]['parent_plan']['sha256'],
        'source_role': action['source_role'], 'action_id': action['action_id'], 'generation': action['generation'],
        'receiver_module': module_name, 'receiver_function': function_name, 'receiver_sha256': receiver_pin['sha256'],
        'actual': actual_binding}
    schema.need(schema.sha(evidence.encode(binding)) == action['binding_sha256'], 'complete actual action binding differs')
    replay.burn_action(state['replay'], mode, action['action_id'])
    _fresh(state)
    return binding


def _capture(state, mode, action, observation, raw_pins):
    # Retain exact original tuple/bytes identities before any codec or comparisons.
    state['pending'][0] = observation
    state['native_actuals'].append(observation)
    schema.need(_TYPE(raw_pins) is tuple, 'source-returned exact raw pin tuple required')
    for pin in raw_pins:
        copying.verify(pin, error_owner=state['errors'])
    binding = {k: action[k] for k in ('action_id', 'generation', 'source_role', 'binding_sha256', 'receiver_sha256')}
    binding.update(mode=mode, epoch_id=state['schedule']['modes'][mode]['epoch_id'],
        full_schedule_sha256=CONFIGURATION['schedule']['sha256'],
        parent_plan_sha256=state['schedule']['modes'][mode]['parent_plan']['sha256'])
    raw = codec.encode_observation(observation, binding)
    _fresh(state)
    pin = copying.write_observation_once_v3(action['wire_path'], raw, error_owner=state['errors'])
    _fresh(state)
    schema.need(copying.read_verified_complete_v3(pin, codec.MAX_BYTES, error_owner=state['errors']) == raw, 'wire readback differs')
    replay.record_captured_return(state['replay'], mode, action['action_id'], pin)
    state['observations'].append({'action': action, 'mode': mode, 'native': observation, 'wire': pin, 'raw_pins': raw_pins})
    state['mode_states'][mode]['accepted'].append((action['kind'], action['role']))
    state['pending'][0] = None
    state['next'] += 1
    _guard(state)
    # Persisted records report observations only; no live phase token escapes.
    return schema.plain_copy(pin)


def run_policy_role(owner, role):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'policy', role)
        policy_state = policy._owner(slots['policy'])
        row = policy_state['plan']['roles'][role]
        schema.need(row['generation'] == action['generation'], 'actual policy generation differs')
        _burn(state, mode, action, {'policy_plan': policy_state['plan_pin'], 'role': role, 'row': row},
              'policy_parent_domain_v1', 'take_policy_observation')
        joined = policy.run_policy(slots['policy'], role)
        actual = policy.take_policy_observation(slots['policy'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_producer_role(owner, role):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'producer', role)
        row = parent._state(slots['parent'])['plan']['producers'][role]
        schema.need(row['epoch_plan']['generation'] == action['generation'], 'actual original producer generation differs')
        _burn(state, mode, action, row, 'parent_completion_v1', 'accept_producer')
        joined = parent.run_producer(slots['parent'], role)
        actual = parent.accept_producer(slots['parent'], joined)
        pins = tuple(actual[k] for k in ('terminal', 'raw_result', 'raw_groups', 'final_source_custody', 'parent_observation'))
        return _capture(state, mode, action, actual, pins)
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def commit_original_exports(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'exports', 'five-original')
        _burn(state, mode, action, {'parent_plan': state['schedule']['modes'][mode]['parent_plan'],
            'export_directory': state['schedule']['modes'][mode]['export_directory']}, 'parent_completion_v1', 'commit_exports')
        actual = parent.commit_exports(slots['parent'])
        slots['exports'] = actual
        # The original negative owner requires already committed exports.
        slots['negative'] = negative.make_negative_parent(slots['parent'],
            {name: state['modules'][name] for name in negative.REQUIRED_MODULES})
        negative.register_fixture_claims(slots['negative'], slots['fixtures'])
        return _capture(state, mode, action, {'original_manifest': actual}, (actual,))
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_negative_group(owner, group):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'negative', group)
        actual_row = negative.planned_action(slots['negative'], group)
        schema.need(actual_row['generation'] == action['generation'], 'actual negative generation differs')
        _burn(state, mode, action, {'negative_plan': state['schedule']['modes'][mode]['negative_plan'], 'group': group, 'row': actual_row},
              'negative_parent_v2', 'take_negative_observation')
        joined = negative.run_negative(slots['negative'], group)
        actual = negative.take_negative_observation(slots['negative'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_group05(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'group05', '05')
        actual_row = negative.planned_action(slots['negative'], '05')
        schema.need(actual_row['generation'] == action['generation'], 'actual Group05 generation differs')
        _burn(state, mode, action, {'negative_plan': state['schedule']['modes'][mode]['negative_plan'], 'group': '05', 'row': actual_row},
              'negative_parent_v2', 'take_group05_observation')
        joined = negative.run_group05(slots['negative'])
        actual = negative.take_group05_observation(slots['negative'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_soname(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'soname', '09-soname')
        actual_row = negative.planned_action(slots['negative'], '09-soname')
        schema.need(actual_row['generation'] == action['generation'], 'actual SONAME generation differs')
        _burn(state, mode, action, {'negative_plan': state['schedule']['modes'][mode]['negative_plan'], 'row': actual_row,
            'fixture_plan': state['schedule']['modes'][mode]['fixture_plan'], 'subcase': '09-soname'},
              'negative_parent_v2', 'take_soname_observation')
        joined = negative.run_soname(slots['negative'])
        actual = negative.take_soname_observation(slots['negative'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def _root_row(slots, action):
    root = owned._state(slots['roots'])
    row = root['plan']['actions'][root['next']]
    schema.need(row['action_id'] == action['action_id'] and row['generation'] == action['generation'] and
                row['source_role'] == action['source_role'] and row['binding_sha256'] == action['binding_sha256'],
                'actual fixed Root action binding differs')
    # Root action row excludes its own binding digest in hashed projection.
    return {k: v for k, v in row.items() if k != 'binding_sha256'}


def run_history_fixture_producer(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'history-fixtures', 'history_fixtures_v1')
        row = _root_row(slots, action)
        selected_driver = fixtures.bind_producer_driver(slots['fixtures'], slots['roots'], action['action_id'])
        schema.need(selected_driver == {k: row['driver_' + k] for k in ('path', 'sha256')},
                    'fixed action fixture driver projection differs')
        _burn(state, mode, action, row, 'fixture_parent_v2', 'take_fixture_observation')
        joined = owned.run_owned_root(slots['roots'], action['action_id'])
        actual = fixtures.take_fixture_observation(slots['fixtures'], slots['roots'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def commit_fixture_exports(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'fixture-exports', 'nine-fixtures')
        _burn(state, mode, action, {'fixture_plan': state['schedule']['modes'][mode]['fixture_plan']},
              'fixture_parent_v2', 'commit_fixture_exports')
        actual = fixtures.commit_fixture_exports(slots['fixtures'])
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_elf_gap(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'elf-gap', 'elf41')
        row = _root_row(slots, action)
        _burn(state, mode, action, row, 'supplemental_receivers_v2', 'take_elf_gap_observation')
        joined = owned.run_owned_root(slots['roots'], action['action_id'])
        actual = supplemental.take_elf_gap_observation(slots['roots'], joined)
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_component_controls(owner, family):
    state = _state(owner)
    try:
        schema.choice(family, CONTROL_FAMILIES)
        mode, action, slots = _next(state, 'component-controls', family)
        row = _root_row(slots, action)
        _burn(state, mode, action, row, 'supplemental_receivers_v2', 'take_component_control_observation')
        joined = owned.run_owned_root(slots['roots'], action['action_id'])
        actual = supplemental.take_component_control_observation(slots['roots'], joined)
        schema.need(actual['family'] == family and actual['family_completion'] is False and
                    actual['complete_finite_union'] is False, 'actual implemented unit scope differs')
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def run_component_envelope(owner):
    """Reached scheduling edge for the actual source-owned family receiver.

    The family receiver burns its actual replay action before its first child.
    The enclosing caller captures that exact return once, without a second burn.
    """
    state = _state(owner)
    try:
        _guard(state)
        schema.need(state['next'] < len(state['order']), 'complete envelope schedule exhausted')
        action = state['actions'][state['order'][state['next']]]
        mode, action, slots = _next(state, 'component-envelope', action['role'])
        schema.need(slots['family_owner'] is not None and slots['family_union_pin'] is None,
                    'same-mode family owner absent or already consumed')
        actual = families.run_next_envelope(slots['family_owner'])
        schema.need(actual['envelope_id'] == action['action_id'] and
            actual['family_completion'] is False and actual['complete_finite_union'] is False and
            actual['runtime_authority'] is False, 'family envelope scope or actual action differs')
        return _capture(state, mode, action, actual, actual['raw_pins'])
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error)
        raise


def close_original_epoch(owner):
    state = _state(owner)
    try:
        mode, action, slots = _next(state, 'epoch-close', 'all13')
        _burn(state, mode, action, {'epoch_id': state['schedule']['modes'][mode]['epoch_id'],
            'parent_plan': state['schedule']['modes'][mode]['parent_plan']}, 'epoch_parent_v5', 'ParentEpoch')
        actual = epoch.ParentEpoch.close(slots['epoch'], slots['authority'])
        slots['epoch_close'] = actual
        return _capture(state, mode, action, actual, ())
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def _refresh_mode(state, mode):
    slots = state['mode_states'][mode]
    original = parent._state(slots['parent'])
    parent._guard(original)
    schema.need(original['phase'] == 'EXPORTED' and all(r['phase'] == 'ACCEPTED' for r in original['runs'].values()),
                'actual original producer receiver PASS absent')
    for run in original['runs'].values():
        schema.need(domain.terminal_facts(run['domain']) == run['terminal'] and
                    parent._snapshot_sources(original['plan'], original['errors']) == run['source_before'],
                    'actual original full producer output/source/terminal freshness differs')
    policy._guard(policy._owner(slots['policy']))
    schema.need(policy._owner(slots['policy'])['phase'] == 'COMPLETE', 'all three genuine policy observations absent')
    negative.verify_all_terminal(slots['negative'])
    fixtures.verify_all_claims(slots['fixtures'])
    schema.need(slots['epoch_close'] is not None, 'original epoch claims accounting absent')
    # Unit observations remain partial. Complete family authority is an actual
    # separately consumed live token from the reached same-operation owner.
    for observed in state['observations']:
        if observed['mode'] == mode and observed['action']['kind'] == 'component-controls':
            schema.need(observed['native'].get('family_completion') is False and
                        observed['native'].get('complete_finite_union') is False,
                        'partial unit scope has been incorrectly promoted')
    schema.need(slots['family_union_pin'] is not None and
        families.verify_consumed_union(slots['family_owner'], slots['parent'], state['owner'],
            state['replay'], mode) is slots['family_union_pin'],
        'complete current same-mode family authority absent')
    for observed in state['observations']:
        if observed['mode'] == mode:
            copying.verify(observed['wire'], codec.MAX_BYTES, error_owner=state['errors'])
            for pin in observed['raw_pins']:
                copying.verify(pin, error_owner=state['errors'])
    _guard(state)


def finish_finite_mode(owner):
    state = _state(owner)
    try:
        mode = state['phase']
        schema.choice(mode, MODES)
        mode, action, slots = _next(state, 'finite-complete', mode)
        required = [(a['kind'], a['role']) for a in state['schedule']['modes'][mode]['actions']
                    if a['phase'] == 'finite' and a['kind'] != 'finite-complete']
        schema.need(slots['accepted'] == required and mode not in state['finite_complete'],
                    'complete actual finite action inventory missing, reordered or repeated')
        schema.need(slots['family_union_pin'] is None, 'complete family union consumer replay')
        slots['family_union_pin'] = families.complete_for_parent(slots['family_owner'], slots['parent'],
            owner, state['replay'], mode)
        _refresh_mode(state, mode)
        _burn(state, mode, action, {'schedule_projection_sha256': state['schedule_projection_sha256'],
            'complete_actual_actions': [list(x) for x in required]}, 'parent_orchestration_v2', 'finish_finite_mode')
        actual = {'schema': 'h25-complete-finite-parent-observation-v2', 'mode': mode,
            'epoch_id': state['schedule']['modes'][mode]['epoch_id'], 'actions': [list(x) for x in required],
            'whole_required_union': state['schedule']['original_requirements'],
            'full_schedule_sha256': CONFIGURATION['schedule']['sha256'],
            'schedule_projection_sha256': state['schedule_projection_sha256'],
            'control_families': list(CONTROL_FAMILIES), 'epoch_close': slots['epoch_close'],
            'component_family_union': slots['family_union_pin'],
            'raw_pins': tuple(x['wire'] for x in state['observations'] if x['mode'] == mode),
            'saved_PASS': False, 'restorable': False, 'full_science_complete': False}
        result = _capture(state, mode, action, actual, actual['raw_pins'])
        state['finite_complete'][mode] = result
        if mode == 'normal':
            # Mint only AFTER source-bound receivers, full inventory, final custody,
            # terminal cleanup, durable raw write/readback and replay record.
            state['normal_authority'] = object()
            state['phase'] = 'NORMAL_COMPLETE'
        else:
            state['phase'] = 'BOTH_FINITE_COMPLETE'
        return result
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def _dispatch_finite_action(owner):
    """Fixed concrete dispatch; no callback or returned child flag selects code."""
    state = _state(owner)
    _guard(state)
    schema.need(state['next'] < len(state['order']), 'finite schedule exhausted')
    mode, unused = state['order'][state['next']]
    action = state['actions'][state['order'][state['next']]]
    schema.need(action['phase'] == 'finite' and state['phase'] == mode,
                'finite dispatch cannot enter the later comparison graph')
    kind, role = action['kind'], action['role']
    if kind == 'policy':
        return run_policy_role(owner, role)
    if kind == 'producer':
        return run_producer_role(owner, role)
    if kind == 'exports':
        return commit_original_exports(owner)
    if kind == 'negative':
        return run_negative_group(owner, role)
    if kind == 'group05':
        return run_group05(owner)
    if kind == 'soname':
        return run_soname(owner)
    if kind == 'history-fixtures':
        return run_history_fixture_producer(owner)
    if kind == 'fixture-exports':
        return commit_fixture_exports(owner)
    if kind == 'elf-gap':
        return run_elf_gap(owner)
    if kind == 'component-controls':
        return run_component_controls(owner, role)
    if kind == 'component-envelope':
        return run_component_envelope(owner)
    if kind == 'epoch-close':
        return close_original_epoch(owner)
    if kind == 'finite-complete':
        return finish_finite_mode(owner)
    raise schema.EpochStop('unimplemented finite schedule action')


def run_complete_finite_union(original_receivers, binding_context):
    """Actual original-parent entry for the two-mode finite source route.

    The existing authenticated bootstrap supplies the genuine module objects
    and sealed context. No gate, grant, scenario or financial input is minted.
    The original enclosing whole-operation meter continues to own all costs,
    including constructor, reread, failure, teardown and final-tail work.
    This returns its live owner only after both complete modes. It does not run
    either later full scientific arm or claim original successful CLOSE.
    """
    owner = make_orchestrator(original_receivers, binding_context)
    state = _state(owner)
    try:
        begin_normal(owner)
        while state['phase'] == 'normal':
            _dispatch_finite_action(owner)
        schema.need(state['phase'] == 'NORMAL_COMPLETE', 'normal finite transition incomplete')
        begin_optimized(owner)
        while state['phase'] == 'optimized':
            _dispatch_finite_action(owner)
        schema.need(state['phase'] == 'BOTH_FINITE_COMPLETE' and
            set(state['finite_complete']) == set(MODES), 'both genuine finite unions incomplete')
        return owner
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error)
        raise


def run_full_arm(owner, arm):
    state = _state(owner)
    try:
        schema.choice(arm, ('baseline-full', 'candidate-full'))
        mode, action, slots = _next(state, 'full', arm)
        for finite_mode in MODES:
            _refresh_mode(state, finite_mode)
        row = _root_row(slots, action)
        _burn(state, mode, action, row, 'full_caller_receiver_v2', 'take_full_observation')
        joined = owned.run_owned_root(slots['roots'], action['action_id'])
        actual = full.take_full_observation(slots['roots'], joined)
        result = _capture(state, mode, action, actual, actual['raw_pins'])
        state['full_results'].append(result)
        return result
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def seal_completed_audit(owner):
    state = _state(owner)
    try:
        _guard(state)
        schema.need(state['next'] == len(state['order']) and len(state['full_results']) == 2 and
                    set(state['finite_complete']) == set(MODES), 'entire fixed whole schedule incomplete')
        for mode in MODES:
            _refresh_mode(state, mode)
        head = replay.seal_audit(state['replay'])
        state['phase'] = 'SEALED'
        # Aggregate source results still do not confer measured gain or fresh-run permission.
        return {'schema': 'h25-complete-parent-audit-v2', 'head': head, 'saved_PASS': False,
            'resume_allowed': False, 'measured_gain': False, 'further_execution_authorized': False}
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        _fail(state, error); raise


def stop_evidence(owner):
    state = _state(owner)
    return state['primary'], state['errors'], state['pending'], tuple(state['native_actuals'])
