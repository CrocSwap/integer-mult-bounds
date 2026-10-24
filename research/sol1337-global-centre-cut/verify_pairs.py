#!/usr/bin/env python3
"""Additive adjacent-pair ceiling replay. Apache-2.0; Codex assisted.

Keeps the original common-axis science and producer pair files unchanged.
All generated files and the producer's mutating replay execute in scratch.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PAIRS = HERE / 'pairs'


def need(value, message):
    if not value:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    origin = json.loads((PAIRS / 'ORIGIN.json').read_text())
    for item in origin['copied_files']:
        need(digest(PAIRS / item['path']) == item['sha256'],
             'unchanged authenticated producer bytes: ' + item['path'])
    original = json.loads((PAIRS / 'SOURCES.json').read_text())
    need(digest(PAIRS / 'SOURCES.json') == origin['producer_sources_sha256'],
         'original producer source receipt')
    for item in json.loads((HERE / 'SOURCES.local.json').read_text()):
        need(digest(HERE / item['path']) == item['sha256'],
             'unchanged retained640 source bytes: ' + item['path'])
    lower = [1, 1, 1, 1, 1, 1, 1, 0, 0]
    for key, cases, classes in [('predecessor_single_screen', 188048, 18),
                                ('predecessor_pair_screen', 1834488, 46)]:
        predecessor = origin[key]
        need(digest(PAIRS / predecessor['path']) == predecessor['sha256'],
             'exact PR4867 receipt: ' + key)
        receipt = json.loads((PAIRS / predecessor['path']).read_text())
        need(receipt['cases'] == cases and len(receipt['rank_delta_classes']) == classes,
             'complete predecessor neighbourhood: ' + key)
        for row in receipt['rank_delta_classes']:
            delta = row['delta']
            prefix = [sum(delta[r] * min(r, j) for r in range(10)) for j in range(1, 10)]
            need(all(a >= b for a, b in zip(prefix, lower)),
                 'inherited complete concave bound: ' + key)
    spec = importlib.util.spec_from_file_location('pair_graph_builder', HERE / 'build_graph.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='sol1337-independent-pairs-') as scratch:
        work = Path(scratch)
        builder.build(work)
        expected = {row['path']: row['sha256'] for row in original['own_files']}
        for name in ['center-contact-graph.txt', 'graph-metadata.json']:
            need(digest(work / name) == expected[name], 'exact producer generated graph: ' + name)
        for name in ['verify.py', 'SCREEN.json']:
            shutil.copyfile(PAIRS / name, work / name)
        binary = work / 'scan'
        subprocess.run(['g++', '-std=c++20', '-O3', '-Wall', '-Wextra', '-Werror',
                        '-I', str(HERE / 'vendor'), str(PAIRS / 'scan.cpp'),
                        '-o', str(binary)], check=True)
        cxx_receipt = work / 'cxx-screen.json'
        subprocess.run([str(binary), str(work / 'center-contact-graph.txt'),
                        str(cxx_receipt)], check=True)
        actual = json.loads(cxx_receipt.read_text())
        saved = json.loads((PAIRS / 'SCREEN.json').read_text())
        float_key = 'floating_discovery_minimum_paid_delta'
        need(abs(actual.pop(float_key) - saved.pop(float_key)) < 1e-12,
             'separate floating diagnostic agrees')
        need(actual == saved, 'complete C++ pair histogram/count receipt')
        # The producer code imports no predecessor rank engine and independently
        # combines complete single-endpoint invoices plus shared-edge correction.
        subprocess.run([sys.executable, '-I', '-O', '-W', 'error', '-B',
                        str(work / 'verify.py')], cwd=work, check=True)
        for name in ['RANK8-CENSUS.json', 'VERIFY.json']:
            need((work / name).read_bytes() == (PAIRS / name).read_bytes(),
                 'independent exact producer receipt: ' + name)
        # Test source-graph rejection through the actual C++ entry point.
        lines = (work / 'center-contact-graph.txt').read_text().splitlines()
        n, f, m, e = map(int, lines[0].split())
        start = 1 + n + f + m
        variables = [int(line.split()[1]) == 0 for line in lines[1:1+n]]
        edge_index = next(i for i in range(start, start+e)
                          if variables[int(lines[i].split()[0])]
                          and variables[int(lines[i].split()[1])]
                          and int(lines[i].split()[2]) == 0)
        for name, field, value in [('negative-paid-sign', 3, -1),
                                   ('nonidentity-shared-map', 4, 1),
                                   ('missing-simple-edge-domain', 2, 1)]:
            mutated = lines.copy()
            edge = mutated[edge_index].split()
            edge[field] = str(value)
            mutated[edge_index] = ' '.join(edge)
            path = work / (name + '.txt')
            path.write_text('\n'.join(mutated) + '\n')
            result = subprocess.run([str(binary), str(path), str(work / 'bad.json')],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            need(result.returncode != 0, 'actual pair graph control rejects: ' + name)
    print('PASS_INDEPENDENT_ADJACENT_PAIRS opposite_cases=261632 profiles=44 '
          'rank0_edges=256 rank8_edges=8 graph_controls=3')


if __name__ == '__main__':
    main()
