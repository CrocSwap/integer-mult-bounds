#!/usr/bin/env python3
"""Regenerate selected F2 producers and compare complete finite certificates.

Requires Python 3.10+ and a C++17 compiler. Only the standard library is used.
All large DAGs, matching dependencies, positive labels, and executables live in
a temporary directory unless --work-dir is supplied. No archived raw DAG is
used as an input. Copyright 2026 icekylinx, Apache-2.0. AI-assisted adaptation
of the partial-swap research handoff and the credited upstream circuit code.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

from partial_swap.graph import graph, export
from partial_swap.positive import run as positive_labels

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).resolve().parent / 'partial_swap'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def complex_histogram(h=28):
    """Count auxiliary transitions from the actual complex side DAG.

    d0 labels are coordinate spaces; d2 pair stars have independent triple
    indicators. Each full-frame center role contributes three rank-h edges.
    This histogram excludes the separately counted data/macro transitions.
    """
    from paired_complex import PairedComplex
    circuit = PairedComplex(h)
    degree = [0] * len(circuit.args)
    ranks = [0] * len(circuit.args)
    for node in sorted(circuit.active):
        kind = circuit.kind[node]
        ranks[node] = (1 if kind == 'in' else circuit.cover(node).bit_count()
                       if kind == 'd0' else circuit.support[node].bit_count())
        if circuit.args[node]:
            for operand in circuit.args[node]:
                degree[operand] += 1
    for _, node, _ in circuit.pieces:
        degree[node] += 1
    hist = [0] * (h+1)
    for node in sorted(circuit.active):
        r = ranks[node]
        if circuit.args[node]:
            hist[r] += degree[node]-1
            hist[h-r] += 1
            for operand in circuit.args[node]:
                require(r >= ranks[operand], 'Complex frame dimensions decrease')
                hist[r-ranks[operand]] += 1
        else:
            hist[1] += degree[node]
    for _, node, _ in circuit.pieces:
        r = ranks[node]
        require(r < h, 'Complex injection frame is too large')
        hist[h-1-r] += 1
        hist[1] += 1
    hist[h] += 3 * (h+1)
    rank_sum = sum(r*n for r, n in enumerate(hist))
    require(rank_sum == h*(circuit.roles+h+1)+2*h*(h+1),
            'Complex rank identity failed')
    return dict(h=h, v=len(circuit.triples), roles=circuit.roles,
                center_roles=h+1, rank_sum=rank_sum, histogram=hist)


def regenerate(work, certificate, dimensions, compiler, include_complex=True):
    require(sys.flags.optimize == 0, 'Run without -O: mathematical assertions must remain enabled')
    programs = {}
    for name in ('match_exported_dag', 'match_positive_dag'):
        programs[name] = work / name
        subprocess.run([*shlex.split(compiler), '-O3', '-std=c++17',
                        str(SOURCE / (name+'.cpp')), '-o', str(programs[name])], check=True)
    results = {}
    for h in dimensions:
        print(f'Regenerating h={h}: scalar DAG', file=sys.stderr, flush=True)
        circuit = graph(h)
        scalar = circuit.verify()
        dag = work / f'triple_base2_{h}.bin'
        export(circuit, dag)
        del circuit
        gc.collect()
        original = json.loads(subprocess.check_output(
            [str(programs['match_exported_dag']), str(dag), str(dag)+'.links'], text=True))
        print(f'Regenerating h={h}: positive labels', file=sys.stderr, flush=True)
        labels = positive_labels(str(dag))
        gc.collect()
        matched = json.loads(subprocess.check_output(
            [str(programs['match_positive_dag']), str(dag), str(dag)+'.positive'], text=True))
        expected = certificate['producers'][str(h)]
        for actual_key, expected_key in (
                ('v', 'v'), ('c', 'additions'), ('q', 'outputs'),
                ('matched', 'matches'), ('R', 'roles'), ('loss', 'loss'),
                ('histogram', 'histogram')):
            require(matched[actual_key] == expected[expected_key],
                    f'h={h}: certificate mismatch for {expected_key}')
        require(original['matched'] == matched['matched'],
                f'h={h}: positive enlargement changed the selected matching count')
        require(matched['loss'] == h*(h-1), f'h={h}: retained-total loss mismatch')
        require(matched['rank_sum'] == h*matched['R']+2*h*(h-1),
                f'h={h}: rank identity mismatch')
        results[str(h)] = dict(**matched, labels=labels, scalar=scalar,
                               envelope_matching=original, certificate_equal=True)
        (work / f'triple_base2_{h}.counts.json').write_text(
            json.dumps(results[str(h)], indent=2)+'\n')
    answer = dict(producers=results, regenerated_from_source=True)
    if include_complex:
        print('Regenerating complex h=28 histogram', file=sys.stderr, flush=True)
        result = complex_histogram(certificate['complex']['h'])
        require(result['histogram'] == certificate['complex']['histogram'],
                'Complex histogram differs from certificate')
        require(result['v'] == certificate['complex']['v'], 'Complex source count mismatch')
        require(result['v']**2*(result['roles']+result['center_roles']) == certificate['complex']['B'],
                'Complex role count mismatch')
        answer['complex'] = dict(**result, certificate_equal=True)
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path,
                        default=ROOT/'certificates'/'partial-swap-input.json')
    parser.add_argument('--dimensions', nargs='+', type=int, choices=(25, 23, 57),
                        default=[25, 23, 57])
    parser.add_argument('--cxx', default=os.environ.get('CXX', 'c++'))
    parser.add_argument('--work-dir', type=Path, help='Keep generated intermediate files here')
    parser.add_argument('--skip-complex', action='store_true')
    parser.add_argument('--output', type=Path, help='Write the complete JSON report to this file')
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text())
    def run(work):
        return regenerate(work, certificate, args.dimensions, args.cxx, not args.skip_complex)
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = run(args.work_dir.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='partial-swap-') as directory:
            result = run(Path(directory))
    encoded = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
