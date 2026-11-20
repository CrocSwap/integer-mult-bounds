theorem rows_seeded (r : @RT) (hp : pub @CALLER r = true) (hs : Nat.testBit SMASK (idxOf r) = true) :
    (exec @TR).row r = tgt @CALLER r := by
  funext k
  obtain ⟨hro, hoN⟩ := reg_idx r
  obtain ⟨hrk, hkN⟩ := reg_idx k
  have hex : exec @TR = run init ((decodeAll ALL).map @MODEL.toEv) := by unfold exec @TR; rw [evs_eq]
  have hL : LegalFrom @MODEL.pb init ((decodeAll ALL).map @MODEL.toEv) := by
    have := @SOUND.1; unfold Legal @TR at this; rw [evs_eq] at this; exact this
  have hR : PRel @MODEL (run init ((decodeAll ALL).map @MODEL.toEv)) s@K := by
    intro j hj
    have := @SOUND.2.1 j hj
    rw [hex] at this
    show _ = @MODEL.locOf (gt 11 t@K j)
    rw [Tr.beq_eq _ _ tT]; exact this
  have hN2 : @MODEL.N ≤ 2 ^ 11 := @MOK.hN
  have hZ : PZ PK s@K := fun j hj hb => by
    have hb' : Nat.testBit z@K j = false := hb
    have := tZ j hj; rw [hb', Bool.false_or, beq_iff] at this; exact this
  have hB : PB PK s@K := fun j hj => by
    have := tG j hj; simp only [tGP, Bool.and_eq_true] at this
    exact ⟨this.1.1.1.1, this.1.1.1.2⟩
  have hoNO : idxOf r < PK.NO := by
    have := tG (idxOf r) (by omega)
    simp only [tGP, Bool.and_eq_true, hs, Bool.not_true, Bool.false_or, blt_iff] at this
    exact this.2.1
  have hg : ∀ j < @MODEL.N, (pz PK (pG PK s@K j) (idxOf r) : ℚ) = if j = idxOf r then (DSC : ℚ) else 0 := by
    intro j hj
    have t := tG j (by omega)
    simp only [tGP, Bool.and_eq_true, decide_eq_true_eq] at t
    obtain ⟨⟨⟨⟨tb, _⟩, tv⟩, _⟩, te⟩ := t
    show (pz PK (gtA PK.Z0 11 g@K j) (idxOf r) : ℚ) = _
    by_cases hb : Nat.testBit SMASK j = true
    · simp only [hb, ↓reduceIte, Bool.not_true, Bool.false_or, Bool.and_eq_true, blt_iff, ble_iff] at tv te
      rw [pz_pk PK_ok tb [(j, (DSC : Int))] (by simp [te.1]) (by simp [sabs, te.2]) tv (idxOf r) hoNO]
      by_cases h : j = idxOf r <;> simp [svz, h]
    · have hb' : Nat.testBit SMASK j = false := by simpa using hb
      simp only [hb', Bool.false_eq_true, ↓reduceIte] at tv
      have : j ≠ idxOf r := fun e => hb (e ▸ hs)
      rw [pz_pk PK_ok tb [] (by simp) (by simp [sabs]) tv (idxOf r) hoNO]; simp [svz, this]
  have ha : ∀ j < @MODEL.N, (pz PK (pA PK s@K j) (idxOf r) : ℚ) = 0 := by
    intro j hj
    have t := tG j (by omega)
    simp only [tGP, Bool.and_eq_true, beq_iff] at t
    show (pz PK (gtA PK.Z0 11 a@K j) (idxOf r) : ℚ) = 0
    rw [t.1.2, pz_Z0 PK_ok PK_Z0]; simp
  have key := prows_from_run @MOK PK_ok PK_Z0 (by decide) (decodeAll ALL) s@K s0 DSC hL hR hZ hB chainAll
    (idxOf r) hoN hg ha (idxOf k) hkN
  have hreg : ∀ j, @MODEL.reg j = regOf j := fun _ => rfl
  rw [hreg, hreg, hro, hrk, ← hex] at key
  have hb : (pz PK (pA PK s0 (idxOf k)) (idxOf r) : ℚ) = svv (colF (idxOf k)) (idxOf r) := by
    have t := tB (idxOf k) hkN
    simp only [tBP, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, blt_iff, ble_iff] at t
    obtain ⟨⟨⟨tb, tv⟩, tk⟩, ts⟩ := t
    show (pz PK (gtA PK.Z0 11 a0 (idxOf k)) (idxOf r) : ℚ) = _
    rw [svv_svz, pz_pk PK_ok tb _ tk ts tv (idxOf r) hoNO]
  rw [hb] at key
  unfold colF at key
  rw [hrk, svv_filter, if_pos hs, svv_colE @CALLER DSC HSC (by decide) idxOf
    (fun a b h => by rw [← (reg_idx a).1, ← (reg_idx b).1, h]) r k hp] at key
  have hD : (DSC : ℚ) ≠ 0 := by norm_num [DSC]
  exact mul_left_cancel₀ hD key
