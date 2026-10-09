#!/usr/bin/env python3
"""Physical paired-cube bit word: per-operation frames, deferred old-value reads and compensated register reuse.

Prepared by eumemic with Anthropic Claude assistance. Apache-2.0. The bit word, its decoder, exact frames and
ledger are the paired-cube bit word of research/paired-cube-bit (PR144's bit ledger). Frame descent under PR130's
general Clifford frames follows PR131; compensated birth-cut reuse follows jamesyc's PR124; deadline (late) reads
follow PR143. Frozen input: references/paired-cube/bit-physical (the word with per-operation frames, read times
and pairs; its exact frames; the partner-pair chronology).

Checks, from the package graph and the frozen word only, with the package checker's exact integer algebra:
  * exact frames; the mod-2 decoder and the source, root and centre geometry of the package checker;
  * register contents: every operation leaves its node's support in its destination (an addition combines the
    supports of its two operands, a copy starts from an empty register), every source role starts with its leaf;
  * every operation frame is G-nondegenerate and contains its node's span, and every role chain
      start -> operation frames (execution order: phase one first) -> root frame -> full space
    is nested and ascending, with each recipient's chain spliced after its donor's last operation; phase one is
    the centre closure and gauged roles are untouched in it;
  * gauges: targets are the response support, frames G-nondegenerate; every gauge is read after phase one and no
    later than its role's first operation;
  * pairs: a matching; the donor is not a root role and its last operation precedes the recipient's read; the
    recipient is gauged; the donor's last frame lies in the recipient's gauge;
  * target chains nested in the actual read chronology; the partner-pair chronology;
  * the spliced recount: W = 2v + R - pairs, recipients' gauge exteriors dropped, deficit 2v - 3 loss;
  * an exact 64-lane F2 replay of the aliased word with arbitrary dirty scratch and time-ordered old-value reads
    restores every register and source and adds x to y, for two seeds; omitting one recipient's read, reading a
    late recipient at the phase cut before its donor's last write, or aliasing a recipient onto a live register
    is rejected.
Writes certificates/paired-cube-bit-physical-input.json with --write; otherwise checks it.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
BIT = ROOT / 'research/paired-cube-bit'
REF = ROOT / 'references/paired-cube/bit-physical'
OUTPUT = ROOT / 'certificates/paired-cube-bit-physical-input.json'
P = 12
LANES = 64
sys.path.insert(0, str(BIT))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read_json(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def loaded(folder=None, package=BIT / 'out'):
    """The package checker's exact algebra on the package graph and a physical word folder; without a frozen
    physical word, the package word itself (operation frames = node frames, no pairs)."""
    from check_paired_cube_bit import Checker  # refuses python -O

    def find(name):
        path = folder / ('%s_p%d.json' % (name, P))
        return path if path.exists() else path.with_suffix('.json.gz')
    if folder is None:
        folder = REF if (REF / ('word_p%d.json.gz' % P)).exists() else package
    chk = Checker.__new__(Checker)
    chk.mut = None
    chk.g = read_json(package / ('graph_p%d.json' % P))
    chk.prof = read_json(package / ('profile_p%d.json' % P))
    chk.w, chk.fr, chk.k = (read_json(find(name)) for name in ('word', 'frames', 'kchron'))
    chk.h, chk.v = chk.g['h'], chk.g['v']
    return chk


def physical(chk):
    from check_paired_cube_bit import dot, reduce_rows
    chk.frames()
    chk.decoder()
    chk.geometry()
    g, w, h, v = chk.g, chk.w, chk.h, chk.v
    dim, sub, nondeg = chk.dimf, chk.sub, chk.nondeg
    args, sup, nf = g['args'], chk.sup, chk.nf
    ops = [tuple(o) for o in w['ops']]
    opf = w.get('op_frame') or [nf[x] for _, _, x in ops]
    require(len(opf) == len(ops) and all(f in dim for f in opf), 'Operation frames')
    roots, rootroles, rf, full = g['roots'], w['rootroles'], w['root_frame'], w['full_frame']
    sources = {int(x): s for x, s in w['sources'].items()}
    rootroles_set = set(rootroles)
    R = 1 + max(max(max(a, b) for a, b, _ in ops), max(rootroles), max(sources.values()))
    phase1 = sorted(w['phase1'])
    pset = set(phase1)
    rest = [i for i in range(len(ops)) if i not in pset]
    order = phase1 + rest
    position = {i: k for k, i in enumerate(order)}
    cut = len(phase1)
    # Phase one is the closure of the centre roots' last operations under per-role precedence.
    previous, pred = {}, []
    for i, (a, b, _) in enumerate(ops):
        pred.append((previous.get(a, -1), previous.get(b, -1)))
        previous[a] = previous[b] = i
    stack = [previous[s] for r, s in zip(roots, rootroles) if r['kind'] == 'center' and s in previous]
    closure = set()
    while stack:
        i = stack.pop()
        if i not in closure:
            closure.add(i)
            stack.extend(j for j in pred[i] if j >= 0)
    require(closure == pset, 'Phase one is the centre closure')
    # Register contents along the execution order.
    content = [0] * R
    for x, s in sources.items():
        content[s] = 1 << x
    role_ops = defaultdict(list)
    for i in order:
        a, b, x = ops[i]
        require(a != b, 'Gate ports')
        if content[a]:
            require(args[x] is not None and {content[a], content[b]} == {sup[y] for y in args[x]}, 'Addition operands')
        else:
            require(content[b] == sup[x], 'Copied value')
        content[a] |= content[b]
        role_ops[a].append(i)
        role_ops[b].append(i)
    require(all(l == sorted(l) for l in role_ops.values()), 'Execution order keeps every role order')
    require(all(s in role_ops or s in rootroles_set for s in range(R)), 'Every role is used')
    # Operation frames: moved frames are G-nondegenerate and contain their node's span.
    chi = chk.chi
    span = {}

    def node_span(x):
        stack = [x]
        while stack:
            y = stack[-1]
            if y in span:
                stack.pop()
            elif args[y] is None:
                span[y] = [chi[y]]
                stack.pop()
            elif all(z in span for z in args[y]):
                span[y] = reduce_rows(span[args[y][0]] + span[args[y][1]], h)[0]
                stack.pop()
            else:
                stack.extend(z for z in args[y] if z not in span)
        return span[x]
    moved = 0
    for f, (_, _, x) in zip(opf, ops):
        if f != nf[x]:
            moved += 1
            require(all(chk.in_frame(u, f) for u in node_span(x)), 'Node span inside operation frame')
    used = set(opf) | set(rf) | set(w['source_frame']) | {z['frame'] for z in w['gauges']}
    used |= {e['mix_frame'] for e in chk.k['entries']}
    require(all(nondeg(f) for f in used), 'G-nondegenerate frames')
    # Starts, gauges and root frames.
    start = {s: w['source_frame'][x] for x, s in sources.items()}
    rootframe = {}
    for j, s in enumerate(rootroles):
        require(s not in rootframe, 'Duplicate root role')
        rootframe[s] = rf[j]
    co = [0] * R
    for r, s in zip(roots, rootroles):
        for t in r['targets']:
            co[s] |= 1 << t
    for i in reversed(order):
        a, b, _ = ops[i]
        co[b] |= co[a]
    touched = {s for i in phase1 for s in ops[i][:2]}
    gauge = {}
    for z in w['gauges']:
        s = z['role']
        require(s not in gauge and s not in start and s not in touched and s in role_ops, 'Gauged role')
        require(sum(1 << t for t in z['targets']) == co[s], 'Gauge targets are the response support')
        require(dim[z['frame']] == z['dim'] > 0, 'Gauge dimension')
        gauge[s] = z
        start[s] = z['frame']
    # Read chronology: before position p means before the operation order[p]; ties in reverse selection order.
    reads = {int(s): t for s, t in w.get('reads', {}).items()}
    require(set(reads) <= set(gauge), 'Reads of gauged roles only')
    when = {}
    for k, z in enumerate(reversed(w['gauges'])):
        s = z['role']
        t = reads.get(s, cut)
        require(cut <= t <= position[role_ops[s][0]], 'Gauge read after phase one and before the first operation')
        when[s] = (t, k)
    # Pairs.
    pairs = [tuple(p) for p in w.get('pairs', [])]
    donors = {a: b for a, b in pairs}
    merge = {b: a for a, b in pairs}
    require(len(donors) == len(merge) == len(pairs) and not set(donors) & set(merge), 'Pair matching')
    for a, b in pairs:
        require(a in role_ops and a not in rootframe and b in gauge, 'Pair kinds')
        last = role_ops[a][-1]
        require(position[last] < when[b][0], 'Donor dies before the recipient read')
        require(sub(opf[last], gauge[b]['frame']), 'Donor frame inside recipient gauge')

    def chain(s):
        return [start.get(s)] + [opf[i] for i in role_ops[s]] + ([rootframe[s]] if s in rootframe else []) + [full]
    # Role chains, spliced at every pair, and the local recount.
    local = Counter()
    for s in range(R):
        if s in merge:
            continue
        seq = chain(s)
        if seq[0] is not None and s not in gauge:
            local[1] += 1  # source injection at <chi_S>
        if s in donors:
            seq = seq[:-1] + chain(donors[s])
        prev = seq[0]
        d0 = 0 if prev is None else dim[prev]
        for f in seq[1:]:
            require(prev is None or sub(prev, f), 'Role chain nesting')
            require(dim[f] >= d0, 'Ascending role chain')
            if dim[f] > d0:
                local[dim[f] - d0] += 1
            prev, d0 = f, dim[f]
    for r, f in zip(roots, rf):
        if r['kind'] == 'center':
            local[dim[f]] += 1  # copied-centre transform
    # Partner-pair chronology on the source registers.
    labels = [set(l) for l in g['labels']]
    source, members = Counter(), Counter()
    for e in chk.k['entries']:
        c, d, mix, cap = e['carrier'], e['passive'], e['mix_frame'], e['deliver_frame']
        require(len(labels[c] & labels[d]) == 1, 'Orthogonal partner pair')
        require(dim[mix] == 2 and chk.in_frame(chi[c], mix) and chk.in_frame(chi[d], mix), 'Mix frame')
        require(sub(mix, cap) and all(dot(chk.cov[t], u) == 0 for t in e['receivers'] for u in chk.B[cap]),
                'Delivery frame inside the receiver caps')
        require(e['carrier_chain'] == [w['source_frame'][c], mix, cap, full] and
                e['passive_chain'] == [w['source_frame'][d], mix, full], 'Partner chains')
        for ch in (e['carrier_chain'], e['passive_chain']):
            for f1, f2 in zip(ch, ch[1:]):
                require(sub(f1, f2), 'Nested partner chain')
                source[dim[f2] - dim[f1]] += 1
        members[c] += 1
        members[d] += 1
    require(all(members[s] == 1 for s in range(v)), 'Each source in one partner pair')
    # Target chains in the actual read chronology: gauge reads, side caps in root order, partner deliveries.
    events = defaultdict(list)
    for s in sorted(when, key=when.get):
        for t in gauge[s]['targets']:
            events[t].append(gauge[s]['frame'])
    deliveries = defaultdict(list)
    for e in chk.k['entries']:
        deliveries[e['deliver_after_root']].append(e)
    for j, r in enumerate(roots):
        if r['kind'] == 'side':
            for t in r['targets']:
                events[t].append(rf[j])
            for e in deliveries.get(j, ()):
                require(sorted(e['receivers']) == sorted(r['targets']), 'Delivery after the receivers own root')
                for t in e['receivers']:
                    events[t].append(e['deliver_frame'])
    require(set(deliveries) <= set(range(len(roots))), 'Delivery roots')
    target = Counter()
    for t in range(v):
        prev, d0 = None, 0
        for f in events[t]:
            require(prev is None or sub(prev, f), 'Target chain nesting')
            require(all(dot(chk.cov[t], u) == 0 for u in chk.B[f]), 'Target frame inside the cap')
            if dim[f] > d0:
                target[dim[f] - d0] += 1
            prev, d0 = f, dim[f]
        require(d0 <= h - 1, 'Target chain below the cap')
        if d0 < h - 1:
            target[h - 1 - d0] += 1
    # The PR144 bit ledger with the spliced chains.
    m, loss = 3 * h, chk.prof['loss']
    children = Counter()
    for part in (local, source, target):
        for r, n in part.items():
            if r and n:
                children[r] += 3 * n
    tails = Counter(z['dim'] for s, z in gauge.items() if s not in merge)
    for d, n in tails.items():
        children[3 * d] += n
    children[2] += 2 * v
    W = 2 * v + R - len(pairs)
    rank = sum(r * n for r, n in children.items())
    require(W * m - rank == 2 * v - 3 * loss, 'Telescoping deficit')
    require(all(0 < r < m for r in children), 'Proper children')
    replay = f2_replay(chk, ops, order, cut, R, sources, when, pairs, role_ops, position)
    srt = lambda c: {r: n for r, n in sorted(c.items()) if n}
    return dict(h=h, v=v, R=R, physical_R=R - len(pairs), pairs=len(pairs),
                late_pairs=sum(when[b][0] > cut for _, b in pairs), operations=len(ops),
                changed_operation_frames=moved, m=m, W_per_vertex=W, rank_per_vertex=rank,
                deficit_per_vertex=W * m - rank, loss=loss, local_histogram=srt(local),
                physical_gauge_histogram=srt(tails), source_data_histogram=srt(source),
                target_data_histogram=srt(target), child_histogram=srt(children), f2_replay=replay,
                checks=dict(register_contents=True, operation_frames_nondegenerate_and_spanning=True,
                            role_chains_nested=True, phase_one_closure=True, gauge_read_window=True,
                            pair_chronology=True, donor_frames_inside_gauges=True,
                            target_chains_nested_in_read_order=True, partner_chronology=True,
                            telescoping_deficit=True))


def f2_replay(chk, ops, order, cut, R, sources, when, pairs, role_ops, position):
    g, w, v = chk.g, chk.w, chk.v
    roots, rootroles = g['roots'], w['rootroles']
    # Exact F2 response of every role's content before its first operation (all reads after the producer).
    response = [0] * R
    for r, s in zip(roots, rootroles):
        for t in r['targets']:
            response[s] ^= 1 << t
    for i in reversed(order):
        a, b, _ = ops[i]
        response[b] ^= response[a]
    gauged = sorted(when, key=when.get)
    merge = {b: a for a, b in pairs}
    centres = [(r, s) for r, s in zip(roots, rootroles) if r['kind'] == 'center']
    sides = [(j, r, s) for j, (r, s) in enumerate(zip(roots, rootroles)) if r['kind'] == 'side']
    deliveries = defaultdict(list)
    for e in chk.k['entries']:
        deliveries[e['deliver_after_root']].append(e)

    def run(seed, omit=None, early=None, alias=None):
        rng = random.Random(seed)
        slot = list(range(R))
        for b, a in merge.items():
            slot[b] = a
        if alias:
            slot[alias[0]] = alias[1]
        x = [rng.getrandbits(LANES) for _ in range(v)]
        y0 = [rng.getrandbits(LANES) for _ in range(v)]
        z0 = {s: rng.getrandbits(LANES) for s in set(slot)}
        z, y, X = dict(z0), list(y0), list(x)
        at = defaultdict(list)
        for s in gauged:
            if s != omit:
                at[cut if s == early else when[s][0]].append(s)

        def read(s):
            value, mask = z[slot[s]], response[s]
            while mask:
                low = mask & -mask
                y[low.bit_length() - 1] ^= value
                mask ^= low

        def gate(i):
            a, b, _ = ops[i]
            require(slot[a] != slot[b], 'Aliased gate ports')
            z[slot[a]] ^= z[slot[b]]
        for s in range(R):
            if s not in when:
                read(s)
        for leaf, s in sources.items():
            z[slot[s]] ^= X[leaf]
        for i in order[:cut]:
            gate(i)
        for r, s in centres:
            for t in r['targets']:
                y[t] ^= z[slot[s]]
        for p in range(cut, len(order)):
            for s in at.get(p, ()):
                read(s)
            gate(order[p])
        for j, r, s in sides:
            for t in r['targets']:
                y[t] ^= z[slot[s]]
            for e in deliveries.get(j, ()):
                X[e['carrier']] ^= X[e['passive']]
                for t in e['receivers']:
                    y[t] ^= X[e['carrier']]
        for e in chk.k['entries']:
            X[e['carrier']] ^= X[e['passive']]
        for i in reversed(order):
            gate(i)
        for leaf, s in sources.items():
            z[slot[s]] ^= X[leaf]
        return z == z0 and X == x, all(y[t] == y0[t] ^ x[t] for t in range(v))

    def rejected(**control):
        try:
            return run(7, **control)[1] is False
        except AssertionError:
            return True
    result = {'seed1': run(1), 'seed2': run(2)}
    require(all(r == (True, True) for r in result.values()), 'Aliased dirty-scratch F2 replay')
    controls = {}
    if pairs:
        b = next(b for _, b in pairs if response[b])
        controls['omitted_recipient_read'] = rejected(omit=b)
        late = [b for a, b in pairs if response[b] and any(ops[i][0] == a and position[i] >= cut for i in role_ops[a])]
        if late:
            controls['read_before_donor_death'] = rejected(early=late[0])
        b = pairs[0][1]
        t = position[role_ops[b][0]]
        live = next(s for s in range(R) if s not in merge and s != pairs[0][0] and role_ops[s] and
                    position[role_ops[s][0]] < t < position[role_ops[s][-1]] and b not in
                    {c for i in role_ops[s] for c in ops[i][:2]})
        controls['alias_onto_live_register'] = rejected(alias=(b, live))
    require(all(controls.values()), 'Replay control accepted')
    return dict(lanes=LANES, seeds_restored_and_y_plus_x=True, rejected_controls=sorted(controls),
                registers=len(set(range(R)) - set(merge)))


def checked_record():
    result = physical(loaded())
    require(json.loads(OUTPUT.read_text()) == json.loads(json.dumps(result)), 'Frozen bit physical input differs')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--word', type=Path, help='physical word folder (default: the frozen input)')
    parser.add_argument('--package', type=Path, default=BIT / 'out', help='package folder with graph and profile')
    a = parser.parse_args()
    result = physical(loaded(a.word, a.package))
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if a.write:
        OUTPUT.write_text(text)
    elif a.word is None:
        require(OUTPUT.read_text() == text, 'Frozen bit physical input differs')
    print('PASS physical paired-cube bit word: %d operation frames moved, %d pairs (%d late), W %d, rank %d, '
          'deficit %d' % (result['changed_operation_frames'], result['pairs'], result['late_pairs'],
                          result['W_per_vertex'], result['rank_per_vertex'], result['deficit_per_vertex']), flush=True)


if __name__ == '__main__':
    main()
