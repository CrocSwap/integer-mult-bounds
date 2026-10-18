# Exact spectator-orbit reduction

This proves an arithmetic equivalence for the historical finite screen in
`scripts/audit_sparse_fusion.py:central_gate_screen`. It does not extend its
construction family or its lower-bound claim. All arithmetic is over F2.

For each of the 64 symmetric three-coordinate blocks S, the original routine
constructs Q = diag(S, I_(h-3)). For each weight-three indicator t it computes
rank(Q + t t^T). Its unary sum includes this rank plus the unchanged
r = rank(Q + I). The original columns are precisely the columns of that
matrix: column i is Q_i XOR t when t_i = 1, otherwise Q_i.

Let P be any coordinate permutation fixing coordinates 0, 1 and 2. The identity
spectator block and zero cross blocks give P Q P^T = Q. Therefore

    P (Q + t t^T) P^T = Q + (P t)(P t)^T.

P is invertible, so these two matrices have equal rank. Two weight-three
indicators belong to the same orbit exactly when their restriction to the
first three coordinates is the same. With `low = t & 7`, their spectator
weight is necessarily `w = 3 - low.bit_count()`. Spectator permutations act
transitively on subsets of size w. The orbit has exactly C(h-3, w) members and
the following indicator is one of them:

    low | (((1 << w) - 1) << 3).

For the admitted h >= 22, all eight low masks have valid representatives.
Every triple appears in exactly one orbit, and the multiplicities sum to
C(h,3), by partitioning triples according to their intersection with the
first three coordinates (equivalently, Vandermonde's identity). Consequently

    sum_(weight(t)=3) [rank(Q + t t^T) + r]
      = sum_(low=0..7) C(h-3, 3-weight(low))
          * [rank(Q + t_low t_low^T) + r].

This identity holds for every tested block, including singular S. It does not
rely on a generic full-rank assumption, random trials, modular lower bounds or
the numerical inequalities of the original theorem.

Only the enumeration, its cardinality and this weighted sum are adapted.
The matrix construction, k and r ranks, all 64 frame cases, the 4,096 ordered
joint-frame pairs, their exact rational inequalities, `require` calls and
every receipt field remain the original ones. The same values enter the same
inequalities, so the adapted routine preserves both their successes and
failures. The complete certificate additionally retains the original finite
phase group, operator identities, mixing tests, hypothetical budgets and
upstream-source checks.

At h=25, the unary rank count changes from 64 C(25,3) = 147,200 to 64*8 = 512.
Each implementation still performs 128 frame-rank calculations and 4,096
joint-pair rank calculations. The timing benefit depends on the interpreter
and input; this count is not a runtime theorem.

The independent tests explicitly map every triple to its representative and
conjugate its matrix. A separate row-elimination implementation checks all
455,424 frame/triple cases at h=22,25,28. Those are exhaustive checks of these
finite instances. The general equivalence above follows from permutation
conjugation, not from extrapolating those checks.

This argument assumes the exact pinned frame geometry Q = diag(S,I), the
three-coordinate change block, weight-three indicators and exact matrix rank over F2.
Changing the spectator block, cross blocks, triple family or distinguished
coordinates requires a new argument. The inherited manuscript's all-size,
realization, hosting, precision/tape and analytic obligations remain outside
this tool. No new kappa, circuit, integer-multiplication runtime or full formal
verification is claimed.
