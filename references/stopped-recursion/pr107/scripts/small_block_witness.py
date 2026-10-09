#!/usr/bin/env python3
"""An exact h=8 rank-two control, not a multiplication improvement.

Triples in F_2^3 lie in unique affine planes. Color by the plane's nonzero
normal. Each of seven colors comprises two disjoint four-point planes.
The resulting label space itself is rational; F_2 indexes only the points.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json

from certify import require
from block_label_targets import hypothetical_counts

ROOT = Path(__file__).resolve().parents[1]


def dot2(a, b):
    return (a & b).bit_count() % 2


def color(triple):
    a, b, c = triple
    normals = [n for n in range(1, 8)
               if dot2(n, a ^ b) == dot2(n, a ^ c) == 0]
    require(len(normals) == 1, 'Triple has no unique affine-plane normal')
    return normals[0]-1


def certificate():
    triples = list(combinations(range(8), 3))
    colors = [color(t) for t in triples]
    neighbors = 0
    for i, s in enumerate(triples):
        for j, t in enumerate(triples[:i]):
            if len(set(s) & set(t)) == 1:
                neighbors += 1
                require(colors[i] != colors[j], 'Improper coloring')
    require(Counter(colors) == {c: 8 for c in range(7)}, 'Wrong color sizes')
    counts = hypothetical_counts(8, 14, 2)
    require(counts['D'] < 0, 'Unexpected positive network deficit')
    return {
        'status': 'EXACT SMALL LABEL WITNESS; NOT A MULTIPLICATION IMPROVEMENT',
        'h': 8, 'ambient_dimension': 14, 'label_rank': 2,
        'triples': triples, 'colors': colors,
        'neighbor_pairs_checked': neighbors,
        'rational_planes': 'U_T=span(e_(2 color(T)), e_(2 color(T)+1))',
        'valid_forms': 'Any rational diagonal form with every diagonal entry nonzero; definite, split, or mixed label signatures',
        'network_deficit': str(counts['D']),
        'deficit_sign_obstruction': 'v=56 < 6*h*(r/k)=336',
        'commuting_projection_obstruction': 'For all h, coordinate labels or pairwise commuting label projections satisfy v*k<=h*r, incompatible with v>6*h*(r/k)',
        'scope': 'A seven-color construction at h=8, with no extension to h=24 supplied',
    }


if __name__ == '__main__':
    out = certificate()
    (ROOT/'certificates/small-block-witness.json').write_text(
        json.dumps(out, indent=2, sort_keys=True)+'\n')
    print('PASS: exact h=8, r=14, k=2 labels; network deficit remains negative')
