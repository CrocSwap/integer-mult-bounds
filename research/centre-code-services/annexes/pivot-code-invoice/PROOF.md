# Exact pivot code and its implementation boundary

The full historical [construction](frozen/work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/pivot-codes/PIVOT-CODES.md) and
[independent review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/moving-code-review-20261020/REVIEW.md) are retained. This wrapper states their
local claim and the exact division boundary. It does not add a new
construction or an unproved caller.

## Code and inverse

Let H be the actual signed pair code on 48 ports, extended by identity on
the other 64 ports. The pinned response satisfies

```text
H E H inverse = direct sum of eight (I-dd transpose) blocks of size 6
               and eight (I-11 transpose) blocks of size 8.
```

The sixteen blocks partition the 112 mode labels. In a signed block,
first apply its signs, and call the resulting entries y_i. Choose the
first coordinate p. The code then performs

```text
y_i -= y_p       for each i other than p
y_p *= k
y_p += y_i       for each i other than p
```

At the end, the pivot is `s=sum(old y_i)`. Each other coordinate is
`t_i=old y_i-old y_p`. Thus the exact inverse is

```text
old y_p = (s-sum(t_i))/k
old y_i = t_i+old y_p.
```

Reversing the literal events implements this inverse on arbitrary
rational inputs. No data is cleared, no accumulator is introduced, and
all 528 fields outside the active bank remain unchanged.

For `I-11 transpose`, the sum changes by the factor `1-k`; every
difference stays fixed. The signs give the same conclusion for
`I-dd transpose`. Let C include H, all signs, and these block words.
Then `C E C inverse=D`, where D is -5 on the eight six-mode pivots,
-7 on the eight eight-mode pivots, and identity on the other 96 fields.
The exact port lists and signs are in the pinned
[program](frozen/work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/pivot-codes/final-normal/PIVOT-CODES.json). This is a coordinate change
for E. It is not a native E inverse; inverting the diagonal factors
would introduce the separate primes five and seven.

## Literal cost and prefix grid

The inherited tariff assigns eight old real units to a complex unit
ADD and two to a sign or one-bit binary scale. An exact odd scan is a
separate operation. The actual H word and its inverse each cost 470.
For each six-mode block the ten unit ADDs cost 80 and the binary scale
costs two. Four mode signs add eight across those blocks, so their
subtotal is `8*82+8=664`. Each eight-mode block has fourteen unit ADDs
and three binary scales, hence `8*(14*8+3*2)=944`. Therefore

```text
470 + 664 + 944 = 2078 old real scalar units.
```

Each six-mode pivot also uses one complex multiplication by three.
There are eight such pivots, hence sixteen real scans. Reversing the
word preserves the scalar tariff and changes these to sixteen real
division scans. Each direction uses zero native children and zero
owned fields inside the declared common chart.

At each stored opcode boundary, expand every row in the original data
columns. Its row one-norm bounds the magnitude by that norm times the
largest input magnitude. The exact retained replay computes maximum
norms 12 forward and 8 inverse. All forward coefficients are integral.
Inverse prefix denominators have binary exponent at most three and
odd-three exponent at most one. These are exact finite-word bounds,
including H and its inverse. Pointwise application gives the same
bounds at every array entry and tensor width. They do not bound all
bit-level ADD temporaries or a complete recursive supplier.

The six-mode blocks are disjoint in mode coordinates. Each inverse
block divides its own pivot once by three. Their local odd heights
therefore take a maximum, not a sum. The final pair inverse is dyadic.
This explains why the local odd height is one rather than eight.

## Exact division domain

Let R0 be the Gaussian dyadic ring. H and its inverse are units over
R0. For an actual forward code image, before a six-mode inverse divides
by three, the value is `s-sum(t_i)=6*old y_p`. Its coefficients on all
original inputs have a factor three. Division by three leaves
`2*old y_p`, and the following binary division recovers the pivot.
The eight-mode block needs only binary division. Thus reversing C on
its valid image uses exact odd division without an extra odd root
factor. [CHECKS.json](CHECKS.json) checks this divisibility at all eight
complex division events and restores all 112 original data columns.

This does not hold for every generic code-coordinate input. Already a
six-mode block with `s=1` and every `t_i=0` requires `old y_p=1/6`.
The actual full inverse has coefficient `1/12` at row 0, column 0.
Thus its generic output need not lie in R0. An intervening operation
must preserve `C(R0^112)` to use the valid-image contract; the word
identity alone does not prove that condition for a new caller.

For generic rational inputs, the inherited
[common-grid proof](frozen/notes/stopped-product-complex.tex),
[local exact-scan account](frozen/work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md), and
[grid specification](frozen/work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/CLIQUE-CODE-GRID.md) apply only with their
premises. All numeric root streams, including arbitrary borrowed
streams, must receive the common scale. Addresses and descriptors are
not scaled. Each complete child needs the declared dyadic semantic
endpoint, the full finite-parent odd height must be bounded, and the
outer endpoint must permit exact unscaling. Arbitrary integer
numerators on the finest grid are not valid root inputs. The local
height-one claim does not discharge these global premises.

One fixed-three real scan has the inherited bound `4*(w_g+1)` arithmetic
head steps per record. Sixteen real scans on n records per field thus
cost at most `64*n*(w_g+1)`, with stream control and root conversions
separate. This is additional to the 2,078-unit scalar invoice. The
retained proofs state the exact signed carry test; no rounded division
is substituted here.

## Entry maps and transported type

Let L=Q squared be the diagonal translations by the actual port labels.
The entry word is `C_in=C L`: first translate each of the 112 fields,
then apply C. The inverse is `L C inverse`. Each direction therefore
has 112 explicit translation maps, with full descriptor and streaming
prices separate from the scalar tariff. The spatial interpreter keeps
an exact translation label on every input coefficient. It verifies
both inverse orders and rejects the opposite order `L C` as an entry
substitute.

Put `q=Q inverse`. For the formal output type `C_out=q C q`, direct
ordered multiplication gives

```text
(q C q) (Q E q) (Q C inverse Q) = q D Q = D.
```

Only equal adjacent phases cancel. No Q is moved through C or E. The
last equality holds because D is scalar and diagonal in physical port
labels. This is the already reviewed code transport identity, under
its common advance and commutation premises. It does not implement
`q C q` or `Q C inverse Q` at a retired native cut. The actual cyclic
word has different source flags at its vertices and no asserted
common full-vertex cut before FULL. Actual cross-bank calls retain
additional odd phases. A productive centre advance, source views,
helper restoration, legal interstage chronology, full map invoice,
raw output decode, and recursive cost remain separate obligations.
No complete kappa improvement follows.
