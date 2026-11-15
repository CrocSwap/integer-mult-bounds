"""Two rational engines, finite overcharges, and the combined strict assembly.
Prepared by Zhihao Chen with OpenAI Codex assistance; Apache-2.0.
"""
import argparse, hashlib, importlib.util, json, math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--complex-check',type=Path,required=True)
    a=ap.parse_args(); out=a.out
    g=json.loads((out/'GLOBAL.json').read_text()); geo=json.loads((out/'GEOMETRY.json').read_text())
    assert g['status']=='PASS_SOURCE_BOUND_NINE_STAGE_BIT_TEMPLATE'
    assert g['geometry_sha256']==sha(out/'GEOMETRY.json')
    v=a.complex_check/'VERIFICATION.json'; cv=json.loads(v.read_text())
    assert cv['status'].startswith('PASS')
    cx=a.complex_check/'work/complex-nine-native/GLOBAL-REVIEW.json'
    cm=a.complex_check/'work/odd-stages/COMPLEX-NINE-CANDIDATE.json'
    ct=a.complex_check/'work/complex-nine-native/INDEPENDENT-TEMPLATE-AUDIT.json'
    # Bind to the actual independently audited complex profile/price, not a
    # title number or a user-supplied decimal.
    cc=json.loads(cm.read_text()); cr=json.loads(cx.read_text()); ca=json.loads(ct.read_text())
    assert cr['status']=='PASS_NINE_STAGE_SOURCE_BOUND_TEMPLATE_OWNERS_PROFILE_AND_FINITE_INVOICE'
    assert cc['two_rational_engines'] and cc['next_grid_rejected']
    b=Q(ca['coarse_complex']); assert b==Q(cc['coarse_candidate'])==Q(cv['complex_coarse'])==Q(999240641319551,10**18)
    audit=json.loads((out/'AUDIT.json').read_text())
    assert audit['status']=='PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT' and audit['template_sha256']==g['template_sha256']
    pricing=a.source/'code/pricing'
    moment=load(pricing/'moment.py','bit9_moment'); other=load(pricing/'base_two_moment.py','bit9_other'); outer=load(pricing/'outer.py','bit9_outer')
    P={int(r):n for r,n in g['profile'].items()}; m=g['m']; W=g['live']; E=sum(P.values()); mass=sum(r*n for r,n in P.items())
    assert (m,W,mass,m*W-mass)==(64,15465,987264,2496)
    root=moment.certify(P,m,W,True); grid=Q(1,10**18); c=Q(int(Q(root['lower'])*10**18),10**18)
    bm=moment.moment(P,m,W,c,True); nm=moment.moment(P,m,W,c+grid,True); assert bm[1]<1<nm[0]
    fallback=32*m*m*E
    _,up=other.moment(m,W,list(P.items()),c); _,bad=other.moment(m,W,[(1,fallback)],c)
    lo,_=other.moment(m,W,list(P.items()),c+grid); lobad,_=other.moment(m,W,[(1,fallback)],c+grid)
    assert up+Q(1,10**16)*bad<1<lo+Q(1,10**16)*lobad
    # Compose two identical weighted recurrences. Both exact moments contract,
    # and every grandchild is at most (42/64)^2 < 1/2 of its grandparent.
    assert 2*max(P)**2<m*m and bm[1]**2<1
    assert not 2*max(P)<m
    # Conservative finite bill: inherited polynomial compiler bounds, every
    # local/owner/copy/idle/bridge item, actual rational route factors, and the
    # explicitly increased nine-stage payload-prefix allowance.
    T,L,R,V,K=8,9,865,120,4; physical=g['physical']; d=m*m; N=2*m
    unit=L*T*g['local_additions']+g['bridge_additions']
    J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*g['bank_assignments']+2*g['copy_erase_episodes']
    high=16*(d+1)**2; good=8*m*m+8; compiler=128*N**3
    selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+(m-1)+m))
    prefix=int(g['global_prefix_bound']); assert prefix<1<<192
    coefficient=unit+J*high+J*physical+E*(good+compiler)+16*m**3+g['copy_erase_episodes']+selectors+prefix+1
    two_level_coefficient=(coefficient+1)**2*(E+1)**2
    assert coefficient<1<<192 and two_level_coefficient<1<<512
    row=2*(m*m+1)+9909+252; assert row==18355<20161
    assert geo['bad_prime_factors']==[2] and geo['route_denominators']==[1,2,4]
    # Existing complex bridge dominates the changed bit finite constants.
    assert two_level_coefficient<1<<30000
    eta=Q(1,10**12); beta=Q(1,10**9); cap=(1-beta)*b
    sv=min(c,Q(int((cap-grid)*10**18),10**18)); assert sv<c and sv<cap
    selected=moment.moment(P,m,W,sv,True); assert selected[1]<1
    chain=[Q(384599,10**10)]; cutoff=[]
    def ceilq(x): return -((-x.numerator)//x.denominator)
    for _ in range(3):
        old=chain[-1]; z=(1-sv)*sv+sv*old
        gaps=[sv-z,1-z-sv,1-z-sv*(1-old),1-sv]
        gap=min(gaps); assert old<z<sv<1-z and gap>0
        bound=max(1,ceilq(36/gap**2),ceilq(2*(4+(two_level_coefficient-1).bit_length())/gap))
        assert Q(bound)*gap**2>=36 and Q(bound)*gap>=2*(4+(two_level_coefficient-1).bit_length())
        cutoff.append(dict(gap=str(gap),cutoff_log2=str(bound))); chain.append(z)
    bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),
                rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)))
    q=chain[-1]*(1-2*eta); bound=(1-eta)*q/(1+q); ticks=bound/grid
    k=Q((ticks.numerator-1)//ticks.denominator,10**18)
    asm=outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta)
    assert len(asm['strict_constraints'])==47 and min(asm['strict_constraints'].values())>0
    try: outer.assembly(chain[-1],b,bridge,k+grid,eta=eta,beta=beta)
    except AssertionError: pass
    else: raise AssertionError('next combined grid point admitted')
    assert k>Q(1,1024) and k==Q(998243154231047,10**18)
    result=dict(status='PASS_CONDITIONAL_COMBINED_KAPPA_ABOVE_2_POW_MINUS_10',
                bit_coarse=str(c),complex_coarse=str(b),selected_bit_coarse=str(sv),
                kappa=str(k),kappa_decimal=format(float(k),'.18f'),log2_kappa=math.log2(float(k)),
                threshold='1/1024',strict_excess=str(k-Q(1,1024)),gain_over_frozen_361_percent=float(k/Q(804849251275843,10**18)-1)*100,
                binding='complex',bit_moment_interval=list(map(str,bm)),next_bit_grid_rejected=True,
                two_rational_engines=True,composed_moment_upper=str(bm[1]**2),halving_depth=2,
                bootstrap_chain=list(map(str,chain)),strict_constraints={n:str(z) for n,z in asm['strict_constraints'].items()},
                next_kappa_grid_rejected=True,local_and_global_bit_sha256=sha(out/'GLOBAL.json'),
                independent_bit_audit_sha256=sha(out/'AUDIT.json'),
                complex_verification_sha256=sha(v),complex_global_sha256=sha(cx),
                finite=dict(unit_additions=unit,route_items=J,selector_calls=selectors,coefficient=str(coefficient),
                            coefficient_bits=coefficient.bit_length(),two_level_coefficient=str(two_level_coefficient),
                            two_level_coefficient_bits=two_level_coefficient.bit_length(),charged_bound_bits=512,
                            payload_prefix_bits=prefix.bit_length(),charged_payload_prefix_bits=192,
                            row_coefficient=row,retained_row_coefficient=20161,cutoff=cutoff),
                retained_obligations=['PR370 E8 local bit and nine copied-total admission',
                    'All-size weighted bit compiler, prime/tape/precision and analytic transfer interfaces',
                    'PR377 local E8 complex theorem, exact Clifford compiler and common fine-grid/row/analytic interfaces'],
                scope='Conditional finite construction and exact arithmetic assembly. No Lean proof or priority claim; no enumeration of the entire orthogonal cover.')
    (out/'COMBINED.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('strict_constraints','bootstrap_chain','finite','bit_moment_interval','composed_moment_upper')}),flush=True)

if __name__=='__main__': main()
