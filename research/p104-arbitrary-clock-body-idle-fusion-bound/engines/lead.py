"""One shared legal body specialization for every disjoint Type A idle pair."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'engines/forward.py': '75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439',
    'engines/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
CROSSING = (F('0.00364665195644044790699554028334161'), F('0.00364665195644044790699554028334162'))


def add(a, b, c):
    return [x + c*y for x, y in zip(a, b, strict=True)]


def minus(stage_set):
    return len({8, 9}.intersection(stage_set)) % 2


def expanded(tape, omitted):
    for clock, e in enumerate(tape):
        if clock in omitted:
            continue
        yield e
        if e[0] == 'J' and e[1] in (8, 9):
            for role in e[2]:
                yield ['A', 'SCALE', role, '-1']
        elif e[:2] == ['A', 'IDLE_ONE'] and minus(e[3]):
            yield ['A', 'SCALE', e[2], '-1']


def collect(tape, unit):
    rows = [unit(i) for i in range(36)]
    inverse = [unit(i) for i in range(36)]
    idles = []

    def shear(d, s, value):
        rows[d] = add(rows[d], rows[s], value)
        inverse[s] = add(inverse[s], inverse[d], -value)

    def scale(d, value):
        rows[d] = [x*value for x in rows[d]]
        inverse[d] = [x/value for x in inverse[d]]

    for clock, e in enumerate(tape):
        if e[0] == 'B':
            continue
        if e[0] == 'J':
            a, b, c, d = e[2]
            shear(b, a, F(1))
            shear(c, d, F(-1))
            if e[1] in (8, 9):
                for role in e[2]:
                    scale(role, F(-1))
            continue
        assert e[0] == 'A'
        _, op, d, *args = e
        if op == 'ADD':
            shear(d, args[0], F(args[1]))
        elif op == 'QUERY':
            assert args[1] == -1
            shear(d, args[0], F(1))
        elif op == 'SCALE':
            scale(d, F(args[0]))
        elif op == 'SWAP':
            s, = args
            rows[d], rows[s] = rows[s], rows[d]
            inverse[d], inverse[s] = inverse[s], inverse[d]
        elif op == 'IDLE_ONE':
            assert minus(args[0]) == 1
            u, v = inverse[d], rows[d]
            assert sum(x*y for x,y in zip(u,v,strict=True)) == 1
            idles.append((clock, d, args[0], u, v))
            scale(d, F(-1))
        else:
            assert op == 'LAMBDA' and args[0] in (-1, 1)
    return idles, rows, inverse


def stop(*_):
    raise TimeoutError('30-second 224-pair body gate cap')


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(30)
    for name, digest in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest
    source = run_path(str(ROOT/'engines/forward.py'))
    h = run_path(str(HERE/'pricing.py'))['power_bounds']
    unit, apply = source['unit'], source['apply']
    caller = loads((ROOT/'inputs/CALLER.json').read_bytes())
    tape = caller['events']
    a = caller['types']['A']
    assert len(a['ports']) == 96 and a['alpha2'] == '-1'
    idles, end, inv = collect(tape, unit)
    assert len(idles) == 30
    for i, row in enumerate(a['diagonal']):
        expected = [x*(-1)**(row[9]+row[10]) for x in unit(i)]
        assert end[i] == inv[i] == expected
    k0, k1 = CROSSING

    def price(n, m):
        x, y = 8*n, 8*m
        return (96*(h(x,k1)[0]+h(y,k1)[0]-h(x+y,k0)[1]),
                96*(h(x,k0)[1]+h(y,k0)[1]-h(x+y,k1)[0]))

    records = []
    for a0, a1 in combinations(idles, 2):
        i, r, m, u, v = a0
        j, s, n, x, y = a1
        if not set(m).isdisjoint(n):
            continue
        assert minus(m+n) == 0
        lower, upper = price(len(m), len(n))
        assert 0 < lower < upper < 96
        witness = next(([a,b,str(u[a]*v[b]),str(x[a]*y[b])]
                        for a in range(36) for b in range(36) if u[a]*v[b] != x[a]*y[b]), None)
        records.append({'clocks':[i,j], 'roles':[r,s], 'masks':[m,n], 'quote':[str(lower),str(upper)],
                        'projector_inequality':witness})
    assert len(records) == 224
    best = min(records,key=lambda v:(-F(v['quote'][1]),v['clocks']))
    early = sorted(len(mask) for _,_,mask,*_ in idles if 8 in mask)
    late = sorted(len(mask) for _,_,mask,*_ in idles if 9 in mask)[-len(early):]
    matching_upper = sum(price(i,j)[1] for i,j in zip(early,late,strict=True))
    literal = list(expanded(tape, set()))
    changed = list(expanded(tape, set(best['clocks'])))
    witness = next(([j,i,str(x),str(y)] for i in range(36)
                    for j,(x,y) in enumerate(zip(apply(literal,unit(i),1),apply(changed,unit(i),1),strict=True))
                    if x != y), None)
    assert bool(witness) == bool(best['projector_inequality'])
    alarm(0)
    print(dumps({'pins':PINS, 'crossing':list(map(str,CROSSING)), 'profile':{'q':1,'negative_body_stages':[8,9]},
                 'pairs':records, 'case_cap':224, 'runner_cap_seconds':30, 'best':best,
                 'disjoint_matching_upper':str(matching_upper), 'max_pairs':len(early),
                 'literal_best_difference':witness,
                 'survivors':[v['clocks'] for v in records if v['projector_inequality'] is None]},
                indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
