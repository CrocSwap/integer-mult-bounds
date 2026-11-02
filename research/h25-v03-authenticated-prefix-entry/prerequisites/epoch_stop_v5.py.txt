"""Opaque error evidence and original-source-admitted per-case raw capture.

Source only. Registry/factory provenance must be established by the authenticated
Root before adverse work. There is no arbitrary supplied callback or retry path.
"""
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying

STOP_CONFIGURATION = None
STOP_EXECUTION_APPROVAL = None
STOP_FUNDING = None
STOP_BYTES = 65536
_TYPE, _LEN = type, len
_SINK_REGISTRY = []


def _gate() -> None:
    schema.exact(STOP_CONFIGURATION, ('leaf_policy_sha256', 'configuration_sha256'))
    schema.exact(STOP_EXECUTION_APPROVAL, ('external_launch_policy_sha256',))
    schema.exact(STOP_FUNDING, ('reservation_sha256',))
    for config in (STOP_CONFIGURATION, STOP_EXECUTION_APPROVAL, STOP_FUNDING):
        for value in config.values():
            schema.digest(value)


def retain_stop(directory: str, operation: str, error_owner) -> dict:
    _custody_state = schema.owner_state(error_owner)
    _io = _custody_state[7]
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    schema.path(directory)
    schema.text(operation, 96)
    _gate()
    record = {'schema': 'h25-negative-epoch-stop-v3', 'status': 'STOP', 'operation': operation,
              'opaque_error_projection': schema.error_snapshot(error_owner),
              'retry_permitted': False, 'partial_products_retained': True, 'complete_cost': None}
    raw = schema.canonical(record)
    schema.need(_LEN(raw) <= STOP_BYTES, 'STOP byte bound exceeded')
    # If this fails, caller's already active except block records the secondary
    # opaquely and bare-reraises its exact original primary. No callback fallback.
    return copying.write_once(directory + '/STOP.json', raw, error_owner=error_owner)


def make_raw_sink(directory: str, error_owner, original_source_guard, original_guard_record,
                  source_sha256: str) -> tuple:
    """Invoke only through the original Root's source-authenticated factory.

    The supplied guard and record must be the original Root factory return,
    adopted before adverse input; this function does not confer that provenance.
    Current source/primitive authentication remains delegated to that original
    guard. Capture functions themselves are source-fixed here and registered by
    opaque identity, so a consumer cannot supply its own writer callback.
    """
    _custody_state = schema.owner_state(error_owner)
    _io = _custody_state[7]
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    schema.path(directory)
    schema.digest(source_sha256)
    schema.check_original_function(original_source_guard, original_guard_record)
    _gate()
    schema.need(_LEN(_SINK_REGISTRY) < 2, 'finite original sink factory count exceeded')
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    _io[10] = True
    try:
        original_source_guard()
    except BaseException as guard_error:
        if _io[12] is None:
            _io[12] = guard_error
        _io[0] = True
        _io[11] = True
        _io[4] = True
        raise
    _io[10] = False
    schema.check_original_function(original_source_guard, original_guard_record)
    copying.require_entries(directory, (), error_owner=error_owner)
    consumed = [False] * schema.CASE_SLOTS

    def capture(index, raw):
        schema.integer(index, 0, schema.CASE_SLOTS - 1)
        schema.need(_TYPE(raw) is bytes and 0 < _LEN(raw) <= schema.RECORD_BYTES, 'raw case bytes differ')
        schema.need(_TYPE(consumed) is list and _LEN(consumed) == schema.CASE_SLOTS, 'raw capture state differs')
        schema.boolean(consumed[index])
        schema.need(consumed[index] is False, 'raw case capture already consumed')
        consumed[index] = True
        # Native integer formatting only after exact type and finite bound.
        name = 'case-%02d.raw.json' % index
        return copying.write_once(directory + '/' + name, raw, error_owner=error_owner)

    capture_record = schema.capture_original_function(capture)
    ticket = object()
    packet = ('h25-original-epoch-raw-sink-v3', ticket, capture, capture_record,
              original_source_guard, original_guard_record, error_owner, directory, source_sha256)
    _SINK_REGISTRY.append(packet)
    return packet


def check_raw_sink(packet, error_owner, expected_source_sha256: str) -> tuple:
    schema.owner_state(error_owner)
    schema.digest(expected_source_sha256)
    schema.need(_TYPE(packet) is tuple and _LEN(packet) == 9, 'original raw sink packet differs')
    schema.text(packet[0], 128)
    schema.need(packet[0] == 'h25-original-epoch-raw-sink-v3' and _TYPE(packet[1]) is object,
                'original raw sink tag/ticket differs')
    schema.need(packet[6] is error_owner, 'raw sink owner differs')
    schema.path(packet[7])
    schema.digest(packet[8])
    schema.need(packet[8] == expected_source_sha256, 'independent raw sink source pin differs')
    # Identity only, never equality on a foreign packet or function.
    found = False
    for original in _SINK_REGISTRY:
        if packet is original:
            found = True
            break
    schema.need(found is True, 'raw sink was not original authenticated factory return')
    schema.check_original_function(packet[2], packet[3])
    schema.check_original_function(packet[4], packet[5])
    return packet


def capture_case(packet, error_owner, expected_source_sha256: str, index: int) -> dict:
    """Persist one rooted raw outcome before any behavior comparison/next case.

    Failures leave RETURNED_NOT_CAPTURED and the opaque raw return/error rooted.
    The caller preserves original failure with a bare re-raise; no sink/source
    guard retry, exception formatter, or callback-bearing cleanup is attempted.
    """
    _custody_state = schema.owner_state(error_owner)
    _io = _custody_state[7]
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    row = schema.case_slot(error_owner, index)
    schema.need(row[3] == 'RETURNED_NOT_CAPTURED', 'case capture state differs')
    original = check_raw_sink(packet, error_owner, expected_source_sha256)
    guard, guard_record, capture, capture_record = original[4], original[5], original[2], original[3]
    schema.check_original_function(guard, guard_record)
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    _io[10] = True
    try:
        guard()
    except BaseException as guard_error:
        if _io[12] is None:
            _io[12] = guard_error
        _io[0] = True
        _io[11] = True
        _io[4] = True
        raise
    _io[10] = False
    schema.check_original_function(guard, guard_record)
    schema.check_original_function(capture, capture_record)
    if row[2] is True:
        raw_value = {'returned_error': schema.project_error(row[1])}
    else:
        raw_value = {'returned_value': schema.plain_copy(row[1])}
    raw = schema.canonical({'schema': 'h25-epoch-raw-case-v3', 'case': row[0], 'slot': index,
                            'capture_state_before_write': 'RETURNED_NOT_CAPTURED',
                            'opaque_original_retained_in_owner': True, 'raw': raw_value})
    receipt = capture(index, raw)
    row[4] = receipt  # Root exact original return before any validation/callback.
    schema.check_original_function(capture, capture_record)
    schema.check_original_function(guard, guard_record)
    if _io[0] or _io[1] or _io[10]:
        raise schema.IO_QUARANTINE_ERROR
    _io[10] = True
    try:
        guard()
    except BaseException as guard_error:
        if _io[12] is None:
            _io[12] = guard_error
        _io[0] = True
        _io[11] = True
        _io[4] = True
        raise
    _io[10] = False
    schema.check_original_function(guard, guard_record)
    schema.check_original_function(capture, capture_record)
    schema.blob(receipt, schema.RECORD_BYTES)
    expected_path = original[7] + '/case-%02d.raw.json' % index
    schema.need(receipt['path'] == expected_path and receipt['sha256'] == schema.sha(raw) and
                receipt['bytes'] == _LEN(raw), 'original raw sink receipt differs')
    row[3] = 'RAW_CAPTURED'
    return receipt
