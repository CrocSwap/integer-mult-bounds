/-
BridgeRung (lane BRIDGE, Nov 20).  The rung chain's D premise IS the bridged network's D.
* `sum_fin_list`      : Σ_{k : Fin L.length} g L[k] = (L.map g).sum.
* `descMass_foldS`    : for every legal trace with subspace MOVE charts, the folded banked net's descent mass
                        Σ_banks max(ht src - ht dst, 0) equals ownDrop (exec tr) (public banks ascend: contribute 0).
* `descMass_fold7113` : BankBanner.descMass (foldBanked7113 ...) = ownDrop (exec tr)  (the rung premise hD's quantity).
* `NetD56`            : the network statement "every P104 NetW with b ≤ a has total drop ≥ 56" (NET-D56, open).
* `rung_hD_of_netD56` : NetD56 ⟹ 56 ≤ descMass (foldBanked7113 caller7113 ...) for EVERY legal #7113 word, i.e. the
                        rung's hD premise is exactly NET-D56 applied to the bridged network (BridgeNet.word_netW).
Kernel only.
-/
import Nov15.BridgeNetInst

set_option linter.unusedSectionVars false

namespace BridgeNet
open Finset Module WordModel Uni UniFold7113

theorem sum_fin_list {α : Type} (L : List α) (g : α → ℤ) :
    ∑ k : Fin L.length, g L[k] = (L.map g).sum := by
  rw [← List.sum_ofFn]
  congr 1
  apply List.ext_getElem <;> simp

theorem sum_filter_ite {α : Type} (L : List α) (p : α → Bool) (f : α → ℤ) :
    (L.map fun m => if p m then 0 else f m).sum = ((L.filter fun m => !p m).map f).sum := by
  induction L with
  | nil => simp
  | cons m L ih => cases hm : p m <;> simp [hm, ih]

variable {R : Type} [Fintype R] [DecidableEq R] {pb : R → Bool}

theorem descMass_foldS {tr : Trace R} (h : Legal pb tr) (hcs : ChartsSubsp (exec tr)) :
    ∑ k : Fin (mlog tr).length,
      max ((finrank (ZMod 2) ((foldS h).src k) : ℤ) - finrank (ZMod 2) ((foldS h).dst k)) 0
      = (ownDrop (exec tr) : ℤ) := by
  have hterm : ∀ m ∈ mlog tr,
      max ((finrank (ZMod 2) (toSub m.src) : ℤ) - finrank (ZMod 2) (toSub m.dst)) 0 =
        if m.pubk then 0 else max ((dim m.src : ℤ) - dim m.dst) 0 := by
    intro m hm
    obtain ⟨hp, ho⟩ := mlog_mem_logs tr m hm
    cases hk : m.pubk
    · obtain ⟨s1, s2⟩ := hcs.1 _ (ho hk)
      simp only [Bool.false_eq_true, if_false]
      rw [← dim_eq_finrank _ s1, ← dim_eq_finrank _ s2]
    · obtain ⟨s1, s2⟩ := hcs.2 _ (hp hk)
      have hlt := mlog_pub_asc tr init h m hm hk
      have hle : finrank (ZMod 2) (toSub m.src) ≤ finrank (ZMod 2) (toSub m.dst) :=
        Submodule.finrank_mono ((toSub_le_iff s1 s2).2 hlt.le)
      simp only [if_true]
      omega
  calc ∑ k : Fin (mlog tr).length,
        max ((finrank (ZMod 2) ((foldS h).src k) : ℤ) - finrank (ZMod 2) ((foldS h).dst k)) 0
      = ∑ k : Fin (mlog tr).length,
          (fun m : MRec R => max ((finrank (ZMod 2) (toSub m.src) : ℤ) - finrank (ZMod 2) (toSub m.dst)) 0)
            (mlog tr)[k] := rfl
    _ = ((mlog tr).map fun m => max ((finrank (ZMod 2) (toSub m.src) : ℤ) -
          finrank (ZMod 2) (toSub m.dst)) 0).sum :=
        sum_fin_list (mlog tr) (fun m : MRec R => max ((finrank (ZMod 2) (toSub m.src) : ℤ) -
          finrank (ZMod 2) (toSub m.dst)) 0)
    _ = ((mlog tr).map fun m => if m.pubk then 0 else max ((dim m.src : ℤ) - dim m.dst) 0).sum := by
        congr 1; exact List.map_congr_left hterm
    _ = (((mlog tr).filter fun m => !m.pubk).map fun m => max ((dim m.src : ℤ) - dim m.dst) 0).sum :=
        sum_filter_ite _ _ _
    _ = (ownDrop (exec tr) : ℤ) := by
        have h2 : (run init tr).olog =
            (((mlog tr).filter (fun m => !m.pubk)).map (fun m => (m.src, m.dst, m.row))).reverse := by
          rw [(run_logs tr init).2]; exact List.append_nil _
        unfold ownDrop exec
        rw [h2, List.map_reverse, List.sum_reverse, List.map_map, Nat.cast_list_sum, List.map_map]
        congr 1
        refine List.map_congr_left fun m _ => ?_
        simp only [Function.comp_apply]
        omega

section W7113
variable {Pt Hl Ow : Type} [Fintype Pt] [Fintype Hl] [Fintype Ow]
  [DecidableEq Pt] [DecidableEq Hl] [DecidableEq Ow]

/-- the rung's descent mass of a folded legal #7113 word IS its owned descent (the bridged NetW's total drop). -/
theorem descMass_fold7113 (cl : Caller Pt) (hP : Ports7113 cl) (hDc : DCount cl) {tr : Trace (Reg Pt Hl Ow)}
    (h : Legal (pub cl) tr) (hw : Word cl (exec tr)) (hfr : FramesSubsp (exec tr)) (hcs : ChartsSubsp (exec tr))
    (hn : OwnedNested (exec tr)) :
    BankBanner.descMass (foldBanked7113 cl hP hDc h hw hfr hcs hn) = (ownDrop (exec tr) : ℤ) :=
  descMass_foldS h hcs

/-- NET-D56 (open network statement): every P104 NetW with b ≤ a has total drop ≥ 56. -/
def NetD56 : Prop := ∀ (n : ℕ) (N : N8.NetW n), (∀ k, N.b k ≤ N.a k) → 56 ≤ ∑ k, N.drop k

/-- **the rung's hD premise is NET-D56 on the bridged network**: for every legal #7113-caller word (any register types)
under the verifier clauses, NetD56 gives 56 ≤ descMass of its folded banked graph. -/
theorem rung_hD_of_netD56 (hnet : NetD56) {tr : Trace (Reg (Fin 104) Hl Ow)}
    (h : Legal (pub caller7113) tr) (hw : Word caller7113 (exec tr)) (hfr : FramesSubsp (exec tr))
    (hcs : ChartsSubsp (exec tr)) (hn : OwnedNested (exec tr)) :
    56 ≤ BankBanner.descMass (foldBanked7113 caller7113 ports_caller7113 dcount_caller7113 h hw hfr hcs hn) := by
  rw [descMass_fold7113]
  obtain ⟨n, N, hd, hba, _⟩ := word_netW caller7113 hw hcs hn σ7113 hlab7113
  have := hnet n N hba
  rw [hd] at this
  exact_mod_cast this

end W7113
end BridgeNet

#print axioms BridgeNet.descMass_fold7113
#print axioms BridgeNet.rung_hD_of_netD56
