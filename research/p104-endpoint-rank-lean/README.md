# A formal endpoint-run rank lower bound for P104

This package formalizes the block-matrix and moment implication used in
[PR2662](https://github.com/CrocSwap/integer-mult-bounds/pull/2662). An independent
binary checker also corroborates its **416 endpoint runs and rank mass 928**.
It imports no predecessor executable and does not repeat the physical dual's
native or logical correctness replay.

The result has two distinct evidence levels:

- Lean checks five generic theorem roots over arbitrary fields and finite
  square blocks. Their only reported axioms are `propext`, `Classical.choice`
  and `Quot.sound`.
- Python reconstructs all source-run binary matrices and ranks. This finite
  source binding is not a Lean certificate. It agrees with the predecessor's
  histogram, using transvections and finite span sets rather than its retained
  native tableau interpreter and Gaussian rank elimination.

No new construction, supplier, unrestricted optimum or kappa is claimed.
The selected record and all frozen predecessors are unchanged.

## Formal statements

For a matrix `U` on `n ⊕ n`, `mixing U` is its input-Z to output-X block B.
`EndpointRank.lean` proves:

1. `mixing_mul` computes `B(UV) = A(U) B(V) + B(U) D(V)`.
2. `mixing_rank_mul_le` proves `rank B(UV) ≤ rank B(U) + rank B(V)`.
3. `word_rank_le` bounds the mixing rank of any finite matrix product by its
   total declared natural-number charge. Each factor must satisfy the explicit
   premise `rank B(U) ≤ charge U`. Empty products are included.
4. `moment_lower_bound` proves `target^p ≤ Σ r_j^p` from
   `target ≤ Σ r_j` and `0 < p ≤ 1`, including empty rank lists.
5. `word_moment_le` combines the actual matrix-product bound and the moment
   bound. It does not take the matrix rank conclusion as an extra premise.

The proof uses rank subadditivity and the rank bounds for products, followed
by subadditivity and monotonicity of the real power. It assumes neither
symplecticity nor invertibility. Those extra structures are needed to identify
physical operations with these matrices, not to prove the inequality.

For the predecessor's restricted rewrite class, Gaussian Clifford monomials
have mixing rank zero and a rank-r positive child has mixing rank r. Thus the
formal charge premise is the relevant one. The physical identification and
its phase convention remain inherited, not formalized here. In particular,
rank additivity is false: a binary rank-one Fourier shear squared is identity.
The finite controls exercise this cancellation.

## Independent finite binding

The exact source is commdata2338's PR2662 at
`b67542b2896c21106f3945673bbf5b6e131408cc`. It retains ywz65's PR2586 word at
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`.
[PREDECESSOR.json](PREDECESSOR.json) authenticates the byte-exact word and
attribution-bearing proof text. [SOURCES.json](SOURCES.json) pins the live
canonical-frame semantics and the existing Lean environment. No retained Python
module is imported, executed or copied into the new checker.

Here is the closed-form binary action used by `verify.py`. Extend a proper
frame basis to an ordered basis with column matrix A, and let d_i be the dual
basis vector to column a_i. The retained canonical chart has

```
K = D_Q P_A,    Q = I + A^(-T) A^(-1),
Gamma_W = K F_dim(W) K^(-1).
```

Consequently its unsigned Pauli action is the product of commuting symplectic
transvections along `(a_i, a_i + d_i)` for the frame's basis indices. ZERO is
identity. FULL uses the retained explicit full Fourier shear, independently of
its displayed basis. Complex conjugation and scalar signs change Pauli phases
but not these binary labels. The binary action of each frame is an involution;
the corresponding phased complex operator need not be.

For every source run, the checker constructs
`Gamma_final Gamma_initial^(-1)` directly. It computes the mixing rank by
exhaustive F2 span closure, never by the predecessor's tableau/rank routines.
It checks the individual edge charges, frame continuity, disjoint source-run
events, initial/final source binding and every ADD barrier, including source reads. It obtains:

```
288 H1 + 16 H3 + 28 H4 + 39 H5 + 30 H6 + 15 H7
416 runs; rank mass 928
```

The computed mixing rank equals the source edge rank mass in every run.
PR2662 supplies matching single-child recipes; their native correctness is
inherited, not replayed here. The other 2,614 units of the predecessor's total
rank mass are outside this certificate. A competing implementation can have any finite number of
Gaussian monomials and positive children inside each fixed run, but may not
cross an ADD or introduce cross-register interactions. The generic formal
inequality therefore supports the predecessor's scoped run optimum, conditional
on the physical charge interpretation. Phases cannot invalidate a necessary
binary lower bound, but this check cannot prove physical operator equality.

The tests compare all 338 consumed frame presentations with a separate literal
P/D/C binary evaluator. They also compare every independent ordered frame
through three address bits, 230 cases, and all 256 pairs of arbitrary 2-by-2
binary matrices. Failure controls cover undercharged children, broken frame
continuity, invalid vectors, source/receipt corruption and exclusive output.
An optimized Git-free export preserves every file's bytes.

## Reproduce

The standard-library finite replay uses Python 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py \
  --package research/p104-endpoint-rank-lean
```

Expected census summary:

```
PASS_P104_ENDPOINT_RANK runs=416 rank_mass=928 no_native_imports no_new_kappa
```

The generic registered hook runs the census and six test groups. It does not
claim to invoke Lean. For the formal proof, use the repository's pinned
Lean 4.21.0 / Mathlib environment:

```sh
cd formal/lean
lake exe cache get
cd ../..
python3.12 -Werror -B research/p104-endpoint-rank-lean/check_lean.py
```

The wrapper requires Mathlib commit
`308445d7985027f538e281e18df29ca16ede2ba3`, checks all five actual axiom reports,
and compiles four altered contracts that must fail elaboration. They falsely
assert rank additivity, remove the child-charge premise, reverse the rank
budget or reverse the exponent range. Expected summary:

```
PASS_ENDPOINT_RANK_LEAN roots=5 invalid_contracts=4
```

`--project PATH` permits an existing cache-bearing formal project only when its
three environment files match the pinned repository files byte-for-byte. Local
Linux checks used that option with the original checkout's identical environment.
Mathlib proof objects came from its existing build cache; Mathlib was not rebuilt
from source. The scoped workflow runs both finite and formal checks. Hosted CI
is separate evidence, not claimed here.

## Limits and expansion decision

This formalizes the generic matrix/moment implication, not the canonical-frame
semantics, source JSON parsing, finite ranks, complex phase, the physical/native
middle or the complete multiplication theorem. The finite checker is a separate
source-bound corroboration, not a replacement for native replay.

The predecessor's 128 fusions, 3,542 total rank mass and physical correctness
retain their original credit. This package does not re-admit them. Actual owners,
decreasing-edge hosting, idle/residual costs, rounded private erasure, precision,
consumer restoration, all-size realization and the other 102 forward corrections
remain outside scope. The family decision is to finish this audit without
expanding construction work. No selected cold replay was run.

### Bounded implementation deviations

Python allocates managed objects during checking. The proof input is fixed at
5,398 events, 416 runs, nine address bits and 18 binary matrix columns. Span sets
and inversion tables have at most 512 entries. JSON inputs have a 500,000-byte
limit; subprocesses have 60- or 120-second timeouts. Temporary formal/export
files use scoped cleanup. This is the managed-runtime exception to fixed
steady-state allocation, not a claim of allocation-free execution. Any extension
beyond nine bits must replace the exhaustive span/inversion implementation and
reassess these bounds. Lean proof induction is kernel-checked structural proof,
not an unbounded runtime traversal in the finite checker.

## Open next questions

Can the canonical-frame transvection semantics and the 416 rank records be
connected to the generic theorem inside Lean? That would remove the current
Python source-to-matrix trust step. First formalize one rank-one endpoint from
the retained P/D/C definition, then add a reflected binary-rank checker. Neither
component is supplied here. [TASK.json](TASK.json) records this question, the
changed task scope and the overlap coverage. Crossing ADDs or admitting a supplier
is a separate research question and is not reopened by this proof.

## Credit

Nick Petalas. Apache-2.0. No independent human review is claimed.

Credit commdata2338 / PR2662 for the endpoint-run theorem, rewrite class,
histogram and fusion construction; ywz65 / PR2586 for the physical dual and
PR2497/2551 for its inherited boundary distinction; Nick Petalas / PR2550 for
the complementary-frame method. Retain Ross Richardson / PR2445,
commdata2338 / PR2393, Hiroki Kumazaki, Philippe Van Velzen,
Chafik Boukhalfa / PR1991, Rohan Arun / PR1972, Adam Gall / PR1940,
Josie Elliston / PR1071, Ali Romman / PR1125 and PR1862,
icekylinx / PR531 and the retained compiler/native lineage. The retained source
text preserves their original attribution. Mathlib supplies the standard rank
and real-power results. This contribution is their scoped formal composition
and independently implemented binary source binding, not a new rank inequality.
