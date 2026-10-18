# A finite rank-one QQ16 child followed by a rounded half-ADD

Fix one 512-complex-coordinate payload. Its norm is the ordinary Hilbert
norm, with real and imaginary components both counted. There is one source
field x and a distinct destination field d. Both are writable by this pair.
Other persistent fields are inaccessible to the implementation.

Let q = 2^ell > 0, M = 2^b and s = b-ell >= 1. Every entry component is a
multiple of q, has magnitude strictly below M, and is exactly representable
with p binary significant bits, p >= 2. These are joint lattice, range and
significand hypotheses. They do not follow from an input norm bound alone.

The native child is the pinned rank-one recipe U = L C R. Its left and
right factors are exact monomial permutations with phases in {1,i,-1,-i}.
For two complex coordinates a+ib and c+id, the central C is

```text
((a-b+c+d) + i(b+a+d-c))/2,
((c-d+a+b) + i(d+c+b-a))/2.
```

The unitary semantics of the retained native recipe are inherited from the
QQ16/native sources. The direct formula above and the pair-first formula
below agree exactly. This package does not recertify every retained native
recipe or its frame interpretation.

## Rounded implementation and defects

Put epsilon = 2^-p. RN rounds each real component to p significant binary
bits, ties to even. There is no overflow, underflow or subnormal truncation
in the finite format proved below. Thus

```text
|RN(v)-v| <= epsilon |v|.
```

First form the four pair sums/differences

```text
sr=RN(a+c), si=RN(b+d), dr=RN(a-c), di=RN(b-d).
```

Then form RN(sr-di), RN(si+dr), RN(sr+di), RN(si-dr), followed by exact
division by two. Apply the exact left monomial to the resulting payload.
Write the returned source as xhat.

On the real coordinate vector, each of the two unnormalized mixing layers
has norm sqrt(2). Componentwise RN has vector error at most epsilon times
its exact operand norm. If e1 is the first-layer error and e2 the second,
then

```text
||e1|| <= epsilon sqrt(2) ||x||,
||e2|| <= epsilon sqrt(2)(sqrt(2)||x|| + ||e1||).
```

The final exact factor 1/2 and the monomials give

```text
||xhat-Ux|| <= (2 epsilon + epsilon^2) ||x||.             (1)
```

Next implement the literal scalar event by exact multiplication of xhat by
-1/2 and one RN per component of d-xhat/2. Write its result as dhat. Its
completed error is relative to the actual returned child value:

```text
||dhat-(d-xhat/2)|| <= epsilon ||d-xhat/2||
                     <= epsilon (||d|| + ||xhat||/2).  (2)
```

In particular this step charges its own nonzero rounding. It does not assume
scalar exactness after an approximate child. Combining the pair against its
ideal input, one may also use

```text
||dhat-(d-Ux/2)||
 <= epsilon ||d|| + (3 epsilon+3 epsilon^2+epsilon^3)||x||/2.
```

For the local allowance u = 2^(-beta-delta-102) in PR3235, choose
p >= beta+delta+104, with nonnegative integer beta,delta. Then
epsilon <= u/4 and 2 epsilon+epsilon^2 <= u. Equations (1) and (2)
therefore satisfy exactly the completed native and ADD error inequalities
used by that conditional envelope. This does not establish its other
53,096 event boundaries or a whole-producer theorem.

## Finite range, lattice and workspace

Use common integer quantum g=q/4 and signed width W=s+6. Initially the
integer components are multiples of four. Rounding an integer multiple of
four to p significant bits preserves that divisibility. Pair/cross numerators
therefore remain multiples of four; the native division by two gives
multiples of two; the half-ADD multiplication gives integers. Neither exact
division discards a bit. RN can coarsen the lattice but never refines it.

Before the native division, the largest component magnitude is less than
4M(1+epsilon)^2 <= 25M/4. The source output magnitude is less than 25M/8.
The half-ADD numerator is less than 41M/16, and its rounded result is less
than 205M/64. All are strictly below 8M. The signed W-bit range in quantum g
is [-8M,8M-g], so every temporary, rounding carry and completed value fits.
The reference checks the width before and after each rounded operation.
No assumption of a floating exponent range wider than this finite lattice
is used.

The implementation may overwrite x after its central butterfly and may
overwrite d at the half-ADD. It uses two owned 512-complex-component buffers
and at most eight real component temporaries. Owned buffers are cleared on
entry and exit. They are not borrowed dirty helpers. The payload storage
allowance is 4,104 W-bit words including x and d. This is an abstract numeric
schedule, not the Python interpreter's allocation or RSS. Two fixed monomial
lookup tables add 11,264 bits of destination/phase metadata. The table and
recipe validation happen before numeric execution; source loading, tests,
code and control storage are outside the payload count.

The reference returns only the two declared writable fields, and clears both
owned buffers before return. It neither reads nor changes another persistent
field. It proves no later restoration of the source or destination, which
are changed by the mathematical events themselves.

## Direct numeric invoice

For the one rank-one child and half-ADD, the explicit schedule charges:

| Primitive | Real component operations |
| --- | ---: |
| Addition or subtraction | 3,072 |
| RN to p significant bits | 3,072 |
| Exact halving | 2,048 |
| Signed monomial move | 2,048 |
| Owned scratch CLEAR, entry plus exit | 4,096 |

Thus the numeric word bill is 3,072 C_RN(W,p) plus 11,264 other W-bit
primitives. RN is a compound integer operation, not an assumed unit-cost
bit operation. `nearest` gives its explicit abs, bit-length, power-of-two
quotient/remainder, tie comparison and reconstruction algorithm. No claim
about a recursive native-child tariff follows from this direct word bill.

Address lookup, owner routing, physical movement, scratch placement, input
preparation and code/control storage remain unpriced. In particular, a
favorable complete supplier allowance is not established here. This is the
local finite numerical contract requested by the handoff, with its direct
arithmetic and logical storage costs exposed for a future physical caller.
