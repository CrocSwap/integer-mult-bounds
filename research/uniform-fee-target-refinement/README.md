# Exact uniform-fee optimum for independent target refinement

This package was produced by Nick Petalas.

**Claim type: scoped written proof with exact finite corroboration.** This is an
accounting theorem about one replacement step in the mixed-target invoice. It is
not a construction, a native or caller proof, a supplier admission or a κ change.
The selected record stays κ = 781451/250000000.

## Setting

A productive target of positive integer rank R is replaced by k ≥ 1 independent
targets of positive integer ranks r_1, …, r_k with Σ r_i = R. Each piece after
the first carries the same paid fee c ≥ 0, so the credit change is

    Δ(r) = Σ φ(r_i) − (k−1)c − φ(R),

for a rank tariff φ on {0, …, R} that is nondecreasing, concave and has φ(0)=0.
This covers the invoice tariff φ(r) = r^t with t = 1−C, 0 < t < 1, and the cap
tariffs min(r, K) of the concave-order comparator. Write
S(k) = (R mod k)·φ(⌈R/k⌉) + (k − R mod k)·φ(⌊R/k⌋) for the balanced k-split.

## Theorem

1. For each k, the balanced partition maximizes Σ φ(r_i) among all k-part
   partitions of R.
2. S(k) is concave in k on 1 ≤ k ≤ R.
3. The best refinement has credit max_k S(k) − (k−1)c. It is attained by the
   balanced partition with k* = the least k such that S(k+1) − S(k) ≤ c (or
   k* = R if no such k exists).
4. **Halving test.** Some refinement strictly improves the target credit if and
   only if φ(⌊R/2⌋) + φ(⌈R/2⌉) − φ(R) > c.

## Proof

Let ψ be the piecewise-linear interpolation of φ at the integers. It is concave
on [0, R] with ψ(0) = 0, and agrees with φ at integers.

(1) A balanced vector is majorized by every other integer vector with the same
length and sum. Karamata's inequality for the concave φ gives
Σ φ(r_i) ≤ S(k).

(2) Write R = qk + s with 0 ≤ s < k. Since q ≤ R/k ≤ q+1,

    k·ψ(R/k) = kφ(q) + (R − kq)(φ(q+1) − φ(q)) = (k−s)φ(q) + sφ(q+1) = S(k).

The perspective g(k) = k·ψ(R/k) of a concave function is concave for k > 0.
Restricting to integers keeps the second differences nonpositive.

(3) By (1), the optimum over all partitions with k pieces is S(k) − (k−1)c.
This function of k is concave by (2), because the fee term is linear. A
concave sequence attains its maximum at the first k where its forward
difference S(k+1) − S(k) − c becomes nonpositive.

(4) Refinement improves the credit iff max over k ≥ 2 of S(k) − (k−1)c exceeds
S(1) = φ(R). By concavity this happens iff the first difference S(2) − S(1) − c
is positive. S(2) is the expression in the halving test. ∎

The hypotheses are needed. The verifier includes a nondecreasing non-concave
tariff (0,0,1,1,1,1,2) on R = 6 with fee 0. Halving gains nothing, yet the
balanced three-way split gains 1. A convex tariff also makes an unbalanced
pair beat the balanced pair.

## Consequence at the selected exponent

Take φ(r) = r^t with t = 1 − 781451/250000000 and the fee of one extra paid
rank-q job per piece, c = q^t. The halving gain becomes positive at:

| Fee job rank q | Least target rank R at which any refinement pays |
|---:|---:|
| 1 | 470 |
| 2 | 940 |
| 4 | 1880 |
| 8 | 3760 |

The verifier checks that the halving gain is at most c for every R below each
threshold and above c for every R from the threshold up to 7520. The gap is
always at least 10^-40, evaluated with 60-digit correctly rounded `Decimal`
exponentials and logarithms. For even R = 2m the test reads
m^t(2 − 2^t) > c, so the threshold is about c/(2 − 2^t) ≈ c/(2C ln 2) pieces
of size two, which grows like 1/C.

These numbers apply the selected value as the tariff exponent for
illustration. They are not a claim about the actual binding supplier's
normalization, any actual helper target, or the legality of any split.
Independence, chronological availability, native delivery, restoration,
and caller costs remain separate obligations. A nonuniform fee menu needs the
existing target-partition optimizer or a separate argument.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B research/uniform-fee-target-refinement/verify.py
python3 -O -B research/uniform-fee-target-refinement/verify.py
```

Expected output, about two seconds:

```
PASS_UNIFORM_FEE_TARGET_REFINEMENT exact_checks=10392 controls=2 thresholds=q1:R>=470 q2:R>=940 q4:R>=1880 q8:R>=3760
```

Part A enumerates every integer partition of every R ≤ 22 under eight exact
rational concave tariffs (linear, harmonic, a concave quadratic and five caps)
and 38 distinct rational fees. It checks items 1–4 against the brute-force optimum.
Part B certifies the threshold table. The finite checks corroborate the proof;
the all-R statement rests on the written argument.

## Open next questions

- **Rank-dependent fees.** If the fee for a piece depends on its rank (an
  adapter whose cost grows with the piece), is the optimum still balanced, and
  does a halving test survive? First step: fees of the form c + d·φ(r_i).
- **Actual helper targets.** Which productive targets in the selected P104
  ledger exceed the q = 1 threshold of 470, and what is the cheapest legal
  per-piece fee for them? Blocked by the selected-invoice exporter, which does
  not yet support the PR6030 source.
- **Joint refinement.** When several targets share one fee (one adapter that
  serves many splits), the fee is no longer additive per piece. Determine the
  joint optimum for a shared fixed fee plus a per-piece fee.

## Credit

The theorem, proof, verifier and threshold table were produced by Nick Petalas.
The signed mixed-target invoice model, the concave-order comparator and the
target-partition optimizer that motivated the uniform-fee question are by zxv
and Ali Romman, as credited in `docs/research/recursive-invoice-preflight.md`
and `docs/research/target-partition-optimization.md`. Karamata's inequality and
the concavity of perspective functions are classical. Apache-2.0.
