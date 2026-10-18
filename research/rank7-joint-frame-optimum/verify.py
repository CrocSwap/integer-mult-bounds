#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recompute the complete fixed-scalar A/B/restore frame optimum."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from math import prod
from pathlib import Path

from eliminate import proof_summary, solve_component
from graph import bounds, build, components, profile
from spaces import rank, require

PACKAGE = Path(__file__).resolve().parent
EXPECTED_PROFILE = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}
EXPECTED_WIDTHS = {4: 26, 5: 2, 6: 16, 7: 52, 8: 99, 9: 213}


def load_words(package=PACKAGE):
    sources = json.loads((package / 'SOURCES.json').read_text(encoding='utf-8'))
    records = sources['exports']
    require([r['local'] for r in records] ==
            ['inputs/base.json.gz', 'inputs/extra.json.gz', 'inputs/NOTICE-PR2979'],
            'exact frozen input inventory')
    words = {}
    for record in records:
        raw = (package / record['local']).read_bytes()
        require(len(raw) < 100000 and hashlib.sha256(raw).hexdigest() == record['sha256'],
                'frozen input bytes')
        if record['local'].endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                decoded = stream.read(800001)
            require(len(decoded) <= 800000, 'decoded input capacity')
            words[Path(record['local']).name.split('.')[0]] = json.loads(decoded)
    return words


def solve(word):
    graph = build(word)
    paid = {r: n for r, n in enumerate(profile(graph.edges, {})) if r and n}
    paid = dict(sorted((Counter(paid) + graph.fixed_profile).items()))
    require(paid == EXPECTED_PROFILE ==
            {int(r): n for r, n in word['report']['local_profile'].items()},
            'complete declared source profile')
    require(dict(graph.widths) == EXPECTED_WIDTHS ==
            {int(r): n for r, n in word['report']['width_inventory'].items()},
            'complete helper widths')
    require(len(word['helper_final']) == 91, '91 private return buffers')
    lower, upper = bounds(graph)
    factors = components(graph, lower, upper)
    rows, comparisons = [], set()
    for component in factors:
        row, vectors = solve_component(component, graph.edges, lower, upper)
        require(row['source_comparison'] == 0, 'source attains component optimum')
        rows.append(row)
        comparisons |= vectors
    return {'scalar_events': len(graph.frames), 'edges': len(graph.edges),
            'variables': sum(map(len, factors)), 'components': len(factors),
            'quotient_dimensions': dict(sorted(Counter(rank(hi) - rank(lo)
                for lo, hi in zip(lower, upper, strict=True)).items())),
            'local_profile': paid, 'width_inventory': dict(sorted(graph.widths.items())),
            'private_buffers': 91, 'max_bucket': max(r['max_bucket'] for r in rows),
            'max_width': max(r['max_width'] for r in rows),
            'attempts': sum(r['attempts'] for r in rows),
            'projected_states': sum(r['states'] for r in rows),
            'feasible_assignments': prod(r['feasible'] for r in rows),
            'optimal_assignments': prod(r['optimal'] for r in rows),
            'comparisons': proof_summary(comparisons), 'component_receipts': rows}


def run(package=PACKAGE):
    results = {name: solve(word) for name, word in load_words(package).items()}
    require(results['base'] == results['extra'], 'both provider optimum receipts agree')
    require(results['base']['scalar_events'] == 6141
            and results['base']['variables'] == 743
            and results['base']['components'] == 210, 'exact source instance')
    return {'status': 'PASS_JOINT_FRAME_OPTIMUM', 'exponent_range': '0 < b <= 1/100',
            'claim': 'The source minimizes the complete local frame tariff in the stated relaxation.',
            'scope': 'Fixed scalar operations/order, endpoints, centre and warp interfaces; no supplier admission.',
            'providers': ['base', 'extra'], 'common_problem': results['base']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
        require(args.output.write_text(rendered, encoding='utf-8') == len(rendered), 'complete receipt write')
    print('PASS_JOINT_FRAME_OPTIMUM providers=2 scalar_events=6141 variable_frames=743 '
          'components=210 range=(0,1/100] no_new_kappa')


if __name__ == '__main__':
    main()
