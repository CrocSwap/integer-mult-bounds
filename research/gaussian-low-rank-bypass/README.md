# A sharp energy obstruction for dense low-rank Gaussian bypasses

This contribution was produced by Nick Petalas. New work is Apache-2.0.

For a d-dimensional unitary target T, an N-dimensional flat unitary child K,
and arbitrary rectangular adapters, write

    T = B K A + H + E,
    rank_C(H)=h,  ||E||_(2->2)<=eta<1,
    M=||A||_1 ||B||_infinity.

The new local obstruction is

    (d-h)(1-eta)^2 <= ||BKA||_F^2 <= d^2 M^2/N.

The bypass H may be dense and have unbounded coefficients. Its kernel forces
the child path to carry d-h almost unit-length orthogonal input directions.
An exact Gaussian family attains both inequalities, so the constant is sharp.
[PROOF.md](PROOF.md) gives the self-contained argument and construction.
Claim type: scoped written proof with exact finite corroboration.
Independent human and formal proof-kernel review are unclaimed.

For two independent width-f Gaussian targets and one rank-two flat child,
an exact endpoint with M<=1 requires bypass matrix rank at least
`2*2^f-4`. A dense bypass of rank at most `2^f` instead requires
`M >= (1-eta)*2^((r-1)f/2)/sqrt(2)` for a rank-r child. Coordinate-matrix
rank here differs from the axis rank used to charge recursive calls.

## What changed

ToikY [#7166](https://github.com/CrocSwap/integer-mult-bounds/pull/7166),
at `6efb5d028b3212fba68edfb725608413622d6ab6`, supplies the rectangular
Gaussian adapter model and sparse-bypass amplitude obstruction. A dense
rank-one matrix can touch every entry. The new argument therefore replaces
the missing-entry test with a kernel/Frobenius-energy bound. No predecessor
scientific verifier or invoice is replayed as this contribution.

The concurrent [column-sparse approximation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19541721)
restricts each bypass column's support and uses maximum column error. This
package restricts the bypass's complex matrix rank and uses operator error.
Neither hypothesis implies the other. ToikY
[#7245](https://github.com/CrocSwap/integer-mult-bounds/pull/7245) addresses
retained whole-output consolidation and leaves changed multi-output children
open. This local necessary condition constructs no paid multi-output child.

## Evidence and reproduction

From the repository root with the tested CPython 3.12.15 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-low-rank-bypass/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-low-rank-bypass/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-low-rank-bypass
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-low-rank-bypass --check-source-history --check-modes
```

Other hosts may substitute their CPython 3.12 executable. The direct marker is
`PASS_GAUSSIAN_LOW_RANK_BYPASS`. The verifier emits a generated JSON receipt
with its interpreter version, exact coverage and all six package-file hashes.
It writes no files. The registered commands run normal and optimized Python.

Exact Gaussian-rational arithmetic checks four flat unitary children of
dimensions 2, 4, 16 and 64; 28 equality witnesses; 48 additional adapter
fixtures; two zero-bypass full-child controls; and 14 rejecting controls.
The equality fixtures use the parameter pairs `(f,r)=(1,2),(1,4),(2,2),
(2,3),(3,2)`, every `q=1,...,min(3,N/2^f)`, and `eta=0,1/2`.
The additional adapters are a declared deterministic fixture family, not an
exhaustive census of all adapters. The error fixtures have `E=eta*T`; the
universal theorem permits arbitrary E with operator norm at most eta.

The checks multiply the literal rectangular maps, eliminate the actual
bypass matrices over Q(i), verify each endpoint and both energy bounds,
and check equality in the sharp family. Rejection controls cover incorrect
rank, removed or sign-reversed bypass, changed error, invalid error domain,
changed child phase, altered adapters, dimension mismatch and invalid child
unitarity/dimensions/flatness. Checks remain active under optimized Python.

## Scope and limits

This is a local algebraic necessary condition and a sharp relaxed witness.
The bypass's rank is not its implementation price. No physical allocation,
dirty workspace restoration, routing, native adaptation, tape/precision
cost, supplier admission, new kappa or complete multiplication theorem is
established. The sharp witness uses an almost full-rank dense bypass and
does not claim a favorable recursive invoice. No Lean, Docker or full
selected-source replay is run. The selected #7000 record is unchanged.

The `coverage-law-change` card changes scope from a completed productive
split to a dense low-rank bypass obstruction. Canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Its catalogue
assessment still names #5599; `certificates/selected-result.json` resolves
the current #7000 context. The card's first metadata orientation passed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, without a scientific replay.
[SOURCES.json](SOURCES.json) pins the catalogue and selected record only as
historical provenance. The theorem and verifier import no predecessor code
or external scientific data. The exact predecessor head above is a model
citation, not a live input or a claimed source-availability certificate.

The verifier has no recursion, subprocess or external dependencies. Matrix
dimensions are capped at 64; each product has at most 64^3 scalar steps.
Python dynamically allocates bounded rational matrices and integers, a
managed-runtime deviation from fixed-allocation rules. Its fixed fixture
domain bounds operand sizes; no arbitrary-input service is provided.
Every function is shorter than 60 lines. Warning-strict normal/optimized
execution and source compilation are the applicable local diagnostics.

## Open next questions

Structured questions are in [TASK.json](TASK.json).

- Can actual eligible bypass maps be bounded by coordinate rank below the
  required floor at one complete Gaussian caller? Start by identifying the
  literal bypass input/output spaces. Charging those maps and every adapter
  remains necessary before claiming a paid gain or a complete obstruction.
- At fixed Gaussian f,r,q and prescribed M, what is the exact minimum bypass
  rank? Begin with one rank deficit greater than one. Sharpness of the
  constant above does not prove that every point on the bound is attainable.

## Credit

Credit ToikY #7166 for the rectangular Gaussian normalization; Clear1nsight
#4932/#4045/#3989 for the earlier scoped fusion boundaries; Rohan Arun #7113
and the retained Gaussian native, controller and compiler lineage. The
general matrix inequalities are elementary classical facts. The new
dense-bypass application, sharp Gaussian witness and finite verifier were
produced by Nick Petalas.
