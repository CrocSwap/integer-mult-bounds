#!/usr/bin/env python3
"""Expose retained arbitrary centers to phase-exact contact compilation.

Apache-2.0. Substantial OpenAI Codex assistance. Credit Cinna Davis #4694,
Cao Yifan #4610, and Dugongue #4841's inverse-image chart convention.
This emits discovery constraints, not a physical supplier certificate.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE / 'vendor'))
import model as M
import retained_verify as R


def build(output):
    raw = (HERE / 'inputs/round3-native.json.gz').read_bytes()
    M.need(sha256(raw).hexdigest() == R.SOURCE_HASH, 'exact retained native bytes')
    p = json.loads(gzip.decompress(raw))
    c = p['canonical']
    frames = c['frames']
    starts, centers, events = R.emit(p)
    nodes, labels, edges = [], [], []
    selected = []

    def new(f, label):
        n = len(nodes)
        nodes.append(f)
        labels.append(label)
        return n

    cur = [new(f, ['entry', r]) for r, f in enumerate(starts)]
    maps = {w['op']: w['G_columns'] for w in c['warps']}
    maps.update({-op: M.inv(g) for op, g in list(maps.items())})
    matrices = [[1 << i for i in range(18)]]
    map_ids = {}
    for op, g in maps.items():
        gi = M.inv(g)
        git = [sum(((gi[j] >> i) & 1) << j for j in range(9)) for i in range(9)]

        def symplectic(v):
            x, z = v & 511, v >> 9
            gx = M.mv(g, x)
            return gx | ((M.mv(git, x ^ z) ^ gx) << 9)

        map_ids[op] = len(matrices)
        matrices.append([symplectic(1 << i) for i in range(18)])

    lags = [M.lagrangian(f, 9) for f in frames]

    def add_edge(a, b, mp=0):
        left = [M.mv(matrices[mp], v) for v in lags[nodes[a]]]
        rank = M.lagrangian_distance(left, lags[nodes[b]], 9)
        edges.append((a, b, rank, 1, mp))

    def move(r, f, dst=None):
        a = cur[r]
        b = new(f, ['transition', r]) if dst is None else dst
        add_edge(a, b)
        cur[r] = b

    # Explicit source transports are combined only into their next actual contact.
    # Every omitted intermediate frame is a source gauge with no logical work.
    # This is exactly #4841's edge model, now applied to all 640 retained roles.
    for i, e in enumerate(events):
        op = e[0]
        if op in ('add', 'scale'):
            refs = e[1:3] if op == 'add' else e[1:2]
            f = e[-1]
            node = new(f, ['contact', i, list(refs)])
            if any(r >= 632 for r in refs):
                selected.append(node)
            for r in refs:
                move(r, f, node)
        elif op == 'warp':
            _, r, symbol, a, b = e
            move(r, a)
            dst = new(b, ['warp', i, r])
            add_edge(cur[r], dst, map_ids[symbol])
            cur[r] = dst
        else:
            M.need(op == 'transport', 'known retained event')

    for r, f in enumerate(c['final'] + [0] * 8):
        move(r, f, new(f, ['exit', r]))
    paid = Counter(rank for a, b, rank, sign, mp in edges if rank)
    M.need(dict(paid) == R.PAID, 'all paid calls including eight center calls')
    helper = Counter(len(frames[c['final'][r]]) - len(frames[c['start'][r]])
                     for r in range(224, 632))
    M.need(dict(helper) == {4: 28, 7: 7, 8: 47, 9: 326}, 'all independent helper targets')
    M.need(len(starts) == 640 and len(centers) == 8, 'all arbitrary persistent inputs')
    selected_set = set(selected)
    lines = [f'{len(nodes)} {len(lags)} {len(matrices)} {len(edges)}']
    lines += [f'{f} {int(n not in selected_set)}' for n, f in enumerate(nodes)]
    lines += [' '.join(map(str, row)) for row in lags + matrices + edges]
    output.mkdir(parents=True, exist_ok=True)
    (output / 'center-contact-graph.txt').write_text('\n'.join(lines) + '\n')
    metadata = dict(source_sha256=sha256(raw).hexdigest(), inputs=640,
                    nodes=len(nodes), edges=len(edges), fixed_nodes=len(nodes)-len(selected),
                    newly_variable_center_contacts=len(selected), selected=selected,
                    paid=dict(sorted(paid.items())), helpers=dict(sorted(helper.items())),
                    independent_center_reward=0, labels=labels)
    (output / 'graph-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    return {k:v for k,v in metadata.items() if k not in ('labels','selected')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output), sort_keys=True))
