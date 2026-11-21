# SPDX-License-Identifier: Apache-2.0
"""Check the directed split theorem instantiation, full price and fixed-word scope."""
from collections import Counter
from dataclasses import replace
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from upstream import install

install()
from binary_receiver import Receiver, source_rule
from calibration import GAP, SPLIT_TARIFF, SPLIT_TILT, PRODUCTIVE_TILT, SPLIT_WEIGHT, prices
from independent_binary_price import mass, rank_price, raw_moments
from module_atoms import balanced_widths
from resources import requirements
from strict_moment import certify
from strong_binary import caller, graph, native_word

CURRENT_LOWER = Q('0.00389011528633')
RAW_LEFT = Q('0.003890115286594461129996942')
RAW_RIGHT = Q('0.003890115286594461129996943')
OLD_H = 114_688_000_000_000
OLD_ENTRANCE = 136_798_773_006_437


def check(ok, message):
    if not ok:
        raise ArithmeticError(message)


def main():
    p = SPLIT_TARIFF
    v, c = p.power, p.bit_c
    word = native_word(v)
    targets, paid = raw_moments(graph(), caller())
    check(Counter(x.rank for x in word.targets) == targets and
          Counter(x.rank for x in word.paid) == paid, 'exact independent contribution lists agree')
    check(mass(targets, 1-RAW_LEFT, 0) > mass(paid, 1-RAW_LEFT, 1) and
          mass(paid, 1-RAW_RIGHT, 0) > mass(targets, 1-RAW_RIGHT, 1), 'directed fixed raw crossing')
    t, z, w = 1-c, SPLIT_TILT, PRODUCTIVE_TILT
    check(SPLIT_WEIGHT == Q(1,64) and 0 < c < z <= 1 and Q(101,100)**250 > 2 and
          Q(101,100)*c/z < SPLIT_WEIGHT, 'universal paid split surcharge majorant')
    denom = mass(targets,t,0)
    alpha = mass(paid,t,1)/denom
    gamma = mass(paid,t+z,1)/(rank_price(12,z)[0]*denom)
    lam = rank_price(15,w)[1]*mass(targets,t-w,1)/denom
    eps = Q(2,p.floor)
    surplus = 1-alpha**v-SPLIT_WEIGHT*gamma**v-lam**v
    check(surplus > eps == Q(1,2**49), 'strict independent rational surplus')
    first = certify(word,c,z,w,v,49,15,split_weight=SPLIT_WEIGHT)
    check((first['raw_paid'],first['raw_productive']) == (104904,18906), 'dyadic split theorem replay')
    check(mass(paid,t,0)+1 > mass(targets,t,1), 'extra rank-one paid cut corrupts the raw price')
    try:
        certify(word,c,z,w,v,49,15)
    except ArithmeticError:
        pass
    else:
        raise ValueError('Old split surcharge unexpectedly funds this exact trial')
    check((word.ambient,word.floor,word.low_cut,word.high_cut,word.power) == (134,15,12,12,268),
          'actual source has the tested cutoff, ambient and factor power')
    check(18_906**v+104_904**v+23_800**v < 2**(18*v) and
          15**v >= 2 * 12**v and 512*v <= min(p.rank_logs), 'all slots and every physical carrier')
    check(5**13>16*4**13 and 8*(Q(13,4)+Q(1,512))<27 and
          18*(Q(13,4)+Q(1,512))<60, 'inherited complete finite geometry budget')
    check(2**64*(v+1)*2**(28*v)<2**(512*v) and
          872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v), 'generation and causal precision guard')
    check(69**100 < 2**611 and 1024*p.floor < 69*15*(p.floor-2), 'complete replication price')
    scale = 4*(134*127)**v*p.floor
    full_debit_bound = Q(611,100)+c*(scale-1).bit_length()
    check(full_debit_bound < 21, 'complete directed 21-bit price')
    receiver = Receiver(2,balanced_widths(1),direct=True,profile=p)
    check(receiver.rule is source_rule(v) and receiver.rule.word is word and receiver.stock>0,
          'same 268-factor binding on the physical receiver')
    ordinary, numerical, rows = prices(p)
    resources = requirements(p)
    check(ordinary==21 and numerical==10 and len(rows)==6, 'full charged supplier and all six stage rates')
    for bad in (replace(p,ordinary=p.kappa+4*GAP),
                replace(p,ordinary=p.ordinary+Q(1,10**14))):
        try:
            prices(bad)
        except ArithmeticError:
            pass
        else:
            raise ValueError('Corrupted full price passed')
    check(resources['all_size_margin_lower_at_entrance']>0 and max(p.rank_logs)<OLD_H and
          resources['log2_sufficient_public_precision']<OLD_ENTRANCE and
          CURRENT_LOWER < p.kappa < RAW_LEFT, 'smaller complete resource bounds and constructive gain')
    out = {'kappa':str(p.kappa), 'gain_over_8032':str(p.kappa-CURRENT_LOWER),
           'bit_trial':str(c), 'paid_split_tail_weight':str(SPLIT_WEIGHT),
           'paid_tilt':str(z), 'target_tilt':str(w), 'band_floor':p.floor, 'factor_power':v,
           'strict_surplus_floor_e24':(surplus*10**24).__floor__(),
           'full_fractional_BIT_debit_upper_e9':(full_debit_bound*10**9).__ceil__(),
           'raw_FIXED_BIT_crossing':[str(RAW_LEFT),str(RAW_RIGHT)],
           'comparison':{'kappa':str(CURRENT_LOWER),'largest_rank_log2':OLD_H,
                         'sufficient_public_exponent':OLD_ENTRANCE},
           'complete_requirements':resources}
    raw = json.dumps(out,indent=2,sort_keys=True)+'\n'
    if len(sys.argv) == 2:
        Path(sys.argv[1]).write_text(raw)
    else:
        print(raw,end='')
    print('PASS_SPLIT_TARIFF_AND_COMPLETE_SIGNED_GAIN',str(p.kappa),ordinary,numerical,flush=True)


if __name__ == '__main__':
    main()
