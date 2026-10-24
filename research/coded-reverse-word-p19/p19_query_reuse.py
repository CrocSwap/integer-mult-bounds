#!/usr/bin/env python3
"""Exact source equality screen for reuse of the existing forward queries.

The algebra is Q[FreeGroup(C,Q) x Z(R)], using the source relations
[R,C]=[R,Q]=0. This screens the common-R listing, not its fresh-block lift.
OpenAI-assisted; Apache-2.0. The word constructor remains unchanged.
"""
import json
from fractions import Fraction
from pathlib import Path

import p19_word as W


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b, coefficient=1):
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, 0) + coefficient * value
        if not result[key]:
            del result[key]
    return result


def left(row, letter):
    result = {}
    for (origin, word, power), value in row.items():
        new = word[1:] if word and word[0] == -letter else (letter,) + word
        result[origin, new, power] = value
    return result


def gaussian(row, power):
    return {(origin, word, exponent + power): value
            for (origin, word, exponent), value in row.items()}


def signature(row):
    return tuple(sorted(row.items()))


def query_span(row, sources):
    basis = {}
    for event, source in sources:
        residual = dict(source)
        weights = {event: Fraction(1)}
        while residual:
            pivot = min(residual)
            if pivot not in basis:
                coefficient = Fraction(1, 1) / residual[pivot]
                basis[pivot] = ({k: coefficient * v for k, v in residual.items()},
                                {k: coefficient * v for k, v in weights.items()})
                break
            vector, recipe = basis[pivot]
            coefficient = -residual[pivot]
            residual = add(residual, vector, coefficient)
            weights = add(weights, recipe, coefficient)
    residual, weights = dict(row), {}
    while residual:
        pivot = min(residual)
        if pivot not in basis:
            return None
        vector, recipe = basis[pivot]
        coefficient = residual[pivot]
        residual = add(residual, vector, -coefficient)
        weights = add(weights, recipe, coefficient)
    reconstructed = {}
    for event, source in sources:
        if event in weights:
            reconstructed = add(reconstructed, source, weights[event])
    need(reconstructed == row, 'query span reconstruction')
    return {str(k): str(v) for k, v in sorted(weights.items())}


def screen(gates, p):
    rows = [{(r, (), 0): 1} for r in range(2 * p)]
    parity = [0] * (2 * p)
    queries = {}
    sources = []
    repairs = []
    repair_sources = []
    for index, gate in enumerate(gates):
        kind = gate[0]
        if kind in ('GAUGE_LOAD', 'GAUGE_UNLOAD'):
            r = gate[1]
            rows[r] = left(rows[r], -1 if kind == 'GAUGE_LOAD' else 1)
        elif kind == 'FORWARD':
            x, y = gate[1:3]
            queries.setdefault(signature(rows[x]), []).append(index)
            sources.append((index, dict(rows[x])))
            rows[y] = add(rows[y], left(left(rows[x], -2), -1))
        elif kind == 'REVERSE':
            x, y = gate[1:3]
            rows[x] = add(rows[x], left(left(rows[y], 1), 2), -1)
        elif kind in ('LETTER', 'IDLE'):
            power = 1 if kind == 'LETTER' else gate[3]
            for r in gate[1:3]:
                rows[r] = gaussian(rows[r], power)
                parity[r] ^= power % 2
        elif kind == 'BRIDGE':
            dst, src, coefficient = gate[1:4]
            if parity[dst] != parity[src]:
                repair_sources.append(dict(rows[src]))
                repairs.append({
                    'event': index, 'destination': dst, 'source': src,
                    'parities': [parity[dst], parity[src]],
                    'earlier_equal_query_sources': queries.get(signature(rows[src]), [])[:],
                    'earlier_query_linear_combination': query_span(rows[src], sources),
                })
            rows[dst] = add(rows[dst], rows[src], coefficient)
        elif kind == 'SWAP':
            x, y, sign = gate[1:]
            rows[x], rows[y] = rows[y], {key: sign * value for key, value in rows[x].items()}
            parity[x], parity[y] = parity[y], parity[x]
        else:
            raise ValueError(kind)
    for repair, row in zip(repairs, repair_sources):
        repair['all_query_linear_combination'] = query_span(row, sources)
    return repairs


def main():
    x = {(0, (), 0): 1}
    y = {(1, (), 0): 1}
    need(left(left(x, 1), -1) == x, 'inverse cancellation')
    need(left(left(x, 1), 2) != left(left(x, 2), 1), 'C/Q order control')
    need(gaussian(left(x, 1), 1) == left(gaussian(x, 1), 1), 'C/R relation')
    need(signature(x) != signature(add(x, y)), 'source update changes reuse key')
    need(query_span(add(x, y), [(0, x), (1, y)]) == {'0': '1', '1': '1'},
         'linear combination of cached queries found')
    need(query_span(y, [(0, x)]) is None, 'independent source rejected')
    control = [('FORWARD', 0, 1), ('LETTER', 2, 3), ('BRIDGE', 2, 0, 1)]
    need(screen(control, 2)[0]['earlier_equal_query_sources'] == [0], 'unchanged query source found')
    changed = control[:2] + [('BRIDGE', 0, 4, 1)] + control[2:]
    need(screen(changed, 3)[0]['earlier_equal_query_sources'] == [], 'changed query source rejected')
    gates = W.native_chain(19, 'I' * 9 + 'T' * 9)
    repairs = screen(gates, 19)
    print(json.dumps({
        'scope': 'common-R symbolic source-equality screen only; no fresh-block or cost admission',
        'gate_count': len(gates),
        'bridge_checkpoints': repairs,
        'checkpoints_with_prior_equal_query': sum(bool(r['earlier_equal_query_sources']) for r in repairs),
        'checkpoints_in_prior_query_span': sum(r['earlier_query_linear_combination'] is not None for r in repairs),
        'checkpoints_in_all_query_span': sum(r['all_query_linear_combination'] is not None for r in repairs),
        'controls_passed': 8,
        'script': Path(__file__).name,
    }, indent=2))


if __name__ == '__main__':
    main()
