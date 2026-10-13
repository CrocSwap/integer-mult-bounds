import Lean

/-!
Source: pinned main 3b6b66891c0ac888521cf591fe306c6286601d4f,
research/community-round8-audit/BANK-SCHEDULE.md, routing/batching paragraphs.

Only ordinary group laws and a reduction homomorphism are assumptions here.
The routing, its inverse, complete-fiber property, and batch disjointness are
proved below. Instantiating these records with GL_72(Z/q^w) and its reduction,
and producing the rational H_s, are separate production obligations.
-/
namespace CurrentMain.BankRouting

universe u v w

structure GroupLaws (G : Type u) where
  mul : G → G → G
  one : G
  inv : G → G
  assoc : ∀ a b c, mul (mul a b) c = mul a (mul b c)
  one_mul : ∀ a, mul one a = a
  mul_one : ∀ a, mul a one = a
  inv_mul : ∀ a, mul (inv a) a = one
  mul_inv : ∀ a, mul a (inv a) = one

variable {G : Type u} {L : Type v} {Role : Type w}

theorem cancel_left (A : GroupLaws G) (a b c : G)
    (h : A.mul a b = A.mul a c) : b = c := by
  have hh := congrArg (A.mul (A.inv a)) h
  simpa only [← A.assoc, A.inv_mul, A.one_mul] using hh

theorem cancel_right (A : GroupLaws G) (a b c : G)
    (h : A.mul b a = A.mul c a) : b = c := by
  have hh := congrArg (fun x => A.mul x (A.inv a)) h
  simpa only [A.assoc, A.mul_inv, A.mul_one] using hh

theorem inverse_product (A : GroupLaws G) (a b : G) :
    A.inv (A.mul a b) = A.mul (A.inv b) (A.inv a) := by
  apply cancel_left A (A.mul a b)
  rw [A.mul_inv, A.assoc, ← A.assoc b, A.mul_inv, A.one_mul, A.mul_inv]

structure Reduction (A : GroupLaws G) (B : GroupLaws L) where
  map : G → L
  map_mul : ∀ a b, map (A.mul a b) = B.mul (map a) (map b)
  map_one : map A.one = B.one

theorem Reduction.map_inv {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (a : G) : r.map (A.inv a) = B.inv (r.map a) := by
  apply cancel_left B (r.map a)
  rw [← r.map_mul, A.mul_inv, r.map_one, B.mul_inv]

/-- A role with embedding H is assigned to bank g H⁻¹. -/
def route (A : GroupLaws G) (g H : G) : G := A.mul g (A.inv H)

/-- The unique invocation serving role H at bank b is b H. -/
def origin (A : GroupLaws G) (b H : G) : G := A.mul b H

theorem origin_route (A : GroupLaws G) (g H : G) :
    origin A (route A g H) H = g := by
  simp only [origin, route, A.assoc, A.inv_mul, A.mul_one]

theorem route_origin (A : GroupLaws G) (b H : G) :
    route A (origin A b H) H = b := by
  simp only [origin, route, A.assoc, A.mul_inv, A.mul_one]

theorem route_injective (A : GroupLaws G) (H g g' : G)
    (h : route A g H = route A g' H) : g = g' := by
  have hh := congrArg (fun b => origin A b H) h
  simpa only [origin_route] using hh

/-- Exactly one visit by each role to each bank; no finite enumeration used. -/
theorem every_bank_once (A : GroupLaws G) (H b : G) :
    ∃ g, route A g H = b ∧ ∀ g', route A g' H = b → g' = g := by
  refine ⟨origin A b H, route_origin A b H, ?_⟩
  intro g' h
  exact route_injective A H g' (origin A b H) (h.trans (route_origin A b H).symm)

theorem reduction_route {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (g H : G) :
    r.map (route A g H) = route B (r.map g) (r.map H) := by
  simp only [route, r.map_mul, r.map_inv]

/-- Routing a complete low-class fiber gives exactly a complete low-class fiber. -/
theorem complete_fiber {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (H : G) (g₀ : L) (b : G) :
    r.map b = route B g₀ (r.map H) ↔
      ∃ g, r.map g = g₀ ∧ route A g H = b := by
  constructor
  · intro hb
    refine ⟨origin A b H, ?_, route_origin A b H⟩
    simp only [origin, r.map_mul, hb]
    exact origin_route B g₀ (r.map H)
  · rintro ⟨g, hg, hgb⟩
    rw [← hgb, reduction_route, hg]

/-- The complete-fiber correspondence has a unique inverse. -/
theorem complete_fiber_once {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (H : G) (g₀ : L) (b : G)
    (hb : r.map b = route B g₀ (r.map H)) :
    ∃ g, r.map g = g₀ ∧ route A g H = b ∧
      ∀ g', r.map g' = g₀ → route A g' H = b → g' = g := by
  obtain ⟨g, hg, hgb⟩ := (complete_fiber r H g₀ b).mp hb
  refine ⟨g, hg, hgb, ?_⟩
  intro g' _ hg'b
  exact route_injective A H g' g (hg'b.trans hgb.symm)

/-- Pairwise distinct low embeddings imply disjoint physical banks within a batch. -/
theorem batch_collision_free {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (H : Role → G)
    (separated : ∀ s t, r.map (H s) = r.map (H t) → s = t)
    (s t : Role) (g g' : G)
    (same_low : r.map g = r.map g')
    (collision : route A g (H s) = route A g' (H t)) :
    s = t ∧ g = g' := by
  have hs : g = A.mul (route A g (H s)) (H s) := (origin_route A g (H s)).symm
  have ht : g' = A.mul (route A g (H s)) (H t) := by
    rw [collision]
    exact (origin_route A g' (H t)).symm
  have low_equation :
      B.mul (r.map (route A g (H s))) (r.map (H s)) =
      B.mul (r.map (route A g (H s))) (r.map (H t)) := by
    rw [← r.map_mul, ← r.map_mul, ← hs, ← ht]
    exact same_low
  have st : s = t := separated s t (cancel_left B _ _ _ low_equation)
  refine ⟨st, ?_⟩
  subst t
  exact route_injective A (H s) g g' collision

/-- Distinct role ports land in distinct low bank types as well. -/
theorem low_ports_distinct {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (H : Role → G)
    (separated : ∀ s t, r.map (H s) = r.map (H t) → s = t)
    (g₀ : L) (s t : Role)
    (collision : route B g₀ (r.map (H s)) = route B g₀ (r.map (H t))) :
    s = t := by
  have hs := origin_route B g₀ (r.map (H s))
  have ht := origin_route B g₀ (r.map (H t))
  rw [← collision] at ht
  apply separated s t
  apply cancel_left B (route B g₀ (r.map (H s)))
  exact hs.trans ht.symm

/-- Adding a bank-family tag prevents aliases across families. -/
theorem tagged_collision {Family : Type} {A : GroupLaws G} {B : GroupLaws L}
    (r : Reduction A B) (H : Family → Role → G)
    (separated : ∀ f s t, r.map (H f s) = r.map (H f t) → s = t)
    (f f' : Family) (s t : Role) (g g' : G)
    (same_low : r.map g = r.map g')
    (collision : (f, route A g (H f s)) = (f', route A g' (H f' t))) :
    f = f' ∧ s = t ∧ g = g' := by
  have ff := congrArg Prod.fst collision
  have rr := congrArg Prod.snd collision
  dsimp at ff rr
  subst f'
  exact ⟨rfl, batch_collision_free r (H f) (separated f) s t g g' same_low rr⟩

end CurrentMain.BankRouting

#print axioms CurrentMain.BankRouting.every_bank_once
#print axioms CurrentMain.BankRouting.complete_fiber
#print axioms CurrentMain.BankRouting.complete_fiber_once
#print axioms CurrentMain.BankRouting.batch_collision_free
#print axioms CurrentMain.BankRouting.low_ports_distinct
#print axioms CurrentMain.BankRouting.tagged_collision

#print axioms CurrentMain.BankRouting.cancel_left
#print axioms CurrentMain.BankRouting.cancel_right
#print axioms CurrentMain.BankRouting.inverse_product
#print axioms CurrentMain.BankRouting.Reduction.map_inv
#print axioms CurrentMain.BankRouting.origin_route
#print axioms CurrentMain.BankRouting.route_origin
#print axioms CurrentMain.BankRouting.route_injective
#print axioms CurrentMain.BankRouting.reduction_route
