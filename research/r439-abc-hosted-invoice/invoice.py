#!/usr/bin/env python3
"""Bit-only nine-stage invoice, adapted from PR510 assemble9.py.

Arithmetic and moment engines: DreamingOfClouds/PR510, the PR463/493 chain,
and their disclosed AI assistance. Apache-2.0. This omits only the unrelated
cited complex/outer assembly loop. Matthieu Pascal, with OpenAI Codex assistance.
"""
import ast
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import sys


def need(ok, message):
    if not ok:
        raise ValueError(message)


def compute(root, work):
    read = lambda p: json.loads(p.read_text())
    pg = read(work / 'v9/nine/GLOBAL.json')
    bg = read(work / 'v9/hosted/GLOBAL.json')
    audit = read(work / 'v9/hosted/AUDIT.json')
    geo = read(work / 'v9/nine/GEOMETRY.json')
    need(audit['status'] == 'PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT', 'hosted audit')
    need(audit['template_sha256'] == bg['template_sha256'], 'audited template')
    P = {int(r): n for r, n in audit['profile'].items()}
    m, W, T, R, V = bg['m'], audit['live'], pg['replicas'], pg['R'], pg['v']
    L = (m - 1) // 7
    K, depth = (L - 1) // 2, bg['halving_depth']
    E = sum(P.values())
    mass = sum(r * n for r, n in P.items())
    need((m, T, R, V, L, W, depth) == (64, 32, 439, 111, 9, 28416, 2), 'fixed model')
    need(m * W - mass == audit['deficit'] == T * (2 * K * V - L * 63), 'rank mass')
    physical, d, N = W + 9, m * m, 2 * m
    unit = L * T * pg['local_additions'] + pg['bridge_additions']
    J = 8 * T * L * (2 * V + R) + 8 * (2 * K * V * T) + 2 * L * T * R + 2 * pg['copy_erase_episodes']
    high, good, compiler = 16 * (d + 1) ** 2, 8 * m * m + 8, 128 * N ** 3
    selectors = 2 * L * T * ((W - 1) + R * m * (geo['max_route_factors'] + 144 + 2 + (m - 1) + m))
    prefix = int(pg['global_prefix_bound'])
    charged_prefix = 64 * ((prefix.bit_length() + 63) // 64)
    terms = dict(scalar_additions=unit, high_precision=J * high, physical_store=J * physical,
                 child_compiler=E * (good + compiler), addresses=16 * m ** 3,
                 copy_erase=pg['copy_erase_episodes'], selectors=selectors, prefix=prefix, constant=1)
    coefficient = sum(terms.values())
    two = (coefficient + 1) ** depth * (E + 1) ** depth
    charged_two = 512 if two.bit_length() <= 512 else 64 * ((two.bit_length() + 63) // 64)
    row = depth * (m * m + 1) + 9909 + 252
    need(prefix < 1 << 192 and charged_prefix == 192, 'nine-stage precision')
    need(two < 1 << 512 and charged_two == 512, 'two-level precision')
    need(2 * max(P) ** depth < m ** depth and row == 18355 < 20161, 'child and row guards')
    engines = root / 'research/e8-bit-carrier-skeleton/code/hub/e8-r740-replica32/code/engines'
    def load(name):
        spec = importlib.util.spec_from_file_location(name, engines / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    M, Other = load('moment'), load('base_two_moment')
    enclosure = M.certify(P, m, W, True)
    c, chi = Q(enclosure['lower']), Q(enclosure['upper'])
    need(c == Q(1733427039589844234749, 10**24), 'unchanged PR589 bit moment')
    fallback = 32 * m * m * E
    lo, hi = Other.moment(m, W, list(P.items()), c)
    bl, bh = Other.moment(m, W, [(1, fallback)], c)
    lo2, hi2 = Other.moment(m, W, list(P.items()), chi)
    bl2, bh2 = Other.moment(m, W, [(1, fallback)], chi)
    need(hi + bh / 10**16 < 1 < lo2 + bl2 / 10**16, 'moment grid brackets')
    result = dict(profile={str(k): v for k, v in sorted(P.items())}, paid_calls=E,
                live=W, physical=physical, rank_mass=mass, deficit=audit['deficit'],
                bit_lower=str(c), next_grid_point_rejected=str(chi), invoice_terms=terms,
                J=J, coefficient=coefficient, two_level_coefficient=two,
                prefix_bits=prefix.bit_length(), charged_prefix_bits=charged_prefix,
                coefficient_bits=coefficient.bit_length(), two_level_bits=two.bit_length(),
                charged_two_level_bits=charged_two, row_coefficient=row,
                maxchild=max(P), halving_depth=depth, new_kappa=False)
    # Execute every statement of the unchanged adapted PR510 bit-invoice
    # prelude, stopping immediately after its `res` assignment. Its subsequent
    # loop assembles historical complex suppliers and is outside this task.
    reference = work / 'a9p/assemble9.py'
    tree = ast.parse(reference.read_text(), filename=str(reference))
    stops = [i for i, node in enumerate(tree.body) if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'res' for t in node.targets)]
    need(len(stops) == 1, 'reference bit-invoice boundary')
    tree.body = tree.body[:stops[0] + 1]
    argv = sys.argv
    namespace = {'__name__': 'reference_bit_invoice'}
    try:
        sys.argv = [str(reference), str(work / 'v9'), str(work / 'v9/hosted'),
                    str(work / 'v9/hosted/AUDIT.json'),
                    str(root / 'research/e8-bit-carrier-skeleton'), str(work / 'unused.json'), '']
        exec(compile(tree, str(reference), 'exec'), namespace)
    finally:
        sys.argv = argv
    ref = namespace['res']
    need(ref['bit_profile'] == result['profile'] and ref['bit_lower'] == result['bit_lower']
         and ref['next_grid_point_rejected'] == result['next_grid_point_rejected'], 'reference moment')
    for key in ('prefix_bits', 'charged_prefix_bits', 'coefficient_bits', 'row_coefficient'):
        need(ref['bit'][key] == result[key], 'reference invoice ' + key)
    need(namespace['coefficient'] == coefficient and namespace['two'] == two
         and namespace['unit'] == unit and namespace['J'] == J
         and namespace['selectors'] == selectors, 'reference exact invoice integers')
    result['unchanged_reference_bit_invoice_agrees'] = True
    return result


if __name__ == '__main__':
    root, work, out = map(Path, sys.argv[1:])
    out.write_text(json.dumps(compute(root, work), indent=2) + '\n')
    print('PASS_R439_ABC_BIT_INVOICE')
