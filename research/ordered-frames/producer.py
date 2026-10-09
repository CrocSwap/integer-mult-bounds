#!/usr/bin/env python3
"""Produce reordered, paid-reclamation words with selected geometric labels.

Derived from the PR63/60/62/57 construction, retaining original attribution.
New ordering, selection and relabeling prepared with OpenAI Codex assistance.
"""
import gzip
from hashlib import sha256
import importlib.util
from itertools import combinations
import json
from multiprocessing import Process
from pathlib import Path
import sys

if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_graph():
    spec = importlib.util.spec_from_file_location(
        'ordered_pair_graph', ROOT / 'research/pair-assembly/pair_graph.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.graph


def reorder(c):
    """Preserve source IDs and same-envelope order; verify all scalar identities."""
    groups = {}
    for node in sorted(c.active):
        if c.args[node]:
            groups.setdefault((c.core[node], c.union[node]), []).append(node)
    def key(item):
        (core, union), nodes = item
        return union.bit_count()-core.bit_count(), -core, union, min(nodes)
    variables = len(c.inputs)
    ids = list(range(variables+1)) + [x for _, nodes in sorted(groups.items(), key=key)
                                     for x in nodes]
    mapping = {x:i for i,x in enumerate(ids)}
    args, core, union, provenance = c.args, c.core, c.union, c.provenance
    c.args = [tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core = [core[x] for x in ids]
    c.union = [union[x] for x in ids]
    c.provenance = [provenance[x] for x in ids]
    c.active = {mapping[x] for x in c.active}
    c.outputs = {k:mapping[v] for k,v in c.outputs.items()}
    c.verify()
    return c


def relabel(d, permutation):
    h, v = d['h'], d['v']
    assert sorted(permutation) == list(range(h))
    triples = list(combinations(range(h), 3))
    assert len(triples) == v
    index = {triple:i for i,triple in enumerate(triples)}
    def triple(t):
        return sorted(permutation[x] for x in t)
    triple_map = {i:index[tuple(triple(t))] for i,t in enumerate(triples)}
    def mask(bits):
        return sum(1 << permutation[i] for i in range(h) if bits >> i & 1)
    d['frames'] = [[mask(c),mask(u)] for c,u in d['frames']]
    d['sources'] = {str(triple_map[int(i)]):slot for i,slot in d['sources'].items()}
    scatter = []
    for a,b in d['scatter']:
        assert v <= a < 2*v and b >= 2*v
        scatter.append([v + triple_map[a-v], b])
    d['scatter'] = scatter
    d['outputs'] = [[s,g,permutation[common],triple(t)]
                    for s,g,common,t in d['outputs']]
    return d


def compile_axis(h):
    config = json.loads((HERE/'selection.json').read_text())['axes'][str(h)]
    import compiler
    graph = load_graph()
    compiler.graph = lambda dimension: reorder(graph(dimension))
    result, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True,
                                     minimum_raise=config['minimum_raise'])
    result.pop('seconds')
    word = relabel(word, config['coordinate_permutation'])
    raw = (json.dumps(word, separators=(',',':'))+'\n').encode()
    path = HERE/f'frame-word-{h}.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as archive:
            archive.write(raw)
    sys.path.insert(0, str(ROOT/'scripts/experiments'))
    from binary_frame_replay import replay
    receipt = replay(path)
    record = dict(compiled=result, replay=receipt, configuration=config,
                  gzip_sha256=sha256(path.read_bytes()).hexdigest(),
                  word_sha256=sha256(raw).hexdigest())
    (HERE/f'axis-{h}.json').write_text(json.dumps(record, indent=2)+'\n')
    print(f'PASS produced and independently replayed h={h}, roles={receipt["roles"]}', flush=True)


if __name__ == '__main__':
    jobs = [Process(target=compile_axis, args=(h,)) for h in (23,25)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
        assert job.exitcode == 0
