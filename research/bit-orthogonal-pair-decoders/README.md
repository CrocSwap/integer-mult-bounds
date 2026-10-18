# Bit-side orthogonal-pair decoders: pairing cost 54 on 102 ports and a 9/17 floor (no new κ)

**Status: research note with an exact decoder construction and a scoped lower bound. No κ claim and no
new supplier.** The selected κ = 0.001661960547713947 (PR942, T37) and every existing file are unchanged.

## What this establishes

The bit unit's copy charge is 63 on 111 ports (x = 63/111). PR757 and PR761 prove that 63 is optimal
for the shipped P111 puncture in the label-decoder model priced by PR446 Theorem C (rational pairing
rank). PR620 searched deeper punctures only under star pricing, and PR595 lists a bit unit with
x = 54/102 as one that "no word realises". This package works in the same Theorem C model on other
punctures.

1. **Mechanism.** A term (λ_a, λ_b) whose reader functional is the label of punctured line a and whose
   source functional is the label of punctured line b costs 6 when a ⊥ b, and 7 when a = b or
   ⟨a, b⟩ = ±1. Its reader lines span a^⊥ and its source lines span b^⊥, and the pairing between those
   hyperplanes has rank 7 − [a ⊥ b]. In F2 terms, the labels must form dual bases: B0[a_j, b_k] = δ_jk,
   which means a_j ⊥ b_j and ⟨a_j, b_k⟩ = ±1 for j ≠ k.
2. **Construction.** Nine such pairs exist (`WITNESS.json`). Puncturing their 18 lines gives an exact
   decoder of cost **54 on 102 ports, x = 9/17 = 0.5294**, below 63/111 = 0.5676 and below the complex
   frame-pair ratio 7/13 of PR968. The decoder identity is checked on all 102 × 102 live pairs.
3. **Floor (finite census plus written proof).** For every puncture of at most 25 lines and every label
   decoder with any number of terms, cst/v ≥ 9/17. Equality holds only for p = 18 with nine
   orthogonal punctured pairs. Nine-term decoders satisfy cst ≥ max(72 − p, 54), and this is attained
   at every p ≤ 25. The proof uses three thresholds: a reader span drops to a hyperplane with 1 puncture
   (its own root) or 14 (a D7 normal), and to rank 6 only with 26.
4. **The selected bit supplier.** Keeping the nine reader functionals fixed, exactly one source dual
   is a root label. Puncturing it gives **P110 with cost 62** (8 × 7 + 6). The necessary capacity
   inequality is 439 ≤ 440 at v = 110, not a verified owner map. Other reader bases on the same
   puncture can contain multiple cost-6 terms: a checked two-pair completion costs 68 overall on P111,
   so it does not improve the cost. At v = 102 the fixed R439 inventory exceeds 408 slots.
5. **Favorable pricing.** With the engines pinned by the selected record:
   - lowering the copy children 7 → 6 on all 288 calls is worth +2.8017% c per unit and +25.2108% c for
     nine units, with ports fixed;
   - PR717 records −2.13% to −2.16% c per deleted port (not reproduced here), so one pair on the shipped
     puncture is worth roughly +0.6% c;
   - κ is complex-bound, so a bit-only gain leaves it unchanged;
   - PR968's P104 complex budget is capped by PR589 at κ = 0.001730427469823602. Lifted above that cap,
     the same budget gives **κ = 0.001753391564497665** (+5.50%), which requires the bit c to rise by at
     least **1.3294%**. One shipped pair falls short of that in this estimate.

## Reproduce

From the repository root, with Python 3.10+ and the standard library only (assertions enabled; the
verifier refuses `-O` because the pinned engines signal rejection with `assert`):

```sh
python3 -I -B research/bit-orthogonal-pair-decoders/verify.py
python3 -I -B research/bit-orthogonal-pair-decoders/independent_check.py
python3 -I -B research/bit-orthogonal-pair-decoders/test_package.py
```

Expected final lines (about 3 s, 2 s and 15 s):

```text
PASS_BIT_ORTHOGONAL_PAIR_DECODERS: code 1+255z^56+255z^64+z^120; thresholds 1/14/theta6=26; witness P102 cst 54 (9/17); chain p=0..25; shipped P111 -> P110 cst 62 (1 dual root, wall 440>=439); copy knob 9 units 25.21084% c; P104 uncapped kappa 0.001753391564497665; controls 6; no new kappa
PASS_BIT_PAIR_INDEPENDENT: membership roots, basis-coordinate functionals, Bareiss ranks; chain p=0..25; thresholds 1/14/26; shipped P110 cst 62
PASS_PACKAGE_TESTS 8
```

`verify.py --out NEW.json` writes the receipt; `RESULTS.json` is that receipt, and the package test
checks that it regenerates byte for byte.

## What the checks cover

| section | content |
|---|---|
| A | 120 lines; B0 = (1 + G) mod 2 has F2 rank 9; reader code 1 + 255z^56 + 255z^64 + z^120; root functionals; all 120 reflections preserve the code |
| B | 8 hyperplane types × 511 functionals; all 120 root hyperplanes directly; all 1080 D7 directions (unique 14-line minimizer, next ≥ 34, pairwise unions ≥ 21); 28 standard rank-6 subspaces (θ6 = 26) |
| C | for one root and all 119 partners: cost 6 (63 orthogonal), 7 (56 odd), 7 (self) |
| D | the witness: F2 duality, entrywise decoder identity on 102 live lines, spans and costs |
| E | explicit decoders for p = 0..25 with cst = max(72 − p, 54) |
| F | the integer inequalities of the ratio theorem and the comparisons with 63/111 and 7/13 |
| G | the PR589 word (pinned file and content hashes): 44 orthogonal ordered pairs, one dual root with readers fixed, P111 cost 63, P110 cost 62, necessary capacity screen; a changed-reader two-pair control costing 68/67 |
| H | pricing pins; PR589 c reproduced exactly; copy knob with two moment engines; bit-only κ unchanged; PR968 P104 capped and uncapped |
| I | controls: swapped partners, a restored partner (cost 55), an odd partner, θ6 sharpness at 26, a D7 reduction, a corrupted B0 pair |
| X | `independent_check.py`: membership-filter roots, basis-coordinate functionals, Bareiss integer ranks, its own simple system, D7 as norm-4 lattice vectors, the shipped P110 |

The written argument is in [PROOF.md](PROOF.md). It cites one classical premise: every root-spanned
subspace is W-conjugate to a standard parabolic one, as in PR939, PR954 and PR968.

## Scope and inherited obligations

- **Covered.** Label decoders of the fixed matrix B0 on the live lines, any number of terms, punctures of
  at most 25 lines, cost = rational pairing rank.
- **Not covered.** Decoders that differ from B0 on orthogonal pairs, non-label factors, punctures of 26 or
  more lines, non-root ports. For n = 10 the bounds are 64 at p = 7, 62 at p = 8, and 60 for p = 9..11.
- **Not a construction of a word.** A cost-6 term needs an asymmetric copy from the span b^⊥ to the span
  a^⊥. PR620 lists the open realization questions: reader frame chains, a nonzero terminal frame with
  restoration, and the common cut. The pricing is a favorable budget; the port price is a recorded PR717
   number. A new owner map must be supplied; the aggregate capacity test alone does not prove hosting.
- **Inherited conditions.** All conditions of the selected record remain: all-size compiler, common-label
  and mutable-source realization, whole-call hosting, precision/tape, analytic transfer and the bit
  supplier's H1-H5 interface.
- **Search scope.** The witness is the first system reached by backtracking with one ordered orthogonal
  pair fixed (W(E8) is transitive on such pairs). A full count of nine-pair systems was started and
  stopped after 15 minutes without a result; no census of these systems is claimed.
- Finite replay is not a formal proof of the multiplication theorem, and the written proof has not had
  independent human review.

## Provenance, credit and overlap

- **Base and assignment.** Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Sprint track 40-49
  (structural decoder research), assignment seed **40** from OS randomness. See [CLAIM.md](CLAIM.md); no
  pinned coordination issue existed, so the claim is local.
- **Model.** Joel Pulikkan / GamingPuzzled (PR620, preliminary content retained as `research/e8-decoder-floors-and-cold14-notes`)
  defined the Theorem C label-decoder floor on the bit side and observed cost-6 orthogonal punctured
  pairs at P111. DreamingOfClouds (PR446 Theorem C; PR595 format limits, deficit identity and hosting
  wall; PR717 P2 bit invoice notes at head `4a97676`; PR589 bit supplier) supplied the copy-cost premise,
  the accounting and the priced word.
- **P111 floor.** Russell Seligmann (PR757, head `e2ec7d7`) and Cody Harris (PR761, head `2877587`) prove
  63 at P111 in this class; part (b) of the theorem reproduces their nine-term value at p = 9 by a
  different, puncture-independent argument, and their ten-term bound is stronger at P111.
- **Complex analogue.** themilkman216 (PR968, `research/complex-frame-pair-decoders`) gave the complex
  frame-pair floor 7/13 and the P104 knob scenario re-implemented in section H. The violator census of
  section B has the same numbers as PR968's table, since |R(λ) \ ω^⊥| = |Viol(λ) ∩ C(ω)|.
- **Star model.** Chi Zhao (PR631), Ross Richardson (PR939, PR954) and Philipp (@mightyOil, PR875) bound
  the star-priced ratio; star pricing charges 7 for both self and orthogonal pairs, so their results and
  this one concern different charges.
- **Selected chain.** Jonathan Capalbo (PR942), Chafik Boukhalfa (PR890), Jeremy Kothe (PR869/870), Hao
  Yan (PR858), DreamingOfClouds (PR589) and eumemic (PR555); this package only reads their pinned inputs.
- **Overlap check.** The full refresh covered 757 open PRs through #1062, including #1060 (a finite
  complex P111 COPY construction with its own extra costs, not a bit supplier), #1020 (complex
  F2 label-pairing ranks at 26 punctures), #1008 (tensor shears on fixed P111), #998 (complex single
  lifts), #966 (prescribed star triples), #912 (Hurwitz routing) and #757/#761 (fixed P111). These
  scopes differ from rational pairing ranks on other bit-side punctures.
- **AI assistance and license.** Prepared for @navinor with substantial AI assistance
  through OpenCode in research, proof, both implementations and documentation; resumed review and
  packaging used GPT-6.1 Sol (OpenAI). Apache-2.0. See [NOTICE.md](NOTICE.md).
