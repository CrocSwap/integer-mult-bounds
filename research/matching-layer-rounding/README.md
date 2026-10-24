# Serial rounded matching layers preserve the data grid and coordinate width

Prepared by `apoursh` with substantial OpenAI Codex
assistance. Apache-2.0. This is a scoped written proof and source-execution
audit; independent human or proof-assistant acceptance is not claimed.

## Contribution and exact interface

[PR4976](https://github.com/CrocSwap/integer-mult-bounds/pull/4976) proves the
sharp sqrt(2) interpolation bound for exact operators inside matching layers.
Its extra-data-bit implication explicitly retains the predecessor's
rounding-event count. This package checks that premise against the actual
rounded executor, [exact.py](../rational-unitary-fft/exact.py), and distinguishes
Euclidean amplitude from the size of each stored coordinate.

For this executor, reordering the disjoint gates within a layer preserves its
rounded endpoint exactly. There is still one error **vector per original
layer**, with the original number of scalar rounding operations. Every stored
state between output writes is a coordinate splice of the adjacent rounded
endpoints. Consequently the existing terminal error budget, fractional grid F,
and signed component width I remain sufficient. No extra fractional or integer
bit is forced solely by serializing these gates or inspecting their output
writes. A Euclidean bound at the new cuts may still require sqrt(2).

This supplies an explicit source-bound explanation of a valid but implicit
step in PR4205's layerwise analysis. It neither disputes PR4976's conservative
extra-bit implication nor reclaims its interpolation theorem. Complete-layer
conditioning and the local arithmetic model remain explicit premises.

## Execution contract and theorem

Fix a positive integer N of complex coordinates, an integer F >= 1, and
u = 2^(-F). Inputs are on
the componentwise u-grid. Each layer is a finite matching of valid square
one- or two-coordinate linear gates with stored Gaussian-rational coefficients;
gate supports are disjoint. Each gate snapshots its input, evaluates its entire
output exactly, then rounds each real and imaginary output component once to
the nearest u-grid point, with halfway cases toward +infinity. Untouched
coordinates are unchanged. Products and partial sums are not rounded.

Let L_j be the exact stored-coefficient layer operator and y_j its rounded
endpoint. If the layer touches m_j coordinates, then:

1. Any permutation of whole gates has the same rounded endpoint and the same
   m_j complex-output rounding operations (2m_j real roundings).
2. The realized residual e_j = y_j - L_j y_(j-1) is supported on those
   coordinates. Each real/imaginary residual is at most u/2 in magnitude, so

   ```
   ||e_j||_2^2 <= (m_j/2) u^2,     ||e_j||_2 <= N u.
   ```

3. At any cut after completed output writes, let E project onto the written
   coordinates. The actual stored state is

   ```
   y_(j,E) = (I-E) y_(j-1) + E y_j
           = [(I-E) + E L_j] y_(j-1) + E e_j.
   ```

   This includes a cut between the two output writes of one gate. It does
   not require E to commute with L_j or the cut map to be invertible.
4. Every stored component is an endpoint component on the original grid.
   If both endpoint Euclidean norms are at most A, each stored real/imaginary
   component is at most A, while the Euclidean norm is at most sqrt(2) A.

The same splice identity holds for the exact trajectory x_j and for the
error y_j-x_j. Errors may depend on the data; no independence or unbiasedness
assumption is used.

### Proof and binding to the retained executor

In `exact.apply`, a valid layer enforces disjoint supports. The executor copies
all inputs of a gate into `before`, computes the complete list `outputs`, and
only then enters the rounding/write loop. Earlier gates cannot have changed
this gate's inputs. Each gate therefore sees the same local input as simultaneous
evaluation from the layer's initial state. Its rounded outputs do not depend
on the order of the other gates.

Each output is rounded once. `round_q` computes `floor(value/u + 1/2)*u`, so
each real residual is at most u/2, including signed ties. An untouched
coordinate has zero residual. Summing the squares of the 2m_j real residuals
proves the stated bound; sqrt(m_j/2) <= N for N >= 1 gives the source's
conservative N u allowance.

At a write cut, each coordinate has either its initial value or its unique
final rounded output. All outputs of a gate were computed before any were
stored. This proves the splice even within that gate's output-write loop,
and proves the component/grid bounds. Adding squared norms on complementary
coordinate sets gives the Euclidean bound. Subtracting the analogous exact
state identity gives the error splice.

For D layers the rounded trajectory is exactly

```
y_j = L_j y_(j-1) + e_j,    j = 1,...,D.
```

At a cut within layer j, there are j-1 completed residuals and the projected
current residual E e_j: at most D residual vectors, not D+1 or the number of
gates. This groups the actual scalar roundings; it neither replaces them by
one scalar rounding nor evaluates errors on the unrounded trajectory.

## Consequence for the Full precision contract

Retain [FULL-PROOF.md](../rational-unitary-fft/FULL-PROOF.md), equations
(14)-(18), as conditional inputs. Let K = K_phys bound exact stored prefixes,
suffixes and their inverses at **complete physical-layer boundaries**;
D <= D_*; ||y_0||_2 <= R; and ||T_hat-T||_2 <= e for the completed stored
operator and intended target. Bounds only at completed atomic calls are
insufficient for this application.

Expanding the realized residual recurrence, terminal suffixes cost at most K
and complete-boundary segments at most K^2. Hence

```
||y_D - T y_0||_2 <= e R + D_* K N 2^(-F),
||y_j||_2 <= A := K R + D_* K^2 N 2^(-F).
```

These are the original terminal-error and completed-layer amplitude allowances.
The original F remains sufficient because neither the rounded endpoint nor the
number of grouped layer residuals changes.

The write-cut splice retains the **component** envelope A. Thus the source's
signed word allocation

```
I = max(1, ceil(log2(max(1,A)))) + 2
```

remains sufficient with the same F. Feeding the larger Euclidean envelope
sqrt(2)A into this component-width formula is unnecessary. A consumer needing
a vector-norm radius at a new cut must still use its appropriate larger radius.

Apply the same argument to the separately executed stored-inverse program
under its own input grid/radius, complete-layer bounds, and stored-to-intended
inverse approximation allowance. The forward endpoint defect alone does not
supply the inverse defect bound. Rounded forward execution is not claimed to
be exactly reversible.

### Component width does not imply partial invertibility

A swap gate sends (0,1) to (1,0). After its first output is stored, the state
is (1,1): Euclidean norm sqrt(2), but every component remains at most one.
The corresponding first-write linear map has identical rows and is singular.
Thus a zero-loss Euclidean assertion or an inverse operator claim would fail
at arbitrary output-write cuts.

Exact gate-product/sum temporaries, coefficient preparation, tape movement,
the predecessor's all-size conditioning proof and supplier admission remain
outside this audit. The source uses unbounded exact rational local arithmetic;
a bounded-word implementation still needs its separate temporary/local-arithmetic
contract. No selected exponent changes.

## Independent finite evidence

`verify.py` authenticates its declared source closure and compares the actual
rounded executor with an independent simultaneous-layer oracle and independent
rational tie rounding. Fixtures target complex nonunitary gates, signed ties,
idle wires, gate permutations, actual FFT/shear gates, and residuals evaluated
on the rounded trajectory. Controls distinguish the snapshot, event-count,
disjoint-support and component-width premises. The written proof is quantified;
finite checks corroborate source binding and selected failure modes.

The bounded suite covers 10 fixtures, 145 gate-permutation orders, 607 rounded
gate-prefix checks, 83 observed coordinate writes and seven controls. Two
complex inputs exercise the actual retained n=2 Builder shear (12 layers,
20 gates, 32 coordinate writes per input), with nonzero realized residuals.

To inspect write cuts, the checker adds a single snapshot callback immediately
after the source assignment `state[i] = value`. Removing that callback restores
the exact original function AST; the output records both AST hashes. Observed
and unmodified execution must agree on the final vector and every source
tracking statistic. The callback only records immutable snapshots; the checker
then compares all writes with an independently evaluated synchronous oracle.
The source's arithmetic and checks are unchanged.

Registered normal and optimized checks passed locally on CPython 3.12.14;
their computed JSON results agree byte for byte. With CPython 3.12 and the
standard library:

```
python3.12 -I -W error -B research/matching-layer-rounding/verify.py
python3.12 -I -O -W error -B research/matching-layer-rounding/verify.py
python3.12 -B scripts/research_package.py --package research/matching-layer-rounding
```

After committing:

```
python3.12 -B scripts/check_research_commit.py --package research/matching-layer-rounding --check-source-history
```

Registered replay, committed export and Git-free direct replay are separate
checks; none establishes the retained all-size premises or human acceptance.

## Scope, overlap and credit

Base `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority revision 7.
The original local interpolation draft was preserved separately after fresh
overlap revealed PR4976. This contribution narrows to rounded execution and
component width. PR4976's operator theorem and its existing independent review,
PR4977's Full allocator substitution, PR5018's Gaussian allocation and PR4829's
sharp exact dirty-shear envelope are credited existing work.

The October 23 entry search covered all 6,918 upstream local note records plus
the new draft and targeted live PR searches for rounded/disjoint gates,
serialization, event counts and `exact.py`. Remote discussion pagination and
unpublished work were not exhausted; the terminal helper had no remote cache.
No exhaustive novelty claim follows. TASK.json records scope/freshness.
The related canonical investigation is
[Discussion #4202](https://github.com/CrocSwap/integer-mult-bounds/discussions/4202).

Credit Jose Manuel (`jmbarrancoml`) for the exact rounded kernel, rational FFT
compiler and Full precision contracts; Vlado Vojdanovski for the schedule;
Chafik Boukhalfa for certified phases; Brian (`JoyboyBrian`) for PR4755/4976's
cut contracts and PR4977/5018's allocator follow-ups; James Reed for the existing
independent PR4976 review; Nick Petalas for the exact dirty-shear refinement;
and Cinna Davis and the retained lineage for the all-size caller. Disjoint-map
commutation and coordinate splicing are elementary; the contribution is their
explicit runtime/precision implication and independent execution controls.
Source notices remain unchanged.

## Open next questions

Can a concrete bounded-word implementation of one actual two-coordinate gate
deliver this final-output rounding contract within the predecessor's temporary
budget? Start with its multiply/add/round order, including signed ties and
intermediate product widths. This matters for transferring stored-state bounds
to physical execution; local arithmetic and temporary-storage specifications
remain separate premises.
