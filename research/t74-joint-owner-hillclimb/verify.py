"""Bounded independent owner/profile/moment and publication-binding checks.

This does not rerun native Clifford phases or the complete controller.  The
separate cold_replay.py command reruns those, with explicit source-bound reuse.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import gzip,hashlib,importlib.util,json

P=Path(__file__).resolve().parent
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)

def actual_windows(contract,order):
    """Independent literal source-event chronology; no emitter is imported."""
    blocks={};stage=None;tail=[]
    for i,e in enumerate(contract['events']):
        if e['kind']in('bank_padding_cover_sweep','translate_every_live_family'):tail.append(i);continue
        if e['kind']=='local_cover_sweep':stage=e['stage'];blocks[stage]=[]
        blocks[stage].append((i,e))
    ranks={int(k.split(',')[1]):v[0]for k,v in contract['windows'].items()}
    last={};interval={};calls={};perrep=defaultdict(list);pos=0
    for t,(s,r)in enumerate(order):
        for i,e in blocks[s]:
            perrep[r].append(i);kind=e['kind']
            if kind=='local_cover_sweep':last[r,contract['stage_pair'][str(s)]]=pos;calls[t]=pos
            elif kind=='bridge':last[r,e['src']]=last[r,e['dst']]=pos
            elif kind=='idle_cover_sweep':
                for c in e['child_indices']:
                    if c in ranks:interval[r,c]=(last.get((r,e['pair']),-1),pos)
            pos+=1
    need(all(v==list(range(30))for v in perrep.values()),'per-replica source-event projection')
    need(set(perrep)==set(range(74))and tail==[30,31],'replicas/global tail')
    return {f'{r},{c}':[ranks[c],[t for t,p in calls.items()if a<p<b]]for(r,c),(a,b)in interval.items()}

def owners_check(rows,plan,contract):
    windows=actual_windows(contract,plan['order'])
    need(plan['windows']==windows,'literal source-event windows')
    need(len(rows)==666*434,'whole helper role count')
    bycall=defaultdict(set);fams=defaultdict(set);bins=defaultdict(list)
    for z in rows:
        t=z['time'];need(0<=t<666,'call time');s,r=plan['order'][t]
        need((s,r)==(z['stage'],z['replica']),'invocation identity')
        h=z['helper'];need(0<=h<434 and h not in bycall[t],'helper coverage/uniqueness');bycall[t].add(h)
        provider=plan['provider_calls'][t]['provider'];widths=plan['provider_registry'][provider]['widths']
        need(z['width']==widths[h],'actual helper width')
        own,ch,port=z['owner_replica'],z['child'],z['port'];key=f'{own},{ch}'
        need(key in windows and t in windows[key][1]and 0<=port<112,'owner window/port')
        family=own*896+(2*plan['pairs'][str(ch)]+plan['sides'][str(ch)])*112+port
        need(z['family']==family and z['copy']==own*112+port,'physical owner address')
        need(family//224!=r*4+contract['stage_pair'][str(s)],'active data family')
        need(family not in fams[t],'one helper per physical family');fams[t].add(family)
        bins[own,ch,port].append(z)
    need(set(bycall)==set(range(666))and all(len(v)==434 for v in bycall.values()),'complete invocation coverage')
    idle=Counter()
    for key,(cap,allowed)in windows.items():
        r,ch=map(int,key.split(','))
        for port in range(112):
            at=0
            for z in sorted(bins[r,ch,port],key=lambda z:z['offset']):
                need(z['offset']==at,'disjoint contiguous pending prefix');at+=z['width']
            need(at<=cap,'pending bin capacity')
            if at<cap:idle[cap-at]+=1
    H=Counter(idle)
    for call in plan['provider_calls']:H.update({int(r):n for r,n in plan['provider_registry'][call['provider']]['actual_paid_profile'].items()})
    need(sum(r*n for r,n in H.items())==73*66304-23680,'global mass/deficit')
    return H,idle

def main():
    need(__debug__,'Assertions must be enabled')
    manifest=read(P/'PACKAGE-MANIFEST.json')
    for rel,digest in manifest.items():need(sha(P/rel)==digest,'package drift: '+rel)
    c=read(P/'BASELINE-CONTRACT.json.gz');plan=read(P/'data/PLAN.json');rows=read(P/'data/OWNERS.json.gz');claim=read(P/'CLAIM.json')
    drops=set(claim['removed_old_helper_indices']);local={'1':2335,'2':512,'3':426,'4':120,'5':38,'8':8}
    for provider,kind in [('gauge44','base'),('extra','extra')]:
        need(plan['provider_registry'][provider]['widths']==[w for i,w in enumerate(c['widths'][provider])if i not in drops],'retained helper widths')
        need(plan['provider_registry'][provider]['actual_paid_profile']==local,'actual changed local histogram')
        word=read(P/f'words/{kind}.json.gz');need(word['report']['local_profile']==local,'word/profile binding')
        need(len(word['removed'])==46 and word['report']['R']-len(word['removed'])==434,'native helper count')
    H,idle=owners_check(rows,plan,c)
    need(dict(H)=={int(r):n for r,n in claim['global_profile'].items()},'complete global histogram')
    need(dict(H)=={int(r):n for r,n in read(P/'data/PROFILE.json').items()},'generated profile')
    need(dict(idle)=={int(r):n for r,n in read(P/'data/CONSTRUCTION.json')['idle'].items()},'actual idle histogram')
    spec=importlib.util.spec_from_file_location('directed_moment',P/'vendor/fine_moment.py');engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    engine.SH=256;engine.GRID=1<<256;engine.LOG_TERMS=100;engine.EXP_TERMS=96
    lo=Q(claim['native_endpoint_lower']);hi=Q(claim['native_endpoint_upper'])
    need(engine.moment(73,66304,sorted(H.items()),lo)[1]<1,'directed lower endpoint')
    need(engine.moment(73,66304,sorted(H.items()),hi)[0]>1,'directed upper endpoint')
    replay=read(P/'evidence/full-replay/REPLAY.json');delta=read(P/'evidence/full-replay/delta/DELTA-ADMISSION.json')
    need(Q(claim['kappa'])<Q(replay['final_kappa'])and replay['final_kappa']==delta['final_kappa'],'published final outer bound')
    need(delta['genuine_improvement_over_pr2312']and Q(delta['gain'])>0,'strict improvement over pinned predecessor')
    for kind in('base','extra'):need(sha(P/f'words/{kind}.json.gz')==replay['changed_words'][kind]['word_sha256'],'fresh native word binding')
    controls=[]
    z=rows[0]
    for key,value,label in [('helper',434,'missing/wrong helper'),('family',-1,'wrong physical family'),('offset',100,'invalid pending prefix'),('time',666,'wrong invocation time')]:
        old=z[key];z[key]=value
        try:
            try:owners_check(rows,plan,c)
            except(ValueError,IndexError,KeyError):controls.append(label)
            else:raise ValueError('Accepted mutation: '+label)
        finally:z[key]=old
    wrong=Counter(H);wrong[1]+=1
    need(sum(r*n for r,n in wrong.items())!=73*66304-23680,'profile mass mutant');controls.append('undercharged profile')
    print('PASS_INDEPENDENT_OWNER_PROFILE_EXACT_MOMENT_AND_PUBLICATION_BINDINGS',claim['decimal'],'roles',len(rows),'controls',len(controls),flush=True)
    print('Scope: bounded owner/moment checks; native Clifford/controller/full outer checks are separate cold_replay obligations.',flush=True)

if __name__=='__main__':main()
