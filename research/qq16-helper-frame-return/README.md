# Exact QQ16 helper return versus endpoint-frame return

The literal local F0 reference returns an isolated arbitrary L224 input z as
`Gz`, where `G=C tensor-power 9` and
`C=1/2 [[1+i,1-i],[1-i,1+i]]`. All other 711 fields return zero on this input
subspace. This identifies all 512 complex input columns, not just constants.

Literal numerical restoration holds exactly on a complex 136-dimensional
subspace. The mismatch has complex rank 376 and sharp relative Hilbert error
2. A coordinate delta spreads to all 512 coordinates; a constant vector returns
literally. Nine negative coordinate lines invert G in this local reference.
[PROOF.md](PROOF.md) gives the precise statement and packing/spectral arguments.

This is a finite exact reference-contract result, not an error caused by
rounding. The source records L224's endpoint frames as 0 and 1. Frame-relative
restoration may be the intended contract, in which case this is not a defect.
A caller demanding the original common-coordinate array must instead restrict
its entry subspace or supply and charge an adapter. Norm preservation and
constant fixtures alone do not decide that contract.

## Evidence and reproduction

[RESULT.json](RESULT.json) records the source-bound all-column certificate.
The primary engine packs 512 columns using radix `2^106`; an exact norm and
denominator bound proves injectivity. The second engine uses independently
written fixed-grid Gaussian arithmetic and a Walsh-transform target. Both
execute the complete 26,099-event source dispatcher. They share that dispatcher,
source loading and the conservative packing bound. They are not independent
native-semantic implementations.

Eight behavioral groups include actual constant/nonconstant returns, a changed
literal ADD, wrong/missing coordinate lines, all 512 Walsh characters,
insufficient-radix and inexact-division controls, corruption of each of the five
live inputs, and a reclassified-input rejection. Validation stays active under
Python optimization.

From the repository root, with standard-library CPython 3.12:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/qq16-helper-frame-return
```

The direct commands in [VERIFY.json](VERIFY.json) also run without Git when the
package and its five declared inputs are exported together. Replay never writes
the committed receipt. `verify.py --write PATH` creates an absent receipt only.
[ENVIRONMENT.json](ENVIRONMENT.json) records the local environment.

All scientific/executable inputs are canonical-main bytes at
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. Exact Git blobs
and SHA256 hashes are in [SOURCES.json](SOURCES.json). No unmerged foreign Git
object is needed for cold replay. The archive members are additionally checked
by the authenticated predecessor loader.

## Scope, budget and expansion decision

Only the 512-coordinate local reference and the isolated L224 input subspace
are covered. Other data/helper input columns, every other helper, the complete
73-axis tensor payload and owner cover, B1, rounded arithmetic and a physical
caller remain outside this result. The reference's native conventions are
inherited. This is not a full-cover restoration objection or a contradiction
of the source's logical frame-relative contract.

The local inverse is constructive, but its physical routing, ownership,
movement, workspace, precision, recursive tariff and consumer charges are
unknown. No favorable complete invoice, supplier, selected-frontier change or
new kappa is claimed. The selected cold replay, Lean, Docker and independent
human/proof-kernel review were not run. Family decision: narrow and stop after
this exact caller-contract calibration, not another adapter search.

## Open next questions

Bind one actual caller's borrowed-helper entry/exit representation to the
literal frame labels. This matters because a numerical norm envelope cannot
promise bytewise restoration. First inspect whether that caller consumes L224
in frame 1 or demands its original array in frame 0. The missing caller and its
complete paid invoice block a physical repair/admission decision. If it already
accepts the frame-relative return, no repair follows from this result.

## Credit

New theorem and checks by Nick Petalas, Apache-2.0. Automated assistance was used;
no independent human or proof-kernel review is claimed. PR3226's reviewer note
already observes qualitative non-literal helper return on general inputs. That
observation is credited, not claimed as new. This package adds the exact
all-column operator, sharp fixed subspace/mismatch and explicit local inverse
for one named helper slice.

The executable dispatcher and exact Gaussian primitives are reused unchanged
from Sricharan Vagvala's PR3101 and Tekalign's PR3017. Credit commdata2338 for
PR3226/3235, Nick Petalas for PR2965/3250/3258/3270, Arham Tahir, Ross Richardson,
Ali Romman and the retained QQ16/native team, Sagar Thakrar, DLamdata, ywz65,
starship-s and Douglas Colkitt. The predecessor notices remain unchanged.
The canonical investigation is
[Discussion2727](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727).

## Verification constraints

Build the Lever produced the rerunnable packed certificate. Prove It Works
required actual source execution and a second arithmetic engine. Test Behavior,
Not Implementation required changed endpoints and rejecting controls.

Power-of-Ten deviations are limited to managed Python allocation and fixed
source loading. New loops are bounded by 26,099 events, 712 fields, 512
coordinates, nine axes, seven pins and eight test groups. Source files are
capped at 32 MB and authenticated before executable loading. Primary denominator
and coefficient bounds are capped at 128 and 2^64; radix width is capped at 196.
Together these bound integer/collection sizes, though Python allocator overhead
is not profiled and this is not a fixed-allocation machine. The authenticated
predecessor has its original bounded caches and dispatcher. Dynamic execution
loads only fixed local source bytes, not generated expressions; the second
engine shares this explicit dispatch boundary. Source-copy controls use private
context-managed temporary directories. Runtime validation uses explicit errors,
not removable assertions. Ruff E/F/B/I/UP/C4/SIM and warning-strict execution
cover new code. A deployed service, changed native contract or variable-size
input requires a separate capacity, static-analysis and dispatch review.
