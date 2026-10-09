#!/usr/bin/env python3
"""Physical frame descent and compensated birth-cut reuse on the selected paired-cube complex word.

Prepared by eumemic with Anthropic Claude assistance. Apache-2.0. The signed word, frozen arcs, gauges,
chronology and shared-core accounting are icekylinx's PR144. Frame descent under PR130's general Clifford
frames and compensated birth-cut reuse follow PR131 and jamesyc's PR124; deadline (late) compensation reads
follow PR143. Frozen inputs: references/paired-cube/physical/{frames,pairs}.json.

Checks, from the regenerated PR144 word and the frozen inputs only:
  * every operation frame contains its node's value span, and every role chain
      start -> operation frames -> root frame -> full space
    is nested, with each recipient's chain spliced after its donor's last operation;
  * every pair: donor ungauged, not a root, its last operation before the recipient's old-value read; the
    recipient gauged and untouched before its read; donor last frame inside the recipient gauge; reads in
    chronological order keep every target chain nested;
  * the spliced positive-rank recount gives the shared-core profile with W = 2v + R - pairs and the unchanged
    deficit 2v - 3 loss;
  * an exact numeric replay mod 2^61-1 of the aliased signed word with arbitrary dirty scratch restores every
    slot and adds x to y, for two seeds; omitting one recipient's read, reading a late recipient before its
    donor's last operation, or flipping one signed coefficient is rejected.
Writes certificates/paired-cube-physical-input.json with --write; otherwise checks it.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import sys
import tempfile

from paired_cube.frames import basis, perp, contained

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references/paired-cube/physical'
OUTPUT = ROOT / 'certificates/paired-cube-physical-input.json'
P = (1 << 61) - 1


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def regenerated_word():
    from paired_cube_producer import regenerate
    expected = json.loads((ROOT / 'certificates/paired-cube-complex-input.json').read_text())
    with tempfile.TemporaryDirectory(prefix='paired-cube-physical-') as d:
        regenerate(expected, Path(d))
        return tuple(json.loads((Path(d) / name).read_text())
                     for name in ('graph.json', 'frames.json', 'selection.json')) + (expected,)


def physical(g, witness, word, record, frames_in, pairs_in):
    h, v, R = g['h'], g['v'], record['R']
    full = basis(1 << i for i in range(h))
    args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g['args']]
    inputs = g['inputs']
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    ann = witness['annihilators']
    ops = [tuple(o) for o in word['ops']]
    coef = [tuple(c) for c in word['opcoeff']]
    phase1 = sorted(word['phase1'])
    pset = set(phase1)
    rest = [i for i in range(len(ops)) if i not in pset]
    sources = {int(x): s for x, s in word['sources'].items()}
    require(len(ops) == record['total_M_operations'], 'Operation count')
    spans = [()] * len(args)
    for x in range(1, len(args)):
        spans[x] = (inputs[x - 1],) if args[x] is None else basis(spans[args[x][0]] + spans[args[x][1]])
    frames = [perp(tuple(ann[x]), h) for _, _, x in ops]  # PR144's full backward-intersection frames
    moved = set()
    for i, F in frames_in:
        require(i not in moved and basis(F) == tuple(F) != frames[i], 'Duplicate, noncanonical or unmoved frame')
        frames[i] = tuple(F)
        moved.add(i)
    changed = len(moved)
    for i, (_, _, x) in enumerate(ops):
        require(contained(spans[x], frames[i]), 'Value span outside operation frame')
    start = [()] * R
    for x, s in sources.items():
        start[s] = (inputs[x - 1],)
    gauge = {}
    for z in word['selected']:
        gauge[z['role']] = perp(tuple(z['annihilator']), h)
        require(len(gauge[z['role']]) == z['rank'], 'Gauge rank')
        start[z['role']] = gauge[z['role']]
    rootframe, rootkind, rootann = {}, {}, {}
    for r, s in zip(roots, word['rootroles']):
        if r['kind'] == 'center':
            U = spans[r['node']]
            require(len(U) == h - 2, 'Centre frame rank')
            A = perp(U, h)
        else:
            A = basis(inputs[t] for t in r['targets'])
            U = perp(A, h)
        require(s not in rootframe, 'Duplicate root role')
        rootframe[s], rootkind[s], rootann[s] = U, r['kind'], A
    role_ops = defaultdict(list)
    for i, (a, b, _) in enumerate(ops):
        require(a != b, 'Gate ports')
        role_ops[a].append(i)
        role_ops[b].append(i)
    position = {i: k for k, i in enumerate(phase1 + rest)}

    def chain(s):
        return [start[s]] + [frames[i] for i in role_ops[s]] + ([rootframe[s]] if s in rootframe else []) + [full]

    # Pairs and deadlines.
    pairs = [(int(a), int(b)) for a, b, _ in pairs_in]
    deadline = {int(b): (None if t is None else int(t)) for _, b, t in pairs_in}
    donors = {a: b for a, b in pairs}
    merge = {b: a for a, b in pairs}
    require(len(donors) == len(merge) == len(pairs) and not set(donors) & set(merge), 'Pair aliases')
    first = {s: l[0] for s, l in role_ops.items()}
    for a, b in pairs:
        require(a not in gauge and a not in rootframe, 'Donor kind')
        require(b in gauge, 'Recipient kind')
        last = role_ops[a][-1]
        t = deadline[b]
        if t is None:  # read at the phase cut, after all of phase one
            require(last in pset and first[b] not in pset, 'Early pair chronology')
        else:          # read immediately before operation t, the recipient's first operation
            require(t == first[b] and t not in pset and position[last] < position[t], 'Late pair chronology')
        require(contained(frames[last], gauge[b]), 'Donor frame outside recipient gauge')
    # Chains, the spliced recount and the profile.
    local = Counter()
    for s in range(R):
        seq = chain(s)
        require(all(contained(A, B) for A, B in zip(seq, seq[1:])), 'Role chain nesting')
        if s in merge:
            continue
        if s in sources.values():
            local[1] += 1
        if s in donors:
            seq = seq[:-1] + chain(donors[s])
        dims = [len(F) for F in seq]
        local.update(d1 - d0 for d0, d1 in zip(dims, dims[1:]) if d1 > d0)
        for t in (s, donors.get(s)):
            if t is not None and rootkind.get(t) == 'center':
                local[len(rootframe[t])] += 1
    # Target chains along the actual read chronology (late reads move; sides last; inputs end).
    cut = len(phase1)
    when = {z['role']: (cut if deadline.get(z['role']) is None else position[deadline[z['role']]], k)
            for k, z in enumerate(reversed(word['selected']))}
    current = [full] * v
    target = Counter()
    for z in sorted(word['selected'], key=lambda z: when[z['role']]):
        A = tuple(z['annihilator'])
        for t in z['targets']:
            require(contained(A, current[t]), 'Target chain order')
            target[len(current[t]) - len(A)] += 1
            current[t] = A
    for r, s in zip(roots, word['rootroles']):
        if r['kind'] == 'side':
            for t in r['targets']:
                require(contained(rootann[s], current[t]), 'Side target order')
                target[len(current[t]) - len(rootann[s])] += 1
                current[t] = rootann[s]
    for t, q in enumerate(inputs):
        require(contained((q,), current[t]), 'Target input')
        target[len(current[t]) - 1] += 1
    require(dict(target) == {int(k): n for k, n in record['target_data_histogram'].items()}, 'Target histogram')
    source = Counter({int(k): n for k, n in record['source_data_histogram'].items()})
    children = Counter({r: 3 * n for r, n in local.items() if r})
    children.update({r: 3 * n for r, n in source.items() if r})
    children.update({r: 3 * n for r, n in target.items() if r})
    tails = Counter(len(U) for s, U in gauge.items() if s not in merge)
    children.update({3 * d: n for d, n in tails.items() if d})
    children[2] += 2 * v
    m, W = 3 * h, 2 * v + R - len(pairs)
    rank = sum(r * n for r, n in children.items())
    require(W * m - rank == 2 * v - 3 * record['loss'] == record['deficit_per_vertex'], 'Telescoping deficit')
    require(all(0 < r < m for r in children), 'Proper children')
    replay = scalar_replay(g, word, R, pairs, deadline, ops, coef, phase1, rest, sources, roots)
    return dict(h=h, v=v, R=R, physical_R=R - len(pairs), pairs=len(pairs),
                late_pairs=sum(t is not None for t in deadline.values()), changed_operation_frames=changed,
                m=m, W_per_vertex=W, rank_per_vertex=rank, deficit_per_vertex=W * m - rank, loss=record['loss'],
                local_histogram=dict(sorted(local.items())), physical_gauge_histogram=dict(sorted(tails.items())),
                source_data_histogram=dict(sorted(source.items())), target_data_histogram=dict(sorted(target.items())),
                child_histogram=dict(sorted(children.items())), scalar_replay=replay,
                checks=dict(value_spans_inside_frames=True, role_chains_nested=True, pair_chronology=True,
                            donor_frames_inside_gauges=True, target_chains_nested_in_read_order=True,
                            telescoping_deficit=True))


def scalar_replay(g, word, R, pairs, deadline, ops, coef, phase1, rest, sources, roots):
    h, v, inputs, labels = g['h'], g['v'], g['inputs'], g['labels']
    inv = lambda a: pow(a % P, P - 2, P)
    half, third, sixth = inv(2), inv(3), inv(6)
    selected = [z['role'] for z in word['selected']]
    deferred = set(selected)
    cseed, dseed = {}, {}
    for r, s in zip(roots, word['rootroles']):
        if r['kind'] == 'center':
            cseed[s] = [int(k == r['coordinate']) for k in range(h)]
        else:
            dseed[s] = {t: half if q == '1/2' else P - half for t, q in zip(r['targets'], r['coefficients'])}
    cvec = [None] * R
    dpart = [dict() for _ in range(R)]
    for s, c in cseed.items():
        cvec[s] = list(c)
    for s, d in dseed.items():
        dpart[s] = dict(d)
    for (a, b, _), (ca, cb) in zip(reversed(ops), reversed(coef)):
        if cvec[a] is not None:
            cvec[b] = [(cb * u) % P for u in cvec[a]] if cvec[b] is None else \
                [(w + cb * u) % P for w, u in zip(cvec[b], cvec[a])]
        for t, u in dpart[a].items():
            dpart[b][t] = (dpart[b].get(t, 0) + cb * u) % P
        if ca != 1:
            if cvec[a] is not None:
                cvec[a] = [(ca * u) % P for u in cvec[a]]
            dpart[a] = {t: (ca * u) % P for t, u in dpart[a].items()}
    scatter = [[third if c in labels[t] else P - sixth for t in range(v)] for c in range(h)]
    merge = {b: a for a, b in pairs}
    late_at = defaultdict(list)
    for b, t in deadline.items():
        if t is not None:
            late_at[t].append(b)
    leaf = {s: x for x, s in sources.items()}
    cubes = [range(k, k + 8) for k in range(0, v, 8)]

    def run(seed, omit=None, early=None, flip=None):
        rng = random.Random(seed)
        live = sorted(set(range(R)) - set(merge))
        slot = {s: i for i, s in enumerate(live)}
        alias = lambda s: slot[merge.get(s, s)]
        x = [rng.randrange(P) for _ in range(v)]
        z = [rng.randrange(P) for _ in live]
        y0 = [rng.randrange(P) for _ in range(v)]
        a, y, yc, chron = list(z), list(y0), [0] * h, []

        def read(s, sign, seed_only=False):
            val = a[alias(s)]
            c = cseed.get(s) if seed_only else cvec[s]
            d = dseed.get(s, {}) if seed_only else dpart[s]
            if c is not None:
                for k, u in enumerate(c):
                    yc[k] = (yc[k] + sign * u * val) % P
            for t, u in d.items():
                y[t] = (y[t] + sign * u * val) % P

        def gate(i):
            (dst, src, _), (ca, cb) = ops[i], coef[i]
            cb = -cb if flip == i else cb
            dd, ss = alias(dst), alias(src)
            require(dd != ss, 'Aliased gate ports')
            a[dd] = (ca * a[dd] + cb * a[ss]) % P
            chron.append((dd, ss, ca, cb))
        for s in range(R):
            if s not in deferred and s not in merge:
                read(s, -1)
        for s, xn in leaf.items():
            a[alias(s)] = (a[alias(s)] + x[xn - 1]) % P
            chron.append((alias(s), None, xn - 1, None))
        for i in phase1:
            gate(i)
        for s in cseed:
            read(s, +1, True)
        for s in reversed(selected):
            if s != omit and (deadline.get(s) is None or s == early):
                read(s, -1)
        for i in rest:
            for s in late_at.get(i, ()):
                if s != omit and s != early:
                    read(s, -1)
            gate(i)
        for s in dseed:
            read(s, +1, True)
        for cube in cubes:
            qs = [inputs[t] for t in cube]
            for i, t in enumerate(cube):
                acc = sum(x[s] if (qs[i] ^ qs[j]).bit_count() == 6 else -x[s] if (qs[i] ^ qs[j]).bit_count() == 2
                          else 0 for j, s in enumerate(cube))
                y[t] = (y[t] + acc * half) % P
        for k in range(h):
            if yc[k]:
                for t in range(v):
                    y[t] = (y[t] + yc[k] * scatter[k][t]) % P
        for dd, ss, ca, cb in reversed(chron):
            if ss is None:
                a[dd] = (a[dd] - x[ca]) % P
            else:
                a[dd] = (ca * (a[dd] - cb * a[ss])) % P
        return a == z, all((y[t] - y0[t] - x[t]) % P == 0 for t in range(v))
    result = {'seed1': run(1), 'seed2': run(2)}
    require(all(r == (True, True) for r in result.values()), 'Aliased dirty-scratch replay')
    controls = {}
    if pairs:
        controls['omitted_recipient_read'] = run(3, omit=pairs[0][1])
    late = [b for b, t in deadline.items() if t is not None]
    if late:
        controls['late_read_before_donor_death'] = run(4, early=late[-1])
    controls['flipped_signed_operation'] = run(5, flip=next(i for i, c in enumerate(coef) if c[1] == -1))
    require(all(r[1] is False for r in controls.values()), 'Replay control accepted')
    return dict(modulus='2^61-1', seeds_restored_and_y_plus_x=True,
                rejected_controls=sorted(controls), slots=R - len(pairs))


def checked_record():
    g, witness, word, record = regenerated_word()
    frames_in = json.loads((REF / 'frames.json').read_text())['frames']
    pairs_in = json.loads((REF / 'pairs.json').read_text())['pairs']
    result = physical(g, witness, word, record, frames_in, pairs_in)
    require(json.loads(OUTPUT.read_text()) == json.loads(json.dumps(result)), 'Frozen physical input differs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    a = parser.parse_args()
    g, witness, word, record = regenerated_word()
    frames_in = json.loads((REF / 'frames.json').read_text())['frames']
    pairs_in = json.loads((REF / 'pairs.json').read_text())['pairs']
    result = physical(g, witness, word, record, frames_in, pairs_in)
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.write:
        OUTPUT.write_text(text)
    else:
        require(OUTPUT.read_text() == text, 'Frozen physical input differs')
    print('PASS physical paired-cube word: %d operation frames moved, %d pairs (%d late), W %d, rank %d, deficit %d'
          % (result['changed_operation_frames'], result['pairs'], result['late_pairs'], result['W_per_vertex'],
             result['rank_per_vertex'], result['deficit_per_vertex']), flush=True)


if __name__ == '__main__':
    main()
