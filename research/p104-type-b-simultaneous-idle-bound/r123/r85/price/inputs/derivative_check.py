"""Check decrease of the complete priced moments through the retained BIT cap."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    'PRICE.json':'52e05b80069ce01cad3b8e5f3cf9123e930de36987bd398dd43f103953a4674a',
    'inputs/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7334-READBACK.json':'337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82',
}


def derivative(histogram,low,high,tariff):
    log,power = tariff['log_bounds'],tariff['power_bounds']
    ln2_low,ln2_high = log(Q(2))
    lower = upper = Q(0)
    for rank,count in histogram.items():
        shift = rank.bit_length()-1
        a,b = log(Q(rank,1<<shift))
        near = -count * power(rank,high)[0] * (a+shift*ln2_low)
        far = -count * power(rank,low)[1] * (b+shift*ln2_high)
        lower += min(near,far)
        upper += max(near,far)
    return lower,upper


def main():
    assert __debug__
    raw = {}
    for name,pin in PINS.items():
        data = (ROOT/name).read_bytes()
        if sha256(data).hexdigest() != pin:
            raise ValueError('Changed dependency '+name)
        raw[name]=data
    price = loads(raw['PRICE.json'])
    readback=loads(raw['inputs/7334-READBACK.json'])
    low,upper=map(Q,readback['new_raw_interval'])
    high=Q(price['retained_bit_premise'])
    assert low < upper == Q(price['old_crossing_upper']) < high
    tariff = run_path(str(ROOT/'inputs/pricing.py'))
    estimates = {}
    for count,quote in price['by_number_of_fused_pairs'].items():
        net=Counter({int(r):n for r,n in price['targets'].items()})
        net.subtract({int(r):n for r,n in quote['paid'].items()})
        bounds=derivative(net,low,high,tariff)
        assert bounds[1]<0
        net[1]-=1
        assert derivative(net,low,high,tariff)==bounds
        with_extra_at_low=tariff['cost'](net,low)
        assert with_extra_at_low[1]<0
        assert Q(quote['complete_margin_with_one_extra_rank_one_at_old_crossing'][1])<0
        estimates[count]={'complete_derivative':list(map(str,bounds)),
                          'extra_rank_one_margin_at_incumbent_crossing_lower':list(map(str,with_extra_at_low)),
                          'same_derivative_with_one_extra_rank_one':True,
                          'one_extra_rank_one_excludes_crossing_in_interval':True}
    print(dumps(dict(input_sha256=PINS,head=price['head'],interval=list(map(str,(low,high))),
                     by_number_of_fused_pairs=estimates,
                     scope='Price only; directed derivative across the retained BIT interval.'),
                indent=2,sort_keys=True))


if __name__=='__main__':
    main()
