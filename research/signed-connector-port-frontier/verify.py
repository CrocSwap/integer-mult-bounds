#!/usr/bin/env python3
"""Replay the scoped signed-connector port rigidity package; no frontier claim.
Ross Richardson, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model
import independent_dense


def load(name):
    return json.loads((HERE / name).read_text())


def source_pins():
    pins = load('SOURCES.json')
    model.require(pins['base_commit'] == '418e40eb2572d930b58c1cf9b82b41c0fc7ee08d', 'exact base pin')
    inventory = pins['archived_sources']
    actual = sorted(str(p.relative_to(HERE)) for p in (HERE / 'sources').iterdir() if p.is_file())
    model.require(actual == sorted(row['path'] for row in inventory), 'archive inventory')
    for row in inventory:
        path = HERE / row['path']
        model.require(path.resolve().is_relative_to(HERE) and not path.is_symlink(), 'local source archive')
        model.require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'archive source hash: ' + row['path'])
    original = load('sources/PR1651-WORD.json')
    normalized = [(kind, 1 if kind == 'R' else op, sign * op if kind == 'R' else sign, root)
                  for kind, op, sign, root in original['word']]
    model.require(model.word_mask(normalized) == 35, 'credited PR1651 witness ports')


def receipt_checks():
    source_pins()
    primary, other, dense = load('CERTIFICATE.json'), load('independent-results.json'), load('DENSE.json')
    expected_counts = [80 if mask == 35 else 0 for mask in range(64)]
    model.require(primary['source_traces'] == 7257600, 'complete source trace domain')
    model.require(primary['restored_traces'] == 3343680, 'restored trace count')
    model.require(primary['feasible_traces'] == 80, 'feasible trace count')
    model.require(primary['counts'] == expected_counts, 'exact singleton port counts')
    model.require(primary['restored_by_source'] == [907200, 483840, 483840, 273600, 483840, 273600, 273600, 164160], 'source restoration profile')
    model.require([w['mask'] for w in primary['witnesses']] == [35], 'exact witness portfolio')
    model.require(other['trace_count'] == primary['source_traces'] and other['restored_trace_count'] == primary['restored_traces'] and other['feasible_source_trace_count'] == primary['feasible_traces'], 'independent coverage agreement')
    model.require(other['restored_by_source_mask'] == primary['restored_by_source'] and other['feasible_trace_count_by_six_bit_port_mask'] == primary['counts'], 'independent complete mask/profile agreement')
    controls = other['controls']
    model.require(controls['swap_rows_0_2']['nonzero_port_mask_counts'] == {'11': 80}, 'row covariance control')
    model.require(controls['swap_columns_0_2']['nonzero_port_mask_counts'] == {'38': 80}, 'column covariance control')
    model.require(controls['negate_column_2']['nonzero_port_mask_counts'] == {'35': 80}, 'signed source control')
    model.require(controls['omit_same_dirt_requirement_invalid']['feasible_source_trace_count'] == 11488, 'dirty-root sensitivity')
    model.require(controls['all_ones_target']['feasible_source_trace_count'] == 281640, 'non-hardcoded target control')
    model.require(controls['replace_entry_2_2_zero_with_one']['feasible_source_trace_count'] == 9360, 'zero coefficient control')
    for witness in primary['witnesses']:
        model.require(model.word_mask(witness['word']) == witness['mask'], 'literal port witness')
        model.require(model.semantic_controls(witness['word']) == 38, 'semantic mutation coverage')
        dual = [(('A' if kind == 'B' else 'B'), op, sign, 1 - root) if kind != 'R' else (kind, op, sign, root)
                for kind, op, sign, root in reversed(witness['word'])]
        model.require(model.word_mask(dual) == 35, 'transpose/reverse/root-swap proof control')
    model.one_root_histogram()
    model.require(independent_dense.build_result(primary) == dense, 'independent dense receipt')
    # Arbitrary exact rational prices; signs may have unequal individual prices.
    model.require(model.tariff(35, [[20, 200]] * 6, [1, 1]) == 664, 'forced port surcharge fixture')
    model.require(model.tariff(35, [['1/3', '2/3']] * 6, ['1/5', '2/5']) == model.Fraction(21, 5), 'rational tariff fixture')
    for pairs, transfers in [([[0, 1]] * 6, [1, 1]), ([[1, -1]] * 6, [1, 1]), ([[1, 1]] * 6, [0, 1])]:
        try:
            model.tariff(35, pairs, transfers)
        except ValueError:
            pass
        else:
            raise ValueError('invalid tariff accepted')
    return primary, other


def run_census(source, build):
    compiler = shutil.which('c++')
    model.require(compiler is not None, 'C++17 compiler c++ is required for both exhaustive enumerators')
    executable = build / Path(source).stem
    subprocess.run([compiler, '-std=c++17', '-O2', '-UNDEBUG', str(HERE / source), '-o', str(executable)], check=True, timeout=60)
    result = subprocess.run([str(executable)], check=True, text=True, stdout=subprocess.PIPE, timeout=90)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-receipts-only', action='store_true', help='internal corruption controls: excludes exhaustive enumeration')
    args = parser.parse_args()
    primary, other = receipt_checks()
    if args.check_receipts_only:
        print('PASS_RECEIPT_CHECK_ONLY no_census_replay')
        return
    with tempfile.TemporaryDirectory(prefix='signed-port-census-') as tmp:
        build = Path(tmp)
        model.require(run_census('census.cpp', build) == primary, 'chronological census receipt')
        model.require(run_census('independent.cpp', build) == other, 'independent endpoint census receipt and controls')
    print('PASS_SIGNED_CONNECTOR_PORT_RIGIDITY traces=7257600 restored=3343680 feasible=80 sole_mask=35 symbolic_controls=38 dense_controls=39 no_new_kappa')


if __name__ == '__main__':
    main()
