/-
Psi findings (internal notes) formalised. See PsiLaw.md.
Kernel only: no sorry, no native_decide.
Build: lake env lean Nov15/PsiLaw.lean   (imports the HubSettle olean)
-/
import Nov15.HubSettle

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace PsiLaw
open Submodule Module Matrix RankLaw HubSettle

/-! ## Part 1. One prefix transform and one V mix -/

section One
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- Two hub-prefix coordinate changes compose into ONE (the two hubs act as one transform). -/
theorem mapRows_comp (L1 L2 : (Reg → K) →ₗ[K] (Reg → K)) (s : TokenCancel.St K Reg C) :
    mapRows L1 (mapRows L2 s) = mapRows (L1 ∘ₗ L2) s := rfl

end One

section Exact
variable {K N G0 G1 : Type*} [Field K] [Fintype N] [Fintype G0] [Fintype G1]
  [DecidableEq N] [DecidableEq G0] [DecidableEq G1]

/-- **(1) psi = two conditions.** A word is hub-exact with prefix `M` iff (a) the non-V G0 rows hit
their targets and (b) the V-ending row spans agree (one invertible V mix). This is
`HubSettle.valid_iff`, restated with the conditions named as in RC8 sec. 1. -/
theorem psi_two_conditions (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (Rn : Matrix G1 N K)
    (R0 : Matrix G1 G0 K) {NV : Type*} [Fintype NV] [DecidableEq NV] (Rn0 Fn0 : Matrix NV G0 K)
    (M : Matrix G0 G0 K) :
    Valid Xn X0 Rn R0 Rn0 Fn0 M ↔
      Rn0 * M = Fn0 ∧ span K (Set.range (fromCols Xn (X0 * M)).row)
        = span K (Set.range (fromCols Rn R0).row) := by
  rw [valid_iff, P, Q, range_vecMulLinear, range_vecMulLinear]

end Exact

/-! ## Part 2. The span law -/

section Span
variable {K G ι : Type*} [Field K] [DecidableEq G]

/-- Remove from register `r`'s end row the content `w` (the removed op's gift). -/
def strip (X : Matrix G ι K) (r : G) (w : ι → K) : Matrix G ι K := X.updateRow r (X r - w)

theorem strip_row_self (X : Matrix G ι K) (r : G) (w : ι → K) : (strip X r w).row r = X.row r - w := by
  simp [strip, Matrix.row]

theorem strip_row_ne (X : Matrix G ι K) (r : G) (w : ι → K) (g : G) (h : g ≠ r) :
    (strip X r w).row g = X.row g := by
  simp [strip, Matrix.row, h]

/-- **SPAN LAW (pure linear algebra).** Removing `w` from one end row leaves the V-ending row span
unchanged (so a V settle can still exist, `vmixM_iff_span`) iff `w` lies in BOTH the old and the
new span. -/
theorem span_strip_iff (X : Matrix G ι K) (r : G) (w : ι → K) :
    span K (Set.range (strip X r w).row) = span K (Set.range X.row) ↔
      w ∈ span K (Set.range X.row) ∧ w ∈ span K (Set.range (strip X r w).row) := by
  constructor
  · intro h
    have h1 : X.row r ∈ span K (Set.range X.row) := subset_span ⟨r, rfl⟩
    have h2 : (strip X r w).row r ∈ span K (Set.range X.row) := h ▸ subset_span ⟨r, rfl⟩
    have hw : w ∈ span K (Set.range X.row) := by
      have := sub_mem h1 h2
      rwa [strip_row_self, sub_sub_cancel] at this
    exact ⟨hw, h ▸ hw⟩
  · rintro ⟨hw, hw'⟩
    apply le_antisymm
    · rw [span_le]
      rintro _ ⟨g, rfl⟩
      by_cases hg : g = r
      · subst hg; rw [strip_row_self]
        exact sub_mem (subset_span ⟨g, rfl⟩) hw
      · rw [strip_row_ne _ _ _ _ hg]; exact subset_span ⟨g, rfl⟩
    · rw [span_le]
      rintro _ ⟨g, rfl⟩
      by_cases hg : g = r
      · subst hg
        have : X.row g = (strip X g w).row g + w := by rw [strip_row_self]; abel
        rw [this]; exact add_mem (subset_span ⟨g, rfl⟩) hw'
      · have := strip_row_ne X r w g hg
        rw [← this]; exact subset_span ⟨g, rfl⟩

/-- Necessity half in the form RC8 states it: if the stripped row set still spans the old span,
then `w` is in the old span ("w must lie in the G1 span"). -/
theorem span_law_necessary (X : Matrix G ι K) (r : G) (w : ι → K)
    (h : span K (Set.range (strip X r w).row) = span K (Set.range X.row)) :
    w ∈ span K (Set.range X.row) := ((span_strip_iff X r w).1 h).1

/-- **RC8 sec. 1 "only if" is NOT an "if".** `w` in the old span does not make the removal
repairable: with a single end row `(1)` and `w = (1)` the stripped row is `0`. The corrected
statement is `span_strip_iff` (w must also lie in the stripped span, i.e. the main's own row
must remain recoverable). -/
theorem span_law_not_sufficient :
    ∃ (X : Matrix (Fin 1) (Fin 1) ℚ) (w : Fin 1 → ℚ),
      w ∈ span ℚ (Set.range X.row) ∧
        span ℚ (Set.range (strip X 0 w).row) ≠ span ℚ (Set.range X.row) := by
  refine ⟨!![1], fun _ => 1, ?_, ?_⟩
  · exact subset_span ⟨0, by ext j; fin_cases j; simp [Matrix.row]⟩
  · intro h
    have h1 := ((span_strip_iff (!![1] : Matrix (Fin 1) (Fin 1) ℚ) 0 (fun _ => 1)).1 h).2
    have hz : (strip (!![1] : Matrix (Fin 1) (Fin 1) ℚ) 0 (fun _ => 1)).row = fun _ => 0 := by
      funext g; fin_cases g; ext j; fin_cases j; simp [strip, Matrix.row]
    rw [hz] at h1
    have : span ℚ (Set.range (fun _ : Fin 1 => (0 : Fin 1 → ℚ))) = ⊥ := by
      rw [eq_bot_iff, span_le]; rintro _ ⟨g, rfl⟩; simp
    rw [this, mem_bot] at h1
    have := congrFun h1 0
    simp at this

end Span

section SpanPrefix
variable {K N G0 G1 : Type*} [Field K] [Fintype N] [Fintype G0] [Fintype G1]
  [DecidableEq N] [DecidableEq G0] [DecidableEq G1]

theorem fromCols_strip (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (M : Matrix G0 G0 K) (r : G1)
    (wn : N → K) (w0 : G0 → K) :
    fromCols (strip Xn r wn) (strip X0 r w0 * M) =
      strip (fromCols Xn (X0 * M)) r (Sum.elim wn (w0 ᵥ* M)) := by
  ext g c
  by_cases hg : g = r
  · subst hg
    rcases c with n | c
    · simp [strip]
    · simp [strip, Matrix.mul_apply, Matrix.vecMul, dotProduct, sub_mul, Finset.sum_sub_distrib]
  · rcases c with n | c
    · simp [strip, hg]
    · simp [strip, hg, Matrix.mul_apply]

/-- **SPAN LAW with the prefix constraint.** Let `M` be a prefix at which the native is exact
(`P M = Q`, the V-ending rows span the targets). Remove content `w = (w_n | w_0)` from main `r`'s
end row; in the prefix model its G0 part is carried by the same `M`, giving `ŵ = (w_n | w_0 M)`.
The hub-only repair (same prefix, one V mix) exists iff `ŵ ∈ span(targets)` and `ŵ` is in the
stripped span. In particular `ŵ ∈ span(targets) = span(V-ending rows)` is NECESSARY. -/
theorem span_law_prefix (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (Rn : Matrix G1 N K)
    (R0 : Matrix G1 G0 K) (M : Matrix G0 G0 K) (r : G1) (wn : N → K) (w0 : G0 → K)
    (hnat : span K (Set.range (fromCols Xn (X0 * M)).row) = span K (Set.range (fromCols Rn R0).row)) :
    VMixM (fromCols (strip Xn r wn) (strip X0 r w0 * M)) (fromCols Rn R0) ↔
      Sum.elim wn (w0 ᵥ* M) ∈ span K (Set.range (fromCols Rn R0).row) ∧
      Sum.elim wn (w0 ᵥ* M) ∈ span K (Set.range
        (fromCols (strip Xn r wn) (strip X0 r w0 * M)).row) := by
  rw [vmixM_iff_span, fromCols_strip, ← hnat]
  exact span_strip_iff _ _ _ |>.trans (by rw [hnat])

theorem span_law_prefix_necessary (Xn : Matrix G1 N K) (X0 : Matrix G1 G0 K) (Rn : Matrix G1 N K)
    (R0 : Matrix G1 G0 K) (M : Matrix G0 G0 K) (r : G1) (wn : N → K) (w0 : G0 → K)
    (hnat : span K (Set.range (fromCols Xn (X0 * M)).row) = span K (Set.range (fromCols Rn R0).row))
    (h : VMixM (fromCols (strip Xn r wn) (strip X0 r w0 * M)) (fromCols Rn R0)) :
    Sum.elim wn (w0 ᵥ* M) ∈ span K (Set.range (fromCols Rn R0).row) :=
  ((span_law_prefix Xn X0 Rn R0 M r wn w0 hnat).1 h).1

end SpanPrefix

/-! ### Corollary: an unshed carrier -/

section Carrier
variable {K G ι : Type*} [Field K] [Fintype G] [DecidableEq G]

/-- A carrier `k` whose V-end row is its own target `R k` plus the content `x` it still holds
makes the V settle consistent only if `x` is in the target span. -/
theorem unshed_forces_span (E R : Matrix G ι K) (h : VMixM E R) (k : G) (x : ι → K)
    (hk : E k = R k + x) : x ∈ span K (Set.range R.row) := by
  rw [vmixM_iff_span] at h
  have h1 : E.row k ∈ span K (Set.range R.row) := h ▸ subset_span ⟨k, rfl⟩
  have h2 : R.row k ∈ span K (Set.range R.row) := subset_span ⟨k, rfl⟩
  have := sub_mem h1 h2
  have e : E.row k - R.row k = x := by
    show E k - R k = x
    rw [hk]; abel
  rwa [e] at this

/-- Non-vacuity, both halves, over `ℚ`: main target `(1,0,0)`, carrier target `(0,1,0)`,
content `x = (0,0,1)` outside the span. Unshed (carrier ends at `(0,1,1)`, main at `(1,1,0)`):
NO V settle. Shed (carrier ends at its target): a V settle exists. -/
def Rt : Matrix (Fin 2) (Fin 3) ℚ := !![1, 0, 0; 0, 1, 0]
def Eun : Matrix (Fin 2) (Fin 3) ℚ := !![1, 1, 0; 0, 1, 1]
def Esh : Matrix (Fin 2) (Fin 3) ℚ := !![1, 1, 0; 0, 1, 0]

theorem unshed_inconsistent : ¬ VMixM Eun Rt := by
  intro h
  have := unshed_forces_span Eun Rt h 1 (![0, 0, 1])
    (by ext j; fin_cases j <;> simp [Eun, Rt])
  have hle : span ℚ (Set.range Rt.row) ≤ LinearMap.ker (LinearMap.proj (R := ℚ) (φ := fun _ : Fin 3 => ℚ) 2) := by
    rw [span_le]; rintro _ ⟨g, rfl⟩
    fin_cases g <;> simp [Rt, Matrix.row]
  have := hle this
  simp at this

theorem shed_consistent : VMixM Esh Rt := by
  refine ⟨!![1, -1; 0, 1], ?_, ?_⟩
  · simp [Matrix.det_fin_two]
  · ext i j; fin_cases i <;> fin_cases j <;> simp [Esh, Rt, Matrix.mul_apply, Fin.sum_univ_two]

end Carrier

/-! ### Corollary: pick -> deliver -> shed needs three meetings -/

section Meetings
variable {K : Type*} [Field K]

/-- A courier's contacts: `pick a` = meeting an x-holder, courier content += a;
`give b` = meeting the main, main receives `b * content`. -/
inductive CEv (K : Type*)
  | pick (a : K)
  | give (b : K)

/-- state = (courier's x-content, total x delivered to the main) -/
def cstep : K × K → CEv K → K × K
  | (c, d), .pick a => (c + a, d)
  | (c, d), .give b => (c, d + b * c)

def crun (st : K × K) (l : List (CEv K)) : K × K := l.foldl cstep st

theorem content_nopick (l : List (CEv K)) (st : K × K) (h : ∀ e ∈ l, ∀ a, e ≠ .pick a) :
    (crun st l).1 = st.1 := by
  induction l generalizing st with
  | nil => rfl
  | cons e es ih =>
    simp only [crun, List.foldl_cons] at ih ⊢
    have h1 := ih (cstep st e) (fun e' he' => h e' (List.mem_cons_of_mem _ he'))
    rw [h1]
    cases e with
    | pick a => exact absurd rfl (h _ List.mem_cons_self a)
    | give b => rfl

theorem exists_pick (l : List (CEv K)) (st : K × K) (h : (crun st l).1 ≠ st.1) :
    ∃ l1 a l2, l = l1 ++ .pick a :: l2 := by
  by_contra hc
  apply h
  apply content_nopick
  intro e he a hea
  subst hea
  obtain ⟨l1, l2, hl⟩ := List.append_of_mem he
  exact hc ⟨l1, a, l2, hl⟩

theorem exists_give (l : List (CEv K)) (st : K × K) (h : (crun st l).2 ≠ st.2) :
    ∃ l1 b l2, l = l1 ++ .give b :: l2 ∧ b * (crun st l1).1 ≠ 0 := by
  induction l generalizing st with
  | nil => exact absurd rfl h
  | cons e es ih =>
    simp only [crun, List.foldl_cons] at h ih ⊢
    by_cases h2 : (List.foldl cstep (cstep st e) es).2 = (cstep st e).2
    · cases e with
      | pick a => exact absurd h2 (by simpa [cstep] using h)
      | give b =>
        refine ⟨[], b, es, rfl, ?_⟩
        intro hb; apply h; rw [h2]; simpa [cstep] using hb
    · obtain ⟨l1, b, l2, hl, hb⟩ := ih (cstep st e) h2
      exact ⟨e :: l1, b, l2, by rw [hl]; rfl, hb⟩

/-- **Three meetings.** A courier that starts and ends with x-content 0 and delivers a nonzero
total `x` to the main must (in this order) pick, give, and then shed. So a repairing carrier has
at least three meetings (pick -> deliver -> shed), matching TWO-STOP (Delivery.two_contacts_needed:
>= 2 contacts with different courier rows) with the pick/shed contacts counted separately. -/
theorem three_meetings (l : List (CEv K)) (h0 : (crun (0, 0) l).1 = 0) (hd : (crun (0, 0) l).2 ≠ 0) :
    ∃ l1 a l2 b l3 a' l4, l = l1 ++ .pick a :: (l2 ++ .give b :: (l3 ++ .pick a' :: l4)) ∧
      b ≠ 0 := by
  obtain ⟨m1, b, m2, hl, hb⟩ := exists_give l (0, 0) hd
  have hc : (crun (0, 0) m1).1 ≠ 0 := fun h => hb (by rw [h, mul_zero])
  obtain ⟨l1, a, l2, h1⟩ := exists_pick m1 (0, 0) hc
  have hcs : ∀ (st : K × K) (b : K), (cstep st (CEv.give b)).1 = st.1 := by
    intro st b; rcases st with ⟨c, d⟩; rfl
  have hrun : crun (0, 0) (m1 ++ CEv.give b :: m2) = crun (cstep (crun (0, 0) m1) (CEv.give b)) m2 := by
    simp [crun, List.foldl_append]
  have hfin : (crun (cstep (crun (0, 0) m1) (CEv.give b)) m2).1 = 0 := by
    rw [← hrun, ← hl]; exact h0
  have hne : (crun (cstep (crun (0, 0) m1) (CEv.give b)) m2).1 ≠
      (cstep (crun (0, 0) m1) (CEv.give b)).1 := by
    rw [hfin, hcs]; exact fun h => hc h.symm
  obtain ⟨l3, a', l4, h2⟩ := exists_pick m2 _ hne
  refine ⟨l1, a, l2, b, l3, a', l4, ?_, ?_⟩
  · rw [hl, h1, h2]; simp
  · intro hb0; apply hb; rw [hb0, zero_mul]

end Meetings

/-! ## Part 3. Exposed reads: no single prefix transform -/

section Exposure
open TokenCancel
variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]

/-- A right multiplication preserves linear relations among rows. -/
theorem relation_obstruction {m n : Type*} [Fintype m] [Fintype n] [DecidableEq n]
    (Eold Enew : Matrix m n K) (y : m → K) (h0 : y ᵥ* Eold = 0) (h1 : y ᵥ* Enew ≠ 0) :
    ¬ ∃ M : Matrix n n K, Eold * M = Enew := by
  rintro ⟨M, rfl⟩
  apply h1
  rw [← Matrix.vecMul_vecMul, h0, Matrix.zero_vecMul]

/-- **Swap law.** The op `p += q*o` commutes with a later `i += a*j` unless the later op READS
`p` (`j = p`) or WRITES `o` (`i = o`). Reading `o` is harmless. -/
theorem add_swap (s : St K Reg C) (p o i j : Reg) (q a : K) (c c' : C)
    (hj : j ≠ p) (hio : i ≠ o) :
    step (step s (.add p o q c)) (.add i j a c') = step (step s (.add i j a c')) (.add p o q c) := by
  simp only [step, St.mk.injEq, and_true]
  funext r
  by_cases hr : r = p <;> by_cases hr' : r = i
  · subst hr; subst hr'; simp [Function.update_apply, hj, hio.symm]; abel
  · subst hr; simp [Function.update_apply, hr', hj, hio.symm]
  · subst hr'; simp [Function.update_apply, hr, hio, hio.symm, hj]
  · simp [Function.update_apply, hr, hr']

/-- **Positive half.** If every event between the new and old time of the op `p += q*o` is an ADD
that neither reads `p` nor writes `o`, the op can be moved earlier with identical final state. -/
theorem move_early (p o : Reg) (q : K) (c : C) (l : List (Ev K Reg C))
    (hl : ∀ e ∈ l, ∃ i j a c', e = .add i j a c' ∧ j ≠ p ∧ i ≠ o) (s : St K Reg C) :
    run (step s (.add p o q c)) l = step (run s l) (.add p o q c) := by
  induction l generalizing s with
  | nil => rfl
  | cons e es ih =>
    obtain ⟨i, j, a, c', rfl, hj, hio⟩ := hl e List.mem_cons_self
    simp only [run]
    rw [add_swap s p o i j q a c c' hj hio]
    exact ih (fun e' he' => hl e' (List.mem_cons_of_mem _ he')) _

/-- The three-register witness: `r = 0`, `o = 1`, reader `u = 2`; the op `r += q*o`
at the old time (after the read) or relocated before the read. -/
def evsOld (q a : K) : List (Ev K (Fin 3) Unit) :=
  [.born 0 (), .born 1 (), .init 2 (), .add 2 0 a (), .add 0 1 q ()]

def evsNew (q a : K) : List (Ev K (Fin 3) Unit) :=
  [.born 0 (), .born 1 (), .init 2 (), .add 0 1 q (), .add 2 0 a ()]

theorem rows_old (q a : K) :
    (run (TokenCancel.start : St K (Fin 3) Unit) (evsOld q a)).row =
      ![Pi.single 0 1 + q • Pi.single 1 1, Pi.single 1 1, a • Pi.single 0 1] := by
  funext r; fin_cases r <;> simp [evsOld, run, step, TokenCancel.start]

theorem rows_new (q a : K) :
    (run (TokenCancel.start : St K (Fin 3) Unit) (evsNew q a)).row =
      ![Pi.single 0 1 + q • Pi.single 1 1, Pi.single 1 1,
        a • (Pi.single 0 1 + q • Pi.single 1 1)] := by
  funext r; fin_cases r <;> simp [evsNew, run, step, TokenCancel.start]

/-- **(3) The exposure obstruction.** Relocating `r += q*o` before a read of `r` by `u` changes
the end rows by `a q o_0` on `u` only. The end rows satisfy the relation `a r - a q o - u = 0`
before and not after, so NO matrix `M` (a fortiori no invertible prefix on the G0 columns)
carries the old end rows to the new ones. -/
theorem exposed_read_no_prefix (q a : K) (hq : q ≠ 0) (ha : a ≠ 0) :
    ¬ ∃ M : Matrix (Fin 3) (Fin 3) K,
      (Matrix.of (run (TokenCancel.start : St K (Fin 3) Unit) (evsOld q a)).row) * M =
        Matrix.of (run (TokenCancel.start : St K (Fin 3) Unit) (evsNew q a)).row := by
  apply relation_obstruction _ _ ![a, -(a * q), -1]
  · funext j
    rw [rows_old]
    fin_cases j <;> simp [Matrix.vecMul, dotProduct, Fin.sum_univ_three, Pi.single_apply] <;> ring
  · intro h
    have := congrFun h 1
    rw [rows_new] at this
    simp [Matrix.vecMul, dotProduct, Fin.sum_univ_three, Pi.single_apply] at this
    rcases this with h | h <;> simp_all

end Exposure

end PsiLaw

#print axioms PsiLaw.psi_two_conditions
#print axioms PsiLaw.span_strip_iff
#print axioms PsiLaw.span_law_not_sufficient
#print axioms PsiLaw.span_law_prefix
#print axioms PsiLaw.unshed_forces_span
#print axioms PsiLaw.unshed_inconsistent
#print axioms PsiLaw.shed_consistent
#print axioms PsiLaw.three_meetings
#print axioms PsiLaw.add_swap
#print axioms PsiLaw.move_early
#print axioms PsiLaw.exposed_read_no_prefix
