# Addendum (Nov 13): retraction of premise PA's "neutral period" wording and of law 5 as stated

No κ impact. No priced word changes. Laws 1–4 are unaffected.

## Retraction

The following statement in PROOF.md (premise PA, Lemma A) and README.md §5 is **retracted**:

> A y-atom of column q leaves Y_q only during Y_q's neutral period or through an owned copy.

Here "neutral" meant: Y_q holds no public x-charge (and no charged token) when its atom leaves. Read that way, it is
**false on E8/P104**. So law 5 as stated is **withdrawn**:

> D ≥ dim{k ∈ ker G : k_N = 0} ≥ n − r − N_neutral − N_owned, with N_neutral the columns whose atom leaves during
> Y's neutral period.

This includes the headline "96 per call on E8/P104 when N_neutral = 0". The corrected, narrower statement below
replaces it.

## The counterexample [C, frame legality P-cond]

**Design ("wasted line contamination").** Start from the σ-anchor schedule. There is one early cell (σ(t), t) per
column on a perfect partner matching σ, and every other cell is settled. Then change one thing per column t:

1. Y_t visits the line ⟨q_s⟩ of a partner s = s(t) ≠ σ(t). There it takes −Z_ts·x_s from a **pure** X_s,
   through a two-read window.
2. Y_t moves to F_t = ⟨q_s, q_σ(t)⟩ ⊆ q_t^⊥. There it is snapshotted, O_t := Y_t = y_t − Z_ts·x_s (an owned
   COPY, unmoved and free), and parked (Y_t −= O_t).
3. The early relay re-adds O_t. Everything else is the anchor design.

Every column's atom leaves while Y_t holds public x-charge, so N_neutral = 0. No owned register moves, so there are
0 owned units and N_owned = 0. The literal bound is therefore n − r = **96**.

**Numbers (E8/P104, Gram from the pinned PR968 file).** Every one of the 104 columns is contaminated:

| contamination map s(t) | distinct sources | D | literal bound |
|---|---|---|---|
| seeded greedy-few map (seed 0) | 7 | **7** | 96 |
| seeded greedy-few map (seed 29) | 9 | 9 | 96 |
| deterministic greedy cover | 5 | 5 | 96 |
| control: s(t) = σ(t) | – | 96 | 96 |
| control: injective second matching | 104 | 96 | 96 |
| clean σ anchors (no contamination) | 0 | 0 | 0 |

**Mechanism.** Contamination is charged per distinct *source*, not per column. Empirically D ≤ ρ_K(sources),
where ρ_K(S) = rank of K = ker G restricted to S. This holds on every design run here and on 92/92 author runs on
A3/A4/E8. It is not proved, and equality fails on some designs.

**Reproduce.**

```sh
python3.12 -I -B research/p104-t-minus-one-laws/counterexample.py   # prints PASS_T1_COUNTEREXAMPLE (~11 s)
```

This is standard library only and exact over Q. It computes D in two ways:

- by the exact witness formula of law 1, extended to contaminated snapshots;
- by a full frame-free simulation with every register written out, where D = rank(arrivals + targets) −
  rank(arrivals) and Y is exact.

The two agree on 54 random A3/A4 designs (clean, x-contaminated and co-read). The E8 rows above are then computed
with the formula, and the clean-anchor value D = 0 agrees with law 1.

**Scope of the counterexample.** The algebra is exact. Frame legality is P-cond:

- **Order.** Relays lump at {0}. Every Y_t then visits its source line while all X are still pure. Next the X's
  read relays at their lines. Snapshot, park and early re-add follow at the 2-dimensional frames F_t.
- **Frames.** q_s, q_σ(t) ⊥ q_t, so the frames nest.
- **The unbuilt part.** The L side is the same unbuilt network that the clean anchor design needs: all L charge
  arrives after the anchor, here at frames ⊇ F_t.

**Price.** None. The park erases the pre-park delivery (Lemma P below), so every column must deliver cell (t, s)
again (+104 reads). D ≥ 0 is the clean design's value, so the design is strictly dominated by the clean anchor
design. The co-read variant (strip x_s from O_t by co-reading the pure X_s) gives D = 0, and it is only a deferral
of that same cell.

## Corrected statement

> **PA (corrected).** A y-atom of column q is a frame-local time difference of Y_q (G4) or an owned unit. In the park
> family F1, every L-cell counted in Y_q^final is delivered after the park snapshot, at frames ⊇ the export frame
> (Lemma P).

Drop "during Y_q's neutral period". As an x-neutrality statement it is false.

## What is proved

The proofs below are in the author's notes. They are summarised here; the package does not machine-check them.

- **G1, all programs [P].** Take any linear program in the σ-world of law 2. Let Q_V be the y-classes, mod
  range G, of token-free combinations of arrivals at V. Then **D ≥ (n − r) − dim Q_V**.
  - *Proof sketch.* Witnesses (0 on x, k ∈ K on y, θ on tokens) kill U. A subspace computation gives
    proj_K(A^⊥) = (A ∩ K*)^⊥, and here A ∩ K* = Q_V.
  - Law 5's inequality is therefore exactly G1 plus PA_gen: Q_V ⊆ span{e_q : q ∈ N}.
- **G2/G3 (Q-ledger) [P].** These steps never change Q:
  - public ADD, SCALE and MOVE;
  - owned deposits that are token-free with zero y-class: U, L, the gauge J ∈ range G·y, and x-only rows.

  Each other owned add changes dim Q by at most 1. So atom scarcity is created only by owned parks, and
  (n − r) − dim Q_V ≤ #(owned adds that are not Π-null).
- **G4 (restorer locality) [P].** A class restored by an unmoved owned row at frame F is a time difference
  Σ c_i (R_i(τ₁) − R_i(τ_i)) of public contents at F. Receipts that are x-only and token-free are invisible to it.
  That is why x-neutrality is the wrong hypothesis.
- **Lemma P, park family F1 [P].** In F1, y_t leaves Y_t by an own-snapshot park: O = Y_t(τ₀) at frame F, then
  Y_t −= O at τ₁ ≥ τ₀ with Y_t still at F. Then Y_t^final = the deliveries after τ₀.
  - Every L-cell counted in Y_t^final, and the L deposit, arrives after τ₀ at frames ⊇ F.
  - F is the last frame at which Y_t holds y_t.
  - So the **48-L-cells-per-exporting-column bill (4,608 on E8 for 96 columns) holds in F1 with no neutrality
    hypothesis**.
  - F1 covers the anchor-style designs that zero Y by parking, and it covers the counterexample.
- **Exchange lemma [P].** Co-reading an unchanged source to strip a pre-export delivery is a deferral: the same
  cell can be delivered after the export with one read fewer.

## What remains open

- **PA_gen outside F1.** These are programs that remove y_t from Y_t by tokened public routes, by the J gauge or
  by carrier preloads, instead of a park. A pre-export delivery is not erased there. The missing step is to bound
  how many G4 time differences can carry distinct column classes without the relay structure.
- **The contamination law D ≤ ρ_K(sources).** It is empirical (92/92) and unproved.
- **Law 3's below-re-add-frame case.** It was conditional on Lemma A. It is now conditional on the corrected PA
  (G1 + PA_gen) and is unchanged otherwise.

## Consequence

- **Law 5 is withdrawn in its original form.** The 96-per-call figure for N_neutral = 0 does not hold for
  arbitrary programs. It fails on E8 in the anchor-design model.
- **The corrected conditional form replaces it.** D ≥ (n − r) − dim Q_V holds for all programs. Law 5's
  inequality holds under PA_gen. In the park family the L-side bill holds unconditionally.
- **Laws 1–4 are unaffected.** That covers the charge law and corrected anchored law, the carried-row law, hub
  additivity and the per-J odd unit.
- **No κ claim** was made or changed. The frontier is untouched.
