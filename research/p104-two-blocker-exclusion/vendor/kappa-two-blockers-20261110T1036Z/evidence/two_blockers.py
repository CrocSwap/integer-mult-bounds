"""Price stationary two-blocker scalar rewrites with collateral public charts."""

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import sys

PREVIOUS = Path(__file__).resolve().parents[2] / 'kappa-chronology-pivot-20261110T1021Z' / 'evidence'
sys.path.insert(0, str(PREVIOUS))
from corrected_contacts import BRACKET, WORD_SHA, bounds, changed_blocks, chart, corrected, inventory, load
from corrected_contacts import propagate, quotient_domain, scalar_history, smooth, solve_equalities, subspace_count, volume


def factor(a, blocker, later, public):
    result = corrected(a, blocker, later, public, owned_blocker=True)
    if result is None:
        result = corrected(a, blocker, later, public, gauss=True)
    if result is None:
        return None
    coeff, correction = result
    if correction and abs(Q(correction[3])) + 1 >= 2**16:
        return None
    return coeff, correction


def reciprocal(a, blocker):
    _, d, s, x, _ = a
    if blocker[0] != 'ADD' or blocker[1:3] != [s, d]:
        return None
    y = Q(blocker[3])
    if not smooth(abs(y.numerator)):
        return None
    q, r = -1/y, -Q(x)*y*y
    if any(abs(v) + 1 >= 2**16 for v in (q, r)):
        return None
    return -q, ('RECIP', d, s, str(q), str(r))


def plans(event, blockers, seq, later, public, allow_recip):
    choices = [(Q(event[3]), [])]
    for index in blockers:
        b = seq[index]
        expanded = []
        for coefficient, corrections in choices:
            a = [*event[:3], str(coefficient), event[-1]]
            options = [factor(a, b, later, public)]
            if allow_recip:
                options.append(reciprocal(a, b))
            for option in options:
                if option is None:
                    continue
                coeff, correction = option
                packet = []
                if correction is not None:
                    cut = index + int(later or b[0] == 'COPY')
                    packet.append(dict(blocker=index, cut=cut, spelling=correction))
                expanded.append((coeff, [*corrections, *packet]))
        choices = expanded
    return [(c, corrections) for c, corrections in choices if abs(c) + 1 < 2**16]


def placements(word, raw, scalar, bridges, allow_recip=False, windows=False):
    seq = word['program']
    public = word['public']
    reads, writes = scalar_history(word)
    history = defaultdict(list)
    for i, (role, event, _) in enumerate(raw):
        history[role].append((event + 1, i))
    for entries in history.values():
        entries.sort()
    far = len(seq) + len(raw)

    def visit(role, cut):
        entries = history[role]
        return entries[bisect_right(entries, (cut, far)) - 1][1]

    for i, old in scalar.items():
        event = seq[i]
        if i not in bridges or event[0] != 'ADD' or max(event[1:3]) >= public:
            continue
        d, s = event[1:3]
        left, right = set(), set()
        for indices in (reads[d], writes[s]):
            j = bisect_left(indices, i)
            assert j == len(indices) or indices[j] != i
            left.update(indices[max(0, j - 3):j])
            right.update(indices[j:j + 3])
        for later, nearest in ((False, sorted(left, reverse=True)), (True, sorted(right))):
            if len(nearest) < 2:
                continue
            first, second = nearest[:2]
            lo, hi = ((second + 1, nearest[2] if len(nearest) > 2 else len(seq)) if later
                      else (nearest[2] + 1 if len(nearest) > 2 else 0, second))
            alternatives = plans(event, (first, second), seq, later, public, allow_recip)
            if allow_recip:
                # The added opposite-pair ADDs are already coframed at their
                # blocker, so all spellings here give the same chart problem.
                if any(not any(p['spelling'][0] == 'RECIP' for p in c) for _, c in alternatives):
                    continue
                alternatives = alternatives[:1]
            for coefficient, corrections in alternatives:
                extras = [tuple(visit(r, p['cut']) for r in p['spelling'][1:3])
                          for p in corrections if p['spelling'][0] == 'ADD']
                cuts = {lo}
                for role in (d, s):
                    h = history[role]
                    start = bisect_right(h, (lo, far))
                    stop = bisect_right(h, (hi, far))
                    cuts.update(k for k, _ in h[start:stop])
                ordered = sorted(cuts)
                for j, cut in enumerate(ordered):
                    pair = visit(d, cut), visit(s, cut)
                    if pair != old or windows:
                        row = dict(add=i, blockers=[first, second], cut=cut, coefficient=str(coefficient),
                                   corrections=corrections, visits=(pair, *extras), direction='later' if later else 'earlier')
                        if windows:
                            row['last_cut'] = ordered[j + 1] - 1 if j + 1 < len(ordered) else hi
                            row['stationary_pairs'] = [(visit(d, p), visit(s, p)) for p in ordered]
                        yield row


def slide_placements(word, raw, scalar, bridges):
    public = word['public']
    length = len(word['program'])
    reads, writes = scalar_history(word)
    history = defaultdict(list)
    for i, (r, event, _) in enumerate(raw):
        history[r].append((event + 1, i))
    for values in history.values():
        values.sort()
    far = len(raw) + length

    def at(r, cut):
        values = history[r]
        return values[bisect_right(values, (cut, far)) - 1][1]

    for use_recip in (False, True):
        for row in placements(word, raw, scalar, bridges, use_recip):
            packets = row['corrections']
            visits = row['visits']
            index = 0
            for packet in packets:
                spell = packet['spelling']
                if spell[0] != 'ADD':
                    continue
                index += 1
                d, s = spell[1:3]
                if max(d, s) >= public:
                    continue
                here = packet['cut']
                lo, hi = 0, length
                for conflicts in (reads[d], writes[s]):
                    j = bisect_left(conflicts, here)
                    if j:
                        lo = max(lo, conflicts[j - 1] + 1)
                    if j < len(conflicts):
                        hi = min(hi, conflicts[j])
                for other in packets:
                    if other is packet:
                        continue
                    cut = other['cut']
                    if cut < here:
                        lo = max(lo, cut + 1)
                    elif cut > here:
                        hi = min(hi, cut - 1)
                    elif other['blocker'] < packet['blocker']:
                        lo = max(lo, here)
                    else:
                        hi = min(hi, here)
                assert lo <= here <= hi and visits[index] == (at(d, here), at(s, here))
                cuts = {lo}
                for r in (d, s):
                    values = history[r]
                    a = bisect_right(values, (lo, far))
                    b = bisect_right(values, (hi, far))
                    cuts.update(cut for cut, _ in values[a:b])
                for cut in sorted(cuts):
                    pair = at(d, cut), at(s, cut)
                    if pair == visits[index]:
                        continue
                    yield row | dict(corrections=[p | {'cut': cut} if p is packet else p for p in packets],
                                     visits=(*visits[:index], pair, *visits[index + 1:]),
                                     slid_from=here, slid_blocker=packet['blocker'])


def slide_move_placements(word, raw, scalar, bridges, edge_only=False):
    sequence = word['program']
    public = word['public']
    history, contacts = defaultdict(list), defaultdict(list)
    for k, (r, event, _) in enumerate(raw):
        if r < public:
            history[r].append((event, k))
    for h in history.values():
        h.sort()
    for i, e in enumerate(sequence):
        if e[0] in ('ADD', 'COPY', 'SCALE'):
            for r in e[1:2] if e[0] == 'SCALE' else e[1:3]:
                contacts[r].append(i)
    index = {k: j for h in history.values() for j, (_, k) in enumerate(h)}
    for use_recip in (False, True):
        for row in placements(word, raw, scalar, bridges, use_recip, windows=True):
            i = row['add']
            old = row['visits'][0]
            seen = set(row.pop('stationary_pairs'))
            for side, k in enumerate(old):
                role = raw[k][0]
                h, j = history[role], index[k]
                for move_after in (True, False):
                    p = j - 1 if move_after else j + 1
                    if not 0 <= p < len(h):
                        continue
                    move = h[j if move_after else p][0]
                    cut = row['cut'] if move_after else row['last_cut']
                    lo, hi = (move + 1, cut) if move_after else (cut, move)
                    assert sequence[move][0] == 'MOVE' and lo <= hi
                    events = contacts[role]
                    k0 = bisect_left(events, lo)
                    if k0 < len(events) and events[k0] == i:
                        k0 += 1
                    if k0 < len(events) and events[k0] < hi:
                        continue
                    packet_cuts = {packet['cut'] for packet in row['corrections']
                                   if role in packet['spelling'][1:3]}
                    if any(lo <= k <= hi for k in packet_cuts) or (hi + 1 in packet_cuts) != edge_only:
                        continue
                    pair = (*old[:side], h[p][1], *old[side + 1:])
                    if pair in seen or pair == scalar[i]:
                        continue
                    yield row | dict(cut=cut, visits=(pair, *row['visits'][1:]),
                                     moved_paid_event=move, move_after=move_after)


def price_box(space, paid, target, state, low, high, neighbors, changed, keys, weights):
    ordered = sorted(paid, key=lambda e: (state[e[0]][1], state[e[1]][1], e))
    tightened = propagate(low, high, keys, ordered)
    if tightened is None:
        return 'incompatible span bounds', []
    lo, hi = tightened
    adjacency = [s.copy() for s in neighbors]
    touched = changed.copy()
    for a, b in keys:
        adjacency[a].add(b)
        adjacency[b].add(a)
        touched.update((a, b))
    blocks = changed_blocks(space, low, high, adjacency, target, touched)
    answers = []
    for block in blocks:
        widths = {i: len(hi[i]).bit_length() - len(lo[i]).bit_length() + 1 for i in block}
        if volume({i: range(n) for i, n in widths.items()}, adjacency, 600000) is None:
            answers.append(dict(block=block, deferred='rank volume'))
        else:
            rank = solve_equalities(block, state, lo, hi, paid, target, keys, weights, True)
            if rank.get('infeasible'):
                return 'incompatible rank equations', []
            answers.append(dict(block=block, rank=rank))
    if any('deferred' in r for r in answers):
        return 'unresolved rank volume', answers
    if sum(Q(r['rank']['upper']) for r in answers) <= 0:
        return 'nonpositive rank upper', []
    for row in answers:
        if Q(row['rank']['upper']) <= 0:
            continue
        block = row['block']
        qs = {i: len(hi[i]).bit_length() - len(lo[i]).bit_length() for i in block}
        sizes = {i: sum(subspace_count(d, r) for r in range(d + 1)) for i, d in qs.items()}
        if max(qs.values()) > 7 or volume({i: range(n) for i, n in sizes.items()}, adjacency, 900000) is None:
            row['deferred'] = 'geometry volume'
        else:
            domains = {i: quotient_domain(lo[i], hi[i]) for i in block}
            exact = solve_equalities(block, state, lo, hi, paid, target, keys, weights, False, domains)
            if exact.get('infeasible'):
                return 'incompatible exact charts', []
            row['exact'] = exact
    upper = sum(Q(r.get('exact', r['rank'])['upper']) for r in answers)
    if upper <= 0:
        return 'nonpositive mixed upper', []
    return 'positive upper requires exact lift', answers


def main(word_path, graph_path, price_path, journal_path, start, cap,
         allow_recip=False, slide=False, slide_move=False, slide_edge=False):
    raw_word = gzip.decompress(word_path.read_bytes())
    assert sha256(raw_word).hexdigest() == WORD_SHA
    word = json.loads(raw_word)
    graph = load('literal_graph', graph_path)
    engine = load('directed_price', price_path)
    raw, _, comp, raw_paid, raw_target, fixed, scalar, original, enter, end, child = inventory(word, graph)
    state0 = {i: chart(s) for i, s in enumerate(original) if s is not None}
    paid0 = Counter((comp[a], comp[b]) for _, a, b in raw_paid)
    lo0, hi0, _ = bounds(original, paid0, {comp[j] for j in fixed})
    left, right = map(Q, BRACKET)
    weights = {r: (engine.raw_margin({r: 1}, right)[0], engine.raw_margin({r: 1}, left)[1])
               for r in range(1, 10)}
    tally = Counter()
    blockers = Counter()
    hits = []
    last = None
    pending = None
    rows = (slide_placements(word, raw, scalar, child) if slide
            else placements(word, raw, scalar, child, allow_recip))
    if slide_move or slide_edge:
        rows = slide_move_placements(word, raw, scalar, child, slide_edge)
    with journal_path.open('x', buffering=1) as journal:
        for position, p in enumerate(rows):
            if position < start:
                continue
            if tally['placements'] >= cap:
                pending = position
                break
            tally['placements'] += 1
            blockers['+'.join(word['program'][j][0] for j in p['blockers'])] += 1
            i = p['add']
            if last != i:
                old, new = comp[scalar[i][0]], len(original)
                branch = child[i]
                split = {j for j, c in enumerate(comp)
                         if c == old and enter[branch] <= enter[j] < end[branch]}
                belong = lambda j: new if j in split else comp[j]
                space = [*original, original[old]]
                paid = Counter((belong(a), belong(b)) for _, a, b in raw_paid)
                target = Counter((belong(a), belong(b)) for a, b in raw_target)
                low, high, adj = bounds(space, paid, {belong(j) for j in fixed})
                changed = {old, new} | {j for j in range(len(original))
                                        if (low[j], high[j]) != (lo0[j], hi0[j])}
                state = state0 | {new: state0[old]}
                cache = {}
                last = i
                tally['ADD bridges'] += 1
            keys = tuple(sorted({tuple(sorted((belong(a), belong(b)))) for a, b in p['visits']
                                 if belong(a) != belong(b)}))
            connected = {old}
            for _ in keys:
                for a, b in keys:
                    if a in connected or b in connected:
                        connected.update((a, b))
            if new in connected:
                status = 'reinstates predecessor equality'
            elif keys in cache:
                tally['duplicate price constraints'] += 1
                status = cache[keys]
            else:
                status, answers = price_box(space, paid, target, state, low, high, adj, changed, keys, weights)
                cache[keys] = status
                if answers:
                    row = dict(position=position, status=status, proposal=p, keys=keys,
                               old_component=old, new_component=new, split_visits=[raw[j] for j in sorted(split)],
                               blocks=answers)
                    hits.append(row)
                    print(json.dumps(row, sort_keys=True), file=journal)
            tally[status] += 1
            if tally['placements'] % 250 == 0:
                print(json.dumps(dict(position=position, add=i, counts=tally), sort_keys=True), file=journal)
    result = dict(word=WORD_SHA, start=start, cap=cap, counts=tally, blockers=blockers,
                  pending=pending, unresolved=len(hits), hits=hits)
    if allow_recip:
        result['scope'] = 'only added directions with a reciprocal opposite-ADD spelling'
    if slide:
        result['scope'] = 'one public correction slides without crossing other stationary packet'
    if slide_move:
        result['scope'] = 'one public paid MOVE slides across new mobile ADD with every other contact fixed'
    if slide_edge:
        result['scope'] = 'additional paid MOVE slides with packet one cut after both MOVE positions'
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('word_path', 'graph_path', 'price_path', 'journal_path'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--cap', type=int, default=26000)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--reciprocal', action='store_true', dest='allow_recip')
    modes.add_argument('--slide-correction', action='store_true', dest='slide')
    modes.add_argument('--slide-move', action='store_true')
    modes.add_argument('--slide-move-edge', action='store_true', dest='slide_edge')
    main(**vars(parser.parse_args()))
