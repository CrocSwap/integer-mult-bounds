# Masked rank-8 complex decoders are locally rigid on every frame-pair puncture (no new κ)

**Status: scoped structural result (an exact infinitesimal certificate) plus a seeded finite sample.
No κ claim and no new supplier.** The selected κ = 0.001672660197076918 and every existing file are
unchanged.

## Task card

- **Card.** `complex-masked-decoder` (complex-mechanisms track), chooser nonce
  `f98900d1d6bdb1d91a0247b80be5acee`, scope key `7acfe4d9cac04f7ba4cb`. Scope **refined**: before
  synthesizing a masked decoder, test whether masking can deform the cheapest known decoders at all.
- **Base and predecessors.** Base `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`.
  https://github.com/CrocSwap/integer-mult-bounds/pull/717 (open, head `4a97676`) defines the masked
  (E-graph) model; https://github.com/CrocSwap/integer-mult-bounds/pull/968 (merged,
  `research/complex-frame-pair-decoders`) gives the frame-pair decoders and the all-pairs floor;
  https://github.com/CrocSwap/integer-mult-bounds/pull/1212 (open, head `072ae2f`) proves global rank-8
  rigidity on P112 and P120 and lists P104 as numerical evidence only.
- **Changed assumption.** The eight-term floor assumes exactness on all live pairs. Here only the
  E-graph entries are fixed (diagonal and orthogonal pairs); odd entries are free, because cost-0 terms
  can repair them.
- **Object and question.** Real K on the live lines with K_ii = 4, K_ij = 0 for orthogonal live pairs and
  rank K ≤ 8. Near K0 = 2G, is the solution set only the diagonal-torus orbit D K0 D⁻¹, on every
  frame-pair puncture P104 = P120 − F0 − F1?
- **Domain.** P120, P112 and all 1260 frames F1 disjoint from a fixed F0, plus 8 seeded random
  punctures at each p = 24, 32, ..., 80. Budget 60 minutes; local only.
- **Optimistic payoff.** A masked deformation with smaller supports would lower the copy charge below
  the 7/13 ratio, about 2.8% of b per copy unit in the earlier knob calculus. The certificate shows that
  no such deformation exists near the normal form, so the local payoff is zero.
- **Claim.** https://github.com/CrocSwap/integer-mult-bounds/discussions/1275

## Result

**Local rigidity.** Let L be the live lines of P120, of P112, or of any P104 frame-pair puncture, and let
V be the set of real L × L matrices K with rank K ≤ 8, K_ii = 4 and K_ij = 0 for orthogonal live pairs.
Then the tangent space of V at K0 = 2G is the tangent space of the torus orbit {D K0 D⁻¹} (dimension
v − 1). Because that orbit lies in V, V coincides with the orbit on a neighbourhood of K0. The
statement holds over C as well, since every rank used below is a rank of a rational matrix.

**Decoder consequence.** A live frame F has K[F, F] = 4I under the mask, so every K in V has rank exactly
8. An eight-costly-term masked decoder whose costly part is close enough to 2G therefore equals
D(2G)D⁻¹. Its rank-8 factorization has the all-pairs normal form supports of
https://github.com/CrocSwap/integer-mult-bounds/pull/968, so that package's floor applies: cost at least
56 on P104 and copy ratio at least 7/13 for punctures of at most 24 lines. Masking cannot locally move
the frame-pair decoders.

**Certificate (exact).** Rank-8 matrices near K0 = L Lᵀ/2 (doubled root coordinates) have tangent
vectors Δ = L Mᵀ + N Lᵀ. For each live line i, the lines E(i) = {i} ∪ {live j orthogonal to i} span
Q⁸, so the masked equations of row i determine N_i from M; what remains is a linear system in M alone,
with 8v unknowns.

- *Upper bound.* Over F_p with p = 2³¹ − 1 that system has rank 7v − 63. Rank over F_p never exceeds rank
  over Q, so its rational kernel has dimension at most v + 63.
- *Lower bound.* The gauge vectors M = L S (64) and torus vectors M = −T L/2 (one per line) satisfy the
  equations (Δ = 0 and Δ = [T, K0] respectively, which vanish on the mask), and their span has rank
  64 + v − 1 over F_p, hence over Q.
- The two bounds meet. Removing the 64 gauge directions, which give Δ = 0, leaves exactly the v − 1 torus
  directions.

**Coverage of all 1260 frame pairs.** Breadth-first search with the 120 root reflections reaches all
2025 frames, giving explicit words w_F with w_F(F0) = F. Schreier elements w_{sF}⁻¹ s w_F fix F0 and
preserve |G|; 66 of them merge the 1260 frames disjoint from F0 into three classes of sizes 896, 336
and 28. These are the three relative positions found in
https://github.com/CrocSwap/integer-mult-bounds/pull/968. The masked system is invariant under such
elements up to a sign conjugation, so one certified representative covers its class. For the three
representatives every equation is inserted, and the rank is exactly 665 = 7 · 104 − 63.

**Sample and control.**

- 64 of 64 seeded random punctures with 24 to 80 lines pass the same exact certificate. This is a finite
  sample, not a theorem about every puncture.
- The decomposable live set D4 ⊕ D4 (24 lines in two mutually orthogonal blocks) is rejected, with rank
  64 against a target of 105, and a known span of 86 because its torus splits into two components.
- The equations of the known kernel are rechecked on random combinations for every certified set.
- Corroboration: the P112 tangent rigidity recorded as checked in
  https://github.com/CrocSwap/integer-mult-bounds/pull/717 (D1) is reproduced here by a separate exact
  method.

## Reproduce

From the repository root, Python 3.10+ and the standard library (about 70 s):

```sh
python3 -I -B research/complex-p104-masked-local-rigidity/verify.py
python3 scripts/research_package.py --package research/complex-p104-masked-local-rigidity --check-only
```

Expected final line:

```text
PASS_P104_MASKED_LOCAL_RIGIDITY: P120, P112 and all 1260 frame-pair punctures (3 classes) infinitesimally rigid at 2G; D4+D4 control rejected; seeded sample p=24..80 rigid 64/64; local only, no new kappa
```

## Scope and remaining obligations

- **Local only.** Components of V away from the torus orbit are not excluded on P104. The global
  statement is proved for P112 and P120 in https://github.com/CrocSwap/integer-mult-bounds/pull/1212,
  not here.
- **Not covered.** Nine or more costly terms (rank-9 costly parts); punctures other than the frame pairs
  except the seeded sample; masked identities on other entry sets; physical copy trees, frames,
  restoration and hosting.
- **Inherited.** The decoder consequence uses the floor theorem and cited flat classification of
  https://github.com/CrocSwap/integer-mult-bounds/pull/968. All all-size/compiler, realization, hosting,
  precision/tape and analytic obligations of the selected record remain. Finite checks are not a formal
  proof of integer multiplication, and the argument has not had independent human review.

## Open next questions

1. **Global rigidity on P104.** An off-orbit component could have smaller supports and beat 7/13. First
   step: pivot on a live frame F (the mask forces K[F, F] = 4I, so K = K[:, F] K[F, :]/4) and solve the
   bilinear system for each of the three classes. Blocked by a written case analysis comparable to the
   P112/P120 proof of https://github.com/CrocSwap/integer-mult-bounds/pull/1212.
2. **Nine masked costly terms on P104.** This is the mixed-β problem of
   https://github.com/CrocSwap/integer-mult-bounds/pull/717 at the ratio-optimal puncture; rank-8
   rigidity does not constrain rank-9 costly parts. First step: the same tangent computation at rank 9
   for one fixed ninth support on one class. Blocked by the choice of a support alphabet.

Structured versions are in [TASK.json](TASK.json).

## Credit

- DreamingOfClouds: the masked (E-graph) decoder model, cost-0 repair terms and the P112 tangent
  rigidity in https://github.com/CrocSwap/integer-mult-bounds/pull/717.
- themilkman216: frame-pair decoders, the 7/13 floor and the three relative positions in
  https://github.com/CrocSwap/integer-mult-bounds/pull/968.
- burntout76: global rank-8 rigidity on P112/P120 and the P104 question in
  https://github.com/CrocSwap/integer-mult-bounds/pull/1212.
- Related masked P112 work: https://github.com/CrocSwap/integer-mult-bounds/pull/1213,
  https://github.com/CrocSwap/integer-mult-bounds/pull/1226,
  https://github.com/CrocSwap/integer-mult-bounds/pull/1236 and
  https://github.com/CrocSwap/integer-mult-bounds/discussions/1267 concern a different puncture;
  https://github.com/CrocSwap/integer-mult-bounds/pull/1071 bounds physical delivery for the frame-pair
  centres, a separate obligation.
- Prepared by Navinor with help from opencode. Apache-2.0.
