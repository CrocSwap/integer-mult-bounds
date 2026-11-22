"""Compare concrete retuned predecessor machines at the exact consumer rate."""

from dataclasses import replace
from fractions import Fraction as Q

from calibration import COMPLEX_C, COMPACT, FIXED_STOCK, HIGH_RATE, SMALL_GAP, prices
from outer_budget import qualify
from resources import requirements

EXAMPLES = {
    ".00389": (HIGH_RATE,(686359,10981738,175707798),1489590),
    ".00389011528": (FIXED_STOCK,(3232696,51723128,827570043,13241120677,211857930826,3389726893208),1515617),
    ".0038901152865907": (SMALL_GAP,(6634625402,106154006424,1698464102779,
        27175425644461,434806810311369,6956908964981897),0),
}


def comparisons():
    g = Q(1,10**17)
    output = {}
    for key, (word, heights, numerical) in EXAMPLES.items():
        k = Q(key)
        mlo = int(10/(COMPLEX_C-k-5*g))+1
        assert not numerical or numerical == mlo
        old_debit = prices(word)[0]
        last = Q()
        for h in heights:
            limit = min(word.eta,(249*(word.bit_c-Q(old_debit,h))+last)/250)
            last = Q(int(limit*10**18)-1,10**18)
        source = replace(word,rank_logs=heights,complex_log=mlo,
                         ordinary=last,kappa=k,positive_stop_denominator=10**17)
        row = requirements(source)
        qualify(k,g,last,COMPLEX_C-Q(10,mlo))
        floors = []
        for prior in (COMPACT,HIGH_RATE,FIXED_STOCK,SMALL_GAP):
            loss = prices(prior)[0]
            for count in range(1,7):
                headroom = prior.bit_c-k-4*g-prior.bit_c*Q(1,250)**count
                if headroom <= 0:
                    continue
                geom = sum(Q(1,16)**j for j in range(count))
                floors.append(1+int(Q(249,250)*loss*geom**2/headroom)+mlo)
        log_b = 40+16384*sum(heights)
        output[key] = {"old_word_power":source.power,"feasible_H":list(heights),
                       "feasible_H_M":mlo,"feasible_A":row["log2_sufficient_public_precision"],
                       "old_A_lower_in_stated_tariffs":min(floors),
                       "feasible_log2_C_le":1+max(2**27,1436+100*mlo+log_b+1)}
    return output
