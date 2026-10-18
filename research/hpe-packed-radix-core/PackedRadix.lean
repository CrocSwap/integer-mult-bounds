/- Apache-2.0. ywz65 with substantial OpenAI Codex assistance.
   Extends the unchanged PR2499 energy grammar; see BOUNDARY.md. -/
import Energy

namespace Packed
def pack (b : Int) : List Int → Int
  | [] => 0
  | a :: as => a + b * pack b as

theorem small_multiple (a b : Int) (_hb : 0 < b)
    (hlo : -b < a) (hhi : a < b) (hm : a % b = 0) : a = 0 := by
  by_cases ha : 0 ≤ a
  · have := Int.emod_eq_of_lt ha hhi
    omega
  · have he := Int.emod_eq_of_lt (by omega : 0 ≤ a+b) (by omega : a+b < b)
    have hz : (a+b) % b = 0 := by simp [hm]
    omega

theorem pack_zero {b : Int} (hb : 0 < b) (xs : List Int)
    (bounds : ∀ x ∈ xs, -b < x ∧ x < b) (h : pack b xs = 0) :
    ∀ x ∈ xs, x = 0 := by
  induction xs with
  | nil => simp
  | cons a as ih =>
      have ha := bounds a (by simp)
      have hm : a % b = 0 := by
        have he := congrArg (fun x => x % b) h
        simpa [pack] using he
      have az : a = 0 := small_multiple a b hb ha.1 ha.2 hm
      have ht : pack b as = 0 := by
        simp [pack, az] at h
        exact (Int.mul_eq_zero.mp h).resolve_left (by omega)
      intro x hx
      simp only [List.mem_cons] at hx
      rcases hx with hx | hx
      · exact hx.trans az
      · exact ih (fun x hx => bounds x (by simp [hx])) ht x hx

theorem square_bound {a m : Int} (hm : 0 ≤ m) (h : a*a ≤ m*m) :
    -m ≤ a ∧ a ≤ m := by
  constructor
  · by_cases hn : -m ≤ a
    · exact hn
    · have ha : m+1 ≤ -a := by omega
      have hmul := Int.mul_self_le_mul_self (by omega : 0 ≤ m+1) ha
      grind
  · by_cases hn : a ≤ m
    · exact hn
    · have ha : m+1 ≤ a := by omega
      have hmul := Int.mul_self_le_mul_self (by omega : 0 ≤ m+1) ha
      grind

theorem four_two (k : Nat) : (4:Int)^k = (2:Int)^k * (2:Int)^k := by
  induction k with
  | zero => simp
  | succ k ih => simp [Int.pow_succ, ih]; grind

#print axioms pack_zero
#print axioms square_bound
#print axioms four_two

def Bound (k : Nat) (z : HPEEnergy.Gaussian) : Prop :=
  z.1*z.1 ≤ (4:Int)^k ∧ z.2*z.2 ≤ (4:Int)^k

def ColumnEntry (k : Nat) (z : HPEEnergy.Gaussian) : Prop :=
  ∃ v w, HPEEnergy.Run k v w ∧ HPEEnergy.energy v = 1 ∧ z ∈ w

theorem entry_bound {k z} (h : ColumnEntry k z) : Bound k z := by
  obtain ⟨v, w, hr, he, hz⟩ := h
  exact HPEEnergy.column_squared_bound hr he hz

theorem scaled_component {k K : Nat} {a : Int} (hk : k ≤ K)
    (h : a*a ≤ (4:Int)^k) :
    -(2:Int)^K ≤ (2:Int)^(K-k)*a ∧ (2:Int)^(K-k)*a ≤ (2:Int)^K := by
  have hp : 0 < (2:Int)^k := Int.pow_pos (by decide)
  have hs : 0 < (2:Int)^(K-k) := Int.pow_pos (by decide)
  have hb := square_bound (by omega : 0 ≤ (2:Int)^k) (four_two k ▸ h)
  have he : (2:Int)^(K-k) * (2:Int)^k = (2:Int)^K := by
    rw [← Int.pow_add, Nat.sub_add_cancel hk]
  have hl := Int.mul_le_mul_of_nonneg_left hb.1 (by omega : 0 ≤ (2:Int)^(K-k))
  have hu := Int.mul_le_mul_of_nonneg_left hb.2 (by omega : 0 ≤ (2:Int)^(K-k))
  rw [he] at hu
  rw [Int.mul_neg, he] at hl
  exact ⟨hl, hu⟩

def delta (k1 k2 K : Nat) (p : HPEEnergy.Gaussian × HPEEnergy.Gaussian) : HPEEnergy.Gaussian :=
  ((2:Int)^(K-k1)*p.1.1 - (2:Int)^(K-k2)*p.2.1,
   (2:Int)^(K-k1)*p.1.2 - (2:Int)^(K-k2)*p.2.2)

theorem delta_bound {k1 k2 K : Nat} (h1 : k1 ≤ K) (h2 : k2 ≤ K)
    {p : HPEEnergy.Gaussian × HPEEnergy.Gaussian}
    (hb1 : Bound k1 p.1) (hb2 : Bound k2 p.2) :
    let b := (2:Int)^(K+2)
    (-b < (delta k1 k2 K p).1 ∧ (delta k1 k2 K p).1 < b) ∧
    (-b < (delta k1 k2 K p).2 ∧ (delta k1 k2 K p).2 < b) := by
  have ar := scaled_component h1 hb1.1
  have ai := scaled_component h1 hb1.2
  have br := scaled_component h2 hb2.1
  have bi := scaled_component h2 hb2.2
  have hp : 0 < (2:Int)^K := Int.pow_pos (by decide)
  simp [delta, Int.pow_succ]
  omega

def packGaussian (b : Int) (xs : List HPEEnergy.Gaussian) : HPEEnergy.Gaussian :=
  (pack b (xs.map Prod.fst), pack b (xs.map Prod.snd))

theorem gaussian_zero {b : Int} (hb : 0 < b) (xs : List HPEEnergy.Gaussian)
    (bounds : ∀ z ∈ xs, (-b < z.1 ∧ z.1 < b) ∧ (-b < z.2 ∧ z.2 < b))
    (h : packGaussian b xs = (0,0)) : ∀ z ∈ xs, z = (0,0) := by
  have hr : pack b (xs.map Prod.fst) = 0 := congrArg Prod.fst h
  have hi : pack b (xs.map Prod.snd) = 0 := congrArg Prod.snd h
  have er := pack_zero hb (xs.map Prod.fst) (by
    intro x hx
    obtain ⟨z, hz, he⟩ := List.mem_map.mp hx
    simpa [← he] using (bounds z hz).1) hr
  have ei := pack_zero hb (xs.map Prod.snd) (by
    intro x hx
    obtain ⟨z, hz, he⟩ := List.mem_map.mp hx
    simpa [← he] using (bounds z hz).2) hi
  intro z hz
  have hzr := er z.1 (List.mem_map.mpr ⟨z,hz,rfl⟩)
  have hzi := ei z.2 (List.mem_map.mpr ⟨z,hz,rfl⟩)
  exact Prod.ext hzr hzi

theorem smaller_radix_sound {k1 k2 K : Nat} (h1 : k1 ≤ K) (h2 : k2 ≤ K)
    (pairs : List (HPEEnergy.Gaussian × HPEEnergy.Gaussian))
    (entries : ∀ p ∈ pairs, ColumnEntry k1 p.1 ∧ ColumnEntry k2 p.2)
    (packed : packGaussian ((2:Int)^(K+2)) (pairs.map (delta k1 k2 K)) = (0,0)) :
    ∀ p ∈ pairs, delta k1 k2 K p = (0,0) := by
  have hd := gaussian_zero (Int.pow_pos (by decide)) (pairs.map (delta k1 k2 K)) (by
    intro z hz
    obtain ⟨p,hp,he⟩ := List.mem_map.mp hz
    subst z
    exact delta_bound h1 h2 (entry_bound (entries p hp).1) (entry_bound (entries p hp).2)) packed
  intro p hp
  exact hd _ (List.mem_map.mpr ⟨p,hp,rfl⟩)

#print axioms entry_bound
#print axioms scaled_component
#print axioms delta_bound
#print axioms gaussian_zero
#print axioms smaller_radix_sound

theorem pack_combo {α : Type} (b a c : Int) (xs : List α) (f g : α → Int) :
    pack b (xs.map (fun p => a*f p-c*g p)) =
    a*pack b (xs.map f)-c*pack b (xs.map g) := by
  induction xs with
  | nil => simp [pack]
  | cons x xs ih => simp [pack, ih]; grind

def scale (s : Int) (z : HPEEnergy.Gaussian) : HPEEnergy.Gaussian :=
  (s*z.1, s*z.2)

theorem packed_compare_sound {k1 k2 K : Nat} (h1 : k1 ≤ K) (h2 : k2 ≤ K)
    (pairs : List (HPEEnergy.Gaussian × HPEEnergy.Gaussian))
    (entries : ∀ p ∈ pairs, ColumnEntry k1 p.1 ∧ ColumnEntry k2 p.2)
    (packed : scale ((2:Int)^(K-k1))
        (packGaussian ((2:Int)^(K+2)) (pairs.map Prod.fst)) =
      scale ((2:Int)^(K-k2))
        (packGaussian ((2:Int)^(K+2)) (pairs.map Prod.snd))) :
    ∀ p ∈ pairs, scale ((2:Int)^(K-k1)) p.1 = scale ((2:Int)^(K-k2)) p.2 := by
  have hr := congrArg Prod.fst packed
  have hi := congrArg Prod.snd packed
  simp only [scale, packGaussian, List.map_map] at hr hi
  have hp : packGaussian ((2:Int)^(K+2)) (pairs.map (delta k1 k2 K)) = (0,0) := by
    apply Prod.ext
    · simp only [packGaussian, List.map_map, Function.comp_def, delta]
      rw [pack_combo]
      simpa [Function.comp_def] using Int.sub_eq_zero.mpr hr
    · simp only [packGaussian, List.map_map, Function.comp_def, delta]
      rw [pack_combo]
      simpa [Function.comp_def] using Int.sub_eq_zero.mpr hi
  have hz := smaller_radix_sound h1 h2 pairs entries hp
  intro p hp
  have he := hz p hp
  have hr := congrArg Prod.fst he
  have hi := congrArg Prod.snd he
  simp [delta] at hr hi
  exact Prod.ext (Int.sub_eq_zero.mp hr) (Int.sub_eq_zero.mp hi)

#print axioms pack_combo
#print axioms packed_compare_sound
end Packed
