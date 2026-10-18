# Fixed-dispatch packing ceiling

Keep PR637's 72 calls (71 JP8, one CK), admitted provider words, geometry,
complete helper roles and finite-invoice convention fixed. Each residual owner
segment has integer capacity at most 48. After assigning every required helper
width once, total unused capacity is fixed at 107028 = 2229·48 + 36.

For 0 < q < 1, the idle contribution to the exact normalized moment is

    73^q / (73·7168) · Σ g^(1-q),

where the sum ranges over positive segment gaps g. The fixed provider
contribution does not depend on the owner assignment. The function x^(1-q)
is strictly concave on positive x and vanishes at zero. If 0 < a ≤ b < 48,
transferring ε = min(a, 48-b) from a to b cannot increase
(a-ε)^(1-q) + (b+ε)^(1-q), and strictly decreases it for ε > 0.
Repeated transfers leave at most one gap strictly between zero and 48.
Consequently every feasible map has idle moment at least that of
2229 gaps of 48 and one gap of 36.

This is a relaxation: transfers in this argument need not respect time windows
or physical families. The independently verified literal owner map in this package realizes
that concentrated gap profile. It attains the relaxation and therefore minimizes
the moment for every q in (0,1) among maps with these fixed inputs. Since each
rank is below 73, the moment is strictly increasing in q. Its positive root lies
below 1: already the fixed supplier contribution at q = 1 exceeds 1
(the supplier has 260438 paid atoms, compared with the denominator 7168).
Thus the same map maximizes
the moment-limited complex exponent ceiling and its monotone κ = q/(1+q)
conversion. Other finite-invoice and outer admission conditions remain separate.

This does not bound constructions with different words, helper widths, dispatch,
geometry, invoice conventions, or additional mathematical improvements. The
reported decimal κ remains an exactly certified lower bound; attaining this
packing profile does not make its rounded decimal the exact root.

The candidate is independently checked against the actual native widths and
profiles, and its 35,424 roles realize this gap profile. There are 16,128 owner
segments of total capacity 387,072, with 280,044 required helper-width units.
The exact certified lower bound is κ = 0.001636461592777116.
