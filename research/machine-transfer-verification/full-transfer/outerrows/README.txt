Outer row supply and uniform descriptor overhead
================================================

This package proves 22 new Lean theorems, using the previously verified exact
floor-depth definition. It provides a simpler all-width choice of outer row
digits for the selected m=575, max child=529 and every W<=137151806. This also
covers the smaller physical role count of the newer PR71/73 construction.

Let D(e)=0 below m and D(e)=1+D(529*floor(e/575)) otherwise. Each internal
step decreases width by at least 575-529=46. Strong induction therefore gives

    46 D(e) <= e.

Choose rho=14D(e), for any fixed radix q>=2. Since 2^28>=137151806,

    W^D(e) <= q^(2rho),       2rho < e    for every e>0.

The second assertion follows from 28<46 when D>0, and from rho=0 otherwise.
Thus there is no exceptional finite set of widths to exclude, no eventual
threshold to infer, and no recursion into a zero-width residual chunk.
This explicit rho need not be the least possible choice; it remains O(log e).

Put N=q^(2rho), P=W^D(e), and R=((N-1)/P+1)P. The exact integer theorems give

    N <= R < N+P <= 2N,       P divides R,
    W^D(e-rho) divides R.

The rows come from existing digits:
    q^(2rho) q^(2(e-rho)) = q^(2e).
Consequently the sole outer rounding increases volume by less than two,
also with arbitrary positive spectator factors. Padding is not introduced
at every recursive node. The generic rho bound is

    rho <= c(1 + 1/(p log(m/tmax))) e^p     for every p>0.

The outer-cost corollary explicitly assumes the physical gathering/padding
contract and a recursive cost bound; it proves that this single layer
preserves the exponent with an explicit constant.

Descriptor uniformity
---------------------
Every descendant retains the complete root main-address range
X=q^(2(e-rho)); these digits may be spectators, but they are not deleted.
This retained-range contract is essential. At depth j<=D(e), with S>=1 an
arbitrary spectator factor, define

    V0=R X S,      Vj=(R/W^j) X S.

Because 2rho<e, we have W^j<=P<=N<=X<=Vj. The formal integer identities give

    V0=W^j Vj <= Vj^2.

Hence log(2V0)<=2log(2Vj). For every fixed positive integer k, a proved
real-power/log estimate gives the explicit uniform bound

    (log(2V0))^k <= 2(2k)^k Vj.

This closes the quantitative absorption step for any fixed polynomial
descriptor cost. It does not implement descriptor arithmetic or prove the
physical complete-spectator contract itself.

Scope and reproduction
----------------------
The row counts, volumes, logarithmic estimates and cost implications are
formal theorems. Streaming digit moves, row gathering/padding/removal,
fixed-tape child execution, and the stated implementation-cost contracts
remain external. This package proves no unconditional multiplication bound.

Use an existing cached Lean4.21.0 project with Mathlib
308445d7985027f538e281e18df29ca16ede2ba3 and matching lean/lake on PATH:

    python3 check.py --lake-project /path/to/formal/lean

The default dependency directory is ../../transfer-proof/recurrence.
Only FloorDepth.lean and FloorRecurrence.lean are needed and rebuilt; their
18 audits are separate from the 22 new audits. The checker validates hashes,
source/declaration inventory, compiler pins and all axiom reports, installs
nothing and uses its own olean directory. proof-manifest.json includes the
declaration-to-English map; verification/ contains fresh build receipts.
