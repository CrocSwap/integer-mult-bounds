"""Independent sparse transfer replay; no predecessor code is executed.

DLamdata with substantial OpenAI Codex assistance, Apache-2.0.
Terms are (input coordinate, q exponent modulo four, 18 stage exponents).
Coefficients are exact pairs of rational numbers, real then imaginary.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def add_into(out, key, value):
    old = out.get(key, ZERO)
    new = (old[0] + value[0], old[1] + value[1])
    if new == ZERO:
        out.pop(key, None)
    else:
        out[key] = new


def identity(n):
    return [{(i, 0, (0,)*18): ONE} for i in range(n)]


def scale(row, value):
    value = F(value)
    return {k: (value*a, value*b) for k, (a, b) in row.items() if value}


def translate(row, q=0, stages=()):
    inc = tuple(stages.count(i) for i in range(1, 19))
    out = {}
    for (source, power, exponent), value in row.items():
        key = (source, (power+q) % 4, tuple(a+b for a, b in zip(exponent, inc)))
        add_into(out, key, value)
    return out


def lambda_step(row, sign):
    # (1+sign*i)/2 + (1-sign*i)q^2/2, applied linearly.
    require(sign in (-1, 1), 'lambda sign')
    out = {}
    for (source, power, exponent), (a, b) in row.items():
        add_into(out, (source, power, exponent), ((a-sign*b)/2, (b+sign*a)/2))
        add_into(out, (source, (power+2) % 4, exponent), ((a+sign*b)/2, (b-sign*a)/2))
    return out


def replay(events, n=35, capture=None):
    rows = identity(n)
    peak = n
    captured = None
    for index, e in enumerate(events):
        op = e[0]
        if op == 'ADD':
            _, dst, src, c = e
            require(dst != src, 'ADD endpoints differ')
            for key, value in scale(rows[src], c).items():
                add_into(rows[dst], key, value)
        elif op == 'SCALE':
            _, dst, c = e
            require(F(c) != 0, 'invertible SCALE')
            rows[dst] = scale(rows[dst], c)
        elif op == 'SWAP':
            _, a, b = e
            rows[a], rows[b] = rows[b], rows[a]
        elif op == 'Q_POWER':
            _, dst, exponent = e
            require(exponent in (-2, 2), 'ordinary even q translation')
            rows[dst] = translate(rows[dst], q=exponent)
        elif op == 'LAMBDA':
            _, dst, sign = e
            rows[dst] = lambda_step(rows[dst], sign)
        elif op in ('QUERY', 'LOCAL'):
            if op == 'QUERY':
                _, dst, src, exponent = e
                require(exponent in (-1, 1), 'thin query exponent')
            else:
                _, stage, src, dst = e
                require(1 <= stage <= 18, 'native stage range')
                exponent = -1
            require(src != dst, 'query endpoints differ')
            for key, value in translate(rows[src], q=exponent).items():
                add_into(rows[dst], key, value)
            if op == 'LOCAL':
                rows[src] = translate(rows[src], stages=(stage,))
                rows[dst] = translate(rows[dst], stages=(stage,))
        elif op in ('IDLE', 'IDLE_ONE'):
            if op == 'IDLE':
                _, a, b, stages = e
                roles = (a, b)
                require(a != b, 'idle endpoints differ')
            else:
                _, a, stages = e
                roles = (a,)
            require(stages and len(set(stages)) == len(stages) and
                    all(type(s) is int and 1 <= s <= 18 for s in stages), 'idle stage set')
            for r in roles:
                rows[r] = translate(rows[r], stages=stages)
        else:
            raise ValueError('unknown event '+str(op))
        peak = max(peak, sum(len(r) for r in rows))
        if index == capture:
            captured = deepcopy(rows)
    return rows, captured, peak


def expected(word):
    out = []
    for i, d in enumerate(word['diagonal']):
        require(len(d) == 20 and d[1] == 0, 'explicit unused stage-zero coordinate')
        require(all(type(x) is int and x >= 0 for x in d[2:]), 'nonnegative stage powers')
        out.append({(i, d[0] % 4, tuple(d[2:])): ONE})
    return out


def roles_used(e):
    slots = {'ADD': (1, 2), 'SCALE': (1,), 'SWAP': (1, 2), 'Q_POWER': (1,),
             'LAMBDA': (1,), 'QUERY': (1, 2), 'LOCAL': (2, 3),
             'IDLE': (1, 2), 'IDLE_ONE': (1,)}
    return tuple(e[i] for i in slots[e[0]])


def check_word(word, witness, check_cut=True):
    require(word['roles'] == 35 and word['stages'] == 18 and len(word['diagonal']) == 35,
            'fixed caller dimensions')
    require(sorted(e[1] for e in word['events'] if e[0] == 'LOCAL') == list(range(1, 19)),
            'exactly one occurrence of each native stage')
    require(all(type(r) is int and 0 <= r < 35 for e in word['events'] for r in roles_used(e)),
            'role range')
    require(witness['handoff_after'] == 344 and witness['pivot'] == 4 and witness['fresh'] == 34,
            'fixed actual handoff')
    rows, cut, peak = replay(word['events'], capture=344 if check_cut else None)
    require(rows == expected(word), 'full independent caller endpoint')
    if check_cut:
        # Directly inspect the actual 35-input program at the handoff, not dual-pair assertions.
        s = translate(lambda_step(identity(35)[4], 1), q=-1)
        require(cut[4] == s and cut[34] == identity(35)[34], 'isolated pivot and untouched fresh input')
        require(all(not any(key[0] in (4, 34) for key in row)
                    for r, row in enumerate(cut) if r not in (4, 34)), 'isolated pivot and fresh columns')
        require(all(34 not in roles_used(e) for e in word['events'][:345]), 'fresh input absent before handoff')
        require([e for e in word['events'][345:] if 4 in roles_used(e)] == [['LAMBDA', 4, -1]],
                'returned pivot never reused by suffix')
        suffix_stages = word['diagonal'][34][2:]
        require(word['diagonal'][34][0] == 0, 'fresh target has no central factor')
        for r in (20, 21):
            require(word['diagonal'][r][0] % 4 == 3 and word['diagonal'][r][2:] == suffix_stages,
                    'other equal normalized group targets')
    return {'events': len(word['events']), 'coefficients': 35*35,
            'peak_nonzero_terms': peak, 'handoff_after': 344,
            'fresh_stages': [i+1 for i, x in enumerate(word['diagonal'][34][2:]) if x],
            'endpoint_sha256': hashlib.sha256(json.dumps(word['diagonal'], separators=(',', ':')).encode()).hexdigest()}


def rejected(fn):
    try:
        fn()
    except ValueError as exc:
        return str(exc)
    raise ValueError('failure control was accepted')


def run():
    old = json.loads((HERE/'source/pr6545/CONTROLLER.json').read_bytes())
    new = json.loads((HERE/'source/pr6551/CONTROLLER.json').read_bytes())
    w = json.loads((HERE/'source/pr6551/WITNESS.json').read_bytes())
    require(w == json.loads((HERE/'source/pr6545/WITNESS.json').read_bytes()), 'unchanged retirement witness')
    require(old['events'][:345] == new['events'][:345], 'same entire normalized handoff prefix')
    require(new['events'][5:334][-1] == ['QUERY', 20, 21, -1], 'source cut after event 328')
    # Independent opcode controls: q retains order four, not two; lambda is an ordinary scalar polynomial.
    unit = identity(1)[0]
    require(translate(unit, q=2) != unit and translate(unit, q=4) == unit, 'q order-four fixture')
    require(lambda_step(lambda_step(unit, 1), -1) == unit, 'lambda inverse fixture')
    require(lambda_step(lambda_step(unit, 1), 1) == translate(unit, q=2), 'lambda square fixture')
    s = translate(lambda_step(unit, 1), q=-1)
    require(translate(lambda_step(s, 1), q=-1) == unit, 'S involution fixture')
    fixture = [['ADD', 1, 0, '1/2'], ['SCALE', 1, '-2'], ['SCALE', 1, '-1/2'],
               ['ADD', 1, 0, '-1/2'], ['SWAP', 0, 1], ['SWAP', 0, 1]]
    require(replay(fixture, n=2)[0] == identity(2), 'dirty two-role inverse fixture')
    result = {'old': check_word(old, w), 'new': check_word(new, w), 'controls': {}}
    # One direct semantic invalidation per distinct source issue; all checker assertions remain on under -O.
    mutations = {}
    bad = deepcopy(new); del bad['events'][344]; mutations['missing_final_cut_ADD'] = bad
    bad = deepcopy(new); bad['events'][344][-1] = '-1'; mutations['wrong_cut_sign'] = bad
    bad = deepcopy(new); bad['events'].insert(345, ['ADD', 34, 4, '1']); mutations['reuse_retired_output'] = bad
    bad = deepcopy(new); bad['diagonal'][34][0] = -1; mutations['unearned_central_target'] = bad
    for op in ('LOCAL', 'QUERY', 'IDLE', 'IDLE_ONE', 'LAMBDA', 'Q_POWER'):
        bad = deepcopy(new)
        del bad['events'][next(i for i, e in enumerate(bad['events']) if e[0] == op)]
        mutations['missing_'+op] = bad
    for name, bad in mutations.items():
        result['controls'][name] = rejected(lambda bad=bad: check_word(bad, w))
    # A change after the handoff that preserves the full diagonal is still disallowed if it touches the retired field.
    bad = deepcopy(new); bad['events'][345:345] = [['ADD', 34, 4, '1'], ['ADD', 34, 4, '-1']]
    result['controls']['endpoint_preserving_retired_reuse'] = rejected(lambda: check_word(bad, w))
    result['status'] = 'PASS_INDEPENDENT_RETIREMENT_CALLER'
    return result


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
