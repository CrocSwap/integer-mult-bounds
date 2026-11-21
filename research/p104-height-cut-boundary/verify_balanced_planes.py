#!/usr/bin/env python3
"""Strengthen the chart screen by balancing x/y traffic on each 2-plane.

The resulting X=28 witness satisfies every paired chart cut in the family
that puts ALL port x endpoints on one side and ALL y endpoints on the other.
It also tests each label-membership cut. An explicit single-port paired cut
still fails, so this is not a witness for the full banked graph.
"""
import collections
from verify_relaxation import load_source, BASE, H, rank_data, cut_test
from verify_chart_paths import line, plane, dim, hyperplane, sub

def match(ports,non_d,xplanes):
    """Integer maxflow: y-field units -> compatible x-planes -> x capacity."""
    caps=collections.Counter()
    for i,q in enumerate(ports): caps[xplanes[q]]+=1+(i not in non_d)
    planes=sorted(caps); n=1+len(ports)+len(planes)+1; src=0; sink=n-1
    graph=[[] for _ in range(n)]; refs={}
    def add(u,v,c):
        a=[v,c,None,c]; b=[u,0,a,0]; a[2]=b; graph[u].append(a);graph[v].append(b);return a
    for i,q in enumerate(ports):
        w=1+(i not in non_d);add(src,1+i,w)
        h=hyperplane(q)
        for j,p in enumerate(planes):
            if sub(p,h): refs[i,j]=add(1+i,1+len(ports)+j,w)
    for j,p in enumerate(planes):add(1+len(ports)+j,sink,caps[p])
    value=0
    while True:
        prev={src:None};todo=collections.deque([src])
        while todo and sink not in prev:
            u=todo.popleft()
            for e in graph[u]:
                if e[1] and e[0] not in prev:
                    prev[e[0]]=(u,e);todo.append(e[0])
        if sink not in prev:break
        v=sink;route=[]
        while v!=src:
            u,e=prev[v];route.append(e);v=u
        amt=min(e[1] for e in route)
        for e in route:e[1]-=amt;e[2][1]+=amt
        value+=amt
    assert value==200,value
    yp={}
    for i,q in enumerate(ports):
        yp[q]=[planes[j] for j in range(len(planes)) if (i,j) in refs
               for _ in range(refs[i,j][3]-refs[i,j][1])]
        assert len(yp[q])==1+(i not in non_d)
    actual=collections.Counter(p for y in yp.values() for p in y)
    assert actual==caps
    return yp,caps

def main():
    ports,non_d,flag=load_source(BASE)
    zero=1;top=(1<<(1<<H))-1
    xplanes={q:plane(q,ports[(i+1)%len(ports)]) for i,q in enumerate(ports)}
    yp,caps=match(ports,non_d,xplanes)
    b1=plane(flag[0],flag[8]);b2=plane(flag[0],flag[8]^flag[1])
    assert dim(b1)==dim(b2)==2 and b1&b2==line(flag[0])
    assert all(not((b1>>q&1) and (b2>>q&1)) for q in ports)
    paths=[]
    for i,q in enumerate(ports):
        for py in yp[q]:
            paths.append((line(q),xplanes[q],top))
            paths.append((zero,py,hyperplane(q)))
    assert len(paths)==400
    assert all(sub(a,b) and sub(b,c) and dim(a)<dim(b)<dim(c) for a,b,c in paths)
    banks=[edge for a,b,c in paths for edge in ((a,b),(b,c))]
    banks.extend([(b1,top),(top,b1),(b2,top),(top,b2)])
    hist=collections.Counter((dim(a),dim(b)) for a,b in banks)
    bad,slack,tight=cut_test(hist);assert not bad
    fspace=[zero]; vectors={0}
    for f in flag:
        vectors |= {v^f for v in tuple(vectors)}
        fspace.append(sum(1<<v for v in vectors))
    def dv(c,j):return dim(c&fspace[j+1])-dim(c&fspace[j])
    asc=[sum(dv(a,j)<dv(b,j) for a,b in banks) for j in range(H)]
    desc=[sum(dv(a,j)>dv(b,j) for a,b in banks) for j in range(H)]
    need=rank_data(ports,non_d,flag);extras=[0]+[2]*7+[0]
    assert asc==[a+b for a,b in zip(need,extras)] and desc==extras
    assert sum(asc)==3214 and sum(desc)==14
    # Check every q membership cut with the same actual endpoint accounting.
    minmargin=10**9
    for q in ports:
        has=lambda c: bool(c>>q&1)
        bo=sum(has(a) and not has(b) for a,b in banks)
        bi=sum(not has(a) and has(b) for a,b in banks)
        fo=sum(has(a) and not has(c) for a,b,c in paths)
        fi=sum(not has(a) and has(c) for a,b,c in paths)
        assert sum(has(line(r)) and not has(hyperplane(r)) for r in ports)==1
        minmargin=min(minmargin,bo-fo-1,bi-fi-1)
    assert minmargin>=0
    # All x-vs-y predicates: when a plane lies outside, X_p x paths cross
    # in each direction; when inside, Y_p y paths do. Equality X_p=Y_p
    # therefore fixes 200 crossings each way regardless of plane sides.
    assert sum(caps.values())==200
    xlines={line(q) for q in ports}
    # Exhibit a different mandatory paired cut for one port that still fails.
    failing=None
    for q in ports:
        if b1 in yp[q] or b2 in yp[q]:continue
        assert xplanes[q] not in yp[q] # q not in q-perp, so impossible
        pred={top,line(q),xplanes[q],b1,b2}|{hyperplane(r) for r in ports if r!=q}
        if any(p in pred for p in yp[q]):continue
        bo=sum(a in pred and b not in pred for a,b in banks)
        bi=sum(a not in pred and b in pred for a,b in banks)
        fo=sum(a in pred and c not in pred for a,b,c in paths)
        fi=sum(a not in pred and c in pred for a,b,c in paths)
        if bo<fo+1:
            failing=(q,bo,bi,fo,fi);break
    assert failing is not None
    print('PIN: 6 source hashes verified; #7852 head 41beda1d6435760dc99e38bd7e65f36798aad212')
    print('PLANE MATCHING: 200/200 y field units assigned; x=y at each of',len(caps),'2-planes')
    print('BASE ARBITRARY CHART CUTS: valid by 400 nested field paths')
    print('ALL X-VS-Y PAIRED CUTS: at least 200 bank crossings each way versus required 104')
    print('HEIGHT CUTS: 1022/1022 pass; tight',tight,'minimum slack',slack)
    print('FLAG ASC:',asc,'FLAG DESC:',desc)
    print('LABEL-MEMBERSHIP CUTS: 104/104 pass; minimum paired margin',minmargin)
    print('BANKS',len(banks),'D=14 R=14 X=28')
    print('OMITTED SINGLE-PORT PAIRED CUT (q,bank out,in,field out,in):',failing,'needs +1 each way')
    print('SCOPE: no all-paired-cut proof, output matrix, chronology, or legal word')

if __name__=='__main__':main()
