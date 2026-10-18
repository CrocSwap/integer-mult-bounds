#!/usr/bin/env python3
"""Optional independent C++ search, requiring g++ with C++20 support."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    data = gzip.decompress((HERE/'inputs/DATA-PHASES.json.gz').read_bytes())
    pairs_raw = (HERE/'inputs/MATCHING.json').read_bytes()
    require(hashlib.sha256(data).hexdigest() == 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa', 'data pin')
    require(hashlib.sha256(pairs_raw).hexdigest() == '4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1', 'matching pin')
    labels = {r['port']: r['q'] for r in json.loads(data)['recipes']}
    planes = [[labels[p] for p in pair] for pair in json.loads(pairs_raw)['matching']]
    adjacency = [sum(1 << j for j, q in enumerate(planes)
                     if all((x & y).bit_count() % 2 == 0 for x in p for y in q)) for p in planes]
    cycles = []
    for subset in itertools.combinations(range(56), 5):
        bits = sum(1 << i for i in subset)
        if not all((adjacency[i] & bits).bit_count() == 2 for i in subset):
            continue
        order = [subset[0]]
        while len(order) < 5:
            options = [i for i in subset if i not in order and adjacency[order[-1]] >> i & 1]
            require(bool(options), 'cycle reconstruction')
            order.append(min(options))
        cycles.append(order)
    require(len(cycles) == 23, 'all 5-subsets cycle count')
    total_nodes = 0
    with tempfile.TemporaryDirectory(prefix='c5-independent-') as tmp:
        directory = Path(tmp)
        binary = directory/'search'
        subprocess.run(['g++', '-std=c++20', '-O3', '-Wall', '-Wextra', str(HERE/'independent.cpp'), '-o', str(binary)], check=True, timeout=60)
        inputs = directory/'planes.txt'
        inputs.write_text(''.join(' '.join(str(x) for i in c for x in planes[i])+'\n' for c in cycles))
        for i in range(23):
            for anchor in (0, 8):
                completed = subprocess.run([str(binary), str(anchor), '19', str(inputs), str(i)], check=True,
                                           capture_output=True, text=True, timeout=30)
                require('found=0' in completed.stdout and 'WITNESS' not in completed.stdout, 'independent exclusion')
                total_nodes += int(completed.stdout.split(' nodes=')[1].split()[0])
        positive = subprocess.run([str(binary), '0', '20', str(inputs), '0'], check=True,
                                  capture_output=True, text=True, timeout=30)
        require('found=1' in positive.stdout and 'WITNESS cost=20' in positive.stdout, 'exact native search positive control')
    print(f'PASS_INDEPENDENT_C5_SEARCH cycles=23 anchors=46 nodes={total_nodes} minimum=20')


if __name__ == '__main__':
    main()
