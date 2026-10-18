#!/usr/bin/env python3
"""Bounded independent controls for the Discussion1516 adversarial review.

Six fixed traces only: simultaneous or nonsimultaneous observations over
Q, F2, and F3. Three additional prefix/zero-work boundary controls.
No producer imports, repository data, selected geometry, or search.
This is not a formal proof, production interpreter, or general circuit library.
"""
from fractions import Fraction
import json


class CheckFailure(Exception):
    pass


def require(ok, message):
    if not ok:
        raise CheckFailure(message)


def fixed_controls(characteristic, simultaneous):
    """Replay one explicitly fixed nested-frame trace, with exact row arithmetic."""
    p = characteristic

    def scalar(x):
        return Fraction(x) if not p else int(x) % p

    def add(a, b, coefficient=1):
        require(len(a) == len(b), 'row-width mismatch')
        return tuple(scalar(x + scalar(coefficient)*y) for x, y in zip(a, b))

    def rank(rows):
        a = [list(map(scalar, row)) for row in rows]
        if not a:
            return 0
        width = len(a[0])
        require(all(len(row) == width for row in a), 'ragged matrix')
        pivots = 0
        for column in range(width):
            candidates = [i for i in range(pivots, len(a)) if a[i][column]]
            if not candidates:
                continue
            i = candidates[0]
            a[pivots], a[i] = a[i], a[pivots]
            inverse = 1/a[pivots][column] if not p else pow(a[pivots][column], -1, p)
            a[pivots] = [scalar(v*inverse) for v in a[pivots]]
            for j in range(len(a)):
                if j != pivots:
                    coefficient = a[j][column]
                    a[j] = [scalar(u-coefficient*v) for u, v in zip(a[j], a[pivots])]
            pivots += 1
            if pivots == len(a):
                break
        return pivots

    require(rank([[1, 1], [1, -1]]) == (1 if p == 2 else 2), 'field-rank control')
    zero = (scalar(0),)*4
    x, d, e, y = [tuple(scalar(i == j) for i in range(4)) for j in range(4)]
    # One carrier at height 2, descending host 3->1, ascending host 0->2.
    # P is the only private role, zero at entry and at exit.
    rows = {'X': x, 'D': d, 'A': e, 'Y': y, 'P': zero}
    heights = {'X': 2, 'D': 3, 'A': 0, 'Y': 0, 'P': 2}
    initial_low = {j: [v for k, v in rows.items() if heights[k] < j] for j in (1, 2, 3)}
    initial_high = {j: [v for k, v in rows.items() if heights[k] >= j] for j in (1, 2, 3)}
    low = {j: set(v) for j, v in initial_low.items()}
    high = {j: set(v) for j, v in initial_high.items()}
    down = {j: 0 for j in (1, 2, 3)}
    up = {j: 0 for j in (1, 2, 3)}
    mass, observations, coexistence = 0, [], []
    clean_y = add(y, x)
    events = [
        ('a', 'P', 'X', 1), ('m', 'P', 0), ('a', 'Y', 'P', 1),
        ('o', 'target_clean', 'Y', 0, clean_y),
        # Target feedback goes uphill and temporarily changes the carrier.
        ('a', 'P', 'Y', 1), ('m', 'P', 2),
        ('a', 'X', 'P', 1), ('a', 'X', 'P', -1),
        ('m', 'P', 0), ('a', 'P', 'Y', -1),
    ]
    if not simultaneous:
        events.append(('a', 'Y', 'P', -1))  # Remove the clean scatter before host observation.
    events += [('z', 'P'), ('m', 'D', 1), ('o', 'descending_host', 'D', 1, d),
               ('m', 'A', 2), ('o', 'ascending_host', 'A', 2, e)]
    saw_target_feedback = False
    for index, event in enumerate(events):
        op, dst = event[:2]
        if op == 'a':
            src, coefficient = event[2:]
            require(src != dst and heights[dst] == heights[src], 'nonlocal scalar event')
            rows[dst] = add(rows[dst], rows[src], coefficient)
            if dst == 'X' and coefficient == 1:
                saw_target_feedback = rows['X'][3] != 0
        elif op == 'm':
            before, after = heights[dst], event[2]
            require(0 <= after <= 3, 'height out of fixed range')
            mass += abs(after-before)
            for j in (1, 2, 3):
                down[j] += int(after < j <= before)
                up[j] += int(before < j <= after)
            heights[dst] = after
        elif op == 'z':
            require(dst == 'P', 'only private work may be cleared in this trace')
            rows[dst] = zero
        elif op == 'o':
            label, register, height, value = event[1:]
            require(heights[register] == height and rows[register] == value, 'false checkpoint')
            observations.append({'label': label, 'event_index': index, 'height': height})
        else:
            raise CheckFailure('unknown fixed event')
        for j in (1, 2, 3):
            low[j].update(v for k, v in rows.items() if heights[k] < j)
            high[j].update(v for k, v in rows.items() if heights[k] >= j)
            require(rank(low[j])-rank(initial_low[j]) <= down[j], 'down-history failure')
            require(rank(high[j])-rank(initial_high[j]) <= up[j], 'up-history failure')
        coexistence.append(rows['Y'] == clean_y and heights['Y'] == 0 and
                           rows['D'] == d and heights['D'] == 1 and
                           rows['A'] == e and heights['A'] == 2)
    expected = {'X': x, 'D': d, 'A': e, 'Y': clean_y if simultaneous else y, 'P': zero}
    require(rows == expected, 'incorrect full exit rows')
    require(heights == {'X': 2, 'D': 1, 'A': 2, 'Y': 0, 'P': 0}, 'incorrect exit heights')
    require(saw_target_feedback, 'missing actual target feedback')
    require(any(coexistence) == simultaneous, 'checkpoint coexistence boundary failed')
    require(mass == sum(down.values()) + sum(up.values()) == 10, 'wrong trace mass')
    profile = []
    for j in (1, 2, 3):
        h_minus, h_plus = int(1 < j <= 3), int(0 < j <= 2)
        required_down = int(j <= 2) + h_minus
        require(down[j] >= required_down and up[j] >= h_plus, 'directional corollary failure')
        profile.append({'j': j, 'down': down[j], 'up': up[j],
                        'new_low_rank': rank(low[j])-rank(initial_low[j]),
                        'new_high_rank': rank(high[j])-rank(initial_high[j]),
                        'required_down': required_down, 'required_up': h_plus})
    require(mass >= (3-1)+(2-0)+2*1, 'host-subtracted inequality failed')

    # A reversible ALL-LIVE prefix is not necessarily invertible on the
    # ORDINARY state after a private input is fixed to zero. Both gates are local.
    ordinary, private = (scalar(1),), (scalar(0),)
    private = add(private, ordinary)
    ordinary = add(ordinary, private, -1)
    require(ordinary == (scalar(0),) and private == (scalar(1),), 'prefix witness wrong')
    require(rank([[0, -1], [1, 1]]) == 2, 'all-live prefix not invertible')
    require(rank([ordinary]) == 0 and rank([ordinary, private]) == 1, 'ordinary-rank witness wrong')
    return {'field': 'Q' if not p else 'F'+str(p),
            'variant': 'simultaneous_exit' if simultaneous else 'checkpoint_only',
            'scatter_rank': 1, 'q': 2, 'host_height_displacement': 4,
            'proved_lower_bound_for_this_contract': 6, 'actual_mass': mass,
            'target_feedback_used': saw_target_feedback,
            'all_clean_obligations_ever_coexisted': any(coexistence),
            'observations': observations, 'cut_profile': profile,
            'reversible_all_live_prefix_can_lose_ordinary_independence': True}


def main():
    fixtures = [fixed_controls(p, simultaneous) for p in (0, 2, 3) for simultaneous in (True, False)]
    print(json.dumps({'status': 'PASS_BOUNDED_BOUNDARY_CONTROLS', 'trace_count': len(fixtures),
                      'distinct_prefix_field_controls': 3,
                      'scope': 'Fixed toy traces only; no exhaustive search or selected-word verification.',
                      'fixtures': fixtures}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
