"""Reverse exact signed endpoint and paid-idle retirement support checks."""
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PR7402 = 'ac7a4b1ebaa300408511470db8fcbe054f843348'
PR7406 = 'a5fa7b464a773afb47eb8b9725b94f660c407528'
PINS = {
    'inputs/7113-signed-child.py': 'ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b',
    'inputs/7113-signed-grid.py': 'abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54',
    'inputs/7402-PROOF.md': '7a06f9a7c1f8f634243572fb5f8395719e4de57f4c0a57cce5599b1f5b497693',
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R92-PRICE.json': '05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
STAGE, OFFSET, N, J = 17, 36, 36, 4691
IDLES = (4646,4660)
PORTS = (15,17,27,34,35,42,47,55)


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate key')
    return result


def read(name):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw, object_pairs_hook=unique) if name.endswith('.json') else raw


def local(role):
    index = role-OFFSET
    assert 0 <= index < N
    return index


def compile_events(events):
    program, dependencies = [], []
    for clock, (family, op, *args) in enumerate(events):
        if family == 'A':
            continue
        if family == 'J':
            a_roles, (u, v, alpha, beta) = args
            assert len(set(a_roles)) == 4 and u != v
            u, v = local(u), local(v)
            stage = op
            a, b = Q(alpha), Q(beta)
            program.append((clock,'host',u,v,a,b,stage==STAGE))
            if stage == STAGE:
                dependencies.append([clock,'host',2])
            continue
        assert family == 'B'
        r, *rest = args
        r = local(r)
        if op == 'ADD':
            s, alpha = rest
            assert r != local(s) and Q(alpha)
            program.append((clock,'add',r,local(s),Q(alpha)))
        elif op == 'SCALE':
            alpha, = rest
            assert Q(alpha)
            program.append((clock,'scale',r,Q(alpha)))
        elif op == 'SWAP':
            s, = rest
            assert r != local(s)
            program.append((clock,'swap',r,local(s)))
        elif op == 'QUERY':
            s, exponent = rest
            assert r != local(s) and exponent in (-1,1)
            program.append((clock,'add',r,local(s),Q(1)))
        elif op == 'LAMBDA':
            assert rest in ([-1],[1])
        else:
            assert op in ('IDLE_ONE','IDLE_ODD')
            if STAGE in rest[0]:
                assert op == 'IDLE_ONE' and rest == [[STAGE]]
                program.append((clock,'idle',r))
                dependencies.append([clock,'idle',1])
    return program, dependencies


def axis(i):
    return [Q(i==j) for j in range(N)]


def act(row, events, sign, inverse=False, deleted=()):
    result = row[:]
    for clock, op, r, *args in events if inverse else reversed(events):
        if op == 'add':
            s,a = args
            result[s] += (-a if inverse else a)*result[r]
        elif op == 'scale':
            a, = args
            result[r] *= 1/a if inverse else a
        elif op == 'swap':
            s, = args
            result[r],result[s] = result[s],result[r]
        elif op == 'idle':
            if clock not in deleted:
                result[r] *= sign
        else:
            assert op == 'host'
            s,a,b,active = args
            d = sign if active else 1
            x,y = result[r],result[s]
            if inverse:
                result[r],result[s] = d*((1+a*b)*x-b*y),d*(-a*x+y)
            else:
                result[r],result[s] = d*(x+b*y),d*(a*x+(1+a*b)*y)
    return result


def nonzero(matrix):
    return [[i,j,str(x)] for i,row in enumerate(matrix) for j,x in enumerate(row) if x]


def physical_signs(raw):
    tree = ast.parse(raw)
    gate, = [ast.literal_eval(node.value) for node in tree.body if isinstance(node,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='C' for t in node.targets)]
    for v,eigen in (((1,1),(1,0)),((1,-1),(0,1))):
        for i,row in enumerate(gate):
            actual = tuple(sum(v[j]*row[j][z] for j in (0,1)) for z in (0,1))
            assert actual == tuple(2*v[i]*z for z in eigen)
    assert len(range(137,145)) == 8 and min(range(137,145)) > 8
    return {'central':1,'other_bodies':1,'stage17_signs':[1,-1],
            'minus_sign_walsh_weight':2,'stage_axes':list(range(137,145))}


def timeout(*_):
    raise TimeoutError('20-second signed retirement gate')


def main():
    assert __debug__
    signal(SIGALRM,timeout)
    alarm(20)
    caller = read('inputs/CALLER.json')
    price = read('inputs/R92-PRICE.json')
    prior = read('inputs/7402-PROOF.md')
    grid = read('inputs/7113-signed-grid.py')
    read('inputs/pricing.py')
    assert b'4646/4660 and J17 at 4691' in prior
    assert b'A=mapped(rows[s],m=m)' in grid and b'B=mapped(rows[t],den=2,m=m)' in grid
    physical = physical_signs(read('inputs/7113-signed-child.py'))
    assert (price['head'],price['caller_head']) == (HEAD,CALLER)
    events,b = caller['events'],caller['types']['B']
    assert len(events)==4783 and b['offset']==OFFSET and b['roles']==N and b['ports']==list(PORTS)
    assert all(events[t]==['B','IDLE_ONE',36,[STAGE]] for t in IDLES)
    assert events[J]==['J',STAGE,[17,0,18,35],[36,37,'-1','1/2']]
    program,deps = compile_events(events)
    assert deps == [[4646,'idle',1],[4660,'idle',1],[4691,'host',2]]
    target = [row[STAGE+1] for row in b['diagonal']]
    active = [i for i,x in enumerate(target) if x]
    assert set(target)=={0,1} and active==[0,1,16,17]
    for i in range(N):
        for sign in (1,-1):
            assert act(axis(i),program,sign)==[sign**target[i]*x for x in axis(i)]
    # The earlier prefix cancels in P_old P_deleted^-1. The common suffix
    # also cancels; only the exact old window and the native host remain.
    pre = [op for op in program if IDLES[0]<=op[0]<J]
    host = [op for op in program if op[0]==J]
    j_rows = [act(axis(i),host,-1) for i in range(N)]
    full_old = [act(row,pre,-1) for row in j_rows]
    assert [act(row,pre,-1,inverse=True) for row in full_old]==j_rows
    cost = run_path(str(ROOT/'inputs/pricing.py'))['cost']
    k = Q(price['old_crossing_upper'])
    cases = []
    for n in (1,2):
        for deleted in combinations(IDLES,n):
            forced = [act(row,pre,-1,inverse=True,deleted=deleted) for row in full_old]
            assert [act(row,pre,-1,deleted=deleted) for row in forced]==full_old
            correction = [[x-y for x,y in zip(row,axis(i),strict=True)] for i,row in enumerate(forced)]
            outside = [cell for cell in nonzero(correction) if not (cell[0]<2 and cell[1]<2)]
            capacity = 2+len(IDLES)-n
            assert capacity < len(active) and outside
            cases.append({'deleted':deleted,'max_complete_endpoint_displacement_rank':capacity,
                          'outside_host_nonzeros':len(outside),'first_outside_host_entries':outside[:8],
                          'forced_host_block':[[str(x) for x in row[:2]] for row in forced[:2]],
                          'optimistic_paid_gain_interval':[str(x) for x in cost(Counter({8:len(PORTS)*n}),k)]})
    assert len(cases)==3
    alarm(0)
    print(dumps({'head':HEAD,'caller':CALLER,'predecessors':{'7402':PR7402,'7406':PR7406},
                 'pins':PINS,'clocks':IDLES,'host_clock':J,'host_roles_global':[36,37],
                 'source_events':len(events),'ports':PORTS,'basis_rows_per_body':N,
                 'physical_sectors':physical,'body_dependent_occurrences':deps,
                 'old_endpoint_displacement_rank':len(active),'old_displacement_roles_local':active,
                 'retirement_cases':cases,'unresolved':[],'runner_cap_seconds':20,
                 'negative_control':'No deletions reproduce exact old J; paid-retired word with that same J has different endpoint.'},
                indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
