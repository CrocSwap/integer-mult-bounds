# Independent check of #4623: monotone extension, copied-input decoder, idle-free controller (no new κ)

**No new κ and no supplier admission.** This is a scoped independent check of
three parts of dillona's [PR #4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623)
(head `fd5d3be12b9d6ee92c8fa089d95bd529c3236563`; canonical discussion
[#4611](https://github.com/CrocSwap/integer-mult-bounds/discussions/4611)) that
pinterbanget's [#4625](https://github.com/CrocSwap/integer-mult-bounds/pull/4625)
did not replay. Nothing is imported from #4623 or #4625. Card: `independent-moment`.

## Scope

1. **(A) Monotone extension** (BUDGET.md): a negative bound at C=.006 (complex) and C=.007 (BIT)
   implies negativity for every larger saving C ≤ 1, for every positive integer p.
2. **(B) Copied-input X decoder** (DECODER.md): the exact correction identity, the forced
   matrices and rank p−1, and the all-concave-moment cumulative certificate.
3. **(T) Sanity**: deleting every whole IDLE call from the source chronology and thinning
   stages 2,4,…,2p−2 gives exactly the stated triangular `Q^-1 U` / `Q V` controller, with
   a degree-(p−1) diagonal border.

## Result: agreement on all three, plus a sharpened ceiling

**(A) holds.** Write h(t)=Σ_r s_r r^t (s = local helpers − local paid) and
J_p(t) = (p+2)h(t) − v(p−1) + 2vp(1+b+2b/p)^t (the Jensen envelope of the 2vp main outputs
whose determinant-forced total rank is 2v[p+b(p+2)]; valid as x^t is concave for t∈[0,1]).
*Lemma.* If σ>0 and every summand c·r^t of J_p satisfies c·(r−σ) ≥ 0, then
d/dt[c(r/σ)^t] = c·ln(r/σ)(r/σ)^t ≥ 0, so J_p(t)/σ^t is nondecreasing on [0,1];
hence J_p(t₀)<0 implies J_p(t)<0 for all t≤t₀, i.e. every C ≥ 1−t₀.
The hypothesis is p-independent: the signed local profile is
complex {1:−2237, 2:−388, 3:−494, 4:−119, 5:−36, 7:+7, 8:+39, 9:+326} and
BIT {1:−1323, 2:−1342, 3:−79, 4:−44, 5:−102, 6:−11, 7:−19, 8:+439}; coefficients (p+2)s_r keep
their sign; the thin queries are a negative rank-1 term; the main base 1+b+2b/p > 1+b.
So any σ in (5,7] (complex) or (7,8] (BIT) works; #4623's σ=6 and 15/2 are valid.
Combined with J_p(t₀) ≤ pA(t₀)+B_J(t₀) (tangent at 1+b), and A, B_J < 0 at the cutoffs,
the exclusion holds for all p ≥ 1 and all C ∈ [cutoff, 1]. My certified intervals
(exp/log series with explicit remainder bounds, outward rounding to 2⁻¹²⁰) reproduce
A = −2.6366097978, B_J = −132.6282065738 (complex, .006) and A = −3.5731057049,
B_J = −133.1717283853 (BIT, .007), widths < 2·10⁻²⁹.

**Sharpening (new, scoped).** The cutoffs are not tight for this model. Certified:
A<0 and B_J<0 already at **C = .005687 (complex)** and **C = .006512 (BIT)**, so the same
argument excludes C ≥ .005687 / C ≥ .006512 for every p. Conversely A>0 at C=.005685 /
.006510; since J_p(t)/p → A(t) as p→∞, the optimistic J_p is positive for large p there,
so this relaxation cannot exclude smaller savings. The model's sharp all-p threshold is in
(.005685, .005687) complex and (.006510, .006512) BIT. This is a ceiling, not a supplier.

**(B) holds in the stated model.** Using the emitted idle-free X block,
z = (I+J)X' − Q⁻¹Jx equals Q⁻¹Dx exactly (p=2..7). Solving M(I−S)=I, N=−MS exactly gives
M=I+J, N=−J, rank p−1 (p=2..7). The cumulative rank sums A_r(p) of (paid − target), with
p−1 fresh rank-one correction queries per port, are affine in p and reproduce DECODER.md's
base/slope table for every listed threshold (e.g. complex r=1: 9172+2461(p−2); r=17: 32+64(p−2);
BIT r=15: 30+63(p−2)); all bases and slopes are positive, so Abel summation with
f(r)=r^(t−1) gives paid > target at every t∈(0,1] and p≥2. Direct certified moment
evaluation agrees at p∈{2,16}, t∈{.01,.5,1}.

**(T) holds.** My hand replay of the source chronology (F_s = D_s S_y(Q⁻¹), B_s = D_s S_x(−Q),
bridges, reverse bridges, signed swap; IDLEs deleted; thin stages without D_s) equals both
the closed form U, V of DISCOVERY.md and the literal pinned source emitter
(`complex_controller_factor.controller(p, 0)` with thin exponents zeroed), coefficient by
coefficient, for p=1..7. Weights w(X_j)=j, w(Y_j)=p−1−j give border degree set exactly
{0,…,p−1}, all diagonal entries are unit monomials (so the limit is the full-rank diagonal
monomial map), det = Π_{thick s} D_s² (p+2 thick stages), and A(1)=I.

## Controls (all rejected as required)

Tampered input bytes; flipped backward-shear sign; no thinning; reversed weights (negative
degrees); a net-negative rank-9 paid term (breaks the separator lemma); non-certification at
complex C=.005 and BIT C=.006 (checker is not vacuous); decoder without fresh queries (some
cumulative sum negative); decoder without the raw-input term (identity fails).

## Reproduce

```sh
python3.12 scripts/research_package.py --package research/pr4623-monotone-decoder-check --check-only
python3.12 scripts/research_package.py --package research/pr4623-monotone-decoder-check
python3.12 -B research/pr4623-monotone-decoder-check/verify.py
```

Standard library only; about 2 s.

## NOT covered

- The precision/approximation lemma (EXACTIFICATION.md) and the H₀(f) budget.
- The repeated whole-controller (K≥2) argument; the determinant/Laurent rank-mass invariant
  itself (taken as stated; #4625 checked the p16 masses).
- Whether the frozen #4470/BIT inventories and the "thin stage = unscaled shear" modelling
  are the right physical contract; any BIT scalar-extension or native implementation.
- Decoder lower bound beyond the stated model (shared/reused internal queries, cross-port or
  operator-valued adapters). Controller sanity was checked only for p=1..7, not symbolically.
- #4625 already performed a sign check of the separator premise; this package adds the
  derivation, a different certified enclosure, the maximal separator ranges and the sharpening.

## Open next questions

- **Does the sharpened ceiling (C* ≈ .005686 complex / .006511 BIT) bind the actual diagonal
  family as p→∞?** It matters because it is the true limit of this idle-free interface under the
  frozen inventories. First step: certify the explicit-diagonal roots pA+B for p up to 2¹⁰ and show
  they increase to C*. Blocked by: nothing.
- **Can the p−1 paid thin queries be reused as the decoder's Q⁻¹x_(i+1) values?** It is the only
  route #4623 leaves open for exact X correction. First step: a chronological ownership/restoration
  check at p=2. Blocked by: an explicit retained-query contract in the source interface.

## Credit

dillona (Dillon) for #4623 and its proofs; pinterbanget for #4625; Matarener for #4602's idle-bill
diagnosis; Cinna Davis (1337isnot1337) for #4440/#4470; zxv and the native/BIT controller lineage
for the source emitter and inventories. Prepared by lm1909 with Claude Code (Claude Opus 5.5)
assistance. No independent human review. Apache-2.0.
