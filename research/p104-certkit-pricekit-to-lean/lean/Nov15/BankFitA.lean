/-
BankFitA (lane LEAN-BANK, Nov 18).  Banked FLAG rung as ONE kernel theorem, any L-call caller block, applied to #7761.
STRUCTURE `BankedGraph` = the BANK1/BANK2 graph premises (cards/WILD/UCEIL/AUDIT-BANK.md names):
  N      : BankNC0.Net over charts Submodule F_2 (F_2^9)          -- P-LIN (scalar banks d k, outputs O), P-LOC + P-ACYC
                                                                     (read: a bank reads inputs born at / earlier deliveries
                                                                     into its source chart; out: outputs read their chart)
  minors : every principal minor of O nonzero                       -- P-WORD principal minors
  con    : BankWireD.Contract N                                      -- main contract + chart model of the 14+14 witness flag
                                                                     rows (OUT/IN of BankFlagB; in-degree, nonzero partner)
  nest   : every bank nested (src ≤ dst ∨ dst ≤ src)                 -- P-NEST
  climb  : every field nested A ≤ B, climbing cl f                   -- P-POS (helpers any climb)
  Mn     : 400 mains, climb 8                                        -- main contract mass
PROVED (kernel only):
  BankedGraph.price         : 400·8^s + 28(9^s-8^s) + helperCredit ≤ Σ paid   (flag-cut + cut lemma, BankHelpA)
  bank_kappa_lt_of_cert     : any L, caller block (T,P), any exact Cert of  cdat T - cdat P - L(400·8^s + 28 D9)
                              ⟹ κ < kbar under  P-1S' (hpaid) + P-CALLER' (hcaller: Σ paid - Σ helper credit ≤ invoice).
  bank_kappa_lt_flag        : #7761's own caller block (2048 calls, BankFitCertA) ⟹ κ < 997/50000 = .01994
                              (root .0199325064; grid-rounded up).
-/
import Nov15.BankHelpA
import Nov15.BankFitCertA

namespace BankFit
open Finset Module BankNC0 BankWireC BankWireD BankHelp SafeRungsPrice

variable {K : Type} {Fld Bank : Type} [Field K] [Fintype Fld] [DecidableEq Fld]
  [Fintype Bank] [LinearOrder Bank]

/-- the banked scalar graph premises (BANK1 + BANK2 + AUDIT-BANK), one call. -/
structure BankedGraph (K Fld Bank : Type) [Field K] [Fintype Fld] [DecidableEq Fld]
    [Fintype Bank] [LinearOrder Bank] where
  N : Net K (Submodule (ZMod 2) V) Fld Bank
  minors : ∀ C : Finset Fld, (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0
  con : Contract N
  nest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k
  cl : Fld → ℕ
  climb : ∀ f, N.A f ≤ N.B f ∧ finrank (ZMod 2) (N.B f) = finrank (ZMod 2) (N.A f) + cl f
  Mn : Finset Fld
  main8 : ∀ f ∈ Mn, cl f = 8
  card : Mn.card = 400

/-- bank price d^s of bank k. -/
noncomputable def bankPrice (G : BankedGraph K Fld Bank) (s : ℝ) (k : Bank) : ℝ :=
  ((dh (finrank (ZMod 2) (G.N.src k)) (finrank (ZMod 2) (G.N.dst k)) : ℕ) : ℝ) ^ s

theorem BankedGraph.price (G : BankedGraph K Fld Bank) {s : ℝ} (hs0 : 0 < s) (hs1 : s ≤ 1)
    (paid : Bank → ℝ) (hpaid : ∀ k, bankPrice G s k ≤ paid k) :
    400 * (8:ℝ) ^ s + 28 * ((9:ℝ) ^ s - (8:ℝ) ^ s) + helperCredit G.N s G.Mn ≤ ∑ k, paid k :=
  net_price28_help G.N hs0 hs1 G.minors G.con G.nest G.cl G.climb G.Mn G.main8 G.card paid hpaid

/-- the flag rung for ANY caller block (T, P) of L calls and any exact certificate of its ceiling function. -/
theorem bank_kappa_lt_of_cert (L : ℕ) (T P : List (ℕ × ℕ)) (kbar : ℝ)
    (hcert : Cert (fun s => cdat s T - cdat s P - L * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s))) kbar)
    (G : Fin L → BankedGraph K Fld Bank) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin L → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) T - cdat (1 - κ) P) :
    κ < kbar := by
  by_contra hge
  push_neg at hge
  have hc := hcert κ hge hκ1.le
  simp only at hc
  have each : ∀ i, 400 * (8:ℝ) ^ (1 - κ) + 28 * ((9:ℝ) ^ (1 - κ) - (8:ℝ) ^ (1 - κ))
      ≤ ∑ k, paid i k - helperCredit (G i).N (1 - κ) (G i).Mn := fun i => by
    have := (G i).price (s := 1 - κ) (by linarith) (by linarith) _ (hpaid i)
    linarith
  have := Finset.sum_le_sum (fun i (_ : i ∈ (Finset.univ : Finset (Fin L))) => each i)
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul,
    Finset.sum_sub_distrib] at this
  linarith

/-- **#7761** (frontier, κ .0038207): its own caller block (2048 calls), flag rung 14+14 ⟹ κ < .01994. -/
theorem bank_kappa_lt_flag (G : Fin 2048 → BankedGraph K Fld Bank) (κ : ℝ) (hκ0 : 0 < κ) (hκ1 : κ < 1)
    (paid : Fin 2048 → Bank → ℝ) (hpaid : ∀ i k, bankPrice (G i) (1 - κ) k ≤ paid i k)
    (hcaller : ∑ i, ∑ k, paid i k - ∑ i, helperCredit (G i).N (1 - κ) (G i).Mn ≤
      cdat (1 - κ) BankFitCertFit7761X28.TB - cdat (1 - κ) BankFitCertFit7761X28.PB) :
    κ < 997 / 50000 := by
  have hcert : Cert (fun s => cdat s BankFitCertFit7761X28.TB - cdat s BankFitCertFit7761X28.PB -
      ((2048 : ℕ) : ℝ) * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s))) (997 / 50000) := by
    have h := BankFitCertFit7761X28.cert
    intro t h1 h2
    have := h t (by norm_num at h1 ⊢; linarith) h2
    unfold BankFitCertFit7761X28.FceilBank at this
    push_cast
    linarith
  exact bank_kappa_lt_of_cert 2048 _ _ _ hcert G κ hκ0 hκ1 paid hpaid hcaller

end BankFit
#print axioms BankFit.bank_kappa_lt_of_cert
#print axioms BankFit.bank_kappa_lt_flag
