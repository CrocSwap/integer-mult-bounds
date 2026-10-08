#!/usr/bin/env python3
"""Rebuild the selected near-balanced binary producers and compare every field.

Dominik Scholz, with substantial OpenAI GPT-6 Astra/Codex assistance.
Apache-2.0. Uses icekylinx's unchanged PR24 base-four producer and matching.
"""
import gc
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

from certify import require
from endpoint_gauge.bit import graph, export
from partial_swap.positive import run as positive_labels

ROOT = Path(__file__).resolve().parents[1]


def regenerate(work, expected, compiler):
    require(sys.flags.optimize == 0, 'Run without -O so finite assertions remain active')
    programs = {}
    for name in ('match_exported_dag', 'match_positive_dag'):
        programs[name] = work/name
        subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17',
                        str(ROOT/'scripts/partial_swap'/(name+'.cpp')),
                        '-o', str(programs[name])], check=True)
    for row in expected:
        h = row['h']
        require(h in (33, 31, 34), 'Unexpected selected axis')
        circuit = graph(h)
        scalar = circuit.verify()
        dag = work/f'axis{h}.bin'
        export(circuit, dag)
        circuit.support_in.cache_clear()
        del circuit
        gc.collect()
        initial = json.loads(subprocess.check_output(
            [str(programs['match_exported_dag']), str(dag), str(dag)+'.links'], text=True))
        labels = positive_labels(str(dag))
        gc.collect()
        final = json.loads(subprocess.check_output(
            [str(programs['match_positive_dag']), str(dag), str(dag)+'.positive'], text=True))
        actual = dict(**final, scalar=scalar, labels=labels, envelope_matching=initial)
        require(actual == row, 'Rebuilt producer differs at h='+str(h))
        require(final['matched'] >= initial['matched'], 'Initial continuations were lost')
        print(f'PASS h={h}: complete scalar, label and histogram record; '
              f'{final["matched"]} final matches')


def main():
    rows = json.loads((ROOT/'certificates/near-balanced-axes.json').read_text())
    require([row['h'] for row in rows] == [33, 31, 34], 'Selected axes')
    with tempfile.TemporaryDirectory(prefix='near-balanced-') as directory:
        regenerate(Path(directory), rows, os.environ.get('CXX', 'c++'))


if __name__ == '__main__':
    main()
