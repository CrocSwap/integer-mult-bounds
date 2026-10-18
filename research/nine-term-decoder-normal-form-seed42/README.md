# Nine-term complex E8 decoders: normal form and residual class (no new κ)

**Status:** research note / scoped structural result. No κ claim, no supplier word.
`certificates/selected-result.json` (PR1094, κ = 0.001672660197076918), `upstream/` and every
existing file are unchanged.

PR968 and PR1077 proved the punctured complex E8 copy-cost floor for **exactly eight** terms.
Decoders with **n ≥ 9 terms** stayed open (PR968 §6, PR1071, PR1077, and PR717's open mixed-β
problem). This package finds the exact algebraic structure of every nine-term decoder and
reduces the open part to one explicit class.

## Results

The model is PR717 B14 / PR968 §1, with real or complex coefficients and ordinary transpose. Assume
the live roots span R^8, which is automatic for p ≤ 56. Proofs are in [PROOF.md](PROOF.md).

1. **Theorem A (any m).** Every exact m-term decoder is D = RA + N1, T = RB + N2. Here R^T N1 = R^T N2 = 0 and
   AB^T = 2I, N1 B^T = 0, A N2^T = 0, N1 N2^T = 0. The converse also holds. The pairing between
   ker A and ker B is nondegenerate.
2. **Corollary B (m = 9).** At most one of D, T has columns outside the live root code: the two junk
   parts satisfy (z·y) n n'^T = 0 with z·y ≠ 0. This is specific to nine terms. An exact ten-term
   decoder with outside-code columns on both factors is checked in C4.
3. **Corollary C.** A one-sided nine-term decoder is the same thing as an **overcomplete
   representation**. Pick nine column normals b_k with one dependency z, set T_jk = <r_j, b_k>, and
   let row i of D be *any* coefficient vector with Σ_k d_ik b_k = 2 r_i. Each line has exactly one
   free scalar.
4. **Lemma D.** Proportional column normals can be merged without increasing cost. So a nine-term
   decoder whose dependency has support |S| ≤ 2 is no cheaper than an eight-term one. PR968/PR1077
   then give cst ≥ max(72 − p, 56) for p ≤ 24.
5. **Propositions E, F.** Terms outside S have forced (unmaskable) row supports. A line skips
   exactly one *ratio class* of masked terms. A line skipping two masked terms k, k' is orthogonal to
   a canonical nonzero vector v_kk'. Hence one deficiency codeword cannot serve two masked row sides
   if its live support spans R^8.
6. **Proposition G (P120).** All 511 codeword supports span R^8, so every column side has full
   label span. A one-sided nine-term decoder on P120 therefore costs exactly 81 − Σ_{k∈S} δ_k, where
   δ_k is the label deficiency of masked row side k. Beating 72 needs Σ δ_k ≥ 10. That forces a
   masked row support of at most 36 lines (U2 = 84), and every cross pair of deficiency codewords must
   be one of 39,255 non-spanning support pairs. Census:
   - 255 complementary pairs;
   - 35,640 pairs whose intersection has rank 7;
   - 3,360 pairs whose intersection has rank 6.

   This census shows that the pairwise argument alone cannot close P120.

**Residual class.** For p ≤ 24, the eight-term floor can fail at nine terms only for decoders with
exactly one factor outside the root code and |S| ≥ 3. The "exactly one" part uses PR1180 (open,
concurrent), which handles the case where both factors stay in the root code. Without PR1180 the
statement reads "at most one".

## Constructions and bounded search (evidence, not proof)

Exact nine-term decoders were built from weight frames of maximal subsystems. Every line is
represented sparsely; for example, in the **A8 weight frame** each E8 root is 2- or 3-sparse.
Each decoder is checked on all 14,400 pairs.

| frame | masked terms | P120 cost | note |
|---|---|---|---|
| A8 weights | 9 | 81 | every row support has 36 = 120 − U2 lines, yet label span 9 |
| A7 weights + A1 root | 8 | 81 | |
| A2 weights + E6 root basis | 3 | 78 | |
| A3 weights + D5 root basis | 4 | 81 | |
| coordinate frame + one root | 5 | 76 | |

`search.py` annealed over every per-line ratio-class choice.

- **Domain:** the five frames, each on P120 and on its self-punctured live set.
- **Stopping rule:** seeds 0–2, 3,000 moves per run, 27 runs in total.
- **Result:** best ratio 67/111 = 0.6036. Nothing came below the shipped 64/112 = 0.5714 or PR968's
  56/104.

Earlier exploratory annealing from the coordinate decoder with 2, 4 or 8 extra root normals
never left 72 (P120) or 64 (P112). Those scratch runs are not packaged. This is a failed search over
the stated domain, not an impossibility theorem. Because no candidate was found, there is nothing to
price. Any complex-only gain would in any case be capped by the PR589 bit supplier, as PR968 §G
shows.

## Reproduce

From the repository root, Python 3.10+, standard library only:

```text
python3 -I -B research/nine-term-decoder-normal-form-seed42/verify.py
```

The run takes about 35 s. Expected final line:

```text
PASS_NINE_TERM_NORMAL_FORM_S42 checks=80 pairs=130305 frames=5 A8_cost=81
```

`--quick` skips the 130,305-pair census (B3–B5). `--out FILE` writes the full JSON certificate. The
bounded search (about 70 s) is:

```text
python3 -I -B research/nine-term-decoder-normal-form-seed42/search.py --iters 3000 --seeds 3
```

Its expected last line begins `SEARCH_DONE runs=27 best_ratio=0.6036`. The recorded run is
[SEARCH.json](SEARCH.json).

What `verify.py` checks:

- **A:** the model: 120 lines, a rank-9 pairing, code weights {56:255, 64:255, 120:1}.
- **B:** the spanning census:
  - all supports span R^8;
  - the rank of all 130,305 pairwise intersections;
  - U1 = 56 and U2 = 84.
- **C:** Theorem A and Corollaries B and C on exact decoders:
  - random one-sided decoders on P112 and P120;
  - the PR1180-shaped outside-code identity;
  - an inexact two-sided control at m = 9;
  - an exact two-sided decoder at m = 10.
- **D:** merging.
- **E:** the ratio classes and v_kk' ≠ 0 on every frame.
- **F:** the frame decoders and the P120 cost formula.
- **G:** controls:
  - a perturbed coefficient;
  - a deleted support entry;
  - a rank-deficient frame;
  - a flipped label;
  - label-span sanity checks.

## Scope and inherited obligations

- **Covered:** the structure of all exact nine-term decoders when the live roots span R^8; the
  reduction of the n = 9 floor question to the residual class; the P120 necessary conditions.
- **Not covered:**
  - a floor for the residual class;
  - m ≥ 10 terms;
  - E-graph-only (masked-identity) decoders, for which see PR1191;
  - p > 56;
  - any copy-tree realization, delivery, restoration, hosting or precision cost.
- **Cited, not recomputed:** PR968's real eight-term floor (including its F6 flat classification)
  and PR1077's complex extension, both on main and pinned in `SOURCES.json`. PR1180's both-root-code
  theorem is cited only for the optional "exactly one factor" refinement. It is open and is not
  re-verified here.
- All inherited conditions of the selected record are unchanged: all-size/compiler, common-label
  and mutable-source realization, whole-call hosting, precision/tape, analytic transfer, and the bit
  supplier's H1–H5. Finite replay is not a formal proof of the multiplication theorem, and the
  written proofs have had no independent human review.

## Provenance, credit and overlap

- **Base:** `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` (main). Sprint track 40–49 (structural
  decoder research), OS-random seed **42**. See [CLAIM.md](CLAIM.md). The claim was recorded locally;
  no coordination post was made.
- **DreamingOfClouds (PR717, PR595):** the B14 decoder model, the cost semantics and the open
  n ≥ 9 / mixed-β question.
- **themilkman216 (PR968)** and **@woklerx (PR1077):** the eight-term floor this package extends the
  reach of.
- **@woklerx (PR1180, open, concurrent):** the arbitrary-m floor when both factors stay in the root
  code. It also gives the outside-code nine-term example that this package's Corollary B explains,
  since that junk is necessarily one-sided.
- **@mightyOil (PR1191, PR1197, open, concurrent):** one-sided mask rigidity for masked identities, and
  restricted P112 ten-term cases. These are adjacent scopes that neither contain nor are contained in
  this one.
- **@burntout76 (PR1212)** and **@DavidAriasC (PR1213), open, concurrent:** rank-8 gauge rigidity and the
  P112 connected component for *masked (E-graph-only) eight-term* decoders. Both list nine or more terms
  as open, and both are disjoint from this all-pairs nine-term scope. The final overlap scan covered open
  PRs through #1221.
- **@3xcalibur-tech (PR1171):** the support-union hierarchy (U1, U2) is re-derived here independently.
- Also credited: PR620 (GamingPuzzled), PR446 Theorem C (DreamingOfClouds) and the selected supplier
  lineage. All code here is independently written; nothing is vendored.
- **AI assistance and license:** prepared with substantial assistance from Claude Opus 5.5
  (Anthropic) via Claude Code, covering the research, proofs, implementation and write-up. Submitted
  by @joaqcoo. Apache-2.0.
