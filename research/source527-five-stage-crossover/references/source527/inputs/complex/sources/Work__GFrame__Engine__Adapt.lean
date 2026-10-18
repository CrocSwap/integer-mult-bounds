import Work.GFrame.Engine.Letters

/-!
# GFrame engine, part 2: the free adapter letters in the RAM (agent key: eng-ram)

One free adapter on the array of one role is ONE linear pass, no recursive call:

* `Gear.permuted`     the address of `x ↦ G.π x` (columnwise), O(1) per entry with the XOR table
                      (as `Gear.shifted`, through `Gear.body_additive` of `Work/Block/Address.lean`);
* `Gear.phase_row`    the `f`-bit row `(z·x_j + c)_j` of an entry, O(1);
* `GRig`              a rig together with the table of `lum` over `Bits f` (`i^popcount`);
* `Rig.perm_cost`, `GRig.phase_cost`   the two letters, work = length of the role table.
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.GF
open Binary Matrix Finset
noncomputable section
section
variable {α : Type*} [Fintype α] [DecidableEq α]

/-- An address permutation acts on an array with `f` columns by moving the address. -/
lemma act_perm (G : APerm α) (f : ℕ) (x : Sky α f → ℂ) (j : Sky α f) :
    matAct f (permMat G) x j = x (fun k => G.π (j k)) := by
  change ∑ i, digitProd (fun _ : Fin f => permMat G) j i * x i = _
  have h (i : Sky α f) : digitProd (fun _ : Fin f => permMat G) j i =
      if (fun k => G.π (j k)) = i then 1 else 0 :=
    prod_delta (κ:=fun _ : Fin f => Space α) _ _
  simp_rw [h]
  simp [ite_mul]

/-- A diagonal phase acts by the scalar `lum` of the row of phase bits. -/
lemma act_phase (z : Space α) (c : F) (f : ℕ) (x : Sky α f → ℂ) (j : Sky α f) :
    matAct f (phaseMat z c) x j = lum (fun k : Fin f => dot z (j k) + c) * x j := by
  unfold matAct phaseMat
  rw [digitProd_diagonal, Matrix.mulVec_diagonal]
  rfl

end
end
end PowerSaving.GF

namespace PowerSaving.RAM
open Binary Ty Finset GF
noncomputable section
universe U V
variable {ι : Type U}

namespace Gear
variable {m : Bool} {B f : ι → ℕ} {s t : Ty} {x : ι → T s}
variable (g : Gear m B f s x)
include g
variable {α : Type*} [Fintype α] [DecidableEq α] (X : Layout α) (r : ℕ)

/-- Address moved by an additive bijection (across the `f` columns). -/
lemma permuted (G : APerm α) (v : ∀ i, Grid α r (f i))
    (h : Knows m B s x (fun i => (book X r (f i)).loc (v i))) :
    Knows m B s x (fun i => (book X r (f i)).loc ((v i).1,
      fun j => G.π ((v i).2 j))) := by
  obtain ⟨hg, hh⟩ := g.grid_fetch X r (v:=v) h
  let K (i : ι) : Grid α r (f i) := ((v i).1, fun j => G.π ((v i).2 j))
  apply g.grid_combine X r (v:=K) hg (g.body_set X (fun i => (K i).2) _)
  intro a
  exact g.body_additive X (fun y => G.π y a) (fun p q => by rw [G.add]; rfl)
    (fun i => (v i).2) hh

/-- The row of phase bits `(z·x_j + c)_j` of an address. -/
lemma phase_row (z : Space α) (c : F) (v : ∀ i, Grid α r (f i))
    (h : Knows m B s x (fun i => (book X r (f i)).loc (v i))) :
    Knows m B s x (fun i => (bits (f i)).loc (fun l : Fin (f i) => dot z ((v i).2 l) + c)) := by
  obtain ⟨_, hh⟩ := g.grid_fetch X r (v:=v) h
  have hv := g.body_additive X (fun y => dot z y) (fun p q => dot_add_right z p q)
    (fun i => (v i).2) hh
  rcases bit_cases c with hc|hc
  · refine hv.cong (fun _ => rfl) (fun i => ?_)
    simp [hc]
  · let q i : Bits (f i) × Bits (f i) := (fun l => dot z ((v i).2 l), fun _ => 1)
    have hf : Knows m B s x (fun i => (bits (f i)).loc (q i).2) :=
      (g.power.minus (Can.wc 1) g.bound).cong (fun _ => rfl) (fun i => by
        change 2^f i-1=(bits _).loc (fun _ => 1)
        rw [← bits_lit]
        simp)
    refine (g.addr_xor q hv hf).cong (fun _ => rfl) (fun i => ?_)
    apply congr_arg (bits (f i)).loc
    ext k; simp [q,hc]

end Gear

/-- A rig together with the table of `lum` over `Bits f` (the fourth roots `i^popcount`). -/
structure GRig {α ρ : Type*} (m : Bool) (B f : ι → ℕ) (s : Ty) (x : ι → T s)
    (cl : Paint) (X : Layout α) (R : Layout ρ) (r : ℕ) (v : ∀ i, Grain α ρ r (f i)) : Prop where
  rig : Rig m B f s x cl X R r v
  lumT : Has m B s (a sc) x fun i => (bits (f i)).tape (fun y : Bits (f i) => lum y)

section
variable {α ρ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]
variable {m : Bool} {B f : ι → ℕ} {s t : Ty} {x : ι → T s}
    {cl : Paint} {X : Layout α} {R : Layout ρ} {r : ℕ} {v : ∀ i, Grain α ρ r (f i)}

omit [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ] in
lemma GRig.gather (h : GRig m B f s x cl X R r v) {κ : Type V} (j : κ → ι) (y : κ → T t)
    (g : Has m (fun k => B (j k)) t s y (fun k => x (j k))) :
    GRig m (fun k => B (j k)) (fun k => f (j k)) t y cl X R r (fun k => v (j k)) :=
  ⟨h.rig.gather j y g, g.then_do (h.lumT.reindex j)⟩

lemma Rig.ferry_perm (h : Rig m B f s x cl X R r v) (l : ρ) (G : APerm α)
    (q : ∀ i, Beach α ρ r (f i))
    (g : Knows m B s x fun i => (fleet X R r (f i)).loc (q i)) :
    Has m B s (c cl) x fun i => ferryM r (f i) l (permMat G) (v i) (q i) := by
  obtain ⟨hl,hk⟩ := h.addrs q g
  have hb := h.read q hl hk
  let t i : Beach α ρ r (f i) := ((q i).1,(q i).2.1,fun j => G.π ((q i).2.2 j))
  have hh := h.read t hl (h.gear.permuted X r G _ hk)
  apply Can.cases_code (q:=fun i => (q i).1) R hl
  intro p
  by_cases he : p=l
  · refine (hh.reindex (fun i : {i // (q i).1=p} => i.1)).cong (fun _ => rfl)
      (fun i => ?_)
    have hql : (q i.val).1 = l := i.property.trans he
    change v i.val ((q i.val).1,(q i.val).2.1,fun j => G.π ((q i.val).2.2 j)) = _
    simp only [ferryM, roleAct, hql, if_true, act_perm]
  · refine (hb.reindex (fun i : {i // (q i).1=p} => i.1)).cong (fun _ => rfl)
      (fun i => ?_)
    have H : (q i.val).1≠l := fun hh => he (i.property.symm.trans hh)
    simp only [ferryM, roleAct, H, ite_false, Prod.mk.eta]

/-- **Free address permutation**: one pass over the role table. -/
lemma Rig.perm_cost (h : Rig m B f s x cl X R r v) (l : ρ) (G : APerm α) :
    Can m B s (a (c cl)) x
      (fun i => (fleet X R r (f i)).tape (ferryM r (f i) l (permMat G) (v i)))
      (fun i => (fleet X R r (f i)).n) := by
  refine h.chart _ ?_
  let S := Σ i, Beach α ρ r (f i)
  have hg := h.gather (fun d : S => d.1)
    (fun d => ((x d.1, (fleet X R r (f d.1)).loc d.2):T (p s w))) (t:=p s w) Can.first
  exact hg.ferry_perm l G (fun d => d.2) Can.second

lemma GRig.ferry_phase (h : GRig m B f s x cl X R r v) (l : ρ) (z : Space α) (c' : F)
    (q : ∀ i, Beach α ρ r (f i))
    (g : Knows m B s x fun i => (fleet X R r (f i)).loc (q i)) :
    Has m B s (c cl) x fun i => ferryM r (f i) l (phaseMat z c') (v i) (q i) := by
  obtain ⟨hl,hk⟩ := h.rig.addrs q g
  have hb := h.rig.read q hl hk
  have hrow := h.rig.gear.phase_row X r z c' (fun i => (q i).2) hk
  have hs : Has m B s sc x
      (fun i => lum (fun k : Fin (f i) => dot z ((q i).2.2 k) + c')) :=
    Can.fetch (t:=sc) (L:=fun i => bits (f i)) (v:=fun i (y : Bits (f i)) => lum y)
      (i:=fun i => (fun k : Fin (f i) => dot z ((q i).2.2 k) + c')) h.lumT hrow
  have hh := hs.mul hb
  apply Can.cases_code (q:=fun i => (q i).1) R hl
  intro p
  by_cases he : p=l
  · refine (hh.reindex (fun i : {i // (q i).1=p} => i.1)).cong (fun _ => rfl)
      (fun i => ?_)
    have hql : (q i.val).1 = l := i.property.trans he
    change lum (fun k : Fin (f i.val) => dot z ((q i.val).2.2 k) + c') *
      v i.val ((q i.val).1,(q i.val).2.1,(q i.val).2.2) = _
    simp only [ferryM, roleAct, hql, if_true, act_phase]
  · refine (hb.reindex (fun i : {i // (q i).1=p} => i.1)).cong (fun _ => rfl)
      (fun i => ?_)
    have H : (q i.val).1≠l := fun hh => he (i.property.symm.trans hh)
    simp only [ferryM, roleAct, H, ite_false, Prod.mk.eta]

/-- **Free diagonal phase**: one pass over the role table (one table look-up per entry). -/
lemma GRig.phase_cost (h : GRig m B f s x cl X R r v) (l : ρ) (z : Space α) (c' : F) :
    Can m B s (a (c cl)) x
      (fun i => (fleet X R r (f i)).tape (ferryM r (f i) l (phaseMat z c') (v i)))
      (fun i => (fleet X R r (f i)).n) := by
  refine h.rig.chart _ ?_
  let S := Σ i, Beach α ρ r (f i)
  have hg := h.gather (fun d : S => d.1)
    (fun d => ((x d.1, (fleet X R r (f d.1)).loc d.2):T (p s w))) (t:=p s w) Can.first
  exact hg.ferry_phase l z c' (fun d => d.2) Can.second

end
end
end PowerSaving.RAM
end OAI

#print axioms OAI.PowerSaving.RAM.Rig.perm_cost
#print axioms OAI.PowerSaving.RAM.GRig.phase_cost
