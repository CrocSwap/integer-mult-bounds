#!/usr/bin/env python3
"""Independent sparse Fraction forward and reverse checks; no native imports.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
The explicit injected vector is a witness input, not an oracle for the response.
"""
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    'research/joint-query/certificate.json.gz': 'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7',
    'research/community-frontier1042-audit/selected-replay.tar.gz': '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load():
    for name, pin in PINS.items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, 'independent source pin')
    p = json.loads(gzip.decompress((ROOT / 'research/joint-query/certificate.json.gz').read_bytes()))
    events = []
    for e in p['programs']['B_1_2']:
        if e[0] == 'retained_core':
            require(e[1:3] == ['backward', 1], 'backward core')
            events.extend(p['core_words']['backward'])
        elif e[0] in ('private_sweep', 'cover_sweep'):
            events.extend(e[2])
        else:
            events.append(e)
    require(len(events) == 27019, 'event count')
    require(events[13489] == ['climb', 'A', 344, 226, 236, 1], 'origin')
    require(events[26472] == ['scalar', ['add', ['L', 93], ['L', 103], -1, 8], 1], 'target')
    with tarfile.open(ROOT / 'research/community-frontier1042-audit/selected-replay.tar.gz') as arc:
        recipes = json.load(arc.extractfile('slots/local/CLIFFORD-RECIPES.json'))
        residuals = json.load(arc.extractfile('slots/local/RESIDUAL-ADAPTERS.json'))
    return events, recipes, residuals


def wire(token):
    require(token[0] in ('L', 'C'), 'wire type')
    return token[1] + (704 if token[0] == 'C' else 0)


def plus(a, b, coefficient=F(1)):
    result = dict(a)
    for x, (r, i) in b.items():
        oldr, oldi = result.get(x, (F(0), F(0)))
        z = oldr + coefficient*r, oldi + coefficient*i
        if z == (0, 0):
            result.pop(x, None)
        else:
            result[x] = z
    return result


def scale(a, coefficient):
    return {x: (r*coefficient, i*coefficient) for x, (r, i) in a.items() if coefficient}


def rotation(z, angle):
    r, i = z
    for _ in range(angle % 4):
        r, i = -i, r
    return r, i


def permutation(record):
    require(len(record['matrix_rows']) == 9, 'nine-axis monomial')
    table = []
    for x in range(512):
        y = record['offset']
        for k, row in enumerate(record['matrix_rows']):
            y ^= ((row & x).bit_count() & 1) << k
        angle = record['phase']
        for a in range(9):
            if (x >> a) & 1:
                angle += record['linear_Z4'][a]
                for b in range(a+1, 9):
                    if ((x >> b) & 1) and ((record['quadratic_rows'][a] >> b) & 1):
                        angle += 2
        table.append((y, angle % 4))
    require(len({y for y, _ in table}) == 512, 'permutation bijection')
    return table


def mono(value, record, adjoint):
    if not value:
        return {}
    result = {}
    for x, (y, phase) in enumerate(permutation(record)):
        source, target, angle = (y, x, -phase) if adjoint else (x, y, phase)
        if source in value:
            result[target] = rotation(value[source], angle)
    return result


def gaussian(value, axis, sign):
    """C_axis or its adjoint from the two translation coefficients."""
    result = {}
    for x, (r, i) in value.items():
        for y, z in ((x, ((r-sign*i)/2, (i+sign*r)/2)),
                     (x ^ axis, ((r+sign*i)/2, (i-sign*r)/2))):
            old = result.get(y, (F(0), F(0)))
            total = old[0] + z[0], old[1] + z[1]
            if total != (0, 0):
                result[y] = total
            else:
                result.pop(y, None)
    return result


def native_adjoint(value, recipe):
    value = mono(value, recipe['left'], True)
    for j in reversed(range(recipe['rank'])):
        value = gaussian(value, 1 << j, -1)
    if recipe['rank']:
        value = mono(value, recipe['right'], True)
    else:
        require(recipe['right'] is None, 'rank-zero native')
    return value


def native_forward(value, recipe):
    if recipe['rank']:
        value = mono(value, recipe['right'], False)
        for j in range(recipe['rank']):
            value = gaussian(value, 1 << j, 1)
    else:
        require(recipe['right'] is None, 'rank-zero native')
    return mono(value, recipe['left'], False)


def encoded(value):
    """Canonical full vector, independently reduced from Fraction components."""
    exponent = 0
    for pair in value.values():
        for v in pair:
            require(v.denominator & (v.denominator-1) == 0, 'Gaussian dyadic component')
            exponent = max(exponent, v.denominator.bit_length()-1)
    real, imag = [0]*512, [0]*512
    for x, (r, i) in value.items():
        real[x] = r.numerator * ((1 << exponent) // r.denominator)
        imag[x] = i.numerator * ((1 << exponent) // i.denominator)
    return real, imag, exponent


def json_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def full_forward(events, recipes, residuals, witness):
    children = {(r['old'], r['new']): r for r in recipes['children']}
    endpoints = {(r['role'], r['port']): r for r in recipes['endpoint_adapters']}
    state = [{} for _ in range(712)]
    state[344] = {x: (F(a, 1 << witness['exponent']), F(b, 1 << witness['exponent']))
                  for x, (a, b) in enumerate(zip(witness['real'], witness['imag'])) if a or b}
    trace, peak, cut = hashlib.sha256(), witness['exponent'], None
    for at in range(13490, len(events)):
        e = events[at]
        if e[0] == 'scalar':
            g, d = e[1], wire(e[1][1])
            if g[0] == 'clear':
                require(d >= 704, 'owned private clear')
                state[d] = {}
            elif g[0] == 'scale':
                state[d] = scale(state[d], F(g[2], g[3]))
            else:
                require(g[0] == 'add', 'known scalar')
                state[d] = plus(state[d], state[wire(g[2])], F(g[3], g[4]))
        elif e[0] == 'climb':
            _, _, d, old, new, rank = e
            require(children[old, new]['rank'] == rank, 'rank binding')
            state[d] = native_forward(state[d], children[old, new])
        elif e[0] == 'adapter':
            _, direction, d, _ = e
            if direction == 'old_to_new' and d < 112:
                state[d] = mono(state[d], endpoints['source', d]['left'], False)
            elif direction == 'new_to_old' and 112 <= d < 224:
                state[d] = mono(state[d], endpoints['target', d-112]['left'], True)
            else:
                require(direction in ('old_to_new', 'new_to_old'), 'adapter direction')
        elif e[0] == 'residual_adapter':
            direction, d, a = e[1:4]
            b = e[4] if len(e) == 5 else 1
            require(direction in ('pre', 'post'), 'residual direction')
            key = str(a) if b == 1 else f'{a}:{b}'
            part = 'right' if direction == 'pre' else 'left'
            state[d] = mono(state[d], residuals['recipes'][key][part], True)
        else:
            require(e[0] == 'phase', 'unknown event in local suffix')
            continue
        packed = encoded(state[d])
        peak = max(peak, packed[2])
        trace.update(json_bytes([at, d, hashlib.sha256(json_bytes(packed)).hexdigest()]) + b'\n')
        if at == 26472:
            cut = dict(state[93])
    return state, peak, trace.hexdigest(), cut


def dual_channel(events, recipes, residuals, target=26472, output=93, coordinate=0):
    children = {(r['old'], r['new']): r for r in recipes['children']}
    endpoints = {(r['role'], r['port']): r for r in recipes['endpoint_adapters']}
    state = [{} for _ in range(712)]
    state[output] = {coordinate: (F(1), F(0))}
    for at in range(target, 13489, -1):
        e = events[at]
        if e[0] == 'scalar':
            g, d = e[1], wire(e[1][1])
            if g[0] == 'clear':
                state[d] = {}
            elif g[0] == 'scale':
                state[d] = scale(state[d], F(g[2], g[3]))
            else:
                require(g[0] == 'add', 'known scalar')
                s = wire(g[2])
                state[s] = plus(state[s], state[d], F(g[3], g[4]))
        elif e[0] == 'climb':
            _, _, d, old, new, rank = e
            require(children[old, new]['rank'] == rank, 'rank binding')
            state[d] = native_adjoint(state[d], children[old, new])
        elif e[0] == 'adapter':
            _, direction, d, _ = e
            if direction == 'old_to_new' and d < 112:
                state[d] = mono(state[d], endpoints['source', d]['left'], True)
            elif direction == 'new_to_old' and 112 <= d < 224:
                state[d] = mono(state[d], endpoints['target', d-112]['left'], False)
            else:
                require(direction in ('old_to_new', 'new_to_old'), 'adapter direction')
        elif e[0] == 'residual_adapter':
            direction, d, a = e[1:4]
            b = e[4] if len(e) == 5 else 1
            require(direction in ('pre', 'post'), 'residual direction')
            key = str(a) if b == 1 else f'{a}:{b}'
            part = 'right' if direction == 'pre' else 'left'
            state[d] = mono(state[d], residuals['recipes'][key][part], False)
        else:
            require(e[0] == 'phase', 'unknown event in local suffix')
    return state[344]


def inner(dual, witness):
    real, imag = F(0), F(0)
    for x, (r, i) in dual.items():
        a, b = F(witness['real'][x], 1 << witness['exponent']), F(witness['imag'][x], 1 << witness['exponent'])
        real += r*a + i*b
        imag += r*b - i*a
    return real, imag


def main():
    events, recipes, residuals = load()
    receipt = json.loads((HERE / 'RESULT.json').read_text())
    witness = receipt['native']['injection']
    require(witness['exponent'] == 0 and len(witness['real']) == len(witness['imag']) == 512,
            'integer witness shape')
    require(all(type(v) is int and v in (-1, 0, 1) for v in witness['real'] + witness['imag']),
            'witness components')
    require(sum(v*v for v in witness['real'] + witness['imag']) == 512, 'witness norm')
    state, peak, trace, cut = full_forward(events, recipes, residuals, witness)
    require(peak == 18, 'independent complete-event guard')
    require(trace == receipt['native']['changed_field_trace_sha256'], 'complete forward trace')
    require(cut == {x: (F(-81921, 262144), F(0)) for x in range(512)}, 'whole attaining vector')
    require({str(i) for i, v in enumerate(state) if v} == set(receipt['nonzero_outputs']),
            'complete endpoint support')
    for i, value in enumerate(state):
        if value:
            require(hashlib.sha256(json_bytes(encoded(value))).hexdigest()
                    == receipt['nonzero_outputs'][str(i)]['sha256'], 'complete endpoint vector')
    print('PASS_QQ16_NATIVE_NOISE_FORWARD guard=18 complete_trace_and_endpoint=matched')
    dual = dual_channel(events, recipes, residuals)
    value = inner(dual, witness)
    require(value == (F(-81921, 262144), F(0)), 'independent native coefficient')
    require((value[0] * (1 << 17)).denominator == 2, 'seventeen-bit rejection')
    for output, expected in ((75, (F(-1, 2), F(0))), (93, (F(1, 2), F(0))),
                             (337, (F(0), F(1, 2)))):
        final_dual = dual_channel(events, recipes, residuals, len(events)-1, output, 0)
        require(inner(final_dual, witness) == expected, 'independent final component')
    print('PASS_QQ16_NATIVE_NOISE_DUAL coefficient=-81921/262144 checks=4 coordinate=0')


if __name__ == '__main__':
    main()
