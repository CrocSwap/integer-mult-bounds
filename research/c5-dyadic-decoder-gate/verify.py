#!/usr/bin/env python3
"""Source-bound C5 gate and explicit hypothesis controls. Tekalign; AI-assisted."""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from algebra import (baseline, check_fit, costs_for, dot, escape_controls,
                     half_fixtures, need, roots_e8)
from search import exclude

HERE = Path(__file__).resolve().parent
PINS = {'DATA-PHASES.json.gz': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
        'MATCHING.json': '4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1'}


def sources():
    bound = {}
    for name, pin in PINS.items():
        raw = (HERE / 'inputs' / name).read_bytes()
        if name.endswith('.gz'):
            raw = gzip.decompress(raw)
        need(hashlib.sha256(raw).hexdigest() == pin, 'source authentication: ' + name)
        bound[name] = raw
    # Parse only after authenticating every input.
    recipes = json.loads(bound['DATA-PHASES.json.gz'])['recipes']
    labels = {r['port']: r['q'] for r in recipes}
    need(len(labels) == len(recipes) == 112 and sorted(labels) == list(range(112)), 'source ports')
    matching = json.loads(bound['MATCHING.json'])['matching']
    need(len(matching) == 56 and sorted(p for pair in matching for p in pair) == list(range(112)), 'matching partition')
    planes = [[labels[p] for p in pair] for pair in matching]
    need(all([[dot(a, b) for b in plane] for a in plane] == [[1, 0], [0, 1]] for plane in planes), 'nondegenerate planes')
    return matching, planes


def cycles_and_classes(planes):
    neighbors = [{j for j, q in enumerate(planes) if all(dot(a, b) == 0 for a in p for b in q)}
                 for p in planes]
    cycles = []
    for a in range(56):
        for b in sorted(neighbors[a]):
            if b <= a:
                continue
            for c in sorted(neighbors[b] - neighbors[a] - {a}):
                if c <= a:
                    continue
                for d in sorted(neighbors[c] - neighbors[b] - neighbors[a] - {a, b}):
                    if d <= a:
                        continue
                    for e in sorted((neighbors[d] & neighbors[a]) - neighbors[b] - neighbors[c] - {b, c}):
                        if e > a and e > b:
                            cycles.append([a, b, c, d, e])
    # A different exhaustive census: all 56 choose 5 vertex sets, degree two.
    neighbor_bits = [sum(1 << j for j in row) for row in neighbors]
    subsets = set()
    for group in itertools.combinations(range(56), 5):
        bits = sum(1 << i for i in group)
        if all((neighbor_bits[i] & bits).bit_count() == 2 for i in group):
            subsets.add(group)
    need(subsets == {tuple(sorted(c)) for c in cycles}, 'independent cycle census')
    need(len(cycles) == 23, 'cycle count')
    classes = {}
    for i, cycle in enumerate(cycles):
        variants = []
        for direction in (cycle, cycle[::-1]):
            for offset in range(5):
                order = direction[offset:] + direction[:offset]
                variants.append((costs_for([planes[j] for j in order]), order))
        prices, order = min(variants)
        classes.setdefault(tuple(prices), []).append({'index': i, 'order': order})
    need(len(classes) == 16, 'cost class count')
    return cycles, classes


def controls(planes):
    rows = baseline(planes)
    names = []
    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            names.append(name)
        else:
            raise ValueError('control did not reject: ' + name)
    bad = [r[:] for r in rows]
    bad[4] = bad[0][:]  # nonadjacent planes now share a forbidden scalar entry.
    rejects('forbidden_cross_entry', lambda: check_fit(bad, planes))
    bad = [r[:] for r in rows]
    bad[0] = [0] * 8
    rejects('missing_diagonal_payload', lambda: check_fit(bad, planes))
    rejects('wrong_common_normalization', lambda: check_fit(rows, planes, 2))
    actual = sum(check_fit(rows, planes))
    rejects('support_only_half_invoice', lambda: need(actual == 10, 'both plane dimensions are paid'))
    prices = costs_for(planes)
    # This sensitivity probe weakens the tariff, rather than the scalar endpoint.
    weak = [c//2 for c in prices]
    result = exclude(weak, 0, 19)
    need(result['found'], 'underpriced search must admit a witness')
    decoded = [None] * 10
    roots = roots_e8()
    for slot, r in result['witness']:
        decoded[slot] = roots[r]
    true_cost = sum(check_fit(decoded, planes))
    need(true_cost >= 20, 'underpriced witness true invoice')
    names.append('underpricing_search_sensitivity')
    return names


def compute():
    matching, planes = sources()
    cycles, classes = cycles_and_classes(planes)
    searches = []
    for prices, members in sorted(classes.items()):
        results = [exclude(list(prices), anchor, 19) for anchor in (0, 8)]
        need(all(not r['found'] for r in results), 'improving finite-domain decoder found')
        searches.append({'prices': list(prices), 'members': members, 'searches': results})
    for cycle in cycles:
        baseline([planes[i] for i in cycle])
    core = [13, 23, 35, 16, 34]
    need(tuple(sorted(core)) in {tuple(sorted(c)) for c in cycles}, 'PR2484 core included')
    return {'schema_version': 1, 'status': 'SCOPED_NEGATIVE_RESULT_NO_NEW_KAPPA',
            'pins': PINS, 'cycles': cycles, 'cost_classes': searches,
            'completed_anchor_searches': 2*len(classes), 'minimum_cost_each_cycle': 20,
            'root_count': 120, 'port_count_per_cycle': 10, 'coefficient': '1/4',
            'positive_half_fixtures': half_fixtures(), 'escape_controls': escape_controls(),
            'controls': controls([planes[i] for i in core]),
            'core_ports': [p for i in core for p in matching[i]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='exclusive creation of a new receipt')
    args = parser.parse_args()
    result = compute()
    if args.write:
        with args.write.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write('\n')
    else:
        expected = json.loads((HERE / 'RESULT.json').read_text())
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), 'exact typed receipt changed')
    print('PASS_C5_DYADIC_DECODER_GATE cycles=23 classes=16 minimum=20 half_gram_floor=proved quarter_escape=72 signed_half_escape=81 no_new_kappa')


if __name__ == '__main__':
    main()
