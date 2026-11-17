# Verification boundaries

The finite replay covers every tridiagonal integer matrix with entries in
{-1,0,1} in dimensions one through three, followed by 156 deterministic
fixtures in dimensions four through thirty-two. The latter include diagonal,
tridiagonal, width-three and full bands, nonsymmetric signed entries,
strictly diagonally dominant instances, and adjacent-transposition matrices
with zero leading diagonal entries. Singular inputs are retained and checked
for rejection, rather than silently removed.

The band routine and dense Gauss-Jordan oracle use different loop structures
and independent support handling. Both are produced by the same contributor.
Every accepted result additionally satisfies both complete inverse identities
by direct multiplication. Three precision pairs check all rounded entries.
The tests cover the algorithm's output contract, not just a recorded hash.

Fifteen rejecting controls cover malformed dimensions, a nonsquare matrix,
Boolean/noninteger entries or parameters, negative or excessive precision,
out-of-band entries, dimension and entry-height limits, and a corrupted
inverse. Two explicit signed half-ties check the output convention.

The finite result is 1,290 invertible matrices, 1,137 singular matrices,
52,308 two-sided inverse entry checks and 508 executed row exchanges.
The three operation-count fixtures are additional complete inversions of
tridiagonal matrices in dimensions eight, sixteen and thirty-two. Their
band/dense rational-operation counts are 327/1248, 1303/9152 and 5175/69504.
These are exact counts of the indicated source-level rational operations,
including operations on zeros, not measurements of elapsed speed, bit work,
or the best available dense solver. Both counted routines return the same
complete exact inverse on each fixture. The asymptotic claim rests on the
written loop bound, not extrapolation from these three counts.

The replay emits a receipt derived from the actual checks and SHA256 of
every package file. `--receipt PATH` writes it exclusively to a caller-chosen
external path; normal replay writes no files. Normal and optimized Python
retain the same explicit checks. Source provenance is checked separately
by the repository metadata runner. No predecessor scientific executable is
imported, copied, or run.

## Code and resource inspection

The public solver boundary enforces N<=256, 0<=w<N, integer entry heights
at most 4096 bits, and nonnegative precision parameters at most 4096.
The verifier's matrix generators have fixed finite product/range bounds.
There is no recursion, dynamic evaluation, subprocess, network request,
background process, or mutable global cache. All functions fit within
sixty physical lines. Explicit exceptions enforce contracts under `-O`.
The receipt destination is the only output resource, owned by a context
manager; failures propagate to the caller.

Power of Ten rule 3 has a managed-runtime deviation in `band_inverse.py`
and `verify.py`: Python integers, fractions and containers allocate during
execution. The solver's fixed input bounds and O(N^2) live entries, together
with the determinant-height argument in PROOF.md, give finite resource
bounds. A fixed-allocation implementation would require bounded native
integer buffers and is outside this rational reference routine. Porting to
such buffers is required before claiming allocation-free operation.

Rule 10 uses warning-strict normal and optimized execution, in-memory syntax
compilation and an AST/function-size inspection. No project-wide diagnostics
policy or unavailable external type-checker result is claimed. Reassess those
checks when adopting this isolated routine into a production entry point.
The code introduces no other intended Power of Ten deviation.

The direct solver, registered commands, metadata/source pins, exact committed
bytes/source history and Git-free exported replay are separate checks. Their
actual outcomes are reported in the PR body. Hosted CI and mathematical
acceptance are separate from local success.
