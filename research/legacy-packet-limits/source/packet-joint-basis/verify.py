#!/usr/bin/env python3
"""Check the frozen negative receipt with a second exact matrix engine.

This checker does not import the producer. Prepared with OpenAI Codex.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from itertools import combinations
import json
from pathlib import Path
import time
import sympy as sp


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run', type=Path, required=True)
    ap.add_argument('--receipt', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    require(__debug__, 'Assertions must be enabled.')
    require(not args.out.exists(), 'Use a new result file.')
    started = time.monotonic()
    data = args.run/'baseline535/source531/research/direct-delivery504-global/inputs/hamming'
    geometry = json.loads((data/'PROTOTYPE.json').read_text())
    modules = json.loads(gzip.decompress((data/'PACKET-PROGRAMS.json.gz').read_bytes()))
    receipt = json.loads(args.receipt.read_text())
    roots, ports = geometry['root_lines'], geometry['binary_ports']
    checked = []
    for module, row in zip(modules, receipt['blocks'], strict=True):
        ids = module['receipt']['source_lines']
        block = module['receipt']['block']
        matrix = sp.Matrix.vstack(sp.eye(8), sp.zeros(16, 8))
        for target, source, numerator, denominator in module['events'][:40]:
            matrix[target, :] += sp.Rational(numerator, denominator)*matrix[source, :]
        subsets, independent = 0, 0
        for parity, expected in enumerate(row['candidate_bases']):
            targets = [s for s in ids if sum(roots[s][i] < 0 for i in block)%2 == parity]
            sources = [s for s in ids if s not in targets]
            source_columns = [ids.index(s) for s in sources]
            candidates = [i for i in range(24)
                          if all(not matrix[i, j] for j in range(8) if j not in source_columns)]
            require(len(candidates) == 12, 'The literal partial row set has changed.')
            own = sp.Matrix([[-sp.Rational(sum(a*b for a, b in zip(roots[t], roots[s])), 4)
                              for s in sources] for t in targets])
            classes = Counter()
            for registers in combinations(candidates, 4):
                subsets += 1
                query = matrix.extract(registers, source_columns)
                if not query.det():
                    continue
                independent += 1
                output = own*query.inv()
                # Connected components are found by graph closure, rather
                # than the producer's disjoint-set routine.
                adjacency = [{i} for i in range(4)]
                for j in range(4):
                    support = {i for i in range(4) if output[i, j]}
                    for i in support:
                        adjacency[i] |= support
                while True:
                    expanded = [set.union(*(adjacency[j] for j in group)) for group in adjacency]
                    if expanded == adjacency:
                        break
                    adjacency = expanded
                components = set(map(frozenset, adjacency))
                sizes = tuple(sorted(map(len, components)))
                classes[sizes] += 1
                require(sizes in ((2, 2), (4,)), 'A new output component type has appeared.')
                for component in components:
                    if len(component) == 4:
                        # Every other non-disjoint Hamming block meets this
                        # block in two coordinates. A cross source has two
                        # nonzero Gram entries and two zero entries against
                        # an orthogonal tetrahedron, so no such source can
                        # enter the common binary output cap.
                        for other in modules:
                            if len(set(other['receipt']['block']) & set(block)) != 2:
                                continue
                            for s in other['receipt']['source_lines']:
                                dots = [sum(a*b for a, b in zip(roots[s], roots[t])) for t in targets]
                                require(sum(bool(x) for x in dots) == 2, 'The cross-source support count is wrong.')
                                require(any((ports[s] & ports[t]).bit_count()%2 for t in targets),
                                        'A cross source entered the full output cap.')
            require(expected['component_counts'] == {str(k): v for k, v in classes.items()},
                    'The producer component counts are wrong.')
        require(subsets == 990 and independent == 630, 'The exact basis count is wrong.')
        for claimed in row['paired_results']:
            protected = set(claimed['left']+claimed['right'])
            donors = [event[1] for event in module['events'][40:]
                      if not protected & set(event[:2])]
            retired = matrix.extract(donors, range(8))
            totals = sp.Matrix([[roots[s][i] for s in ids] for i in block])
            deficit = retired.col_join(totals).rank()-retired.rank()
            require(deficit == claimed['center_rank_deficit'], 'An unpaid center direction was claimed free.')
        checked.append(dict(block=block, subsets=subsets, bases=independent, center_cases=len(row['paired_results'])))
    # These controls alter mathematical claims, not input hashes or paths.
    case = next(claim for block in receipt['blocks'] for claim in block['paired_results']
                if claim['center_rank_deficit'] == 4)
    require(case['optimistic_helpers']-case['center_rank_deficit'] == 32,
            'The no-cost center mutation did not reach its false lower inventory.')
    control = receipt['negative_control']
    require(all(not (vector & ports[target]).bit_count()%2
                for vector in control['required_cap']
                for target in receipt['blocks'][0]['candidate_bases'][0]['tetrahedron']),
            'The printed output cap includes a forbidden restored direction.')
    require(any((ports[control['source']] & ports[t]).bit_count()%2
                for t in receipt['blocks'][0]['candidate_bases'][0]['tetrahedron']),
            'The dense output frame control does not reject a real source column.')
    controls = [dict(name='Remove four required center directions', rejected=True,
                     reason='Exact quotient rank is four, rather than zero'),
                dict(name='Replace the dense output cap by the full frame', rejected=True,
                     reason='A required source port has nonzero binary pairing with a restored output')]
    args.out.write_text(json.dumps(dict(status='PASS_SECOND_EXACT_ENGINE', elapsed_seconds=round(time.monotonic()-started, 6),
                                        blocks=checked, controls=controls, sympy_version=sp.__version__,
                                        source_helpers_arbitrary_state_checked=False, kappa_gain=False), indent=2)+'\n')
    print(json.dumps(dict(status='PASS_SECOND_EXACT_ENGINE', blocks=len(checked), controls=len(controls),
                         elapsed_seconds=round(time.monotonic()-started, 6))))


if __name__ == '__main__':
    main()
