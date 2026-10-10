"""Second retiming search on the post-sink word: greedy descent of sum phi(r), phi(r)=r ln(120/r), over single ADD gates
(candidates: frames on either operand chain, constructed minimal join of the preceding frames [+ operand span], maximal
meet of the following frames) and connected same-frame blocks. usage: python3 -B discovery/descent2_dump.py POSTSINK.pkl; python3 -B discovery/descent2_search.py POSTSINK.pkl OUT.json [passes] [--noblocks] [--runmax=K]; python3 discovery/descent2_freeze.py POSTSINK.pkl OUT.json descent2-selection.json. Prepared with Anthropic Claude assistance; Apache-2.0"""
import sys,pickle,json,math,time,hashlib,importlib.util
from collections import Counter,defaultdict
from array import array
from pathlib import Path
t0=time.time()
D=pickle.load(open(sys.argv[1],'rb'));outp=Path(sys.argv[2]);PASSES=int(sys.argv[3]) if len(sys.argv)>3 else 6;BLOCKS='--noblocks' not in sys.argv;RUNMAX=int(next((a.split('=')[1] for a in sys.argv if a.startswith('--runmax=')),'3'))
spec=importlib.util.spec_from_file_location('bk',Path(__file__).resolve().parent.parent/'gen5bit/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py');bk=importlib.util.module_from_spec(spec);spec.loader.exec_module(bk)
reduce_rows,kernel,rank,dot=bk.reduce_rows,bk.kernel,bk.rank,bk.dot
old=array('i');old.frombytes(D['records']);A,B,dimf=D['A'],D['B'],D['dimf'];chi=D['chi'];h=D['h'];v=D['v'];n=D['nregs'];initial=D['initial'];final=D['final'];ZERO=D['ZERO']
assert n==len(initial)
def canon(rows):
    Bc,_=reduce_rows(rows,h);return tuple(sorted(map(tuple,Bc),key=lambda r:next(i for i,x in enumerate(r) if x)))
ids={}
for f in sorted(B):ids.setdefault(canon(B[f]),f)
NEW={}
def register(rows):
    key=canon(rows)
    if key in ids:return ids[key]
    f=max(B)+1;An,_=kernel(list(key),h);B[f],A[f],dimf[f]=key,An,len(key);ids[key]=f;NEW[f]=key;return f
cc={}
def sub(f1,f2):
    if f1==f2:return True
    r=cc.get((f1,f2))
    if r is None:
        r=dimf[f1]<=dimf[f2] and all(dot(a,b)==0 for a in A[f2] for b in B[f1]);cc[(f1,f2)]=r
    return r
nd={}
def nondeg(f):
    r=nd.get(f)
    if r is None:
        Bf,Af=B[f],A[f]
        if not Bf or len(Bf)==h:r=True
        elif len(Bf)<=len(Af):
            s=[sum(b) for b in Bf];M=[[9*dot(Bf[i],Bf[j])-s[i]*s[j] for j in range(len(Bf))] for i in range(len(Bf))];r=rank(M,len(Bf))==len(Bf)
        else:
            s=[sum(a) for a in Af];M=[[(9-h)*dot(Af[i],Af[j])+s[i]*s[j] for j in range(len(Af))] for i in range(len(Af))];r=rank(M,len(Af))==len(Af)
        nd[f]=r
    return r
jc={};mc={}
def join(fs):
    fs=tuple(sorted(set(fs)))
    if len(fs)==1:return fs[0]
    r=jc.get(fs)
    if r is None:
        top=max(fs,key=lambda f:dimf[f])
        if all(sub(f,top) for f in fs):r=top
        else:r=register([row for f in fs for row in B[f]])
        jc[fs]=r
    return r
def meet(fs):
    fs=tuple(sorted(set(fs)))
    if len(fs)==1:return fs[0]
    r=mc.get(fs)
    if r is None:
        bot=min(fs,key=lambda f:dimf[f])
        if all(sub(bot,f) for f in fs):r=bot
        else:
            K,_=kernel([row for f in fs for row in A[f]],h);r=register(K) if K else register([])
        mc[fs]=r
    return r
LN=[0.0]+[d*math.log(120/d) for d in range(1,121)]
def cost(x,y):return LN[dimf[y]-dimf[x]]
N=len(old)//6
chain={i:[] for i in initial};owner={i:[] for i in initial};gate_slots={};gates=[];fixed=set();copy=None
for k in range(N):
    op,a,b,c,f,z=old[6*k:6*k+6]
    if op==1:
        sl=[(a,len(chain[a]))];chain[a].append(f);owner[a].append(k)
        if b!=n:sl.append((b,len(chain[b])));chain[b].append(f);owner[b].append(k)
        gate_slots[k]=sl;gates.append(k)
        if b==n or (copy is not None and (a==copy[0] or b==copy[0])):fixed.add(k)
    elif op==2:copy=(a,b,c);chain[a].append(c);owner[a].append(-1)
    elif op==3:copy=None
gate_frame={k:old[6*k+4] for k in gates}
def prevf(r,p):return chain[r][p-1] if p>0 else initial[r]
def nextf(r,p):return chain[r][p+1] if p+1<len(chain[r]) else final[r]
def hist():
    H=Counter()
    for i in initial:
        bef=initial[i]
        for f in chain[i]+[final[i]]:
            d=dimf[f]-dimf[bef];assert d>=0
            if d:H[d]+=1
            bef=f
    return H
H0=hist();L0=sum(LN[d]*c for d,c in H0.items())
print('gates',len(gates),'fixed',len(fixed),'calls',sum(H0.values()),'mass',sum(d*c for d,c in H0.items()),'L %.3f'%L0,'%.0fs'%(time.time()-t0),flush=True)
def spanok(g,need):
    Ag=A[g]
    return all(all(dot(x,chi[s])==0 for x in Ag) for s in need)
spanframe_cache={}
def spanframe(need):
    key=frozenset(need)
    r=spanframe_cache.get(key)
    if r is None:r=register([chi[s] for s in need]) if need else register([]);spanframe_cache[key]=r
    return r
selected={};moves=Counter();gain_by=Counter()
# block bookkeeping: span need of each gate is recorded during sweep (only for gates in plateau candidate blocks)
def gate_eval(slots,g):
    return sum(cost(prevf(r,p),g)+cost(g,nextf(r,p)) for r,p in slots)
def setframe(k,g):
    for r,p in gate_slots[k]:chain[r][p]=g
    gate_frame[k]=g
    if g==old[6*k+4]:selected.pop(k,None)
    else:selected[k]=g
for it in range(PASSES):
    columns=[{i:1} if i<v else {} for i in range(n)];center=None;moved=0;gain=0.0;needs={}
    for k in range(N):
        op,a,b,c,f,z=old[6*k:6*k+6]
        if op==0:continue
        if op==2:center=a;continue
        if op==3:center=None;continue
        source=center if b==n else b;ca=columns[a]
        for s,x in columns[source].items():
            y=ca.get(s,0)+c*x
            if y:ca[s]=y
            else:del ca[s]
        if k in fixed:continue
        need=set()
        if not(v<=a<2*v):need.update(ca)
        if not(v<=b<2*v) and b!=n:need.update(columns[b])
        if BLOCKS:needs[k]=frozenset(need)
        slots=gate_slots[k];cur=gate_frame[k]
        P=[prevf(r,p) for r,p in slots];Nx=[nextf(r,p) for r,p in slots]
        cand=set()
        for r,p in slots:cand.update(chain[r]);cand.add(initial[r]);cand.add(final[r])
        J=join(P);M=meet(Nx)
        if not sub(J,M):continue
        cand.add(J);cand.add(M)
        base=gate_eval(slots,cur)
        opts=[]
        for g in cand:
            if g==cur:continue
            if not(sub(J,g) and sub(g,M)):continue
            d=gate_eval(slots,g)-base
            if d<-1e-9:opts.append((d,g))
        if not opts:continue
        opts.sort()
        done=False
        for d,g in opts:
            if nondeg(g) and spanok(g,need):
                setframe(k,g);moved+=1;gain+=d;moves['chain' if g in initial.values() or any(g in chain[r] for r,p in slots) and g not in NEW else 'constructed']+=1;done=True;break
        if not done:
            # minimal frame containing the operand span as well
            JS=join([J,spanframe(need)])
            if JS!=J and sub(JS,M) and JS!=cur and nondeg(JS):
                d=gate_eval(slots,JS)-base
                if d<-1e-9:setframe(k,JS);moved+=1;gain+=d;moves['constructed_span']+=1
    print('pass',it,'single moved',moved,'gain %.4f'%gain,'selected',len(selected),'new frames',len(NEW),'%.0fs'%(time.time()-t0),flush=True)
    bm=0;bgain=0.0
    if BLOCKS:
        def block_try(ks,tag):
            ks=set(ks);slots=[(r,p) for k in ks for r,p in gate_slots[k]];sset=set(slots)
            bprev=[];bnext=[];regs=set();edges=set()
            for r,p in slots:
                regs.add(r);edges.add((r,p-1,p));edges.add((r,p,p+1))
                if (r,p-1) not in sset:bprev.append(prevf(r,p))
                if (r,p+1) not in sset:bnext.append(nextf(r,p))
            J=join(bprev);M=meet(bnext)
            if not sub(J,M):return 0
            def fr(r,p,g):
                if g is not None and (r,p) in sset:return g
                return initial[r] if p<0 else final[r] if p>=len(chain[r]) else chain[r][p]
            def ev(g):
                return sum(cost(fr(r,p,g) if (r,p) in sset else fr(r,p,None),fr(r,q,g) if (r,q) in sset else fr(r,q,None)) for r,p,q in edges)
            # current cost uses actual frames
            base=sum(cost(fr(r,p,None),fr(r,q,None)) for r,p,q in edges)
            cand={J,M}
            for r in regs:cand.update(chain[r]);cand.add(initial[r]);cand.add(final[r])
            opts=sorted((ev(g)-base,g) for g in cand if sub(J,g) and sub(g,M))
            for d,g in opts:
                if d>=-1e-9:break
                if nondeg(g) and all(spanok(g,needs[k]) for k in ks):
                    for k in ks:setframe(k,g)
                    moves[tag]+=1;moves[tag+'_gates']+=len(ks);return d
            return 0
        for r in chain:
            ow=owner[r]
            for p in range(1,len(ow)):
                k1,k2=ow[p-1],ow[p]
                if k1>=0 and k2>=0 and k1!=k2 and k1 in needs and k2 in needs:
                    d=block_try((k1,k2),'pair')
                    if d:bm+=2;bgain+=d
                for L in range(4,RUNMAX+1):
                    if p>=L-1:
                        ks=ow[p-L+1:p+1]
                        if min(ks)>=0 and len(set(ks))==L and all(k in needs for k in ks):
                            d=block_try(ks,'run%d'%L)
                            if d:bm+=L;bgain+=d
                if p>=2:
                    k0=ow[p-2]
                    if k0>=0 and k0 in needs and len({k0,k1,k2})==3 and k1 in needs and k2 in needs:
                        d=block_try((k0,k1,k2),'triple')
                        if d:bm+=3;bgain+=d
        print('pass',it,'blocks moved gates',bm,'gain %.4f'%bgain,'%.0fs'%(time.time()-t0),flush=True)
    if not moved and not bm:break
H1=hist();L1=sum(LN[d]*c for d,c in H1.items())
delta=Counter(H1);delta.subtract(H0);delta={d:c for d,c in sorted(delta.items()) if c}
print('moves',dict(moves),'delta',delta,'removed calls',sum(H0.values())-sum(H1.values()),'L %.4f -> %.4f (dL %.4f)'%(L0,L1,L1-L0),flush=True)
def sha_basis(Bf):return hashlib.sha256(json.dumps([list(r) for r in Bf],separators=(',',':')).encode()).hexdigest()
entries=[]
for k in sorted(selected):
    op,a,b,c,f,z=old[6*k:6*k+6];g=selected[k]
    entries.append(dict(record=k,scalar=[a,b,c,z],category=D['cats'][z],old_dimension=dimf[f],old_basis_sha256=sha_basis(B[f]),new_basis=[list(map(int,r)) for r in B[g]],new_dimension=dimf[g],constructed=g in NEW))
outp.write_text(json.dumps(dict(source_record_count=N,selected_gate_count=len(entries),local_delta={str(d):c for d,c in delta.items()},removed_calls=sum(H0.values())-sum(H1.values()),dL_local=L1-L0,moves=dict(moves),new_frames=len({e['new_basis'].__repr__() for e in entries if e['constructed']}),entries=entries),indent=1)+'\n')
print('wrote',outp,len(entries),'%.0fs'%(time.time()-t0))
