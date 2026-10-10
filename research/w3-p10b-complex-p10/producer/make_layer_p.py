#!/usr/bin/env python3
"""make_layer.py: discovery of a frozen physical layer for three query modules (NOT run by verify.py).

verify.py never searches: it reads layers/<set>/ and checks it. This script is how those files were found, kept for
provenance and for re-pinning after a module changes. Recipe (the same for the control and the result):
  1. the source-aligned graph of PR #194's pipeline with the given modules (aligned_word.py's construction);
  2. fresh carrier arcs: the deterministic Hopcroft-Karp carrier matching of PR #200/#233's discovery harness
     (pr233/matching.py, ordering 'reverse'), arcs of local donors dropped (as the mapped arcs of PR #193/#194 drop
     them), then PR #162's greedy extension restricted to query donors (extend_floor.py);
  3. compile_closure + select, then PR #200's operation-frame descent on that word (pr233/physical_opt.py single
     endpoint moves, bundles.py equal-frame components, joint.py adjacent components; up to three cycles);
  4. source_aligned_local_v4.py's forward closure with the descended frames as preferred frames (clipped to the
     future cap; local operations keep their literal spans);
  5. reuse pairs, two recipes on the same frames: 'parity' = source_aligned_local_v4.py --avoid-parity-erasure (PR
     #193's minimum-weight full matching avoiding PR #184's parity erasures), 'mw' = PR #200/#233's maximum-weight
     late compensated pairing (pr233/pairs_mw.py) with harness.descend's last-late-pair order;
  6. kernel pairs: PR #184's complex_frame_flow.py --witness --purify-source-donors --recycle-kernels on the
     aligned tree written by aligned_word.py (its own maximum matching), frozen as found.
Writes layers/<set>/{matching-arcs,physical-frames,physical-pairs-parity,physical-pairs-mw,kernel-pairs-parity,
kernel-pairs-mw}.json and, for a set of package modules, records the module files used in SOURCE.json's
module_sets (a module given outside modules/ is first copied there). Then run verify.py --write (re-pins
SOURCE.json, sets the claims, regenerates the certificates) and verify.py.

usage: python3 -B discovery/make_layer.py --set cmod [--tmod F] [--pmod F] [--qmod F]
       python3 -B discovery/make_layer.py --set pr168-v4          (PR #168 v4's three files from the rebuilt tree)
A module not given defaults to the set's current entry in SOURCE.json. Needs numpy/scipy as verify.py; about five
minutes. Floating-point scores choose the frames and pairs; nothing here is a proof.
"""
import argparse
import bisect
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
sys.dont_write_bytecode = True
HERE = Path('/home/claude/cx')
PKG = Path('/home/claude/cx')
PR168 = dict(tmod='tmod_TE_TD_TB3_1_1_4_full_6.0617964e-4.json', pmod='pmod_J0_full_6.0666810e-4.json',
             qmod='qmod_climb3u_best.json')
DESCRIPTIONS = dict(
    arcs='Frozen carrier arcs of the source-aligned word (discovery/make_layer.py step 2): deterministic HK carrier '
         'matching (PR200/233 harness, ordering reverse) on query donors plus PR162 extension; checked by compile_closure.',
    frames='Frozen operation frames (source_aligned_local_v4.py canonical form: operations whose frame differs from the '
           'closure frame), from PR200 descent on the aligned word and the script\'s forward closure.',
    parity='Frozen reuse pairs [donor, recipient, deadline]: PR193 recipe (source_aligned_local_v4.py '
           '--avoid-parity-erasure minimum-weight full matching), in the script\'s control order.',
    mw='Frozen reuse pairs [donor, recipient, deadline]: PR200/233 maximum-weight late compensated pairing '
       '(pairs_mw.py) with the last late pair moved to the phase cut.',
    kernel='Frozen kernel pairs of the frame flow on this layer (complex_frame_flow.py --witness --recycle-kernels).')


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(',', ':')) + '\n')


def log(msg, t0=time.monotonic()):
    print('[%6.1fs] %s' % (time.monotonic() - t0, msg), flush=True)


def rebuild_tree(dest):
    spec = importlib.util.spec_from_file_location('pr233_layer_verify', PKG / 'references/pr233-layer/verify.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.rebuild(dest)
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--set', required=True, help='layer name: writes layers/<set>/')
    ap.add_argument('--tmod', type=Path); ap.add_argument('--pmod', type=Path); ap.add_argument('--qmod', type=Path)
    ap.add_argument('--tree', type=Path, help='an already rebuilt PR #202 tree (default: rebuild into a temporary directory)')
    ap.add_argument('--out', type=Path, help='output directory (default: layers/<set>)')
    ap.add_argument('--p', type=int, default=11)
    ap.add_argument('--local', type=Path, default=None)
    a = ap.parse_args()
    out = (a.out or PKG / 'layers' / a.set).resolve()
    source = dict(module_sets={})
    current = {}
    with tempfile.TemporaryDirectory(prefix='make-layer-') as d:
        root = a.tree.resolve() if a.tree else rebuild_tree(Path(d).resolve())
        src = root / 'references/paired-cube/sources'
        mods, record = {}, {}
        for k in PR168:
            given = getattr(a, k)
            if given is None:
                rel = current[k]
                mods[k] = root / rel[5:] if rel.startswith('tree:') else PKG / rel
                record[k] = rel
                continue
            given = given.resolve()
            mods[k] = given
            record[k] = str(given)
        sys.path.insert(0, str(root / 'scripts'))
        sys.path.insert(0, str(HERE / 'pr233'))
        sys.path.insert(0, str(HERE))
        from paired_cube.graph import Graph
        from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
        from paired_cube.closure import compile_closure
        from paired_cube.gauges import select
        from paired_cube.frames import basis, perp, contained
        from matching import carrier_matching
        from extend_floor import extended_arcs
        import physical_opt
        import bundles
        import joint
        from pairs_mw import pairs_maxweight
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import min_weight_full_bipartite_matching
        # 1. graph (aligned_word.py / source_aligned_local_v4.py construction)
        local = json.loads((src / 'local_L1.json').read_text())
        if a.local is not None:
            local = json.loads(a.local.read_text())
        else:
            local['G'] = {k: 's' for k in local['G']}
            local['A'] = {k: 'fd' for k in local['A']}
        builder = Graph(a.p, local=local)
        g = builder.finish(triple_module_from(mods['tmod'], a.p), pair_module_from(mods['pmod'], a.p - 1), all_but_one_from(mods['qmod'], a.p - 2))
        g = merge_outputs(g, builder, 'f8:00111100')
        g['matching_frames'] = 'coordinate'
        h, v = g['h'], g['v']
        newcut = v + g['counts']['local_channel_additions']
        # 2. fresh arcs
        arcs, stats = carrier_matching(g, 'reverse')
        arcs = [x for x in arcs if x[0] > newcut]
        arcs = extended_arcs(g, arcs, min_donor=newcut + 1)
        assert all(x[0] > newcut for x in arcs)
        log('arcs: %d (HK matched %d of %d donors)' % (len(arcs), stats['matched'], stats['donors']))
        # 3. descent on the aligned word
        base, w = compile_closure(g, arcs)
        row, word = select(g, base, w)
        o = physical_opt.Physical(g, w, word, row)
        for k in range(3):
            r1 = o.descend(6); r2 = bundles.descend(o, 3); r3 = joint.descend(o, 3, 'forward', k)
            if not any(x['changed'] for x in r1) and not any(x['moved_components'] for x in r2) and not any(x['moved'] for x in r3):
                break
        dframes = o.frames
        log('descent done')
        # 4. forward closure (source_aligned_local_v4.py, preferred frames = descended frames)
        p, w = compile_closure(g, arcs)
        p, word = select(g, p, w)
        ops = word['ops']
        assert len(ops) == len(dframes)
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
        log('frames: %d of %d operations moved from their closure frames' % (len(moved), len(ops)))
        # 5. pairs
        role_ops = defaultdict(list)
        for i, (aa, bb, _) in enumerate(ops):
            role_ops[aa].append(i)
            role_ops[bb].append(i)
        pos = {i: k for k, i in enumerate(chron)}
        for slot in role_ops:
            role_ops[slot].sort(key=pos.__getitem__)
        last_write = {}
        for i, (aa, bb, x) in enumerate(ops):
            last_write[aa] = max(last_write.get(aa, -1), pos[i])

        def control_order(pairs):
            controls = [q for q in pairs if q[2] is not None and last_write.get(q[0], -1) >= len(pset)]
            if controls:
                chosen = controls[-1]
                pairs.remove(chosen)
                pairs.append(chosen)
            return pairs
        recipients = sorted(gauge)
        recipient_set = set(recipients)
        donors = [slot for slot in range(R) if slot not in recipient_set and slot not in root_frames and slot in role_ops]
        groups = defaultdict(list)
        for j, slot in enumerate(recipients):
            groups[gauge[slot]].append((pos[role_ops[slot][0]], j))
        group_data = []
        for U, ls in groups.items():
            ls.sort()
            group_data.append((U, [x for x, _ in ls], [j for _, j in ls]))
        cache, indices, indptr = {}, [], [0]
        for slot in donors:
            last = role_ops[slot][-1]
            U = frames[last]
            eligible = cache.get(U)
            if eligible is None:
                eligible = cache[U] = [(ps, js) for V, ps, js in group_data if contained(U, V)]
            for ps, js in eligible:
                indices.extend(js[bisect.bisect_right(ps, pos[last]):])
            indptr.append(len(indices))
        parity = []
        for cube in range(v // 8):
            for bit in range(2):
                parity.append(basis(tuple(g['inputs'][8 * cube + j] for j in range(8) if j.bit_count() % 2 == bit)))
        erasable = {}

        def weight(slot, j):
            key = (frames[role_ops[slot][-1]], gauge[recipients[j]])
            if key not in erasable:
                U, V = key
                erasable[key] = len(U) <= 3 and any(contained(U, S) and contained(S, V) for S in parity)
            return 2.0 if erasable[key] else 1.0
        weights = np.array([weight(slot, indices[k]) for r, slot in enumerate(donors) for k in range(indptr[r], indptr[r + 1])])
        wmatrix = csr_matrix((weights, np.array(indices, dtype=np.int32), np.array(indptr, dtype=np.int32)), shape=(len(donors), len(recipients)))
        rows, cols = min_weight_full_bipartite_matching(wmatrix.T.tocsr())
        matched = np.full(len(donors), -1)
        matched[cols] = rows
        pairs_parity = control_order([[slot, recipients[j], None if role_ops[slot][-1] in pset else role_ops[recipients[j]][0]]
                                      for slot, j in zip(donors, matched) if j >= 0])
        o = physical_opt.Physical(g, w, dict(word, selected=selected), p)
        for i, U in enumerate(frames):
            o.frames[i] = tuple(U)
        pairs_mw, mwstats = pairs_maxweight(o)
        good = [k for k, (dd, b, t) in enumerate(pairs_mw) if t is not None and any(i not in o.phase and o.ops[i][0] == dd for i in o.role_ops[dd])]
        if good:
            pairs_mw.append(pairs_mw.pop(good[-1]))
        log('pairs: parity %d, mw %d (of %d gauges)' % (len(pairs_parity), len(pairs_mw), len(recipients)))
        dump(out / 'matching-arcs.json', dict(description=DESCRIPTIONS['arcs'], matching_arcs=arcs))
        dump(out / 'physical-frames.json', dict(description=DESCRIPTIONS['frames'], frames=moved))
        dump(out / 'physical-pairs-parity.json', dict(description=DESCRIPTIONS['parity'], pairs=pairs_parity))
        dump(out / 'physical-pairs-mw.json', dict(description=DESCRIPTIONS['mw'], pairs=pairs_mw))
        # 6. kernel pairs: aligned tree with aligned_word.py, flow with its own kernel matching
        for recipe in ('mw',):
            tree = out / ('tree-' + recipe)
            for cmd in ([PKG / 'aligned_word_p.py', '--p', str(a.p)] + (['--local', a.local] if a.local else []) + ['--tree', root, '--tmod', mods['tmod'], '--pmod', mods['pmod'], '--qmod', mods['qmod'],
                         '--arcs', out / 'matching-arcs.json', '--frames', out / 'physical-frames.json',
                         '--pairs', out / ('physical-pairs-%s.json' % recipe), '--out', tree],
                        [root / 'research/source-assisted/decision/complex_frame_flow.py', '--tree', tree, '--cache', tree / 'cache',
                         '--out', tree / 'flow.json', '--witness', '--purify-source-donors', '--recycle-kernels']):
                r = subprocess.run([sys.executable, '-B', *map(str, cmd)], cwd=root, capture_output=True, text=True)
                if r.returncode:
                    raise SystemExit('FAILED: %s\n%s%s' % (cmd[0], r.stdout[-3000:], r.stderr[-3000:]))
            kernel = json.loads((tree / 'flow.witness.json').read_text())['kernel_pairs']
            flow = json.loads((tree / 'flow.json').read_text())
            dump(out / ('kernel-pairs-%s.json' % recipe), dict(description=DESCRIPTIONS['kernel'], kernel_pairs=kernel))
            log('%s: flow new_R %d, kernel reuses %d, numerical three-stage root %.7e' % (recipe, flow['new_R'], len(kernel), flow['numerical_local_root']))
    log('wrote %s' % out)
    if False:
        source['module_sets'][a.set] = dict(sorted(record.items()))
        (PKG / 'SOURCE.json').write_text(json.dumps(source, indent=1) + '\n')
        log('recorded the modules of %s in SOURCE.json: %s; now run verify.py --write, then verify.py' % (a.set, record))


if __name__ == '__main__':
    main()
