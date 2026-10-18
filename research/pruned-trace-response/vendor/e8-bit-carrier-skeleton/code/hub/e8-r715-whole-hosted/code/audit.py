"""Independent eleven-stage schedule, geometry embedding and hosted ownership audit.
Derived from PR386/436/443/444 and DaysSky PR442; all source notices retained.
Eleven-stage integration by chafreaky with OpenAI Codex assistance, Apache-2.0.
No emitter, schedule constructor, hosting solver or expander is imported.
Usage: audit.py PARENT443_CANDIDATE OUT
"""
import copy,gzip,hashlib,json,sys
from local_audit import local_audit
from collections import Counter,defaultdict
from pathlib import Path
K,L,M,T,V,R=5,11,78,8,120,715
DATA=2*K*V*T
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load_template=lambda p:json.loads(gzip.decompress(p.read_bytes()))

def windows(schedule):
    last={};seen=[];win={};ranks={};pairs={}
    for position,event in enumerate(schedule):
        kind=event['kind']
        if kind=='local_cover_sweep':
            seen.append((position,event['stage'],event['pair']));last[event['pair']]=position
        elif kind=='bridge':
            last[event['dst']]=position;last[event['src']]=position
        elif kind=='idle':
            i=event['idx'];assert i not in win
            win[i]={s for pos,s,p in seen if last.get(event['pair'],-1)<pos<position and p!=event['pair']}
            ranks[i]=event['rank'];pairs[i]=event['pair']
        else:assert kind=='exchange' and position==len(schedule)-1
    return win,ranks,pairs

def schedule_check(schedule):
    # Ten formal integer rows, keeping the signs lost by F2 reduction.
    rows=[[int(i==j) for j in range(2*K)] for i in range(2*K)]
    levels=[-1]*K;stages=[];bridges=0;exchanged=False;idles=[]
    def add(dst,src,c):rows[dst]=[x+c*y for x,y in zip(rows[dst],rows[src])]
    for e in schedule:
        kind=e['kind'];assert not exchanged
        if kind=='local_cover_sweep':
            s,p,rev=e['stage'],e['pair'],e['reverse']
            assert s==len(stages) and 0<=s<L and p==max(0,(s-1)//2) and rev==bool(s%2)
            assert levels[p]==s-1
            add(2*p,2*p+1,-1) if rev else add(2*p+1,2*p,1)
            levels[p]=s;stages.append(s)
        elif kind=='idle':
            p,lo,hi=e['pair'],e['source_level'],e['target_level']
            assert 0<=p<K and levels[p]==lo and lo<=hi<=L-1 and e['rank']==7*(hi-lo)
            assert e['idx']==len(idles);idles.append((p,lo,hi,e['rank']));levels[p]=hi
        elif kind=='bridge':
            dst,src,c=e['dst'],e['src'],e['coefficient']
            assert 0<=dst<K and 0<=src<K and dst!=src and c in (-1,1) and levels[dst]==levels[src]
            add(2*dst,2*src,c);add(2*src+1,2*dst+1,-c);bridges+=1
        else:
            assert kind=='exchange' and levels==[L-1]*K
            for p in range(K):rows[2*p],rows[2*p+1]=rows[2*p+1],[-x for x in rows[2*p]]
            exchanged=True
    assert exchanged and rows==[[int(i==j) for j in range(2*K)] for i in range(2*K)]
    assert stages==list(range(L)) and bridges==3*(K-1)
    return idles

def audit(t,parent,widths):
    assert (t['m'],t['h'],t['stages'],t['replicas'],t['live'],t['private_centre_reserve'])==(M,8,L,T,DATA,9)
    assert t['banks_per_stage']==0 and t['bank_padding'] is None
    for key in ('local_programs','residual_isometries','entrance_rank_total','source_record_sha256','bit_operator'):
        assert t[key]==parent[key],key
    schedule_check(t['schedule'])
    win,rank,pair=windows(t['schedule']);hs=t['hosting'];used=defaultdict(set);hosted={}
    assert hs['windows']=={str(i):[pair[i],rank[i],sorted(win[i])] for i in win if rank[i] and win[i]}
    for i,cp,off,w,s,h in hs['slots']:
        assert i in win and s in win[i] and 0<=s<L and 0<=h<R*T and 0<=cp<2*V*T
        assert w==widths[h%R]>0 and 0<=off and off+w<=rank[i]
        cells=set(range(off,off+w));assert not cells&used[i,cp];used[i,cp]|=cells
        assert (s,h) not in hosted;hosted[s,h]=(i,cp,off,w)
    assert set(hosted)=={(s,h) for s in range(L) for h in range(R*T)}
    rem={};summaries={}
    for i in rank:
        if not rank[i]:continue
        for cp in range(2*V*T):rem[i,cp]=rank[i]-len(used[i,cp])
        if str(i) in hs['windows']:
            summaries[str(i)]={str(r):n for r,n in sorted(Counter(rem[i,cp] for cp in range(2*V*T)).items())}
    assert hs['remainders']==summaries
    assert len(t['calls'])==L*T;seen=set();paid=Counter()
    localhash={ori:hashlib.sha256(json.dumps(es,separators=(',',':')).encode()).hexdigest() for ori,es in t['local_programs'].items()}
    for index,c in enumerate(t['calls']):
        s,rep=c['stage'],c['replica'];p=max(0,(s-1)//2);rev=bool(s%2)
        assert (s,rep)==divmod(index,T) and c['pair']==p and c['orientation']==('reverse' if rev else 'forward')
        assert c['local_hash']==localhash[c['orientation']]
        own=c['owners'];assert len(own)==2*V+R
        assert len({(f,tuple(route)) for f,route in own})==2*V+R
        for j,(f,route) in enumerate(own):
            assert 0<=f<DATA
            if j<2*V:
                side=j//V;side=1-side if rev else side
                assert f==rep*(2*K*V)+(2*p+side)*V+j%V and route==['data',s,j%V]
            else:
                h=j-2*V;i,cp,off,w=hosted[s,rep*R+h];owner_rep,within=divmod(cp,2*V);side,port=divmod(within,V)
                assert pair[i]!=p and f==owner_rep*(2*K*V)+(2*pair[i]+side)*V+port
                assert route==['hosted',i,off,w]
                assert (s,rep,h) not in seen;seen.add((s,rep,h))
        for z in t['local_programs'][c['orientation']]:
            if z[0]==0 and z[4]:paid[z[4]]+=1
            if z[0]==2:paid[z[5]]+=1
    assert len(seen)==L*T*R
    for r in rem.values():
        if r:paid[r]+=1
    assert M*DATA-sum(r*n for r,n in paid.items())==T*(2*K*V-72*L)
    assert M**2<=2*max(paid)**2 and M**3>2*max(paid)**3
    return paid

def expanded_digest(t):
    h=hashlib.sha256();count=0
    for call in t['calls']:
        for op in t['local_programs'][call['orientation']]:
            row=[op[0],call['owners'][op[1]]]
            if op[0]==0:row.extend(op[2:])
            else:
                row.append(call['owners'][op[2]] if op[2]<2*V+R else [t['live'],['private',0]])
                row.extend(op[3:])
            h.update(json.dumps(row,separators=(',',':')).encode());h.update(b'\n');count+=1
    return h.hexdigest(),count


def physical_prefix(t):
    bounds={i:1 for i in range(t['live'])};scratch=t['live'];bounds[scratch]=0;maximum=1
    stages=defaultdict(list)
    for c in t['calls']:stages[c['stage']].append(c)
    for e in t['schedule']:
        if e['kind']=='local_cover_sweep':
            for c in stages[e['stage']]:
                for z in t['local_programs'][c['orientation']]:
                    tag=z[0]
                    if tag==0:continue
                    dst=c['owners'][z[1]][0]
                    if tag==1:
                        sr=scratch if z[2]==2*V+R else c['owners'][z[2]][0]
                        bounds[dst]=bounds[dst]+abs(z[3])*bounds[sr]
                    elif tag==2:bounds[scratch]=bounds[dst]
                    else:assert tag==3;bounds[scratch]=0
                    maximum=max(maximum,bounds[dst],bounds[scratch])
        elif e['kind']=='bridge':
            for replica in range(T):
                for port in range(V):
                    for side in (0,1):
                        dp,sp=(e['dst'],e['src']) if side==0 else (e['src'],e['dst'])
                        dst=replica*2*K*V+(2*dp+side)*V+port;sr=replica*2*K*V+(2*sp+side)*V+port
                        bounds[dst]+=bounds[sr];maximum=max(maximum,bounds[dst])
    assert bounds[scratch]==0
    return maximum

def main():
    par,geometry_parent,out=map(Path,sys.argv[1:]);t=load_template(out/'GLOBAL-TEMPLATE.json.gz');pt,local_result=local_audit(par)
    g=read(out/'GLOBAL.json');geo=read(out/'GEOMETRY.json');pg=read(geometry_parent/'GEOMETRY.json')
    state=read(par/'records/249-states.json');fs=read(par/'records/frames.json')['frames']
    widths=[8-fs[str(state['initial'][str(h)])]['dim'] for h in range(240,955)]
    P=audit(t,pt,widths)
    assert geo['m']==78 and geo['stages']==11 and len(geo['ports'])==120 and not geo['bank_slots'] and not geo['bank_permutations']
    for p,old in zip(geo['ports'],pg['ports']):
        assert {k:v for k,v in p.items() if k!='routes'}=={k:v for k,v in old.items() if k!='routes'}
        assert p['routes'][:9]==old['routes'] and len(p['routes'])==11
        for s,route in enumerate(p['routes']):
            if s==0:assert route==dict(stage=0,axes=list(range(8)),identity=True)
            else:
                assert route==dict(stage=s,axes=list(range(8))+list(range(8+7*(s-1),8+7*s)),elementary_inverse_replay=old['routes'][1]['elementary_inverse_replay'])
                assert len(set(route['axes']))==15 and max(route['axes'])<M
    idle=schedule_check(t['schedule'])
    assert idle==[(e['pair'],e['source_level'],e['target_level'],e['rank']) for e in geo['idle_per_port_and_data_member']]
    assert t['geometry_sha256']==sha(out/'GEOMETRY.json')==g['geometry_sha256']
    assert t['source_record_sha256']==sha(par/'records/249-records.bin')==g['source_records_sha256']
    th=hashlib.sha256(gzip.decompress((out/'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest();assert th==g['template_sha256']
    digest,count=expanded_digest(t);assert digest==g['emitted_program_sha256'] and count==g['emitted_events']
    assert P==Counter({int(r):n for r,n in g['profile'].items()})
    assert (g['live'],g['physical'],g['hosted_residuals'],g['bank_assignments'],g['deficit'])==(9600,9609,62920,0,3264)
    assert g['rank_mass']==sum(r*n for r,n in P.items()) and g['paid_calls']==sum(P.values()) and g['maxchild']==max(P)
    assert g['independent_unbanked_scalar_columns']==9065 and len(g['scalar_stages'])==11 and g['all_scalar_columns_restored']
    assert g['omitted_bridge_shears_rejected']==list(range(24))
    prefix=physical_prefix(t);assert int(g['global_prefix_bound'])==prefix
    assert g['global_prefix_bits']==prefix.bit_length() and g['charged_prefix_bits']==64*((prefix.bit_length()+63)//64)
    assert prefix>1<<192 # Old independent-replica charge is not reused.
    controls=[]
    def reject(name,fn):
        q=copy.deepcopy(t);fn(q)
        try:audit(q,pt,widths)
        except (AssertionError,KeyError,IndexError,TypeError):controls.append(name)
        else:raise AssertionError('accepted '+name)
    slot=lambda q:q['hosting']['slots'][0]
    reject('slot outside window',lambda q:slot(q).__setitem__(4,10))
    reject('copy outside family',lambda q:slot(q).__setitem__(1,2*V*T))
    reject('negative slot offset',lambda q:slot(q).__setitem__(2,-1))
    reject('wrong residual width',lambda q:slot(q).__setitem__(3,slot(q)[3]+1))
    reject('duplicate helper',lambda q:q['hosting']['slots'].append(slot(q)))
    reject('missing helper',lambda q:q['hosting']['slots'].pop())
    reject('owner replica does not match assignment',lambda q:q['calls'][0]['owners'][240].__setitem__(0,q['calls'][0]['owners'][240][0]+1200))
    reject('cross-replica data',lambda q:q['calls'][0]['owners'][0].__setitem__(0,1200))
    reject('wrong hosted coordinate',lambda q:q['calls'][0]['owners'][240][1].__setitem__(2,99))
    reject('helper changed to bank',lambda q:q['calls'][0]['owners'][240][1].__setitem__(0,'bank'))
    reject('wrong call orientation',lambda q:q['calls'][0].__setitem__('orientation','reverse'))
    reject('duplicate call',lambda q:q['calls'].__setitem__(1,q['calls'][0]))
    reject('dropped final stage',lambda q:q.__setitem__('calls',[c for c in q['calls'] if c['stage']<10]))
    reject('wrong idle rank',lambda q:next(e for e in q['schedule'] if e['kind']=='idle').__setitem__('rank',1))
    reject('omitted bridge',lambda q:q['schedule'].pop(next(i for i,e in enumerate(q['schedule']) if e['kind']=='bridge')))
    reject('wrong bridge sign',lambda q:next(e for e in q['schedule'] if e['kind']=='bridge').__setitem__('coefficient',-1))
    reject('omitted terminal exchange',lambda q:q['schedule'].pop())
    reject('understated live stock',lambda q:q.__setitem__('live',q['live']-1))
    reject('missing remainder summary',lambda q:q['hosting']['remainders'].pop(next(iter(q['hosting']['remainders']))))
    reject('wrong residual isometry',lambda q:q['residual_isometries'][0]['orthogonal_rows_numerator'][0].__setitem__(0,99))
    reject('omitted local instruction',lambda q:q['local_programs']['forward'].pop())
    reject('wrong reflected copy rank',lambda q:next(z for z in q['local_programs']['reverse'] if z[0]==2).__setitem__(5,0))
    res=dict(status='PASS_INDEPENDENT_ELEVEN_STAGE_HOSTING_AUDIT',template_sha256=th,emitted_program_sha256=digest,
             emitted_events=count,profile={str(r):n for r,n in sorted(P.items())},live=9600,physical=9609,hosted_residuals=62920,
             bank_assignments=0,rank_mass=sum(r*n for r,n in P.items()),deficit=3264,maxchild=max(P),geometry_routes=1320,
             halving_depth=3,physical_prefix_bits=prefix.bit_length(),charged_prefix_bits=g['charged_prefix_bits'],local_audit=local_result,mutations_rejected=controls)
    (out/'AUDIT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
if __name__=='__main__':main()
