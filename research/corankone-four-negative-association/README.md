# Negative association of four binary full-guard indicators

**A dimension-uniform proof with an exact finite component. No new kappa.**

For four pairwise orthogonal rank-one idempotents over `F_2`, the full-guard
indicators under one complete uniformly sampled `GL_m(F_2)` header are
negatively associated for every `m >= 4`. The covariance is strictly negative
for any two nonconstant increasing real functions of disjoint, nonempty
sets of these four indicators.

This answers Open next question 1 of **lee-phys's #5073**, whose theorem covers
three indicators. **Nick Petalas's #4599** proves the four-way intersection
bound, explicitly leaving general negative association outside its scope.
The new work proves the eight additional mixed-event inequalities required
by the `3+1` and `2+2` splits. It cites the known counting laws; it does not
claim a new law or another independent audit of the predecessor proofs.

## 1. Domain and counting inputs

Let `U_1,...,U_4` be rank-one idempotents on `F_2^m` with `U_i U_j=0` for
`i != j`, and put `P_i=I-U_i`. Draw `G` uniformly from the whole group
`GL_m(F_2)`. Event `E_i` says that all leading principal minors of
`G P_i G^-1`, of orders `1,...,m-1`, are nonzero. Write `Z_i=1_Ei`.

The four image lines and their common-kernel complement give a simultaneous
basis in which `U_i=e_i e_i^T`. A fixed right change of basis permutes the
complete header domain, as does a permutation of the four distinguished
lines. Thus the law of `Z` is exchangeable. This also proves that checking
the standard diagonal idempotents loses no admissible quadruple.

Put `n=m-1`, `X=2^(n+1)`, and let `p_k` be the probability that any specified
`k` of the events occur (`p_0=1`). The exact laws in Petalas's
#4227/#4261/#4275 give, for `0 <= k <= 4`,

```text
p_k = N_k(n) / [2^(kn) product_(j=0)^(k-1) (X-2^j)],
N_0(n)=1.
```

For `k>=1`, Theorem 2 of the retained
[character-law proof](../corankone-triple-header-law/PROOF.md) defines

```text
N_k(n) = sum_c (-1)^|c| Z_k(c)^n,
Z_k(c) = sum_(sigma in {0,1,2}^k)
         (-1)^(sum_(i,j: sigma_i=1, sigma_j=2) c_ij),
```

where `c` ranges over zero-diagonal binary `k` by `k` matrices.
The factors `2^(k(k-1))` from Fourier inversion and
`2^(k(m-k))` from the completion denominator combine to `2^(kn)`.
In particular `N_1=3^n` and `N_2=9^n-2*7^n+5^n`.
The collected spectra for `k=3,4` are the cited #4275 corollary and
[#4599 Section 2](../corankone-four-correlation/PROOF.md).
`SPECTRA` in [verify.py](verify.py) records those exact integer data.
All proof sources are pinned as historical provenance in [SOURCES.json](SOURCES.json).

The complete finite-GL denominator is retained throughout. No asymptotic
replacement of the header distribution is used.

## 2. Exhausting the increasing-event types

For a disjoint pair of increasing events `F,H`, define the positive gap

```text
Delta(F,H) = Pr(F) Pr(H) - Pr(F and H) = -Cov(1_F,1_H).
```

Up to exchanging the two supports, their sizes are `1+1`, `2+1`, `3+1`,
or `2+2`. The nonconstant increasing Boolean functions number `1,4,18`
on one, two and three bits. On three bits their complete list, up to input
permutation, is

| Type | Number of labelled functions | Expectation |
|---|---:|---|
| `x` | 3 | `p1` |
| `AND2` | 3 | `p2` |
| `OR2` | 3 | `2p1-p2` |
| `AND3` | 1 | `p3` |
| `x AND (y OR z)` | 3 | `2p2-p3` |
| `MAJ3` (at least two) | 1 | `3p2-2p3` |
| `x OR (y AND z)` | 3 | `p1+p2-p3` |
| `OR3` | 1 | `3p1-3p2+p3` |

This list can also be obtained by listing the nonempty antichains of nonempty
subsets of a three-element set; their minimal true inputs determine each
increasing event. The verifier independently enumerates all truth tables,
checks monotonicity, and applies subset Mobius inversion. It does not assume
that checking conjunctions suffices.

If the two expectations are `sum_i a_i p_i` and `sum_j b_j p_j`, disjointness
and multilinearity give

```text
Delta = (sum_i a_i p_i)(sum_j b_j p_j) - sum_(i,j) a_i b_j p_(i+j).   (1)
```

The 39 labelled event pairs for canonical splits reduce to exactly these
11 gap polynomials. Letters in the two columns always use disjoint inputs.

| Row | First event | Second | Gap |
|---|---|---|---|
| 1 | `x` | `x` | `p1^2-p2` |
| 2 | `AND2` | `x` | `p1*p2-p3` |
| 3 | `OR2` | `x` | `2p1^2-p1*p2-2p2+p3` |
| 4 | `AND3` | `x` | `p1*p3-p4` |
| 5 | `x AND (y OR z)` | `x` | `2p1*p2-p1*p3-2p3+p4` |
| 6 | `MAJ3` | `x` | `3p1*p2-2p1*p3-3p3+2p4` |
| 7 | `x OR (y AND z)` | `x` | `p1^2+p1*p2-p1*p3-p2-p3+p4` |
| 8 | `OR3` | `x` | `3p1^2-3p1*p2+p1*p3-3p2+3p3-p4` |
| 9 | `AND2` | `AND2` | `p2^2-p4` |
| 10 | `AND2` | `OR2` | `2p1*p2-p2^2-2p3+p4` |
| 11 | `OR2` | `OR2` | `4p1^2-4p1*p2+p2^2-4p2+4p3-p4` |

Rows 1-3 are already covered by #5073. Rows 4-11 are the new inequalities.
Including all eleven in one small certificate checks completeness of the
four-variable argument without making predecessor replay the contribution.

## 3. Exact certificates for every dimension

Use the common positive denominator

```text
Q(n) = 16^n product_(j=0)^3 (2^(n+1)-2^j),
A_k(n) = 2^((4-k)n) N_k(n) product_(j=k)^3 (2^(n+1)-2^j).
```

For `n>=3`, `Q>0`, `A_0=Q`, and `p_k=A_k/Q`. Substitution in (1) gives

```text
S(n) = Q(n)^2 Delta
     = (sum_i a_i A_i(n))(sum_j b_j A_j(n))
       - Q(n) sum_(i,j) a_i b_j A_(i+j)(n).                         (2)
```

Every expression here is a finite signed power sum `sum_b c_b b^n` with
positive integer bases. It is enough to store a dictionary `b -> c_b`:
addition adds coefficients and multiplication sends `(b,d)` to `b*d`.
Each factor `2^(n+1)-2^j` is exactly the dictionary `{2:2, 1:-2^j}`.
Consequently (2) specifies the entire expansion by integer operations,
including all cancellations; no fitting from numerical samples occurs.

**Tail lemma.** Let `B` be the largest surviving base with coefficient `c>0`,
let `b<B` be the next base, and let `C` be the sum of absolute coefficients
of all remaining terms. If `c B^N > C b^N`, then for every integer `n>=N`,

```text
S(n) >= c B^n - C b^n > 0.
```

Indeed, the ratio `(b/B)^n` decreases. This is a uniform proof after one
exact integer comparison, not extrapolation from finitely many dimensions.

Expanding (2) gives the following certificate. The verifier recomputes each
tuple and checks its strict tail inequality. For each row it separately
checks `S(n)>0` for every `3<=n<N`, using both exact rational moments and
the expanded integer numerator.

| Row | `B` | `c` | `b` | `C` | `N` |
|---|---:|---:|---:|---:|---:|
| 1 | 28672 | 128 | 20480 | 143872 | 21 |
| 2 | 21504 | 128 | 19456 | 419520 | 81 |
| 3 | 28672 | 256 | 21504 | 680640 | 28 |
| 4 | 16128 | 96 | 14592 | 2820224 | 103 |
| 5 | 21504 | 256 | 19456 | 3626656 | 96 |
| 6 | 21504 | 384 | 19456 | 6850144 | 98 |
| 7 | 28672 | 128 | 21504 | 3367488 | 36 |
| 8 | 28672 | 384 | 21504 | 4395776 | 33 |
| 9 | 16128 | 128 | 14592 | 2919872 | 101 |
| 10 | 21504 | 256 | 19456 | 3726336 | 96 |
| 11 | 28672 | 512 | 21504 | 5020608 | 32 |

There are **692 exact finite-prefix comparisons**, with no gap between each
prefix and its tail. The largest cutoff is `n=103` (`m=104`). This establishes
all eleven strict inequalities for every integer `m>=4`.

Finally, any increasing real function on a finite cube is a constant plus
a nonnegative linear combination of increasing-event indicators: use its
successive nontrivial superlevel sets. For a nonconstant function at least
one coefficient is positive. Bilinearity of covariance and the strict event
inequalities therefore give strict negativity for two nonconstant functions
on disjoint nonempty supports. Constants and empty supports give zero. QED.

## 4. Corroboration and a necessary sampling hypothesis

The finite proof component is author-checked, not proof-kernel verified.
[verify.py](verify.py) also checks all 39 labelled cases directly from the
16-atom law for `4<=m<=104`: **3,939 truth-table comparisons**, plus 33
tail probes and eight explicit rejection/domain controls. The truth-table
and rational evaluations use the cited moments, so they are separately
represented calculations, not independent validations of those counting laws.

[boundary.py](boundary.py) is a separately implemented calculation with no
spectra or moment formulas. It enumerates all **20,160** invertible `4x4`
binary matrices, explicitly forms each `G P_i G^-1`, and computes the three
principal determinants. Each specified atom of weight `0,1,2,3,4` occurs
`3480,3816,228,12,0` times respectively. The intersection counts for each
specified subset of sizes `1,2,3,4` are `4536,252,12,0`.
It checks all support placements: **174** nonconstant increasing-event pairs
have strictly negative covariance; **444** constant-involved pairs have zero.

The same checker restricts the header to the **1,344** matrices with first row
`[0,1,1,1]`. The pair `E_1` and `E_2 AND E_3` then has counts `432,4` and
joint count `2`, giving positive covariance
`(1344*2-432*4)/1344^2 = 960/1344^2`.
Thus arbitrary restricted header collections are genuinely outside the theorem.
A further control replaces `G^-1` by `G`; it changes both an explicit atom
and the full law. These controls remain active under optimized Python.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/corankone-four-negative-association --check-only
python3.12 -B scripts/research_package.py --package research/corankone-four-negative-association
```

The registered replay runs both files in normal and optimized isolated Python.
For a Git-free package directory, run `python3.12 -I -B verify.py` and
`python3.12 -I -B boundary.py`, and repeat with `-O`. Both are read-only.
The proof checker prints `PASS_CORANKONE_FOUR_NEGATIVE_ASSOCIATION`; the
boundary checker prints `PASS_GL4_FOUR_GUARD_BOUNDARY`.

## Scope, provenance and credit

Scientific base: fresh canonical main `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`,
priority revision 7. [Discussion #5086](https://github.com/CrocSwap/integer-mult-bounds/discussions/5086)
is the canonical claim/result. [TASK.json](TASK.json) records a changed scope
of `formal-interface-lemma`: a counting side result, with no Lean claim.

Credit **lee-phys** for the three-event theorem and explicit open question in
#5073, head `1aace155467e4a560bdb5b28f4f0fdc60a45c29d`; **Nick Petalas** for
#4227/#4261/#4275, the grouped comparison #4777, and #4599 (head
`19ca650c67ad2722790dc60c0bfd12989479b06a`). Retain Cinna Davis's BIT request
context, source527, commdata2338 and Jose Manuel's normalizer/closure lineage,
and Chris R / Clear1nsight's earlier counting context. New proof and integration:
**Krzysztof Wojt with substantial OpenAI Codex assistance**; bounded Luna agents
independently enumerated event types and constructed the literal GL4 check,
which the primary agent inspected and reran. No independent human review or
formal proof-kernel acceptance is claimed. Apache-2.0.

This is not a physical supplier or a multiplication-exponent improvement.
The result covers exactly four orthogonal binary kernel lines and a complete
uniform header. Five or more events, odd fields, nonorthogonal kernels and
conditioned/restricted header laws are not covered. Header production, selection,
emission, dispatch, dirty restoration, stock and whole-caller costs remain
unpriced; unknown costs are not zero. No selected-frontier change, selected
scientific cold replay, native/Lean/Docker build or all-size admission is claimed.
The selected-baseline sparse-input diagnostic reported 503 omitted files;
the full selected source-binding orientation was not run in this scoped checkout.

## Open next questions

1. Does negative association persist for five orthogonal binary kernel lines?
   This would control larger shared-header groupings. First derive the `3+2`
   increasing-event comparisons from the existing general character law and
   test their signs; the four-event table and its tail bounds do not settle
   them. No additional census or follow-up is reserved here.
2. Can a concrete paid caller realize the complete uniform-header premise and
   use this dependence bound? Pin its sampling/conditioning rule first, since
   the fixed-row counterexample excludes a free transfer to restricted headers.
   Then price selection, emission, dispatch and restoration against an actual
   consumer. That physical construction and its complete bill are absent.
