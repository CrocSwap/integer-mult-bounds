#!/usr/bin/env python3
"""Independent finite native/absolute-phase audit, stdlib only.

No imports from author verifier, Clifford compiler, or native operators. Derives
native columns from inverse-permutation Gram bits. Equality of 18 Pauli images
plus the zero ket proves equality of the two finite Clifford operators. Gaussian
integer vectors preserve absolute phase. Does not replay the 632-column word or
prove an all-width supplier theorem. Apache-2.0; OpenAI Codex assistance.
"""
import argparse, collections, functools, gzip, hashlib, json, pathlib, subprocess, time
from . import source
N=9; D=1<<N; PIN='ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c'

def need(c,m):
    if not c: raise ValueError(m)
def parity(v):return v.bit_count()%2
def lin(cols,x):
    y=0
    while x:
        b=x&-x;y^=cols[b.bit_length()-1];x-=b
    return y

def gram_native(cols):
    perm=[lin(cols,x) for x in range(D)]
    need(len(set(perm))==D,'native G invertible')
    back=[0]*D
    for x,y in enumerate(perm):back[y]=x
    gi=[back[1<<j] for j in range(N)]
    diagonal=[1^parity(v) for v in gi]
    cross=[sum(parity(gi[j]&gi[k])<<k for k in range(j+1,N)) for j in range(N)]
    def phase(y):
        return (sum(diagonal[j] for j in range(N) if y>>j&1)+2*sum(parity(cross[j]&y) for j in range(N) if y>>j&1))%4
    return tuple((y,phase(y)) for y in perm)

def inverse_mono(m):
    out=[None]*D
    for x,(y,q) in enumerate(m):out[y]=(x,-q%4)
    need(None not in out,'monomial permutation')
    return tuple(out)

def recipe_mono(r):
    rows=r['matrix_rows'];alpha=r['linear_Z4'];Q=r['quadratic_rows']
    need(len(rows)==len(alpha)==len(Q)==N,'recipe field dimensions')
    need(all(0<=v<D for v in rows+Q),'recipe bit field ranges')
    need(all((Q[i]>>j&1)==(Q[j]>>i&1) for i in range(N) for j in range(N)),'symmetric Q')
    need(all(alpha[i]%2==(Q[i]>>i&1) for i in range(N)),'Z4 diagonal convention')
    out=[]
    for x in range(D):
        y=sum(parity(v&x)<<i for i,v in enumerate(rows))^r['offset']
        q=r['phase']+sum(alpha[j] for j in range(N) if x>>j&1)+2*sum(parity((Q[j]>>(j+1))&(x>>(j+1))) for j in range(N) if x>>j&1)
        out.append((y,q%4))
    need(len({y for y,q in out})==D,'recipe invertible')
    return tuple(out)

@functools.lru_cache(None)
def mono_table(m):
    back={y:x for x,(y,q) in enumerate(m)};out=[]
    for kind in ('X','Z'):
        for j in range(N):
            def value(y):
                x=back[y]
                return ((m[x^(1<<j)][0]^y,(m[x^(1<<j)][1]-m[x][1])%4) if kind=='X' else (0,2*(x>>j&1)))
            v,p=value(0);z=0
            for k in range(N):
                vk,q=value(1<<k);need(vk==v and (q-p)%2==0,'Clifford affine Pauli')
                z|=((q-p)%4//2)<<k
            # All columns independently verify the recovered Pauli conjugation.
            need(all(value(y)==(v,(p+2*parity(z&y))%4) for y in range(D)),'all native Pauli columns')
            out.append((v,z,p))
    return tuple(out)

def multiply(a,b):
    x,z,p=a;v,w,q=b
    return x^v,z^w,(p+q+2*parity(z&v))%4

def apply_table(t,p):
    x,z,q=p;out=(0,0,q)
    for j in range(N):
        if x>>j&1:out=multiply(out,t[j])
    for j in range(N):
        if z>>j&1:out=multiply(out,t[N+j])
    return out

def rank(vec):
    piv={}
    for v in vec:
        while v:
            j=v.bit_length()-1
            if j not in piv:piv[j]=v;break
            v^=piv[j]
    return len(piv)

@functools.lru_cache(None)
def frame(U):
    r=len(U)
    if not r:return ()
    if r==N:return tuple(('C',1<<j,1) for j in range(N))
    basis=[]
    for v in list(U)+[1<<j for j in range(N)]:
        if rank(basis+[v])>len(basis):basis.append(v)
    need(len(basis)==N,'frame basis completion')
    k=gram_native(basis)
    return (('M',inverse_mono(k)),)+tuple(('C',1<<j,1) for j in range(r))+(('M',k),)

def adjoint(circuit):return tuple(('M',inverse_mono(e[1])) if e[0]=='M' else ('C',e[1],-e[2]) for e in reversed(circuit))
def irot(a,q):
    r,s=a
    return ((r,s),(-s,r),(-r,-s),(s,-r))[q%4]

def act_zero(circuit):
    vec=[(0,0)]*D;vec[0]=(1,0);den=0
    for e in circuit:
        if e[0]=='M':
            nxt=[(0,0)]*D
            for x,(y,q) in enumerate(e[1]):nxt[y]=irot(vec[x],q)
            vec=nxt
        else:
            q,s=e[1:];nxt=[]
            # C_q=((1+i)I+(1-i)X_q)/2. Its inverse conjugates i.
            for x,(a,b) in enumerate(vec):
                c,d=vec[x^q];nxt.append((a-s*b+c+s*d,b+s*a+d-s*c))
            vec=nxt;den+=1
        while den and all(a%2==b%2==0 for a,b in vec):
            vec=[(a//2,b//2) for a,b in vec];den-=1
    return tuple(vec),den

def circuit_table(circuit):
    t=tuple([(1<<j,0,0) for j in range(N)]+[(0,1<<j,0) for j in range(N)])
    for e in circuit:
        if e[0]=='M':t=tuple(apply_table(mono_table(e[1]),p) for p in t)
        else:
            q,s=e[1:]
            t=tuple((x^q,z,(p+(3 if s==1 else 1))%4) if parity(q&z) else (x,z,p) for x,z,p in t)
    return t

def conjugate(circuit):
    return tuple(('M',tuple((y,-q%4) for y,q in e[1])) if e[0]=='M' else ('C',e[1],-e[2]) for e in circuit)

def raw_read(repo,path):
    return source.raw(path)

def read(repo,path):
    raw=raw_read(repo,path)
    return raw,json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)

def run(repo):
    started=time.monotonic();a=argparse.Namespace(limit=None,output=None)
    pkg='research/kappa-round3-warp-20261022/';oldpkg='research/warp-interface-20261022/'
    raw,w=read(repo,pkg+'ACTUAL-WORD.json.gz');_,base=read(repo,oldpkg+'ACTUAL-WORD.json.gz');_,ph=read(repo,pkg+'PHASE-VALIDATION.json.gz');_,freeze=read(repo,pkg+'ACTUAL-WORD-FREEZE.json');manifest,src=read(repo,pkg+'SOURCES.json')
    need(hashlib.sha256(gzip.decompress(raw)).hexdigest()==freeze['canonical_payload_sha256']==ph['actual_word_canonical_sha256'],'actual payload pin')
    need(hashlib.sha256(manifest).hexdigest()==ph['source_manifest_sha256'],'phase manifest pin')
    need(all(hashlib.sha256(raw_read(repo,s['path'])).hexdigest()==s['sha256'] for s in src['files']),'source manifest bytes')
    c=w['canonical'];b=base['canonical'];need(c['h']==9,'nine-coordinate native domain');need(c['frames'][:len(b['frames'])]==b['frames'],'inherited frame prefix')
    need(all(len(U)<=N and all(type(x) is int and 0<x<D for x in U) and rank(U)==len(U) for U in c['frames']),'exact independent frame bases')
    oldG={v['op']:v['G_columns'] for v in b['warps']};newG={v['op']:v['G_columns'] for v in c['warps']};need(set(oldG)==set(newG)==set(range(1,73)),'72 exact shared maps')
    need(len(c['warps'])==len(b['warps'])==72,'one binding per map')
    need(all(newG[op]==oldG[op] for op in range(47,59)),'all twelve prelude-shared maps unchanged')
    changed=sorted(op for op in newG if newG[op]!=oldG[op]);need(changed==ph['changed_G_operators'] and len(changed)==20,'exact changed20 map set')
    maps={op:gram_native(cols) for op,cols in newG.items()};records={v['operator']:v for v in ph['native_operator_columns']};need(set(records)==set(changed),'changed native recipe coverage')
    for op in changed:
        r=records[op];need(r['G_columns']==newG[op] and r['recipe']['rank']==0 and r['recipe']['right'] is None,'changed map fields');need(recipe_mono(r['recipe']['left'])==maps[op],'changed native 512 columns + absolute phases')
    sets={d:{tuple(e[2:]) for e in p if e[0]=='warp'} for d,p in w['programs'].items()};need(sets['forward']==sets['backward'],'both actual signed warp class sets')
    classes={(r['operator'],r['input'],r['output']):r for r in ph['actual_warp_classes']};need(set(classes)==sets['forward'] and len(classes)==len(ph['actual_warp_classes'])==180,'180 class exact phase receipt coverage')
    counts=collections.Counter();controls={};results=[]
    for n,(key,r) in enumerate(sorted(classes.items())):
        if a.limit is not None and n>=a.limit:break
        op,u,v=key;need(r['G_columns']==newG[abs(op)],'same G shared at every occurrence')
        U,V=tuple(c['frames'][u]),tuple(c['frames'][v]);g=newG[abs(op)]
        if op<0:g=[inverse_mono(maps[-op])[1<<j][0] for j in range(N)]
        need({lin(g,x) for x in span(U)}==span(V),'signed transported exact frame subspace')
        physical=adjoint(frame(U))+(('M',maps[op] if op>0 else inverse_mono(maps[-op])),)+frame(V)
        for d in ('forward','backward'):
            actual=physical if d=='forward' else conjugate(physical);rec=r['recipes'][d];need(rec['rank']==0 and rec['right'] is None,'rank zero native recipe')
            decoded=(('M',recipe_mono(rec['left'])),)
            need(circuit_table(actual)==circuit_table(decoded),'all 18 independent Pauli images '+str((key,d)))
            need(act_zero(actual)==act_zero(decoded),'independent absolute phase '+str((key,d)))
            counts[d]+=1
        results.append(list(key))
        if n==0:
            wrong=dict(r['recipes']['forward']['left']);wrong['phase']=(wrong['phase']+1)%4
            controls['global_phase_preserves_Paulis_but_rejected']=circuit_table((('M',recipe_mono(wrong)),))==circuit_table(physical) and act_zero((('M',recipe_mono(wrong)),))!=act_zero(physical)
    controls['transpose_map_rejected']=any(gram_native([sum((newG[op][j]>>i&1)<<j for j in range(N)) for i in range(N)])!=maps[op] for op in changed)
    controls['sign_adjoint_differs_from_entry_conjugation']=any(inverse_mono(maps[op])!=tuple((y,-q%4) for y,q in maps[op]) for op in changed)
    need(all(controls.values()),'all independent negative controls')
    out={'status':'PASS_INDEPENDENT_ALL_180_NATIVE_PHASE_CLASSES' if len(results)==180 else 'PASS_BOUNDED_NATIVE_PHASE_CLASSES','pin':PIN,'changed_maps':changed,'native_columns_each':512,'frame_classes_checked':len(results),'directions':dict(counts),'controls':controls,'seconds':time.monotonic()-started,'coverage':results,'actual_payload_sha256':freeze['canonical_payload_sha256'],'scope':'Finite exact 9-coordinate maps and frame-bound native phases; 632-column word and all-width supplier theorem separate.'}
    return out

def span(U):
    out={0}
    for x in U:out|={y^x for y in list(out)}
    return out

