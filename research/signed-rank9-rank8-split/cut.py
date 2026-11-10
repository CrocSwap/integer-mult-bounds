"""Independent exact cut, operand rebinding and full-domain split identities."""
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

WORD='34085a6c502ac07530001bdcbc85ad0ec9637f5dda28c9593a0b0d6dd6613d24'
CUT=37412
LO,HI=37403,39691
MOVE=38784
ROLE,PIVOT,FRAME=533,1468,745
A={533:Q(1),1454:Q(-2)}
B={533:Q(1),1468:Q(1),843:Q(-1)}
C={533:Q(1),1251:Q(4),1468:Q(1),1454:Q(-2)}
D={1468:Q(1)}
G=[['ADD',1468,533,'1',3],['ADD',1468,1251,'4',3],['ADD',1468,1454,'-2',3]]
J=[['ADD',533,1468,'-1',745],['ADD',843,1468,'1',745],
   ['ADD',1468,533,'1',745],['ADD',1468,1454,'-2',745]]


def update(v,k,a):
    x=v.get(k,Q(0))+a
    if x:v[k]=x
    else:v.pop(k,None)


def row(vector,events):
    v=vector.copy()
    for e in reversed(events):
        op,r=e[:2]
        a=v.get(r,Q(0))
        if not a or op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            del v[r]
        elif op=='SCALE':
            update(v,r,a*(Q(e[-2])-1))
        elif op=='COPY':
            del v[r]
            update(v,e[2],a*Q(e[-2]))
        elif op=='ADD':
            update(v,e[2],a*Q(e[-2]))
        else:raise AssertionError(op)
    return v


def column(vector,events):
    v=vector.copy()
    for e in events:
        op,r=e[:2]
        if op=='MOVE':continue
        if op in ('INIT','CLEAR'):
            v.pop(r,None)
        elif op=='SCALE':
            update(v,r,v.get(r,Q(0))*(Q(e[-2])-1))
        elif op=='COPY':
            value=Q(e[-2])*v.get(e[2],Q(0))
            v.pop(r,None)
            update(v,r,value)
        elif op=='ADD':
            update(v,r,Q(e[-2])*v.get(e[2],Q(0)))
        else:raise AssertionError(op)
    return v


def operands(e):
    return (1,2) if e[0] in ('ADD','COPY') else (1,)


def inverse(events):
    return [[*e[:-2],str(-Q(e[-2])),e[-1]] for e in reversed(events)]


def span(basis):
    s={0}
    for x in basis:
        assert x not in s
        s|={v^x for v in s}
    return s


def fmt(v):
    return {str(k):str(x) for k,x in sorted(v.items())}


def main(path):
    raw=gzip.decompress(path.read_bytes())
    assert sha256(raw).hexdigest()==WORD
    w=json.loads(raw); seq=w['program']; n=w['public']
    assert n==1481 and w['owned_fields']==51 and len(seq)==71238
    assert seq[MOVE]==['MOVE',533,3,747,False]
    contacts=[i for i in range(LO,HI) if any(seq[i][k]==ROLE for k in operands(seq[i]))]
    assert contacts==[MOVE] and LO<=CUT<MOVE<HI
    chart={r:w['initial'][r] for r in (533,843,1251,1454,1468)}
    for op,r,*args in seq[:CUT]:
        if r not in chart:continue
        if op=='MOVE':
            assert chart[r]==args[0]
            chart[r]=args[1]
        else:
            assert op in ('ADD','COPY','SCALE') and chart[r]==args[-1]
    assert chart=={533:3,843:745,1251:747,1454:745,1468:745}
    assert span(w['frames'][3])<span(w['frames'][745])<span(w['frames'][747])
    assert span(w['frames'][3])<span(w['frames'][745])<span(w['frames'][245])
    assert [len(w['frames'][i]) for i in (3,745,747,245)]==[0,3,6,8]
    h=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    assert not (set(C)|set(D))&h
    assert all((w['initial'][r],w['final'][r])==(3,245) for r in set(C)|set(D))
    assert row(A,seq[:CUT])==C and column(B,seq[CUT:])==D
    at=column(B,seq[CUT:43039])
    assert {r:at.get(r,Q(0)) for r in (843,1123,1468,1480)}=={843:0,1123:0,1468:1,1480:0}
    assert sum(q*B.get(r,0) for r,q in A.items())==sum(q*D.get(r,0) for r,q in C.items())==1
    assert row(D,J)==A and column(B,J)==D
    assert row(D,G)==C and column(D,G)==D
    assert row(D,seq)==D and column(D,seq)==D
    alpha=C.copy()
    del alpha[PIVOT]
    assert row(alpha,seq)==alpha

    def shift(e,successor=False):
        z=e.copy()
        for i in operands(z):
            if z[i]>=n:z[i]+=1
            elif successor and z[i]==PIVOT:z[i]=n
        return z
    rebound=[{'source_index':i,'before':e,'after':shift(e,True)}
             for i,e in enumerate(seq) if i>=CUT and any(e[k]==PIVOT for k in operands(e))]
    inserted={'input':inverse(G),'at_cut':[['MOVE',533,3,745,False]]+J+
              [shift(e,True) for e in inverse(J)]+[['MOVE',533,745,747,False]],
              'output':[shift([*e[:-1],245],True) for e in G]}
    program=inserted['input']+[shift(e) for e in seq[:CUT]]+inserted['at_cut']
    program += [shift(e,True) for i,e in enumerate(seq[CUT:],CUT) if i!=MOVE]
    program += inserted['output']
    final=w['final']+[245]
    final[PIVOT]=745
    new=dict(w,public=n+1,initial=w['initial']+[745],final=final,program=program)
    current=new['initial']+[None]*w['owned_fields']
    old_owned=[]; new_owned=[]
    for i,e in enumerate(program):
        op,r=e[:2]
        if op=='MOVE':
            assert current[r]==e[2] and e[4]==(r>=n+1)
            current[r]=e[3]
        elif op=='INIT':
            assert r>=n+1 and current[r] is None
            current[r]=e[2]
        elif op=='CLEAR':
            assert r>=n+1 and current[r]==e[2]
            current[r]=None
        else:
            assert current[r]==e[-1]
            if op in ('ADD','COPY'):assert current[e[2]]==e[-1]
        if op in ('INIT','CLEAR') or op=='MOVE' and e[4]:
            new_owned.append([op,r-1,*e[2:]])
    for e in seq:
        if e[0] in ('INIT','CLEAR') or e[0]=='MOVE' and e[4]:old_owned.append(e)
    assert current==final+[None]*w['owned_fields'] and old_owned==new_owned
    checked=(533,843,1251,1454,1468,1480,n)
    for r in checked:
        expected=row({r:Q(1)},seq) if r<n else {n:Q(1)}
        expected={i+(i>=n and r<n):x for i,x in expected.items()}
        assert row({r:Q(1)},program)==expected
    def hist(seq):
        out={}
        for e in seq:
            if e[0]=='MOVE':
                rank=abs(len(w['frames'][e[2]])-len(w['frames'][e[3]]))
                out[rank]=out.get(rank,0)+1
        return out
    hh,hn=hist(seq),hist(program)
    assert {r:hn.get(r,0)-hh.get(r,0) for r in set(hh)|set(hn) if hn.get(r,0)!=hh.get(r,0)}=={3:2,6:-1}
    payload=json.dumps(new,sort_keys=True,separators=(',',':')).encode()
    print(json.dumps({'status':'PASS_FULL_DOMAIN_RANK8_SPLIT_CUT_IDENTITIES',
          'independent_emitter_canonical_sha256':sha256(payload).hexdigest(),
          'all_charts_checked':len(program),'explicit_endpoint_rows_checked':checked,
          'owned_motion_events_preserved':len(old_owned),
          'canonical_word_sha256':WORD,'source_events':len(seq),'source_public':n,
          'contact_free_interval':[LO,HI],'old_move_index':MOVE,'insert_before':CUT,
          'old_frames_at_cut':chart,'split_pivot':PIVOT,'new_public_role':n,
          'old_pivot_final':FRAME,'new_initial_final':[FRAME,245],
          'exact_prefix_row':fmt(row(A,seq[:CUT])),'exact_suffix_column':fmt(column(B,seq[CUT:])),
          'existing_split_cut_direction':{str(r):str(at.get(r,0)) for r in (843,1123,1468,1480)},
          'full_old_pivot_row':fmt(row(D,seq)),'full_old_pivot_column':fmt(column(D,seq)),
          'full_old_boundary_adjoint':fmt(row(alpha,seq)),'inserted':inserted,'rebound':rebound,
          'predicted_events':len(seq)+sum(map(len,inserted.values()))-1,
          'paid_delta':{'3':2,'6':-1},'target_delta':{'3':1,'5':1,'8':-1}},indent=2))


if __name__=='__main__':
    main(Path(sys.argv[1]))
