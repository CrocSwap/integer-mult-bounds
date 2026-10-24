"""Exact finite controls for grouped address routes and phase rank.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
import time

HERE=Path(__file__).resolve().parent


def rank(vectors):
    pivots={}
    for value in vectors:
        while value:
            lead=value.bit_length()-1
            if lead not in pivots:
                pivots[lead]=value;break
            value^=pivots[lead]
    return len(pivots)


def digits(value,n,G):
    return [(value>>(G*j))&((1<<G)-1) for j in range(n)]


def paired_control_word(state,positions,sources,K,G):
    """Literal twelve compact swaps and ten modular rotations.

    State=(front u,front t,active binary field y,back b). Each back swap is
    made and undone; offsets never use the field being rotated. No address
    decoding or conditional data assignment implements the desired endpoint.
    """
    n=len(positions)
    if not (K>0 and G>0 and n==len(sources) and n>0):
        raise ValueError('nonempty fixed selected-position context')
    if len(set(positions))!=n or set(positions)&set(sources):
        raise ValueError('distinct selected targets, no selected source is a target')
    rho=positions[0]%K
    if any(p<0 or p%K!=rho for p in positions+sources):
        raise ValueError('all selected positions must have the same rho in distinct K-bit chunks')
    f=max(max(positions),max(sources))//K+1
    if any(p+K>f*K for p in positions):
        raise ValueError('highest overflowing target window needs the separate elementary pair')
    bits=f*K;Ymod=1<<bits;B=1<<G;Cmod=B**n
    u,t,y,b=state;swaps=rotations=0
    def packed_target(value,controls=None):
        return sum((((value>>p)&1) ^ (controls[j] if controls is not None else 0))*(B**j)
                   for j,p in enumerate(positions))
    def earlier():
        nonlocal u,t,y,b,swaps,rotations
        controls=[w&1 for w in digits(u,n,G)]
        td=digits(t,n,G)
        y=(y+sum(2*z*w*(1<<p) for p,z,w in zip(positions,controls,td)))%Ymod;rotations+=1
        t,b=b,t;swaps+=1
        b=(b+packed_target(y))%Cmod;rotations+=1
        t,b=b,t;swaps+=1
        td=digits(t,n,G)
        y=(y+sum(z*(1-2*w)*(1<<p) for p,z,w in zip(positions,controls,td)))%Ymod;rotations+=1
        t,b=b,t;swaps+=1
        b=(b-packed_target(y,controls))%Cmod;rotations+=1
        t,b=b,t;swaps+=1
    earlier()
    u,b=b,u;swaps+=1
    b=(b+sum(((y>>p)&1)*(B**j) for j,p in enumerate(sources)))%Cmod;rotations+=1
    u,b=b,u;swaps+=1
    earlier()
    u,b=b,u;swaps+=1
    b=(b-sum(((y>>p)&1)*(B**j) for j,p in enumerate(sources)))%Cmod;rotations+=1
    u,b=b,u;swaps+=1
    return (u,t,y,b),dict(compact_swaps=swaps,modular_rotations=rotations)


def matching_checks():
    K,G=6,2;B=1<<G;n=2;f=4;total=0
    for rho in [0,2,5]:
        positions=[rho,rho+2*K];sources=[rho+K,rho+3*K]
        covered=sum(((1<<K)-1)<<p for p in positions)
        rest=((1<<(f*K))-1)^covered
        good_words=[sum(w*(B**j) for j,w in enumerate(ds)) for ds in product(range(B-1),repeat=n)]
        for guards,parities,source_bits,extra,u,t,b in product(
                product([8,23],repeat=n),product([0,1],repeat=n),product([0,1],repeat=n),
                [0,rest],good_words,good_words,[0,1,B**n-1]):
            y=extra+sum((2*g+a)<<p for g,a,p in zip(guards,parities,positions))
            for p,z in zip(sources,source_bits):y=(y&~(1<<p))|(z<<p)
            expected=y^sum(z<<p for z,p in zip(source_bits,positions))
            state=(u,t,y,b);out,invoice=paired_control_word(state,positions,sources,K,G)
            assert out==(u,t,expected,b),(rho,state,out,expected)
            assert invoice==dict(compact_swaps=12,modular_rotations=10)
            assert all(((y>>(p+1))&((1<<(K-1))-1))==((expected>>(p+1))&((1<<(K-1))-1)) for p in positions)
            assert all(((y>>p)&1)==((expected>>p)&1) for p in sources)
            total+=1
    # Parent's independent audit supplied a failure outside the same-rho
    # contract. The public model must reject this structural premise, not
    # silently advertise correctness for adjacent overlapping guard windows.
    try:paired_control_word((1,1,32,0),[0,1],[2,3],6,2)
    except ValueError as error:
        overlap_control=dict(rejected=True,reason=str(error),
            positions=[0,1],sources=[2,3],state=[1,1,32,0])
    else:raise AssertionError('overlapping target windows were admitted')
    return dict(cases=total,K=K,G=G,target_chunks=[0,2],source_chunks=[1,3],
                rho=[0,2,5],dirty_good_digits=[0,1,2],arbitrary_back_samples=[0,1,15],
                endpoint_and_dirty_restoration=True,swaps=12,rotations=10,
                overlapping_guard_window_control=overlap_control)


def two_involutions(p):
    n=len(p);first=list(range(n));second=list(range(n));seen=set()
    for start in range(n):
        if start in seen:continue
        cycle=[];j=start
        while j not in seen:
            seen.add(j);cycle.append(j);j=p[j]
        L=len(cycle)
        for j,x in enumerate(cycle):
            first[x]=cycle[-j%L];second[x]=cycle[(1-j)%L]
    return first,second


def permutation_checks():
    count=0
    for n in range(1,9):
        for p in permutations(range(n)):
            a,b=two_involutions(p)
            assert all(a[a[j]]==b[b[j]]==j and b[a[j]]==p[j] for j in range(n))
            count+=1
    return dict(permutations=count,maximum_selected_bits=8,
                involutions_per_permutation=2,parallel_control_layers=6,
                scope='Finite permutation control plus written all-cycle reversal proof; not an uncharged descriptor operation.')


def rank_checks():
    total=0
    for n in range(1,7):
        for u in range(1,1<<(2*n)):
            def pairing(v):
                return (((u&((1<<n)-1))&(v>>n)).bit_count()+((u>>n)&v).bit_count())&1
            defect=[u if pairing(1<<j) else 0 for j in range(2*n)]
            assert rank(defect)==1;total+=1
    tensor=[]
    for f in range(1,33):
        tensor_rank=rank([1<<j for j in range(f)])
        global_rank=rank([(1<<f)-1]*f)
        assert tensor_rank==f and global_rank==1
        tensor.append(dict(columns=f,tensor_transvection_defect_rank=f,global_phase_defect_rank=1))
    return dict(nonzero_pauli_transvections=total,maximum_address_axes=6,global_vs_tensor=tensor)


def main():
    began=time.monotonic()
    result=dict(status='PASS_SCOPED_GROUPED_ROUTE_AND_RANK_CONTROLS',author='Cao Yifan',new_kappa=False,
        matching=matching_checks(),permutation=permutation_checks(),rank=rank_checks(),
        complete_phase_adapter_cost='One paid Gaussian rank r correction plus O(V*((f*log(p))^tau+1)) movement for r fixed-length blocks; no free tensor-column phases.',
        scope='Finite arithmetic/permutation controls supplement the written all-size compact-control extension. Actual Phi native invoice, endpoint restoration, precision and whole-job transfer are separate.',
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-began)
    (HERE/'GROUPED-ROUTE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],result['matching']['cases'],result['permutation']['permutations'],
          result['rank']['nonzero_pauli_transvections'],round(result['seconds'],3),flush=True)


if __name__=='__main__':main()
