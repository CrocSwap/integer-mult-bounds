"""In-process F2 replay of a collective-kernel family selection on the gen4 word (adapted from alt272/scripts/gen4_kernel.py).
Multi-donor families: at the family cut every donor pays d += p at the entrance E (kernel_setup), un-sheared d -= p at FULL
(kernel_restore); pivot starts at E and loses its compensation reads. Donor chains are validated by the nested-MOVE assertion.
Controls: omit all setup / all restore gates; omit one sampled family's gates (size 3 and size 4) -> all must fail."""
import sys, json, importlib.util, time, collections, hashlib, math, struct
from array import array
from fractions import Fraction as Q
PKG, DUMP, SEL, OUT = sys.argv[1:5]
LIMIT = int(sys.argv[5]) if len(sys.argv)>5 else 10**9
def load(name, path):
    s=importlib.util.spec_from_file_location(name, path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m
t0=time.time()
ctx=load('p_prepare', PKG+'/prepare.py').prepare(); raw=load('p_raw', PKG+'/raw_ledger.py').run(ctx)
producer=load('p_phys', PKG+'/code/physical527.py').run(dict(ctx), ctx['SOURCE_TEXT'])
producer=load('p_parity', PKG+'/parity_transform.py').run(producer)
print('produced', time.time()-t0, flush=True)
W,C=producer['W'],producer['C']; old=producer['records']; initial=dict(producer['initial_state']); ZERO,FULL=producer['ZERO'],producer['FULL']; v=W.v; n=2*v+len(producer['context']['regs'])
cats=list(producer['physical']['category_names']); readcat=cats.index('dirty_read'); setupcat=len(cats); restorecat=len(cats)+1; cats+=['kernel_setup','kernel_restore']
assert hashlib.sha256(old.tobytes()).hexdigest()=='60830cb24fbdd5a26942c4aa897d0ae30738ca5772ab83d6c57be666ddc95f7a'
sel=json.load(open(SEL))
entries=[dict(pivot=p['a'],donors=[p['b']],cut=p['cut'],cut_read=p['cut_read'],rank=p['rank'],basis=p['basis'],kind='pair') for p in sel['pairs']]
entries+=[dict(pivot=f['pivot'],donors=f['donors'],cut=f['cut'],cut_read=f['cut_read'],rank=f['rank'],basis=f['basis'],kind=f['kind']) for f in sel['families']]
entries=entries[:LIMIT]
final=dict(initial)
for k in range(0,len(old),6):
    if old[k]==0: final[old[k+1]]=old[k+3]
# transcript facts: reads, first touch frames
members=set(e['pivot'] for e in entries)|set(d for e in entries for d in e['donors'])
pivots={e['pivot'] for e in entries}; assert len(pivots)==len(entries) and not (pivots & {d for e in entries for d in e['donors']}), 'pivot reused or pivot is a donor'
lastread={}; firsttouch={}; nreads=collections.Counter()
for k in range(0,len(old),6):
    op,a,b,c,f,z=old[k:k+6]; i=k//6
    if op==1:
        if b in members and z==readcat and f==ZERO and v<=a<2*v and c%2: lastread[b]=i; nreads[b]+=1; continue
        for s in (a,b):
            if s in members and s not in firsttouch: firsttouch[s]=(i,f)
    elif op==2:
        if a in members and a not in firsttouch: firsttouch[a]=(i,c)
memcut=collections.defaultdict(int); bycut=collections.defaultdict(list); chosen={}
for e in entries:
    ms=[e['pivot']]+e['donors']
    cut=max(lastread[s] for s in ms); assert cut==e['cut'] and [old[6*cut+j] for j in (1,2,3)]==e['cut_read'], ('cut mismatch',e)
    assert cut<min(firsttouch[s][0] for s in ms)
    f=W.register(e['basis']); assert C.dimf[f]==e['rank'] and C.nondeg(f), ('entrance', e)
    for s in ms:
        assert initial[s]==ZERO and final[s]==FULL and C.sub(f,firsttouch[s][1]), ('entrance not inside first frame', s)
        memcut[s]=max(memcut[s],cut)
    e['frame']=f; chosen[e['pivot']]=e; bycut[cut].append(e); initial[e['pivot']]=f
for cut in bycut: bycut[cut].sort(key=lambda e:(e['rank'],e['pivot']))
print('entries', len(entries), collections.Counter(e['kind'] for e in entries), 'distinct cuts', len(bycut), 'rank hist', dict(sorted(collections.Counter(e['rank'] for e in entries).items())), flush=True)
state=dict(initial); out=array('i'); temporary=None; skipped=0; gate_index={}  # record index of each emitted setup/restore gate per entry
def move(s,f):
    before=state[s]
    if before==f: return
    assert C.sub(before,f),('nonnested',s,before,f); gap=C.dimf[f]-C.dimf[before]; assert gap>=0; out.extend((0,s,before,f,gap,0)); state[s]=f
def add(a,b,c,f,z): move(a,f); move(b,f); out.extend((1,a,b,c,f,z))
for k in range(0,len(old),6):
    op,a,b,c,f,z=old[k:k+6]; i=k//6
    if op==1:
        if b in chosen and f==ZERO and z==readcat: assert i<=chosen[b]['cut']; skipped+=1
        else:
            if not (b in members and z==readcat and f==ZERO and v<=a<2*v):   # donors keep their compensation reads
                for s in (a,b):
                    if s in members: assert i>memcut[s], ('touched before cut', s)
            add(a,b,c,f,z)
    elif op==2:
        assert temporary is None; move(a,c); state[b]=f; temporary=(a,b,c); out.extend((op,a,b,c,f,z))
        if a in members: assert i>memcut[a]
    elif op==3: assert temporary==(a,b,c); out.extend((op,a,b,c,f,z)); del state[b]; temporary=None
    if i in bycut:
        assert temporary is None
        for e in bycut[i]:
            for d in e['donors']:
                add(d,e['pivot'],1,e['frame'],setupcat); gate_index.setdefault(e['pivot'],[]).append(len(out)//6-1)
for s in sorted(final): move(s,final[s])
for e in entries:
    for d in e['donors']: add(d,e['pivot'],-1,FULL,restorecat); gate_index[e['pivot']].append(len(out)//6-1)
assert state==final and skipped==sum(nreads[e['pivot']] for e in entries)
print('emitted', len(out)//6, 'records; removed reads', skipped, 'gates', 2*sum(len(e['donors']) for e in entries), time.time()-t0, flush=True)
def replay(records,reverse=False,omit=None,omit_idx=()):
    columns=[1<<i for i in range(n+1)]; wanted=[1<<i for i in range(n)]; temporary=None; count=0; omit_idx=set(omit_idx)
    for t in range(v): wanted[v+t]^=1<<t
    for k in (range(len(records)-6,-1,-6) if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if z==omit or (k//6) in omit_idx: continue
            assert c%2; columns[a]^=columns[b]; count+=1
        elif op==(3 if reverse else 2): temporary=a; columns[b]=columns[a]
        elif op==(2 if reverse else 3): assert columns[a]==columns[b]; temporary=None
    wrong=sum(1 for i in range(n) if columns[i]!=wanted[i])
    if omit is None and not omit_idx: assert not wrong, ('F2 failure', reverse, wrong)
    else: assert wrong, 'vacuous control'
    return count, wrong
fw=replay(out); iv=replay(out,True); c1=replay(out,omit=setupcat); c2=replay(out,omit=restorecat)
print('F2 replay PASS forward/inverse; ADDs', fw[0], 'controls wrong rows: omit all setup', c1[1], 'omit all restore', c2[1], time.time()-t0, flush=True)
samples={}
for kind in ('tri','quad','quint','pair'):
    e=next((e for e in entries if e['kind']==kind),None)
    if e is None: continue
    g=gate_index[e['pivot']]; nd=len(e['donors'])
    r_setup=replay(out,omit_idx=g[:nd]); r_one=replay(out,omit_idx=g[:1]); r_restore=replay(out,omit_idx=g[nd:])
    samples[kind]=dict(pivot=e['pivot'],donors=e['donors'],rank=e['rank'],wrong_rows_omit_family_setup=r_setup[1],wrong_rows_omit_one_donor_gate=r_one[1],wrong_rows_omit_family_restore=r_restore[1])
    print('per-family controls', kind, samples[kind], flush=True)
# frame census of the emitted word
hist=collections.Counter(); st=dict(initial)
for k in range(0,len(out),6):
    op,a,b,c,f,z=out[k:k+6]
    if op==0: assert st[a]==b and C.sub(b,c); st[a]=c; hist[C.dimf[c]-C.dimf[b]]+=1 if C.dimf[c]>C.dimf[b] else 0
    elif op==1: assert st[a]==st[b]==f
    elif op==2: assert st[a]==c; st[b]=f; hist[z]+=1
    elif op==3: del st[b]
hist={k:c for k,c in hist.items() if k and c}
oldh=collections.Counter({int(k):c for k,c in producer['physical']['paid_histogram'].items()}); delta=collections.Counter(hist); delta.subtract(oldh); delta={k:c for k,c in delta.items() if c}
print('one-stage histogram delta', dict(sorted(delta.items())), 'rank mass', sum(k*c for k,c in hist.items()), 'vs', producer['physical']['paid_rank_mass'], flush=True)
if LIMIT>=10**9:
    exp={int(k):c for k,c in sel['expected_local_delta'].items()}
    print('delta matches selection model:', delta==exp, flush=True)
    if delta!=exp: print('  model delta', dict(sorted(exp.items())))
# price with the validated ledger model (entrances removed from the five-stage histogram)
gauges=collections.Counter({int(k):c for k,c in raw['auxiliary_entrance_rank_histogram'].items()})
for e in entries: gauges[e['rank']]+=1
five=collections.Counter({r:5*c for r,c in hist.items()}); five.update({int(k):c for k,c in raw['five_stage_profile']['idle_histogram'].items()})
H5=collections.Counter(five)
H5={k:c for k,c in H5.items() if c}
cost=load('p_moment', PKG+'/moment.py')
mass=sum(k*c for k,c in H5.items()); assert mass%10==0, mass
W_lit=mass//2+2200; literal={k:60*c for k,c in H5.items()}; normalized={k:c//5 for k,c in literal.items()}; Wn=W_lit//5; m=120
root=cost.certify(normalized,m,Wn,True); c=Q(int(Q(root['lower'])*10**18),10**18); bm=cost.moment(normalized,m,Wn,c,True); nb=cost.moment(normalized,m,Wn,c+Q(1,10**18),True); assert bm[1]<1<nb[0]
chain=[Q(384599,10**10)]
for _ in range(3): chain.append((1-c)*c+c*chain[-1])
bit=chain[-1]; eta=Q(1,10**12); q=bit*(1-2*eta); mn=(1-eta)*q/(1+q); ticks=mn*10**18; kap=Q((ticks.numerator-1)//ticks.denominator,10**18)
print('PRICE (ledger model, banks not re-tiled): W_lit', W_lit, 'W', Wn, 'coarse %.15e kappa %.15e' % (float(c), float(kap)), 'entrance ranks', dict(sorted(gauges.items())), flush=True)
json.dump(dict(entries=len(entries),kinds=dict(collections.Counter(e['kind'] for e in entries)),removed_reads=skipped,records=len(out)//6,adds=fw[0],controls=dict(omit_all_setup_wrong=c1[1],omit_all_restore_wrong=c2[1]),per_family_controls=samples,delta={str(k):c for k,c in sorted(delta.items())},W_lit=W_lit,kappa=str(kap),kappa_float=float(kap),coarse=str(c),entrance_ranks={str(k):c for k,c in sorted(gauges.items())},seconds=time.time()-t0), open(OUT,'w'), indent=1)
