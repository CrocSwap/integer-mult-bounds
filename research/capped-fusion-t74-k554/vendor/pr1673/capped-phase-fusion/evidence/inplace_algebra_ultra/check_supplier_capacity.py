"""Exact capacity controls in the large-g, gG >> single-axis-ell regime."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json


def main():
    # p itself has one million binary exponent bits. Only short descriptions
    # and modest exact powers are needed; no input tensor is materialized.
    logp=1_000_000
    eps=Fraction(998,1000)
    beta=Fraction(93,1000)
    interior=Fraction(907,1000)
    d_exp=int(eps*logp)
    g_exp=int(beta*logp)
    ell_exp=logp-d_exp
    g=1<<g_exp
    ell=1<<ell_exp
    G=4*logp+6
    K=128*G
    # This deliberately large constant safely exceeds the published fixed
    # row-stock coefficient for this finite control; it is not a new bound.
    q0=100_000*(g_exp+G.bit_length()+1)
    reserved=(3*g*G+K-1)//K+q0+3
    assert K+int(interior*logp)<ell
    assert g*G>ell
    assert reserved<=g//16
    assert (g*K*G).bit_length()<logp
    assert g_exp<d_exp
    receipt={
        'status':'pass','arithmetic':'exact integer',
        'log2_p':logp,'epsilon':str(eps),'beta':str(beta),
        'log2_d':d_exp,'log2_g':g_exp,'log2_single_axis_ell':ell_exp,
        'G':G,'K':K,'row_stock_test_coefficient':100_000,
        'gG_exceeds_single_axis_ell':True,
        'one_neighborhood_fits_axis':True,
        'all_routing_reservoirs_fit_full_tensor':True,
        'reservation_at_most_h_over_16':True,
        'purpose':'discriminates erroneous gG<=ell / beta<1-epsilon restriction',
    }
    Path(__file__).with_name('SUPPLIER-CAPACITY-CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
