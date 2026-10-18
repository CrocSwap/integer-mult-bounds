#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only exact finite replay; --write-result explicitly regenerates the receipt."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def local(name):
    spec = importlib.util.spec_from_file_location('p104_reuse_' + name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


sources, compose, price = (local(name) for name in ('sources', 'compose', 'price'))


def reject(action, expected):
    try:
        action()
    except ValueError as error:
        sources.require(expected in str(error), 'wrong rejection reason: ' + str(error))
        return str(error)
    raise ValueError('invalid control accepted: ' + expected)


def verify():
    with sources.predecessor() as directory:
        C = sources.module('coalesced', directory / 'coalesced.py')
        base = C.construct()
        built = compose.construct(C, base)
        print('PASS full 735-column identity, chronology and retained event correspondence', flush=True)
        hosted = sources.module('hosting', directory / 'hosting.py').verify(built['report'])
        prices = price.verify(C, sources.module('budget', directory / 'budget.py'), built, base, hosted)
        controls = {}
        for fault, expected in (
            ('missing_reused_contact', 'full 735-column endpoint identity failed'),
            ('wrong_contact_coefficient', 'full 735-column endpoint identity failed'),
            ('retain_dirty_compensation', 'full 735-column endpoint identity failed'),
            ('ascending_private_contact', 'nonmonotone composed transport'),
        ):
            controls[fault] = reject(lambda fault=fault: compose.construct(C, base, fault), expected)
        stale = dict(base, scalar_operations=deepcopy(base['scalar_operations']))
        stale['scalar_operations'][90]['coefficient'] = '3'
        controls['stale_coalesced_event_binding'] = reject(
            lambda: compose.construct(C, stale), 'coalesced source event binding')

        omitted = dict(built, report=deepcopy(built['report']),
                       transport_edges=[e for e in built['transport_edges'] if e['register'] != compose.HELPER])
        del omitted['report']['candidate_public_profile']['9']
        del omitted['report']['combined_profile']['9']
        controls['omit_unused_helper_boundary_charge'] = reject(
            lambda: price.bind(C, omitted, base, hosted), 'complete public mass binding')
        bad_copy = dict(built, report=deepcopy(built['report']))
        bad_copy['report']['private_COPY_profile']['7'] -= 1
        controls['omit_private_copy_charge'] = reject(
            lambda: price.bind(C, bad_copy, base, hosted), 'private invoice occurrence binding')
        bad_width = dict(built, report=deepcopy(built['report']))
        bad_width['report']['complete_public_widths'][compose.HELPER] = 0
        controls['retire_helper_without_repricing_owner_widths'] = reject(
            lambda: sources.module('bad_hosting', directory / 'hosting.py').verify(bad_width['report']),
            'whole helper lifetimes')
        bad_hosted = dict(hosted, complete_public_widths_sha256='0' * 64)
        controls['stale_owner_width_binding'] = reject(
            lambda: price.bind(C, built, base, bad_hosted), 'owner invoice width binding')
        archive_pin, = json.loads((HERE / 'SOURCES.json').read_text())['archives']
        raw = (HERE / archive_pin['path']).read_bytes()
        controls['changed_predecessor_bytes'] = reject(
            lambda: sources.checked_bytes(raw + b'!', archive_pin['sha256'], archive_pin['path']),
            'source hash:')
        print('PASS complete cost/owner bill and ten semantic/source failure controls', flush=True)
        native = sources.module('native', directory / 'native_checks.py').verify(C.native_witness(built))
        sources.require(native['paid_profile'] == built['report']['combined_profile']
                        and native['native_rank_mass'] == 5894
                        and native['literal_transport_occurrences'] == len(built['transport_edges']),
                        'native invoice does not match the composed word')
        sources.require(native['private_path_gaussian_columns'] == 4096
                        and native['intrinsic_monomial_endpoint_adapters'] == 208
                        and native['wrong_global_phase_control_rejected'], 'native phase coverage')
        print('PASS literal native lowering, 208 adapters, 4096 Gaussian columns and phase rejection', flush=True)
        return dict(status='PASS_FINITE_COALESCED_PRIVATE_REUSE',
                    scope='Finite forward word and complete conditional invoice; no global/backward/precision/all-size supplier or new exponent.',
                    composition=built['report'], native=native, conditional_hosting=hosted,
                    pricing=prices, negative_controls=controls,
                    source_archive_sha256=archive_pin['sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = verify()
    path = HERE / 'RESULT.json'
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        sources.require(result == json.loads(path.read_text()), 'recorded result differs from replay')
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print(result['status'], 'receipt=' + digest)


if __name__ == '__main__':
    main()
