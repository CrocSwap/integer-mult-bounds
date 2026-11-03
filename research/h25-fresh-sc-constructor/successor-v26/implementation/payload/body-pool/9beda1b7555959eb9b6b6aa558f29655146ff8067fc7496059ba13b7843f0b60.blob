"""Two additive models for the exact v5 close closure; no OS cleanup claim.

Both models call the same source-owned constructor used by the real factory,
with an explicit Python fake in the native-close slot. Neither model invokes
make_group_sink, an OS operation, a guard, compiler, parser or native kernel.
Authoring this module did not execute its bodies.
"""
import group_evidence_v5 as evidence
from receipt_contract_v1 import need, record, finish, validate

SCHEMA = 'h25-field-sink-close-model-control-receipt-v5'
CASE_IDS = ('model-sink-close-success-repeat', 'model-sink-close-raises-repeat')
NORMAL_CASE_COUNT = 2
OPTIMIZED_CASE_COUNT = 2


class ModelCloseFault(Exception):
    pass


def expectations():
    return {
        'model-sink-close-success-repeat': {
            'first_raised': False, 'first_exception_is_original': False,
            'first_return_error_is_none': True, 'repeat_error_is_original': False,
            'repeat_error_is_none': True, 'all_returned_summaries_equal': True,
            'directory_closed': True, 'directory_close_attempted': True,
            'directory_close_outcome': 'CONFIRMED', 'directory_close_error_present': False,
            'model_close_calls': 1, 'model_descriptor_arguments': [73],
            'holder_consumed_before_call': [True], 'holder_consumed_after_calls': True,
            'repeated_calls': 2, 'real_os_close_calls': 0},
        'model-sink-close-raises-repeat': {
            'first_raised': True, 'first_exception_is_original': True,
            'first_return_error_is_none': False, 'repeat_error_is_original': True,
            'repeat_error_is_none': False, 'all_returned_summaries_equal': True,
            'directory_closed': False, 'directory_close_attempted': True,
            'directory_close_outcome': 'UNCONFIRMED_AFTER_EXCEPTION', 'directory_close_error_present': True,
            'model_close_calls': 1, 'model_descriptor_arguments': [73],
            'holder_consumed_before_call': [True], 'holder_consumed_after_calls': True,
            'repeated_calls': 2, 'real_os_close_calls': 0}}


def run_close_model_controls(mode):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'close model exact mode')
    rows, expected = [], expectations()
    for case_id in CASE_IDS:
        holder, arguments, consumed = [73], [], []
        marker = ModelCloseFault('model-close-failed-original-object')
        should_raise = case_id == 'model-sink-close-raises-repeat'
        def fake_close(fd):
            arguments.append(fd)
            consumed.append(holder[0] is None)
            need(type(fd) is int and fd == 73, 'close model exact descriptor')
            if should_raise:
                raise marker
        state = {'index': 1, 'raw_pins': [('model', {'file': 'MODEL-ONLY', 'bytes': 7})],
                 'validation_pins': [], 'stop_pin': None, 'reserved_bytes': 7}
        closer = evidence._make_close_sink(holder, fake_close, state, evidence.SCHEMA, 9)
        first, first_error = None, None
        try:
            first = closer()
        except BaseException as failure:
            first_error = failure
        second, third = closer(), closer()
        need(type(second) is tuple and len(second) == 2 and
             type(third) is tuple and len(third) == 2, 'close model repeated exact tuple')
        summary, repeated_error = second
        need(type(summary) is dict and set(summary) == {'schema', 'completed_groups', 'expected_groups',
             'raw_pins', 'validation_pins', 'stop_pin', 'reserved_bytes', 'directory_closed',
             'directory_close_attempted', 'directory_close_outcome', 'directory_close_error_present'},
             'close model summary exact shape')
        need(summary['schema'] == evidence.SCHEMA and summary['completed_groups'] == 1 and
             summary['expected_groups'] == 9 and summary['raw_pins'] == [['model', {'file': 'MODEL-ONLY', 'bytes': 7}]] and
             summary['validation_pins'] == [] and summary['stop_pin'] is None and summary['reserved_bytes'] == 7,
             'close model original evidence survives close outcome')
        if first_error is None:
            need(type(first) is tuple and len(first) == 2, 'close model successful first tuple')
        observed = {
            'first_raised': first_error is not None,
            'first_exception_is_original': first_error is marker,
            'first_return_error_is_none': first is not None and first[1] is None,
            'repeat_error_is_original': repeated_error is marker and third[1] is marker,
            'repeat_error_is_none': repeated_error is None and third[1] is None,
            'all_returned_summaries_equal': summary == third[0] and (first is None or first[0] == summary),
            'directory_closed': summary['directory_closed'],
            'directory_close_attempted': summary['directory_close_attempted'],
            'directory_close_outcome': summary['directory_close_outcome'],
            'directory_close_error_present': summary['directory_close_error_present'],
            'model_close_calls': len(arguments), 'model_descriptor_arguments': arguments,
            'holder_consumed_before_call': consumed, 'holder_consumed_after_calls': holder[0] is None,
            'repeated_calls': 2, 'real_os_close_calls': 0}
        rows.append(record(case_id, observed, expected[case_id], {
            'proof_class': 'MODEL_BRANCH_ONLY', 'source_constructor': 'group_evidence_v5._make_close_sink',
            'native_close_replaced_by_explicit_python_model': True,
            'actual_os_close_qualified': False, 'factory_executed': False}))
    inner = finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
    result = {'schema': SCHEMA, 'proof_class': 'MODEL_BRANCH_ONLY', 'runtime_qualified': False,
              'actual_os_close_qualified': False, 'actual_native_calls': 0,
              'source_constructor': 'group_evidence_v5._make_close_sink', 'observations': inner}
    return validate_model_receipt(result, mode)


def validate_model_receipt(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'proof_class', 'runtime_qualified',
         'actual_os_close_qualified', 'actual_native_calls', 'source_constructor', 'observations'},
         'close model exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['proof_class'] == 'MODEL_BRANCH_ONLY' and
         receipt['source_constructor'] == 'group_evidence_v5._make_close_sink', 'close model source/provenance')
    need(receipt['runtime_qualified'] is False and receipt['actual_os_close_qualified'] is False and
         type(receipt['actual_native_calls']) is int and receipt['actual_native_calls'] == 0,
         'close model cannot qualify actual cleanup')
    validate(receipt['observations'], CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT,
             expectations(), mode)
    return receipt
