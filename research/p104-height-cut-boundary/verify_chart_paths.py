#!/usr/bin/env python3
"""Tight X=28 witness including all baseline chart cuts and two HS cuts.

This is a separate extension; it does not alter the frozen height/flag
witness. A field is assigned a nested 2-bank path. Paths alone certify all
base directed cuts for every chart subset. Extra HS cuts are tested for two
explicit chart predicates. The witness is still not a legal banked graph.
"""
import collections
from verify_relaxation import load_source, BASE, H, rank_data, cut_test

def line(q): return (1<<0) | (1<<q)
def plane(q,r): return (1<<0) | (1<<q) | (1<<r) | (1<<(q^r))
def dim(c):
    n=c.bit_count()
    assert n and n&(n-1)==0
    return n.bit_length()-1
def hyperplane(q):
    return sum(1<<v for v in range(1<<H) if (v&q).bit_count()%2==0)
def sub(a,b): return a&~b==0

def main():
    ports, non_d, flag=load_source(BASE)
    zero=1
    top=(1<<(1<<H))-1
    lines={line(q) for q in ports}
    hys={hyperplane(q) for q in ports}
    assert len(lines)==len(hys)==104
    # x paths contain the actual line and an actual nested dimension-2 chart.
    xplanes={q:plane(q,ports[(i+1)%len(ports)]) for i,q in enumerate(ports)}
    assert all(dim(p)==2 and sub(line(q),p) and sub(p,top) for q,p in xplanes.items())
    choices=sorted(set(xplanes.values()))
    # Choose each y path's intermediate from the x-plane family when able;
    # the explicit second chart predicate then tests their actual overlap.
    yplanes={}
    for q in ports:
        h=hyperplane(q)
        found=next((p for p in choices if sub(p,h)),None)
        if found is None:
            vec=[v for v in range(1,1<<H) if (v&q).bit_count()%2==0]
            found=plane(vec[0],vec[1])
        assert dim(found)==2 and sub(found,h)
        yplanes[q]=found
    # Keep separate path occurrences for multiple fields (D ports).
    paths=[]
    for idx,q in enumerate(ports):
        for _ in range(1+(idx not in non_d)):
            paths.append((line(q),xplanes[q],top))
            paths.append((zero,yplanes[q],hyperplane(q)))
    assert len(paths)==400
    assert all(sub(a,b) and sub(b,c) and dim(a)<dim(b)<dim(c) for a,b,c in paths)
    banks=[edge for a,b,c in paths for edge in ((a,b),(b,c))]
    for k in range(1,8):
        f=line(flag[k])
        banks.extend([(zero,f),(f,zero)]*2)
    hist=collections.Counter((dim(a),dim(b)) for a,b in banks)
    assert hist=={(1,2):200,(2,9):200,(0,2):200,(2,8):200,(0,1):14,(1,0):14}
    bad,slack,tight=cut_test(hist)
    assert not bad
    # Compute flag-coordinate crossing counts directly from the actual
    # subspaces: d_j(c)=dim(c∩F_{j+1})-dim(c∩F_j).
    fspace=[zero]
    vectors={0}
    for f in flag:
        vectors |= {v^f for v in tuple(vectors)}
        fspace.append(sum(1<<v for v in vectors))
    def dv(c,j):
        return dim(c&fspace[j+1])-dim(c&fspace[j])
    asc=[sum(dv(a,j)<dv(b,j) for a,b in banks) for j in range(H)]
    desc=[sum(dv(a,j)>dv(b,j) for a,b in banks) for j in range(H)]
    need=rank_data(ports,non_d,flag)
    extras=[0]+[2]*7+[0]
    assert asc==[a+b for a,b in zip(need,extras)] and desc==extras
    assert sum(asc)==3214 and sum(desc)==14
    # The first predicate retains x field endpoints, but no 0 or hyperplane.
    # The second also retains ALL x intermediate charts; y paths chosen to
    # overlap those charts must still supply 104 crossings each way.
    fixed1=lines|{top}
    fixed2=fixed1|set(xplanes.values())
    def count(pred):
        bout=sum(a in pred and b not in pred for a,b in banks)
        bin_=sum(a not in pred and b in pred for a,b in banks)
        fout=sum(a in pred and c not in pred for a,b,c in paths)
        fin=sum(a not in pred and c in pred for a,b,c in paths)
        return bout,bin_,fout,fin
    for pred in (fixed1,fixed2):
        assert all(a in pred and c in pred for a,b,c in paths[::2])
        assert all(a not in pred and c not in pred for a,b,c in paths[1::2])
        bo,bi,fo,fi=count(pred)
        assert bo>=fo+104 and bi>=fi+104,(bo,bi,fo,fi)
    matched=sum(1+(i not in non_d) for i,q in enumerate(ports) if yplanes[q] in choices)
    # All singleton base cuts: using distinct chart vertices, independently
    # test bank outgoing against the field source-to-end outgoing demand.
    charts=set([zero,top])
    charts.update(c for p in paths for c in p)
    charts.update(c for edge in banks for c in edge)
    for v in charts:
        bo=sum(a==v and b!=v for a,b in banks)
        fo=sum(a==v and c!=v for a,b,c in paths)
        assert bo>=fo
    # A witness-adaptive paired cut still fails: choose each plane's side to
    # minimize its x/y path crossings. All 104 x endpoint pairs remain inside
    # and their y partners outside, so the full dir_extras needs 104 each way.
    xp=collections.Counter(); yp=collections.Counter()
    for i,q in enumerate(ports):
        w=1+(i not in non_d)
        xp[xplanes[q]]+=w
        yp[yplanes[q]]+=w
    adaptive=fixed1|{p for p in set(xp)|set(yp) if yp[p] <= xp[p]}
    assert all(a in adaptive and c in adaptive for a,b,c in paths[::2])
    assert all(a not in adaptive and c not in adaptive for a,b,c in paths[1::2])
    ac=count(adaptive)
    assert ac==(57,57,0,0) and ac[0]<104 and ac[1]<104,ac
    print('PIN: 6 source hashes verified; #7852 head 41beda1d6435760dc99e38bd7e65f36798aad212')
    print('400 FIELDS: each has a 2-bank nested path through its actual line or hyperplane')
    print('BASE CHART CUTS: valid for all subsets by each-path telescoping; singleton controls',len(charts))
    print('HEIGHT CUTS: 1022/1022 pass, tight',tight,'minimum slack',slack)
    print('FLAG: ascent',asc,'descent',desc)
    print('TWO HS CHART CUTS: (bank out, bank in, field out, field in)',count(fixed1),count(fixed2))
    print('OVERLAPPING Y-PATHS:',matched,'of 200')
    print('BANKS',len(banks),'D=14 R=14 X=28')
    print('OMITTED PAIRED CHART CUT:',ac,'requires +104 in each direction')
    print('SCOPE: no output transfer matrix, coupling for all chart cuts, causality or legal word is supplied')

if __name__=='__main__':
    main()
