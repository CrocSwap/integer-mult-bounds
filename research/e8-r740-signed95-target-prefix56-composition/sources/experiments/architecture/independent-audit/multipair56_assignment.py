"""Independent source-slot/window/stock/payment audit; geometry separate."""
from pathlib import Path
import gzip,json,hashlib,struct
from collections import Counter,defaultdict

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
NEW=ROOT/'experiments/architecture/target-prefix-multipair-complete/global/hosted'
OLD=ROOT/'experiments/stage-search/pr441-signed-retime/full/bit426-source-centres'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def template(p):return json.loads(gzip.decompress(p.read_bytes()))
def main():
    t=template(NEW/'GLOBAL-TEMPLATE.json.gz');parent=template(OLD/'global/GLOBAL-TEMPLATE.json.gz')
    g=read(NEW/'GLOBAL.json');LOCAL=NEW.parent/'signed';st=read(LOCAL/'records/249-states.json');fs=read(LOCAL/'records/frames.json')['frames']
    R=st['R'];T=t['replicas'];M=t['m'];V=120;DATA=T*1200
    assert (R,T,M)==(740,8,78)
    widths=[]
    for h in range(R):
        f=fs[str(st['initial'][str(240+h)])];widths.append(8-f['dim'])
        # Current admitted entrances are coordinate subspaces, not merely
        # spaces of the same dimension. A direct permutation is available.
        supports=[tuple(i for i,x in enumerate(row) if x) for row in f['B']]
        assert all(len(s)==1 for s in supports) and len(set(supports))==f['dim']
    assert Counter(widths)==Counter({8:645,7:87,4:8})
    sched=t['schedule'];locals={e['stage']:(pos,e) for pos,e in enumerate(sched) if e['kind']=='local_cover_sweep'}
    idles={e['idx']:(pos,e) for pos,e in enumerate(sched) if e['kind']=='idle'}
    slots={};used=defaultdict(set);window_checks=0;reflection_checks=0
    for i,cp,off,w,s,h in t['hosting']['slots']:
        assert (s,h) not in slots and 0<=cp<240 and 0<=h<R and w==widths[h]
        p,e=idles[i];q,l=locals[s];assert q<p and l['pair']!=e['pair']
        # Examine every intervening physical schedule event. No same-pair
        # idle is silently ignored. This verifies the actual source recipe.
        for ev in sched[q+1:p]:
            if ev['kind']=='local_cover_sweep':assert ev['pair']!=e['pair']
            elif ev['kind']=='bridge':assert e['pair'] not in (ev['src'],ev['dst'])
            elif ev['kind']=='idle':assert ev['pair']!=e['pair']
            else:raise AssertionError('unclassified intervening operator')
        # Reflection reverses the identical open interval, preserving no-touch.
        n=len(sched);rp=n-1-q;rq=n-1-p;assert rq<rp
        assert list(reversed(sched[q+1:p]))==list(reversed(sched))[rq+1:rp]
        reflection_checks+=1
        start=1 if e['source_level']==-1 else 8+7*e['source_level']
        stop=8+7*e['target_level'];pending=set(range(start,stop))
        assert len(pending)==e['rank']
        axes=set(range(start+off,start+off+w));assert axes<=pending
        key=(i,cp);assert not axes&used[key];used[key]|=axes
        slots[s,h]=(i,cp,off,w,axes);window_checks+=1
    oldcalls={(c['stage'],c['replica']):c for c in parent['calls']}
    bank=defaultdict(set);percall=0
    for c in t['calls']:
        s,rep,p=c['stage'],c['replica'],c['pair'];owners=c['owners']
        assert owners[:240]==[[rep*1200+(2*p+(1-side if c['orientation']=='reverse' else side))*V+port,['data',s,port]] for side in range(2) for port in range(V)] and len(owners)==240+R
        distinct=set()
        for h,(f,r) in enumerate(owners[240:]):
            if (s,h) in slots:
                i,cp,off,w,axes=slots[s,h];side,port=divmod(cp,V)
                assert f==rep*1200+(2*idles[i][1]['pair']+side)*V+port
                assert r==['hosted',i,off,w] and p!=idles[i][1]['pair']
                target=(f,tuple(sorted(axes)))
            else:
                assert r[0]=='bank' and r[2]==widths[h] and DATA<=f<t['live']
                axes=set(range(r[1],r[1]+r[2]));assert axes<=set(range(64)) and not axes&bank[f]
                bank[f]|=axes;target=(f,tuple(sorted(axes)))
            assert target not in distinct;distinct.add(target)
        percall+=1
    assert sorted(bank)==list(range(DATA,t['live'])) and all(len(x)==64 for x in bank.values())
    raw=list(struct.iter_unpack('<6i',(LOCAL/'records/249-records.bin').read_bytes()));normalized={}
    assert t['source_record_sha256']==sha(LOCAL/'records/249-records.bin')
    for rev in (False,True):
        events=[]
        for op,x,y,c,f,z in reversed(raw) if rev else raw:
            if op==0: events.append([0,x,c if rev else y,y if rev else c,f,int(rev)])
            elif op==1:events.append([1,x,y,-c if rev else c,f,int(rev)])
            elif op==(3 if rev else 2):events.append([2,x,y,c,f,8,int(rev)])
            else:events.append([3,x,y,c,f,z,int(rev)])
        normalized['reverse' if rev else 'forward']=events
    H=Counter()
    for c in t['calls']:
        assert t['local_programs'][c['orientation']]==normalized[c['orientation']]
        for z in t['local_programs'][c['orientation']]:
            if z[0]==0 and z[4]:H[z[4]]+=1
            elif z[0]==2:H[z[5]]+=1
    for i,(pos,e) in idles.items():
        if e['rank']==0:continue
        for cp in range(240):
            r=e['rank']-len(used[i,cp])
            if r:H[r]+=T
    assert dict(H)=={int(r):n for r,n in g['profile'].items()}
    mass=sum(r*n for r,n in H.items());deficit=M*t['live']-mass
    assert mass==745536 and deficit==3264
    result=dict(status='PASS_INDEPENDENT_SIGNED95_ASSIGNMENT_WINDOWS_REFLECTION_STOCK_AND_PAID_PROFILE',
        inputs={str(p.relative_to(ROOT)):sha(p) for p in [NEW/'GLOBAL-TEMPLATE.json.gz',NEW/'GLOBAL.json',LOCAL/'records/249-states.json',LOCAL/'records/frames.json',OLD/'global/GLOBAL-TEMPLATE.json.gz']},
        residual_width_inventory=dict(Counter(widths)),slots_per_replica=len(slots),hosted_total=len(slots)*T,
        actual_window_checks=window_checks,reflection_checks=reflection_checks,per_invocation_slot_injection_checks=percall,
        live=t['live'],physical=g['physical'],bank_families=len(bank),rank_mass=mass,deficit=deficit,profile=dict(H),
        reported_deficit=g['deficit'],reported_deficit_consistent=g['deficit']==deficit,
        scope='All actual source slots/windows/reflected open intervals, coordinate entrance support, bank tiling and paid profile. Actual selected rational sigma matrices and signed global route/prefix/invoice require separate geometry/compiler checks; slot distinctness is not a substitute for actual route matrices.')
    (OUT/'MULTIPAIR56-ASSIGNMENT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status']);print('deficit',deficit,'reported',g['deficit'])
if __name__=='__main__':main()
