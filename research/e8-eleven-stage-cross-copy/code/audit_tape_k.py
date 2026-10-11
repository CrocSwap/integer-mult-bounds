# Independent ownership/window audit, extending DaysSky PR442, chafreaky PR444 (OpenAI Codex) and higherbeing PR448 (cross-copy
# pieces); no generator imports.
# Generalised to an arbitrary odd stage count, any replica count and host-every-residual templates by DreamingOfClouds with
# Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
"""Independent ownership/window audit of a CROSS-COPY idle-axis-hosted compressed S-stage bit template (pieces on one or two
copies of one idle child, PR #448).
Usage: audit_tape_k.py PARENT_DIR HOSTED_DIR OUT.json [--nine SUBDIR] [--records SUBDIR]
PARENT_DIR holds the parent's records/ and nine/-style GLOBAL files via --parent-nine (default PARENT_DIR/nine).
At the nine-stage defaults this performs PR #444's checks and fourteen mutations; at S = 11 the mutations that need a
bank are replaced by stage-count, window and exterior-coordinate controls."""
import copy, gzip, hashlib, json, sys
from collections import Counter, defaultdict
from pathlib import Path
V=120
read=lambda p:json.loads(Path(p).read_text())
template=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()))

def windows(schedule):
    last={}; seen=[]; win={}; rank={}; pair={}
    for pos,e in enumerate(schedule):
        if e['kind']=='local_cover_sweep':
            seen.append((pos,e['stage'],e['pair']));last[e['pair']]=pos
        elif e['kind']=='bridge':
            last[e['dst']]=pos;last[e['src']]=pos
        elif e['kind']=='exchange':
            assert pos==len(schedule)-1
        else:
            assert e['kind']=='idle'
            i=e['idx'];assert i not in win
            win[i]={s for q,s,p in seen if last.get(e['pair'],-1)<q<pos and p!=e['pair']}
            rank[i]=e['rank'];pair[i]=e['pair']
    return win,rank,pair

def audit(t,parent,widths,depth):
    L,T,M=t['stages'],t['replicas'],t['m']; K=(L-1)//2; R=len(widths); DATA=2*K*V*T; DEFICIT=T*(2*K*V-9*8*L)
    assert L>=5 and L%2==1 and M==1+7*L
    mutable={'version','live','banks_per_stage','hosting','helper_route','calls','schedule'}
    assert set(t)==set(parent)|{'hosting'}
    assert {k:v for k,v in t.items() if k not in mutable}=={k:v for k,v in parent.items() if k not in mutable}
    assert t['replicas']==T and t['m']==M and t['private_centre_reserve']==9
    sched=copy.deepcopy(parent['schedule']);idx=0
    for e in sched:
        if e['kind']=='idle':e['idx']=idx;idx+=1
    assert t['schedule']==sched
    W,rank,pair=windows(t['schedule']);hs=t['hosting']
    assert hs['windows']=={str(i):[pair[i],rank[i],sorted(W[i])] for i in W if rank[i]>0 and W[i]}
    used=defaultdict(set);hosted={}
    for s,h,i,segs in hs['pieces']:
        assert i in W and s in W[i] and 0<=s<L and 0<=h<R and 1<=len(segs)<=2
        assert sum(w for _,_,w in segs)==widths[h]>0 and all(w>0 for _,_,w in segs)
        if len(segs)==2:     # a residual straddles exactly one boundary of the tape: end of copy c, start of copy c+1
            (c1,o1,w1),(c2,o2,w2)=segs;assert c2==c1+1 and o2==0 and o1+w1==rank[i]
        for cp,off,w in segs:
            assert 0<=cp<2*V and 0<=off and off+w<=rank[i]
            cells=set(range(off,off+w));assert not cells & used[i,cp];used[i,cp]|=cells
        assert (s,h) not in hosted;hosted[s,h]=(i,segs)
    rem={};summaries={}
    for i in rank:
        if not rank[i]:continue
        for cp in range(2*V):rem[i,cp]=rank[i]-len(used[i,cp])
        if str(i) in hs['windows']:
            summaries[str(i)]={str(r):n for r,n in sorted(Counter(rem[i,cp] for cp in range(2*V)).items())}
    assert hs['remainders']==summaries
    banks={int(s):n for s,n in hs['banks_per_stage'].items()}
    assert set(banks)==set(range(L)) and all(isinstance(n,int) and n>=0 for n in banks.values())
    tb=t['banks_per_stage'];assert tb==parent['banks_per_stage'] or {int(s):n for s,n in tb.items()}==banks   # nine-stage parent: PR #448 keeps the parent's field
    base={};end=DATA
    for s in range(L):base[s]=end;end+=banks[s]
    assert t['live']==end
    assert len(t['calls'])==L*T and len(parent['calls'])==L*T
    occ=defaultdict(set);bank_count=0;host_count=0
    assert {(c['stage'],c['replica']) for c in t['calls']}=={(s,r) for s in range(L) for r in range(T)}
    for c,pc in zip(t['calls'],parent['calls']):
        assert {k:v for k,v in c.items() if k!='owners'}=={k:v for k,v in pc.items() if k!='owners'}
        s,rep,p=c['stage'],c['replica'],c['pair'];own=c['owners']
        assert len(own)==2*V+R and own[:2*V]==pc['owners'][:2*V]
        for h,(f,r) in enumerate(own[2*V:]):
            if (s,h) in hosted:
                i,segs=hosted[s,h];fam=lambda cp:rep*(2*K*V)+(2*pair[i]+cp//V)*V+cp%V
                assert pair[i]!=p
                if len(segs)==1:
                    cp,off,w=segs[0];assert r==['hosted',i,off,w] and f==fam(cp)
                else:
                    (c1,o1,w1),(c2,o2,w2)=segs;assert r==['hosted-split',i,o1,w1,fam(c2),o2,w2] and f==fam(c1)
                assert 0<=f<DATA;host_count+=1
            else:
                assert len(r)==3 and r[0]=='bank' and r[2]==widths[h]
                assert base[s]<=f<base[s]+banks[s]
                assert 0<=r[1] and r[1]+r[2]<=M
                cells=set(range(r[1],r[1]+r[2]));assert not cells & occ[f];occ[f]|=cells
                bank_count+=1
    assert set(occ)==set(range(DATA,end)) and all(x==set(range(M)) for x in occ.values())
    assert host_count==len(hosted)*T and host_count+bank_count==L*T*R
    paid=Counter()
    for c in t['calls']:
        for z in t['local_programs'][c['orientation']]:
            if z[0]==0 and z[4]:paid[z[4]]+=1
            if z[0]==2:paid[z[5]]+=1
    for r in rem.values():
        if r:paid[r]+=T
    assert M*end-sum(r*n for r,n in paid.items())==DEFICIT
    assert M**depth>2*max(paid)**depth
    split_count=sum(1 for _,segs in hosted.values() if len(segs)==2)*T
    return paid,host_count,bank_count,split_count

def digest(t):
    # Independent streamed hashing uses the same specified JSON instruction format.
    h=hashlib.sha256();n=0;R=len(t['calls'][0]['owners'])-2*V
    for call in t['calls']:
        for z in t['local_programs'][call['orientation']]:
            x=[z[0],call['owners'][z[1]]]
            if z[0]==0:x.extend(z[2:])
            else:
                x.append(call['owners'][z[2]] if z[2]<2*V+R else [t['live'],['private',0]])
                x.extend(z[3:])
            h.update(json.dumps(x,separators=(',',':')).encode());h.update(b'\n');n+=1
    return h.hexdigest(),n

def main():
    opt={sys.argv[i]:sys.argv[i+1] for i in range(1,len(sys.argv)-1) if sys.argv[i].startswith('--')}
    pos=[x for x in sys.argv[1:] if not x.startswith('--') and x not in opt.values()]
    par,bd,out=map(Path,pos[:3]);nine=opt.get('--nine','nine');rec=opt.get('--records','records')
    pt=template(par/nine/'GLOBAL-TEMPLATE.json.gz')
    t=template(bd/'GLOBAL-TEMPLATE.json.gz');g=read(bd/'GLOBAL.json');pg=read(par/nine/'GLOBAL.json')
    st=read(par/rec/'249-states.json');frames=read(par/rec/'frames.json')['frames']
    L=t['stages'];T=t['replicas'];M=t['m'];K=(L-1)//2;R=pg['R'];depth=g['halving_depth'];DATA=2*K*V*T
    widths=[8-frames[str(st['initial'][str(h)])]['dim'] for h in range(2*V,2*V+R)]
    P,host,bank,split=audit(t,pt,widths,depth)
    th=hashlib.sha256(gzip.decompress((bd/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
    assert th==g['template_sha256'] and g['parent_template_sha256']==pg['template_sha256']
    assert P==Counter({int(r):n for r,n in g['profile'].items()})
    DEFICIT=T*(2*K*V-9*8*L)
    assert (g['live'],g['physical'],g['rank_mass'],g['deficit'],g['paid_calls'],g['maxchild'])==(t['live'],t['live']+9,sum(r*n for r,n in P.items()),DEFICIT,sum(P.values()),max(P))
    assert g['hosted_residuals']==host and g['bank_assignments']==bank and g['split_residuals']==split
    dg,n=digest(t);assert dg==g['emitted_program_sha256'] and n==g['emitted_events']==pg['emitted_events']
    assert dg!=pg['emitted_program_sha256']
    controls=[]
    def reject(name,fn):
        q=copy.deepcopy(t);fn(q)
        try:audit(q,pt,widths,depth)
        except (AssertionError,KeyError,IndexError,TypeError):controls.append(name)
        else:raise AssertionError('accepted '+name)
    def owner(q,kind):
        return next(o for c in q['calls'] for o in c['owners'][2*V:] if o[1][0]==kind)
    Wd,rk,pr=windows(t['schedule'])
    pcs=lambda q:q['hosting']['pieces']
    first_split=lambda q:next(pc for pc in pcs(q) if len(pc[3])==2)
    def outside_stage(q):
        pc=pcs(q)[0];pc[0]=next(x for x in range(L) if x not in Wd[pc[2]])
    reject('piece outside window',outside_stage)
    reject('copy index outside family',lambda q:pcs(q)[0][3][0].__setitem__(0,2*V))
    reject('negative piece offset',lambda q:pcs(q)[0][3][0].__setitem__(1,-1))
    reject('wrong residual width',lambda q:pcs(q)[0][3][0].__setitem__(2,1+pcs(q)[0][3][0][2]))
    reject('duplicate helper',lambda q:pcs(q).append(pcs(q)[0]))
    reject('omitted helper',lambda q:pcs(q).pop())
    reject('hosted owner in another replica or outside the data stock',lambda q:owner(q,'hosted').__setitem__(0,owner(q,'hosted')[0]+2*K*V))
    reject('hosted owner on a wrong data family',lambda q:owner(q,'hosted').__setitem__(0,q['calls'][0]['owners'][0][0]))
    reject('split pieces on non-adjacent copies',lambda q:first_split(q)[3][1].__setitem__(0,first_split(q)[3][1][0]+1))
    reject('split piece widths do not sum to the residual width',lambda q:first_split(q)[3][1].__setitem__(2,first_split(q)[3][1][2]+1))
    reject('split residual keeps only its first piece',lambda q:first_split(q)[3].pop())
    reject('split owner record changed',lambda q:owner(q,'hosted-split')[1].__setitem__(3,owner(q,'hosted-split')[1][3]+1))
    if bank:
        reject('wrong bank slot',lambda q:owner(q,'bank')[1].__setitem__(1,M))
        reject('wrong bank stage',lambda q:owner(q,'bank').__setitem__(0,t['live']-1))
    reject('wrong call orientation',lambda q:q['calls'][0].__setitem__('orientation','reverse'))
    reject('duplicate call',lambda q:q['calls'].__setitem__(1,q['calls'][0]))
    reject('changed idle rank',lambda q:next(e for e in q['schedule'] if e['kind']=='idle').__setitem__('rank',1))
    reject('understated live stock',lambda q:q.__setitem__('live',q['live']-1))
    reject('missing remainder summary',lambda q:q['hosting']['remainders'].pop(next(iter(q['hosting']['remainders']))))
    reject('stale stage count',lambda q:q.__setitem__('stages',L-2))
    reject('hosted coordinate beyond the pending set',lambda q:pcs(q)[0][3][0].__setitem__(1,rk[pcs(q)[0][2]]))
    reject('overlapping hosted coordinates',lambda q:pcs(q).append(pcs(q)[0][:1]+[(pcs(q)[0][1]+1)%R]+pcs(q)[0][2:]))
    res=dict(status='PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT',template_sha256=th,emitted_program_sha256=dg,emitted_events=n,
             profile={str(r):z for r,z in sorted(P.items())},live=t['live'],physical=t['live']+9,hosted_residuals=host,
             bank_assignments=bank,split_residuals=split,rank_mass=sum(r*n for r,n in P.items()),deficit=DEFICIT,maxchild=max(P),mutations_rejected=controls)
    out.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
if __name__=='__main__':main()
