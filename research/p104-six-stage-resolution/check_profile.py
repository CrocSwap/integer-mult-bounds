# SPDX-License-Identifier: Apache-2.0
"""Qualify both parameterized signed profiles with two directed price readers."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
from upstream import install

install()
from band_product import production_supplier
from binary_receiver import Receiver, source_rule
from calibration import (COMPLEX_C,FIXED_STOCK,GAP,PRODUCTIVE_TILT,SMALL_GAP,SPLIT_TARIFF,
                         SPLIT_TILT,SPLIT_WEIGHT,prices)
from independent_binary_price import mass,rank_price,raw_moments
from module_atoms import balanced_widths
from outer_budget import qualify
from positive import power_le
from resources import requirements
from strict_moment import certify
from strong_binary import caller,graph,native_word

RAW_LEFT = Q('0.003890115286594461129996942')
RAW_RIGHT = Q('0.003890115286594461129996943')


def check(ok,message):
    if not ok:
        raise ArithmeticError(message)


def reject(run,*args):
    try:
        run(*args)
    except ArithmeticError:
        return
    raise ValueError('The corrupted control passed')


def check_profile(p,expected_debit,targets,paid):
    v,c=p.power,p.bit_c
    word=native_word(v)
    check(Counter(x.rank for x in word.targets)==targets and Counter(x.rank for x in word.paid)==paid,
          'independent literal inventories agree')
    check((word.ambient,word.floor,word.low_cut,word.high_cut)==(134,15,12,12),
          'installed word takes the certified physical positions and split cap')
    t,z,w=1-c,SPLIT_TILT,PRODUCTIVE_TILT
    denom=mass(targets,t,0)
    alpha=mass(paid,t,1)/denom
    gamma=mass(paid,t+z,1)/(rank_price(12,z)[0]*denom)
    lam=rank_price(15,w)[1]*mass(targets,t-w,1)/denom
    surplus=1-alpha**v-SPLIT_WEIGHT*gamma**v-lam**v
    eps=Q(2,p.floor)
    check(0<eps<surplus and mass(paid,t,0)+1>mass(targets,t,1),
          'independent price passes and one excess rank-one cut fails')
    certify(word,c,z,w,v,p.floor.bit_length()-2,15,split_weight=SPLIT_WEIGHT)
    reject(certify,word,c,z,w,v,p.floor.bit_length()-2,15)
    check(18_906**v+104_904**v+23_800**v<2**(18*v) and
          5**13>16*4**13 and 8*(Q(13,4)+Q(1,512))<27 and
          18*(Q(13,4)+Q(1,512))<60 and 15**v>=2*12**v and
          512*v<=min(p.rank_logs), 'actual order, splits, rank width and source enumeration')
    check(2**64*(v+1)*2**(28*v)<2**(512*v) and
          872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v), 'generation and causal precision guard')
    binary,numeric,rows=prices(p)
    check(binary==expected_debit and numeric==10 and len(rows)==6,'complete BIT, positive and stage bills')
    positive=COMPLEX_C-Q(numeric,p.complex_log)
    g=Q(1,p.positive_stop_denominator)
    signed=qualify(p.kappa,g,p.ordinary,positive)
    reject(qualify,p.kappa,GAP,p.ordinary,positive)
    reject(qualify,p.kappa,Q(0),p.ordinary,positive)
    reject(qualify,p.kappa,g,p.kappa+4*g,positive)
    reject(qualify,p.kappa,g,p.ordinary,p.kappa+5*g)
    reject(prices,replace(p,positive_stop_denominator=GAP.denominator))
    res=requirements(p)
    check(res['all_size_margin_lower_at_entrance']>0,'complete size, precision and stripe certificate')
    control=Receiver(2,balanced_widths(1),direct=True,profile=p)
    check(control.rule is source_rule(v) and control.rule.word is word and control.stock>0,
          'this profile enters the physical BIT receiver')
    return {'kappa':str(p.kappa),'g':str(g),'bit_trial':str(c),'factor_power':v,'band_floor':p.floor,
            'certified_surplus_floor_e24':(surplus*10**24).__floor__(),'positive_paid_cap':str(positive),
            'signed':signed,'complete_requirements':res}


def check_stop_dispatch():
    check(power_le(4,3,128) and not power_le(4,4,128), 'integer discrimination at a feasible cutoff')
    for den in (10**14,10**17):
        check(not power_le(2,den,1<<1000) and power_le(1,den,1<<1000),'exact reduced power stop')
    # Check the actual production supplier constructor and its cache key on two ranks.
    with patch('strong_complex.artifacts',return_value=SimpleNamespace(graph=None,layout=None)), \
         patch('strong_complex.word',return_value=object()):
        small=production_supplier(9,10**17)
        old=production_supplier(9,10**14)
        check(small is not old and small.carrier==old.carrier==512 and
              small.denominator==10**17 and old.denominator==10**14, 'positive runtime policy and cache')
    production_supplier.cache_clear()


def main():
    check_stop_dispatch()
    T,P=raw_moments(graph(),caller())
    check(mass(T,1-RAW_LEFT,0)>mass(P,1-RAW_LEFT,1) and
          mass(P,1-RAW_RIGHT,0)>mass(T,1-RAW_RIGHT,1), 'fixed-word raw directed bracket')
    check(FIXED_STOCK.rank_logs==SPLIT_TARIFF.rank_logs and FIXED_STOCK.ordinary==SPLIT_TARIFF.ordinary
          and FIXED_STOCK.bit_c==SPLIT_TARIFF.bit_c, 'fixed-stock comparison')
    fixed=check_profile(FIXED_STOCK,21,T,P)
    near=check_profile(SMALL_GAP,22,T,P)
    check(SPLIT_TARIFF.kappa<FIXED_STOCK.kappa<SMALL_GAP.kappa<RAW_LEFT,
          'both complete gains are below the fixed-word raw ceiling')
    report={'fixed_stock':fixed,'near_crossing':near,'baseline_kappa':str(SPLIT_TARIFF.kappa),
            'same_stock_gain':str(FIXED_STOCK.kappa-SPLIT_TARIFF.kappa),
            'largest_gain':str(SMALL_GAP.kappa-SPLIT_TARIFF.kappa),
            'fixed_word_raw_interval':[str(RAW_LEFT),str(RAW_RIGHT)],
            'remaining_gap_upper':str(RAW_RIGHT-SMALL_GAP.kappa)}
    content=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if len(sys.argv)==2:
        Path(sys.argv[1]).write_text(content)
    else:
        print(content,end='')
    print('PASS_SMALL_GAP_COMPLETE_SIGNED_GAIN',SMALL_GAP.kappa,FIXED_STOCK.kappa,flush=True)


if __name__=='__main__':main()
