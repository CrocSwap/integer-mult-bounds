#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explicit arbitrary-positive-replica lift of the authenticated T37 parent.

This constructs dedicated source banks, not hosted helper assignments. Source
lineage: PR558/589, PR741/799/870 controller routes, PR1193 T37 bank envelope,
PR2679/2751/2766 replay. No provider/native source or phase recipe is modified.
"""
import argparse, copy, gzip, hashlib, json, os
from collections import Counter
from pathlib import Path

SOURCE = Path(__file__).resolve().parent/'inputs/GLOBAL-TEMPLATE.json.gz'
REFERENCE = SOURCE.parent.parent/'GLOBAL-TEMPLATE.json.gz'
SOURCE_SHA = '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'
SOURCE_ID = '514e59314c8e2fa3c22d0a48083816f6686211090835e8f8775318c1c3e992d8'
M, STAGES, DATA_PER_REPLICA, HELPERS, BANK_PER_GROUP, PRIVATE = 73, 9, 896, 504, 4536, 514

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def identity(x): return hashlib.sha256(canonical(x)).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p=Path(p); raw=p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def require(x,why):
    if not x: raise ValueError(why)
def source():
    require(sha(SOURCE)==SOURCE_SHA,'source byte hash')
    s=read(SOURCE); require(identity(s)==SOURCE_ID,'source content hash')
    return s

def grouping(T):
    require(isinstance(T,int) and T>0,'positive integer T')
    return [8]*(T//8)+([T%8] if T%8 else [])

def build(T, groups=None, order=None):
    s=source(); groups=grouping(T) if groups is None else list(groups)
    require(sum(groups)==T and all(isinstance(q,int) and 1<=q<=8 for q in groups),'group partition')
    olddata=37*896; data=T*896; live=data+len(groups)*BANK_PER_GROUP
    t=copy.deepcopy({k:v for k,v in s.items() if k not in ('calls','bank_padding','local_programs')})
    # Programs are immutable and reused literally; there is no new phase oracle.
    t['local_programs']=s['local_programs']
    t.update(version='arbitrary-T-dedicated-source-bank-envelope-v1',live=live,physical=live+PRIVATE)
    templates={(c['stage'],c['replica']):c for c in s['calls'] if c['replica']<8}
    location={}; off=0
    for g,q in enumerate(groups):
        for lane in range(q): location[off+lane]=(g,lane)
        off+=q
    order=[(st,r) for st in range(9) for r in range(T)] if order is None else [tuple(x) for x in order]
    require(len(order)==9*T and set(order)=={(st,r)for st in range(9)for r in range(T)},'call coverage')
    require(all([st for st,r in order if r==rep]==list(range(9))for rep in range(T)),'per-replica stage order')
    calls=[]
    for st,r in order:
        g,lane=location[r]; old=templates[st,lane]
        c={k:copy.deepcopy(v) for k,v in old.items() if k!='owners'}; c['replica']=r
        c['owners']=[[f-lane*896+r*896,copy.deepcopy(route)]for f,route in old['owners'][:224]]
        c['owners'] += [[data+g*BANK_PER_GROUP+st*HELPERS+h,copy.deepcopy(route)]for h,(_,route) in enumerate(old['owners'][224:])]
        calls.append(c)
    t['calls']=calls
    widths=[9 if len(route)==2 else route[2] for _,route in templates[0,0]['owners'][224:]]
    children=[]
    for g,q in enumerate(groups):
        for st in range(9):
            for h,w in enumerate(widths):
                axes=list(range(q*w,M))
                children.append(dict(family=data+g*BANK_PER_GROUP+st*HELPERS+h,rank=len(axes),axis_indices=axes,orthogonal_axes=[1<<j for j in axes]))
    t['bank_padding']=dict(s['bank_padding'],families=list(range(data,live)),children=children)
    for z in t['idle_children']: z['replicas']=T
    for e in t['execution_schedule']:
        if 'replicas'in e: e['replicas']=list(range(T))
        if e['kind']=='bank_padding_cover_sweep': e['families']=[data,live]
        if e['kind']=='translate_every_live_family': e.update(families=[0,live],charged_calls_per_cover=live)
    t['cover_final_correction'].update(families=[0,live],charged_calls_per_cover=live)
    t['private_namespace']={'centers':[live,live+8],'reserved_tableau':[live+8,live+512],'coefficient':[live+512,live+514]}
    t['replica_lift']=dict(replicas=T,data_stock=data,bank_stock=len(groups)*BANK_PER_GROUP,groups=groups,source_template_content_sha256=SOURCE_ID,phase_recipe_unchanged=True)
    # The inherited wording replica//8 is false for a partial nonterminal group.
    t['route_semantics']['helper']='Cumulative explicit replica_lift.groups select bank group and local lane. Residual/spectator routes retain source coordinates. Each group has nine dedicated 504-family banks.'
    check(t,groups)
    return t

def check(t,groups):
    """Independent formula/actual-route checks, without trusting build's map."""
    s=source(); T=sum(groups); G=len(groups); D=896*T; L=D+9*504*G
    require(t['m']==73 and t['live']==L and t['physical']==L+514,'full dedicated reserve')
    require(t['replica_lift']['groups']==groups and t['replica_lift']['replicas']==T,'group metadata')
    for k in ('recipe','local_programs','exact_data_phase_recipe_sha256','exact_local_clifford_recipe_sha256','residual_adapter_sha256','adapter_policy','cover','expanded_scalar_interface','port_restriction','supplier_substitution'):
        require(t[k]==s[k],f'unchanged source/phase/cover field {k}')
    expected_calls={(st,r)for st in range(9)for r in range(T)}
    require(len(t['calls'])==9*T and {(c['stage'],c['replica'])for c in t['calls']}==expected_calls,'literal call coverage')
    sc={(c['stage'],c['replica']):c for c in s['calls']}
    loc={}; start=0
    for g,q in enumerate(groups):
        for r in range(start,start+q):loc[r]=(g,r-start,q)
        start+=q
    widths={}; usedbanks=set()
    for c in t['calls']:
        st,r=c['stage'],c['replica']; g,lane,q=loc[r]; old=sc[st,lane]
        require({k:v for k,v in c.items()if k not in('owners','replica')}=={k:v for k,v in old.items()if k not in('owners','replica')},'source call/frame/orientation contract')
        require(len(c['owners'])==728 and len({f for f,_ in c['owners']})==728,'one role per physical family per invocation')
        for i,(f,route) in enumerate(c['owners'][:224]):
            of,orr=old['owners'][i]
            require(f==r*896+of-lane*896 and 0<=f<D and route==orr,'literal unchanged data route')
        for h,(f,route) in enumerate(c['owners'][224:]):
            require(f==D+g*4536+st*504+h and route==old['owners'][224+h][1],'dedicated helper route')
            require(route[0]==2,'helper route type')
            w=9 if len(route)==2 else route[2]
            require(1<=w<=9,'helper width')
            if len(route)==2:require(route==[2,lane],'width-nine lane')
            else:require(route==[2,lane*w,w,list(range(8*w,8*w+9-w))],'residual/spectator orthogonal embedding')
            require((g,st,h)not in widths or widths[g,st,h]==w,'consistent widths')
            widths[g,st,h]=w;usedbanks.add(f)
    require(usedbanks==set(range(D,L)),'every reserved bank is actually used')
    require(t['bank_padding']['families']==list(range(D,L)),'charged bank family coverage')
    require(len(t['bank_padding']['children'])==9*504*G,'one charged complement per bank')
    pad={z['family']:z for z in t['bank_padding']['children']}
    require(len(pad)==9*504*G,'unique padding families')
    paid=Counter()
    for (g,st,h),w in widths.items():
        q=groups[g]; f=D+g*4536+st*504+h; z=pad[f]; axes=list(range(q*w,73))
        require(z==dict(family=f,rank=73-q*w,axis_indices=axes,orthogonal_axes=[1<<j for j in axes]),'exact orthogonal bank complement')
        # All used residual blocks plus complement partition every coordinate.
        cover=[j for lane in range(q)for j in range(lane*w,(lane+1)*w)]+axes
        require(cover==list(range(73)),'complete pairwise orthogonal residual/complement partition')
        require(8*w+9-w<=73,'spectator map fits physical family')
        paid[z['rank']]+=1
    require(len(t['idle_children'])==len(s['idle_children']),'all idle children retained')
    for a,b in zip(t['idle_children'],s['idle_children']):require(a==dict(b,replicas=T),'literal idle child')
    require(len(t['execution_schedule'])==32,'source event count')
    for j,(a,b) in enumerate(zip(t['execution_schedule'],s['execution_schedule'])):
        e=copy.deepcopy(b)
        if 'replicas'in e:e['replicas']=list(range(T))
        if e['kind']=='bank_padding_cover_sweep':e['families']=[D,L]
        if e['kind']=='translate_every_live_family':e.update(families=[0,L],charged_calls_per_cover=L)
        require(a==e,f'literal source event {j}')
    require(t['cover_final_correction']==dict(s['cover_final_correction'],families=[0,L],charged_calls_per_cover=L),'paid full-family final correction')
    require(t['private_namespace']=={'centers':[L,L+8],'reserved_tableau':[L+8,L+512],'coefficient':[L+512,L+514]},'all private reserves retained')
    return dict(T=T,groups=groups,data=D,bank_stock=9*504*G,parent_live=L,parent_physical=L+514,calls=9*T,parent_idle=T*len(s['idle_children']),parent_idle_rank_mass=T*sum(z['rank']for z in s['idle_children']),bank_padding_profile=dict(sorted(paid.items())),dedicated_helper_invocations=9*T*504,private=dict(centers=8,reserved_tableau=504,coefficient=2),source_phase_sha=t['exact_data_phase_recipe_sha256'])

def expand_schedule(parent,order):
    # Independent expansion of the fixed source stage blocks. No optimizer used.
    T=parent['replica_lift']['replicas'];order=[tuple(v)for v in order]
    require(len(order)==9*T and set(order)=={(s,r)for s in range(9)for r in range(T)},'async call coverage')
    require(all([s for s,r in order if r==rep]==list(range(9))for rep in range(T)),'async source stage projection')
    blocks={}; active=None
    for j,e in enumerate(parent['execution_schedule'][:30]):
        if e['kind']=='local_cover_sweep':active=e['stage'];blocks[active]=[]
        require(active is not None,'source begins with local call');blocks[active].append((j,e))
    result=[]
    for time,(st,r) in enumerate(order):
        for j,e in blocks[st]: result.append(dict(e,source_event=j,replica=r,replicas=[r],time=time))
    result += [dict(e,source_event=j)for j,e in enumerate(parent['execution_schedule'])if j>=30]
    project={r:[]for r in range(T)}
    for e in result[:-2]:project[e['replica']].append(e['source_event'])
    require(all(v==list(range(30))for v in project.values()),'all thirty literal events per source replica')
    require([e['source_event']for e in result[-2:]]==[30,31],'two global source events')
    return result

def compare74():
    actual=read(REFERENCE);groups=actual['replica_lift']['groups'];order=[(c['stage'],c['replica'])for c in actual['calls']]
    ours=build(74,groups,order)
    ignore={'version','route_semantics'}
    require({k:v for k,v in ours.items()if k not in ignore}=={k:v for k,v in actual.items()if k not in ignore},'actual T74 complete semantic identity')
    require(ours['route_semantics']['data']==actual['route_semantics']['data'] and ours['route_semantics']['work']==actual['route_semantics']['work'],'T74 other route semantics unchanged')
    return dict(status='PASS',reference_file_sha256=sha(REFERENCE),reference_content_sha256=identity(actual),identical_fields=[k for k in ours if k not in ignore],differences=['version label','helper route explanatory string only'],source_call_order_matched=True)

def write_new(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True); lock=p.with_suffix(p.suffix+'.lock')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        os.write(fd,str(os.getpid()).encode());os.close(fd);fd=None
        require(not p.exists(),'preserve existing output')
        raw=canonical(x)
        if p.suffix=='.gz':
            b=bytearray(gzip.compress(raw,mtime=0));b[9]=255;raw=bytes(b)
        with p.open('xb')as h:h.write(raw)
    finally:
        if fd is not None:os.close(fd)
        lock.unlink()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--T',type=int,default=80);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--order',type=Path)
    a=ap.parse_args();require(not a.out.exists(),'fresh output directory required');a.out.mkdir(parents=True)
    order=read(a.order)if a.order else None
    t=build(a.T,order=order);receipt=check(t,t['replica_lift']['groups']);receipt['T74_comparison']=compare74()
    stages=[(c['stage'],c['replica'])for c in t['calls']];sched=expand_schedule(t,stages)
    receipt.update(status='PASS_EXPLICIT_SOURCE_PARENT_GEOMETRY',source_file_sha256=SOURCE_SHA,source_content_sha256=SOURCE_ID,source_recipe_unchanged=True,source_events_per_replica=30,global_tail=[30,31],expanded_events=len(sched),phase_claim='Literal reuse of authenticated source local programs and phase recipes; this is not a fresh native phase replay.',scope='Dedicated parent only; final hosted owner assignment/invoice/admission remains separate.',script_sha256=sha(__file__))
    write_new(a.out/'GLOBAL-TEMPLATE.json.gz',t);write_new(a.out/'SOURCE-SCHEDULE.json.gz',sched)
    receipt['template_content_sha256']=identity(t);receipt['template_file_sha256']=sha(a.out/'GLOBAL-TEMPLATE.json.gz');receipt['schedule_content_sha256']=identity(sched)
    write_new(a.out/'RESULT.json',receipt)
    require(sha(SOURCE)==SOURCE_SHA,'source unchanged after output')
    print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
