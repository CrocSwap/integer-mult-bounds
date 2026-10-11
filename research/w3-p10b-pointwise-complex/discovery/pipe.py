#!/usr/bin/env python3
"""cxup pipe.py: p=10 complex word for given modules -> layer (arcs, descended frames, mw pairs) -> aligned word ->
PR #184 flow -> five-stage float price.  Recipe = #327 make_layer_p.py steps 1-6 (mw only), re-written for screening.
usage: pipe.py --tree T --tmod F --pmod F --qmod F [--centre46] --out DIR [--keep]
Prints one JSON line {R, new_R, five, three, ...}.  Discovery only (NOT run by verify.py).
Layout: run it from a flat directory that also holds aligned_word_p.py, centre46.py, discovery/pr327/*.py and
discovery/pr327/pr233/*.py of this package (it imports them from its own directory); --tree is the rebuilt PR #202
tree. The package's layer was produced with CXUP_SPEC set to the spec (graph built by the spec builder, whose graph
for this spec equals centre46.finish_centre46's; verify.py anchor (e)); without CXUP_SPEC, --centre46 builds the
same graph. Floating-point scores choose frames and pairs; nothing here is a proof.
Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance; Apache-2.0."""
import argparse, bisect, json, math, subprocess, sys, time, os, shutil
from collections import defaultdict, Counter
from pathlib import Path
HERE = Path(__file__).resolve().parent


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(',', ':')) + '\n')


def five_price(child, v, h, R):
    Hinv = Counter()
    for r, n in child.items():
        r = int(r); n = n - (2 * v if r == 2 else 0)
        assert n % 3 == 0, (r, n)
        if n: Hinv[r] += n // 3
    H5 = Counter({r: 5 * n for r, n in Hinv.items()})
    for r in (2 * h - 2, h - 1, 2 * h + 2, 4): H5[r] += 2 * v
    m, W = 5 * h, 4 * v + R
    lo, hi = 0.0, 0.01
    for _ in range(100):
        a = (lo + hi) / 2
        if math.fsum(n * (r / m) ** (1 - a) for r, n in H5.items()) < W: lo = a
        else: hi = a
    return lo, H5, m, W


def build_graph(root, mods, centre, P):
    sys.path.insert(0, str(root / 'scripts')); sys.path.insert(0, str(HERE))
    from paired_cube.graph import Graph
    from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
    local = json.loads((root / 'references/paired-cube/sources/local_L1.json').read_text())
    local['G'] = {k: 's' for k in local['G']}
    local['A'] = {k: 'fd' for k in local['A']}
    builder = Graph(P, local=local)
    if centre:
        from centre46 import load_pmod46, finish_centre46
        g = finish_centre46(builder, triple_module_from(mods['tmod'], P), load_pmod46(mods['pmod'], P - 1), all_but_one_from(mods['qmod'], P - 2))
    else:
        g = builder.finish(triple_module_from(mods['tmod'], P), pair_module_from(mods['pmod'], P - 1), all_but_one_from(mods['qmod'], P - 2))
    g = merge_outputs(g, builder, 'f8:00111100')
    g['matching_frames'] = 'coordinate'
    return g


def layer(root, g, cycles=3, log=print):
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube.frames import basis, perp, contained
    from matching import carrier_matching
    from extend_floor import extended_arcs
    import physical_opt, bundles, joint
    from pairs_mw_p import pairs_maxweight
    h, v = g['h'], g['v']
    newcut = v + g['counts']['local_channel_additions']
    arcs, stats = carrier_matching(g, os.environ.get('ORDERING', 'reverse'))
    arcs = [x for x in arcs if x[0] > newcut]
    arcs = extended_arcs(g, arcs, min_donor=newcut + 1)
    base, w = compile_closure(g, arcs)
    row, word = select(g, base, w)
    compile_R = base['R']
    o = physical_opt.Physical(g, w, word, row)
    for k in range(cycles):
        r1 = o.descend(6); r2 = bundles.descend(o, 3); r3 = joint.descend(o, 3, 'forward', k)
        if not any(x['changed'] for x in r1) and not any(x['moved_components'] for x in r2) and not any(x['moved'] for x in r3):
            break
    dframes = o.frames
    p, w = compile_closure(g, arcs)
    p, word = select(g, p, w)
    ops = word['ops']
    newargs = [None] + [None if x is None else [t + 1 for t in x] for x in g['args']]
    newroots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    spans = [()] + [(q,) for q in g['inputs']]
    for aa, bb in newargs[v + 1:]:
        spans.append(basis(spans[aa] + spans[bb]))
    root_frames = {}
    for r, slot in zip(newroots, word['rootroles']):
        root_frames[slot] = spans[r['node']] if r['kind'] == 'center' else perp(basis(g['inputs'][t] for t in r['targets']), h)
    R = p['R']
    pset = set(word['phase1'])
    previous = [-1] * R
    parents = []
    for i, (aa, bb, x) in enumerate(ops):
        parents.append((previous[aa], previous[bb]))
        previous[aa] = previous[bb] = i
        if x <= newcut and len(spans[x]) <= 2:
            pset.add(i)
    todo = list(pset)
    while todo:
        i = todo.pop()
        for j in parents[i]:
            if j >= 0 and j not in pset:
                pset.add(j); todo.append(j)
    word['phase1'] = sorted(pset)
    p['phase1_operations'] = len(pset)
    chron = sorted(pset) + [i for i in range(len(ops)) if i not in pset]
    cap = [perp(root_frames[s], h) if s in root_frames else () for s in range(R)]
    maxima = [None] * len(ops)
    for i in reversed(chron):
        aa, bb, x = ops[i]
        A = basis(cap[aa] + cap[bb])
        maxima[i] = perp(A, h)
        cap[aa] = cap[bb] = A
    selected = [z for z in word['selected'] if z['rank'] == h - 4]
    gauge = {z['role']: perp(tuple(z['annihilator']), h) for z in selected}
    current = [() for _ in range(R)]
    for x, slot in word['sources'].items():
        current[slot] = (g['inputs'][int(x) - 1],)
    for slot, U in gauge.items():
        current[slot] = U
    frames = [None] * len(ops)
    for i in chron:
        aa, bb, x = ops[i]
        want = spans[x] if x <= newcut else perp(basis(perp(tuple(dframes[i]), h) + perp(maxima[i], h)), h)
        U = basis(spans[x] + want + current[aa] + current[bb])
        assert contained(U, maxima[i]), ('Forward frame outside future cap', i)
        frames[i] = current[aa] = current[bb] = U
    moved = [[i, list(U)] for i, U in enumerate(frames) if U != perp(tuple(w['annihilators'][ops[i][2]]), h)]
    o = physical_opt.Physical(g, w, dict(word, selected=selected), p)
    for i, U in enumerate(frames):
        o.frames[i] = tuple(U)
    pairs_mw, mwstats = pairs_maxweight(o)
    good = [k for k, (dd, b, t) in enumerate(pairs_mw) if t is not None and any(i not in o.phase and o.ops[i][0] == dd for i in o.role_ops[dd])]
    if good:
        pairs_mw.append(pairs_mw.pop(good[-1]))
    dropped = len(word['selected']) - len(selected)
    return dict(arcs=arcs, frames=moved, pairs=pairs_mw, compile_R=compile_R, R=R, gauges=len(selected),
                dropped=dropped, unpaired=len(selected) - len(pairs_mw), selected_hist=p['selected_rank_histogram'])


def run(root, *args):
    r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError('FAILED: %s\n%s%s' % (args[0], r.stdout[-2000:], r.stderr[-2000:]))
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tree', type=Path, required=True)
    ap.add_argument('--tmod', type=Path, required=True); ap.add_argument('--pmod', type=Path, required=True)
    ap.add_argument('--qmod', type=Path, required=True)
    ap.add_argument('--centre46', action='store_true')
    ap.add_argument('--p', type=int, default=10)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--keep', action='store_true')
    a = ap.parse_args()
    t0 = time.time()
    root = a.tree.resolve(); out = a.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    mods = dict(tmod=a.tmod.resolve(), pmod=a.pmod.resolve(), qmod=a.qmod.resolve())
    if os.environ.get('CXUP_SPEC'):
        import spec
        g = spec.graph(root, os.environ['CXUP_SPEC'])
    else:
        g = build_graph(root, mods, a.centre46, a.p)
    L = layer(root, g)
    t1 = time.time()
    dump(out / 'matching-arcs.json', dict(matching_arcs=L['arcs']))
    dump(out / 'physical-frames.json', dict(frames=L['frames']))
    dump(out / 'physical-pairs-mw.json', dict(pairs=L['pairs']))
    tree = out / 'tree'
    run(root, HERE / 'aligned_word_p.py', '--p', a.p, *(['--centre46'] if a.centre46 else []), '--tree', root,
        '--tmod', mods['tmod'], '--pmod', mods['pmod'], '--qmod', mods['qmod'], '--arcs', out / 'matching-arcs.json',
        '--frames', out / 'physical-frames.json', '--pairs', out / 'physical-pairs-mw.json', '--out', tree)
    run(root, root / 'research/source-assisted/decision/complex_frame_flow.py', '--tree', tree, '--cache', tree / 'cache',
        '--out', out / 'flow.json', '--witness', '--purify-source-donors', '--recycle-kernels')
    fd = json.loads((out / 'flow.json').read_text())
    kern = json.loads((out / 'flow.witness.json').read_text())['kernel_pairs']
    dump(out / 'kernel-pairs-mw.json', dict(kernel_pairs=kern))
    v, h = g['v'], g['h']
    five, H5, m, W = five_price(fd['child_histogram'], v, h, fd['new_R'])
    res = dict(R=L['R'], compile_R=L['compile_R'], new_R=fd['new_R'], gauges=L['gauges'], dropped=L['dropped'],
               unpaired=L['unpaired'], pairs=len(L['pairs']), arcs=len(L['arcs']), moved=len(L['frames']),
               kernel=len(kern), three=fd['numerical_local_root'], five=five, W=W,
               layer_s=round(t1 - t0, 1), total_s=round(time.time() - t0, 1))
    dump(out / 'result.json', res)
    if not a.keep:
        shutil.rmtree(tree, ignore_errors=True)
        for f in ('flow.witness.json',):
            try: (out / f).unlink()
            except FileNotFoundError: pass
    print(json.dumps(res), flush=True)


if __name__ == '__main__':
    main()
