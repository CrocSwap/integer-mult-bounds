#!/usr/bin/env python3
"""Audit the final balanced graph using dense global triple coefficients.

Run from the repository root:
  python3 scripts/experiments/pr62_exploration/audit_balanced_coarse.py \
      --check certificates/balanced-coarse-independent-audit.json

No physical compilation is run. This audit reconstructs source coefficients,
common cores and covers directly through the scalar DAG. It does not use
the producer's local-support or cross-common-point provenance routines.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts/experiments'))
import balanced_coarse_compiler as producer


def source_hashes():
    """Check all manifest dependencies independently and retain exact hashes."""
    pending = [producer.PIN / 'SOURCE.json']
    paths = {Path(__file__).resolve()}
    visited = set()
    while pending:
        manifest = pending.pop().resolve()
        if manifest in visited:
            continue
        visited.add(manifest)
        paths.add(manifest)
        data = json.loads(manifest.read_text())
        for name, expected in data['files'].items():
            path = (manifest.parent / name).resolve()
            assert sha256(path.read_bytes()).hexdigest() == expected, f'Changed source: {path}'
            paths.add(path)
        if 'shared_dependency_manifest' in data:
            dependency = (manifest.parent / data['shared_dependency_manifest']).resolve()
            assert sha256(dependency.read_bytes()).hexdigest() == data['shared_dependency_manifest_sha256'], dependency
            pending.append(dependency)
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def audit(h):
    circuit = producer.graph(h)
    triples = list(combinations(range(h), 3))
    assert circuit.h == h and circuit.inputs == triples
    n = len(triples)
    expected_keys = {(p, (p,)) for p in range(h)}
    expected_keys.update((p, tuple(sorted((p, a, b))))
                         for p in range(h)
                         for a, b in combinations([v for v in range(h) if v != p], 2))
    assert set(circuit.outputs) == expected_keys

    # Reconstruct the reachable node set from the output ports.
    active = set()
    stack = list(circuit.outputs.values())
    while stack:
        node = stack.pop()
        if node in active:
            continue
        assert 0 < node < len(circuit.args)
        active.add(node)
        if circuit.args[node] is not None:
            stack.extend(circuit.args[node])
    assert active == circuit.active

    signals = {}
    cores = {}
    covers = {}
    additions = 0
    digest = sha256()
    width = (n + 7) // 8
    for node in sorted(active):
        operands = circuit.args[node]
        if operands is None:
            assert 1 <= node <= n
            signals[node] = 1 << (node - 1)
            cores[node] = covers[node] = sum(1 << v for v in triples[node - 1])
        else:
            a, b = operands
            assert 0 < a < node and 0 < b < node
            assert not signals[a] & signals[b], f'Overlapping addition at {node}'
            signals[node] = signals[a] ^ signals[b]
            cores[node] = cores[a] & cores[b]
            covers[node] = covers[a] | covers[b]
            additions += 1
        assert cores[node], f'No common point at {node}'
        assert circuit.core[node] == cores[node], f'Wrong core at {node}'
        assert circuit.union[node] == covers[node], f'Wrong cover at {node}'
        digest.update(json.dumps((node, operands, cores[node], covers[node]), separators=(',', ':')).encode() + b'\n')
        digest.update(signals[node].to_bytes(width, 'little'))
    assert additions == circuit.additions
    assert {node for node in active if circuit.args[node] is None} == set(range(1, n + 1))

    for (common, target), node in sorted(circuit.outputs.items()):
        omitted = set(target) - {common}
        expected = sum(1 << j for j, triple in enumerate(triples)
                       if common in triple and not omitted.intersection(triple))
        assert signals[node] == expected, f'Wrong output {(common, target)}'
        digest.update(json.dumps((common, target, node), separators=(',', ':')).encode() + b'\n')

    return dict(h=h, inputs=n, outputs=len(expected_keys), active_nodes=len(active),
                additions=additions, direct_global_coefficient_sha256=digest.hexdigest(),
                all_additions_disjoint=True, all_output_coefficients_exact=True,
                all_cores_and_covers_exact=True, every_node_has_common_point=True,
                complete_output_inventory=True, active_set_exact=True,
                scope='Scalar DAG only; physical dirty-role and profile checks are separate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Save the receipt instead of printing it.')
    parser.add_argument('--check', type=Path, help='Require an exact match to an existing receipt.')
    args = parser.parse_args()
    hashes = source_hashes()
    rows = [audit(h) for h in (23, 25)]
    assert source_hashes() == hashes, 'Sources changed during the audit'
    receipt = dict(source_hashes=hashes, results=rows,
                   scope='Independent dense global scalar coefficients and core/cover audit of balanced_coarse_compiler.graph. No compilation or new kappa calculation.')
    if args.check:
        assert receipt == json.loads(args.check.read_text()), 'Audit receipt differs'
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded)
    elif not args.check:
        print(encoded, end='')
    print('Independent balanced-coarse scalar audit passed at h=23 and h=25.', file=sys.stderr)


if __name__ == '__main__':
    main()
