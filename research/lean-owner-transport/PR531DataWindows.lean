/- Generated from the pinned PR531 complete hosted template.
Original construction: icekylinx and credited predecessors; Apache-2.0.
Projection/proofs: Rohan Arun with OpenAI Codex assistance. -/
import PR531TableData
import OwnerSeparation
namespace OwnerTransport.PR531DataWindows
open OwnerTable OwnerSeparation PR531Table
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def stagePair (s : Nat) : Nat := (#[0, 0, 0, 1, 1, 2, 2, 3, 3][s]?).getD 0

def checkWindow (g : Nat) : Bool :=
  (witness.window g).times.all (fun t =>
    decide ((witness.call t).2 ≠ g / 18 ∨
      witness.lane (g % 18) / 2 ≠ stagePair (witness.call t).1))

theorem all_windows_checked : checkRange checkWindow 0 144 = true := by decide

theorem windows_avoid_data : WindowsAvoidData witness stagePair := by
  intro r child hr hc t ht
  change r < 8 at hr
  change child < 18 at hc
  have hg : r * 18 + child < 144 := by omega
  have h := range_sound checkWindow 0 144 (r * 18 + child)
    all_windows_checked (by omega) (by omega)
  have hh := List.all_eq_true.mp h t ht
  have hdiv : (r * 18 + child) / 18 = r := div_tail _ _ _ hc
  have hmod : (r * 18 + child) % 18 = child := by omega
  simpa only [decide_eq_true_eq, hdiv, hmod] using hh

theorem all_active_pairs_fit :
    checkRange (fun t => decide (2 * stagePair (witness.call t).1 + 2 ≤ witness.lanes)) 0 72 = true := by decide

theorem active_pair_fits (t : Nat) (ht : t < witness.calls) :
    2 * stagePair (witness.call t).1 + 2 ≤ witness.lanes := by
  have h := range_sound _ 0 72 t all_active_pairs_fit (by omega) ht
  exact of_decide_eq_true h

theorem all_call_replicas_fit :
    checkRange (fun t => decide ((witness.call t).2 < witness.replicas)) 0 72 = true := by decide

theorem call_replica_fits (t : Nat) (ht : t < witness.calls) :
    (witness.call t).2 < witness.replicas := by
  exact of_decide_eq_true (range_sound _ 0 72 t all_call_replicas_fit (by omega) ht)

end OwnerTransport.PR531DataWindows
