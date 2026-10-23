"""Check the source-bound carried-frame search baseline, not a new supplier.

Apache-2.0. Prepared by Cinna Davis with substantial OpenAI Codex assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for row in manifest['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed live source: ' + row['path'])
    sys.path.insert(0, str(HERE / 'search'))
    spec = importlib.util.spec_from_file_location('frontier_graph', HERE / 'search/graph.py')
    graph = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(graph)

    def validate_paid(edges):
        paid = Counter()
        for u, v, rank, _ in edges:
            a, b = graph.NF[u], graph.NF[v]
            need(graph.spaces[a] <= graph.spaces[b], 'Paid subspace inclusion')
            need(rank == len(graph.frames[b]) - len(graph.frames[a]), 'Actual paid rank')
            if rank:
                paid[rank] += 1
        return paid

    paid = validate_paid(graph.paid)
    need(paid == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8},
         'Complete original paid invoice including eight centers')
    helpers = Counter()
    for role, u, v, rank, _ in graph.helpers:
        a, b = graph.NF[u], graph.NF[v]
        need(224 <= role < 632 and graph.spaces[a] < graph.spaces[b],
             'Strict arbitrary helper endpoint')
        need(rank == len(graph.frames[b]) - len(graph.frames[a]), 'Whole helper rank')
        helpers[rank] += 1
    need(helpers == {4: 28, 7: 7, 8: 47, 9: 326}, 'All 408 helpers counted once')
    need([graph.NF[i] for i in graph.starts] == graph.c['start'], 'Actual input ABI')
    need([graph.NF[i] for i in graph.ends] == graph.c['final'], 'Actual output ABI')
    for u, v, op, basis in graph.warp:
        image = {graph.image(graph.Gs[op], x) for x in graph.spaces[graph.NF[u]]}
        need(image == graph.spaces[graph.NF[v]], 'Actual native subspace transport')
    for op in range(1, 73):
        need(len({graph.image(graph.Gs[op], x) for x in range(512)}) == 512,
             'Invertible native map')

    wrong = list(graph.paid)
    u, v, rank, extra = next(e for e in wrong if e[2])
    wrong[wrong.index((u, v, rank, extra))] = (u, v, rank + 1, extra)
    try:
        validate_paid(wrong)
    except ValueError as error:
        need(str(error) == 'Actual paid rank', 'Wrong-rank rejection reason')
    else:
        raise ValueError('False recursive price accepted')
    bad_map = list(graph.Gs[1])
    bad_map[0] = 0
    need(len({graph.image(bad_map, x) for x in range(512)}) < 512,
         'Noninvertible native mutation rejected')

    data = dict(nodes=graph.NF, paid=graph.paid, warps=graph.warp,
                helpers=graph.helpers, starts=graph.starts, ends=graph.ends)
    digest = sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    result = dict(status='PASS_CARRIED_FRAME_SEARCH_BASELINE_ONLY',
                  graph_sha256=digest, nodes=len(graph.NF), paid_edges=len(graph.paid),
                  native_occurrences=len(graph.warp), paid=dict(paid), helpers=dict(helpers),
                  inherited_swap_replay='632 arbitrary inputs, both orientations; sign/frame controls',
                  controls=['false_paid_rank', 'noninvertible_native_map'], new_kappa=None)
    target = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        target.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        need(json.loads(target.read_bytes()) == json.loads(json.dumps(result)),
             'Committed graph receipt')
    print(result['status'])


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit(subprocess.run([sys.executable, '-I', '-B', __file__,
                                        *(['--write'] if '--write' in sys.argv else [])]).returncode)
    main()
