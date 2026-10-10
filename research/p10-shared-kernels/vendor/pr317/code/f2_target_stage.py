#!/usr/bin/env python3
# Prepared with substantial OpenAI Codex assistance. Apache-2.0.
# Target-prefix mechanism follows PR268/PR273 and the PR312 stage; exact F2 discovery and emission are freshly replayed.
"""Apply disjoint exact F2 target-prefix dependencies to an actual scalar word.

Usage: f2_target_stage.py CAND_DIR SELECTION.json OUT_DIR
This is a characteristic-two transform. It does not assert integer endpoint
agreement: the downstream signed-word/norm admission must reprice this word.
All frame bases are inherited; downstream exact nondegeneracy is still required.
"""
import hashlib, json, shutil, struct, sys
from array import array
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
if not __debug__: raise SystemExit('assertions required')
P, SELP, O = map(Path, sys.argv[1:4])
assert P.resolve() != O.resolve()
S=json.loads((P/'249-states.json').read_text())
FJ=json.loads((P/'frames.json').read_text()); H=FJ['h']
F={int(k):v for k,v in FJ['frames'].items()}; D={k:v['dim'] for k,v in F.items()}
V=S['v']; n=S['n']; ZERO=S['ZERO']
I={int(k):v for k,v in json.loads((P/'COHORT249-INITIAL.json').read_text()).items()}
FINAL={int(k):v for k,v in S['final'].items()}
R=array('i'); R.frombytes((P/'COHORT249-RECORDS.bin').read_bytes()); N=len(R)//6
sel=json.loads(SELP.read_text()); cut=sel['cut_record']; groups=sel['groups']
sha=lambda data:hashlib.sha256(data).hexdigest()
input_sha=sha(R.tobytes()); assert input_sha==sel['input_raw_sha256']==S['record_sha256']
assert N==S['record_count'] and 0<=cut<N and groups
assert sel['input_scalar_sha256']==S['physical']['scalar_projection_sha256']
BIDX={json.dumps(v['B'],separators=(',',':')):k for k,v in F.items()}
own={}; closes=defaultdict(list)
for j,g in enumerate(groups):
    g['frame']=BIDX[json.dumps(g['close_basis'],separators=(',',':'))]
    g['dependent']={int(k):v for k,v in g['dependent'].items()}
    assert cut<g['close_after_record']<N and D[g['frame']]==g['close_rank']
    closes[g['close_after_record']].append(j)
    used=set(g['dependent'])|{p for ps in g['dependent'].values() for p in ps}
    assert used==set(g['targets']) and not(set(g['dependent']) & {p for ps in g['dependent'].values() for p in ps})
    for t,ps in g['dependent'].items():assert ps and len(ps)==len(set(ps)) and t not in ps
    for t in g['targets']:
        assert 0<=t<V and t not in own; own[t]=j
        assert all(sum(x*y for x,y in zip(b,S['source_covectors'][t]))==0 for b in F[g['frame']]['B']), 'target close cap'
@lru_cache(None)
def sub(a,b):
    return D[a]<=D[b] and all(sum(x*y for x,y in zip(ar,br))==0 for ar in F[b]['A'] for br in F[a]['B'])
# Exact prefix responses in every formal column, including dirty registers.
cols=[1<<i for i in range(n)]+[0]; center=None; resps=Counter(); state=dict(I)
for i in range(N):
    op,a,b,c,f,z=R[6*i:6*i+6]
    if op==0:assert state[a]==b;state[a]=c
    elif op==1:
        assert c % 2 == 1
        if i>cut:
            if b-V in own:assert i>groups[own[b-V]]['close_after_record'], 'active member used as source'
            if a-V in own and i<=groups[own[a-V]]['close_after_record']:resps[a-V]^=cols[b]
        cols[a]^=cols[b]
    elif op==2:
        assert center is None and b==n;center=a;cols[n]=cols[a];state[n]=f
    elif op==3:assert center==a;center=None;cols[n]=0;del state[n]
    else:raise AssertionError(op)
    if i==cut:assert center is None and all(state[V+t]==ZERO for t in own)
    for j in closes.get(i,[]):
        assert center is None
        for t,ps in groups[j]['dependent'].items():
            response=resps[t]
            for p in ps:response^=resps[p]
            assert response==0, ('prefix dependency',j,t)
want=[1<<i for i in range(n)]
for t in range(V):want[V+t]^=1<<t
assert center is None and cols[:n]==want and state==FINAL
print('PASS exact prefix dependencies and input columns',flush=True)
# Re-emit the actual word, lazily charging every ascent.
state=dict(I); out=array('i'); inserted=[];deleted=[];center=None;hist=Counter();pairs=set()
zmax=max(R[6*i+5] for i in range(N) if R[6*i]==1); SETUP,RESTORE=zmax+1,zmax+2

def move(a,f):
    before=state[a]
    if before==f:return
    assert sub(before,f),(a,before,f)
    d=D[f]-D[before];assert d>=0
    out.extend((0,a,before,f,d,0));state[a]=f;pairs.add((before,f))
    if d:hist[d]+=1

def add(a,b,c,f,z):
    move(a,f);move(b,f)
    assert a!=b and c % 2 == 1
    if center is not None:assert a not in(center[0],n)
    out.extend((1,a,b,c,f,z))

def batch(j,sign,frame,z):
    g=groups[j]
    for t in g['targets']:move(V+t,frame)
    for t,ps in g['dependent'].items():
        for p in ps:add(V+t,V+p,sign,frame,z);inserted.append(len(out)//6-1)
for i in range(N):
    op,a,b,c,f,z=R[6*i:6*i+6]
    if op==1:
        j=own.get(a-V)
        if j is not None and a-V in groups[j]['dependent'] and cut<i<=groups[j]['close_after_record']:deleted.append(i)
        else:add(a,b,c,f,z)
    elif op==2:
        assert center is None and b==n;move(a,c);out.extend((op,a,b,c,f,z));state[b]=f;center=(a,b,c);hist[z]+=1
    elif op==3:
        assert center==(a,b,c) and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];center=None
    if i==cut:
        assert center is None and all(state[V+t]==ZERO for t in own)
        for j in range(len(groups)):batch(j,-1,ZERO,SETUP)
    for j in closes.get(i,[]):
        assert center is None;batch(j,1,groups[j]['frame'],RESTORE)
for a,f in sorted(FINAL.items()):move(a,f)
assert state==FINAL and center is None

def legality(word):
    state=dict(I);paid=Counter();ctr=None
    for k in range(0,len(word),6):
        op,a,b,c,f,z=word[k:k+6]
        if op==0:
            assert state[a]==b and sub(b,c) and D[c]-D[b]==f
            # Both reflected local ledgers have this same rank increment.
            assert len(F[b]['A'])-len(F[c]['A'])==f
            state[a]=c
            if f:paid[f]+=1
        elif op==1:
            assert a!=b and c % 2 == 1 and state[a]==state[b]==f
            if ctr is not None:assert a not in(ctr,n)
        elif op==2:
            assert ctr is None and b==n and state[a]==c and z==D[c]
            ctr=a;state[n]=f;paid[z]+=1
        elif op==3:
            assert ctr==a and b==n and state[a]==c and state[n]==f
            ctr=None;del state[n]
        else:raise AssertionError(op)
    assert ctr is None and state==FINAL
    return paid
oldhist=legality(R); newhist=legality(out);assert newhist==hist
for a,b in pairs:assert len(F[a]['A'])-len(F[b]['A'])==D[b]-D[a] and sub(a,b)
delta=hist.copy();delta.subtract(oldhist);delta={str(k):v for k,v in sorted(delta.items()) if v}
assert delta==sel['expected_total_delta'] and sum(int(k)*v for k,v in delta.items())==0
print('PASS legality and both reflected local ledgers',len(pairs),flush=True)

def replay(word,reverse=False,omit=None):
    cols=[1<<i for i in range(n)]+[0];copy=None
    for k in (range(len(word)-6,-1,-6) if reverse else range(0,len(word),6)):
        op,a,b,c,f,z=word[k:k+6]
        if op==1:
            if k//6==omit:continue
            cols[a]^=cols[b]
        elif op==(3 if reverse else 2):assert copy is None;copy=a;cols[n]=cols[a]
        elif op==(2 if reverse else 3):assert copy==a;copy=None;cols[n]=0
    return cols[:n]==want and copy is None
assert replay(out) and replay(out,True) and replay(R,True)
assert not replay(out,omit=inserted[0])
print('PASS every independent column forward/inverse and omitted-setup negative control',flush=True)

def source_span(word):
    # Arbitrary-precision integer source covectors, with inherited COPY exemption.
    content=[[0]*H for _ in range(n+1)]
    for i in range(V):assert D[I[i]]==1;content[i]=list(F[I[i]]['B'][0])
    checked=bad=0;maxabs=0;cache={}
    for k in range(0,len(word),6):
        op,a,b,c,f,z=word[k:k+6]
        if op==1:
            for r in(a,b):
                if V<=r<2*V or r==n:continue
                key=(f,tuple(content[r]))
                if key not in cache:cache[key]=all(sum(x*y for x,y in zip(ar,content[r]))==0 for ar in F[f]['A'])
                bad+=not cache[key];checked+=1
            content[a]=[x+c*y for x,y in zip(content[a],content[b])]
            maxabs=max(maxabs,max(map(abs,content[a]),default=0))
        elif op==2:content[n]=list(content[a])
        elif op==3:content[n]=[0]*H
    return dict(checked=checked,violations=bad,maximum_absolute_coefficient=maxabs)
sp_old=source_span(R);sp_new=source_span(out)
assert sp_new['violations']==sp_old['violations'],(sp_old,sp_new)
print('PASS source span',sp_old,sp_new,flush=True)
# Preserve input provenance and all non-word sidecars, including REORDER-STAGE.
O.mkdir(parents=True,exist_ok=True)
for p in P.iterdir():
    if p.is_file():shutil.copy2(p,O/p.name)
raw=out.tobytes();outsha=sha(raw)
for name in('COHORT249-RECORDS.bin','249-records.bin'):O.joinpath(name).write_bytes(raw)
S.update(record_sha256=outsha,record_count=len(out)//6)
O.joinpath('249-states.json').write_text(json.dumps(S,sort_keys=True,indent=2)+'\n')
compact_sha=None
if (P/'SOURCE-BINDING.json').exists():
    bind=json.loads((P/'SOURCE-BINDING.json').read_text());freed=set(bind['freed_roles']);live=[r for r in range(n) if r not in freed]
    mp={r:i for i,r in enumerate(live)};mp[n]=len(live)
    compact=b''.join(struct.pack('<6i',op,mp[a],b if op==0 else mp[b],c,f,z) for op,a,b,c,f,z in struct.iter_unpack('<6i',raw))
    compact_sha=sha(compact);O.joinpath('COMPACT-RECORDS.bin').write_bytes(compact)
    bind.update(word_sha256=outsha,compact_word_sha256=compact_sha)
    O.joinpath('SOURCE-BINDING.json').write_text(json.dumps(bind,sort_keys=True,indent=2)+'\n')
shutil.copyfile(SELP,O/'EXTRA-TARGET-SELECTION.json')
receipt=dict(status='PASS_LITERAL_F2_TARGET_PREFIX_STAGE',records_in=N,record_count=len(out)//6,
    groups=len(groups),dependents=sum(len(g['dependent']) for g in groups),inserted=len(inserted),deleted=len(deleted),
    input_record_sha256=input_sha,output_record_sha256=outsha,raw_sha256=outsha,compact_word_sha256=compact_sha,
    selection_sha256=sha(SELP.read_bytes()),paid_histogram=dict(sorted(hist.items())),histogram_delta=delta,
    forward=True,inverse=True,all_independent_columns=n,dirty_restoration=True,both_reflected_local_ledgers=True,
    checked_frame_pairs=len(pairs),omitted_setup_rejected=True,source_span_input=sp_old,source_span_output=sp_new,
    integer_endpoint_equivalence='not claimed: characteristic-two transform; downstream actual signed-word norm is required',
    prime_nondegeneracy='existing frames only, inherited from input; full exact downstream admission still required',
    setup_category=SETUP,restore_category=RESTORE)
O.joinpath('EXTRA-TARGET-STAGE.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps(receipt,indent=1))
