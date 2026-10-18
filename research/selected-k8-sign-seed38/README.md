# Sign normalization of the selected PR1042 scalar word

**Finite complex-supplier circuit construction. No new kappa.**
Ross Richardson's retained sign compiler reduces the PR696 comparison word for
the PR1042 seven-slot k8 construction by **408 real-component primitives per
orientation**. This package supplies the complete source-bound transfer and
two exact implementations of its verification.

| Complete scalar projection | PR696 comparison word | Sign-normalized word | Saved |
| --- | ---: | ---: | ---: |
| Forward | 149,002 | 148,594 | 408 |
| Backward / inverse transpose | 149,018 | 148,610 | 408 |

The comparison applies Sagar Thakrar's retained PR696 lowering to the frozen
PR1042 programs. These counts include both real and imaginary components.
They price every copy, clear, coefficient preparation, source access, shift,
target update and final sign restoration. They are instruction counts, not
measured runtime improvements or a fresh global invoice.

The exact base is `ba82555c64e1879e4b7decce28186f208fcb8262`.
Its accepted conditional kappa is `1672188119205421/1000000000000000000`,
from PR1042. [BASE-SELECTED.json](BASE-SELECTED.json) preserves that selection.
The actual construction inputs are the `slots/local/` members of
`research/community-frontier1042-audit/selected-replay.tar.gz`.
The retained `gauge44-slots-t16/evidence/local/` files describe an R492 ancestor
and are not used by this contribution.
The [maintainer review](../../docs/research/community-batch1047-review.md)
identifies the mutable-leaver, seven-slot and T16 construction chain.

## Reproduce

From the repository root, run this offline command with Python 3.12:

```sh
python3 -I -O -B research/selected-k8-sign-seed38/check.py
```

Expected final line:

```text
PASS_SELECTED_K8_SIGN_PACKAGE runs=2166+2166 columns=713 saved=408/408 controls=120 no_new_kappa
```

The command writes nothing. It reconstructs both complete primitive streams,
compares the full deterministic receipt, and runs the mathematical controls.
All acceptance conditions remain active with Python optimization enabled.
No third-party packages, native compiler, cached replay or Git checkout are required.

Additional arithmetic, source-corruption and relocation checks:

```sh
python3 -I -O -B research/selected-k8-sign-seed38/test_package.py
```

Expected: four tests pass. The tests include 10,000 differential arithmetic
steps and a minimal offline relocation with the pinned source archive.

## Construction and completed coverage

The compiler transforms each maximal same-frame scalar run independently.
It defers register negations, adjusts the signs of additions, and propagates
signs through copies. It pays every remaining negation at the run boundary.
Every non-scalar event and every literal frame change terminates a run.
No sign state crosses a physical boundary.

Both orientations contain 24,767 events, 19,693 scalar macros and 2,166 runs.
Each orientation has 29 changed runs and 2,137 runs with zero cost change.
No run increases cost on these pinned inputs.

| Changed run class, per orientation | Runs | Real primitives saved |
| --- | ---: | ---: |
| Frame-zero run starting at event 8176 | 1 | 128 |
| Short helper runs, frames `37 + 29*k`, `0 <= k < 14` | 14 | 56 |
| Longer helper runs, the same fourteen frames | 14 | 224 |
| Total | 29 | 408 |

[EXPECTED.json](EXPECTED.json) identifies every changed interval, its exact
cost and its arbitrary-input endpoint digest. It also records every zero-gain
run through the complete census and the complete boundary-map digest.
The new circuit is exactly the pinned predecessor compiler applied to each
run after the pinned PR696 lowering. Full emitted-stream hashes authenticate
both orientations without committing another large generated stream.

The OS-generated assignment seed is **38**, selecting the complex-supplier track.
It selects the third candidate and backward-first verification.
The domain covers every run in both frozen programs, with no sampling or timeout.
The stopping rule is one complete census, exact boundary verification and packaging.
This is a finite application, not a shortest-circuit search or an optimality claim.
[CLAIM.json](CLAIM.json) records the candidates, overlap inspection and local claim.
No pinned sprint coordination issue existed.

## Exactness and accounting

[verify.py](verify.py) uses sparse `Fraction` rows.
[independent.py](independent.py) uses normalized integer rows with dyadic denominators.
The second implementation independently reconstructs the lowering, run boundaries
and sign compiler. It imports neither `Fraction` nor the primary or predecessor code.
Both implementations reproduce every field of the same receipt, including stream
hashes, costs, run maps, access order, prefix measurements and paid profiles.
Both implementations come from the same AI-assisted contribution.

A fresh basis at each run checks its complete linear map on arbitrary dirty inputs.
Touched registers receive explicit columns. Untouched registers retain identity
columns and cannot occur in a changed instruction. The complete scalar projection
also runs on all **704 logical plus nine arbitrary private input columns**.
This avoids treating a clean-input identity as a dirty-workspace substitution.

Every register's maximum row-L1 norm and denominator depth agree at each run.
The sign invariant proves coefficient magnitudes agree at corresponding prefixes.
The scalar-only projection also has unchanged row-L1 maxima of **131088 forward**
and **1154896 backward**, with four and seventeen fractional bits respectively.
These projection measurements exclude non-scalar semantics and do not reduce
the inherited physical precision allocation.

All 480 helper columns retain their original boundary maps.
All nine private registers erase in the complete scalar projection.
The non-negation instruction sequence retains exactly the same registers and order.
Copies, clears, shifts and source accesses therefore receive the same charges.
Only the number of physical negations changes: **560 to 356 per real component**.
The complete paid profile remains
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` in either orientation.
No helper, frame transition, restoration or recursive child is added or omitted.
Since this profile is unchanged, no exponent improvement follows from these counts.

The command rejects 116 actual-run mutants: 30 missing boundary negations,
28 missing target updates, and 58 wrong addition signs.
Four additional controls reject a prefix excursion, dirty-work mistakes and
cross-frame sign cancellation. A positive copy-fanout control demonstrates that
this compiler can increase cost on other inputs. The [proof](PROOF.md) explains
why a universal saving theorem is not claimed.

## Provenance, overlap and remaining scope

[SOURCE-PINS.json](SOURCE-PINS.json) binds all four consumed repository inputs.
The published source archive, code and replay receipt have exact byte pins.
Five archive members have separate payload pins. Compressed member pins cover
decompressed bytes, and a canonical content hash identifies the selected R480 word.
The replay receipt binds each original member and the selected assembly.
The frozen selected context has its own hash. The audited PR1042 source head is
`7e8ef087c02a77038a28a337a7ee3a77039cac0d`.

- **Ross Richardson, [PR919](https://github.com/CrocSwap/integer-mult-bounds/pull/919):**
  the sign method, compiler and historical CK evidence. Inspected head:
  `79ee104a90c3c7c244362cce74997fce37923ce9`.
  This package claims the current k8 transfer, not priority for the method.
- **Sagar Thakrar, [PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696):**
  the retained copy/unit lowering and arbitrary-dirty-work convention.
  Reviewed source head: `5a3f983715027c4fd83f50bc9001d4b18463bed1`.
- **Jeremy Kothe, PR1004/1005/1018/1022/1028/1031/1042:** the selected scalar word.
  The selected chain credits Rohan Arun's PR987 slots, Hao Yan's T16 controller,
  Chafik Boukhalfa's frames, icekylinx's gauge and the retained predecessor lineage.
  DreamingOfClouds' PR589 on eumemic's PR555 remains the selected bit supplier.
- **PR1115 and PR1118:** distinct U8 shear rewrites and historical CK coefficient
  synthesis. Those claimed classes caused the first two candidates to be rejected.
  Their code and savings are not composed here.
- **woklerx, [PR1132](https://github.com/CrocSwap/integer-mult-bounds/pull/1132):**
  the concurrent R492/R480 provenance reconciliation exposed the wrong-input trap
  during final overlap inspection. It caused the input correction before submission.
  Inspected head: `36a82dd551cd18b8b32c2013ba928f59ad52678c`.
  Its pending code is not an implementation dependency.
- **PR883/916 and PR932:** historical X4 precondition and compensation constructions.
  This package does not claim superiority over those different replacements.
- **PR1143 and PR1142:** commuting-ADD frame barriers and full replay-capsule closure.
  This contribution changes primitive sign handling within fixed runs.
  Its five-member source binding does not claim a full capsule audit.

Native Clifford/frame/wrapper execution, production-emitter integration, whole-call
hosting, the global invoice and outer assembly remain separate obligations.
The retained native receipt authenticates the original source, not a new native replay.
All-size compilation, common-label/mutable-source realization, precision/tape,
exact recovery, analytic transfer and bit H1-H5 assumptions remain inherited.
Finite scalar identities do not formally prove the full multiplication theorem.

This contribution adds only this package. It leaves the selected frontier and
`upstream/` unchanged. New material is Apache-2.0. Predecessor code stays in its
original location with its original attribution and license.
Prepared through **@Scratch-net with substantial OpenAI Codex assistance** in
research, implementation, proof writing, verification and packaging.
No independent human review is claimed.
See [VALIDATION.md](VALIDATION.md) for execution evidence and the final overlap check.
