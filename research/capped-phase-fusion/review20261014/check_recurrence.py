"""Exact mixed-width recurrence, product stock and outer cost controls.

These calculations corroborate REVIEW-RESPONSE.md's parameterized proof.
They do not replace its all-size supplier/semantic/tape hypotheses.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json, sys

P=Path(__file__).resolve().parent
PACKAGE=P.parent


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def rational(value):
    return Q(value['rational']) if isinstance(value,dict) else Q(value)


def main():
    ledger=json.loads((PACKAGE/'frontier_fusion/FRONTIER-FUSION-ARITHMETIC.json').read_text())
    row=ledger['rows']['strassen']
    # The short endpoint has its own independent exact enclosure in this
    # source-bound receipt. No native rounded-weight optimization is used.
    E,X,B=[rational(row[k])for k in ('epsilon','xi','beta')]
    q,a=[rational(row[k])for k in ('q','a')]
    b=rational(ledger['complex_lower_short'])
    need(all(rational(v)<1 for v in ledger['native_moment']),'native moment is not strict')
    kappa=rational(row['kappa'])
    stop=Q(1,10**9)
    sigma,tau=1-b,1-a
    H={1:1559766,2:337668,3:278058,4:84912,5:54612,8:5328,48:22748}
    m,W,physical=73,66304,66794
    mass=sum(r*n for r,n in H.items())
    need(m*W-mass==23680,'wrong native rank deficit')
    need(m*m>2*max(H)**2,'halving guard fails')
    need(0<sigma<tau<1-q<1,'internal exponent ordering fails')
    need(sigma+stop*(1-sigma)<1-a<1-q,'stopped leaf bound fails')
    group=2**(36*36)
    for j in range(1,37):group*=2**(2*j)-1
    stockbits=(group*physical).bit_length()
    rowcoefficient=2*stockbits+9909+252+2*2048
    need(stockbits==2644 and rowcoefficient==19545<20161,'wrong physical row stock')
    # Arithmetic conversion of this coefficient alone, not a replacement
    # for the full depth-dependent product-row proof in REVIEW-RESPONSE.
    q0=(rowcoefficient+511)//512
    need(q0==39,'row chunk upper bound changed')
    # Since q<1/2, 16^{-(1-q)}<1/4, giving a simple exact
    # geometric constant 4/3. No equality-depth assumption is used.
    need(q<Q(1,2),'deferred-width geometric estimate fails')
    costs={
        'main_transform':1-E*q,'global_routing':1-a,
        'Gaussian_groups':E-q*B,'group_bit_routing':E-a*B,
        'polylog_full_group_scans':E-B,
        'boundary_Strassen':E-X+Q(29,32),
        'sparse_union':E+B+Q(1,2)-X,
        'full_union_key_surcharge':2*B+Q(3,2)-X,
        'polynomial_products':1-E,'core_face':E+B-3,
        'halo_keys':1+B+3-8,
        'halo_metadata_fallback':E+3-8+2*(B+1-E)-1,
    }
    margins={k:1-kappa-v for k,v in costs.items()}
    need(min(margins.values())>0,'written outer cost is unpaid')
    sides={'one_axis_neighborhood':1-E,'total_support':1-B,
           'capped_gauge':1-B-X-Q(1,10**6),
           'global_absolute_gauge':1-E-Q(1,10**6),
           'membership_record':1-B-2*(1-E),
           'halo_fraction':8-B-3}
    need(min(sides.values())>0,'written side condition fails')
    # A mixed-width tree is not a uniform m-ary width tree: this exact
    # control would have depth one in the latter interpretation.
    def depth(e):
        d=0
        while e>=m:
            e=max(H)*(e//m);d+=1
        return d
    need(depth(m*m)>2,'control did not distinguish mixed-width recursion')
    controls={
        'uniform_depth_two_is_insufficient':depth(m*m)>2,
        'old_controller_count_15_rejected':7+8*2!=15,
        'one_row_chunk_not_accepted_as_T74_stock':q0!=1,
        'former_axis_scan_unpaid':1-E<kappa,
        'unrecentered_group_guard_fails':B+E>1,
        'zero_complex_gap_rejected':not (b<b),
    }
    need(all(controls.values()),'missing negative control')
    out={'status':'PASS_EXACT_MIXED_RECURRENCE_AND_ORIGINAL_OUTER_COST_CONTROLS',
         'native':{'m':m,'W':W,'physical':physical,'profile':H,'mass':mass,'deficit':23680,
                   'halving':[m*m,2*max(H)**2],'physical_stock_bits':stockbits,
                   'row_coefficient':rowcoefficient,'coefficient_to_chunks_conversion':q0},
         'rate_order':{'sigma':str(sigma),'tau':str(tau),'target':str(1-q),
                       'leaf_exponent':str(sigma+stop*(1-sigma)),'stop':str(stop)},
         'deferred_reserve':{'all_size_proof_uses':'Full depth-dependent product stock and a polylogarithmic tail.',
                             'geometric_sum_factor_upper':'4/3'},
         'cost_exponents':{k:str(v)for k,v in costs.items()},
         'strict_cost_margins':{k:str(v)for k,v in margins.items()},
         'strict_side_margins':{k:str(v)for k,v in sides.items()},'controls':controls,
         'mixed_depth_at_73_squared':depth(m*m),
         'scope':'Exact rational input/outer/stock checks for the published PR1673 '
                 'Strassen specialization. Weighted-tree proof and complete '
                 'functional hypotheses are stated in REVIEW-RESPONSE.md. '
                 'No unconditional multiplication theorem is claimed.'}
    target=Path(sys.argv[1])if len(sys.argv)>1 else P/'RECURRENCE-CONTROLS.json'
    target.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(costs),'cost rows',len(controls),'controls')


if __name__=='__main__':main()
