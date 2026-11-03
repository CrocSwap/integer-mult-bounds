"""Bounded pure-predicate entry; no C/kernel/process history claim.

Parent may source-admit this route separately from run_all. It imports only
fixture/receipt/pure-control modules. A run remains a control invocation and
requires exact source/stage/command/resource admission before execution.
"""
import elf_controls_v1 as elf
import provider_controls_v1 as providers
from receipt_contract_v1 import need, validate

SCHEMA = 'h25-pure-elf-provider-control-observations-v1'
NORMAL_CASE_COUNT = 91
OPTIMIZED_CASE_COUNT = 91


def run_pure(elf_module, mode):
    need(type(mode) is str and mode in ('normal', 'optimized'), 'pure control mode')
    result = {'schema': SCHEMA, 'status': 'PURE_PREDICATE_OBSERVATIONS_ONLY', 'mode': mode,
              'elf': elf.run_static_elf_controls(elf_module.admit_service_elf, elf_module.ELFAdmissionError, mode),
              'providers': providers.run_provider_controls(elf_module.admit_service_elf,
                  elf_module.admit_loaded_maps, elf_module.provider_requests,
                  elf_module.admit_runtime_provider_map, elf_module.ELFAdmissionError, mode),
              'declared_observation_count': NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT,
              'actual_target_elf_admitted': False, 'kernel_capability_qualified': False,
              'full_163_obligations_covered': False, 'full_finite_union_qualified': False}
    return validate_pure(result, mode)


def validate_pure(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'status', 'mode', 'elf', 'providers',
      'declared_observation_count', 'actual_target_elf_admitted', 'kernel_capability_qualified',
      'full_163_obligations_covered', 'full_finite_union_qualified'}, 'pure exact receipt keys')
    need(receipt['schema'] == SCHEMA and receipt['status'] == 'PURE_PREDICATE_OBSERVATIONS_ONLY' and receipt['mode'] == mode,
         'pure receipt status/mode')
    for module, key in ((elf, 'elf'), (providers, 'providers')):
        validate(receipt[key], module.CASE_IDS,
                 module.NORMAL_CASE_COUNT if mode == 'normal' else module.OPTIMIZED_CASE_COUNT,
                 module.expectations(), mode)
    need(type(receipt['declared_observation_count']) is int and receipt['declared_observation_count'] ==
         (NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT) ==
         receipt['elf']['case_count'] + receipt['providers']['case_count'], 'pure literal observation count')
    for key in ('actual_target_elf_admitted', 'kernel_capability_qualified',
                'full_163_obligations_covered', 'full_finite_union_qualified'):
        need(receipt[key] is False, 'pure receipt exceeds evidence boundary')
    return receipt
