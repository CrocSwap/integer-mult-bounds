"""Exact CK helper-column search and emitted compensation; Apache-2.0.
Prepared with substantial OpenAI Codex assistance; contributed by David Awad.
The retained binary-Horner price is credited to icekylinx and supplier lineage.
"""
from fractions import Fraction as Q
import hashlib
import json

SEED = 24


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def price(q):
    """Real-component cost, including coefficient work clear on both ends."""
    q = Q(q)
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, 'non-dyadic coefficient')
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def columns(word):
    require((word['v'], word['R'], word['h']) == (112, 492, 9), 'geometry')
    out = [[0] * 112 for _ in range(492)]
    seen = set()
    for op, t, s, n, d, f in word['compensation']:
        require(op == 'add' and 112 <= t < 224 and 224 <= s < 716
                and f == 0 and d in (1, 2, 4) and n != 0, 'compensation shape')
        require((t, s) not in seen, 'duplicate compensation entry')
        seen.add((t, s))
        out[s - 224][t - 112] = n * (4 // d)
    return out


def search(word):
    cols = columns(word)
    eligible = [r for r in range(492)
                if word['start'][r + 224] == 0 and word['final'][r + 224] == 1]
    require(all(not any(c) or r in eligible for r, c in enumerate(cols)),
            'compensation reads wrapped helper')
    bound = 2 * max(abs(x) for c in cols for x in c)
    costs = {n: price(Q(n, 4)) for n in range(-bound, bound + 1)}
    totals = [sum(costs[x] for x in c) for c in cols]
    profitable = []
    for a in eligible:
        for b in eligible:
            if a == b:
                continue
            for sign in (-1, 1):
                changed = sum(costs[y - sign * x] for x, y in zip(cols[a], cols[b]))
                saving = totals[b] - changed - 2 * price(sign)
                if saving > 0:
                    profitable.append([saving, a, b, sign])
    profitable.sort(key=lambda x: (-x[0], (x[1] - SEED) % 492,
                                   (x[2] - SEED) % 492, x[3]))
    used, chosen = set(), []
    for record in profitable:
        _, a, b, _ = record
        if a not in used and b not in used:
            chosen.append(record)
            used.update((a, b))
    return dict(seed=SEED, eligible_helpers=len(eligible),
                candidates=2 * len(eligible) * (len(eligible) - 1),
                profitable=len(profitable), profitable_sha256=digest(profitable),
                pairs=chosen, before=sum(totals),
                saving=sum(p[0] for p in chosen),
                stopping_rule='Exhaust all legal ordered pairs and both signs; one greedy disjoint pass.')


def gate(t, s, q):
    q = Q(q)
    return ['add', t, s, q.numerator, q.denominator, 0]


def construct(word, recipe):
    cols = columns(word)
    changed = [c[:] for c in cols]
    prep, restore, used = [], [], set()
    for saving, a, b, sign in recipe['pairs']:
        require(type(a) is int and type(b) is int and 0 <= a < 492 and 0 <= b < 492,
                'helper range')
        require(a != b and a not in used and b not in used, 'non-disjoint pairs')
        require(sign in (-1, 1), 'pair sign')
        require(all(word['start'][r + 224] == 0 and word['final'][r + 224] == 1
                    for r in (a, b)), 'wrapped or nonzero-frame helper')
        used.update((a, b))
        changed[b] = [y - sign * x for x, y in zip(cols[a], cols[b])]
        actual = sum(price(Q(y, 4)) - price(Q(z, 4))
                     for y, z in zip(cols[b], changed[b])) - 2 * price(sign)
        require(actual == saving and saving > 0, 'pair price')
        prep.append(gate(a + 224, b + 224, sign))
        restore.append(gate(a + 224, b + 224, -sign))
    middle = [gate(t + 112, s + 224, Q(changed[s][t], 4))
              for t in range(112) for s in range(492) if changed[s][t]]
    return prep + middle + restore


def dual(gates):
    # The native backward stream applies inverse transpose to EACH gate,
    # retaining chronological order. Inverse transpose is a homomorphism.
    return [gate(s, t, -Q(n, d)) for op, t, s, n, d, f in gates]


def block_replay(gates, primitives=False):
    """Separate sparse arbitrary-input replay, optionally executing Horner work."""
    state = [{r: Q(1)} for r in range(717)]  # 716 live + arbitrary private work
    cost = 0
    def add(t, s, q):
        require(t != s, 'aliased add')
        row = state[t]
        for k, value in state[s].items():
            value = row.get(k, Q(0)) + q * value
            if value:
                row[k] = value
            else:
                row.pop(k, None)
    for op, t, s, n, d, f in gates:
        require(op == 'add' and f == 0 and 0 <= t < 716 and 0 <= s < 716,
                'invalid block gate')
        q = Q(n, d)
        require(q != 0 and t != s, 'zero or aliased add')
        if not primitives:
            add(t, s, q)
            continue
        require(q.denominator & (q.denominator - 1) == 0, 'non-dyadic')
        state[716] = {}
        cost += 2
        for i, bit in enumerate(bin(abs(q.numerator))[2:]):
            if i:
                state[716] = {k: 2 * v for k, v in state[716].items()}
                cost += 2
            if bit == '1':
                add(716, s, Q(1))
                cost += 2
        for _ in range(q.denominator.bit_length() - 1):
            state[716] = {k: v / 2 for k, v in state[716].items()}
            cost += 2
        add(t, 716, Q(1 if q > 0 else -1))
        state[716] = {}
        cost += 4
    return state, cost
