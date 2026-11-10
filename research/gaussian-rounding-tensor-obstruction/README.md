# A sharp obstruction to native tensor consistency

**No new κ.** For every native tensor size `N=2^n`, `n>=1`, a Gaussian-integer
rounder cannot simultaneously respect global Gaussian-unit rotations, agree
with the ideal transform whenever that ideal output is already integral, and
make independent row and column applications commute. This package proves
that incompatibility for every map with the stated properties, without any
bijection, error, sum, period or implementation assumption.

The failure has an explicit universal witness. Let `U=M^⊗n`, where

\[
 M=\frac12\begin{pmatrix}1+i&1-i\\1-i&1+i\end{pmatrix},\qquad
 \alpha=(1-i)^n,\qquad
 \lambda_r=(-i)^n i^{\operatorname{wt}(r)}.
\]

Every `lambda_r` is a Gaussian unit. On the array `X=lambda z^T`, the difference
between row-after-column and column-after-row is exactly

\[
 e_0\,[\alpha(Uz-Fz)]^T.
\]

At `z=e0`, all `N` entries of the first row differ and the Frobenius norm of
the discrepancy is at least `sqrt(N)`. Nearest-even component rounding attains
that lower bound, so it is sharp for the stated class. This broad-class
attainment example is nonbijective. If `F(e0)` is nonzero, as injectivity or
sum preservation requires, the sharp squared discrepancy rises to
`2N - 2^(floor(n/2)+1)`. An explicit conservative bijection attains that
stronger bound, but its approximation error is unbounded and it fails the
exact native square. A separate [four-axis construction](https://github.com/CubeJerry/integer-mult-bounds/blob/6ea7d0886e62d6c0f53aa90ae8691dbcc61ea04a/research/four-axis-exact-square-grid/PROOF.md)
now attains the stronger fixed-witness bound at `n=4` while preserving the
sharp uniform error `sqrt(8) h`, exact native square, bijection and sum.
This does not establish a worst-case tensor-discrepancy optimum. At grid
spacing `h`, all stated discrepancy norms are multiplied by `h`.

## Why this result matters

A single rounded native block can have exact algebraic identities without
being consistent across different tensor decompositions. Ali Romman's
CrocSwap/integer-mult-bounds#6509 already records a concrete four-coordinate
noncommutation example. This result identifies a general incompatibility of
three precisely stated interfaces, for all `n>=1`, and gives the exact defect
instead of only another example or an unsuccessful search.

The proof is short and structural. The vector `lambda` has unit entries but
`U lambda=alpha e0`; also `alpha U` has only unit entries. Exactness on integral
ideal images determines each column action, while global unit covariance
determines each row action. Comparing the two orders forces the displayed
defect identity. At the basis input, its entries are units minus multiples of
the nonunit `alpha`, so none can vanish. [PROOF.md](PROOF.md) gives the complete
argument and all quantifiers.

This is a boundary for a proposed native rounding interface, not a
counterexample to the selected multiplication theorem. Applying it to a
supplier requires showing that the actual caller imposes all three
requirements. The selected record and all five inherited assumptions remain
unchanged. No construction, source profile, paid recurrence or κ is changed.

## Reproduction and exact checks

From the repository root, using Python 3.12 and its standard library:

```sh
python3 -W error -B research/gaussian-rounding-tensor-obstruction/verify.py
```

Expected status: `PASS_GAUSSIAN_ROUNDING_TENSOR_OBSTRUCTION`.

The checker constructs the native matrices by tensoring the original
`2 x 2` matrix with exact rational Gaussian arithmetic. It compares them
against the closed denominator and unit-column formulas for `n=0..6`.
It evaluates both complete nonlinear fiber orders on twelve fixtures for
`n=1..4`, as well as one signed large-word fixture at scale `2^257` (258
component bits). It checks 84 global-phase cases, 56 integral-image cases,
the sharp nearest-even witnesses, and the `n=0` identity boundary. The stronger
attainment construction is checked for `n=1..6`, with exact squared defects
`2,4,12,24,56,112`, literal inverse compositions, complex sum, global phase
and integral-image exactness. Four additional full fiber evaluations check
those conservative-bijection witnesses for `n=1..4`.

Seven controls address material hypotheses or failure modes:

* The identity map remains integer-valued, phase-covariant and commuting,
  but fails exactness on integral ideal images.
* The ideal linear transform commutes on rational Gaussian arrays but fails
  the required integer codomain.
* Coordinatewise floor rounding preserves integral ideal images but fails
  global unit covariance. It is not claimed to commute under relaxed
  assumptions.
* Omitting the `alpha/conjugate(alpha)` phase from `lambda` fails the exact
  denominator identity.
* The asserted zero tensor defect is rejected on the explicit witness.
* A strictly larger universal lower bound is rejected by the nearest-even
  example that attains the stated bound.
* Swapping only part of a Gaussian-unit orbit is rejected for breaking phase
  covariance in the sharper bijective attainment construction.

Normal and optimized Python modes use the same explicit checks; no
proof-relevant Python `assert`, floating-point approximation or tolerance is
used. The finite checks support the proof; they do not replace the all-`n`
algebraic argument. There is no bounded search whose failure is being called
an impossibility theorem.

Registered metadata and replay commands are:

```sh
python3 -B scripts/research_package.py --package research/gaussian-rounding-tensor-obstruction --check-only
python3 -B scripts/research_package.py --package research/gaussian-rounding-tensor-obstruction
```

Executed under CPython 3.12.14: metadata/source-pin checks and the registered
ordinary/optimization-mode replay passed. The independent mathematical review
in [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md) derives the all-axis phases,
rank-one identity, both sharp bounds, attaining maps and hypothesis boundaries
without treating finite tests as a universal proof. It is a separately assigned
AI review, not human review or proof-kernel formalization.

The replay needs no predecessor checkout, external service, solver, generated
lookup table or third-party Python package.

## Scope and source pins

Global unit covariance means multiplying the **whole input vector** by one
of `1,-1,i,-i`. The theorem does not assume separate coordinate phases.
Exactness on integral ideal images means `F(z)=Uz` whenever `Uz` lies in the
Gaussian lattice. The proof actually uses that condition only on the two
explicit families `lambda Z[i]` and `alpha Z[i]^N`. Row and column actions use
the same map independently, with no shared state and a fixed coordinate order.

The theorem does not prohibit stateful or enlarged representations, different
row and column maps, approximate consistency, or changes to one of its
hypotheses. It also does not refute exact same-block square/fourth-power
identities. The `n=0` case is deliberately excluded: there the native map is
the identity and commuting integer implementations exist.

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) retains the exact original `uniform-transfer-audit`
card and records the assigned, narrower obstruction scope. The predecessor
#6509 proof is pinned at head
`a4173e810c4d34a1d13b9745af123ad0ec6cfed5`, path
`research/conservative-gaussian-rounding/PROOF.md`, Git blob
`b7047476aaa5e2bb149c92a8a40a9b2ab444ef73`. Its concrete example is context,
not a runtime dependency or a premise required by the new proof. This
package does not assert that every predecessor rounder satisfies both
hypotheses. [SOURCES.json](SOURCES.json) records exact provenance.

The source-history preflight needs full Git history; this workspace is
shallow, and no ancestry-certification pass is claimed. All theorem statements
and executable evidence are package-local and require no pending Git object.

Prepared by @CubeJerry (Jerry Chen) with substantial OpenAI Codex assistance.
The four-axis denominator argument arose during separate exact-square work;
the lead supplied and checked the all-axis Gaussian denominator extension and
sharp nearest-even attainment. Ali Romman is credited for the earlier
conservative-rounding noncommutation example. All new work is Apache-2.0.
No human proof audit or proof-kernel formalization is claimed.

## Open next questions

1. **Which exactness contract is required at an actual native caller?**
   Audit one pinned caller's uses of the two explicit families
   `lambda Z[i]` and `alpha Z[i]^N`, together with global unit covariance and
   independent fiber order. This would determine whether the obstruction
   applies there; the present theorem does not infer those requirements from
   informal terminology.
2. **Can a useful representation relax one condition at a complete paid cost?**
   Start with a stated mechanism, such as retained rounding state or a relaxed
   integral-image contract, and prove its replacement composition law before
   pricing every new state, restoration and routing operation. Existence,
   error quality and a favorable complete recurrence are all still open.
3. **Which other dimensions admit bounded-error, exact-square attainment?**
   The companion four-axis construction now settles `n=4`: its certified
   `F(e0)=e3` gives squared discrepancy 24 while preserving sharp uniform
   error and the exact native square. The precise source is pinned in
   [SOURCES.json](SOURCES.json). Other dimensions and additional caller
   contracts remain open here. Start with a specified dimension and error,
   reversal and square requirements; the all-dimension piecewise attainer
   in this package still has unbounded error. Fixed-witness attainment does
   not optimize worst-case tensor discrepancy.

The structured relevance and blockers are in [TASK.json](TASK.json).
