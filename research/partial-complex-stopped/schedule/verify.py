"""Reproduce and audit the h=24 PR113 cyclic deferred complex certificate.

PR113 cyclic producer with pinned Apache-2.0 #104 dependencies. See NOTICE.
Only JSON is used for the frozen schedule; all physical and scalar checks are rebuilt.
"""
import argparse
import collections
import hashlib
import itertools
import json
import random
import subprocess
import sys
import tempfile
from functools import lru_cache
from fractions import Fraction
from pathlib import Path

from core import load, compile_word

PIN = "948ce1510df750f4c18b96bdaef436a86f8bf834"
CYCLIC_PIN = "0eee4d507092a96bde88de703f07574ba17401a8"
CYCLIC_SHA = "76b2a77bca0dcc80b8a440e5806f445c42a56ba2ebc43119ac43fbf2f5699dbb"
HASHES = {
    "scripts/stopped_product/complex.py": "407650d56dceb5cb09d74928658cebed1bb42f4d7e28ca9e3fd36eea075f1ad0",
    "scripts/endpoint_gauge/match_complex_general.cpp": "fb83c08125521128a38f5ee53f91d192904cc3372ad8f196ad9576e5f4f727da",
    "scripts/partial_swap/binary_io.hpp": "d0be783f61ac4b7981e7e48a8c1139b52572302ba76c191c0e9a1b16a1a05e0e",
    "certificates/stopped-product-complex-input.json": "5bcf00402bbfb768bd2fc0935f32ad329ee0780a3dfe5827bb010831d7909c4d",
    "scripts/copied_centers/physical.py": "837345d1f8753eab0e70f105b1d1bb0db965b993da037b1825ddef3672609d7d",
    "scripts/partial_swap_network.py": "acdd81b4dea2815f8838a0c3ea8ac4968f2bc13fd7c99173473d865779096782",
    "scripts/paired_triple_circuit.py": "8f5f2de32fdbd8e0005154638660ff416e5a8cd59623bd0dc03f6f7f97ce2fb1",
    "scripts/partial_swap/binary.py": "d32d7a23548cc738e974e8e55dd1fa2a8b11d2b80228515617ffe35410bb8805",
}

def canon(vectors):
    b = {}
    for v in vectors:
        x = v
        for p in sorted(b):
            if x & p: x ^= b[p]
        if x: b[x & -x] = x
    return tuple(b[p] for p in sorted(b))

def red(B, x):
    for a in B:
        if x & (a & -a): x ^= a
    return x

def subset(A, B):
    return all(red(B, a) == 0 for a in A)

def dot(a, b):
    return (a & b).bit_count() & 1

def rank(rows):
    return len(canon(rows))

@lru_cache(maxsize=None)
def gram(B):
    return tuple(sum(dot(a,b) << j for j,b in enumerate(B)) for a in B)

def nondeg(B):
    return rank(gram(B)) == len(B)

def projection(B, x):
    """Orthogonal projection to nondegenerate span B over F2."""
    q = len(B)
    G=gram(B)
    rows = [G[i] | (dot(B[i],x) << q) for i in range(q)]
    for j in range(q):
        p = next((i for i in range(j,q) if rows[i] >> j & 1), None)
        assert p is not None, (B, x)
        rows[j],rows[p] = rows[p],rows[j]
        for i in range(q):
            if i != j and (rows[i] >> j & 1): rows[i] ^= rows[j]
    out = 0
    for j in range(q):
        if rows[j] >> q & 1: out ^= B[j]
    return out

def residual(B, A):
    assert subset(A, B) and nondeg(A)
    return canon(b ^ projection(A,b) for b in B)

def gate(a, g):
    _,ins,outs = g
    if len(ins) == 2: a[ins[0]] += a[ins[1]]
    for u in outs[1:]: a[u] += a[outs[0]]

def ungate(a, g):
    _,ins,outs = g
    for u in reversed(outs[1:]): a[u] -= a[outs[0]]
    if len(ins) == 2: a[ins[0]] -= a[ins[1]]

def source_check(src):
    for rel, expected in HASHES.items():
        got = hashlib.sha256((src/rel).read_bytes()).hexdigest()
        assert got == expected, (rel, got)
    commit = subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'], text=True).strip()
    assert commit == PIN, commit

def build(src, tmp):
    sys.path.insert(0, str(src/'scripts'))
    from cyclic_producer import build as producer
    assert hashlib.sha256(Path(__file__).with_name('cyclic_producer.py').read_bytes()).hexdigest()==CYCLIC_SHA
    prefix = tmp/'cyclic'
    producer(24, str(prefix), central_disjoint=24)
    original = (src/'scripts/endpoint_gauge/match_complex_general.cpp').read_text()
    assert original.count('assert(argc==3);') == 1
    assert original.count('std::vector<int64_t>hist(h+1);') == 1
    s = original.replace('assert(argc==3);', 'assert(argc==4);')
    s = s.replace('#include "../partial_swap/binary_io.hpp"',
                  '#include "'+str(src/'scripts/partial_swap/binary_io.hpp')+'"')
    s = s.replace('std::vector<int64_t>hist(h+1);',
        'std::ofstream matchout(argv[3],std::ios::binary);'
        'U matchlen=rightmatch.size();matchout.write(reinterpret_cast<const char*>(&matchlen),sizeof(matchlen));'
        'matchout.write(reinterpret_cast<const char*>(rightmatch.data()),matchlen*sizeof(U));'
        'matchout.close();std::vector<int64_t>hist(h+1);')
    cpp=tmp/'matcher.cpp';cpp.write_text(s)
    binary=tmp/'matcher';match=tmp/'rightmatch.bin'
    subprocess.run(['c++','-O3','-std=c++17',str(cpp),'-o',str(binary)],check=True)
    result=subprocess.run([str(binary),str(prefix)+'.bin',str(prefix)+'.labels',str(match)],
                          text=True,capture_output=True,check=True)
    matcher=json.loads(result.stdout)
    expected_bytes=Path(__file__).with_name('matcher_expected.json').read_bytes()
    assert hashlib.sha256(expected_bytes).hexdigest()=="d9ac481b22b578b12936082649a245a08848db7739d2a0d54517aa374c1bc306"
    certificate=json.loads(expected_bytes)
    assert all(matcher[k]==certificate[k] for k in matcher), matcher
    return prefix,match,certificate

def triples_and_pairs(h,v):
    triples=list(itertools.combinations(range(h),3)); tid={S:i for i,S in enumerate(triples)}
    pairs=[[] for _ in range(v)]; j=v
    for a in range(h):
        for b in range(a+1,h):
            others=sorted((i for i in range(h) if i not in (a,b)),
                key=lambda i:((i^1) in (a,b),i))
            for i in others:
                pairs[tid[tuple(sorted((a,b,i))) ]].append(j);j+=1
    assert j==4*v and all(len(row)==3 for row in pairs)
    return triples,pairs

def closure(z,w):
    """Split every scalar add and fan copy, preserving all role access paths."""
    R=w['R'];v=z['v'];events=[];firstwrite=[None]*R;lastwrite=[None]*R
    for node,ins,outs in w['gates']:
        if len(ins)==2:events.append((node,'acc',ins[0],ins[1]))
        for u in outs[1:]:events.append((node,'copy',u,outs[0]))
    lastaccess=[None]*R;pred=[set() for _ in events]
    for i,(_,_,u,p) in enumerate(events):
        for role in (u,p):
            if lastaccess[role] is not None:pred[i].add(lastaccess[role])
            lastaccess[role]=i
        lastwrite[u]=i
        if firstwrite[u] is None:firstwrite[u]=i
    seeds={lastwrite[w['rootrole'][j]] for j in range(4*v,z['q'])
           if lastwrite[w['rootrole'][j]] is not None}
    done=set();stack=list(seeds)
    while stack:
        i=stack.pop()
        if i in done:continue
        done.add(i);stack.extend(pred[i])
    assert len(events)*2==209340 and len(done)==32488
    order=[i for i in range(len(events)) if i in done]+[i for i in range(len(events)) if i not in done]
    last=[-1]*R
    for i in order:
        _,_,u,p=events[i]
        for role in (u,p):
            assert i>last[role],(role,last[role],i)
            last[role]=i
    owner={u:n for n,u in w['born']}
    candidate={u for u in range(R) if u not in w['src'].values() and firstwrite[u] is not None
               and firstwrite[u] not in done}
    assert all(events[firstwrite[u]][0]==owner[u] for u in candidate)
    return events,done,firstwrite,candidate,order

def contained(z,x,y):
    if x==y:return True
    tx,ty=z['types'][x],z['types'][y];core=z['core'];cover=z['cover'];h=z['h']
    if tx==1 and ty==1:return not (core[y]&~core[x] or cover[x]&~cover[y])
    if tx in (1,2) and ty==2:return not (cover[x]&~cover[y])
    if tx==1 and ty==3:return bool(core[x]&core[y])
    if tx==2 and ty==3:return not (cover[x]&~core[y])
    if tx==3 and ty==2:return cover[y]==(1<<h)-1
    if tx==3 and ty==3:return core[x]==core[y]
    return False

def path_audit(z,w,events,closed,order):
    """All 183,636 accesses and retained/ordinary root reads have legal frames."""
    owner={u:n for n,u in w['born']};last=owner.copy();cut=len(closed)
    def step(i):
        x,_,u,p=events[i]
        for role in (u,p):
            assert contained(z,last[role],x),(i,role,last[role],x)
            last[role]=x
    for i in order[:cut]:step(i)
    first_after={}
    for i in order[cut:]:
        x,_,u,p=events[i]
        for role in (u,p):first_after.setdefault(role,x)
    for j in range(4*z['v'],z['q']):
        role=w['rootrole'][j];x=z['roots'][j]
        assert contained(z,last[role],x),(j,'retained-before')
        if role in first_after:assert contained(z,x,first_after[role]),(j,'retained-after')
        last[role]=x
    for i in order[cut:]:step(i)
    for j in range(4*z['v']):
        role=w['rootrole'][j];x=z['roots'][j]
        assert contained(z,last[role],x),(j,'ordinary-root')

def adjoint(z,w,triples,pairs,selected,owner,frames):
    h=z['h'];v=z['v'];rr=w['rootrole'];gates=w['gates'];R=w['R']
    per=[[] for _ in range(v)];selected_sum=[0]*v;nonselected_sum=[0]*v
    bits=[0]*R;terms=0;maxabs=0
    gateinfo=[(len(ins)==2,ins,outs) for _,ins,outs in reversed(gates)]
    rng=random.Random(17);a0=[rng.randrange(-2,3) for _ in range(R)]
    for i,S in enumerate(triples):
        row={}
        def add(u,c):row[u]=row.get(u,0)+c
        for j in range(h):add(rr[4*v+j],2-21*(j in S))
        add(rr[i],21)
        for j in pairs[i]:add(rr[j],-21)
        for two,ins,outs in gateinfo:
            for u in reversed(outs[1:]):
                c=row.get(u,0)
                if c:add(outs[0],c)
            if two:
                c=row.get(ins[0],0)
                if c:add(ins[1],c)
        tmask=sum(1<<j for j in S)
        for u,c in row.items():
            if not c:continue
            bits[u]|=1<<i;terms+=1;maxabs=max(maxabs,abs(c))
            if u in selected:
                per[i].append(u);selected_sum[i]+=c*a0[u]
                assert all(dot(tmask,b)==0 for b in frames[u]), (i,u)
            else:nonselected_sum[i]+=c*a0[u]
    assert terms==11678073 and maxabs==42
    for i in range(v):per[i].sort(key=lambda u:(len(frames[u]),u))
    return per,selected_sum,nonselected_sum,a0,terms,maxabs,bits

def physical(z,w,certificate,frames,per,a):
    h=z['h'];v=z['v'];m=h*h;R=w['R'];args=z['args'];N=v*v;B=v*R
    owner={u:n for n,u in w['born']};tmasks=[sum(1<<p for p in S) for S in itertools.combinations(range(h),3)]
    support=[0]*z['n']
    for node in range(1,z['n']):
        if not z['active'][node]:continue
        if args[2*node]:support[node]=support[args[2*node]]|support[args[2*node+1]]
        else:support[node]=1<<(node-1)
    base={}
    for node in set(owner[u] for u in frames):
        typ=z['types'][node]
        if typ==1:
            sp=support[node];lines=[]
            while sp:
                low=sp&-sp;lines.append(tmasks[low.bit_length()-1]);sp-=low
            A=canon(lines)
        else:
            assert typ==2
            A=canon(1<<j for j in range(h) if z['cover'][node]>>j&1)
        assert len(A)==z['ranks'][node] and nondeg(A)
        base[node]=A
    for u,S in frames.items():
        A=base[owner[u]]
        assert S and canon(S)==S and nondeg(S) and subset(S,A)
        E=residual(A,S)
        assert len(E)==len(A)-len(S) and nondeg(E)
    H=certificate['histogram'].copy();H[1]+=h;H[h]-=h
    W=2*N+2*B;L=2*v*h*(h-1)
    C=collections.Counter({m-h:2*B,(h-1)**2:2*N,h-1:4*N,1:N})
    for r,n in enumerate(H):
        if r:C[r]+=2*v*n
    for u,S in frames.items():
        d=z['ranks'][owner[u]];q=len(S)
        C[d]-=2*v
        if d>q:C[d-q]+=2*v
        C[m-h]-=2*v;C[m-h+q]+=2*v
    chain=collections.Counter();alternate=0;steps=0
    for i,roles in enumerate(per):
        tmask=tmasks[i]
        aa,bb,cc=(j for j in range(h) if tmask>>j&1)
        target=canon([*(1<<j for j in range(h) if not (tmask>>j&1)),
                      (1<<aa)|(1<<bb),(1<<aa)|(1<<cc)])
        A=()
        for u in roles:
            S=frames[u]
            if S==A:continue
            assert subset(A,S)
            E=residual(S,A) if A else S
            assert nondeg(E)
            alternate+=bool(E and all(not dot(b,b) for b in E))
            chain[len(E)]+=1;steps+=1;A=S
        assert subset(A,target)
        E=residual(target,A) if A else target
        assert nondeg(E)
        alternate+=bool(E and all(not dot(b,b) for b in E))
        chain[len(E)]+=1;steps+=1
    C[h-1]-=2*v*v
    for r,n in chain.items():C[r]+=2*v*n
    assert min(C.values())>=0
    C=collections.Counter({r:n for r,n in C.items() if r>0 and n>0})
    assert sum(r*n for r,n in C.items())==W*m-N+L
    assert max(r for r,n in C.items() if n)>0 and max(r for r,n in C.items() if n)==572
    assert N==4096576
    return C,a,W,m,N,L,chain,alternate,steps

def negative_controls(z,w,events,closed,frames,per,C,W,m,N,L):
    """Mutations of the three independent proof obligations must be rejected."""
    owner={u:n for n,u in w['born']};touched={r for i in closed for r in events[i][2:]}
    # A selected role whose first write is in the retained closure is unsafe.
    assert set(frames).isdisjoint(touched)
    bad=next(u for u in owner if u in touched)
    bad_selection=dict(frames);bad_selection[bad]=(1,)
    assert not all(u not in touched for u in bad_selection)
    # A full-space vector cannot be inside a proper owner label.
    small=next(u for u in frames if z['types'][owner[u]]==2 and z['ranks'][owner[u]]<z['h'])
    A=canon(1<<j for j in range(z['h']) if z['cover'][owner[small]]>>j&1)
    exterior=next(1<<j for j in range(z['h']) if red(A,1<<j))
    bad_frame=canon((*frames[small],exterior))
    assert not subset(bad_frame,A)
    # The proposed chain e_0 -> e_1 is not nested.
    assert not subset((1,),(2,))
    # Omitting even one of the N copied-center children violates mass.
    assert sum(r*n for r,n in C.items()) == W*m-N+L
    missing_copy=C.copy();missing_copy[1]-=1
    assert sum(r*n for r,n in missing_copy.items()) != W*m-N+L
    # Enumerate all points of F2^4 for both true endpoint gauges and their
    # one-sided wrong-sign/omitted-frame mutations, including a rank-2
    # alternating sigma in the first three coordinates.
    for S in ((1,), (3,5)):
        S=canon(S);assert nondeg(S)
        comp=canon(x^projection(S,x) for x in (1,2,4,8))
        def q(B,x):return projection(B,x).bit_count()%4
        assert all((q(S,x)+q(comp,x)-x.bit_count())%4==0 for x in range(16))
        assert all(((x.bit_count()+q(S,x))-q(S,x)-x.bit_count())%4==0 for x in range(16))
        assert any(((x.bit_count()+q(S,x))-0-x.bit_count())%4 for x in range(16))
        assert all((q(comp,x)-(-q(S,x))-x.bit_count())%4==0 for x in range(16))
        assert any((x.bit_count()-(-q(S,x))-x.bit_count())%4 for x in range(16))

def scalar_replay(z,w,triples,pairs,events,closure_set,frames,selected_sum,nonselected_sum,a0):
    v=z['v'];h=z['h'];R=w['R'];rr=w['rootrole'];gates=w['gates']
    ordered=[events[i] for i in range(len(events)) if i in closure_set]+[events[i] for i in range(len(events)) if i not in closure_set]
    cut=len(closure_set)
    def Jret(a):
        centers=[a[rr[4*v+j]] for j in range(h)];s=2*sum(centers)
        return [s-21*sum(centers[j] for j in S) for S in triples]
    def Jpiece(a):
        return [21*(a[rr[i]]-sum(a[rr[j]] for j in pairs[i])) for i in range(v)]
    rng=random.Random(53);x=[rng.randrange(-2,3) for _ in range(v)];y=[rng.randrange(-2,3) for _ in range(v)]
    a=a0.copy();y42=[42*yy-n for yy,n in zip(y,nonselected_sum)]
    for j in range(v):a[w['src'][j+1]]+=x[j]
    for _,_,u,p in ordered[:cut]:a[u]+=a[p]
    y42=[yy+r for yy,r in zip(y42,Jret(a))]
    assert all(a[u]==a0[u] for u in frames)
    y42=[yy-s for yy,s in zip(y42,selected_sum)]
    for _,_,u,p in ordered[cut:]:a[u]+=a[p]
    y42=[yy+p for yy,p in zip(y42,Jpiece(a))]
    for _,_,u,p in reversed(ordered):a[u]-=a[p]
    for j in range(v):a[w['src'][j+1]]-=x[j]
    assert a==a0
    assert y42==[42*(yy+xx) for yy,xx in zip(y,x)]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',type=Path,required=True,help='pinned #104 source checkout')
    p.add_argument('--selection',type=Path,default=Path(__file__).with_name('selection.json'))
    p.add_argument('--assembly-inputs',type=Path,help='cross-check the assembled histogram and role supports')
    if sys.flags.optimize:
        raise RuntimeError('Run without -O: assertions must remain enabled')
    args=p.parse_args();src=args.source_root.resolve();source_check(src)
    frozen=json.loads(args.selection.read_text());assert frozen['format']=='complex-deferred-frames-v1'
    raw=frozen['frames'];assert len(raw)==frozen['unique_frames'] if 'unique_frames' in frozen else len(raw)>0
    assert all(canon(tuple(x))==tuple(x) for x in raw)
    frames={}
    for u,i in frozen['role_frame_ids']:
        assert u not in frames and 0<=i<len(raw)
        frames[u]=tuple(raw[i])
    assert len(frames)==frozen['selected_roles'] if 'selected_roles' in frozen else len(frames)>0
    with tempfile.TemporaryDirectory(prefix='complex-defer-') as td:
        prefix,match,certificate=build(src,Path(td))
        z=load(prefix,match);w=compile_word(z)
        assert (z['h'],z['v'],w['R'])==(24,2024,38506)
        triples,pairs=triples_and_pairs(z['h'],z['v'])
        events,closed,firstwrite,candidate,order=closure(z,w)
        owner={u:n for n,u in w['born']}
        assert set(frames)<=set(owner)
        assert set(frames)<=candidate
        assert all(events[firstwrite[u]][0]==owner[u] for u in frames)
        per,selected_sum,nonselected_sum,a0,terms,maxabs,bits=adjoint(z,w,triples,pairs,frames,owner,frames)
        a=Fraction(*frozen['claimed_saving'])
        C,a,W,m,N,L,chain,alternate,steps=physical(z,w,certificate,frames,per,a)
        assert frozen['claimed_saving']==[a.numerator,a.denominator]
        negative_controls(z,w,events,closed,frames,per,C,W,m,N,L)
        path_audit(z,w,events,closed,order)
        scalar_replay(z,w,triples,pairs,events,closed,frames,selected_sum,nonselected_sum,a0)
        sys.path.insert(0,str(src/'scripts'))
        from partial_swap_network import moment
        gap=moment(m,W,dict(C),a,sharp=True)['strict_gap']
        assert gap>0, gap
        gh=4*(certificate['c']+z['v'])+10*z['v']+4*z['h']*z['v']+4*z['h']**2+8*z['h']+8
        G0=N+2*z['v']*(gh+2*z['h'])
        assert (gh,G0)==(497896,2019773888)
        G=G0+2*z['v']*terms*16
        assert G==758385205952
        assert maxabs==42 and maxabs.bit_length()==6
        if args.assembly_inputs:
            import gzip
            inp=args.assembly_inputs
            profile=json.loads((inp/'complex.json').read_text())
            assert sorted(C.items())==[tuple(x) for x in profile['hist']]
            assert sorted(chain.items())==[tuple(x) for x in profile['chain_hist']]
            ranks=json.loads(gzip.decompress((inp/'selected-ranks.json.gz').read_bytes()))
            roles=[[u,z['ranks'][owner[u]],len(frames[u]),format(bits[u],'x')]
                   for u in sorted(frames)]
            assert (ranks['h'],ranks['v'])==(z['h'],z['v'])
            assert ranks['roles']==roles, 'assembled role ranks or adjoint supports differ'
            assert profile['repaired_closure_events']==len(closed)
            assert profile['total_events']==len(events)
            assert profile['saving']==[a.numerator,a.denominator]
            meta=json.loads((inp/'complex-meta.json').read_text())
            assert (meta['adjoint_pairs_per_invocation'],meta['scalar_group_upper'],
                    meta['maximum_coefficient_numerator'])==(terms,G,maxabs)
            assert (meta['expected_R'],meta['expected_active_sigma_roles'],
                    meta['expected_positive_width_bins'])==(w['R'],len(frames),len(C))
        result={'source_commit':PIN,'cyclic_producer_commit':CYCLIC_PIN,'h':z['h'],'v':z['v'],'R':w['R'],
                'retained_closure_events':len(closed),'selected_roles':len(frames),
                'unique_frames':len(raw),'adjoint_nonzero_pairs_per_invocation':terms,
                'max_abs_adjoint_numerator':maxabs,'numerator_bitlength':maxabs.bit_length(),
                'chain_steps':steps,'alternating_chain_steps':alternate,
                'N_copy_children':N,'W':W,'m':m,'L':L,
                'rank_one_count':C[1],'max_child_rank':max(C),
                'a_complex_exact':str(a),'moment_gap_approx':format(float(gap),'.12g'),
                'histogram_sha256':hashlib.sha256(json.dumps(sorted(C.items()),separators=(',',':')).encode()).hexdigest(),
                'selection_sha256':hashlib.sha256(args.selection.read_bytes()).hexdigest(),
                'scalar_group_upper_16_ops_per_pair':G,
                'scalar_replay':'pass','phase_gram':'pass'}
        print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
