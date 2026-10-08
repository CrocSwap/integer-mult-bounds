#!/usr/bin/env python3
"""Compile the pair-assembly graph with PR #57's joint frame compiler.

PR #57's compiler (scripts/experiments/binary_frame_compiler.py, by eumemic
with OpenAI Codex assistance) is used unchanged; only the graph it compiles is
swapped, exactly as its own skip_frame_compiler.py swaps in PR #53's graph.
The graph source is hash-pinned below. Every word is checked by the compiler on
the complete input and dirty basis in both orientations, and frame_verify.py
replays it independently. Adapted with assistance from Claude (Anthropic).
Usage: python frame_compile.py   (writes words and frame-compiler.json here)
"""
import sys
sys.dont_write_bytecode = True
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from multiprocessing import Process

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
GRAPH = HERE.parent/'pair_graph.py'
GRAPH_SHA256 = '3d47e89d2649c90800a276bdd0480131def50e0bdf92c122a19494b55bf17420'


def load_graph():
    assert sha256(GRAPH.read_bytes()).hexdigest() == GRAPH_SHA256, 'pair_graph.py changed'
    spec = importlib.util.spec_from_file_location('pinned_pair_graph', GRAPH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.graph


def compile_axis(h):
    import binary_frame_compiler as compiler
    compiler.graph = load_graph()
    result, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True)
    raw = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    path = HERE/f'frame-word-{h}.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as archive:
            archive.write(raw)
    from binary_frame_replay import replay
    receipt = replay(path)
    (HERE/f'frame-compiled-{h}.json').write_text(json.dumps(dict(
        compiled=result, replay=receipt, gzip_sha256=sha256(path.read_bytes()).hexdigest(),
        word_sha256=sha256(raw).hexdigest()), indent=2)+'\n')
    print(f"h={h} roles={result['roles']} replay roles={receipt['roles']}", flush=True)


if __name__ == '__main__':
    jobs = [Process(target=compile_axis, args=(h,)) for h in (23, 25)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
        assert job.exitcode == 0
    axes = {str(h): json.loads((HERE/f'frame-compiled-{h}.json').read_text()) for h in (23, 25)}
    record = dict(status='Joint frame compilation of the pair-assembly graph; complete dirty basis both orientations',
                  axes=axes, source=dict(graph='research/pair-assembly/pair_graph.py', graph_sha256=GRAPH_SHA256,
                                         compiler='scripts/experiments/binary_frame_compiler.py (PR #57, unchanged)'))
    (HERE/'frame-compiler.json').write_text(json.dumps(record, indent=2)+'\n')
    for h in (23, 25):
        (HERE/f'frame-compiled-{h}.json').unlink()
    print('PASS compiled and independently replayed both axes', flush=True)
