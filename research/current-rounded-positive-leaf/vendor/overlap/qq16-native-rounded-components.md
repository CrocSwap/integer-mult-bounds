# Concrete component rounding in the native QQ16 F0 reference

Arham Tahir's [PR3036](https://github.com/CrocSwap/integer-mult-bounds/pull/3036)
leaves open whether its two deterministic scalar rounding errors survive the
physical native maps. **They do for the finite reference lowering specified
below.** All 480 borrowed helpers restore as numerical values, yet a unit data
input is lost. No freely chosen fault is injected.

The new evidence includes the native butterfly interiors, adapters, residual
wrappers and all eight additional native lines. The source's recursive child
tariff is not assigned to this direct finite implementation. There is no new
supplier or kappa claim.

## Finite statement and operation order

Use the pinned joint-query `programs.F_0`, including the literal forward core,
on 712 fields of 512 complex coordinates. Let `1` be the unnormalized real
constant payload. Initialize

```
L112 = Y0 = 1; L224 = 2^65 * 1; all other fields = 0.
```

Here L0..L111 are X, L112..L223 are Y, L224..L703 are dirty helpers,
and C0..C7 are private fields. L224 has ordinary frame endpoints `(0,1)`.
The exact reference returns this entry unchanged.

Each real component uses binary round-to-nearest, ties-to-even, with 53
significand bits. Scalar ADD means **separate rounded multiplication and ADD**.
Scalar coefficients are checked to be exactly representable. A native recipe
is its serialized right monomial, coordinate Gaussian lines in increasing
axis order, then its left monomial, including global phase. Monomials perform
signed coordinate permutations and real/imaginary exchanges. Phase tags in
the event stream are control labels, following the source semantics.

For each disjoint complex pair `(a+ib,c+id)`, a positive Gaussian line uses
this pair-first real lowering, rounding each displayed sum/difference:

```
rp = RN(a+c); ip = RN(b+d); rd = RN(a-c); id = RN(b-d)
out0 = (RN(rp-id)/2, RN(ip+rd)/2)
out1 = (RN(rp+id)/2, RN(ip-rd)/2)
```

Division by two is exact on this execution. The operation order is part of
the claim. CLEAR applies only to owned private fields. Zero-valued child
inputs may be skipped by the interpreter because every primitive maps zero
exactly to zero; this is an execution shortcut, not a cost saving claim.

Under this lowering the final numerical values are

```
Y0 = 0
Y2 = Y25 = Y78 = Y99 = -1/2 * 1
L224 = 2^65 * 1
all other outputs = 0.
```

The maximum data-field Hilbert error is `sqrt(512)`, equal to the entry
data-field norm. Every physical helper returns its entry value and every
private output is zero. Signed-zero bit patterns are not compared.

Exactly two completed scalar ADD sites round, at unfiltered zero-based
expanded events **3887 and 4060**, each on 512 real components. At both cuts
the actual native target/source vectors are `(1/2 * 1, 2^65 * 1)` and the
coefficient is `-1/2`. Thus each real component rounds
`-2^64 + 1/2` to `-2^64`, losing `1/2`. These are deterministic arithmetic
decisions. Every native butterfly's internal operation and every scalar
multiplication is exact on the resulting trajectory.

## Evidence and source binding

[RESULT.json](RESULT.json) is recomputed by a shared-exponent integer-vector
interpreter. Rounding discards low significand bits with an explicit signed
nearest-even decision; dyadic denominators are exact and exponents unbounded.
All observed nonzero primitive binary exponents lie in `[-2,67]`, checked
inside the normal finite binary64 range. This witness needs neither underflow
nor overflow.

A second engine uses actual Python binary64 scalar multiplication/ADD and
separately written float Gaussian butterflies and complex phase rotations.
The engines agree at **all 26,089 changed-field cuts** of the complete
26,099-event program and all **364,544 complex endpoint amplitudes**. The
cut comparison uses canonical exact dyadic-vector hashes; the complete final
vectors and both marked operand pairs are compared directly. Both engines
share the source event dispatcher and the credited monomial index table.
This is arithmetic corroboration, not an independent audit of every source
recipe or its Clifford theorem.

Exact arithmetic, 65-bit precision on the same dirty input, and removal of
the dirty input all recover the correct native endpoint with no rounding.
The wider control is a sufficient escape for this input, not a general
precision bound or minimum.

Seven behavioral groups check 36,882 decisions against an enumerated finite
binary system, 5,008 integer decisions against hardware binary64, Gaussian
basis columns, a changed literal ADD, a used native global-phase mutation,
and scientific-input, receipt and primitive-source corruption. Both positive
fixtures and actual failing variants are exercised.

Source commits, Git blobs, archive-member hashes and the unchanged vendored
primitive evaluator are recorded in [SOURCES.json](SOURCES.json). The two
external scientific inputs are declared for invalidation in
[VERIFY.json](VERIFY.json). The selected record and catalogue are historical
provenance. Frozen predecessor packages and the selected frontier are unchanged.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-native-rounded-components
```

Expected marker: `PASS_QQ16_NATIVE_ROUNDED_COMPONENTS`, seven passing
behavioral groups, then `PASS_REGISTERED_RESEARCH_PACKAGE`. Replay is read-only;
`verify.py --write PATH` only creates an absent receipt. Direct `verify.py` and
`test_verify.py` also work in a source export containing the package and its
two declared inputs. See TASK.json for the actual task and verification status.

## Consequence and limits

The scalar-rounding handoff is resolved for one explicit finite native
lowering. Exact dirty restoration alone still does not imply data accuracy,
even when the errors come from actual correctly rounded component operations.
[PR2965](https://github.com/CrocSwap/integer-mult-bounds/pull/2965)'s conditional
completed-output transfer remains unchanged; producer tolerances are its premises.

This checks the retained 512-coordinate native recipes under their inherited
local chart/access interpretation. It proves no all-depth tensor statement,
arbitrary-input error estimate, child-tariff implementation, exact signed-zero
restoration, owner routing or physical machine/tape/storage bound. It neither
audits B1/the decoder nor supplies a paid consumer, complete supplier, selected
cold replay, formal-kernel proof or multiplication theorem. Other numerical
lowerings and common grids can avoid the loss.

Family decision: **narrow and stop** after this local numerical implication.
The direct finite numerical bill is not a favorable complete recursive invoice.
Native recursive cost, physical movement/storage, dirty-range policy, B1,
consumer and supplier admission remain additional or unknown; unknowns are
not assigned zero cost. No downstream implementation campaign is proposed.

## Open next questions

Can a pinned finite native producer meet the required completed-output tolerance
with an explicit dirty-input bound and grid/precision policy? Start by deriving
its all-cut component magnitudes and exact-cancellation rules, then charge the
native children, layout/movement, workspace/restoration and actual consumer.
This matters because the output-error theorem assumes producer accuracy; the
missing complete numerical/physical caller contract blocks supplier adoption.
The structured handoff is in [TASK.json](TASK.json). Local registered replay
on Linux / CPython 3.12.14 passes; hosted CI is separate.

## Credit

Prepared by **Sricharan Vagvala (@theon199), with substantial OpenAI Codex
assistance**. New interpreter, audit, controls and prose are Apache-2.0. No
independent human review, hosted CI pass or formal-kernel review is claimed.

Credit **Arham Tahir / PR3036** at `3717c1e684553c57bc73300410df65438a9ef095`
for the concrete scalar witness, two sites and numerical-conjugacy handoff;
**Tekalign (@tekuuu) / PR3017** at `0f493f4c264fbc70ee14364b68af260d858c143c`
for the native semantics, exact vector primitives and member pins. The
180-line [vendor/native.py](vendor/native.py) is reused byte-for-byte with its
author/license retained; it is a working dependency, not new independent
native-semantic evidence. Credit Nick Petalas / PR2965, Arham Tahir / PR2995,
Ali Romman and the QQ16 team, Sagar Thakrar, DLamdata, ywz65, starship-s,
Ross Richardson, Douglas Colkitt and the retained supplier/native/scalar lineage
in the [original notice](../joint-query/NOTICE.md).

## Publication handoff

The verified numerical code and receipt are public at fork commit
[`946a399d6ae1667236bb395d21c33c749e000877`](https://github.com/theon199/integer-mult-bounds/commit/946a399d6ae1667236bb395d21c33c749e000877).
The [contribution branch](https://github.com/theon199/integer-mult-bounds/tree/research/qq16-native-rounded-audit)
may add publication-status documentation only. GitHub denied both PR creation
and Discussion posting with `Resource not accessible by integration`; no PR
or public CLAIM was created. The result is complete for its stated finite
scope and released. A maintainer can review the public artifact or open the
[fork comparison](https://github.com/CrocSwap/integer-mult-bounds/compare/main...theon199:research/qq16-native-rounded-audit?expand=1).
