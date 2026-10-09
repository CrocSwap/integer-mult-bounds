#!/usr/bin/env python3
"""Incremental new h28 mixed-center producer and exact selected corner checks.

Copyright 2026 icekylinx, Apache-2.0; OpenAI GPT-6 Astra/Codex assisted
integration. Reuse validated bit25/23 producers without regenerating them.
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

from copied_centers.corners import require, verify as verify_corner
from copied_centers.physical import copied_histogram
from endpoint_gauge_producer import compare
from structured_bulk.complex import build as complex_build

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text())


def reused_bit(axes, previous):
    require([row['h'] for row in axes] == [25,23], 'Wrong selected bit dimensions')
    answer = {}
    for row in axes:
        h = row['h']
        old = previous['producers'][str(h)]
        for current, retained in (('v','v'), ('c','additions'), ('q','outputs'),
                                  ('R','roles'), ('matching','matches'),
                                  ('loss','loss'), ('histogram','histogram')):
            require(row[current] == old[retained], f'Bit h={h}: mismatch in {current}')
        require(row['baseline_R'] == row['c']+row['q'] and
                row['R'] == row['baseline_R']-row['matching'],
                f'Bit h={h}: inconsistent selected carrier accounting')
        require(row['label_source'] == 'positive', 'Wrong selected bit labels')
        require(not any('eligible' in key for key in row),
                'Research terminal-eligibility data must not enter the selected input')
        answer[str(h)] = dict(reused_validated_producer=True,
                             baseline_certificate_equal=True,
                             copied=copied_histogram(row))
    return answer


def regenerate(work, axes, expected_complex, corner, previous_bit, compiler):
    require(sys.flags.optimize == 0, 'Run without -O: producer assertions must remain enabled')
    bit = reused_bit(axes, previous_bit)
    print('Checking 47 exact rational pivots and 315 weight-independent zero minors',
          file=sys.stderr, flush=True)
    corner_result = verify_corner(corner)
    require(expected_complex['h'] == 28 and expected_complex['central_disjoint'] == 19,
            'Wrong selected complex producer')
    print('Regenerating only new complex h=28, d=19 scalar producer',
          file=sys.stderr, flush=True)
    prefix = work / 'complex_d19_28'
    construction = complex_build(28, prefix, central_disjoint=19)
    gc.collect()
    program = work / 'match_complex_general'
    source = ROOT/'scripts'/'endpoint_gauge'/'match_complex_general.cpp'
    subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17', str(source),
                    '-o', str(program)], check=True)
    matched = json.loads(subprocess.check_output(
        [str(program), str(prefix)+'.bin', str(prefix)+'.labels'], text=True))
    compare(matched, expected_complex, 'complex h=28, d=19')
    require(construction['R'] == matched['baseline_R'], 'Wrong raw complex role count')
    copied = copied_histogram(matched)
    return dict(bit=bit, corner=corner_result,
                complex=dict(**matched, central_disjoint=19, construction=construction,
                             copied=copied, certificate_equal=True),
                old_bit_producer_regeneration_skipped=True,
                incremental_selected_checks_only=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name, filename in (
            ('bit-axes','copied-centers-bit-axes.json'),
            ('complex-input','copied-centers-complex-input.json'),
            ('corner','copied-centers-corner-25-23.json'),
            ('previous-bit','partial-swap-input.json')):
        parser.add_argument('--'+name, type=Path, default=ROOT/'certificates'/filename)
    parser.add_argument('--cxx', default=os.environ.get('CXX','c++'))
    parser.add_argument('--work-dir', type=Path, help='Keep generated intermediates')
    parser.add_argument('--output', type=Path, help='Write full incremental result JSON')
    args = parser.parse_args()
    inputs = [read(path) for path in (args.bit_axes,args.complex_input,
                                     args.corner,args.previous_bit)]
    def run(work):
        return regenerate(work, *inputs, args.cxx)
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = run(args.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='copied-centers-') as directory:
            result = run(Path(directory))
    encoded = json.dumps(result,indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded,end='')


if __name__ == '__main__':
    main()
