theorem certs_sound : ∀ c ∈ certs, HFrame (lamSet (lamMask (cu1 c) (cu2 c))) :=
  fun c hc => cert_sound c (List.all_eq_true.1 certs_ok c hc)


/-- AllOrNothing instantiated with the CERTIFIED frame fact (H_frame no longer a hypothesis). -/
theorem all_or_nothing_real (c : List Nat) (hc : c ∈ certs) (A B : Finset (Fin 104))
    (H_FS4 : ind (A ∩ B) ∈ Fperp) (H_supp : A ⊆ lamSet (lamMask (cu1 c) (cu2 c))) :
    A ∩ B = ∅ ∨ (A = lamSet (lamMask (cu1 c) (cu2 c)) ∧ lamSet (lamMask (cu1 c) (cu2 c)) ⊆ B) :=
  all_or_nothing Fperp _ A B (certs_sound c hc) H_FS4 H_supp

/-! ## non-vacuity -/
/-- parity form of "1_Lam ∈ F^perp" for every certified Lam: each frame meets Lam in an even number of
ports (so {0, 1_Lam} is the exact intersection, not just {0}).  Stated on masks (popcount parity). -/
def par128 (m : Nat) : Nat :=
  let v := m ^^^ (m >>> 64)
  let v := v ^^^ (v >>> 32)
  let v := v ^^^ (v >>> 16)
  let v := v ^^^ (v >>> 8)
  let v := v ^^^ (v >>> 4)
  let v := v ^^^ (v >>> 2)
  (v ^^^ (v >>> 1)) &&& 1

def evenMeet (lam : Nat) : Bool :=
  (List.range 759).all (fun i => par128 (frameAt i &&& lam) == 0)

theorem frames_meet_even_lam0 : evenMeet (lamMask (cu1 (certs.getD 0 [])) (cu2 (certs.getD 0 []))) = true := by
  decide +kernel

/-- negative control: a tampered certificate is rejected by the checker -/
theorem tampered_rejected :
    certOK ((certs.getD 0 []).set 3 ((certs.getD 0 []).getD 3 0 + 1)) = false := by decide +kernel
theorem untampered_ok : certOK (certs.getD 0 []) = true := by decide +kernel

#print axioms certs_sound
#print axioms all_or_nothing_real

end FrameCert
