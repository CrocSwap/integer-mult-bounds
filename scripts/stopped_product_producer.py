#!/usr/bin/env python3
"""Regenerate only the new h24 aligned all-disjoint rational-center producer.

Copyright 2026 icekylinx, Apache-2.0. Prepared with OpenAI GPT-6 Astra and
Codex assistance. Prior paired circuit and matcher attribution is retained
in NOTICE. No old bit producer is regenerated.
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

from copied_centers.corners import require
from copied_centers.physical import copied_histogram
from endpoint_gauge_producer import compare
from stopped_product.complex import build

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def regenerate(work, bit, expected, previous_bits, compiler):
    require(sys.flags.optimize == 0, 'Run without -O: mathematical assertions must remain enabled')
    require(bit['h'] == 23 and bit['label_source'] == 'positive', 'Wrong selected bit axis')
    old = next(row for row in previous_bits if row['h'] == 23)
    for key in ('h','v','c','q','baseline_R','matching','R','loss','histogram','label_source'):
        require(bit[key] == old[key], 'Reused bit producer mismatch: '+key)
    require(bit['R'] == bit['c']+bit['q']-bit['matching'], 'Bit role identity failed')
    bit_copied = copied_histogram(bit)
    require((expected['h'],expected['central_disjoint'],expected['center_denominator']) ==
            (24,24,21), 'Wrong rational-center parameters')
    print('Regenerating only complex h=24: aligned pair stars, all24 disjoint centers, divisor21',
          file=sys.stderr, flush=True)
    prefix = work/'complex_rational_d24_24'
    construction = build(24, prefix, central_disjoint=24)
    gc.collect()
    program = work/'match_complex_general'
    source = ROOT/'scripts'/'endpoint_gauge'/'match_complex_general.cpp'
    subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17', str(source),
                    '-o', str(program)], check=True)
    matched = json.loads(subprocess.check_output(
        [str(program), str(prefix)+'.bin', str(prefix)+'.labels'], text=True))
    compare(matched, expected, 'complex h=24 rational centers')
    require(construction['R'] == matched['baseline_R'], 'Wrong raw complex roles')
    phase_copied = copied_histogram(matched)
    return dict(bit=dict(reused_validated_producer=True, certificate_equal=True,
                         copied=bit_copied),
                complex=dict(**matched, central_disjoint=24, center_denominator=21,
                             construction=construction, copied=phase_copied,
                             certificate_equal=True),
                old_bit_regeneration_skipped=True,
                scope='Exact new scalar supports, rational scatter, nested frames and matching histogram. '
                      'The common odd-denominator grid and recursive tape transfer remain written proof interfaces.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name, filename in (
            ('bit-axis','stopped-product-bit-axis.json'),
            ('complex-input','stopped-product-complex-input.json'),
            ('previous-bits','copied-centers-bit-axes.json')):
        parser.add_argument('--'+name, type=Path, default=ROOT/'certificates'/filename)
    parser.add_argument('--cxx', default=os.environ.get('CXX','c++'))
    parser.add_argument('--work-dir', type=Path, help='Keep generated intermediate files')
    parser.add_argument('--output', type=Path, help='Write full incremental verification JSON')
    args = parser.parse_args()
    inputs = [read(path) for path in (args.bit_axis,args.complex_input,args.previous_bits)]
    def run(work):
        return regenerate(work,*inputs,args.cxx)
    if args.work_dir:
        args.work_dir.mkdir(parents=True,exist_ok=True)
        result = run(args.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='stopped-product-') as directory:
            result = run(Path(directory))
    encoded = json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded,end='')


if __name__ == '__main__':
    main()
