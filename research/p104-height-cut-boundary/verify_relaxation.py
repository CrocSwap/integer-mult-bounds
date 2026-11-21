#!/usr/bin/env python3
"""Exact witness for a named relaxation of #7852's joint mass wall.

Reads the pinned Lean source for P104 port and flag data, checks SHA-256,
and uses integer max-flow to assign nested coordinate subspaces to the
height witness. No solver, floating point, Lean build, or network needed.
See RESULT.md for the precise model and omissions.
"""
import ast
import collections
import hashlib
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent / 'pinned'
PINS = {
    'UniFold7113.lean': 'd3dbc8613472562469769e0b12049a7abffd912e1d04a40d81df73c4877a611c',
    'UniFold7113Inst.lean': '2cffbe3feae4e5e32dcd1cc5efaaecc1ff42eb65dce6e18d710faec0213bec0d',
    'BankFlagB.lean': '4b9c06410e395409570f4fd82f196a22c772eb43e749ab867c0c0e24c450f6f7',
    'BankFitHS1.lean': 'b55f011cca76fea1b8720953e381046f286d059a3f5b3e78af62d9d97c6291ee',
    'BankHelpA.lean': '611e83def237f8423d5472efa8df06a0260933321d82a65f93df6766bd6cda8a',
    'WordRungJoint.lean': '0be5a66adb2a36e2224709820917f9c6a7720054999249e54b23c5ab5d8691b8',
}

# counts of bank endpoints (source height, destination height).
ARCS = {(0,2):200, (0,3):14, (1,0):14, (1,2):90, (1,3):96,
        (2,3):90, (2,5):200, (3,6):200, (5,8):200, (6,9):200}
H = 9

def load_source(base):
    texts = {}
    for name, want in PINS.items():
        data = (base / name).read_bytes()
        got = hashlib.sha256(data).hexdigest()
        assert got == want, f'{name}: SHA-256 {got}, expected {want}'
        texts[name] = data.decode()
    def ll(name, field):
        match = re.search(r'def ' + field + r' : List ℕ := (\[[^\]]+\])', texts[name])
        assert match, (name, field)
        return ast.literal_eval(match.group(1))
    return (ll('UniFold7113.lean', 'ports7113'),
            ll('UniFold7113Inst.lean', 'nonD7113'),
            ll('BankFlagB.lean', 'flag'))

def rank_data(ports, non_d, flag):
    assert len(ports) == len(set(ports)) == 104
    assert len(non_d) == 8 and len(set(non_d)) == 8
    assert len(flag) == H
    coord = {}
    for bits in range(1 << H):
        q = 0
        for j, b in enumerate(flag):
            if bits >> j & 1:
                q ^= b
        assert q not in coord
        coord[q] = bits
    need = [0] * H
    for idx, q in enumerate(ports):
        weight = 1 + (idx not in non_d)
        x_skip = coord[q].bit_length() - 1  # line first enters flag
        y_skip = next(j for j, f in enumerate(flag) if (q & f).bit_count() % 2)
        for j in range(H):
            need[j] += weight * ((j != x_skip) + (j != y_skip))
    assert sum(need) == 3200
    return need

def allocate(up_groups, target):
    """Integral max-flow from bank groups to 9 flag positions."""
    ng = len(up_groups)
    source, sink, n = 0, ng + 10, ng + 11
    graph = [[] for _ in range(n)]
    def edge(a, b, cap):
        forward = [b, cap, None, cap]
        reverse = [a, 0, forward, 0]
        forward[2] = reverse
        graph[a].append(forward)
        graph[b].append(reverse)
        return forward
    handles = []
    for z, ((i,j), count) in enumerate(up_groups):
        edge(source, 1+z, (j-i)*count)
        handles.append([edge(1+z, 1+ng+k, count) for k in range(H)])
    for k, t in enumerate(target):
        edge(1+ng+k, sink, t)
    flow = 0
    while True:
        parent = {source: None}
        q = collections.deque([source])
        while q and sink not in parent:
            u = q.popleft()
            for e in graph[u]:
                if e[1] and e[0] not in parent:
                    parent[e[0]] = (u, e)
                    q.append(e[0])
        if sink not in parent:
            break
        v = sink
        path = []
        while v != source:
            u, e = parent[v]
            path.append(e)
            v = u
        delta = min(e[1] for e in path)
        for e in path:
            e[1] -= delta
            e[2][1] += delta
        flow += delta
    assert flow == sum(target), (flow, sum(target))
    allocation = [[e[3]-e[1] for e in row] for row in handles]
    return allocation

def materialize(up_groups, allocation):
    """Make actual nested coordinate pairs, independently per bank.

    A group has N sets each of size d, with prescribed coordinate totals.
    Repeatedly take d largest remaining counts (bipartite Havel-Hakimi),
    checked exhaustively below.
    """
    banks=[]
    for (((i,j), count), remaining) in zip(up_groups, allocation):
        rem=remaining[:]
        for _ in range(count):
            choices=sorted(range(H), key=lambda k: (-rem[k], k))[:j-i]
            assert all(rem[k] > 0 for k in choices)
            for k in choices:
                rem[k]-=1
            delta=sum(1<<k for k in choices)
            available=[k for k in range(H) if not (delta>>k & 1)]
            src=sum(1<<k for k in available[:i])
            dst=src | delta
            assert src.bit_count()==i and dst.bit_count()==j and src & ~dst == 0
            banks.append((src,dst))
        assert rem == [0]*H
    # 14 one-level descents, two across each of flag cuts 2..8.
    banks.extend([(1<<k, 0) for k in range(1,8) for _ in range(2)])
    return banks

def cut_test(arcs):
    bad=[]
    min_slack=None
    tight=0
    for mask in range(1,(1<<10)-1):
        bit=lambda i: (mask>>i)&1
        dem=200*(bit(0) and not bit(8))+200*(bit(1) and not bit(9))
        sep=(bit(1)==bit(9) and bit(0)==bit(8) and bit(1)!=bit(0))
        rhs=dem+104*sep
        got=sum(c for (i,j),c in arcs.items() if bit(i) and not bit(j))
        slack=got-rhs
        if slack < 0:
            bad.append((mask,got,rhs))
        min_slack=slack if min_slack is None else min(min_slack,slack)
        tight += (slack==0)
    return bad,min_slack,tight

def main():
    base=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else BASE
    ports, non_d, flag = load_source(base)
    need=rank_data(ports,non_d,flag)
    extras=[0]+[2]*7+[0]
    target=[a+b for a,b in zip(need,extras)]
    up=sorted((a,c) for a,c in ARCS.items() if a[0] < a[1])
    alloc=allocate(up,target)
    banks=materialize(up,alloc)
    assert collections.Counter((s.bit_count(),d.bit_count()) for s,d in banks)==collections.Counter(ARCS)
    asc=[sum((not(s>>k & 1)) and (d>>k & 1) for s,d in banks) for k in range(H)]
    desc=[sum((s>>k & 1) and not(d>>k & 1) for s,d in banks) for k in range(H)]
    assert asc == target and desc == extras, (asc,desc,target,extras)
    ascent=sum((d.bit_count()-s.bit_count()) for s,d in banks if s < (1<<H) and s & ~d == 0)
    descent=sum((s.bit_count()-d.bit_count()) for s,d in banks if d & ~s == 0)
    assert (ascent,descent,ascent-3200)==(3214,14,14)
    bad,slack,tight=cut_test(ARCS)
    assert not bad and slack==0
    # A single omitted descent fails a required flag cut and destroys X=28.
    removed=next((s,d) for s,d in banks if s.bit_count()>d.bit_count())
    broken=banks[:]
    broken.remove(removed)
    k=(removed[0]^removed[1]).bit_length()-1
    assert sum((s>>k & 1) and not(d>>k & 1) for s,d in broken)==1 < extras[k]
    # Automatically find a single-bank removal that fails some height cut.
    for arc in ARCS:
        test=ARCS.copy(); test[arc]-=1
        failed,_,_=cut_test(test)
        if failed:
            break
    assert failed
    # Concrete obstruction to realizing this as a BankedGraph: the
    # singleton chart P={span(q)} has two outgoing x-fields, but none of
    # the coordinate bank sources is that line. The source-side cut
    # inequality for arbitrary chart predicates would demand at least two.
    q=ports[0]
    assert q==11 and 0 not in non_d and q not in flag
    field_out=2
    bank_out=sum(s.bit_count()==1 and flag[s.bit_length()-1]==q for s,d in banks)
    assert bank_out==0 and bank_out < field_out
    # Two distinct ways to meet X=112 while violating one 56 half.
    for add_src,add_dst,expected in [(0,1,(14,98)), (1,0,(98,14))]:
        extra=[(add_src,add_dst)]*84
        augmented=banks+extra
        ext_arcs=ARCS.copy()
        ext_arc=(add_src.bit_count(),add_dst.bit_count())
        ext_arcs[ext_arc]=ext_arcs.get(ext_arc,0)+84
        assert not cut_test(ext_arcs)[0]
        ext_asc=[sum(not(s>>j & 1) and (d>>j & 1) for s,d in augmented) for j in range(H)]
        ext_desc=[sum((s>>j & 1) and not(d>>j & 1) for s,d in augmented) for j in range(H)]
        assert all(x>=y for x,y in zip(ext_asc,target))
        assert all(x>=y for x,y in zip(ext_desc,extras))
        assert (sum(ext_desc),sum(ext_asc)-3200)==expected
    print('PINS: 6 SHA-256 verified; expected PR head 41beda1d6435760dc99e38bd7e65f36798aad212')
    print('FIELDS: 104 labels; 96 D; 200 each of 0->8 and 1->9; climb 3200')
    print('FLAG FIELD DEMAND:', need)
    print('FLAG ASCENDING:', asc, 'DESCENDING:', desc)
    print('HEIGHT CUTS: 1022/1022 pass; minimum slack',slack,'tight',tight)
    print('BANKS:',len(banks),'ASCENT:',ascent,'DESCENT:',descent,'R:',ascent-3200,'X:',descent+ascent-3200)
    print('17 REPEATS: X total',17*(descent+ascent-3200),'required',17*112)
    print('TRADEOFF CONTROLS: (D,R)=(14,98) and (98,14) each meet all retained cuts')
    print('NEGATIVE CONTROL: removing descent fails flag level',k+1)
    print('NEGATIVE CONTROL: decrement',arc,'fails',len(failed),'height cuts; first',failed[0])
    print('OUTSIDE RELAXATION: singleton span(11) cut needs',field_out,'outgoing banks; witness has',bank_out)

if __name__ == '__main__':
    main()
