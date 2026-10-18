# Why a REJECT is sound

The verifier checks every computational step. The argument below is written out by hand; it is not formalised.

## Setting

**The word.** A word is in the bitE8/1+mut format, with v = 111 and R = 439.
- Its registers are sources x (0..v−1), targets y (v..2v−1) and helpers s (2v..).
- Its sections are D, A, the scatter (nine COPY snapshots of the retained totals, added into targets at frame 0, then erased), B and C.
- Frames are closed label lists, so frame a ⊆ frame b exactly when its labels are included. Engine 2 checks closure for every frame.
- A gate first climbs each operand to its frame. Frames never descend.

**The raw word.** W0 = (A, scatter, B) maps z = (x, s) to Uz, and y to y + x + Ks. Here V = I and J = I, checked on every word.

**The cut σ.** This is the moment right after the scatter. At σ every target is still at frame 0 (`xcheck_p.py:269`). Each target ends at its t⊥ (`final[v+t]`).

**An entrance.** It is given by:
- a support c, a nonzero set of helpers inside some class I(V) of #1253's closure L;
- a pivot p ∈ c with start[p] = E, where E is a nonzero frame inside V;
- the gauge q ^= p for each q ∈ c \ {p}, applied at frame E before A;
- optional source donors x_s ^= p, where the line of s lies in E.

The **pivot coefficient** of a value w is π_c(w) = |d(w) ∩ c| + |x(w) ∩ D_S| mod 2, where d is the helper part and x the source part. The **response** is ρ = Kc + 1_{D_S}, and T = supp ρ:
- the entrance is a **kernel entrance** (the #1179 case) if T = ∅;
- it is **late-compensated** if T ≠ ∅ and the missing compensation is supplied after σ.

## The class LC-fav

These are the premises.
- **P1.** The word data are unchanged: lines, frames (new closed frames may be appended), start except start[p], final, A with its gates and frames, ret, and the COPY centres and ranks. Scatter rows may gain snapshot terms, which only enlarges the class.
- **P2.** Before A there is only D′ at frame 0, then the gauge at the single frame E. There are no other gates and no new wires before σ.
- **P3.** Targets stay at frame 0 until the scatter.
- **P4.** After σ, anything is allowed that satisfies all of these:
  - it is a finite sequence of common-frame, invertible F2 operations with monotone frames;
  - fresh registers may be used if they are restored;
  - B and C may be replaced arbitrarily;
  - there is no new COPY, descent or reset;
  - the endpoint is (x, y, s) ↦ (x, y + x, s) on all 661 columns, and every register reaches its final frame.
- **P5.** Exactly one helper (p) starts at a nonzero frame.

**Lemma 1 (cone; the dependency-path argument of #1128 PROOF.md §1).** A value at frame U depends only on registers whose frames lay inside U along the dependency path. The scatter's COPY descent is the only exception.
- So D′ and every register at frame 0 before σ have π_c = 0.
- So every contribution of D′ to a helper or a target is x-free and has zero coefficient on the pivot input s_p. (D′ need not restore z; the proof uses only this property, applied to the full pre-A change of coordinates Γ′ = gauge ∘ D′.)

**Lemma 2 (monotone span; the dual of #1128 PROOF.md §2's erasure invariant).** Fix U = t⊥. Let Σ(τ) be the span of the values of the registers whose frame lies in U after τ post-scatter steps. Then Σ(τ′) ⊆ Σ(τ) ⊕ Fresh for τ′ ≥ τ.
- A step at a frame f ⊆ U only mixes registers that are already in the set.
- A step at a frame f ⊄ U removes its operands from the set for good, because frames never descend.

**W_t.** Let G_t be the set of values at σ of every register r ≠ v+t whose frame at σ lies in t⊥, together with the nine snapshots. Then W_t is the set of helper parts d(u) of the F2 combinations u of G_t with x(u) = 0. This is the y-free form; the y-zero form gives the same spaces on these words.

**Theorem.** In LC-fav, if the endpoint holds, then every t ∈ T has some u ∈ W_t with u · c = 1.

**Frames at σ.** A is fixed and E ⊆ V ⊆ F_q for every q ∈ c (E lies inside every first-contact frame of the support, and inside each donor's first A frame). So under the entrance every register reaches σ at its raw frame, and the register sets in Lemma 2 are the same for the raw and the modified word.

**Proof.**
1. Target t ends at U = t⊥. By Lemma 2, its final value y_t + x_t lies in the span at σ of the modified registers, raw_r(σ) + δ_r. The fresh part is zero, because the final value has no fresh coordinate.
2. In the same way, the raw end value y_t + x′_t + K_t s′ lies in Σ_raw(σ).
3. Let Δ be their difference. Then Δ has no x part in the original coordinates, and π_c(Δ) = ρ_t.
4. Write the modified σ-values as raw_r(σ) + δ_r + σ_r, where δ_r is D′'s contribution and σ_r collects the snapshot terms that P1 lets scatter rows gain (σ_r = 0 for non-targets). Then Δ = Σ (a_r + b_r) raw_r(σ) + Σ a_r δ_r + Σ a_r σ_r.
   - The δ terms carry no x part and no pivot, by Lemma 1.
   - The σ terms are sums of snapshots, which are generators in G_t; fold them into u.
   - So u = Σ (a_r + b_r) raw_r(σ) + Σ a_r σ_r has x(u) = 0 and π_c(u) = ρ_t = 1, and lies in span G_t.
5. The term for r = t is raw_t(σ). Modulo y, it is the sum of t's snapshots, so it lies in G_t.
6. Hence d(u) ∈ W_t and d(u) · c = 1. ∎

So a support is **rejected** in LC-fav if some t ∈ T has W_t ⊆ c⊥. Adding pivot-free dirt to the generators cannot change this, so the verdict does not depend on the choice of D′.

## Narrower classes

**A6** is the post-scatter program B ++ C left unchanged, plus inserted target reads [F, v+t, [r]]. Here r is one of:
- a z register;
- a snapshot (at σ only);
- a target that has received no inserted read (a read-only relay).

Raw gates keep their frames, and actual frames contain the raw frames. So every read needs cur_t ∪ cur_r ⊆ F ⊆ next_t ∩ next_r, computed from the raw frames. The span of every value read this way contains every reachable compensation. This makes A6's REJECT sound for the A6 class.

Both engines sweep insertion points through B only. That is enough: on all five words C is entirely at FULL and touches no target, and no target ends at FULL (the verifier asserts this). A register r not yet raised by C still holds its end-of-B value with next_r = FULL, so a read during C has the same value and legality as a read at τ = |B|. Once r is at FULL it lies outside t⊥ and cannot be read.

A6 is contained in LC-fav, so an LC-fav REJECT is also an A6 REJECT. The verifier checks that every A6 space lies inside the LC-fav space.

**A6R** is A6 plus storage relays, where a target that received inserted reads may itself be read later.
- Stored content keeps a frame tag: the join of the frames that delivered it.
- A read of u delivers u's whole value, which lies in the span of the stored entries whose tags fit the read frame.
- Restoring the relay is ignored, so A6R over-approximates. It is used only to show that the triple is **not** excluded once storage relays are allowed.

**The scout prototype's strict class.** It allows a read when the reading register's frame lies in t's next frame, with no check on the register being read (the carrier). That class is not physical; it is reported only to explain the scout's numbers. On these words its results equal LC-fav's.

## What the classes exclude

- a changed A, changed pre-scatter frame paths, or gates and wires before σ;
- targets leaving frame 0 before the scatter;
- a new or changed COPY, and scatter changes beyond added snapshot terms;
- gauge shears after A, or at more than one frame (the #1253 out-of-scope list);
- source-dependent basis changes other than the donor shear;
- several simultaneous entrances (see below);
- recursive interfaces, hosting and pricing.

Several entrances need a joint test, which is not run here: for every t, the vector (K_t · c_i)_i must lie in {(u · c_i)_i : u ∈ W_t}.

## Not sufficient

LC-fav admits the triple {444, 470, 578}, but that is not a construction.
- Under A6 the triple is rejected: only 150 and 197 of its 8 targets are coverable.
- Under A6R (storage relays, restoration ignored) all 8 are coverable.
- If only targets in T may store content, just 4 of the 8 are coverable.

So, within A6R (B ++ C fixed, insertion-only target reads), covering all 8 targets needs storage relays outside T, which must later be restored. The broader class LC-fav also allows a rewritten B or C and fresh restored registers, which A6R does not model. The triple is therefore **OPEN**, and this package hands it on.

A positive answer would at most save the pivot's first climb, i.e. the local −H1 (−H2 + H1 for p = 578). Width-8 hosting cancels it with +H1 (#1179, #1253), and the bit side does not bind. So no κ follows either way.
