"""Price the fixed (7,2,5,4) tree before its Gaussian retirement.

The binary supplier and mixed root are from PR6348 and PR6398. The
independent retirement is from PR6545. All source authors keep their credit.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter


def need(ok, message):
    if not ok:
        raise ValueError(message)


def formula_invoice(local):
    targets = Counter({r: 18*n for r, n in local['helpers'].items()})
    paid = Counter({r: 18*n for r, n in local['paid'].items()})
    paid[1] += 17*104
    # The four trees have fourteen internal nodes.
    for size, count in {2: 8, 3: 2, 4: 2, 5: 1, 7: 1}.items():
        targets[1+8*size] += 208*count
        paid[8*size] += 208*count
    for rank, count in {145: 1, 73: 2, 1: 1, 17: 1, 41: 1}.items():
        targets[rank] += 104*count
    paid[16] += 104
    paid[40] += 104
    return targets, paid


def difference(after, before):
    out = Counter({int(k): v for k, v in after.items()})
    out.subtract({int(k): v for k, v in before.items()})
    return {rank: count for rank, count in out.items() if count}


def compare(after, before):
    targets = difference(after['targets'], before['targets'])
    paid = difference(after['paid'], before['paid'])
    need(targets == {16: -104, 40: 104, 41: 208, 57: -208},
         'Complete productive change from PR6545')
    need(paid == {16: -104, 40: 312, 56: -208},
         'Complete paid change from PR6545')
    signed = difference(targets, paid)
    need(signed == {40: -208, 41: 208, 56: 208, 57: -208},
         'Exact two-interval concave difference')
    return {'targets': targets, 'paid': paid, 'signed': signed,
            'gain_formula': '208*(H41-H40-H57+H56)',
            'rank_mass_change': sum(r*n for r, n in targets.items())}
