#!/usr/bin/env python3
"""Emit one streamed quadratic GF(2) system in the documented binary format."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import numpy as np
from model import ROOT, check_sources, require, array_hash
from quadratic import prepare, constraint_batches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True, help='model.npz from a successful verify --output run')
    parser.add_argument('--profiles', type=int, nargs=2, required=True, choices=range(3))
    parser.add_argument('--output', type=Path, help='Default writes binary to stdout for piping to code/solve.cpp')
    args = parser.parse_args()
    check_sources()
    expected = json.loads((ROOT / 'evidence/MODEL.json').read_text())
    with np.load(args.model, allow_pickle=False) as data:
        state = dict(adjacency=data['adjacency'], q=[data[f'q{i}'] for i in range(3)])
    require(array_hash(state['adjacency']) == expected['geometry']['adjacency_hash'], 'Cached adjacency hash')
    for i in range(3):
        require(array_hash(state['q'][i]) == expected['features'][i]['quadratic_hash'], 'Cached quadratic feature hash')
    first, second = args.profiles
    variables, count, selected = prepare(state, first, second)
    stream = args.output.open('wb') if args.output else sys.stdout.buffer
    try:
        stream.write(struct.pack('<II', variables, count))
        for batch in constraint_batches(state, first, second, selected):
            stream.write(batch.tobytes())
    finally:
        if args.output:
            stream.close()


if __name__ == '__main__':
    main()
