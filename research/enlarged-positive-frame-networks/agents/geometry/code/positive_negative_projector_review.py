#!/usr/bin/env python3
"""Independent exact Gram controls for actual enlarged positive frames."""
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse,json,time
from independent_axis_review import read


def mm(A,B):
    return [[sum(x*y for x,y in zip(row,col)) for col in zip(*B)] for row in A]


def check(h,F,sy):
    f=F.bit_count();s=3-f;assert f in (1,2)
    classes=sorted({abs(x) for x in sy if abs(x)>1})
    vectors=[[Q((1 if x>0 else -1) if abs(x)==c else 0) for x in sy] for c in classes]
    sizes=[sum(abs(x) for x in row) for row in vectors]
    sigma=[sum(row) for row in vectors]
    rank=len(classes);V=sum(t*t/k for t,k in zip(sigma,sizes));d=s*s+(f-1)*V
    B=[[s*vectors[c][i]+sigma[c]*Q(F>>i&1) for c in range(rank)] for i in range(h)]
    G=[[Q(i==j)-Q(1,9) for j in range(h)] for i in range(h)]
    BT=list(map(list,zip(*B)))
    gram=[[s*s*sizes[i]*Q(i==j)+(f-1)*sigma[i]*sigma[j] for j in range(rank)] for i in range(rank)]
    inverse=[[Q(i==j,s*s*sizes[i])-(f-1)*sigma[i]*sigma[j]/(s*s*sizes[i]*sizes[j]*d) for j in range(rank)] for i in range(rank)]
    assert mm(mm(BT,G),B)==gram
    assert mm(gram,inverse)==[[Q(i==j) for j in range(rank)] for i in range(rank)]
    P=mm(mm(mm(B,inverse),BT),G)
    t=Q(-4,3*(h+3));v=t/(1+h*t)
    rows=[sum(row) for row in P];cols=[sum(row[j] for row in P) for j in range(h)];total=sum(rows)
    transformed=[[P[i][j]+t*cols[j]-v*rows[i]-t*v*total for j in range(h)] for i in range(h)]
    D=[[sum(a[i]*a[j]/k for a,k in zip(vectors,sizes)) for j in range(h)] for i in range(h)]
    u=[sum(q*a[i]/k for a,k,q in zip(vectors,sizes,sigma)) for i in range(h)]
    w=[Q(F>>i&1)-Q(4,h+3) for i in range(h)]
    z=[Q(F>>i&1)+1 for i in range(h)]
    formula=[[D[i][j]+(s*u[i]*z[j]+s*w[i]*u[j]+V*w[i]*z[j]-(f-1)*u[i]*u[j])/d for j in range(h)] for i in range(h)]
    assert formula==transformed
    K=lcm(*(int(k) for k in sizes));dnum=int(d*K);denominator=(h+3)*K*dnum
    assert d*K==dnum
    assert all((x*denominator).denominator==1 for row in transformed for x in row)
    assert all(abs(x)<=2*h+8 for row in transformed for x in row)
    assert mm(transformed,transformed)==transformed
    return dict(forced=F,symbols=sy,rank=rank,class_sizes=list(map(int,sizes)),class_sums=list(map(int,sigma)),
                K=K,dnum=dnum,clearing_denominator=denominator,
                explicit_gram_inverse_pass=True,complete_rational_projector_equals_formula=True,idempotence_pass=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--witness',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--all',action='store_true');args=ap.parse_args()
    start=time.monotonic();document=json.loads(args.witness.read_text());record=document.get('producer',document)
    dag=Path(record['dag_path']);labels=Path(str(dag)+'.positive')
    h,v,n,q,operands,core,cover,roots,kind,active,ranks,forced,symbols=read(dag,labels)
    unique={}
    for node in range(1,n):
        if active[node] and operands[2*node] and forced[node].bit_count() in (1,2):
            sy=tuple(symbols[node*h:(node+1)*h]);class_sizes={c:sum(abs(x)==c for x in sy) for c in set(abs(x) for x in sy) if c>1}
            key=(forced[node],sy) if args.all else (forced[node].bit_count(),max(class_sizes.values()),any(x<0 for x in sy))
            if key not in unique:unique[key]=(forced[node],sy)
    chosen=list(unique.items()) if args.all else sorted(unique.items(),key=lambda row:(-row[0][1],row[0]))[:8]
    cases=[]
    for at,(key,(F,sy)) in enumerate(chosen):
        cases.append(check(h,F,list(sy)))
        if (at+1)%25==0:print(json.dumps({'completed_frames':at+1,'total_frames':len(chosen),'elapsed_seconds':time.monotonic()-start}),flush=True)
    assert cases
    result=dict(status='PASS ACTUAL POSITIVE-FRAME NEGATIVE-BASIS GRAM CONTROLS',h=h,cases=cases,
                elapsed_seconds=time.monotonic()-start,completed_utc=datetime.now(timezone.utc).isoformat(),
                input_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.witness,dag,labels)},
                source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                all_distinct_addition_frames=args.all,
                scope='Actual rational positive projectors; complete physical multiset and per-matrix minor bounds remain separate')
    assert not args.output.exists();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','h','elapsed_seconds')}),flush=True)
