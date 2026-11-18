# FibreK (Nov 17): Theorem K and G2 for pure relabels, in Lean

`Nov15/FibreK.lean`, Lean 4.33.0-rc1 + Mathlib, kernel only: no `sorry`, no `native_decide`; every theorem prints
`[propext, Classical.choice, Quot.sound]`. Builds in 10 s / 2.9 GB (runlean.sh guard). Reuses `SwapNull` (Blk, Undo, rowSw,
colSw; olean built into .lake/build/lib/lean/Nov15) and `CallerCost` (Hist, Inv, invoice, Dh/Dinv).

## 1. THEOREM K (AUDIT2: sound with fixes)
P0 is an explicit hypothesis: `Table {tT tP : ℕ → Hist}` = the ranks a helper pays on T for climb d = e - b and on P for a
helper MOVE of |Δdim| = d (the price checker's per-call ranks; AUDIT2 could not find the README in the tree, so the table is a parameter,
not a quoted constant). A word is `E : Inv` (fixed by the ends) plus helpers `{b, e, steps}`.
* `K_word`:  `Fi (nativeInv E tb H) t = FK E tb (Ssum H) (PiW H) t`, i.e. F(t) = Σ_r (T_r − P_r) r^(1−t) is a function of
  (E, S = multiset of helper MOVEs (src dim, tgt dim), Π = multiset {e_h − b_h}). Births/ends enter only through Π; ADD/SCALE/SWAP
  appear nowhere (they are not in the table).
* `K_congr`, `kappa_depends_only`: same (E, S, Π) ⇒ same F, same roots, also for the caller invoice
  `K_invoice : Fi (invoice c n L) t = Fi c t + L · FK E tb S Π t` (CallerCost.invoice).
* `d0_native`: for `d0Table` (ranks = gaps) the helper part is Σ_h [f(e−b) − Σ_steps f(gap)] (the per-helper D0 identity of
  FloorD0/V2Bridge, f = r ln r, Dh convention).
Remark: the dependence on S is only through the multiset of GAPS |Δdim|; the source dim itself is not priced.

## 2. G2 for PURE relabels (AUDIT2: sound with fixes)
Model: registers `Reg` (Fintype), final matrix `F : Matrix Reg Reg K`; `HelpersId H F` = every helper's final row is its own unit
vector; hub gauge = `Undo V G F F'` := ∃ L M, Blk V L ∧ Blk G M ∧ L·F'·M = F (SwapNull; invertibility NOT demanded, which only
strengthens the conclusions). σ permutes helpers only (`σ x = x` off H). β, ε : birth/end dims; V ⊆ H = the helpers with ε = d
(one chart, `hE : ε x = d ↔ V x`).
* `tail_force`: F' = rowSw σ F (SwapNull.tail_run), L ∈ Blk(V′), M ∈ Blk(G0) ⇒ every moved helper x ∉ V′ has x, σ x ∈ G0.
* `tail_pairs`: with G0 ⊆ {β = 0} and **V′ = σ⁻¹ V** (`fun x => V (σ x)`), the (birth,end) multiset {(β x, ε (σ x))} equals
  {(β x, ε x)}. Proof: σ carries H∖V′ onto H∖V keeping β (moved ⇒ both birth 0); V′∖V and V∖V′ are birth-0 and |V′| = |V|
  (`map_birth_eq`).
* `head_force`, `head_pairs`, DIRECT (not by time reversal): F' = colSw σ F (SwapNull.head_run), L ∈ Blk(V) (V unchanged), M ∈ Blk(G1)
  where **G1 is the NEW births-at-0 set** (`G1 x → β (σ x) = 0`); moved x ∉ V ⇒ σ⁻¹x, x ∈ G1 ⇒ β x = β (σ x) = 0. Pair multiset
  {(β (σ x), ε x)} = {(β x, ε x)}. This is the head analogue of V′ = σ⁻¹V (the time-reversal image of "prefix ↔ V"); using the
  native G0 here is the head-side form of R1's slip.
* `tail_Pi`, `head_Pi`: Π unchanged. `tail_F_null`, `head_F_null`: FK (hence F(t), hence κ by K) unchanged, for any S, E, tb. S
  being unchanged by a swap is SwapNull.stays_multiset (not re-proved; the theorem takes S as the common argument).
* `c3_not_undoable`: Lean check of AUDIT2's observation. R1's 3-cycle C3 (a=(5→9), b=(0→7), c=(0→9), σ: a→b→c→a, identity F)
  is NOT undoable under V′ = σ⁻¹V for any G0 ⊆ {β=0}: its pair multiset changes (`c3_pairs_change`), which `tail_pairs` forbids
  for undoable relabels. (Undoable only under the native V = the retracted slip.)

No paper statement was found false as written. Corrections to the wording: (i) heads need the NEW G0 (G1 above), "same proof under
time reversal" is right only with that substitution; (ii) K needs P0 as a stated table; (iii) G2 conclusions about κ also need
S unchanged (SwapNull.stays_multiset), which is a separate hypothesis here.

## 3. NOT covered
* relabel + interior gauge D(t) jointly (D(end) ≠ I on helper rows; AUDIT2 item 2/4): the model has D = I, F' = P_σ F exactly.
* the LOOP claim (THEORY2 §2 "interiors differ by a time-slice gauge, κ-null"): UNSOUND as stated (D(t) = U′U⁻¹ exists for any two
  circuits; legality of D(t+1) T D(t)⁻¹ and D(end) = I are the content). Not formalised; only the true restatement
  "same skeleton ⇒ κ-null" follows from K_word (S and Π fixed).
* "native = max over fibre": NOT established (needs the joint case above, theorem R with the real the price checker concavity, and S that
  includes END charts for D helpers). R (re-pairing monotonicity), G1-tree, T (cover lemma), U in full generality are not formalised.
* mixed head+tail sequences (only each pure case); multi-chart V ends; helpers not ending identity.
* The real the price checker table values are not instantiated (`Table` is abstract; `d0Table` is the D0 convention).
