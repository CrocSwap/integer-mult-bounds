# KPR5 material: the END-CAP OBSTRUCTION (B258, Oct 13). Read drag plus versions plus the perp(P_t) cap forces copies.

## Setting (k8/#1018-type complex local; frames are binary subspaces of F_2^9; V targets y_t with ports u_t, u_t·u_t = 1)
- (R1, SPEC) Common frame: an ADD t += q·s at frame F climbs BOTH t and s to ⊇ F (03-motifs.tex:157; gk_word.py:116; audit_local.py:137-138).
- (R2, SPEC) Sink interface: Y_t's sink label S_t is a complement hyperplane of ⟨u_t⟩, i.e. S_t = w_t^⊥ with w_t·u_t = 1.
  Sources: 03-motifs.tex:625-668 and 05-layers.tex:141-154; bit form 04-swap.tex:117-121; format-limits-corrected C.3.
  Lemma R pins w_t = u_t when the drop-free taint of t spans u_t^⊥.
- (R3, C priced) Nesting: a register's frame is monotone. A non-nested edge G→S costs d(G,S) = dim G + dim S − 2 dim(G∩S) rank per call.
  It is enforced as a hard rule for targets by gk_word.py:102/:117 and audit_local.py:122/:142.

## Lemma (read drag)
Let D_s(τ) be the join of all op frames on register s strictly before time τ. By R1 and R3, frame(s) at τ ⊇ D_s(τ). This holds whether s was written or only READ, because reads climb s too.
If y_t reads s directly at τ, then frame(y_t) at the end ⊇ D_s(τ).

## Theorem (end-cap obstruction)
Suppose y_t reads s directly at τ and D_s(τ) ⊄ w^⊥ for every admissible w (under Lemma R: D_s(τ) ⊄ u_t^⊥, i.e. one op on s before τ used a frame with a direction off u_t's cap).
Then a word that keeps s's value at τ for this chain must pay one of:
- (a) a VERSION of s: a register that holds s's value at τ with frame ⊆ u_t^⊥.
  - Either a copy taken before the first offending op (needs no write to s in between),
  - or a reconstruction from the operands of the writes that occurred after that copy (forward substitution, extra ADDs);
- (b) a REORDER that moves every offending op on s after τ. This is legal only for ops that commute with the read: other reads of s, not writes;
- (c) ≥ 1 rank unit per call on target t: FULL sink with M_in(X_t) = 0, or a descent FULL→S_t, d = 1 (B29/B35, rank-intrinsic);
- (d) a descent on s itself, d ≥ 1 per call (R3; reader descents ≈ 2r/call, registered dead R39-H/J24-C1).
Proof sketch: by the Lemma, frame(y_t) ⊇ D_s(τ) ⊄ S_t, so the final edge to S_t is non-nested. By R2, no complement sink fixes it, so (c) or (d) is paid unless the read is redirected to another register (a) or the order is changed (b). QED.
Corollary (versions): if s is WRITTEN after the offending op and before τ, then (a) needs a version, not a snapshot. A copy taken before the drag carries the wrong value, so either the copy must also receive the later writes (it becomes a second register, i.e. the existing S3 copy) or the value must be reconstructed.

## Price on the k8/#1018 invoice (exact, deficit-honest; cards/B258/kap_free.py)
- (c): −2.819% κ per unit per call, linear (+16 units −45.06%; ≥ about 36 units: no saving).
- (a) copy: a helper ≈ +0.04 to 0.14% to delete, so a copy is 20 to 70 times cheaper than (c).
- Hence copies are economically forced whenever the obstruction fires. That is the ≈ 268 S3/S4 copy population.
- Measured scope: B252/B253, 84 words. Every deletion fires on 4 targets per S3 copy. Every violator ends FULL with u_t inside the frame, so no complement-sink freedom applies even without Lemma R.

## Scope (what the theorem does NOT exclude)
- Fixed op order and a fixed multiset are assumed in the measured instances. (b), joint deletion+reorder, has never been run (B256/B257 are running it).
- The theorem does not exclude (a) by reconstruction: it adds ADDs and frame mass but no register (B256).
- It does not exclude a decoder whose pairing is asymmetric, so that Lemma R no longer pins w_t (C.6: none exists at E8 window ≤ 9).
- It does not exclude non-projection rational labels (the B37 hole), where sinks need not be idempotent complements.
- Helpers are out of scope: they have arbitrary ends via helper_final (#593/#599), and the obstruction applies only to registers that feed targets.

## Escapes, ranked (from SYN-24)
1. Version reconstruction (B256).
2. Cap-ascending drag ordering with joint deletion (B256/B257).
3. Snapshot hoist on the final word (B257).
4. Motif/decoder redesign changing the u_t's (outside the current family).
