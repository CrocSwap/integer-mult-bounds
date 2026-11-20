/-
UniTrans (lane UNI-TRANS, Nov 19).  The transpose of a banked graph, read through the mass accounting.  Kernel only.
  HData / ofG          : the height data of G that the masses read (bank src/dst charts, field A/B charts).
  rev, prp, tr         : reverse (bank.transpose: src<->dst, A<->B), chart perp C ↦ C⊥ (DB.perp, dim 9 - dim),
                         and the full transpose tr = prp ∘ rev.
  rev_D/prp_D/tr_D ... : EXACT accounting.  rev and prp swap descents and rises and negate the field climb;
                         tr keeps D, rises and climb.  So R(G) = D(G^T) is FALSE for tr (it reads R = D, i.e. W = 0;
                         PAD: R 56, D 64), and for rev/prp  D(G^T) = R(G) + Σc  (not R).
  rev_not_climb        : rev G violates the BankedGraph climb premise at every main field (cl = 8): G^T is not a
                         BankedGraph, so Theorem G cannot be applied to it as stated.
  hostedRise_eq_owned  : with a public bank set whose rises telescope to Σc (pub_telescope, the word fact),
                         R(G) = owned rise mass = owned DESCENT mass of rev G.  This is the correct transposed half.
  ownedRise_ge_of_emb  : a BankedGraph Gt with an injective bank map into G's owned banks, each descent of Gt at most
                         the rise of its image, gives descMass Gt ≤ owned rise.
  HasULayout / mass    : "G has a unified layout" (ULayout + ComputesS + ports + ≤ 8 pieces + OTI discharges) ⟹ D ≥ 56.
  kappa_word_lt_banner_trans : 17 graphs under the #7113 block, each with a unified layout (D side) and a transposed
                         owned-rise witness Gt carrying a unified layout (R side), plus telescope, HSContract, Valid
                         ⟹ κ < .0093453742.
  t7669 shape check (decide): 13 owned rise pieces glue at shared frames into 8 chains = reverses of the 8 descent
                         shapes, mass 56.  (Script trans/tr2.py: the 5 glues are same-frame, NONE carries value.)
-/
import Nov15.UniOwnedBank
import Nov15.BankUnifyB
import Nov15.DecoderBridge

set_option linter.unusedSectionVars false
namespace UniTrans
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie BankPrem
  BankCallerGen BankBig ThmG BankUnify UniOwnedBank T7669Data UniWC DecoderWall ChainRow BankMassF BankWireD

abbrev Chr := Submodule (ZMod 2) V

/-- height data of a banked graph. -/
structure HData (Fld Bank : Type) where
  src : Bank → Chr
  dst : Bank → Chr
  A : Fld → Chr
  B : Fld → Chr

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

namespace HData
variable (H : HData Fld Bank)

noncomputable def hh (c : Chr) : ℤ := (ht c : ℤ)
noncomputable def D : ℤ := ∑ k, max (hh (H.src k) - hh (H.dst k)) 0
noncomputable def Rise : ℤ := ∑ k, max (hh (H.dst k) - hh (H.src k)) 0
noncomputable def Cl : ℤ := ∑ f, (hh (H.B f) - hh (H.A f))

/-- reverse transpose (bank.transpose): banks and fields run backwards. -/
def rev : HData Fld Bank := ⟨H.dst, H.src, H.B, H.A⟩
/-- chart perp. -/
noncomputable def prp : HData Fld Bank := ⟨fun k => DB.perp (H.src k), fun k => DB.perp (H.dst k),
  fun f => DB.perp (H.A f), fun f => DB.perp (H.B f)⟩
/-- full transpose. -/
noncomputable def tr : HData Fld Bank := H.rev.prp

theorem hh_perp (c : Chr) : hh (DB.perp c) = 9 - hh c := by
  have h := DB.perp_rank c
  have h' : ht c + ht (DB.perp c) = 9 := h
  unfold hh; omega

theorem rev_D : H.rev.D = H.Rise := rfl
theorem rev_Rise : H.rev.Rise = H.D := rfl
theorem rev_Cl : H.rev.Cl = - H.Cl := by
  unfold Cl rev; simp only; rw [← Finset.sum_neg_distrib]; exact sum_congr rfl fun _ _ => by ring

theorem prp_D : H.prp.D = H.Rise := by
  unfold D Rise prp; simp only [hh_perp]; exact sum_congr rfl fun _ _ => by congr 1; ring
theorem prp_Rise : H.prp.Rise = H.D := by
  unfold D Rise prp; simp only [hh_perp]; exact sum_congr rfl fun _ _ => by congr 1; ring
theorem prp_Cl : H.prp.Cl = - H.Cl := by
  unfold Cl prp; simp only [hh_perp]; rw [← Finset.sum_neg_distrib]; exact sum_congr rfl fun _ _ => by ring

/-- the full transpose keeps D, the rises and the climb (so it keeps R and W). -/
theorem tr_D : H.tr.D = H.D := by unfold tr; rw [prp_D, rev_Rise]
theorem tr_Rise : H.tr.Rise = H.Rise := by unfold tr; rw [prp_Rise, rev_D]
theorem tr_Cl : H.tr.Cl = H.Cl := by unfold tr; rw [prp_Cl, rev_Cl]; ring

/-- owned split: rises / descents on banks outside the public set. -/
noncomputable def RiseOn (P : Bank → Prop) [DecidablePred P] : ℤ :=
  ∑ k ∈ univ.filter P, max (hh (H.dst k) - hh (H.src k)) 0
noncomputable def DOn (P : Bank → Prop) [DecidablePred P] : ℤ :=
  ∑ k ∈ univ.filter P, max (hh (H.src k) - hh (H.dst k)) 0

theorem rev_DOn (P : Bank → Prop) [DecidablePred P] : H.rev.DOn P = H.RiseOn P := rfl

theorem Rise_split (P : Bank → Prop) [DecidablePred P] :
    H.Rise = H.RiseOn P + H.RiseOn (fun k => ¬ P k) := by
  unfold Rise RiseOn; rw [sum_filter_add_sum_filter_not]

end HData

/-- the height data of a banked graph. -/
def ofG (G : BankedGraph ℚ Fld Bank) : HData Fld Bank := ⟨G.N.src, G.N.dst, G.N.A, G.N.B⟩

theorem descMass_ofG (G : BankedGraph ℚ Fld Bank) : descMass G = (ofG G).D := rfl

theorem Cl_ofG (G : BankedGraph ℚ Fld Bank) : (ofG G).Cl = ∑ f, (G.cl f : ℤ) := by
  unfold HData.Cl ofG HData.hh; simp only
  exact sum_congr rfl fun f _ => by have := (G.climb f).2; simp only [ht]; omega

theorem hostedRise_ofG (G : BankedGraph ℚ Fld Bank) : hostedRise G = (ofG G).Rise - (ofG G).Cl := by
  rw [Cl_ofG]; rfl

/-- **R(G) = D(rev G) - Σc**: the reverse transpose's descent mass is R PLUS the whole field climb. -/
theorem hostedRise_eq_rev (G : BankedGraph ℚ Fld Bank) : hostedRise G = (ofG G).rev.D - (ofG G).Cl := by
  rw [hostedRise_ofG, HData.rev_D]

/-- **the full transpose keeps D**: R(G) = D(G^T) holds iff R = D (W = 0), false in general (PAD). -/
theorem descMass_tr (G : BankedGraph ℚ Fld Bank) : (ofG G).tr.D = descMass G := HData.tr_D _

theorem hostedRise_tr (G : BankedGraph ℚ Fld Bank) : (ofG G).tr.Rise - (ofG G).tr.Cl = hostedRise G := by
  rw [HData.tr_Rise, HData.tr_Cl, hostedRise_ofG]

/-- **rev G is not a banked graph**: at a main field the reversed field descends by 8, so no climb witness. -/
theorem rev_not_climb (G : BankedGraph ℚ Fld Bank) (f : Fld) (hf : f ∈ G.Mn) :
    ¬ ∃ c : ℕ, ht ((ofG G).rev.B f) = ht ((ofG G).rev.A f) + c := by
  rintro ⟨c, hc⟩
  have h1 : ht (G.N.B f) = ht (G.N.A f) + G.cl f := (G.climb f).2
  have h2 := G.main8 f hf
  simp only [ofG, HData.rev] at hc
  omega

/-- **hosted half = owned rises**: if the public banks' rises telescope to (at least) the field climb, R is at least the
owned rise mass, which is the owned DESCENT mass of the reverse transpose (equality under exact telescoping). -/
theorem hostedRise_ge_owned (G : BankedGraph ℚ Fld Bank) (pub : Bank → Prop) [DecidablePred pub]
    (htel : ∑ f, (G.cl f : ℤ) ≤ (ofG G).RiseOn pub) :
    (ofG G).rev.DOn (fun k => ¬ pub k) ≤ hostedRise G := by
  rw [HData.rev_DOn, hostedRise_ofG, Cl_ofG, HData.Rise_split _ pub]; linarith

theorem hostedRise_eq_owned (G : BankedGraph ℚ Fld Bank) (pub : Bank → Prop) [DecidablePred pub]
    (htel : (ofG G).RiseOn pub = ∑ f, (G.cl f : ℤ)) :
    hostedRise G = (ofG G).rev.DOn (fun k => ¬ pub k) := by
  rw [HData.rev_DOn, hostedRise_ofG, Cl_ofG, HData.Rise_split _ pub]; linarith

/-- a banked transpose witness of the owned rises: every descent of Gt sits on a distinct owned rise of G. -/
theorem ownedRise_ge_of_emb {Ft Bt : Type} [Fintype Ft] [DecidableEq Ft] [Fintype Bt] [LinearOrder Bt]
    (Gt : BankedGraph ℚ Ft Bt) (G : BankedGraph ℚ Fld Bank) (pub : Bank → Prop) [DecidablePred pub]
    (e : Bt → Bank) (he : Function.Injective e)
    (hpub : ∀ j, (ht (Gt.N.dst j) : ℤ) < ht (Gt.N.src j) → ¬ pub (e j))
    (hle : ∀ j, (ht (Gt.N.src j) : ℤ) - ht (Gt.N.dst j) ≤ (ht (G.N.dst (e j)) : ℤ) - ht (G.N.src (e j))) :
    descMass Gt ≤ (ofG G).RiseOn (fun k => ¬ pub k) := by
  classical
  set g : Bank → ℤ := fun k => if pub k then 0 else max ((ht (G.N.dst k) : ℤ) - ht (G.N.src k)) 0 with hg
  have hg0 : ∀ k, 0 ≤ g k := fun k => by simp only [hg]; split_ifs <;> omega
  have step : ∀ j, max ((ht (Gt.N.src j) : ℤ) - ht (Gt.N.dst j)) 0 ≤ g (e j) := by
    intro j
    by_cases hd : (ht (Gt.N.dst j) : ℤ) < ht (Gt.N.src j)
    · have := hpub j hd; have := hle j; simp only [hg, if_neg (hpub j hd)]; omega
    · have := hg0 (e j); omega
  calc descMass Gt = ∑ j, max ((ht (Gt.N.src j) : ℤ) - ht (Gt.N.dst j)) 0 := rfl
    _ ≤ ∑ j, g (e j) := sum_le_sum fun j _ => step j
    _ = ∑ k ∈ univ.image e, g k := (sum_image fun a _ b _ h => he h).symm
    _ ≤ ∑ k, g k := sum_le_sum_of_subset_of_nonneg (subset_univ _) fun k _ _ => hg0 k
    _ = (ofG G).RiseOn (fun k => ¬ pub k) := by
        unfold HData.RiseOn; rw [sum_filter]
        exact sum_congr rfl fun k _ => by simp only [hg, ofG, HData.hh]; split_ifs <;> simp_all

/-- **G has a unified layout** (with its discharges): the hypothesis of the unified floor, packaged. -/
def HasULayout (G : BankedGraph ℚ Fld Bank) : Prop :=
  ∃ (R Tr Tu Tz C D : Type) (_ : Fintype R) (_ : Fintype Tr) (_ : Fintype Tu) (_ : Fintype Tz)
    (_ : DecidableEq Tr) (_ : DecidableEq Tu) (_ : Fintype C) (_ : DecidableEq C) (_ : Fintype D)
    (_ : DecidableEq D) (Λ : ULayout G R Tr Tu Tz) (cs : Fin 104 → ℚ) (cr : R → C) (ct : Tr → C)
    (dr : R → D) (du : Tu → D),
    ComputesS G Λ.xin Λ.yout cs ∧ (∀ p, DF.lq p ∈ G.N.A (Λ.xin p)) ∧
    (∀ s, ∀ y ∈ G.N.B (Λ.yout s), dot (DF.lq s) y = 0) ∧ Λ.pieces ≤ 8 ∧
    (∀ c, Λ.DischW cr ct c) ∧ (∀ d, Λ.DischU dr du d)

theorem HasULayout.mass {G : BankedGraph ℚ Fld Bank} (h : HasULayout G) : 56 ≤ descMass G := by
  obtain ⟨R, Tr, Tu, Tz, C, D, _, _, _, _, _, _, _, _, _, _, Λ, cs, cr, ct, dr, du, hC, hin, hout, h8, hW, hU⟩ := h
  exact Λ.mass_ge_56_disch cs hC hin hout h8 cr ct dr du hW hU

/-- **the transposed half**: a transpose witness Gt of G's owned rises carrying a unified layout gives R ≥ 56. -/
structure TransWitness (G : BankedGraph ℚ Fld Bank) where
  pub : Bank → Prop
  dpub : DecidablePred pub
  tel : ∑ f, (G.cl f : ℤ) ≤ @HData.RiseOn _ _ _ (ofG G) pub dpub
  Ft : Type
  Bt : Type
  iFt : Fintype Ft
  dFt : DecidableEq Ft
  iBt : Fintype Bt
  oBt : LinearOrder Bt
  Gt : BankedGraph ℚ Ft Bt
  e : Bt → Bank
  inj : Function.Injective e
  hpub : ∀ j, (ht (Gt.N.dst j) : ℤ) < ht (Gt.N.src j) → ¬ pub (e j)
  hle : ∀ j, (ht (Gt.N.src j) : ℤ) - ht (Gt.N.dst j) ≤ (ht (G.N.dst (e j)) : ℤ) - ht (G.N.src (e j))
  lay : HasULayout Gt

theorem TransWitness.hR {G : BankedGraph ℚ Fld Bank} (T : TransWitness G) : 56 ≤ hostedRise G := by
  letI := T.dpub; letI := T.iFt; letI := T.dFt; letI := T.iBt; letI := T.oBt
  have h1 := T.lay.mass
  have h2 := ownedRise_ge_of_emb T.Gt G T.pub T.e T.inj T.hpub T.hle
  have h3 := hostedRise_ge_owned G T.pub T.tel
  rw [HData.rev_DOn] at h3
  linarith

/-- **`kappa_word_lt_banner_trans`**: 17 graphs under the #7113 caller block, each with a unified layout (live half
D ≥ 56) and a transpose witness with a unified layout (hosted half R ≥ 56): κ < .0093453742. -/
theorem kappa_word_lt_banner_trans (c : Caller ℚ Fld Bank 17) (hT : c.T = Tcal) (hP : c.P = Pcal)
    (hc : ∀ i, HSContract (c.G i).N) (hLD : ∀ i, HasULayout (c.G i)) (hLR : ∀ i, TransWitness (c.G i))
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 93453742 / 10000000000 :=
  kappa_word_lt_banner c hT hP hc (fun i => (hLD i).mass) (fun i => (hLR i).hR) κ hκ0 hκ1 hV

end UniTrans

/-! ## t7669 transposed-shape check (decide).  Data: cards/WILD/UNIMODEL/trans/tr2.py on GEN/STACK/t7669.json.gz.
Piece = (start frame, dims, end frame).  Glue = the unique piece starting at a piece's end frame. -/
namespace UniTransT7669

def pieces : List (ℕ × List ℕ × ℕ) :=
  [(601, [1,3,4,8], 477), (599, [1,3,4], 1091), (600, [1,3,4,8], 517), (598, [1,3,4,8], 518), (529, [7,8], 531),
   (595, [1,6,7], 529), (549, [7,8], 559), (593, [1,7], 549), (594, [1,5,6,7], 541), (597, [1,5], 1031),
   (1031, [5,8], 591), (541, [7,8], 543), (1091, [4,8], 267)]

/-- descent chain shapes of t7669 (L5 / um1). -/
def descShapes : List (List ℕ) :=
  [[8,4,3,1], [8,4,3,1], [8,4,3,1], [8,4,3,1], [8,5,1], [8,7,1], [8,7,6,1], [8,7,6,5,1]]

def heads : List (ℕ × List ℕ × ℕ) := pieces.filter fun p => !(pieces.any fun q => q.2.2 = p.1)

/-- one same-frame glue step. -/
def glue (p : ℕ × List ℕ × ℕ) : List ℕ :=
  match pieces.find? (fun q => q.1 = p.2.2) with
  | some q => p.2.1 ++ q.2.1.tail
  | none => p.2.1

def chains : List (List ℕ) := heads.map glue

def mass (l : List ℕ) : ℕ := l.getLast! - l.head!

theorem glue_unique : ∀ p ∈ pieces, (pieces.filter fun q => q.1 = p.2.2).length ≤ 1 := by decide
theorem glued_no_second : ∀ p ∈ pieces, ∀ q ∈ pieces, q.1 = p.2.2 → ¬ pieces.any (fun r => r.1 = q.2.2) := by decide
theorem eight_chains : chains.length = 8 := by decide
theorem chains_are_transposed : (chains.map List.reverse).isPerm descShapes = true := by decide
theorem pieces_mass : (pieces.map fun p => mass p.2.1).sum = 56 := by decide
theorem chains_mass : (chains.map mass).sum = 56 := by decide
theorem chain_masses : chains.map mass = [7,7,7,7,7,7,7,7] := by decide

end UniTransT7669

#print axioms UniTrans.hostedRise_eq_rev
#print axioms UniTrans.descMass_tr
#print axioms UniTrans.rev_not_climb
#print axioms UniTrans.hostedRise_eq_owned
#print axioms UniTrans.TransWitness.hR
#print axioms UniTrans.kappa_word_lt_banner_trans
#print axioms UniTransT7669.chains_are_transposed
