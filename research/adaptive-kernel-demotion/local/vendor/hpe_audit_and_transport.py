"""Rebuild arbitrary-dirt compensation and transport a changed local word.

Prepared for icekylinx with GPT-6 Astra assistance. Apache-2.0.
Adapted from PR425/433 (icekylinx), PR484's audit_gk.py
(DreamingOfClouds), and Round19's 112-port transport. This auditor does not
import a constructor, a nominated compensation table, or a global price.
Only the changed scalar word and its actual frame chains are checked here.
"""
import argparse
import copy
import gzip
import hashlib
import json
import time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def content_hash(path):
    data = path.read_bytes()
    return hashlib.sha256(gzip.decompress(data) if path.suffix == '.gz' else data).hexdigest()


def basis(vs):
    pivots = {}
    for x in vs:
        for k in sorted(pivots, reverse=True):
            if x >> k & 1:
                x ^= pivots[k]
        if x:
            k = x.bit_length() - 1
            for j in pivots:
                if pivots[j] >> k & 1:
                    pivots[j] ^= x
            pivots[k] = x
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def apply(e, rows):
    if e[0] == 'scale':
        _, target, a, b, *_ = e
        q = Q(a, b)
        assert q
        rows[target] = {j: q*x for j, x in rows[target].items()}
    else:
        _, target, source, a, b, *_ = e
        assert target != source
        q = Q(a, b)
        for j, x in list(rows[source].items()):
            value = rows[target].get(j, Q(0)) + q*x
            if value:
                rows[target][j] = value
            else:
                rows[target].pop(j, None)


def inverse(e):
    e = copy.deepcopy(e)
    if e[0] == 'add':
        e[3] *= -1
    else:
        e[2], e[3] = e[3], e[2]
    return e


def dual(e):
    e = inverse(e)
    if e[0] == 'add':
        e[1], e[2] = e[2], e[1]
    return e


def state_maps(prefix, n):
    """P = exact state map of the prefix (precondition + compensation + A + cut + B), and P^-1 (rows as sparse dicts)."""
    P = [{r: Q(1)} for r in range(n)]
    for e in prefix:
        apply(e, P)
    Pinv = [{r: Q(1)} for r in range(n)]
    for e in reversed(prefix):
        apply(inverse(e), Pinv)
    return P, Pinv


def cone_violations(P, Pinv, hpe, mapping, endB, final, frames):
    """COLD-HPE / CONE PRE-CHECK.  Necessary conditions for helper h (raw index) to end at U = final[h] under ANY
    monotone common-frame cleanup of the end-of-B state P (frames only climb, every gate at a common frame):
      row    (J26-H dependency bound): every g in supp(row h of P^-1) has end-of-B frame <= U -- h is rebuilt from them;
      column (dirt-column lemma):       every g != h with P[g][h] != 0 has end-of-B frame <= U -- the column of P at h,
             restricted to rows whose frame is not <= U, changes only by invertible row operations unless h is read at a
             frame not <= U, so it can reach e_h only if it is already zero there.
    Both are implied by the exact endpoint replay plus the frame checks below; here they fail FAST, with the reason."""
    inside = lambda a, b: basis(frames[a] + frames[b]) == frames[b]
    viol = []
    for h in hpe:
        U = final[mapping[h]]
        viol += [('row', h, g) for g, x in sorted(Pinv[h].items()) if x and not inside(endB[mapping[g]], U)]
        viol += [('column', h, g) for g in range(len(P)) if g != h and P[g].get(h) and not inside(endB[mapping[g]], U)]
    return viol


def run(raw_path, routing_path, out):
    start_time = time.monotonic()
    word, routing = read(raw_path), read(routing_path)
    v, h, helpers = word['report']['v'], word['report']['h'], word['report']['R']
    assert h == 9 and v == 112 and routing['v'] == v
    n = 2*v + helpers
    ident = lambda: [{r: Q(1)} for r in range(n)]
    main = word['A'] + word['cut'] + word['B']
    assert all(not v <= e[2] < 2*v for e in word['A'] + word['B']
               if e[0] == 'add' and not v <= e[1] < 2*v)
    matrix = ident()
    for e in main:
        apply(e, matrix)
    dirty = [{} for _ in range(n)]
    for r in range(v, 2*v):
        dirty[r] = {j: x for j, x in matrix[r].items() if j >= 2*v}
    for e in word['precondition']:
        apply(e, dirty)
    compensation = [['add', r, j, -q.numerator, q.denominator, []]
                    for r in range(v, 2*v) for j, q in sorted(dirty[r].items())]
    entering = set(map(int, word.get('start_extra', {})))
    assert all(e[2] not in entering for e in compensation), 'zero-frame compensation reads an entering helper'
    cleanup = [inverse(e) for e in reversed(word['A'] + word['B'])
               if not v <= e[1] < 2*v]
    if 'refactored_cleanup' in word:
        # REFACTORED CLEANUP (cold low-frame ends): the cleanup is not the literal reversed inverse of A+B but another exact
        # factorisation of the same inverse.  Nothing about it is trusted: it may only touch non-target registers (T rows
        # stay the compensated data accumulators), every gate is dyadic (checked below), and the arbitrary-dirt endpoint
        # replay below must be exact in BOTH orientations for the full reordered program.  Inherited words keep the literal
        # assertion (the else branch), so their outputs are unchanged.
        assert all(not v <= r < 2*v for e in word['cleanup'] for r in ([e[1]] + ([e[2]] if e[0] == 'add' else []))), 'refactored cleanup touches a target'
        assert all(e[0] in ('add', 'scale') for e in word['cleanup'])
        cleanup = word['cleanup']
    else:
        assert [e[:-1] for e in cleanup] == [e[:-1] for e in word['cleanup']], 'cleanup is not the literal reversed inverse of A+B'
    # HPE: hyperplane-ended helpers.  'early_cleanup' = [[cleanup index, frame vectors], ...] are cleanup gates executed
    # right after B (before the final climbs) at the given frame; 'helper_final' = {helper: frame vectors} replaces FULL as
    # that helper's terminal frame.  The scalar program is the reordered one and is replayed exactly below, so a move that
    # does not commute with the skipped cleanup prefix is rejected by the arbitrary-dirt endpoint assertion.
    early = [(int(i), f) for i, f in word.get('early_cleanup', [])]
    helper_final = {int(r): f for r, f in word.get('helper_final', {}).items()}
    early_idx = [i for i, _ in early]
    assert len(set(early_idx)) == len(early_idx) and all(0 <= i < len(cleanup) for i in early_idx)
    assert all(2*v <= r < n for r in helper_final)
    # COLD-HPE: a COLD helper (not in start_extra, entrance frame 0 = bottom) may also end at a proper subspace U.
    # It is the E = bottom instance of #593's theorems: its wrappers are the (0, U) recipes R_{0,U}, L_{0,U} (checked
    # exactly by hpe_adapters_local), emitted as residual_adapter events like an entering helper's.
    cold_hpe = sorted(r for r in helper_final if r not in entering)
    # COLD-HPE wrapper order: R_{0,U}^-1 is emitted with the entry adapters, after the zero-frame precondition and
    # compensation, so (exactly as for an entering helper, asserted above) nothing before it may touch a cold-ended helper.
    assert all(r not in set(cold_hpe) for e in word['precondition'] + compensation for r in ([e[1]] + ([e[2]] if e[0] == 'add' else []))), 'zero-frame precondition/compensation touches a cold hyperplane-ended helper before its wrapper'
    # ENTERING helpers (start frame E != 0): their wrapper R_E^-1 precedes every gate on them, so the zero-frame precondition
    # and compensation may not touch them either (mirrors hpe_emit_local's start-frame-0 rule here, at the scalar audit).
    assert all(r not in entering for e in word['precondition'] + compensation for r in ([e[1]] + ([e[2]] if e[0] == 'add' else []))), 'zero-frame precondition/compensation touches an entering helper'
    tail =[word['cleanup'][i][:-1] + [f] for i, f in early]
    rest = [e for i, e in enumerate(word['cleanup']) if i not in set(early_idx)]
    program = word['precondition'] + compensation + main + tail + rest
    for backward in (False, True):
        actual = ident()
        for e in program:
            apply(dual(e) if backward else e, actual)
        expected = ident()
        for t in range(v):
            expected[t if backward else v+t][v+t if backward else t] = Q(-1 if backward else 1)
        assert actual == expected, ('arbitrary-dirt endpoint', backward)
    # The native scalar compiler allows dyadic additions and signed binary scales.
    for e in program:
        q = Q(e[3], e[4]) if e[0] == 'add' else Q(e[2], e[3])
        assert q.denominator & (q.denominator-1) == 0
        if e[0] == 'scale':
            a = abs(q.numerator)
            assert a and a & (a-1) == 0

    tau = lambda x: x ^ (43 if (x & 43).bit_count() % 2 else 0)
    ports = routing['ports']
    assert len(set(ports)) == v and set(map(tau, word['ports'])) == set(ports)
    mapping = {i: ports.index(tau(p)) for i, p in enumerate(word['ports'])}
    mapping.update({v+i: v+mapping[i] for i in range(v)})
    mapping.update({r: r for r in range(2*v, n)})
    full = tuple(1 << i for i in range(h-1, -1, -1))
    frames, frame_ids = [(), full], {(): 0, full: 1}

    def fid(vectors):
        frame = basis(vectors)
        if frame not in frame_ids:
            frame_ids[frame] = len(frames)
            frames.append(frame)
        return frame_ids[frame]

    def transform(e):
        e = copy.deepcopy(e)
        e[1] = mapping[e[1]]
        if e[0] == 'add':
            e[2] = mapping[e[2]]
        if e[-1] is not None:
            e[-1] = fid([tau(x) for x in e[-1]])
        return e

    canonical = {key: [transform(e) for e in word[key]]
                 for key in ('A', 'B', 'cut', 'cleanup', 'precondition')}
    canonical['compensation'] = [transform(e) for e in compensation]
    if tail:
        canonical['tail'] = [transform(e) for e in tail]                  # HPE (absent for inherited words: identical output)
    canonical['cleanup'] = [transform(e) for e in rest]                   # HPE (full cleanup minus the early gates)
    canonical['start'] = [fid([p]) for p in ports] + [0]*(v+helpers)
    for r, frame in word.get('start_extra', {}).items():
        assert 2*v <= int(r) < n
        canonical['start'][int(r)] = fid([tau(x) for x in frame])
    canonical['final'] = ([1]*v +
        [fid(x for x in range(1, 1 << h) if (x & p).bit_count() % 2 == 0) for p in ports] +
        [1]*helpers)
    for r, frame in helper_final.items():                                 # HPE
        canonical['final'][r] = fid([tau(x) for x in frame])
    canonical.update(h=h, v=v, R=helpers, ports=ports, frames=frames,
                     centers=[mapping[r] for r in word['centers']],
                     center_frames=[fid(tau(x) for x in frame) for frame in word['center_frames']])
    levels = {mapping[v+int(t)]-v: fid(tau(x) for x in frame)
              for t, frame in word.get('target_levels', {}).items()}
    canonical['target_levels'] = {str(t): f for t, f in levels.items()}
    current, paid, edges = canonical['start'].copy(), Counter(), set()

    def climb(r, f):
        old = current[r]
        assert basis(frames[old] + frames[f]) == frames[f], ('nonmonotone', r, old, f)
        if old != f:
            degree = len(frames[f]) - len(frames[old])
            assert degree > 0
            paid[degree] += 1
            edges.add((old, f))
            current[r] = f

    for part in ('A', 'B'):
        if part == 'B':
            assert all(current[r] == f for r, f in zip(canonical['centers'], canonical['center_frames']))
            assert all(current[v+t] == levels.get(t, 0) for t in range(v))
            for r, frame in zip(canonical['centers'], canonical['center_frames']):
                served = {levels.get(e[1]-v, 0) for e in canonical['cut'] if e[2] == r}
                old = frame
                for f in sorted(served, key=lambda f: -len(frames[f])):
                    assert basis(frames[old] + frames[f]) == frames[old]
                    if old != f:
                        paid[len(frames[old])-len(frames[f])] += 1
                        edges.add((old, f))
                        edges.add((f, old))
                        old = f
        for e in canonical[part]:
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
                climb(r, e[-1])
    if helper_final:                                                      # COLD-HPE / CONE PRE-CHECK at the end-of-B frames
        P, Pinv = state_maps(word['precondition'] + compensation + main, n)
        cone = cone_violations(P, Pinv, sorted(helper_final), mapping, current.copy(), canonical['final'], frames)
        assert not cone, ('hpe cone pre-check (row / column)', cone[:8])
    for e in canonical.get('tail', []):                                   # HPE: early cleanup gates at their common frame
        for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
            climb(r, e[-1])
    for r, f in enumerate(canonical['final']):
        climb(r, f)
    # HPE: the remaining cleanup runs at FULL, so it may touch only registers whose terminal frame is FULL; a
    # hyperplane-ended helper is touched by nothing after its tail gates.
    for e in canonical['cleanup']:
        assert all(canonical['final'][r] == 1 for r in [e[1]] + ([e[2]] if e[0] == 'add' else [])), ('cleanup on non-FULL end', e)
    assert all(len(frames[canonical['final'][r]]) < h for r in helper_final)
    assert dict(paid) == {int(r): count for r, count in word['report']['local_profile'].items()}, 'paid local profile differs from the reported local_profile'
    canonical['local_profile'] = dict(sorted(paid.items()))
    canonical['edges'] = sorted(edges)
    out.mkdir(parents=True, exist_ok=False)
    payload = json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode()
    (out/'CANONICAL-WORD.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    (out/'FULL-WORD.json.gz').write_bytes(gzip.compress(json.dumps(word, sort_keys=True, separators=(',', ':')).encode(), mtime=0))
    receipt = dict(status='PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES',
                   input_content_sha256=content_hash(raw_path), routing_content_sha256=content_hash(routing_path),
                   canonical_content_sha256=hashlib.sha256(payload).hexdigest(),
                   live_columns_each_orientation=n, helpers=helpers,
                   compensation_additions=len(compensation), scalar_operations=len(program),
                   center_rank_sum=sum(map(len, word['center_frames'])),
                   local_profile=dict(sorted(paid.items())), local_rank_mass=sum(r*z for r, z in paid.items()),
                   widths=[len(frames[canonical['final'][r]])-len(frames[canonical['start'][r]]) for r in range(2*v, n)],
                   frames=len(frames), directed_edges=len(edges),
                   tau=43, target_port_order_matches_baseline=True,
                   seconds=time.monotonic()-start_time,
                   scope='Fresh exact forward and inverse-transpose scalar replay on every arbitrary input; all native frame chains and dyadic primitives. Phase lowering, wrappers, global owners and global assembly are separate.')
    if tail or helper_final:
        receipt.update(hyperplane_ended_helpers=sorted(helper_final), early_cleanup_gates=len(tail))
    if cold_hpe:                                                          # COLD-HPE (absent for words without cold ends)
        receipt.update(cold_hyperplane_ended_helpers=cold_hpe)
    if 'refactored_cleanup' in word:                                      # REFACTORED CLEANUP (absent for inherited words)
        receipt.update(refactored_cleanup_gates=len(word['cleanup']), refactored_cleanup=word['refactored_cleanup'])
    (out/'SCALAR-FRAME-AUDIT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: value for k, value in receipt.items() if k != 'widths'}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--routing', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.raw, args.routing, args.out)
