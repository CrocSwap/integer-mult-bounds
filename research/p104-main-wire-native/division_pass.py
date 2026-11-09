#!/usr/bin/env python3
"""Exact division by an odd d as one least-significant-bit-first pass (standard library).  python3 -I -B division_pass.py
The scalars 1/3 and 1/5 are 1/(2^2 - 1) and 1/(2^2 + 1): multiplying by 3 or 5 is one shift and one add or subtract, and the checked exact division by d (3, 5 and the products 9, 15, 25, 45, 75, 125, 225, 375, 1125 that occur
as odd parts of denominators) is one pass over the bits of a two's-complement integer from the least significant bit: at each bit the quotient bit is read off the input bit and a carry c with 0 <= c < d, and
at the end c must equal the value fixed by the signs; a nonzero remainder is reported by that final test.
Exhaustive test: every integer of width 1 to 12 bits, every divisor above: exact division gives the quotient, every non-divisible input is flagged.  Ends PASS_DIVISION_PASS."""
import sys
sys.dont_write_bytecode = True
def dv(N, w, d):
    u = N & ((1 << w) - 1); c = 0; o = 0
    for i in range(w):
        b = (u >> i) & 1; x = (b - c) % 2; c = (c + d * x - b) // 2
        assert 0 <= c < d
        o |= x << i
    sN = (u >> (w - 1)) & 1; sQ = (o >> (w - 1)) & 1
    return o - (sQ << w), c == d * sQ - sN
tot = bad = rej = non = 0
for d in (3, 5, 9, 15, 25, 45, 75, 125, 225, 375, 1125):
    for w in range(1, 13):
        for N in range(-(1 << (w - 1)), 1 << (w - 1)):
            q, ok = dv(N, w, d); tot += 1
            if N % d == 0: bad += (not ok or q * d != N)
            else: non += 1; rej += not ok
print('cases %d, exact quotients wrong %d, non-divisible inputs %d, flagged %d' % (tot, bad, non, rej))
if bad or rej != non: raise SystemExit('FAIL')
print('PASS_DIVISION_PASS')
