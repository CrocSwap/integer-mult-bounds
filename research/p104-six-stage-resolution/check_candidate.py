#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the installed six-stage profile from both directed price engines."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
import json
from types import SimpleNamespace
from unittest.mock import patch
from upstream import install
install()
from band_product import production_supplier
from binary_receiver import Receiver,source_rule
from calibration import (NEAR_RAW,SMALL_GAP,GAP,COMPLEX_C,SPLIT_TILT,
                         PRODUCTIVE_TILT,prices)
from check_profile import RAW_LEFT, RAW_RIGHT, check, reject, check_stop_dispatch
from independent_binary_price import raw_moments,mass,rank_price
from module_atoms import balanced_widths
from outer_budget import qualify
from positive import power_le
from resources import requirements
from strict_moment import certify,UNIT,moment,power_interval
from strong_binary import graph,caller,native_word

def main():
 check_stop_dispatch()
 check(not power_le(2,10**20,1<<1000) and power_le(1,10**20,1<<1000),'exact new stop threshold')
 with patch('strong_complex.artifacts',return_value=SimpleNamespace(graph=None,layout=None)),patch('strong_complex.word',return_value=object()):
  a=production_supplier(9,10**20);b=production_supplier(9,10**17)
  check(a is not b and a.carrier==b.carrier==512 and a.denominator==10**20,'actual stopping policy and cache binding')
 production_supplier.cache_clear()
 T,P=raw_moments(graph(),caller());p=NEAR_RAW;v,c=p.power,p.bit_c
 check(p.kappa==Q('0.00389011528659443') and p.kappa>SMALL_GAP.kappa and p.kappa<RAW_LEFT,'strict gain below raw bound')
 check(len(p.rank_logs)==6,'retained six funded stages')
 word=native_word(v)
 check(Counter(x.rank for x in word.targets)==T and Counter(x.rank for x in word.paid)==P,'source and price inventories agree')
 check((word.ambient,word.floor,word.low_cut,word.high_cut)==(134,15,12,12),'actual powered source parameters')
 t,z,w=1-c,SPLIT_TILT,PRODUCTIVE_TILT
 denom=mass(T,t,0)
 alpha=mass(P,t,1)/denom
 gamma=mass(P,t+z,1)/(rank_price(12,z)[0]*denom)
 lam=rank_price(15,w)[1]*mass(T,t-w,1)/denom
 surplus=1-alpha**v-2*gamma**v-lam**v
 # Recompute the same power from independent integer-root interval enclosures.
 d2=moment(T,t,False)
 alpha2=Q(moment(P,t,True),d2)
 gamma2=Q(moment(P,t+z,True)*UNIT,d2*power_interval(12,z)[0])
 lam2=Q(moment(T,t-w,True)*power_interval(15,w)[1],d2*UNIT)
 surplus2=1-alpha2**v-2*gamma2**v-lam2**v
 lower_e30=(min(surplus,surplus2)*10**30).__floor__()
 check(min(surplus,surplus2)>Q(lower_e30,10**30)>Q(2,p.floor),'both directed classic split surpluses')
 certify(word,c,z,w,v,p.floor.bit_length()-2,15)
 # A dyadic trial known to lie above the independently bracketed crossing must fail.
 upper=Q((RAW_RIGHT*(2**70)).__ceil__(),2**70)
 check(upper>RAW_RIGHT,'crossing control')
 reject(certify,word,upper,z,w,v,p.floor.bit_length()-2,15)
 check(mass(P,t,0)+1>mass(T,t,1),'one extra paid rank-one position exceeds raw surplus')
 check(18_906**v+104_904**v+23_800**v<2**(18*v) and
       5**13>16*4**13 and 8*(Q(13,4)+Q(1,512))<27 and
       18*(Q(13,4)+Q(1,512))<60 and 15**v>=2*12**v and
       512*v<=min(p.rank_logs),'complete split census, enumeration and frame guard')
 check(2**64*(v+1)*2**(28*v)<2**(512*v) and
       872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v),'generation and causal precision')
 bit,numeric,stages=prices(p)
 check((bit,numeric,len(stages))==(28,10,6),'complete staged invoices')
 positive=COMPLEX_C-Q(numeric,p.complex_log);g=Q(1,p.positive_stop_denominator)
 signed=qualify(p.kappa,g,p.ordinary,positive)
 reject(qualify,p.kappa,GAP,p.ordinary,positive)
 reject(qualify,p.kappa,Q(0),p.ordinary,positive)
 reject(qualify,p.kappa,g,p.kappa+4*g,positive)
 reject(qualify,p.kappa,g,p.ordinary,p.kappa+5*g)
 reject(prices,replace(p,positive_stop_denominator=GAP.denominator))
 res=requirements(p)
 # Replace the old listed-rank G<2^50 convenience by the source's general
 # v*G <= 13*H/4 + v. The latter follows from (5/4)^13 > 2^4.
 H=max(p.complex_log,*p.rank_logs)
 Gplus1=(13*H+4*v-1)//(4*v)+2
 nodes=res['raw_structural_nodes_log2_upper'];q=res['native_volume_log2_upper']
 local_exponent=4*nodes+8*(H+1).bit_length()+512
 check(Gplus1<=4*(H+1) and 19+2*nodes+Gplus1.bit_length()<local_exponent<q,
       'unbounded-H native slots fit the dynamic q allocation')
 check((p.positive_stop_denominator.bit_length()+1)<512,'fixed stopping comparator fits reserved controls')
 check(res['all_size_margin_lower_at_entrance']>0,'all-size stock and precision certificate')
 receiver=Receiver(2,balanced_widths(1),direct=True,profile=p)
 check(receiver.rule is source_rule(v) and receiver.rule.word is word and receiver.stock>0,'profile reaches physical BIT receiver')
 report={'kappa':str(p.kappa),'positive_stop':str(g),'binary_price':str(c),'power':v,'floor':p.floor,
         'surplus_floor_e30':lower_e30,'positive_paid_cap':str(positive),'signed':signed,
         'raw_interval':[str(RAW_LEFT),str(RAW_RIGHT)], 'raw_gap_upper':str(RAW_RIGHT-p.kappa),
         'improvement_over_8035':str(p.kappa-SMALL_GAP.kappa),
         'stage_rates':[str(t[2]) for t in stages], 'forest_G_plus_1_upper':Gplus1,
         'native_slot_log_upper':19+2*nodes+Gplus1.bit_length(),
         'local_exponent_upper':local_exponent, 'complete_requirements':res}
 content=json.dumps(report,sort_keys=True,indent=2)+'\n'
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(content)
 else:print(content,end='')
 print('PASS_NEAR_RAW_SIX_STAGE_SIGNED_GAIN',p.kappa,flush=True)
if __name__=='__main__':main()
