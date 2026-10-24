#!/usr/bin/env python3
"""Reconstruct the finite path certificate; refuse occupied outputs.

Apache-2.0. Substantial OpenAI Codex assistance. Classical BFS and binary
linear algebra; credits and scope are in README.md and PROOF.md.
"""
from collections import defaultdict, deque
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prelude_path_checker', HERE / 'verify.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def generate():
    payload = V.authenticate((V.ROOT / V.SOURCE).read_bytes())
    word, links = V.skeleton(payload, 'forward')
    c = payload['canonical']; frames = c['frames']
    adjacent = defaultdict(list)
    for a, b in links:
        adjacent[a].append(b)
    cases = []
    for op in range(47, 59):
        pre = next(i for i, e in enumerate(word) if e[0] == 'warp' and e[2] == op
                   and len(frames[e[3]]) == 1)
        role = word[pre][1][1]; first = pre + 1; start = ('scalar', first)
        case = dict(operator=op, prelude_event=pre, first_scalar_event=first,
                    source_role=role, input_vector=frames[c['start'][role]][0],
                    forced_image_vector=45, witnesses=[])
        queue = deque([start]); paths = {start: [start]}; intersection = set(range(512))
        while queue and len(intersection) > 2:
            node = queue.popleft()
            if node[0] == 'exit':
                end = node[1]; basis = frames[c['final'][end]]
                new = intersection & V.span(basis)
                if new != intersection:
                    normal = next(n for n in range(1, 512)
                                  if all((n & v).bit_count() % 2 == 0 for v in basis))
                    path = paths[node]
                    case['witnesses'].append(dict(nodes=path,
                        roles=[min(links[a, b]) for a, b in zip(path, path[1:])],
                        output_role=end, normal=normal))
                    intersection = new
            for node2 in adjacent[node]:
                if node2 not in paths:
                    paths[node2] = paths[node] + [node2]; queue.append(node2)
        V.need(intersection == {0, 45}, 'reconstructed main-output intersection')
        cases.append(case)
    cert = dict(schema_version=1, payload_sha256=V.PAYLOAD_SHA, cases=cases)
    V.verify_certificate(payload, cert)
    return cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    certificate = generate()
    with args.output.open('x') as handle:
        json.dump(certificate, handle, indent=2, sort_keys=True); handle.write('\n')
    print(args.output)


if __name__ == '__main__':
    main()
