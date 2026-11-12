"""Independent reverse component inventory and orthogonal-dual direct flow."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    'endpoint_replay.py': '24d63caf9e647840f47675fecf775803c509f5fbc7ae6fc6b5d450782ec1d81d',
    'cut_flow.py': 'a16c67f11d216d0a7d7f4caf0b994cc0a1dcbc01d667ed0924691f72f0959cdb',
    'reverse_inventory.py': 'ac01889cd8e917b5c3f93dcefaa19c159efc18bcdd6973b94b481f08185d0127',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
SCALE = 10**52


@cache
def orthogonal(space):
    # Recover a basis from the actual reverse inventory span, rather than
    # reusing the forward word's displayed basis or chart assignment.
    basis, span = [], {0}
    for point in sorted(space):
        if point not in span:
            basis.append(point)
            span |= {point ^ x for x in span}
    assert span == space
    answer = {v for v in range(512) if not any((v & x).bit_count() & 1 for x in basis)}
    assert len(space) * len(answer) == 512
    return answer


def controls():
    W = frozenset({0, 1, 2, 3})
    dual = orthogonal(W)
    v = 1
    assert v not in dual
    section = frozenset(x for x in W if (x & v).bit_count() % 2 == 0)
    assert len(section) * 2 == len(W)
    assert orthogonal(section) == dual | {x ^ v for x in dual}
    lower, upper = frozenset({0, 1}), W
    assert orthogonal(upper) < orthogonal(lower)


def stop(*_):
    raise TimeoutError('60-second orthogonal-dual flow cap')


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(60)
    for path, digest in PINS.items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest
    raw = decompress((ROOT / 'inputs/7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw)
    assert len(word['program']) == 76466
    base = run_path(str(ROOT / 'endpoint_replay.py'))
    rev = run_path(str(ROOT / 'reverse_inventory.py'))
    flow = run_path(str(ROOT / 'cut_flow.py'))
    primal, allowed, original_edges = base['inventory'](word, rev)
    paid = sum(e[-1] for e in original_edges)
    productive = len(original_edges)-paid
    assert (len(primal), len(allowed), paid, productive) == (1517, 553, 2573, 193)
    dual = [orthogonal(frozenset(space)) for space in primal]
    edges = [(high, low, gap, paid) for low, high, gap, paid in original_edges]
    assert all(dual[a] < dual[b] and len(dual[b]) == (len(dual[a]) << d) for a,b,d,_ in edges)
    controls()
    push, arc = flow['push_until_cut'], flow['arc']
    base['control'](push, arc)
    tariff = run_path(str(ROOT / 'inputs/pricing.py'))['power_bounds']
    k0 = Q('0.00364665195644044790699554028334161')
    k1 = Q('0.00364665195644044790699554028334162')
    h = [(Q(0), Q(0))] + [(tariff(r, k1)[0], tariff(r, k0)[1]) for r in range(1,10)]
    bounds = [(0,0)] + [(floor(SCALE*(h[r][0]-h[r-1][1])),
                           ceil(SCALE*(h[r][1]-h[r-1][0]))) for r in range(1,10)]
    assert all(0 < a <= b for a,b in bounds[1:])
    center = [a+b for a,b in bounds]
    radius = sum(b-a for a,b in bounds)
    assert 0 < radius < min(center[1:])
    vertices = []
    for rank in range(1,10):
        for sign in (-1,1):
            p = center.copy()
            p[rank] += sign*radius
            vertices.append(p)
    rows, active, partial = [], [], None
    capped = False
    try:
        for v in range(1,512):
            frozen = base['compile_edges'](v, dual, allowed, edges)
            active.append([v,frozen[0]])
            partial = [v, []]
            for price in vertices:
                partial[1].append(base['flow_value'](frozen,price,price,push,arc,cancel=True))
            rows.append(partial)
            partial = None
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    print(dumps(dict(head=base['HEAD'], caller=base['CALLER'], pins=PINS, groups=len(dual),
                     eligible_groups=len(allowed), paid_edges=paid, target_edges=productive,
                     distinct_dual_spaces=orthogonal.cache_info().misses, scale=2*SCALE,
                     box=bounds[1:], center=center[1:], radius=radius,
                     vectors=len(rows), vertices=len(vertices), active=active, cap_seconds=60,
                     rows=rows, partial_row=partial, capped=capped,
                     max=max((max(v) for _,v in rows),default=None)),
                indent=2, sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
