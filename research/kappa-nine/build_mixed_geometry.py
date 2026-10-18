"""Build the finite graph certificate for the local block proof."""
from hashlib import sha256
from itertools import combinations
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json

from local_rank_test import color_y, line_graph
from local_support_elimination import CLIQUE, TRIPLES, classes
from mixed_rank_obstruction import forcing_witness
from target_budget import root_bounds
from verify_mixed_geometry import BASE, SOURCE_PATHS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def build():
    blocks = []
    groups = classes()
    for block, line in enumerate(CLIQUE):
        partitions = []
        for point in line:
            for outside in (7, 8):
                labels = [list(TRIPLES[i]) for i in groups[point][1]
                          if outside in TRIPLES[i]]
                singleton = sorted((set(line) - {point}) | {outside})
                partitions.append({'point': point, 'outside': outside,
                                   'singleton': singleton,
                                   'others': [t for t in labels if t != singleton]})
        graph = line_graph(block)
        blocks.append({'block': block, 'line': list(line),
                       'partitions': partitions,
                       'edges': [[list(TRIPLES[i]), list(TRIPLES[j])]
                                 for i, j in graph['edges']]})
    pairs = []
    for regular in combinations(range(7), 2):
        point, = set(CLIQUE[regular[0]]) & set(CLIQUE[regular[1]])
        witnesses = [forcing_witness(point, z, set(range(7)) - set(regular))
                     for z in (7, 8)]
        pairs.append({'regular_blocks': list(regular), 'point': point,
                      'forced_block': witnesses[0]['exception_block'],
                      'forced_labels': [w['triple'] for w in witnesses],
                      'cliques': [[list(TRIPLES[i]) for i in w['clique']]
                                  for w in witnesses]})
    coloring = color_y()
    rows = {4: Q(1), 26: Q(4), 30: Q(10) + Q(26, 525), 169: Q(2), 195: Q(10)}
    budget = []
    for degree in (511, 99):
        budget.append({'degree': degree, 'roots': [
            {'child': child, 'count': str(count),
             'interval': [str(x) for x in root_bounds(Q(225, child), degree)]}
            for child, count in sorted(rows.items())]})
    return {
        'status': 'SCOPED ALGEBRAIC OBSTRUCTION; NO NEW KAPPA',
        'base_commit': BASE,
        'source_sha256': {p: sha256((ROOT / p).read_bytes()).hexdigest()
                          for p in SOURCE_PATHS},
        'budget_context': {'dimension': 225, 'volume_per_label': '12',
                           'roles_per_label_per_axis': '5',
                           'complex_coarse': '0.001664727258740678855772',
                           'bit_coarse': '0.001733427039589844234749',
                           'moment_checks': budget},
        'normal_form_blocks': blocks,
        'regular_pair_witnesses': pairs,
        'remaining_exception_sets': [list(c) for n in (6, 7)
                                     for c in combinations(range(7), n)],
        'coordinate_control': [{'label': list(TRIPLES[i]), 'block': k}
                               for i, k in sorted(coloring.items())],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(), indent=2) + '\n')
    print('Wrote 7 local block certificates and 21 regular-pair witnesses.')
