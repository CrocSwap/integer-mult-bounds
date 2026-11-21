/-
BankUnifyB (lane LEAN-UNIFY, Nov 19).  The unified banner.  Kernel only.
  DischW / DischU      : per-component OTI evidence: (i) FOLD-disjoint (ancestor / tail sets of the component's groups
                         pairwise disjoint and inside the component), (ii) HALL (heads δ ≤ 1, members drop ≥ 1,
                         #small heads ≤ #members), or (iii) the named hypothesis OTIComp.  (i), (ii) are facts about G.
  mass_ge_56_disch     : ULayout + discharges ⟹ descMass G ≥ 56.
  bank_kappa_lt_unified: κ < .00952721 for every K-call caller (sign form) and every banked graph with a unified layout.
  bank_kappa_lt_unified_fam / _disjoint : family form; hypothesis-free OTI (one component per side, disjoint lists).
  ofDescentLayout      : every BankBig.DescentLayout is a ULayout (no trunks/tails; zigzags → groups; W1 → free chains),
                         same pieces.
  ofGLayout            : every ThmG.GLayout with nonempty groups is a ULayout (tails at the group end), pieces = |R|.
  kappa7761_lt_unified : #7761 through ofGLayout ∘ ofChainTieG (8 groups); only Valid remains.
-/
import Nov15.BankUnifyA

open Module Submodule Finset

namespace BankUnify
open DecoderWall ChainRow BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie
  BankPrem BankCallerGen BankBig ThmG

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]
variable {G : BankedGraph ℚ Fld Bank} {R Tr Tu Tz : Type} [Fintype R] [Fintype Tr] [Fintype Tu] [Fintype Tz]
  [DecidableEq Tr] [DecidableEq Tu]

namespace ULayout
variable (Λ : ULayout G R Tr Tu Tz)

/-- W-side component evidence. -/
def DischW {C : Type} [DecidableEq C] (cr : R → C) (ct : Tr → C) (c : C) : Prop :=
  ((∀ r, cr r = c → ∀ t ∈ Λ.ancL r, ct t = c) ∧
    ∀ r r', cr r = c → cr r' = c → r ≠ r' → Disjoint (Λ.ancL r).toFinset (Λ.ancL r').toFinset) ∨
  ((∀ r, cr r = c → dW (Λ.hd r) ≤ 1) ∧ (∀ t, ct t = c → 1 ≤ Λ.dTr t) ∧
    (univ.filter (fun r => cr r = c ∧ 1 ≤ dW (Λ.hd r))).card ≤ (univ.filter (fun t => ct t = c)).card) ∨
  OTIComp (fun r => dW (Λ.hd r)) Λ.dTr cr ct c

/-- U-side component evidence. -/
def DischU {D : Type} [DecidableEq D] (dr : R → D) (du : Tu → D) (d : D) : Prop :=
  ((∀ r, dr r = d → ∀ u ∈ Λ.tailL r, du u = d) ∧
    ∀ r r', dr r = d → dr r' = d → r ≠ r' → Disjoint (Λ.tailL r).toFinset (Λ.tailL r').toFinset) ∨
  ((∀ r, dr r = d → dU (Λ.en r) ≤ 1) ∧ (∀ u, du u = d → 1 ≤ Λ.dTu u) ∧
    (univ.filter (fun r => dr r = d ∧ 1 ≤ dU (Λ.en r))).card ≤ (univ.filter (fun u => du u = d)).card) ∨
  OTIComp (fun r => dU (Λ.en r)) Λ.dTu dr du d

/-- **D ≥ 56, unified.** -/
theorem mass_ge_56_disch (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Λ.pieces ≤ 8) {C D : Type} [Fintype C] [DecidableEq C] [Fintype D] [DecidableEq D]
    (cr : R → C) (ct : Tr → C) (dr : R → D) (du : Tu → D)
    (hWc : ∀ c, Λ.DischW cr ct c) (hUc : ∀ d, Λ.DischU dr du d) : 56 ≤ descMass G := by
  have hcore := (Λ.core cs hC hin hout h8).2
  have hfb := Λ.fold_bounds cs hC hin hout h8
  have hW := oti_of_comp (fun r => dW (Λ.hd r)) Λ.dTr cr ct fun c => by
    rcases hWc c with ⟨hin', hdis⟩ | ⟨h1, h2, h3⟩ | h
    · exact otiComp_disjoint _ _ _ _ c (fun r => (Λ.ancL r).toFinset) (fun r _ => (hfb r).1)
        (fun r hr t ht => hin' r hr t (List.mem_toFinset.1 ht)) hdis
    · exact otiComp_hall _ _ _ _ c h1 h2 h3
    · exact h
  have hU := oti_of_comp (fun r => dU (Λ.en r)) Λ.dTu dr du fun d => by
    rcases hUc d with ⟨hin', hdis⟩ | ⟨h1, h2, h3⟩ | h
    · exact otiComp_disjoint _ _ _ _ d (fun r => (Λ.tailL r).toFinset) (fun r _ => (hfb r).2)
        (fun r hr u hu => hin' r hr u (List.mem_toFinset.1 hu)) hdis
    · exact otiComp_hall _ _ _ _ d h1 h2 h3
    · exact h
  linarith

/-- hypothesis-free: every trunk feeds ≤ 1 group and every tail is fed by ≤ 1 group. -/
theorem mass_ge_56_disjoint (cs : Fin 104 → ℚ) (hC : ComputesS G Λ.xin Λ.yout cs)
    (hin : ∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) (hout : ∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0)
    (h8 : Λ.pieces ≤ 8)
    (hdW : ∀ r r', r ≠ r' → Disjoint (Λ.ancL r).toFinset (Λ.ancL r').toFinset)
    (hdU : ∀ r r', r ≠ r' → Disjoint (Λ.tailL r).toFinset (Λ.tailL r').toFinset) : 56 ≤ descMass G :=
  Λ.mass_ge_56_disch cs hC hin hout h8 (fun _ => ()) (fun _ => ()) (fun _ => ()) (fun _ => ())
    (fun _ => Or.inl ⟨fun _ _ _ _ => rfl, fun r r' _ _ h => hdW r r' h⟩)
    (fun _ => Or.inl ⟨fun _ _ _ _ => rfl, fun r r' _ _ h => hdU r r' h⟩)

end ULayout

/-! ## the unified κ bound -/

/-- **`bank_kappa_lt_unified`** (sign-condition form): every K-call caller whose block satisfies
cdat T − cdat P ≤ K (cdat T1 − cdat P1) on [0,1], every per-call banked graph carrying a unified layout (≤ 8 pieces)
with per-component OTI evidence on both sides: κ < .00952721. -/
theorem bank_kappa_lt_unified (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu Tz : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, Fintype (Tz i)] [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, ULayout (c.G i) (R i) (Tr i) (Tu i) (Tz i)) (h8 : ∀ i, (Λ i).pieces ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {C D : Fin K → Type} [∀ i, Fintype (C i)] [∀ i, DecidableEq (C i)] [∀ i, Fintype (D i)]
    [∀ i, DecidableEq (D i)] (cr : ∀ i, R i → C i) (ct : ∀ i, Tr i → C i) (dr : ∀ i, R i → D i)
    (du : ∀ i, Tu i → D i) (hWc : ∀ i c', (Λ i).DischW (cr i) (ct i) c')
    (hUc : ∀ i d', (Λ i).DischU (dr i) (du i) d')
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  kappa_of_mass K hK c hTP hc
    (fun i => (Λ i).mass_ge_56_disch (cs i) (hC i) (hin i) (hout i) (h8 i) (cr i) (ct i) (dr i) (du i)
      (hWc i) (hUc i)) oi oc hF hW κ hκ0 hκ1 hV

/-- family form: T = K·T1 ++ Tc, P = K·P1 ++ Pc with cdat Tc ≤ cdat Pc on [0,1]. -/
theorem bank_kappa_lt_unified_fam (K : ℕ) (hK : 0 < K) (Tc Pc : List (ℕ × ℕ))
    (hsign : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s Tc ≤ cdat s Pc) (c : Caller ℚ Fld Bank K)
    (hT : c.T = famT K Tc) (hP : c.P = famP K Pc) (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu Tz : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, Fintype (Tz i)] [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, ULayout (c.G i) (R i) (Tr i) (Tu i) (Tz i)) (h8 : ∀ i, (Λ i).pieces ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {C D : Fin K → Type} [∀ i, Fintype (C i)] [∀ i, DecidableEq (C i)] [∀ i, Fintype (D i)]
    [∀ i, DecidableEq (D i)] (cr : ∀ i, R i → C i) (ct : ∀ i, Tr i → C i) (dr : ∀ i, R i → D i)
    (du : ∀ i, Tu i → D i) (hWc : ∀ i c', (Λ i).DischW (cr i) (ct i) c')
    (hUc : ∀ i d', (Λ i).DischU (dr i) (du i) d')
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified K hK c (by rw [hT, hP]; exact hTP_fam K Tc Pc hsign) hc Λ h8 cs hC hin hout
    cr ct dr du hWc hUc oi oc hF hW κ hκ0 hκ1 hV

/-- hypothesis-free OTI: every trunk feeds ≤ 1 group and every tail is fed by ≤ 1 group (per call). -/
theorem bank_kappa_lt_unified_disjoint (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {R Tr Tu Tz : Fin K → Type} [∀ i, Fintype (R i)] [∀ i, Fintype (Tr i)] [∀ i, Fintype (Tu i)]
    [∀ i, Fintype (Tz i)] [∀ i, DecidableEq (Tr i)] [∀ i, DecidableEq (Tu i)]
    (Λ : ∀ i, ULayout (c.G i) (R i) (Tr i) (Tu i) (Tz i)) (h8 : ∀ i, (Λ i).pieces ≤ 8)
    (cs : Fin K → Fin 104 → ℚ) (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    (hdW : ∀ i r r', r ≠ r' → Disjoint ((Λ i).ancL r).toFinset ((Λ i).ancL r').toFinset)
    (hdU : ∀ i r r', r ≠ r' → Disjoint ((Λ i).tailL r).toFinset ((Λ i).tailL r').toFinset)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  kappa_of_mass K hK c hTP hc
    (fun i => (Λ i).mass_ge_56_disjoint (cs i) (hC i) (hin i) (hout i) (h8 i) (hdW i) (hdU i))
    oi oc hF hW κ hκ0 hκ1 hV

/-! ## both earlier structures are unified layouts -/

/-- a BankBig zigzag as a unified group. -/
def uOfZig {n : ℕ} (P : ZigPre n) : UPre := ⟨P.a, P.b, P.b_le, P.route, P.fresh, P.beta, P.beta_ne⟩

theorem uOfZig_carried {n : ℕ} (P : ZigPre n) : ∀ k, (uOfZig P).carried k = P.carried k
  | 0 => rfl
  | k + 1 => by
    funext p
    show P.beta (k + 1) * (uOfZig P).carried k p + P.fresh (k + 1) p = _
    rw [uOfZig_carried P k]; rfl

/-- a Theorem-G pure group as a unified group. -/
def uOfH (H : HPre) : UPre :=
  ⟨H.ch, fun j => H.ch (j + 1), H.desc, fun _ => le_refl _, H.fresh, H.beta, H.beta_ne⟩

theorem uOfH_carried (H : HPre) : ∀ k, (uOfH H).carried k = H.carried k
  | 0 => rfl
  | k + 1 => by
    funext p
    show H.beta (k + 1) * (uOfH H).carried k p + H.fresh (k + 1) p = _
    rw [uOfH_carried H k]; rfl

variable {T U : Type} [Fintype T] [Fintype U]

/-- **BankBig ⊂ unified.** -/
def ofDescentLayout (Λ : DescentLayout G T U) : ULayout G U Empty Empty T where
  xin := Λ.xin
  yout := Λ.yout
  zl := Λ.zl
  grp := fun u => uOfZig (Λ.zg u)
  eg := fun x => Λ.e (Sum.inr x)
  eT := fun t => t.elim
  eU := fun u => u.elim
  zlen := Λ.len
  zch := Λ.zch
  ez := fun x => Λ.e (Sum.inl x)
  inj := by
    rintro (x | x | x | x) (y | y | y | y) h
    all_goals first | exact x.elim | exact y.elim | skip
    · exact congrArg Sum.inl (Sum.inr.inj (Λ.inj h))
    · exact absurd (Λ.inj h) (by simp)
    · exact absurd (Λ.inj h) (by simp)
    · exact congrArg (Sum.inr ∘ Sum.inr ∘ Sum.inr) (Sum.inl.inj (Λ.inj h))
  gsrc := fun x => Λ.gsrc x
  gdst := fun x => Λ.gdst x
  gcar := fun x p => by rw [uOfZig_carried]; exact Λ.gcar x p
  zsrc := fun x => Λ.zsrc x
  zdst := fun x => Λ.zdst x
  zcar := fun x p => Λ.zcar x p
  ancL := fun _ => []
  anc_nodup := fun _ => List.nodup_nil
  anc_ord := fun _ => trivial
  tdesc := fun t => t.elim
  dep := fun r j p _ hf => (Λ.zg r).fresh_in j p hf
  reasc := fun r k j p hkj _ hG hf => Λ.reasc r k j hkj hG ⟨p, hf⟩ ((Λ.zg r).fresh_supp j p hf)
  gath_ge := fun r k hG => Λ.gath_ge r k hG
  mu := fun u => u.elim
  att := fun u => u.elim
  att_le := fun u => u.elim
  ucar := fun u => u.elim
  ureasc := fun u => u.elim
  tailL := fun _ => []
  tail_nodup := fun _ => List.nodup_nil
  tail_mem := fun u => u.elim
  tail_ord := fun _ => trivial
  udesc := fun u => u.elim
  silent := fun k hk => by
    rcases Λ.silent k hk with ⟨x | x, hx⟩ | h0 | hng
    · exact Or.inr (Or.inr (Or.inl ⟨x, hx⟩))
    · exact Or.inl ⟨x, hx⟩
    · exact Or.inr (Or.inr (Or.inr (Or.inl h0)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr hng)))

theorem ofDescentLayout_pieces (Λ : DescentLayout G T U) : (ofDescentLayout Λ).pieces = Λ.pieces := rfl

/-- step re-indexing Fin (len − 1 + 1) ≃ Fin len for nonempty groups. -/
def stepEq {R : Type} (len : R → ℕ) (hlen : ∀ r, 0 < len r) :
    (Σ r : R, Fin (len r - 1 + 1)) ≃ (Σ r : R, Fin (len r)) :=
  Equiv.sigmaCongrRight fun r => finCongr (Nat.sub_add_cancel (hlen r))

/-- **Theorem G ⊂ unified** (tails attach at the last step). -/
noncomputable def ofGLayout (Λ : GLayout G R Tr Tu) (hlen : ∀ r, 0 < Λ.len r) : ULayout G R Tr Tu Empty where
  xin := Λ.xin
  yout := Λ.yout
  zl := fun r => Λ.len r - 1
  grp := fun r => uOfH (Λ.grp r)
  eg := fun x => Λ.eg (stepEq Λ.len hlen x)
  eT := Λ.eT
  eU := Λ.eU
  zlen := fun c => c.elim
  zch := fun c => c.elim
  ez := fun x => x.1.elim
  inj := by
    let F : (Σ r : R, Fin (Λ.len r - 1 + 1)) ⊕ (Tr ⊕ (Tu ⊕ (Σ c : Empty, Fin c.elim))) →
        (Σ r : R, Fin (Λ.len r)) ⊕ (Tr ⊕ Tu) :=
      Sum.map (stepEq Λ.len hlen) (Sum.map id (Sum.elim id fun z => z.1.elim))
    have hF : Function.Injective F := by
      refine Sum.map_injective.2 ⟨(stepEq Λ.len hlen).injective, Sum.map_injective.2 ⟨Function.injective_id, ?_⟩⟩
      rintro (a | a) (b | b) h
      · exact congrArg Sum.inl h
      · exact b.1.elim
      · exact a.1.elim
      · exact a.1.elim
    have e : Sum.elim (fun x => Λ.eg (stepEq Λ.len hlen x))
        (Sum.elim Λ.eT (Sum.elim Λ.eU fun x : (Σ c : Empty, Fin c.elim) => x.1.elim)) =
        Sum.elim Λ.eg (Sum.elim Λ.eT Λ.eU) ∘ F := by
      funext x; rcases x with x | x | x | x
      · rfl
      · rfl
      · rfl
      · exact x.1.elim
    rw [e]; exact Λ.inj.comp hF
  gsrc := fun x => Λ.gsrc (stepEq Λ.len hlen x)
  gdst := fun x => Λ.gdst (stepEq Λ.len hlen x)
  gcar := fun x p => by rw [uOfH_carried]; exact Λ.gcar (stepEq Λ.len hlen x) p
  zsrc := fun x => x.1.elim
  zdst := fun x => x.1.elim
  zcar := fun x => x.1.elim
  ancL := Λ.ancL
  anc_nodup := Λ.anc_nodup
  anc_ord := Λ.anc_ord
  tdesc := Λ.tdesc
  dep := fun r j p _ hf => by
    rcases Nat.eq_zero_or_pos j with rfl | hj0
    · exact Λ.head_supp r p hf
    · exact le_hullW _ _ _ ((Λ.grp r).antitone_ch (Nat.zero_le j) ((Λ.grp r).fresh_supp j p hj0 hf))
  reasc := fun r k j p hkj _ _ hf =>
    (Λ.grp r).antitone_ch (show (k : ℕ) + 1 ≤ j by omega) ((Λ.grp r).fresh_supp j p (by omega) hf)
  gath_ge := fun r k _ => inf_le_right.trans ((Λ.grp r).antitone_ch (show (k : ℕ) + 1 ≤ Λ.len r - 1 + 1 by
    have := k.2; omega))
  mu := Λ.mu
  att := fun _ r => Λ.len r - 1
  att_le := fun _ _ _ => le_refl _
  ucar := fun u p => by
    rw [Λ.ucar]
    refine sum_congr rfl fun r _ => ?_
    rw [uOfH_carried]
  ureasc := fun _ _ _ _ _ _ h1 h2 => absurd h2 (by omega)
  tailL := Λ.tailL
  tail_nodup := Λ.tail_nodup
  tail_mem := Λ.tail_mem
  tail_ord := fun r => by
    show OrdU _ _ ((Λ.grp r).ch 0 ⊓ (Λ.grp r).ch (Λ.len r - 1 + 1)) _
    rw [Nat.sub_add_cancel (hlen r), inf_eq_right.2 ((Λ.grp r).antitone_ch (Nat.zero_le _))]
    exact Λ.tail_ord r
  udesc := Λ.udesc
  silent := fun k hk => by
    rcases Λ.silent k hk with ⟨x, hx⟩ | ⟨u, hu⟩ | h0 | hng
    · exact Or.inl ⟨(stepEq Λ.len hlen).symm x, by simp only [Equiv.apply_symm_apply]; exact hx⟩
    · exact Or.inr (Or.inl ⟨u, hu⟩)
    · exact Or.inr (Or.inr (Or.inr (Or.inl h0)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr hng)))

theorem ofGLayout_pieces (Λ : GLayout G R Tr Tu) (hlen) : (ofGLayout Λ hlen).pieces = Fintype.card R := by
  simp [ULayout.pieces]

end BankUnify

namespace Bridge7761
open BankUnify ThmG BankBig BankTie BankPrem BankCallerGen

theorem len7761_pos (r : Fin 8) : 0 < (ofChainTieG τ7761 hcov7761G).len r := by
  show 0 < clen r
  fin_cases r <;> decide

/-- **NON-VACUITY (group branch)**: #7761 instantiates `bank_kappa_lt_unified_disjoint` with its 8 chains entered as
unified GROUPS (ofGLayout ∘ ofChainTieG); only Valid remains. -/
theorem kappa7761_lt_unified (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified_disjoint 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761)
    (fun _ => HS7761 hO7761) (R := fun _ => Fin 8) (Tr := fun _ => Empty) (Tu := fun _ => Empty)
    (Tz := fun _ => Empty) (fun _ => ofGLayout (ofChainTieG τ7761 hcov7761G) len7761_pos)
    (fun _ => (ofGLayout_pieces _ _).trans_le (by simp)) (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy)
    (fun _ r r' _ => by simp [ofGLayout, ofChainTieG]) (fun _ r r' _ => by simp [ofGLayout, ofChainTieG])
    (fun _ => fun e : Empty => e.elim) (fun _ => fun e : Empty => e.elim)
    (fun _ => gflow7761) (fun _ => le_of_eq gW7761.symm) κ hκ0 hκ1 hV

/-- **NON-VACUITY (W1 branch)**: #7761 through ofDescentLayout ∘ ofChainTie (8 free chains). -/
theorem kappa7761_lt_unified_W1 (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_unified_disjoint 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761)
    (fun _ => HS7761 hO7761) (R := fun _ => Empty) (Tr := fun _ => Empty) (Tu := fun _ => Empty)
    (Tz := fun _ => Fin 8) (fun _ => ofDescentLayout (ofChainTie τ7761 hcov7761G))
    (fun _ => ((ofDescentLayout_pieces _).trans (ofChainTie_pieces τ7761 hcov7761G)).trans_le (by simp))
    (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy)
    (fun _ r => r.elim) (fun _ r => r.elim)
    (fun _ => fun e : Empty => e.elim) (fun _ => fun e : Empty => e.elim)
    (fun _ => gflow7761) (fun _ => le_of_eq gW7761.symm) κ hκ0 hκ1 hV

end Bridge7761

#print axioms BankUnify.ULayout.mass_ge_56_disch
#print axioms BankUnify.ULayout.mass_ge_56_disjoint
#print axioms BankUnify.bank_kappa_lt_unified
#print axioms BankUnify.bank_kappa_lt_unified_fam
#print axioms BankUnify.bank_kappa_lt_unified_disjoint
#print axioms BankUnify.ofDescentLayout
#print axioms BankUnify.ofGLayout
#print axioms Bridge7761.kappa7761_lt_unified
#print axioms Bridge7761.kappa7761_lt_unified_W1
