#!/usr/bin/env python3
"""Merge two pairs of singleton bit outputs and regenerate their physical word.

Apache-2.0. huxint, with substantial OpenAI Codex assistance.
The output-merging idea is adapted from eumemic's complex construction in
PR161 and the bit composition published in huxint's PR170. This version uses
PR168's new pair module and nested-prefix all-but-one module. The bit graph,
compiler, frame exporter and checker retain eumemic's and icekylinx's credits.

For each target merge (face1, edge01) and (face2, edge02), retaining one
singleton read per pair. Additions have disjoint source supports and each
merged value has exactly the original XOR contribution at that target.
The two-input sums share DAG nodes between equal selector pairs. Their
reads stay at singleton caps; the partner-pair delivery schedule is retained.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'research/paired-cube-bit'))
import paired_cube_bit_word as gen
from check_paired_cube_bit import Checker

P = 12
SPECS = (('face1', 'edge01'), ('face2', 'edge02'))
FILES = ('graph', 'word', 'frames', 'kchron', 'profile')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def merged_graph():
    module = gen.HERE / 'data' / gen.MODULES[P]
    builder = gen.BitGraph(P)
    original = builder.finish(json.loads(module.read_text()), gen.nested_prefix(P-2))
    need(gen.check_decoder(original) == 0, 'Original exact mod-2 decoder')
    groups = {channel: k for k, spec in enumerate(SPECS) for channel in spec}
    found, keep, centers = {}, [], []
    for root in original['roots']:
        if root['kind'] == 'center':
            centers.append(root)
        elif root['channel'] in groups:
            need(len(root['targets']) == 1, 'Only singleton roots may be merged')
            key = (groups[root['channel']], root['targets'][0], root['channel'])
            need(key not in found, 'Duplicate singleton channel')
            found[key] = root['node']
        else:
            keep.append(root)
    merged, multiplicity = [], Counter()
    for group, target in sorted({(k, t) for k, t, _ in found}):
        left, right = (found[group, target, c] for c in SPECS[group])
        need(not builder.s[left] & builder.s[right], 'Disjoint merged supports')
        node = builder.add(left, right)
        need(builder.s[node] == builder.s[left] ^ builder.s[right], 'Exact merged contribution')
        merged.append(dict(node=node, targets=[target], kind='side', channel='paired'+str(group)))
        multiplicity[target] += 1
    need(multiplicity == Counter({t: 2 for t in range(original['v'])}),
         'Both channel pairs merged at every target')
    graph = dict(original, roots=keep+merged+centers, args=builder.a)
    need(gen.check_decoder(graph) == 0, 'Merged exact mod-2 decoder')
    return graph, dict(p=P, h=graph['h'], v=graph['v'],
                       merged_channel_pairs=[list(s) for s in SPECS],
                       merged_reads=len(merged), original_roots=len(original['roots']),
                       merged_roots=len(graph['roots']),
                       pair_module_sha256=sha256(module.read_bytes()).hexdigest())


def regenerate(output, frozen_arcs, *, check=False):
    """Rebuild all five checker inputs; no frame/role inventory is trusted."""
    need(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    graph, merge_receipt = merged_graph()
    profile, witness = gen.compile_word(graph, frozen=frozen_arcs, plain_k=8)
    gauges, internal, target, word = gen.select_gauges(graph, profile, witness)
    row = gen.profile(profile, gauges, internal, target)
    arcs = sorted([x-1, witness['usecode'][u]] for x, u in witness['arcs'].items())
    if frozen_arcs is not None:
        need(arcs == sorted(frozen_arcs), 'Frozen carrier arcs replayed exactly')
    # Modular tests here are discovery guards. The independent checker below
    # completes every rational frame and tests its Gram matrix over Q.
    cache, geometry = {}, witness['geo']
    need(all(gen.nondeg_id(geometry, geometry.perp(witness['ann'][x]), cache)
             for x in witness['order']), 'Nondegenerate node frames')
    need(all(gen.nondeg_id(geometry, frame, cache) for frame in witness['rframe']),
         'Nondegenerate root frames')
    exported = gen.export(P, graph, profile, witness, word, row)
    exported['profile'] = row
    output.mkdir(parents=True, exist_ok=True)
    encoded = {name+'_p%d.json' % P: gen.dumps(exported[name]) for name in FILES}
    for name, data in encoded.items():
        path = output / name
        if check:
            need(path.read_text() == data, 'Byte-identical regeneration: '+name)
        else:
            path.write_text(data)
    checked = Checker(output, P).run()
    need((checked['roles'], checked['W'], checked['m'], checked['deficit']) ==
         (row['R'], row['W_per_vertex'], row['m'], row['deficit_per_vertex']),
         'Independently reconstructed merged bit inventory')
    return dict(merge=merge_receipt, checked=checked, arcs=arcs,
                input_sha256={name: sha256(data.encode()).hexdigest() for name, data in encoded.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'build/paired-cube-lifetime/merge-paired')
    parser.add_argument('--arcs', type=Path, default=HERE/'selected/bit/arcs.json')
    parser.add_argument('--solve-matching', action='store_true', help='Discovery only; write the resulting arcs')
    parser.add_argument('--check', action='store_true', help='Rebuild and compare the five existing files byte for byte')
    args = parser.parse_args()
    need(not sys.flags.optimize, 'Run without -O; assertions must remain enabled')
    frozen = None if args.solve_matching else json.loads(args.arcs.read_text())
    result = regenerate(args.out, frozen, check=args.check)
    if args.solve_matching:
        args.arcs.parent.mkdir(parents=True, exist_ok=True)
        args.arcs.write_text(gen.dumps(result['arcs']))
    print('PASS merged bit word: %d roles, W=%d; full rational-frame checker and deterministic source reconstruction'
          % (result['checked']['roles'], result['checked']['W']))


if __name__ == '__main__':
    main()
