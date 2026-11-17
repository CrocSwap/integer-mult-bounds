# V2FloorNative: IntFeasible by native_decide

**WARNING: the theorems `v2floor_joint_native` and `v2floor_beta_native` DEPEND ON `Lean.ofReduceBool` (native_decide).**
This is an explicit exception, for this one purpose only, kept in its own files. No kernel-only file imports them
(`V2FloorFinal`, `V2FloorCover`, `V2FloorBound`, ... do not). Code that runs natively is plain Lean (no `@[implemented_by]`, no `@[extern]`).

## Statement
`V2FloorNativeJoint.v2floor_joint_native` : for every plan E realising all 2,625 pairs, 1,839,727,178,682 / 2^30 = 1,713.38 <= cost(E).
`V2FloorNativeBeta.v2floor_beta_native`   : same for the 1,822 beta pairs, 1,536,575,200,417 / 2^30 = 1,431.05.
Both are V2FloorFinal.floor_joint / floor_beta with `IntFeasible` discharged by `fullCheck d N T M = true` (native_decide) and
`fullCheck_sound` (kernel-checked). Inputs are only the stated model data (pairs.txt as D_joint / D_beta, T from V2FloorCost) and the small
table Mstar (below), which is itself verified by the run.

## What `fullCheck` runs (V2FloorNativeChk.lean)
1. prepOK: pair data sanity (L masks < 512), grouping of pairs by L table (flatten is a permutation of the pair list), distinct upper tables.
2. A DFS (`go'`, V2FloorNativeTab2) over EVERY subspace of F2^9 exactly once (each subspace a member list, 512-bit table rebuilt from it). At each
   subspace S of dimension n:
   - Y role (1 <= n <= 8): for each class c (log2 of the size of the upper space), #{distinct upper tables u of class c with S <= U_u} <= Mstar(n, c).
     So Mstar is VERIFIED over all subspaces, not trusted. (Mstar = max over Y; <= the Gaussian binomial that check.c uses, so it is tighter.)
   - X role (1 <= n <= 7): for every b in n+1..8, with recsX = pairs with L <= S <= U: either the plain total sum_{recsX} sum_{k in [n,b)} num <= T n b,
     or the relaxation sum_c topsum(Mstar(b,c), weights of the class-c upper tables) <= T n b (check.c's top-M relaxation).
3. Soundness (kernel-checked): enumerator completeness (`complete`, every Submodule of F2^9 is reached: lead-position reduction argument, Node/Step/Inv),
   table <-> Submodule dictionary (Rep', RepT, RepT_le_iff, Rep'_kerMs with the F2 inner product, Rep'_Lms), top-M lemma (`top_le`), grouping lemma
   (`sum_group`), and `core` (the list-level bound), `sound_aux` / `fullCheck_sound`.

## Files
V2FloorNativeTab (Step/Inv/complete, first DFS), V2FloorNativeTab2 (member-list DFS `go'`, `enum_all'`), V2FloorNativeLists (top-M, grouping),
V2FloorNativeData (L/U tables, containment), V2FloorNativeChk (checks + soundness; NO native_decide), V2FloorNativeJoint / V2FloorNativeBeta (the only
native_decide files).
Mstar joint (rows b = 1..8, cols c = 0..9): [[0,0,1,5,0,0,25,10,62,0],[0,0,1,2,0,0,15,8,36,0],[0,0,0,1,0,0,8,6,20,0],[0,0,0,0,0,0,5,4,12,0],
[0,0,0,0,0,0,4,3,8,0],[0,0,0,0,0,0,1,2,4,0],[0,0,0,0,0,0,0,1,2,0],[0,0,0,0,0,0,0,0,1,0]]; beta: all mass in column 8 (62,36,20,12,8,4,2,1).
Generator: a small C program (not shipped); the numbers are re-verified by the Lean run.

## Status
- Compiled with standard axioms (no native_decide): V2FloorNativeTab, Tab2, Lists, Data, Chk (soundness `fullCheck_sound`).
- `V2FloorNativeBeta.v2floor_beta_native` compiled (verified build, not rebuilt for this package, see CHECK.txt):
  axioms [propext, Classical.choice, Quot.sound, native_check_beta._native.native_decide.ax_1_1] (the last one is the native_decide axiom, via `Lean.ofReduceBool`).
- The joint native file (V2FloorNativeJoint) is part of the earlier package, not this one.
- Peak memory about 2.3 GB (imports); the check itself runs over every subspace of F2^9.
