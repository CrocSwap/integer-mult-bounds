"""Concrete terminal receiver for ELF gap and separately sourced fault Roots.

A recipe catalogue is never a completed control report. Control driver/source
and all expected raw oracle contracts must exist and be independently admitted;
the source-only gate blocks this receiver while those bodies are absent.
"""
import epoch_schema_v5 as schema
import epoch_copy_v5 as copying
import group01_evidence_v1 as evidence
import parent_domain_v1 as domain
import owned_root_v2 as owned
import component_control_validation_v1 as component_wire

CONTROL_EXECUTORS_CONFIGURATION = None
_TYPE, _LEN = type, len
_TERMINAL_LIMIT = 16777216
_early_codec_MAX_DEPTH = 32
_early_codec_MAX_NODES = 200000
_early_codec_MAX_CONTAINER = 16384
_early_codec_MAX_STRING_CHARS = 65536
_early_codec_MAX_BYTES = 65536
_early_codec_MAX_INTEGER_BITS = 128
_early_codec_MAX_ENCODED = 2 * 1024 * 1024
ELF_ENTRIES = ('admit_service_elf', 'admit_loaded_maps', 'provider_requests',
               'admit_runtime_provider_map', 'admit_bootstrap_import_profile')


def _read(state, path, limit):
    pin = copying.inspect(path, limit, error_owner=state['errors'])
    raw = copying.read_verified_complete_v3(pin, limit, error_owner=state['errors'])
    return pin, raw


def _typed_equal_v3(actual, expected, depth=0):
    """Exact native comparison; no bool/int or tuple/list collapse."""
    schema.need(depth <= 64, 'exact terminal comparator depth exceeded')
    kind = _TYPE(actual)
    if kind is not _TYPE(expected):
        return False
    if actual is None:
        return True
    if kind is bool or kind is int or kind is str or kind is bytes:
        return actual == expected
    if kind is tuple or kind is list:
        return len(actual) == len(expected) and all(_typed_equal_v3(a, b, depth + 1) for a, b in zip(actual, expected))
    if kind is dict:
        for mapping in (actual, expected):
            schema.need(len(mapping) <= 16384 and all(_TYPE(key) is str for key in mapping),
                        'exact terminal comparator native dictionary keys required')
        return set(actual) == set(expected) and all(_typed_equal_v3(actual[k], expected[k], depth + 1) for k in actual)
    raise schema.EpochStop('foreign terminal comparator value rejected')


def _integer_fields_v3(record, names):
    for key in names:
        schema.integer(record[key], 0, (1 << 128) - 1)


def take_elf_gap_observation(owner, joined):
    state = owned._state(owner)
    run = None
    try:
        state, run = owned._joined(owner, joined)
        row = run['plan']
        schema.need(row['source_role'] == 'elf41' and row['phase'] == 'finite', 'wrong concrete ELF Root')
        expected = row['evidence_plan']
        schema.exact(expected, ('schema', 'mode', 'entry_counts', 'record_kinds', 'authority_bindings',
            'terminal_relative', 'required_output_bytes', 'required_terminal_bytes', 'leaf_source'))
        schema.need(expected['schema'] == 'h25-gap41-parent-evidence-v2' and expected['mode'] == state['mode'] and
            expected['terminal_relative'] == 'gap-terminal-v2.typed' and expected['required_output_bytes'] == 469762048 and
            expected['required_terminal_bytes'] == _TERMINAL_LIMIT, 'complete original ELF resource/output contract differs')
        schema.blob(expected['leaf_source'])
        copying.verify(expected['leaf_source'], error_owner=state['errors'])
        run['actual_raw'] = {}
        actual = run['actual_raw']
        actual['stdout'] = _read(state, row['evidence_directory'] + '/stdout.raw', schema.LOG_BYTES)
        actual['stderr'] = _read(state, row['evidence_directory'] + '/stderr.raw', schema.LOG_BYTES)
        actual['terminal'] = _read(state, row['output'] + '/gap-terminal-v2.typed', _TERMINAL_LIMIT)
        schema.need(actual['stderr'][1] == b'', 'ELF Root stderr differs')
        final = _early_codec_decode(actual['stdout'][1], schema.LOG_BYTES)
        terminal = _early_codec_decode(actual['terminal'][1], _TERMINAL_LIMIT)
        run['actual_native'] = (final, terminal)
        schema.exact(final, ('schema', 'status', 'artifact', 'all_known_tokens_consumed',
            'original_parser_class_available', 'original_parser_class_id', 'close_attempted', 'close_confirmed',
            'unknown_acquisition', 'quarantined', 'first_primary_id', 'all_error_slot_ids',
            'late_native_error_typed_records', 'evidence_incomplete', 'no_full_caller_or_native_admission',
            'opaque_objects_retained_until_process_exit'))
        schema.integer(final['original_parser_class_id'], 1, (1 << 128) - 1)
        schema.need(final['schema'] == 'h25-gap41-terminal-artifact-receipt-v3' and final['status'] == 'COMPLETE' and
            final['all_known_tokens_consumed'] is True and final['original_parser_class_available'] is True and
            final['quarantined'] is False and final['first_primary_id'] is None and
            final['all_error_slot_ids'] == () and final['late_native_error_typed_records'] == () and
            final['evidence_incomplete'] is False and final['no_full_caller_or_native_admission'] is True and
            final['opaque_objects_retained_until_process_exit'] is True,
            'ELF final postcleanup status differs; preterminal handoff is insufficient')
        for key in ('close_attempted', 'close_confirmed', 'unknown_acquisition'):
            schema.need(_TYPE(final[key]) is tuple and _LEN(final[key]) == 5 and all(_TYPE(v) is bool for v in final[key]),
                        'ELF exact native cleanup flags differ')
        schema.need(final['close_attempted'] == final['close_confirmed'] and all(final['close_confirmed']) and
                    not any(final['unknown_acquisition']), 'ELF known close or acquisition uncertainty')
        artifact = final['artifact']
        schema.exact(artifact, ('name', 'created', 'intended_bytes', 'sha256', 'readback_complete', 'close_attempted',
            'close_confirmed', 'directory_fsync_complete', 'maximum_bytes', 'ordinary_stdout_maximum_bytes'))
        _integer_fields_v3(artifact, ('intended_bytes', 'maximum_bytes', 'ordinary_stdout_maximum_bytes'))
        schema.need(artifact['name'] == expected['terminal_relative'] and artifact['created'] is True and
            artifact['intended_bytes'] == actual['terminal'][0]['bytes'] and artifact['sha256'] == actual['terminal'][0]['sha256'] and
            all(artifact[k] is True for k in ('readback_complete', 'close_attempted', 'close_confirmed', 'directory_fsync_complete')) and
            artifact['maximum_bytes'] == _TERMINAL_LIMIT and artifact['ordinary_stdout_maximum_bytes'] == schema.LOG_BYTES,
            'ELF terminal artifact full custody differs')
        schema.exact(terminal, ('schema', 'parent_receipt', 'error_slots', 'first_primary_id', 'overflow',
            'native_error_typed_records', 'pending_values_typed_chunks', 'pending_raw_typed_chunks', 'pending_flags',
            'pending_error_id', 'pending_return_id', 'pending_builder_id', 'known_fd_tokens', 'pending_acquisitions',
            'close_attempted', 'close_confirmed', 'unknown_acquisition', 'quarantined', 'evidence_incomplete',
            'last_source_path', 'original_root_ready', 'root_internal_uncertainty', 'original_parser_registry_available',
            'original_parser_class_available', 'original_parser_class_id', 'all_nonterminal_known_cleanup_attempts_before_encoding',
            'reserved_terminal_token_retained_until_bounded_artifact_write', 'opaque_objects_retained_until_process_exit',
            'native_or_full_union_admission'))
        schema.integer(terminal['original_parser_class_id'], 1, (1 << 128) - 1)
        schema.need(_TYPE(terminal['pending_flags']) is tuple and len(terminal['pending_flags']) == 4 and
                    all(_TYPE(v) is bool for v in terminal['pending_flags']), 'ELF exact native pending bool tuple required')
        schema.need(terminal['schema'] == 'h25-gap41-terminal-raw-v3' and terminal['error_slots'] == () and
            terminal['first_primary_id'] is None and terminal['overflow'] is None and terminal['native_error_typed_records'] == () and
            terminal['quarantined'] is False and terminal['evidence_incomplete'] is False and
            terminal['original_root_ready'] is True and terminal['root_internal_uncertainty'] is None and
            terminal['original_parser_registry_available'] is True and terminal['original_parser_class_available'] is True and
            terminal['original_parser_class_id'] == final['original_parser_class_id'] and
            terminal['all_nonterminal_known_cleanup_attempts_before_encoding'] is True and
            terminal['reserved_terminal_token_retained_until_bounded_artifact_write'] is True and
            terminal['opaque_objects_retained_until_process_exit'] is True and terminal['native_or_full_union_admission'] is False,
            'ELF retained raw cleanup/source envelope differs')
        schema.need(terminal['pending_values_typed_chunks'] == () and terminal['pending_raw_typed_chunks'] == () and
            terminal['pending_flags'] == (False, False, False, False) and
            all(terminal[k] is None for k in ('pending_error_id', 'pending_return_id', 'pending_builder_id')),
            'ELF raw terminal still retains unvalidated pending values')
        for key in ('pending_acquisitions', 'close_attempted', 'close_confirmed', 'unknown_acquisition'):
            schema.need(_TYPE(terminal[key]) is tuple and len(terminal[key]) == 5 and
                all(_TYPE(v) is bool for v in terminal[key]), 'ELF raw token flag shape differs')
        tokens = terminal['known_fd_tokens']
        schema.need(_TYPE(tokens) is tuple and len(tokens) == 5 and tokens[:4] == (None,) * 4 and
            _TYPE(tokens[4]) is int and tokens[4] >= 0 and
            terminal['pending_acquisitions'] == (False,) * 5 and terminal['unknown_acquisition'] == (False,) * 5 and
            terminal['close_attempted'] == terminal['close_confirmed'] == (True, True, True, True, False),
            'ELF only reserved terminal file token may remain before encoding')
        handoff = terminal['parent_receipt']
        schema.exact(handoff, ('schema', 'status', 'executor_receipt', 'parent_fd_close_attempted',
                              'parent_fd_close_confirmed', 'authority_bindings', 'native_or_full_union_admission'))
        schema.need(handoff['schema'] == 'h25-gap41-parent-handoff-v2' and
            handoff['status'] == 'PURE_41_CASES_30_OBLIGATIONS_OBSERVED_SINK_CLOSED' and
            handoff['parent_fd_close_attempted'] is True and handoff['parent_fd_close_confirmed'] is True and
            handoff['native_or_full_union_admission'] is False and
            evidence.same_json(handoff['authority_bindings'], expected['authority_bindings']), 'ELF parent/source handoff differs')
        result = handoff['executor_receipt']
        schema.exact(result, ('schema', 'status', 'mode', 'cases', 'calls', 'returns', 'exact_rejects',
            'fixture_constructions', 'full_input_inverses', 'entry_counts', 'pure_obligations_observed', 'all202_complete',
            'compound_runtime_complete', 'native_authority', 'full_finite_union_complete', 'performance_gain_claimed',
            'raw_pins', 'sink_close', 'sink_receipt', 'model_only', 'failure_owner_records'))
        schema.need(result['schema'] == 'h25-gap41-observations-v1' and result['status'] == handoff['status'] and
            result['mode'] == state['mode'] and all(_TYPE(result[k]) is int and result[k] == v for k, v in
                (('cases', 41), ('calls', 66), ('returns', 31), ('exact_rejects', 35), ('fixture_constructions', 76),
                 ('full_input_inverses', 35), ('pure_obligations_observed', 30), ('failure_owner_records', 0))) and
            all(result[k] is False for k in ('all202_complete', 'compound_runtime_complete', 'native_authority',
                'full_finite_union_complete', 'performance_gain_claimed', 'model_only')),
            'ELF complete literal cases/calls/fixtures or limited scope differs')
        schema.exact(result['entry_counts'], ELF_ENTRIES)
        schema.need(evidence.same_json(result['entry_counts'], expected['entry_counts']), 'ELF original entry census differs')
        close = result['sink_close']
        schema.exact(close, ('schema', 'directory_close_attempted', 'directory_closed', 'close_error_present', 'evidence_incomplete'))
        schema.need(_typed_equal_v3(close, {'schema': 'h25-gap-directory-close-v2', 'directory_close_attempted': True,
            'directory_closed': True, 'close_error_present': False, 'evidence_incomplete': False}), 'ELF sink close incomplete')
        sink = result['sink_receipt']
        schema.exact(sink, ('schema', 'model_only', 'directory_identity', 'attempted_files', 'reserved_bytes',
            'write_bytes_returned', 'raw_write_bytes_complete', 'files', 'file_close_attempts',
            'file_close_confirmations', 'directory_close_attempted', 'directory_closed',
            'directory_close_error_present', 'owner_error_records', 'quarantined', 'evidence_incomplete'))
        _integer_fields_v3(sink, ('attempted_files', 'reserved_bytes', 'write_bytes_returned',
            'raw_write_bytes_complete', 'file_close_attempts', 'file_close_confirmations', 'owner_error_records'))
        schema.need(_TYPE(sink) is dict and sink['schema'] == 'h25-gap-durable-sink-receipt-v2' and
                    sink['model_only'] is False and sink['quarantined'] is False and sink['evidence_incomplete'] is False and
                    sink['owner_error_records'] == 0, 'ELF sink raw custody incomplete')
        schema.need(sink['directory_close_attempted'] is True and sink['directory_closed'] is True and
            sink['directory_close_error_present'] is False, 'ELF sink directory custody remains open')
        files = sink['files']
        schema.need(_TYPE(files) is tuple and _LEN(files) == 276 and
            [x['kind'] for x in files] == expected['record_kinds'] and
            _TYPE(result['raw_pins']) is tuple and result['raw_pins'] == files[:-1], 'ELF exact complete record census differs')
        total = 0
        for index, file in enumerate(files):
            schema.exact(file, ('index', 'kind', 'filename', 'intended_bytes', 'complete', 'readback_complete',
                               'file_close_confirmed', 'sha256', 'write_bytes_returned'))
            _integer_fields_v3(file, ('index', 'intended_bytes', 'write_bytes_returned'))
            schema.need(_TYPE(file['index']) is int and file['index'] == index and
                file['filename'] == '%04d-%s.typed' % (index, file['kind']) and file['complete'] is True and
                file['readback_complete'] is True and file['file_close_confirmed'] is True and
                file['write_bytes_returned'] == file['intended_bytes'], 'ELF raw record completed custody differs')
            pin = copying.inspect(row['output'] + '/gap-evidence-v1/' + file['filename'], error_owner=state['errors'])
            schema.need(pin['bytes'] == file['intended_bytes'] and pin['sha256'] == file['sha256'], 'ELF actual durable raw bytes differ')
            copying.verify(pin, error_owner=state['errors'])
            actual[file['filename']] = (pin, None)
            total += pin['bytes']
        schema.need(total <= 469762048 and sink['attempted_files'] == sink['file_close_attempts'] ==
            sink['file_close_confirmations'] == 276 and sink['raw_write_bytes_complete'] == total and
            sink['reserved_bytes'] == total and sink['write_bytes_returned'] == total, 'ELF full record byte/close bill differs')
        for pin, raw in actual.values():
            copying.verify(pin, error_owner=state['errors'])
        owned._accepted(state, run)
        return {'schema': 'h25-owned-gap41-observation-v2', 'mode': state['mode'], 'action_id': row['action_id'],
            'generation': row['generation'], 'terminal': run['terminal'], 'launch': run['launch'],
            'raw_pins': tuple(pin for pin, unused in actual.values()), 'cases': 41, 'calls': 66, 'fixtures': 76,
            'terminal_native': final, 'native24_or_full202_admission': False, 'saved_PASS': False}
    except BaseException as error:
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['unknown_owner']['quarantine'][0] = True
        state['phase'] = 'STOP'
        if run is not None:
            run['primary'][0] = error
        raise


def take_component_control_observation(owner, joined):
    """Receive the actual implemented unit protocol; never complete a family.

    The real source-fixed component root calls main() after its admitted
    bootstrap. The independent validator authenticates protocol shape only.
    Original owned terminal, current source, configured case identity and all
    named full byte artifacts are checked here. Missing unit bodies remain a
    complete-finite blocker in the orchestrator.
    """
    state = owned._state(owner)
    run = None
    try:
        schema.exact(CONTROL_EXECUTORS_CONFIGURATION, ('source_contract', 'units'))
        schema.blob(CONTROL_EXECUTORS_CONFIGURATION['source_contract'], schema.RECORD_BYTES)
        copying.verify(CONTROL_EXECUTORS_CONFIGURATION['source_contract'], error_owner=state['errors'])
        state, run = owned._joined(owner, joined)
        expected = run['plan']['evidence_plan']
        schema.exact(expected, ('schema', 'family', 'unit_id', 'source', 'validator_source', 'raw_artifacts',
            'expected_context', 'event_contract', 'source_contract_sha256'))
        schema.need(expected['schema'] == 'h25-component-unit-evidence-plan-v2' and
            expected['source_contract_sha256'] == CONTROL_EXECUTORS_CONFIGURATION['source_contract']['sha256'] and
            evidence.same_json(expected, CONTROL_EXECUTORS_CONFIGURATION['units'][expected['unit_id']]),
            'source-fixed implemented unit contract absent')
        for key in ('source', 'validator_source'):
            schema.blob(expected[key]); copying.verify(expected[key], error_owner=state['errors'])
        schema.need(expected['source']['sha256'] == run['plan']['driver_sha256'] and
            component_wire.__file__ == expected['validator_source']['path'], 'actual unit/validator source differs')
        run['actual_raw'] = {}
        actual = run['actual_raw']
        schema.need(_TYPE(expected['raw_artifacts']) is list and len(expected['raw_artifacts']) <= 256,
                    'bounded complete unit byte inventory required')
        for declaration in expected['raw_artifacts']:
            schema.exact(declaration, ('name', 'path', 'maximum_bytes'))
            schema.label(declaration['name']); schema.path(declaration['path'])
            schema.integer(declaration['maximum_bytes'], 0, schema.FILE_BYTES)
            schema.need(declaration['name'] not in actual and declaration['name'] not in ('stdout', 'stderr'),
                        'unit raw artifact name repeated')
            actual[declaration['name']] = _read(state, declaration['path'], declaration['maximum_bytes'])
        for stream in ('stdout', 'stderr'):
            actual[stream] = _read(state, run['plan']['evidence_directory'] + '/' + stream + '.raw', schema.LOG_BYTES)
        schema.need(actual['stderr'][1] == b'', 'component unit child stderr differs')
        observed = component_wire.validate_protocol(actual['stdout'][1], expected['unit_id'], state['mode'])
        run['actual_protocol'] = observed
        schema.need(observed['wire_protocol_complete'] is True and observed['protocol_is_case_PASS'] is False and
            observed['family_completion'] is False and observed['complete_finite_union'] is False and
            observed['stdout_sha256'] == actual['stdout'][0]['sha256'], 'unit wire scope differs')
        schema.need(evidence.same_json(observed['events'][0]['decoded'], expected['expected_context']),
                    'actual component context differs from independent configuration')
        actual_contract = [{'ordinal': event['ordinal'], 'kind': event['kind'], 'target': event['target'],
            'raw_ordinal': event['payload']['raw_ordinal'] if event['kind'] == 'ORACLE' else None}
            for event in observed['events']]
        schema.need(evidence.same_json(actual_contract, expected['event_contract']),
                    'source-derived unit raw/oracle sequence differs')
        byte_images = {(pin['bytes'], pin['sha256']) for name, (pin, raw) in actual.items() if name not in ('stdout', 'stderr')}
        _component_bytes(observed['events'], byte_images, [0])
        for pin, raw in actual.values():
            copying.verify(pin, error_owner=state['errors'])
        owned._accepted(state, run)
        return {'schema': 'h25-owned-component-unit-observation-v2', 'family': expected['family'],
            'unit_id': expected['unit_id'], 'mode': state['mode'], 'terminal': run['terminal'],
            'raw_pins': tuple(pin for pin, unused in actual.values()), 'protocol': observed,
            'family_completion': False, 'complete_finite_union': False, 'saved_PASS': False}
    except BaseException as error:
        if state['unknown_owner']['primary'][0] is None:
            state['unknown_owner']['primary'][0] = error
        state['unknown_owner']['quarantine'][0] = True
        state['phase'] = 'STOP'
        if run is not None:
            run['primary'][0] = error
        raise


def _component_bytes(value, actual_images, budget, depth=0):
    """Digest observations cannot replace the separately retained complete bytes."""
    budget[0] += 1
    schema.need(budget[0] <= 200000 and depth <= 64, 'component complete byte traversal bound')
    if _TYPE(value) is dict:
        if 'full_bytes_required_separately' in value:
            schema.need(value['full_bytes_required_separately'] is True and
                (value['byte_observation_length'], value['byte_observation_sha256']) in actual_images,
                'component full native byte artifact absent')
        for item in value.values():
            _component_bytes(item, actual_images, budget, depth + 1)
    elif _TYPE(value) in (list, tuple):
        for item in value:
            _component_bytes(item, actual_images, budget, depth + 1)


def _early_codec_decode(raw, limit=_early_codec_MAX_ENCODED):
    """Portable bounded readback of .typed evidence; no target modules involved."""
    if type(raw) is not bytes or type(limit) is not int or not 1 <= limit <= 16 * 1024 * 1024 or len(raw) > limit:
        raise RuntimeError('typed decode input bound')
    cursor, nodes = 0, 0

    def number(terminal):
        nonlocal cursor
        start = cursor
        while cursor < len(raw) and raw[cursor] != terminal:
            if cursor - start > 40:
                raise RuntimeError('typed decode number bound')
            cursor += 1
        if cursor == len(raw):
            raise RuntimeError('typed decode incomplete number')
        value = raw[start:cursor]
        cursor += 1
        if not value or any(x < 48 or x > 57 for x in value) or (len(value) > 1 and value[0] == 48):
            raise RuntimeError('typed decode noncanonical count')
        return int(value)

    def item(depth):
        nonlocal cursor, nodes
        nodes += 1
        if depth > _early_codec_MAX_DEPTH or nodes > _early_codec_MAX_NODES or cursor >= len(raw):
            raise RuntimeError('typed decode shape limit')
        tag = raw[cursor]
        cursor += 1
        if tag == 110:
            return None
        if tag == 121:
            return True
        if tag == 122:
            return False
        if tag == 105:
            negative = cursor < len(raw) and raw[cursor] == 45
            if negative:
                cursor += 1
            value = number(59)
            if int.bit_length(value) > _early_codec_MAX_INTEGER_BITS or (negative and value == 0):
                raise RuntimeError('typed decode integer bound')
            return -value if negative else value
        if tag == 115 or tag == 98:
            size = number(58)
            if size > 4 * _early_codec_MAX_STRING_CHARS or cursor + size > len(raw):
                raise RuntimeError('typed decode string size')
            value = raw[cursor:cursor + size]
            cursor += size
            if tag == 98:
                if size > _early_codec_MAX_BYTES:
                    raise RuntimeError('typed decode bytes bound')
                return value
            value = value.decode('utf-8')
            if len(value) > _early_codec_MAX_STRING_CHARS:
                raise RuntimeError('typed decode characters bound')
            return value
        if tag == 100 or tag == 116 or tag == 108:
            size = number(58)
            if size > _early_codec_MAX_CONTAINER:
                raise RuntimeError('typed decode collection size')
            if tag == 100:
                output, previous = {}, None
                for _ in range(size):
                    key = item(depth + 1)
                    if type(key) is not str or (previous is not None and key <= previous):
                        raise RuntimeError('typed decode dictionary ordering')
                    previous = key
                    output[key] = item(depth + 1)
                return output
            output = [item(depth + 1) for _ in range(size)]
            return tuple(output) if tag == 116 else output
        raise RuntimeError('typed decode unknown tag')

    result = item(0)
    if cursor != len(raw):
        raise RuntimeError('typed decode trailing data')
    return result
