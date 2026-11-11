"""Independent exact binary-scope audit of signed invoice and flow/cut equality."""
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction as F
from hashlib import sha256
from itertools import pairwise
from pathlib import Path
from time import monotonic
import gzip
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'source'
GRID = 10**48
TARGET = F(10018846261809, 2500000000000000)
HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
INPUTS = {
    'inputs/WORD.json.gz': '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'inputs/EARLY-RESULT.json': '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'powers.py': 'c0c460b464d7c836fb887010b57119be322aae686736b86820aae3544d380bee',
}


def source(path):
    data = (SOURCE / path).read_bytes()
    assert sha256(data).hexdigest() == INPUTS[path]
    return data


def basis(vectors):
    pivot = {}
    for v in vectors:
        while v.bit_length() in pivot:
            v ^= pivot[v.bit_length()]
        assert v
        pivot[v.bit_length()] = v
    return pivot


def inside(vectors, pivot):
    for v in vectors:
        while v:
            if v.bit_length() not in pivot:
                return False
            v ^= pivot[v.bit_length()]
    return True


def log_scaled(value):
    z = (value - 1) / (value + 1)
    term = z
    q = F(0)
    for j in range(0, 160, 2):
        q += term / (j+1)
        term *= z*z
    return 2*q, 2*(q+term/(161*(1-z*z)))


def exp_minus(value, steps):
    term = F(1)
    total = F(1)
    for j in range(1, steps+1):
        term *= -value / j
        total += term
    return total


def verify_power(rank, value):
    if not rank:
        assert value == (0, 0)
        return
    exponent = rank.bit_length()-1
    unit_lo, unit_hi = log_scaled(F(rank, 1 << exponent))
    two_lo, two_hi = log_scaled(F(2))
    xlo = TARGET*(unit_lo+exponent*two_lo)
    xhi = TARGET*(unit_hi+exponent*two_hi)
    assert 0 <= xlo <= xhi < 1
    # Round the exponents outward before Taylor, keeping intermediate
    # numerators small without losing the finer-than-grid audit.
    fine = 10**64
    xlo = F((xlo*fine).__floor__(), fine)
    xhi = F((xhi*fine).__ceil__(), fine)
    low = GRID*rank*exp_minus(xhi, 49)
    high = GRID*rank*exp_minus(xlo, 50)
    assert value[0] <= low <= high <= value[1], rank


def read_model():
    word = json.loads(gzip.decompress(source('inputs/WORD.json.gz')))
    early = json.loads(source('inputs/EARLY-RESULT.json'))
    caller = json.loads(source('inputs/CALLER.json'))
    source('powers.py')
    primary = runpy.run_path(str(SOURCE/'powers.py'))
    assert primary['GRID'] == GRID and primary['TARGET'] == TARGET
    initial, final = word['initial'], word['final']
    n = word['public']
    program = word['program']
    frame = word['frames']
    ranks = [len(v) for v in frame]
    bases = [basis(v) for v in frame]
    subset = {}
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2'] + word['hosted']['Y2'])
    assert len(main) == 400

    def nested(a, b):
        key = a,b
        if key not in subset:
            subset[key] = ranks[a] < ranks[b] and inside(frame[a], bases[b])
        return subset[key]

    def rank(a, b, owned):
        if a == b:
            return 0
        if nested(a, b) or owned and nested(b, a):
            return abs(ranks[a]-ranks[b])
        return None

    chart = {(-1, r): f for r, f in enumerate(initial)}
    current = initial + [None]*word['owned_fields']
    contacts = [[(-1, r)] for r in range(n)] + [[] for _ in range(word['owned_fields'])]
    chains = []
    paid = Counter()
    for t, row in enumerate(program):
        op, r = row[:2]
        if op == 'MOVE':
            a, b, owned = row[2:]
            assert current[r] == a and owned == (r >= n)
            rr = rank(a, b, owned)
            assert rr
            paid[rr] += 1
            current[r] = b
            continue
        f = row[-1]
        key = (t, 0)
        chart[key] = f
        if op == 'INIT':
            assert r >= n and not contacts[r] and current[r] is None
            current[r] = f
        roles = {r, row[2]} if op in ('ADD', 'COPY') else {r}
        for role in roles:
            assert current[role] == f
            contacts[role].append(key)
        if op == 'CLEAR':
            assert r >= n and contacts[r]
            chains.append((r, contacts[r]))
            contacts[r] = []
            current[r] = None
    assert current == final + [None]*word['owned_fields'] and not any(contacts[n:])
    assert len(chains) == 70
    movable = {k for k in chart if k[0] != -1}
    terminal = {}
    for r, f in enumerate(final):
        key = (len(program), r)
        chart[key] = f
        contacts[r].append(key)
        chains.append((r, contacts[r]))
        if r not in main:
            terminal[key] = initial[r]
            movable.add(key)
    edges = [(a,b,r >= n) for r, seq in chains for a,b in pairwise(seq)]
    native_paid = Counter(rr for a,b,owned in edges if (rr := rank(chart[a],chart[b],owned)))
    assert native_paid == paid and sum(paid.values()) == 6280 and len(edges) == 137891
    assert len(chart) == 73165 and len(terminal) == 1101
    copies = sum(e[0] == 'J' for e in caller['events'])
    assert copies == 17
    target = Counter(rank(initial, chart[v], False) for v, initial in terminal.items())
    assert min(target) > 0
    P, T = [Counter({r: copies*q for r, q in hist.items()}) for hist in (paid, target)]
    for kind, info in caller['types'].items():
        count = len(info['ports'])
        for sign, offset, *bits in info['diagonal']:
            assert (sign, offset, len(bits)) == (-1, 0, copies)
            T[1+8*sum(bits)] += count
    for event in caller['events']:
        if event[0] == 'J':
            continue
        kind, op, _, *args = event
        count = len(caller['types'][kind]['ports'])
        if op == 'QUERY':
            P[1] += count
        elif op in ('IDLE_ONE', 'IDLE_ODD'):
            P[8*len(args[0])+int(op == 'IDLE_ODD')] += count
    assert P == Counter({int(k):n for k,n in early['invoice']['P'].items()})
    assert T == Counter({int(k):n for k,n in early['invoice']['T'].items()})
    assert sum(P.values()) == 110536 and sum(T.values()) == 22461
    prices = {r: tuple(int(v*GRID) for v in primary['power'](r,TARGET)) for r in P.keys()|T.keys()|set(range(1,10))}
    prices[0] = (0,0)
    for r,v in prices.items():
        verify_power(r,v)
    incident = defaultdict(list)
    charts = defaultdict(list)
    for i,(a,b,_) in enumerate(edges):
        incident[a].append(i)
        incident[b].append(i)
    for v in sorted(movable):
        charts[chart[v]].append(v)
    return chart, rank, terminal, edges, incident, charts, copies, P, T, prices


def dinic(n, s, t, caps, clock):
    """Return feasible flow and prove equal capacity of the residual cut."""
    adj = [[] for _ in range(n)]
    graph = []
    for (u,v),cap in sorted(caps.items()):
        if cap:
            assert cap > 0 and u != v
            i = len(graph)
            graph.extend(([u,v,cap,cap],[v,u,0,0]))
            adj[u].append(i)
            adj[v].append(i+1)
    sys.setrecursionlimit(max(sys.getrecursionlimit(), n+50))
    total = 0
    while True:
        clock()
        levels = [-1]*n
        levels[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for i in adj[u]:
                _,v,r,_ = graph[i]
                if r and levels[v] == -1:
                    levels[v] = levels[u]+1
                    q.append(v)
        if levels[t] == -1:
            break
        cursor = [0]*n
        def augment(u, capacity):
            if u == t:
                return capacity
            while cursor[u] < len(adj[u]):
                i = adj[u][cursor[u]]
                _,v,r,_ = graph[i]
                if r and levels[v] == levels[u]+1:
                    d = augment(v, min(capacity,r))
                    if d:
                        graph[i][2] -= d
                        graph[i^1][2] += d
                        return d
                cursor[u] += 1
            return 0
        limit = sum(caps[s,v] for v in range(n))
        while (delta := augment(s,limit)):
            clock()
            total += delta
    lhs = [0]*n
    certificate = []
    for u,v,r,c in graph[::2]:
        f = c-r
        assert 0 <= f <= c
        lhs[u] += f
        lhs[v] -= f
        if f:
            certificate.append([u,v,f])
    assert lhs[s] == total == -lhs[t] and all(not lhs[i] for i in range(n) if i not in (s,t))
    cut = [i for i,l in enumerate(levels) if l >= 0]
    assert s in cut and t not in cut
    inside = set(cut)
    assert total == sum(c for (u,v),c in caps.items() if u in inside and v not in inside)
    return total, certificate, cut


def compile_case(model, pair):
    chart, rank, terminal, edges, incident, charts, copies, P, T, prices = model
    lo,hi = pair
    labels = (lo,hi)
    vertices = sorted(charts[lo] + charts[hi])
    var = {v:i for i,v in enumerate(vertices)}
    E = sorted(set(i for v in vertices for i in incident[v]))
    n = len(vertices)
    s,t = n,n+1
    max_finite = max(max(v) for v in prices.values())
    hard = (len(E)+len(vertices)+1)*(2*max_finite+1)
    unary = [[0,0] for _ in vertices]
    cap = Counter()
    old = 0

    def edge(a,b,owned):
        d = rank(a,b,owned)
        return hard if d is None else prices[d][0]

    def terminal_cost(v, z):
        d = rank(terminal[v],z,False)
        return hard if d is None or d == 0 else -prices[d][1]

    for i in E:
        a,b,owned = edges[i]
        old += edge(chart[a],chart[b],owned)
        if a in var and b in var:
            cap[var[a],var[b]] += edge(lo,hi,owned)
            cap[var[b],var[a]] += edge(hi,lo,owned)
        elif a in var:
            for bit,f in enumerate(labels):
                unary[var[a]][bit] += edge(f,chart[b],owned)
        else:
            for bit,g in enumerate(labels):
                unary[var[b]][bit] += edge(chart[a],g,owned)
    for v in vertices:
        if v in terminal:
            old += terminal_cost(v,chart[v])
            for bit,z in enumerate(labels):
                unary[var[v]][bit] += terminal_cost(v,z)
    offset = 0
    for i,(a,b) in enumerate(unary):
        m = min(a,b)
        offset += m
        cap[s,i] += b-m
        cap[i,t] += a-m
    assert all(c>=0 for c in cap.values())
    return vertices,E,old,offset,cap


def quote_case(model, scope, pair, changed):
    chart, rank, terminal, edges, incident, charts, copies, P, T, prices = model
    vertices,E,old,offset,cap=scope
    labels=tuple(pair)
    assert set(changed) <= set(vertices)
    assert all(f in labels and f != chart[v] for v,f in changed.items())
    paid = P.copy()
    productive = T.copy()
    objective = 0
    for i in E:
        a,b,owned = edges[i]
        old_r = rank(chart[a],chart[b],owned)
        new_r = rank(changed.get(a,chart[a]),changed.get(b,chart[b]),owned)
        assert new_r is not None
        if old_r:
            paid[old_r] -= copies
        if new_r:
            paid[new_r] += copies
        objective += prices[new_r][0]
    for v in vertices:
        if v in terminal:
            old_r = rank(terminal[v],chart[v],False)
            new_r = rank(terminal[v],changed.get(v,chart[v]),False)
            assert new_r
            productive[old_r] -= copies
            productive[new_r] += copies
            objective -= prices[new_r][1]
    final_clock = max(k[0] for k in chart)
    upper = sum(q*prices[r][1] for r,q in productive.items())-sum(q*prices[r][0] for r,q in paid.items())
    baseline = sum(q*prices[r][1] for r,q in T.items())-sum(q*prices[r][0] for r,q in P.items())
    assert upper == baseline+copies*(old-objective)
    return {'status':'PASS_EXACT_DIRECTED_BINARY_CUT','head':HEAD,'pair':pair,
            'movable_vertices':len(vertices),'changed_vertices':len(changed),
            'directed_whole_upper':str(F(upper,GRID)),
            'signed_paid':dict(+paid),'signed_targets':dict(+productive),
            'rank_surplus':sum(r*(productive[r]-paid[r]) for r in productive.keys()|paid.keys()),
            'event_relabels':sorted((k,f) for (k,r),f in changed.items() if k<final_clock),
            'helper_final_relabels':sorted((r,f) for (k,r),f in changed.items() if k==final_clock),
            'site_tests':0},objective


def certificate_record(pair, scope, flow, nonzero, side, upper):
    vertices,E,old,offset,caps = scope
    return {'pair':pair,'offset':offset,'flow_value':flow,'nonzero_flow':nonzero,'source_side':side,
            'capacity_sha256':sha256(json.dumps([[u,v,c] for (u,v),c in sorted(caps.items()) if c],
                                                separators=(',',':')).encode()).hexdigest(),
            'signed_target_upper':upper}


def verify_case(model, result, clock):
    chart = model[0]
    pair=result['pair']
    scope=compile_case(model,pair)
    vertices,E,old,offset,cap=scope
    n=len(vertices)
    flow,nonzero,side=dinic(n+2,n,n+1,cap,clock)
    final_clock = max(k[0] for k in chart)
    changed = {(k,0): f for k,f in result['event_relabels']}
    changed.update({(final_clock,r): f for r,f in result['helper_final_relabels']})
    actual,value=quote_case(model,scope,pair,changed)
    assert value==offset+flow
    # JSON serialization normalizes integer histogram keys and tuple relabels.
    for key in actual:
        assert json.loads(json.dumps(actual[key]))==result[key], key
    return certificate_record(pair,scope,flow,nonzero,side,actual['directed_whole_upper'])


def solve_case(model, pair, clock):
    scope=compile_case(model,pair)
    vertices,E,old,offset,cap=scope
    n=len(vertices)
    flow,nonzero,side=dinic(n+2,n,n+1,cap,clock)
    reachable=set(side)
    changed={v:pair[int(i not in reachable)] for i,v in enumerate(vertices)
             if model[0][v]!=pair[int(i not in reachable)]}
    actual,value=quote_case(model,scope,pair,changed)
    assert value==offset+flow
    return actual,certificate_record(pair,scope,flow,nonzero,side,actual['directed_whole_upper'])


def main():
    assert __debug__
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('receipt',type=Path)
    ap.add_argument('--seconds',type=int,default=120)
    args=ap.parse_args()
    end=monotonic()+args.seconds
    def clock():
        if monotonic()>=end:
            raise TimeoutError('independent audit cap')
    r=json.loads(args.receipt.read_bytes())
    assert r['head']==HEAD
    model=read_model()
    checked=[]
    unresolved=[]
    for row in r['cuts']:
        if row['status']!='PASS_EXACT_DIRECTED_BINARY_CUT':
            unresolved.append(row['pair'])
            continue
        clock()
        checked.append(verify_case(model,row,clock))
    print(json.dumps({'status':'PASS_INDEPENDENT_FLOW_CUT_AND_DIRECTED_INVOICE','head':HEAD,
        'receipt_sha256':sha256(args.receipt.read_bytes()).hexdigest(),'checks':checked,
        'unresolved':unresolved+r['unvisited']},sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
