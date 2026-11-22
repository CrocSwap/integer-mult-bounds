"""Exact dyadic design threshold for the fixed seven heights and ordinary transfer."""

from fractions import Fraction


def verify():
    # Proved by GLOBAL-PROOF and reconstructed by global_crossing.py.
    lower = Fraction("0.003890115286594461129996942")
    upper = Fraction("0.003890115286594461129996943")
    target = Fraction("0.003890115286594461")
    eta = Fraction("0.0039")
    gap = Fraction(1, 10**21)
    heights = [2 * 10**12 * 16**i for i in range(7)]
    results = {}
    for bits in (64, 65, 66):
        denominator = 2**bits
        numerator = (upper * denominator) // 1
        price = Fraction(numerator, denominator)
        # Thus this is the maximum possible *raw-funded* point on its mesh.
        assert price < lower < upper < price + Fraction(1, denominator)
        unrounded = 0
        booked = 0
        for stage, height in enumerate(heights, 1):
            debited = price - Fraction(11, 8 * height)
            unrounded = (249 * debited + unrounded) / 250
            limit = min(eta, (249 * debited + booked) / 250)
            if stage < 7:
                booked = ((limit // gap) - 1) * gap
        results[bits] = (numerator, unrounded - target - 4 * gap,
                         limit - target - 5 * gap)

    # The unrounded recurrence is an upper bound even if the previous rates
    # may be chosen freely. It increases in price and in the previous rate.
    # Every dyadic with <=64 denominator bits is also on the 64-bit mesh.
    assert results[64][0] == 71759961109033309
    assert results[64][1] == Fraction(-6679915143415124983420909,
                                      274877906944000000000000000000000000000000000)
    assert results[65][0] == 143519922218066619
    assert results[65][2] == Fraction(7905295224657471,
                                      4398046511104000000000000000000000000)
    assert results[66][0] == 287039844436133239
    assert results[66][2] == Fraction(27007124810227343,
                                      1759218604441600000000000000000000000)
    assert results[64][1] < 0 < results[65][2] < results[66][2]
    return results


if __name__ == "__main__":
    for bits, (n, upper_gap, booking_gap) in verify().items():
        print(bits, n, "unrounded_limit_minus_target_4g", upper_gap,
              "rounded_limit_minus_booking_5g", booking_gap)
    print("PASS_RAW_AND_ORDINARY_MINIMUM_DYADIC_DEPTH_65")
