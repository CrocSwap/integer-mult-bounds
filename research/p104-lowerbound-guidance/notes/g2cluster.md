# G2CLUSTER G2C (Nov 20, Opus, theory + exact replay). Own code here: gfa.py (global FA engine), gfa_test.py (fuzz → fuzz20k.log), gadgets2.py (→ gadgets2.log), asc56g.py (→ asc56g.log), netattr_rside.py (→ netattr_rside.log), epoch2.py / epoch2g.py / epoch2h.py (exhaustive F2-decoder minima). venv, 1 proc, threads=1; no SAT/Lean/advisor/push/kill.
Why this differs from UPHASE: UP put weights only on publics and priced each owned lifetime by its raw content. Here EVERY register carries an FA weight, owned ones included. Intakes after outputs push weight back onto their sources, descents flush, and coldness is judged on the EFFECTIVE content.

VERDICT: R ≥ 56 for ALL runs is NOT closed. Three things are proved [P], and they are verified exactly:
- G2 is closed. It was an artefact of a raw-content coldness test.
- G3 is closed for nested re-intake. One row per lifetime.
- The residual is sharp: hot intake in both time directions. It provably needs the global final-cold condition, as the NETATTR note warned.
No counter-run was found.

## 1. Global FA identity [P]
- Sweep forward. Every register r carries W_r ∈ Q^targets.
- ADD d += λs gives W_s += λ([d=X_t]e_t − W_d). This holds for any kinds of d and s.
- Owned descent C→C': the labels of W_r that leave C' are flushed as a row (W_out, content, C).
- CLEAR emits (W_r, content, chart).
- Invariant: X(τ) − X(0) = Σ_r W_r r(τ) + Σ emitted rows. This is exact telescoping, the same one-line check as UP §2.
- Public weights only ever sit inside the chart, and every row's w sits inside its emission chart.
- Hence odd receipts = Σ_rows w ĉ^T, with ĉ the effective content (x-balance as in UP §2(c)).
- [C] 0 identity fails and 0 invariant violations, in 20k fuzz runs and their adjoints, the gadgets, and both asc56 runs.

## 2. NRI lemma (closes G3 except descend-then-reintake) [P]
Hypotheses: the lifetime is never flushed (no output label leaves the chart before a later intake), and every intake has effective content cold at its chart. Then it emits ONE row, with price ≤ dim Bl − dim(Bl∩A) ≤ cost, where Bl = span(labels of w) and A = ∩ intake charts.
- Proof of the price bound: the pairing Bl × A^⊥ factors through Bl/(Bl∩A).
- Proof of the cost bound:
  - Up to the last intake C_a, the cost is ≥ dim C_a − dim A (UP's modular induction, which uses only the path).
  - Labels added before the last intake lie in C_a.
  - The ascent after it is ≥ dim(C_a+B_after) − dim C_a.
  - Bl + A ⊆ C_a + B_after.
- UP's own multi-epoch example (C1→D1, intake at D1, then D2) is now ONE row of price dim D2 − dim C1 = cost. The cross-term a1·γ2 vanishes on odd cells.
- [C] 15,477 certified lifetimes in fuzz20k (UP generator, seed 11): price > bound 0 times, bound > cost 0 times.

## 3. G2 is in class P [P + C]
- UP flagged G2's adjoint lifetimes as hot because their raw content holds x_1 (they read adjoint X_r).
- The effective content is x_1 − y_1 + y_0 ↦ y_0, which is cold at <2,4>. GTD holds.
- So G2 satisfies the hypotheses of UP §4 (class P), and global PA charges the row to O1: price 1 = cost 1, Σ = 3 = R.
- G3 is P as before.
- gadgets2.log: G1 is F∩P; G2 and G3 are P. Identity and odd-cell checks give 0 fails.

## 4. NETATTR cross-check (coordinator note) [P + C]
- Network chart c corresponds to run chart c^⊥. A relay j→k needs b_j ⊆ a_k, which on the run side is the chart containment A_k ⊆ B_j. That is a DESCENT, so only an owned register can realise it, and it pays e.
- netattr_rside.log: instance (i) becomes one descend-then-reintake lifetime, <2> → <2,5> → <5> → <1,4>. It reproduces exactly the 6 odd cells, and R = 3 = the required decoder mass 3 (tight).
- So the network failure is NOT an R-side failure: the network's "free ascent" e costs e in R.
- My G3 route is consistent with the note: no local segment map, one row (§2) or flush rows (§5).

## 5. Descend-then-reintake (flushed lifetimes): open, no counterexample
- [C] fuzz20k: 5,840 flushed, cold lifetimes; the flush-row price exceeded cost 0 times.
- [P] Rectangle rows cannot close this case in general. Walk <e3> → <e1,e2,e3> → <e1,e2> → <e1,e2,e4,e5> has cost 5:
  - the forward, backward and signed covers each cost 6 (hand computation, §5 of this note's derivation);
  - but the exhaustive F2-decoder minima are 4 and 5 ≤ R (epoch2.py, epoch2g.py; rank 4).
- Any proof therefore needs label-split rows.
- [CONJ] Flush rows (or a label-split refinement) give Σ price ≤ cost. One shape to test is "up d ≥ 3, down 1, up 1" at N ≥ 5; flush rows predict an overcount there.

## 6. The residual (what is left of HostToDec_Q)
These are runs with a lifetime whose effective intake is hot in BOTH the forward run and the adjoint, plus §5.
- [C] fuzz20k: F' 8,279, P' 8,586, F'∪P' 11,304 of 20k.
- Row sum exceeds R in 12 runs, all outside F'∪P'. The smallest has 43 ops: R = 0, a cost-0 lifetime with price 1, and publics whose finals are not cold (Y_s final ≠ y_s).
- So in unconstrained runs a hot intake really is free (publics carry it and never clean it). No per-lifetime or per-cluster law can close hot intakes. A proof must use the final-cold constraint globally, e.g. a joint FA/PA mixed attribution where the cleaner of each hot public is charged.
- asc56 (no-mix and mixed) stays exact: 8 rows × 7, Σ = 56 = R, all NRI and cold (asc56g.log).

LADDER (updated): PR56 R-side ⇐ Wall56@Q96 + [every lifetime is NRI with effective-cold intake in the run or in its adjoint (one direction for the whole run)]. G2 is closed; G3 is closed except descend-then-reintake.
NEXT:
- (i) Prove the flush-row bound, or find its N ≥ 5 counter-walk and the label-split repair.
- (ii) A mixed FA/PA attribution that charges the cleaner of each hot public; the final-cold constraint must be used.
