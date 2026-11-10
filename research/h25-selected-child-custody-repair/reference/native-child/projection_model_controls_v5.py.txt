"""Source-authored callback models for the actual v5 projection functions.

The authenticated aggregate supplies its actual error projector/carrier and
source-owned evidence module. Fixtures are ordinary Python model objects with
observable callbacks. These models grant no kernel, OS, full-writer or complete
union qualification. Authoring did not import or execute any target body.
"""
from types import FunctionType, ModuleType
from receipt_contract_v1 import need, record, finish, validate

SCHEMA = 'h25-field-projection-model-control-receipt-v5'
JSON_CASE_IDS = (
    'model-json-native-literal', 'model-json-foreign-metaclass',
    'model-json-list-subclass-metaclass', 'model-json-nested-foreign',
    'model-json-foreign-dict-key')
EXCEPTION_CASE_IDS = (
    'model-error-native-str', 'model-error-native-foreign-arg',
    'model-error-native-multiple-args', 'model-error-foreign-exception-callbacks',
    'model-error-native-str-subclass-arg', 'model-error-native-truncated-str')
CASE_IDS = JSON_CASE_IDS + EXCEPTION_CASE_IDS
NORMAL_CASE_COUNT = 11
OPTIMIZED_CASE_COUNT = 11


class ModelCallbackFault(Exception):
    pass


def _expected_projection(label, type_provenance, message, message_provenance, truncated=False):
    return {'schema': 'h25-safe-error-projection-v5', 'type': label,
            'type_provenance': type_provenance, 'message': message,
            'message_provenance': message_provenance, 'message_truncated': truncated,
            'opaque_exception_retained_separately': True}


def expectations():
    result = {}
    for case_id in JSON_CASE_IDS:
        positive = case_id == 'model-json-native-literal'
        rejection = None if positive else ('group evidence JSON key must be exact str'
            if case_id == 'model-json-foreign-dict-key' else 'group evidence JSON exact value/collection bound')
        result[case_id] = {'accepted': positive, 'payload_matches_literal': positive,
            'error_is_exact_runtimeerror': not positive, 'rejection_message': rejection,
            'callback_count': 0, 'callbacks': [], 'real_os_or_private_field_operations': 0}
    projections = {
        'model-error-native-str': _expected_projection('RuntimeError', 'EXACT_NATIVE_TYPE',
            'native-model-message', 'EXACT_STR_ARGUMENT'),
        'model-error-native-foreign-arg': _expected_projection('RuntimeError', 'EXACT_NATIVE_TYPE',
            None, 'OMITTED_NON_SINGLE_STR_ARGUMENTS'),
        'model-error-native-multiple-args': _expected_projection('RuntimeError', 'EXACT_NATIVE_TYPE',
            None, 'OMITTED_NON_SINGLE_STR_ARGUMENTS'),
        'model-error-foreign-exception-callbacks': _expected_projection('OPAQUE_FOREIGN_EXCEPTION',
            'OPAQUE_FOREIGN_TYPE', None, 'OMITTED_FOREIGN_TYPE'),
        'model-error-native-str-subclass-arg': _expected_projection('RuntimeError', 'EXACT_NATIVE_TYPE',
            None, 'OMITTED_NON_SINGLE_STR_ARGUMENTS'),
        'model-error-native-truncated-str': _expected_projection('RuntimeError', 'EXACT_NATIVE_TYPE',
            'q' * 4096, 'EXACT_STR_ARGUMENT', True)}
    for case_id in EXCEPTION_CASE_IDS:
        result[case_id] = {'projection': projections[case_id], 'callback_count': 0, 'callbacks': [],
            'carrier_is_original': True, 'primary_is_original': True, 'secondary_is_original': True,
            'teardown_is_original': True, 'cause_is_original': True, 'real_os_or_private_field_operations': 0}
    return result


def _fixtures(events):
    def callback(name):
        events.append(name)
        raise ModelCallbackFault('model forbidden callback')
    class CallbackMeta(type):
        def __eq__(cls, other):
            events.append('metaclass-equality')
            return True
        def __getattribute__(cls, name):
            if name == '__name__':
                return callback('metaclass-name')
            return type.__getattribute__(cls, name)
    class Foreign(metaclass=CallbackMeta):
        __hash__ = object.__hash__  # fixture dictionary insertion needs no custom callback
        def __eq__(self, other): return callback('foreign-equality')
        def __len__(self): return callback('foreign-length')
        def __iter__(self): return callback('foreign-iteration')
        def __getitem__(self, key): return callback('foreign-getitem')
        def __str__(self): return callback('foreign-str')
        def __repr__(self): return callback('foreign-repr')
    class ForeignList(list, metaclass=CallbackMeta):
        def __len__(self): return callback('list-subclass-length')
        def __iter__(self): return callback('list-subclass-iteration')
        def __getitem__(self, key): return callback('list-subclass-getitem')
    class ForeignString(str, metaclass=CallbackMeta):
        def __str__(self): return callback('str-subclass-str')
        def __repr__(self): return callback('str-subclass-repr')
        def __len__(self): return callback('str-subclass-length')
        def __getitem__(self, key): return callback('str-subclass-getitem')
    class ForeignError(Exception, metaclass=CallbackMeta):
        def __getattribute__(self, name): return callback('exception-getattribute')
        def __str__(self): return callback('exception-str')
        def __repr__(self): return callback('exception-repr')
        def __eq__(self, other): return callback('exception-equality')
        def __hash__(self): return callback('exception-hash')
    return Foreign, ForeignList, ForeignString, ForeignError


def run_projection_model_controls(evidence_module, error_projector, error_carrier, mode):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'projection model exact mode')
    need(type(evidence_module) is ModuleType and type(error_projector) is FunctionType and
         type(error_carrier) is type, 'projection model source-owned handles required')
    rows, expected = [], expectations()
    for case_id in CASE_IDS:
        events = []
        Foreign, ForeignList, ForeignString, ForeignError = _fixtures(events)
        if case_id in JSON_CASE_IDS:  # case_id is a literal exact str from CASE_IDS
            if case_id == 'model-json-native-literal':
                value = {'b': [True, None, 17, (False,)], 'a': '\n\u2603\U0001f600'}
            elif case_id == 'model-json-foreign-metaclass': value = Foreign()
            elif case_id == 'model-json-list-subclass-metaclass': value = ForeignList([1])
            elif case_id == 'model-json-nested-foreign': value = [Foreign()]
            else: value = {Foreign(): 'literal-native-value'}
            need(events == [], 'projection model fixture construction unexpectedly called back')
            raw, failure = None, None
            try:
                raw = evidence_module._encode(value, 1048576)
            except BaseException as caught:
                failure = caught
            exact_error = type(failure) is RuntimeError
            rejection_message = None
            if exact_error:
                args = BaseException.__dict__['args'].__get__(failure, BaseException)
                need(type(args) is tuple and len(args) == 1 and type(args[0]) is str,
                     'projection model exact native rejection text')
                rejection_message = args[0]
            observed = {'accepted': failure is None,
                'payload_matches_literal': type(raw) is bytes and raw == b'{"a":"\\n\\u2603\\ud83d\\ude00","b":[true,null,17,[false]]}\n',
                'error_is_exact_runtimeerror': exact_error, 'rejection_message': rejection_message,
                'callback_count': len(events), 'callbacks': list(events), 'real_os_or_private_field_operations': 0}
        else:
            if case_id == 'model-error-native-str': original = RuntimeError('native-model-message')
            elif case_id == 'model-error-native-foreign-arg': original = RuntimeError(Foreign())
            elif case_id == 'model-error-native-multiple-args': original = RuntimeError(Foreign(), 'native-tail')
            elif case_id == 'model-error-foreign-exception-callbacks': original = ForeignError('opaque-model-error')
            elif case_id == 'model-error-native-str-subclass-arg': original = RuntimeError(ForeignString('foreign-subclass'))
            else: original = RuntimeError('q' * 5000)
            need(events == [], 'projection model exception fixture construction unexpectedly called back')
            projection = error_projector(original)
            failure_record = {'group': 'projection-model', 'return_state': 'NOT_RETURNED',
                'primary_error': projection, 'next_group_started': False}
            carrier = error_carrier(failure_record, original, original, teardown=original)
            caught_carrier = None
            try:
                raise carrier from original
            except BaseException as caught:
                caught_carrier = caught
            observed = {'projection': projection, 'callback_count': len(events), 'callbacks': list(events),
                'carrier_is_original': caught_carrier is carrier,
                'primary_is_original': caught_carrier.primary_exception is original,
                'secondary_is_original': caught_carrier.secondary_capture_exception is original,
                'teardown_is_original': caught_carrier.teardown_exception is original,
                'cause_is_original': caught_carrier.__cause__ is original, 'real_os_or_private_field_operations': 0}
        rows.append(record(case_id, observed, expected[case_id], {
            'proof_class': 'MODEL_BRANCH_ONLY', 'actual_os_or_sink_io_qualified': False,
            'source_functions': ['group_evidence_v5._encode', 'run_controls_v5._error_record',
                                 'run_controls_v5.GroupControlError'],
            'fixture_setup_callbacks': 0, 'source_handles_require_caller_admission': True}))
    inner = finish(rows, CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT, expected, mode)
    result = {'schema': SCHEMA, 'proof_class': 'MODEL_BRANCH_ONLY', 'runtime_qualified': False,
        'actual_os_or_sink_io_qualified': False, 'actual_os_or_private_field_operations': 0,
        'safe_json_model_count': 5, 'safe_error_model_count': 6,
        'source_handles_require_caller_admission': True, 'observations': inner}
    return validate_model_receipt(result, mode)


def validate_model_receipt(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'proof_class', 'runtime_qualified',
        'actual_os_or_sink_io_qualified', 'actual_os_or_private_field_operations', 'safe_json_model_count',
        'safe_error_model_count', 'source_handles_require_caller_admission', 'observations'},
        'projection model exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['proof_class'] == 'MODEL_BRANCH_ONLY' and
        receipt['source_handles_require_caller_admission'] is True, 'projection model source provenance')
    need(receipt['runtime_qualified'] is False and receipt['actual_os_or_sink_io_qualified'] is False and
         type(receipt['actual_os_or_private_field_operations']) is int and receipt['actual_os_or_private_field_operations'] == 0,
         'projection model cannot qualify actual writer or native operations')
    need(type(receipt['safe_json_model_count']) is int and receipt['safe_json_model_count'] == 5 and
         type(receipt['safe_error_model_count']) is int and receipt['safe_error_model_count'] == 6,
         'projection model exact independent group census')
    validate(receipt['observations'], CASE_IDS, NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT,
             expectations(), mode)
    return receipt
