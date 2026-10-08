#!/usr/bin/env python3
"""Full replay of the skip-prefix cloned producers with PR #43's independent checks.

For h in (23,25): rebuild the scalar DAG (cloned_graph.py), verify the scalar
identity, run PR #43's dense global-bitset audit, profile the pinned carrier
matching with profiles.cpp (LINKS_IN mode, admissibility asserted per edge),
recount every matched use independently (PR #43 producer.recount), and replay
the complete physical timeline and dirty basis in both orientations
(PR #43 original_timeline.check). All outputs must equal the pinned JSON.

The independent checkers are imported unchanged from research/copied-fixed
(Chafik Boukhalfa, PR #43; RaD/hipotures PR #41 timeline compiler).
Adapted from Rohan Arun with Anthropic Claude assistance (PR49).
Prepared by Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import gc
import importlib.util
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PR43 = ROOT/'research/copied-fixed'
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(PR43))
_spec = importlib.util.spec_from_file_location('skip_clones53_pr43_producer', PR43/'producer.py')
pr43_producer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pr43_producer)
import original_timeline as timeline       # noqa: E402  (PR #43 / RaD timeline compiler)
from verify import exactness, require     # noqa: E402  (PR #43 CRT minor bounds)
from partial_swap.graph import export     # noqa: E402
sys.path.insert(0, str(HERE))
from cloned_graph import graph           # noqa: E402


from clone_io import read, check_sources, REPLAY_INPUTS  # noqa: E402


def links(path):
    raw = Path(path).read_bytes()
    require(len(raw) >= 8, 'Links file header')
    n, count = struct.unpack_from('<2I', raw)
    require(len(raw) == 8+8*count, 'Links file format')
    edges = [list(struct.unpack_from('<2I', raw, 8+8*i)) for i in range(count)]
    require(all(0 < donor < n for donor, _ in edges), 'Invalid donor node')
    require(len({donor for donor, _ in edges}) == count, 'Duplicate donor')
    require(len({use for _, use in edges}) == count, 'Duplicate recipient use')
    return n, edges


def run(work, write=False):
    require(not sys.flags.optimize, 'Assertions must remain enabled')
    check_sources(REPLAY_INPUTS)
    pr43_producer.check_sources()
    exe = work/'profiles'
    subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                    '-include', 'algorithm', '-I', str(ROOT/'scripts/partial_swap'),
                    str(HERE/'profiles.cpp'), '-o', str(exe)], check=True)
    receipt = {}
    for h in (23, 25):
        print('Rebuilding cloned PR53 producer h='+str(h), flush=True)
        c = graph(h)
        scalar = c.verify()
        degree, ranks, outputs, audit = pr43_producer.dense_audit(c)
        dag, out_links = work/f'h{h}.bin', work/f'h{h}.uses'
        export(c, dag)
        pinned = HERE/f'links-{h}.uses'
        n, selected = links(pinned)
        require(n == len(c.args), 'Matching DAG node count differs')
        independent = pr43_producer.recount(c, degree, ranks, outputs, pinned)
        env = dict(os.environ, LINKS_IN=str(pinned))
        original = json.loads(subprocess.check_output([str(exe), str(dag), str(out_links)],
                                                      text=True, env=env))
        exported_n, exported = links(out_links)
        require(n == exported_n == len(c.args), 'Matching DAG node count differs')
        require(sorted(map(tuple, selected)) == sorted(map(tuple, exported)), 'Profiler matching differs from pin')
        require(original == independent, 'Independent physical recount failed')
        fixed = read(str(dag)+'.round3_rankone_certified_profiles.json')
        require(fixed['crt_disagreements'] == 0, 'CRT disagreement')
        exactness(h)
        row = dict(original, dag_path=str(dag))
        timeline.basis.cache_clear(); timeline.contained.cache_clear()
        compiled = timeline.check({'producer': row, 'selected_links': {'links': selected}}, True)
        compiled = {k: v for k, v in compiled.items() if k not in ('containment_cache', 'dag_sha256')}
        timeline.basis.cache_clear(); timeline.contained.cache_clear()
        outputs_now = {f'scalar-{h}.json': scalar, f'original-{h}.json': original,
                       f'profiles-{h}.json': fixed, f'timeline-{h}.json': compiled}
        for name, value in outputs_now.items():
            if write:
                (HERE/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
            require(json.loads(json.dumps(value)) == read(HERE/name), 'Replay mismatch: '+name)
        print('PASS h=%d scalar, dense audit, pinned-links profile, independent recount, '
              'full timeline and dirty basis (both orientations)' % h, flush=True)
        receipt[str(h)] = dict(scalar=scalar, dense_audit=audit, independent_recount=independent,
                               fixed_profile=fixed, full_timeline=compiled,
                               links_sha256=sha256(pinned.read_bytes()).hexdigest(),
                               dag_sha256=sha256(dag.read_bytes()).hexdigest())
        del c
        gc.collect()
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--write', action='store_true', help='Regenerate pinned JSON (maintainers only)')
    args = parser.parse_args()
    if args.work_dir:
        args.work_dir.mkdir(parents=True, exist_ok=True)
        result = run(args.work_dir, args.write)
    else:
        with tempfile.TemporaryDirectory(prefix='skip-clone-producers-') as directory:
            result = run(Path(directory), args.write)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
