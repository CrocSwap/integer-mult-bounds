"""Unconfigured SOURCE ONLY: durable burns, never runtime-result authority.

The fixed full parent must authenticate this module before import and own every
actual receiver call. This component does not launch work, claim PASS, restore
ParentEpoch/ParentCompletion capabilities, or authorize the optimized mode.
An externally admitted persistent directory, no deletion/rollback, original
runtime/filesystem semantics and exclusive trusted writer remain premises.
"""
import os
import stat
import sys
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import epoch_parent_v5 as epoch
import parent_completion_v1 as parent
import parent_domain_v1 as domain
import replay_receiver_closure_v1 as closure
import configured_inverse_v2 as configured

CONFIGURATION = None
SOURCE_REVIEW = None
RUNTIME_CONFIGURATION = None
PERSISTENCE_CONFIGURATION = None
FULL_ORCHESTRATOR_CONFIGURATION = None
NATIVE_PROFILE_CONFIGURATION = None
SOURCE_CLOSURE_CONFIGURATION = None
STAGE_APPROVAL = None
COMMAND_APPROVAL = None
FUNDING = None
EXECUTION_APPROVAL = None

# A separate source-owned registry does not consume either original closure
# registration or alter the original epoch's 21-key private state.
_BATCHES = []
_SHARED = parent._UNKNOWN_OWNER
_STAT, _GETPID = os.stat, os.getpid
_TYPE, _LEN = type, len
_REQUIRED = parent.REQUIRED_MODULES + ('persistent_replay_v1', 'replay_receiver_closure_v1', 'configured_inverse_v2')
MODES = ('normal', 'optimized')
MAX_ACTIONS_PER_MODE = 256
MAX_CHAIN_RECORDS = 4096
PREDECESSOR_FIXED_SOURCE_PINS = {
    'epoch_schema_v5': 'b89a789654be87bde40a47300f4d9702dce2b90e6ab3be9a2025f6d8041b3e9a',
    'epoch_copy_v5': '4f459d0336d59975df787c24373e18dad4044c3a24137392e890115f811b3211',
    'epoch_parent_v5': '058059912144863a4b2bfe4fc9ffc5233b4ab20ee5a7355bde66f4d3f6f28712',
    'parent_completion_v1': 'd4ee1b7ce4a42b73261984ffb1b9ceb5bb0165223e04a253588f83b99f6981a5',
    'parent_domain_v1': '9205e14d6661fb5df0597f0ad7b2206006f2d31f01f784805f64c13875663282',
    'parent_closure_v1': '2d831cff8bd444de2d6941645d571e07618ede404a1f45692b557f61494b334a',
}
# Exact independently reviewed V3 successor templates, retained in V4.
FIXED_SOURCE_TEMPLATE_VERSION = 'h25-replay-current-template-map-v4'
FIXED_SOURCE_PINS = {'epoch_schema_v5': 'b89a789654be87bde40a47300f4d9702dce2b90e6ab3be9a2025f6d8041b3e9a', 'epoch_copy_v5': 'b8303732ede41dd48aa767f2c40cbbff249f34e2621f532b5484d38a218a0f69', 'epoch_parent_v5': '058059912144863a4b2bfe4fc9ffc5233b4ab20ee5a7355bde66f4d3f6f28712', 'parent_completion_v1': '97f71e3cae08852808a80fa29818304cbc80c6bfa2c32d60e6d1fbd281062f75', 'parent_domain_v1': '9205e14d6661fb5df0597f0ad7b2206006f2d31f01f784805f64c13875663282', 'parent_closure_v1': '95cc1b7e05ff247fb8146ec64a74656da7893458a187ef832f33c4e736c28a2d'}

def _verify_source_template_v4(name, source_pin, record, raw):
    schema.text(name, 128)
    schema.blob(source_pin)
    schema.exact(record, ('module', 'template_sha256', 'configured_sha256', 'assignments'))
    schema.text(record['module'], 128)
    schema.digest(record['template_sha256']); schema.digest(record['configured_sha256'])
    schema.need(record['module'] == name and record['configured_sha256'] == source_pin['sha256'],
                'independently configured receiver source differs')
    if name in FIXED_SOURCE_PINS:
        schema.need(record['template_sha256'] == FIXED_SOURCE_PINS[name],
                    'reviewed current template inverse target differs')
    # Strict configured bytes plus complete literal-None inverse remains intact.
    return configured.verify_configured_source(raw, record)



def _gate():
    schema.exact(CONFIGURATION, ('registry_directory', 'registry_identity', 'registry_anchor',
        'batch_id', 'plan', 'receiver_policy', 'source_inventory', 'configured_sources', 'configuration_sha256'))
    schema.path(CONFIGURATION['registry_directory'])
    schema.exact(CONFIGURATION['registry_identity'], ('device', 'inode', 'mode', 'uid', 'gid'))
    for key, value in CONFIGURATION['registry_identity'].items():
        schema.integer(value, 0, (1 << 127) - 1)
    identity = CONFIGURATION['registry_identity']
    schema.need(identity['inode'] > 0 and stat.S_ISDIR(identity['mode']) and
                stat.S_IMODE(identity['mode']) == 0o700, 'fixed durable registry directory identity differs')
    for key in ('registry_anchor', 'plan', 'receiver_policy', 'source_inventory', 'configured_sources'):
        schema.blob(CONFIGURATION[key], schema.RECORD_BYTES)
    schema.need(CONFIGURATION['registry_anchor']['path'] ==
                CONFIGURATION['registry_directory'] + '/REGISTRY-ANCHOR.json',
                'registry anchor cannot be relocated by a session or mode')
    schema.digest(CONFIGURATION['batch_id'])
    schema.digest(CONFIGURATION['configuration_sha256'])
    # Digest excludes its own field; this is a binding, not an admission claim.
    body = {key: value for key, value in CONFIGURATION.items() if key != 'configuration_sha256'}
    schema.need(schema.sha(schema.canonical(body)) == CONFIGURATION['configuration_sha256'],
                'replay configuration contents differ')
    for value, label in ((SOURCE_REVIEW, 'SOURCE_REVIEW'),
        (RUNTIME_CONFIGURATION, 'RUNTIME_CONFIGURATION'),
        (PERSISTENCE_CONFIGURATION, 'PERSISTENCE_CONFIGURATION'),
        (FULL_ORCHESTRATOR_CONFIGURATION, 'FULL_ORCHESTRATOR_CONFIGURATION'),
        (NATIVE_PROFILE_CONFIGURATION, 'NATIVE_PROFILE_CONFIGURATION'),
        (SOURCE_CLOSURE_CONFIGURATION, 'SOURCE_CLOSURE_CONFIGURATION'),
        (STAGE_APPROVAL, 'STAGE_APPROVAL'), (COMMAND_APPROVAL, 'COMMAND_APPROVAL'),
        (FUNDING, 'FUNDING'), (EXECUTION_APPROVAL, 'EXECUTION_APPROVAL')):
        schema.need(_TYPE(value) is tuple and _LEN(value) == 2 and _TYPE(value[0]) is str and
                    value[0] == label, 'exact replay external gate absent')
        schema.digest(value[1])


def _fresh(state):
    # No I/O, callbacks or projections before the common owner's refusal.
    schema.need(parent._UNKNOWN_OWNER is _SHARED, 'original shared owner changed')
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
                _SHARED['iterator_uncertain'][0] is False,
                'unknown ownership prohibits new replay I/O and original parent work')
    schema.need(_STAT is os.stat and _GETPID is os.getpid and _GETPID() == state['pid'],
                'replay primitive or same-process owner differs')


def _read(state, pin):
    _fresh(state)
    raw = copying.read_verified_complete_v3(pin, schema.RECORD_BYTES, error_owner=state['errors'])
    _fresh(state)
    return raw


def _write(state, path, raw):
    _fresh(state)
    # Existing V5 owns every descriptor and known-close attempt; an O_EXCL
    # collision is a permanent burn/STOP, never a probe followed by retry.
    pin = copying.write_once(path, raw, error_owner=state['errors'])
    _fresh(state)
    # An explicit second exact readback follows V5 file+directory fsync and its
    # first full identity/hash readback. This is paid, not cached evidence.
    schema.need(_read(state, pin) == raw, 'durable event exact byte readback differs')
    return pin


def _directory(state):
    _fresh(state)
    info = _STAT(state['configuration']['registry_directory'], dir_fd=None, follow_symlinks=False)
    actual = {'device': info.st_dev, 'inode': info.st_ino, 'mode': info.st_mode,
              'uid': info.st_uid, 'gid': info.st_gid}
    schema.need(actual == state['configuration']['registry_identity'], 'durable registry replaced')
    # The original fixed anchor is never generated from observations or reset.
    _read(state, state['configuration']['registry_anchor'])


def _guard(state):
    _fresh(state)
    _gate()
    schema.need(schema.canonical(CONFIGURATION) == state['configuration_raw'], 'replay configuration changed')
    _fresh(state)
    closure.check_receivers(state['receivers'])
    _fresh(state)
    _directory(state)
    for key in ('plan', 'receiver_policy', 'source_inventory', 'configured_sources'):
        _read(state, state['configuration'][key])
    # All independently expected source/header/compiler/link/profile inputs
    # are re-read. Finite bounds reject an oversized inventory; they never
    # permit an omitted tail or move source costs outside the parent bill.
    for pin in state['source_inventory']:
        _fresh(state)
        copying.verify(pin, error_owner=state['errors'])
        _fresh(state)
    # Re-read every existing record before extending the chain. The quadratic
    # I/O is deliberately explicit; no speedup or free custody cache is claimed.
    for pin in state['records']:
        _read(state, pin)
    _directory(state)


def _entry(token):
    schema.need(_TYPE(token) is object, 'exact process-local replay owner required')
    for known, state in _BATCHES:
        if token is known:
            return state
    raise schema.EpochStop('unknown replay owner; serialized identity is not a capability')


def _plan(raw, configuration):
    plan = schema.decode(raw)
    schema.exact(plan, ('schema', 'batch_id', 'full_schedule_sha256', 'normal', 'optimized'))
    schema.need(plan['schema'] == 'h25-persistent-reservation-plan-v1' and
                plan['batch_id'] == configuration['batch_id'], 'replay plan binding differs')
    schema.digest(plan['full_schedule_sha256'])
    epochs, generations, keys = set(), set(), set()
    for mode in MODES:
        row = plan[mode]
        schema.exact(row, ('epoch_id', 'parent_plan_sha256', 'actions'))
        schema.label(row['epoch_id'])
        schema.digest(row['parent_plan_sha256'])
        schema.need(row['epoch_id'] not in epochs, 'cross-mode epoch reuse')
        epochs.add(row['epoch_id'])
        schema.need(_TYPE(row['actions']) is list and 1 <= _LEN(row['actions']) <= MAX_ACTIONS_PER_MODE,
                    'complete explicit action plan absent or oversized')
        for action in row['actions']:
            schema.exact(action, ('action_id', 'generation', 'source_role', 'binding_sha256'))
            schema.label(action['action_id'])
            schema.label(action['generation'])
            schema.label(action['source_role'])
            schema.digest(action['binding_sha256'])
            key = (mode, action['action_id'])
            schema.need(key not in keys and action['generation'] not in generations,
                        'duplicate action or cross-mode generation reuse')
            keys.add(key)
            generations.add(action['generation'])
    return plan


def _append(state, basename, kind, payload):
    _guard(state)
    schema.need(state['record_count'] < MAX_CHAIN_RECORDS, 'complete chain capacity exhausted')
    sequence = state['record_count']
    # Burn the in-memory sequence before canonicalization or acquisition.
    state['record_count'] += 1
    event = {'schema': 'h25-persistent-replay-event-v1', 'batch_id': state['configuration']['batch_id'],
        'configuration_sha256': state['configuration']['configuration_sha256'],
        'plan_sha256': state['configuration']['plan']['sha256'], 'sequence': sequence,
        'previous': state['head'], 'kind': kind, 'payload': payload,
        'runtime_authority': False, 'cached_result_authority': False}
    raw = schema.canonical(event)
    path = state['configuration']['registry_directory'] + '/' + basename
    pin = _write(state, path, raw)
    # No new event may follow until exact durable readback and final registry
    # custody return. Partial write/readback/custody failure burns this batch.
    _directory(state)
    state['records'].append(pin)
    state['head'] = pin
    return pin


def reserve_batch(original_receivers):
    """Durably burn both epochs/all declared generations; return only live owner.

    Reservation does not authorize any launch, either mode, or return PASS.
    Optimized work still requires the future concrete full normal-PASS receiver.
    No caller supplies a directory, replacement generation or prior completion.
    """
    schema.need(_SHARED is parent._UNKNOWN_OWNER and _SHARED['primary'][0] is None and
                _SHARED['quarantine'][0] is False and _SHARED['pending'][0] is False and
                _SHARED['iterator_uncertain'][0] is False, 'earlier uncertainty forbids registry construction')
    state = None
    try:
        domain.refresh_unknown_owner(_SHARED)
        schema.need(_SHARED['quarantine'][0] is False, 'original owner requires teardown')
        _gate()
        schema.need(_LEN(_BATCHES) == 0, 'one replay batch per owning parent; no retry')
        errors = schema.make_error_owner()
        native = schema.owner_state(errors)
        state = {'pid': _GETPID(), 'phase': 'RESERVING', 'errors': errors, 'native': native,
            'configuration': schema.plain_copy(CONFIGURATION), 'configuration_raw': schema.canonical(CONFIGURATION),
            'receivers': None, 'plan': None, 'source_inventory': None, 'records': [], 'record_count': 0,
            'head': None, 'actions': {}, 'epoch_markers': {}, 'generation_markers': {},
            'primary': [None], 'capture_pending': [None], 'closed': False}
        token = object()
        _BATCHES.append((token, state))
        _directory(state)
        policy = schema.decode(_read(state, state['configuration']['receiver_policy']))
        schema.exact(policy, _REQUIRED)
        schema.exact(original_receivers, _REQUIRED)
        inverse_records = schema.decode(_read(state, state['configuration']['configured_sources']))
        schema.exact(inverse_records, _REQUIRED)
        for name, source_pin in policy.items():
            record = inverse_records[name]
            _verify_source_template_v4(name, source_pin, record, _read(state, source_pin))
        # Template pins remain required; actual configured bytes are separately pinned.
        # A consistent inverse is not bootstrap/configuration/launch approval.
        schema.need(original_receivers['persistent_replay_v1'] is sys.modules[__name__] and
                    original_receivers['replay_receiver_closure_v1'] is closure and
                    original_receivers['epoch_schema_v5'] is schema and
                    original_receivers['epoch_copy_v5'] is copying and
                    original_receivers['epoch_parent_v5'] is epoch and
                    original_receivers['parent_completion_v1'] is parent and
                    original_receivers['parent_domain_v1'] is domain, 'original replay receiving objects differ')
        _fresh(state)
        state['receivers'] = closure.bind_receivers(original_receivers, policy, errors)
        _fresh(state)
        inventory = schema.decode(_read(state, state['configuration']['source_inventory']))
        schema.exact(inventory, ('schema', 'files'))
        schema.need(inventory['schema'] == 'h25-replay-source-inventory-v1' and
                    _TYPE(inventory['files']) is list and 1 <= _LEN(inventory['files']) <= schema.MAX_SEQUENCE,
                    'complete source inventory requires reviewed bounded shards')
        # Each outer row is a pinned shard; a shard holds up to256 complete file
        # pins. Every shard and every listed input are paid on every guard.
        source_files, paths = [], set()
        for shard in inventory['files']:
            schema.blob(shard, schema.RECORD_BYTES)
            source_files.append(shard)
            shard_data = schema.decode(_read(state, shard))
            schema.exact(shard_data, ('schema', 'files'))
            schema.need(shard_data['schema'] == 'h25-replay-source-shard-v1' and
                        _TYPE(shard_data['files']) is list and 1 <= _LEN(shard_data['files']) <= schema.MAX_SEQUENCE,
                        'source shard shape differs')
            for pin in shard_data['files']:
                schema.blob(pin)
                schema.need(pin['path'] not in paths, 'duplicate full-source path')
                paths.add(pin['path'])
                source_files.append(pin)
        schema.need(all(pin['path'] in paths for pin in policy.values()),
                    'receiver source omitted from complete inventory')
        state['source_inventory'] = source_files
        state['plan'] = _plan(_read(state, state['configuration']['plan']), state['configuration'])
        configuration = state['configuration']
        _append(state, 'batch-' + configuration['batch_id'] + '.json', 'BATCH_RESERVED',
                {'mode_order': list(MODES), 'retry_or_restore_allowed': False,
                 'full_schedule_sha256': state['plan']['full_schedule_sha256']})
        for mode in MODES:
            row = state['plan'][mode]
            # Key excludes mode, batch, source/configuration and session path:
            # moving any of those cannot resurrect an old epoch/generation.
            epoch_key = schema.sha(schema.canonical({'epoch_id': row['epoch_id']}))
            state['epoch_markers'][mode] = _append(state, 'epoch-' + epoch_key + '.json', 'EPOCH_RESERVED',
                {'mode': mode, 'epoch_id': row['epoch_id'], 'parent_plan_sha256': row['parent_plan_sha256']})
            for action in row['actions']:
                generation_key = schema.sha(schema.canonical({'generation': action['generation']}))
                pin = _append(state, 'generation-' + generation_key + '.json', 'GENERATION_RESERVED',
                    {'mode': mode, 'epoch_id': row['epoch_id'], 'action': action})
                key = (mode, action['action_id'])
                state['generation_markers'][key] = pin
                state['actions'][key] = {'phase': 'RESERVED', 'source': action, 'raw_pin': None}
        _append(state, 'batch-' + configuration['batch_id'] + '-reserved.json', 'RESERVATION_COMPLETE',
                {'epochs': 2, 'generations': _LEN(state['actions']), 'launches_authorized': 0})
        state['phase'] = 'RESERVED'
        return token
    except BaseException as error:
        # Reserve the exact delivered primary before any fallible helper.
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        if state is not None:
            if state['primary'][0] is None:
                state['primary'][0] = error
            state['phase'] = 'STOP'
        # No STOP-file acquisition, cleanup retry, repair, unlink or restore.
        raise


def burn_action(owner, mode, action_id):
    """One-shot durable denial of replay, NOT permission to execute the action."""
    state = _entry(owner)
    try:
        _guard(state)
        schema.need(state['phase'] == 'RESERVED' and not state['closed'], 'registry is terminal')
        schema.choice(mode, MODES)
        schema.label(action_id)
        key = (mode, action_id)
        schema.need(key in state['actions'], 'action absent from independently reviewed complete plan')
        action = state['actions'][key]
        schema.need(action['phase'] == 'RESERVED', 'same-parent action replay')
        action['phase'] = 'ATTEMPT_CONSUMED'
        generation = action['source']['generation']
        digest = schema.sha(schema.canonical({'generation': generation}))
        pin = _append(state, 'consume-' + digest + '.json', 'ATTEMPT_CONSUMED',
            {'mode': mode, 'action_id': action_id, 'generation': generation,
             'reservation': state['generation_markers'][key], 'runtime_authority': False})
        return schema.plain_copy(pin)
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        if state['primary'][0] is None:
            state['primary'][0] = error
        state['phase'] = 'STOP'
        raise


def record_captured_return(owner, mode, action_id, raw_pin):
    """Bind already captured raw bytes before a concrete receiver compares them.

    Caller provenance and raw result encoding belong to the exact actual
    receiver. This API neither decodes that payload nor substitutes its codec,
    accepts a child PASS, or converts native tuple/bytes policy data to JSON.
    """
    state = _entry(owner)
    try:
        _guard(state)
        schema.choice(mode, MODES)
        schema.label(action_id)
        key = (mode, action_id)
        schema.need(key in state['actions'], 'unknown action capture')
        action = state['actions'][key]
        schema.need(action['phase'] == 'ATTEMPT_CONSUMED' and not state['closed'], 'capture replay or closed log')
        action['phase'] = 'CAPTURE_ATTEMPT_CONSUMED'
        # Root the returned pin in source-owned state before validating/copying.
        # The actual original writer already owns raw bytes and its descriptor.
        state['capture_pending'][0] = raw_pin
        schema.blob(raw_pin)
        _fresh(state)
        copying.verify(raw_pin, error_owner=state['errors'])
        _fresh(state)
        pin_copy = schema.plain_copy(raw_pin)
        generation = action['source']['generation']
        digest = schema.sha(schema.canonical({'generation': generation}))
        event_pin = _append(state, 'capture-' + digest + '.json', 'RAW_RETURN_CAPTURED',
            {'mode': mode, 'action_id': action_id, 'generation': generation, 'raw': pin_copy,
             'semantic_validation': 'NOT_PERFORMED_BY_REPLAY_COMPONENT'})
        _fresh(state)
        copying.verify(raw_pin, error_owner=state['errors'])
        _fresh(state)
        action['raw_pin'] = pin_copy
        action['phase'] = 'RAW_CAPTURED_NOT_VALIDATED'
        state['capture_pending'][0] = None
        return schema.plain_copy(event_pin)
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        if state['primary'][0] is None:
            state['primary'][0] = error
        state['phase'] = 'STOP'
        raise


def seal_audit(owner):
    """Return a fresh durable audit head; never complete the scientific task."""
    state = _entry(owner)
    try:
        _guard(state)
        schema.need(state['phase'] == 'RESERVED' and not state['closed'], 'audit already consumed')
        state['closed'] = True
        counts = {name: sum(row['phase'] == name for row in state['actions'].values())
                  for name in ('RESERVED', 'ATTEMPT_CONSUMED', 'CAPTURE_ATTEMPT_CONSUMED',
                               'RAW_CAPTURED_NOT_VALIDATED')}
        head = _append(state, 'batch-' + state['configuration']['batch_id'] + '-audit.json', 'AUDIT_SEALED',
                       {'counts': counts, 'full_completion': False, 'resume_allowed': False})
        state['phase'] = 'SEALED'
        return {'schema': 'h25-persistent-replay-audit-head-v1', 'head': schema.plain_copy(head),
            'records': state['record_count'], 'configuration_sha256': state['configuration']['configuration_sha256'],
            'full_completion': False, 'runtime_authority': False, 'resume_allowed': False}
    except BaseException as error:
        if _SHARED['primary'][0] is None:
            _SHARED['primary'][0] = error
        _SHARED['quarantine'][0] = True
        if state['primary'][0] is None:
            state['primary'][0] = error
        state['phase'] = 'STOP'
        raise


def stop_evidence(owner):
    """No I/O or projection: retained actual slots for original outer teardown."""
    state = _entry(owner)
    return state['primary'], state['errors'], state['capture_pending']
