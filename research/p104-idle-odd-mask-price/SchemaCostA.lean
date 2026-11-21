/-
SchemaCostA (lane SCHEMACOST, Nov 20).  Part A: the J-schema hypothesis (`JB` / `JA`) of the caller laws is DERIVED from the
verifier's record grammar.

Source (data, not run): the `validate` of the mixed-root-caller/1 verifier (operator_ring.py, imb-native research/p104-query-only-interval/vendor):
  * the event list is [plain events and J records]; J records carry stages `stages == [1..L]` in order ("fresh ordered joint stages"),
    hence: exactly one J per stage, in call order, and the word is   P_0 J_0 P_1 J_1 ... P_{L-1} J_{L-1} P_L   (plain blocks P_c);
  * J record = A-part [x,y,u,v] (pairwise distinct, "joint distinct fields") and B-part [s,t,al,be] (s /= t), with the exact gauge
    al = -1, be = 1/2 ("exact hosted gauge") and the exact HOST2 coefficients alpha2 = -1, beta2 = 0;
  * diagonal targets `dg[:2] == [-1, 0]`  (q-exponent -1: ODD targets), masks in {0,1}.
The A-part and B-part act on disjoint register ranges, so each type is a caller word by itself (CALLERWORD §3); a J record of that
word is the macro `jA` resp. `jB` of CallerWord.
Here: `GramB` / `GramA` = a one-type record word (the normal form above); `GramB.jb` / `GramA.ja` build the schema; the headline caller laws
are restated with NO schema hypothesis and NO odd-target hypothesis.
Kernel only.
-/
import Nov15.CallerJASchema

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace SchemaCost
open Finset Matrix CallerSign CallerWord CallerAsm

/-! ## block lists -/
section blocks
variable {α : Type*}

def blocks (f : ℕ → List α) (k : ℕ) : List α := (List.range k).flatMap f

theorem blocks_succ (f : ℕ → List α) (k : ℕ) : blocks f (k + 1) = blocks f k ++ f k := by
  simp [blocks, List.range_succ]

theorem blocks_split (f : ℕ → List α) (k s : ℕ) (hs : s < k) (post : List α) :
    ∃ R, blocks f k ++ post = blocks f s ++ f s ++ R := by
  induction k generalizing post with
  | zero => omega
  | succ k ih =>
    rcases Nat.lt_succ_iff_lt_or_eq.mp hs with h | h
    · obtain ⟨R, hR⟩ := ih h (f k ++ post)
      exact ⟨R, by rw [blocks_succ, List.append_assoc, hR]⟩
    · subst h; exact ⟨post, by rw [blocks_succ]⟩

theorem blocks_length_mono (f : ℕ → List α) {s t : ℕ} (h : s ≤ t) :
    (blocks f s).length ≤ (blocks f t).length := by
  induction t, h using Nat.le_induction with
  | base => exact le_rfl
  | succ t _ ih => rw [blocks_succ, List.length_append]; omega

end blocks

/-! ## one-type record word (normal form of the validated caller) -/

/-- a one-type caller in block normal form: plain blocks `pre c` before the J record of stage `c`, a final plain block, `jx c` the
macro-expansion of the stage-`c` J record. -/
structure Blk (n k : ℕ) where
  pre : Fin k → List (Ev n k)
  jx : Fin k → List (Ev n k)
  post : List (Ev n k)
  ex : Fin n → ℤ
  mask : Fin n → Finset (Fin k)

namespace Blk
variable {n k : ℕ} (B : Blk n k)

def f (c : ℕ) : List (Ev n k) := if h : c < k then B.pre ⟨c, h⟩ ++ B.jx ⟨c, h⟩ else []

def evs : List (Ev n k) := blocks B.f k ++ B.post

def word : CWord n k := ⟨B.evs, B.ex, B.mask⟩

def pos (s : Fin k) : ℕ := (blocks B.f s.val).length + (B.pre s).length

theorem f_fin (s : Fin k) : B.f s.val = B.pre s ++ B.jx s := by simp [f, s.isLt]

theorem split (s : Fin k) : ∃ R, B.evs = blocks B.f s.val ++ B.pre s ++ B.jx s ++ R := by
  obtain ⟨R, hR⟩ := blocks_split B.f k s.val s.isLt B.post
  exact ⟨R, by simp only [evs]; rw [hR, B.f_fin]; simp [List.append_assoc]⟩

theorem len_ge (s : Fin k) : B.pos s + (B.jx s).length ≤ B.evs.length := by
  obtain ⟨R, hR⟩ := B.split s
  rw [hR]; simp [pos]; omega

theorem get_jx (s : Fin k) (i : ℕ) (hi : i < (B.jx s).length) :
    ∃ h : B.pos s + i < B.evs.length, B.evs[B.pos s + i] = (B.jx s)[i] := by
  obtain ⟨R, hR⟩ := B.split s
  have h1 : (blocks B.f s.val ++ B.pre s).length = B.pos s := by simp [pos]
  have e1 : B.evs = (blocks B.f s.val ++ B.pre s) ++ (B.jx s ++ R) := by
    rw [hR]; simp [List.append_assoc]
  have h2 : B.evs[B.pos s + i]? = some (B.jx s)[i] := by
    rw [e1, List.getElem?_append_right (by omega)]
    rw [show B.pos s + i - (blocks B.f s.val ++ B.pre s).length = i by omega,
      List.getElem?_append_left hi]
    simp
  exact List.getElem?_eq_some_iff.mp h2

theorem get_jx' (s : Fin k) (i : ℕ) (e : Ev n k) (he : (B.jx s)[i]? = some e)
    (h : B.pos s + i < B.evs.length) : B.evs.get ⟨B.pos s + i, h⟩ = e := by
  obtain ⟨hi, he'⟩ := List.getElem?_eq_some_iff.mp he
  obtain ⟨h2, h3⟩ := B.get_jx s i hi
  simpa [List.get_eq_getElem, h3, he'] using (show B.evs[B.pos s + i] = e from h3.trans he')

theorem pos_gap (s t : Fin k) (h : s < t) : B.pos s + (B.jx s).length ≤ B.pos t := by
  have h1 : (blocks B.f (s.val + 1)).length = B.pos s + (B.jx s).length := by
    rw [blocks_succ, B.f_fin]; simp [pos]; omega
  have h2 := blocks_length_mono B.f (show s.val + 1 ≤ t.val from h)
  simp only [pos] at *
  omega

end Blk

/-! ## type B -/

structure GramB (n k : ℕ) where
  pre : Fin k → List (Ev n k)
  post : List (Ev n k)
  u : Fin k → Fin n
  v : Fin k → Fin n
  uv : ∀ s, u s ≠ v s
  ex : Fin n → ℤ
  mask : Fin n → Finset (Fin k)
  ex_eq : ∀ r, ex r = -1

namespace GramB
variable {n k : ℕ} (G : GramB n k)

def blk : Blk n k where
  pre := G.pre
  jx := fun s => jB s (G.u s) (G.v s) (-1) (1 / 2)
  post := G.post
  ex := G.ex
  mask := G.mask

def word : CWord n k := G.blk.word

theorem jx_len (s : Fin k) : (G.blk.jx s).length = 3 := by simp [blk, jB]

theorem hodd : ∀ r, G.word.ex r % 2 = 1 := by
  intro r; show G.ex r % 2 = 1; rw [G.ex_eq]; norm_num

def jb : JB G.word where
  pos := G.blk.pos
  mono := by
    intro s t h
    have := G.blk.pos_gap s t h
    rw [G.jx_len s] at this
    show G.blk.pos s < G.blk.pos t
    omega
  lt := by
    intro s
    have := G.blk.len_ge s
    rw [G.jx_len s] at this
    show G.blk.pos s + 2 < G.blk.evs.length
    omega
  u := G.u
  v := G.v
  a := fun _ => -1
  b := fun _ => 1 / 2
  a0 := fun _ => by norm_num
  b0 := fun _ => by norm_num
  uv := G.uv
  h0 := fun s => G.blk.get_jx' s 0 _ (by simp [blk, jB]) _
  h1 := fun s => G.blk.get_jx' s 1 _ (by simp [blk, jB]) _
  h2 := fun s => G.blk.get_jx' s 2 _ (by simp [blk, jB]) _

end GramB


section headlinesB
open CallerHP CallerBridge
variable {n k : ℕ} (G : GramB n k)

/-- HEADLINE B (Q = 0): NO schema and NO odd-target hypothesis (both come from the grammar). -/
theorem gramB_hp (hL : Legal G.word) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota G.word) = 2 * k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.jb.col s) (G.jb.col s)).det)
    (hdeg : ∀ r, 2 ≤ (G.word.mask r).card) :
    cHat G.word ≤ HPr k :=
  word_hp_B hL G.jb G.hodd hk hQ0 hn hlam hdeg

/-- HEADLINE B (thin columns allowed). -/
theorem gramB_hpq (hL : Legal G.word) (hk : 77 ≤ k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.jb.col s) (G.jb.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (G.word.mask r).card) :
    cHatQ G.word < 128891 / 1000 :=
  word_hpq hL G.jb G.hodd hk hn hlam hdeg1

end headlinesB

/-! ## type A -/

structure GramA (n k : ℕ) where
  pre : Fin k → List (Ev n k)
  post : List (Ev n k)
  x : Fin k → Fin n
  y : Fin k → Fin n
  u : Fin k → Fin n
  v : Fin k → Fin n
  hxy : ∀ s, x s ≠ y s
  hxu : ∀ s, x s ≠ u s
  hxv : ∀ s, x s ≠ v s
  hyu : ∀ s, y s ≠ u s
  hyv : ∀ s, y s ≠ v s
  huv : ∀ s, u s ≠ v s
  ex : Fin n → ℤ
  mask : Fin n → Finset (Fin k)
  ex_eq : ∀ r, ex r = -1

namespace GramA
variable {n k : ℕ} (G : GramA n k)

def blk : Blk n k where
  pre := G.pre
  jx := fun s => jA s (G.x s) (G.y s) (G.u s) (G.v s) (-1)
  post := G.post
  ex := G.ex
  mask := G.mask

def word : CWord n k := G.blk.word

theorem jx_len (s : Fin k) : (G.blk.jx s).length = 6 := by simp [blk, jA]

theorem hodd : ∀ r, G.word.ex r % 2 = 1 := by
  intro r; show G.ex r % 2 = 1; rw [G.ex_eq]; norm_num

def ja : JA G.word where
  pos := G.blk.pos
  mono := by
    intro s t h
    have := G.blk.pos_gap s t h
    rw [G.jx_len s] at this
    show G.blk.pos s < G.blk.pos t
    omega
  sep := by
    intro s t h
    have := G.blk.pos_gap s t h
    rw [G.jx_len s] at this
    show G.blk.pos s + 1 < G.blk.pos t
    omega
  lt := by
    intro s
    have := G.blk.len_ge s
    rw [G.jx_len s] at this
    show G.blk.pos s + 5 < G.blk.evs.length
    omega
  x := G.x
  y := G.y
  u := G.u
  v := G.v
  α := fun _ => -1
  α0 := fun _ => by norm_num
  hxy := G.hxy
  hxu := G.hxu
  hxv := G.hxv
  hyu := G.hyu
  hyv := G.hyv
  huv := G.huv
  h0 := fun s => G.blk.get_jx' s 0 _ (by simp [blk, jA]) _
  h1 := fun s => G.blk.get_jx' s 1 _ (by simp [blk, jA]) _
  h2 := fun s => G.blk.get_jx' s 2 _ (by simp [blk, jA]) _
  h3 := fun s => G.blk.get_jx' s 3 _ (by simp [blk, jA]) _
  h4 := fun s => G.blk.get_jx' s 4 _ (by simp [blk, jA]) _
  h5 := fun s => G.blk.get_jx' s 5 _ (by simp [blk, jA]) _

end GramA

section headlinesA
open CallerHP CallerBridge
variable {n k : ℕ} (G : GramA n k)

theorem gramA_hp (hL : Legal G.word) (hk : 3 ≤ k)
    (hQ0 : Fintype.card (Iota G.word) = 2 * k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.ja.col s) (G.ja.col s)).det)
    (hdeg : ∀ r, 2 ≤ (G.word.mask r).card) :
    cHat G.word ≤ HPr k :=
  word_hp_A hL G.ja G.hodd hk hQ0 hn hlam hdeg

theorem gramA_hpq (hL : Legal G.word) (hk : 77 ≤ k) (hn : n + 2 = Fintype.card (Iota G.word))
    (hlam : ∀ s, IsUnit ((sgK (βw G.word) (sgG (Aw G.word Complex.I) (Bw G.word Complex.I))).submatrix
      (G.ja.col s) (G.ja.col s)).det)
    (hdeg1 : ∀ r, 1 ≤ (G.word.mask r).card) :
    cHatQ G.word < 128891 / 1000 :=
  CallerJA.word_hpq_A hL G.ja G.hodd hk hn hlam hdeg1

end headlinesA

/-! ## non-vacuity of the grammar -> schema derivation: concrete 3-stage records with plain blocks -/
section nonvac

/-- 3 stages, 4 roles, one plain ADD before stage 1 and one plain SCALE after the last record. -/
def gB : GramB 4 3 where
  pre := fun s => if s = 1 then [Ev.add 2 3 1] else []
  post := [Ev.scale 0 2]
  u := fun _ => 0
  v := fun _ => 1
  uv := fun _ => by decide
  ex := fun _ => -1
  mask := fun _ => ∅
  ex_eq := fun _ => rfl

theorem gB_pos : (gB.jb.pos 0, gB.jb.pos 1, gB.jb.pos 2) = (0, 4, 7) := by
  simp [gB, GramB.jb, Blk.pos, blocks, Blk.f, GramB.blk, jB, List.range_succ]

theorem gB_len : gB.word.evs.length = 11 := by
  simp [gB, GramB.word, Blk.word, Blk.evs, blocks, Blk.f, GramB.blk, jB, List.range_succ]

def gA : GramA 4 2 where
  pre := fun s => if s = 1 then [Ev.add 2 3 1] else []
  post := []
  x := fun _ => 0
  y := fun _ => 1
  u := fun _ => 2
  v := fun _ => 3
  hxy := fun _ => by decide
  hxu := fun _ => by decide
  hxv := fun _ => by decide
  hyu := fun _ => by decide
  hyv := fun _ => by decide
  huv := fun _ => by decide
  ex := fun _ => -1
  mask := fun _ => ∅
  ex_eq := fun _ => rfl

theorem gA_pos : (gA.ja.pos 0, gA.ja.pos 1) = (0, 7) := by
  simp [gA, GramA.ja, Blk.pos, blocks, Blk.f, GramA.blk, jA, List.range_succ]

end nonvac

end SchemaCost

#print axioms SchemaCost.GramB.jb
#print axioms SchemaCost.GramA.ja
#print axioms SchemaCost.gramB_hp
#print axioms SchemaCost.gramB_hpq
#print axioms SchemaCost.gramA_hp
#print axioms SchemaCost.gramA_hpq
#print axioms SchemaCost.gB_pos
#print axioms SchemaCost.gA_pos
