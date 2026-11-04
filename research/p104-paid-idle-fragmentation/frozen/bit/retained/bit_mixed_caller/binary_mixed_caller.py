#!/usr/bin/env python3
"""Complete staged binary mixed-projector caller and exact invoice.

Binary-child recursion adapted from the Apache-2.0 public mixed-projector-
query-root/controller.py (Ali Romman, Cinna Davis, OpenAI Codex; PR6348/6398
lineage). The six-field binary projectors and characteristic-two proof are
newly synthesized here; no dyadic or complex normalizer is imported.
"""
from pathlib import Path
from collections import Counter
from decimal import Decimal,localcontext
from copy import deepcopy
import gzip,json,hashlib,sys,time,argparse
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
from search_binary_root import N,ALL,I,bits,mm,add,rank,inv,span
SOURCE=H/'inputs'/'BIT-NATIVE-WORD.json.gz'
SOURCE_SHA='51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
BODY=7;PORTS=111;KSTAR=Decimal('.00424927762')

def columns_to_matrix(cols):return tuple(sum(((v>>i)&1)<<j for j,v in enumerate(cols))for i in range(N))
def act(P,v):return sum(((r&v).bit_count()%2)<<i for i,r in enumerate(P))

def simultaneous_basis(P,masks):
    cols=[]
    for m in masks:
        vs=[v for v in range(1,64)if all(act(A,v)==(v if m>>j&1 else 0)for j,A in enumerate(P))]
        assert len(vs)==1;cols.append(vs[0])
    F=columns_to_matrix(cols);assert mm(F,inv(F))==I
    return F

def native_basis(P,R,site,r):
    u=(1<<site)if site<6 else ALL;v=(ALL^(1<<site))if site<6 else ALL
    im=sorted({act(P,x)for x in range(64)});ker=[x for x in range(64)if act(P,x)==0]
    w=next(x for x in im if (x&v).bit_count()%2);cols=[u,w]
    for x in im:
        if len(cols)==r:break
        if not (x&v).bit_count()%2 and rank(cols+[x])>len(cols):cols.append(x)
    assert len(cols)==r
    for x in ker:
        if len(cols)==6:break
        if rank(cols+[x])>len(cols):cols.append(x)
    C=columns_to_matrix(cols);ci=inv(C);E=(2,0,0,0,0,0);D=tuple((1<<j)if j<r else 0 for j in range(6))
    assert mm(mm(C,E),ci)==R and mm(mm(C,D),ci)==P
    return C

def best_tree(n,k=.00374459235882726):
    Hh=lambda r:r**(1-k);cost=[0.]*(n+1);trees=[1]*(n+1)
    for q in range(2,n+1):
        val,a=min((cost[a]+cost[q-a],a)for a in range(1,q))
        cost[q]=val+2*Hh(BODY*q)+1-2*Hh(BODY*q+1);trees[q]=[trees[a],trees[q-a]]
    return trees[n]

def construct(sizes=(7,2,2,7)):
    assert len(sizes)==4 and all(isinstance(n,int)and n>0 for n in sizes)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    data=json.loads((H/'BINARY-ROOT-SEARCH.json').read_text());P=[tuple(x)for x in data['roots'][0]['projectors']];R=[tuple(x)for x in data['nilpotents']]
    full=tuple(data['full_sites']);ranks=tuple(data['stage_ranks']);masks=(15,3,12,0,2,4);F=simultaneous_basis(P,masks)
    events=[];targets={};nodes=[];stage=0;next_role=6
    def emit(op,*args):events.append([op,*args])
    def mix(A):
        a=list(A);ops=[]
        for j in range(6):
            k=next(k for k in range(j,6)if a[k]>>j&1)
            if k!=j:a[j],a[k]=a[k],a[j];ops.append(['SWAP',j,k])
            for k in range(6):
                if k!=j and a[k]>>j&1:a[k]^=a[j];ops.append(['ADD',k,j])
        assert tuple(a)==I
        events.extend(reversed(ops))
    def label(tree):
        nonlocal stage
        if tree==1:stage+=1;return dict(stage=stage,stages=[stage])
        a,b=map(label,tree);return dict(left=a,right=b,stages=a['stages']+b['stages'])
    roots=[label(best_tree(n))for n in sizes]
    def supplier(tree,x,y):
        nonlocal next_role
        if 'stage'in tree:emit('LOCAL',tree['stage'],y,x);return
        a,b=next_role,next_role+1;next_role+=2;ss=tree['stages'];nodes.append(dict(roles=[a,b],stages=ss))
        emit('SWAP',x,b);emit('SWAP',y,a);emit('SWAP',a,b)
        emit('ADD',x,a);emit('ADD',b,y);emit('QUERY',a,b);emit('ADD',b,y);emit('ADD',x,a)
        emit('IDLE',a,b,ss)
        supplier(tree['left'],y,x);supplier(tree['right'],x,y)
        emit('ADD',x,a);emit('ADD',a,x);emit('SWAP',y,b);emit('ADD',b,y)
        targets[a]=ss;targets[b]=ss
    mix(F);idx=0;site_bases=[]
    for site in range(7):
        if site in full:
            r=ranks[idx];C=native_basis(P[idx],R[site],site,r);tree=roots[idx];idx+=1
        else:
            # Any rank-two projector onto the nilpotent's native pair works
            # for a thin query; build its basis directly from u and a v=1 row.
            u=1<<site;v=ALL^u;cols=[u,next(x for x in range(1,64)if (x&v).bit_count()%2)]
            for x in range(1,64):
                if not (x&v).bit_count()%2 and rank(cols+[x])>len(cols):cols.append(x)
                if len(cols)==6:break
            C=columns_to_matrix(cols);assert mm(mm(C,(2,0,0,0,0,0)),inv(C))==R[site]
        site_bases.append(C);mix(inv(C))
        if site in full:
            supplier(tree,0,1)
            for r0 in range(2,r):emit('IDLE_ONE',r0,tree['stages'])
        else:emit('QUERY',0,1)
        emit('ADD',0,1);mix(C)
    mix(inv(F))
    for role,m in enumerate(masks):targets[role]=[s for j,tree in enumerate(roots)if m>>j&1 for s in tree['stages']]
    assert stage==sum(sizes)and next_role==2*stage-2
    word=dict(schema='binary-mixed-projector-caller/1',roles=next_role,stages=stage,body_rank=BODY,ports=PORTS,ambient_rank=1+BODY*stage,child_sizes=sizes,child_trees=[best_tree(n)for n in sizes],full_sites=full,stage_ranks=ranks,projectors=P,nilpotents=R,input_basis=F,output_basis=inv(F),site_bases=site_bases,root_masks=masks,nodes=nodes,events=events,diagonal=[dict(q=1,stages=targets[r])for r in range(next_role)],native_source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),scope='Complete staged caller over the retained native interface; binary ordinary ADD/SWAP only, all independent public main roles, unchanged independent native helper families.')
    return word

def replay(word):
    n=word['roles'];width=word['stages']+1;zero=(0,)*width
    rows=[[{zero}if i==j else set()for j in range(n)]for i in range(n)];seen=[]
    def shifted(row,stages=(),q=0):
        out=[]
        for cell in row:
            dst=set()
            for key in cell:
                a=list(key);a[0]^=q
                for s in stages:a[s]+=1
                tup=tuple(a)
                if tup in dst:dst.remove(tup)
                else:dst.add(tup)
            out.append(dst)
        return out
    for e in word['events']:
        op=e[0]
        if op=='ADD':
            _,a,b=e;rows[a]=[x^y for x,y in zip(rows[a],rows[b])]
        elif op=='SWAP':_,a,b=e;rows[a],rows[b]=rows[b],rows[a]
        elif op in('LOCAL','QUERY'):
            if op=='LOCAL':_,s,src,dst=e;seen.append(s)
            else:_,dst,src=e
            rows[dst]=[x^y for x,y in zip(rows[dst],shifted(rows[src],q=1))]
            if op=='LOCAL':rows[src]=shifted(rows[src],[s]);rows[dst]=shifted(rows[dst],[s])
        elif op=='IDLE':
            _,a,b,ss=e;rows[a]=shifted(rows[a],ss);rows[b]=shifted(rows[b],ss)
        elif op=='IDLE_ONE':_,a,ss=e;rows[a]=shifted(rows[a],ss)
        else:raise AssertionError(op)
    expected=[]
    for i,d in enumerate(word['diagonal']):
        key=(1,)+tuple(int(s in d['stages'])for s in range(1,width))
        expected.append([{key}if i==j else set()for j in range(n)])
    assert sorted(seen)==list(range(1,width)),'Native stage multiplicity'
    assert rows==expected,'Complete independent-stage polynomial endpoint'
    return dict(all_public_coefficients=n*n,native_stages=len(seen),events=len(word['events']),polynomial_ring=f'F2[q,D1,...,D{word["stages"]}]/(q^2-1)',stage_variables_are_independent_and_not_assumed_involutions=True,endpoint='diag(q times product of each declared stage subset)')

def invoice(word):
    src=json.loads(gzip.decompress(SOURCE.read_bytes()));ff=src['frames'];p0=Counter(abs(ff[str(e[2])]['dim']-ff[str(e[3])]['dim'])for e in src['program']if e[0]=='MOVE');t0=Counter(abs(ff[str(src['final'][r])]['dim']-ff[str(src['start'][r])]['dim'])for r in range(222,src['public']))
    f=word['stages'];paid=Counter({r:f*n for r,n in p0.items()});targets=Counter({r:f*n for r,n in t0.items()});ops=Counter(e[0]for e in word['events'])
    for e in word['events']:
        if e[0]=='QUERY':paid[1]+=PORTS
        elif e[0]=='IDLE':paid[BODY*len(e[3])]+=2*PORTS
        elif e[0]=='IDLE_ONE':paid[BODY*len(e[2])]+=PORTS
    for d in word['diagonal']:targets[1+BODY*len(d['stages'])]+=PORTS
    def margin(k):return sum(n*r**(1-k)for r,n in targets.items())-sum(n*r**(1-k)for r,n in paid.items())
    a,b=.003,.005
    for _ in range(60):
        m=(a+b)/2
        if margin(m)>0:a=m
        else:b=m
    with localcontext()as ctx:
        ctx.prec=70
        def dmargin(k):return sum(Decimal(n)*Decimal(r)**(1-k)for r,n in targets.items())-sum(Decimal(n)*Decimal(r)**(1-k)for r,n in paid.items())
        checks={str(k):str(dmargin(k))for k in (Decimal('.00374458'),Decimal('.00374459'),Decimal('.00374459235'),Decimal('.0042'),KSTAR)}
    return dict(native_paid_profile=dict(sorted(p0.items())),native_helper_profile=dict(sorted(t0.items())),paid_profile=dict(sorted(paid.items())),productive_profile=dict(sorted(targets.items())),paid_jobs=sum(paid.values()),productive_jobs=sum(targets.values()),paid_rank_mass=sum(r*n for r,n in paid.items()),productive_rank_mass=sum(r*n for r,n in targets.items()),rank_surplus=sum(r*n for r,n in targets.items())-sum(r*n for r,n in paid.items()),event_counts=dict(ops),raw_crossing_float=(a+b)/2,decimal70_margins=checks,largest_paid_rank=max(paid),largest_productive_rank=max(targets),main_public_fields=word['roles']*PORTS,native_public_helpers=f*sum(t0.values()),added_owned_fields=0,scope='Full staged invoice with retained source helper outputs. Decimal margins are high-precision checks, not outward rational interval or outer-transfer admission.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--children',default='7,2,2,7');ap.add_argument('--name',default='BINARY-MIXED-CALLER');args=ap.parse_args()
    sizes=tuple(map(int,args.children.split(',')));assert all(x.isalnum()or x in '_-' for x in args.name)
    t=time.monotonic();word=construct(sizes);receipt=replay(word);neg={}
    for op in('LOCAL','QUERY','IDLE','IDLE_ONE'):
        bad=deepcopy(word);del bad['events'][next(i for i,e in enumerate(bad['events'])if e[0]==op)]
        try:replay(bad)
        except AssertionError as ex:neg[op]=str(ex)
        else:raise AssertionError('Adverse control accepted: '+op)
    raw=json.dumps(word,separators=(',',':')).encode();p=H/(args.name+'.json.gz');p.write_bytes(gzip.compress(raw,mtime=0));bill=invoice(word)
    out=dict(status='PASS_COMPLETE_BINARY_MIXED_CALLER_AND_INVOICE',caller_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),native_source_sha256=word['native_source_sha256'],replay=receipt,adverse_controls=neg,invoice=bill,seconds=time.monotonic()-t,admission_pending=['independent replay','retained physical common-central/body route audit','outward rational moment and outer-transfer ledger'],new_global_kappa_claim=False)
    (H/(args.name+'-RESULT.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
