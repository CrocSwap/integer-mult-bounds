# Exact three-grid admission for the sixteen-coordinate unitary code

The actual sixteen-coordinate code has a paid scalar implementation at
a proved common I or FULL cut. Each direction costs 5,702 old real
scalar units, sixteen real multiplications by three, and sixteen real
divisions by three. It uses no scratch field or native child. Every
prefix has at most one factor three and two binary factors in its
coefficient denominators.

The code does not preserve the dyadic module on arbitrary inputs.
The preliminary dyadic code does not supply the required divisibility.
The retained common odd grid supplies it, with the root conversion,
added width, and local scans stated below.

There is also an exact limit on reuse without matched types. For the
actual complete code C,

```text
h_3(C^m) = h_3((C*)^m) = m,     for every integer m >= 1.
```

Thus no bounded three-adic lattice is stable under both the actual
preliminary code and its packing factor. This does not exclude a caller
whose complete typed operations cancel their boundary codes.

## Frozen inputs and scope

The actual matrix is the first sixteen-coordinate packing in
`independent-review-20261017/odd-unitary-packing-20261020`.
Its decompressed `run-normal/PACKING.json.gz` has SHA256
`b460c1b4603f4b75da5ca4bf1da4a642f2cc4d970599f9c1068832e7b230ac32`.
Its source freeze is
`22769396f123964addb9024b2fda452148388c67868714b4121a8fe3bfb9d410`.

That packet supplies the actual 112 by 112 matrices, the sixteen
original centre readers, the decoder, four packing quartets, and
literal dyadic preliminary words. It proves that C is unitary and
that the sixteen readers are obtained from sixteen output coordinates.
It does not supply a native implementation of the changed response.
In particular, all 96 ordinary diagonal entries of this C are nonzero.

This packet copies the preliminary component words without change,
emits the rational packing words, and checks the complete result
against that frozen C on all 1,280 real input columns. The 528 complex
fields outside the 112 code fields remain unchanged.

This C is not a modified extension of the later 24-coordinate native
code. No trace, support, or implementation result is transferred to
such an extension without its own matrix proof.

The scalar tariff is pinned to
`new-core-transfer-20261017/low-displacement-20261020/check_response.py`,
SHA256 `c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8`.
As in the source component-word emitter, each real component has half
the cost of one complex instruction in that tariff.

## The rational packing word

Use the following two complex matrices and the permutation P with
output order `(0,2,1,3)`:

```text
A = [[1, 1+i], [-1+i, 1]],
B = [[1-i, -i], [-i, 1+i]],
A* A = B* B = 3I.

R = (1/3) diag(A*,A*) P diag(B,B)
  = diag(A^-1,A^-1) P diag(B,B).
```

The last factorization has fewer odd scans than scaling all four
outputs separately. It first applies two B blocks, then the paid
middle exchange, then two A inverses.

For two distinct complex data fields x and y, A has the word

```text
x += (1+i)y
y *= 3
y += (-1+i)x.
```

Its inverse is the reverse word, with subtraction and division by
three. To apply B, put `a=(1-i)/2` and `b=(1+i)/2`, then use

```text
x += a y
x *= 1-i
y *= b
y *= 3
y += a x.
```

No complex multiplication primitive is assumed. For `x=r+i s`,
multiplication by `1-i` uses

```text
r += s;  s *= 2;  s -= r.
```

Multiplication by `(1+i)/2` uses

```text
r -= s;  s *= 2;  s += r;  r /= 2;  s /= 2.
```

A complex ADD is expanded into its real component ADDs. Every
exchange uses three ADDs and a sign on each real component. The
inverse packing is the gatewise inverse of this literal word.

One quartet costs 210 old real units, four real multiplication scans,
and four real division scans. The actual four disjoint quartets are

```text
(0,71,27,78)
(53,41,111,37)
(20,47,7,63)
(57,104,46,110).
```

The four packings therefore cost 840 old units and 32 real odd scans
per direction. Their instruction count is 256. Every prefix has binary
height one and odd height one. The exact real coefficient row-sum
peaks are seven for the packing and six for its inverse.

The preliminary word and its inverse each cost 4,862 old units.
Joining the correct words gives C and C*, each with 2,110 component
instructions and the stated 5,702 old units plus 32 odd scans.
The complete prefix row-sum peaks are 17 for C and 28/3 for C*.
Both have binary height two and odd height one. These are exact
instruction-boundary content bounds. They do not price primitive
ADD interiors, recursive children, or a full supplier's precision.

## Exact divisibility domain

Put `R0=Z[i,1/2]`. The integer Gaussian numerator N=3R has rank one
over the field `R0/(3)`, which is the field with nine elements.
For `x in R0^4`, the exact condition is

```text
R x belongs to R0^4
if and only if
x0 + ((1-i)/2)x1 - (1+i)x2 - x3 = 0 modulo 3.          (1)
```

The first numerator row, divided by its nonzero first entry modulo
three, gives the row in (1). The other numerator rows are its
Gaussian multiples. The realified numerator has rank two modulo
three. Thus (1) is one Gaussian condition, or two real conditions.
The checker verifies that rank from the literal numerator.

Each B word is dyadic before its odd multiplication. Each A inverse
has only one complex division, and all later operations are dyadic.
The two A inverse blocks have disjoint targets. Thus the literal
division domain agrees with the condition that its complete output
is dyadic; there is no hidden intermediate odd denominator of
higher order.

The preliminary Cpre is a Gaussian-dyadic unit, with dyadic inverse.
Its values on the four packing fields can therefore be arbitrary.
For example, take the original input `Cpre* e_0`, where e_0 is the
first actual packing coordinate. That input is dyadic. Its value
before R is e_0, and R e_0 contains genuine thirds. A binary guard
cannot remove that factor. The checker also rejects the unscaled
arbitrary-input contract in both packing directions.

A code-image argument can avoid a root factor only after the
actual input satisfies (1), and its counterpart for every quartet.
A caller must prove preservation of those congruences under all
intervening maps and all arbitrary borrowed columns. The fact that
the complete C is unitary does not prove this property.

## Paid exact grid

The retained model admits fixed odd arithmetic. The source method is
`interface-proof/rational-decoder/sources/notes/stopped-product-complex.tex`,
in “One exact odd-denominator grid”. The explicit three-scan proof is
`independent-review-20261017/odd-grid-a8-20261017/A8-ODD-GRID.md`,
SHA256 `e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01`.
Its borrowed-state and active-path argument is retained here.

For a signed w-bit numerator, division by three reads bits from low
to high, starts with carry c=0, and uses

```text
output bit a = (input bit b - c) mod 2,
next carry  = (c + 3a - b)/2.
```

The carry stays in `{0,1,2}`. If s_in and s_out are the sign bits,
the quotient is exact precisely when `c_final=3 s_out-s_in`.
Multiplication writes `(3b+c) mod 2`, updates to
`floor((3b+c)/2)`, and checks `c_final=3 s_in-s_out`.
The allocation must prevent multiplication overflow.

These operations overwrite the same record and need only finite
control. One real scan costs at most `4(w_g+1)` arithmetic-head
steps. Descriptor and record-counter work is separate. The checker
exhausts 8,188 signed division/multiplication cases, including
nonmultiples and overflow rejection.

For n records in each complex array, one full code direction adds
at most `128 n(w_g+1)` arithmetic-head steps for its 32 odd scans,
in addition to 5,702 old scalar units and separate linear descriptor
work. Odd scans are not charged as old binary SCALE instructions.

Suppose one finite parent has prefix odd height at most M after
every completed child is replaced by its exact Gaussian-dyadic
endpoint on all physical roles. If D bounds the recursive edge
depth, use

```text
K = M(D+1),       common grid = 2^-P / 3^K.
```

At the outer entrance, multiply the integer numerators of every
physical numeric stream by `3^K`. Include arbitrary borrowed data,
helpers, and numeric work streams. Do not scale addresses or tags.
All formats remain fixed during the computation.

Every prefix then has an integer numerator on this grid. At a
literal division by three its input numerator is divisible by three.
A completed dyadic child does not add odd height, even on rational
input. The complete local word may contain the new code as a parent
operation, but calling it a parent operation does not prove the
complete parent's endpoint is dyadic.

At the outer return, exact unscaling requires the intended
Gaussian-dyadic endpoint on all roles, including each borrowed role.
If N_real counts all real numeric records, the two outer conversions
cost at most

```text
8 N_real K (w_g+1) arithmetic-head steps,
```

plus separate linear descriptor work. The added width is at most
`2K` bits. These conversions are required costs, not free changes
of notation. A new supplier must prove its actual depth, full
prefix guard, complete endpoint, and strict recurrence inequality.

Matching rational boundary types are a further permitted case.
The proof in
`native-escape-20261017/rational-code-admission-20261020/TYPED-CODE-POTENTIAL.md`
applies to exact endpoints `C_out A C_in^-1` when all actual types
match and A is dyadic on the complete semantic state. The inverses
cancel in order. It does not require the codes to commute. A caller
must also prove its decoded child-entry types and its internal
prefix height. A code on 112 fields does not automatically restrict
to an admissible type for a recursive call on one field.

## Exact power growth for the actual C

Let K3 be the unramified quadratic extension `Q_3(i)`. The polynomial
`X^2+1` is irreducible modulo three, so three is inert in the
Gaussian integers. In K3,

```text
v_3(a+ib) = min(v_3(a),v_3(b))
```

for rational a and b. Normalize `|3|_3=1/3`. For a matrix use the
maximum absolute value of its entries. This norm is submultiplicative
and agrees with the induced coordinate maximum norm.

The actual frozen matrix satisfies

```text
h_3(C) = 1,
trace(C) = (11+7i)/6.
```

The trace has valuation minus one. In a finite extension containing
the eigenvalues, the non-Archimedean triangle inequality gives

```text
3 = |trace(C)|_3 <= max_j |lambda_j|_3 <= ||C||_3 = 3.
```

The right inequality follows by applying C to an eigenvector whose
largest coordinate has norm one. Thus an eigenvalue has absolute
value exactly three. For every positive integer m, its eigenvector
and submultiplicativity give

```text
3^m <= ||C^m||_3 <= ||C||_3^m = 3^m.
```

Therefore `h_3(C^m)=m`. The adjoint has conjugate trace and the same
entry norm, so the identical proof gives `h_3((C*)^m)=m`.
The checker recomputes the trace from the complete actual matrix
and checks the first four power heights. Those finite checks support
the theorem; the eigenvalue argument proves it for all m.

A full lattice over the valuation ring is bounded above and below
by two scalar multiples of the coordinate lattice. If C preserved
such a lattice, its powers would be bounded in the coordinate norm.
The displayed equality excludes that possibility. Any lattice
stable under both Cpre and R would be stable under `C=R Cpre`.
It is therefore also excluded.

The packing R alone is different: `R^4=I`, and its first three
powers have odd height one. A finite invariant lattice exists for
that finite group. This does not control its dyadic interleavings.
For example, set `S=diag(-1,1,1,1)`. The matrix `3RS` has Gaussian
rank one modulo three and trace `-2+2i`, which is nonzero there.
Its every positive power is nonzero modulo three. Hence
`h_3((RS)^m)=m` as well.

Neither power result forbids a sequence of genuine matching code
transitions `C_t A_t C_s*`. Their intermediate types can cancel.
It forbids treating repeated unmatched complete C calls as a
bounded-height provider solely because each call is unitary.

## Native access and remaining obligations

At a current I cut, the scalar word acts in the existing common
body chart. At a completed FULL cut, the exact stage views gather
the 112 fields, apply the word, and undo the views. A conservative
count is 224 complete view maps per code application, or 448
operations if route and translation are charged separately.
The source is
`bridge-access-20261017/general-stage-views-20261020/GENERAL-VIEWS.md`.
The grid scalar commutes with those exact linear maps.

This does not admit the code on a mixed or retired hole bank.
It does not make responses from different stages equal. The 96
nonzero ordinary diagonals still need a changed native response
construction. The scalar code, the representation change, and
the native implementation are separate costs.

No recursive host, changed supplier, complete exponent, or kappa
improvement is claimed.

## Reproduction and credit

Run `check_packing.py --out <new-directory>` under both
`python3 -I -B` and `python3 -I -O -B`. The expected status is
`PASS_RATIONAL_PACKING_GRID`. Compare both output files byte for byte.

The checks bind the frozen source and tariff, emit both packing
words, compose both complete codes, check all 1,280 real columns
and both inverse orders, test the exact signed scans, reject an
unscaled arbitrary input, compute the residue rank and prefix bills,
and reproduce the actual trace and four power heights.

The independent-review lane found and froze the sixteen-coordinate
unitary packing and the dyadic preliminary words. This lane supplies
the paid packing words, the grid admission and divisibility limit,
and the actual-code power theorem. The retained rational-decoder
work supplies the fixed-odd scan and common-grid method. AI
assistance was used throughout.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
