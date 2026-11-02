"""Identify the exact raw funding limit of the classified mixed root.

All prices use rational intervals. The selected binary tree histograms
are checked against every alternative at their sizes. Larger child sizes
use the separate all-size ceiling proof.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def tree_histogram(tree):
    if tree == 1:
        return 1, Counter()
    need(isinstance(tree, list) and len(tree) == 2, 'A literal binary child')
    a, left = tree_histogram(tree[0])
    b, right = tree_histogram(tree[1])
    return a+b, left+right+Counter({a+b: 1})


def run(local, E, root, price, ceiling):
    lower, upper = map(Q, price['raw_root_interval'])
    need(Q(ceiling['ceiling']) == upper and Q(ceiling['finite_margin_upper']) < 0
         and Q(ceiling['tail_margin_upper']) < 0 and Q(ceiling['tail_derivative_upper']) < 0,
         'The all-size exclusion is at the refined crossing upper endpoint')
    need(upper-lower == Q(1, 10**26), 'The exact raw bracket has width 10^-26')
    need(lower-Q(price['kappa']) == Q(1, 10**26), 'The certified claim is one grid step below the bracket')
    paid = {int(r): c for r, c in local['paid'].items()}
    helpers = {int(r): c for r, c in local['helpers'].items()}
    targets = {int(r): c for r, c in price['targets'].items()}
    calls = {int(r): c for r, c in price['paid'].items()}
    raw = Counter(targets)
    raw.subtract(calls)
    raw = {r: c for r, c in raw.items() if c}
    tree_data = [tree_histogram(tree) for tree in root['children']]
    sizes = [n for n, _ in tree_data]
    need(sizes == [7, 2, 2, 7], 'The candidate uses the actual optimized children')
    invoice = Counter({r: 18*c for r, c in helpers.items()})
    invoice.subtract({r: 18*c for r, c in paid.items()})
    for mask in root['masks']:
        invoice[8*sum(n*b for n, b in zip(sizes, mask))+1] += 104
    invoice[1] -= 3*104
    invoice[16] -= 2*104
    for _, histogram in tree_data:
        for n, count in histogram.items():
            invoice[8*n+1] += 2*104*count
            invoice[8*n] -= 2*104*count
            invoice[1] -= 104*count
    need({r: c for r, c in invoice.items() if c} == raw,
         'The root and literal child histograms give the complete signed invoice')
    def margin(k):
        a, b = E.moment(targets, 1-k), E.moment(calls, 1-k)
        return a[0]-b[1], a[1]-b[0]
    need(margin(lower)[0] > 0 and margin(upper)[1] < 0 and Q(price['derivative_upper']) < 0,
         'The literal invoice has exactly one crossing in the refined interval')

    h = {r: E.power(r, 1-lower) for r in range(1, 802)}
    native = (E.moment(paid, 1-lower)[0]-E.moment(helpers, 1-lower)[1])/104
    costs = [Q(0)]*100
    for n in range(2, 100):
        node = 2*h[8*n][0]+1-2*h[8*n+1][1]
        costs[n] = min(costs[a]+costs[n-a]+node for a in range(1, n))
    pairs = {}
    nine = []
    for n in range(2, 99):
        values = [h[8*n+1][1]-n*native-costs[n-b]-costs[b]
                  +h[8*b+1][1]-h[8*b][0] for b in range(1, n)]
        pairs[n] = max(values)
        if n == 9:
            nine = values
    alternatives = [h[8*n+1][1]+pairs[x]+pairs[n-x]-2
                    for n in range(4, 100) for x in range(2, n-1)
                    if (x, n-x) != (9, 9)]
    other_totals = max(alternatives)
    other_split = h[145][1]+pairs[9]+max(value for b, value in enumerate(nine, 1) if b != 2)-2
    need(other_totals < 0 and other_split < 0,
         'Every different child-size profile already loses at the lower endpoint')
    tail_upper = h[801][1]+2*h[401][1]-100*(native-1)+2*(h[9][1]-h[8][0])-6
    tail_derivative = 8*(1-lower)*(h[801][1]/801+h[401][1]/401)-(native-1)
    need(tail_upper < 0 and tail_derivative < 0,
         'Every total at least 100 already loses at the lower endpoint')

    # Distinct tree shapes with the same node-size histogram have the same
    # invoice. Enumerate histograms, including every split, through size seven.
    histograms = {1: {tuple([0]*8)}}
    for n in range(2, 8):
        histograms[n] = set()
        for a in range(1, n):
            for left in histograms[a]:
                for right in histograms[n-a]:
                    histograms[n].add(tuple(x+y+(j == n) for j, (x, y) in enumerate(zip(left, right))))
    node_interval = {}
    for n in range(2, 8):
        a, b = E.power(8*n, 1-lower), E.power(8*n+1, 1-lower)
        c, d = E.power(8*n, 1-upper), E.power(8*n+1, 1-upper)
        node_interval[n] = (2*a[0]+1-2*b[1], 2*c[1]+1-2*d[0])
        need(node_interval[n][0] <= node_interval[n][1], 'Increasing binary-node cost on the interval')
    gaps = []
    selected = tree_data[0][1]
    need(tree_data[3][1] == selected and len(histograms[2]) == 1, 'The symmetric children have identical bills')
    selected_tuple = tuple(selected[j] for j in range(8))
    need(selected_tuple in histograms[7], 'The selected tree histogram is present')
    for histogram in histograms[7]-{selected_tuple}:
        difference = [x-y for x, y in zip(histogram, selected_tuple)]
        gap = sum(c*node_interval[n][0 if c >= 0 else 1]
                  for n, c in enumerate(difference) if c)
        need(gap > 0, 'Every other seven-leaf tree bill is larger throughout the bracket')
        gaps.append(gap)

    # A constructive strictifier is available arbitrarily near the raw
    # crossing: alpha<1 below it; these two tail bounds hold on the full
    # bracket. This statement is about the finite supplier, not a new
    # outer-endpoint certificate at the crossing itself.
    target_lower = E.moment(targets, 1-upper)[0]
    gamma_upper = E.moment(calls, 1-lower+Q(1, 7))[1]/(E.power(12, Q(1, 7))[0]*target_lower)
    delta_upper = Q(sum(targets.values())*13)/(E.power(12, lower)[0]*target_lower)
    need(gamma_upper < Q(31, 32) and delta_upper < Q(31, 32), 'Both tails are uniformly below one near the limit')
    return {'raw_limit_interval': list(map(str, (lower, upper))),
            'signed_invoice': {str(r): c for r, c in sorted(raw.items())},
            'unique_selected_sizes_up_to_pair_exchange': sizes,
            'other_pair_total_checks': len(alternatives), 'other_pair_total_margin_upper': str(other_totals),
            'other_nine_leaf_split_margin_upper': str(other_split),
            'lower_endpoint_tail_margin_upper': str(tail_upper),
            'lower_endpoint_tail_derivative_upper': str(tail_derivative),
            'seven_leaf_histograms': len(histograms[7]), 'selected_seven_leaf_histogram': dict(selected),
            'minimum_alternative_tree_cost_gap': str(min(gaps)),
            'uniform_tail_gamma_upper': str(gamma_upper), 'uniform_tail_delta_upper': str(delta_upper),
            'certified_kappa_distance_upper': str(upper-Q(price['kappa'])),
            'statement': 'The exact family raw-funding supremum is the unique zero of the displayed signed invoice. At that zero the raw paid and productive moments are equal, so the strict compiler does not certify equality.',
            'scope': 'Fixed PR6375 source; the classified minimum-idle root family; every positive binary child size and binary tree shape; admitted saving range through .0034.'}
