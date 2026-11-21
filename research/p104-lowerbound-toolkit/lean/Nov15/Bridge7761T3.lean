/-
Bridge7761T3 (lane CHAINTIE, Nov 18).  #7761's `BankTie.ChainTie` instance on G7761 hO7761 (T = Fin 8 chains, 23 steps):
  chain7761 c / L7761 : the relay chains: chart of step j = chartOf (cid c j) (clamped past the end), beta = D5's, gath = 0
                        (BankMedA regathers), fresh_j := d_j(xin p) - β_j d_(j-1)(xin p) read from the packed digits (T1/T2 suppChk gives fresh_supp);
  τ7761               : e = bank position (injective: injChk), hsrc/hdst from chainFact, xin = xi, yout = yo,
                        hcar : carried = G.N.d (e x) (xin p) (relay recursion collapses by definition of fresh).
  hcov7761G           : every descent bank of G7761 is some τ7761.e x.   Kernel only.
-/
import Nov15.Bridge7761T2
import Nov15.Bridge7761P

namespace Bridge7761
open Finset Module BankNC0 BridgeP

theorem dig_dd7 (c j : ℕ) (hc : c < 8) (hj : j < clen c) (p : Fin 104) :
    dRec Recipe7761 ⟨cpos c j, (chainFact c j hc hj).1⟩ (xi p) = dqN c j p := by
  have hk := (chainFact c j hc hj).1
  have hg : (xi p).val < 256 := by rw [xi_val]; have := xf_lt p; omega
  have h := dig_extract ⟨cpos c j, hk⟩ (digOK c j hc hj) (xi p) hg
  have hd : (dk (cpos c j) : ℚ) ≠ 0 := by exact_mod_cast (dk_pos _ hk).ne'
  unfold dqN
  rw [eq_div_iff hd, mul_comm]
  have e : (xField.getD (p : ℕ) 0) = (xi p).val := by rw [xi_val]; rfl
  rw [e]
  exact h

noncomputable def dd7 (c : Fin 8) (j : ℕ) (p : Fin 104) : ℚ :=
  if h : j < clen c then dRec Recipe7761 ⟨cpos c j, (chainFact c j c.2 h).1⟩ (xi p) else 0

noncomputable def freshv (c : Fin 8) (j : ℕ) (p : Fin 104) : ℚ :=
  if j < clen c then (if j = 0 then dd7 c 0 p else dd7 c j p - cbeta c j * dd7 c (j - 1) p) else 0

theorem dd7_eq (c : Fin 8) (j : ℕ) (hj : j < clen c) (p : Fin 104) : dd7 c j p = dqN c j p := by
  unfold dd7; rw [dif_pos hj]; exact dig_dd7 c j c.2 hj p

theorem freshv_eq (c : Fin 8) (j : ℕ) (hj : j < clen c) (p : Fin 104) : freshv c j p = freshQN c j p := by
  unfold freshv freshQN
  rw [if_pos hj]
  by_cases h0 : j = 0
  · subst h0; simp only [if_true]; exact dd7_eq c 0 hj p
  · simp only [if_neg h0]
    rw [dd7_eq c j hj p, dd7_eq c (j - 1) (by omega) p]

theorem cid_succ_ge (c j : ℕ) (hj : clen c ≤ j) : cid c (j + 1) = cid c j := by
  unfold cid; rw [min_eq_right (by omega), min_eq_right (by omega)]

noncomputable def chain7761 (c : Fin 8) : ChainRow.RelayChain ℚ DF.lq (clen c) where
  ch j := chartOf (cid c j)
  desc j := by
    by_cases h : j < clen c
    · obtain ⟨hk, h1, h2, h3, -, -, -⟩ := chainFact c j c.2 h
      have := chart_desc (cpos c j) hk (by rw [h1, h2]; exact h3)
      rw [h1, h2] at this; exact this
    · rw [cid_succ_ge c j (by omega)]
  fresh := freshv c
  fresh_supp := fun j p hne => by
    by_cases h : j < clen c
    · rw [freshv_eq c j h p] at hne
      exact lq_mem_chart _ (chainFact c j c.2 h).2.2.2.2.1 p (supp c j p c.2 h p.2 hne)
    · exact absurd (by unfold freshv; rw [if_neg h]) hne
  gath := fun _ _ => 0
  gath_supp := fun _ _ h => absurd rfl h
  beta := cbeta c
  beta_ne := fun j => by
    by_cases h : j < clen c
    · exact (chainFact c j c.2 h).2.2.2.2.2.2
    · unfold cbeta; rw [if_neg h]; exact one_ne_zero

noncomputable def L7761 : ChainRow.ChainLayout ℚ DF.lq (Fin 8) where
  len c := clen c
  chain := chain7761

theorem carried_dd7 (c : Fin 8) (p : Fin 104) : ∀ j, j < clen c → (chain7761 c).carried j p = dd7 c j p := by
  intro j
  induction j with
  | zero =>
    intro h
    show freshv c 0 p = _
    unfold freshv; rw [if_pos h]; simp
  | succ j ih =>
    intro h
    have ih' := ih (by omega)
    show cbeta c (j + 1) * (chain7761 c).carried j p + freshv c (j + 1) p = _
    rw [ih']
    unfold freshv; rw [if_pos h, if_neg (by omega)]
    simp only [Nat.add_sub_cancel]; ring

noncomputable def τ7761 : BankTie.ChainTie (G7761 hO7761) (Fin 8) where
  L := L7761
  e := fun x => ⟨cpos x.1 x.2, (chainFact x.1 x.2 x.1.2 x.2.2).1⟩
  inj := by
    intro x y h
    have h' : cpos x.1 x.2 = cpos y.1 y.2 := by simpa using congrArg Fin.val h
    obtain ⟨h1, h2⟩ := cpos_inj x.1 x.2 y.1 y.2 x.1.2 x.2.2 y.1.2 y.2.2 h'
    obtain ⟨c, j⟩ := x; obtain ⟨c', j'⟩ := y
    have h1' : c = c' := Fin.ext h1
    subst h1'
    have : j = j' := Fin.ext h2
    subst this; rfl
  hsrc := fun x => by
    show chartOf (cid x.1 x.2) = chartOf (srcId (cpos x.1 x.2))
    rw [(chainFact x.1 x.2 x.1.2 x.2.2).2.1]
  hdst := fun x => by
    show chartOf (cid x.1 (x.2 + 1)) = chartOf (dstId (cpos x.1 x.2))
    rw [(chainFact x.1 x.2 x.1.2 x.2.2).2.2.1]
  xin := xi
  yout := yo
  hcar := fun x p => by
    show (chain7761 x.1).carried x.2 p = dRec Recipe7761 ⟨cpos x.1 x.2, _⟩ (xi p)
    rw [carried_dd7 x.1 p x.2 x.2.2]
    unfold dd7; exact dif_pos (show (x.2 : ℕ) < clen x.1 from x.2.2)

theorem mem_flatten_pos (k : ℕ) (h : k ∈ chPos.flatten) : ∃ c j, c < 8 ∧ j < clen c ∧ cpos c j = k := by
  rw [List.mem_flatten] at h
  obtain ⟨l, hl, hk⟩ := h
  obtain ⟨c, hc, rfl⟩ := List.mem_iff_getElem.1 hl
  obtain ⟨j, hj, hjk⟩ := List.mem_iff_getElem.1 hk
  have hc8 : c < 8 := by have := chain_count.1; omega
  refine ⟨c, j, hc8, ?_, ?_⟩
  · unfold clen; rw [List.getD_eq_getElem _ _ hc]; exact hj
  · unfold cpos; rw [List.getD_eq_getElem _ _ hc, List.getD_eq_getElem _ _ hj]; exact hjk

theorem hcov7761G (k : Fin 5746) (h : ¬ (G7761 hO7761).N.src k ≤ (G7761 hO7761).N.dst k) :
    ∃ x, τ7761.e x = k := by
  obtain ⟨c, j, hc, hj, hk⟩ := mem_flatten_pos k (hcov7761' k h)
  refine ⟨⟨⟨c, hc⟩, ⟨j, hj⟩⟩, ?_⟩
  apply Fin.ext
  exact hk

end Bridge7761
#print axioms Bridge7761.τ7761
#print axioms Bridge7761.hcov7761G
