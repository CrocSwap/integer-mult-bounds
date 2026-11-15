#!/usr/bin/env python3
"""Independent contact DAG, reverse endpoint-conditioned DP and rational prices.

Uses a separately retained positive-Taylor interval implementation. It does not
import frames.py, run a native application, or claim a kappa improvement.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
from fractions import Fraction as F
from itertools import product
import argparse
import gzip
import hashlib
import json
import runpy

HERE = Path(__file__).resolve().parent
CANONICAL = 'df1fc415915abd8d0f1bbfe8ad530c02f9cd82692f548ed2817ba6bd948fc55c'
TARGETS = ('.0046502223357', '.0046530568657')
GRID = 10**40
AMBIENT = (1 << 512) - 1


def need(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def hull(rows):
    values = [0]
    for row in rows:
        if row not in values:
            values.extend([v ^ row for v in values])
    return sum(1 << value for value in values)


@lru_cache(None)
def basis(mask):
    rows, generated = [], 1
    while mask & ~generated:
        missing = mask & ~generated
        rows.append((missing & -missing).bit_length() - 1)
        generated = hull(tuple(rows))
    need(generated == mask, 'valid binary subspace')
    return tuple(rows)


@lru_cache(None)
def join(a, b):
    return hull(basis(a) + basis(b))


def dimension(mask):
    size = mask.bit_count()
    need(size > 0 and size & (size - 1) == 0, 'power-of-two subspace size')
    return size.bit_length() - 1


def corridors(word, free):
    """Graph constraints, with no dependency on proposer corridor arrays."""
    count = word['public']
    frames = [hull(tuple(row)) for row in word['frames']]
    need(all(dimension(a) == len(b) for a, b in zip(frames, word['frames'])),
         'all source frame bases independent')
    mains = set(word['live']) | {r + 112 for r in word['live']}
    mains |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    helpers = set(range(count)) - mains
    need(len(mains) == 400 and len(helpers) == 1101, 'source owner partition')
    predecessors, successors, anchors, events = [], [], [], []

    def vertex(parents, anchor, event):
        k = len(predecessors)
        parents = list(dict.fromkeys(parents))
        predecessors.append(parents)
        successors.append([])
        anchors.append(anchor)
        events.append(event)
        for p in parents:
            need(p < k, 'acyclic chronological contact graph')
            successors[p].append(k)
        return k

    paths, last = [], []
    for r, frame in enumerate(word['initial']):
        k = vertex([], None if free and r in helpers else frames[frame], ('SOURCE', r))
        paths.append([k])
        last.append(k)
    charts = word['initial'] + [None] * word['owned_fields']
    public_paid, owned_paid, contacts = Counter(), Counter(), []
    for i, event in enumerate(word['program']):
        op, dst = event[:2]
        if op == 'MOVE':
            before, after, owned = event[2:]
            need(charts[dst] == before and owned == (dst >= count), 'source MOVE owner/entrance')
            rank = dimension(frames[after]) - dimension(frames[before])
            if dst < count:
                need(frames[before] & frames[after] == frames[before] and rank > 0,
                     'source public monotone MOVE')
                public_paid[rank] += 1
            else:
                owned_paid[abs(rank)] += 1
            charts[dst] = after
        elif op == 'INIT':
            need(dst >= count and charts[dst] is None, 'owned activation')
            charts[dst] = event[2]
        elif op == 'CLEAR':
            need(dst >= count and charts[dst] == event[2], 'owned retirement')
            charts[dst] = None
        elif op in ('ADD', 'COPY', 'SCALE'):
            roles = event[1:3] if op in ('ADD', 'COPY') else event[1:2]
            if op in ('ADD', 'COPY'):
                need(charts[roles[0]] == charts[roles[1]] == event[4], 'source contact chart')
            public = [r for r in roles if r < count]
            owned = [r for r in roles if r >= count]
            anchor = frames[charts[owned[0]]] if owned else None
            k = vertex([last[r] for r in public], anchor, (i, op))
            contacts.append(k)
            for r in public:
                paths[r].append(k)
                last[r] = k
        else:
            raise ValueError('unexpected opcode ' + op)
    need(charts == word['final'] + [None] * word['owned_fields'], 'source endpoints')
    for r, frame in enumerate(word['final']):
        paths[r].append(vertex([last[r]], None if free and r in helpers else frames[frame], ('TARGET', r)))
    lower = []
    for k, parents in enumerate(predecessors):
        current = 1
        for p in parents:
            current = join(current, lower[p])
        if anchors[k] is not None:
            need(current & anchors[k] == current, 'anchor contains predecessor floor')
            current = anchors[k]
        lower.append(current)
    upper = [None] * len(predecessors)
    for k in reversed(range(len(predecessors))):
        current = AMBIENT
        for child in successors[k]:
            current &= upper[child]
        if anchors[k] is not None:
            need(current & anchors[k] == anchors[k], 'anchor contained in successor ceiling')
            current = anchors[k]
        upper[k] = current
        need(lower[k] & current == lower[k], 'nonempty subspace corridor')
    intervals = [[(dimension(lower[k]), dimension(upper[k])) for k in path] for path in paths]
    zero_contacts = [k for k in paths[770] if events[k][0] in (34010, 34011)]
    need(len(zero_contacts) == 2 and all(lower[k] == upper[k] == frames[115] for k in zero_contacts),
         'known-zero public gap forced to identical frame115')
    return dict(paths=intervals, public_paid=public_paid, owned_paid=owned_paid,
                helpers=helpers, frames=frames, vertices=len(predecessors),
                contact_vertices=len(contacts),
                widths=Counter(dimension(upper[k]) - dimension(lower[k]) for k in contacts))


def reverse_dp(intervals, powers, helper):
    """State (final,current) preserves endpoint pair until credit is charged."""
    low, high = intervals[-1]
    tail = {(end, end): (0, 0) for end in range(low, high + 1)}
    transitions = 0
    for low, high in reversed(intervals[:-1]):
        result = {}
        for (end, nxt), (a, b) in tail.items():
            for current in range(low, min(high, nxt) + 1):
                increment = powers[nxt - current]
                value = a + increment[0], b + increment[1]
                key = end, current
                transitions += 1
                if key not in result:
                    result[key] = value
                else:
                    result[key] = min(result[key][0], value[0]), min(result[key][1], value[1])
        if not result:
            return None, transitions
        tail = result
    values = [(a - powers[end - start][1], b - powers[end - start][0]) if helper else (a, b)
              for (end, start), (a, b) in tail.items()]
    return (min(a for a, b in values), min(b for a, b in values)), transitions


def fixtures():
    # Integer prices avoid interval ambiguity and distinguish total endpoint
    # credit from incorrectly independent/multiple credited subsegments.
    powers = {k: (k * 10 - k * k, k * 10 - k * k) for k in range(5)}
    cases = [[(0, 0), (0, 2), (1, 3), (3, 3)],
             [(0, 2), (2, 2), (2, 4)],
             [(0, 0), (2, 2), (1, 1)]]
    checked = 0
    for path in cases:
        for helper in (False, True):
            candidates = []
            for seq in product(*(range(a, b + 1) for a, b in path)):
                if all(a <= b for a, b in zip(seq, seq[1:])):
                    value = sum(powers[b - a][0] for a, b in zip(seq, seq[1:]))
                    if helper:
                        value -= powers[seq[-1] - seq[0]][0]
                    candidates.append(value)
            actual, _ = reverse_dp(path, powers, helper)
            expected = (min(candidates),) * 2 if candidates else None
            need(actual == expected, 'reverse endpoint DP agrees with exhaustive fixture')
            checked += 1
    a, b = hull((1,)), hull((2,))
    need(a & b != a and a & b != b, 'conflicting lower/upper anchor control')
    return dict(exhaustive_reverse_dp_cases=checked, infeasible_descent_rejected=True,
                conflicting_anchors_rejected=True, endpoint_credit_coupled=True)


def zero_guard(word):
    # A nonzero modular evaluation is an exact rational nonzero-row witness,
    # not a probabilistic inference. All denominators are checked invertible.
    prime = 1000003
    count = word['public']
    values = [[int.from_bytes(hashlib.sha256(f'{r}/{j}'.encode()).digest()[:8], 'big') % prime
               for j in range(3)] for r in range(count)] + [[0] * 3 for _ in range(word['owned_fields'])]
    need(all(any(row) for row in values[:count]), 'initial nonzero witnesses')

    @lru_cache(None)
    def coefficient(s):
        q = F(s)
        need(q.denominator % prime, 'denominator invertible modulo probe prime')
        return q.numerator * pow(q.denominator, -1, prime) % prime

    zero, witnessed = [], 0
    for i, event in enumerate(word['program']):
        op, dst = event[:2]
        if op in ('INIT', 'CLEAR'):
            values[dst] = [0] * 3
        elif op in ('ADD', 'COPY'):
            if op == 'COPY':
                need(not any(values[dst]), 'COPY destination zero in probes')
            values[dst] = [(a + coefficient(event[3]) * b) % prime
                           for a, b in zip(values[dst], values[event[2]])]
        elif op == 'SCALE':
            values[dst] = [a * coefficient(event[2]) % prime for a in values[dst]]
        elif op != 'MOVE':
            raise ValueError(op)
        if dst < count:
            if any(values[dst]):
                witnessed += 1
            else:
                zero.append([i, dst])
    need(zero == [[34010, 770]], 'sole public zero state')
    need(word['program'][34009:34012] == [['COPY', 1525, 770, '1', 115],
         ['ADD', 770, 1525, '-1', 115], ['ADD', 770, 607, '1', 115]], 'exact zero interval identity')
    return dict(modulus=prime, deterministic_probes=3, nonzero_public_states=witnessed,
                zero_public_states=zero, free_zero_relabeling_gap_rank=0)


def main(write=False):
    blob = (HERE / 'retained/7613/word.json.gz').read_bytes()
    word = json.loads(gzip.decompress(blob))
    canonical = hashlib.sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    need(canonical == CANONICAL, 'exact latest7613 source canonical hash')
    invoice_blob = (HERE / 'retained/7613/invoice-new.json').read_bytes()
    invoice = json.loads(invoice_blob)
    targets = {int(r): n for r, n in invoice['targets'].items()}
    paid = {int(r): n for r, n in invoice['paid'].items()}
    engine = runpy.run_path(str(HERE / 'retained/independent_interval.py'))
    author = json.loads((HERE / 'frames.json').read_text())
    need(author['source_canonical_sha256'] == canonical, 'primary receipt source identity')
    reference = {(row['mode'], row['target']): row for row in author['cases']}
    prices = {}
    for target in TARGETS:
        powers = {0: (0, 0)}
        for rank in sorted(set(range(1, 10)) | set(targets) | set(paid)):
            low, high = engine['power'](rank, 1 - F(target))
            powers[rank] = (low * GRID).__floor__(), (high * GRID).__ceil__()
        prices[target] = powers
    cases = []
    for free in (False, True):
        model = corridors(word, free)
        fixed_paid = {r: paid.get(r, 0) - 17 * model['public_paid'][r]
                      for r in set(paid) | set(model['public_paid'])}
        need(all(n >= 0 for n in fixed_paid.values()), 'fixed debit residual nonnegative')
        caller_paid = {r: fixed_paid.get(r, 0) - 17 * model['owned_paid'][r]
                       for r in set(fixed_paid) | set(model['owned_paid'])}
        need(all(n >= 0 for n in caller_paid.values()), 'fixed caller debit nonnegative')
        helpers = Counter(dimension(model['frames'][word['final'][r]]) -
                          dimension(model['frames'][word['initial'][r]]) for r in model['helpers'])
        need(all(r > 0 for r in helpers), 'source productive helper ranks positive')
        fixed_targets = {r: targets.get(r, 0) - 17 * helpers[r] for r in set(targets) | set(helpers)}
        need({r: n for r, n in fixed_targets.items() if n} ==
             {9:416, 17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 137:208},
             'fresh helper target credit separated from complete fixed caller')
        for target in TARGETS:
            powers = prices[target]
            lo = hi = transitions = 0
            for r, path in enumerate(model['paths']):
                value, count = reverse_dp(path, powers, free and r in model['helpers'])
                need(value is not None, 'nonempty field dimension path')
                lo += value[0]
                hi += value[1]
                transitions += count
            def moment(hist):
                return tuple(sum(n * powers[r][j] for r, n in hist.items()) for j in (0, 1))
            t, f = moment(fixed_targets if free else targets), moment(fixed_paid)
            margin = t[0] - f[1] - 17 * hi, t[1] - f[0] - 17 * lo
            need(margin[1] < 0, 'negative optimistic full signed moment')
            mode = 'free_helper_endpoints' if free else 'fixed_endpoints'
            prior = reference[mode, target]
            need(model['widths'] == Counter({int(k): v for k, v in prior['contact_dimension_width_counts'].items()}),
                 'independent contact corridor census agrees')
            for key, interval in [('native_net_cost_interval', (lo, hi)),
                                  ('full_target_minus_paid_interval', margin)]:
                a, b = map(F, prior[key])
                need(max(a, F(interval[0], GRID)) <= min(b, F(interval[1], GRID)),
                     'independent rational interval overlap: ' + key)
            cases.append(dict(mode=mode, target=target, public_fields=word['public'],
                              main_fields=400, helper_fields=1101, graph_vertices=model['vertices'],
                              contact_vertices=model['contact_vertices'],
                              contact_dimension_width_counts=dict(model['widths']),
                              reverse_dp_transitions=transitions,
                              native_net_cost_interval=[str(F(x, GRID)) for x in (lo, hi)],
                              full_target_minus_paid_interval=[str(F(x, GRID)) for x in margin],
                              full_target_minus_paid_float=[float(F(x, GRID)) for x in margin],
                              primary_intervals_overlap=True))
    result = dict(status='PASS_INDEPENDENT_FRAME_CORRIDOR_BOUNDS', source_canonical_sha256=canonical,
                  source_gzip_sha256=hashlib.sha256(blob).hexdigest(),
                  invoice_sha256=hashlib.sha256(invoice_blob).hexdigest(),
                  cases=cases, controls=fixtures(), known_zero_public_gap_audit=zero_guard(word),
                  scope='Necessary signed-moment bounds for exact7613 fixed scalar word, main endpoints, '
                  'owned chronology and caller, with monotone public F2^9 frame paths. Free-helper mode '
                  'also permits arbitrary independent helper endpoints with coupled new rank credit. '
                  'Shared contact agreement, exact subspace inclusion and extra basis charges are relaxed. '
                  'No kappa improvement, source admission or general algorithmic impossibility is claimed.')
    receipt = HERE / 'independent-frames.json'
    if write:
        receipt.write_text(json.dumps(result, indent=2) + '\n')
    else:
        frozen = json.loads(receipt.read_text())
        normalized = json.loads(json.dumps(result, sort_keys=True))
        need(normalized == frozen, 'complete independent receipt unchanged')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    main(parser.parse_args().write)
