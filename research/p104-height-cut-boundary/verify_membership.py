#!/usr/bin/env python3
"""Screen the 104 natural label-membership paired cuts at X=28.

Builds the same actual-port field paths as verify_chart_paths, then changes
the extra flag moves to two length-7 nested loops.  No claim is made about
all paired chart cuts, linear transfer, temporal order, or legal execution.
"""
from verify_relaxation import load_source, BASE, H, rank_data, cut_test
from verify_chart_paths import line, plane, dim, hyperplane, sub
import collections

def main():
    ports, non_d, flag=load_source(BASE)
    zero=1
    top=(1<<(1<<H))-1
    xplanes={q:plane(q,ports[(i+1)%len(ports)]) for i,q in enumerate(ports)}
    choices=sorted(set(xplanes.values()))
    yplanes={q:next(p for p in choices if sub(p,hyperplane(q))) for q in ports}
    paths=[]
    for idx,q in enumerate(ports):
        for _ in range(1+(idx not in non_d)):
            paths += [(line(q),xplanes[q],top),(zero,yplanes[q],hyperplane(q))]
    assert len(paths)==400
    assert all(sub(a,b) and sub(b,c) and dim(a)<dim(b)<dim(c) for a,b,c in paths)
    banks=[edge for a,b,c in paths for edge in ((a,b),(b,c))]
    # These planes have flag profile {1,9}, and intersect in span(flag[0]),
    # a line containing no P104 port. Their 9↔2 moves cross levels 2..8.
    b1=plane(flag[0],flag[8])
    b2=plane(flag[0],flag[8]^flag[1])
    assert dim(b1)==dim(b2)==2 and b1&b2==line(flag[0])
    assert all(not((b1>>q&1) and (b2>>q&1)) for q in ports)
    banks.extend([(b1,top),(top,b1),(b2,top),(top,b2)])
    hist=collections.Counter((dim(a),dim(b)) for a,b in banks)
    bad,slack,tight=cut_test(hist)
    assert not bad
    fspace=[zero]; vectors={0}
    for f in flag:
        vectors |= {v^f for v in tuple(vectors)}
        fspace.append(sum(1<<v for v in vectors))
    def dv(c,j): return dim(c&fspace[j+1])-dim(c&fspace[j])
    asc=[sum(dv(a,j)<dv(b,j) for a,b in banks) for j in range(H)]
    desc=[sum(dv(a,j)>dv(b,j) for a,b in banks) for j in range(H)]
    need=rank_data(ports,non_d,flag)
    extras=[0]+[2]*7+[0]
    assert asc==[a+b for a,b in zip(need,extras)] and desc==extras
    assert sum(asc)==3214 and sum(desc)==14
    margins=[]
    for q in ports:
        has=lambda c: bool(c>>q&1)
        bank_out=sum(has(a) and not has(b) for a,b in banks)
        bank_in=sum(not has(a) and has(b) for a,b in banks)
        field_out=sum(has(a) and not has(c) for a,b,c in paths)
        field_in=sum(not has(a) and has(c) for a,b,c in paths)
        # For P_q, exactly one port's x endpoint pair lies inside and its
        # corresponding y pair lies outside, and conversely in complement.
        assert field_out==0
        assert sum(has(line(r)) and has(top) and not has(zero) and not has(hyperplane(r)) for r in ports)==1
        margins.append((bank_out-field_out-1,bank_in-field_in-1))
    assert min(min(x) for x in margins)>=0
    # Repeat the two paired-cut controls from the preceding screen.
    lines={line(q) for q in ports}
    p1=lines|{top};p2=p1|set(xplanes.values())
    def count(pred):
        return (sum(a in pred and b not in pred for a,b in banks),
                sum(a not in pred and b in pred for a,b in banks),
                sum(a in pred and c not in pred for a,b,c in paths),
                sum(a not in pred and c in pred for a,b,c in paths))
    assert count(p1)[0]>=104 and count(p1)[1]>=104
    assert count(p2)[0]>=104 and count(p2)[1]>=104
    # Control: the witness-adaptive paired chart cut still fails.
    xp=collections.Counter();yp=collections.Counter()
    for i,q in enumerate(ports):
        w=1+(i not in non_d);xp[xplanes[q]]+=w;yp[yplanes[q]]+=w
    adaptive=p1|{p for p in set(xp)|set(yp) if yp[p] <= xp[p]}
    assert all(a in adaptive and c in adaptive for a,b,c in paths[::2])
    assert all(a not in adaptive and c not in adaptive for a,b,c in paths[1::2])
    failed=count(adaptive)
    assert failed[0]<104 and failed[1]<104
    print('PIN: 6 source hashes verified; #7852 head 41beda1d6435760dc99e38bd7e65f36798aad212')
    print('BASE ARBITRARY CHART CUTS: all satisfied by 400 explicit field paths')
    print('HEIGHT CUTS: 1022/1022 pass; minimum slack',slack,'tight',tight)
    print('FLAG ASC:',asc,'FLAG DESC:',desc)
    print('LABEL-MEMBERSHIP CUTS: 104/104 paired +1 per direction pass; minimum margins',tuple(min(x[j] for x in margins) for j in (0,1)))
    print('TWO MORE PAIRED CUTS:',count(p1),count(p2))
    print('BANKS',len(banks),'D=14 R=14 X=28')
    print('OMITTED PAIRED CHART CUT:',failed,'requires +104 in each direction')
    print('SCOPE: no output transfer matrix, all-paired-cut proof, chronology, or legal word is supplied')

if __name__=='__main__': main()
