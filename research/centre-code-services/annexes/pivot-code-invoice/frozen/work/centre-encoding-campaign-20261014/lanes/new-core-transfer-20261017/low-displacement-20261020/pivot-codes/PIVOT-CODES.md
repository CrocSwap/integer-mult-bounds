# Centre sums in existing data fields

The exact rank-sixteen response has an in-place code on its 112
data fields. The code puts its sixteen centre sums in sixteen
existing data fields and puts independent complement data in the
other 96 fields. It needs no additional field and no zero input.

Let H be the actual signed pair code on the large 48 ports, extended
by identity on the small 64 ports. In these coordinates the response
is the direct sum of eight signed six-mode blocks I-dd^T and eight
eight-port blocks I-11^T. The signed vectors have entries of absolute
value one. Their exact port lists and signs come from the frozen
rank-sixteen native payload.

Apply H. In each block, first multiply each coordinate by its sign.
Let p be the first coordinate of the block and let k be its size.
Apply the following word:

```text
x_i -= p          for all other coordinates i
p *= k
p += x_i          for all other coordinates i
```

The pivot now holds the sum of the old signed coordinates. Each
other coordinate holds its old signed value minus the old signed
pivot. The reverse word recovers every input. It does not clear
arbitrary data or use an accumulator.

Call this complete code C. Let A be the set of its sixteen pivot
ports. The exact matrix identity is

```text
C E C^-1 = D,
```

where D multiplies the first eight pivots by -5, the other eight
pivots by -7, and the 96 complement fields by 1. This is a coordinate
change for the full response. It is not a native inverse response.

## Literal cost and retained grid

The one-way pair code H costs 470 old real scalar units. The eight
six-mode capture words and their four signs cost 664 units and
sixteen real fixed-three multiplication scans. The eight small
capture words cost 944 units. Thus C costs

```text
470 + 664 + 944 = 2078 old real scalar units,
plus 16 real fixed-three multiplication scans.
```

Its inverse has the same old scalar cost and sixteen real
fixed-three division scans. Each direction uses no native child
and no owned field.

The forward prefix row one-norm is at most 12. Its binary and odd
fractional heights are zero. The inverse prefix row one-norm is at
most 8, with at most three new binary fractional bits and one new
factor three in the denominator. These bounds include the pair code
and its inverse. The blocks are disjoint in mode coordinates, so
their eight divisions do not add eight powers of three.

The fixed-three scans require the retained common-root grid on all
numeric input streams, including arbitrary borrowed streams. The
grid theorem and its root conversion are a separate implementation
dependency. This packet proves the local height bound. It does not
claim a complete recursive precision invoice.

## Entry square code and transport

Let L=Q^2. Each L_p is the actual translation by q_p. The entry code

```text
C_in = C L
```

is literal: apply one translation to each of the 112 current data
fields, then apply C. These are 112 explicit address maps, with
their descriptor and streaming costs separate from the scalar
invoice. The translation is on the input side of C. The checker
rejects the opposite order.

This word is available on the current physical arrays at a common
entry chart. A use at another cut must prove its views. In
particular, this is not a free capture inside the cyclic native
word. That word has different source flags at each vertex and no
common full-vertex cut before FULL.

Write q=Q^-1. The proposed transported code is

```text
C_out = q C q.
```

Its exact algebraic action on the physical response is

```text
C_out (Q E q) C_out^-1
    = q C E C^-1 Q
    = q D Q
    = D.
```

The cancellations occur only at equal adjacent ports. No Q is
moved through C or E. The last equality holds because D is diagonal
in the physical port labels and has scalar entries.

This identity makes the encoded centre action simple. It does not
implement C_out or its inverse at a retired output cut. A raw-output
decoder, the next-stage transition, the full productive helper
contract, and recursive child hosting remain separate obligations.
The current native word still advances only the two data banks.

## Verification

`emit_pivot_codes.py` pins the native response and the actual pair
geometry. It checks all 640 independent inputs, with 528 fields
outside the active bank unchanged. It checks every centre sum,
every complement row, both inverse orders, and C E C^-1=D.

The spatial interpreter stores exact translation labels on each
input coefficient. It checks C_in, both literal spatial inverse
orders, and the wrong-side-square control. It does not replace an
unproved output chart by a free scalar cut.

The final outputs are in `final-normal/` and `final-optimized/`.
Both files are byte-identical between these runs. The earlier empty
run directories are retained: the invoice check caught a manual
double count of the pair code. The exact literal invoice is 2078.

The code uses the native rank-sixteen response, the retained-grid
construction, and the moving-code identity developed by the root,
native-escape, and coherent-port lanes. AI assistance was used.
No PR or complete supplier improvement is claimed.
