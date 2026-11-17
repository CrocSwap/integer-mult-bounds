/-
V2FloorNativeTab2 (lane LEAN-NEXT21, Nov 16): faster DFS state for the native route. A subspace is carried as its list of
member masks `ms` (Rep'), the 512-bit table is rebuilt from it (`tabOf`), and children are generated through the submasks of
the free positions (`subs`) instead of scanning 2^j candidates. `enum_all'` is `enum_all` for this state.
No native_decide here.
-/
import Nov15.V2FloorNativeTab

namespace V2Floor
open Finset Module
attribute [local instance] Classical.propDecidable
set_option maxHeartbeats 2000000

/-- ms lists exactly the members of S (as masks < 512). -/
def Rep' (ms : List ℕ) (S : Sub) : Prop := (∀ v ∈ ms, v < 512) ∧ ∀ v < 512, v ∈ ms ↔ vec v ∈ S

def addv' (ms : List ℕ) (w : ℕ) : List ℕ := ms ++ ms.map (· ^^^ w)

theorem Rep'_bot : Rep' [0] ⊥ := by
  refine ⟨by simp, fun v hv => ?_⟩
  rw [List.mem_singleton, Submodule.mem_bot]
  constructor
  · rintro rfl; exact vec_zero
  · intro h; exact vec_inj hv (by norm_num) (h.trans vec_zero.symm)

theorem Rep'_add {ms : List ℕ} {w : ℕ} {S : Sub} (h : Rep' ms S) (hw : w < 512) :
    Rep' (addv' ms w) (S ⊔ Submodule.span (ZMod 2) {vec w}) := by
  have hx : ∀ v, v < 512 → (v ^^^ w) < 512 := fun v hv => by
    have := Nat.xor_lt_two_pow (n := 9) (x := v) (y := w) (by norm_num; omega) (by norm_num; omega)
    norm_num at this; exact this
  refine ⟨?_, fun v hv => ?_⟩
  · intro v hv
    simp only [addv', List.mem_append, List.mem_map] at hv
    rcases hv with hv | ⟨u, hu, rfl⟩
    · exact h.1 v hv
    · exact hx u (h.1 u hu)
  · rw [mem_sup_vec, ← h.2 v hv, ← h.2 _ (hx v hv)]
    simp only [addv', List.mem_append, List.mem_map]
    constructor
    · rintro (h1 | ⟨u, hu, rfl⟩)
      · exact Or.inl h1
      · right; simpa [Nat.xor_assoc] using hu
    · rintro (h1 | h1)
      · exact Or.inl h1
      · right; exact ⟨v ^^^ w, h1, by simp [Nat.xor_assoc]⟩

/-- 512-bit table of a member list. -/
def tabOf (ms : List ℕ) : ℕ := ms.foldl (fun a v => a ||| (1 <<< v)) 0

theorem foldl_or_testBit (ms : List ℕ) (a k : ℕ) :
    (ms.foldl (fun a v => a ||| (1 <<< v)) a).testBit k = (a.testBit k || decide (k ∈ ms)) := by
  induction ms generalizing a with
  | nil => simp
  | cons v ms ih =>
    simp only [List.foldl_cons, ih, Nat.testBit_or, testBit_one_shl, List.mem_cons]
    by_cases h : v = k
    · subst h; simp
    · have h' : ¬ k = v := fun e => h e.symm
      by_cases h2 : a.testBit k = true <;> simp [h, h', h2]

theorem tabOf_lt {ms : List ℕ} (h : ∀ v ∈ ms, v < 512) : tabOf ms < 2 ^ 512 := by
  apply Nat.lt_pow_two_of_testBit
  intro i hi
  unfold tabOf
  rw [foldl_or_testBit]
  have : i ∉ ms := fun hm => by have := h i hm; omega
  simp [this]

/-- the table is a Rep. -/
def RepT (t : ℕ) (S : Sub) : Prop := t < 2 ^ 512 ∧ ∀ v < 512, t.testBit v = decide (vec v ∈ S)

theorem RepT_of_Rep' {ms : List ℕ} {S : Sub} (h : Rep' ms S) : RepT (tabOf ms) S := by
  refine ⟨tabOf_lt h.1, fun v hv => ?_⟩
  unfold tabOf
  rw [foldl_or_testBit]
  simp only [Nat.zero_testBit, Bool.false_or]
  rw [Bool.eq_iff_iff, decide_eq_true_iff, decide_eq_true_iff]
  exact h.2 v hv

/-- submasks of f below bit i. -/
def subs (f : ℕ) : ℕ → List ℕ
  | 0 => [0]
  | i + 1 => if f.testBit i then subs f i ++ (subs f i).map (· ||| 2 ^ i) else subs f i

theorem mem_subs (f : ℕ) : ∀ i r, r < 2 ^ i → (∀ b < i, r.testBit b = true → f.testBit b = true) → r ∈ subs f i := by
  intro i
  induction i with
  | zero => intro r hr _; simp at hr; simp [subs, hr]
  | succ i ih =>
    intro r hr hb
    simp only [subs]
    by_cases hbit : r.testBit i = true
    · have hf : f.testBit i = true := hb i (by omega) hbit
      simp only [hf, if_true, List.mem_append, List.mem_map]
      right
      refine ⟨r ^^^ 2 ^ i, ih _ ?_ ?_, ?_⟩
      · have := clear_bit (x := r) (j := i) hr (fun h => by
          have := bits_of_lt h i le_rfl; simp [this] at hbit)
        exact this
      · intro b hb' hbt
        apply hb b (by omega)
        rw [Nat.testBit_xor, Nat.testBit_two_pow] at hbt
        by_cases hh : i = b
        · omega
        · simpa [hh] using hbt
      · apply Nat.eq_of_testBit_eq
        intro b
        simp only [Nat.testBit_or, Nat.testBit_xor, Nat.testBit_two_pow]
        by_cases hh : i = b
        · subst hh; simp [hbit]
        · simp [hh]
    · have hr' : r < 2 ^ i := by
        apply lt_two_pow_of_bits
        intro b hbb
        rcases Nat.eq_or_lt_of_le hbb with h | h
        · subst h; simpa using hbit
        · exact bits_of_lt hr b h
      have := ih r hr' (fun b hb' => hb b (by omega))
      by_cases hf : f.testBit i = true
      · simp only [hf, if_true, List.mem_append]; exact Or.inl this
      · simp only [hf, if_false]; exact this

def go' (chk : List ℕ → ℕ → Bool) : ℕ → ℕ → List ℕ → ℕ → ℕ → Bool
  | 0, _, ms, _, n => chk ms n
  | k + 1, j, ms, l, n =>
    go' chk k (j + 1) ms l n &&
    (subs ((2 ^ j - 1) ^^^ l) j).all (fun r => go' chk k (j + 1) (addv' ms (2 ^ j ||| r)) (l ||| 2 ^ j) (n + 1))

theorem go_sound' (chk : List ℕ → ℕ → Bool) : ∀ k j ms l n (S : Sub), Rep' ms S → l < 2 ^ j → j + k = 9 →
    go' chk k j ms l n = true → ∀ S2 l2 n2,
      Relation.ReflTransGen Step ⟨j, S, l, n⟩ ⟨9, S2, l2, n2⟩ → ∃ ms2, Rep' ms2 S2 ∧ chk ms2 n2 = true := by
  intro k
  induction k with
  | zero =>
    intro j ms l n S hrep hl hj hgo S2 l2 n2 hr
    simp only [go'] at hgo
    rcases Relation.ReflTransGen.cases_head hr with h | ⟨c, hs, _⟩
    · simp only [St.mk.injEq] at h
      obtain ⟨_, rfl, _, rfl⟩ := h
      exact ⟨ms, hrep, hgo⟩
    · cases hs <;> omega
  | succ k ih =>
    intro j ms l n S hrep hl hj hgo S2 l2 n2 hr
    have hj9 : j < 9 := by omega
    simp only [go', Bool.and_eq_true, List.all_eq_true] at hgo
    rcases Relation.ReflTransGen.cases_head hr with h | ⟨c, hs, hrest⟩
    · simp only [St.mk.injEq] at h; omega
    · cases hs with
      | skip _ _ _ _ _ =>
        exact ih (j + 1) ms l n S hrep (lt_of_lt_of_le hl (Nat.pow_le_pow_right (by norm_num) (by omega)))
          (by omega) hgo.1 S2 l2 n2 hrest
      | add _ _ _ _ r _ hr2 hrl =>
        have hmem : r ∈ subs ((2 ^ j - 1) ^^^ l) j := by
          apply mem_subs _ _ _ hr2
          intro b hb hbt
          rw [Nat.testBit_xor, Nat.testBit_two_pow_sub_one]
          have : l.testBit b = false := by
            by_contra hc
            have hc' : l.testBit b = true := by simpa using hc
            have : (r &&& l).testBit b = true := by rw [Nat.testBit_and]; simp [hbt, hc']
            rw [hrl] at this; simp at this
          simp [hb, this]
        have h := hgo.2 r hmem
        have hw : (2 ^ j ||| r) < 512 := by
          have := pow_succ_le hj9
          have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
          have : (2 ^ j ||| r) < 2 ^ (j + 1) := by
            rw [or_eq_xor hr2]; apply xor_lt' <;> omega
          omega
        exact ih (j + 1) _ _ _ _ (Rep'_add hrep hw) (Nat.or_lt_two_pow (by
          have := pow_succ_le hj9; have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
          omega) (by have hp : 2 ^ (j + 1) = 2 * 2 ^ j := by rw [pow_succ]; ring
                     omega)) (by omega) h S2 l2 n2 hrest

theorem enum_all' (chk : List ℕ → ℕ → Bool) (h : go' chk 9 0 [0] 0 0 = true) :
    ∀ S : Sub, ∃ ms n, Rep' ms S ∧ fdim S = n ∧ chk ms n = true := by
  intro S
  obtain ⟨l, n, hr⟩ := complete 9 le_rfl S (fun v hv _ => by simpa using hv)
  have hinv := inv_rtg hr inv_init
  obtain ⟨ms2, hms2, hc⟩ := go_sound' chk 9 0 [0] 0 0 ⊥ Rep'_bot (by norm_num) rfl h S l n hr
  exact ⟨ms2, n, hms2, hinv.2.2.1, hc⟩

end V2Floor
