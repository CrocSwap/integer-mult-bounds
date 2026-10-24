# Sign-metric responses and unit centre capture

This annex retains two exact 112-port matrix constructions and a scoped
lower bound. The first response has 24 diagonal exceptions and a diagonal
sign metric. Its selected reader has no right inverse over the Gaussian
dyadic ring. A second response uses 32 FULL fields and gives a dyadic unit
row code with 16 centre fields. The prior independent review also gives
an option that keeps the first response and expands its read set to 32
fields. These are algebraic results. No native word, complete invoice, or
complete kappa improvement follows.

The two original proofs are [the sign-metric reflection](frozen/root/SIGN-METRIC-INVOLUTIONS-20261020.md)
and [unit centre capture](frozen/root/SIGN-METRIC-UNIT-CAPTURE-20261020.md).
The retained independent reviews cover [the response and its exact scope](frozen/lanes/oblique-native-20261017/sign-metric-review-20261020/REVIEW.md),
[the whole selected-reader obstruction](frozen/lanes/oblique-native-20261017/sign-metric-review-20261020/READER-ADDENDUM.md),
and [the unit code, minimum, and unchanged-response option](frozen/lanes/oblique-native-20261017/sign-metric-unit-review-20261020/REVIEW.md).
[SOURCES.json](SOURCES.json) binds all 26 original files.

## The 24-exception response

Let `R = Z[i,1/2]`. For a diagonal sign matrix `D` and a column `w`
with `w* D w = 2`, set `S = I - w w* D`. Here `*` is the conjugate
transpose. Direct multiplication gives

```text
S^2 = I,       S* = D S D,       S* D S = D.
```

Each block has correction rank one. In each of the eight six-mode
blocks, two coordinates have negative metric sign and all entries of
`w` have norm one. In each of the eight eight-mode blocks, one coordinate
has negative metric sign and its entry of `w` is a sign times `1+2i`.
The latter norm is five, so its metric norm is `7-5=2`. No division by
five occurs in this response construction.

The selected ports are closed under the actual physical pair code `H`.
Thus `H` commutes with `D`. Its Gram matrix is `2I` on the large component
and `I` on the small component; the response does not mix the components.
The physical matrix `A = H^-1 S H` therefore satisfies

```text
A^2 = I,       A* = D A D,       A* D A = D.
```

Its correction rank is 16, determinant is one, and trace is 80. Its
diagonal has sixteen entries equal to two, eight equal to six, and 88
zeros. Each ordinary physical row keeps its old support. The ordinary
principal block is unchanged, but all 24 selected columns change within
the ordinary rows. This construction is not a selected-row replacement.

For a diagonal unitary field operator `Z` that commutes with `D`,
`D (Z A)* D = (Z A)^-1`. The order is fixed; it does not require `A Z = Z A`.
For two-bank shears the signs act on both banks. Each sign still has a
cost, and all intervening progress must commute with `D` or have a proved
conjugated implementation. The identity removes neither stage dependence
nor a final phase.

## The reader obstruction and its two escapes

Write `A = I + U V`. In the 24 selected columns, each of the eight
small-block rows of `V` has one entry, a sign times `1-2i`. The ring map
`R -> F5` with `i -> 3` and `1/2 -> 3` sends all eight restricted rows
to zero. Thus the entire selected reader has no right inverse over `R`.
This rules out arbitrary Gaussian-dyadic normalization on those columns,
not only one square minor. It does not exclude proved division on a code
image, other source columns, or a different representation.

The unit-capture construction selects two coordinates in each eight-mode
block and uses entries `(1+i)d` there. Its metric norm is `6-2-2=2`.
The selected reader entries are signs times `1-i`, whose inverse is
`(1+i)/2` up to sign. The six-mode blocks stay fixed. There are 32 FULL
fields, with diagonal entries two on 16 fields and three on 16 fields.
The original 16 centre pivots form a Gaussian-dyadic unit minor after
the actual pair code. Both the FULL set and the centre set are pair-closed.

For the physical reader, let `P` be those 16 pivots and set

```text
L = V_P^-1 V,       L_P = I,       L A = -L.
C_P = L,           C_R = I_R.
(C-I)^2 = 0,        C^-1 = 2I-C.
```

Both `C` and its inverse are Gaussian dyadic on arbitrary input arrays.
Only 16 rows carry centre values. The other 16 FULL fields can retain
response values. No zero-target or code-image promise is used.

The sign metric does not pass through this row code. The actual matrices
satisfy `C* D C != D` and `(C A)* != D (C A)^-1 D`. A caller must therefore
distinguish `Z A` from `Z C A`. The sign-only adjoint conversion for the
first matrix does not apply to the second matrix by inheritance.

There is a separate escape with the unchanged 24-exception response.
Add the eight ordinary small ports `5,4,35,12,29,32,26,31` to its FULL
read set. Use those ports as the small centre pivots. Their reader entries
are `-1`; the large minor is unchanged. The resulting 32-field read set
has a unit 16-column minor. This option keeps the response and metric,
but uses different small centre slots. Its native access remains open.

## Exact scope of the minimum

In an independent rank-one reflection over the Gaussian rationals with
a diagonal sign metric, one exceptional diagonal coordinate in a block
of size `k > 3` requires a rational Gaussian norm `k-3`. A six-mode block
would require norm three. Reduction modulo three and descent exclude
that norm. Zero exceptions also contradict the trace `k-2`. Two
exceptions are therefore necessary in each six-mode block. One exception
is possible in an eight-mode block, where norm five is available.

For arbitrary blockwise reader normalization over `R`, require every
diagonal exception and every reader pivot to lie in the FULL selected
fields. One FULL field in an eight-mode block then has the norm-five
unit obstruction. These hypotheses require at least two FULL fields per
block, hence 32 in total. The construction attains that count with 16
centre fields. The actual pair-closed representation preserves this split.

This minimum does not cover coupled blocks, higher correction rank,
non-diagonal metrics, a mixed representation that is not pair-closed,
normalization from other frames, code-image division, extra carriers,
or a different transfer grammar. It is not a general native lower bound.
The parent package's sharp unitary C24 coordinate bound and its signed
reciprocal C16 code concern different matrices and reader maps.

## Reproduction

Use Python 3.11 or later, the standard library, at least 3 GiB free space,
and a new output directory outside the annex. No network or external
package is required.
From this annex directory, run:

```sh
python3 -I -B replay.py --out /tmp/sign-metric-capture-annex
```

The final line must be:

```text
PASS_SIGN_METRIC_CAPTURE_ANNEX
```

[The fresh receipt](evidence/REPLAY.json) records ten sequential runs:
the two producers and the three independent checks, each with normal
and optimized Python. All receipts and both full response payloads match
the frozen bytes. The independent response checks use integer real
matrices; they do not import the Gaussian-pair producers. The reader
check uses the full selected reader and its finite-field obstruction.

The checks cover all 112 ports, both physical metric identities, the
rank contraction, pair closure, both minor inverse orders, both code
inverse orders, and `L A = -L`. Controls reject a bilinear transpose,
missing metric signs, a broken pair, a one-exception real-sign attempt,
and metric inheritance through `C`. They retain examples outside the
lower-bound class. The symbolic minimum is a written proof; finite
checks do not replace its hypotheses.

The runner copies the frozen tree to its new output directory before it
runs any script. It preserves all source bytes and uses their original
relative layout. No import adaptation is needed. It does not run or
change the main encoder suite. [ANNEX-MANIFEST.json](ANNEX-MANIFEST.json)
is separate from the accepted parent manifest.

## Costs and open next questions

No Gaussian scalar lowering, native response word, centre-access word,
or recursive invoice is supplied. The old real-1760 scalar tariff and
old 16-carrier native profile do not apply to these changed columns and
32 target paths. A complete caller must supply those paths, track the
actual coded response, check intervening progress, and price all boundary
codes, signs, phases, storage, and precision. No claim of applicability
to the current selected supplier follows from this historical packet.

The next questions are a literal complex scalar lowering, native access
for each stated centre choice, and a complete forward/backward caller
with its cost and precision proof. They remain open. This annex adds no
new research or proposed repair. [NOTICE.md](NOTICE.md) records the source
contributions, license, and AI assistance.
