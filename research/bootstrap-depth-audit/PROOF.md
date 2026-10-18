# A ceiling with independent savings at each bootstrap level

This argument audits the scalar accounting in Rohan Arun's PR387 at
`d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea`. It assumes the inherited completed
ordinary-supplier contract and certified coarse-root bracket. It proves a
limit of that accounting, not a lower bound on an algorithm's actual runtime.

## 1. The retained recurrence

The stopped-leaf estimate in the pinned proof, with saving s and preceding
ordinary saving a, is

```
T(e)/V = O(e^(1-s) + e^((1-s)^2+s(1-a)) + e^s log(e)).
```

The middle term gives the accounted saving

```
F_s(a) = 1 - ((1-s)^2+s(1-a)) = s(1-s+a).
```

The other terms require positive gaps; ignoring those restrictions can only
enlarge the set of certificates considered here. In particular, we may allow
`a_j <= F_(s_j)(a_(j-1))` at each level, with independent `0 < s_j < u`.
This is an optimistic relaxation, not a construction of every such schedule.

The initial saving a0 is fixed and satisfies `0 <= a0 < u < 1/32`.
In PR387 every legal s is below its true complex coarse root, which the
inherited moment certificate places below u. Its bit-supplier restriction,
positive backoff and beta restrictions only reduce the permitted set.

## 2. A uniform envelope

Set `A_0=a0` and `A_j=F_u(A_(j-1))`. For `0 <= a <= A` and
`0 <= s <= u < 1/2`, the exact identity

```
F_u(A) - F_s(a)
  = u(A-a) + (u-s)(1-u-s+a)
```

has a nonnegative right-hand side. In our domain its second factor is
strictly positive, since `1-u-s+a >= 1-2u > 0`. Induction therefore gives
`a_j <= A_j`; with the legal strict bound `s_j < u`, it is strict for j>=1.
Skipping a level or reverting to the preceding certificate cannot evade the
bound, because `A_j > A_(j-1)`.

Indeed,

```
u-A_j = u(u-A_(j-1)),
A_j = u-u^j(u-a0),
A_j-A_(j-1) = u^(j-1)(1-u)(u-a0) > 0.
```

These identities prove the envelope for all finite depths and all real
per-level saving choices in the stated interval. No grid search is being
substituted for this argument.

## 3. Transfer to the compact assembly margin

PR387 uses `q=a(1-2 eta)` and `M=(1-eta)q/(1+q)`. Its legal parameters have
`a>0` and `0<eta<1/2`. Thus

```
M < q/(1+q) < a/(1+a) <= A_j/(1+A_j) = C_j.
```

The function x/(1+x) is increasing for x>=0: its difference between y and x
is `(y-x)/((1+x)(1+y))`. Any certificate that exceeds κ in every performance
margin must in particular have `M>κ`. Consequently `C_j<=κ` excludes that
certificate. This reasoning does not assume that the compact margin remains
the minimum after independently changing parameters.

For the pinned values

```
a0 = 384599/10^10
u  = 999632926176283805554/10^24
κ  = 199726931618167/(2*10^17),
```

exact integer cross-multiplication gives

```
0.546434 * 10^-18 < κ-C_5 < 0.546435 * 10^-18.
```

Since C_j is increasing with j, depths 0 through 5 are excluded. The use of
the **upper** coarse endpoint means more precision within the inherited root
bracket cannot rescue five levels. The argument permits zero supplier slack
as a limiting relaxation and independent choices at each level; it is stronger
than the predecessor's five-level test at its one published slack tuple.

The exact integer implementation is separate from the rational recurrence.
If `u=p/q` and `a0=h/k`, put

```
N_j = k*p*q^j - p^j(k*p-h*q),
D_j = k*q^(j+1).
```

Then `A_j=N_j/D_j`, and `C_j=N_j/(D_j+N_j)`. For `κ=K/V`, the verifier
records the strictly positive integer `K(D_5+N_5)-V*N_5`, as well as the
fully reduced rational gap. No floating-point result is used for admission.

## 4. The sixth level and the starting-supplier boundary

For the published lower coarse endpoint l, the source chooses
`eta=beta=10^-18`, `backoff=10^-24` and `s=(1-beta)l-backoff`. Recomputing its
six steps from a0 gives the exact pinned chain and positive recurrence gaps.
Its compact margin satisfies

```
0.406 * 10^-18 < M_6-κ < 0.407 * 10^-18.
```

This confirms the compact-margin part of the published six-level certificate.
It does not establish the inherited supplier construction or independently
replay the other assembly constraints. There is no claimed new κ.

Solving `C_5>κ` for the initial saving gives the necessary condition

```
a0 > u - (u - κ/(1-κ))/u^5 = a_required.
0.000586993 < a_required < 0.000586994.
```

This threshold is exact for the optimistic scalar envelope at u. At equality,
strict assembly slack still prevents admission. The real root and supplier
conditions can require a larger starting saving. A changed starting saving
`a0=3/5000=0.0006<u` already makes the optimistic five-level ceiling exceed κ;
the verifier checks this as a negative control on any unqualified depth claim.

Different starting suppliers, stopped-leaf recurrences, outer assemblies or
sharper analysis are outside this result. All-size compilation, dirty-register
restoration, completed spectators, fixed tapes, finite cutoffs, precision and
analytic transfer remain inherited obligations. The source's full moment
bracket is assumed rather than established by this small arithmetic audit.

Isaac Grannis (@BagMan9), with substantial OpenAI Codex assistance. Apache-2.0.
Credit Rohan Arun's PR185/PR387, the supplier lineage and the outer-assembly
authors listed in README.md and the preserved notices.
