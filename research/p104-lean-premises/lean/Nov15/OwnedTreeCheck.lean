/-
LEAN-PREM6: instances of OwnedTree on the real data (generated OwnedTreeData.lean).
-/
import Nov15.OwnedTree
import Nov15.OwnedTreeData

namespace OwnedTree
open OwnedSkeleton

/-- Real call sites: all 6250 MOVE events of the word. -/
theorem e3_tree_real (d : ℕ) : execU sitesAll d [] [] = some [] := e3_tree sitesAll d
theorem n_sites : sitesAll.length = 6250 := by decide +kernel
theorem n_sites_owned : sitesOwned.length = 47 := by decide +kernel

/-- The caller's op alphabet has no owned-storage op (codes 0..6 are ADD SCALE LAMBDA SWAP QUERY
IDLE_ODD IDLE_ONE; 7 is J = one native call). -/
theorem caller_alphabet : callerOps.all (fun x => decide (x ≤ 7)) = true := by decide +kernel
theorem caller_17_calls : callerOps.count 7 = 17 := by decide +kernel
theorem caller_len : callerOps.length = 4783 := by decide +kernel

/-- Depth 1 with the first 4 real owned-MOVE call sites (root + 4 child units, 2,0xx events; more sites
exceed the 3.5 GB kernel-evaluation guard, the general case is `e3_tree_real`). -/
theorem concrete_d1_owned : execU (sitesOwned.take 4) 1 [] [] = some [] := by decide +kernel

/-- Control 2: the real skeleton with its last event dropped, used as the child unit of the real parent,
is rejected (leak crosses the child boundary into the parent's CLEARs). -/
theorem c_real_child_leak :
    execBad skel.dropLast [skel.length / 2] [] = none := by decide +kernel

#print axioms e3_tree_real
#print axioms concrete_d1_owned
#print axioms c_real_child_leak
#print axioms caller_alphabet

end OwnedTree
