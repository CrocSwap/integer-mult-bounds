"""Independent event-slot allocator for original-envelope carrier matchings.

Read-only inputs; explicitly selected JSON output. No producer/import side effects.
Accepts the weighted arcs dump or a list of {donor,event} selected edges.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct


def load_dag(path):
    raw = Path(path).read_bytes()
    h, v, n, q = struct.unpack_from('<4I', raw)
    at = 16
    def take(code, count):
        nonlocal at
        values = struct.unpack_from('<' + str(count) + code, raw, at)
        at += struct.calcsize(code) * count
        return values
    flat = take('I', 2*n)
    args = list(zip(flat[::2], flat[1::2]))
    core, cover = take('Q', n), take('Q', n)
    roots, kind, active = take('I', q), take('I', q), take('B', n)
    assert at == len(raw)
    return h, v, n, q, args, core, cover, roots, kind, active


def selected(record):
    if isinstance(record, list):
        return [(x['donor'], x['event']) for x in record]
    if 'selected' in record:
        return selected(record['selected'])
    answer = []
    for x in record['donors']:
        if x['match_j_plus1']:
            j = x['match_j_plus1'] - 1
            hits = [e for k, e, _ in x['arcs'] if k == j]
            assert len(hits) == 1
            answer.append((x['donor'], hits[0]))
    return answer


def run(dag, record, complete_dirty=False):
    h,v,n,q,args,core,cover,roots,kind,active = load_dag(dag)
    rank = [0]*n
    uses = [[] for _ in range(n)]
    nodes = [x for x in range(1,n) if active[x]]
    sources = [x for x in nodes if not args[x][0]]
    additions = [x for x in nodes if args[x][0]]
    assert len(sources) == v
    for x in nodes:
        rank[x] = cover[x].bit_count()-core[x].bit_count() if args[x][0] else 1
        if args[x][0]:
            assert all(active[y] and y<x for y in args[x])
            for side,y in enumerate(args[x]):
                uses[y].append(2*x+side)
    for j,x in enumerate(roots):
        uses[x].append((1<<31)|j)
    def node(e):
        return roots[e&0x7fffffff] if e>>31 else e//2
    def value(e):
        return node(e) if e>>31 else args[e//2][e&1]
    def order(e):
        x = node(e)
        return rank[x], n+(e&0x7fffffff) if e>>31 else x
    def nested(x,y):
        return not(core[y]&~core[x]) and not(cover[x]&~cover[y])
    edges = selected(record)
    donor_to_event, incoming, continuation = {}, {}, {}
    for u,e in edges:
        assert u in additions and e in uses[value(e)]
        assert u not in donor_to_event and e not in incoming
        assert value(e) in args[u] and order(2*u)<order(e)
        assert nested(u,node(e))
        side = args[u].index(value(e))
        donor_to_event[u] = e
        incoming[e] = u
        continuation[2*u+side] = e
    heads = {x:[e for e in uses[x] if e not in incoming] for x in nodes}
    assert all(heads.values())
    slots, last, values, source_slots, ops = {}, [], [], [], []
    support = {}
    def allocate(x):
        slot = len(last)
        last.append(x)
        values.append(0)
        return slot
    def chain(e,slot):
        while True:
            assert e not in slots
            slots[e] = slot
            if e not in continuation:
                break
            e = continuation[e]
    for x in sorted(nodes,key=lambda x:(rank[x],x)):
        if not args[x][0]:
            support[x] = 1<<sources.index(x)
            for e in heads[x]:
                slot = allocate(x)
                values[slot] = support[x]
                source_slots.append((slot,x))
                chain(e,slot)
            continue
        ins = [slots[2*x+i] for i in range(2)]
        assert ins[0] != ins[1]
        for side,slot in enumerate(ins):
            e = 2*x+side
            expected = incoming[e] if e in incoming else args[x][side]
            assert last[slot] == expected
            last[slot] = x
        preserved = next((i for i in range(2) if 2*x+i in continuation),1)
        pivot, other = ins[1-preserved],ins[preserved]
        values[pivot] ^= values[other]
        ops.append((pivot,other))
        support[x] = support[args[x][0]] ^ support[args[x][1]]
        assert support[args[x][0]] & support[args[x][1]] == 0
        for k,e in enumerate(heads[x]):
            slot = pivot if k == 0 else allocate(x)
            if k:
                values[slot] ^= values[pivot]
                ops.append((slot,pivot))
            assert values[slot] == support[x]
            chain(e,slot)
    outslots = [slots[(1<<31)|j] for j in range(q)]
    assert len(set(outslots)) == q
    assert len(last) == len(additions)+q-len(edges)
    for j,s in enumerate(outslots):
        e = (1<<31)|j
        assert last[s] == (incoming[e] if e in incoming else roots[j])
        assert values[s] == support[roots[j]]
        assert e not in continuation
    centers = [j for j,k in enumerate(kind) if k]
    assert len(centers) == h
    assert {core[roots[j]] for j in centers} == {1<<i for i in range(h)}
    assert all(cover[roots[j]] == (1<<h)-1 and rank[roots[j]] == h-1 for j in centers)
    def token(tag):
        return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8],'little')
    dirty = [1<<i for i in range(len(last))] if complete_dirty else [token('dirty:'+str(i)) for i in range(len(last))]
    saved = dirty[:]
    data = {x:1<<(len(last)+i) for i,x in enumerate(sources)} if complete_dirty else {x:token('input:'+str(x)) for x in sources}
    expected_values = dict(data)
    for x in sorted(additions):
        expected_values[x] = expected_values[args[x][0]] ^ expected_values[args[x][1]]
    def circuit(reverse=False):
        for dst,src in reversed(ops) if reverse else ops:
            dirty[dst] ^= dirty[src]
    def inject():
        for s,x in source_slots:
            dirty[s] ^= data[x]
    circuit()
    out = [dirty[s] for s in outslots]
    circuit(True)
    inject()
    circuit()
    out = [a^dirty[s] for a,s in zip(out,outslots)]
    circuit(True)
    inject()
    assert dirty == saved
    assert out == [expected_values[x] for x in roots]
    return dict(h=h, additions=len(additions), outputs=q, matches=len(edges),
                roles=len(last), exact_all_source_coefficients=True,
                exact_terminal_slots=q, copied_center_outputs=len(centers),
                matched_output_uses=sum(e>>31 for _,e in edges),
                matched_center_uses=sum(((1<<31)|j) in incoming for j in centers),
                copied_rank_saving=h*(h-1), scalar_additions=len(ops),
                dirty_wrapper_regression=True, source_slots=len(source_slots),
                complete_dirty_basis=complete_dirty,
                complete_dirty_basis_vectors=len(last)+len(sources) if complete_dirty else None,
                dag_sha256=hashlib.sha256(Path(dag).read_bytes()).hexdigest(),
                selected_edges_sha256=hashlib.sha256(json.dumps(sorted(edges),separators=(',',':')).encode()).hexdigest(),
                audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dag',required=True)
    parser.add_argument('--matching',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--complete-dirty',action='store_true')
    a = parser.parse_args()
    result = run(a.dag,json.loads(Path(a.matching).read_text()),a.complete_dirty)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS exact original-envelope matching schedule',result['h'],result['matches'])
