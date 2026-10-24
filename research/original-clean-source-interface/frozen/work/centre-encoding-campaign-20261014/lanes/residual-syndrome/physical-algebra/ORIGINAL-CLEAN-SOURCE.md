# Clean one-core shears in the original complex frames

## Result

One raw core, with the physical ADDs below, restores all 480 arbitrary
helper contents. No helper input enters a data output. The exact data
maps are

```
forward:  (x,y) -> (x,y+D_plus x),
backward: (x,y) -> (x-D_minus y,y),
D_plus  = I-KR+KRQ,
D_minus = I-KR+KRQ^-1.
```

Here `R` is the actual eight-row centre matrix, `K=R^T/4`, and
`R R^T=56I`. The product order is part of the statement. Neither `R`
nor `K` is assumed to commute with `Q`.

The word uses the original native frames at every positive tensor
width. It needs no characteristic phase, parity restriction, second
replica, new field, new native child, or new address map. All eight
former modes again perform their complete width-nine helper jobs on
arbitrary physical input. The other 472 helper jobs are retained.

This is a local component. `D_plus` and `D_minus` need not be equal.
The changing-chart data controller and its full supplier cost remain
open. No kappa improvement or complete supplier is claimed.

## Pinned source and interface

The raw source is `history-encoding/FULL-MODE-PROGRAMS.json.gz`, with
decompressed SHA256
`f271842a741584389e166e700e262f161b0dd570ce8c7a540f2717e90ead5205`.
The eight selected helper slots are
`[225,226,229,232,241,242,257,258]`. The raw word uses no private centre
field. The matrix `R` comes from `circuit-interface/INTERFACE.json`,
whose SHA256 is
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

After the original entry alignment, the physical frames are

```
X: Q -> F,       Y: I -> F Q^-1,       u: I -> F.
```

These are the raw source's original complex frames. The common
completed exterior commutes with the local full transform. Scalar
`R` and `K` also commute with a transform applied equally to their
input and output fields. Thus the displayed physical ADDs have the
content actions used below. Expressing an arbitrary helper input in
this common reference frame is a change of coordinates in the proof;
it requires no physical preparation or matched old-owner prefix.

The raw complete content maps on the data and these eight helpers are

```
F_raw: x'=x, y'=y+(I-KR)x-Ku,       u'=-u-2Rx,
B_raw: x'=x-(I+KR)y-8Ku, y'=y,     u'=-u-Ry/4.
```

Each of the other 472 helper content rows is the identity. This
statement, together with the exact original helper frames, determines
its complete native job. The new word preserves those jobs rather
than imposing a carried-state domain on a caller.

## Forward word

Let the arbitrary mode input be `z`. Execute the following physical
operations in order:

```
u += R X_phys;
Y_phys += K u;
u -= R X_phys;

raw forward core;

u += 2 R X_phys_out;
u = -u.
```

At entry, `X_phys` contains `Qx` in the common exterior frame. The
first three ADDs return the mode to `z` and change the target content
to `y+Kz+KRQx`. The raw core then gives

```
y_out = y+Kz+KRQx+(I-KR)x-Kz = y+D_plus x,
u_out = -z-2Rx.
```

At exit, both `X_phys_out` and the mode have the common full frame.
The last ADD and negation therefore return the mode content to `z`.
The cancellation of `Kz` holds for every arbitrary mode input.

## Backward word

Execute

```
u -= R Y_phys/4;

raw backward core;

u += R Y_phys_out/8;
X_phys_out -= 8 K u;
u -= R Y_phys_out/8;
u = -u.
```

At entry, the mode becomes `z-Ry/4`. The raw core gives

```
x_raw = x-y+KRy-8Kz,
u_raw = -z,
y_raw = y.
```

The output `Y` frame is `F Q^-1`. The first output ADD therefore
changes the mode content to `-z+RQ^-1y/8`. The target ADD gives

```
x_out = x-y+KRy-KRQ^-1y = x-D_minus y.
```

The next ADD removes the query, and the final negation restores `z`.
The inverse phase on this output read is essential. Replacing it by
`Q` is not a valid version of this map.

## Scope of the algebra

The two derivations need only the stated raw maps and native frames.
They do not use `Q^4=I`, an involution, or a scalar square. In an
abstract interface, `Q` can be any invertible port operator for which
these raw maps and the common frame intertwiners hold. For the actual
supplier, `Q` is the original port-dependent complex line transform.

The following ordered identities can be used by a later controller:

```
D_plus Q^-1 + D_minus = I+Q^-1,
D_minus Q + D_plus = I+Q.
```

They follow by expansion without moving `Q` through `KR`. They do not
show that either kernel has a cheap inverse, or that nine calls with
different routed centre matrices have a free decoder. A shear with
either kernel is invertible by changing its update sign, whether or
not that kernel itself is invertible. The displayed forward and
backward maps are not mutual inverses on the same ordered data banks.

## Literal word and cost

The payload `ORIGINAL-CLEAN-SOURCE-PROGRAMS.json.gz` has decompressed
SHA256
`abfcbfc40bac24e284be63623d9b18f1bb6d4d6ec1b9fa7e9bba27330f323667`.
It gives every added physical ADD and negation, the raw core pin, and
the precise expansion order:

```
old entry alignment;
new prefix;
unchanged raw core;
new suffix;
old exit and owner view.
```

All original idle maps, stage alignments, and terminal rules remain
in force. The added opcodes specify mathematical physical operations;
this packet does not claim admission by an existing supplier parser.
Each real dyadic coefficient uses the same real ADD macro on the real
and imaginary components. No phase scan or temporary field is needed.

| Quantity per call | Forward | Backward |
| --- | ---: | ---: |
| Added complex ADDs | 1,792 | 1,792 |
| Final complex mode negations | 8 | 8 |
| Added real primitives | 17,040 | 22,416 |
| Raw core plus added real primitives | 221,458 | 226,834 |
| Retained native events | 5,056 | 5,056 |
| Retained paid native rank | 5,522 | 5,522 |
| New native children, fields, or maps | 0 | 0 |

The forward added scalar count is
`2*448*8 + 448*12 + 448*10 + 16 = 17040`.
The backward count is
`448*12 + 2*448*14 + 448*10 + 16 = 22416`.
The two-real-component ADD bounds for magnitudes `1`, `2`, `1/4`, and
`1/8` are `8`, `10`, `12`, and `14`, respectively. The raw bound is
204,418 in each direction. The retained paid profile is
`{1:2412,2:418,3:432,4:142,5:82}`.

These are scalar-event bounds. They exclude the inherited native map,
owner route, address, control, and recursive costs. A complete
construction must also pay for its changed data controller. No cost
from the characteristic or paired packets is imported into this word.

## Verification and remaining work

`emit_original_clean_source.py` checks both complete maps on all 704
formal input columns, all 480 restored helper rows, and the absence of
every helper-to-data coefficient. It uses exact rational coefficients
and free ordered Laurent words. Only adjacent powers of the same
`Q_p` cancel. It does not commute different port phases or reduce
powers modulo four. Missing-prefix, missing-negation, wrong-order,
and wrong-output-phase controls fail as required.

The producer inherits the reviewed raw core and its native phase
proof. It checks the retained scalar frame chronology and prices
every added event. An independent new-word replay and a direct
original-owner binding are separate review obligations. The initial
and final data computation is still controlled by the unresolved
global word. The ordinary recursive width interface can be used if
that global word is completed; no even-width remainder rule is needed
for this component.

The coordinating agent supplied the all-width cleaning formulas.
This lane supplied the literal expansion and exact replay, using the
earlier raw helper-mode construction. The work used OpenAI Codex
assistance under the user's direction. No human review is claimed.
