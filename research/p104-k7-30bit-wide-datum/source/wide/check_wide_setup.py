"""Serial fixed-installer bound at individual datum width w=2^40 (30-bit ordinary heights).

The arithmetic implementation, its proof and its finite tests are the unchanged
#8057/#8055 ones in research/tiered-native-multiplier/check_serial_setup.py and
serial_setup.py; only the explicit width parameter of the written bound changes.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tiered-native-multiplier"))

import check_serial_setup as narrow

WIDTH = 2**40


def clock(w=WIDTH, actions=2**68):
    h = 2*w + 2
    # One Euclid/Bezout reduction, as in SERIAL-SETUP.md, plus eight elementary passes.
    bezout_cost = 2**16*(h + 4)*(7*h + 9)
    elementary = 2**16*(h + 4)**2
    scalar = bezout_cost + 8*elementary
    assert scalar < 2**110
    store = 4*w*actions
    lookup = 8*store*512*128
    action = lookup + scalar + 2**120
    total = (actions + 1)*action*2**32
    exponent = total.bit_length()
    assert total < 2**exponent
    return dict(max_datum_bits=w, lookup=lookup, local_arithmetic=scalar,
                all_setup=total, setup_exponent=exponent)


def main():
    old = narrow.clock()
    assert old["max_datum_bits"] == 2**38 and old["setup_exponent"] == 228
    # The written bound is monotone in w; the narrow instance is the w=2^38 case.
    assert clock(2**38)["all_setup"] == old["all_setup"] < 2**228
    new = clock()
    assert (new["lookup"], new["setup_exponent"]) == (2**129, 230)
    assert new["all_setup"] > old["all_setup"] and new["all_setup"] < 2**230
    # Each ordinary H<2^30 keeps 2^(92H) and the control exponent 1024H+3 below w.
    top = 2**30 - 1
    assert 92*top < WIDTH and 1024*top + 3 < WIDTH <= 1024*(top + 1) + 3
    narrow.main()
    print("PASS_WIDE_DATUM_SETUP", json.dumps(new))


if __name__ == "__main__":
    main()
