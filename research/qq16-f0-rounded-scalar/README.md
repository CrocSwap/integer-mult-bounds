# Correct rounding can lose data in the F0 scalar projection

The literal QQ16 F0 **common-chart scalar projection**, executed with ordinary
binary64 arithmetic, loses a unit data input despite exactly restoring every
dirty helper. This supplies a concrete rounding example beyond the freely
admissible relative fault in [PR2995](https://github.com/CrocSwap/integer-mult-bounds/pull/2995)
and its [PR3017 native binding](https://github.com/CrocSwap/integer-mult-bounds/pull/3017).
Those packages explicitly leave concrete rounding open.

This result is about the scalar projection only. It does not replace native
operators by identities in the physical producer or exhibit its rounding failure.

## Exact experiment

Use all 26,099 events obtained by concatenating the certificate's forward core
and F0 wrappers. There are 21,025 scalar instructions. As in the predecessor's
common-chart projection, omit the 3,486 climbs, 1,090 adapters, 480 residual
adapters, ten phase tags and eight new native lines. Flatten each private
sweep's scalar body in literal order. Event indices below are zero-based in
that expanded projection, including omitted events.

Registers L0..L111 are X, L112..L223 are Y, L224..L703 are the 480 borrowed
helpers, and C0..C7 are the owned private fields. Initialize

```text
Y0 = 1,  L224 = T = 2^65; every other input = 0.
```

Exact rational execution returns precisely that entry state. With 53-bit
significands and round-to-nearest, ties-to-even, the result instead is

```text
Y0 = 0,
Y2 = Y25 = Y78 = Y99 = -1/2,
L224 = 2^65;
every other output = 0.
```

All 480 borrowed helpers restore **exactly**, and all eight private outputs
are zero. The maximum absolute data error is one. There is no overflow or
underflow in the binary64 replay.

Exactly two ADD instructions round: events 3887 and 4060, targeting L112 and
L139. At each, the stored target is 1/2, source L224 is T, and coefficient is
-1/2. Hence the exact operation result is `(1-T)/2`; binary64 stores `-T/2`,
with error -1/2. Every other scalar instruction is exact on the computed path.
The complete signed continuation produces the five differences above.
The two faults are consequences of the specified arithmetic, not chosen errors.

For the first rounding decision, the representable number immediately toward
zero from `-2^64` is `-2^64+2^11`. The exact result `-2^64+1/2` is strictly
closer to `-2^64`. Thus this example does not depend on a tie-breaking accident.

## Evidence and controls

[RESULT.json](RESULT.json) records the full projection hash, both fault records,
every case's final 712-coordinate digest and chronological changed-field trace
digests. Exact, rounded, clean-helper and wider executions are recomputed.

- The exact rational rounding interpreter implements a single correctly rounded
  completed `target + coefficient*source`, with unbounded exponents. Actual
  Python binary64, using separate multiplication and ADD, agrees at **every
  scalar instruction** and on every final coordinate for the 53-bit witness.
  These are two implementations of the arithmetic, not two native producers.
- Four checked cases use p=8,24,53,113 and T=2^(p+12). They have the same two
  faults and five errors. This is finite coverage, not an all-p theorem.
- For each case, p+12 significand bits reproduce the exact endpoint with zero
  rounded instructions. The exact trace's largest required significand is
  precisely p+12. This is a sufficient escape for these inputs, not a general
  F0 precision bound. Removing the dirty input also removes every fault.
- A separately implemented, explicitly enumerated finite binary number system
  checks 7,740 nearest-rounding decisions, with additional signed tie controls.
  Sign and power-of-two input scaling, changed/omitted literal gates, corrupted
  source/receipt, and an optimized Git-free public replay are tested.

Run from the repository root with standard-library Python 3.12:

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-f0-rounded-scalar
```

Direct normal or optimized `verify.py` execution also works without Git when
the package and its single declared scientific input are copied together.
Default replay is read-only. `--write` creates an absent receipt and refuses
to overwrite one. Source hashes and originating task/selected-record provenance
are in [SOURCES.json](SOURCES.json); actual scope and next questions are in
[TASK.json](TASK.json).

## Implication and limits

Exact dirty restoration does not ensure data accuracy for this literal scalar
implementation. A producer contract needs an actual range/grid/precision policy
if it relies on this projection. The completed-output transfer in
[PR2965](https://github.com/CrocSwap/integer-mult-bounds/pull/2965) is unchanged:
it assumes, rather than establishes, producer accuracy.

The omitted native maps generally make intermediate physical vectors nonconstant.
Consequently the scalar rounding operation need not represent component rounding
in those vectors. PR3017's binding of a freely admissible defect does not bind
the two deterministic rounding errors here. That new implication remains open.
No native child interiors, B1, decoder replay, all-size realization, physical
ownership/movement, consumer invoice, selected cold replay or multiplication
theorem is verified here. No supplier or new kappa is claimed.

Family decision: **narrow and stop** after this concrete arithmetic witness.
No construction expansion or full favorable budget is asserted; physical
costs remain unknown.

## Open next questions

Can the two deterministic scalar roundings be realized by an actual native
producer? Track physical frame vectors and component arithmetic at both marked
cuts, then replay their continuation and helper restoration. The blocker is
numerical conjugacy, not another arbitrary-defect sensitivity calculation.

Alternatively, can a pinned native producer avoid this loss with a sufficiently
wide common grid and bounded dirty range? Supply its actual all-cut range,
rounded-child and restoration contracts before charging a complete consumer.
The p+12 control above is evidence only for this scalar input family.

## Attribution

New witness, implementation and tests: Arham Tahir, with substantial OpenAI Codex
assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
Credit Nick Petalas/PR2965 for the producer-error handoff, Arham Tahir/PR2995 for
the earlier scalar relative-fault audit, Tekalign (tekuuu)/PR3017 for its native
binding, Ali Romman and the QQ16 team for the reviewed producer, and Sagar Thakrar,
DLamdata and the supplier/native/scalar lineage retained in
[the original notice](../joint-query/NOTICE.md). Frozen predecessors are unchanged.
