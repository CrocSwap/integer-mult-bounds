"""Bounded source-bound capacity proof checks and actual physical-cut controls."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit_sources import authenticate, need, opened
from inventory import build, canonical, controls, verify_record


def cold_controls():
    result = []
    for name in ('layout', 'trace', 'packet_engine', 'children'):
        need(name not in sys.modules, 'cold-control entry')
        with patch.dict(sys.modules, {name: ModuleType(name)}):
            try:
                with opened():
                    raise ValueError('warm alias reached physical cohort')
            except ValueError as error:
                need(str(error) == 'cold capacity-audit cohort', 'preloaded source rejected at entry')
                result.append(name)
            else:
                raise ValueError('preloaded alias accepted')
    return result


def run():
    inputs = authenticate()
    inventory = json.loads((HERE / 'INVENTORY.json').read_text())
    verify_record(inventory)
    static_controls = controls(inventory)
    aliases = cold_controls()
    with opened():
        from physical_checks import selected_source, successful_cuts, short_capacity, outside_resident_control
        binding, definition, identifier = selected_source()
        cold = successful_cuts(binding, definition, identifier, depth=2, warm_count=0)
        warm = successful_cuts(binding, definition, identifier, depth=2, warm_count=17)
        need(cold['restored_parent_labels'] != warm['restored_parent_labels'],
             'different warm slot identities were actually exercised')
        need(cold['controlled_output_sha256'] == warm['controlled_output_sha256'],
             'same controlled endpoint through different actual labels')
        short = [short_capacity(binding, definition, residue_capacity=64, index_capacity=26,
                                expected_bank='index'),
                 short_capacity(binding, definition, residue_capacity=14, index_capacity=64,
                                expected_bank='residue')]
        outsider = outside_resident_control(binding, definition)
    return dict(marker='PASS_RECURSIVE_PHYSICAL_CAPACITY_PREFIX', source_inputs=inputs,
                historical_dimension=64, maximum_rank=42, current_selected_admission=False,
                universal_envelope=inventory['envelope']['total'],
                inventory_controls=static_controls, rejected_preloaded_aliases=aliases,
                nested_cuts=[cold, warm], short_capacity=short, root_domain_control=outsider,
                no_new_kappa=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true', help='explicit author-only receipt creation')
    args = parser.parse_args()
    actual = run()
    receipt = HERE / 'RESULT.json'
    if args.emit:
        receipt.write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n')
    else:
        expected = json.loads(receipt.read_text())
        need(canonical(actual) == canonical(expected), 'complete typed physical-capacity receipt')
    print(json.dumps(actual, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
