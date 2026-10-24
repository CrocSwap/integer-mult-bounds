#!/usr/bin/env python3
"""Check the actual support spaces by XOR closure and nullspace equations."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

import argparse

ANNEX = Path(__file__).resolve().parents[1]
PARENT = ANNEX.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", required=True)
OUT = Path(parser.parse_args().out).resolve()
OUT.mkdir(parents=True, exist_ok=True)
HERE = ANNEX / "frozen" / 'lanes/independent-review-20261017/centre-support-review-20261018'
CAMPAIGN = HERE.parents[2]
LANES = CAMPAIGN/'lanes'
ROOT = CAMPAIGN/'root'
PINS = {
    'CENTRE-SUPPORT-GEOMETRY-20261018.md': 'a3df65d159899fbaf7110958275615fc406ecbd077d9d620f7f49ccbe4b923f5',
    'CENTRE-SUPPORT-GEOMETRY-20261018.json': 'dafd6c0af3f8aad852a7c80258118487744921c9a61474b1441e3755f8e3b205',
    'check_centre_support_geometry_20261018.py': '99582e42007012d31dcddc14e05da8c5aac75c1f3b546c00ef0fcf0169f081b2',
}
SOURCE_PINS = {
    'history-encoding/independent-skeleton-20261018/fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz':
        'b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5',
    'controller-followthrough-20261017/structured-centres/STRUCTURED-CENTRES-PROGRAM.json.gz':
        '2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1',
}


def need(test, label):
    if not test:
        raise ValueError(label)


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in values}
    return values


def nullspace(equations):
    rows = list(dict.fromkeys(equations))
    pivots = []
    for column in range(9):
        choice = next((i for i in range(len(pivots), len(rows)) if rows[i] >> column & 1), None)
        if choice is None:
            continue
        slot = len(pivots)
        rows[slot], rows[choice] = rows[choice], rows[slot]
        for i in range(len(rows)):
            if i != slot and rows[i] >> column & 1:
                rows[i] ^= rows[slot]
        pivots.append(column)
    answer = []
    for free in range(9):
        if free not in pivots:
            value = 1 << free
            for row, column in zip(rows, pivots):
                if row >> free & 1:
                    value |= 1 << column
            answer.append(value)
    need(all(not (row & vector).bit_count() % 2 for row in equations for vector in answer), 'Nullspace equations')
    return span(answer)


def main():
    for name, pin in PINS.items():
        need(sha256((ROOT/name).read_bytes()).hexdigest() == pin, 'Root source pin '+name)
    data = []
    for relative, pin in SOURCE_PINS.items():
        raw = gzip.decompress((LANES/relative).read_bytes())
        need(sha256(raw).hexdigest() == pin, 'Actual source pin '+relative)
        data.append(json.loads(raw))
    ports = [record['q'] for record in data[0]['transfers']]
    need([record['port'] for record in data[0]['transfers']] == list(range(112)), 'Actual port order')
    need(len(set(ports)) == 112 and all(q.bit_count() % 2 for q in ports), 'Distinct odd source lines')
    supports = [set(int(p) for p, value in row.items() if F(value)) for row in data[1]['centre_rows']]
    need(len(supports) == 8 and all(len(s) == 12 for s in supports), 'Eight twelve-port supports')
    spaces = [span(ports[p] for p in support) for support in supports]
    duals = [nullspace([ports[p] for p in support]) for support in supports]
    need(all(len(s) == 128 for s in spaces) and all(len(d) == 4 for d in duals), 'Primal and dual dimensions')
    wanted = [{0, 7, 42, 45}, {0, 25, 45, 52}, {0, 45, 82, 127}, {0, 45, 76, 97},
              {0, 45, 76, 97}, {0, 7, 42, 45}, {0, 25, 45, 52}, {0, 45, 82, 127}]
    need(duals == wanted, 'All actual annihilator vectors')
    groups = [[0, 5], [1, 6], [2, 7], [3, 4]]
    group = {v: k for k, values in enumerate(groups) for v in values}
    for i in range(8):
        for j in range(8):
            same = group[i] == group[j]
            need((spaces[i] == spaces[j]) == same, 'Exact equal-space classes')
            need(len(spaces[i] & spaces[j]) == (128 if same else 64), 'Exact pair intersection')
            if i != j:
                need(len(supports[i] & supports[j]) == (0 if same else 2), 'Complete four-partite incidence')
    all_ports = set.union(*supports)
    need(len(all_ports) == 48 and all(sum(p in s for s in supports) == 2 for p in all_ports), 'All source incidences')
    ambient = span(ports[p] for p in all_ports)
    need(ambient == {v for v in range(512) if not (v & 45).bit_count() % 2}, 'Exact common hyperplane')
    common = set.intersection(*spaces)
    need(len(common) == 32, 'Exact common intersection dimension')
    independent = [set()] + [{i} for i in range(8)] + [set(g) for g in groups]
    for chosen in independent:
        need(all(not supports[i] & supports[j] for i in chosen for j in chosen if i != j), 'All compatible subsets')
    certificate = json.loads((ROOT/'CENTRE-SUPPORT-GEOMETRY-20261018.json').read_bytes())
    need(certificate['query_supports'] == [sorted(s) for s in supports]
         and certificate['annihilators'] == [sorted(d-{0}) for d in duals]
         and certificate['equal_subspace_classes'] == groups
         and sorted(certificate['maximum_independent_sets']) == sorted(groups)
         and certificate['conditional_eight_query_rank_lower_bound'] == 62, 'Certificate binding')
    result = {'status': 'PASS_INDEPENDENT_CENTRE_SUPPORT_GEOMETRY', 'source_pins': PINS,
              'source_decompressed_pins': SOURCE_PINS, 'support_dimensions': [7]*8,
              'equal_space_classes': groups, 'pairwise_distinct_space_intersection_dimension': 6,
              'common_space_dimension': 5, 'ambient_dimension': 8,
              'direct_schedule_lower_bound': 62,
              'method': 'Explicit primal XOR closure; independent RREF nullspace equations; exact set intersections; complete multipartite graph proof.',
              'scope': 'One direct capture per row with single unwarped carriers on monotone source-subspace chains. Pair coding violates this carrier premise.',
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'CHECKS.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
