# A sharp uniform bound for all triangular parity macro cuts

**Scoped theorem:** every prefix, suffix, inverse prefix and inverse suffix
of the exact lower-triangular parity compiler, at complete-shear boundaries,
has infinity norm at most `1/(1−η)` when the symbol's tail `l1` is at most
`η < 1`. Thus **2 suffices at `η ≤ 1/2`, independently of depth**, and no
smaller constant bounds all four kinds of cuts uniformly in dyadic dimension.
No new κ, full gate-level stability theorem or supplier admission is claimed.

The source [SHALLOW-TOEPLITZ.md §3 and §6](../unconditional-batched-crt/vendor/SHALLOW-TOEPLITZ.md)
already gives polynomial circuit bounds. This result sharpens the *composed
macro-cut* bound to a constant: it controls an unfinished child multiplied by
its ancestor shear, not just each descendant matrix separately. It covers the
source's parallel child execution and every order-preserving interleaving of
the disjoint child macros. Serial even-first execution is only one such order.

The actual caller is [GAUSSIAN.md's triangular compiler](../unconditional-batched-crt/GAUSSIAN.md),
which supplies part of the conditional error ledger in
[one-factor-of-t](../one-factor-of-t/README.md). Internal dirty-shear gates,
generator normalization and the completed Gaussian stage remain separate.

## Statement and proof

Let `N=2^h`, `f(0)=1`, and `Σ_{j=1}^{N−1}|f_j| ≤ η < 1`, with real or
complex coefficients. Write `T=T_N(f)` for multiplication by `f` modulo `z^N`.
At each node write `f(z)=e(z²)+z o(z²)` and, modulo `z^(N/2)`, set

```text
k = o/e,       s = e − z o²/e,
U = [I, T(zk); 0, I],       L = [I, 0; T(k), I],
T = L diag(E,S) U,           E=T(e), S=T(s).
```

The matrices in this identity use the even/odd coordinate order. Simultaneous
row/column permutation preserves the infinity norm. Execute `U`, the two
recursive child programs on disjoint coordinates, then `L`. A macro is a
whole such shear, not one gate of its FFT implementation. Reordering coordinates
also has norm one and does not change the argument.

For any cut, including either endpoint, let `P` be the executed prefix and
`Q` the remaining suffix, so `T=QP`. We prove simultaneously

```text
max(‖P‖∞, ‖P⁻¹‖∞, ‖Q‖∞, ‖Q⁻¹‖∞) ≤ 1/(1−η).
```

The one-dimensional leaf is the identity. For the induction step, put

```text
a = ‖e−1‖₁,  b = ‖o‖₁,  c = 1−a,  d = c²−b².
```

Here coefficient `l1` is submultiplicative, truncation cannot increase it,
and `a+b ≤ η < 1`, hence `c>b≥0` and `d>0`. Neumann expansion gives

```text
‖k‖₁ ≤ b/c,
‖s−1‖₁ ≤ a+b²/c ≤ a+b ≤ η.
```

These shared-budget estimates are the one-level mechanism of James Reed's
[#4699](https://github.com/CrocSwap/integer-mult-bounds/pull/4699); they are
rederived here so the proof does not depend on unmerged executable code.
The induction hypothesis bounds **each of the four child cut operators** by

```text
X = 1/c      for E,         Y = c/d      for S,
```

since `1−(a+b²/c)=d/c`. During the child phase, an arbitrary interleaving
is some pair of legal child cuts. If their prefixes are `P_e,P_s` and
suffixes are `Q_e,Q_s`, then exactly

```text
P    = diag(P_e,P_s) U,         P⁻¹ = U⁻¹ diag(P_e⁻¹,P_s⁻¹),
Q    = L diag(Q_e,Q_s),         Q⁻¹ = diag(Q_e⁻¹,Q_s⁻¹) L⁻¹.
```

For a block row, add its block norms. The nontrivial block-row bounds and
their nonnegative gaps below `B=1/(c−b)` are:

| Operator | Block-row upper bound | `B` minus that upper bound |
|---|---|---|
| `P` | `(c+b)/c²` | `b²/[c²(c−b)]` |
| `P⁻¹` | `1/c+b/d` | `b²/(c d)` |
| `Q` | `b/c²+c/d` | `b³/(c² d)` |
| `Q⁻¹` | `(c+b)/d` | `0` |

Every other block row is bounded by `X` or `Y`, both at most `B`.
Thus all four norms are at most `B=1/(1−a−b) ≤ 1/(1−η)`.
The cuts just after `U` and just before `L` are included by taking identity
or completed child cuts. At the two outer endpoints use
`‖T‖∞ ≤ 1+η ≤ 1/(1−η)` and the Neumann bound
`‖T⁻¹‖∞ ≤ 1/(1−η)`. This completes induction for every dyadic `N` and every
legal child interleaving, including simultaneous layers of disjoint macros.

## Sharpness and the remaining three-halves question

For `f(z)=1−ηz`, the last row of `T_N(f)⁻¹` has absolute sum

```text
1+η+⋯+η^(N−1) = (1−η^N)/(1−η).
```

As dyadic `N` grows this tends to `1/(1−η)`. This inverse is an inverse
prefix at the final cut (and an inverse suffix at the initial cut).
Consequently the common four-operator constant is optimal. This is not a
claim that every one of the four kinds individually needs that constant.

Even a **forward suffix** can exceed `3/2`: take `N=4` and
`f=(1,1/2,0,0)`. Immediately after the root right shear `U`, the suffix is
`L diag(I,I−Z/4)`. In original coordinate order its last row is
`(0,−1/4,1/2,1)`, of absolute sum **7/4**. Thus a one-level factor cap of
`3/2` cannot be assigned to all composed cuts.

Whether **forward prefixes alone** always satisfy `1+η` remains open here.
This refines the initial investigation rather than claiming its sharp
forward-prefix question was solved. #4701, #4702, #4704, #4705 and #4706 give
individual `N=8` forward-prefix examples; none is used as a universal proof.

## Exact controls and reproduction

```sh
python3 -B scripts/research_package.py --package research/triangular-parity-uniform-prefix --check-only
python3.12 -B scripts/research_package.py --package research/triangular-parity-uniform-prefix
python3.12 -O -B research/triangular-parity-uniform-prefix/verify.py
```

The standard-library checker independently builds the literal parity matrices,
checks their endpoint identity, enumerates **every pair of child cut matrices**
for seven rational fixtures at `N=1,2,4,8,16`, and checks all four operators at
116 distinct fixture cuts. Signed dense tails, the zero tail, `η=3/4`, and the
half-budget pure-odd family are included. It checks the exact `7/4` suffix row
and geometric inverse formula. Wrong Schur sign, missing left shear and
reversed macro order must change the endpoint; a tail outside the hypothesis
exceeds 2. Runtime is a few seconds. Explicit failures remain active under `-O`.
These finite controls test implementation and failure modes; the induction above,
not the finite fixtures, supplies the universal claim.

The proof was separately reviewed by a second Codex agent, which also used an
independent sparse row-action checker for three child interleaving schedules.
This is additional AI checking, not independent human or maintainer acceptance.
Source blobs and SHA256 hashes are in [SOURCES.json](SOURCES.json); replay inputs
are in [VERIFY.json](VERIFY.json). No external PR checkout is needed.

## Open next questions

1. **Is `1+η` the sharp forward-prefix bound?** It would improve the one-sided
   macro error budget. First derive a row-level invariant retaining correlation
   between `P_e` and `P_e E⁻¹`; the norm-product induction above loses that
   correlation. No exact forward counterexample or proof is supplied here.
2. **What happens inside one actual dirty-shear circuit?** The Gaussian caller
   needs gate-level precision, not just macro boundaries. Bind the §2 FFT/twist
   implementation and its inverse to the four macro envelopes, then account for
   gate rounding. The local coefficient norms, generator compiler, row gap and
   `p^100` normalization must still be justified; this package does not price them.

## Provenance and credit

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7,
selected conditional κ=`60403/20000000`. Canonical investigation:
[Discussion #4715](https://github.com/CrocSwap/integer-mult-bounds/discussions/4715).
At entry, overlap coverage comprised 480 open PRs (2026-10-22T17:40:03Z),
3632 Discussion records (17:41:08Z), and all 5860 local notes. Coverage omits
arbitrary diffs and is not proof of novelty. Submission freshness is in TASK.json.

- Vlado Vojdanovski/#1673 supplies the shallow Toeplitz compiler; Cinna Davis's
  #4100 retains it at the later Gaussian caller, preserving its source lineage.
- Ryanson Jonathan's `one-factor-of-t` identifies the error-ledger obligation;
  it credits unpaidmoon's #4371 and the earlier #4320/#4311 audits.
- Jose Manuel (`jmbarrancoml`), #4198 at
  `e457d5e912a27307d725827aeca7198169320b84`, supplies exact rational Stein
  generators and a separate polynomial generator-macro bound; its triangular
  child execution is explicitly outside that result. This is complementary.
- James Reed's one-level result is #4699 at
  `67c70cc7d190fc4f728292d8f384c13f26f90385`; the finite series is #4701 at
  `f6769f4542584057423935e7070ccf3c71d954e9`, #4702 at
  `1767e47008695dd05ec16d67e3dfe8ceb25afcf3`, #4704 at
  `93d3b4416a2be3bdfc684481e4e3d01670c3a534`, #4705 at
  `3b71da338aeae3008244a132fc7dccf52800cbd8`, and #4706 at
  `adb541f871698ed45d9d36d02617b6b9760f2b3e`.

Prepared for Brian with substantial OpenAI Codex assistance. Apache-2.0.
