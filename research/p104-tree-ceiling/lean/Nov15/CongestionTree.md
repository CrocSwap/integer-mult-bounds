# CongestionTree: node-partition tree bound + port-realised refinement, kernel-certified

Files (all `Nov15/`, kernel only, no sorry / native_decide, axioms propext, Classical.choice, Quot.sound; each file built alone under runlean.sh, peak <= 3.2 GB):
`CTreeCore` (core-only: `Row`, `Row.check` = the DP-row conditions), `CTree{cg,ga,gb}Defs/P*/Data{CG,GA,GB}` (the certified DP tables, 230 rows each, one `decide +kernel` per row),
`CongestionTreeCore` (row soundness, `Tr`, `tree_cost_ge`, `reduction`, `tree_lower`), `CongestionTreeW` (weight certificate `W_lower`), `CongestionTreePiece` (`tree_regs_lower`, `tree_piece`),
`CongestionTreeCert{CG,GD}*` (Defs, Wt0-13/Wt, D, S/T/U/L per piece), `CongestionTree` (final).  The generators of the data files are not part of this package.

## Certified results (true values, not the earlier digits)
| theorem | covers t in | kappa <= | earlier (measured-profile) figure | why different |
|---|---|---|---|---|
| `ceiling_native_J` (old) | [.0118103, 1] | .0118103 | | |
| `ceiling_tree_CG` | [.0117694, 1] | **.0117694** | .0117604 | The earlier computation used the frontier count profile (79x48, 21x47, ...); Lean takes only the stated counts (|J| >= 4962, <= 48 partners, <= 104 sources): Lagrange line, tree lift 28.5096 = 1.0165 x 4962 spF; float class crossing .0117696, certified at .0117694 (margin 6.2e-3). .0117693 fails (margin -5.0e-3). |
| `ceiling_tree_GD` | [.0116750, 1] | **.0116750** | .0116675 | same reason (class-min x1.0525 at t=.0118; the DP weights here are frozen at a0 = .011675 and bounded below by a kernel monotonicity cert); .0116749 fails (margin -8.1e-3). |
Both, for t in [t0, 1]: F(1 - t, invoice (caller 6 7) n 17) < 0, on [tJ0, 1] by `ceiling_native_J` (its own hypotheses are kept), on [a0, tJ0] by two `tree_piece`s.  Only the tree piece uses the new premises.

## What is kernel-checked
* `Row.check W rs r` (per row, 230 rows x 3 tables): G(x,0)=0, G(x,.) monotone, `Ge(x,j) <= floor(W[dim x][dim y]/n x) + G(y,j)` for every allowed child y with j <= m(y), `G(x,k) <= Ge(x,j) + G(x,k-j)` (all 1<=j<=k<=m(x)); leaves have G = 0.  `rowOK_of_check`, `step` (child families), `tree_cost_ge`: G(r,|R|)/SC <= cost of ANY `Tr` tree (induction on `Tr`, nested list recursion).
* `reduction`: double counting `sum_s tree_s <= sum_e w_e` from "a move is used by <= nm e sources" + Nodup of each tree's move list.
* `tree_lower`: per source `lam k_s - gamma_c <= SC (tree_s + cap x_s)` from `lineOK` (49x49 integer check per class and piece), summed with |J| >= 4962, |S| <= 104, |B| >= nB.  DP data is NOT shrunk: full 230-shape DP tables checked by `decide`; no float, no rounding gap (weights floor(1e14 c2) from `W_lower`).
* `W_lower`/`wtOK`: for every s in [1 - tJ0, 1 - a0], W a b / 1e14 <= c2(gs s) a b: point enclosure at s = 1 - a0 (`Fup (negCF cf)`) plus `dLo (negCF cf) > 0` on the window (h9, k0 nonincreasing in s, so no monotonicity hypothesis).  28 pairs x 2.
* per piece: sigma (`sigOK`), `Fup cfC` point, unit lower bound (`Fup` of 8^s-9^s), `lineOK`, table arithmetic (norm_num), `cfC` derivative cert on [.93, 1 - a0] (so F_base monotonicity is proved, `hFbT_of`).

## Hypotheses of `ceiling_tree_CG` / `_GD` (status)
Old ones (as `ceiling_native_J`; unchanged status): hmono, hd9, hmix, hk, hmass, hmd, hmr, hF, hY, hst, hEex = natives computed facts (register/lifetime structure, exact identities); hcong*, hdist, hJ (used only for t in [tJ0, 1]) = open (I2 / register machine), hspMono/hcstMono (paper theorem: c2 nondecreasing in t), hspTab/hcstTab/hspTabJ/hcstTabJ (outward-Decimal brackets, data).
New ones (all in `TreeData` + 4 binders):
1. `T.J, T.S`: junk cells (source, reader) with sources <= 104 (`hScard`), each source <= 48 partners (`hfib`), |J| >= 4962 (`hJcard`; natives: |J^arr| = 4962 computed) -- natives.
2. `T.R, T.x, hcell, hxk`: a source's cells are either transported (x_s, each pays `capC`) or have a reader in R_s -- open (I2 path + own56 transport cap, as in hcong).
3. `T.htreeA/htreeB (Tr ...)`: for each source the union of its cells' I2 paths contains an out-tree of charts: nodes are shapes (rows) of the 230-shape DAG (`hr`, `hside`: shape in list, `Row.ok` = dim up, n up, m down), child edge = a nested move e with nm e = n(A), dA, dB its dimensions; readers of a node are covered by the readers of its children (`hcov`, subset, NOT disjoint) and |R| <= m(chart) (`hm`) -- open (nested moves, path = chain of moves meeting at charts; the node-partition argument).  Disjointness of reader sets is not needed for the lower bound and is dropped.
4. `T.hMv, hnd, hcap`: tree moves Nodup, every move used by <= nm e = n(A) sources (I2 capacity) -- open.
5. `T.Mreg, T.Mun, hMsub, hdim` and `hP1`: the tree's moves are register steps up to owned rises; `sum_{Mreg} c2 + capC * sum x <= sum regs c2 + Omega`  -- open (same I2 charge as hcong, aggregated by moves; includes the transported cap).  `hP2`: owned-rise moves weigh <= corrC = 8 cst -- open (an uncharged edge saves <= c2).
6. `hcstMonoT` (cst monotone on [a0, 1/10]), `hcst0/1` (cst(b) <= cH brackets) -- same status as hcstMono/hcstTab (data).
7. GD only: `Bset` (>= 48 sources) whose trees use only the edges `E48` realised by concrete nested charts (`rsB` = rows with `mask` = E48) -- natives computed fact (per-port union of cell lattices over all 29,212 subspaces; edge sets fall into 3 classes of 24, 32 and 48 ports; the 48 ports of the last class have the edge set E48 = the mask of `gbR`; the other 56 sources are assigned the unrestricted DAG `gaR`, whose edge set contains every port's realised set).  The exhaustive count (the (3,4,12) and (5,8,6) charts cover only 1,344 of 4,992 cells) is the reason for E48; it is a concrete enumeration, NOT reproduced in Lean and not script-checked for this package (open: would need the subspace lattice of F_2^8 as data).  Source/class counts (104, 48) are computed facts.
8. `T.dA, dB, nm` positivity / dims: derived inside (`hdim`, row facts).

## Paper checks
* No false step found: tree DP (independent Python and C programs) = `Row.check` DP (same recursion; Python/C/Lean agree on F(48) = .2755792 at t=.0117604, restricted class B .2975394).
* Corrections to the earlier (measured-profile) statements: (i) ceilings .0117604 / .0116675 use measured count profiles / max(out,in) and are not statements of the Lean form; the Lean certificates are .0117694 / .0116750 (9.0e-6 and 7.5e-6 weaker).  (ii) reader-set disjointness is not needed.  (iii) OUT and IN give the identical DP table (F equal at every k), so `max(out,in)` only differs through the count profile; only OUT is formalised.
* `hdist`-style per-cell claim is replaced, not weakened: nothing here uses spF; weights enter only through `W_lower`.
