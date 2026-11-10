"""Check the exact caller error contract and an attaining lower witness.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    data = (HERE / 'inputs/CONTROLLER.json').read_bytes()
    rows = json.loads((HERE / 'SOURCES.json').read_text())['files']
    pin = next(r for r in rows if r['usage'] == 'input')
    need(sha256(data).hexdigest() == pin['sha256'], 'Caller source hash')
    return json.loads(data)


def lower_witness(word, output):
    """Use real scalar recurrences at Q=D_j=I, with no normalizer errors."""
    weights = [F(int(i == output)) for i in range(word['roles'])]
    injections = {}
    for t in range(len(word['events']) - 1, -1, -1):
        event = word['events'][t]
        op = event[0]
        if op in ('ADD', 'SCALE', 'QUERY'):
            roles = [event[1]]
        elif op == 'LOCAL':
            roles = event[2:4]
        elif op == 'IDLE':
            roles = event[1:3]
        elif op == 'IDLE_ONE':
            roles = [event[1]]
        else:
            roles = []
        injections[t] = [(r, (weights[r] > 0) - (weights[r] < 0)) for r in roles]
        if op == 'ADD':
            weights[event[2]] += F(event[3]) * weights[event[1]]
        elif op == 'SCALE':
            weights[event[1]] *= F(event[2])
        elif op == 'SWAP':
            a, b = event[1:]
            weights[a], weights[b] = weights[b], weights[a]
        elif op == 'QUERY':
            weights[event[2]] += weights[event[1]]
        elif op == 'LOCAL':
            weights[event[2]] += weights[event[3]]
    state = [F(0)] * word['roles']
    for t, event in enumerate(word['events']):
        op = event[0]
        if op == 'ADD':
            state[event[1]] += F(event[3]) * state[event[2]]
        elif op == 'SCALE':
            state[event[1]] *= F(event[2])
        elif op == 'SWAP':
            a, b = event[1:]
            state[a], state[b] = state[b], state[a]
        elif op == 'QUERY':
            state[event[1]] += state[event[2]]
        elif op == 'LOCAL':
            state[event[3]] += state[event[2]]
        for role, error in injections[t]:
            state[role] += error
    return state[output], injections


def normalizer():
    """Check all real basis columns and each local error column exactly."""
    # Gaussian pairs keep every operation rational.
    def add(a, b):
        return a[0]+b[0], a[1]+b[1]
    def mul(a, b):
        return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]
    def circuit(x, y, sign, errors):
        minus_i = (F(0), -sign)
        x = add(add(x, mul(minus_i, y)), errors[0])
        x = add(mul((F(1, 2), F(sign, 2)), x), errors[1])
        y = add(mul((F(1), F(sign)), y), errors[2])
        y = add(add(y, mul(minus_i, x)), errors[3])
        return x, y
    zero = (F(0), F(0))
    columns = []
    for sign in (-1, 1):
        for j in range(4):
            z = [F(int(i == j)) for i in range(4)]
            x, y = (z[0], z[1]), (z[2], z[3])
            got = circuit(x, y, sign, [zero]*4)
            a, b = (F(1, 2), F(sign, 2)), (F(1, 2), F(-sign, 2))
            need(got == (add(mul(a,x),mul(b,y)), add(mul(b,x),mul(a,y))),
                 'Literal normalizer basis column')
        norms = []
        for j in range(4):
            errors = [zero]*4
            errors[j] = (F(1), F(0))
            xy = circuit(zero, zero, sign, errors)
            norms.append(sum(c*c for v in xy for c in v))
        need(norms == [1, 2, 1, 1], 'Four exact error-column squared norms')
        columns.append(list(map(int, norms)))
    need(F(3, 2)**2 > 2, 'The rational square-root majorant is outward')
    return columns


def main():
    word = authenticate()
    from bounds import calculate, identity, step, bound, N
    need((word['roles'], word['stages'], len(word['events'])) == (34,18,570),
         'Complete caller dimensions')
    result = calculate()
    need(result['prefix'] == ['18',279,0], 'Exact prefix envelope')
    need(result['common_error'] == '943/2', 'Complete uniform error envelope')
    maxima = {k: str(max(map(F, values))) for k, values in result['errors'].items()}
    need(maxima == {'scalar':'795/2','local':'28','query':'18','idle':'28'},
         'Separate primitive error contracts')
    witnesses = [lower_witness(word, i)[0] for i in range(34)]
    lower, output = max((v,i) for i,v in enumerate(witnesses))
    need(lower == 307 and 2**8 < lower < F(result['common_error']) < 2**9,
         'Nine guard bits suffice and eight fail in this contract')
    # A column test distinguishes the transpose from the forward operation.
    for trans in (False, True):
        m = identity()
        step(m, ['ADD',0,1,'3/2'], 0, trans)
        a,b = (1,0) if trans else (0,1)
        need(bound(m)[a][b] == F(3,2) and bound(m)[b][a] == 0,
             'Forward and suffix orientation')
    for q in range(4):
        m = identity()
        for event in word['events']:
            step(m, event, q)
        for i in range(N):
            for j in range(N):
                cell = m[i][j]
                if i != j:
                    need(not cell, 'Zero off-diagonal endpoint')
                else:
                    target = word['diagonal'][i]
                    from bounds import unit
                    need(cell == {tuple(target[2:]): unit(q*target[0])},
                         'Exact independent-stage endpoint')
    result.update(status='PASS_MIXED_CALLER_ERROR_BUDGET', maxima=maxima,
                  lower_witness={'amplification':str(lower),'output':output,
                                 'Q':'I','stages':'I','normalizer_error':0},
                  normalizer_error_squared_norms=normalizer(),
                  sufficient_guard_bits=9, insufficient_guard_bits=8,
                  boundary_signal_bound='18*M+8487*epsilon',
                  scope='Abstract unitary-stage error contract; no native error or new kappa.')
    encoded = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(encoded)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'Exact result receipt')
    print(encoded,end='')


if __name__ == '__main__':
    main()
