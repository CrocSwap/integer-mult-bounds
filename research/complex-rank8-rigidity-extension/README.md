# Rank-8 rigidity passes to supersets: P105–P110 partial-frame punctures, and P111 from PR1212 alone (no new κ)

**Status: scoped structural result. No κ claim, no construction.** It builds on the rank-8 rigidity line of PR1212
(burntout76, `research/complex-rank8-decoder-rigidity/`, open, head `57099cb5`), PR1389 and PR1399. It answers
PR1399's open next question, the intermediate punctures P105–P110, as far as a linear argument reaches.

In PR717's E-graph (masked) model, a live set L is *rigid* if every rank-≤8 solution K of PR1212's system (E)
(`K_ii = 4`, `K_ij = 0` on orthogonal live pairs, odd entries free) is `D(2G)D⁻¹`. Rigidity is what turns
PR968's eight-term floor into a floor for masked decoders with exactly eight costly terms (PR1212 §8).

**Lemma 10 (extension).** Suppose L ⊂ L′, L is rigid, and the roots of L span R⁸. Suppose also that for each new
line i, the lines of L orthogonal to i span `r_i^⊥`. Then L′ is rigid.

The proof ([PROOF.md](PROOF.md)) is a few lines of linear algebra. K′[L,L] already has rank 8, so each new row
is `2uᵀRᵀD⁻¹` on L. The zeros against the orthogonal old lines force `u ∝ r_i`, and the diagonal fixes the
scale. There is no zero exclusion, no DRUP certificate and no class argument.

**Theorem.** E8 \ S is rigid whenever S lies in the union of two disjoint frames. The P104 units are rigid by
PR1212, PR1389 and PR1399. The span condition holds on all 1260 units for all 16 new lines, with at least 52
orthogonal live lines each.

**What it reaches.** For P112 minus X:

- **Coverage rule.** FRAME0 ∪ X lies in a union of two disjoint frames exactly when X lies in a frame inside
  P112.
- **P111.** Every line lies in a type-(2,2,2,2) frame, so P111 rigidity follows from PR1212 alone. This is a
  second proof of PR1389's P111 result.
- **P110.** All 3304 orthogonal-pair units are rigid, again from PR1212 alone.
- **P105–P109.** 29232, 77868, 70560, 35280 and 10080 covered X for |X| = 3, …, 7. The PROOF.md table splits
  them by which predecessor they need.

The eight-costly-term floor on each covered unit is then cst ≥ 72 − p with p = 8 + |X|, by PR968
Theorem 4(b) via PR1212 §8.

## Reproduce

From the repository root, Python 3.10+, standard library only, about 1 s:

```sh
python3 -I -B research/complex-rank8-rigidity-extension/verify.py
```

Expected final line:

```text
PASS_COMPLEX_RANK8_RIGIDITY_EXTENSION: checks 14; Lemma 10 on all 1260 bi-frame units; 226324 punctures P105-P110 covered (all 3304 orthogonal-pair P110); P111 from PR1212 alone; P104 rigidity cited from PR1212/PR1389/PR1399
```

The verifier has its own E8 model and recomputes everything it uses:

- the 2025 frames and W(E8) transitivity on them;
- the three FRAME0-stabiliser orbits of the 1260 frames in P112, matched to the three types;
- the span condition;
- the cover census, the P111 cover, the P105–P110 table and the odd-pair P110 orbits.

It also runs exact rational checks of the lemma's mechanism and three controls:

- a rank-9 solution escapes;
- without the span condition there is a rank-8 non-gauge extension;
- a perturbed orthogonal entry is rejected.

## Not covered

- **Punctures containing an odd pair.** No frame contains an odd pair, so Lemma 10 from a P104 unit cannot
  reach them. This is most of P105–P110. At P110 it is 2912 pairs in two stabiliser orbits, of sizes 224
  and 2688.
- Orthogonal X that do not extend to a frame inside P112, for example 1792 of the 31024 orthogonal triples.
- **Inherited P104 rigidity** is cited, not recomputed. The type-(2,2,2,2) units come from PR1212 Theorem 1′,
  which is open and so is the whole chain. The other two types come from PR1389 and PR1399, both unmerged and
  unreviewed. P111 and all of P110's covered units need only PR1212.
- **Nine or more costly terms.** Rank-8 rigidity says nothing about rank ≥ 9; see control.rank9-escapes.
- PR968's flat-classification premise (F6) is inherited through the floor. Attainment of 72 − p on these
  particular units is not checked.
- The written proof has had no independent human review. There is no construction and no κ change, and every
  condition of the selected record is unchanged.

## Open next questions

**Odd-pair P110.** Is P112 minus an odd pair {x, y} rigid? These are the two stabiliser orbits of sizes 224 and
2688 (see [TASK.json](TASK.json)).

- *Why it matters.* They are the whole remaining eight-term gap at P110, and the extension lemma cannot reach
  them.
- *A feasible first step.* Per orbit, pick a pivot frame inside the unit. Test PR1212's (I3) and (I4) on the
  complete classes, then PR1399's Lemma 9 witness connectivity for the lines of incomplete classes. Build the
  zero-exclusion CNF with PR1212's `make_proof.py`.
- *The blocker.* Zero exclusion passes up to supersets, but these units contain no smaller unit with a known
  certificate. Each orbit therefore needs its own DRUP proof.

## Credit

- **burntout76 / Brett Halligan (PR1212):** the rigidity theorem, (E), the type-(2,2,2,2) units, the transport
  and §8's floor argument.
- **themilkman216 (PR968):** the eight-term floor 72 − p and its puncture theorem.
- **DreamingOfClouds (PR717):** the E-graph model.
- **PR1389, PR1399 (JosieElliston):** the type-(4,4) and admissible P104 units.

Prepared by JosieElliston with substantial assistance from Claude Opus 5.5 (Anthropic) via Claude Code,
covering the lemma, verifier and write-up. Apache-2.0.
