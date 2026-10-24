# Constant centre readers for the actual rank-sixteen and rank-thirty responses

The actual factors E=I+UV have an invertible constant matrix B0=VU in
both source families. A section can therefore use

```text
J_in = Q^2 U,             D_in = B0^-1 V Q^2.
```

Since Q^4=I on every physical line, D_in J_in=I. This choice does not
need the translation inverse of VQ^2U. In particular, the singularity
of that translation matrix in the rank-sixteen family does not obstruct
this reader. Source capture, physical views, and the later returned
code still need their own proofs.

This packet gives literal scalar words for B0, B0^-1, G0=I+B0, and
G0^-1. Every word acts on one existing centre bank in a proved common
chart. It uses no owned field, no native child, and no address map
inside that chart. It is not a native query service on an arbitrary
retired bank.

The four rank-sixteen words also work in independent linear frames
on their fields. The proof below makes this stronger scope explicit.

## Actual matrices and complete local prices

The checker pins the actual U and V in the rank-thirty response and
the frozen rank-sixteen native extension. It forms VU directly and
checks E=I+UV against each source's full 112-port response.

For rank sixteen,

```text
B0 = diag(-6 I_8, -8 I_8),
G0 = diag(-5 I_8, -7 I_8).
```

For rank thirty, B0 has eight blocks B and fourteen scalar blocks.
Eleven scalar blocks are -5 and three are -3. Here

```text
B = [-4  1],             G = I+B = [-3  1].
    [ 2 -2]                       [ 2 -1]
```

Thus G0 has eight copies of G, eleven scalars -4, and three scalars -2.
The block G has determinant one. Its inverse is integral.

All prices below include every sign, binary scale, and unit ADD in
the literal word. Fixed-odd scans are separate from the old scalar
tariff. A complex unit ADD costs eight old real units. A complex sign
or one-bit binary scale costs two.

| Family and direction | Old real scalar units | Real fixed-odd scans |
| --- | ---: | --- |
| Rank sixteen B0 | 96 | 16 multiplications by 3 |
| Rank sixteen B0^-1 | 96 | 16 divisions by 3 |
| Rank sixteen G0 | 32 | 16 multiplications by 5 and 16 by 7 |
| Rank sixteen G0^-1 | 32 | 16 divisions by 5 and 16 by 7 |
| Rank thirty B0 | 204 | 22 multiplications by 3 and 22 by 5 |
| Rank thirty B0^-1 | 204 | 22 divisions by 3 and 22 by 5 |
| Rank thirty G0 or G0^-1 | 270 | 0 |

The rank-sixteen reader therefore needs only the odd prime three.
The primes five and seven are needed when that caller uses G0^-1.
For rank thirty, the reader uses three and five, but G0 and its
inverse are Gaussian dyadic. These are different obligations.

## Short large-block words

For B on a pair (x,y), use

```text
y -= x
x *= 3
x -= y
y *= 2
negate x and y
```

The outputs are (-4x_old+y_old, 2x_old-2y_old). This word has two
unit ADDs, one binary scale, two signs, and one complex fixed-odd
multiplication. Its old scalar charge is 22. Reverse the event order
and invert each event to obtain B^-1 with the same old charge and
one complex division by three.

For G use

```text
y -= 2x
x -= y
negate x and y
```

Implement y-=2x by doubling x, doing one unit ADD, and halving x.
The temporary scale is restored before the next update. The outputs
are (-3x_old+y_old, 2x_old-y_old). Its price is 24 old units. Reversing
the literal word gives G^-1 at the same price.

No live field is cleared or overwritten. Each scalar gate is an
invertible rational operation on arbitrary centre inputs. Unrelated
data, arbitrary borrowed fields, and private fields are unchanged.

## Independent frames for the rank-sixteen constants

All gates in each rank-sixteen word act on one field at a time.
For any declared linear frame F_j and scalar c in the word,

```text
c F_j z = F_j(c z).
```

This identity holds for each binary scale, sign, and exact fixed-odd
operation. It also holds for arbitrary independent choices of F_j on
the sixteen fields. Thus these four words need no frame alignment
and no entry or exit view. Their prices in the table are unchanged
at such a framed cut.

The identity is exact. An unproved rounded division cannot use it
to claim restoration. The common odd grid and full precision guard
remain required. The frame argument does not form the centre,
establish ownership, or move a source read to that cut.

The rank-thirty words have interfield ADDs within their eight pairs.
Those ADDs still need their actual common frame or a proved
intertwiner. This paragraph does not remove that requirement.

## Prefix bounds and exact grids

The checker uses exact fractions on all centre columns and two
arbitrary spectator columns. It verifies that no event reads or writes
a spectator. Thus the unchanged-field claim holds for any number of
unrelated roles. It checks both inverse orders and each valid-code
division.

| Family and word | Maximum stored row sum | Binary height | New odd height |
| --- | ---: | ---: | --- |
| Rank sixteen B0 | 8 | 0 | 0 |
| Rank sixteen B0^-1 | 1 | 3 | 1 at 3 |
| Rank sixteen G0 | 7 | 0 | 0 |
| Rank sixteen G0^-1 | 1 | 0 | 1 at 5 and 7 |
| Rank thirty B0 | 5 | 0 | 0 |
| Rank thirty B0^-1 | 3/2 | 1 | 1 at 3 and 5 |
| Rank thirty G0 | 4 | 0 | 0 |
| Rank thirty G0^-1 | 5 | 2 | 0 |

The row sums are relative to the maximum magnitude of the module's
input fields. Twice the displayed bound is a safe bound for a
unit-ADD temporary. The stored input has row sum one, even when all
later inverse values have smaller magnitude.

Generic inverse calls use the exact common-grid method in
`CLIQUE-CODE-GRID.md`, with the prime set in this table. A valid
B0-code or G0-code can use its inverse without a new odd root factor.
Immediately before each inverse division, the relevant linear
combination has the required odd factor. The checker tests this
divisibility on every input column. A generic reader input must not
be labelled a valid code without that proof.

The fixed-odd scan cost is at most 4(w_g+1) arithmetic-head steps per
real record. Thus the rank-sixteen B0 inverse adds at most
64 n(w_g+1) such steps for n records per real field. The rank-thirty
B0 inverse adds at most 176 n(w_g+1). Descriptor and record-counter
work is separate and linear. Any required entry and exit views retain
their full address-map prices. The diagonal rank-sixteen constants
require none.

## A whole-state code for a section

The following statement supplies a typed-code interface. It does not
claim that the supplier has implemented the required entry or exit.
Let J and D be actual operators with DJ=I_r. Choose r data rows A
such that J_A is a Gaussian-dyadic unit. Let O denote the other data
rows. Define the square data code

```text
C(a) = (D a, a_O - J_O J_A^-1 a_A).
```

For code coordinates (c,r), its inverse is

```text
u = c - D_O r,
a_A = J_A u,
a_O = r + J_O u.
```

Substitution proves both inverse orders. The proof uses
D_A J_A+D_O J_O=I. It does not commute D through J.
Extend C by identity on every unrelated physical role, including
all borrowed roles. This gives a whole-state type.

If J, J_A^-1, and the required routes and frames are Gaussian dyadic,
the odd height of both C and C^-1 is at most the odd height of D.
For the rank-sixteen reader above this is one at three. For the
rank-thirty reader it is one at three and five. The native children
and all scalar prefixes still need the typed relations in
`TYPED-CODE-POTENTIAL.md`. These local code bounds do not establish
those relations.

In particular, replacing a bank's entry type C_in by its output type
C_out requires the exact full endpoint C_out A C_in^-1 with dyadic
semantic A on all roles. Productive helper progress, address frames,
interstage changes, and the final raw output remain separate
obligations. No factor is cancelled merely because two callers use
the same odd primes.

## Reproduction and attribution

Run the companion checker with a new output directory:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_centre_constants.py --out /tmp/centre-constants-normal
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_centre_constants.py --out /tmp/centre-constants-optimized
```

Expected status: `PASS_ACTUAL_CENTRE_CONSTANT_CODES`. Both output
files must match byte for byte.

The source factors come from the cyclic-pair and low-displacement
work. The coherent-port lane supplied the constant-reader choice,
the square section code, and the short G block factor. This packet
supplies the short B block factor, actual complete constant words,
and their exact local grid and cost bounds. OpenAI Codex assisted
the proof and checks. No publication is authorized. Before a future
PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
