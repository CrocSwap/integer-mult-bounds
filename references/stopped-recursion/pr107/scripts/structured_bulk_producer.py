#!/usr/bin/env python3
"""Reproduce only the new structured-bulk producer work and exact profiles.

Copyright 2026 icekylinx, Apache-2.0. AI-assisted integration. Requires Python
and a GCC/Clang C++17 compiler with unsigned __int128 for the supplied modular
profiler. Unchanged h32/h30 positive producers are not rebuilt or rechecked.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

from endpoint_gauge.bit import graph, export
from endpoint_gauge_producer import compare
from structured_bulk.complex import build as complex_build
from structured_bulk.exactness import require, verify as verify_exactness

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


def read(path):
    return json.loads(path.read_text())


def compare_selected(actual, expected):
    for key in ('h','v','c','q','baseline_R','matched','R',
                'orientation_changes','rank_sum','loss'):
        require(actual[key] == expected[key], 'Selected bit mismatch: '+key)
    if 'histogram' in expected:
        require(actual['histogram'] == expected['histogram'], 'Selected histogram mismatch')


def export_bit(work, h, validate):
    print(f'Structured bulk bit h={h}: scalar DAG'+
          (' and exact support checks' if validate else ' for fixed-basis profiling only'),
          file=sys.stderr, flush=True)
    circuit = graph(h)
    scalar = circuit.verify() if validate else None
    path = work / f'triple{h}.bin'
    export(circuit, path)
    circuit.support_in.cache_clear()
    del circuit
    gc.collect()
    return path, scalar


def regenerate(work, bit_axes, expected_profiles, exactness, complex_input,
               previous_bit, compiler):
    require(sys.flags.optimize == 0, 'Run without -O: finite assertions must remain enabled')
    axes = {a['h']:a for a in bit_axes}
    require([a['h'] for a in bit_axes] == [32,30,36], 'Wrong selected bit axes')
    require([a['internal_profile_mode'] for a in bit_axes] ==
            ['generic','fixed_I_plus_J','generic'], 'Wrong bit profile modes')
    previous = {a['h']:a for a in previous_bit}
    # The scalar counts persist at h30, but its old positive histogram is
    # deliberately not compared or consumed by the new fixed-basis moment.
    compare_selected(previous[32], axes[32])
    compare_selected(previous[30], axes[30])
    programs = {}
    for directory, name in (('partial_swap','match_exported_dag'),
                            ('structured_bulk','rankone_profiles'),
                            ('endpoint_gauge','match_complex_general')):
        programs[name] = work / name
        subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17',
                        str(SCRIPTS/directory/(name+'.cpp')), '-o',
                        str(programs[name])], check=True)
    answer = dict(reused_bit_axes=[32,30], bit={}, complex={},
                  unchanged_positive_producers_skipped=True)
    dag, scalar = export_bit(work, 36, True)
    matched = json.loads(subprocess.check_output(
        [str(programs['match_exported_dag']), str(dag)], text=True))
    compare_selected(matched, axes[36])
    answer['bit']['36'] = dict(**matched, scalar=scalar, certificate_equal=True,
                               label_mode='original_envelope')

    dag, _ = export_bit(work, 30, False)
    print('Reconstructing h30 original matching and all fixed-basis CRT profiles',
          file=sys.stderr, flush=True)
    original = json.loads(subprocess.check_output(
        [str(programs['rankone_profiles']), str(dag)], text=True))
    compare_selected(original, axes[30])
    profile = read(Path(str(dag)+'.round3_rankone_certified_profiles.json'))
    for key in ('h','v','R','loss','rank_sum','field_prime','frames',
                'distinct_matrices','blocks'):
        require(profile[key] == expected_profiles[key], 'Fixed-basis profile mismatch: '+key)
    exact = verify_exactness(exactness, profile)
    answer['bit']['30'] = dict(original_matching=original, profile=profile,
                               exactness=exact, certificate_equal=True,
                               label_mode='original_envelope_fixed_I_plus_J')

    require(complex_input['dimensions'] == [30,30,40] and
            complex_input['central_disjoint'] == [19,19,35], 'Wrong mixed centers')
    expected = {}
    for record in complex_input['scalar_circuits']:
        key = (record['h'], record['central_disjoint'])
        require(key not in expected or expected[key] == record,
                'Repeated complex axes have inconsistent records')
        expected[key] = record
    require(set(expected) == {(30,19),(40,35)}, 'Wrong selected complex producers')
    for (h,d), record in expected.items():
        print(f'Structured bulk complex h={h}, d={d}: exact mixed-center producer',
              file=sys.stderr, flush=True)
        prefix = work / f'complex_d{d}_{h}'
        construction = complex_build(h, prefix, central_disjoint=d)
        gc.collect()
        matched = json.loads(subprocess.check_output(
            [str(programs['match_complex_general']), str(prefix)+'.bin',
             str(prefix)+'.labels'], text=True))
        compare(matched, record, f'complex h={h}, d={d}')
        require(matched['baseline_R'] == construction['R'], 'Wrong raw complex roles')
        require(matched['loss'] == h*(h-1), 'Wrong mixed-center loss')
        answer['complex'][f'{h}:{d}'] = dict(**matched, construction=construction,
                                            certificate_equal=True)
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name, filename in (
            ('bit-axes', 'structured-bulk-bit-axes.json'),
            ('rankone-profiles', 'structured-bulk-rankone-profiles.json'),
            ('rankone-exactness', 'structured-bulk-rankone-exactness.json'),
            ('complex-input', 'structured-bulk-complex-input.json'),
            ('previous-bit', 'endpoint-gauge-bit-axes.json')):
        parser.add_argument('--'+name, type=Path, default=ROOT/'certificates'/filename)
    parser.add_argument('--cxx', default=os.environ.get('CXX','c++'))
    parser.add_argument('--work-dir', type=Path, help='Keep large generated intermediates here')
    parser.add_argument('--output', type=Path, help='Write complete incremental verification report')
    args = parser.parse_args()
    inputs = [read(path) for path in (args.bit_axes, args.rankone_profiles,
                                     args.rankone_exactness, args.complex_input,
                                     args.previous_bit)]
    def run(work):
        return regenerate(work, *inputs, args.cxx)
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = run(args.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='structured-bulk-') as directory:
            result = run(Path(directory))
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
