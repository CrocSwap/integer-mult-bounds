#!/usr/bin/env python3
"""Regenerate selected endpoint-gauge bit and complex finite producers.

Copyright 2026 icekylinx, Apache-2.0. AI-assisted integration of the credited
endpoint-gauge research handoff. Standard-library Python and C++17 only;
raw DAGs, label files, and compiled matchers are temporary by default.
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
from endpoint_gauge.complex import build as complex_build
from partial_swap.positive import run as positive_labels

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare(actual, expected, context):
    """Compare the complete selected producer record, including every rank."""
    keys = ('h', 'v', 'c', 'q', 'baseline_R', 'matched', 'R',
            'orientation_changes', 'rank_sum', 'loss', 'histogram')
    for key in keys:
        require(actual[key] == expected[key], f'{context}: mismatch in {key}')


def regenerate(work, bit_certificate, complex_certificate, dimensions, compiler):
    require(sys.flags.optimize == 0, 'Run without -O: finite assertions must remain enabled')
    programs = {}
    for directory, name in (('partial_swap', 'match_exported_dag'),
                            ('partial_swap', 'match_positive_dag'),
                            ('endpoint_gauge', 'match_complex_general')):
        programs[name] = work / name
        subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17',
                        str(SCRIPTS / directory / (name+'.cpp')),
                        '-o', str(programs[name])], check=True)
    expected_bit = {record['h']: record for record in bit_certificate}
    expected_complex = {record['h']: record
                        for record in complex_certificate['scalar_circuits']}
    answer = dict(bit={}, complex={}, regenerated_from_source=True,
                  bit_base_threshold=4, complex_triple_base_threshold=2)
    for h in dimensions:
        print(f'Endpoint gauge bit h={h}: ordinary-base scalar DAG',
              file=sys.stderr, flush=True)
        circuit = graph(h)
        scalar = circuit.verify()
        require([((k==1)+k) % 2 for k in range(4)] == [0, 0, 0, 1],
                'Bit side-output plus retained-total scalar identity failed')
        scalar['retained_total_scalar_identity_exact'] = True
        dag = work / f'triple{h}.bin'
        export(circuit, dag)
        circuit.support_in.cache_clear()
        del circuit
        gc.collect()
        original = json.loads(subprocess.check_output(
            [str(programs['match_exported_dag']), str(dag), str(dag)+'.links'],
            text=True))
        labels = positive_labels(str(dag))
        gc.collect()
        matched = json.loads(subprocess.check_output(
            [str(programs['match_positive_dag']), str(dag), str(dag)+'.positive'],
            text=True))
        compare(matched, expected_bit[h], f'bit h={h}')
        require(original['matched'] == matched['matched'],
                f'bit h={h}: positive enlargement changed selected matching count')
        require(matched['loss'] == h*(h-1), f'bit h={h}: wrong retained-total loss')
        require(matched['rank_sum'] == h*matched['R']+2*h*(h-1),
                f'bit h={h}: rank identity failed')
        answer['bit'][str(h)] = dict(**matched, scalar=scalar, labels=labels,
                                    envelope_matching=original, certificate_equal=True)
        print(f'Endpoint gauge complex h={h}: scalar DAG and exact coefficients',
              file=sys.stderr, flush=True)
        prefix = work / f'complex_general_{h}'
        construction = complex_build(h, prefix)
        gc.collect()
        matched = json.loads(subprocess.check_output(
            [str(programs['match_complex_general']), str(prefix)+'.bin',
             str(prefix)+'.labels'], text=True))
        compare(matched, expected_complex[h], f'complex h={h}')
        require(matched['baseline_R'] == construction['R'],
                f'complex h={h}: baseline role count mismatch')
        require(matched['loss'] == h*h, f'complex h={h}: wrong center loss')
        require(matched['rank_sum'] == h*matched['R']+2*h*h,
                f'complex h={h}: rank identity failed')
        answer['complex'][str(h)] = dict(**matched, construction=construction,
                                        certificate_equal=True)
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bit-certificate', type=Path,
                        default=ROOT/'certificates'/'endpoint-gauge-bit-axes.json')
    parser.add_argument('--complex-certificate', type=Path,
                        default=ROOT/'certificates'/'endpoint-gauge-complex-input.json')
    parser.add_argument('--dimensions', nargs='+', type=int, choices=(32, 30, 40),
                        default=[32, 30, 40])
    parser.add_argument('--cxx', default=os.environ.get('CXX', 'c++'))
    parser.add_argument('--work-dir', type=Path, help='Keep generated intermediates here')
    parser.add_argument('--output', type=Path, help='Write the complete JSON report')
    args = parser.parse_args()
    bit = json.loads(args.bit_certificate.read_text())
    complex_data = json.loads(args.complex_certificate.read_text())
    def run(work):
        return regenerate(work, bit, complex_data, args.dimensions, args.cxx)
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = run(args.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='endpoint-gauge-') as directory:
            result = run(Path(directory))
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
