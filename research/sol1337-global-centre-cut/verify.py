#!/usr/bin/env python3
"""Source-pinned complete common-axis paid-profile replay. Apache-2.0."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise RuntimeError(message)


def main():
    for item in json.loads((HERE / 'SOURCES.local.json').read_text()):
        need(hashlib.sha256((HERE / item['path']).read_bytes()).hexdigest()
             == item['sha256'], 'retained source bytes: ' + item['path'])
    spec = importlib.util.spec_from_file_location('build_graph', HERE / 'build_graph.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='sol1337-global-centre-') as scratch:
        work = Path(scratch)
        meta = builder.build(work)
        need(meta['newly_variable_center_contacts'] == 184 and meta['inputs'] == 640,
             'retained640 variable boundary')
        rows = (work / 'center-contact-graph.txt').read_text().splitlines()
        n, f, m, e = map(int, rows[0].split())
        need((n, e) == (19197, 34830), 'actual graph dimensions')
        nodes = [tuple(map(int, row.split())) for row in rows[1:1+n]]
        charts = [list(map(int, row.split())) for row in rows[1+n:1+n+f]]
        groups = {fi for fi, fixed in nodes if not fixed}
        need(len(groups) == 9, 'nine original chart groups')
        common = None
        for fi in groups:
            span = {0}
            for x in charts[fi]:
                span |= {v ^ x for v in list(span)}
            common = span if common is None else common & span
        need(common == {0}, 'complete literal ambient axis domain')
        binary = work / 'scan'
        subprocess.run(['g++', '-std=c++20', '-O3', '-Wall', '-Wextra', '-Werror',
                        str(HERE / 'scan.cpp'), '-o', str(binary)], check=True)
        result = work / 'screen.json'
        subprocess.run([str(binary), str(work / 'center-contact-graph.txt'),
                        str(result), '262143'], check=True)
        expected = json.loads((HERE / 'SCREEN.json').read_text())
        need(json.loads(result.read_text()) == expected, 'complete screen receipt')
        need(expected['distinct_rank_configurations'] == 419
             and expected['independent_rank_configuration_checks'] == 419,
             'all retained rank configurations checked')
        need(all(r['minimum_integer_delta'] == 0 and r['negative_configurations'] == 0
                 for r in expected['results']), 'all integer prefix optima zero')
        edge_start = 1+n+f+m
        edges = [list(map(int, row.split())) for row in rows[edge_start:]]
        internal = next(i for i, t in enumerate(edges)
                        if not nodes[t[0]][1] and not nodes[t[1]][1] and t[2] == 8)
        for name, field, value in [('negative-sign', 3, -1),
                                   ('nonidentity-internal-map', 4, 1),
                                   ('changed-old-invoice', 2, 7)]:
            mutated = rows.copy()
            edge = edges[internal].copy()
            edge[field] = value
            mutated[edge_start+internal] = ' '.join(map(str, edge))
            path = work / (name + '.txt')
            path.write_text('\n'.join(mutated) + '\n')
            check = subprocess.run([str(binary), str(path), str(work/'bad.json'), '1'],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            need(check.returncode != 0, 'mutation rejects: ' + name)
    print('PASS_GLOBAL_CENTRE_CUT axes=262143 configurations=419 exact_prefix_cuts=3771 controls=3')


if __name__ == '__main__':
    main()
