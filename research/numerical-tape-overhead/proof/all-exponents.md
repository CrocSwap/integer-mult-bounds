# A computable input length for each requested exponent

Let \(q\ge2\) be an integer. Set \(D=(60q)^3\) and let \(j\) be the first integer starting at 2 for which \(2^j\ge jD+2\). Define \(t_q=\max(1{,}572{,}864{,}480,jD)\). The fixed multiplier with the [fixed adaptive Walsh guard](address-native-staircase.md) satisfies
\[
    \log_2\log_2 n\ge t_q
      \quad\Longrightarrow\quad
    T(n)\le n(\ln n)^{1/2+1/q}.
\]
Both the coefficient one and the input cutoff are part of this estimate. Neither the program nor its control depends on \(q\). The following numbers use only integer arithmetic.

| \(q\) | Time exponent | \(j\) | Sufficient \(\log_2\log_2 n\) |
|---:|---:|---:|---:|
| 10 | 0.6 | 33 | 7,128,000,000 |
| 100 | 0.51 | 44 | 9,504,000,000,000 |
| 1,000 | 0.501 | 54 | 11,664,000,000,000,000 |
| 10,000 | 0.5001 | 64 | 13,824,000,000,000,000,000 |
| 100,000 | 0.50001 | 74 | 15,984,000,000,000,000,000,000 |

For \(q=1000\) the separate [three-slope history calculation](routing-label-walsh.md) supplies a lower sufficient threshold. The table evaluates the [60-coefficient smooth formula](profile-limit.md) uniformly in \(q\).

## Proof

The search terminates. For example, \(b=\lceil\log_2(2D+4)\rceil\) has \(b\le2D+4\); therefore \(2^{2b}\ge(2D+4)^2\ge2bD+2\). Also \(j\ge2\), \(t_q\ge jD\ge2D>4097\). Write \(t=\log_2\log_2 n\), \(\ell=\log_2 n\). Once \(t\ge t_q\), the actual input is in the coprime branch: exact packing gives \(\ell<2k\), whereas the dyadic branch requires \(k<2^{4096}\). Its [eventual smooth estimate](profile-limit.md) covers an extra bit at that length,
\[
        2T(n)\le n\sqrt{\ell}\,2^{60\Phi(t)} .
\]
At \(jD\) one has \(D\log_2(jD+2)\le Dj\). Since \(\log_2(t+2)/t\) is decreasing, \(D\log_2(t+2)\le t\) for every \(t\ge t_q\). Cubing gives \(60\Phi(t)\le t/q\). Thus \(2T(n)\le n\ell^{1/2+1/q}\). Finally \(\ell=\ln n/\ln 2\le2\ln n\) and \(1/2+1/q\le1\), proving the claimed natural-log coefficient. [Whole-integer implication and table receipts](../S008/Frontier.lean) · [Uniform real comparison](../S008/NumericalCutoff.lean) · [Profile density](../S008/WholeProfile.lean) · [Natural-input geometry](../S008/InputClock.lean)

The exponent excess tends to zero with increasing \(q\). The displayed cutoffs increase with \(q\); this argument gives no single finite input beyond which the exponent is exactly \(1/2\).

The formal proof applies the logarithm test at $jD$ and the smooth construction at $t_q$. This distinction matters for small $q$, where the smooth-bound floor exceeds $jD$. [Proof for every integer $q$](../S008/IntegerBounds.lean).
