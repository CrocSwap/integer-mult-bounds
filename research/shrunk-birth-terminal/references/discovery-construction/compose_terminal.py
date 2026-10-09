#!/usr/bin/env python3
"""Compose disjoint terminal elimination with an exact shrunk/birth word.

Original terminal-elision identity: SovereignSteak, PR122.
Shrunk frames: Joel Pulikkan, PR125. Birth reuse: James Chang, PR124.
PR117 DAG: eumemic; deferred compiler: Avi Eisenberg and Rohan Arun.
This explicit composition, complete word/profile checks and all-column
response audit were prepared with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import argparse, gzip, json, pickle, resource, subprocess, sys, time

assert not sys.flags.optimize, 'Assertions must remain enabled'
W=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--frames',type=Path,required=True)
p.add_argument('--matches',type=Path,required=True)
p.add_argument('--readouts',type=Path,default=W/'baseline/READOUTS.pkl')
p.add_argument('--scalar-bill',type=Path,default=W/'baseline/READOUT_COST.json')
p.add_argument('--out',type=Path,required=True)
p.add_argument('--terminal-roles',type=Path,help='JSON list of exact terminal IDs; validated after supplied real birth matches.')
a=p.parse_args();start=time.monotonic();O=a.out.resolve();O.mkdir(parents=True,exist_ok=False)
source_directory=O/'construction-sources';source_directory.mkdir()
source_bytes={q.name:q.read_bytes() for q in [Path(__file__),W/'terminal_inventory.py']}
for name,data in source_bytes.items():(source_directory/name).write_bytes(data)
inputs=O/'inputs';inputs.mkdir();pins={}
for source,name in [(a.frames,'FRAMES.pkl'),(a.matches,'BIRTH_MATCHES.json.gz'),(a.readouts,'READOUTS.pkl'),(a.scalar_bill,'READOUT_COST.json')]:
    data=source.read_bytes();(inputs/name).write_bytes(data);assert source.read_bytes()==data
    pins[name]={'source_path':str(source.resolve()),'sha256':sha256(data).hexdigest(),'bytes':len(data)}
selection_args=[]
if a.terminal_roles:
    data=a.terminal_roles.read_bytes();(inputs/'TERMINAL_ROLES.json').write_bytes(data);assert a.terminal_roles.read_bytes()==data
    pins['TERMINAL_ROLES.json']={'source_path':str(a.terminal_roles.resolve()),'sha256':sha256(data).hexdigest(),'bytes':len(data)}
    selection_args=['--terminal-roles',str(inputs/'TERMINAL_ROLES.json')]
subprocess.run([sys.executable,str(source_directory/'terminal_inventory.py'),'--frames',str(inputs/'FRAMES.pkl'),'--matches',str(inputs/'BIRTH_MATCHES.json.gz'),'--readouts',str(inputs/'READOUTS.pkl'),'--out',str(O/'inventory.json'),*selection_args],check=True,stdout=subprocess.DEVNULL)
inventory=json.loads((O/'inventory.json').read_text())
g=pickle.loads((inputs/'FRAMES.pkl').read_bytes());readouts=pickle.loads((inputs/'READOUTS.pkl').read_bytes())
choice=json.loads(gzip.decompress((inputs/'BIRTH_MATCHES.json.gz').read_bytes()))
bill=json.loads((inputs/'READOUT_COST.json').read_text())
R=len(g['first']);v=g['v'];h=g['h'];m=h*h;N=v*v
merge={r['recipient']:r['donor'] for r in choice['pairs']}
removed={r['role'] for r in inventory['selected']};selected={r['role']:r for r in inventory['selected']}
assert removed and not removed & (set(merge)|set(merge.values()))
live=set(range(R))-set(merge)-removed
assert len(live)==choice['R']-len(removed)
physical=lambda s:2*v+merge.get(s,s)

frames=[()];ids={():0}
def fid(F):
    F=tuple(F)
    if F not in ids:ids[F]=len(frames);frames.append(F)
    return ids[F]
def basis(rows):
    piv={}
    for x in rows:
        for q in sorted(piv,reverse=True):
            if x>>q&1:x^=piv[q]
        if x:
            q=x.bit_length()-1
            for r in piv:
                if piv[r]>>q&1:piv[r]^=x
            piv[q]=x
    return tuple(piv[q] for q in sorted(piv,reverse=True))
FULL=fid(tuple(1<<i for i in range(h-1,-1,-1)))
U=[fid(F) for F in g['U']];tm=[fid((mask,)) for mask in g['tm']]
@lru_cache(None)
def dual(i):
    A=frames[i];piv={r.bit_length()-1 for r in A};out=[]
    for j in range(h):
        if j not in piv:
            x=1<<j
            for r in A:
                if r>>j&1:x|=1<<(r.bit_length()-1)
            out.append(x)
    return fid(basis(out))
@lru_cache(None)
def nested(i,j):
    for x in frames[i]:
        for r in frames[j]:
            if x>>(r.bit_length()-1)&1:x^=r
        if x:return False
    return True
@lru_cache(None)
def nondeg(i):
    A=frames[i]
    return len(basis(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(A)) for x in A))==len(A)

word=[];forward_workspace=[];direct_origins=[];ALL=(1<<v)-1
def gate(d,s,sign,F,remember=False):
    assert d!=s and d>=2*v and d-2*v in live
    e=('g',d,s,sign,F);word.append(e)
    if remember:forward_workspace.append(e)
def oldread(s,F):
    mask=ALL if g['reach_all'][s] else g['reach'][s]
    if s in removed:
        assert mask==1<<selected[s]['target']
        word.append(('f',v,mask,F,('removed-old-read',s)))
    else:
        word.append(('r',physical(s),v,mask,-1,F,('old',s)))
def source(s):
    assert s not in removed
    x=g['first'][s];assert 1<=x<=v
    gate(physical(s),x-1,1,U[x],True)
def mix(i):
    op,s,t,x=g['ops'][i]
    if op==0:return
    dst,src=(s,t) if op==1 else (t,s)
    assert src not in removed
    if dst in removed:
        assert i not in g['phase']
        row=selected[dst];event=('d',v+row['target'],physical(src),row['coefficient_numerator'],U[x],i,dst)
        word.append(event);direct_origins.append({'operation_index':i,'removed_role':dst,'source_role':src,'physical_source':physical(src),'target':row['target'],'frame_id':U[x],'coefficient_numerator':row['coefficient_numerator']})
    else:gate(physical(dst),physical(src),1,U[x],True)

for s in range(R):
    if s not in g['placed']:oldread(s,0)
for s,x in enumerate(g['first']):
    if x<=v and s not in g['placed']:source(s)
for i in sorted(g['phase']):mix(i)
for s in g['center_roles']:
    j=g['terminal'][s];F=U[g['roots'][j]];assert len(frames[F])==h-1
    word.append(('c',physical(s),v,ALL,1,F,0,('center',j-(len(g['roots'])-h))))
for s,F in sorted(g['placed'].items(),key=lambda z:(len(z[1]),z[0])):oldread(s,fid(F))
for s,x in enumerate(g['first']):
    if x<=v and s in g['placed']:source(s)
for i in range(len(g['ops'])):
    if i not in g['phase']:mix(i)
for s,j in sorted(g['terminal'].items(),key=lambda z:z[1]):
    if j<len(g['roots'])-h:
        t=g['targets'][j];F=dual(tm[t])
        if s in removed:word.append(('f',v,1<<t,F,('removed-terminal-read',s)))
        else:word.append(('r',physical(s),v,1<<t,1,F,('side',j,s)))
for _,d,s,sign,F in reversed(forward_workspace):gate(d,s,-sign,FULL)
assert len(direct_origins)==sum(x['incoming_count'] for x in inventory['selected'])

active=list(range(2*v))+[2*v+s for s in sorted(live)];active_set=set(active)
initial=[None]*(2*v+R);finish=[None]*len(initial)
for t in range(v):initial[t]=tm[t];initial[v+t]=0;finish[t]=FULL;finish[v+t]=dual(tm[t])
for s in live:initial[2*v+s]=fid(g['placed'].get(s,()));finish[2*v+s]=FULL

def scan(events,begin,end):
    current=begin[:];hist=Counter();copies=0;counts=[Counter(current[:v]),Counter(current[v:2*v])];digest=sha256();incidences=0
    def promote(s,F):
        nonlocal incidences
        assert s in active_set and current[s] is not None
        old=current[s]
        if old==F:return
        assert nested(old,F),('Illegal frame',s,frames[old],frames[F])
        assert nondeg(old) and nondeg(F),('Degenerate endpoint frame',old,F)
        r=len(frames[F])-len(frames[old]);assert r>0
        hist[r]+=1;current[s]=F;incidences+=1
        if s<2*v:
            bank=s//v;counts[bank][old]-=1
            if not counts[bank][old]:del counts[bank][old]
            counts[bank][F]+=1
    def targets(bank,mask,F):
        assert bank in (0,v) and mask>=0 and not(mask&~ALL)
        if len(counts[bank//v])==1 and counts[bank//v].get(F)==v:return
        while mask:
            b=mask&-mask;mask-=b;promote(bank+b.bit_length()-1,F)
    for e in events:
        digest.update(repr(e).encode())
        if e[0]=='g':
            _,d,s,c,F=e;assert c in (-1,1);promote(d,F);promote(s,F)
        elif e[0]=='d':
            _,d,s,c,F,idx,role=e;assert c in (-21,21);promote(d,F);promote(s,F)
        elif e[0]=='r':
            _,s,bank,mask,sign,F,key=e;promote(s,F);targets(bank,mask,F)
        elif e[0]=='f':
            _,bank,mask,F,key=e;targets(bank,mask,F)
        else:
            _,s,bank,mask,sign,F,T,key=e;promote(s,F);targets(bank,mask,T)
            assert (F==FULL and T==0) or nested(F,T) or nested(T,F)
            rank=abs(len(frames[F])-len(frames[T]));assert rank==h-1;hist[rank]+=1;copies+=1
    for s in active:promote(s,end[s])
    assert current==end
    return {'histogram':dict(hist),'copies':copies,'transitions':incidences,'word_sha256':digest.hexdigest()}

forward=scan(word,initial,finish)
def swap(s):return s+v if s<v else (s-v if s<2*v else s)
def reflect(e):
    if e[0]=='g':
        _,d,s,c,F=e;return ('g',swap(d),swap(s),-c,dual(F))
    if e[0]=='d':
        _,d,s,c,F,idx,role=e;return ('d',swap(d),swap(s),-c,dual(F),idx,role)
    if e[0]=='r':
        _,s,bank,mask,sign,F,key=e;return ('r',swap(s),v-bank,mask,-sign,dual(F),key)
    if e[0]=='f':
        _,bank,mask,F,key=e;return ('f',v-bank,mask,dual(F),key)
    _,s,bank,mask,sign,F,T,key=e;return ('c',swap(s),v-bank,mask,-sign,dual(F),dual(T),key)
reverse=[reflect(e) for e in reversed(word)]
assert [reflect(e) for e in reversed(reverse)]==word
rb=[None]*len(initial);re=[None]*len(initial)
for s in active:rb[swap(s)]=dual(finish[s]);re[swap(s)]=dual(initial[s])
backward=scan(reverse,rb,re)
assert forward['histogram']==backward['histogram'] and forward['copies']==backward['copies']==h
H=Counter({int(r):2*v*n for r,n in forward['histogram'].items()})
for s in live:H[m-h+len(frames[initial[2*v+s]])]+=2*v
H[(h-1)**2]+=2*v*v;H[1]+=v*v
H=Counter({r:n for r,n in H.items() if n})
oldH=Counter({int(r):n for r,n in choice['child_histogram'].items()})
delta=Counter();packets=[]
for row in inventory['selected']:
    sigma,M,F0=(row[k] for k in ['sigma','M','F0'])
    before=[m-h+sigma,1,F0-sigma,h-1-M];after=[m,F0-M,0,0]
    assert 0<=sigma<=M<=F0<=h-1 and sum(before)==sum(after)
    before_sorted=sorted(before,reverse=True);after_sorted=sorted(after,reverse=True)
    assert all(sum(after_sorted[:k])>=sum(before_sorted[:k]) for k in range(1,5))
    assert before_sorted!=after_sorted
    for width in before:
        if width:delta[width]-=2*v
    # The width-m term is only the padding used to compare changing W.
    if F0>M:delta[F0-M]+=2*v
    packets.append({'role':row['role'],'target':row['target'],'old':before,'new_with_dummy_m':after})
expected=Counter(oldH)
expected.update(delta);expected=Counter({r:n for r,n in expected.items() if n})
assert all(n>=0 for n in expected.values()) and H==expected,('Full profile != exact complete packet sum',H-expected,expected-H)
newR=len(live);newW=2*v*v+2*v*newR;rank=sum(r*n for r,n in H.items())
assert m*newW-rank==choice['deficit']==g['base_profile']['deficit']
hinges={k:sum(min(r,k)*n for r,n in H.items())+2*v*len(removed)*min(m,k)-sum(min(r,k)*n for r,n in oldH.items()) for k in range(1,m+1)}
assert all(x<=0 for x in hinges.values()) and min(hinges.values())<0

def plus(a,b):
    out=[];carry=0
    for i in range(max(len(a),len(b))):
        x=a[i] if i<len(a) else 0;y=b[i] if i<len(b) else 0
        out.append(x^y^carry);carry=(x&y)|(x&carry)|(y&carry)
    if carry:out.append(carry)
    while out and not out[-1]:out.pop()
    return tuple(out)
def scaled(mask,n):return tuple(mask if n>>i&1 else 0 for i in range(n.bit_length()))

def responses(events,inputbank,outputbank,expected_sign):
    P,M=[()]*R,[()]*R;XP,XM=[()]*v,[()]*v
    def accumulate(aux,positive,negative):
        assert aux>=2*v and aux-2*v in live
        r=aux-2*v;P[r],M[r]=plus(P[r],positive),plus(M[r],negative)
    for e in reversed(events):
        kind=e[0]
        if kind=='f':continue
        if kind in ('r','c'):
            aux,bank,sign=e[1],e[2],e[4];assert bank==outputbank
            key=e[-1]
            if key[0]=='old':s=key[1];seed=False
            elif key[0]=='side':s=key[2];seed=True
            else:s=next(s for s in g['center_roles'] if g['terminal'][s]==len(g['roots'])-h+key[1]);seed=True
            aa=readouts['terminal_positive' if seed else 'positive'][s]
            bb=readouts['terminal_negative' if seed else 'negative'][s]
            if sign<0:aa,bb=bb,aa
            accumulate(aux,aa,bb)
        elif kind=='d':
            _,dst,src,num,F,idx,role=e
            assert outputbank<=dst<outputbank+v and abs(num)==21
            aa=scaled(1<<(dst-outputbank),abs(num));bb=()
            if num<0:aa,bb=bb,aa
            accumulate(src,aa,bb)
        else:
            _,dst,src,sign,F=e;assert dst>=2*v
            aa,bb=P[dst-2*v],M[dst-2*v]
            if sign<0:aa,bb=bb,aa
            if src>=2*v:accumulate(src,aa,bb)
            else:
                assert inputbank<=src<inputbank+v,'Target used as control'
                t=src-inputbank;XP[t],XM[t]=plus(XP[t],aa),plus(XM[t],bb)
    dirty_ok=all(P[s]==M[s] for s in live)
    if expected_sign>0:source_ok=all(aa==plus(bb,scaled(1<<t,42)) for t,(aa,bb) in enumerate(zip(XP,XM)))
    else:source_ok=all(bb==plus(aa,scaled(1<<t,42)) for t,(aa,bb) in enumerate(zip(XP,XM)))
    digest=sha256()
    for arrays in (P,M,XP,XM):
        for row in arrays:
            digest.update(len(row).to_bytes(4,'little'))
            for plane in row:digest.update(plane.to_bytes((v+7)//8,'little'))
    return {'all_dirty_zero':dirty_ok,'source_is_expected_signed_identity':source_ok,'response_sha256':digest.hexdigest()}

forward_scalar=responses(word,0,v,1);reverse_scalar=responses(reverse,v,0,-1)
assert all(forward_scalar[k] and reverse_scalar[k] for k in ['all_dirty_zero','source_is_expected_signed_identity'])
direct_index=next(i for i,e in enumerate(word) if e[0]=='d')
omitted=responses(word[:direct_index]+word[direct_index+1:],0,v,1)
assert not (omitted['all_dirty_zero'] and omitted['source_is_expected_signed_identity'])
mutant=list(word);e=mutant[direct_index];mutant[direct_index]=e[:3]+(-e[3],)+e[4:]
wrong_sign=responses(mutant,0,v,1)
assert not (wrong_sign['all_dirty_zero'] and wrong_sign['source_is_expected_signed_identity'])
mutant=list(word);e=mutant[direct_index];mutant[direct_index]=e[:4]+(0,)+e[5:]
try:scan(mutant,initial,finish)
except AssertionError:illegal_frame_rejected=True
else:illegal_frame_rejected=False
assert illegal_frame_rejected

# Preserve the whole previously paid scalar bill and add an explicit safe
# direct-output bill. Each +/-21/42 update is 21 same-frame +/-1/42
# shears, with no new role, source copy or frame incidence. The extra
# eight groups are conservative bookkeeping allowance only.
# No savings from removed gates/readouts are needed for this upper bound.
extra_scalar=29*len(direct_origins)
newlocal=bill['local_scalar_upper']+extra_scalar
newG=16*(2*v*newlocal+8*N)
assert newG>=bill['global_scalar_group_upper']
profile=dict(g['base_profile']);profile.update(R=newR,W=newW,total_rank=rank,maxchild=max(H),child_multiplicities=dict(sorted(H.items())),pre_terminal_physical_roles=choice['R'],virtual_roles=R,birth_reuses=len(merge),terminal_eliminations=len(removed),terminal_direct_updates=len(direct_origins),deferred_roles=len(g['placed'])-len(removed),role_count_scope='Explicit physical birth-reused and terminal-elided word; DAG role formula is the pre-composition virtual count.',replay={'method':'Exact signed bit-plane all-column responses over Q, both orientations','source_columns':v,'dirty_columns':newR,'target_columns':v,'forward_signed_identity':1,'reflected_signed_identity':-1,'scratch_restored':True})
dd=Counter({int(k):n for k,n in profile['deferred_dims'].items()})
for row in inventory['selected']:dd[row['sigma']]-=1
profile['deferred_dims']=dict(sorted((k,n) for k,n in dd.items() if n))
scalar_bill={**{k:value for k,value in bill.items() if k not in {'rss_KiB','rss_bytes','seconds'}},'status':'PASS conservative scalar upper bound for new terminal composition','inherited_local_scalar_upper':bill['local_scalar_upper'],'terminal_direct_updates':len(direct_origins),'terminal_extra_scalar_charge':extra_scalar,'local_scalar_upper':newlocal,'global_scalar_group_upper':newG,'terminal_charge_rule':'Keep the entire inherited scalar bill and add 29 groups per direct output update: 21 same-frame shears of coefficient +/-1/42, plus eight conservative bookkeeping groups. No new role, source copy or frame incidence is introduced; denominator42 and odd21 grid are unchanged.','expansion':'Each numerator n/42 is |n| same-frame shears of coefficient sign(n)/42, with no new roles, source copies or frame transitions. Reverse all workspace/source gates chronologically. The retained eight-scan allowance, factor16 and explicit endpoint groups conservatively bound scalar bookkeeping/wrappers. Direct terminal updates use the same expansion, with eight additional bookkeeping groups per update.','original_bill_sha256':pins['READOUT_COST.json']['sha256']}
physical_record={'status':'PASS new composed literal word, full exact source/dirty responses and complete paid frames in both orientations','physical_roles':newR,'virtual_roles':R,'birth_reuses_preserved':len(merge),'terminal_roles_eliminated':len(removed),'distinct_terminal_targets':len({r['target'] for r in inventory['selected']}),'source_columns':v,'dirty_columns':newR,'target_columns':v,'coefficient_denominator':42,'direct_output_coefficient_numerators':[-21,21],'word_blocks':len(word),'forward_workspace_gates':len(forward_workspace),'forward_frame':forward,'reflected_frame':backward,'forward_scalar':forward_scalar,'reflected_scalar':reverse_scalar,'mutations':{'omitted_redirect_rejected':True,'wrong_redirect_sign_rejected':True,'illegal_redirect_frame_rejected':illegal_frame_rejected},'no_birth_slot_removed':True,'source_reads_at_original_operation_indices':True,'target_never_controls':True,'inverse_exact_reverse_of_actual_retained_workspace_events':True,'rank_deficit_preserved':True,'complete_profile_equals_packet_sum':True,'all_integer_hinges_nonpositive':True,'minimum_hinge':min(hinges.values()),'all_packets_sigma_equal_M_equal_F0':all(r['sigma']==r['M']==r['F0'] for r in inventory['selected']),'seconds':time.monotonic()-start,'input_pins':pins,'scope':'Finite exact composed physical witness and conservative scalar accounting; inherited all-size, fixed-tape, stopped-product and analytic transfer remain hypotheses. New kappa must be assembled separately.'}
payload={'h':h,'v':v,'virtual_roles':R,'physical_roles':sorted(live),'eliminated_terminal_roles':sorted(removed),'birth_pairs':choice['pairs'],'frames':[list(F) for F in frames],'initial_frames':initial,'final_frames':finish,'word':word,'direct_source_bindings':direct_origins,'input_sha256':{k:x['sha256'] for k,x in pins.items()}}
wordbytes=gzip.compress(json.dumps(payload,separators=(',',':')).encode(),mtime=0);(O/'word.json.gz').write_bytes(wordbytes)
physical_record['word_file_sha256']=sha256(wordbytes).hexdigest()
physical_record['seconds']=time.monotonic()-start
physical_record['rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1024 if sys.platform=='linux' else 1)
for name,x in [('complex-profile.json',profile),('READOUT_COST.json',scalar_bill),('physical-audit.json',physical_record),('majorization.json',{'packets':packets,'hinges':hinges,'profile_delta':dict(sorted(delta.items())),'padding_per_removed_role':m,'replication':2*v})]:
    (O/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
assert all((W/name).read_bytes()==data for name,data in source_bytes.items()), 'Construction sources changed during this run'
sources={str(Path('construction-sources')/name):sha256(data).hexdigest() for name,data in source_bytes.items()}
(O/'SOURCE.json').write_text(json.dumps({'inputs':pins,'construction_sources':sources,'source_attribution':'PR122 terminal-elision identity; PR125 shrunk frames; PR124 birth reuse; PR117 scalar DAG; this new explicit composition and audits with OpenAI Codex assistance.'},indent=2,sort_keys=True)+'\n')
print(json.dumps({k:physical_record[k] for k in ['status','physical_roles','birth_reuses_preserved','terminal_roles_eliminated','source_columns','dirty_columns','word_blocks','all_packets_sigma_equal_M_equal_F0','seconds','word_file_sha256']}|{'W':newW,'total_rank':rank,'deficit':m*newW-rank,'G':newG,'output':str(O)},indent=2))
