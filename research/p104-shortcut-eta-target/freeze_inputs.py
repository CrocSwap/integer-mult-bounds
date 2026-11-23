#!/usr/bin/env python3
"""Freeze source-bound grade histograms and transport cells for the independent bill."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

ap = ArgumentParser()
ap.add_argument('--runtime', required=True, type=Path)
ap.add_argument('--expected-result', required=True, type=Path)
ap.add_argument('--output', required=True, type=Path)
args = ap.parse_args()
runtime = args.runtime.resolve()
sys.path.insert(0, str(runtime))
from upstream import install
install()
from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL
from grades import numerical_source, numerical_recipe
from raw_binary_stage import binary_word
from strong_complex import digest

atlas, word, g_targets, g_paid, g_cells = numerical_source()
ordinary = binary_word()
assert digest(atlas.graph) == 'ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35'
assert (len(word.targets), len(word.paid), len(g_cells)) == (52608, 281328, 51)
assert (len(ordinary.targets), len(ordinary.paid), len(ordinary.cells)) == (18906, 104652, 24)
assert (ENTRY.rank_logs, ENTRY.complex_log, TERMINAL.rank_logs, TERMINAL.complex_log) == (
    (3000, 3080), 1024, (8192, 106000, 1681001), 85406)

def histogram(hist):
    return [[str(Fraction(rank)), int(count)] for rank, count in sorted(hist.items())]

def cells(entries):
    return [[str(Fraction(r)), str(Fraction(k)), str(Fraction(q))]
            for (r, k), q in sorted(entries.items())]

def profile(p):
    return {'ordinary_heights': list(p.rank_logs), 'gaussian_height': p.complex_log,
            'kappa': str(p.kappa), 'eta': str(p.eta), 'stop_denominator': p.positive_stop_denominator}

files = ('installations.py', 'strong_complex.py', 'w5669_shortcut5.json.gz', 'grades.py',
         'raw_binary_stage.py', 'strong-bit.json.gz', 'typed_transport.py')
data = {'source': {'pr': 8088, 'head': '06691302af526a488f3dee0298035f86b6e69c51',
                   'shortcut_graph_sha256': digest(atlas.graph),
                   'runtime_sha256': {name: sha256((runtime / name).read_bytes()).hexdigest() for name in files},
                   'expected_result_sha256': sha256(args.expected_result.read_bytes()).hexdigest()},
        'ordinary': {'trial': str(BINARY_C), 'targets': histogram(Counter(ordinary.targets)),
                     'paid': histogram(Counter(ordinary.paid)), 'cells': cells(ordinary.cells),
                     'level_floor': 18960, 'debit': '11239/8192', 'suffix_coefficient': '64',
                     'tariff': '47/20', 'reserve': '256/255'},
        'gaussian': {'trial': str(GAUSSIAN_C), 'targets': histogram(g_targets.histogram),
                     'paid': histogram(g_paid.histogram), 'cells': cells(g_cells),
                     'level_floor': 1874, 'upper_divisor': 1724, 'ambient': 306,
                     'largest_target': 258, 'debit': '32493/262144',
                     'typed_counts': [len(t.paid) for t in numerical_recipe(1024).types()]},
        'entry': profile(ENTRY), 'terminal': profile(TERMINAL)}
out = args.output.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
print('PASS_FROZEN_LITERAL_INVOICE_INPUTS', out, sha256(out.read_bytes()).hexdigest(), flush=True)
