# F0 dirty restoration does not imply a data-only relative-defect bound

The literal reviewed QQ16 F0 word has a cancellation at which one admissible
completed ADD defect produces **`4 u T` final data error**, although every one
of its 480 borrowed helpers restores exactly. Here `T` is the magnitude of one
initial dirty helper, and the original data have maximum norm one.

This is a new, source-bound **common-chart scalar audit**, following Nick
Petalas's [PR2965 producer-error handoff](../qq16-producer-defect-transfer/README.md).
It identifies an obstruction to deriving its F0 completed-output tolerance from
local relative ADD inequalities alone. PR2965 explicitly leaves producer
interiors and dirty-helper bounds open; this result confirms that boundary,
rather than finding a defect in that theorem. It does not implement or reject
a particular rounded producer. Exact dyadic ADDs avoid the injected fault.

## Statement and exact witness

Use the scalar projection of `programs.F_0` in the pinned
[joint-query certificate](../joint-query/certificate.json.gz): expand the
forward retained core, expand each sweep body in order, and retain the scalar
operations. There are 26,099 events before scalar filtering and 21,025 scalar
macros. Frame changes, native children and adapters are not numerical
operations in **this defined scalar model**. F0 has no cover-map events.

At each completed ADD `d <- d + c s`, permit an arbitrary destination defect

```
|eta| <= u (|d| + |c| |s|)
```

measured on the actual pre-instruction operands. All other operations can be
exact. This is a permissive error specification, not a claim that any concrete
rounding algorithm can realize every allowed eta. Let `u > 0` and `T > 0`.
Set original input `L112 = 1`, dirty helper `L359 = T`, and all other inputs,
including the eight owned private fields, to zero. Thus the original-data norm
is exactly one, independent of T.

Immediately before event **24438 (zero-based, before filtering)**, the exact
state has `L39 = -4T`, `L359 = T`. Its literal instruction is

```json
["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]
```

The ideal destination becomes zero. Choose `eta = 8uT` immediately after this
ADD, saturating the stated local allowance. Continue the whole word exactly.
The final ideal state equals the input on this witness family. The unit fault's
final response is recorded in [RESULT.json](RESULT.json): precisely 52 data
fields have coefficient +1/2 or -1/2, including coefficient -1/2 at `L2` (X2).
Every helper and private response is zero. Therefore

```
max_data |faulty output - ideal output| = |eta|/2 = 4uT.
```

All 480 helpers equal their original values and all eight owned private
outputs are zero **even with this fault**, on this witness family. The fault
can be made a deterministic state-dependent ADD implementation by adding
`u (|d|+4|s|)` only at this instruction; the other ADDs are exact. Thus it is
not necessary to assume independent, random, or repeated errors.

The coefficient identities prove the statement for all positive rational or
real T and u in this scalar model. The checker evaluates exact dyadic cases
`T=1, 2^8, 2^64, 2^256`, with `u=2^-80`, as finite controls; it does not infer
the quantified claim by extrapolating those cases.

## Consequence for the producer interface

There is no finite constant C such that the local inequalities above plus exact
helper restoration imply completed F0 data error at most `C u H`, when H bounds
only the original data and helper magnitude is unrestricted. Take H=1 and
T>C/4. The conclusion remains false if u is required to be arbitrarily small.

For PR2965's sufficient F0 tolerance `H 2^(-beta-8)`, a necessary condition for
accepting **every fault allowed by this specification** on this family is

```
u <= (H/T) 2^(-beta-10).
```

With `u=2^-p`, this requires `p >= beta+10+log2(T/H)`. It is only a necessary
condition from one fault; it is not a sufficient producer precision bound or
an optimal reserve. It leaves PR2965's endpoint constants 49 and 1923 intact.
A constant absolute defect eta at this event instead gives `|eta|/2`,
independent of T. Exact grid-preserving execution gives eta=0. A bound on dirty
magnitudes or a stronger numerical specification could therefore escape this
obstruction; this package does not supply such an implementation or its cost.

## Scalar evidence and native boundary

The primary checker uses exact rational **forward state propagation**, without
importing predecessor code. A separate [adjoint checker](independent.py)
propagates linear functionals **backward**: two prefix rows establish the cut
coefficients; all 712 suffix rows independently recover the complete unit-fault
response. These are separate algorithms by the same AI-assisted author, not
independent human review. Source hashes bind the literal word and the cited
predecessor contract. Source bytes and the selected frontier remain unchanged.

The checked cut ledger narrows that follow-up: after the marked event the
retained core has 475 scalar events, all annotated with frame label 1, and
240 residual adapters acting only on helpers (plus one phase marker). There
are no remaining core climb or data-adapter events. This is an inventory,
not a proof that every annotation denotes the required physical operator.

This result is not an injection experiment inside a physical native child.
The existing [native review](../joint-query/evidence/NATIVE-REVIEW.md) inherits
the core lift and checks new wrapper access. An endpoint identity alone does
not establish how an internal fault transforms. To lift this audit to an
actual payload execution one must bind the marked cut to unitary register
gauges `U_i`, with each scalar instruction represented by
`U_after E_i U_before^-1`, and verify the ideal non-scalar transitions. Under
that additional cutwise conjugacy, a common unit payload times the scalar
witness gives the same norm bound; the proof is immediate by cancellation of
successive gauges. **That cutwise binding is not verified here.** Physical
child interiors, component rounding and wrapper arithmetic need their own
contracts. No physical producer-failure or universal algorithm barrier follows.

## Reproduce

From the repository root, using standard-library Python 3.12:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/qq16-producer-dirty-fault
```

Direct read-only commands also work with Python 3.10+:

```sh
python3 -I -O -B research/qq16-producer-dirty-fault/verify.py
python3 -I -O -B research/qq16-producer-dirty-fault/independent.py
python3 -I -B research/qq16-producer-dirty-fault/test_audit.py
```

Behavioral controls cover altered sources/receipt, the fault sign and location,
zero dirty input, absolute rather than relative defects, optimized execution,
and a Git-free relocated copy. In particular, an earlier data cancellation
fault changes 102 helper outputs: restoration is checked, not inferred from
being near the end of the word. Default replay writes no scientific artifact;
`--write` creates an absent receipt and refuses to overwrite it.

## Open next questions

Can this exact cut be bound to the actual native register gauges? Pin the core
frame registry and native recipes, identify the physical input and output
gauges at event 24438, and propagate one payload error through the suffix.
This would decide whether the scalar sensitivity holds for the retained native
producer. The missing cutwise binding, not the endpoint F0 identity, is the
blocker. A full recursive child replay has not run.

Can a producer avoid the fault while retaining an affordable complete bill?
Start with a declared common dyadic grid and a bound on the actual dirty inputs,
then prove which ADDs are exact and bound completed native-child errors. The
new necessary reserve only applies to the permissive relative specification.
Grids, overflow, dirty ranges, physical movement/hosting, F17 consumption and
restoration costs remain open. Family decision: **narrow and stop** after this
audit; no additional decoder or census is proposed.

## Sources and credit

Scientific base: main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision
6. [TASK.json](TASK.json) records the assignment, refined scope, overlap and
submission freshness; [SOURCES.json](SOURCES.json) pins exact inputs.

Credit Nick Petalas / PR2965 (`526f2c242202b31b15e09a7502dfb8ff757b2bad`) for the
completed producer-error transfer and explicit handoff; Ali Romman and the
joint-query team for F0/B1; Arham Tahir / PR2681 and ywz65 / PR2707/2540 for the
ordered inverse and decoder; and starship-s, Sagar Thakrar, Ross Richardson,
Douglas Colkitt and the native/geometry/supplier lineage retained in those
sources. No predecessor package is copied or modified. The elementary scaling
argument is standard; the new contribution is this literal restoration-preserving
fault witness and its two exact checks. Prepared by Arham Tahir with substantial
OpenAI Codex assistance. Apache-2.0. No new supplier, kappa, full selected cold
replay, physical cost certificate or formal-kernel proof is claimed.
