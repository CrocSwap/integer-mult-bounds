"""Separate Boolean/raw interpreter and rational helper-job matching.

The state is all658 original symbols, never just the111 SOURCE symbols.
Frames specify actual ADDRESS pullbacks; equality of VALUE rows alone is
insufficient. The rank7 owned-copy backend is inherited, charged and leased.
"""
from fractions import Fraction as F
from collections import Counter

N=658;V=111
LOCAL={1:1319,2:1342,3:78,4:39,5:102,6:10,7:18}

def need(c,m):
    if not c:raise ValueError(m)

def rank(a):
    a=[[F(v)for v in row]for row in a]
    if not a:return 0
    r=0
    for j in range(len(a[0])):
        k=next((i for i in range(r,len(a))if a[i][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];x=a[r][j];a[r]=[v/x for v in a[r]]
        for i in range(r+1,len(a)):
            if a[i][j]:
                x=a[i][j];a[i]=[v-x*w for v,w in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r

def inverse(a):
    n=len(a);a=[[F(x)for x in row]+[F(i==j)for j in range(n)]for i,row in enumerate(a)]
    for j in range(n):
        k=next(i for i in range(j,n)if a[i][j]);a[j],a[k]=a[k],a[j]
        q=a[j][j];a[j]=[v/q for v in a[j]]
        for i in range(n):
            if i!=j and a[i][j]:
                q=a[i][j];a[i]=[v-q*w for v,w in zip(a[i],a[j])]
    return [row[n:]for row in a]

def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]

def project(frame):
    b=[[F(x)for x in row]for row in frame['B']]
    if not b:return [[F(0)]*8 for _ in range(8)]
    bt=list(map(list,zip(*b)))
    return mm(mm(bt,inverse(mm(b,bt))),b)

def verify(word,frames,reference,reverse=False):
    need(word['active_ordinary_roles']==word['namespace']==N,'Original namespace658')
    need(len(word['start'])==len(word['final'])==N,'All original boundaries')
    need(word['start'][:222]==reference['start'][:222]and word['final'][:222]==reference['final'][:222],
         'Exact main SOURCE/Y interface, including coordinate flags')
    need(all(f==0 for f in word['start'][222:]),'All436 helper inputs start arbitrary and cold')
    expected_helpers=Counter(frames[str(f)]['dim']for f in word['final'][222:])
    need(expected_helpers=={4:4,8:432},'Actual independent partial-target ranks')
    used={f for f in word['start']+word['final']}
    for e in word['records']:
        if e[0]==0:used.update(e[2:4])
        else:used.add(e[4])
    for f in used:
        frame=frames[str(f)];b,a=frame['B'],frame['A'];d=frame['dim']
        need(len(b)==d and len(a)==8-d and rank(b+a)==8,'Complete actual frame bases')
        need(all(sum(x*y for x,y in zip(u,v))==0 for u in b for v in a),'Frame orthogonal complement')
    state=list(word['final']if reverse else word['start'])+[None]
    rows=[1<<i for i in range(N)]+[0]
    lease=None;calls=Counter();copies=adds=0
    iterator=reversed(word['records'])if reverse else iter(word['records'])
    for e in iterator:
        need(len(e)==6,'Literal six-field records')
        op,d,s,c,f,_=e
        need(0<=d<N,'Only ordinary destinations')
        if reverse:
            if op==0:s,c=c,s
            elif op==1:c=-c
            else:op=5-op
        if op==0:
            need(lease is None and state[d]==s,'Current MOVE owner/frame; no live-copy motion')
            low,high=(frames[str(c)],frames[str(s)])if reverse else(frames[str(s)],frames[str(c)])
            need(high['dim']-low['dim']==f and 0<f<8,'Proper actual SOURCE rank')
            need(all(sum(x*y for x,y in zip(u,v))==0 for u in low['B']for v in high['A']),
                 'Nested QQ address projector')
            state[d]=c;calls[f]+=1
        elif op==1:
            need(0<=s<=N and d!=s and c in(-1,1),'Unit signed ADD, interpreted mod2')
            need(state[d]==state[s]==f,'Actual common ADDRESS frame')
            need(d!=lease and(s!=N or lease is not None),'Immutable copy-source lease')
            rows[d]^=rows[s];adds+=1
        elif op==2:
            need(s==N and lease is None and state[N]is None and rows[N]==0,'Owned zero receiver')
            need(state[d]==c and f==0 and frames[str(c)]['dim']==7,'Charged rank7 copy backend')
            lease=d;state[N]=f;rows[N]=rows[d];copies+=1;calls[7]+=1
        else:
            need(op==3 and s==N and lease==d and state[d]==c and state[N]==f,'Actual owned-copy return')
            need(rows[N]==rows[d],'Erasure reconstructs every original input column')
            lease=None;state[N]=None;rows[N]=0
    wanted=[(1<<i)^((1<<(i-V))if V<=i<2*V else 0)for i in range(N)]+[0]
    need(rows==wanted,'All658 independent RAW columns and privatezero')
    need(state==list(word['start']if reverse else word['final'])+[None]and lease is None,'All physical exit frames')
    need(calls==LOCAL and copies==9,'All recursive calls, including owned copies, charged')
    return {'columns':N,'helper_ranks':dict(sorted(expected_helpers.items())),
            'paid':dict(sorted(calls.items())),'COPY_episodes':copies,'unit_ADDs':adds,
            'direction':'inverse'if reverse else'forward'}

def helper_matchers(word,frames):
    out={}
    eye=[[F(i==j)for j in range(8)]for i in range(8)]
    reversal=[[F(i+j==7)for j in range(8)]for i in range(8)]
    def direct_sum(a,b):
        return [row+[F(0)]*8 for row in a]+[[F(0)]*8+row for row in b]
    def physical(p):
        a=[[eye[i][j]-p[i][j]for j in range(8)]for i in range(8)]
        b=mm(p,reversal);c=mm(reversal,p);d=mm(mm(reversal,a),reversal)
        return [a[i]+b[i]for i in range(8)]+[c[i]+d[i]for i in range(8)]
    for role in range(222,N):
        f=word['final'][role]
        if f==1:continue
        frame=frames[str(f)];p=project(frame);k=frame['dim']
        need(k==4 and mm(p,p)==p and rank(p)==4,'Actual physical rank4 idempotent')
        # Image first, kernel second; no Euclidean square-root is needed.
        s=[[F(x)for x in col]for col in zip(*(frame['B']+frame['A']))]
        si=inverse(s);q=[[F(i==j and i<k)for j in range(8)]for i in range(8)]
        need(mm(mm(s,q),si)==p,'Equal-rank whole-job matcher')
        m=direct_sum(s,mm(mm(reversal,s),reversal))
        mi=direct_sum(si,mm(mm(reversal,si),reversal))
        need(mm(mm(mi,physical(p)),m)==physical(q),'Actual reversed-tail16D normalization')
        out[str(role)]={'frame':f,'rank':k,'projector':p,'matcher':s,'matcher_inverse':si,
                       'canonical_input_route_matrix':'matcher_inverse',
                       'canonical_return_route_matrix':'matcher',
                       'physical_reversed_tail_covariance':True,
                       'all_f':'Tensor I_f; C_(8f)=C8 tensor Cf and the two Cf factors cancel.'}
    need(set(out)=={'462','463','466','468'},'Only four changed helper target types')
    return out
