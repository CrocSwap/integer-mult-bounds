#!/usr/bin/env python3
"""aligned_word_spec.py: PR #327's aligned_word_p.py with one change: the graph may be built from a per-invocation
module spec (--spec SPEC.json, resolved against --spec-root): spec_graph.finish_spec, i.e. PR #327's
centre46.finish_centre46 with the pair module of every invocation (i, bit) and the all-but-one module of every
invocation (i, j, mode) looked up in the spec's tables, followed by the same merge_outputs(f8:00111100). With --spec
the options --tmod/--pmod/--qmod are ignored (the spec names them) and --centre46 is implied. Without --spec it is
aligned_word_p.py byte for byte in behaviour (verify.py checks the --spec path against aligned_word_p.py on a spec
with one module per kind, and the source differs from aligned_word_p.py only in this docstring, the two options and
the graph-building branch).
Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance; Apache-2.0. aligned_word_p.py is
DreamingOfClouds' (PR #327, from PR #304), on PR #202's source_aligned_local_v4.py (ikeboy) and icekylinx's
source_aligned_local.py. Its docstring follows.

aligned_word_p.py: PR #194's source-aligned complex word for given query modules and a frozen physical layer, at any
cube size p.

PR #304's aligned_word.py with three changes: (1) --p (default 11): Graph(p) and the module sizes p, p - 1, p - 2
replace the literals 11, 10, 9; (2) --centre46: the pair module carries a 37th root (the sum of all its inputs) that
supplies the star centre (centre46.py, the effect of PR #315's Graph.finish patch); (3) when select() chooses gauges
that the script then drops (rank other than h - 4, or unpaired), the record's gauge ledger (selected_roles,
selected_rank_histogram, remaining_internal_histogram) is corrected to the kept gauges, so that PR #200's checker can
recount it; nothing is dropped at p = 11 or on the annealed p = 10 modules, so the output is then unchanged. At
p = 11 without --centre46 it is aligned_word.py.

This is research/source-assisted-v4/source_aligned_local_v4.py of PR #202 (ikeboy, PR #193/#194; derived from
icekylinx's research/source-assisted/decision/source_aligned_local.py, GPT-6 Astra assistance, Apache-2.0) with
its four discovery steps replaced by inputs:
  * the three query modules are --tmod/--pmod/--qmod (the script hard-codes PR #168 v4's three files); they are
    loaded and contract-checked by the tree's own loaders (triple_module_from, pair_module_from, all_but_one_from);
  * the carrier arcs are --arcs (the script maps PR #168's frozen matching through the PR #168 v4 word); the tree's
    compile_closure() checks them (one donor per use, acyclic generalized dependencies, every value span inside its
    frame, exact positive-rank ledger);
  * the preferred frame of every query operation is its frame in --frames (the script inherits PR #168's physical
    frames). The forward closure, the clipping to the exact future cap and the minimal-frame check of every local
    pair are the script's, unchanged, and the closure must return every frozen frame unchanged;
  * the reuse pairs are --pairs (as the script's own --pairs option). Each pair must be an edge of the script's
    candidate graph (donor ungauged and not a root, its last frame inside the recipient's gauge frame, its last
    operation before the recipient's first, deadline as the script assigns it) and the list must already be a
    fixed point of the script's last-late-control reordering.
Everything else, in the script's order: local configuration (G all 's', A all 'fd'), Graph.finish, merge
f8:00111100, compile_closure, select, the rank-at-most-two local phase-one prefix with its role predecessors, gauge
filtering, the target data histogram, the exact physical checks of scripts/paired_cube_physical.py (nested chains,
pair legality, spliced recount, exact numeric replay with mutations rejected) and the files written: cache/
{graph,frames,selection,record}.json, references/paired-cube/physical/{frames,pairs}.json and
certificates/paired-cube-sinks-input.json, byte for byte in the script's encoding. Given PR #168's modules and the
script's own arcs, frames and pairs it reproduces the script's output byte for byte (verify.py checks this).

usage: aligned_word_p.py [--p P] [--centre46] --tree TREE --tmod F --pmod F --qmod F --arcs F --frames F --pairs F --out DIR
Run with the rebuilt PR #202 tree as working directory, as the upstream scripts are; -O is refused.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import sys
import time

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')


def read(p):
    return json.loads(Path(p).read_text())


def write(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, separators=(',', ':')) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, required=True, help='the rebuilt PR #202 tree (its scripts/ are imported)')
    ap.add_argument('--tmod', type=Path, required=True, help='disjoint-triple module (triple_module_from, p = 11)')
    ap.add_argument('--pmod', type=Path, required=True, help='pair module (pair_module_from, n = 10)')
    ap.add_argument('--qmod', type=Path, required=True, help='all-but-one module (all_but_one_from, n = 9)')
    ap.add_argument('--arcs', type=Path, required=True, help='{"matching_arcs": [[donor node, use code], ...]}')
    ap.add_argument('--frames', type=Path, required=True, help='{"frames": [[operation, frame rows], ...]}')
    ap.add_argument('--pairs', type=Path, required=True, help='{"pairs": [[donor, recipient, deadline], ...]}')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--p', type=int, default=11, help='cube size p (cp10 generalisation; 11 = the original script)')
    ap.add_argument('--centre46', action='store_true', help='cp10: pair module with an extra full-sum root supplies the star centre (agent-cmod finish_centre46)')
    ap.add_argument('--spec', type=Path, default=None, help='per-invocation module spec (spec_graph.py); implies --centre46')
    ap.add_argument('--spec-root', type=Path, default=None, help='directory the spec paths are relative to')
    a = ap.parse_args()
    start = time.monotonic()
    sys.path.insert(0, str(a.tree / 'scripts'))
    from paired_cube.graph import Graph
    from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
    from paired_cube.closure import compile_closure
    from paired_cube.gauges import select
    from paired_cube.frames import basis, perp, contained
    import paired_cube_physical as physical
    s = a.tree / 'references/paired-cube/sources'
    local = read(s / 'local_L1.json')
    local['G'] = {k: 's' for k in local['G']}
    local['A'] = {k: 'fd' for k in local['A']}
    builder = Graph(a.p, local=local)
    if a.spec is not None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from centre46 import load_pmod46
        import spec_graph
        spec = read(a.spec)
        assert spec['p'] == a.p and spec.get('centre46', True), 'spec is not a centre-sharing p = %d spec' % a.p
        table = spec_graph.expand(spec, a.spec_root or a.spec.parent)
        loaded = {}

        def get(path, loader, n):
            if path not in loaded:
                loaded[path] = loader(path, n)
            return loaded[path]
        g = spec_graph.finish_spec(builder, triple_module_from((a.spec_root or a.spec.parent) / spec['tmod'], a.p),
                                   lambda i, bit: get(table['p', i, bit], load_pmod46, a.p - 1),
                                   lambda i, j, mode: get(table['q', i, j, mode], all_but_one_from, a.p - 2))
    elif a.centre46:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from centre46 import load_pmod46, finish_centre46
        g = finish_centre46(builder, triple_module_from(a.tmod, a.p), load_pmod46(a.pmod, a.p - 1), all_but_one_from(a.qmod, a.p - 2))
    else:
        g = builder.finish(triple_module_from(a.tmod, a.p), pair_module_from(a.pmod, a.p - 1), all_but_one_from(a.qmod, a.p - 2))
    g = merge_outputs(g, builder, 'f8:00111100')
    g['matching_frames'] = 'coordinate'
    h, v = g['h'], g['v']
    newcut = v + g['counts']['local_channel_additions']
    newargs = [None] + [None if x is None else [t + 1 for t in x] for x in g['args']]
    newroots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    # frozen carrier arcs (in place of the arcs mapped from PR #168's matching)
    arcs = read(a.arcs)['matching_arcs']
    assert len({x for x, _ in arcs}) == len(arcs), 'one arc per donor'
    p, w = compile_closure(g, arcs)
    assert w['matching_arcs'] == arcs, 'compile_closure did not keep the frozen arcs'
    p, word = select(g, p, w)
    assert all(ca in (-1, 1) and cb in (-1, 1) for ca, cb in word['opcoeff'])
    print(json.dumps(dict(stage='word', local=g['counts']['local_channel_additions'], arcs=len(arcs), R=p['R'],
                          selected=p['selected_rank_histogram'], seconds=time.monotonic() - start)), flush=True)
    ops = word['ops']
    # frozen preferred frames (in place of the frames inherited from PR #168's physical layer)
    frames_in = read(a.frames)['frames']
    desired = [perp(tuple(w['annihilators'][x]), h) for _, _, x in ops]
    for i, F in frames_in:
        desired[i] = tuple(F)
    spans = [()] + [(q,) for q in g['inputs']]
    for aa, bb in newargs[v + 1:]:
        spans.append(basis(spans[aa] + spans[bb]))
    root_frames = {}
    for r, slot in zip(newroots, word['rootroles']):
        root_frames[slot] = spans[r['node']] if r['kind'] == 'center' else perp(basis(g['inputs'][t] for t in r['targets']), h)
    R = p['R']
    pset = set(word['phase1'])
    # Both signs of a pair must occur before the center cut (source_aligned_local_v4.py, unchanged).
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
                pset.add(j)
                todo.append(j)
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
        assert contained(spans[x], maxima[i])
    selected = [z for z in word['selected'] if z['rank'] == h - 4]
    gauge = {z['role']: perp(tuple(z['annihilator']), h) for z in selected}
    current = [() for _ in range(R)]
    for x, slot in word['sources'].items():
        current[slot] = (g['inputs'][int(x) - 1],)
    for slot, U in gauge.items():
        current[slot] = U
    frames = [None] * len(ops)
    minimal_pairs = query_ops = 0
    for i in chron:
        aa, bb, x = ops[i]
        if x <= newcut:
            want = spans[x]
        else:
            want = desired[i]
            query_ops += 1
            want = perp(basis(perp(want, h) + perp(maxima[i], h)), h)
        U = basis(spans[x] + want + current[aa] + current[bb])
        assert contained(U, maxima[i]), ('Forward frame outside future cap', i)
        frames[i] = current[aa] = current[bb] = U
        if x <= newcut and len(spans[x]) == 2:
            assert U == spans[x], ('Local pair failed its minimal physical frame', i)
            minimal_pairs += 1
    for slot, U in root_frames.items():
        assert contained(current[slot], U)
    bad = [i for i in range(len(ops)) if frames[i] != desired[i]]
    assert not bad, ('the forward closure changes %d frozen frames, first at operation %d' % (len(bad), bad[0]))
    role_ops = defaultdict(list)
    for i, (aa, bb, _) in enumerate(ops):
        role_ops[aa].append(i)
        role_ops[bb].append(i)
    pos = {i: k for k, i in enumerate(chron)}
    for slot in role_ops:
        role_ops[slot].sort(key=pos.__getitem__)
    recipients = sorted(gauge)
    recipient_set = set(recipients)
    donors = {slot for slot in range(R) if slot not in recipient_set and slot not in root_frames and slot in role_ops}
    for slot in recipients:
        assert role_ops[slot][0] not in pset
    # frozen reuse pairs (in place of the script's matching; the script's own --pairs option)
    pairs = read(a.pairs)['pairs']
    assert len({d for d, _, _ in pairs}) == len({b for _, b, _ in pairs}) == len(pairs), 'one pair per donor and recipient'
    for d, b, t in pairs:
        assert d in donors and b in recipient_set, ('pair outside the candidate roles', d, b)
        last, first = role_ops[d][-1], role_ops[b][0]
        assert contained(frames[last], gauge[b]), ('donor last frame outside the recipient gauge', d, b)
        assert pos[last] < pos[first], ('donor not dead before the recipient', d, b)
        assert t == (None if last in pset else first), ('deadline differs from the script\'s rule', d, b, t)
    # The inherited negative replay moves its last late recipient to the phase cut (unchanged); the frozen list
    # must already be in that order.
    last_write = {}
    for i, (aa, bb, x) in enumerate(ops):
        last_write[aa] = max(last_write.get(aa, -1), pos[i])
    controls = [q for q in pairs if q[2] is not None and last_write.get(q[0], -1) >= len(pset)]
    if controls:
        chosen = controls[-1]
        assert pairs[-1] == chosen, 'frozen pairs are not in the script\'s control order'
    kept = {b for _, b, _ in pairs}
    chosen = word['selected']
    word['selected'] = [z for z in selected if z['role'] in kept]
    # complex-p10: keep the record's gauge ledger equal to the gauges the word keeps. select() may choose gauges of
    # rank other than h - 4 (or unpaired ones); the script drops them from the selection, but its record still counts
    # their births, which PR #200's complex checker (verify_fused.py) recounts and rejects. Each dropped birth is
    # reversed (H[r - d] -= 1, H[r] += 1 with r the rank of the role's first frame, as select() booked it). Nothing is
    # dropped at p = 11 on PR #168 v4's or PR #304's modules, nor on this package's annealed modules: the record is then
    # untouched (byte for byte). Only the verifiers read these three fields.
    keep_roles = {z['role'] for z in word['selected']}
    dropped = [z for z in chosen if z['role'] not in keep_roles]
    if dropped:
        first_x = {}
        for aa, bb, x in ops:
            first_x.setdefault(aa, x)
            first_x.setdefault(bb, x)
        H = list(p['remaining_internal_histogram'])
        ranks = dict(p['selected_rank_histogram'])
        for z in dropped:
            r, d = h - len(w['annihilators'][first_x[z['role']]]), z['rank']
            H[r - d] -= 1
            H[r] += 1
            ranks[d] -= 1
            if not ranks[d]:
                del ranks[d]
        p['remaining_internal_histogram'], p['selected_rank_histogram'], p['selected_roles'] = H, ranks, len(word['selected'])
    moved = [[i, list(U)] for i, U in enumerate(frames) if U != perp(tuple(w['annihilators'][ops[i][2]]), h)]
    assert moved == frames_in, 'frozen frames are not in the script\'s canonical form'
    deadline = {b: t for _, b, t in pairs}
    Y = [() for _ in range(v)]
    target = Counter()
    for z in sorted(word['selected'], key=lambda z: len(pset) if deadline[z['role']] is None else pos[deadline[z['role']]]):
        U = gauge[z['role']]
        for t in z['targets']:
            assert contained(Y[t], U)
            target[len(U) - len(Y[t])] += 1
            Y[t] = U
    for r, slot in zip(newroots, word['rootroles']):
        if r['kind'] == 'side':
            U = root_frames[slot]
            for t in r['targets']:
                assert contained(Y[t], U)
                target[len(U) - len(Y[t])] += 1
                Y[t] = U
    for t in range(v):
        target[h - 1 - len(Y[t])] += 1
    p['target_data_histogram'] = dict(target)
    print(json.dumps(dict(stage='physical', query_ops=query_ops, moved_frames=len(moved), minimal_pair_ops=minimal_pairs,
                          pairs=len(pairs), gauges=len(word['selected']), seconds=time.monotonic() - start,
                          dropped_gauges=dict(sorted(Counter(z['rank'] for z in dropped).items())))), flush=True)
    out = a.out
    for name, data in [('graph.json', g), ('frames.json', w), ('selection.json', word), ('record.json', p)]:
        write(out / 'cache' / name, data)
    write(out / 'references/paired-cube/physical/frames.json', {'frames': moved})
    write(out / 'references/paired-cube/physical/pairs.json', {'pairs': pairs})
    result = physical.physical(g, w, word, p, moved, pairs)
    write(out / 'certificates/paired-cube-sinks-input.json', result)
    print(json.dumps(dict(stage='checked', R=p['R'], physical_R=result['physical_R'], arcs=len(arcs), moved_frames=len(moved),
                          pairs=len(pairs), seconds=time.monotonic() - start)), flush=True)


if __name__ == '__main__':
    main()
