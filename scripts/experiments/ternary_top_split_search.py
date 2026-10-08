#!/usr/bin/env python3
"""Screen arbitrary top partitions against physical stream-role counts.

The fast path uses fingerprint interning and is explicitly exploratory.
Any winner requires independent exact support certification before integration.
Existing retained producers, templates, and certificates are never modified.
"""
from array import array
from itertools import combinations
from pathlib import Path
import argparse
import json
import struct
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ternary_split_search import Search, H28_SELECTED_STATES, baseline
from intersection_circuit import feasible


def export(h, nl, path, builder):
    if not 1 <= nl < h:
        raise ValueError('Top split must have two nonempty parts')
    nr = h-nl
    inputs = list(combinations(range(h), 5))
    input_index = {t: i for i, t in enumerate(inputs)}
    templates, template_index, stages = [], {}, []

    def template(key):
        if key not in template_index:
            c = builder(*key)
            mapping = {i: i for i in range(len(c.inputs)+1)}
            gates = []
            for node in c.active:
                if c.args[node]:
                    a, b = c.args[node]
                    gates.append((mapping[a], mapping[b]))
                    mapping[node] = len(c.inputs)+len(gates)
            outputs = [mapping[node] for node in c.outputs]
            template_index[key] = len(templates)
            templates.append((key, len(c.inputs), gates, outputs))
        return template_index[key]

    for degree in (5, 2):
        targets = list(combinations(range(h), degree))
        target_index = {t: i for i, t in enumerate(targets)}
        cases = []
        for b in range(max(0, degree-nr), min(degree, nl)+1):
            tl = list(combinations(range(nl), b))
            tr = list(combinations(range(nr), degree-b))
            outmap = [target_index[s+tuple(nl+x for x in t)] for s in tl for t in tr]
            for a in range(max(0, 5-nr), min(5, nl)+1):
                il = list(combinations(range(nl), a))
                ir = list(combinations(range(nr), 5-a))
                source_map = [input_index[s+tuple(nl+x for x in t)]+1 for s in il for t in ir]
                for u in range(3):
                    if not feasible(nl, a, b, u) or not feasible(nr, 5-a, degree-b, 2-u):
                        continue
                    left = template((nl, a, b, u))
                    right = template((nr, 5-a, degree-b, 2-u))
                    lc, rc = len(templates[left][2]), len(templates[right][2])
                    first = len(ir)*lc+len(tl)*rc <= len(tr)*lc+len(il)*rc
                    cases.append((left, right, len(il), len(ir), len(tl), len(tr),
                                  int(first), source_map, outmap))
        stages.append((len(targets), cases))
    with Path(path).open('wb') as stream:
        def words(values):
            stream.write(struct.pack('<'+'I'*len(values), *values))
        words([h, len(inputs), len(templates), len(stages)])
        for key, ni, gates, outs in templates:
            words([*key, ni, len(gates), len(outs)])
            words([x for pair in gates for x in pair])
            words(outs)
        for count, cases in stages:
            words([count, len(cases)])
            for left, right, il, ir, tl, tr, first, sources, targets in cases:
                words([left, right, il, ir, tl, tr, first])
                words(sources)
                words(targets)
    return dict(h=h, top_split=[nl, nr], local_templates=len(templates),
                local_additions=sum(len(t[2]) for t in templates))


def append_screening_cores(path):
    """Compute cores exactly for the fingerprint-produced graph, not its map."""
    path = Path(path)
    with path.open('rb') as stream:
        h, v, n, q = struct.unpack('<4I', stream.read(16))
        parents = array('I')
        parents.fromfile(stream, 2*n)
    if sys.byteorder != 'little':
        parents.byteswap()
    if path.stat().st_size != 16+9*n+4*q:
        raise ValueError('Expected a fingerprint DAG without appended source cores')
    cores = array('I', [0])*n
    inputs = list(combinations(range(h), 5))
    if len(inputs) != v:
        raise ValueError('Source dimension mismatch')
    for i, points in enumerate(inputs, 1):
        cores[i] = sum(1 << j for j in points)
    for i in range(v+1, n):
        a, b = parents[2*i:2*i+2]
        if not 0 < a < i or not 0 < b < i:
            raise ValueError('Non-topological fingerprint DAG')
        cores[i] = cores[a] & cores[b]
    if sys.byteorder != 'little':
        cores.byteswap()
    with path.open('ab') as stream:
        cores.tofile(stream)


def run_json(argv, log):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True)
    Path(log).write_text(result.stderr)
    if result.returncode:
        return dict(failed=True, returncode=result.returncode, stderr=result.stderr[-3000:])
    return json.loads(result.stdout)


def template_builder(search, mode):
    """Return the reproducible inherited, per-state, or selected builder."""
    if mode not in ('inherited', 'selected', 'dp'):
        raise ValueError('Unknown template mode')
    selected = {key[1:] for key in H28_SELECTED_STATES}
    def builder(*key):
        use_search = mode == 'dp' or (mode == 'selected' and key[1:] in selected)
        return search.build(*key) if use_search else baseline.build(*key)
    return builder


def screen(h, split, mode, search, workdir, fingerprint, dual, stream, depth, mixed):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    builder = template_builder(search, mode)
    start = time.monotonic()
    plan, dag = workdir/'plan.bin', workdir/'dag.bin'
    result = dict(status='FINGERPRINT SCREEN ONLY; EXACT SUPPORT CHECK REQUIRED',
                  mode=mode, plan=export(h, split, plan, builder))
    result['support_screen'] = run_json([fingerprint, plan, dag], workdir/'fingerprint.log')
    if not result['support_screen'].get('failed'):
        append_screening_cores(dag)
        targets = workdir/'targets.bin'
        result['frames'] = run_json([dual, dag, workdir/'unresolved.txt',
                                    workdir/'classes.bin', targets], workdir/'frames.log')
        if not result['frames'].get('failed'):
            cmd = [stream, dag, targets, depth, workdir/'links.bin']+(['mixed'] if mixed else [])
            result['stream'] = run_json(cmd, workdir/'stream.log')
    result['elapsed_seconds'] = time.monotonic()-start
    (workdir/'screen.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--h', type=int, default=28)
    p.add_argument('--splits', type=int, nargs='+', default=[12, 13, 15, 16])
    p.add_argument('--modes', nargs='+', choices=('inherited', 'selected', 'dp'),
                   default=['inherited', 'selected', 'dp'])
    p.add_argument('--workdir', type=Path, required=True)
    p.add_argument('--fingerprint', type=Path, default=Path('/private/tmp/ternary-target-fingerprint'))
    p.add_argument('--dual', type=Path, default=Path('/private/tmp/ternary-target-dual'))
    p.add_argument('--stream', type=Path, default=Path('/private/tmp/ternary-stream-reuse'))
    p.add_argument('--depth', type=int, default=1)
    p.add_argument('--mixed', action='store_true')
    args = p.parse_args()
    search = Search()
    for split in args.splits:
        for mode in args.modes:
            result = screen(args.h, split, mode, search,
                            args.workdir/f'h{args.h}-split{split}-{mode}',
                            args.fingerprint, args.dual, args.stream, args.depth, args.mixed)
            print(json.dumps(dict(split=split, mode=mode,
                                  additions=result['support_screen'].get('retained_additions_if_no_collision'),
                                  roles=result.get('stream', {}).get('new_roles'),
                                  frame_valid=result.get('frames', {}).get('every_final_frame_nondegenerate'),
                                  seconds=result['elapsed_seconds'])), flush=True)
