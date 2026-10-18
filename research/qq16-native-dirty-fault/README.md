# A native binding for the QQ16 dirty-helper fault

**Scoped mathematical audit; no new supplier or κ.** Arham Tahir's
[PR2995](https://github.com/CrocSwap/integer-mult-bounds/pull/2995), head
`8ba0358b62edbeb16a0842473500c468d8c0759b`, exhibits a restoration-preserving
fault in F0's scalar projection but leaves its native binding open. This
package closes that binding **on its particular witness family**, using exact
Gaussian-dyadic vectors and the actual serialized native recipes.

The resulting native example still has maximum data error **`4 u T`** from
one allowed completed ADD defect, with all 480 helpers restored exactly and
all eight private fields zero. Here the original data norm is one and T is
the initial norm of one borrowed helper. Thus the permissive local relative
ADD contract, even with exact helper restoration, cannot guarantee a producer
error bound depending only on the original data. The scalar witness, its
52-field response and its necessary precision reserve are credited to PR2995;
the new evidence is their native realization and restricted tensor lift.

This is **not a failure of an implemented rounding algorithm**. Correctly
rounded exact cancellation may produce zero at the marked instruction.
An exact common-grid ADD implementation also avoids the injected defect.
The result rules out an implication from the stated permissive specification,
not every numerical implementation or multiplication algorithm.

## Exact statement

Use the reviewed `programs.F_0` in the pinned
[joint-query certificate](../joint-query/certificate.json.gz), with its
retained local native core and completed child operators. At one completed
ADD `d <- d+c s`, permit a destination error e satisfying

```
||e|| <= u (||d|| + |c| ||s||),          u > 0.
```

Norms are payload Hilbert norms, maximized over data fields and cover owners,
as in [Nick Petalas's PR2965](../qq16-producer-defect-transfer/README.md).
All other completed operations are exact. For each positive common tensor
depth λ, let χ be the unit constant payload, uniform across cover owners.
Choose physical input `L112=χ`, `L359=Tχ`, all other fields zero, with T>0.
These are legal local field values under the retained independent-field and
full-cover access contract; no finite grid or global supplier is asserted.

At expanded, unfiltered, zero-based event **24438**, the literal instruction is

```json
["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]
```

The actual native operands are `(-4Tχ,Tχ)`. After their exact cancellation,
insert `e=8uTχ`, saturating the allowance. The complete native continuation
has error `±4uTχ` in exactly 52 data fields and zero error in every helper and
private field. The ideal execution returns this chosen input unchanged.
Thus every physical helper is restored on this witness, including the dirty
helper L359; this is not a statement that arbitrary helper inputs are always
returned to their original physical bits.

The fault is at **one instruction site**, uniformly over the addressed
payload components/owners. It is not a single hardware-bit or single-address
fault. Such coherent, state-dependent defects are allowed by the stated
completed-ADD contract. For this constant input the same injection also
satisfies the corresponding pointwise component-relative inequality.

No finite C can therefore make that specification imply data error at most
`C u H` for all dirty inputs when H bounds only the original data: set H=1
and choose T>C/4. To guarantee PR2965's sufficient F0 tolerance
`H 2^(-beta-8)` against every such allowed defect requires at least

```
u <= (H/T) 2^(-beta-10).
```

This repeats PR2995's necessary reserve with a native justification. It is
neither a sufficient precision bound nor an optimal reserve.

## Why the scalar witness lifts

The general common-frame conjugation argument is predecessor work, including
[the selected native lift](../selected-centre-native-lift/README.md) and
`Stream.conj_matrix`; this package does not claim it as new. Only the vector
identities needed by the present witness are checked here, rather than all
columns of every native operator.

Let `1` denote the unnormalized 512-entry constant vector and let `T_f` be
the canonical operator for the stored ordered frame f. Define `v_f=T_f 1`.
Both frame 0 (identity) and frame 1 (the full coordinate line product) give
`v_f=1`. Other frame vectors need not be constant. In particular, ignoring
the entry adapter at source port 39 is a rejecting control.

The checker reconstructs all 1,004 frame vectors from the published
canonical-frame formula. For each of the 2,880 distinct child recipes used
by the forward core, with its exact global phase and normalization, it checks

```
(L F_r R) v_old = v_new.
```

It also checks all 224 source/target adapter identities on these vectors in
both directions, every core ADD's source and target frame, all 3,486 child
occurrences, and the complete entry/exit conversion multiplicities. Serialized
monomials use `D, P, X, phase` order. Their quadratic form reads each strict
upper-triangle coefficient once; the old symmetric representation and the
new upper-triangle representation have the same meaning. No phase is dropped.

For the three scalar trajectories (data basis L112, dirty basis L359, and the
unit error injected at the cut), every wrapped helper is zero at both its
residual entrance and exit. All **1,440** such boundary values are checked.
Its actual inverse right/left monomial therefore maps zero to zero. This
avoids assuming that a residual helper's initial and final gauges coincide.
The only nonzero initial helper, L359, has ordinary endpoints `(0,1)` and
both fix the constant vector. Private CLEARs produce zero in their declared
frames and cannot erase ordinary helper errors.

Induction through the literal core now gives `physical_i=a_i v_frame(i)`
between conversions, where the a_i follow the scalar word. At event 24438
both operands have frame 1, so their vectors really are constant. The same
induction applies to the injected constant error. Source and target endpoint
adapters return the relevant vectors to constants. In the F0 wrapper there
are no cover-map events; all eight used native line recipes independently
fix `1`. Each wrapper ADD/SCALE/CLEAR preserves the constant subspace.
Consequently the entire scalar witness and its exact restoration statements
hold in the local native word, not only its scalar projection.

For tensor depth λ, tensor each checked vector identity. Equal frames remain
equal tensors, while each scalar coefficient acts **once**, not to power λ.
Zero residual boundaries remain zero. Normalize the common constant tensor
to χ. This proves the same coefficients and Hilbert-norm bound for every
positive λ; it is not extrapolation from a numerical sample of tensor depths.
Identity spectators and the retained stage-zero chart embeddings preserve
the argument. Uniformity over owners is compatible with their bijective
views/translations. This last interpretation inherits the reviewed
[core embedding and sweep contract](../joint-query/evidence/BRIDGE-REVIEW.md);
it is not a new global placement, hosting or address-cost proof.

## Reproduction and evidence

From the repository root, standard-library CPython 3.12:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-native-dirty-fault
```

Expected: `PASS_QQ16_NATIVE_DIRTY_FAULT`, eight passing behavioral tests, then
the package runner's success. Registered CPython 3.12.14 passes; a read-only,
Git-free export also passes with optimized CPython 3.14.7. The native vector check and complete replay
take about 30 seconds on the development host. The command authenticates
every declared live input before reading the native archive. It imports no
predecessor executable code and writes no scientific artifact. `--write PATH`
on `verify.py` creates an absent receipt and refuses to overwrite it.

[RESULT.json](RESULT.json) contains exact source-derived event/frame digests,
the complete 52-field response and replay counts. Independently of the
frame-reduced proof, the same package executes **all 26,099 events** directly
on 512-component Gaussian-dyadic vectors, including inverse residual wrappers.
For `T=256`, `u=2^-20`, `eta=1/512`, all **364,544 endpoint amplitudes** agree
with the stated result; maximum data error is `1/1024`. This literal path
shares the primitive vector evaluator, but does not use scalar projection
or frame vectors to execute the native word. It is a corroborating algorithm
by the same assisted author, not independent human or formal-kernel review.

Controls reject an altered child global phase, omitted nonconstant adapter,
missing kernel normalization, altered wrapper global phase, wrong fault
location, modified source and marked-instruction sign. An earlier fault at
24434 affects 102 helper outputs and fails the zero residual-boundary test.
Analytic basis-column and quadratic-form controls check primitive conventions.
All eight wrapper recipes also agree with their line operator on a vector
with distinct Gaussian components. Exact/absolute-error and zero-dirty
controls retain the legitimate ways to escape the obstruction.

## Scope

This closes the native binding for one F0 fault family. It does not check
every native operator column, arbitrary internal faults, concrete rounded
child implementations, grids/overflow, dirty-input ranges, physical machine
steps/storage, a paid F17 consumer, global hosting, or the full multiplication
theorem. Existing child operator semantics and the reviewed full-cover access
contract are inherited. The selected frontier and every frozen input remain
unchanged; a selected cold replay is therefore not part of this audit.

## Open next questions

The useful next question is whether a source-bound finite F0 implementation
can **exclude this fault and meet the complete producer tolerance**. Begin
with its actual dyadic grid, the dirty-input bound and the instructions that
perform rounding. Prove exactness at cancellations where possible, and bound
the remaining native-child defects and the whole physical bill. This matters
because reducing a headline precision constant cannot replace those premises.
The absence of an admitted numerical producer and its paid caller is the
blocker. [TASK.json](TASK.json) records this handoff and the bounded scope.
Family decision: narrow and stop; no new construction search.

## Provenance and credit

Scientific base: `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority
revision 6, OS assignment seed **67** (adversarial mathematical audit).
Submission base: `d8e0f83f00191df62174b641e9fff055c357f641`; the coordination
update leaves all eight live inputs and the selected record unchanged.
[SOURCES.json](SOURCES.json) records exact repository and archive-member pins.
The native archive is the retained source at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, SHA256
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727#discussioncomment-18978907)
was checked against recent PRs and Discussion comments before posting.

Credit Arham Tahir/PR2995 for the precise fault and handoff; Nick Petalas/
PR2965 (`526f2c242202b31b15e09a7502dfb8ff757b2bad`) for the producer-tolerance
contract; Ali Romman and the QQ16 team for the retained program; Sagar Thakrar
for the exact Clifford conventions and selected recipe audit; DLamdata for
the selected native-frame lift; ywz65, starship-s, Ross Richardson, Douglas
Colkitt and the remaining supplier/native lineage retained in the joint-query
notices. The independent evaluator here follows their published semantics;
their native recipe theorem and general conjugation lemma are not new claims.
Prepared by **Tekalign (@tekuuu), with substantial OpenAI Codex assistance**.
Apache-2.0. No independent human review is claimed.
