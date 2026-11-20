import Nov15.BlockLaw2Par
import Nov15.BlockLaw2Ev0
import Nov15.BlockLaw2Ev1
import Nov15.BlockLaw2Ev2
import Nov15.BlockLaw2Ev3
import Nov15.BlockLaw2Ev4
import Nov15.BlockLaw2Ev5
import Nov15.BlockLaw2Key
import Nov15.BlockLaw2Pl0
import Nov15.BlockLaw2Pl1
import Nov15.BlockLaw2Pl2
import Nov15.BlockLaw2Pl3
import Nov15.BlockLaw2Pl4
import Nov15.BlockLaw2Pl5
import Nov15.BlockLaw2D8
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.FieldTheory.Finiteness
namespace BlockLaw2
open FrameCert BlockComplete BlockLaw BlockLaw2Par BlockLaw2Key BlockLaw2D8

/-! ## 1. 1_Lam ∈ Fperp for every certified section -/
theorem certs_even_chk : certs.all evenChk = true :=
  all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (all_app4 (BlockLaw2Ev0.ev0) BlockLaw2Ev0.ev1) BlockLaw2Ev0.ev2) BlockLaw2Ev0.ev3) BlockLaw2Ev0.ev4) BlockLaw2Ev0.ev5) BlockLaw2Ev0.ev6) BlockLaw2Ev0.ev7) BlockLaw2Ev1.ev8) BlockLaw2Ev1.ev9) BlockLaw2Ev1.ev10) BlockLaw2Ev1.ev11) BlockLaw2Ev1.ev12) BlockLaw2Ev1.ev13) BlockLaw2Ev1.ev14) BlockLaw2Ev1.ev15) BlockLaw2Ev2.ev16) BlockLaw2Ev2.ev17) BlockLaw2Ev2.ev18) BlockLaw2Ev2.ev19) BlockLaw2Ev2.ev20) BlockLaw2Ev2.ev21) BlockLaw2Ev2.ev22) BlockLaw2Ev2.ev23) BlockLaw2Ev3.ev24) BlockLaw2Ev3.ev25) BlockLaw2Ev3.ev26) BlockLaw2Ev3.ev27) BlockLaw2Ev3.ev28) BlockLaw2Ev3.ev29) BlockLaw2Ev3.ev30) BlockLaw2Ev3.ev31) BlockLaw2Ev4.ev32) BlockLaw2Ev4.ev33) BlockLaw2Ev4.ev34) BlockLaw2Ev4.ev35) BlockLaw2Ev4.ev36) BlockLaw2Ev4.ev37) BlockLaw2Ev4.ev38) BlockLaw2Ev4.ev39) BlockLaw2Ev5.ev40) BlockLaw2Ev5.ev41) BlockLaw2Ev5.ev42) BlockLaw2Ev5.ev43) BlockLaw2Ev5.ev44) BlockLaw2Ev5.ev45) BlockLaw2Ev5.ev46) BlockLaw2Ev5.ev47

theorem certs_even_ind : ∀ c ∈ certs, ind (lamSet (lamMask (cu1 c) (cu2 c))) ∈ Fperp := by
  intro c hc
  have := List.all_eq_true.1 certs_even_chk c hc
  unfold evenChk at this
  rw [lamMask'_eq] at this
  exact evenMeet_sound _ this

/-- F^perp ∩ F2^Lam = {0, 1_Lam} EXACTLY (1_Lam itself lies in F^perp), for all 1152 certified Lams -/
theorem Fperp_cap_exact (c : List Nat) (hc : c ∈ certs) :
    ind (lamSet (lamMask (cu1 c) (cu2 c))) ∈ Fperp ∧
    ∀ x ∈ Fperp, (∀ p, x p ≠ 0 → p ∈ lamSet (lamMask (cu1 c) (cu2 c))) →
      x = 0 ∨ x = ind (lamSet (lamMask (cu1 c) (cu2 c))) :=
  ⟨certs_even_ind c hc, certs_sound c hc⟩

/-- for ANY blocking 7-dim section given by normals: 1_Lam ∈ F^perp -/
theorem blocking_one_Lam (u1 u2 : Nat) (h1 : 0 < u1) (h2 : 0 < u2) (hne : u1 ≠ u2)
    (h1' : u1 < 512) (h2' : u2 < 512)
    (hb : ∀ i, i < 759 → frameAt i &&& lamMask u1 u2 ≠ 0) :
    ind (lamSet (lamMask u1 u2)) ∈ Fperp := by
  obtain ⟨c, hc, hl⟩ := block_complete u1 u2 h1 h2 hne h1' h2' hb
  rw [← hl]; exact certs_even_ind c hc

/-- semantic form: M = common kernel of two distinct nonzero normals, frame-blocking: 1_{Lam M} ∈ F^perp -/
theorem sem_one_Lam (M : Submodule (ZMod 2) V) (u1 u2 : Nat) (h1 : 0 < u1) (h2 : 0 < u2)
    (hne : u1 ≠ u2) (h1' : u1 < 512) (h2' : u2 < 512)
    (hM : ∀ v, v ∈ M ↔ dotN u1 v = 0 ∧ dotN u2 v = 0) (hb : SemBlocking M) :
    ind (Lam M) ∈ Fperp := by
  rw [← lamSet_eq_Lam M u1 u2 hM]
  exact blocking_one_Lam u1 u2 h1 h2 hne h1' h2' ((sem_blocking_iff M u1 u2 hM).1 hb)

/-! ## non-vacuity, branch 2 (A ∩ B ≠ ∅) at a real certified section -/
theorem c0_mem : certs.getD 0 [] ∈ certs := certs0_mem

theorem Lam_c0_nonempty : (Lam (KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])))).Nonempty := by
  refine ⟨⟨cp0 (certs.getD 0 []), by decide +kernel⟩, ?_⟩
  classical
  simp only [Lam, Finset.mem_filter, Finset.mem_univ, true_and]
  rw [mem_KerN]
  have := (lam_bit (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))
    ⟨cp0 (certs.getD 0 []), by decide +kernel⟩).1 (by decide +kernel)
  exact this

/-- REAL INSTANCE of branch 2: M = ker(129,257) (certified 7-dim blocking), A = B = Lam M (30 ports):
all hypotheses hold (blocking by certificate, ind(A∩B) ∈ F^perp by the parity lift, A ⊆ Lam), A ∩ B ≠ ∅,
so the law forces branch 2 (branch 1 is refuted). -/
theorem branch2_instance :
    let M := KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))
    Lam M ∩ Lam M ≠ ∅ ∧ ¬ (Lam M ∩ Lam M = ∅) ∧ (Lam M = Lam M ∧ Lam M ⊆ Lam M) := by
  intro M
  have hne : Lam M ∩ Lam M ≠ ∅ := by
    rw [Finset.inter_self]; exact Finset.nonempty_iff_ne_empty.1 Lam_c0_nonempty
  refine ⟨hne, hne, ⟨rfl, Finset.Subset.refl _⟩⟩

theorem branch2_forced :
    let M := KerN (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))
    (Lam M ∩ Lam M = ∅ ∨ (Lam M = Lam M ∧ Lam M ⊆ Lam M)) ∧ Lam M ∩ Lam M ≠ ∅ := by
  intro M
  refine ⟨?_, ?_⟩
  · refine all_or_nothing_sub M (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])) (by decide +kernel)
      (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (mem_KerN _ _)
      nv_semblocking (Lam M) (Lam M) ?_ (fun t ht => by
        classical
        simpa [Lam] using ht)
    rw [Finset.inter_self]
    exact sem_one_Lam M (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])) (by decide +kernel)
      (by decide +kernel) (by decide +kernel) (by decide +kernel) (by decide +kernel) (mem_KerN _ _)
      nv_semblocking
  · rw [Finset.inter_self]; exact Finset.nonempty_iff_ne_empty.1 Lam_c0_nonempty


theorem certs_plane : certs.all planeChk = true :=
  all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (all_appP (BlockLaw2Pl0.pl0) BlockLaw2Pl0.pl1) BlockLaw2Pl0.pl2) BlockLaw2Pl0.pl3) BlockLaw2Pl0.pl4) BlockLaw2Pl0.pl5) BlockLaw2Pl0.pl6) BlockLaw2Pl0.pl7) BlockLaw2Pl1.pl8) BlockLaw2Pl1.pl9) BlockLaw2Pl1.pl10) BlockLaw2Pl1.pl11) BlockLaw2Pl1.pl12) BlockLaw2Pl1.pl13) BlockLaw2Pl1.pl14) BlockLaw2Pl1.pl15) BlockLaw2Pl2.pl16) BlockLaw2Pl2.pl17) BlockLaw2Pl2.pl18) BlockLaw2Pl2.pl19) BlockLaw2Pl2.pl20) BlockLaw2Pl2.pl21) BlockLaw2Pl2.pl22) BlockLaw2Pl2.pl23) BlockLaw2Pl3.pl24) BlockLaw2Pl3.pl25) BlockLaw2Pl3.pl26) BlockLaw2Pl3.pl27) BlockLaw2Pl3.pl28) BlockLaw2Pl3.pl29) BlockLaw2Pl3.pl30) BlockLaw2Pl3.pl31) BlockLaw2Pl4.pl32) BlockLaw2Pl4.pl33) BlockLaw2Pl4.pl34) BlockLaw2Pl4.pl35) BlockLaw2Pl4.pl36) BlockLaw2Pl4.pl37) BlockLaw2Pl4.pl38) BlockLaw2Pl4.pl39) BlockLaw2Pl5.pl40) BlockLaw2Pl5.pl41) BlockLaw2Pl5.pl42) BlockLaw2Pl5.pl43) BlockLaw2Pl5.pl44) BlockLaw2Pl5.pl45) BlockLaw2Pl5.pl46) BlockLaw2Pl5.pl47

/-! ## 2. no blocking subspace of dimension <= 6 (and hence monotonicity gives nothing more to list) -/
def Vz (M : Submodule (ZMod 2) V) (u : Nat) : Prop := ∀ v ∈ M, dotN u v = 0

lemma dotN_xor (u w : Nat) (v : V) : dotN (u ^^^ w) v = dotN u v + dotN w v := by
  unfold dotN
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl (fun j _ => ?_)
  rw [Nat.testBit_xor]
  by_cases h1 : u.testBit j.val = true <;> by_cases h2 : w.testBit j.val = true <;>
    simp [h1, h2, zmod2_cancel]

lemma Vz_xor {M : Submodule (ZMod 2) V} {u w : Nat} (hu : Vz M u) (hw : Vz M w) : Vz M (u ^^^ w) := by
  intro v hv; rw [dotN_xor, hu v hv, hw v hv]; simp

lemma Vz_cancel {M : Submodule (ZMod 2) V} {p q : Nat} (hp : Vz M p) (hpq : Vz M (p ^^^ q)) : Vz M q := by
  have := Vz_xor hp hpq
  rwa [xor_cc] at this

lemma semBlocking_mono {M M' : Submodule (ZMod 2) V} (h : M ≤ M') (hb : SemBlocking M) :
    SemBlocking M' := by
  intro i hi
  obtain ⟨t, ht1, ht2⟩ := hb i hi
  exact ⟨t, ht1, h ht2⟩

lemma pair_blocking (M : Submodule (ZMod 2) V) (hb : SemBlocking M) (x y : Nat)
    (hx : Vz M x) (hy : Vz M y) : ∀ i, i < 759 → frameAt i &&& lamMask x y ≠ 0 :=
  (sem_blocking_iff (KerN x y) x y (mem_KerN x y)).1
    (semBlocking_mono (fun v hv => (mem_KerN x y v).2 ⟨hx v hv, hy v hv⟩) hb)

lemma lineBad_false (M : Submodule (ZMod 2) V) (hb : SemBlocking M) (x y : Nat)
    (hx : Vz M x) (hy : Vz M y) : lineBad x y = false := by
  by_contra hbad
  have h : lineBad x y = true := by simpa using hbad
  unfold lineBad at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true'] at h
  obtain ⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩ := h
  have := blocking_key x y h1 h2 h3 h4 h5 (pair_blocking M hb x y hx hy)
  rw [this] at h6
  exact absurd h6 (by simp)

/-- the six ordered readings of a certified pair (blocking_key, with the certificate kept) -/
theorem blocking_cert (x y : Nat) (h1 : 0 < x) (h2 : 0 < y) (hne : x ≠ y) (h1' : x < 512) (h2' : y < 512)
    (hb : ∀ i, i < 759 → frameAt i &&& lamMask x y ≠ 0) :
    ∃ c ∈ certs, (x = cu1 c ∧ y = cu2 c) ∨ (x = cu1 c ∧ y = cu1 c ^^^ cu2 c) ∨ (x = cu2 c ∧ y = cu1 c) ∨
      (x = cu1 c ^^^ cu2 c ∧ y = cu1 c) ∨ (x = cu2 c ∧ y = cu1 c ^^^ cu2 c) ∨
      (x = cu1 c ^^^ cu2 c ∧ y = cu2 c) := by
  obtain ⟨a, b, ha0, hab, hbc, hb512, hL, hxy⟩ := canon_exists2 x y h1 h2 hne h1' h2'
  have hcan : canonP a b = true := by simp [canonP, ha0, hab, hbc]
  have hrow := table_ok a (by omega)
  unfold rowOK at hrow
  have h3 := List.all_eq_true.1 hrow b (List.mem_range.2 hb512)
  rw [hcan] at h3
  simp only [Bool.not_true, Bool.false_or] at h3
  obtain ⟨w, hw⟩ : ∃ w, w = (tabW a >>> (12 * b)) % 4096 := ⟨_, rfl⟩
  rw [← hw] at h3
  unfold entryOK3 at h3
  by_cases hw759 : w < 759
  · exfalso
    rw [if_pos hw759, beq_iff_eq, lamMask'_eq, hL] at h3
    exact hb _ hw759 h3
  · rw [if_neg hw759] at h3
    obtain ⟨c, hc, hc1, hc2⟩ := listed_mem a b (by omega) hb512 h3
    exact ⟨c, hc, by rw [hc1, hc2]; exact hxy⟩

/-- an annihilator code outside any small finite set exists when dim M <= 6 -/
lemma exists_outside (M : Submodule (ZMod 2) V) (h6 : Module.finrank (ZMod 2) M ≤ 6)
    (S : Finset Nat) (hS : S.card < 8) : ∃ u, u < 512 ∧ Vz M u ∧ u ∉ S := by
  classical
  by_contra hcon
  push Not at hcon
  have hsum := Subspace.finrank_add_finrank_dualAnnihilator_eq (K := ZMod 2) (V := V) M
  have hV : Module.finrank (ZMod 2) V = 9 := by simp
  have h3 : 3 ≤ Module.finrank (ZMod 2) M.dualAnnihilator := by omega
  haveI : Module.Finite (ZMod 2) M.dualAnnihilator := inferInstance
  haveI : Finite M.dualAnnihilator := Module.finite_of_finite (ZMod 2)
  haveI : Fintype M.dualAnnihilator := Fintype.ofFinite _
  have hcard : Fintype.card M.dualAnnihilator = 2 ^ Module.finrank (ZMod 2) M.dualAnnihilator := by
    rw [Fintype.card_eq_nat_card, Module.natCard_eq_pow_finrank (K := ZMod 2) (V := M.dualAnnihilator)]
    simp
  have h8 : 8 ≤ Fintype.card M.dualAnnihilator := by
    rw [hcard]
    calc 8 = 2 ^ 3 := by norm_num
      _ ≤ 2 ^ Module.finrank (ZMod 2) M.dualAnnihilator := Nat.pow_le_pow_right (by norm_num) h3
  let ψ : M.dualAnnihilator → Nat := fun φ => Classical.choose (exists_code φ.1)
  have hψ : ∀ φ : M.dualAnnihilator, ψ φ < 512 ∧ ∀ v, φ.1 v = dotN (ψ φ) v :=
    fun φ => Classical.choose_spec (exists_code φ.1)
  have hle : (Finset.univ : Finset M.dualAnnihilator).card ≤ S.card := by
    apply Finset.card_le_card_of_injOn ψ
    · intro φ _
      apply hcon _ (hψ φ).1
      intro v hv
      rw [← (hψ φ).2 v]
      exact (Submodule.mem_dualAnnihilator _).1 φ.2 v hv
    · intro φ _ φ' _ h
      apply Subtype.ext
      apply LinearMap.ext
      intro v
      rw [(hψ φ).2 v, (hψ φ').2 v]
      have : ψ φ = ψ φ' := h
      rw [this]
  rw [Finset.card_univ] at hle
  omega

/-- NO frame-blocking subspace has dimension <= 6. -/
theorem no_blocking_le6 (M : Submodule (ZMod 2) V) (h6 : Module.finrank (ZMod 2) M ≤ 6)
    (hb : SemBlocking M) : False := by
  obtain ⟨x, hx512, hxV, hx⟩ := exists_outside M h6 {0} (by simp)
  obtain ⟨y, hy512, hyV, hy⟩ := exists_outside M h6 {0, x} (Finset.card_le_two.trans_lt (by norm_num))
  have hx0 : 0 < x := by
    have : x ≠ 0 := by simpa using hx
    omega
  have hy0 : 0 < y := by
    have : y ≠ 0 := fun h => hy (by simp [h])
    omega
  have hxy : x ≠ y := fun h => hy (by simp [h])
  obtain ⟨c, hc, hcase⟩ := blocking_cert x y hx0 hy0 hxy hx512 hy512 (pair_blocking M hb x y hxV hyV)
  have hxy' : Vz M (x ^^^ y) := Vz_xor hxV hyV
  -- a = cu1 c, b = cu2 c both annihilate M
  have hab : Vz M (cu1 c) ∧ Vz M (cu2 c) := by
    rcases hcase with ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩ | ⟨h1, h2⟩
    · rw [h1] at hxV; rw [h2] at hyV; exact ⟨hxV, hyV⟩
    · rw [h1] at hxV; rw [h2] at hyV; exact ⟨hxV, Vz_cancel hxV hyV⟩
    · rw [h1] at hxV; rw [h2] at hyV; exact ⟨hyV, hxV⟩
    · rw [h1] at hxV; rw [h2] at hyV; exact ⟨hyV, Vz_cancel hyV hxV⟩
    · rw [h1] at hxV; rw [h2] at hyV
      have : Vz M (cu2 c ^^^ cu1 c) := by rw [Nat.xor_comm]; exact hyV
      exact ⟨Vz_cancel hxV this, hxV⟩
    · rw [h1] at hxV; rw [h2] at hyV
      have : Vz M (cu2 c ^^^ cu1 c) := by rw [Nat.xor_comm]; exact hxV
      exact ⟨Vz_cancel hyV this, hyV⟩
  obtain ⟨ha, hb2⟩ := hab
  have hS4 : ({0, cu1 c, cu2 c, cu1 c ^^^ cu2 c} : Finset Nat).card < 8 :=
    Finset.card_le_four.trans_lt (by norm_num)
  obtain ⟨u, hu512, huV, hu⟩ := exists_outside M h6 _ hS4
  have hu' : ¬ (u = 0 ∨ u = cu1 c ∨ u = cu2 c ∨ u = cu1 c ^^^ cu2 c) := by simpa using hu
  have hplane := List.all_eq_true.1 (List.all_eq_true.1 certs_plane c hc) u (List.mem_range.2 hu512)
  have e1 := lineBad_false M hb (cu1 c) u ha huV
  have e2 := lineBad_false M hb (cu2 c) u hb2 huV
  have e3 := lineBad_false M hb (cu1 c ^^^ cu2 c) u (Vz_xor ha hb2) huV
  have e4 := lineBad_false M hb (cu1 c) (cu2 c ^^^ u) ha (Vz_xor hb2 huV)
  have e5 := lineBad_false M hb (cu2 c) (cu1 c ^^^ u) hb2 (Vz_xor ha huV)
  have e6 := lineBad_false M hb (cu1 c ^^^ cu2 c) (cu1 c ^^^ u) (Vz_xor ha hb2) (Vz_xor ha huV)
  unfold planeOK at hplane
  rw [e1, e2, e3, e4, e5, e6] at hplane
  simp only [Bool.or_false, Bool.or_eq_true, beq_iff_eq] at hplane
  tauto

/-- every blocking subspace has dimension >= 7 -/
theorem blocking_dim_ge7 (M : Submodule (ZMod 2) V) (hb : SemBlocking M) :
    7 ≤ Module.finrank (ZMod 2) M := by
  by_contra h
  exact no_blocking_le6 M (by omega) hb


/-! ## 3. real instance of the 8-row ALL-OR-NOTHING law (branch 2, A ∩ B ≠ ∅) and sharpness of dim >= 7 -/
theorem c0_normals : cu1 (certs.getD 0 []) = 129 ∧ cu2 (certs.getD 0 []) = 257 := by decide +kernel

noncomputable abbrev M0 : Submodule (ZMod 2) V := KerN 129 257

theorem M0_blocking : SemBlocking M0 := by
  have := nv_semblocking
  rw [c0_normals.1, c0_normals.2] at this
  exact this

theorem M0_count : (Finset.univ.filter (fun v : V => dotN 129 v = 0 ∧ dotN 257 v = 0)).card = 128 := by
  decide +kernel

theorem finrank_M0 : Module.finrank (ZMod 2) M0 = 7 := by
  classical
  have hcard : Nat.card M0 = 128 := by
    rw [Nat.card_eq_fintype_card, Fintype.card_subtype]
    rw [← M0_count]
    congr 1
    ext v
    simp [M0, mem_KerN]
  have hp := Module.natCard_eq_pow_finrank (K := ZMod 2) (V := M0)
  rw [hcard, Nat.card_zmod] at hp
  have : (2 : Nat) ^ Module.finrank (ZMod 2) M0 = 2 ^ 7 := by rw [← hp]; norm_num
  exact Nat.pow_right_injective (le_refl 2) this

/-- SHARPNESS: a 7-dimensional frame-blocking subspace exists, so `blocking_dim_ge7` is tight -/
theorem blocking_dim7_exists : ∃ M : Submodule (ZMod 2) V, SemBlocking M ∧ Module.finrank (ZMod 2) M = 7 :=
  ⟨M0, M0_blocking, finrank_M0⟩

def pt7 : Fin 7 → Fin 104 := ![19, 20, 21, 22, 23, 25, 34]

theorem pt7_inj_lin : LinearIndependent (ZMod 2) (fun i => lab (pt7 i)) := by
  rw [Fintype.linearIndependent_iff]
  decide +kernel

theorem pt7_in_M0 : ∀ i, lab (pt7 i) ∈ M0 := by
  intro i
  rw [mem_KerN]
  revert i
  decide +kernel

theorem span_Lam_eq : Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104))) = M0 := by
  classical
  apply le_antisymm
  · apply Submodule.span_le.2
    rintro _ ⟨t, ht, rfl⟩
    simpa [Lam] using ht
  · have h1 : Submodule.span (ZMod 2) (Set.range (fun i => lab (pt7 i))) ≤ M0 :=
      Submodule.span_le.2 (by rintro _ ⟨i, rfl⟩; exact pt7_in_M0 i)
    have h2 : Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (Set.range (fun i => lab (pt7 i)))) =
        Module.finrank (ZMod 2) M0 := by
      rw [finrank_span_eq_card pt7_inj_lin, finrank_M0]; simp
    have h3 := Submodule.eq_of_le_of_finrank_eq h1 h2
    refine h3.ge.trans ?_
    apply Submodule.span_mono
    rintro _ ⟨i, rfl⟩
    refine ⟨pt7 i, ?_, rfl⟩
    simpa [Lam] using pt7_in_M0 i

/-- REAL INSTANCE of the headline all_or_nothing_8row with A ∩ B ≠ ∅: D = S = A = B = Lam M0 (30 ports),
M0 = ker(129,257) = span of the labels of D, 7-dimensional and frame-blocking; ind(A∩B) ∈ F^perp is
PROVED (parity lift).  Branch 1 is refuted, so branch 2 is the output. -/
theorem all_or_nothing_8row_branch2 :
    (Lam M0 ∩ Lam M0).Nonempty ∧
    (Lam M0 = Lam (Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104)))) ∧
      Lam (Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104)))) ⊆ Lam M0 ∧
      Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104))) ≤
        Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104)))) := by
  classical
  have hne : (Lam M0 ∩ Lam M0).Nonempty := by
    rw [Finset.inter_self]
    have := Lam_c0_nonempty
    rw [c0_normals.1, c0_normals.2] at this
    exact this
  refine ⟨hne, ?_⟩
  have hFS4 : ind (Lam M0 ∩ Lam M0) ∈ Fperp := by
    rw [Finset.inter_self]
    exact sem_one_Lam M0 129 257 (by norm_num) (by norm_num) (by norm_num) (by norm_num) (by norm_num)
      (mem_KerN 129 257) M0_blocking
  have h7 : Module.finrank (ZMod 2) (Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104)))) = 7 := by
    rw [span_Lam_eq]; exact finrank_M0
  have hbl : SemBlocking (Submodule.span (ZMod 2) (lab '' ((Lam M0 : Finset (Fin 104)) : Set (Fin 104)))) := by
    rw [span_Lam_eq]; exact M0_blocking
  have key := all_or_nothing_8row (Lam M0) (Lam M0) (Lam M0) (Lam M0) h7 hbl (Finset.Subset.refl _)
    (Finset.Subset.refl _) hFS4
  rcases key with h | h
  · exfalso
    exact (Finset.nonempty_iff_ne_empty.1 hne) h
  · exact h

/-! ## tamper / negative controls -/
theorem tamper_even_rejected : evenMeet 1 = false := by decide +kernel
theorem untampered_even : evenMeet (lamMask' (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))) = true := by
  decide +kernel
theorem lineBad_listed_false : lineBad (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 [])) = false := by
  decide +kernel
theorem lineBad_unlisted_true : lineBad 1 2 = true := by decide +kernel
theorem nv8_listed : 3 ∈ L8 := by decide +kernel
theorem nv8_unlisted : 1 ∉ L8 := by decide +kernel
theorem nv8_tamper : (frameAt 0 &&& lamMask' 3 3 == 0) = false := by decide +kernel
theorem nv8_nonblocking : ∃ i, i < 759 ∧ frameAt i &&& lamMask 1 1 = 0 := by
  refine ⟨(tab8 >>> (12 * 1)) % 4096, by decide +kernel, ?_⟩
  rw [← lamMask'_eq]; decide +kernel
/-- semantic 8-dim completeness: the hyperplane ker(a) is frame-blocking iff a is one of the 136 listed -/
theorem sem_blocking8_iff (a : Nat) (h0 : 0 < a) (h : a < 512) : SemBlocking (KerN a a) ↔ a ∈ L8 :=
  (sem_blocking_iff (KerN a a) a a (mem_KerN a a)).trans (blocking8_iff a h0 h)
theorem nv8_sem : SemBlocking (KerN 3 3) := (sem_blocking8_iff 3 (by norm_num) (by norm_num)).2 nv8_listed
theorem nv8_sem_not : ¬ SemBlocking (KerN 1 1) := fun hb => nv8_unlisted
  ((sem_blocking8_iff 1 (by norm_num) (by norm_num)).1 hb)

#print axioms all_or_nothing_8row_branch2
#print axioms blocking_dim7_exists
#print axioms sem_blocking8_iff

#print axioms certs_even_ind
#print axioms Fperp_cap_exact
#print axioms blocking_one_Lam
#print axioms sem_one_Lam
#print axioms branch2_forced
#print axioms no_blocking_le6
#print axioms blocking_dim_ge7
#print axioms BlockLaw2D8.blocking8_iff
end BlockLaw2
