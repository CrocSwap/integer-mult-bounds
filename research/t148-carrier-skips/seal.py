#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Seal only actual completed baseline and composition releases."""
import argparse
import json
from fractions import Fraction as Q
from pathlib import Path

import verify as v


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--composition', type=Path, required=True)
    args = parser.parse_args()
    baseline, work = args.baseline.resolve(), args.composition.resolve()
    old = v.read(baseline / 'RESULT.json')
    result = v.read(work / 'RESULT.json')
    v.need(old['status'] == 'PASS_T740_R1_COMPLETE_RELEASE', 'completed baseline gate')
    v.need(result['status'] == 'PASS_T148_CARRIER_SKIPS_COMPLETE_RELEASE', 'completed composition gate')
    arithmetic = v.calculate(include_owners=False)
    for key in ['kappa', 'complex_lower', 'previous', 'gain']:
        v.need(Q(result[key]) == arithmetic[key], 'actual exact result: ' + key)
    inner = work / 'run/candidate'
    admission = v.read(inner / 'RESULT.json')
    v.need(admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete original admission')
    v.need(admission['source_manifest_sha256'] == v.SOURCE_SHA and
           {int(k): n for k, n in admission['profile'].items()} == v.PROFILE, 'actual new-word composed source/profile')
    strict = inner / 'release/verify/strict'
    counts = dict(admission=len(v.read(strict / 'ADMISSION-CONTROLS.json')['rejected_controls']),
                  bit=len(v.read(strict / 'BIT-CONTROLS.json')['rejected_controls']),
                  controller=len(v.read(strict / 'global/audit/ASYNC-AUDIT.json')['mutations_rejected']),
                  independent_owner=len(v.read(strict / 'INDEPENDENT.json')['controls_rejected']),
                  geometry=len(v.read(inner / 'release/verify/GEOMETRY-CONTROLS.json')['rejected']))
    v.need(counts == dict(admission=139, bit=12, controller=25, independent_owner=8, geometry=6), 'every actual rejecting control')
    invoice = v.read(strict / 'global/audit/PREFIX-AND-INVOICE.json')
    v.need(invoice['physical'] == 133117 and invoice['private_zero_buffers'] == 91 and
           invoice['global_prefix_bits'] < invoice['charged_prefix_bits'] == 2048, 'full charged physical/prefix invoice')
    ledger_path = inner / 'package/outer/LEDGER.json'
    ledger = v.read(ledger_path)
    row = ledger['rows']['struct_boundary_radix_union']
    v.need(Q(row['kappa']['rational']) == arithmetic['kappa'] and len(row['strict_checks']) == 63 and
           all(Q(value['rational']) > 0 for value in row['strict_checks'].values()), 'all63 strict outer margins')
    v.need(len(ledger['rejecting_controls']['struct_boundary_radix_union']) == 17, 'all17 outer rejecting cases')
    hashes = {}
    for source, name, field in [
        (baseline / 'run/candidate/release/RELEASE-RECEIPT.json', 'BASELINE-RELEASE-RECEIPT.json', 'baseline_release_sha256'),
        (inner / 'release/RELEASE-RECEIPT.json', 'RELEASE-RECEIPT.json', 'release_sha256'),
        (ledger_path, 'OUTER-LEDGER.json', 'outer_ledger_sha256')]:
        raw = source.read_bytes()
        v.need(not any(marker in raw.lower() for marker in
               [b'/mnt/c/', b'c:\\users\\', b'c:/users/', b'/home/', b'/users/']), 'no machine paths in published receipt')
        (v.P / 'evidence' / name).write_bytes(raw)
        hashes[field] = v.sha(source)
    native = v.read(work / 'run/native/NATIVE-RECEIPT.json')
    v.need(native['fresh_current_provider_count'] == 2 and native['manifest_sha256'] == v.SOURCE_SHA,
           'both changed native providers fresh and source-bound')
    for tag in ['base', 'extra']:
        v.need(native['providers'][tag]['word_sha256'] == v.sha(v.P / ('vendor/WORD-' + tag + '.json.gz')),
               'exact freshly compiled provider word')
    claim = dict(status=result['status'], source_head=v.HEAD, source_manifest_sha256=v.SOURCE_SHA,
                 profile={str(r): n for r, n in v.PROFILE.items()}, replicas=148, calls=1332,
                 roles=543456, physical=133117, private_buffers=91,
                 **{key: str(arithmetic[key]) for key in ['kappa', 'complex_lower', 'previous', 'gain']})
    save(v.P / 'CLAIM.json', claim)
    evidence = dict(status=result['status'], baseline_complete_release=True, composition_complete_release=True,
                    controls=counts, fresh_current_native_providers=2,
                    retained_native_scope='Explicitly authenticated unchanged cache from the completed cold baseline.',
                    baseline_result_sha256=v.sha(baseline / 'RESULT.json'),
                    composition_result_sha256=v.sha(work / 'RESULT.json'),
                    admission_result_sha256=v.sha(inner / 'RESULT.json'),
                    native_receipt_sha256=v.sha(work / 'run/native/NATIVE-RECEIPT.json'),
                    outer_strict_rows=63, outer_rejecting_cases=17,
                    global_prefix_bits=invoice['global_prefix_bits'], charged_prefix_bits=2048,
                    physical=133117, private_zero_buffers=91, **hashes)
    save(v.P / 'evidence/VALIDATION.json', evidence)
    print(claim['status'], claim['gain'], flush=True)


if __name__ == '__main__':
    main()
