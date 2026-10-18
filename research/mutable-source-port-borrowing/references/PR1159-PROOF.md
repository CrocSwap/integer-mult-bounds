# Quotient-ring execution and complete cost

## Interface

Fix integer L-by-L matrices A_0,...,A_(n−1), an ordered binary/ternary factor
tree, and w >= 1. Let M = 2^w and V = (Z/MZ)^L. Data registers contain
canonical residues 0,...,M−1. Each matrix induces an additive endomorphism
of V, with its coefficients reduced modulo M. A complete leaf on distinct
ports s,t performs

```
row[t] <- row[t] + q A_i row[s]  (mod M),    q in {+1, -1},
```

preserving its source and all other arrays and clearing its owned private
work. No inverse of a matrix, field assumption or division by two is used.

Use PR1057's fixed mutable pool [2,3,1,4], excluding the current source and
target before choosing one or two connectors. Row zero is the external
source and never a mutable port. Three dirty arrays plus the output leave
enough ports for every binary/ternary node at every depth. Internal children
may temporarily modify other ancestor ports; they restore them on return.
All recursive boundaries exchange residues, without signed decoding.

## All-tree restoration

This is an instantiation of the credited PR1057 additive-group contract.
For a binary node with child maps B,C, the four completed shears execute

```
z += Bx;  y += Cz;  z -= Bx;  y -= Cz.
```

The connector restores, and the target increment is
`C(z+Bx) - Cz = CBx`. All statements hold in V for arbitrary initial z
and y. For three children B,C,D, the eight completed shears

```
U; V; W; V^-1; U^-1; V; W^-1; V^-1
```

give the difference `D(z2 + C z1 + CBx) - D(z2 + C z1) = DCBx` and
restore both connectors. The child induction hypothesis supplies these
boundary shears independently of all borrowed dirt. Thus the full tree
adds `A_(n−1)...A_0 x` to y and restores every other data row, modulo M.
The negative call reverses the literal leaf word and negates each sign.
Factors need not commute. A finite-width residue has a unique canonical bit
pattern, so equality in V gives bitwise restoration of all dirty arrays.

Equivalently, reduction Z -> Z/MZ commutes with integer addition,
subtraction and multiplication. Reducing every intermediate of the literal
integer program gives the same final residue as reducing only its result.
The integer lift may exceed w bits arbitrarily. Only the reduced state is
stored, and the temporary arithmetic capacities below are bounded locally.

This does not license arbitrary nonlinear operations. For example, 1 and 5
are congruent modulo four, while floor(1/2) and floor(5/2) give different
residues. Saturating signed arithmetic also fails the group law. The retained
counterexamples test those boundaries explicitly.

## Integer recovery without an intermediate bound

Assume the external integer input and initial output satisfy
`||x||_infinity <= X` and `||y||_infinity <= Y`, with X,Y nonnegative.
Let `K_i = max_r sum_j |A_i[r,j]|`, and `G = product_i K_i`.
The triangle inequality gives `||A_i v|| <= K_i ||v||`, hence both signs
of the desired final output have norm at most `R = Y + GX`.

Choose

```
2^(w-1) > max(X, R),
w = max(1, bit_length(max(X,R)) + 1)  is sufficient.
```

The X term preserves representation of the unchanged external input even
when a zero factor makes G = 0. R >= Y already covers the initial output.
Signed decoding chooses the representative in `[-2^(w-1), 2^(w-1)-1]`.
Because the true final integer lies strictly inside this interval, its
residue determines it uniquely. Dirty rows have no small-norm hypothesis:
they can begin as arbitrary w-bit patterns and are returned unchanged.

For the 52-factor fixture, every K_i = 2, X=Y=7 and
`R = 31,525,197,391,593,479 < 2^55 = 36,028,797,018,963,968`; w=56
suffices. The inherited PR1057 prefix majorant for the same tree is

```
H(leaf) = 1 + K,
H(node) = (arity+1) K^(number of factors below node) max H(child).
```

It gives 114 sufficient signed bits when every initial cell is bounded by
seven, and 167 for arbitrary signed 56-bit dirty values. These are comparisons
to a proved sufficient majorant, not integer-width lower bounds. The stress
fixture's independently executed integer lift actually reaches 90 signed
bits. The credited 56-factor plan retains 1,568 calls and gives a separate
119-to-60 comparison of sufficient widths.

## Literal dense leaf and private work

The reference machine has five data arrays of length L and a read-only
residue coefficient table. Its four private scalar registers have capacities:

| Register | Use | Capacity |
|---|---|---:|
| a | row accumulator | w+1 unsigned bits |
| v | source/target value and signed target update | w+2 signed bits |
| c | coefficient residue | w unsigned bits |
| p | unreduced product | 2w unsigned bits |

For each output coordinate, zero a. For each source coordinate, read v and
c, multiply into p, reduce p to its low w bits, add p to a, and reduce a to
its low w bits. Then read the current target into v, add or subtract a,
reduce v to its low w bits, and write it back. Finally zero all four private
registers. Four startup zero assignments are explicit too.

Before each multiplication both operands lie in [0,M−1], so p < M^2 fits
2w bits. After product reduction, the accumulator addition is at most
2M−2 and fits w+1 unsigned bits. The signed target update lies between
−(M−1) and 2M−2 and fits w+2 signed bits. The next reduction returns a
canonical w-bit value. These bounds do not depend on recursion depth or
the magnitude of the integer lift. The private storage is **5w+3 bits**.

`LOW(b,w)` is a paid operation replacing a b-bit work value by its low w
bits. On an explicit bit representation it can overwrite the upper b−w
bits with zero, with its access/routing work charged by the implementation.
The reference interpreter uses a mask and checks all register capacities.
Neither LOW nor private clearing is treated as free or asserted reversible.
The private registers are owned work with a zero exit contract; the arbitrary
dirty restoration theorem applies to the five data arrays.

Per leaf, the exact command bill is

```
L^2 multiplies
L^2 + L adds/subtracts
2L^2 + L reductions
L + 4 zero assignments
2L^2 + L reads (including coefficient reads)
L writes.
```

This is `6L^2 + 5L + 4` commands, compared to the inherited integer leaf's
`4L^2 + 4L + 4`. For L=2 it is 38 versus 28. With N=1,376 calls, including
startup, the modular execution has 5,504 multiplies, 8,256 adds/subtracts,
13,760 reductions, 8,260 zero assignments, 13,760 reads and 2,752 writes:
**52,292 commands**. Preparation and output decoding are additional below.

## Recurrence and full conditional price

If `C_t(s,d,q,w)` is the actual cost of a completed subtree at its specified
ports, define it by summing the child costs over the displayed four- or
eight-call template, including each negative call. Address-dependent costs
are evaluated at their actual ports. When the completed-child prices are
sign-symmetric and independent of ports, this reduces to

```
binary:  2 C_0 + 2 C_1,
ternary: 2 C_0 + 4 C_1 + 2 C_2.
```

No array copy, zeroing, width conversion or additional data-restoration work
is required at an internal boundary. Control/routing costs are still paid.
The leaf multiplicities and planner are exactly those of PR1057; this pass
does not optimize them or alter the direct all-role call obstruction.

For N dense leaves at a common w, let MUL(w) include the implementation of
a w-by-w product with its 2w-bit destination, ADD(b) its indicated unsigned
or signed operation, Z(b) clearing, and LOW(b,w) reduction. The arithmetic
and private-clearing term is exactly

```
N L^2 [MUL(w) + ADD_unsigned(w+1) + LOW(2w,w) + LOW(w+1,w)]
+ N L [ADD_signed(w+2) + LOW(w+2,w)]
+ [N(L+1)+1] Z(w+1)
+ (N+1) [Z(w+2) + Z(w) + Z(2w)].
```

Original coefficient access/preparation, input encoding and decoding are
separate paid terms. Setup reads the nL^2 original signed coefficients,
reduces them and writes the residue table; it encodes the 2L input/output
cells. Thus it includes **nL^2+2L reductions** (212 in the main fixture),
their reads/writes and the original coefficient/input widths. Computing
norms and G, the width, the parent plan and the unrolled program is paid
setup too, with its own integer/control storage. Original coefficient
descriptors or source storage retained by the caller must be added to the
table's nL^2 w bits. Final signed decoding costs L instances of a declared
decode/read/write routine. No conversion is inserted inside recursion.

The exact data itinerary uses cells `sL+j`, `tL+i` and
`5L+(factor*L+i)L+j`. Each leaf returns the data head to cell zero. Let D be
the measured intercell distance and E the number of reads plus writes.
For the specified full-cell scans and returns, add

```
w E bit actions,
w D + 2(w-1)E data-head moves,
E Address(a) address/control cost,  a = ceil(log2(5L+nL^2)).
```

The interpreter and a separate closed itinerary agree on D=1,332,416,
E=16,512, a=8: 924,672 data bit actions and 76,431,616 data-head moves at
w=56. Private-register arithmetic travel is included in the implementation
of MUL/ADD/LOW/Z, not in this data-region head count.

An unrolled leaf record uses `b=max(1,ceil(log2 n))+2*3+1` bits for factor,
two ports and sign. Charge Nb storage/read bits, 2Nb forward-and-rewind
program-head moves and N calls of an explicit dispatcher `Dispatch(b,a,log L)`.
Here b=13 and Nb=17,888. Backend control storage, any additional frame or
supplier source-access adapter, and coefficient/input setup and decoding
must be added. No fixed-tape compiler or measured timing is claimed.

This full conditional bill exposes the trade: narrower data and arithmetic
operands, unchanged recursive calls, more reduction commands and wider
private product storage than the data width. Its benefit depends on actual
MUL/ADD/LOW, preparation and routing implementations. There is no inferred
new kappa or asymptotic supplier improvement.
