"""Certify a unique positive raw crossing with Laguerre's tail-sum rule.

For F(t) = sum_r c_r r^t with distinct positive ranks r_0 < ... < r_n, the
number of zeros of F on t > 0, counted with multiplicity, is at most the
number of sign changes in the tail sums B_k = c_k + ... + c_n.
PROOF.md gives the argument. This checker uses exact integers only.

Apache-2.0. Produced by Nick Petalas. The invoice is Ali Romman's
research/balanced-query-tree bill (PR6348).
"""
import decimal
import json
import pathlib
import sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
SOURCE = HERE.parent / 'balanced-query-tree' / 'RESULT.json'
MARKER = 'PASS_TAIL_SUM_CROSSING_UNIQUENESS'


def need(condition, label):
    if not condition:
        raise SystemExit('FAIL: ' + label)


def sign(value):
    return (value > 0) - (value < 0)


def changes(values):
    """Sign changes in a sequence, ignoring zeros."""
    signs = [sign(v) for v in values if v]
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)


def signed(targets, paid):
    ranks = sorted(set(targets) | set(paid))
    need(all(isinstance(r, int) and r >= 1 for r in ranks), 'Positive integer ranks')
    return [(r, targets.get(r, 0) - paid.get(r, 0)) for r in ranks
            if targets.get(r, 0) != paid.get(r, 0)]


def tail_sums(coefficients):
    """B_k = c_k + ... + c_n, listed in increasing rank order."""
    out, total = [], 0
    for _, c in reversed(coefficients):
        total += c
        out.append(total)
    return out[::-1]


def certify(targets, paid):
    """Return the certificate, or None if the tail-sum rule does not settle it."""
    c = signed(targets, paid)
    descartes = changes([v for _, v in c])
    tails = tail_sums(c)
    laguerre = changes(tails)
    f0 = sum(v for _, v in c)
    f1 = sum(r * v for r, v in c)
    # F(0) = B_0 < 0 < F(1): at least one root in (0,1); laguerre == 1 caps all of t > 0.
    unique = laguerre == 1 and f0 < 0 < f1
    return {'descartes_changes': descartes, 'tail_sum_changes': laguerre,
            'F0_count_difference': f0, 'F1_rank_mass_surplus': f1,
            'signed_coefficients': [[r, v] for r, v in c], 'tail_sums': tails,
            'unique_simple_root_in_0_1_and_none_above': unique}


def value_sign(c, t):
    """Sign of F at t with 60-digit decimals (consistency control, not the proof)."""
    with decimal.localcontext() as ctx:
        ctx.prec = 60
        total = sum(v * (decimal.Decimal(r).ln() * t).exp() for r, v in c)
    need(abs(total) > decimal.Decimal('1e-30'), 'Sample point away from the root')
    return sign(total)


def load():
    data = json.loads(SOURCE.read_text())
    local, physical = data['local'], data['physical']
    helpers = {int(k): v for k, v in local['helpers'].items()}
    local_paid = {int(k): v for k, v in local['paid'].items()}
    calls, queries, ports = physical['full_calls'], 16, physical['ports']
    targets = Counter({r: calls * v for r, v in helpers.items()})
    targets.update({int(k): v for k, v in physical['main_targets'].items()})
    paid = Counter({r: calls * v for r, v in local_paid.items()})
    paid[1] += queries * ports
    paid.update({int(k): v for k, v in physical['whole_idle_jobs'].items()})
    need((sum(targets.values()), sum(paid.values())) == (14214, 70523), 'Source field and call totals')
    return dict(targets), dict(paid)


def main():
    targets, paid = load()
    cert = certify(targets, paid)
    need(cert['F1_rank_mass_surplus'] == 808, 'Rank-mass surplus 808')
    need(cert['F0_count_difference'] == 14214 - 70523, 'Count difference')
    need(cert['descartes_changes'] == 13, 'Descartes budget 13')
    need(cert['tail_sum_changes'] == 1, 'One tail-sum sign change')
    need(cert['unique_simple_root_in_0_1_and_none_above'], 'Unique simple positive root')
    c = [tuple(x) for x in cert['signed_coefficients']]
    # Consistency with the source enclosure (0.00314934401301, 0.00314934401302):
    # F(1-k) < 0 just above the root and > 0 just below, i.e. t = 1-k.
    D = decimal.Decimal
    need(value_sign(c, D(1)) > 0, 'F(1) > 0')
    need(value_sign(c, D('0.99685')) < 0, 'F(0.99685) < 0, above k = 0.00315')
    need(value_sign(c, D('0.99686')) > 0, 'F(0.99686) > 0, below k = 0.00314')
    # Controls: the rule must fail closed on invoices it cannot settle.
    two = certify({1: 6, 6: 2}, {2: 4, 3: 3})      # 2(2^t-3/2)(3^t-2): two interior roots
    need(two['tail_sum_changes'] >= 2 and not two['unique_simple_root_in_0_1_and_none_above'],
         'Two-root control rejected')
    flipped = certify(paid, targets)
    need(not flipped['unique_simple_root_in_0_1_and_none_above'], 'Reversed invoice rejected')
    bumped = dict(targets)
    bumped[153] -= 208
    need(not certify(bumped, paid)['unique_simple_root_in_0_1_and_none_above'], 'Removed root target rejected')
    if '--json' in sys.argv:
        print(json.dumps(cert, indent=1))
    print(MARKER)


if __name__ == '__main__':
    main()
