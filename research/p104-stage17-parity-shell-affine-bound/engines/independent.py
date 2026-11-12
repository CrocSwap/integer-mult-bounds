"""Literal signed Gaussian replay and GF(2) affine-rank test for two return lanes."""
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PREDECESSOR = 'a5fa7b464a773afb47eb8b9725b94f660c407528'
PINS = {
    'inputs/PROJECTOR.json': 'c36cb8d3fae7bccd15566c2f83f2d2bd8abeeb334381cbf3212d5d9b3d965c35',
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
    'inputs/R173-INDEPENDENT.json': 'd53dfc746467daff3bddf25fd7d2ce11d2d984f0bd71c14d18277c6a0dad7b32',
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
}
CLOCKS, ROLES, M = (4646, 4660), (36, 37, 52, 53), 8


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate JSON key')
    return result


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw, object_pairs_hook=unique) if name.endswith('.json') else raw


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col, strict=True))
             for col in zip(*b, strict=True)] for row in a]


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    m = [row + unit for row, unit in zip(a, identity(n), strict=True)]
    for j in range(n):
        i = next(i for i in range(j, n) if m[i][j])
        m[j], m[i] = m[i], m[j]
        scale = m[j][j]
        m[j] = [x/scale for x in m[j]]
        for i in range(n):
            if i != j:
                scale = m[i][j]
                m[i] = [x-scale*y for x, y in zip(m[i], m[j], strict=True)]
    assert [row[:n] for row in m] == identity(n)
    return [row[n:] for row in m]


def physical_projector(caller, old):
    tape = caller['events']
    assert len(tape) == 4783
    assert all(tape[clock] == ['B','IDLE_ONE',36,[17]] for clock in CLOCKS)
    m = identity(4)
    for kind, op, dest, *args in tape[CLOCKS[0]+1:CLOCKS[1]]:
        assert kind == 'B' and op in ('ADD','SCALE')
        r = ROLES.index(dest)
        if op == 'ADD':
            src, value = args
            m[r] = [x+Q(value)*y for x, y in zip(m[r], m[ROLES.index(src)], strict=True)]
        else:
            m[r] = [Q(args[0])*x for x in m[r]]
    mi = inverse(m)
    assert m[0][0] == mi[0][0] == 0 and mm(m,mi) == identity(4)
    e = [[Q(i == j == 0) for j in range(4)] for i in range(4)]
    f = mm(mm(mi,e),m)
    assert not any(x for a in (mm(e,f),mm(f,e)) for row in a for x in row)
    p = [[x+y for x, y in zip(a, b, strict=True)] for a, b in zip(e, f, strict=True)]
    assert mm(p,p) == p and sum(p[i][i] for i in range(4)) == 2
    assert p == [[Q(x) for x in row] for row in old['projector']]
    return p


def mul(a, b):
    x,y = a
    z,w = b
    return x*z-y*w, x*w+y*z


def local_modes(gate, adjoint):
    entries = [[(gate[j][i][0], -gate[j][i][1]) if adjoint else gate[i][j]
                for j in range(2)] for i in range(2)]
    modes = []
    for d in (0,1):
        v = (1,(-1)**d)
        image = [tuple(sum(v[j]*entries[i][j][k] for j in range(2)) for k in range(2))
                 for i in range(2)]
        real, imag = image[0]
        assert real % 2 == imag % 2 == 0
        assert image[1] == (v[1]*real,v[1]*imag)
        modes.append((real//2,imag//2))
    for i in range(2):
        for j in range(2):
            terms = [mul(entries[i][k],entries[k][j]) for k in range(2)]
            assert tuple(map(sum,zip(*terms))) == (4*(i != j),0)
    return modes


def residual(u, m, modes, adjoint):
    d = (1,0)
    for j in range(m):
        d = mul(d,modes[(u>>j)&1])
    # Exact Walsh character of the all-ones translation.
    x = (-1)**(u & ((1<<m)-1)).bit_count()
    e = ((1+x)//2, (-1 if adjoint else 1)*(1-x)//2)
    return (d[0]-e[0],d[1]-e[1])


def affine_hull(points):
    origin = points[0]
    pivots = {}
    for point in points[1:]:
        reduced = point ^ origin
        while reduced:
            pivot = reduced.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = (reduced,point)
                break
            reduced ^= pivots[pivot][0]
    return origin, pivots


def timeout(*_):
    raise TimeoutError('20-second exact signed affine cap')


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(20)
    caller = read('inputs/CALLER.json')
    old = read('inputs/R173-INDEPENDENT.json')
    projectors = read('inputs/PROJECTOR.json')
    assert (old['benchmark'],old['caller'],old['clocks']) == (HEAD,CALLER,list(CLOCKS))
    assert (projectors['head'],projectors['caller'],projectors['inclusive_window']) == (HEAD,CALLER,list(CLOCKS))
    assert projectors['rank'] == 2 and old['physical_stage_axes'] == list(range(137,145))
    p = physical_projector(caller,old)
    tree = ast.parse(read('inputs/7113-signed-child.py'))
    gate, = [ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id == 'C' for t in node.targets)]
    forward, adjoint = local_modes(gate,False), local_modes(gate,True)
    addresses, phases = [], [Counter(),Counter()]
    for lane in (0,1):
        for u in range(1<<M):
            r, s = residual(u,M,forward,False), residual(u,M,adjoint,True)
            assert s == (r[0],-r[1])
            assert r == ((0,0),(0,0),(-2,0),(0,-2))[u.bit_count()%4]
            phases[lane][str(r)] += 1
            if r != (0,0):
                addresses.append((lane<<M)|u)
    origin, pivots = affine_hull(addresses)
    assert len(addresses) == 240 and len(pivots) == 9
    assert {i for i in pivots} == set(range(M+1))
    # Negative control: discard a dirty lane and the affine rank falls.
    assert len(affine_hull([a for a in addresses if a < 1<<M])[1]) == 8
    # The same witness works at each m=8f >= 8. A weight-2 word excluding j
    # and its weight-3 extension differ by e_j; opposite lanes give the last bit.
    direction_witnesses = []
    for j in range(M):
        a,b = [i for i in range(M) if i != j][:2]
        low = (1<<a)|(1<<b)
        high = low|(1<<j)
        assert low in addresses and high in addresses and low^high == 1<<j
        direction_witnesses.append([j,low,high])
    assert 3 in addresses and (3|(1<<M)) in addresses
    direction_witnesses.append([M,3,3|(1<<M)])
    affordable = Q(old['rank16_affordability_upper'])
    assert affordable < Q('1.003') < 2
    alarm(0)
    print(dumps({'head':HEAD,'caller':CALLER,'pr7406':PREDECESSOR,'pins':PINS,'clocks':CLOCKS,
                 'selected_axes':old['physical_stage_axes'],'projector':[[str(x) for x in r] for r in p],
                 'case_count':512,'forward_residual_multiplicities_by_lane':phases,
                 'residual_modes_per_lane':120,'residual_modes_total':240,
                 'residual_volume_old_lane':'15/16','affine_origin':origin,'affine_pivots':pivots,
                 'unit_direction_witnesses':direction_witnesses,'affine_rank':len(pivots),
                 'affine_chart_old_lane_volume':'2','affordability_upper':str(affordable),
                 'all_widths':'m=8f, integer f>=1; affine rank m+1; chart volume 2 old lanes',
                 'discard_one_lane_control_rank':8,'runner_cap_seconds':20,'build_admitted':False},
                indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
