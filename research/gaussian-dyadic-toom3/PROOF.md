# Gaussian-dyadic five-product interpolation

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Put G = Z[i], pi = 1+i and R = G[1/2] = G[1/pi]. The inputs are
two independent coefficient triples a and b in G. Five output fields y
have arbitrary initial values in G. The endpoint is

    y_k += sum_(j+l=k) a_j b_l,   0 <= k <= 4.

All six inputs are preserved. Two additional fields start at zero and
return to zero. A PRODUCT call is the exact additive operation
`target += left*right`, preserving its distinct source fields. Its full
implementation is a premise, and it is counted once wherever invoked.

There is a word with five PRODUCT calls, sixty coefficient ADDs and four
SCALEs. A coefficient ADD means exactly `target += c*source`, with its
displayed Gaussian-integer coefficient c. It is a charged macro, not a
unit-cost claim about multiplication by c. Two SCALEs multiply by a
Gaussian associate of pi; two divide by an associate of pi. Every
intermediate value is a Gaussian integer on this contract. No division
by an odd integer, approximate rounding or hidden product uncomputation
is used. Every operation and its inverse is listed by `program()`.

Five is the minimum number of scalar products in the usual bilinear
model over Q(i), with linear input forms and linear output decoding.
Among integral point-evaluation interpolation schemes, denominator
height one in pi is also optimal. These are algebraic statements, not
native, recursive or bit-operation tariffs.

## The square of evaluation points

Let A(z) = a_0+a_1 z+a_2 z^2 and similarly B(z). Use the five points

    0, 1, i, pi, infinity.

Infinity means the leading coefficient, so its product is a_2 b_2.
For c = (c_0,...,c_4), the five polynomial evaluations form Vc, where

    V = [1  0   0       0     0]
        [1  1   1       1     1]
        [1  i  -1      -i     1]
        [1  pi  2i   -2+2i   -4]
        [0  0   0       0     1].

The determinant is 2. One way to see this is to expand at the infinity
row and use the cubic Vandermonde determinant on 0,1,i,pi. Its six
differences multiply to 2. Each finite Lagrange denominator has exactly
one factor pi, up to a Gaussian unit. Thus every entry of V^-1 lies in
pi^-1 G. This statement concerns the entries, and does not claim that
one scalar division suffices for the entire decoder.

The following row operations give a more direct constructive proof.
Number rows 0,...,4. Starting from V, perform in the stated order:

1. Subtract row 0 and row 4 from each of rows 1 and 2. Subtract row 0
   from row 3 and add four times row 4 to row 3.
2. Subtract i times row 1 from row 2. Subtract pi times row 1 from
   row 3. Add i times row 2 to row 3. Add (1-i) times row 3 to row 2.
3. Divide row 2 by -pi and row 3 by i*pi.
4. Subtract rows 2 and 3 from row 1.

After step 1 the nontrivial middle block has rows

    [1, 1, 1], [i, -1, -i], [pi, 2i, -2+2i].

After step 2 it has rows `[1,1,1]`, `[0,-pi,0]`,
`[0,0,i*pi]`. Steps 3 and 4 produce the identity. There are exactly
twelve coefficient ADDs and two SCALEs. Call their product D; then
DV=I. Reversing and inverting these operations implements V with
twelve coefficient ADDs and two integral SCALEs.

The sole denominators in D are the two step-3 divisors. In particular,
the square removes the factor 3 in the historical 0,1,-1,2,infinity
interpolation without increasing its five bilinear products. It does
not assert a lower total scalar, native or physical cost.

## Dirty outputs and scratch restoration

First encode the five dirty outputs by V. Their current values become
Vy. Add A(z)B(z) to the corresponding output at each of the five points.
Evaluation commutes with polynomial multiplication, so these additions
give exactly Vy+Vc = V(y+c). Finally apply D, obtaining y+c.
The preexisting y is neither cleared nor assumed zero.

At 0 and infinity, the PRODUCT inputs are the original a_0,b_0 and
a_2,b_2. At each of 1,i,pi, accumulate the three terms of A(z) into
the first clean field and the three terms of B(z) into the second.
Use the fields in one PRODUCT call, then reverse the six coefficient
ADDs. PRODUCT preserves its sources, so both fields return to zero.
They are reused only after restoration. The six public inputs are
never modified, including during evaluation and cleanup.

Each of those three sites pays twelve coefficient ADDs including
cleanup, for 36 in total. Encoding and decoding pay 24 more ADDs and
four SCALEs. There are exactly five PRODUCT calls, not ten. Products
are added directly into the encoded dirty outputs; no product scratch
field has to be uncomputed. The word has 69 instructions on thirteen
Gaussian fields: six preserved inputs, five dirty outputs and two
initially clean evaluation fields.

All encoder operations are integral. After the five products, the
outputs are V(y+c) with y+c in G^5. Every decoder prefix maps V times
an integral vector to an integral vector: this is immediate for the
ADDs; before the two divisions the affected rows are respectively
-pi and i*pi times one coordinate. Thus both divisions are exact.
This proves the integer-grid claim for all inputs, beyond finite tests.
It also proves the inverse word by reversing every operation.

The same identity holds in an associative R-algebra with central i.
Polynomial expansion preserves the order a_j b_l, so no commutativity
of the data entries is needed. The executable implements scalar G only.

## Sharp denominator and product obstructions

First consider any five homogeneous degree-four evaluations at
Gaussian-integer point pairs (u,v). Such a row is

    (v^4, u v^3, u^2 v^2, u^3 v, u^4).

Modulo pi, G/(pi) is F2. A nonzero pair reduces to one of the three
projective points (0,1), (1,0), (1,1); a zero pair gives a zero row.
The reduced evaluation matrix therefore has rank at most three.
It cannot have an integral inverse, since reducing that inverse would
give rank five. Allowing extra integral linear preprocessing of these
five returned evaluations does not raise their rank.

Consequently no such interpolation scheme has all decoder entries in
G. If decoder entries are Gaussian dyadics, at least one has negative
pi valuation. The constructed V has all entries of its inverse in
pi^-1 G, and eight entries outside G, so height one is attained and
optimal. This obstruction assumes integral evaluation forms and linear
interpolation from those values. It excludes neither non-evaluation
bilinear algorithms nor moving divisions into nonintegral encoders.

For the product count, flatten the convolution tensor with its output
index on one side. Its five rows have disjoint, nonempty supports among
the nine ordered monomials a_j b_l, hence rank five over Q(i). A product
of one linear a-form and one linear b-form, followed by a linear output
map, contributes rank at most one to this flattening. At least five
such products are necessary. The construction attains five. This is
the standard bilinear-rank argument; arbitrary nonlinear circuits and
unrelated native operators are outside its hypotheses.

## Relevance and limits

Gonzalo Mier's PR3974 supplies the historical Toom-3 screen, five-product
comparison and missing source-embedding question. Its calculations are
cited premises; none is replayed or audited here. The new contribution
is this source-relative Gaussian-dyadic interpolation, its optimal
denominator height, and its literal restoring five-call boundary.
Toom-Cook evaluation and Lagrange interpolation are classical; no
global literature priority for complex Toom formulas is claimed.

Chris R / Clear1nsight's PR3992 already excludes the stated same-width
Toom-only boundary for the first selected nine-climb group. Changing
interpolation nodes supplies no extra information channel and does
not bypass that obstruction. This module needs an actual bilinear
convolution consumer, rather than nine independent linear outputs.
The six inputs, five outputs and clean fields must have compatible
frames, placement, ranges and ownership. The clean fields are an
explicit resource premise, not free dirty workspace. Their admission,
movement, exact Gaussian division, PRODUCT implementation, coefficient
access, precision, stock and complete signed recursive invoice are
unpriced. No selected record or frontier changes, and all five selected
framework assumptions retain their status.

## Executable verification and resource scope

`verify.py` independently forms and rationally inverts V, compares all
five columns of both literal transforms, checks 36 real/imaginary
bilinear coefficient cases and ten dirty-output columns, and checks
complete endpoints on 729 real cube cases, 257 complex dirty cases,
one large signed case and the maximum 4096-bit entrance. It exercises
the complete inverse as stated in the receipt. Every instruction
omission is detected on nine explicitly enumerated basis fixtures.
The binary projective obstruction is separately enumerated. Written
proofs supply the universal claims; these checks supply bounded exact
construction evidence.

The code has no recursion, network, subprocess, dynamic execution or
output-file writes. Program lengths are bounded by 128; the actual
word has 69 instructions. Registers have at most 4096-bit components
on entry. The mathematical identity has no bit-size bound. A returned
value may exceed the API entrance cap, so composition with the inverse
requires checking that cap; inverse round trips are tested on the
257 complex fixtures. The two large fixtures test forward execution.

Power-of-Ten rule 3 deviation: CPython allocates integers, tuples and
Fractions dynamically. The scientific run has thirteen registers, five
products, two 5-by-5 rational matrices and finitely bounded fixture
domains; only one endpoint fixture is live. Each coefficient is fixed,
and all data expressions have degree at most two, bounding intermediate
bit lengths by twice the entrance bit length plus a fixed constant.
The public finite word is the declared program or its inverse, not an
untrusted program language. The nine omission fixtures and API/domain
controls exercise failure paths. A fixed-storage implementation would
need a separately charged bit-array backend and is not supplied here.

Every function is checked to fit within sixty physical lines. All
runtime checks use explicit exceptions and remain enabled under -O.
Warning-strict normal/optimized execution and AST inspection are the
available local Python diagnostics. No static type-checker proof or
production diagnostic-policy change is claimed. A generated stdout
receipt binds all package files by SHA256; no receipt is handwritten.
