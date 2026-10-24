#!/usr/bin/env python3
"""Check the separated source telescope and its selected width consequence.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inputs():
    rows = json.loads((PACKAGE / 'SOURCES.json').read_text())['files']
    result = {}
    for row in rows:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(sha256(raw).hexdigest() == row['sha256'], 'source changed: ' + row['path'])
            result[row['path']] = raw
    return result


def powers(inventory, height, cap):
    result = [Counter({1: 1})]
    for _ in range(height):
        following = Counter()
        for value, count in result[-1].items():
            for rank, copies in inventory.items():
                if value * rank <= cap:
                    following[value * rank] += count * copies
        result.append(following)
    return result


def telescope(targets, paid, cap):
    low, width = min(targets), max(targets)
    need(2 <= low and max(paid) < low and cap >= 1, 'separated default-height domain')
    height, power = 0, 1
    while power * low <= cap:
        height += 1
        power *= low
    tp, pp = powers(targets, height, cap), powers(paid, height, cap)
    counts = [sum(a * b for r, a in pp[d].items() for k, b in tp[height-d].items()
                  if r * k <= cap) for d in range(height+1)]
    w, q = sum(targets.values()), sum(paid.values())
    need(counts[-1] == q**height, 'every all-paid word is eligible')
    total = w*q**height + (w-q)*sum(counts[:-1])
    deficits = [q**d*w**(height-d)-counts[d] for d in range(height)]
    need(total-w**(height+1) == (q-w)*sum(deficits), 'deficit identity')
    need(all(value >= 0 for value in deficits), 'negative eligibility deficit')
    need(all(w*counts[d] >= q*counts[d-1] for d in range(1, height+1)),
         'negative missing-parent count')
    if q > w:
        need(total >= w**(height+1), 'all-height lower bound')
        need((total == w**(height+1)) == (cap >= width**height), 'equality threshold')
    return height, total, counts


def clear(flow):
    for method in (flow.column, flow.points, flow.units, flow.demand):
        method.cache_clear()


def completed(raw):
    targets, paid = Counter(), Counter()
    for rank, count in raw['targets'].items():
        rank = int(rank)
        targets[max(21, rank)] += count
        if rank < 21:
            paid[21-rank] += count
    paid.update({int(rank): count for rank, count in raw['paid'].items()})
    split = Counter()
    for rank, count in paid.items():
        whole, remainder = divmod(rank, 20)
        split[20] += whole * count
        if remainder:
            split[remainder] += count
    return targets, +split


def verify():
    source = inputs()
    name = 'research/direct-mixed-flow/flow.py'
    namespace = {'__file__': str(ROOT/name), '__name__': 'pinned_flow'}
    exec(compile(source[name], name, 'exec'), namespace)
    flow_type = namespace['Flow']
    tiny, literal, monotone = 0, 0, 0
    for ranks in ((2, 3), (2, 4), (3, 4)):
        for weights in product((1, 2), repeat=2):
            targets = dict(zip(ranks, weights))
            for count in (1, 2, 4):
                paid = {1: count, min(ranks)-1: count}
                previous = None
                for cap in range(1, 25):
                    height, expected, _ = telescope(targets, paid, cap)
                    flow = flow_type(targets, paid, max(targets)*cap)
                    result = flow.merged()
                    need(result['height'] == height and result['source_count'] == expected,
                         'independent ordered products differ from pinned flow')
                    if cap in (1, 2, 3, 4) and weights == (1, 1) and count == 1:
                        word = [r for r, c in paid.items() for _ in range(c)]
                        exact = flow.literal(word)
                        need(exact['sources'] == result['sources'] and exact['exits'] == result['exits'],
                             'literal chronological flow differs')
                        literal += 1
                    if previous is not None and previous[0] == height:
                        sign = sum(paid.values())-sum(targets.values())
                        need(sign*(expected-previous[1]) <= 0, 'fixed-height monotonicity')
                        monotone += 1
                    previous = height, expected
                    tiny += 1
                    clear(flow)
    raw = json.loads(source['research/joint-helper-lattice/RESULT.json'])
    need(raw['productive_fields'] == 10928 and raw['paid_calls'] == 64620, 'raw field/call counts')
    need(raw['strictification']['floor'] == 21 and raw['strictification']['cutoff'] == 20
         and raw['strictification']['power'] == 1024, 'selected completion and split rule')
    targets, paid = completed(raw)
    need(sum(targets.values()) == 10928 and sum(paid.values()) == 77564, 'reduced invoice')
    selected = []
    caps = {cap for height in range(1, 5)
            for cap in (21**height-1, 21**height, 21**height+1,
                        21**(height+1)-1, 145**height) if cap < 21**5}
    for cap in sorted(caps):
        h, total, _ = telescope(targets, paid, cap)
        flow = flow_type(targets, paid, 145*cap)
        need(flow.merged()['source_count'] == total, 'selected reduced-power source count')
        selected.append({'cap': cap, 'height': h, 'sources': total})
        clear(flow)
    # Concrete false extensions and omissions must disagree with actual counts.
    _, full, f = telescope({2: 1, 4: 1}, {1: 4}, 2)
    need(full != 2*f[0], 'root-only control did not distinguish missing sources')
    need(full != 2*sum(f), 'missing subtraction control did not distinguish')
    _, below, _ = telescope({2: 1, 4: 1}, {1: 1}, 2)
    need(below == 3 and below < 2**2, 'Q<W counterexample')
    outside = flow_type({2: 1, 4: 1}, {3: 1}, 8)
    need(outside.merged()['source_count'] == 2 and 2 != 2+(2-1)*1,
         'unseparated counterexample')
    clear(outside)
    raised = flow_type({2: 1, 3: 1}, {1: 3}, 3, extra_height=1)
    need(raised.merged()['source_count'] != telescope({2: 1, 3: 1}, {1: 3}, 1)[1],
         'changed-height counterexample')
    clear(raised)
    h = raw['compiler']['H']
    w, low, ambient = 10928**1024, 21**1024, 145**1024
    hlo = (h-ambient.bit_length())//low.bit_length()
    xlo = hlo*(w.bit_length()-1)
    need(1000*(low-1)*xlo > 3054*low*h, 'strict selected 3.054 lower coefficient')
    need(1000*(low-1)*xlo < 3055*low*h, 'rounded 3.055 claim must fail')
    need(10000*30694 < 10051*30540, 'combined bracket ratio below 1.0051')
    need(inputs() == source, 'source changed during verification')
    return {'schema_version': 1, 'tiny_flows': tiny, 'literal_flows': literal,
            'fixed_height_comparisons': monotone, 'selected_reduced_flows': selected,
            'negative_controls': 6, 'H': h, 'hlo': hlo, 'Xlo': xlo,
            'W_bit_length': w.bit_length(), 'L_bit_length': low.bit_length(),
            'M_bit_length': ambient.bit_length(), 'strict_lower_K_over_N': '3054/1000',
            'inherited_upper_K_over_N': '30694/10000', 'selected_kappa': raw['kappa']}


if __name__ == '__main__':
    result = verify()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(not sys.argv[1:], 'use no arguments or --emit')
        need(result == json.loads((PACKAGE/'RESULT.json').read_text()), 'result receipt changed')
        print('PASS_SEPARATED_SOURCE_TELESCOPE K/N>3.054 no_new_kappa')
