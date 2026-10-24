# Complete finite all-height exit decision beyond coefficient domination

This result replaces coefficient domination by a finite, complete all-height decision for a fixed rational exit-comparison law. It gives an explicit tail cutoff, a constructive strict uniform margin, and an accepting law whose falling-factorial coefficient test fails. It answers the released [Discussion #5338](https://github.com/CrocSwap/integer-mult-bounds/discussions/5338). The complete kappa calculation is unchanged.

**Exact domain.** Let X be a specified finite probability law on [0,1], with rational support and positive rational weights. Let p>=1 be an integer and A,B,beta,eta be positive rationals. Define

    N(G)=E[(A+X_0+...+X_G)^p],
    D(G)=(B+beta G)^p,                 G=0,1,2,... .

The question is whether some rational lambda<eta satisfies N(G)<=lambda D(G) at every height. The fixed source's IID exit identity is retained; no change to chronological jobs is made. The decision is complete for these fixed comparison data. Irrational log laws, interval moment inputs and upper majorants need the separate qualification below.

The exact first p moments determine N as a rational polynomial of degree at most p. Grouping the p factors by equality of their IID indices gives the source Bell-polynomial identity. Its highest coefficient is mu_1^p, where mu_1=E X. The denominator has highest coefficient beta^p. The implementation uses the credited Bell/shift formulas and then converts the falling-factorial basis into ordinary monomials. No product histogram at an unbounded height is needed.

**Finite polynomial test, including cancelled leading terms.** Let f(G)=sum_(j=0)^d a_j G^j after removing every zero highest coefficient. If f is identically zero, it is nonnegative everywhere but not strictly positive. A constant has its literal sign. If d>=1 and a_d>0, set

    S=sum_(j<d, a_j<0) |a_j|,
    N_tail=max(1, floor(S/a_d)+1).                       (1)

For every real G>=N_tail, positive lower terms can be discarded and G^j<=G^(d-1). Thus

    f(G) >= G^(d-1)(a_d G-S) > 0.

Consequently f>=0 at all integer heights if and only if its exact values at G=0,...,N_tail-1 are nonnegative. For strict positivity, use strict prefix comparisons. If the highest nonzero coefficient is negative, apply (1) to -f; its cutoff is an explicit failing height for f. This handles equal leading terms by inspecting the actual lower-degree polynomial. It is a finite decision, not a polynomial-time complexity claim; the cutoff can be large in the input bit length.

**Uniform contraction is stronger than pointwise strictness.** Put r_inf=(mu_1/beta)^p. If r_inf>=eta, no lambda<eta can work. This includes equality, even if N(G)<eta D(G) at every finite height. For example G/(G+1)<1 everywhere but has no uniform bound below1.

If r_inf<eta, set lambda0=(eta+r_inf)/2 and apply (1) to f0=lambda0 D-N. Its highest coefficient is positive. Let N_tail be the resulting cutoff and set

    M=max(lambda0, max_(0<=G<N_tail) N(G)/D(G)).

The empty finite maximum is omitted. If M>=eta, the prefix supplies a failing height. Otherwise

    lambda=(M+eta)/2 < eta

is an explicit rational certificate: the prefix is bounded by M, and the tail is bounded by lambda0. This procedure is complete. Indeed any existing uniform margin forces r_inf<eta and every finite prefix ratio below eta. The test then constructs a margin. Conversely each accepted result gives a literal prefix plus a proved tail. This avoids the unsound inference from finitely sampled heights, or from strict finite-height inequalities at an equal limiting ratio.

For a supplied fixed lambda, use the polynomial test directly on lambda D-N; cancellation of its degree-p term can either pass or fail. Such a fixed-lambda result must still satisfy lambda<eta to pay the compiler's source complements.

**A discriminating paid law.** Let X be Bernoulli(1/2), p=2, A=1, B=49/16, beta=1 and lambda=7/25. Then

    N(G)=G^2/4+7G/4+5/2,
    lambda D(G)-N(G)=3G^2/100-7G/200+807/6400.

The falling-factorial coefficient of (G)_1 in this difference is -1/200. Thus the source's coefficientwise test rejects this lambda. Formula (1) gives N_tail=2. The prefix values are 807/6400 and775/6400, both positive, and the proved tail covers every G>=2. This is a strict all-height pass. It is a comparison-law discriminator, not a fully funded native supplier. The checker also constructs a uniform rational certificate under the separate test capacity eta=29/100.

**Source calibration and preserved obstruction.** The checker reconstructs the existing p24 rational upper-moment list from LOG-MOMENTS: v=260, q0=431/500, L=3/2, epsilon=1/100000, A=139/40, B=5149/1000 and beta=127/125. Its25 original coefficient ratios remain below39/2000. The new finite decision also passes at capacity39/2000, with tail cutoff1. This rechecks the algebraic comparison only; it does not rerun the raw profile, logarithm enclosure, excess, base or native proof engines.

The cited capped-reference result supplies a source lower barrier m1>857/1000 and an upper bound eta<0.019675906372710418424472814350 for its fixed p23 question. Exact rational arithmetic confirms

    ((857/1000)/(127/125))^23 > 0.019675906372710418424472814350.

Hence that reference majorant still fails at the leading limit. The present method cannot repair it by changing how lower coefficients are compared. This is not a lower bound on the actual completed paid log law: splitting can lower actual log ranks. The distinction and inherited source bounds are retained, not silently strengthened.

**Upper-moment and compiler boundary.** If the inputs are only proved upper moments, the same Bell formula supplies a polynomial upper bound, because its falling-factorial expression is monotone in each moment at integer G. The finite decision is complete for that polynomial inequality and sufficient for the actual law. Failure is not a proof that the actual completed law fails. Interval estimates can be rounded outwards to rational upper moments for the same sufficient use; they do not inherit exact-law completeness.

To use a passing exit certificate in the source induction, retain lambda<eta=t m^(t-1), the original superpotential and exact exit inventory, the base guard m^(1-t)<=(1+ln(m)/a)^p, and the final rank guard (h+H)^p<h^p 2^((z-t)H). The comparisons a/ln(J)<=A, (a+ln(m))/ln(J)>=B and ln(k_min)/ln(J)>=beta must still be proved for the completed unit. Native implementation, full paid completion mass, ownership, precision, stock and recovery remain separate obligations. No numerical refinement is called a new construction.

**Exact evidence.** Independent finite convolution checks672 polynomial values across96 parameter contexts. There are288 uniform-margin decisions, each with a replayed passing polynomial, a literal failing height or a limiting-ratio rejection. The old-screen discriminator needs only two prefix values. The source p24 calibration checks25 coefficients and its finite decision. Nine boundary controls cover cancelled leading terms, integer equality, a zero uniform gap, the retained p23 barrier and invalid probability laws. All operations use rational arithmetic; the checker uses no numerical root approximation.

Credit the retained [WEIGHTED-EXITS proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/net-tax-rank-compiler/WEIGHTED-EXITS.md) and [LOG-MOMENTS proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/net-tax-rank-compiler/LOG-MOMENTS.md) supply the IID exit law, Bell/shift coefficients and preserved complement/base guards. They retain zxv's logarithmic and net-tax contributions, Jacob Alan Sussman's separated integer compiler, and the native/outer lineage. JoyboyBrian's [PR #5042](https://github.com/CrocSwap/integer-mult-bounds/pull/5042) supplied the exact-raw-moment scope and [PR #5070](https://github.com/CrocSwap/integer-mult-bounds/pull/5070) supplied the true capped-reference obstruction in the [retained proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/capped-paid-law-obstruction/README.md). Classical Bell identities and polynomial tail bounds retain their credit. The new contribution is their complete fixed-data all-height acceptance method, strict-margin construction and discriminating source-interface example.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/complete-all-height-exits
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_COMPLETE_ALL_HEIGHT_EXITS`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Bind exact completed-law moments or proved upper moments to a changed source construction and retain every complement, base and final-rank guard. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
