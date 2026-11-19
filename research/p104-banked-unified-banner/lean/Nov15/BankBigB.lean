/-
BankBigB.  THE BIG BANNER: mass-floor decoder (BankBigA, five Theorem-W shapes and
mixtures, tied to G) × generic caller (BankCallerGen.cert_gen).  Kernel only.
  bank_kappa_lt_big_gen : any K > 0 calls whose block satisfies cdat T − cdat P ≤ K (cdat T1 − cdat P1) on [0,1].
  bank_kappa_lt_big     : family form: T = K·T1 ++ Tc, P = K·P1 ++ Pc, cdat Tc ≤ cdat Pc on [0,1]  ⟹  κ < .00952721.
  ofChainTie            : every BankTie.ChainTie + hcov is a DescentLayout (pure-chain case, U = Empty, pieces = card T).
  kappa7761_lt_big      : NON-VACUITY: #7761 (τ7761, 8 pure chains, G7761, caller7761 = 2048 calls) instantiates
                          bank_kappa_lt_big_gen; remaining hypothesis: Valid only.
Per call the layout types T i, U i may differ.
-/
import Nov15.BankBigA
import Nov15.BankCallerGen
import Nov15.Bridge7761T4

namespace BankBig
open Finset Module BankNC0 BankWireC BankFit BankHelp BankBanner SafeRungsPrice BankFitHS BankTie BankPrem
  DecoderWall BankCallerGen

variable {Fld Bank : Type} [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- **BIG BANNER (sign-condition form).** -/
theorem bank_kappa_lt_big_gen (K : ℕ) (hK : 0 < K) (c : Caller ℚ Fld Bank K)
    (hTP : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s c.T - cdat s c.P ≤ K * (cdat s T1 - cdat s P1))
    (hc : ∀ i, HSContract (c.G i).N)
    {T U : Fin K → Type} [∀ i, Fintype (T i)] [∀ i, Fintype (U i)]
    (Λ : ∀ i, DescentLayout (c.G i) (T i) (U i)) (h8 : ∀ i, (Λ i).pieces ≤ 8) (cs : Fin K → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 := by
  have hD : ∀ i, 56 ≤ descMass (c.G i) := fun i =>
    layout_mass_ge_56 (Λ i) (cs i) (hC i) (hin i) (hout i) (h8 i)
  have hXD : ∀ i, 2 * descMass (c.G i) ≤ excess (c.G i) := fun i => xbal_tied (c.G i) (oi i) (oc i) (hF i) (hW i)
  exact bank_kappa_lt_banner_of_cert K c.T c.P _ (by norm_num) (cert_gen K hK c.T c.P hTP) c.G hc hD hXD
    κ hκ0 hκ1 _ (fun i k => bankPrice_le_specInvoice (c.G i) (by linarith) k) (hcaller_of_valid c _ _ hV)

/-- **BIG BANNER `bank_kappa_lt_big`** (family form): every banked graph with a tied descent layout of the five
Theorem-W shapes (≤ 8 pieces), every K-call caller of the family, κ < .00952721. -/
theorem bank_kappa_lt_big (K : ℕ) (hK : 0 < K) (Tc Pc : List (ℕ × ℕ))
    (hsign : ∀ s : ℝ, 0 ≤ s → s ≤ 1 → cdat s Tc ≤ cdat s Pc) (c : Caller ℚ Fld Bank K)
    (hT : c.T = famT K Tc) (hP : c.P = famP K Pc)
    (hc : ∀ i, HSContract (c.G i).N)
    {T U : Fin K → Type} [∀ i, Fintype (T i)] [∀ i, Fintype (U i)]
    (Λ : ∀ i, DescentLayout (c.G i) (T i) (U i)) (h8 : ∀ i, (Λ i).pieces ≤ 8) (cs : Fin K → Fin 104 → ℚ)
    (hC : ∀ i, ComputesS (c.G i) (Λ i).xin (Λ i).yout (cs i))
    (hin : ∀ i p, DF.lq p ∈ (c.G i).N.A ((Λ i).xin p))
    (hout : ∀ i s, ∀ y ∈ (c.G i).N.B ((Λ i).yout s), dot (DF.lq s) y = 0)
    {O : Type} [Fintype O] (oi oc : Fin K → O → Chart)
    (hF : ∀ i, (gModel (c.G i) (oi i) (oc i)).Flow) (hW : ∀ i, 0 ≤ (gModel (c.G i) (oi i) (oc i)).W)
    (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid c (1 - κ) (fun i k => specInvoice (c.G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_big_gen K hK c (by rw [hT, hP]; exact hTP_fam K Tc Pc hsign) hc Λ h8 cs hC hin hout
    oi oc hF hW κ hκ0 hκ1 hV

/-! ## pure-chain case: ChainTie ⟹ DescentLayout -/

variable {G : BankedGraph ℚ Fld Bank} {T : Type} [Fintype T]

def zOfRelay {m : ℕ} (C : ChainRow.RelayChain ℚ DF.lq m) : ZPre :=
  ⟨C.ch, C.desc, C.fresh, C.fresh_supp, C.beta⟩

theorem zOfRelay_carried {m : ℕ} (C : ChainRow.RelayChain ℚ DF.lq m) :
    ∀ k, (zOfRelay C).carried k = C.carried k
  | 0 => rfl
  | k + 1 => by
    funext p
    show C.beta (k + 1) * (zOfRelay C).carried k p + C.fresh (k + 1) p = _
    rw [zOfRelay_carried C k]; rfl

theorem zOfRelay_zc {m : ℕ} (C : ChainRow.RelayChain ℚ DF.lq m) (n : ℕ) : (zOfRelay C).zc n = 0 := by
  classical
  unfold ZPre.zc ChainRow.ZData.zc
  refine Finset.sum_eq_zero fun i _ => ?_
  rw [if_neg]
  exact fun h => C.beta_ne i h.2

noncomputable def ofChainTie (τ : ChainTie G T)
    (hcov : ∀ k, ¬ G.N.src k ≤ G.N.dst k → ∃ x, τ.e x = k) : DescentLayout G T Empty where
  xin := τ.xin
  yout := τ.yout
  len := τ.L.len
  zch := fun c => zOfRelay (τ.L.chain c)
  zl := fun u => u.elim
  zg := fun u => u.elim
  e := Sum.elim τ.e (fun x => x.1.elim)
  inj := by
    rintro (x | x) (y | y) h
    · exact congrArg Sum.inl (τ.inj h)
    · exact y.1.elim
    · exact x.1.elim
    · exact x.1.elim
  zsrc := fun x => τ.hsrc x
  zdst := fun x => τ.hdst x
  zcar := fun x p => by rw [zOfRelay_carried]; exact τ.hcar x p
  gsrc := fun x => x.1.elim
  gdst := fun x => x.1.elim
  gcar := fun x => x.1.elim
  reasc := fun u => u.elim
  gath_ge := fun u => u.elim
  silent := fun k hk => Or.inl (by obtain ⟨x, hx⟩ := hcov k hk; exact ⟨Sum.inl x, hx⟩)

theorem ofChainTie_pieces (τ : ChainTie G T) (hcov) : (ofChainTie τ hcov).pieces = Fintype.card T := by
  simp [DescentLayout.pieces, ofChainTie, zOfRelay_zc]

end BankBig

namespace Bridge7761
open BankBig BankTie BankPrem BankCallerGen

/-- **NON-VACUITY**: #7761 instantiates the big banner through the pure-chain case (only Valid remains). -/
theorem kappa7761_lt_big (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (hV : Valid (caller7761 hO7761) (1 - κ) (fun i k => specInvoice ((caller7761 hO7761).G i) (1 - κ) k)) :
    κ < 952721 / 100000000 :=
  bank_kappa_lt_big_gen 2048 (by norm_num) (caller7761 hO7761) (by exact hTP7761) (fun _ => HS7761 hO7761)
    (T := fun _ => Fin 8) (U := fun _ => Empty) (fun _ => ofChainTie τ7761 hcov7761G)
    (fun _ => (ofChainTie_pieces τ7761 hcov7761G).trans_le (by simp)) (fun _ => cc) hC7761
    (fun _ p => hin7761 p) (fun _ s y hy => hout7761 s y hy)
    (fun _ => fun e : Empty => e.elim) (fun _ => fun e : Empty => e.elim)
    (fun _ => gflow7761) (fun _ => le_of_eq gW7761.symm) κ hκ0 hκ1 hV

end Bridge7761
#print axioms BankBig.bank_kappa_lt_big_gen
#print axioms BankBig.bank_kappa_lt_big
#print axioms BankBig.ofChainTie_pieces
#print axioms Bridge7761.kappa7761_lt_big
