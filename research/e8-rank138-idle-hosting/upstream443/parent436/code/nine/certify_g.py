"""Two rational engines, finite overcharges and the strict outer assembly for the compressed nine-stage bit supplier.

Port of PR #386's certify.py (Zhihao Chen, with OpenAI Codex assistance; Apache-2.0); generalisation by eumemic with
Anthropic Claude assistance (Apache-2.0). The bit side is the original, line by line, with R and the live stock read
from GLOBAL.json instead of PR #370's literals (865, 15,465, rank mass 987,264). The complex side is not rebuilt here:
each cited complex coarse saving b (data/complex-b-nine.json) goes through the original selection, three-step
bootstrap, cutoff and 47-constraint assembly, and the resulting kappa must equal the value cited with it.
With --regression (PR #370's word) the original literals are asserted, including #386's c, b and kappa.
usage: certify_g.py --pricing DIR --out DIR --complex-b FILE [--regression]"""
import argparse, hashlib, importlib.util, json, math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--pricing',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); ap.add_argument('--complex-b',type=Path,required=True)
    ap.add_argument('--regression',action='store_true')
    a=ap.parse_args(); out=a.out
    g=json.loads((out/'GLOBAL.json').read_text()); geo=json.loads((out/'GEOMETRY.json').read_text())
    assert g['status']=='PASS_SOURCE_BOUND_NINE_STAGE_BIT_TEMPLATE'
    assert g['geometry_sha256']==sha(out/'GEOMETRY.json')
    audit=json.loads((out/'AUDIT.json').read_text())
    assert audit['status']=='PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT' and audit['template_sha256']==g['template_sha256']
    pricing=a.pricing
    moment=load(pricing/'moment.py','bit9_moment'); other=load(pricing/'base_two_moment.py','bit9_other'); outer=load(pricing/'outer.py','bit9_outer')
    P={int(r):n for r,n in g['profile'].items()}; m=g['m']; W=g['live']; E=sum(P.values()); mass=sum(r*n for r,n in P.items())
    assert (m,W,m*W-mass)==(64,64*120+9*g['R'],2496)
    if a.regression: assert (m,W,mass,m*W-mass)==(64,15465,987264,2496)
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
    T,L,R,V,K=8,9,g['R'],120,4; physical=g['physical']; d=m*m; N=2*m
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
    if a.regression: assert c==Q(1057833103534317,10**18)
    kappas={}
    for s_ in json.loads(a.complex_b.read_text())['suppliers']:
        b=Q(s_['b'])
        eta=Q(1,10**12); beta=Q(1,10**9); cap=(1-beta)*b
        # Seed: PR #431's two-supplier policy, strictly below (1 - beta) times both suppliers. When the bit side
        # is the larger (c > b) it is exactly PR #386's/#425's complex-bound selection min(c, cap - grid).
        sv=Q(int(((1-beta)*min(b,c)-grid)*10**18),10**18); assert sv<c and sv<cap
        if c>b: assert sv==min(c,Q(int((cap-grid)*10**18),10**18))
        binding='complex' if c>b else 'bit'
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
        if a.regression: assert k==Q(s_['kappa_with_pr370_bit']), (s_['name'],str(k),s_['kappa_with_pr370_bit'])
        kappas[s_['name']]=dict(complex_coarse=str(b),selected_bit_coarse=str(sv),kappa=str(k),kappa_decimal=format(float(k),'.18f'),
                               binding=binding,bit_headroom_percent=float(c/b-1)*100,bootstrap_chain=list(map(str,chain)),
                               cutoff=cutoff,strict_constraints={n:str(z) for n,z in asm['strict_constraints'].items()},
                               minimum_strict_constraint=str(min(asm['strict_constraints'].values())),
                               next_kappa_grid_rejected=True,cited_kappa_with_pr370_bit=s_['kappa_with_pr370_bit'],source=s_['source'])
        print('   with %s b = %.15e: kappa = %s = %.15e (%s-bound; %s; 47 strict constraints positive, next grid point rejected)'
              % (s_['name'],float(b),k,float(k),binding,'equal to the cited value' if k==Q(s_['kappa_with_pr370_bit'])
                 else 'cited with the PR #370 bit: %.15e, change %+.6f%%' % (float(Q(s_['kappa_with_pr370_bit'])),100*float(k/Q(s_['kappa_with_pr370_bit'])-1))),flush=True)
    if a.regression: assert kappas['pr386']['kappa']=='998243154231047/1000000000000000000'
    result=dict(status='PASS_COMPRESSED_NINE_STAGE_BIT_SUPPLIER',
                bit_coarse=str(c),bit_coarse_decimal=format(float(c),'.18f'),m=m,live=W,R=R,
                bit_moment_interval=list(map(str,bm)),next_bit_grid_rejected=True,
                two_rational_engines=True,composed_moment_upper=str(bm[1]**2),halving_depth=2,maxchild=max(P),
                local_and_global_bit_sha256=sha(out/'GLOBAL.json'),independent_bit_audit_sha256=sha(out/'AUDIT.json'),
                finite=dict(unit_additions=unit,route_items=J,selector_calls=selectors,coefficient=str(coefficient),
                            coefficient_bits=coefficient.bit_length(),two_level_coefficient=str(two_level_coefficient),
                            two_level_coefficient_bits=two_level_coefficient.bit_length(),charged_bound_bits=512,
                            payload_prefix_bits=prefix.bit_length(),charged_payload_prefix_bits=192,
                            row_coefficient=row,retained_row_coefficient=20161),
                kappa_with_cited_complex=kappas,
                retained_obligations=['PR370 E8 local bit and nine copied-total admission',
                    'All-size weighted bit compiler, prime/tape/precision and analytic transfer interfaces',
                    'The cited complex suppliers and their own interfaces (not rebuilt here)'],
                scope='Conditional finite construction and exact arithmetic assembly. No Lean proof or priority claim; no enumeration of the entire orthogonal cover.')
    (out/'BIT-NINE.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS compressed nine-stage bit coarse saving c = %s = %.15e (m 64, live %d, two engines, next grid point rejected, two-level halving, finite coefficient %d bits)'
          % (c,float(c),W,two_level_coefficient.bit_length()),flush=True)

if __name__=='__main__': main()
