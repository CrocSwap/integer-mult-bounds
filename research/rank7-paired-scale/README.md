# Paired Gaussian SCALE without a separate dirty bank

The complete prelude/A scalar layer of the pinned PR3076 providers can execute
every negative SCALE using its own real and imaginary target words and one
clean carry. A four-shear modular circuit replaces PR3152's two separate real
negations. At `W=84`, it saves **700,392 logical gates** per complete layer in
both providers and orientations. The separate dirty-bank requirement for SCALE
is eliminated at the logical circuit boundary.

| Complete scalar layer, both components | CNOTs | Toffolis |
|---|---:|---:|
| PR3152 one-carry predecessor | 7,677,700 | 3,616,848 |
| Paired SCALE | 7,132,540 | 3,461,616 |
| Saving | 545,160 | 155,232 |

This closes PR3152's logical auxiliary-bank handoff through a changed contract.
The two banks belong to the same Gaussian target. They hold arbitrary live data
and both reach their required outputs. No third component bank is borrowed.
The carry returns to zero before the next scalar event. ADD retains PR3152's
temporarily writable, restored source contract.

The source-bound example is forward native event **6872** in both providers,
`SCALE(L292, 1/-1)`. Its next event is `ADD(L333, L292, -1)`. The circuit acts
on each encoded Gaussian coordinate of L292; its whole component pair and carry
are ready before that read. Actual tape locations, routing and the price of
paired access remain open. This is a logical circuit construction and complete
scalar-subsequence invoice, not supplier admission or a new kappa.

Counts follow PR3152's convention of one encoded component pair per emitted
scalar macro. For an actual role with many coordinates, its circuit repeats
over those coordinates. This normalized scalar invoice is not the full array
or physical-access bill.

[PROOF.md](PROOF.md) gives the all-width identity, signed boundary, ownership
and tariff. [RESULT.json](RESULT.json) records fresh native/capacity bindings,
all four dispatches, the exact example and serialized SCALE-circuit hashes.
Cold replay checks 95 small circuits over 867,048 complete pair/carry truth
columns with their literal inverses, plus 540 independently interpreted
Boolean-list fixtures and 253 width tariffs. Fourteen behavioral groups test
wrong signs/coefficients, missing cleanup, invalid alignment/range, dirty carry,
foreign wires, a missing macro and altered source bytes. The native engine and
MAJ/UMA adder are inherited implementations, not independent reimplementations.

## Reproduce

Python 3.12, standard library only. From the repository root, choose a fresh
external directory:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/paired-scale-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/bytecode" \
  uv run --python 3.12 --no-project python -W error -B \
  research/rank7-paired-scale/verify.py --work "$RUN/replay" \
  > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-paired-scale/RESULT.json
TMPDIR="$RUN/tmp" PYTHONPYCACHEPREFIX="$RUN/test-bytecode" \
  uv run --python 3.12 --no-project python -O -W error -B \
  research/rank7-paired-scale/test_pairscale.py
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -B \
  scripts/research_package.py --package research/rank7-paired-scale
```

Without `--work`, replay removes its temporary outputs beneath TMPDIR.
[SOURCES.json](SOURCES.json) binds all 30 live predecessor inputs before their
import; [VERIFY.json](VERIFY.json) declares them for replay invalidation.
[UPSTREAM.json](UPSTREAM.json) separately pins the byte-identical PR3152
`scalars.py` and result receipt retained under `vendor/`, including their original
paths, Git blobs and exact head `66ee36401536625714c9937e36bbe7ef115da05f`.
Direct replay needs these files but no Git or network. The generic provenance
check additionally needs Git history. No frozen predecessor package is edited.

## Open next questions

Can an actual Gaussian layout supply this paired writable access with a paid
movement bound? Start with the named event in RESULT.json, bind both component
locations and their exclusive interval, and price all accesses and carry
movement. The logical bank assignment does not prove cheap physical access.

Can the complete producer and consumer retain the saving? Price residual
adapters, frame/warp/climb operations, recursive children, clean stock, source
access, routing and eventual cleanup on the same layout before extending the
implementation. [TASK.json](TASK.json) records the proved, constructive and
unknown obligations and the decision to stop at this local closure.
The recursive rank profile, moment and selected frontier remain unchanged.

## Credit

Nick Petalas contributed this paired implementation, complete source-bound
delta, ownership argument and proof. The modular identity is elementary;
no novelty is claimed for elementary shears or the MAJ/UMA primitive.
Cuccaro, Draper, Kutin and Moulton supply the adder. PR3152 supplies the
one-carry full scalar composition and comparator; PR3081 supplies the earlier
local one-carry dyadic ADD; PR3088, PR3094 and PR3090 supply guard, caller and
capacity predecessors. The explicit released handoff is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18996179).

The retained lineage includes PR3080/3078/3076/3060/3056, dcharb78/PR3042,
Jeremy Kothe/PR3015, Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226,
DLamdata, eumemic, icekylinx, Tekalign and the credited native, geometry and
owner contributors. Their source notices remain at the pinned input paths.
The two vendor files are retained byte-identical under Apache-2.0. New work
is Apache-2.0. Development and internal read-only review used substantial
automated assistance; no independent human or proof-kernel review is claimed.
