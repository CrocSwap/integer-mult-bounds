"""Enumerate constant-value delivery windows and exact frame-domain candidates."""
import json,gzip,copy,itertools,time,contextlib,io
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
import eliminate_helpers as E
P,ROOT,w,S,A=E.P,E.ROOT,E.w,E.S,E.A
FULL=S.M.FULL
@lru_cache(None)
def join(a,b):return A.basis(a+b)
@lru_cache(None)
def meet(a,b):return S.M.meet(a,b)
def inside(a,b):return join(a,b)==b

def windows(h):
    n=704;cur=[(p,) for p in w['ports']]+[()]*(n-112)
    for q,fr in w['start_extra'].items():cur[int(q)]=A.basis(fr)
    cur[h]=()
    for e in w['A']:
        rs=A.registers(e);U=cur[rs[0]]
        for r in rs[1:]:U=join(U,cur[r])
        for r in rs:cur[r]=U
    for q,fr in zip(w['centers'],w['center_frames']):
        assert inside(cur[q],A.basis(fr));cur[q]=A.basis(fr)
    lo=[]
    for e in w['B']:
        lo.append(cur.copy())
        if h in A.registers(e):continue
        rs=A.registers(e);U=cur[rs[0]]
        for r in rs[1:]:U=join(U,cur[r])
        for r in rs:cur[r]=U
    lo.append(cur.copy())
    hi=[FULL]*112+[A.basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[FULL]*480
    for q,fr in w['helper_final'].items():hi[int(q)]=A.basis(fr)
    hi[h]=()
    for i,fr in reversed(w['early_cleanup']):
        e=w['cleanup'][i]
        if h in A.registers(e):continue
        rs=A.registers(e);U=hi[rs[0]]
        for r in rs[1:]:U=meet(U,hi[r])
        for r in rs:hi[r]=U
    after=[hi.copy()]
    for e in reversed(w['B']):
        if h not in A.registers(e):
            rs=A.registers(e);U=hi[rs[0]]
            for r in rs[1:]:U=meet(U,hi[r])
            for r in rs:hi[r]=U
        after.append(hi.copy())
    return lo,list(reversed(after))

def move(vec,e,forward):
    u=defaultdict(F,vec)
    if 112<=e[1]<224:
        if e[0]=='scale':u[e[1]]=u[e[1]]*F(e[2],e[3]) if forward else u[e[1]]/F(e[2],e[3])
        elif 112<=e[2]<224:u[e[1]]+=(1 if forward else -1)*F(e[3],e[4])*u[e[2]]
    return {t:q for t,q in u.items() if q}

def deliveries(h,r,lo,hi):
    pos=r['B'];src=r['old'][2];v={e[1]:F(e[3],e[4]) for e in r['new']};B=w['B']
    left=max([-1]+[i for i,e in enumerate(B[:pos]) if e[1]==src])+1
    right=min([len(B)]+[i for i,e in enumerate(B) if i>=pos and e[1]==src])
    vectors={pos:v};cur=v
    for i in range(pos-1,left-1,-1):cur=move(cur,B[i],False);vectors[i]=cur
    cur=v
    for i in range(pos,right):cur=move(cur,B[i],True);vectors[i+1]=cur
    found=[];seen=set();tested=0
    for at,vec in sorted(vectors.items()):
        assert len(vec)<=8
        for order in itertools.permutations(sorted(vec)):
            tested+=1;f=lo[at][src];gates=[];valid=True
            for t in order:
                f=join(f,lo[at][t])
                if not inside(f,hi[at][src]) or not inside(f,hi[at][t]):valid=False;break
                q=vec[t];gates.append(['add',t,src,q.numerator,q.denominator,list(f)])
            if valid:
                key=tuple((g[1],g[3],g[4],tuple(g[-1])) for g in gates)+(tuple(hi[at][src]),)
                if key not in seen:found.append(dict(position=at,gates=gates));seen.add(key)
    return dict(source=src,original_position=pos,left=left,right=right,placements_tested=tested,candidates=found)

if __name__=='__main__':
    results=[]
    for old in json.loads((P/'PRODUCER-ELIMINATION.json').read_text()):
        h=old['helper'];t0=time.monotonic()
        try:
            _,recipe=E.eliminate(w,h);lo,hi=windows(h);ds=[deliveries(h,r,lo,hi) for r in recipe]
            r=dict(helper=h,status='NO_ADMITTED_REPLACEMENT',deliveries=ds,combinations_tested=0,local_pass=[])
            options=[d['candidates'] for d in ds]
            for combo in itertools.product(*options):
                r['combinations_tested']+=1;schedule=defaultdict(list)
                for c in combo:schedule[c['position']]+=c['gates']
                try:
                    nw,_=E.eliminate(w,h,schedule);nw=S.optimize(nw);path=P/f'scheduled-{h}-{r["combinations_tested"]}.json.gz';path.write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0))
                    with contextlib.redirect_stdout(io.StringIO()):A.run(path,path.with_suffix('.AUDIT.json'),ROOT)
                    rr=dict(path=path.name,schedule=dict(schedule),profile=nw['report']['local_profile'],**S.screen(nw));r['local_pass'].append(rr);r['status']='PASS_EXACT_LOCAL';print('FOUND',json.dumps(rr),flush=True)
                except (AssertionError,RuntimeError,ValueError) as e:r['last_rejection']=str(e)
                if r['combinations_tested']>=100:r['combination_limit']=100;break
        except (AssertionError,RuntimeError,ValueError) as e:r=dict(helper=h,status='REJECTED_PRECONDITION',reason=str(e))
        r['seconds']=time.monotonic()-t0;results.append(r);print({k:v for k,v in r.items() if k not in ['deliveries','local_pass']},'candidate counts',[len(d['candidates']) for d in r.get('deliveries',[])],flush=True)
        (P/'SCHEDULED-ELIMINATION.json').write_text(json.dumps(results,indent=2)+'\n')
