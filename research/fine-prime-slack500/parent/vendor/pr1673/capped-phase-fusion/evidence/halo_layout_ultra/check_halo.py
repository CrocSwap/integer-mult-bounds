"""Exact finite core-convolution plus sparse face-correction replay."""
from itertools import product
from collections import Counter,defaultdict
from pathlib import Path
import json,math

HERE=Path(__file__).resolve().parent
def box(ranges):return product(*(range(a,b) for a,b in ranges))
def flat(x,N):
    z=0
    for a in x:z=z*N+a
    return z
def unflat(z,N,g):
    x=[]
    for _ in range(g):x.append(z%N);z//=N
    return tuple(reversed(x))
def gather_permutation(widths,b):
    starts=[];t=0
    for h in widths:starts.append(t);t+=h
    selected=[s+j for s in starts for j in range(b)]
    targets=list(range(t-len(selected),t))
    pi=list(range(t))
    for s,u in zip(selected,targets):pi[s]=u
    for s,u in zip(sorted(set(targets)-set(selected)),sorted(set(selected)-set(targets))):pi[s]=u
    assert sorted(pi)==list(range(t))
    assert all(pi[s]==u for s,u in zip(selected,targets))
    assert {i for i,j in enumerate(pi) if i!=j}<=set(selected)|set(targets)
    return dict(widths=widths,inner_bits=b,permutation=pi,support=sum(i!=j for i,j in enumerate(pi)),bound=2*len(selected))

def sparse_copies(data,N,L,g,Q):
    """One source traversal; destination windows are enumerated from flags."""
    result=[]
    for tile in product(*(range(q) for q in Q)):
        for x in product(range(N),repeat=g):
            origin=tuple(t*N+a for t,a in zip(tile,x));value=data[origin]
            active=[j for j,a in enumerate(x) if a<2*L or a>=N-2*L]
            for j in active:
                for side in (0,1):
                    choices=[]
                    for i,a in enumerate(x):
                        if i<j:opts=[(0,a)]
                        elif i==j:
                            opts=[]
                            if side==0:
                                if a<2*L:opts.append((0,a))
                                if a>=N-L:opts.append((1,a-N))
                            else:
                                if a>=N-2*L:opts.append((0,a))
                                if a<L:opts.append((-1,a+N))
                        else:
                            opts=[(0,a)]
                            if a<L:opts.append((-1,a+N))
                            if a>=N-L:opts.append((1,a-N))
                        choices.append(opts)
                    for selected in product(*choices):
                        dest=tuple((tile[i]+selected[i][0])%Q[i] for i in range(g))
                        y=tuple(v[1] for v in selected)
                        result.append(((j,side,dest,y),value))
    return result

def radix(records,key):
    pairs=[(key(k),k,v) for k,v in records]
    bits=max((k.bit_length() for k,_,_ in pairs),default=0)
    for b in range(bits):
        zero=[];one=[]
        for row in pairs:(one if row[0]>>b&1 else zero).append(row)
        pairs=zero+one
    assert [k for k,_,_ in pairs]==sorted(k for k,_,_ in pairs)
    return [(k,v) for _,k,v in pairs],bits

def key_encoder(N,L,g,Q):
    # Deliberately scramble coarse address significance. This represents the
    # displaced coordinate slots in a support-limited gather.
    coarse=[(i,j) for i,q in enumerate(Q) for j in range(q.bit_length()-1)]
    coarse=coarse[::2]+coarse[1::2][::-1]
    def enc(key):
        j,side,tile,y=key
        out=j*2+side
        for i,b in coarse:out=(out<<1)|((tile[i]>>b)&1)
        for a in y:out=(out*(N+2*L))+(a+L)
        return out
    return enc

def replay(N,L,g,Q):
    assert N>4*L and N&(N-1)==0 and all(q>=2 and q&(q-1)==0 for q in Q)
    S=[N*q for q in Q];global_ranges=[(0,s) for s in S]
    raw={x:1+sum((i+3)*a*a+(i+1)*a for i,a in enumerate(x)) for x in box(global_ranges)}
    pre=lambda x:1+sum((i+1)*a for i,a in enumerate(x))%3
    post=lambda x:1+sum((i+2)*a for i,a in enumerate(x))%2
    data={x:v*pre(x) for x,v in raw.items()}
    kernels=[[((i+2)*(z+L+1))*(-1 if z==0 else 1) for z in range(-L,L+1)] for i in range(g)]
    shifts=list(product(range(-L,L+1),repeat=g))
    weight={z:math.prod(kernels[i][a+L] for i,a in enumerate(z)) for z in shifts}
    direct={x:post(x)*sum(weight[z]*data[tuple((a-b)%s for a,b,s in zip(x,z,S))] for z in shifts) for x in data}
    merged={};wrong=interior=0
    for tile in product(*(range(q) for q in Q)):
        core=[data[tuple(t*N+a for t,a in zip(tile,unflat(u,N,g)))] for u in range(N**g)]
        for u in range(N**g):
            x=unflat(u,N,g);glob=tuple(t*N+a for t,a in zip(tile,x))
            val=post(glob)*sum(w*core[(u-sum(z[i]*N**(g-1-i) for i in range(g)))%(N**g)] for z,w in weight.items())
            wrong+=val!=direct[glob]
            if all(L<=a<N-L for a in x):
                interior+=1;assert val==direct[glob];merged[glob]=val
    copies=sparse_copies(data,N,L,g,Q)
    records,keybits=radix(copies,key_encoder(N,L,g,Q))
    assert len({k for k,v in records})==len(records)
    grouped=defaultdict(dict)
    for (j,side,tile,y),value in records:grouped[j,side,tile][y]=value
    boundary=0;seen_output=set()
    for (j,side,tile),values in grouped.items():
        ranges=[(0,N) if i<j else ((-L,2*L) if side==0 else (N-2*L,N+L)) if i==j else (-L,N+L) for i in range(g)]
        assert set(values)==set(box(ranges))
        for i in range(g):
            newranges=ranges.copy();a,b=ranges[i];newranges[i]=(a+L,b-L)
            filtered={}
            for x in box(newranges):
                filtered[x]=sum(kernels[i][z+L]*values[tuple(a-z if k==i else a for k,a in enumerate(x))] for z in range(-L,L+1))
            values=filtered;ranges=newranges
        for x,val in values.items():
            glob=tuple(t*N+a for t,a in zip(tile,x));assert glob not in seen_output;seen_output.add(glob)
            val*=post(glob);assert val==direct[glob];merged[glob]=val;boundary+=1
    assert merged==direct and interior+boundary==len(data) and wrong>0
    tiles=math.prod(Q)
    expected_copies=tiles*2*sum((N**j)*(3*L)*(N+2*L)**(g-j-1) for j in range(g))
    assert len(copies)==expected_copies
    expected_boundary=tiles*(N**g-(N-2*L)**g)
    assert boundary==expected_boundary
    return dict(N=N,L=L,g=g,coarse_sizes=Q,input_records=len(data),interior_outputs=interior,
        corrected_boundary_outputs=boundary,gathered_halo_records=len(copies),predicted_halo_records=expected_copies,
        direct_flattening_wrong_outputs=wrong,radix_key_bits=keybits,
        exact_tensor_outputs_checked=len(data),diagonal_conjugations_checked=True,
        scalar_coefficients='signed asymmetric integer product kernel')

def main():
    cases=[replay(8,1,2,[2,4]),replay(8,1,3,[2,2,2]),replay(16,2,2,[2,2])]
    perms=[gather_permutation([5,7,6],3),gather_permutation([4,4,4],3),gather_permutation([9,6],4)]
    out=dict(status='PASS_EXACT_CORE_PLUS_SPARSE_BOUNDARY_TENSOR_CONVOLUTION',cases=cases,
        support_limited_gathers=perms,
        scope='Finite exact map, sparse-copy completeness, unique scatter, radix ordering and support controls; asymptotic fixed-tape costs are in the companion proof.')
    (HERE/'HALO-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
