"""Exact kappa of the k8 / #1018 invoice with k extra rank-1 local units per call (72 calls), deficit-honest (cards/B258/kap_free.py,
which calls the package's own price_profile.py and replaces only the 2560 deficit pin).  Prints the base, the exact change for each k,
and the first k in 33..48 at which the certificate stops existing."""
import os, sys
sys.path.insert(0, os.environ['EO_ROOT'] + '/cards/B258')
import kap_free as K
base = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
k0 = K.kappa(base)
print('base kappa %.15e' % k0)
for k in (1, 2, 4, 16, 32):
    l = dict(base); l[1] += k; kk = K.kappa(l)
    print('+%d rank-1 local units: kappa %.9e  %+.3f%%  per unit %+.4f%%' % (k, kk, 100 * (kk - k0) / k0, 100 * (kk - k0) / k0 / k))
first = None
for k in range(33, 49):
    l = dict(base); l[1] += k
    try: K.kappa(l)
    except (AssertionError, RuntimeError) as ex: first = k; why = type(ex).__name__; break
print('first k with no certificate:', first, '(exact certificate refused by price_profile.py: %s)' % why)
# break-even of the best pre-cap credit against one unit per violating y (arithmetic on the numbers above and on the recorded band)
band = 3.5152   # percent: bit-cap ceiling of the 112 S4 copies gone (cards/B248/ceil.py: +3.5152%), the largest credit any copy deletion can have
l1 = dict(base); l1[1] += 1
unit = 100 * (k0 - K.kappa(l1)) / k0
print('break-even: best credit %.2f%% / 80 copies = %.4f%% per copy; one unit costs %.3f%% per violating y -> a deletion pays only if it breaks <= %.4f caps per copy'
      % (band, band / 80, unit, (band / 80) / unit))
