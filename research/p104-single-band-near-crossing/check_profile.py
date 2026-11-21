# SPDX-License-Identifier: Apache-2.0
"""Check the new profile inside the authenticated, privately adapted #8030 export."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from upstream import install
install()
from binary_receiver import Receiver, source_rule
from calibration import GAP, NEAR_CROSSING, PRICE_MATCH, prices
from independent_binary_price import mass, rank_price, raw_moments
from module_atoms import balanced_widths
from resources import requirements
from strict_moment import certify
from strong_binary import caller,graph,native_word

RAW_LEFT = Q('.003890115286594')
RAW_RIGHT = Q('.003890115286595')
SOURCE_COMPLEMENT_CLAIM = Q('.00389011528360')
PEER_PRICE_MATCH_H = 1_568_000_000_000
REFERENCE_H = 299_610_000_000_000


def check(ok,msg):
    if not ok:
        raise ValueError(msg)


def powers(targets,paid,c,v):
    t=1-c; z=Q(19,64); w=Q(31,64)
    denom=mass(targets,t,0)
    alpha=mass(paid,t,1)/denom
    gamma=mass(paid,t+z,1)/(rank_price(12,z)[0]*denom)
    loss=rank_price(15,w)[1]*mass(targets,t-w,1)/denom
    bound=alpha**v+2*gamma**v+loss**v
    check(0<min(alpha,gamma,loss)<=max(alpha,gamma,loss)<1,'valid exact t-weight ratios')
    return bound


def check_operator_quantities(word,profile):
    v=word.power
    Hs=profile.rank_logs
    check((word.ambient,word.floor,word.low_cut,word.high_cut,v)==(134,15,12,12,320),
          'runtime consumes the exact one-band word')
    check(15**v>=2*12**v and 134**v<2**(8*v) and 512*v<=min(Hs), 'ambient, integer separation and generation budget')
    check(18_906**v+104_904**v+23_800**v < 2**(18*v), 'all physical tuple and split positions including remainders')
    check(5**13>16*4**13 and 18*(Q(13,4)+Q(1,512))<60 and 8*(Q(13,4)+Q(1,512))<27,
          'virtual height, unit enumeration and exact integer-column widths')
    check(2**64*(v+1)*2**(28*v)<2**(512*v), 'every raw native record at each production carrier')
    check(872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v), 'active causal context allowance at the first possible width')
    check(72**10000 * (4*(134*127)**v*profile.floor)**39 < 2**240000,
          'independent 24-bit band with complete ordinary factor')
    check(72**10000 * (4*(134*127)**v*profile.floor)**39 >= 2**230000,
          '23 bits fails this exact conservative tariff test')


def main():
    p=NEAR_CROSSING; v=p.power; c=p.bit_c
    t,pay=raw_moments(graph(),caller())
    word=native_word(v)
    check(Counter(x.rank for x in word.targets)==t and Counter(x.rank for x in word.paid)==pay,
          'both independent literal invoice reconstructions agree')
    check(sum(r*n for r,n in pay.items())==285_600 and max(t)==127 and max(pay)==56, 'true physical histogram')
    check(mass(t,1-RAW_LEFT,0)>mass(pay,1-RAW_LEFT,1) and mass(pay,1-RAW_RIGHT,0)>mass(t,1-RAW_RIGHT,1),
          'directed raw crossing endpoints on the literal word')
    check(dict((r,t[r]-pay[r]) for r in range(1,9))==dict(enumerate((-48972,-44892,-1980,-900,-1044,-2916,-480,14520),1)),
          'same monotone paired-rank crossing contract')
    check(c<RAW_LEFT and mass(pay,1-c,0)+1>mass(t,1-c,1), 'one additional paid rank-one call rejects the strict trial')
    first=certify(word,c,Q(19,64),Q(31,64),v,43,15)
    check(first['raw_paid']==104904 and first['raw_productive']==18906,'independent dyadic finite source gate')
    strict_upper=powers(t,pay,c,v)
    check(strict_upper < 1-Q(1,2**43),'independent rational series certificate')
    check(powers(t,pay,c,288)>=1,'preceding factor-count control for the chosen sufficient tariff')
    check_operator_quantities(word,p)
    physical=Receiver(2, balanced_widths(1), direct=True, profile=p)
    check(physical.rule is source_rule(v) and physical.rule.word is word and physical.stock>0,
          'candidate supplied to the actual receiver with a legal finite stock')
    rb,rz,rows=prices(p)
    stock=requirements(p)
    check(rb==24 and rz==10 and len(rows)==6 and p.kappa+4*GAP<p.ordinary and
          stock['all_size_margin_lower_at_entrance']>0, 'six ordinary stages, positive charge and outer guards')
    try:
        prices(replace(p,ordinary=p.kappa+4*GAP))
    except ArithmeticError as e:
        check('numerical consumer' in str(e),'boundary control failed at exact intended gate')
    else:
        raise ValueError('strict signed ordinary equality passed')
    old_upper=RAW_RIGHT-Q(869,REFERENCE_H)
    hmin=5/(RAW_RIGHT-SOURCE_COMPLEMENT_CLAIM-4*GAP)
    match_ceiling=RAW_RIGHT-Q(5,PEER_PRICE_MATCH_H)-4*GAP
    check(p.kappa>old_upper>SOURCE_COMPLEMENT_CLAIM>match_ceiling and hmin//1+1==1692047377327,
          'strict comparison and scoped stock-floor obstruction')
    event={'source':'6285dd829114705862e8d91facaedc1f31d3cfcb','paid':dict(sorted(pay.items())),
           'productive':dict(sorted(t.items())),'c':str(c),'epsilon':str(Q(1,2**43)),
           'strict_surplus_lower_grid_24':str(Q(((1-strict_upper)*10**24)//1,10**24)),
           'application':stock,'raw_BIT_crossing':[str(RAW_LEFT),str(RAW_RIGHT)],
           'claim':str(p.kappa),'kappa_over_8031':str(p.kappa-SOURCE_COMPLEMENT_CLAIM),
           'old_relaxed_ceiling':str(old_upper),'strict_separation':str(p.kappa-old_upper),
           'fixed_word_raw_gap':str(RAW_RIGHT-p.kappa),'fixed_8030_required_H':int(hmin)+1,
           'known_good_8030_application':str(PRICE_MATCH.kappa),
           'controls':['one extra paid rank one','288 at fixed trial and fixed Chernoff offsets',
                       '23-bit bound criterion fails','equality at the signed ordinary gate']}
    txt=json.dumps(event,sort_keys=True,indent=2)+'\n'
    if len(sys.argv)>1:
        Path(sys.argv[1]).write_text(txt)
    else:
        print(txt,end='')
    print('PASS_320_PROFILE_STRICT_ORDINARY_AND_SIGNED_APPLICATION',str(p.kappa),flush=True)


if __name__=='__main__':
    main()
