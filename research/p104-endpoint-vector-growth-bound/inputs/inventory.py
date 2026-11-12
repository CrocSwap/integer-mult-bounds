"""Exact current-word common-frame screen for closed public helper components."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

HERE = Path(__file__).resolve().parent
PINS = {
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def span(vectors):
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return result


def inventory(w):
    roles = w['public'] + w['owned_fields']
    main = set(w['live']) | {i + 112 for i in w['live']} | set(w['hosted']['X2']) | set(w['hosted']['Y2'])
    assert w['public'] == 1501 and len(main) == 400
    eligible = set(range(w['public'])) - main
    assert len(eligible) == 1101
    parent, nodes, contacts, moves = [], [], [], []

    def node(role, chart, endpoint=False):
        n = len(nodes)
        nodes.append([role, chart, endpoint])
        parent.append(n)
        return n

    def root(i):
        while parent[i] != i:
            i, parent[i] = parent[i], parent[parent[i]]
        return i

    active = [node(i, c, True) for i, c in enumerate(w['initial'])] + [None]*w['owned_fields']
    assert len(active) == roles
    for t,(op,r,*a) in enumerate(w['program']):
        old = active[r]
        if op == 'INIT':
            assert old is None
            active[r] = node(r,a[0])
        elif op == 'CLEAR':
            assert nodes[old][1] == a[0]
            active[r] = None
        elif op == 'MOVE':
            assert nodes[old][1] == a[0]
            new = node(r,a[1])
            moves.append((t,old,new))
            active[r] = new
        elif op in ('ADD','COPY'):
            s,_,c = a
            assert nodes[old][1] == nodes[active[s]][1] == c
            parent[root(active[s])] = root(old)
            contacts.append((t,old,op))
        else:
            assert op == 'SCALE' and nodes[old][1] == a[1]
            contacts.append((t,old,op))
    assert all(active[i] is None for i in range(w['public'], roles))
    for i,c in enumerate(w['final']):
        assert nodes[active[i]][1] == c
        nodes[active[i]][2] = True
    groups, uses, incident = defaultdict(list),defaultdict(list),defaultdict(list)
    for i,n in enumerate(nodes):
        groups[root(i)].append(n)
    for t,n,op in contacts:
        uses[root(n)].append((t,op))
    for t,a,b in moves:
        ra,rb = root(a),root(b)
        assert ra != rb
        incident[ra].append((t,nodes[b][1],'source'))
        incident[rb].append((t,nodes[a][1],'target'))
    return eligible,groups,uses,incident


def main():
    assert __debug__
    alarm(40)
    for name,h in PINS.items():
        assert sha256((HERE/name).read_bytes()).hexdigest() == h
    raw = decompress((HERE/'inputs/7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    w = loads(raw)
    assert len(w['program']) == 76466
    e,groups,uses,incident = inventory(w)
    frames = [tuple(v) for v in w['frames']]
    spaces = [span(v) for v in frames]
    assert all(len(s)==1<<len(v) for s,v in zip(spaces,frames,strict=True))
    ranks = [len(v) for v in frames]
    h = run_path(str(HERE/'inputs/pricing.py'))['power_bounds']
    lo,hi = map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))

    @cache
    def gain(delta):
        left = sum(n*h(r,hi if n>0 else lo)[0 if n>0 else 1] for r,n in delta)
        right = sum(n*h(r,lo if n>0 else hi)[1 if n>0 else 0] for r,n in delta)
        return 17*left,17*right

    counts, cases = Counter(),[]
    for g, members in groups.items():
        if sum(op=='ADD' for _,op in uses[g]) < 2:
            continue
        counts['multi_add'] += 1
        if any(r not in e for r,_,_ in members):
            counts['main_or_owned'] += 1
            continue
        if any(endpoint for _,_,endpoint in members):
            counts['fixed_endpoint'] += 1
            continue
        counts['closed_pure'] += 1
        current, = {c for _,c,_ in members}
        d = ranks[current]
        edges = sorted(incident[g])
        assert edges and all(w['program'][t][0]=='MOVE' for t,_,_ in edges)
        lower = [c for _,c,_ in edges if ranks[c] < d]
        upper = [c for _,c,_ in edges if ranks[c] > d]
        assert len(lower)+len(upper)==len(edges)
        assert all(spaces[c] <= spaces[current] for c in lower)
        assert all(spaces[current] <= spaces[c] for c in upper)
        min_r = max((ranks[c]+1 for c in lower),default=0)
        max_r = min((ranks[c]-1 for c in upper),default=9)
        low_space = span(x for c in lower for x in frames[c])
        high_space = set.intersection(set(range(512)),*(spaces[c] for c in upper))
        assert low_space <= spaces[current] <= high_space
        first = max(min_r,len(low_space).bit_length()-1)
        last = min(max_r,len(high_space).bit_length()-1)
        assert first <= d <= last
        stock = Counter(abs(d-ranks[c]) for _,c,_ in edges)

        def quote(k):
            delta = stock.copy()
            delta.subtract(abs(k-ranks[c]) for _,c,_ in edges)
            return gain(tuple(sorted((r,n) for r,n in delta.items() if n)))

        relaxed = [k for k in sorted({min_r,max_r}) if quote(k)[1]>0]
        if not relaxed:
            counts['dimension_nonpositive'] += 1
            continue
        feasible = [(k,quote(k)) for k in sorted({first,last}) if quote(k)[1]>0]
        if feasible:
            counts['geometry_survivor'] += 1
        else:
            counts['geometry_exclusion'] += 1
        cases.append({'first_contact':uses[g][0][0],'old_chart':current,'old_rank':d,
                      'roles':sorted({r for r,_,_ in members}),'contacts':uses[g], 'moves':edges,
                      'relaxed_ranks':[min_r,max_r],'feasible_ranks':[first,last],
                      'price_positive_relaxed':[(k,quote(k)) for k in relaxed],
                      'price_positive_feasible':feasible,'lower_span':sorted(low_space),'upper_span':sorted(high_space)})
    alarm(0)
    print(dumps({'pins':PINS,'counts':counts,'cases':sorted(cases,key=lambda x:x['first_contact']),
                 'runner_cap_seconds':40,'paid_zero_disallowed':True,'seed':None},sort_keys=True,indent=2,default=str))


if __name__ == '__main__':
    main()
