# Every selected zero-frame precondition cut has the same centre reader

**Scoped negative result; no new kappa.** Moving the proposed unitary action
earlier through any of the selected word's 7,400 zero-frame precondition gates
does not evade [PR2491](https://github.com/CrocSwap/integer-mult-bounds/pull/2491).
The complete physical eight-centre reader is identical at all 7,401 cuts.
Consequently the same full-dirty-input obstruction excludes every paired
four-cycle output block permutation at every one of those cuts.

The decisive fact is simpler than transporting Gram matrices through a general
nonunitary prefix: **all 7,400 gates write only to fields 112 through 223, and
the reader has zero columns on all 112 of those target fields.** This was not
assumed for a different prefix or deduced merely from invertibility.

| Exact covered object | Result |
|---|---|
| Precondition scalar word | 7,344 ADDs and 56 nonzero scales |
| Write destinations | Exactly the 112 Y fields, indices 112..223 |
| Arbitrary input fields | 704, including all 480 dirty helpers |
| Active scalar reader columns | 227; none is a Y field |
| Cut positions | 0..7400 after that many precondition gates |
| Complete reader entries checked at each cut | 8 × 704 = 5,632 |
| Distinct full readers / Gram diagonals | One / one |
| Paired four-cycle output permutations | 1,260, all excluded at every cut |

The diagonal Gram coefficients remain
`(150,130,146,134,122,126,142,146)`. No value occurs four times.
The 9,325,260 cut/permutation consequences are certified by a complete cut
invariance check and a complete permutation census, not by repeating the same
permutation loop 7,401 times. The receipt compresses the constant cut table into
the exact interval `[0,7400]` and retains the full reader and all 1,260 witnesses.

## Proof and actual native boundary

Let H be the payload Hilbert space and let M be the physical reader at the
post-precondition, pre-entry-adapter cut of PR2491. Its authenticated typed
prefix proof gives

`M = T_out (A tensor I_H) U`,

where U is block diagonal over all 704 input fields and unitary, T_out is block
diagonal and unitary, and A is the exact 8-by-704 rational reader. The eight
centres are `(92,57,81,224,11,240,9,256)`, with output frames 415..422. The source
reader segment is the half-open emitted-event interval `[7401,12550)`; it
contains 704 entry adapters, 3,451 scalar gates and 992 frame climbs.

The new replay checks every column of A against the pinned PR2491 certificate,
and verifies `A[:,112:224]=0`. Since U is block diagonal, **M vanishes on the
entire physical Y subspace**, without assuming any Clifford operator preserves
constants or identifying physical and logical coordinates.

Here is the general annihilated-write lemma. If a linear map M vanishes on a
subspace Y and `range(C-I)` is contained in Y, then `MC=M`. A composition of
such maps has the same property, since each factor individually preserves M.
No unitarity of C and no commutation between C and U are required.

For each actual physical precondition gate C_j, every modified field is a Y
field, so `range(C_j-I)` is contained in Y. Thus, at cut k, the suffix of the
precondition program satisfies

`M_k = M C_7400 ... C_(k+1) = M`, for every `0 <= k <= 7400`.

The pinned gates are invertible: ADD operands are distinct and each scale is
nonzero. Every input at each cut is therefore arbitrary and attainable; there
is no hidden promise that workspace is clean. The actual 352 touched fields
also have start frame zero and avoid all 240 residual-adapter fields, but that
extra calibration is **not needed** by the annihilated-write lemma.

PR2491's exact frame factorization now gives
`(M_k M_k*)_ii = (A A^T)_ii I_H` at every audited cut. If a unitary input action P
and a unitary output block permutation Q satisfy `M_k P = Q M_k`, then
`M_k M_k* = Q M_k M_k* Q*`. Hence the scalar diagonal coefficients must be
equal along each output cycle, including when each edge carries its own
unitary payload map. No diagonal value occurs four times, ruling out two
four-cycles. Both physical output permutations and frame-conjugated output
permutations are included, as in the predecessor.

This is a written operator argument for every H to which the retained exact
frame identities apply, plus a finite exhaustive census of the selected word's
cuts. It is not a formal-kernel proof, a fresh native compiler audit, an all-size
supplier proof, or a universal obstruction to changed cuts.

## Evidence, independence and defect controls

`verify.py` authenticates the selected archive, seven exact archive members and
the retained PR2491 files before importing its credited typed-segment checker.
It newly reconstructs A by reverse Fraction covectors and pulls back through
every precondition gate, checking the entire reader at every cut. It compares
the complete committed `RESULT.json`; normal replay does not generate or repair
missing evidence. `--write-result` is explicit and refuses an existing result.

`independent.py` imports neither verifier. It constructs all 704 symbolic rows
forward using integer-dyadic arithmetic, then removes prefix gates
chronologically by inverse column operations. The two recurrences agree on all
readers and Gram coefficients. Its proof review is in `REVIEW.md`; this is
separate AI-assisted verification, not independent human review.

Controls change actual ADD and scale destinations to a reader-visible field,
omit helper dependence, corrupt fixed evidence and source bytes, and exercise
a noncommuting two-shear fixture. Actual prefix sign changes and reordering
are accepted: their writes remain in the reader's kernel, so rejecting those
as reader errors would be incorrect. A separate exact fixture takes
`A=diag(1,...,8)` and `C=A^-1`; then `AC=I`, which admits paired cycles although
A does not. This shows why generic invertibility does not transfer the old
Gram obstruction and why the source-bound write-subspace condition matters.
The package tests also remove the named write-subspace guard and confirm its
dedicated fault test stops rejecting the intended fault.

## Reproduce

From the repository root, standard-library Python only:

```sh
python3.12 -I -B scripts/research_package.py --package research/selected-reader-precondition-cuts
python3.14 -I -B -O research/selected-reader-precondition-cuts/verify.py
python3.14 -I -B -O research/selected-reader-precondition-cuts/independent.py
```

The source base is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The exact scientific predecessor is PR2491 at
`c25a4ce22a887daf8cba8b3cfad72796752ab2ee`; `PREDECESSOR.json` preserves its file
Git blobs, SHA256 values and authorship. `SOURCES.json` pins the selected archive
and original selection metadata. The task-picker draw is explicitly changed
from `bit-helper-contract` to this live missing-interface audit; it does not
claim to complete a bit H2/K replacement. The claim is in
[Discussion2488](https://github.com/CrocSwap/integer-mult-bounds/discussions/2488#discussioncomment-18950286).

Local exact checks and hosted CI are separate. No full selected cold replay,
new invoice, selected record change, hosted-CI success or supplier admission
is asserted by this package.

## Open next questions

Choose a genuinely changed reader: a cut after reader-active operations,
different copied totals, output rescaling, or a paid nonunitary input action.
Start by reconstructing the complete dirty-input native reader and Gram blocks
at that named cut. Earlier placement **within this precondition prefix** is now
covered and need not be searched again. Even an algebraic intertwiner still
needs literal native child-cost correspondence, source/target restoration,
owner placement, routing and precision; PR2500's separate cost distinction
continues to apply. No next numerical kappa claim follows from this obstruction.

## Attribution and license

New cut-invariance proof, checks and packaging by Ross Richardson with substantial
OpenAI Codex assistance, including a separate mathematical specialist; Apache-2.0.
Credit ywz65/PR2491 for the full dirty reader, native factorization, Gram
obstruction and explicit changed-cut question; its retained files remain exact.
Credit Aaron Wang/PR2464, Cinna Davis/PR1391 and PR1410, Ross Richardson/PR2500,
Sagar Thakrar and the retained typed-echo lineage. The selected construction is
Rohan Arun's PR1094 on Jeremy Kothe's word with the credited DreamingOfClouds,
icekylinx, chafreaky and preceding geometry/compiler contributions. The work does
not claim priority for the predecessor obstruction or its native compiler.
