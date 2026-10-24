# Independent review of the actual constant centre readers

The exact checks pass for both source families. There is no unresolved
local finding in the scalar words, their costs, or the square section
identity. The rank-sixteen words are valid in independent linear frames
on their existing fields. This review does not establish source capture,
native access, field ownership, a controller, or a complete supplier.

The source hashes and the final producer proof hash are in
`SOURCE-MANIFEST.json`. The review imports no producer module.
It does not replay a native program.

## Source reconstruction

The checker reads the actual correction factors U and V. It computes
B0=VU and checks the complete 112-port identity E=I+UV against each
source response. U has only denominators one and two. V is integral
in both source families.

The rank-sixteen matrices are

```text
B0 = diag(-6 I_8, -8 I_8),
G0 = I+B0 = diag(-5 I_8, -7 I_8).
```

The rank-thirty B0 consists of eight copies of B, eleven scalar
blocks -5, and three scalar blocks -3:

```text
B = [-4  1],       B^-1 = [-1/3  -1/6],
    [ 2 -2]               [-1/3  -2/3]

G = [-3  1],       G^-1 = [-1 -1].
    [ 2 -1]               [-2 -3]
```

The checker verifies all entries, including every off-block zero.
It verifies both inverse orders for B0 and G0.

## Literal word and complete price

For the B word, after y-=x and x*=3 the values are (3x,y-x).
The next subtraction gives (4x-y,y-x). Doubling the second value
and negating both values gives (-4x+y,2x-2y), as required.
The word uses two unit ADDs, one binary scale, two signs, and one
complex multiplication by three. Its old scalar price is 22.

For G, the first update gives y-2x. The next subtraction gives
3x-y in the first field. Negating both values gives (-3x+y,2x-y).
The temporary doubling and halving of x implement the first update
without a new field. The old price is 24.

The review uses the emitted literal words. It checks every input
column by forward row propagation and by reverse output-covector
propagation. It includes two arbitrary spectator columns and checks
that no event reads or writes outside the centre bank. All inverse
words have the stated endpoint.

| Family | Word, in either direction | Old real scalar units | Real fixed-odd scans |
| --- | --- | ---: | --- |
| Rank sixteen | B0 | 96 | 16 at three |
| Rank sixteen | G0 | 32 | 16 at five and 16 at seven |
| Rank thirty | B0 | 204 | 22 at three and 22 at five |
| Rank thirty | G0 | 270 | 0 |

The forward scans multiply. The inverse scans divide. The odd scans
are additional to the old scalar price. They are not free old unit
operations. No word clears a field or discards an arbitrary input.
Each update is an invertible rational operation.

## Independent frames for rank sixteen

The checker explicitly verifies that none of the four rank-sixteen
words has an interfield ADD. Each event on field j is c I_j for a
rational scalar c. For any declared linear frame F_j,

```text
(c I_j) F_j = F_j (c I_j).
```

Thus every prefix commutes with diag(F_1,...,F_16), even when all
frames differ. The scalars on the first eight fields need not equal
the scalars on the last eight fields. This is an exact identity at
every field width.

Consequently, these four scalar words need no entry or exit views
for frame alignment once the actual sixteen fields and their numeric
format are admitted. Exact odd division still needs the common grid
and the full precision guard. The identity does not apply to an
unproved rounded quotient.

The rank-thirty words contain pair ADDs. Those updates still require
the actual pair frames or a proved operator that connects them.
This review does not remove that condition.

## Prefix and grid checks

The exact prefix maxima agree with the producer table:

| Family | Word | Stored row sum | Binary height | Odd height |
| --- | --- | ---: | ---: | --- |
| Rank sixteen | B0 | 8 | 0 | 0 |
| Rank sixteen | B0 inverse | 1 | 3 | 1 at three |
| Rank sixteen | G0 | 7 | 0 | 0 |
| Rank sixteen | G0 inverse | 1 | 0 | 1 at five and seven |
| Rank thirty | B0 | 5 | 0 | 0 |
| Rank thirty | B0 inverse | 3/2 | 1 | 1 at three and five |
| Rank thirty | G0 | 4 | 0 | 0 |
| Rank thirty | G0 inverse | 5 | 2 | 0 |

The rank-thirty unit-ADD operand row sums have the same maxima as
the respective stored row sums. There are no such operands in the
rank-sixteen words. The producer's factor-two temporary bound is
therefore conservative.

The review checks all stored numerators and all odd divisions on
generic integer grids. Sufficient respective grid scales for the
four inverse words are 24, 35, 30, and 4 in the table's family order.
These include binary scale as well as odd scale.

The review also starts each inverse at its exact forward matrix.
Every division is then exact with no root scale at all, and the
complete endpoint is identity. This is a valid-code result. It does
not certify an arbitrary reader input as a valid code.

## The reader and the square section

For the actual constant factors, define

```text
J = Q^2 U,
D = B0^-1 V Q^2.
```

The relation Q^4=I gives

```text
DJ = B0^-1 V Q^4 U = B0^-1 B0 = I.
```

No translation inverse of VQ^2U occurs in this proof. It does not
form the value VQ^2 a on physical hardware or prove where that value
is available.

For a row set A with an invertible J_A, write O for the other rows.
Put t=J_A^-1 a_A. Then

```text
a = J t + embed_O r,       r=a_O-J_O J_A^-1 a_A,
D a = t+D_O r.
```

It follows that the square code and inverse are

```text
C a = (D a, a_O-J_O J_A^-1 a_A),
u = c-D_O r,
a_A = J_A u,
a_O = r+J_O u.
```

This proves both inverse orders with the factors in their given
order. No factors are commuted. Extending both maps by identity on
every unrelated role gives a complete whole-state type.

DJ=I alone does not imply that a coordinate minor J_A is a dyadic
unit. For example, J=(3,5)^T and D=(2,-1) satisfy DJ=1, but neither
one-row minor of J is a unit over Z[1/2]. The minor condition is a
separate premise of the general construction.

For these actual sources, one canonical finite row-minor check
satisfies that premise algebraically. The row lists are in
`CHECKS.json`. Both U_A inverses are integral. The checker constructs
the full square C and C^-1 at Q^2=I and checks both inverse orders
on all 112 data columns.

The phase extension is

```text
J_A = Q_A^2 U_A,       J_A^-1 = U_A^-1 Q_A^2.
```

This uses the actual identity (Q_A^2)^2=I. For the odd-height claim,
the declared Q^2 operators, routes, and frames must also be Gaussian
dyadic. The fourth-power identity alone does not imply that coefficient
condition.

If J and J_A^-1 are Gaussian dyadic, each coefficient in C or C^-1
uses at most one factor D. Hence both odd heights are bounded by the
height of D. The actual common-chart checks give height one at three
for rank sixteen, and height one at three and five for rank thirty.
The finite minor witnesses do not supply a physical capture word.

## Typed recursion and remaining obligations

The square code can be a type in the conditional theorem reviewed
in `clique-code-grid-review-20261020`. It does not by itself establish
a child endpoint C_out A C_in^-1. The actual caller must prove that
identity on every data, borrowed, and live numeric work column.
It must also prove the decoded child-entry and internal-prefix bounds.

The rank-sixteen frame result removes alignment views only for the
four diagonal scalar words on an existing centre bank. It does not
create that bank, establish a lease, admit a source read, preserve
helper progress, or prove an interstage return. No native, controller,
supplier, or kappa claim is made here.

The independent normal and optimized runs both return
`PASS_INDEPENDENT_ACTUAL_CENTRE_CONSTANT_REVIEW`. Their receipts are
byte-identical. Run the checker with new output directories:

```text
python3 -I -B check_review.py --out review-final-normal
python3 -I -O -B check_review.py --out review-final-optimized
```

No PR, commit, push, or publication is authorized. Before any future
PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
