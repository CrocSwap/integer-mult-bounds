# Frame-pair decoders: the exact 8-term copy-cost floor for punctured complex units (no new κ)

**Status: research note and scoped structural result. No κ claim, no new supplier.** The selected
κ = 0.001661960547713947 (PR942, T37) and every existing file are unchanged.

## What this establishes

The selected complex supplier is the binding side. Its copied-information cost is the decoder
constant, cst = 64 on 112 ports, inside the deficit 37·(8·112 − 9·64) = 11840 of T37. PR717 (DreamingOfClouds,
open) found two cheaper non-star decoders by random walks: cst 63 on single-line P111 punctures, and
cst 56 on one P104. This package explains that mechanism, bounds it, and prices it. It works in
PR717's own B14 model, for exact 8-term decoders (D = RA, T = R·2A^{-T}).

1. **Mechanism.** Take a term whose row and column normals are roots α and β with ⟨α, β⟩ odd.
   If both lines are punctured, it costs exactly 7 (for p ≤ 24). If either line is live, or if
   α = β (the coordinate decoder), it costs 8. The reason is short: the labels of N(α) span the
   hyperplane H_α = u_α^⊥ in F2^9, the line's own label lies outside it, and the pairing H_α × H_β
   has rank 8 − [⟨α, β⟩ odd]. All three vendored PR717 hits have exactly this
   structure. Every cost-7 term is an odd root pair with both lines punctured, and the per-term costs
   agree with PR717's recorded values.
2. **Construction family.** Take a second frame F1. If there is a dual root basis on F0 ∪ F1 in which
   every term pairs a line of F0 with a line of F1, the 16-line puncture P104 = P120 − F0 − F1 has
   cst 56. A complete census of the 1260 frames inside P112 finds:
   - **896** frames admit such decoders, with exactly 8 each; all 7168 are exact with eight cost-7
     terms;
   - **364** admit none. In these, some pair of F1 lines shares four F0-neighbours.

   PR717's randomly drawn P104 clique is one of the 896.
3. **Floor (theorem, finite census plus written proof).** For every puncture of p ≤ 24 lines, every
   exact 8-term decoder has

       cst ≥ 72 − p  (p ≤ 15),      cst ≥ 56  (p ≤ 24),

   and both bounds are attained at every p. Hence the copy ratio satisfies **cst/v ≥ 7/13** through 24
   punctures, with equality only at p = 16, cst = 56. The shipped P112 has 4/7. So PR717's P104 is
   ratio-optimal in this class, and its P111 hits are cost-optimal among 9-line punctures. The
   P112 = 64 floor is re-derived for exact 8-term decoders by a different argument.
4. **Favorable budget on the selected frontier.** These numbers transport PR717's P1 knob model to the
   selected T37 profile and price it with the same pinned moment and outer engines as the selected
   record:
   - P111: b rises 0.67%, giving κ 0.001673104139787043.
   - P104: b rises 5.51%, which takes it **above the bit supplier**. κ is then capped by PR589 at
     **0.001730427469823602**, 4.12% above the selected value. That cap applies to *any*
     complex-only change.

   So a realization of the asymmetric (α ≠ β) centres improves κ only if its extra costs lower b by
   less than the 5.51% gain, measured against the selected b. It reaches the bit cap only if they lower
   b by less than about 1.3%, since the P104 knob value of b is 1.33% above the bit c. PR717 recorded,
   but did not ship, an estimate of −0.1% to −10% net b for building these decoders.

Searches for cheaper exact 8-term complex decoders through deeper punctures (p ≤ 24) are closed by
item 3. The remaining open directions are in the Scope section below.

## Reproduce

From the repository root, Python 3.10+, standard library only, assertions enabled (about 30 s):

```sh
python3 -I -B research/complex-frame-pair-decoders/verify.py
```

Expected: 48 `PASS` check lines, no `FAIL`, exit status 0, and the final line

```text
PASS_COMPLEX_FRAME_PAIR_DECODERS: types 8; D7 orbit 1080; frames 1260 (admissible 896); chain p=0..24; P104 7/13; bit cap kappa 0.001730427469823602; controls 6
```

Add `--out /new/file.json` to write the complete certificate: census, chain, hit replay, prices and
log.

## What `verify.py` checks

| section | content |
|---|---|
| A | 120 lines; the pairing (⟨r_i, r_j⟩ + 1) mod 2 has F2 rank 9 with distinct rows. This is PR717's S9 label pairing, computed without PR717's coordinates. |
| B | All 8 W(E8) hyperplane-flat types × all 511 hyperplanes and 130,305 codimension-2 pairs. Minimum violators to reach an 8-dim span: E7 (root) 1 (its own line), D7 14, all others ≥ 27; a root by any other hyperplane ≥ 24. A 7-dim span needs ≥ 25. The root fact is checked for all 120 roots directly. |
| C | The 1080-direction D7 orbit: unique 14-line sets, pairwise unions ≥ 21, none equal to a root functional. |
| D | All 1260 frames in P112 and all splits S ⊆ F0, T ⊆ F1: 896 × 8 decoders, each with AᵀB = 2I and eight cost-7 terms, plus one full 104 × 104 entrywise check; 364 frames have no solution. The three relative positions are reported. |
| E | An explicit exact decoder for every p = 0..24 with cst = max(72 − p, 56), and full-rank live sets. |
| F | Replay of PR717's P104 and two P111 decoders: exactness, root-pair structure of every cost-7 term, and agreement with PR717's recorded per-term costs. |
| G | Hash-pinned engines (the same hashes as the selected ASSEMBLY.json inputs). Gate: the selected record (T37, 37 replicas, inferred from the deficit identity) reproduces b and κ exactly. Then the P111 and P104 knob scenarios, two-engine moment checks, outer κ with the next-grid/η/β controls, and the PR589 cap. |
| H | Negative controls: a mutated decoder loses exactness; restoring one self-line gives 57 = 72 − 15; the even coordinate decoder on the same P104 stays at 64; the 364 inadmissible frames; swapped partners; a 25-line set does reach a 7-dim span, so the threshold is sharp. |

The theorem's lower-bound argument is in [PROOF.md](PROOF.md). The finite facts it uses are
sections A–C. One step is cited rather than recomputed: the classical fact that every hyperplane
flat of a Weyl arrangement is conjugate to a standard one (8 types for E8). The D7 orbit, which is
the only non-root type below the thresholds, is enumerated directly.

## Scope and inherited obligations

- **Covered.** Decoders with exactly 8 terms that are exact on all live pairs. This is the D2/D3
  scope of PR717. The census does not depend on which lines are punctured, for any puncture of at
  most 24 of the 120 lines.
- **Not covered: decoder classes.**
  - n ≥ 9 terms, including PR717's open mixed-β problem on P112 (the PR845 family excluded one such
    class);
  - decoders exact only on the E-graph, with cost-0 terms for the odd entries;
  - punctures of more than 24 lines;
  - labels outside this model.
- **Not covered: construction.** No word is built. The knob pricing is a favorable budget, not a
  supplier. Realizing asymmetric centres raises unresolved questions: centre reads, frame legality,
  phase frames and restoration. PR717 recorded unpaired-centre parity costs (≥ 78) and 96 pair-split
  conflicts, which are not re-derived here. The knob model removes a port as one modal source and
  target climb per call plus nine idle rank-48 children per replica, exactly as in PR717 P1.
- **Inherited conditions.** All of the selected record's conditions are unchanged: all-size
  compiler, common-label and mutable-source realization, whole-call hosting, precision/tape,
  analytic transfer, and the bit supplier's H1–H5 interface.
- **Not a formal proof.** Finite replay is not a formal proof of the multiplication theorem. The
  written lower-bound proof has not had independent human review.

## Provenance, credit and overlap

- **Base and assignment.** Base commit `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`. The work started at
  `47481c89` (PR890 T21 selected) and was rebased when T37 was published; the theorem is unaffected,
  and on T21 the P111 knob value was κ 0.001673101338175894. Sprint track 40–49 (structural decoder
  research), assignment seed **47** from OS randomness. See
  [CLAIM.md](CLAIM.md). No pinned coordination issue existed, so the claim is local.
- **DreamingOfClouds, PR717** (open, head `4a97676`). The B14 model, the D1–D3 findings that this
  package explains and bounds, and the P1 knob calculus. Three decoder files are vendored byte for
  byte with git-blob and SHA-256 pins in [SOURCES.json](SOURCES.json) (Apache-2.0).
- **Joel Pulikkan / GamingPuzzled, PR620**, merged as `research/e8-decoder-floors-and-cold14-notes`.
  The complex frame decoder of cost 64 and the star-floor census.
- **DreamingOfClouds, PR595** (merged, `research/format-limits*`). The (Dfc) identity, the format
  ceiling and the copy-charge prices.
- **PR845.** The one-added-total exclusion on P112, a different class.
- **icekylinx, PR514/P112.** The 112-port puncture.
- **The selected T37/T21 chain.** Jonathan Capalbo (PR942), Chafik Boukhalfa (PR890), Jeremy Kothe
  (PR869/870), Hao Yan (PR858), DreamingOfClouds (PR589) and eumemic (PR555). This package only reads their pinned pricing
  inputs.
- **Overlap.** Bit-side puncture and pairing-rank results (#631, #761, #875, #939) and the
  Gaussian/Eisenstein copy floors (#738, #770, #798, #868, #888) concern other units or the
  non-binding bit side. Before submission, no open PR addressed exact 8-term complex decoders under
  punctures.
- **AI assistance and license.** Prepared with substantial assistance from Claude Opus 5.5
  (Anthropic) via Claude Code: the research, proof, implementation and documentation. Submitted by
  the account holder. Apache-2.0.
