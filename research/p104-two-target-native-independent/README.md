# Independent native binding for the P104 two-target correction

PR2445's correction of **Y0 and Y1** now has a finite native Clifford
certificate for all **236 added transport occurrences**. Its **161 distinct
frame pairs** are absent from the original channel's 740-pair certificate.
Every pair has an exact forward recipe and an exact adjoint recipe, including
global phase, with the inherited positive-child rank. A separately written
checker composes the forward recipes with the retained native channel and
checks every one of **128,164 boundary coefficients over 358 arbitrary inputs**.

This closes the finite forward native-binding handoff in
[PR2445](https://github.com/CrocSwap/integer-mult-bounds/pull/2445), exact head
`6def43ad673b91dbd491389964d1dcd059bf2ac2`. The two-target construction and
78-lifetime minimum belong to that predecessor. No new helper minimum, complete
supplier, global recursive invoice, all-size proof or kappa is claimed here.

This is PR2458's independently written full-column checker, now retained at
`research/p104-two-target-native-independent`. The distinct package path lets it
coexist with [PR2454](https://github.com/CrocSwap/integer-mult-bounds/pull/2454)'s
`research/p104-two-target-native` package. The PR2458 literal circuit, native
certificate, mathematical receipt and predecessor source pins are unchanged.

## Exact covered operator

Fix the nine-bit physical label isometry and canonical chart representatives
`Gamma_W` from [PR1991's retained channel](../p104-native-channel/README.md).
For every register r, maintain `physical_r = Gamma_W(r) logical_r`.
A transport A to B is exactly `Gamma_B Gamma_A^-1`; a scalar ADD or COPY uses
one identical current chart on both operands. The checker binds exact
representatives, not just equal binary spans.

For a logical boundary matrix S, induction gives the physical block map

`physical_r(final) = sum_s S[r,s] Gamma_final(r) Gamma_initial(s)^-1 physical_s(initial)`.

The source and target intrinsic endpoint adapters are unchanged and rechecked.
The forward scalar matrix is checked entry by entry: Y0 and Y1 acquire their
matching source, the other 102 targets acquire the original G/2 row, all 104
sources restore logically, and all **150 arbitrary dirty helpers** restore
logically. This includes the original 72 and the 78 added helpers. Their
physical arrays change with the prescribed endpoint charts: in particular,
an added helper starts at ZERO and finishes at FULL. Logical restoration does
not assert bytewise or physical-array equality across that change.

The original eight private-copy lifetimes are retained. Their inherited
owned-copy discard contract is used explicitly; the checker does not pretend
the live copy was reversibly returned to zero.

The independent native interpreter checks all 18 signed Pauli images and the
complete exact Gaussian-dyadic image of basis zero for each of the **322
forward/adjoint recipes**. Equal Pauli conjugations determine a Clifford up
to scalar phase, and equality on this nonzero state fixes that phase. Thus
the comparison establishes each complete 512-dimensional operator, rather
than a sampled input test. [REVIEW.md](REVIEW.md) states the proof and reuse
boundary. This is finite exact computation plus a written composition argument,
not a formal proof-kernel result.

**The adjoint recipes cover individual transports only.** They do not execute
or certify the inverse transpose of the complete program with COPY/discard.
The complete backward interface remains a separate obligation.

## Accounting

The newly compiled pairs do not alter the predecessor's literal word or costs.

| Added quantity | Exact value |
| --- | ---: |
| Nested transport occurrences | 236 |
| Distinct directed frame pairs | 161 |
| Forward plus adjoint native recipes | 322 |
| Added profile | 142 H1 + 16 H2 + 18 H6 + 60 H7 |
| Added boundary rank mass | 702 |
| Added scalar ADDs / helper lifetimes | 440 / 78 |

The full forward word has 4,734 events, 1,646 transport occurrences and rank
mass 3,070. Every native recipe contains one positive Fourier-type child of
its declared rank and two rank-zero Gaussian monomial adapters. Rank-zero
adapters still perform address/phase work. This table is a finite operator and
local rank invoice; it does not price physical scalar lowering, adapter routing,
recursive owners, idle/residual children, tape, approximate arithmetic or the
all-size compiler. Boundary rank progress is not automatically recursive excess.

## Reproduce

Python 3.12, standard library. Default verification reads fixed evidence and
never generates a missing certificate. It imports no producer or Clifford
compiler. The optional regeneration runs the credited compiler in temporary
storage and compares the **complete decompressed mathematical payload**.

The wrapper compiles package code from source bytes directly. Each external
source and vendored input is read once into an authenticated byte snapshot.
The unchanged retained checker loads its transitive interpreter inside a fresh
private tree containing those exact bytes and no existing caches; the scalar
replay reads the authenticated data snapshots. The optional Clifford compiler
also executes its authenticated source bytes directly. Existing timestamp and
unchecked-hash `.pyc` files are neither trusted nor copied into that tree.
This covers the complete runtime source graph without modifying predecessors
or patching the process-wide importer.

```sh
python3.12 -I -O -B research/p104-two-target-native-independent/verify.py --regenerate
python3.12 -I -O -B research/p104-two-target-native-independent/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-two-target-native-independent
```

Expected marker: `PASS_P104_TWO_TARGET_NATIVE no_new_kappa`.
The new checker requires ten semantic fault controls and accepts two equivalent
presentations. The behavioral suite checks missing evidence, source drift,
malformed receipts, exclusive output, a Git-free read-only export and a changed
gzip header. Timestamp and unchecked-hash cache controls establish that the
seeded caches are executable, preserve valid replay including regeneration,
and reject the review's wrong-phase rank-seven recipe at its exact phase
predicate. These controls cover package helpers, both retained checker modules
and the optional compiler. The suite also removes only the exact-phase
predicate in memory and requires the phase control suite to fail, establishing
defect sensitivity.

[RESULT.json](RESULT.json) is the fixed exact receipt.
[SOURCES.json](SOURCES.json) pins every runtime input by Git blob and SHA256.
The literal predecessor circuit is the only vendored data; the existing native
channel, compiler and independent interpreter remain unchanged in their own
package. All required inputs are declared in [VERIFY.json](VERIFY.json), so a
Git-free export consists of this package and those six runtime files at their
listed relative paths. `--out` accepts only a new file. The separate explicit
`--emit-initial-result --out PATH` option is for authoring, not default checking.

The inherited native checker is replayed, not claimed as a new independent
implementation. It proves all inherited transport operators via signed Pauli
and exact phase checks; this package does not rerun its optional 4,096 private
basis-column enumeration. No selected-frontier cold replay, hosted CI result,
human review or proof-assistant verification is claimed by these local checks.

## Sources, credit and scope

Scientific base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
Its historical selected-record pin has SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
This package does not change the selected frontier.
The literal PR2445 circuit SHA256 is
`c34d94128decc426e7528302ab2570967293a1b293f184fdd89fd376addd61f9`.
The original overlap snapshot and changed catalogue scope are recorded in
[TASK.json](TASK.json).

Credit Ross Richardson / PR2445 for the complete two-target logical word and
sharing proof; commdata2338 / PR2393 for the one-target acquisition proof and
sharing handoff; Hiroki Kumazaki / PR2353 and Philippe Van Velzen for the relay
model. Chafik Boukhalfa / PR1991 supplies native channel lowering and the
physical label binding, Rohan Arun / PR1972 the original scalar/frame channel,
Adam Gall / PR1940 its schedule, Josie Elliston / PR1071 the fixture, and Ali
Romman / PR1125 and PR1862 the retained geometry/native interpreter lineage.
The exact compiler is retained through icekylinx / PR531 and the
PR523/514/507/425/433 ancestry. Original notices remain under
`research/p104-native-channel/notices/`; no predecessor file is modified.

Prepared for Ross Richardson with substantial OpenAI Codex assistance in
implementation, derivation and writing, including a separate mathematical
specialist who wrote the new native-binding/forward checker without importing
the producer. No blind or independent human review is claimed. New material
and the retained literal circuit are Apache-2.0.

## Open next questions

First specify and emit the complete dual program under its actual private-copy
contract, then check scalar direction, chart adapters and every private lifetime.
Transport adjoints alone do not settle this.

For a full correction, name a third target and test collector rank and chronology
before extending the word. The other 102 corrections, actual global hosting and
idle/residual invoice, physical scalar/address costs, precision/tape and all-size
admission remain the gates to any supplier or exponent claim. Structured first
steps and blockers are in TASK.json; this package closes only its fixed finite
forward native-binding question.
