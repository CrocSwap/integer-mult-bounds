# Every intermediate frame is necessary in the 14 proportional triples

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

This is a source-bound obstruction for a declared carrier-recoding model. It
does not claim a new multiplier, a new kappa, or a global native optimum.

## 1. Domain and exact census

The input is the exact #6702 native word used by #6726, with compressed SHA256
`e8c7a9d54d98a4cfa27e15593016b3908afed303e0f480076ed3f596192e5a4d`.
Eligible intervals are exactly those of #6765/#6767: two consecutive forward
MOVEs on a public helper, at least one intermediate ADD export, and only SCALE
writes to that helper between the MOVEs. Actual main roles `live` and
`live+112` are excluded; unused main-register slots remain eligible.

An exact rational replay on all 771 public old inputs gives 631 intervals in
523 projective held-row classes: 429 singletons, 80 doubletons and 14 triples.
The complete source endpoint on all 800 fields and its COPY-zero condition are
checked. Each triple consists of consecutive intervals on one helper:

    A -> B -> C -> D -> E

There are exactly four unique old MOVEs. Each held row is nonzero and the
helper receives only MOVE/SCALE writes over its combined window. The four
paid ranks and all removed ADDs are reconstructed from the exact word.
The frame labels encode GF(2) basis lists. Their actual spans are nested along
each of these 14 chains, and each relevant span has a unique frame ID in the
word, so the residence census does not miss an equivalent differently encoded
carrier frame.

## 2. Allowed recoding and a single common target

Fix one triple. Let `i,j` be its first/last MOVE. Let `lo` be immediately
after the previous non-SCALE helper write, and `hi` the next non-SCALE helper
write after `j`, with program endpoints if absent. The old row of the helper
is `a(t)v` throughout cuts `lo..hi`, where `v` is its nonzero row at `i` and
`a(t)` is a nonzero rational scalar. Source SCALEs retain their scalar action
and follow the retimed helper. Every other field's scalar program and residence
history remain fixed.

A topology retains A/E and any proper subset of B/C/D. It deletes every
original helper export strictly between `i` and `j`. It may insert arbitrarily
many ADDs with arbitrary rational coefficients from the helper into any other
public or live owned field resident at a retained frame. The helper cannot be
a recipient. Original exports at retained frames may be reinserted, so the
delete-all convention also represents schedules that keep those original
exports. No final constraint is imposed on any full-bank public output,
granting arbitrary free cleanup there. Proper public outputs and the actual
COPY pre-zero observable remain constrained. Dirty owned CLEAR is allowed.

**The deleted-export target D is identical for all seven topologies.** It is
the sum of the original response of every deleted export, including exports
whose frame is retained. Reinstating any of those exports simply contributes
its original response as an allowed new injection. This common-target
formulation is essential for the subset argument below; it is not legitimate
to compare changing targets merely because column inventories are nested.

## 3. Chronology and its sound relaxation

A cut `t` occurs before old instruction `t`. Retained outer reads impose

    lower = max(lo, 1 + every retained A-read before i),
    upper = min(hi, every retained E-read after j).

For a retained frame list `F0=A,F1,...,Fm=E`, a legal path has ordered cuts
`lower <= t1 <= ... <= tm <= upper`; injections at Fk occur in its residence
window between neighboring cuts (and `lo`/`hi` at the endpoints). Equal cuts
may be interpreted as ordered MOVEs and injections at the same old cut. This
admits one-, two- and three-cut systems. Additional legality restrictions can
only remove schedules.

Our obstruction deliberately grants more than all these systems. For each
retained frame F, collect the unchanged suffix-response vector of every other
public or live owned field at **every** cut in `lo..hi` where it is resident
at F, whether or not a single helper schedule can realize those choices
together. A response and its frame are constant between field touches, so the
finite residence census represents this complete union. Every chronological
column set is a subset of this union. Therefore failure of the union span
excludes every cut system without sampling or enumerating cut tuples.

## 4. Why a response span is necessary

Let S(t,r) be the suffix response from adding one scalar unit to recipient r
at cut t, observed on proper final public outputs and the COPY pre-zero row.
The COPY instruction is treated as ADD together with its precondition row;
CLEAR erases an owned perturbation. All later feedback after `hi` is included
in this suffix response.

The helper has no recipient-dependent write within `lo..hi`; consequently
recipient perturbations cannot alter its source row before any deleted or
inserted export. Deleting all original exports changes the observed all-input
matrix by `-D tensor v`. An inserted ADD with coefficient b contributes
`b a(t) S(t,r) tensor v`. This identity holds simultaneously for arbitrarily
many injections; it does not assume that pairs fail independently. The direct
forward combined-error replay additionally checks the sum for every triple.

Because v is nonzero, preserving every old input requires

    D = sum b a(t) S(t,r).

Thus D must lie in the rational span of the allowed residence columns. No
finite bound on the number of injections is assumed.

## 5. Forty-two exact separators cover all 98 topologies

For each of 14 triples and each one of B/C/D, form the maximal retained-frame
inventory that omits just that frame. The certificate gives a rational linear
functional lambda satisfying, over Q exactly,

    lambda(S) = 0  for every column in that entire time-union inventory,
    lambda(D) = 1.

There are 42 such certificates. Their coefficients belong to
`{-3,-2,-1,-1/2,1,2,4}`. Every proper subset of B/C/D omits at least one frame,
so its entire time-union inventory is contained in one of these maximal
inventories, with the same D. Hence all seven topologies for all 14 triples
fail: **98 topologies, including all 14 complete four-to-one fusions**.

All computations used for acceptance are rational identities. A modular
exploration suggested these witnesses, but no finite-field lifting premise or
denominator restriction enters the theorem. In particular arbitrary rational
injection coefficients, hence all dyadic coefficients, are excluded.

## 6. Exact shared-MOVE bill and limits

Let the unique old MOVE ranks be r1,r2,r3,r4. Their bill is
`H(r1)+H(r2)+H(r3)+H(r4)`, with each shared MOVE counted once. Retaining frame
indices `0=k0<k1<...<km=4` replaces this by
`sum_j H(r_(k(j-1)+1)+...+r_kj)`. The direct fusion uses `H(r1+r2+r3+r4)`.
The certificate records all seven resulting rank lists per triple. These are
complete transport comparisons inside this fixed edit; they do not furnish a
paying construction because the necessary endpoint condition already fails.

The result does not cover changing source rows, recipient histories, a new
source basis, interacting different helpers, arbitrary new carrier frames,
additional deleted exports outside the window, or changed output contracts.
It excludes only the stated exact native word and the stated fixed-source
recoding class. All five framework assumptions remain. It does not update the
selected result or establish full formal verification of integer multiplication.

## 7. Inspectable exact functionals and three necessary constraints

Here `x_r` denotes coordinate r of the observed final public response, not an
old-input coefficient. Every listed coordinate is a constrained proper output.
The three columns are the exact functionals when B, C or D is omitted.

| Helper | Four unique old ranks | Omit B | Omit C | Omit D |
| --- | --- | --- | --- | --- |
| 226 | 1, 2, 1, 1 | $-x_{226} + x_{485}$ | $-2x_{213}$ | $-2x_{214}$ |
| 230 | 1, 2, 1, 2 | $-2x_{219}$ | $-2x_{220}$ | $-2x_{221}$ |
| 232 | 3, 1, 1, 1 | $x_{171}$ | $x_{172}$ | $-x_{227} + x_{234}$ |
| 236 | 3, 1, 1, 1 | $x_{208}$ | $x_{209}$ | $-x_{234}$ |
| 299 | 2, 1, 2, 1 | $-2x_{150}$ | $-2x_{199}$ | $-x_{297}$ |
| 329 | 1, 1, 1, 4 | $-2x_{221}$ | $-2x_{219} + 2x_{223}$ | $x_{325}$ |
| 395 | 2, 1, 2, 1 | $-2x_{207}$ | $2x_{204}$ | $-\frac{1}{2}x_{393}$ |
| 434 | 3, 1, 1, 1 | $2x_{138} + 2x_{223}$ | $2x_{200} + 2x_{223}$ | $-2x_{223} - 2x_{435}$ |
| 436 | 1, 2, 1, 2 | $-2x_{210} + 4x_{223}$ | $2x_{198} + 4x_{223}$ | $-2x_{118} + 4x_{223}$ |
| 438 | 2, 1, 1, 1 | $-2x_{170}$ | $-2x_{160}$ | $-x_{585}$ |
| 440 | 3, 1, 1, 1 | $-x_{172} - 2x_{223}$ | $x_{220} - x_{223}$ | $x_{220} - x_{221} - x_{223} - x_{587}$ |
| 444 | 3, 1, 1, 1 | $-x_{209} - x_{223}$ | $-x_{181} - 3x_{223}$ | $-x_{214} + x_{435} - x_{589}$ |
| 446 | 3, 1, 1, 1 | $x_{208} + 2x_{223}$ | $x_{180} + 2x_{223}$ | $-x_{218} + x_{223} - x_{590}$ |
| 449 | 2, 1, 1, 1 | $-2x_{143}$ | $-2x_{212}$ | $-2x_{214} - x_{226}$ |

For each triple, write `Lambda = (lambda_B, lambda_C, lambda_D)`. The
certificate gives `Lambda(D)=(1,1,1)`. Every column at A or E has image zero;
a column at B, C or D can affect only its corresponding coordinate. Indeed,
each of the other two maximal omission certificates includes that frame and
annihilates its complete residence inventory. In particular, if `D_B,D_C,D_D`
are the original export contributions grouped by frame, then
`lambda_j(D_k)` is exactly the Kronecker delta. This is also an explicit
three-dimensional collection of necessary response constraints for any
proposed new carrier inventory.

A new column that has a nonzero missing coordinate can invalidate one
separator; that alone is insufficient for construction. Its projected columns
must supply all missing coordinates, and its actual chronological delivery
and complete cost must still be established. All 42 witnesses already separate
using final proper outputs alone; the COPY monitor is nevertheless retained
in both complete response reconstructions.
