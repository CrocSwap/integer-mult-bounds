"""Bounded signed-unit target-pair experiment on the pinned selected X4 word.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
The mechanism follows Sricharan Vagvala's PR749; its code is not imported.
"""
import copy
import gzip
import hashlib
import json
import random
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(value, label):
    if not value:
        raise RuntimeError(label)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def apply(gate, rows, dual=False):
    if gate[0] == 'add':
        t, s = gate[1:3]
        q = Q(gate[3], gate[4])
        if dual:
            t, s, q = s, t, -q
        require(t != s, 'self add')
        for k, x in list(rows[s].items()):
            z = rows[t].get(k, Q(0)) + q*x
            if z:
                rows[t][k] = z
            else:
                rows[t].pop(k, None)
    elif gate[0] == 'scale':
        t = gate[1]
        q = Q(gate[2], gate[3])
        if dual:
            q = 1/q
        rows[t] = {k: q*x for k, x in rows[t].items()}
    else:
        raise RuntimeError('unknown logical gate')


def compensation(word):
    v, n = word['v'], 2*word['v']+word['R']
    raw = [{i: Q(1)} for i in range(n)]
    for gate in word['A']+word['cut']+word['B']:
        apply(gate, raw)
    dirt = [{} for _ in range(n)]
    for t in range(v, 2*v):
        dirt[t] = {k: x for k, x in raw[t].items() if k >= 2*v}
    for gate in word['precondition']:
        require(gate[-1] == 0, 'nonzero precondition frame')
        apply(gate, dirt)
    return {t: {k: -x for k, x in dirt[t].items()} for t in range(v, 2*v)}


def add(t, s, q, frame=0):
    q = Q(q)
    require(t != s and q != 0, 'invalid generated add')
    return ['add', t, s, q.numerator, q.denominator, frame]


def row_gates(matrix):
    return [add(t, s, q) for t, row in sorted(matrix.items()) for s, q in sorted(row.items()) if q]


def scalar_cost(gate):
    if gate[0] in ('clear', 'copy'):
        return 2
    q = Q(gate[3], gate[4]) if gate[0] == 'add' else Q(gate[2], gate[3])
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b-1) == 0, 'invalid dyadic scalar')
    if gate[0] == 'scale':
        require(a & (a-1) == 0, 'nonunit scale')
        return 2*(abs(a.bit_length()-b.bit_length()) + int(q < 0))
    return 2*(3+a.bit_length()-1+a.bit_count()+b.bit_length()-1)


def row_cost(row):
    return sum(scalar_cost(add(-1, s, q)) for s, q in row.items() if q)


def combine(a, b, sign):
    row = dict(a)
    for k, x in b.items():
        y = row.get(k, Q(0))+sign*x
        if y:
            row[k] = y
        else:
            row.pop(k, None)
    return row


def search(matrix, seed=39):
    # Complete enumeration; one seeded disjoint greedy pass, no optimality claim.
    scores = []
    for t in sorted(matrix):
        before = row_cost(matrix[t])
        for u in sorted(matrix):
            if t == u:
                continue
            for sign in (-1, 1):
                changed = combine(matrix[t], matrix[u], sign)
                after = row_cost(changed)+2*scalar_cost(add(t, u, sign))
                scores.append([before-after, t, u, sign])
    shuffled = list(scores)
    random.Random(seed).shuffle(shuffled)
    shuffled.sort(key=lambda x: -x[0])
    selected, used = [], set()
    for gain, t, u, sign in shuffled:
        if gain > 0 and not used.intersection((t, u)):
            selected.append([t, u, sign, gain])
            used.update((t, u))
    require(selected, 'no profitable signed-unit target pair')
    return selected, dict(domain=len(scores), profitable=sum(s[0] > 0 for s in scores),
                         scores_sha256=digest(scores), stopping_rule='all ordered target pairs, signs -1/+1; one greedy pass')


def factored(matrix, selected):
    transformed = copy.deepcopy(matrix)
    used = set()
    for t, u, sign, gain in selected:
        require(sign in (-1, 1) and t in matrix and u in matrix and t != u, 'invalid recipe')
        require(not used.intersection((t, u)), 'overlapping target pairs')
        used.update((t, u))
        transformed[t] = combine(matrix[t], matrix[u], sign)
        require(gain == row_cost(matrix[t])-row_cost(transformed[t])-2*scalar_cost(add(t, u, sign)), 'recipe gain')
    prep = [add(t, u, sign) for t, u, sign, _ in selected]
    restore = [add(t, u, -sign) for t, u, sign, _ in reversed(selected)]
    return prep+row_gates(transformed)+restore


def dual(gate):
    result = list(gate)
    if result[0] == 'add':
        result[1], result[2], result[3] = result[2], result[1], -result[3]
    else:
        result[2], result[3] = result[3], result[2]
    return result


def scalar_event(gate, backward=False):
    e = dual(gate) if backward else gate
    if e[0] == 'add':
        scalar = ['add', ['L', e[1]], ['L', e[2]], e[3], e[4]]
    else:
        scalar = ['scale', ['L', e[1]], e[2], e[3]]
    return ['scalar', scalar, 0]


def splice(program, canonical, replacement, backward=False):
    require(program[0] == ['phase', 'zero_frame_precondition'], 'initial phase')
    end = program.index(['phase', 'entry_adapters'])
    original = canonical['precondition']+canonical['compensation']
    require(program[1:end] == [scalar_event(e, backward) for e in original], 'baseline compensation boundary')
    start = 1+len(canonical['precondition'])
    return program[:start]+[scalar_event(e, backward) for e in replacement]+program[end:]


def lower(scalar):
    """Literal one-real-component primitive word, including all private work.

    w is the inherited private coefficient stream. It is cleared before and
    after each add; each access/double/half/update/clear is an instruction.
    """
    tag, t = scalar[0], tuple(scalar[1])
    if tag == 'clear':
        return [('clear', t)]
    if tag == 'copy':
        return [('copy', t, tuple(scalar[2]))]
    q = Q(scalar[3], scalar[4]) if tag == 'add' else Q(scalar[2], scalar[3])
    a, b = abs(q.numerator), q.denominator
    require(a and b & (b-1) == 0, 'lowering dyadic')
    if tag == 'scale':
        require(a & (a-1) == 0, 'lowering unit scale')
        power = a.bit_length()-b.bit_length()
        result = [('scale', t, Q(2) if power > 0 else Q(1, 2)) for _ in range(abs(power))]
        if q < 0:
            result.append(('scale', t, Q(-1)))
        return result
    require(tag == 'add', 'unknown lowering')
    s, w = tuple(scalar[2]), ('W', 0)
    result = [('clear', w)]
    for i, bit in enumerate(bin(a)[2:]):
        if i:
            result.append(('scale', w, Q(2)))
        if bit == '1':
            result.append(('add', w, s, Q(1)))
    result.extend(('scale', w, Q(1, 2)) for _ in range(b.bit_length()-1))
    result.extend([('add', t, w, Q(1 if q > 0 else -1)), ('clear', w)])
    require(2*len(result) == scalar_cost(scalar), 'lowering price')
    return result


def replay_emitted(events, n, v, backward=False):
    """Exact all-column macro replay and positive primitive-prefix enclosure."""
    # Arbitrary inputs for all eight private centres and the coefficient stream
    # are included. Their inherited CLEAR contract erases them, not restores dirt.
    keys = [('L', i) for i in range(n)]+[('C', i) for i in range(8)]+[('W', 0)]
    state = {key: {i: Q(1)} for i, key in enumerate(keys)}
    bound = {key: Q(1) for key in keys}
    peak = Q(1)
    paid = Counter()
    count = macros = 0
    for event in events:
        if event[0] in ('climb', 'center'):
            paid[event[5] if event[0] == 'climb' else event[4]] += 1
            continue
        if event[0] != 'scalar':
            continue
        scalar = event[1]
        macros += 1
        for primitive in lower(scalar):
            count += 2  # identical real and imaginary component instructions
            tag, t = primitive[:2]
            if tag == 'clear':
                bound[t] = Q(0)
                state[t] = {}
            elif tag == 'copy':
                bound[t] = bound[primitive[2]]
                state[t] = dict(state[primitive[2]])
            elif tag == 'scale':
                bound[t] *= abs(primitive[2])
                state[t] = {k: primitive[2]*x for k, x in state[t].items()}
            else:
                bound[t] += abs(primitive[3])*bound[primitive[2]]
                for k, x in list(state[primitive[2]].items()):
                    z = state[t].get(k, Q(0))+primitive[3]*x
                    if z:
                        state[t][k] = z
                    else:
                        state[t].pop(k, None)
            peak = max(peak, bound[t])
    for i in range(n):
        expected = {i: Q(1)}
        if backward and i < v:
            expected[i+v] = Q(-1)
        elif not backward and v <= i < 2*v:
            expected[i-v] = Q(1)
        require(state['L', i] == expected, 'emitted endpoint '+str(i))
    require(all(not state[k] for k in keys[n:]), 'private centre/stream erasure')
    bits = peak.numerator.bit_length()-peak.denominator.bit_length()+1
    return dict(real_component_primitives=count, scalar_macros=macros,
                prefix_l1=str(peak), prefix_bits=bits,
                paid_profile=dict(sorted(paid.items())), checked_columns=n+9,
                private_input_contract='eight centres and coefficient stream are erased by charged CLEARs',
                program_sha256=digest(events))


def logical_program(word, replacement):
    return word['precondition']+replacement+word['A']+word['cut']+word['B']+word['tail']+word['cleanup']
