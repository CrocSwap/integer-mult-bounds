/-
, piece (A): the order-8 letter symmetry on the 720 job orders of SPECBREAK survivor #0 (RB5/RB6).
Letters A..F = 0..5.  Group G = <(AB), (CD), (AC)(BD)> (dihedral, order 8).  Orders = permutations of the six letters,
acted on by relabelling letters:  g . o = o.map g.
  * finite data: `Gl` (8 letter permutations), `reps` (RB5/reps0.txt, 90 orders);
  * `Gl` is closed under composition (so it is a group action), `reps` are orders, pairwise in distinct orbits, and
    every one of the 720 orders is the image of a rep  =>  EXACTLY 90 orbits  (decide +kernel);
  * invariance of the kill condition: for every g in Gl there is a model-preserving relabelling rho |-> rho'' (identity on
    parameters for the elements fixing the pairs {A,B},{C,D}, conjugation by the (2 3)-swap of the middle 2x2 block for
    the elements exchanging them) with  Rel_{g.o}(rho) => Rel_o(rho'')  and  Kill_o(rho'') => Kill_{g.o}(rho).
    So `Kill` for the 90 reps gives `Kill` for all 720 orders (theorem `reduction`).
-/
import Nov15.Spec0K0Core
import Mathlib.Data.List.Perm.Basic
import Mathlib.Data.List.Permutation
import Mathlib.Data.List.FinRange

namespace Spec0K0

/-! ## finite data -/

/-- image list of a letter permutation, as a function -/
def fn (l : List (Fin 6)) : Fin 6 → Fin 6 := fun c => l.getD c.val 0

def Gl : List (List (Fin 6)) := [
  [0,1,2,3,4,5],
  [2,3,0,1,4,5],
  [0,1,3,2,4,5],
  [3,2,0,1,4,5],
  [1,0,2,3,4,5],
  [2,3,1,0,4,5],
  [1,0,3,2,4,5],
  [3,2,1,0,4,5]]

def reps : List (List (Fin 6)) := [
  [0,1,2,3,4,5],
  [0,1,2,3,5,4],
  [0,1,2,4,3,5],
  [0,1,2,4,5,3],
  [0,1,2,5,3,4],
  [0,1,2,5,4,3],
  [0,1,4,2,3,5],
  [0,1,4,2,5,3],
  [0,1,4,5,2,3],
  [0,1,5,2,3,4],
  [0,1,5,2,4,3],
  [0,1,5,4,2,3],
  [0,2,1,3,4,5],
  [0,2,1,3,5,4],
  [0,2,1,4,3,5],
  [0,2,1,4,5,3],
  [0,2,1,5,3,4],
  [0,2,1,5,4,3],
  [0,2,3,1,4,5],
  [0,2,3,1,5,4],
  [0,2,3,4,1,5],
  [0,2,3,4,5,1],
  [0,2,3,5,1,4],
  [0,2,3,5,4,1],
  [0,2,4,1,3,5],
  [0,2,4,1,5,3],
  [0,2,4,3,1,5],
  [0,2,4,3,5,1],
  [0,2,4,5,1,3],
  [0,2,4,5,3,1],
  [0,2,5,1,3,4],
  [0,2,5,1,4,3],
  [0,2,5,3,1,4],
  [0,2,5,3,4,1],
  [0,2,5,4,1,3],
  [0,2,5,4,3,1],
  [0,4,1,2,3,5],
  [0,4,1,2,5,3],
  [0,4,1,5,2,3],
  [0,4,2,1,3,5],
  [0,4,2,1,5,3],
  [0,4,2,3,1,5],
  [0,4,2,3,5,1],
  [0,4,2,5,1,3],
  [0,4,2,5,3,1],
  [0,4,5,1,2,3],
  [0,4,5,2,1,3],
  [0,4,5,2,3,1],
  [0,5,1,2,3,4],
  [0,5,1,2,4,3],
  [0,5,1,4,2,3],
  [0,5,2,1,3,4],
  [0,5,2,1,4,3],
  [0,5,2,3,1,4],
  [0,5,2,3,4,1],
  [0,5,2,4,1,3],
  [0,5,2,4,3,1],
  [0,5,4,1,2,3],
  [0,5,4,2,1,3],
  [0,5,4,2,3,1],
  [4,0,1,2,3,5],
  [4,0,1,2,5,3],
  [4,0,1,5,2,3],
  [4,0,2,1,3,5],
  [4,0,2,1,5,3],
  [4,0,2,3,1,5],
  [4,0,2,3,5,1],
  [4,0,2,5,1,3],
  [4,0,2,5,3,1],
  [4,0,5,1,2,3],
  [4,0,5,2,1,3],
  [4,0,5,2,3,1],
  [4,5,0,1,2,3],
  [4,5,0,2,1,3],
  [4,5,0,2,3,1],
  [5,0,1,2,3,4],
  [5,0,1,2,4,3],
  [5,0,1,4,2,3],
  [5,0,2,1,3,4],
  [5,0,2,1,4,3],
  [5,0,2,3,1,4],
  [5,0,2,3,4,1],
  [5,0,2,4,1,3],
  [5,0,2,4,3,1],
  [5,0,4,1,2,3],
  [5,0,4,2,1,3],
  [5,0,4,2,3,1],
  [5,4,0,1,2,3],
  [5,4,0,2,1,3],
  [5,4,0,2,3,1]]

def idl : List (Fin 6) := List.finRange 6

theorem Gl_length : Gl.length = 8 := by decide +kernel
theorem Gl_id : idl ∈ Gl := by decide +kernel
theorem Gl_perm : ∀ g ∈ Gl, g.Perm idl := by decide +kernel
theorem Gl_closed : ∀ g ∈ Gl, ∀ h ∈ Gl, idl.map (fun c => fn g (fn h c)) ∈ Gl := by decide +kernel

theorem reps_length : reps.length = 90 := by decide +kernel
theorem reps_perm : ∀ r ∈ reps, r.Perm idl := by decide +kernel
theorem reps_nodup : reps.Nodup := by decide +kernel
theorem perms_length : idl.permutations'.length = 720 := by decide +kernel

/-- canonical form of an order: the orbit element with least base-6 code -/
def enc (l : List (Fin 6)) : ℕ := l.foldl (fun a x => 6*a + x.val) 0
def canon (p : List (Fin 6)) : List (Fin 6) :=
  (Gl.map (fun g => p.map (fn g))).foldl (fun m q => if enc q < enc m then q else m) p

theorem coverC : (idl.permutations'.all fun p => reps.contains (canon p)) = true := by decide +kernel
theorem distC : (reps.all fun r => Gl.all fun g => !(reps.contains (r.map (fn g))) || (r.map (fn g) == r)) = true := by
  decide +kernel
theorem Gl_inv : ∀ g ∈ Gl, ∃ h ∈ Gl, ∀ c, fn h (fn g c) = c := by decide +kernel

theorem foldl_sel {α : Type*} (f : α → α → α) (hf : ∀ m q, f m q = m ∨ f m q = q) :
    ∀ (l : List α) (m : α), l.foldl f m = m ∨ l.foldl f m ∈ l := by
  intro l
  induction l with
  | nil => intro m; left; rfl
  | cons q qs ih =>
    intro m
    simp only [List.foldl_cons, List.mem_cons]
    rcases ih (f m q) with h | h
    · rcases hf m q with h' | h'
      · left; rw [h, h']
      · right; left; rw [h, h']
    · right; right; exact h

theorem canon_mem (p : List (Fin 6)) : ∃ g ∈ Gl, p.map (fn g) = canon p := by
  unfold canon
  rcases foldl_sel (fun m q => if enc q < enc m then q else m)
      (fun m q => by by_cases h : enc q < enc m <;> simp [h]) (Gl.map (fun g => p.map (fn g))) p with h | h
  · refine ⟨idl, Gl_id, ?_⟩
    rw [h]
    have hid : fn idl = id := funext (by decide)
    rw [hid, List.map_id]
  · obtain ⟨g, hg, hgq⟩ := List.mem_map.mp h
    exact ⟨g, hg, hgq⟩

/-- every order is the image of a representative -/
theorem cover : ∀ p ∈ idl.permutations', ∃ r ∈ reps, ∃ g ∈ Gl, r.map (fn g) = p := by
  intro p hp
  have h1 := List.all_eq_true.mp coverC p hp
  have hr : canon p ∈ reps := List.contains_iff_mem.mp h1
  obtain ⟨g, hg, hgp⟩ := canon_mem p
  obtain ⟨h, hh, hinv⟩ := Gl_inv g hg
  refine ⟨canon p, hr, h, hh, ?_⟩
  rw [← hgp, List.map_map]
  have : (fn h ∘ fn g) = id := funext hinv
  rw [this, List.map_id]

/-- representatives lie in pairwise distinct orbits: hence exactly 90 orbits -/
theorem distinct : ∀ r ∈ reps, ∀ s ∈ reps, (∃ g ∈ Gl, r.map (fn g) = s) → r = s := by
  intro r hr s hs ⟨g, hg, h⟩
  have h1 := List.all_eq_true.mp distC r hr
  have h2 := List.all_eq_true.mp h1 g hg
  rw [h] at h2
  have : reps.contains s = true := List.contains_iff_mem.mpr hs
  rw [this] at h2
  exact (by simpa [h] using h2 : s = r).symm

/-! ## the kill condition is invariant -/

section
variable {K : Type*} [Field K]

/-- conjugation by the swap of coordinates 2 and 3 -/
def conj (U : M4 K) : M4 K :=
  ⟨U.m11,U.m13,U.m12,U.m14, U.m31,U.m33,U.m32,U.m34, U.m21,U.m23,U.m22,U.m24, U.m41,U.m43,U.m42,U.m44⟩

theorem conj_mm (A B : M4 K) : conj (mm A B) = mm (conj A) (conj B) := by
  ext <;> simp only [conj, mm] <;> ring
theorem conj_conj (A : M4 K) : conj (conj A) = A := by cases A; rfl
theorem conj_I4 : conj (I4 : M4 K) = I4 := by simp only [conj, I4, diag4]
theorem conj_Z4 : conj (Z4 : M4 K) = Z4 := by simp only [conj, Z4, diag4]
theorem conj_zero4 : conj (zero4 : M4 K) = zero4 := by simp only [conj, zero4, diag4]
theorem conj_inj {A B : M4 K} (h : conj A = conj B) : A = B := by
  have := congrArg conj h; rwa [conj_conj, conj_conj] at this

theorem conj_unit (d1 d2 : K) (U : M4 K) : UnitRel d1 d2 (conj U) ↔ UnitRel d2 d1 U := by
  simp only [UnitRel, conj]
  constructor
  · rintro ⟨a, b, c, d⟩; exact ⟨d, c, b, a⟩
  · rintro ⟨a, b, c, d⟩; exact ⟨d, c, b, a⟩

theorem conj_omega (d1 d2 : K) (U : M4 K) : omega d1 d2 (conj U) = omega d2 d1 U := by
  simp only [omega, conj]; ring

theorem conj_LLm (d1 d2 : K) (U : M4 K) : LLm d1 d2 (conj U) = conj (LLm d2 d1 U) := by
  ext <;> simp only [LLm, conj, mm, diag4] <;> ring

theorem conj_KU (d1 d2 : K) (U : M4 K) : KU d1 d2 (conj U) ↔ KU d2 d1 U := by
  unfold KU
  rw [conj_omega, conj_LLm]
  constructor
  · rintro ⟨a, b⟩; refine ⟨a, conj_inj ?_⟩; rw [b, conj_zero4]
  · rintro ⟨a, b⟩; refine ⟨a, ?_⟩; rw [b, conj_zero4]

/-- word product of the letters of `o` lying in `S`, in order (right-nested) -/
def wp : List (Fin 6) → (Fin 6 → Bool) → (Fin 6 → M4 K) → M4 K
  | [], _, _ => I4
  | c :: cs, S, ρ => if S c then mm (ρ c) (wp cs S ρ) else wp cs S ρ

theorem wp_map (ε : M4 K → M4 K) (hmul : ∀ A B, ε (mm A B) = mm (ε A) (ε B)) (hI : ε I4 = I4)
    (g : Fin 6 → Fin 6) (ρ ρ'' : Fin 6 → M4 K) (hρ : ∀ c, ρ (g c) = ε (ρ'' c)) (S : Fin 6 → Bool) :
    ∀ o : List (Fin 6), wp (o.map g) S ρ = ε (wp o (fun c => S (g c)) ρ'') := by
  intro o
  induction o with
  | nil => simp only [List.map_nil, wp, hI]
  | cons c cs ih =>
    simp only [List.map_cons, wp]
    by_cases h : S (g c)
    · simp only [h, if_true, hmul, hρ, ih]
    · simp only [h, Bool.false_eq_true, if_false, ih]

def sABCD : Fin 6 → Bool := fun c => decide (c.val < 4)
def sALL : Fin 6 → Bool := fun _ => true
def sABF : Fin 6 → Bool := fun c => decide (c.val = 0 ∨ c.val = 1 ∨ c.val = 5)
def sCDF : Fin 6 → Bool := fun c => decide (c.val = 2 ∨ c.val = 3 ∨ c.val = 5)
def sABE : Fin 6 → Bool := fun c => decide (c.val = 0 ∨ c.val = 1 ∨ c.val = 4)
def sCDE : Fin 6 → Bool := fun c => decide (c.val = 2 ∨ c.val = 3 ∨ c.val = 4)

/-- the relations / the kill statement for the order `o` and the letter matrices `ρ` -/
def Rel' (o : List (Fin 6)) (ρ : Fin 6 → M4 K) : Prop :=
  Rel (wp o sABCD ρ) (wp o sALL ρ) (wp o sABF ρ) (wp o sCDF ρ) (wp o sABE ρ) (wp o sCDE ρ)
def Kill' (o : List (Fin 6)) (ρ : Fin 6 → M4 K) : Prop :=
  Kill (wp o sABF ρ) (wp o sCDF ρ) (wp o sABE ρ) (wp o sCDE ρ)

/-- the model: letters A..D are job matrices, E, F the flag matrices -/
def ModelOK (ρ : Fin 6 → M4 K) : Prop :=
  (∀ c : Fin 6, c.val < 4 → ∃ a b c' p1 p2 q1 q2 : K, JobOK a b c' p1 p2 q1 q2 ∧ ρ c = MJ a b c' p1 p2 q1 q2) ∧
  (∃ e1 e2 e3 : K, EpsOK e1 e2 e3 ∧ ρ 4 = MEm e1 e2 e3 ∧ ρ 5 = MFm e1 e2 e3)

theorem conj_MJ (a b c p1 p2 q1 q2 : K) :
    conj (MJ a b c p1 p2 q1 q2) = MJ (-a) c b p2 p1 q2 q1 := by
  ext <;> simp only [conj, MJ] <;> ring
theorem conj_MEm (e1 e2 e3 : K) : conj (MEm e1 e2 e3) = MEm (-e1) e3 e2 := by
  ext <;> simp only [conj, MEm] <;> ring
theorem conj_MFm (e1 e2 e3 : K) : conj (MFm e1 e2 e3) = MFm (-e1) e3 e2 := by
  ext <;> simp only [conj, MFm] <;> ring

theorem jobOK_conj {a b c p1 p2 q1 q2 : K} (h : JobOK a b c p1 p2 q1 q2) :
    JobOK (-a) c b p2 p1 q2 q1 := by
  obtain ⟨h0, h1, h2, h3, h4⟩ := h
  refine ⟨by linear_combination h0, by linear_combination h1 * 0 + h2, by linear_combination h1, ?_, ?_⟩
  · linear_combination h4
  · linear_combination h3

theorem epsOK_conj {e1 e2 e3 : K} (h : EpsOK e1 e2 e3) : EpsOK (-e1) e3 e2 := by
  unfold EpsOK at *; linear_combination h

def SideF (g : Fin 6 → Fin 6) : Prop :=
  g 4 = 4 ∧ g 5 = 5 ∧ ∀ c, sABCD (g c) = sABCD c ∧ sABF (g c) = sABF c ∧ sCDF (g c) = sCDF c ∧
    sABE (g c) = sABE c ∧ sCDE (g c) = sCDE c
def SideT (g : Fin 6 → Fin 6) : Prop :=
  g 4 = 4 ∧ g 5 = 5 ∧ ∀ c, sABCD (g c) = sABCD c ∧ sABF (g c) = sCDF c ∧ sCDF (g c) = sABF c ∧
    sABE (g c) = sCDE c ∧ sCDE (g c) = sABE c

instance (g : Fin 6 → Fin 6) : Decidable (SideF g) := by unfold SideF; infer_instance
instance (g : Fin 6 → Fin 6) : Decidable (SideT g) := by unfold SideT; infer_instance

theorem Gl_side : ∀ g ∈ Gl, SideF (fn g) ∨ SideT (fn g) := by decide +kernel

/-- generic relabelling: `ρ'' c = ε (ρ (g c))` stays in the model, and word products transform by `ε` -/
theorem step_gen (ε : M4 K → M4 K) (hmul : ∀ A B, ε (mm A B) = mm (ε A) (ε B)) (hI : ε I4 = I4)
    (hinv : ∀ A, ε (ε A) = A)
    (hεJ : ∀ a b c p1 p2 q1 q2 : K, JobOK a b c p1 p2 q1 q2 →
      ∃ a' b' c' p1' p2' q1' q2' : K, JobOK a' b' c' p1' p2' q1' q2' ∧ ε (MJ a b c p1 p2 q1 q2) = MJ a' b' c' p1' p2' q1' q2')
    (hεE : ∀ e1 e2 e3 : K, EpsOK e1 e2 e3 →
      ∃ e1' e2' e3' : K, EpsOK e1' e2' e3' ∧ ε (MEm e1 e2 e3) = MEm e1' e2' e3' ∧ ε (MFm e1 e2 e3) = MFm e1' e2' e3')
    (g : Fin 6 → Fin 6) (h4 : g 4 = 4) (h5 : g 5 = 5) (hjob : ∀ c : Fin 6, c.val < 4 → (g c).val < 4)
    (ρ : Fin 6 → M4 K) (hρ : ModelOK ρ) :
    ∃ ρ'' : Fin 6 → M4 K, ModelOK ρ'' ∧
      ∀ (S : Fin 6 → Bool) (r : List (Fin 6)), wp (r.map g) S ρ = ε (wp r (fun c => S (g c)) ρ'') := by
  obtain ⟨hj, e1, e2, e3, he, h4', h5'⟩ := hρ
  refine ⟨fun c => ε (ρ (g c)), ⟨?_, ?_⟩, ?_⟩
  · intro c hc
    obtain ⟨a, b, c', p1, p2, q1, q2, hok, hρc⟩ := hj (g c) (hjob c hc)
    obtain ⟨a', b', c'', p1', p2', q1', q2', hok', hε⟩ := hεJ a b c' p1 p2 q1 q2 hok
    exact ⟨a', b', c'', p1', p2', q1', q2', hok', by simp only [hρc, hε]⟩
  · obtain ⟨e1', e2', e3', hok', hε4, hε5⟩ := hεE e1 e2 e3 he
    exact ⟨e1', e2', e3', hok', by simp only [h4, h4', hε4], by simp only [h5, h5', hε5]⟩
  · intro S r
    exact wp_map ε hmul hI g ρ _ (fun c => (hinv _).symm) S r

theorem step_F (g : Fin 6 → Fin 6) (hg : SideF g) (ρ : Fin 6 → M4 K) (hρ : ModelOK ρ) (r : List (Fin 6)) :
    ∃ ρ'' : Fin 6 → M4 K, ModelOK ρ'' ∧ (Rel' (r.map g) ρ → Rel' r ρ'') ∧ (Kill' r ρ'' → Kill' (r.map g) ρ) := by
  obtain ⟨h4, h5, hs⟩ := hg
  have hS : ∀ S : Fin 6 → Bool, (∀ c, S (g c) = S c) → (fun c => S (g c)) = S := fun S h => funext h
  have hjob : ∀ c : Fin 6, c.val < 4 → (g c).val < 4 := by
    intro c hc
    have := (hs c).1
    simp only [sABCD, decide_eq_decide] at this
    exact this.mpr hc
  obtain ⟨ρ'', hm, hw⟩ := step_gen id (fun _ _ => rfl) rfl (fun _ => rfl)
    (fun a b c p1 p2 q1 q2 h => ⟨a, b, c, p1, p2, q1, q2, h, rfl⟩)
    (fun e1 e2 e3 h => ⟨e1, e2, e3, h, rfl, rfl⟩) g h4 h5 hjob ρ hρ
  have w := fun S => hw S r
  simp only [id] at w
  refine ⟨ρ'', hm, ?_, ?_⟩
  · unfold Rel'
    rw [w sABCD, w sALL, w sABF, w sCDF, w sABE, w sCDE, hS sABCD (fun c => (hs c).1), hS sALL (fun _ => rfl),
      hS sABF (fun c => (hs c).2.1), hS sCDF (fun c => (hs c).2.2.1), hS sABE (fun c => (hs c).2.2.2.1),
      hS sCDE (fun c => (hs c).2.2.2.2)]
    exact id
  · unfold Kill'
    rw [w sABF, w sCDF, w sABE, w sCDE, hS sABF (fun c => (hs c).2.1), hS sCDF (fun c => (hs c).2.2.1),
      hS sABE (fun c => (hs c).2.2.2.1), hS sCDE (fun c => (hs c).2.2.2.2)]
    exact id

theorem step_T (g : Fin 6 → Fin 6) (hg : SideT g) (ρ : Fin 6 → M4 K) (hρ : ModelOK ρ) (r : List (Fin 6)) :
    ∃ ρ'' : Fin 6 → M4 K, ModelOK ρ'' ∧ (Rel' (r.map g) ρ → Rel' r ρ'') ∧ (Kill' r ρ'' → Kill' (r.map g) ρ) := by
  obtain ⟨h4, h5, hs⟩ := hg
  have hS : ∀ S S' : Fin 6 → Bool, (∀ c, S (g c) = S' c) → (fun c => S (g c)) = S' := fun S S' h => funext h
  have hjob : ∀ c : Fin 6, c.val < 4 → (g c).val < 4 := by
    intro c hc
    have := (hs c).1
    simp only [sABCD, decide_eq_decide] at this
    exact this.mpr hc
  obtain ⟨ρ'', hm, hw⟩ := step_gen conj conj_mm conj_I4 conj_conj
    (fun a b c p1 p2 q1 q2 h => ⟨-a, c, b, p2, p1, q2, q1, jobOK_conj h, conj_MJ _ _ _ _ _ _ _⟩)
    (fun e1 e2 e3 h => ⟨-e1, e3, e2, epsOK_conj h, conj_MEm _ _ _, conj_MFm _ _ _⟩) g h4 h5 hjob ρ hρ
  have w := fun S => hw S r
  have a1 := hS sABCD sABCD (fun c => (hs c).1)
  have a2 := hS sALL sALL (fun _ => rfl)
  have a3 := hS sABF sCDF (fun c => (hs c).2.1)
  have a4 := hS sCDF sABF (fun c => (hs c).2.2.1)
  have a5 := hS sABE sCDE (fun c => (hs c).2.2.2.1)
  have a6 := hS sCDE sABE (fun c => (hs c).2.2.2.2)
  refine ⟨ρ'', hm, ?_, ?_⟩
  · unfold Rel' Rel
    rw [w sABCD, w sALL, w sABF, w sCDF, w sABE, w sCDE, a1, a2, a3, a4, a5, a6]
    rintro ⟨h3, h7, k1, k2, k5, k6⟩
    refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
    · apply conj_inj; rw [h3, conj_Z4]
    · apply conj_inj; rw [h7, conj_I4]
    · exact (conj_unit _ _ _).mp k2
    · exact (conj_unit _ _ _).mp k1
    · exact (conj_unit _ _ _).mp k6
    · exact (conj_unit _ _ _).mp k5
  · unfold Kill' Kill
    rw [w sABF, w sCDF, w sABE, w sCDE, a3, a4, a5, a6]
    rintro ⟨k1, k2, k5, k6⟩
    exact ⟨(conj_KU _ _ _).mpr k2, (conj_KU _ _ _).mpr k1, (conj_KU _ _ _).mpr k6, (conj_KU _ _ _).mpr k5⟩

/-- Reduction: Kill on the 90 representatives gives Kill on all 720 orders. -/
theorem reduction
    (hreps : ∀ r ∈ reps, ∀ ρ : Fin 6 → M4 K, ModelOK ρ → Rel' r ρ → Kill' r ρ) :
    ∀ o : List (Fin 6), o.Perm idl → ∀ ρ : Fin 6 → M4 K, ModelOK ρ → Rel' o ρ → Kill' o ρ := by
  intro o ho ρ hρ hrel
  obtain ⟨r, hr, g, hg, rfl⟩ := cover o (List.mem_permutations'.mpr ho)
  have hside := Gl_side g hg
  have key : ∃ ρ'' : Fin 6 → M4 K, ModelOK ρ'' ∧ (Rel' (r.map (fn g)) ρ → Rel' r ρ'') ∧ (Kill' r ρ'' → Kill' (r.map (fn g)) ρ) := by
    rcases hside with h | h
    · exact step_F (fn g) h ρ hρ r
    · exact step_T (fn g) h ρ hρ r
  obtain ⟨ρ'', hm, h1, h2⟩ := key
  exact h2 (hreps r hr ρ'' hm (h1 hrel))
end

end Spec0K0

#print axioms Spec0K0.reduction
#print axioms Spec0K0.cover
#print axioms Spec0K0.distinct
#print axioms Spec0K0.Gl_closed
#print axioms Spec0K0.step_T
