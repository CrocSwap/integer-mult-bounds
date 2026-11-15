#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""kappa as a function of the stage count k (our KFORMULA lane).  Standard library only.

Closed-form two-arm rho = 2 caller C(k) (arms floor(k/2) | ceil(k/2), 2 hubs, grow 2; the CALLERMAP closed formula),
with g = h - 1 = 8, for 96 type-A and 8 type-B ports:
  per port  T: 2*T[g j + 1] for j = 1..a and j = 1..b (arm roles), 2*T[g k + 1] (hubs)
            P: 2*P[g j] for j = 2..a-1 and j = 2..b-1 (grouped idles)
  type A:   4*P[g] + 4*P[1]          type B: 2k*P[g] + 4*P[g+1]
Invoice(k) = C(k) + k * N, N = the per-call native invoice of a word (default: #7546's).
Laws [P, derivation in README Part D]:
  S(k)  = 96k - 208 = 2k(v - c) - rho*v               (v = 104, c = 56, rho = 2)
  D0(k)/104 = beta k ln k + alpha k + O(ln k),        beta = 2(2h - 1) = 34
  kappa(k) ~ (2(1 - c/v) - rho/k) / (2(2h - 1) ln k + alpha)   (first order)
  stationarity: kappa* = rho/(beta k*) = 1/((2h - 1) k*)
API: caller(k) -> dict(T, P, nJ);  price(k, native) -> pricekit price dict;  first_order(k, alpha)
CLI: python3 kformula.py [k ...]       (control: C(17) == the #7113 caller invoice and prices #7546)
"""
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pricekit as pk  # noqa: E402

NA, NB = 96, 8
V, C_OWNED, RHO, H = 104, 56, 2, 9


def caller(k, g=8, nA=NA, nB=NB):
    a, b = k // 2, k - k // 2
    T = Counter(); P = Counter()
    for arm in (a, b):
        for j in range(1, arm + 1):
            T[g * j + 1] += 2
        for j in range(2, arm):
            P[g * j] += 2
    T[g * k + 1] += 2
    TA = Counter({r: v * (nA + nB) for r, v in T.items()})
    PA = Counter({r: v * (nA + nB) for r, v in P.items()})
    PA[g] += 4 * nA; PA[1] += 4 * nA
    PA[g] += 2 * k * nB; PA[g + 1] += 4 * nB
    return dict(T=+TA, P=+PA, nJ=k)


def price(k, native, digits=30):
    return pk.price(pk.invoice(caller(k), native), digits)


def S_closed(k):
    return 96 * k - 208


def first_order(k, alpha, h=H, v=V, c=C_OWNED, rho=RHO):
    eps = 2 * (1 - c / v)
    return (eps - rho / k) / (2 * (2 * h - 1) * math.log(k) + alpha)


def main(argv):
    W = pk.load(HERE / 'data' / 'base-7546-word.json.gz'); nat = pk.native_from_word(W)
    C7 = pk.caller_invoice(pk.load(HERE / 'data' / 'caller-7113.json.gz'))
    c17 = caller(17)
    print('closed form C(17) == #7113 caller invoice: T', c17['T'] == C7['T'], 'P', c17['P'] == C7['P'], 'nJ', C7['nJ'])
    print(pk.cite('C(17) x #7546 native', price(17, nat)))
    ks = [int(x) for x in argv] or list(range(6, 41)) + [48, 64, 96, 128]
    for k in ks:
        p = price(k, nat, 20)
        print(k, p['S'], '%.1f' % float(p['D0']), pk.kstr(p['kappa'], 15))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
