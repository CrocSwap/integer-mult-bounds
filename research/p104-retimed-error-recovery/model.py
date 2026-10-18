"""Exact logical response of one pinned word; no predecessor code imports."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def plus(target, source, scalar):
    for key, value in source.items():
        value = target.get(key, 0) + scalar * value
        if value:
            target[key] = value
        else:
            target.pop(key, None)


def space(basis):
    values = {0}
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, 'frame vector')
        values |= {x ^ vector for x in values}
    need(len(values) == 2 ** len(basis), 'frame independence')
    return frozenset(values)


def norm(row, weights=None):
    return sum((abs(v) * (weights[k] if weights else 1)
                for k, v in row.items()), Q(0))


def replay(word):
    initial = word['initial_frames']
    values = {r: {r: Q(1)} for r in initial}
    errors = {r: {} for r in initial}
    frames = {r: space(b) for r, b in initial.items()}
    peaks = {k: {'value': Q(1) if k == 'P' else Q(0), 'cut': 0,
                 'role': sorted(initial)[0]} for k in ('P', 'A', 'K', 'J', 'N')}
    weights, operand, native = {}, {}, {}
    erasures, snapshots, counts, profile = [], {}, Counter(), Counter()
    score_digest = sha256()
    for index, event in enumerate(word['program']):
        op, r, *args = event
        counts[op] += 1
        if op == 'zero':
            need(r not in values, 'allocation of live private role')
            values[r], errors[r], frames[r] = {}, {}, space(args[0])
            continue
        need(r in values, 'use of absent role')
        if op == 'erase':
            need(not values[r] and frames[r] == space(args[0]), 'nonzero ideal erase')
            erasures.append({'cut': index, 'role': r, 'A': str(norm(errors[r])),
                             'K': str(norm(errors[r], weights)),
                             'J': str(norm(errors[r], operand))})
            snapshots[(index, r)] = (values[r].copy(), errors[r].copy())
            del values[r], errors[r], frames[r]
            continue
        if op == 'transport':
            old, new, rank = args
            old, new = space(old), space(new)
            need(frames[r] == old and (old <= new or new <= old), 'transport frames')
            need(type(rank) is int and rank > 0 and
                 rank == abs(len(new).bit_length() - len(old).bit_length()), 'rank')
            operand[index], weights[index], native[index] = norm(values[r]), Q(1), Q(1)
            frames[r] = new
            profile[rank] += 1
        elif op == 'add':
            source, scalar, basis = args
            need(source in values and source != r, 'ADD roles')
            need(frames[r] == frames[source] == space(basis), 'ADD chart')
            scalar = Q(scalar)
            operand[index] = norm(values[r]) + abs(scalar) * norm(values[source])
            weights[index], native[index] = 1 + abs(scalar), Q(0)
            plus(values[r], values[source], scalar)
            plus(errors[r], errors[source], scalar)
        elif op == 'sign':
            scalar, basis = args
            need(Q(scalar) == -1 and frames[r] == space(basis), 'exact sign')
            values[r] = {k: -v for k, v in values[r].items()}
            errors[r] = {k: -v for k, v in errors[r].items()}
        else:
            raise ValueError('unknown operation')
        if op in ('transport', 'add'):
            errors[r][index] = Q(1)
        scores = {'P': norm(values[r]), 'A': norm(errors[r]),
                  'K': norm(errors[r], weights), 'J': norm(errors[r], operand),
                  'N': norm(errors[r], native)}
        payload = [index + 1, r, {key: str(v) for key, v in scores.items()}]
        score_digest.update((json.dumps(payload, sort_keys=True) + '\n').encode())
        for key, score in scores.items():
            if score > peaks[key]['value']:
                peaks[key] = {'value': score, 'cut': index + 1, 'role': r}
                snapshots[('peak', key)] = (values[r].copy(), errors[r].copy())
    need(frames == {r: space(b) for r, b in word['final_frames'].items()}, 'final frames')
    need(len(erasures) == 8 and len(values) == 358, 'private/public lifetimes')
    final = {r: (values[r], errors[r]) for r in values}
    return {'peaks': peaks, 'weights': weights, 'operand': operand, 'native': native,
            'snapshots': snapshots, 'erasures': erasures, 'final': final,
            'counts': dict(counts), 'profile': dict(profile),
            'all_cut_score_sha256': score_digest.hexdigest()}


def adjoint(program, cut, role, public):
    """Reverse covector substitution, independently of forward row operations."""
    covector, defects = {role: Q(1)}, {}
    for index in range(cut - 1, -1, -1):
        op, target, *args = program[index]
        weight = covector.get(target, Q(0))
        if op in ('add', 'transport') and weight:
            defects[index] = weight
        if op == 'add' and weight:
            source, scalar, _ = args
            updated = covector.get(source, Q(0)) + Q(scalar) * weight
            if updated:
                covector[source] = updated
            else:
                covector.pop(source, None)
        elif op == 'sign' and weight:
            covector[target] = -weight
        elif op == 'zero':
            covector.pop(target, None)
        elif op == 'erase':
            need(not weight, 'reverse live state crosses discarded role')
    need(set(covector) <= set(public), 'adjoint initial roles')
    return covector, defects


def literal(program, cut, public, inputs, defects):
    """Collinear Hilbert-vector execution, using scalar values, not response maps."""
    state = {r: Q(inputs.get(r, 0)) for r in public}
    discarded = []
    for index, event in enumerate(program[:cut]):
        op, target, *args = event
        if op == 'zero':
            state[target] = Q(0)
        elif op == 'erase':
            discarded.append(state.pop(target))
        elif op == 'add':
            source, scalar, _ = args
            state[target] += Q(scalar) * state[source] + defects.get(index, 0)
        elif op == 'transport':
            state[target] += defects.get(index, 0)
        elif op == 'sign':
            state[target] = -state[target]
        else:
            raise ValueError('literal operation')
    return state, discarded


def nearest(value, spacing):
    need(spacing > 0, 'positive recovery spacing')
    ratio = value / spacing
    lower = ratio.numerator // ratio.denominator
    offset = ratio - lower
    need(offset != Q(1, 2), 'half-grid ambiguity')
    return (lower + (offset > Q(1, 2))) * spacing
