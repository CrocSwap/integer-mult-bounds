"""Price corrected one-blocker ADD retimings with collateral public rechart."""

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

PREVIOUS = Path(__file__).resolve().parents[2] / 'kappa-nonbridge-pairs-20261110T0937Z' / 'evidence'
sys.path.insert(0, str(PREVIOUS))
from nonbridge_screen import BRACKET, WORD_SHA, bounds, changed_blocks, chart, load, propagate, quotient_domain, subspace_count, volume
from release import inventory
from constrained import solve_equalities


def scalar_history(word):
    reads, writes = defaultdict(list), defaultdict(list)
    for i, e in enumerate(word['program']):
        if e[0] in ('ADD', 'COPY', 'SCALE'):
            writes[e[1]].append(i)
            reads[e[1] if e[0] == 'SCALE' else e[2]].append(i)
    return reads, writes


def window(indices, position, skip=None):
    j = bisect_left(indices, position)
    left = j - 1
    right = j
    while left >= 0 and indices[left] in (position, skip):
        left -= 1
    while right < len(indices) and indices[right] in (position, skip):
        right += 1
    return indices[left] if left >= 0 else -1, indices[right] if right < len(indices) else None


def smooth(n):
    assert n > 0
    for prime in (2, 3, 5):
        while n % prime == 0:
            n //= prime
    return n == 1


def corrected(a, b, later, public, owned_blocker=False, gauss=False):
    _, d, s, x, _ = a
    x = Q(x)
    op, e = b[:2]
    if gauss:
        if op != 'ADD' or e != s or b[2] != d:
            return None
        y = Q(b[3])
        z = 1 + x*y
        if not z or not (smooth(abs(z.numerator)) and smooth(z.denominator)):
            return None
        first, second = (1/z, z) if later else (z, 1/z)
        if any(abs(q) + 1 >= 2**16 for q in (x/z, y/z, first, second)):
            return None
        return x/z, ('GAUSS', d, s, str(z), str(y/z), str(first), str(second))
    if op == 'SCALE':
        assert e in (d, s)
        y = Q(b[-2])
        coeff = x * y if (e == d) == later else x / y
        return coeff, None
    if op == 'COPY' and owned_blocker and e >= public and b[2] == d:
        y = Q(b[-2])
        return x, ('ADD', e, s, str(x*y if later else -x*y))
    if op != 'ADD' or (not owned_blocker and max(e, b[2]) >= public):
        return None
    t = b[2]
    assert s == e or d == t
    if s == e and d == t:
        return None
    y = Q(b[-2])
    if s == e:
        correction = ('ADD', d, t, str(-x*y if later else x*y))
    else:
        correction = ('ADD', e, s, str(x*y if later else -x*y))
    return x, correction


def choices(word, raw, raw_id, scalar, child, free_correction=False, owned_blocker=False, gauss=False):
    program = word['program']
    public = word['public']
    reads, writes = scalar_history(word)
    histories = defaultdict(list)
    for i, (role, event, _) in enumerate(raw):
        histories[role].append((event + 1, i))
    for items in histories.values():
        items.sort()
    infinity = len(program) + len(raw)

    def at(r, cut):
        items = histories[r]
        return items[bisect_right(items, (cut, infinity)) - 1][1]

    def joint_cuts(roles, lo, hi):
        cuts = {lo}
        for r in roles:
            h = histories[r]
            first = bisect_right(h, (lo, infinity))
            last = bisect_right(h, (hi, infinity))
            cuts.update(k for k, _ in h[first:last])
        return sorted(cuts)

    for i, (u, v) in scalar.items():
        event = program[i]
        if i not in child or event[0] != 'ADD' or max(event[1:3]) >= public:
            continue
        d, s = event[1:3]
        barriers = reads[d], writes[s]
        nearby = [window(ls, i) for ls in barriers]
        left = max(row[0] for row in nearby)
        right = min((row[1] for row in nearby if row[1] is not None), default=len(program))
        for blocker, later in ((left, False), (right, True)):
            if blocker < 0 or blocker == len(program):
                continue
            b = program[blocker]
            if owned_blocker and (b[0] not in ('ADD', 'COPY') or max(b[1:3]) < public):
                continue
            plan = corrected(event, b, later, public, owned_blocker, gauss)
            if plan is None:
                continue
            coefficient, correction = plan
            if abs(coefficient) + 1 >= 2**16 or (correction and abs(Q(correction[3])) + 1 >= 2**16):
                continue
            next_bounds = [window(ls, i, blocker) for ls in barriers]
            lo = max(row[0] for row in next_bounds) + 1
            hi = min((row[1] for row in next_bounds if row[1] is not None), default=len(program))
            if later:
                lo = max(lo, blocker + 1)
            else:
                hi = min(hi, blocker)
            if lo > hi:
                continue
            # A COPY must see its still-zero destination before any correction.
            added_cut = blocker + int(later or b[0] == 'COPY')
            added = tuple(at(r, added_cut) for r in correction[1:3]) if correction else None
            additions = [(added_cut, added)]
            if free_correction:
                if correction is None:
                    continue
                p, q = correction[1:3]
                prior, after = [], []
                for conflicts in (reads[p], writes[q]):
                    j = bisect_left(conflicts, added_cut)
                    prior.append(conflicts[j - 1] + 1 if j else 0)
                    after.append(conflicts[j] if j < len(conflicts) else len(program))
                assert max(prior) <= added_cut <= min(after)
                additions = []
                for k in joint_cuts((p, q), max(prior), min(after)):
                    pair = at(p, k), at(q, k)
                    if pair != added:
                        additions.append((k, pair))
            for cut in joint_cuts((d, s), lo, hi):
                a, b = at(d, cut), at(s, cut)
                if (a, b) == (u, v):
                    continue
                for k, pair in additions:
                    yield i, blocker, cut, str(coefficient), k, correction, (a, b), pair


def screen(word, graph, price, journal, free_correction=False, cap=None, owned_blocker=False, gauss=False):
    raw, raw_id, comp, raw_paid, raw_target, fixed, scalar, original, enter, end, child = inventory(word, graph)
    base = {i: chart(s) for i, s in enumerate(original) if s is not None}
    paid0 = Counter((comp[a], comp[b]) for _, a, b in raw_paid)
    old_lo, old_hi, _ = bounds(original, paid0, {comp[i] for i in fixed})
    left, right = map(Q, BRACKET)
    weights = {r: (price.raw_margin({r: 1}, right)[0], price.raw_margin({r: 1}, left)[1])
               for r in range(1, 10)}
    counts = Counter()
    hits = []
    last = None
    cache = {}
    pending = None
    for i, blocker, cut, coefficient, correction_cut, correction, moved, added in choices(
            word, raw, raw_id, scalar, child, free_correction, owned_blocker, gauss):
        if cap is not None and counts['candidate placements'] >= cap:
            pending = dict(add=i, blocker=blocker, cut=cut, correction_cut=correction_cut)
            break
        counts['candidate placements'] += 1
        counts['corrected ' + word['program'][blocker][0]] += 1
        if last != i:
            old, new = comp[scalar[i][0]], len(original)
            branch = child[i]
            split = {j for j, c in enumerate(comp) if c == old and enter[branch] <= enter[j] < end[branch]}
            belong = lambda j: new if j in split else comp[j]
            space = [*original, original[old]]
            paid = Counter((belong(a), belong(b)) for _, a, b in raw_paid)
            target = Counter((belong(a), belong(b)) for a, b in raw_target)
            low, high, adj = bounds(space, paid, {belong(j) for j in fixed})
            changed = {old, new} | {j for j in range(len(original))
                                    if (low[j], high[j]) != (old_lo[j], old_hi[j])}
            old_state = base | {new: base[old]}
            paid_order = sorted(paid, key=lambda e: (old_state[e[0]][1], old_state[e[1]][1], e))
            cache = {}
            last = i
            counts['ADD bridges with placements'] += 1
        pairs = [tuple(sorted(map(belong, moved)))]
        if added is not None:
            pairs.append(tuple(sorted(map(belong, added))))
        key = tuple(sorted({(a, b) for a, b in pairs if a != b}))
        connected = {old}
        for _ in key:
            for a, b in key:
                if a in connected or b in connected:
                    connected.update((a, b))
        if new in connected:
            counts['reinstates predecessor equality'] += 1
            continue
        if key in cache:
            counts['duplicate priced equality'] += 1
            counts[cache[key]] += 1
            continue
        narrowed = propagate(low, high, key, paid_order)
        if narrowed is None:
            status = 'incompatible span bounds'
        else:
            lo, hi = narrowed
            neighbors = [s.copy() for s in adj]
            touched = changed.copy()
            for a, b in key:
                touched.update((a, b))
                neighbors[a].add(b)
                neighbors[b].add(a)
            blocks = changed_blocks(space, low, high, neighbors, target, touched)
            rank = []
            exact = []
            for block in blocks:
                widths = {j: len(hi[j]).bit_length() - len(lo[j]).bit_length() + 1 for j in block}
                if volume({j: range(n) for j, n in widths.items()}, neighbors, 600000) is None:
                    rank.append(dict(deferred=True, vertices=block))
                else:
                    rank.append(solve_equalities(block, old_state, lo, hi, paid, target, key, weights, True))
            if any(row.get('infeasible') for row in rank):
                status = 'incompatible ranks'
            elif any(row.get('deferred') for row in rank):
                status = 'rank table deferred'
            elif sum(Q(row['upper']) for row in rank) <= 0:
                status = 'nonpositive rank upper'
            else:
                for block in blocks:
                    qs = {j: len(hi[j]).bit_length() - len(lo[j]).bit_length() for j in block}
                    sizes = {j: sum(subspace_count(d, r) for r in range(d + 1)) for j, d in qs.items()}
                    if max(qs.values()) > 7 or volume({j: range(n) for j, n in sizes.items()},
                                                       neighbors, 800000) is None:
                        exact.append(dict(deferred=True, vertices=block))
                    else:
                        domains = {j: quotient_domain(lo[j], hi[j]) for j in block}
                        exact.append(solve_equalities(block, old_state, lo, hi, paid, target, key,
                                                      weights, False, domains))
                if any(row.get('infeasible') for row in exact):
                    status = 'incompatible exact charts'
                elif any(row.get('deferred') for row in exact):
                    mixed = sum(Q(p['upper'] if e.get('deferred') else e['upper']) for p, e in zip(rank, exact))
                    status = ('nonpositive mixed upper' if (free_correction or owned_blocker or gauss) and mixed <= 0
                              else 'exact table deferred')
                elif sum(Q(row['upper']) for row in exact) <= 0:
                    status = 'nonpositive exact upper'
                elif sum(Q(row['lower']) for row in exact) > 0:
                    status = 'positive chart assignment'
                else:
                    status = 'interval unresolved'
            if status in ('positive chart assignment', 'rank table deferred', 'exact table deferred', 'interval unresolved'):
                row = dict(status=status, add=i, blocker=blocker, cut=cut, coefficient=coefficient,
                           correction_cut=correction_cut, correction=correction, key=key,
                           old_component=old, new_component=new, split_visits=[raw[j] for j in sorted(split)],
                           moved_visits=[raw[j] for j in moved], added_visits=[raw[j] for j in added] if added else None,
                           rank=rank, exact=exact)
                hits.append(row)
                print(json.dumps(row, sort_keys=True), file=journal, flush=True)
        cache[key] = status
        counts[status] += 1
        if counts['candidate placements'] % 200 == 0:
            print(json.dumps(dict(progress=dict(counts), add=i)), file=journal, flush=True)
    result = dict(word=WORD_SHA, counts=counts, unresolved=len(hits), hits=hits)
    if free_correction:
        result.update(scope='additional commuting correction visit pairs', pending=pending)
    if owned_blocker:
        result['scope'] = 'only ADD or COPY blockers touching owned roles, adjacent corrections'
    if gauss:
        result['scope'] = 'opposite public ADD blocker with retuned coefficient and adjacent diagonal correction'
    return result


def main(word, graph, price, journal, cap=None, owned_blocker=False, gauss=False):
    raw = gzip.decompress(word.read_bytes())
    assert sha256(raw).hexdigest() == WORD_SHA
    with journal.open('x') as out:
        result = screen(json.loads(raw), load('chronology_graph', graph), load('directed_price', price), out,
                        cap is not None, cap, owned_blocker, gauss)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    assert __debug__
    assert len(sys.argv) in (5, 6)
    mode = sys.argv[5] if len(sys.argv) == 6 else None
    main(*(Path(p) for p in sys.argv[1:5]), int(mode) if mode not in (None, '--owned', '--gauss') else None,
         mode == '--owned', mode == '--gauss')
