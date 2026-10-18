# A shortest three-ADD replacement for one rank-seven restore block

This package shortens one literal block in both of dcharb78's [PR3042][3042]
words. Restore has **211 rather than 212 gates**. Its derived inverse cleanup
has **5,215 rather than 5,216 gates**. The replacement uses no new register,
frame or scalar coefficient outside the inherited dyadic alphabet.

The recursive paid profile is unchanged. This is a scalar-program improvement,
not a new κ or a measured physical speedup. Frozen predecessors and the selected
frontier are unchanged.

## Exact replacement

PR3042 head `84cc406ad91ec53fff329a11a445d7effe564a77`,
`edits/FINAL-WORD-{base,extra}.json.gz`, has the following zero-based
restore slice `[175:179]`. Every gate uses the same rank-seven frame
`[256,128,64,38,20,10,1]`. Set `x = X22` and `y = X230`.

```text
before                 after
x -= y                 y += x
y += x                 x -= y
x -= y                 y += 2*x
y += x
```

Both maps send arbitrary dirty inputs `(x,y)` to `(-y,x-y)`. Other registers
are unchanged. `contract.py` checks the literal preimage, replaces this one
slice and derives inverse cleanup from the actual new forward body.

The matrix identity also holds for a common linear idempotent `P`, not just
scalar substitutions. In `Q[P]/(P²-P)`, both projected programs have matrix

```text
[ I-P    -P  ]
[  P    I-2P ]
```

Equivalently, the map is `(-y,x-y)` on the image of `P` and identity on its
kernel. `projected_block` checks this exact polynomial identity. The tests
include a nonorthogonal rational idempotent and a non-idempotent failure
control. A common frame matters; ordinary scalar equality alone would not
justify changing frames.

### Three gates are necessary in the stated alphabet

Allow either elementary ADD direction with any rational coefficient, or an
invertible SCALE of either row. A product of at most two ADDs always has a
unit diagonal entry. A product involving a SCALE and at most one ADD has a
zero off-diagonal entry. Two SCALEs are diagonal. The required matrix
`[[0,-1],[1,-1]]` has neither property. Thus at least three gates are necessary,
and the displayed dyadic ADD sequence attains the bound.

`minimality.py` checks all 16 ordered pairs of gate kinds with independent
symbolic coefficients. Every pair has a constant entry inconsistent with the
target, for every rational coefficient choice. Identity SCALEs pad words of
length zero or one, so these cases are covered too. The inverse matrix
`[[-1,1],[-1,0]]` has the same three-gate minimum, checked separately.
This is not a finite coefficient search. The minimum concerns these
two-register maps and alphabet; no whole-word optimality or general circuit
lower bound is claimed.

## Complete bill and boundary

The checker compares the full 704-column rational restore operators. Equality
is on arbitrary dirty register values, not just reachable or sampled states.
Consequently the block can replace its predecessor in any unchanged scalar
context. It also preserves the inverse and dual operator.

For both providers, finite-set frame enumeration checks all A, B and restore
gates, A/B warp boundaries, centre cuts and final endpoints. Every register's
ordered sequence of frame-dimension jumps is unchanged. So are all 408 ordered
helper widths, 91 private buffers and every other word section except restore
and cleanup. Both source cleanups and the derived new cleanups are checked.
The inverse cleanup changes only `[33:37]` to a three-gate hunk. Its exact
operator is checked separately on register 22 and private buffer 934, for
arbitrary dirty buffer values. The frame checker is reused byte-for-byte
from [PR3050][3050], not presented as a new independent implementation.

The PR3042 local profile remains

```text
{1:2433, 2:712, 3:232, 4:108, 5:18, 8:8}
```

The unchanged T74 allocation and call boundaries therefore retain the complete
profile, conditional on their inherited legality:

```text
{1:1637688, 2:474192, 3:159468, 4:71928,
 5:13716, 8:5328, 48:28190}
rank mass = 4816512 = 74 * 65088
physical families = 66304 + 408 + 8 + 91 + 2 = 66813
```

`whole_bill` reconciles the pinned source invoice with PR2979's retained
profile and PR3042's `666 * (-12 H1 + 6 H2)` delta. The contraction adds no
further delta. Thus it changes neither the recursive moment nor its packing
ceiling. The two removed gates are listed scalar ADDs, not a certified saving
of two native instructions. Native lowering can expand or combine scalar gates.

## Reproduce

Python 3.12 and its standard library suffice. No network or in-checkout output
is needed. The registered replay takes about two seconds on the measured host.

```sh
python3.12 -B scripts/research_package.py \
  --package research/rank7-restore-contraction
```

With `RUN` an existing session-owned external output directory:

```sh
python3.12 -W error -B research/rank7-restore-contraction/verify.py > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-restore-contraction/evidence/RESULT.json
python3.12 -W error -B research/rank7-restore-contraction/verify.py \
  --emit-word base > "$RUN/WORD-base.json"
python3.12 -W error -B research/rank7-restore-contraction/verify.py \
  --emit-word extra > "$RUN/WORD-extra.json"
```

Emission first runs the full finite audit. The receipt records canonical
uncompressed word hashes; JSON formatting and gzip containers are not proof
criteria. [VENDOR.json](VENDOR.json) pins the exact PR3042 inputs and retained
frame checker. [SOURCES.json](SOURCES.json) pins main's invoice dependency.
Fourteen test groups cover actual emitted words, arbitrary dirty states,
symbolic templates and rejecting semantic, frame, cleanup, source and invoice
controls. [ENGINEERING.md](ENGINEERING.md) records diagnostic commands and limits.

## Scope and decision

Base main is `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The assigned scope is an explicit override of `complex-new-helper-inventory`.
Inspection did not justify another paid-profile source-sharing construction;
this one bounded pivot retains a useful scalar contraction. It does **not**
meet that card's new-inventory or ceiling-improvement target. The selected
source-binding baseline and the card's packing-ceiling positive control pass.

This is an author-checked finite identity and source application, not
independent human or formal-kernel review. The general elementary-matrix
algebra is standard; the contribution is its pinned application, inverse
cleanup and complete unchanged-cost check. No fresh native/compiler,
ownership, movement/backing, prefix/magnitude, precision/tape, all-size,
recursive caller, analytic or modern-outer release is run here. Inherited
supplier premises remain premises. The separate PR3042+T740 release claim
is not taken over or certified by this package.

## Open next questions

Does the actual inherited native compiler emit fewer primitives for the
contracted block and its inverse? This determines whether the listed scalar
saving survives lowering. Export the two words above, bind them into PR3042's
existing replay chain, and compare exact native primitive counts with the
pinned source. That requires a separate replay/admission budget; no physical
speedup follows from the gate counts alone. No further census is justified
by this local contraction.

## Credit

Nick Petalas contributed the contraction, shortest-block proof and verification
package. Credit dcharb78 for PR3042's six-skip restore words, Jeremy Kothe for
PR3015's original restore edit and declared-edit interface, and Marius-Paul
Dumitrean for PR2979's words and allocation. PR3050 supplies the unchanged
finite-set frame checker. The retained [credits](vendor/CREDITS.md) and
[notice](vendor/NOTICE) preserve Mason Hale, Jeremy Diviney, Yiyang Lu,
Tekalign, Ross Richardson, Dugongue, icekylinx, themilkman216 and the
geometry/native/owner lineage. Apache-2.0. Development used substantial
automated assistance.

[3042]: https://github.com/CrocSwap/integer-mult-bounds/pull/3042
[3050]: https://github.com/CrocSwap/integer-mult-bounds/pull/3050
