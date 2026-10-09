#!/usr/bin/env python3
"""Audit balanced/split scalar graphs in independent dense triple coordinates.

Prepared for Thomas DiFiore with OpenAI Codex assistance. Dense support and
literal renumbering checks derive from PR74. Construction credits: Avi
Eisenberg (PR62), eumemic (PR69), Rohan Arun (PR65), Chafik Boukhalfa (PR71),
and Rohan Garg (PR59 split operation). Inherited Apache-2.0 notices remain.
"""
import argparse
import ast
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import sys
import types

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR71 = ROOT/'references/frame-compiler/pr71'
PR69 = ROOT/'references/frame-compiler/pr69'
RECEIPT = HERE/'graph-audit.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def archive_files(folder, expected_commit):
    manifest_path = folder/'SOURCE.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['commit'] == expected_commit
    files = [manifest_path]
    for name, digest in manifest['files'].items():
        path = folder/name
        assert sha256(path.read_bytes()).hexdigest() == digest, name
        files.append(path)
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
    assert reordered.outputs == {target:mapping[node] for target,node in original.outputs.items()}
    return dict(source_ids_unchanged=True,within_frame_original_order_preserved=True,
                selected_frame_order_exact=True,every_original_edge_preserved=True,
                every_original_output_preserved=True)


def audit():
    files = archive_files(PR71, '1bef94fd40a746452548c84a4a8f8834670a3113')
    files += archive_files(PR69, '91aa1f17e6e3fc063241686a41a34ddd0dc24c50')
    provider_path = PR71/'scripts/experiments/split_pair_graph.py'
    provider = load('audit_archived_split_pair_provider', provider_path)
    producer = load('audit_balanced_split_producer', HERE/'producer.py')
    # Independently reconstruct the unnumbered composition from retained inputs.
    # Loading the PR69 driver would execute unrelated compiler imports; its only
    # consumed construction input here is the pair of literal source fragments.
    original_driver = PR69/'scripts/experiments/balanced_coarse_compiler.py'
    fragments = {}
    for statement in ast.parse(original_driver.read_text()).body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in ('BEFORE', 'AFTER'):
                    fragments[target.id] = ast.literal_eval(statement.value)
    assert set(fragments) == {'BEFORE', 'AFTER'}
    original_module = provider._graph
    graph_path = Path(original_module.__file__)
    source = graph_path.read_text()
    assert source.count(fragments['BEFORE']) == 1
    transformed = types.ModuleType('audit_balanced_split_unordered_graph')
    transformed.__file__ = str(graph_path)
    exec(compile(source.replace(fragments['BEFORE'], fragments['AFTER']),
                 str(graph_path)+':balanced-columns', 'exec'), transformed.__dict__)
    axes = {}
    for h in (23, 25):
        provider._graph = original_module
        original = provider.graph(h)
        original_receipt = dense_audit(original)
        provider._graph = transformed
        unnumbered = provider.graph(h)
        unnumbered_receipt = dense_audit(unnumbered)
        reordered = producer.graph(h)
        reordered_receipt = dense_audit(reordered)
        assert unnumbered_receipt == reordered_receipt
        assert original_receipt['prescribed_output_support_sha256'] == reordered_receipt['prescribed_output_support_sha256']
        assert original.inputs == reordered.inputs
        assert set(original.outputs) == set(reordered.outputs)
        axes[str(h)] = dict(original_pr71=original_receipt,
                           combined_reordered=reordered_receipt,
                           identical_input_basis_and_prescribed_output_set=True,
                           prescribed_output_supports_equal_original_pr71=True,
                           combined_before_after_dense_receipts_identical=True,
                           renumbering=renumbering_audit(unnumbered, reordered))
    provider._graph = original_module
    files += [HERE/'producer.py', Path(__file__).resolve()]
    return dict(status='PASS independent dense scalar support and literal renumbering audit',
                axes=axes,
                source_sha256={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest()
                               for path in sorted(set(files))},
                scope='Both finite dimensions; full global triple input basis; every addition has '
                      'disjoint operands; every core/cover is exact; all prescribed output supports '
                      'agree with original PR71; renumbering preserves every literal edge and output. '
                      'Physical words, dirty-basis identity, fixed profiles, exact moment and assembly '
                      'are checked separately. Inherited analytic and all-size transfer hypotheses remain assumed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true', help='Write the deterministic audit receipt.')
    args = parser.parse_args()
    result = audit()
    if args.record:
        RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        assert result == json.loads(RECEIPT.read_text()), 'Graph audit receipt mismatch'
    print('PASS independent balanced/split graph audit h=23 and h=25', flush=True)


if __name__ == '__main__':
    main()
