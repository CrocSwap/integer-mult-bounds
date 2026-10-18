# Independent finite native binding review

This review concerns the literal `inputs/CIRCUIT.json` from PR2445 at
`6def43ad673b91dbd491389964d1dcd059bf2ac2`, SHA256
`c34d94128decc426e7528302ab2570967293a1b293f184fdd89fd376addd61f9`.
It checks an exact forward extension of the retained P104 channel, conditional
on its existing private-copy/discard model. It does not change the correction
construction or claim a multiplication exponent.

The package is retained as `p104-two-target-native-independent` so PR2458's
checker coexists with the separately authored PR2454 package at the original
`p104-two-target-native` path. Its literal circuit, native certificate, exact
mathematical receipt and predecessor source pins are byte-identical to the
original PR2458 head `3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6`.

`check.py` does not import `compile.py`, the Clifford compiler, or the PR2445
producer. The existing independent
[`check_native.py`](../p104-native-channel/check_native.py) is reused explicitly
to validate the inherited channel, physical label isometry and intrinsic
endpoint adapters. Its independently written
[`native_verify.py`](../p104-native-channel/vendor/native_verify.py) supplies the
exact signed-Pauli and Gaussian dyadic operator interpreter. This reuse is not
claimed as a second implementation of those routines. The insertion binding,
chart consistency, new full-program replay and controls are new independent
checks. The historical channel's own proof and attribution remain in
[`PROOF.md`](../p104-native-channel/PROOF.md) and
[`README.md`](../p104-native-channel/README.md).

## Exact transport obligation

The frozen isometry maps compressed labels into a physical nine-dimensional
binary space. The inherited checker reconstructs the 120 doubled-coordinate
E8 root lines, inverse compressed Gram form and orthonormal basis, and checks
all 14,400 physical pairings. The new certificate must use exactly that same
isometry. Each literal old/new frame is mapped through it.

For every span, the checker constructs its highest-pivot reduced basis by
enumerating at most 512 elements and taking the minimum element with each
occurring highest bit. This differs from the compiler's elimination algorithm.
Every actual physical basis in both native certificates must equal that
canonical representative. Comparing spans alone would leave the possibility
of inconsistent chart representatives; comparing the canonical basis tuples
against the inherited recipes and adapters closes that gap.

Write `Gamma(A)` for the retained physical frame operator. For each directed
pair `A -> B`, both recipes must have the positive rank
`abs(dim(B)-dim(A))`, the spans must be nested, and the interpreter proves

```text
forward = Gamma(B) Gamma(A)^*
adjoint = Gamma(A) Gamma(B)^*.
```

The comparison checks all 18 signed Pauli-generator images and an exact
Gaussian image of the zero basis vector. For these Clifford operators, the
signed Pauli action fixes the operator up to scalar phase; a nonzero state
column fixes the phase. Thus this is a full 512-dimensional operator check,
not merely an unsigned symplectic check or a floating-point sample. The
retained checker uses the same criterion for inherited transports and endpoint
adapters; this replay does not additionally enumerate all 512 columns of its
eight private descents (`all_private_copy_gaussian_columns` is zero).

Explicitly, if the compared unitary operators are `U` and `V`, equality of
their signed conjugations implies `V* U` commutes with every coordinate `X`
and `Z`. Commuting with all `Z` makes it diagonal in the computational basis;
commuting with every `X` makes all diagonal entries equal. Hence `U = c V`.
The exactly compared nonzero vector `U|0> = V|0>` forces `c = 1`. This argument
depends on both recipes being the admitted invertible Clifford primitives,
which the recipe-domain checks and interpreter validate.

The occurrence audit binds all 236 added transports, without duplicates or
omissions, to insertion/event indices in the literal circuit. The invoice is
`{1:142, 2:16, 6:18, 7:60}`, with added rank mass 702. There are 161 distinct
directed pairs and 322 checked orientations. None of those 161 directed
canonical pairs occurs in the 740-pair inherited certificate; this is a
comparison with that one retained certificate, not a general novelty claim.

## Complete forward composition

Give every one of the 358 boundary inputs an independent formal column:
104 sources, 104 targets and 150 dirty helpers (72 inherited, 78 added).
For every live register `r`, the checker maintains the invariant

```text
physical_value(r) = Gamma(frame(r)) sum_j row[r,j] z_j,
```

where each `z_j` is an arbitrary 512-coordinate complex input array and every
row coefficient is an exact rational dyadic. A verified transport changes
the frame and leaves the row unchanged. A scalar ADD is accepted only when
the actual canonical physical charts of both registers and its literal
common frame agree, then performs exact rational row addition.

The complete stream is the 496-event insertion at cut zero, all 4,058 inherited
events, and the 180-event insertion at cut 4,058. No source/query events are
removed from the replay. There are 3,064 scalar ADDs, 1,646 transports and
eight each of private initialization, COPY and discard: 4,734 events total.

Private storage follows the inherited contract precisely. `C` must be absent
before initialization; COPY requires a zero destination and a common physical
chart. Each lifetime copies the prescribed `Q0` through `Q7` source and closes
by discarding the owned copy in its prescribed chart. Discard does not require
its copied row to vanish, and this work does not reinterpret it as reversible
zero uncomputation. `C` is not an arbitrary dirty boundary input.

Every one of the `358 * 358 = 128164` endpoint coefficients, including zeros,
is compared explicitly, with the expected ordinary Gram entries reconstructed
from doubled root coordinates. All 358 final charts are also compared. The
result is

```text
Y0 = y0 + x0,                  Y1 = y1 + x1,
Yt = yt + (1/2) sum_s G[t,s] xs for t = 2,...,103,
Xs = xs for all 104 sources,
Hr = hr for all 150 dirty helpers,
```

as logical values in their recorded final charts. Source and dirty-helper
charts finish at the full Fourier frame. Their physical arrays are therefore
not asserted to equal their initial physical arrays. The retained target exit
adapters remain valid because the corresponding target final charts are
unchanged. Their intrinsic conversion carries no additional positive child.

The canonical full coefficient enumeration has SHA256
`173270a37d06a06538083bcfcd4e4b73ad13f295e28d527e851cb36a475f928a`.
The digest is a compact reproducibility receipt after explicit coefficient
equality; it is not the equality test itself.

## Defect-sensitive controls and coverage

Ten corrupted inputs must reject at the named mathematical predicate:

- Wrong forward global phase and wrong adjoint global phase.
- A missing occurrence and a duplicated occurrence.
- A wrong paid rank and a wrong physical root label.
- Omitted added dirty compensation and omitted added capture cleanup.
- Omitted inherited gather compensation and omitted inherited query cleanup.

The four scalar controls set a named ADD coefficient to zero without changing
transport indices, so endpoint coefficient equality must detect them. The
global-phase controls leave the signed Pauli action unchanged. The rejection
harness checks the reason and raises unexpected acceptance outside its caught
exception path. `run_controls` is exposed so a test can delete the exact phase
predicate and verify that the control suite then fails.

Two equivalent inputs accept: reversal of every supplied correction frame
basis and reversal of the certificate edge/occurrence ordering. These controls
exercise semantic invariance. File-byte provenance is checked by `replay` and
the package wrapper separately, rather than used to reject the semantic
mutations before their intended predicate is reached.

## Source execution and cache regression

The original wrapper hashed the retained Python files but loaded them through
ordinary importers. A matching timestamp cache or unchecked-hash cache can
therefore execute different code even under `-I -O -B`; the last flag prevents
cache writes, not cache reads. This was a source-binding defect, not a failure
of the original finite matrix identity.

`source_exec.py` now retains the exact bytes that passed each input hash. New
package modules and the optional Clifford compiler are compiled from source
bytes directly. The unchanged retained checker and its transitive interpreter
load inside a fresh private tree written only from those authenticated bytes.
No existing cache is copied there. After loading, only the retained pure
`validate` and `roots` functions are used, and the new replay reads data from
the authenticated snapshots. No predecessor source or process-wide importer
is changed.

The behavioral tests seed executable timestamp and unchecked-hash caches for
the local source helper/checker, the retained checker/interpreter and the
optional Clifford compiler. A standard-import probe first demonstrates that
the defective interpreter cache really executes under the test flags. The
correct wrapper then accepts the valid fixed certificate, regenerates its full
payload and preserves all files despite those caches.

For each cache format, the test also changes a rank-seven forward recipe's
global phase by one, multiplying its operator by i, and updates only the
certificate hash in the expected receipt. The seeded interpreter cache keeps
signed Pauli comparisons but skips seven-child exact phase comparisons, the
same mathematical failure mode as the review witness. The corrected default
wrapper ignores that cache and rejects at `added forward edge: exact global
phase`. The test restores all data after the control. The original ten
semantic fault controls, two equivalent presentations and explicit
phase-predicate deletion control remain required.

Reproduction from the repository root:

```sh
python3 research/p104-two-target-native-independent/check.py
```

The first complete local replay passed all operator, coefficient, chart and
control checks. The receipt records the exact scope; this is a finite exact
arithmetic computation with a written composition invariant, not a formal
proof-kernel artifact.

The 16 October 2026 source-execution revision passed both declared commands
(`verify.py --regenerate` and `test_verify.py`, each with `-I -O -B`) on
CPython 3.12.12 and 3.14.6, including all eight behavioral groups. Package
metadata/source-pin checks passed. The four retained evidence files and all
six runtime inputs were compared byte-for-byte with their original pins.
Hosted CI and the selected-frontier cold replay are separate checks.

## Remaining obligations

Verifying both adjoints of each added transport does **not** verify a complete
backward or inverse-transpose program with COPY and discard. No such program
is supplied here. Physical prefix denominator/height bounds, recursive child
implementation, chronological global helper owners and all-size admission
also remain open. Only two of the 104 target channels are corrected; the
other 102 retain `G/2`. The 702 added rank mass is a local complete transport
invoice, not a complete recursive supplier cost or an exponent improvement.

Prepared by Ross Richardson with substantial OpenAI Codex assistance. The
compiler and this checker were developed by separate agents with disjoint
file ownership; the checker used the fixed emitted certificate and retained
independent interpreter, not compiler calls. New work is Apache-2.0, with
predecessor attribution and notices retained.
