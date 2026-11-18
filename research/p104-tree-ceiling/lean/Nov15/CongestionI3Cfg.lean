import Nov15.CongestionI3Data

/-!
CONGESTION-I3 configuration half .  Kernel-checked facts about the 8 rank-8 C=56 decoder configurations
(internal notes sec. 2): z.z' = 0, and the census of the "unique" even cells (cells that exactly one chain can touch).
`dot` = F2 dot product of 9-bit labels; chain k = (z_k, z'_k) (virtual lines 104..119, labels `Ulab`); the chain k's support on the
cell (t, s) (t, s < 104) is G[t, z_k] * G[s, z'_k] (nonzero pattern `Gmask`).
-/
set_option linter.constructorNameAsVariable false
namespace CongestionI3

/-- parity of the 9 low bits -/
def par (x : ℕ) : ℕ :=
  let a := (x ^^^ (x >>> 4)) &&& 15
  let b := a ^^^ (a >>> 2)
  ((b ^^^ (b >>> 1)) ^^^ (x >>> 8)) &&& 1
theorem par_test : (List.range 512).all (fun x => par x == ((List.range 9).foldl (fun acc i => acc + (x >>> i) % 2) 0) % 2) = true := by decide +kernel
def dot (a b : ℕ) : ℕ := par (a &&& b)
def lab (i : ℕ) : ℕ := Ulab.getD i 0
/-- G[t, z] ≠ 0 for t < 104, z in 104..119 -/
def gnz (t z : ℕ) : Bool := ((Gmask.getD t 0) >>> (z - 104)) % 2 == 1

/-- the even cells: t ≠ s, q_t . q_s = 0 -/
def even (t s : ℕ) : Bool := t != s && dot (lab t) (lab s) == 0
/-- chains that may touch (t,s): q_t ⊥ z_k and q_s ⊥ z'_k (frames of the chain) -/
def Kset (c : List (ℕ × ℕ)) (t s : ℕ) : List ℕ :=
  (List.range c.length).filter fun k =>
    dot (lab t) (lab (c.getD k (0, 0)).1) == 0 && dot (lab s) (lab (c.getD k (0, 0)).2) == 0
/-- chains whose product is nonzero at (t,s) -/
def Tset (c : List (ℕ × ℕ)) (t s : ℕ) : List ℕ :=
  (List.range c.length).filter fun k => gnz t (c.getD k (0, 0)).1 && gnz s (c.getD k (0, 0)).2
/-- the unique cells of chain k: even, exactly one chain (k) may touch them, and it does -/
def isUniq (c : List (ℕ × ℕ)) (k t s : ℕ) : Bool := even t s && Kset c t s == [k] && Tset c t s == [k]
def uniqCells (c : List (ℕ × ℕ)) (k : ℕ) : Finset (ℕ × ℕ) :=
  (Finset.range 104 ×ˢ Finset.range 104).filter fun p => isUniq c k p.1 p.2 = true

/-- orthogonality z.z' = 0 for all rows -/
def cfgOK (c : List (ℕ × ℕ)) : Bool := c.length == 8 && c.all fun p => dot (lab p.1) (lab p.2) == 0
/-- chain index of every unique cell, one pass over the 104 x 104 cells -/
def uniqOwners (c : List (ℕ × ℕ)) : List ℕ :=
  (List.range 104).flatMap fun t => (List.range 104).filterMap fun s =>
    if even t s then
      (match Kset c t s with
       | [k] => if Tset c t s == [k] then some k else none
       | _ => none)
    else none
def uniqCensus (c : List (ℕ × ℕ)) : List ℕ := (List.range 8).map fun k => (uniqOwners c).count k

theorem cfgs_len : cfgs.length = 8 := by decide +kernel
theorem cfgs_ok : cfgs.all cfgOK = true := by decide +kernel
/-- every chain of every configuration has exactly 330 unique cells (2640 = 8 * 330 per configuration, F1 sec. 2); one theorem per
configuration (kernel memory is per declaration). -/
theorem cfg_uniq0 : uniqCensus (cfgs.getD 0 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq1 : uniqCensus (cfgs.getD 1 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq2 : uniqCensus (cfgs.getD 2 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq3 : uniqCensus (cfgs.getD 3 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq4 : uniqCensus (cfgs.getD 4 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq5 : uniqCensus (cfgs.getD 5 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq6 : uniqCensus (cfgs.getD 6 []) = List.replicate 8 330 := by decide +kernel
theorem cfg_uniq7 : uniqCensus (cfgs.getD 7 []) = List.replicate 8 330 := by decide +kernel

theorem uniqCells_disjoint (c : List (ℕ × ℕ)) {k k' : ℕ} (h : k ≠ k') : Disjoint (uniqCells c k) (uniqCells c k') := by
  rw [Finset.disjoint_left]
  intro p hp hp'
  simp only [uniqCells, Finset.mem_filter, isUniq, Bool.and_eq_true, beq_iff_eq] at hp hp'
  have := hp.2.1.2.symm.trans hp'.2.1.2
  simp at this
  exact h this

end CongestionI3

#print axioms CongestionI3.cfg_uniq7
#print axioms CongestionI3.uniqCells_disjoint
