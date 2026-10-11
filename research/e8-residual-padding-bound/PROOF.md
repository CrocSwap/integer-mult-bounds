# Exact residual padding optimum for the enlarged204 T32 inventory

Let the bank width be 73, and let the prescribed residual ranks 9, 8, 7, 5, 4 have respective counts 18464, 4896, 288, 608, 736. For any real alpha with 0 < alpha <= 1/100, define

`f(r) = r * ((73/r)**alpha - 1)` for r > 0, and f(0) = 0.

The minimum sum of padding f-values is exactly **1495 f(1)**. The checked T32 packing attains it with 2943 banks and 1495 rank-one padding blocks. This is a statement about padding with a fixed real-child inventory and bank width, not a global optimum for the multiplication construction.

Assign the five real ranks dual weights `(1/8, -1/64, -5/32, -7/16, -37/64)`. For a bank containing counts x of the real ranks, write w for their total dual weight and p for the unused rank capacity. The verifier exhausts all 4765 possible nonnegative integer x satisfying `sum(r*x[r]) <= 73`, including the empty bank.

It certifies `f(p) >= w*f(1)` as follows. If w <= 0 the claim is immediate. If p = 1 it checks w <= 1. In all other positive-w cases it checks p >= 2 and the exact integer inequality

`73**(64*(19*p - 20*w)) >= p**(64*19*p)`.

This implies `(19/20)*p*log(73/p) >= w*log(73)`. To turn it into the required exponential inequality, put L = log(73), l = log(73/p). The checked positive Taylor partial sum for exp(5) exceeds 73, so L < 5. For 0 < alpha <= 1/100, alpha*L < 1/20 and

`exp(alpha*L) <= 1/(1-alpha*L) < 20/19`.

The inequalities `exp(alpha*l)-1 >= alpha*l` and `exp(alpha*L)-1 <= alpha*L*exp(alpha*L)` therefore give

`f(p)/f(1) >= (19/20)*p*log(73/p)/log(73) >= w`.

If the padding rank p is split into several positive-rank blocks, its cost cannot decrease: `f(r)=73**alpha*r**(1-alpha)-r` is concave with f(0)=0 for 0 < alpha < 1, and hence is subadditive. Thus the bound also covers multiple padding blocks, including when an unsplit rank would exceed the child-depth limit.

Summing over all banks gives at least `dot(counts, dual)*f(1) = 1495*f(1)`. Every bank in the supplied T32 packing has p in {0,1} and w=p, attaining equality. Counts and all arithmetic in this certificate use exact integers or rational numbers; no solver result or floating approximation is trusted.

The proof does not optimize bank width, real-child counts, local programs, phases, compiler costs, or analytic assumptions. Proportional copies of this residual inventory inherit the same per-copy optimum; different inventories require a new certificate.

Run `python3 -B verify.py /tmp/padding-bound-result.json` from this directory, using a fresh output path outside the package. Python standard library only. The checker verifies the complete package inventory before and after the proof, matches the frozen expected scientific result, and writes a JSON receipt.
