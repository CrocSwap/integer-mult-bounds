"""Source-bound reversible P104 replay. Tekalign/Codex, Apache-2.0."""
import argparse
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 512
ZERO = [(0, 0)] * N


def need(ok, message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def module(raw, name):
    out = types.ModuleType(name)
    exec(compile(raw, name, 'exec'), out.__dict__)
    return out


def inputs(root=ROOT):
    sources = loads((HERE / 'SOURCES.json').read_bytes())
    data = {}
    for pin in sources['files']:
        if pin['usage'] != 'input':
            continue
        raw = (root / pin['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + pin['path'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source blob: ' + pin['path'])
        data[pin['path']] = raw
    word = loads(data['research/p104-rounded-collector/inputs/WORD.json'])
    native = loads(gzip.decompress(data['research/p104-rounded-collector/inputs/NATIVE.json.gz']))
    recipes = bind(word, native)
    predecessor = module(data['research/p104-rounded-native-child/arithmetic.py'],
                         'authenticated_nearest_reference')
    lift = module((HERE / 'lifting.py').read_bytes(), 'integer_lifting')
    return lift, predecessor, recipes


def bind(word, native):
    """Occurrence binding adapted from PR2999; no native theorem presumed."""
    need(len(word['program']) == 5398, 'word length')
    local = word['program'][2025:2040]
    frame = local[0][2]
    names = ['D31', 'D30', 'D29', 'D28', 'D27']
    need(local[0] == ['zero', 'C', frame] and len(frame) == 8, 'allocation')
    need(local[1:6] == [['add', 'C', s, 1, frame] for s in names], 'gather')
    need(local[7] == ['add', 'Q7', 'C', '1', local[6][3]], 'query update')
    need(local[9:14] == [['add', 'C', s, '-1', frame] for s in reversed(names)], 'ungather')
    need(local[14] == ['erase', 'C', frame], 'erase')
    frames = dict(word['initial_frames'])
    for event in word['program'][:2025]:
        op, reg = event[:2]
        if op == 'transport':
            need(frames[reg] == event[2], 'prefix frame')
            need(event[4] == abs(len(event[2])-len(event[3])), 'prefix rank')
            frames[reg] = event[3]
        elif op == 'add':
            need(reg != event[2] and frames[reg] == frames[event[2]] == event[4], 'prefix ADD')
        elif op == 'sign':
            need(frames[reg] == event[3] and int(event[2]) in (-1, 1), 'prefix sign')
        else:
            raise ValueError('prefix not invertible')
    need(all(frames[s] == frame for s in names) and frames['Q7'] == local[6][3], 'cut frames')
    recipes = []
    for index in (2031, 2033):
        records = [t for t in native['transports'] if index in t['events']]
        need(len(records) == 1, 'unique native occurrence')
        t = records[0]
        need(word['program'][index] == ['transport', 'C', t['old'], t['new'], 7], 'native binding')
        need(t['recipe']['rank'] == 7, 'native rank')
        recipes.append(t['recipe'])
    need(local[6][2:4] == list(reversed(local[8][2:4])), 'return endpoints')
    return recipes


def pair_checks(lift):
    maximum = 0
    nonzero = 0
    for a, b, c, d in itertools.product(range(-4, 5), repeat=4):
        x, y = (a, b), (c, d)
        p, q = lift.pair(x, y)
        need(lift.pair(p, q, True) == (x, y), 'pair inverse')
        u, v = lift.pair(x, y, True)
        need(lift.pair(u, v) == (x, y), 'inverse surjectivity')
        nums = (a-b+c+d, b+a+d-c, a+b+c-d, b-a+d+c)
        parity = ((b-d) % 2) - ((a-c) % 2)
        correction = (parity, -parity, parity, -parity)
        need(tuple(2*t for t in p+q) == tuple(x+y for x, y in zip(nums, correction)),
             'closed parity formula')
        error = sum((v-Fraction(w, 2))**2 for v, w in zip(p+q, nums))
        need(error <= 1, 'pair absolute defect')
        maximum = max(maximum, error)
        nonzero += bool(error)
    need(maximum == 1 and nonzero > 0, 'sharp pair error')
    p, q = lift.pair((1, 0), (0, 0))
    need(lift.pair((2, 0), (0, 0)) != (tuple(2*t for t in p), tuple(2*t for t in q)),
         'nonlinear control')
    return dict(exhaustive_pairs=9**4, nonzero_defects=nonzero, max_squared_error=str(maximum))


def ideal_columns(lift, plans):
    """All ideal complex basis columns; never used to infer nonlinear equality."""
    left, right = plans[0]
    vleft, vright = plans[1]
    coefficients = []
    for delta in range(128):
        a, b = 1, 0
        for bit in range(7):
            sign = -1 if delta >> bit & 1 else 1
            a, b = a-sign*b, b+sign*a
        coefficients.append((a, b))
    h = hashlib.sha256()
    for col in range(N):
        basis = list(ZERO)
        basis[col] = (1, 0)
        exact = lift.exact(basis, 7, left, right)
        x, phase = right[col]
        inner = list(ZERO)
        for delta, coefficient in enumerate(coefficients):
            inner[x ^ delta] = lift.rot(coefficient, phase)
        need(exact == lift.permute(inner, left), 'tensor oracle column')
        back = lift.exact(exact, 7, vleft, vright)
        need(back == lift.shift(basis, 14), 'literal ideal inverse')
        h.update(json.dumps(exact, separators=(',', ':')).encode())
    return dict(columns=N, coordinates=N*N, sha256=h.hexdigest())


def defect(lift, actual, F, source, f, plans):
    left, right = plans
    exact = lift.exact(source, 7, left, right)
    common = max(F, f+7)
    return lift.norm2(lift.difference(lift.shift(actual, common-F),
                                    lift.shift(exact, common-f-7))), common


def check_collector(lift, sources, query, f, b, plans):
    snapshot = json.dumps([sources, query])
    left, right = plans[0]
    result = lift.collector(sources, query, f, b, left, right)
    need(snapshot == json.dumps([sources, query]), 'immutable sources and entrance query')
    F = result['grid']
    need(f <= F <= f+b+8, 'grid metadata bound')
    error, common = defect(lift, result['sent'], F, result['entrance'], f, plans[0])
    need(error <= 112**2 * (1 << (2*(common-F))), 'absolute outbound error')
    need(error * (1 << (2*(b+1+f))) <= lift.norm2(result['entrance']) * (1 << (2*common)),
         'outbound half-relative margin')
    inv_error, inv_common = defect(lift, result['returned'], F, result['sent'], F, plans[1])
    need(Fraction(error, 1 << (2*common)) == Fraction(inv_error, 1 << (2*inv_common)),
         'unitary paired-defect identity')
    need(inv_error * (1 << (2*b)) <= lift.norm2(result['sent']) * (1 << (2*(inv_common-F))),
         'inverse relative error')
    need(lift.difference(result['query'], lift.shift(query, F-f)) == result['sent'], 'query delivery')
    wc = 2*(len(lift.cycles(left))+len(lift.cycles(right)))
    need(result['meter'] == dict(pairs=3584, wrapper_values=2048, field_adds=11,
                                wrapper_cycles=wc, wrapper_swaps=2048+wc), 'literal invoice')
    need(not lift.norm2(result['private']), 'private cleanup')
    return dict(grid=F, fractional_bits_added=F-f,
                error_numerator=error, error_grid=common,
                output_sha256=hashlib.sha256(json.dumps(result['query']).encode()).hexdigest())


def collisions(lift, predecessor, recipes, plans):
    left, right = plans[0]
    summaries = []
    for b in (0, 1, 8, 64, 256):
        for f in (0, 19, 300):
            A = 1 << (b+8)
            low, high = list(ZERO), list(ZERO)
            low[0], high[0] = (A, 0), (A+1, 0)
            low = lift.permute(low, lift.inverse_plan(right))
            high = lift.permute(high, lift.inverse_plan(right))
            old0, oldf0, _ = predecessor.execute(low, f, b, recipes[0])
            old1, oldf1, _ = predecessor.execute(high, f, b, recipes[0])
            need(old0 == old1 and oldf0 == oldf1 == f, 'predecessor collision')
            new0 = lift.collector([low] + [list(ZERO) for _ in range(4)], list(ZERO), f, b, left, right)
            new1 = lift.collector([high] + [list(ZERO) for _ in range(4)], list(ZERO), f, b, left, right)
            need(new0['grid'] == new1['grid'] == f, 'same-grid comparison')
            need(new0['sent'] != new1['sent'], 'lost-bit separation')
            check_collector(lift, [high] + [list(ZERO) for _ in range(4)], list(ZERO), f, b, plans)
            summaries.append(dict(b=b, f=f, separation_norm2=lift.norm2(lift.difference(new0['sent'], new1['sent']))))
    return summaries


def fixtures(lift, plans):
    rng = random.Random(53)
    reports = []
    for width in (2, 17, 130, 400):
        for f, b in ((0, 0), (19, 8), (300, 64)):
            values = [[(rng.randrange(-(1 << width), 1 << width),
                        rng.randrange(-(1 << width), 1 << width)) for _ in range(N)]
                      for _ in range(6)]
            reports.append(check_collector(lift, values[:5], values[5], f, b, plans))
    for exact_cancel in (False, True):
        large = [(rng.randrange(-(1 << 150), 1 << 150), rng.randrange(-99, 100)) for _ in range(N)]
        opposite = [(-a, -b) for a, b in large]
        tiny = list(ZERO)
        if not exact_cancel:
            tiny[53] = (1, -1)
        reports.append(check_collector(lift, [large, opposite, tiny, list(ZERO), list(ZERO)],
                                       large, 19, 32, plans))
    return reports


def run(root=ROOT):
    lift, predecessor, recipes = inputs(root)
    plans = [(lift.plan(r['left']), lift.plan(r['right'])) for r in recipes]
    return dict(status='PASS_P104_REVERSIBLE_LIFTING',
                pair=pair_checks(lift), ideal_native=ideal_columns(lift, plans),
                collisions=collisions(lift, predecessor, recipes, plans),
                collector_fixtures=fixtures(lift, plans),
                invoice=lift.invoice(wrapper_cycles=2*sum(len(lift.cycles(p)) for p in plans[0])),
                scope='Finite paired numerical collector; written all-input lifting proof; no fast recursive tariff or kappa.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as f:
            f.write(payload)
    else:
        expected = loads((HERE / 'RESULT.json').read_bytes())
        need(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True), 'typed result mismatch')
    print(result['status'], 'pairs=6561 columns=512 collectors=29 controls=separate')


if __name__ == '__main__':
    main()
