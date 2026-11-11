"""Recover an actual nested chart witness for the residual positive rank bound."""

from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from math import prod
from pathlib import Path
import gzip
import json
import sys

from constrained import solve_equalities
from eliminate import domain
from release import BRACKET, WORD_SHA, bounds, changed_blocks, chart, inventory, join, load, subspace_count


def volume(domains, graph, cap):
    sizes = {i:len(s) for i,s in domains.items()}
    adj = {i:graph[i]&sizes.keys() for i in sizes}
    total = 0
    while adj:
        work = {i:sizes[i]*prod(sizes[j] for j in ns) for i,ns in adj.items()}
        v = min(adj,key=lambda i:(work[i],i))
        ns = adj.pop(v)
        total += work[v]
        if total > cap:
            return None
        for n in ns:
            adj[n].remove(v)
            adj[n].update(ns-{n})
    return total


def quotient_domain(lo, hi):
    q = len(hi).bit_length()-len(lo).bit_length()
    if q <= 5:
        return domain(lo,hi)
    axes = []
    found = set(lo)
    for v in sorted(hi):
        if v not in found:
            axes.append(v)
            found |= {v ^ w for w in found}
    assert len(axes)==q and found==hi
    states = []
    for rank in range(q+1):
        for pivots in combinations(range(q),rank):
            slots = [(row,c) for row,p in enumerate(pivots) for c in range(p+1,q) if c not in pivots]
            for vals in product((0,1),repeat=len(slots)):
                rows = [axes[p] for p in pivots]
                for (row,c),value in zip(slots,vals):
                    if value:
                        rows[row] ^= axes[c]
                space = set(lo)
                for v in rows:
                    space |= {v ^ w for w in space}
                states.append(chart(space))
    assert len(states)==len(set(states))==sum(subspace_count(q,r) for r in range(q+1))
    return sorted(states)


def rank_conflict(block, base, domains, ranks, paid, target, equalities):
    """Find a deterministic geometric arc obstruction at the relaxed ranks."""
    active = set(block)
    links = defaultdict(set)
    rules = defaultdict(list)
    for a,b in paid.keys()|target.keys():
        if a not in active and b not in active:
            continue
        links[a].add(b)
        links[b].add(a)
        rules[a,b].append('subset')
        rules[b,a].append('superset')
    for a,b in equalities:
        if a != b and (a in active or b in active):
            links[a].add(b)
            links[b].add(a)
            rules[a,b].append('equal')
            rules[b,a].append('equal')
    allowed = {i:tuple(m for m,r in domains[i] if r==ranks[i]) if i in active else (base[i][0],)
               for i in links}
    sizes = {i:len(v) for i,v in allowed.items()}
    if not all(sizes.values()):
        return dict(status='empty rank domain',vertices=[i for i,n in sizes.items() if not n])
    arcs = deque(sorted(rules))
    changes = []
    while arcs:
        a,b = arcs.popleft()
        requirements=rules[a,b]
        compatible = lambda x,y: all((x==y if rule=='equal' else
                                     not x&~y if rule=='subset' else not y&~x)
                                    for rule in requirements)
        revised=tuple(x for x in allowed[a] if any(compatible(x,y) for y in allowed[b]))
        if len(revised)==len(allowed[a]):
            continue
        changes.append(dict(vertex=a,neighbor=b,relations=requirements,
                            before=len(allowed[a]),after=len(revised)))
        if not revised:
            return dict(status='empty domain by arc consistency',failed_edge=[a,b],
                        initial_sizes=sizes,changes=changes)
        allowed[a]=revised
        arcs.extend((v,a) for v in sorted(links[a]) if v!=b)
    return dict(status='arc consistency alone does not exclude',initial_sizes=sizes,changes=changes)


def refine(word, row, graph, engine):
    raw, ids, comp, raw_paid, raw_target, fixed, scalar, original, entry, end, child = inventory(word, graph)
    base = {i:chart(s) for i,s in enumerate(original) if s is not None}
    old_lo, old_hi, _ = bounds(original, Counter((comp[a],comp[b]) for _,a,b in raw_paid), {comp[i] for i in fixed})
    left,right = map(Q,BRACKET)
    weights = {r:(engine.raw_margin({r:1},right)[0],engine.raw_margin({r:1},left)[1]) for r in range(1,10)}
    adds = row['adds']
    roots = {e:comp[scalar[e][0]] for e in adds}
    split = {e:len(original)+j for j,e in enumerate(adds)}
    ordered = sorted(adds,key=lambda e:entry[child[e]])

    def belong(i):
        c=comp[i]
        for e in ordered:
            if comp[i]==roots[e] and entry[child[e]]<=entry[i]<end[child[e]]:
                c=split[e]
        return c

    space = [*original,*(original[roots[e]] for e in adds)]
    states = base | {split[e]:base[roots[e]] for e in adds}
    paid = Counter((belong(a),belong(b)) for _,a,b in raw_paid)
    target = Counter((belong(a),belong(b)) for a,b in raw_target)
    lo,hi,neighbors = bounds(space,paid,{belong(i) for i in fixed})
    eq = [tuple(belong(ids[r,start-1]) for r,start,_ in p['new_visits']) for p in row['moved']]
    assert list(map(list,eq))==row['cut_components']
    lower,upper = lo.copy(),hi.copy()
    order = sorted(paid,key=lambda e:(states[e[0]][1],states[e[1]][1],e))
    iterations=0
    while True:
        before=(lower.copy(),upper.copy())
        for u,v in eq:
            lower[u]=lower[v]=join(lower[u],lower[v])
            upper[u]=upper[v]=upper[u]&upper[v]
        for u,v in order:
            lower[v]=join(lower[v],lower[u])
        for u,v in reversed(order):
            upper[u]&=upper[v]
        iterations+=1
        if any(not l<=h for l,h in zip(lower,upper)):
            return dict(status='impossible by propagated weak nesting',iterations=iterations)
        if (lower,upper)==before:
            break
    changed = {i for i,(l,h) in enumerate(zip(lo,hi))
               if i>=len(original) or (l,h)!=(old_lo[i],old_hi[i])}
    changed |= set(roots.values())
    for u,v in eq:
        changed.update((u,v))
        if u!=v:
            neighbors[u].add(v)
            neighbors[v].add(u)
    blocks = changed_blocks(space,lo,hi,neighbors,target,changed)
    frame_spaces = {graph.span(basis) for basis in word['frames']}
    results = []
    for block in blocks:
        q = {i:len(upper[i]).bit_length()-len(lower[i]).bit_length() for i in block}
        sizes = {i:sum(subspace_count(d,r) for r in range(d+1)) for i,d in q.items()}
        rank = solve_equalities(block,states,lower,upper,paid,target,eq,weights,True,{})
        packet = dict(vertices=block,quotient_dimensions=q,domain_sizes=sizes,rank_relaxation=rank)
        if not rank.get('infeasible') and Q(rank['upper'])>0:
            ranks = rank['selected_ranks']
            existing = {i:sorted(chart(s) for s in frame_spaces if lower[i]<=s<=upper[i]) for i in block}
            at_rank = {i:[s for s in existing[i] if s[1]==ranks[i]] for i in block}
            for key, selected in [('existing_charts_at_best_ranks',at_rank),('all_existing_charts',existing)]:
                work=volume(selected,neighbors,1200000)
                if work is not None:
                    packet[key]=solve_equalities(block,states,lower,upper,paid,target,eq,weights,False,selected)
            exact_volume = volume({i:range(n) for i,n in sizes.items()},neighbors,2400000)
            packet['exact_table_volume']=exact_volume
            if max(q.values())<=7 and exact_volume is not None:
                whole={i:quotient_domain(lower[i],upper[i]) for i in block}
                packet['full_chart_search']=solve_equalities(block,states,lower,upper,paid,target,eq,weights,False,whole)
                diagnostic=rank_conflict(block,states,whole,ranks,paid,target,eq)
                if 'failed_edge' in diagnostic:
                    affected=set(diagnostic['failed_edge'])
                    diagnostic['contact_visits']={i:[raw[j] for j in range(len(raw)) if belong(j)==i]
                                                  for i in sorted(affected)}
                    diagnostic['touching_move_events']=[k for k,a,b in raw_paid
                                                        if {belong(a),belong(b)}<=affected]
                packet['best_rank_geometric_diagnostic']=diagnostic
        results.append(packet)
    return dict(status='refined',iterations=iterations,results=results,source_pair=row)


def main(word_path,pair_path,graph_path,price_path):
    raw=gzip.decompress(word_path.read_bytes())
    source=json.loads(pair_path.read_bytes())
    assert sha256(raw).hexdigest()==WORD_SHA==source['word']
    assert len(source['hits'])==1
    out=refine(json.loads(raw),source['hits'][0],load('chart_graph',graph_path),load('directed_price',price_path))
    print(json.dumps(dict(word=WORD_SHA,**out),indent=2))


if __name__=='__main__':
    main(*(Path(p) for p in sys.argv[1:]))
