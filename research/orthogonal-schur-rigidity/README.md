# Orthogonal Schur residuals cannot change under sector padding

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written proof with exact finite corroboration. For commuting
orthogonal projections with prescribed invertible leading blocks A,B and
product block H, the whole noncommuting Schur residual pair is fixed up
to simultaneous unitary equivalence. Enlarging any of the four joint
sectors adds only commuting scalar summands.

Put T00=I-A-B+H, T10=A-H, T01=B-H and T11=H. Existence is equivalent to
positivity of all four effects and ambient dimension

```text
n >= n0 = rank(T00)+rank(T10)+rank(T01)+rank(T11).
(S,Z) = one fixed core pair plus copies of (0,0), (1,0), (0,1), (1,1),
        up to a simultaneous unitary change of residual coordinates.
```

In particular the commutator rank and every nonzero commutator singular
value are independent of padding. There is a single feasible rank at
every admitted dimension in this orthogonal class. This closes off
ambient padding as a way to change the rank while retaining these
compressed effects and self-adjointness. [PROOF.md](PROOF.md) gives the
existence construction, core isometry and Schur decomposition.

The minimum positive-operator dilation and its Gram-isometry argument
are classical. The contribution is the explicit Schur-interface
restriction and its consequences. No literature-wide priority is claimed.

## Scalar consequence

For d=1, A=a>0, B=b>0, H=h, set c=(a-h)(b-h)/(ab). The exact
Schur-commutator norm is sqrt(c(1-c)); its rank is two if
0<h<min(a,b) and zero otherwise. At a=1/2, b=2/3, h=1/6 the norm is
exactly 1/2 and the core dimension is three. The rational fixture realizes
it in dimension eight and checks the core by exact rational coordinates.
Existence at minimum dimension is over R or C; rational orthonormal
coordinates at that dimension are not asserted.

At a=b=h=1 every orthogonal residual pair commutes, regardless of
padding. Krzysztof Wojt's unrestricted maximal-rank theorem permits
rank two at dimension five with these same compressed scalars.
Orthogonality is therefore a material restriction on that interface.

## Evidence and reproduction

The standard-library verifier checks 267 explicitly generated candidates,
rejecting 130 for singular pivots and admitting 137. These cover all
four-sector dimension profiles in ambient dimensions two through four
under two fixed rational orthogonal conjugations, with pivot sizes one
and two when available. Nine further profiles in dimensions five through
seven use pivot sizes one through three. These are finite fixture
families, not a census of all orthogonal matrices or effect triples.

For each admission the checker computes literal Schur complements,
extracts the positive Gram effects, removes the inactive sector spaces,
and checks the complete ordered residual decomposition. Their
commutator ranks have histogram {0:110, 2:25, 4:2}. It also checks:

- 93 scalar norm/rank identities by full rational commutator products.
- 32 padded and rotated realizations, with three seed cores at each of
  pivot sizes one and two and two seeds at size three. All four padding
  sectors occur. Explicit Gram isometries fix the observed coordinates
  and intertwine both original projections and both Schur residuals.
- The separate half-norm fixture and its dimension-three core.
- Eight controls for idempotence, self-adjointness, commutation, singular
  pivots, pivot sizes and indefinite effects.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/orthogonal-schur-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/orthogonal-schur-rigidity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/orthogonal-schur-rigidity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/orthogonal-schur-rigidity --check-source-history
```

Any CPython 3.12 executable may replace the displayed path. The direct
marker is PASS_ORTHOGONAL_SCHUR_RIGIDITY. Its JSON receipt is generated on
stdout and binds all seven package files by SHA256. Direct replay writes
nothing. Both registered commands have 120-second caps. Local checks use
CPython 3.12.15; hosted execution is reported separately in the PR.

## Scope and sources

The base is canonical main e54523517d0f03e58352e647c403a5af3e525a57,
priority revision eight and selected #7000. The binding-only orientation
passed. This changes the formal-interface-lemma card to a written
algebraic side theorem. No selected assumption is discharged, and no
selected-frontier change or new kappa follows.

Credit Krzysztof Wojt / krzysztofwojt
[#5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128) for the
arbitrary-pivot interface, its four sector compression products, its
maximal-rank theorem and its smaller-rank question. Nick Petalas
[#6031](https://github.com/CrocSwap/integer-mult-bounds/pull/6031) and
apoursh [#6053](https://github.com/CrocSwap/integer-mult-bounds/pull/6053)
already settle the unrestricted oblique rank/dimension trade-off. The
new work restricts realizations to orthogonal projections and determines
the entire residual core. Their scientific verifiers are not imported
or replayed. The ordered Schur and sector lineage credited there,
including ssafwann, Ryanson Jonathan and lee-phys, keeps its credit.
[SOURCES.json](SOURCES.json) binds their proof/README texts as provenance;
the standalone mathematical checker has no external live inputs.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595337)
and [TASK.json](TASK.json) record scope and overlap. Targeted live PR
searches, active Discussions, recent handoffs, main README searches and
local claims were checked. The cached scan covered 826 open PRs and
7,444 Discussion records; sparse local coverage was incomplete.
Arbitrary diffs and unpublished work remain outside coverage.

The proof covers finite real and complex Hilbert spaces, exact
compressions, commuting orthogonal projections and invertible pivots.
The finite checks use real rational matrices only. No singular-pivot,
indefinite-metric, approximate or rational-minimum-dimension theorem is
claimed. Physical preparation, native realization, dirty restoration,
precision, stock, compiler, header frequencies and outer transfer remain
separate. No actual selected caller is bound to this orthogonal contract.
Independent human and formal proof-kernel review are unclaimed. No Lean,
Docker, predecessor scientific suite or selected cold replay was run.

## Open next questions

1. Does one actual header or native boundary impose simultaneous
   orthogonality for its projectors? Pin its inner product and exact
   entrance/exit bases before applying this result. The source-bound
   self-adjoint contract and complete physical costs are missing.
2. How stable is the residual core under perturbing the positive
   effects? Start on a fixed-rank stratum with positive lower bounds
   for A and B. Rank changes and small pivots prevent applying an
   unqualified uniform continuity bound.

## Implementation bounds

The checker has no recursion, subprocesses, network or generated code.
All loops range over fixed fixtures or matrices capped at 32 rows and
columns, including augmented inverses; admitted ambient dimensions are
capped at fourteen. All functions fit within sixty physical lines.
Explicit exceptions remain enabled under optimization. Receipts read
the fixed seven package files. Python warning-strict normal/optimized
execution and in-memory AST compilation supply diagnostics; no separate
static analyzer is installed for this package.

Managed rational arithmetic and collection allocation are a deviation
from fixed-allocation rules. Fixed fixture counts, bounded matrix sizes
and bounded rational seed vectors bound live storage and arithmetic;
runtime allocations are not instrumented. Ordinary Python iteration
and library dispatch are used with fixed visible targets. The explicit
local import path supports isolated Python execution. Larger or
externally supplied matrices require a new resource assessment.
