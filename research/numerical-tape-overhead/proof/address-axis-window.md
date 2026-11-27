# Coprime short axes at every width $k\ge2^{32}$

**Theorem.** Let $k\ge2^{32}$ be an integer, $w=20\lceil\log_2k\rceil$, $X=2^w$, $Y=\lfloor X/k^2\rfloor$, and $1\le A\le2^{k+1}$. Every interval of $Y$ consecutive integers contains an integer coprime to $A$. In particular the [existing odd-coprime descending search](foundations/coprime-axes.md) constructs all short axes and their dense occupied box throughout the range of the [fixed-tape routing bound](routing-outer-permutations.md). Setting $A=2\prod_{\rm earlier}a_i$ enforces oddness and pairwise coprimality. Each such $A$ is at most $2^{k+1}$. The retained product is at least $2^k(1-k^{-2})^{\lfloor k/w\rfloor}\ge2^{k-1}\ge2h$, as in the source attachment.

The proof here combines the exact number of prime factors affordable above the sieve range with the actual truncation degree of each inclusion–exclusion summand. The data-path algorithm and its charged gcd trials remain the same.

## Independent band estimates

Write $t=\log_2k\ge32$, $z=k^{11/8}$ and $B=\log_2z=11t/8\ge44$. Let $u_j=z^{1/2^j}$. Process bands $(\sqrt{u_j},u_j]$ for $0\le j<J=\lfloor\log_2(B/2)\rfloor$, so $J\ge4$ and the residual cutoff $U=u_J$ lies in $[4,16)$. Put $\gamma_j=B/2^{j+1}$ and $a=\lfloor\gamma_j\rfloor$. As in the earlier sieve proof, primes in $(2^v,2^{v+1}]$ divide $\binom{2^{v+1}}{2^v}<2^{2^{v+1}}$ and have total reciprocal mass at most $2/v$. Summing $v=a,\ldots,2a+1$ gives band mass at most $2\ln2+3/a$, since $\sum_{v=a}^{2a+1}1/v\le1/a+\ln((2a+1)/a)$ and $\ln(1+1/(2a))\le1/(2a)$.

Let $V_j=\prod_{p\in j}(1-1/p)$ and let $\sigma_j=\sum_{p\in j}1/p$. The following bounds hold according to the *actual* lower band endpoint.

| $a$ at least | $\sigma_j$ less than | $V_j^{-1}$ less than |
|---|---:|---:|
| 16 | $8/5$ | 5 |
| 8 | $9/5$ | 7 |
| 4 | $11/5$ | 12 |
| 2 | 3 | 64 |

Indeed $\ln2<7/10$ by the exponential series through degree three. With $p>2^a$ one has $-\ln(1-1/p)\le (2^a/(2^a-1))/p$. For the first row, $(65536/65535)(8/5)<1601/1000<\ln5$, using the first five positive terms of $2\operatorname{artanh}(2/3)$. For the other rows use $\ln2>2(1/3+(1/3)^3/3)$, $\ln7\ge3\ln2-1/7$, and $\ln12\ge3\ln2+1/3$. These rational comparisons are reproduced exactly by the [checker](../checks/address-axis-window.py).

Let $s$ be the number of bands with $\gamma_j\ge16$. Then $s\le\log_2(B/16)$ and every subsequent or residual prime is at most $2^{32}$. The survival product through 256 exceeds $1/10$ by multiplying the 54 primes in that bounded range. The single band $(256,65536]$ satisfies the second row and $(65536,2^{32}]$ satisfies the first. Thus all primes through the end of our subsequent bands have product greater than $1/(10\cdot7\cdot5)>1/384$. The genuine independent survival through $z$ is at least

$$
\frac{5^{-s}}{384}\ \ge\ \frac{16^3}{384B^3}.
$$

The finite check through 256 is the only enumeration needed. The checker also proves the stronger product through 65536 is above $1/20$.

## Truncation and transfer to an interval

Use the even truncation $4+2j$ in band $j$. Write $Q_j$ for the truncated inclusion–exclusion polynomial and $E_j$ for the omitted elementary symmetric term of degree $5+2j$. With $h_j$ the actual indicator of survival, Bonferroni gives $0\le h_j\le Q_j$ and $Q_j-h_j\le E_j$. Therefore $\prod h_j\ge\prod Q_j-\sum_j E_j\prod_{i\ne j}Q_i$. Multiply by the exact residual survival indicator.

In the independent prime model, the relative loss against $\prod\mathbb E Q_j$ in the right side is at most $\sum_j V_j^{-1}\sigma_j^{5+2j}/(5+2j)!$. Because $B\ge44$, the first three bands have $a\ge22,11,5$ respectively. All subsequent bands have $a\ge2$. Consequently the relative loss is at most

$$
5\frac{(8/5)^5}{5!}+
7\frac{(9/5)^7}{7!}+
12\frac{(11/5)^9}{9!}+
64\frac{3^{11}}{11!}+
\frac{64\cdot3^{13}}{13!(1-9/(14\cdot15))}
=\frac{488355916353421}{565877812500000}<\frac78 .
$$

Disjointness of bands supplies independence. Since $\mathbb E Q_j\ge V_j$, the expected lower polynomial, including its exact residual factor, is greater than $D=4/(3B^3)$. Using the optional finite product through 65536 gives $D=4/B^3$ instead.

Within any of its $J+1$ product expressions, a squarefree monomial is specified uniquely by its divisor, with coefficient of modulus one. Each expression has at most one omitted $E_j$, adding at most one unit of weighted exponent. The full series of ordinary degrees sums to $\sum_{j\ge0}(4+2j)2^{-j}=12$. Its unused tail at $J$ is $2^{-J}(12+4J)$. The residual product of all primes $\le U<16$ is at most $U^6$. Thus every actual divisor occurring in an expression is at most

$$
U^6 z^{13}/U^{12+4J}\le 2^{-44}z^{13},
$$

since $U\ge4$ and $J\ge4$. For each divisor the number of interval multiples differs from $Y/d$ by at most one. With $Y\ge k^{18}/2$ and $J+1\le2t$, the interval discrepancy as a fraction of $Y$ is at most $4t2^{-44-t/8}$. Its ratio to $D=4/(3B^3)$ is at most $24t^4 2^{-44-t/8}<1/1024$. Here $t\le64\cdot2^{t/32}$ follows from $2^x\ge x\ln2$ and $2\ln2>1$.

Finally, each prime $p\mid A$ above $z$ uses more than $B$ bits of $\log_2 A$. There are at most $(k+1)/B$ such primes. Each excludes at most $Y/z+1$ integers, so the two losses divided by $Y$ are at most $(2/B)2^{-3t/8}$ and $(4/B)2^{-17t}$. The first relative to $D$ is bounded by $\tfrac32B^2 2^{-3t/8}$, which decreases for $t\ge32$ and equals $363/512<3/4$ at 32. The second relative loss is at most $3B^2 2^{-17t}<1/1024$ throughout. Thus the true surviving fraction exceeds $D(1-3/4-2/1024)>0$. This proves the interval statement and the success of every actual descent.

The [exact arithmetic check](../checks/address-axis-window.py) verifies the finite prime products and integer/rational comparisons. The proof controls all later real $t=\log_2 k$ by the displayed analytic inequalities. The elementary sieve is not executed by the multiplier.

The checked [Lean module](../S008/AxisSieve.lean) proves the finite-degree tail identity, the binomial pointwise Bonferroni bound, the integer-interval divisor discrepancy, the one-omission product comparison, the supplementary 54-prime estimate, the rational band-loss bound, and positivity from the normalized error estimates. [address-check-sieve.sh](../verify.py) compiles with Lean 4.34.1 and warning-as-error, replays every declaration in this module with leanchecker against pinned Mathlib commit d13f23b723b8a846827a245b89c10fc7d3f11612, and prints the axioms of seven principal results. Its output lists only propositional extensionality, classical choice, and quotient soundness. The application of the elementary sieve to the actual prime bands and the deduction about the caller's coprime search are supplied by the written proof above.
