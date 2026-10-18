# Composite-radix boundary of the averaged cyclotomic height argument

**Mathematical audit and conditional precision bound; no new kappa.**

The prime-power averaging argument in Chafik's [PR1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025)
uses `d/phi(d) <= 2`. That step cannot be reused unchanged for mixed
radices: at the seed-selected radix `r=134`, it reads
`134/phi(134)=67/33>2`. This is a counterexample to that intermediate
inequality outside its stated domain, **not a defect in PR1025**.

Replacing two by `r/phi(r)` repairs the argument. The extra factor
cancels the field degree in the algebraic-norm estimate, so the sufficient
circle-gap exponent remains `O(r^2 log^2 r)` for **every radix whose
conjugate-reciprocal resultant is nonzero**. Jason Willems's
[PR666](https://github.com/CrocSwap/integer-mult-bounds/pull/666) supplies that
condition for `r=2*p^a`, every prime `p>=5` and integer `a>=1`.
The argument below repeats the seed-2 specialization explicitly.

This adds a mixed-radix application of the averaged-height method to PR666's
older worst-embedding bound. It does not establish nonvanishing for every
composite radix. No solver, working word size, supplier profile, selected
frontier, or multiplication exponent is changed.

## Reproduce and inspect

Python 3.10+; standard library only. From the repository root:

```sh
python3 -I -O -B research/composite-height-audit-seed67/verify.py
```

Expected final line:

```text
PASS_COMPOSITE_HEIGHT_AUDIT_S67 radices=132 characters=8910 lifts=19 family_budgets=136 controls=9 no_new_kappa
```

The exact receipt is [EXPECTED.json](EXPECTED.json). The checker imports no
predecessor arithmetic implementation. It checks:

- all 8,910 nontrivial character maps at every integer radix 3 through 134,
  including 487,412 unit-image occurrences, uniform fibers and rational
  harmonic envelopes;
- all 19 instances `r=2*p^a<=134`, `p>=5` prime: independently reconstructed
  cyclotomic polynomials, literal tail products, the reciprocal's degree loss,
  and explicit modular Bezout identities;
- 136 budget cases, for every prime `5<=p<=67` and `1<=a<=8`, plus the
  132 conditional finite-radix budgets. These are integer exponent calculations,
  not allocations or executions of arrays of those sizes;
- nine rejected mathematical/admission mutations, including the invalid
  prime-power ratio, nonunit averaging, lost fiber multiplicity, shifted or
  damaged reciprocals, the excluded prime three and a wrong seed identity.

The analytic inequalities are justified by the written proof below. The
finite checker does not numerically enclose all logarithmic heights, prove
the theorem for all radices, or formalize it in a proof assistant.

The eight package tests additionally check all 19 square Sylvester matrices
by a separate dense elimination implementation. A shifted reciprocal and
the excluded prime three make that independent matrix check singular.

For isolated source/receipt fault tests and the registered replay:

```sh
python3 -I -O -B research/composite-height-audit-seed67/test_verify.py
python3.12 -B scripts/research_package.py --package research/composite-height-audit-seed67
```

## Statement

Let `r>=3`, `n=r-1`, `D=phi(r)`, `ell=ceil(log2 r)`, and take
`zeta=exp(2 pi i/r)`. Every primitive embedding is covered by a unit k
modulo r. Set

```text
a_(k,j) = product_(s=j+1)^(r-1) (1-zeta^(ks)),
f_k(z) = sum_(j=0)^n a_(k,j) z^j,
P_k(z) = f_k(z)/r,                 H_k = sum_j |a_(k,j)|.
```

The empty product is one. Define
`f_k*(z)=z^n conjugate(f_k(1/conjugate(z)))`. Assume the resultant
of `f_1` and `f_1*` is nonzero. This hypothesis is separate from
the following height estimate and must not be inferred from a finite budget.

Put

```text
T = min(n D r, (3 n r (ell+1)^2)/2 + 2 n D ell),
d_r = 1 + 2 ell + T.
```

Both terms defining T are integers, because `nr=r(r-1)` is even.
Then, for every primitive embedding k and every `|z|=1`,

```text
|P_k(z)| >= 2^(-d_r).
```

For every cyclic length `L>=1`, integer stride w, and `|tau|=1`,
with `U=tau Z_L^w`, the inherited Fourier transfer gives

```text
||P_k(U)^(-1)||_infinity <= 2^(2 d_r + r + 2).
```

Here `T <= (35/8) r^2 ell^2`, so both exponents have order
`O(r^2 log^2 r)`, independently of the number of prime factors.
This statement remains conditional on the nonzero resultant.

## Proof: the averaging step for arbitrary radices

Write `t=log r` with natural logarithms and `C=r/phi(r)`.
Use the same sampled function as PR1025:
`L(0)=0` and `L(s)=log|1-zeta^s|` for `1<=s<r`, with normalized
discrete Fourier coefficients `Lhat(h)`.
The product over all nonzero residues is r, hence `Lhat(0)=t/r`.

For completeness, the Fourier-mass estimate needs no prime-power
hypothesis. Set `delta=1/r`, `rho=1-delta`, and
`Lrho(s)=log|1-rho zeta^s|`, now including s=0.
Its absolutely convergent logarithm series has Fourier coefficient mass
at most `sum_(m>=1) rho^m/m=t`; aliasing cannot increase that mass.
For `a_s=|1-zeta^s|`, `s!=0`,

```text
|L(s)-Lrho(s)| <= delta/(2rho) + delta^2/(2rho a_s^2).
```

This follows by taking half the logarithm of
`|1-rho zeta^s|^2/a_s^2 = rho(1+delta^2/(rho a_s^2))`,
then using `-log(1-delta)<=delta/rho` and `log(1+x)<=x`.
Concavity of sine gives `a_s>=4 min(s,r-s)/r`.
Pairing residues and using `sum_(j>=1) j^-2<=2` gives
`sum_(s!=0) a_s^-2<=r^2/4`. Therefore

```text
sum_(s!=0) |L(s)-Lrho(s)| <= 1/2 + 1/(8rho) <= 11/16.
```

At zero the omitted correction is exactly t. For any sampled E, its
normalized transform satisfies `sum_h |Ehat(h)|<=sum_s |E(s)|`.
Consequently

```text
sum_h |Lhat(h)| <= 2t+11/16 <= 2t+1.                 (1)
```

Next fix `h!=0 mod r` and put `q=r/gcd(h,r)`.
The reduction map from units modulo r onto units modulo q is surjective
for **every divisor q**, not only prime powers. To see this, lift a unit
modulo q and use the Chinese remainder theorem to make the lift equal
to one modulo each prime dividing r but not q. Primes dividing q
already do not divide the lift. As a surjective homomorphism of finite
groups, this map has equal fibers. Multiplication by `h/gcd(h,r)`
permutes the units modulo q.

For every consecutive interval I,

```text
|sum_(s in I) zeta^(hks)| <= 2/|1-zeta^(hk)|.
```

Averaging the right side over units k therefore gives
`phi(q)^(-1) sum_(j unit mod q) 1/sin(pi j/q)`. Pair j with q-j,
use `sin(pi j/q)>=2 min(j,q-j)/q`, and enlarge to all nonzero
residues. With harmonic numbers H_m this is at most

```text
(q/phi(q)) H_floor(q/2)
 <= (r/phi(r)) (1+log r)
 = C(1+t).                                         (2)
```

The middle inequality uses
`q/phi(q)=product_(p|q) p/(p-1)<=product_(p|r) p/(p-1)`.
The possible middle residue is only overcounted. The envelope is
independent of I; no maximum is moved through an average.

Let M_k be the maximum of zero and the logarithms of the tail-product
coefficients. Fourier inversion and the zero mode yield

```text
M_k <= t + sum_(h!=0) |Lhat(h)| 2/|1-zeta^(hk)|.
```

Since `H_k<=r exp(M_k)`, (1) and (2) give the general-radix bound

```text
sum_(k unit mod r) log H_k
 <= D [2t+C(2t+1)(1+t)].                            (3)
```

At prime powers `C<=2`, this recovers PR1025's
`D(4t^2+8t+2)`. At mixed radices the replacement by C is essential
to this derivation; the counterexample `67/33>2` concerns precisely
that step.

## Proof: resultant, dyadic exponent and operator transfer

The coefficients of f are algebraic integers. In the cyclotomic field,
let R be the determinant of the 2n by 2n Sylvester coefficient matrix
with columns `f,zf,...,z^(n-1)f,f*,zf*,...,z^(n-1)f*`.
Our hypothesis gives R nonzero, so its algebraic norm is a nonzero integer.

At embedding k each column has Euclidean norm at most H_k, hence
`|R_k|<=H_k^(2n)`. Complex conjugation commutes with the cyclotomic
embeddings. The chosen embedding and its distinct conjugate have
equal determinant modulus and equal H. Bounding all other norm factors
therefore gives

```text
|R| >= product_(k outside the chosen conjugate pair) H_k^(-n).
```

The adjugate supplies `A f+B f*=R`, with degrees below n and every
coefficient of A and B bounded by `H^(2n-1)`.
On the unit circle, `|f*|=|f|`, so the local cofactor powers cancel
the two removed embeddings:

```text
|P(z)| >= H / [2rn product_k H_k^n]
       >= 1 / [2rn product_k H_k^n].                (4)
```

The last step uses the monic coefficient, which gives H>=1.
This is Ali Romman's PR621 norm/cofactor argument with PR1025's
embedding-specific heights. It assumes neither a rational resultant
nor that the average height bounds each individual embedding.

Use `2/3<log 2<3/4` and `t<=ell log 2`. The exponent from (3)
satisfies

```text
nD [2t+C(2t+1)(1+t)] / log 2
 <= nD [2ell + (3C/2)(ell+1)^2]
  = 2nD ell + (3nr/2)(ell+1)^2.                    (5)
```

This is the cancellation of the totient factor. The uniform alternative
`H_k<=2^r-1<2^r` bounds the same exponent by nDr.
Also `2rn<=2^(1+2ell)`. Equations (4)-(5) establish the displayed d_r.
For ell>=2, `(ell+1)^2<=(9/4)ell^2` and
`2ell<=ell^2`; using n<=r and D<=r gives the stated `35/8` envelope.

For the operator statement, put `g(t)=1/P(exp(it))`.
The gap and `|P'|<=n(2^r-1)/r` bound g and its derivative.
Parseval and Cauchy-Schwarz, with
`sum_(k!=0) k^-2<=4`, bound the absolute sum of its Fourier
coefficients by

```text
2^d_r + [2n(2^r-1)/r] 2^(2d_r) <= 2^(2d_r+r+2).
```

Every integer power of U has infinity norm one. Substituting U into
the absolutely convergent Laurent series gives a two-sided inverse of
P(U), with the same norm bound. This includes zero and noncoprime
strides; the proof uses the series as an analytic argument, not an
algorithm.

## A certified composite family

For `r=2*p^a`, `p>=5` prime and `a>=1`, reduction at any prime
ideal above p sends a primitive r-th root to -1 because

```text
Phi_(2*p^a)(x) = (x+1)^(p^(a-1)(p-1))  (mod p).
```

Literal tail products and conjugation followed by reversal then give

```text
f_r(z)  -> z^(r-2)(z+2),
f_r*(z) -> 1+2z.
```

There is **no shift on the reciprocal**. The seed identity
`2(z+2)-(1+2z)=3` and the reciprocal's constant term one prove
coprimality when p>=5. Equivalently, at its only root
`z=-1/2`, the first polynomial has value
`(-1/2)^(r-2) * 3/2 != 0`.

The reduced first polynomial remains monic of degree n. Even though
the reciprocal loses degree, coprimality makes the original square
coefficient map injective: if `A f+B f*=0` and both multiplier degrees
are below n, then f divides B, forcing B=0 and A=0.
Thus the resultant is nonzero modulo that ideal, hence in characteristic
zero. This is the seed-2 specialization of PR666; the lifting theorem
and this nonvanishing family are credited to that predecessor.

At p=3 the reduced pair has the common root z=1. The checker rejects
that **lifting route**. It is not a characteristic-zero counterexample
at radix six, which PR666 covers separately.

For the seed family, the gap exponents are:

| Radix | Old coarse dyadic exponent | New sufficient exponent |
|---:|---:|---:|
| 134 = 2*67 | 1,176,269 | 1,176,269 |
| 8,978 = 2*67^2 | 356,393,327,561 | 28,312,479,536 |
| 601,526 = 2*67^3 | 107,201,688,658,439,141 | 246,481,130,023,766 |

The old column is the common coarse envelope `1+2ell+nDr`, not
PR666's sharper fixed-radix certificates or an executed working precision.
Only exponent arithmetic is performed at the larger radices.

## Provenance and limits

Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
[SOURCES.json](SOURCES.json) records SHA256 and Git-blob pins for:

- Chafik's PR1025 proof at `6ef2168ac90d42926bceb7ac9b2e029463800c76`:
  regularization, Fourier mass and averaged-height/norm method.
- Jason Willems (@at1as), PR666 lifting at
  `8e5a8d4da5bf6d83dc0b39ec90fea15e3cf627d6`:
  the composite nonvanishing family and reciprocal-degree argument.
- Ali Romman, PR621 at the base's retained
  `research/prime-power-cyclic-inverse/PROOF.md`:
  kernel, resultant/cofactor and uniform cyclic-operator transfer, with
  the pinned OpenAI exact-DFT and classical q-Pochhammer lineage.
  Existing source notices and licenses are unchanged.

Remote proof references are pinned citations, not runtime inputs. The new
proof is written out here; the checker uses only its own arithmetic and the
declared retained source binding. This is independent implementation evidence,
not independent human review.

[TASK.json](TASK.json) records OS seed 67, the three candidates, local claim,
bounded domain, stopping rule and overlap review. PR668 checks resultants,
PR796 checks nonarchimedean valuations, and PR803/832 refine the
circle-to-operator step; this package adds none of those results.
Its change is the primitive-unit average for mixed radices and cancellation
of its totient factor. No closed search is reopened.

## Open next questions

Can this bound be incorporated into a paid
composite-radix solver while charging coefficient preparation, rounding,
scratch restoration and tape access? A first step is one explicit PR666
radix with a complete error recurrence. That implementation is absent here.
The circle-gap improvement alone supplies no reduction in executed precision,
recursive cost or kappa. All selected compiler, common-label/mutable-source,
hosting, precision/tape and analytic multiplication obligations remain inherited.
See the structured question in TASK.json.

Prepared for Hanson Sun (@bbMisk) with substantial OpenAI Codex assistance
in derivation, implementation, verification and writing. No subagents,
independent human review, formal proof or literature-priority claim.
New material is Apache-2.0.
