#!/usr/bin/env python3
"""Exact endpoint-gauge counts, moments, basis combinatorics and assembly.

Copyright 2026 icekylinx. Apache-2.0.
Adapted from the Pro handoff with substantial OpenAI GPT-6 Astra and Codex
assistance; retained scalar and analytic sources are credited in SOURCES.json.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, prod
from pathlib import Path
import json

from certify import Parameters, require
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from partial_swap_network import moment
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]
AB = Q(2993093,250000000000)
AC = Q(3,125000)
KAPPA = Q(119723,20000000000)


def validate_axis(row, complex_field=False):
    h = row['h']
    require(row['v'] == comb(h,3), 'Triple count')
    require(row['q'] == (4*row['v']+h+1 if complex_field else 3*row['v']+h), 'Output uses')
    require(row['baseline_R'] == row['c']+row['q'], 'Unmatched roles')
    require(row['R'] == row['baseline_R']-row['matched'], 'Carrier roles')
    require(row['loss'] == h*(h if complex_field else h-1), 'Retained loss')
    hist=row['histogram']
    require(len(hist)==h+1 and all(isinstance(n,int) and n>=0 for n in hist), 'Histogram')
    require(sum(r*n for r,n in enumerate(hist)) == row['rank_sum'] == h*row['R']+2*row['loss'], 'Internal rank mass')


def bit_profile(rows):
    a, b, k = (row['h'] for row in rows)
    require((a,b,k)==(32,30,40), 'Selected dimensions')
    H, m = a*b, a*b*k
    N = rows[0]['v'] * rows[1]['v'] * rows[2]['v']
    B1, B2, B3 = (N//row['v']*row['R'] for row in rows)
    require(B3>=B1, 'Auxiliary bank matching')
    E, W = B3-B1, 2*N+B2+B3
    L = sum(N//row['v']*row['loss'] for row in rows)
    s = W*m - 2*N + 2*L
    z = Counter()
    def add(n, *widths):
        for t in widths:
            if n and t:
                z[t] += n
    add(B1, m-2*(a+k))
    add(B1*(a+k), 1)
    add(E, k, m-2*k)
    add(B2, b, m-2*b)
    add(2*N, k-2, H-2*k+2, m-2*H-2*k+2)
    add(2*N*(2*k-1), 1)
    add(2*N, H-2*a-2*b+2)
    add(2*N*(a+b-1), 1)
    for h, row in zip((a, b, k), rows):
        validate_axis(row)

        add(2*N, 1, h-2)
        for r, n in enumerate(row['histogram']):
            copies = N//row['v']*n
            if 2*r > h:
                add(copies, 2*r-h)
                add(copies*(h-r), 1)
            else:
                add(copies*r, 1)
    require(sum(t*n for t,n in z.items())==s, 'Bit rank mass')
    return dict(dimensions=[a,b,k], m=m, N=N, B1=B1, B2=B2, B3=B3,
                E=E, W=W, L=L, total_rank=s, deficit=2*N-2*L,
                singletons=z[1], child_multiplicities=dict(sorted(z.items())))


def complex_profile(data):
    rows=data['scalar_circuits']
    require([r['h'] for r in rows]==[32,30,40], 'Complex dimensions')
    for row in rows: validate_axis(row, True)
    a,b,k=(r['h'] for r in rows)
    m=a*b*k; N=prod(r['v'] for r in rows)
    B1,B2,B3=(N//r['v']*r['R'] for r in rows)
    require(B3>=B1, 'Complex bank matching')
    W=2*N+B2+B3
    L=sum(N//r['v']*r['loss'] for r in rows)
    s=W*m-2*N+2*L
    profiles=[(m-a-k,B1),(m-k,B3-B1),(m-b,B2),
              ((a*b-1)*(k-1),2*N),((a-1)*(b-1),2*N)]
    z=Counter()
    for t,n in profiles: z[t]+=n
    for row in rows:
        for r,n in enumerate(row['histogram']):
            if r: z[r]+=N//row['v']*n
    remaining=s-sum(t*n for t,n in z.items())
    # All unbatched physical-data transitions retain one child per rank.
    require(remaining>=0, 'Negative remaining physical rank')
    z[1]+=remaining
    computed=dict(m=m,N=N,B1=B1,B2=B2,B3=B3,W=W,L=L,total_rank=s,
                  deficit=2*N-2*L,remaining_singleton_rank=remaining)
    for key,value in computed.items(): require(value==data[key], 'Complex count: '+key)
    require(profiles==[(p['width'],p['count']) for p in data['macros']], 'Complex macros')
    require(dict(z)=={int(t):n for t,n in data['child_multiplicities'].items()}, 'Complex child list')
    require(sum(t*n for t,n in z.items())==s, 'Complex rank mass')
    return computed,z


def precision_guard(data):
    a,b,k=32,30,40; m=a*b*k
    q=m+2*(a+b+k)+a*b
    small=(a-1)*(b-1); largest=m-b
    large=[p['width'] for p in data['macros'] if p['width']>small]
    rho,gamma=Q(19,10),Q(9997,10000)
    lower,upper=500000000,460
    require(2*min(large)>q, 'Two large children can fit on a path')
    require(m**19>lower**10 and small**9<upper**10, 'Precision power enclosures')
    # The conservative bound t^rho/m^rho+(q-t)*upper/lower is
    # increasing throughout the large-child range (exact tenth powers).
    require(rho**10*min(large)**9*lower**10>upper**10*m**19, 'Path bound monotonicity')
    x=Q(m-largest,m)
    path=1-rho*x+Q(9,10)*x*x+Q((q-largest)*upper,lower)
    no_large=Q(q*upper,lower)
    require(max(path,no_large)<gamma, 'Precision path contraction')
    actual=dict(rho=rho,gamma=gamma,path_rank_budget=q,largest_child=largest,
                largest_small_child=small,m_power_lower=lower,small_power_upper=upper,
                path_moment_upper=path,no_large_path_upper=no_large)
    for key,value in actual.items(): require(value==Q(data['guard'][key]), 'Recorded guard: '+key)
    # A width-independent operation allowance for the stopped-depth proof.
    E=128*(data['W']+m+1)**3
    require(36*data['W']**3+16*data['total_rank']+16*data['W']+8*m+4<E, 'Local operation allowance')
    dependency=Q(E+16*m+1)/(1-gamma)
    beta,zeta=Q(1,1000),Q(1,10000)
    raw=128*m*(1+1/zeta)*dependency
    C0=-(-raw.numerator//raw.denominator)
    require(dependency*(1-gamma)>=E and dependency>=16*m, 'Depth allowance')
    return dict(**actual,E=E,dependency_constant=dependency,C0=C0,
                C1=rho-(rho-1)*beta+zeta,zeta=zeta,strict_gap=gamma-max(path,no_large))


def basis_combinatorics():
    a,b,k=32,30,40; H=a*b
    R=list(range(a))+list(range(1,a))+[0]
    C=[a-1]+list(range(a-1))+list(range(a))
    completions=[]
    for beta in range(b):
        prescribed={}
        def prescribe(row,col):
            require(row not in prescribed or prescribed[row]==col, 'Inconsistent prescribed row')
            require(col not in prescribed.values() or prescribed.get(row)==col, 'Inconsistent prescribed column')
            prescribed[row]=col
        for i,label in enumerate(R):
            if i%b==beta: prescribe(i//b,label)
        for j,label in enumerate(C):
            i=H-2*a+j
            if i%b==beta: prescribe(i//b,label)
        unused=iter(c for c in range(a) if c not in prescribed.values())
        completions.append([prescribed[r] if r in prescribed else next(unused) for r in range(a)])
    forward=[(0,b),(1,b+1)]+[(j+2,j+1) for j in range(b-2)]+[(0,b-1)]
    dual=[(b,0),(b+1,1),(b+1,2)]+[(j-2,j-1) for j in range(4,b+2)]
    for edges in (forward,dual):
        require(len(edges)==a-1, 'A5 tree edge count')
        seen={0}
        while True:
            expanded=seen|{y for x,y in edges if x in seen}|{x for x,y in edges if y in seen}
            if expanded==seen: break
            seen=expanded
        require(seen==set(range(a)), 'A5 tree connectivity')
    require(H>=2*(a+k) and k>=a+1, 'Outer boundary room')
    return dict(row_labels=R,inverse_column_labels=C,permutation_completions=completions,
                A5_forward_tree=forward,A5_dual_tree=dual,
                scope='Finite prescription compatibility and tree connectivity; generic minors are proved in the note.')


def certificate():
    inputs=[ROOT/'certificates'/f'endpoint-gauge-{name}.json' for name in ('input','bit-axes','complex-input')]
    saved,axes,complex_data=(json.loads(p.read_text()) for p in inputs)
    bit=bit_profile(axes)
    require(json.loads(json.dumps(bit))==saved['bit'], 'Saved bit profile')
    cn,cr=complex_profile(complex_data)
    bm=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB,True)
    cm=moment(cn['m'],cn['W'],cr,AC,False)
    require(bm['strict_gap']==Q(saved['bit_moment_gap']), 'Saved bit moment')
    require(cm['strict_gap']==Q(saved['complex_moment_gap'])==Q(complex_data['strict_gap']), 'Saved complex moment')
    guard=precision_guard(complex_data)
    tau=1-AB
    p=Parameters(tau=tau,sigma=1-AC,epsilon=1/(2+AB),c=Q(1),
                 lam=tau+Q(1,10**20),lamp=tau+Q(2,10**20),kappa=KAPPA,
                 beta=Q(1,1000),delta=Q(1,10**16),C1=guard['C1'])
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs['packed_overhead']=p.lam-ex['internal']
    cs['reserved_axes']=p.lamp-ex['preprocessing']
    margins=fast_margins(p)
    require(len(cs)==29 and all(x>0 for x in cs.values()), '29 strict interface conditions')
    require(len(margins)==7 and min(margins.values())>KAPPA, 'Seven strict assembly margins')
    for values,key in [(vars(p),'parameters'),(ex,'recurrence_exponents'),(cs,'constraint_slacks'),(margins,'assembly_margins')]:
        require(values=={k:Q(v) for k,v in saved[key].items()}, 'Saved assembly: '+key)
    gap=min(margins.values())-KAPPA
    require(gap==Q(saved['absorption_gap']), 'Absorption gap')
    sources=inputs+[Path(__file__).resolve(),ROOT/'scripts/endpoint_gauge_producer.py',ROOT/'scripts/partial_swap_network.py']
    sources+=sorted(p for p in (ROOT/'scripts/endpoint_gauge').iterdir() if p.is_file())
    sources+=sorted((ROOT/'notes').glob('endpoint-gauge-*.tex'))
    return dict(status='Conditional endpoint-gauge integer-multiplication witness',kappa=KAPPA,
                bit=dict(counts=bit,**bm),complex=dict(counts=cn,**cm),guard=guard,
                basis_combinatorics=basis_combinatorics(),
                assembly=dict(parameters=vars(p),recurrence=ex,constraints=cs,margins=margins,absorption_gap=gap),
                inherited_commit='f2ab41aebad47861caf6316282c1793e5513845e',
                source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
                scope='Exact arithmetic and finite basis combinatorics; producer regeneration is separate. '
                      'Generic basis existence, recursive compilation and retained analytic/tape interfaces remain written proofs.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'certificates/endpoint-gauge-network.json')
    args=parser.parse_args()
    result=certificate()
    args.output.write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS endpoint-gauge kappa=119723/20000000000 = 5.98615e-6')
    print('29 strict constraints; 7 assembly margins; both moments and precision guard')

if __name__=='__main__': main()
