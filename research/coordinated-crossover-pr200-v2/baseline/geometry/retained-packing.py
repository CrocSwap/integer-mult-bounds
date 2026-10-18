"""Exact gauge charts and completed-residual bank allocation.

Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from array import array
from collections import Counter
from fractions import Fraction as Q
from math import gcd
from pathlib import Path
import hashlib,json,sys

def inverse_integer(a):
    """Fraction-free Gauss-Jordan; return integral C,d with a C = d I."""
    n=len(a)
    m=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    previous=1
    factors=[]
    for k in range(n):
        pivot=next((i for i in range(k,n) if m[i][k]),None)
        if pivot is None:
            raise ValueError('Singular basis')
        m[k],m[pivot]=m[pivot],m[k]
        if pivot != k:factors.append(('swap',k,pivot,1,1))
        p=m[k][k]
        if p != previous:
            ratio=Q(previous,p)
            factors.append(('scale',k,k,ratio.numerator,ratio.denominator))
        for i in range(n):
            if i==k:continue
            u=m[i][k]
            if u:
                ratio=Q(-u,previous)
                factors.append(('add',i,k,ratio.numerator,ratio.denominator))
            for j in range(2*n):
                if j==k:continue
                value=p*m[i][j]-u*m[k][j]
                assert value % previous==0
                m[i][j]=value//previous
            m[i][k]=0
        previous=p
    d=m[0][0]
    assert d and all(m[i][j]==d*int(i==j) for i in range(n) for j in range(n))
    c=[row[n:] for row in m]
    common=abs(d)
    for row in c:
        for x in row:common=gcd(common,x)
    d//=common
    c=[[x//common for x in row] for row in c]
    if d<0:d=-d;c=[[-x for x in row] for row in c]
    return c,d,factors

def color_incidence(left,right,nleft,nright,colors):
    """Incremental two-color swaps; parallel edges are identified separately."""
    assert len(left)==len(right)
    full=(1<<colors)-1
    lf=[full]*nleft;rf=[full]*nright
    lc=[array('i',[-1])*colors for _ in range(nleft)]
    rc=[{} for _ in range(nright)]
    labels=array('i',[-1])*len(left)
    swaps=longest=0
    def remove(e):
        u,v,c=left[e],right[e],labels[e]
        assert lc[u][c]==e and rc[v][c]==e
        lc[u][c]=-1;del rc[v][c]
        lf[u]|=1<<c;rf[v]|=1<<c
    def add(e,c):
        u,v=left[e],right[e]
        assert lf[u]&(1<<c) and rf[v]&(1<<c)
        labels[e]=c;lc[u][c]=e;rc[v][c]=e
        lf[u]&=~(1<<c);rf[v]&=~(1<<c)
    for e,(u,v) in enumerate(zip(left,right)):
        common=lf[u]&rf[v]
        if common:
            add(e,(common&-common).bit_length()-1)
            continue
        assert lf[u] and rf[v]
        a=(lf[u]&-lf[u]).bit_length()-1
        b=(rf[v]&-rf[v]).bit_length()-1
        path=[];r=u
        while True:
            edge=lc[r][b]
            if edge<0:break
            path.append(edge);bank=right[edge]
            assert bank!=v
            edge=rc[bank].get(a,-1)
            if edge<0:break
            path.append(edge);r=left[edge]
        changes=[(edge,b if labels[edge]==a else a) for edge in path]
        for edge,_ in changes:remove(edge)
        for edge,c in changes:add(edge,c)
        add(e,b)
        swaps+=1;longest=max(longest,len(path))
    return labels,{'swaps':swaps,'longest_swapped_path':longest}

def check_coloring(left,right,labels,nleft,nright,colors,full_left=False):
    assert len(left)==len(right)==len(labels)
    lm=[0]*nleft;rm=[0]*nright
    for u,v,c in zip(left,right,labels):
        assert 0<=u<nleft and 0<=v<nright and 0<=c<colors
        bit=1<<c
        assert not lm[u]&bit and not rm[v]&bit
        lm[u]|=bit;rm[v]|=bit
    if full_left:assert all(mask==(1<<colors)-1 for mask in lm)

def build(BIT):
    sys.path.insert(0,str(BIT/'scripts'))
    import paired_cube_bit_physical as P
    chk=P.loaded();chk.frames()
    wordpath=BIT/'build/source-assisted-bit-bootstrap/emitted-word.json'
    w=json.loads(wordpath.read_text())
    receipt=json.loads((BIT/'build/source-assisted-bit-bootstrap/emitted-physical.json').read_text())
    assert hashlib.sha256(wordpath.read_bytes()).hexdigest()==receipt['word_sha256']
    R=w['R'];donors={a for a,b in w['pairs']};recipients={b for a,b in w['pairs']};gauges={z['role']:z for z in w['gauges']}
    assert len(donors)==len(recipients)==len(w['pairs'])==1760
    assert not donors&recipients and not donors&gauges.keys() and recipients<=gauges.keys()
    physical=sorted(set(range(R))-recipients);ren={r:i for i,r in enumerate(physical)}
    assert len(physical)==receipt['physical_R']==17588
    selected=set(gauges)-recipients
    assert len(selected)==2200 and {gauges[r]['dim'] for r in selected}=={20}
    assert {gauges[r]['dim'] for r in recipients}=={21}
    # Interior rank-21 recipient starts are already paid splices, not entrance residuals.
    inventory=Counter(gauges[r]['frame'] for r in selected)
    digest=hashlib.sha256();maxops=maxnum=maxden=0
    for f,count in sorted(inventory.items()):
     A=chk.A[f];source=chk.B[f];assert len(A)==4 and len(source)==20
     residual=[]
     for a in A:
      row=[15*x-sum(a) for x in a];d=gcd(*row);residual.append([x//d for x in row])
     assert all(9*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b)==0 for a in residual for b in source)
     B=list(map(list,zip(*(residual+source))))
     C,d,ops=inverse_integer(B)
     for left,right in ((B,C),(C,B)):
      assert all(sum(x*y for x,y in zip(row,col))==d*int(i==j) for i,row in enumerate(left) for j,col in enumerate(zip(*right)))
     replay=[list(map(Q,row)) for row in B]
     for op,i,j,num,den in ops:
      if op=='swap':replay[i],replay[j]=replay[j],replay[i]
      elif op=='scale':replay[i]=[Q(num,den)*x for x in replay[i]]
      else:
       assert op=='add';replay[i]=[x+Q(num,den)*y for x,y in zip(replay[i],replay[j])]
     assert all(x==int(i==j) for i,row in enumerate(replay) for j,x in enumerate(row))
     maxops=max(maxops,len(ops));maxnum=max(maxnum,max(abs(op[3]) for op in ops));maxden=max(maxden,d,max(op[4] for op in ops))
     digest.update(json.dumps([f,count,B,C,d,ops],separators=(',',':')).encode())
    assert max(maxnum,maxden)<2**80
    families={4:sorted(selected),24:sorted(set(physical)-selected)}
    degree=9;copies=3;small=degree*len(selected)//6
    assert 6*small==degree*len(selected)
    large=(degree*len(families[24])-2*small)//3
    assert 3*large+2*small==degree*len(families[24])
    left=[];right=[];offsets=[];counts=Counter();bank=0
    for pattern,n in (({4:6,24:2},small),({24:3},large)):
     for _ in range(n):
      offset=0
      for rank,mult in sorted(pattern.items()):
       for _ in range(mult):
        role=families[rank][counts[rank]//degree]
        left.append(ren[role]);right.append(bank);offsets.append(offset);counts[rank]+=1;offset+=rank
      assert offset==72
      bank+=1
    assert all(counts[r]==degree*len(rs) for r,rs in families.items())
    labels,stats=color_incidence(left,right,len(physical),bank,degree)
    check_coloring(left,right,labels,len(physical),bank,degree,full_left=True)
    first={};rejected=False
    for e,r in enumerate(left):
     if r not in first:first[r]=e;continue
     old=labels[e];labels[e]=labels[first[r]]
     try:check_coloring(left,right,labels,len(physical),bank,degree,full_left=True)
     except AssertionError:rejected=True
     finally:labels[e]=old
     break
    assert rejected
    incidence=hashlib.sha256()
    for r,b,c,o in zip(left,right,labels,offsets):incidence.update(f'{r},{b},{c},{o}\n'.encode())
    H=Counter({int(r):copies*n for r,n in receipt['child_histogram'].items()})
    assert H.pop(60)==copies*len(selected)
    assert not any(r>22 for r in H)
    W=2*w['v']*copies+bank;mass=sum(r*n for r,n in H.items())
    assert 72*W-mass==copies*receipt['deficit_per_vertex']==5808
    K=18*((W-1)+len(physical)*72*(maxops+71))
    record=dict(status='PASS exact actual-chain chart and incidence checks',source_commit='201737a1ec4f936e166e2481fb9e88104cb2ccc7',
     word_sha256=receipt['word_sha256'],physical_roles=len(physical),interior_splices=len(recipients),gauge_roles=len(selected),
     distinct_gauges=len(inventory),copies=copies,banks=bank,patterns=[dict(rank4=6,rank24=2,count=small),dict(rank4=0,rank24=3,count=large)],
     incidences=len(left),W=W,m=72,rank_mass=mass,deficit=5808,maxchild=max(H),child_histogram=dict(sorted(H.items())),
     chart_sha256=digest.hexdigest(),incidence_sha256=incidence.hexdigest(),max_chart_factors=maxops,max_num=maxnum,max_den=maxden,
     conservative_selector_calls=K,color_stats=stats,conflicting_assignment_rejected=rejected)

    return record
