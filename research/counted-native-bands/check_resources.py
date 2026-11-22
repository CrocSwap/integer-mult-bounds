"""Check the finite constants of the rank census and the real predecessor image lower bound."""

from collections import Counter
from fractions import Fraction
import json
from math import prod

from calibration import PROFILES, SPLIT_TILT, PRODUCTIVE_TILT, prices, entrance
from strict_moment import power_interval, moment, UNIT
from strong_binary import native_word
from strong_complex import word, load_changed
from upstream import HERE


def primes(r):
    p = 2
    while p * p <= r:
        if r % p == 0:
            yield p
            while r % p == 0:
                r //= p
        p += 1
    if r > 1:
        yield r


def check_alphabet(word):
    target = Counter(p.rank for p in word.targets)
    paid = Counter(p.rank for p in word.paid)
    all_primes = set(primes(12))
    for rank in {*target, *paid}:
        all_primes.update(primes(rank))
    assert max(*target,*paid) < 256 and len(all_primes) <= 10
    assert set(p for r in paid for p in primes(r)) <= {2, 3, 5, 7}
    assert max(sum(paid.values()), sum(target.values())) <= 281568
    assert sum(k * v for k, v in paid.items()) <= 153 * 281568
    assert min(target.values()) >= 48
    return target, paid, sorted(all_primes)


def surplus(word, c, lo, tilt, drop, bits):
    t = 1-c
    targets, paid, _ = check_alphabet(word)
    den = moment(targets, t, False)
    alpha = Fraction(moment(paid, t, True), den)
    gamma = Fraction(moment(paid, t+tilt, True)*UNIT, den*power_interval(12,tilt)[0])
    lost = Fraction(moment(targets,t-drop,True)*power_interval(lo,drop)[1], den*UNIT)
    assert Fraction(0) < c <= Fraction(1,250) and tilt >= Fraction(1,4)
    assert alpha**word.power + gamma**word.power/64 + lost**word.power < 1-Fraction(1,1<<bits)


def inventory():
    raw_positive = word(*load_changed(HERE / "inputs"))
    positive_primes = check_alphabet(raw_positive)[2]
    surplus(raw_positive, Fraction(2043,524288), 16, Fraction(19,64), Fraction(23,64), 14)
    assert 2**249 * 129**250 >= 257**250
    assert Fraction(4,615) + Fraction(1,128) < Fraction(1,64)
    assert 5**13 > 16 * 4**13
    assert 4 * 281568 < 2**21 and 4*153*281568 < 12*2**24
    rows = {}
    for name, p in PROFILES.items():
        raw = native_word(p.power)
        target, paid, bit_primes = check_alphabet(raw)
        high = p.power != 128
        tilt = SPLIT_TILT if p.power in (268,285) else Fraction(19,64)
        drop = PRODUCTIVE_TILT if p.power in (268,285) else Fraction(31 if high else 26,64)
        surplus(raw,p.bit_c,15 if high else 16,tilt,drop,p.floor.bit_length()-2)
        if high:
            assert target[15] >= 2**7
        else:
            assert 4 * 8**84 * 64**43 == 16**128
            assert min(target[r] for r in (4,8,64)) >= 2**7
        assert max(paid) >= 12 and raw.ambient == 134
        bit_loss, pos_loss, _ = prices(p)
        h = max(*p.rank_logs, p.complex_log)
        assert min(p.rank_logs) >= 512*p.power
        stages = len(p.rank_logs)+1
        d = 1000*(h+2)
        new_exp = (stages * (2**4096 + d**100)).bit_length()
        old_lower = 7*(max(p.rank_logs)-2-9*p.power)
        assert old_lower > new_exp
        rows[name] = dict(kappa=str(p.kappa),binary_heights=p.rank_logs,positive_height=p.complex_log,
                          complete_activation=entrance(p),fixed_setup_log_le=new_exp,
                          former_installed_log_gt=old_lower,
                          prior_fixed_setup_log_le=1024*h+stages.bit_length(),
                          binary_debit=bit_loss, positive_debit=pos_loss)
    return {"binary_primes":bit_primes,"positive_primes":positive_primes,"profiles":rows}


if __name__ == "__main__":
    print(json.dumps(inventory(), sort_keys=True, indent=2))
