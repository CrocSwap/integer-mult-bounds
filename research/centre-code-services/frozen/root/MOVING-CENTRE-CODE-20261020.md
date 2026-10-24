# A centre code that moves with the native phase

A change to the reader removes the inverse requirement in
RANK30-PHASE-SECTION-20261020.md. The useful matrix is the constant
B=VU, rather than VQ^2U. For both actual low-rank responses, B is
invertible. The new entry code uses scalar maps and translations.
After the native advance it has exactly the section and reader of
the terminal correction.

The rank-sixteen response has an additional property. Its induced
centre action is diagonal. In the transported code, its complete
conjugated response can therefore be applied by sixteen scalar
multiplications on existing data carriers. No centre cohort is needed.
The exit remains encoded. This result does not remove that exit code
or prove its compatibility with an interleaved productive call.

## Hypotheses and actual responses

Let E=I+UV be an invertible scalar response on n fields. The matrices
U and V have full column and row rank r. Assume B=VU is invertible.
Put H=I+B. Then H is invertible. Direct multiplication gives
H^-1=I-V E^-1 U.

Let Q be the diagonal matrix of actual native line phases. Assume
Q_p^4=I exactly, and let L=Q^2. Each L_p is the specified simultaneous
translation. Let F be one common native operator which commutes with
Q and with every scalar matrix on these fields. Define the physical
data advance

```text
A = F Q^-1.
```

The commutation premise is material. A port-dependent routed F need
not commute with U, V, or the chosen scalar code.

The actual rank-thirty factor has B equal to eight blocks

```text
[ -4   1 ]
[  2  -2 ]
```

and eleven scalar blocks -5 and three scalar blocks -3. The 2 by 2
blocks have determinant 6.

For the actual rank-sixteen factor,

```text
B = diag(-6 I_8, -8 I_8),
H = diag(-5 I_8, -7 I_8).
```

Thus the rank-sixteen section reader needs only the odd divisor 3.
The inverse centre action needs 5 and 7. These are different steps
with different exact-grid obligations.

The rank-sixteen factor is taken from the actual frozen native response,
not from a new hypothetical matrix. Its native word, full inverse,
rank factor, and ordinary principal block have separate exact reviews.
The selected ordinary inverse can require 31; the whole-bank code here
does not use that principal inverse.

## A section with the required reader

At entry set

```text
J_in = L U,
D_in = B^-1 V L.
```

Since L^2=I, D_in J_in=I. Both maps use only scalar operations and
the declared translations. There is no inverse of VLU.

Advance the data by A and a centre bank by F. The transported maps are

```text
J_out = A J_in F^-1 = Q U,
D_out = F D_in A^-1 = B^-1 V Q^-1.
```

The exact desired response is therefore

```text
M = Q E Q^-1 = I+J_out B D_out.
```

This is the required negative-phase reader VQ^-1. It does not have the
reader mismatch of the earlier section D=(VLU)^-1 V.

For arbitrary a,z, use the lossless section swap

```text
S_in(a,z) = ((I-J_in D_in)a+J_in z, D_in a).
```

It is an involution. Its short word is

```text
a += J_in z
z -= D_in a
a += J_in z
z *= -1
```

The stored value of z is transferred into the data; it is not erased.
The middle operation needs a priced additive service. One option is
to apply B to z, subtract V L a, and apply B^-1 to z.

All entry translations can be grouped. If S_0 is the same swap with
J=U and D=B^-1V, then

```text
S_in = diag(L,I) S_0 diag(L,I).
```

Thus two passes of L on the data suffice for this explicit lowering.
At n=112 this is 224 declared translation-map calls. They retain their
packed-map cost. The scalar swap and its fixed-odd scans are separate.

Let S_out be the transported swap. Its defining exact relation is

```text
diag(A,F) S_in = S_out diag(A,F).
```

It satisfies

```text
S_out diag(M,I) S_out = diag(I,H).
```

To check the last identity, write a=b+J_out c with D_out b=0.
S_out exchanges c and z; M leaves b fixed and sends c to Hc.
Conjugation therefore leaves the data fixed and sends z to Hz.
This proof includes every arbitrary data and centre input.

## A square code on the existing data bank

There is no need to introduce r new centre fields if a scalar change
of the existing n coordinates is allowed. Choose r physical rows P
such that U_P is invertible, and write R for the other rows. Define

```text
C_0 a = (c,b),
c = B^-1 V a,
b = a_R-U_R U_P^-1 a_P.
```

The r centre outputs use the P carriers. The other outputs use R.
The inverse is

```text
t = c-B^-1 V_R b,
a_P = U_P t,
a_R = U_R t+b.
```

These formulas prove invertibility. They also give

```text
C_0 E C_0^-1 = diag(H,I_(n-r)).
```

The actual rank-thirty unit minor is checked in a separate lane packet.
The actual rank-sixteen pivot word uses an unnormalized sum and a
different complement after its pair code. It is a different conjugator.
The more general transport statement below applies to both words.

The normalization is optional. Replacing c by V a multiplies the first
r output rows by B. Because B commutes with H, the new code still
conjugates E to diag(H,I). This sum code is dyadic when U_P^-1 is
dyadic. Its inverse uses B^-1 only on values in the proved code image.
There the odd divisions are exact. This valid-code statement does not
establish divisibility after an arbitrary intervening operation.

More generally, let C be any invertible scalar code with
C E C^-1=K. The following transport uses this identity alone.

Take the physical entry code to be

```text
C_in = C L.
```

Moving it through A gives

```text
C_out = A C_in A^-1 = Q^-1 C Q^-1.
```

The response M has the following action in the output code:

```text
C_out M C_out^-1 = Q^-1 K Q.
```

This identity is exact and keeps the order of all port phases. It is
not enough to diagonalize E as a scalar matrix and then discard Q.

For the normalized code, K=diag(H,I_R), so the first block is
Q_P^-1 H Q_P. For the actual rank-sixteen pivot word K is diagonal.
Therefore Q^-1 K Q=K. At this encoded cut M is exactly eight multiplications
by -5, eight multiplications by -7, and identity on the other 96
coordinates. It uses the sixteen existing pivot fields. An inverse
response uses the reciprocals, with their stated 5/7 grid requirement.

This proves a useful encoded primitive. Start with the entry code
C_in a, apply the complete advance A, and then apply the stated centre
action. The physical output is C_out M A a. It is the required
response and advance in the declared output code. Preparing C_in
uses only the scalar code and translations. All native work is in A.
This primitive does not prove that a larger productive word has this
advance as a separable step at a legal common cut.

## A finite reuse cycle

Assume successive data advances are A_s=F_s Q^-1, with the same Q.
Assume each F_s commutes with C and Q. These hypotheses can hold
for a construction family; they must be checked on the actual routed
operators in a supplier.

Conjugating the code through successive advances gives the exact cycle

```text
C L
  -> Q^-1 C Q^-1
  -> L C
  -> Q C Q
  -> C L.
```

The identities use Q^4=I. At every even cut the code and its inverse
use only C and translations. Thus two advances can consume one cheap
entry code and return a cheap exit code without a separate odd-phase
decode. Four advances return the original code.

Alternatively, an advance F_+ Q^-1 followed by F_- Q transports the
first output code directly back to C L, under the same commutation
conditions. The identity does not require the two F operators to be
equal.

Interleaved operations require their own typed endpoints. They cannot
be ignored when applying this cycle. In particular, a port code that
mixes different stage routes can violate the commutation premise.
The current three-call controller also ends at an odd cut. Neither
the cycle nor a bounded codebook alone removes that final code.

## Remaining construction obligations

The exact coefficient and phase identities solve a specific obstacle:
the centre reader can be obtained by transport from a scalar and
translation entry code, with no extra field cohort. The actual
rank-sixteen response then has a diagonal centre action.

The next required work is to bind that code to a complete productive
caller. Such a caller must check the chronology of each capture, all
interleaved ADDs, the current and past owner views, arbitrary borrowed
state, and the final raw endpoint. It must implement an exit decode
or a proved matching code transition. It must price all scalar,
translation, view, and exact-grid work, as well as recursive children.
An unpriced output code does not constitute a supplier improvement.

## Credit and status

The independent moving-code review is:

```text
../lanes/bridge-review-20261017/moving-code-review-20261020/FREEZE.json
SHA256 0432a54d1e99122b61472c203a590ea8bd8508f13e3c80a086eb42430ecfc279
```

It checks both actual square codes, every data input column, the complete
arbitrary-input section swaps, the source matrices, and the all-width
transport argument. Normal and optimized runs give identical receipts.
The rank-thirty swap costs 5076 dyadic scalar primitives, 224 translation
maps, and 22 complex fixed-odd multiply/divide pairs. The rank-sixteen
swap costs 4448 dyadic primitives, 224 maps, and eight such pairs. Both
have exact stored opcode-prefix row norm 12. These swaps use a separate
centre cohort; they are not the no-cohort pivot-code invoice.

The frozen rank-sixteen pivot code is:

```text
../lanes/new-core-transfer-20261017/low-displacement-20261020/
pivot-codes/FREEZE.json
SHA256 86a1abd93f4ebc37ae54dbaabf5cade3b62a6d1d7fcd54d4f3cf5e58785b37b7
```

Its code and inverse each cost 2078 old real scalar units plus sixteen
real fixed-3 scans in the declared literal lowering. Entry C Q^2 adds
112 explicit translation maps. It uses sixteen existing pivots and no
owned or additional field. A valid-code inverse has exact divisions;
arbitrary inverse inputs need the admitted exact grid. Its producer
checks all 640 roles. The moving-code review separately checks the
112-field matrix and both inverse orders. The complete physical caller
remains outside both checks.

The coherent-port lane found the corrected reader and the square-code
transport formula. The native-escape lane bound B and H to both actual
factors and supplied their short scalar services. The bridge-review lane
checked the transported section and grouped its entry translations.
The root supplied the finite reuse cycle and this combined statement.
The low-displacement response, cyclic native family, signed pair code,
and prior translation-code work are credited in their source packets.

The actual scalar factors, both square codes, every input column, and
the phase transport identities have separate independent review in the
bridge-review lane. The proof above gives the all-width statement and
the finite reuse cycle. It uses AI assistance. No PR or publication is
authorized. Before any future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
