#!/usr/bin/env python3
"""Independently audit aligned split graphs in dense global triple coordinates.

Prepared for Thomas DiFiore with OpenAI Codex assistance. Dense support and
literal renumbering checks derive from PR74. Inherited construction credits:
Avi Eisenberg PR62; eumemic PR69; Rohan Arun PR65; Chafik Boukhalfa PR71;
Rohan Garg PR59. Original sources and Apache-2.0 notices remain preserved.
"""
import argparse
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT/'references/frame-compiler/pr71'
RECEIPT = HERE/'graph-audit.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_files():
    path = ARCHIVE/'SOURCE.json'
    manifest = json.loads(path.read_text())
    assert manifest['commit'] == '1bef94fd40a746452548c84a4a8f8834670a3113'
    files = [path]
    for name, expected in manifest['files'].items():
        source = ARCHIVE/name
        assert sha256(source.read_bytes()).hexdigest() == expected, name
        files.append(source)
    return files


def dense_audit(c):
    """Avoid the producer's local support and provenance helper functions."""
    triples = list(combinations(range(c.h), 3))
    assert c.inputs == triples
    variables = len(triples)
    assert c.variables == {triple:i+1 for i,triple in enumerate(triples)}
    width = (variables+7)//8
    frame_width = (c.h+7)//8
    signals = {}
    incident = [0]*c.h
    for i,triple in enumerate(triples):
        signals[i+1] = 1<<i
        for point in triple:
            incident[point] |= 1<<i
    additions, frames, sources = [], [], set()
    for node in sorted(c.active):
        args = c.args[node]
        if args:
            a,b = args
            assert a in c.active and b in c.active
            assert a<node and b<node
            assert not signals[a]&signals[b]
            signals[node] = signals[a]|signals[b]
            assert c.core[node] == c.core[a]&c.core[b]
            assert c.union[node] == c.union[a]|c.union[b]
            operands = sorted((signals[a],signals[b]))
            additions.append(sha256(b''.join(
                value.to_bytes(width,'little') for value in [signals[node],*operands])).digest())
        else:
            assert 1<=node<=variables
            sources.add(node)
            mask = sum(1<<point for point in triples[node-1])
            assert c.core[node] == c.union[node] == mask
        assert c.core[node]
        frames.append(sha256(
            c.core[node].to_bytes(frame_width,'little')
            +c.union[node].to_bytes(frame_width,'little')
            +signals[node].to_bytes(width,'little')).digest())
    assert sources == set(range(1,variables+1))
    expected_targets = {(common,(common,)) for common in range(c.h)}
    expected_targets.update((common,triple) for triple in triples for common in triple)
    assert set(c.outputs) == expected_targets
    output_records = []
    for (common,target),node in sorted(c.outputs.items()):
        assert node in c.active
        expected = incident[common]
        for point in target:
            if point != common:
                expected &= ~incident[point]
        assert signals[node] == expected
        output_records.append((common,target,sha256(expected.to_bytes(width,'little')).hexdigest()))
    return dict(h=c.h, inputs=variables, active_nodes=len(c.active),
                additions=len(additions), outputs=len(c.outputs),
                every_source_coordinate_exact=True,
                every_operand_id_strictly_earlier=True,
                all_additions_disjoint_in_dense_global_coordinates=True,
                all_core_and_cover_recurrences_exact=True,
                complete_prescribed_output_set=True,
                every_prescribed_output_support_exact=True,
                addition_support_and_operand_multiset_sha256=sha256(b''.join(sorted(additions))).hexdigest(),
                frame_and_support_multiset_sha256=sha256(b''.join(sorted(frames))).hexdigest(),
                prescribed_output_support_sha256=sha256(json.dumps(
                    output_records,separators=(',',':')).encode()).hexdigest())


def renumbering_audit(original, reordered):
    """Check source IDs, the selected frame order, and each literal old edge."""
    groups = {}
    for node in sorted(original.active):
        if original.args[node]:
            groups.setdefault((original.core[node],original.union[node]),[]).append(node)
    def key(item):
        (core,cover),nodes = item
        return cover.bit_count()-core.bit_count(), -core, cover, min(nodes)
    variables = len(original.inputs)
    ids = list(range(variables+1)) + [node
        for _,nodes in sorted(groups.items(),key=key) for node in nodes]
    mapping = {node:i for i,node in enumerate(ids)}
    assert len(mapping) == len(ids)
    assert all(mapping[i]==i for i in range(variables+1))
    assert reordered.active == {mapping[node] for node in original.active}
    assert len(reordered.args) == len(ids)
    for old,new in mapping.items():
        expected = tuple(mapping[x] for x in original.args[old]) if original.args[old] else None
        assert reordered.args[new] == expected
        assert reordered.core[new] == original.core[old]
        assert reordered.union[new] == original.union[old]
        assert reordered.provenance[new] == original.provenance[old]
    assert reordered.outputs == {target:mapping[node] for target,node in original.outputs.items()}
    return dict(source_ids_unchanged=True,within_frame_original_order_preserved=True,
                selected_frame_order_exact=True,every_original_edge_preserved=True,
                every_original_output_preserved=True, every_original_provenance_record_preserved=True)


def audit():
    files = archive_files() + [HERE/'partition_graph.py',HERE/'selection.json',Path(__file__).resolve()]
    hashes = {str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest()
              for path in sorted(set(files))}
    partition = load('audited_aligned_partition', HERE/'partition_graph.py')
    original = load('audit_original_pr71', ARCHIVE/'scripts/experiments/split_pair_graph.py')
    assert partition.SPLITS == {23:6, 25:9}
    axes = {}
    for h in (23, 25):
        baseline = original.graph(h)
        before = partition.graph(h, ordered=False)
        after = partition.graph(h, ordered=True)
        baseline_receipt = dense_audit(baseline)
        before_receipt = dense_audit(before)
        after_receipt = dense_audit(after)
        assert before_receipt == after_receipt
        assert baseline.inputs == before.inputs == after.inputs
        assert set(baseline.outputs) == set(before.outputs) == set(after.outputs)
        assert baseline_receipt['prescribed_output_support_sha256'] == after_receipt['prescribed_output_support_sha256']
        axes[str(h)] = dict(
            initial_pair_splits=partition.SPLITS[h],
            selected_partition={key:json.loads((HERE/'selection.json').read_text())['axes'][str(h)][key] for key in ('groups','anchor_pairs','coarse_word','expected_scalar_sha256')},
            original_pr71=baseline_receipt,
            aligned_partition=after_receipt,
            identical_input_basis_and_prescribed_output_set=True,
            prescribed_output_supports_equal_original_pr71=True,
            original_and_reordered_dense_receipts_identical=True,
            renumbering=renumbering_audit(before, after))
    for name, expected in hashes.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    return dict(
        status='PASS independent dense scalar support and literal renumbering audit',
        axes=axes, source_sha256=hashes,
        independence='The dense checker does not call the graph producer support or provenance '
                     'helpers. It independently expands every node into the complete global input '
                     'basis and checks every source, edge, disjoint sum, frame recurrence and '
                     'prescribed output. Ordered and unordered graphs come from the same frozen '
                     'factory; exact dense output checks and an independently reconstructed '
                     'literal node mapping validate them.',
        scope='Both finite dimensions. The scalar target is identical to original PR71. '
              'Physical words, dirty-basis identities, carry exchanges, fixed profiles, exact '
              'moments and assembly are separate checks. Inherited analytic and all-size '
              'transfer hypotheses remain assumed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='Write the deterministic audit receipt.')
    args = parser.parse_args()
    result = audit()
    if args.record:
        RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert result == json.loads(RECEIPT.read_text()), 'Graph audit receipt mismatch'
    print('PASS independent aligned-partition graph audit h=23 and h=25', flush=True)


if __name__ == '__main__':
    main()
