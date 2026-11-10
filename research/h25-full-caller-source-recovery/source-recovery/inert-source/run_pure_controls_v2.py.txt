"""Versioned, source-admitted synthetic predicate route; all execution gated.

The external harness should call run_initial then persist its bounded raw
return, call run_extended then persist its bounded raw return, and only then
call combine_groups/validate_pure. This exposes group progress and preserves
returns before outer validation; failed inner operations retain their original
exception/stderr through the external STOP envelope. No kernel/C import occurs.
"""
import run_pure_controls_v1 as initial
import elf_extended_controls_v2 as extension
from elf_literal_fixture_v2 import initial_v1_adapter
from receipt_contract_v1 import need

SCHEMA = 'h25-pure-elf-provider-control-observations-v2'
STATUS = 'PURE_PREDICATE_OBSERVATIONS_ONLY'
NORMAL_CASE_COUNT = 201
OPTIMIZED_CASE_COUNT = 201
INITIAL_CASE_COUNT = 91
EXTENDED_CASE_COUNT = 110
DECLARED_NEGATIVE_OBLIGATIONS = 202


def run_initial(elf_module, mode):
    return initial.run_pure(initial_v1_adapter(elf_module), mode)


def run_extended(elf_module, mode):
    return extension.run_extended(elf_module, mode)


def combine_groups(initial_receipt, extended_receipt, mode):
    receipt = {'schema': SCHEMA, 'status': STATUS, 'mode': mode,
        'initial': initial_receipt, 'extended': extended_receipt,
        'initial_observation_count': INITIAL_CASE_COUNT,
        'extended_observation_count': EXTENDED_CASE_COUNT,
        'observation_count': NORMAL_CASE_COUNT if mode == 'normal' else OPTIMIZED_CASE_COUNT,
        'declared_negative_obligations': DECLARED_NEGATIVE_OBLIGATIONS,
        'all_202_obligations_covered': False, 'original_163_obligations_preserved': True,
        'actual_target_elf_admitted': False, 'kernel_capability_qualified': False,
        'full_finite_union_qualified': False, 'source_model_or_native_calls_in_this_route': False}
    return validate_pure(receipt, mode)


def run_pure(elf_module, mode):
    initial_receipt = run_initial(elf_module, mode)
    extended_receipt = run_extended(elf_module, mode)
    return combine_groups(initial_receipt, extended_receipt, mode)


def validate_pure(receipt, mode):
    need(type(receipt) is dict and set(receipt) == {'schema', 'status', 'mode', 'initial', 'extended',
        'initial_observation_count', 'extended_observation_count', 'observation_count',
        'declared_negative_obligations', 'all_202_obligations_covered',
        'original_163_obligations_preserved', 'actual_target_elf_admitted',
        'kernel_capability_qualified', 'full_finite_union_qualified',
        'source_model_or_native_calls_in_this_route'}, 'pure v2 exact receipt keys')
    need(type(mode) is str and mode in ('normal', 'optimized') and receipt['mode'] == mode and
         receipt['schema'] == SCHEMA and receipt['status'] == STATUS, 'pure v2 status/mode')
    initial.validate_pure(receipt['initial'], mode)
    extension.validate_extended(receipt['extended'], mode)
    need(type(receipt['initial_observation_count']) is int and receipt['initial_observation_count'] == 91 and
         type(receipt['extended_observation_count']) is int and receipt['extended_observation_count'] == 110 and
         type(receipt['observation_count']) is int and receipt['observation_count'] == 201 and
         receipt['initial']['declared_observation_count'] == 91 and receipt['extended']['case_count'] == 110,
         'pure v2 independent literal counts')
    need(type(receipt['declared_negative_obligations']) is int and receipt['declared_negative_obligations'] == 202 and
         receipt['original_163_obligations_preserved'] is True, 'pure v2 obligation ledger')
    for name in ('all_202_obligations_covered', 'actual_target_elf_admitted',
                 'kernel_capability_qualified', 'full_finite_union_qualified',
                 'source_model_or_native_calls_in_this_route'):
        need(receipt[name] is False, 'pure v2 receipt exceeds its evidence scope')
    return receipt
