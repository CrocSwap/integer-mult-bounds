# The mixed native F0 rounding witness at every precision

The same five-field error reported by Ross Richardson in
[PR3067](https://github.com/CrocSwap/integer-mult-bounds/pull/3067) occurs for
every integer precision `p >= 8`, under that package's mixed arithmetic model.
PR3067 checked four finite precisions and explicitly left the all-precision
statement open. The witness itself, its physical binding and its error pattern
are predecessor results. This package supplies the uniform implication by
symbolic execution, not another finite precision sweep.

The scope is exactly one literal `F_0` word, one tensor factor with nine active
axes and 512 payload coordinates, and owner-uniform inputs. Real and imaginary
scalar ADD results round to a p-bit binary significand, nearest with ties to
even and unbounded exponents. Completed native maps, their interiors, endpoint
and residual adapters, SCALEs and owned CLEARs remain exact. Every scalar
coefficient product on this family is certified exactly representable for all
`p >= 8`.

## Result

Set physical `L112 = ONE`, `L224 = 2^(p+12) ONE`, and all other fields zero.
The exact execution returns this entry. The mixed rounded execution differs
from it only as follows.

```text
L112                  -ONE
L114,L137,L190,L211    -ONE/2
all 480 helpers       exactly their entry values
all eight private C   zero
```

Only scalar events 3887 and 4060 round. Each contributes `-ONE/2`. The maximum
output-error norm equals the input data norm `sqrt(512)`, so its relative error
is one. Signed power-of-two scaling preserves the theorem. Scaling by `1/32`
gives input data norm at most one with the same relative error. The dirty
magnitude still grows with p. This is not a fixed-input failure at every
precision or a theorem about bounded dirty state.

[PROOF.md](PROOF.md) gives the affine-rounding lemma and induction. Every
component has the symbolic form `a*2^(p+12)+b` with exact Gaussian-dyadic
coefficients. Two endpoint binade checks and an even grid-index condition prove
one rounding decision for the entire precision ray. The literal word passes
all these checks with threshold eight. No optimality of that threshold is
claimed.

This is an accuracy-contract obstruction with exact completed native maps.
The concurrent [PR3305](https://github.com/CrocSwap/integer-mult-bounds/pull/3305)
clean-helper original-input collision uses a fully rounded model and is
separate. Neither its theorem nor its implementation is used here.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/qq16-f0-all-precision
```

Direct commands, also usable from a source export without Git:

```sh
python3 -I -Werror -B research/qq16-f0-all-precision/verify.py
python3 -I -O -Werror -B research/qq16-f0-all-precision/test_verify.py -v
```

`RESULT.json` is the exact canonical receipt. The verifier compares every one
of the 712 symbolic output vectors with the stated ideal and rounded endpoints.
Its 40,556 vector rounding/product obligations comprise 38,326 constant-vector
checks and 2,230 mixed-or-leading-vector checks. All nonconstant checks inspect
all 1,024 real/imaginary components. These are proof obligations for the ray,
not sampled precisions.

Eight behavioral groups include 3,762 separate exact-neighbor rounding checks,
explicit ties and sign changes, rejected unstable binades and tie parity,
non-dyadic inputs, source corruption and live-input reclassification. The
unchanged predecessor executor separately agrees at `p=8,127,256`. Exact ADD
and wrong-gate controls change the endpoint. The two dispatchers share the
credited exact native evaluator; this is not an independent Clifford audit.

The registered replay passed on CPython 3.12.15, Linux x86_64, including all
eight groups under optimization. Strict Ruff E,F,I,B,UP,RUF and formatting
checks passed. These are local results; hosted checks are tracked separately.

All six runtime source files are canonical-main blobs at
`463113d675af7410ac91d53a4fed51ec6494eb9a`. `SOURCES.json` records their exact
hashes. The frozen archive's consumed member hashes are additionally checked
by the unchanged PR3067 loader. Replay needs no unrelated pending-PR object.
The source export must preserve the declared repository-relative paths. No
input is regenerated or modified.

## Limits and research decision

This is a scoped written proof with an executable finite certificate of its
symbolic premises. No independent human or proof-kernel review is claimed.
Native-internal rounding, bounded exponents, overflow, a fixed caller entry
lattice, multi-layer/full-cover execution, F0/B1 controller closure, source
access, paid movement, backing/storage, recursive tariffs, dirty cleanup for a
different contract and the F17 consumer are not proved or priced here. No
selected cold replay, Lean or Docker run is required or claimed. There is no
supplier admission, selected-frontier change or new kappa.

The family decision is narrow and stop. This theorem removes a finite-case
limitation from one concrete negative accuracy result. It does not justify
another decoder or construction search. Unknown physical costs remain unknown.

## Open next questions

Can an admitted caller bound the dirty-to-data ratio and choose a sufficient
paid precision for the actual rounded native interiors? Pin its entry grid,
range and endpoint contract, then account for every occupied intermediate and
its consumer. The lack of a complete paid caller blocks supplier admission.
Exact-grid arithmetic and bounded dirty state remain legitimate escapes.

Can the sufficient threshold eight be reduced for this same mixed-model
family? The first step is to inspect which affine predicate fails below eight.
No research decision currently requires a sharper threshold, so another search
is not proposed here.

## Credit and engineering notes

Arham Tahir supplied PR3036's scalar witness at
`3717c1e684553c57bc73300410df65438a9ef095`. Ross Richardson supplied PR3067's
physical witness and finite implementation at
`e1e28b4070ae52efa5a9d0aa826bc588be7206f2`. Tekalign supplied PR3017's exact
native evaluator at `0f493f4c264fbc70ee14364b68af260d858c143c`. Nick Petalas's PR2965 supplies the conditional
producer-output bridge, not an implementation of its premise. Credit Ali Romman,
Sagar Thakrar, DLamdata, ywz65, starship-s, Douglas Colkitt and the retained
QQ16/supplier/native lineage as recorded in the unchanged predecessor notices.
New symbolic proof, checker and controls by Nick Petalas. Substantial AI
assistance was used in derivation, implementation and checks. Apache-2.0.

Build the Lever determined the rerunnable symbolic certificate rather than a
prose extrapolation. Prove It Works determined full endpoint comparisons,
direct native controls and exact publication checks.

The Power of Ten managed-runtime deviation applies to `verify.py` and its
controls. Python integers, Fractions and tuples allocate dynamically. State is
bounded by two arrays of 712 vectors with 1,024 components each, the fixed
26,099-event word, and a 65,536-entry rounding cache. Each authenticated input
read is capped at 32 MB. Tests use finite ranges and temporary directories with
scoped cleanup. The imported immutable evaluator retains its bounded 9-axis
loops and 256-entry monomial cache. Direct predecessor controls also use its
bounded 32,768-entry integer-rounding cache. Its existing runtime-source compilation is
restricted to authenticated bytes, not arbitrary expressions. The new code
uses no recursion; functions stay below 60 lines and validation remains active
under optimization. Strict Ruff and warning-as-error checks accompany replay.
This is not an allocation-free tape implementation. A physical implementation
must replace these managed objects with its own bounded storage and costs.
