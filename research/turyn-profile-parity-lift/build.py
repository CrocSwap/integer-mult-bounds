#!/usr/bin/env python3
"""Rebuild the actual-port parity lift and explicit binary labels.

Only the earlier new standard-library geometry producer is imported, at a
verified hash. No predecessor executable source is imported or executed.
"""
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def require(ok,message):
    if not ok: raise ValueError(message)

def active(first,second):
    return all(sum(x*y for x,y in zip(first[k:k+8],second[k:k+8])) for k in (0,8,16))

def rank(rows):
    pivots={}
    for row in rows:
        while row:
            pivot=row.bit_length()-1
            if pivot not in pivots:
                pivots[pivot]=row
                break
            row^=pivots[pivot]
    return len(pivots)

def labels_from_roots(coordinates,profile):
    low=(profile+1)%3
    gram=[]
    for a in coordinates:
        row=[]
        for b in coordinates:
            dot=sum(a[8*low+i]*b[8*low+i] for i in range(8))
            require(dot%4==0,'Integral low-root pairing')
            row.append((1+dot//4)%2)
        gram.append(row)
    selected=[];rows=[]
    for index,row in enumerate(gram):
        packed=sum(x<<i for i,x in enumerate(row))
        if rank(rows+[packed])>len(rows):
            rows.append(packed);selected.append(index)
    require(len(selected)==9,'Low-root Gram rank nine')
    h=[[gram[a][b] for b in selected] for a in selected]
    def dot(a,b):
        return sum(h[i][j] for i in range(9) if a>>i&1 for j in range(9) if b>>j&1)%2
    remaining=[1<<i for i in range(9)];units=[]
    while remaining:
        index=next((i for i,x in enumerate(remaining) if dot(x,x)),None)
        if index is not None:
            u=remaining.pop(index);units.append(u)
            remaining=[v^u if dot(v,u) else v for v in remaining]
        else:
            u=remaining.pop(0)
            index=next(i for i,v in enumerate(remaining) if dot(u,v))
            v=remaining.pop(index)
            remaining=[x^(u if dot(x,v) else 0)^(v if dot(x,u) else 0) for x in remaining]
            a=units.pop()
            units.extend([a^u,a^v,a^u^v])
    require(all(dot(a,b)==(i==j) for i,a in enumerate(units) for j,b in enumerate(units)),
            'Exact orthonormal basis of binary Gram')
    labels=[]
    for row in gram:
        labels.append(sum((sum(row[selected[k]] for k in range(9) if u>>k&1)%2)<<i
                          for i,u in enumerate(units)))
    require(all((a&b).bit_count()%2==gram[i][j]
                for i,a in enumerate(labels) for j,b in enumerate(labels)), 'Full label Gram equality')
    return labels

def lift(classes,ports,clique_classes):
    used=sorted({c for clique in clique_classes for c in clique})
    index={c:i for i,c in enumerate(used)}
    edges=sorted({tuple(sorted((index[a],index[b])))
                  for clique in clique_classes for a,b in combinations(clique,2)})
    compatibility={};neighbors=[[] for _ in used]
    for i,j in edges:
        forward=[0]*8;backward=[0]*8
        for a,x in enumerate(classes[used[i]]):
            for b,y in enumerate(classes[used[j]]):
                if active(ports[x],ports[y]):
                    forward[a]|=1<<b;backward[b]|=1<<a
        compatibility[i,j]=forward;compatibility[j,i]=backward
        neighbors[i].append(j);neighbors[j].append(i)
    statistics=Counter()
    def visit(domains,depth):
        statistics['nodes']+=1
        statistics['maximum_depth']=max(statistics['maximum_depth'],depth)
        queue=deque(compatibility)
        while queue:
            i,j=queue.popleft()
            keep=sum(1<<a for a in range(8) if domains[i]>>a&1 and compatibility[i,j][a]&domains[j])
            if keep!=domains[i]:
                if not keep:
                    statistics['empty_domains']+=1
                    return None
                domains[i]=keep
                queue.extend((k,i) for k in neighbors[i] if k!=j)
        unresolved=[i for i,d in enumerate(domains) if d.bit_count()>1]
        if not unresolved:
            return [d.bit_length()-1 for d in domains]
        vertex=min(unresolved,key=lambda i:(domains[i].bit_count(),-len(neighbors[i]),i))
        for choice in range(8):
            if domains[vertex]>>choice&1:
                child=domains.copy();child[vertex]=1<<choice
                result=visit(child,depth+1)
                if result is not None:
                    return result
        return None
    choices=visit([255]*len(used),0)
    require(choices is not None,'Consistent actual-port lift exists')
    return used,choices,[[index[c] for c in clique] for clique in clique_classes],dict(statistics)

def build():
    sources=json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in sources['files'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source pin: '+name)
    spec=importlib.util.spec_from_file_location('new_pinned_geometry',HERE.parent/'turyn-profile-cnf/build.py')
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    ports,digest=geometry.construct_ports()
    groups=[defaultdict(list) for _ in range(3)]
    for i,row in enumerate(ports):
        norms=[sum(x*x for x in row[8*k:8*k+8]) for k in range(3)]
        high=norms.index(16)
        key=tuple(x for k in range(3) if k!=high for x in row[8*k:8*k+8])
        groups[high][key].append(i)
    classes=[]
    for high in range(3):
        for key in sorted(groups[high]):
            classes.append(groups[high][key])
    require(len(classes)==2880 and all(len(group)==8 for group in classes),'Complete eight-port class map')
    quotient=json.loads((ROOT/'research/turyn-code-space/evidence/PARITY-CERTIFICATE.json').read_text())['cliques']
    profiles=[];search=[]
    for high in range(3):
        restrictions=[[c for c in clique if c//960==high] for clique in quotient]
        used,choices,cliques,statistics=lift(classes,ports,restrictions)
        ids=[classes[c][choice] for c,choice in zip(used,choices)]
        coordinates=[list(ports[i]) for i in ids]
        profiles.append({'profile':high,'classes':used,'clique_classes':restrictions,'cliques':cliques,
                         'selected_ports':ids,'coordinates':coordinates,
                         'nine_bit_labels':labels_from_roots(coordinates,high),'all_ports_sha256':digest})
        search.append({'profile':high,'source_classes':len(used),'choices_per_class':8,
                       'stopping_rule':'First exact lift, not enumeration or optimality search','statistics':statistics})
    first=profiles[0];bad=None
    for position,source_class in enumerate(first['classes']):
        for alternate in classes[source_class]:
            if alternate==first['selected_ports'][position]:
                continue
            for clique in first['cliques']:
                if position not in clique:
                    continue
                for other in clique:
                    if other!=position and not active(ports[alternate],first['coordinates'][other]):
                        bad={'profile':0,'position':position,'source_class':source_class,
                             'original_port':first['selected_ports'][position],
                             'replacement_port':alternate,'replacement_coordinates':list(ports[alternate]),
                             'broken_required_edge':[position,other]}
                        break
                if bad:break
            if bad:break
        if bad:break
    require(bad is not None,'A valid same-class representative can fail an actual clique edge')
    chosen={c:row for profile in profiles for c,row in zip(profile['classes'],profile['coordinates'])}
    global_cliques=[]
    for index,clique in enumerate(quotient):
        missing=[]
        for a,b in combinations(clique,2):
            if a//960!=b//960:
                dots=[sum(chosen[a][8*k+i]*chosen[b][8*k+i] for i in range(8)) for k in range(3)]
                if 0 in dots:missing.append({'classes':[a,b],'integer_block_dots':dots})
        require(missing,'These particular separate lifts are not global actual cliques')
        global_cliques.append({'clique_index':index,'missing_cross_profile_edges':len(missing),
                               'first_missing_edge':missing[0]})
    global_scope={'scope':'These independently chosen per-profile lifts do not form global actual 24-cliques. This is not a search over other global choices.',
                  'cliques':global_cliques}
    low_roots={}
    for row in ports:
        if sum(x*x for x in row[:8])==16:
            low_roots[tuple(row[8:16])]=row
    ordered_roots=sorted(low_roots)
    require(len(ordered_roots)==120,'Complete low-root set for upper bound')
    upper={'selected_low_block':'(profile+1) mod 3','roots':[list(root) for root in ordered_roots],
           'nine_bit_labels':labels_from_roots([low_roots[r] for r in ordered_roots],0),
           'all_ports_sha256':digest}
    return {'CERTIFICATE.json':{'profiles':profiles},'SAME-CLASS-CONTROL.json':bad,
            'GLOBAL-SCOPE-CONTROL.json':global_scope,
            'FULL-PROFILE-UPPER.json':upper,
            'BUILD.json':{'searches':search,'assignment_seed':78}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for name,data in build().items():
        (args.output/name).write_text(json.dumps(data,indent=2)+'\n')
        print(name)

if __name__=='__main__':main()
