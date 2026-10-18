# Complete scalar layer with one clean carry

The complete PR3094 prelude/A scalar layer admits a one-clean-carry
implementation when each macro can exclusively borrow and restore a second
operand bank. At 64-bit input precision (`W=84`), all 9,992 macros per
provider/orientation use **82 fewer clean carry bits** and **1,938,818 fewer
unweighted logical Boolean gates**. Both providers and orientations give:

| Both real components | CNOTs | Toffolis | Clean carry bits |
|---|---:|---:|---:|
| PR3094 direct caller | 6,806,482 | 6,426,884 | 83 |
| One-carry caller | 7,677,700 | 3,616,848 | 1 |

CNOTs increase by 871,218; Toffolis decrease by 2,810,036. These are logical
circuit counts, not a runtime or kappa improvement. At every supported width
`23 <= W <= 256`, the combined saving is exactly `25108W−170254` gates.
The two W-bit operand banks are additional to the carry. For ADD, the source
is temporarily writable and restored; for SCALE, a disjoint arbitrary dirty
bank must be supplied and is restored. No native ownership assignment for
that SCALE bank is provided. This changes PR3094's gate-level read-only
source contract.

The construction extends PR3081's credited MAJ/UMA wired half-ADD to every
signed-power ADD in the actual stream. Negation uses three modular shears
and a swap, avoiding a full clean carry bank even for negative SCALEs.
Other SCALE shifts retain their literal inherited circuits and guards.
The source bytes, frames, recursive children and cleanup contract stay frozen.

[PROOF.md](PROOF.md) derives the identities, restoration and exact uniform
invoice. [RESULT.json](RESULT.json) records fresh native/capacity bindings,
all four dispatch hashes and circuit hashes. Cold replay passes 124 exhaustive
small circuits with 314,560 complete truth columns, their literal inverses,
and 1,550 fixtures evaluated with a separate Boolean-list interpreter.
Twelve behavioral groups cover sign/cleanup mutants, dirty carry, alignment,
overflow, source corruption and malformed ownership/width boundaries.
The inherited native engine is executed, not independently reimplemented.

## Reproduce

Python 3.12, standard library only. From the repository root, choose a fresh
external directory and run:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/one-carry-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  uv run --python 3.12 --no-project python -W error -B \
  research/rank7-one-carry-scalars/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-one-carry-scalars/RESULT.json
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/test-bytecode" \
  uv run --python 3.12 --no-project python -O -W error -B \
  research/rank7-one-carry-scalars/test_scalars.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-one-carry-scalars
```

Without `--work`, replay removes its temporary outputs beneath TMPDIR.
[SOURCES.json](SOURCES.json) authenticates all 30 live predecessor inputs
before import; [VERIFY.json](VERIFY.json) declares them for CI invalidation.
No predecessor is copied or edited. Direct replay needs the declared source
files but no Git/network; the generic provenance check needs Git history.
[ENGINEERING.md](ENGINEERING.md) records bounds and verification limits.

## Open next questions

Can one literal native SCALE event borrow an actual dirty W-bit bank with
exclusive access and return it before the next cut? Name the owner, lifetime,
entry format and complete movement cost before lowering that event. No physical
bank assignment or access tariff is established by the circuit template.

Can the complete producer and consumer retain the one-carry saving? Price
residual adapters, frame/warp/climb operations, recursive children, stock,
routing and eventual cleanup on the same layout. [TASK.json](TASK.json)
records the obligation ledger and decision to stop at this scalar composition.
The recursive rank profile, moment, selected kappa and full supplier admission
remain unchanged; this is not a complete multiplication theorem.

## Credit

Nick Petalas contributed the complete scalar composition, dirty-bank negation,
source-bound invoice and proof. Cuccaro, Draper, Kutin and Moulton supply the
MAJ/UMA adder; PR3081 already realizes the local wired dyadic ADD, and PR3088
shares its sign-fill across four physical ADDs. PR3094 supplies the complete
scalar guard/binding baseline and retained PR3090/3080 sources. No novelty
is claimed for those primitives, signed powers or elementary modular shears.

The retained lineage includes PR3078/3076/3060/3056, dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
DLamdata, eumemic, icekylinx, Tekalign and the credited native, geometry and
owner contributors. Original source notices remain at their pinned paths.
New work is Apache-2.0. Development and internal read-only review used substantial
automated assistance; no independent human or proof-kernel review is claimed.
