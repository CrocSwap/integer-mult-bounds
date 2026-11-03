"""Additive source control aggregator; no kernel/full qualification shortcut."""
from types import FunctionType, CellType
import native_field_controls_v1 as native
import transport_controls_v1 as transport
import collector_controls_v1 as collector
import elf_controls_v1 as elf
import provider_controls_v1 as providers
import loader_model_controls_v1 as models
from receipt_contract_v1 import need, validate

SCHEMA = 'h25-indexed-field-additive-controls-v1'
STATUS = 'SOURCE_CONTROL_OBSERVATIONS_COMPLETE_RUNTIME_GATE_OPEN'
NORMAL_NONMODEL_COUNT = 169
OPTIMIZED_NONMODEL_COUNT = 169
NORMAL_MODEL_COUNT = 33
OPTIMIZED_MODEL_COUNT = 33
MAX_CONTEXTS = 41  # native15 + transport14 + collector12; module cap64
GROUPS = ('native', 'transport', 'collector', 'elf', 'providers')
MODULES = (native, transport, collector, elf, providers)


def _admit_control_transport(control_transport):
    need(type(control_transport) is tuple and len(control_transport) == 2, 'control transport exact shape')
    functions, records = control_transport
    need(type(functions) is tuple and len(functions) == 3 and type(records) is tuple and len(records) == 3,
         'control transport function census')
    getters = tuple(FunctionType.__dict__[name].__get__ for name in native.FIELDS)
    cell_get = CellType.__dict__['cell_contents'].__get__
    for target, captured in zip(functions, records):
        need(type(captured) is tuple and len(captured) == 3 and target is captured[0] and
             type(target) is FunctionType and type(captured[1]) is tuple and len(captured[1]) == 7 and
             type(captured[2]) is tuple, 'control transport original target')
        for getter, expected in zip(getters, captured[1]):
            need(id(getter(target, FunctionType)) == id(expected), 'control transport original environment')
        need(captured[1][3] is None and captured[1][4] is None, 'control transport source defaults')
        for cell, expected in captured[2]:
            try: actual_id = id(cell_get(cell, CellType))
            except ValueError: raise RuntimeError('control transport original closure empty') from None
            need(actual_id == id(expected), 'control transport original closure')
    return functions


def run_all(field_control_transport, authority_source, authority_digest, root, capability,
            api, compile0, exec0, elf_module, mode):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'control exact mode')
    functions = _admit_control_transport(field_control_transport)
    original_new, original_transport, original_models = functions
    # Caller authenticates original Root functions before every later factory
    # call. No late module attribute can replace the actual captured targets.
    made = [0]
    def new_fixture():
        _admit_control_transport(field_control_transport)
        made[0] += 1
        need(made[0] <= MAX_CONTEXTS, 'aggregate native fixture bound')
        return original_new()
    def new_transport():
        _admit_control_transport(field_control_transport)
        made[0] += 1
        need(made[0] <= MAX_CONTEXTS, 'aggregate native fixture bound')
        return original_transport()
    receipts = {}
    receipts['native'] = native.run_native_field_controls(new_fixture, mode)
    receipts['transport'] = transport.run_transport_controls(new_transport, mode)
    receipts['collector'] = collector.run_collector_controls(new_transport, authority_source,
        authority_digest, root, capability, api, compile0, exec0, mode)
    receipts['elf'] = elf.run_static_elf_controls(elf_module.admit_service_elf, elf_module.ELFAdmissionError, mode)
    receipts['providers'] = providers.run_provider_controls(elf_module.admit_service_elf,
        elf_module.admit_loaded_maps, elf_module.provider_requests,
        elf_module.admit_runtime_provider_map, elf_module.ELFAdmissionError, mode)
    _admit_control_transport(field_control_transport)
    model = models.run_loader_model_controls(original_models(), mode)
    result = {'schema': SCHEMA, 'status': STATUS, 'mode': mode,
              'nonmodel_observed_count': sum(r['case_count'] for r in receipts.values()),
              'model_observed_count': model['observations']['case_count'],
              'native_fixture_contexts': made[0], 'groups': receipts, 'root_model': model,
              'kernel_capability_qualified': False, 'full_finite_union_qualified': False,
              'required_guarded_cases_status': 'REQUIRED_NOT_EXECUTED_BY_THIS_ENTRY'}
    return validate_all(result, mode)


def validate_all(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'status', 'mode',
      'nonmodel_observed_count', 'model_observed_count', 'native_fixture_contexts', 'groups',
      'root_model', 'kernel_capability_qualified', 'full_finite_union_qualified', 'required_guarded_cases_status'},
      'aggregate exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['status'] == STATUS and receipt['mode'] == mode,
         'aggregate status/mode')
    need(receipt['kernel_capability_qualified'] is False and receipt['full_finite_union_qualified'] is False and
         receipt['required_guarded_cases_status'] == 'REQUIRED_NOT_EXECUTED_BY_THIS_ENTRY',
         'source controls cannot substitute for guarded runtime qualification')
    need(type(receipt['groups']) is dict and tuple(receipt['groups']) == GROUPS, 'aggregate exact group order')
    for name, module in zip(GROUPS, MODULES):
        literal = module.NORMAL_CASE_COUNT if mode == 'normal' else module.OPTIMIZED_CASE_COUNT
        validate(receipt['groups'][name], module.CASE_IDS, literal, module.expectations(), mode)
    models.validate_model_receipt(receipt['root_model'], mode)
    nonmodel = NORMAL_NONMODEL_COUNT if mode == 'normal' else OPTIMIZED_NONMODEL_COUNT
    model = NORMAL_MODEL_COUNT if mode == 'normal' else OPTIMIZED_MODEL_COUNT
    need(type(receipt['nonmodel_observed_count']) is int and receipt['nonmodel_observed_count'] == nonmodel and
         type(receipt['model_observed_count']) is int and receipt['model_observed_count'] == model and
         receipt['root_model']['observations']['case_count'] == model,
         'aggregate literal counts')
    need(type(receipt['native_fixture_contexts']) is int and receipt['native_fixture_contexts'] == MAX_CONTEXTS,
         'aggregate actual context count')
    return receipt
