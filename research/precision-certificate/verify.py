#!/usr/bin/env python3
"""Finite precision refinement from pinned inventories, without producer imports.

Copyright 2026 Muhammed Ali Mehmood. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

import independent_moments as M
import independent_assembly as A

HERE = Path(__file__).resolve().parent
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(100000)
PIN = '2c4a380126640abfcdce398ced255d1dd5d1d007'
GRID = 10**15
COMPLEX = Q(656348434433, 1000000000000000)
COARSE = Q(660025378359, 1000000000000000)
ATOM = Q(41225961513, 62500000000000)
KAPPA = Q(655917923729, 1000000000000000)
ETA = BETA = PHASE_GAP = Q(1, GRID)
BASELINE = Q(13118356069, 20000000000000)
FIXED_HASHES = {
    'inputs/paired-cube-sinks-input.json': '17c190e8a812c2be31a06816fa6f5305d8b82f2ff7ba5a182203f6a19b10f773',
    'inputs/paired-cube-bit-physical-input.json': '6735294e8639da09eb3eb2234cbc5814298442a6c946b5534bcf6e48903547f3',
    'inputs/paired-cube-complex-input.json': 'b1898950f95a7ce618f376d14e628061b345a519e7bcac76b67d277deeec9af5',
    'independent_moments.py': '4d398b4600f7aeaf73a36c68ebc9727de0451399512769282684ae9d4804f594',
    'independent_assembly.py': '99584fe21922926ed9766ec5bc75a06ae531f396bf41ef87baafde248e1f9b9b',
    'LICENSE': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4',
}
SOURCE_FILES = set(FIXED_HASHES) | {'verify.py', 'test_precision.py', 'README.md', 'PROOF.md', 'NOTICE'}


def check_source_manifest(manifest, read_bytes):
    A.require(manifest['upstream_commit'] == PIN, 'Wrong upstream revision label')
    hashes = manifest['source_sha256']
    A.require(type(hashes) is dict and set(hashes) == SOURCE_FILES, 'Incomplete source closure')
    for name, expected in FIXED_HASHES.items():
        A.require(hashes[name] == expected, 'Wrong frozen source pin: ' + name)
    for name, expected in hashes.items():
        A.require(sha256(read_bytes(name)).hexdigest() == expected, 'Source byte mismatch: ' + name)


def paid_profile(row):
    """Reconstruct every paid child, then compare the frozen complete inventory."""
    h, v, roles, loss = (row[k] for k in ('h', 'v', 'physical_R', 'loss'))
    A.require(all(type(x) is int and x > 0 for x in (h, v, roles)), 'Invalid physical dimensions')
    A.require(type(loss) is int and loss >= 0, 'Invalid loss')
    for key in ('R', 'pairs'):
        A.require(type(row[key]) is int and row[key] >= 0, 'Invalid logical/pair stock')
    sinks = row.get('sinks', 0)
    A.require(type(sinks) is int and sinks >= 0, 'Invalid sink count')
    A.require(roles == row['R'] - row['pairs'] - sinks, 'Physical role recount')
    width, stock = 3*h, 2*v+roles
    children = Counter()
    for name in ('local_histogram', 'source_data_histogram', 'target_data_histogram'):
        for rank, count in A.component_histogram(row[name], h).items():
            children[rank] += 3*count
    for rank, count in A.component_histogram(row['physical_gauge_histogram'], h-1).items():
        children[3*rank] += count
    children[2] += 2*v
    children = dict(sorted(children.items()))
    A.require(children == M.normalize_children(row['child_histogram'], width), 'Paid child reconstruction')
    mass = sum(rank*count for rank, count in children.items())
    deficit = width*stock-mass
    A.require((width, stock, mass, deficit) == (row['m'], row['W_per_vertex'],
        row['rank_per_vertex'], row['deficit_per_vertex']), 'Dimension and rank recount')
    A.require(deficit == 2*v-3*loss > 0, 'Shared-core telescoping deficit')
    return dict(width=width, stock=stock, children=children, mass=mass, deficit=deficit)


def arithmetic(complex_row, bit_row, scalar_row):
    cp, bp = paid_profile(complex_row), paid_profile(bit_row)
    complex_bound = M.require_contraction(M.supplier_bounds(
        cp['width'], cp['stock'], cp['children'], COMPLEX))
    bit_bound = M.certify_bit_supplier(bp['width'], bp['stock'], bp['children'], COARSE, atom=ATOM)
    threshold = COARSE/(1+COARSE-M.OLD)
    A.require(ATOM-Q(1, GRID) <= threshold < ATOM, 'Atom is not first strict grid point')
    successors = {}
    for side, p, saving in (('complex', cp, COMPLEX), ('bit', bp, COARSE)):
        bounds = M.supplier_bounds(p['width'], p['stock'], p['children'], saving+Q(1, GRID),
            bad_fraction=M.BAD if side == 'bit' else Q(0),
            fallback_children_per_edge=32*p['width']**2 if side == 'bit' else 0)
        A.require(bounds['total_lower'] >= 1, side + ' supplier successor not rejected')
        successors[side] = dict(saving=saving+Q(1, GRID), total_lower=bounds['total_lower'])
    bridge = A.reconstruct_bridge(scalar_row, complex_row)
    assembled = A.balanced_assembly(bridge, bit_bound['effective_saving'], COMPLEX,
        KAPPA, eta=ETA, beta=BETA, phase_gap=PHASE_GAP)
    minimum = assembled['minimum_margin']
    A.require(KAPPA < minimum <= KAPPA+Q(1, GRID), 'Headline strict grid interval')
    try:
        A.balanced_assembly(bridge, bit_bound['effective_saving'], COMPLEX,
            KAPPA+Q(1, GRID), eta=ETA, beta=BETA, phase_gap=PHASE_GAP)
    except ValueError as error:
        A.require('compact_phase_layer_above_kappa' in str(error), 'Wrong headline successor failure')
    else:
        raise ValueError('Headline successor accepted')
    A.require(KAPPA > BASELINE, 'Refinement does not improve pinned headline')
    return A.serialize(dict(schema_version=1, upstream_commit=PIN, kappa=KAPPA,
        pinned_baseline_kappa=BASELINE, improvement=KAPPA-BASELINE,
        supplier_grid=GRID, atom_grid=GRID, headline_grid=GRID,
        phase_gap=PHASE_GAP, complex_profile=cp, bit_profile=bp,
        complex=complex_bound, bit=bit_bound, atom_threshold=threshold,
        supplier_successors=successors, headline_successor=KAPPA+Q(1, GRID),
        headline_successor_rejected=True, finite_bridge=bridge, assembly=assembled,
        scope='Independent exact arithmetic from pinned stored inventories. Local schedule, phases, uniform compiler, analytic and fixed-tape interfaces remain proof obligations.'))


def regenerate():
    manifest_raw = (HERE/'SOURCE.json').read_bytes()
    check_source_manifest(json.loads(manifest_raw), lambda name: (HERE/name).read_bytes())
    read = lambda name: json.loads((HERE/'inputs'/name).read_bytes())
    result = arithmetic(read('paired-cube-sinks-input.json'),
                        read('paired-cube-bit-physical-input.json'),
                        read('paired-cube-complex-input.json'))
    result['source_manifest_sha256'] = sha256(manifest_raw).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the recomputed precision certificate')
    args = parser.parse_args()
    text = json.dumps(regenerate(), indent=2, sort_keys=True)+'\n'
    path = HERE/'certificate.json'
    if args.write:
        path.write_bytes(text.encode('utf-8'))
    else:
        A.require(path.read_bytes() == text.encode('utf-8'), 'Stored precision certificate differs')
    print('PASS conditional precision kappa=' + str(KAPPA) + '; exact supplier moments, paid inventories, finite bridge, all 47 inequalities and next-grid controls')


if __name__ == '__main__':
    main()
