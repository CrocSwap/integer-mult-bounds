"""Strict source-only parser for the unchanged original helper/triple protocol.

No function is invoked during source work. Independent parent launch, actual
producer PID/generation, source closure and whole-domain evidence remain required.
"""
import json
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying

PARSER_CONFIGURATION = None
PARSER_EXECUTION_APPROVAL = None
PARSER_FUNDING = None
_TYPE, _LEN = type, len
ORIGINAL_HELPER_SHA256 = 'aa0a315110e031e19291970c9611fe5e0f91465fa20eaec51e81186099563f78'
PRODUCTION_HEADERS = ('field_service_v1.h', 'field_loader_snapshot_v1.h')
PRELAUNCH_KEYS = ('schema', 'status', 'command', 'timeout_seconds', 'context',
    'stdout_path', 'stderr_path', 'attempt_path', 'journal_path', 'process_group_policy',
    'operational_log_threshold_bytes', 'child_only_inherited_hard_file_limit_bytes',
    'returncode', 'process_id', 'direct_child_reaped', 'spawn_entered', 'spawn_returned',
    'descendant_termination_joined', 'failure_log_hashes_final')
STARTED_KEYS = PRELAUNCH_KEYS + ('parent_file_limits_before', 'preexec_code_sha256', 'single_thread_before_spawn')
FINAL_KEYS = STARTED_KEYS + ('logs', 'parent_file_limits_after')


def _decode_original(raw: bytes, limit: int) -> dict:
    schema.integer(limit, 1, schema.RAW_RESULT_BYTES)
    schema.need(_TYPE(raw) is bytes, 'exact legacy bytes required')
    schema.need(_LEN(raw) <= limit, 'legacy record byte bound differs')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=schema._pairs,
                       parse_constant=schema._reject_constant)
    schema.need(_TYPE(value) is dict, 'legacy record is not exact object')
    return schema.plain_copy(value)


def _source_row(value) -> None:
    schema.exact(value, ('sha256', 'bytes', 'mode'))
    schema.digest(value['sha256'])
    schema.integer(value['bytes'], 1, schema.FILE_BYTES)
    schema.integer(value['mode'], 0, 0o7777)


def _limits(value) -> None:
    schema.sequence(value, 2)
    for item in value:
        schema.integer(item, -1, (1 << 64) - 1)
        schema.need(item == -1 or item >= 16 * 1024 * 1024, 'inherited file limit below original cap')
    soft, hard = value
    schema.need((soft == -1 and hard == -1) or
                (soft != -1 and (hard == -1 or soft <= hard)), 'invalid inherited soft/hard order')


def _census(value, expected_pid: int) -> None:
    schema.integer(expected_pid, 1, (1 << 31) - 1)
    schema.exact(value, ('process_id', 'task_ids', 'task_count'))
    schema.integer(value['process_id'], 1, (1 << 31) - 1)
    schema.integer(value['task_count'], 1, 1)
    schema.sequence(value['task_ids'], 1)
    schema.integer(value['task_ids'][0], 1, (1 << 31) - 1)
    schema.need(value['process_id'] == value['task_ids'][0] == expected_pid, 'original producer thread identity differs')


def _context(value, expected, role) -> None:
    keys = ('source', 'source_name', 'no_cached_binary', 'module_name', 'target')
    if role == 'production':
        keys += ('source_headers', 'system_header_admission_sha256')
    schema.exact(value, keys)
    _source_row(value['source'])
    schema.text(value['source_name'], 256)
    schema.text(value['module_name'], 256)
    schema.boolean(value['no_cached_binary'])
    schema.path(value['target'])
    if role == 'production':
        schema.exact(value['source_headers'], PRODUCTION_HEADERS)
        for row in value['source_headers'].values():
            _source_row(row)
        schema.digest(value['system_header_admission_sha256'])
    schema.need(value == expected, 'original compiler context differs')


def _event(event, kind, expected, row, context, compiler_pid) -> None:
    schema.choice(kind, ('PRELAUNCH_INTENT', 'STARTED', 'EXIT0_LOGS_STABLE_PENDING_SOURCE_CUSTODY'))
    keys = PRELAUNCH_KEYS if kind == 'PRELAUNCH_INTENT' else STARTED_KEYS if kind == 'STARTED' else FINAL_KEYS
    schema.exact(event, keys)
    for key in ('schema', 'status', 'process_group_policy'):
        schema.text(event[key], 128)
    schema.need(event['schema'] == 'h25-cold-build-attempt-v1' and event['status'] == kind and
                event['process_group_policy'] == 'INHERIT_OUTER_GROUP_NO_NEW_SESSION', 'original event tag differs')
    schema.need(_TYPE(event['command']) is list and 1 <= _LEN(event['command']) <= 64, 'original argv shape differs')
    for argument in event['command']:
        schema.text(argument, 8192)
    schema.need(event['command'] == expected['command'], 'original event command differs')
    schema.integer(event['timeout_seconds'], 1, 15)
    schema.need(event['timeout_seconds'] == expected['timeout_seconds'], 'original timeout differs')
    _context(event['context'], context, row['role'])
    for event_key, row_key in (('stdout_path', 'stdout'), ('stderr_path', 'stderr'),
                               ('attempt_path', 'attempt'), ('journal_path', 'journal')):
        schema.path(event[event_key])
        schema.need(event[event_key] == row[row_key]['path'], 'original event origin differs')
    schema.integer(event['operational_log_threshold_bytes'], schema.LOG_BYTES, schema.LOG_BYTES)
    schema.integer(event['child_only_inherited_hard_file_limit_bytes'], 16 * 1024 * 1024, 16 * 1024 * 1024)
    for key in ('spawn_entered', 'spawn_returned', 'descendant_termination_joined', 'failure_log_hashes_final'):
        schema.boolean(event[key])
    schema.need(event['descendant_termination_joined'] is False and event['failure_log_hashes_final'] is False,
                'direct-child evidence cannot become outer-domain authority')
    if kind == 'PRELAUNCH_INTENT':
        schema.need(event['returncode'] is None and event['process_id'] is None and
                    event['direct_child_reaped'] is None and event['spawn_entered'] is False and
                    event['spawn_returned'] is False, 'original prelaunch fields differ')
        return
    schema.integer(event['process_id'], 1, (1 << 31) - 1)
    schema.integer(compiler_pid, 1, (1 << 31) - 1)
    schema.need(event['process_id'] == compiler_pid and event['spawn_entered'] is True and
                event['spawn_returned'] is True, 'original started process differs')
    _limits(event['parent_file_limits_before'])
    schema.need(event['parent_file_limits_before'] == expected['parent_file_limits'], 'independent inherited limits differ')
    schema.digest(event['preexec_code_sha256'])
    schema.need(event['preexec_code_sha256'] == expected['preexec_code_sha256'], 'independent preexec bytecode pin differs')
    _census(event['single_thread_before_spawn'], expected['producer_process_id'])
    if kind == 'STARTED':
        schema.need(event['returncode'] is None and event['direct_child_reaped'] is None, 'started event claims completion')
    else:
        schema.integer(event['returncode'], 0, 0)
        schema.boolean(event['direct_child_reaped'])
        schema.need(event['direct_child_reaped'] is True, 'direct compiler child not reaped')
        _limits(event['parent_file_limits_after'])
        schema.need(event['parent_file_limits_after'] == expected['parent_file_limits'], 'parent limits changed')


def authenticate_original_build(row: dict, expected: dict, *, error_owner) -> dict:
    schema.owner_state(error_owner)
    schema.exact(PARSER_CONFIGURATION, ('leaf_policy_sha256', 'configuration_sha256', 'original_helper_sha256'))
    schema.exact(PARSER_EXECUTION_APPROVAL, ('external_launch_policy_sha256',))
    schema.exact(PARSER_FUNDING, ('reservation_sha256',))
    for config in (PARSER_CONFIGURATION, PARSER_EXECUTION_APPROVAL, PARSER_FUNDING):
        for value in config.values():
            schema.digest(value)
    schema.need(PARSER_CONFIGURATION['original_helper_sha256'] == ORIGINAL_HELPER_SHA256, 'original helper source protocol differs')
    schema.build(row)
    schema.need(row['role'] in schema.ROLES[:3] and row['producer_role'] == 'group01', 'variant cannot become original row')
    schema.exact(expected, ('role', 'command', 'timeout_seconds', 'source', 'source_name', 'module_name',
                           'source_headers', 'system_header_admission_sha256', 'preexec_code_sha256',
                           'producer_process_id', 'parent_file_limits'))
    schema.choice(expected['role'], schema.ROLES[:3])
    schema.need(expected['role'] == row['role'], 'independent original role differs')
    schema.need(_TYPE(expected['command']) is list and 1 <= _LEN(expected['command']) <= 64, 'independent argv shape differs')
    for argument in expected['command']:
        schema.text(argument, 8192)
        schema.need(_LEN(argument) > 0, 'empty independent compiler argument')
    schema.path(expected['command'][0])
    schema.integer(expected['timeout_seconds'], 1, 15)
    _source_row(expected['source'])
    schema.text(expected['source_name'], 256)
    schema.text(expected['module_name'], 256)
    schema.digest(expected['preexec_code_sha256'])
    schema.integer(expected['producer_process_id'], 1, (1 << 31) - 1)
    _limits(expected['parent_file_limits'])
    if row['role'] == 'production':
        schema.exact(expected['source_headers'], PRODUCTION_HEADERS)
        for header in expected['source_headers'].values():
            _source_row(header)
        schema.digest(expected['system_header_admission_sha256'])
    else:
        schema.need(expected['source_headers'] is None and expected['system_header_admission_sha256'] is None,
                    'fixture cannot borrow production header authority')
    expected = schema.plain_copy(expected)
    schema.need(schema.sha(schema.canonical({'argv': expected['command']})) == row['command_sha256'], 'original command pin differs')
    copying.verify(row['original_output'], error_owner=error_owner)
    receipt = _decode_original(copying.read_verified(row['original_receipt'], 65536, error_owner=error_owner), 65536)
    receipt_keys = ('command', 'returncode', 'stdout', 'stderr', 'attempt_path', 'attempt_journal_path',
                    'process_policy', 'source', 'source_name', 'no_cached_binary', 'module_name', 'path', 'status', 'binary')
    if row['role'] == 'production':
        receipt_keys += ('source_headers', 'system_header_admission_sha256')
    schema.exact(receipt, receipt_keys)
    # Both sides are bounded native copies before any nested comparison.
    schema.integer(receipt['returncode'], 0, 0)
    schema.boolean(receipt['no_cached_binary'])
    for key in ('status', 'process_policy', 'source_name', 'module_name'):
        schema.text(receipt[key], 256)
    for key in ('path', 'attempt_path', 'attempt_journal_path'):
        schema.path(receipt[key])
    schema.need(_TYPE(receipt['command']) is list and 1 <= _LEN(receipt['command']) <= 64, 'receipt argv shape differs')
    for argument in receipt['command']:
        schema.text(argument, 8192)
    _source_row(receipt['source'])
    _source_row(receipt['binary'])
    schema.need(receipt['command'] == expected['command'] and receipt['no_cached_binary'] is True and
                receipt['status'] == 'COLD_NATIVE_BUILD_SOURCE_CUSTODY_PASS' and
                receipt['path'] == row['original_output']['path'] and receipt['attempt_path'] == row['attempt']['path'] and
                receipt['attempt_journal_path'] == row['journal']['path'] and
                receipt['process_policy'] == 'INHERIT_OUTER_GROUP_NO_NEW_SESSION', 'original cold receipt differs')
    for key in ('source', 'source_name', 'module_name'):
        schema.need(receipt[key] == expected[key], 'original source/module field differs')
    schema.need(receipt['binary'] == {'sha256': row['original_output']['sha256'], 'bytes': row['original_output']['bytes'],
                                     'mode': row['original_output']['identity']['mode'] & 0o7777}, 'actual original binary differs')
    if row['role'] == 'production':
        schema.exact(receipt['source_headers'], PRODUCTION_HEADERS)
        for header in receipt['source_headers'].values():
            _source_row(header)
        schema.digest(receipt['system_header_admission_sha256'])
        schema.need(receipt['source_headers'] == expected['source_headers'] and
                    receipt['system_header_admission_sha256'] == expected['system_header_admission_sha256'], 'original headers differ')
    attempt = _decode_original(copying.read_verified(row['attempt'], 65536, error_owner=error_owner), 65536)
    schema.exact(attempt, FINAL_KEYS)
    schema.integer(attempt['process_id'], 1, (1 << 31) - 1)
    context = {'source': expected['source'], 'source_name': expected['source_name'], 'no_cached_binary': True,
               'module_name': expected['module_name'], 'target': row['original_output']['path']}
    if row['role'] == 'production':
        context.update(source_headers=expected['source_headers'], system_header_admission_sha256=expected['system_header_admission_sha256'])
    _event(attempt, 'EXIT0_LOGS_STABLE_PENDING_SOURCE_CUSTODY', expected, row, context, attempt['process_id'])
    schema.exact(attempt['logs'], ('stdout', 'stderr'))
    for stream in ('stdout', 'stderr'):
        snapshot = attempt['logs'][stream]
        schema.exact(snapshot, ('path', 'bytes_before', 'bytes_after', 'prefix_bytes_hashed', 'prefix_sha256',
            'preview_bytes', 'preview_utf8', 'stable_during_snapshot', 'complete_file_sha256', 'raw_finality',
            'operational_threshold_bytes', 'child_inherited_hard_file_limit_bytes'))
        schema.path(snapshot['path'])
        for key in ('bytes_before', 'bytes_after', 'prefix_bytes_hashed'):
            schema.integer(snapshot[key], 0, schema.LOG_BYTES)
        schema.digest(snapshot['prefix_sha256'])
        schema.digest(snapshot['complete_file_sha256'])
        schema.integer(snapshot['preview_bytes'], 0, 512)
        schema.text(snapshot['preview_utf8'], 512)
        schema.boolean(snapshot['stable_during_snapshot'])
        schema.text(snapshot['raw_finality'], 128)
        schema.integer(snapshot['operational_threshold_bytes'], schema.LOG_BYTES, schema.LOG_BYTES)
        schema.integer(snapshot['child_inherited_hard_file_limit_bytes'], 16 * 1024 * 1024, 16 * 1024 * 1024)
        raw_log = copying.read_verified(row[stream], schema.LOG_BYTES, error_owner=error_owner)
        preview = raw_log[:512]
        schema.need(schema.canonical(snapshot) == schema.canonical(receipt[stream]) and snapshot['path'] == row[stream]['path'] and
                    snapshot['bytes_before'] == snapshot['bytes_after'] == snapshot['prefix_bytes_hashed'] == row[stream]['bytes'] and
                    snapshot['prefix_sha256'] == snapshot['complete_file_sha256'] == row[stream]['sha256'] and
                    snapshot['stable_during_snapshot'] is True and
                    snapshot['raw_finality'] == 'DIRECT_CHILD_EXIT0_AND_STABLE_COMPLETED_LOG' and
                    snapshot['preview_bytes'] == _LEN(preview) and snapshot['preview_utf8'] == preview.decode('utf-8', errors='replace'),
                    'complete original raw log/preview differs')
    raw_journal = copying.read_verified(row['journal'], schema.JOURNAL_BYTES, error_owner=error_owner)
    lines = raw_journal.splitlines(keepends=True)
    schema.need(_LEN(lines) == 3 and all(line.endswith(b'\n') for line in lines), 'missing/extra/retried original journal')
    events = [_decode_original(line, 65536) for line in lines]
    for kind, event in zip(('PRELAUNCH_INTENT', 'STARTED', 'EXIT0_LOGS_STABLE_PENDING_SOURCE_CUSTODY'), events):
        _event(event, kind, expected, row, context, attempt['process_id'])
    schema.need(schema.canonical(events[-1]) == schema.canonical(attempt), 'original final journal/attempt differs')
    return {'schema': 'h25-original-build-data-authentication-v3', 'role': row['role'],
            'original_build_record_sha256': schema.sha(schema.canonical(row)),
            'original_receipt_sha256': row['original_receipt']['sha256'],
            'original_helper_sha256': ORIGINAL_HELPER_SHA256,
            'actual_parent_launch_terminal_custody_binding_still_required': True, 'not_runtime_authority': True}
