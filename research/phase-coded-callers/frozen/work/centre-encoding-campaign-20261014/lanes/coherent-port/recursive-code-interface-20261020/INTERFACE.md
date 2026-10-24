# A closed upper code and its recursive access conditions

The changed terminal has a useful closed code family. On a fixed
selected row set P and its complement R, write

```text
N(B) = iota_P B pi_R,
C(B) = I+N(B).
```

The coefficients of B can be spatial operators. They need not commute.
For all B and D,

```text
N(B)N(D)=0,
C(B)C(D)=C(B+D),
C(B)^-1=C(-B).                                      (1)
```

Thus this code does not acquire products of reader coefficients while
the row partition remains fixed. This is a positive interface result.
It does not, by itself, supply a recursive native implementation.

The actual next child must receive the right code on its gathered
axes. A change of those axes need not leave a scalar reader. An
actual reader edge below gives a four-line operator after such a
change. Also, a deeper recursive call uses a new row digit. Its
selected projection is not the projection in (1).

This note separates these two access conditions from the closed
algebra. It does not prove that every possible coded recursion fails.
No new supplier, native saving, or kappa bound is claimed.

The coordinating and independent-review lanes proposed the changed
terminal and its four-code rule. This note checks their recursive
interface conditions against the actual reader and child contract.

## Sources and unchanged contracts

All paths in this note are relative to the campaign lanes directory.
`CHECKS.json` gives the full paths and digests.

The actual selected set, reader H, and response D come from
`new-core-transfer-20261017/low-displacement-20261020/row-only-capture-20261020/run-normal/PRODUCTIVE-CAPTURE.json.gz`.
Its decompressed digest is
`7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2`.
There are 16 selected and 96 ordinary ports. The exact checks give

```text
D=-H^T,
HD=diag(-5 I8,-7 I8).
```

H has 160 signed half coefficients and 56 unit coefficients. Its
direct scalar ADD word costs 2,048 old real primitives.

The clean forward and backward words are the frozen
`CLEAN-LATE-EXCHANGE.json.gz` and `CLEAN-DUAL.json.gz` in that lane.
They have 224 data fields and 416 other fields. The 416 fields are
arbitrary and unchanged. They are not clean storage.

The routed no-reset terminal is pinned by
`independent-review-20261017/no-reset-terminal-factor-20261020/FREEZE.json`,
digest
`1b1f191e9de1ef20b88aca6d870f93fe68b0923e8b05a87d9ca7d960e0385963`.
Its terminal factor is

```text
diag(Q_P,Q_R^2,-I) W^-1 L W,
W=diag(I_P,Q_R,I_R).
```

This is a decoder on `(beta,h,R)`. It is not a bare supplier code.
The selected-X sign and the final bank exchange are separate.

The current recursive source, `notes/batched-complex-rows.tex`, keeps
all compact and spectator ranges in a child and gives that child
exactly 1/W of its parent's volume. Its selected axes are gathered
before the call. Each recursive level has a new row digit. The
complete dirty-helper contract in `research/idle-axis-hosting/PROOF.md`
requires the exact pending native operator on arbitrary helper input.
Neither contract grants a joint code on unrelated principal arrays.

## The changed terminal

In the pinned terminal, omit only the last shear

```text
b <- b-H0 t.
```

The other seven shears give `(alpha,u,-v)`, where
`alpha=a+H0 u`. After the stated signs and the positive Q on the
112 recovered data fields, the output is

```text
(F25 Y0, F25 K(H0) X0),
K(B)=Q C(B) q,       q=Q^-1.                         (2)
```

Here H0 is the root reader. Its scalar port map has no stage route.
It commutes with the common full transform. The Q operators in (2)
remain on their own fields.

For one common Q, (1) gives

```text
K(B)K(D)=K(B+D).
```

The omitted shear changes the endpoint claim. It does not delete
the cost of reading H0 from a caller that requires the raw output.

If the 16 selected positive Q operations are also omitted, the code is

```text
Khat(B) = [[q_P, B q_R],
           [0,   I_R ]].                            (3)
```

The resulting terminal has 192 line operations. This code includes
a selected diagonal phase. It is not a member of the unipotent
family (1).

## What survives at one row digit

Let A preserve the P/R row partition, with diagonal blocks A_P and A_R.
The blocks can contain noncommuting spatial or parent-field operators.
Direct multiplication gives

```text
A C(B) A^-1 = C(A_P B A_R^-1).                       (4)
```

Consequently, all upper defects inserted at one internal row digit
remain one upper defect under a word of such operations. This remains
true if its B block links several parent principal arrays. A native
array advance, an address view that does not change that row digit,
and a scalar parent-field operation all preserve the partition.
Equation (4) is an algebraic statement; the coefficient that it
produces may require native work to read.

If each principal array instead has its own stored code, an ADD has
an explicit relative-code condition. For stored arrays
`xhat=C(Bx)x` and `yhat=C(By)y`, the semantic ADD `x<-x+c y` requires

```text
xhat <- xhat+c C(Bx-By)yhat.                         (5)
```

The unchanged ADD is valid only if the relative code acts as the
identity on the source state. The source is arbitrary here. One can
instead track a joint code by (4), but that choice does not make its
eventual removal free.

## Exact child entrance

Write Q_U for the port line operator defined by one gathered native
block U. Suppose the stored code is `K_U(B)=Q_U C(B) q_U`. The next
child uses gathered block V and the usual physical input `Q_V x`.
Its logical input code is exactly

```text
q_V K_U(B) Q_V
 = I+iota_P [q_V,P Q_U,P B q_U,R Q_V,R] pi_R.        (6)
```

When U and V, their row roles, and their views agree, the adjacent
factors cancel and (6) is C(B). This is the useful matched entrance.
For distinct gathered blocks, (6) is still upper, but it need not be
a plain scalar or affine reader.

The actual H edge from ordinary port 2 to selected port 0 has
coefficient 1/2. Their native labels are respectively 35 and 11.
Use two disjoint equal-width native blocks. At one tensor copy,
the nonconstant coefficient in (6) has the four line directions

```text
11, 35, 11<<9, 35<<9
```

with signs `(+1,-1,-1,+1)`. They are linearly independent. The exact
Gaussian column of the operator has 16 nonzero entries, each
computed by the checker. Its symplectic Fourier rank is four.
At tensor width f its column support is exactly `16^f`. If the
blocks coincide, the same calculation gives the identity.

This check does not impose a restriction on all possible new code
services. It shows that the current scalar reader does not certify
this changed entrance. A fixed finite sum of payload monomial reads
cannot equal that coefficient for every width. A word with a growing
number of scalar ADDs, a new native reader, or a different gather can
remain possible; each needs its own cost and source contract.

The example uses the complete-row child contract to choose disjoint
gathered blocks. It does not claim that a specific two calls in the
latest 640-field global host use those blocks. Such a host has not
been admitted for this new interface.

## Why the retained left-reader service is not enough

For a central forward shear with response E, codes on both banks
give the exact typed operation in bank order (X,Y):

```text
diag(Cx,Cy) [[I,0],[E,I]] diag(Cx,Cy)^-1
 = [[I,0],[Cy E Cx^-1,I]].                          (7)
```

The retained fixed-reader service supplies `Cy E`. It supplies (7)
when the source code is the identity, or when a separate proved
operation supplies the right factor `Cx^-1`. It does not establish
that factor merely because the next physical entrance contains Q.

The inverse adjoint of the left-coded response is `E* Cy*`.
For an upper code, `Cy*` is lower. It is generally not `Cy^-1`,
which is upper with its sign changed. Thus the forward service and
its current adjoint are not yet a closed recursive code alphabet.
The missing operation is an actual source-code cancellation or a
different native response with the full block in (7).

## Fresh row digits

The same partition cannot be used without change at every depth
under the retained 1/W child-volume contract. The parent role is
fixed within one principal child array. The child's own selected
and ordinary roles belong to a later row digit.

This distinction is visible without native phases. Restrict to one
actual nonzero H edge and put `C=I+(1/2)e_12`. On d independent row
digits, the corresponding product is `C^tensor d`. Then

```text
(C^tensor d-I)^(d+1)=0,
(C^tensor d-I)^d != 0.                              (8)
```

For example, d=2 has a nonzero product of the two nilpotent maps.
The checker verifies d=1,2,3,4 exactly. In general the top term is
`d! (C-I)^tensor d`, which is nonzero in characteristic zero.

Thus the square-zero claim at one row digit does not prove a
depth-independent square-zero claim for the whole recursion.
Equation (8) is not a lower bound on removal cost. A structured
multi-digit code can still have a short description and a separate
algorithm. No such full algorithm is supplied here.

## A valid four-code identity

The polynomial `q^3-q^2+q-I` vanishes at the one-copy eigenvalues
1 and -i. It fails at tensor width two: at eigenvalue -1 it equals
-4. Therefore the original alternating-sign four-code proposal
does not apply at all widths.

There is a corrected identity. Let A be any map from R to P, and
let q act on P with `q^4=I`. Set

```text
K_(e,s) = [[q^e, s q^(e-1) A],
           [0,   I           ]].
```

Use the chronological sequence

```text
(e,s) = (1,+1), (3,+1), (1,-1), (3,-1).
```

The first two codes have product
`I+N((q^3+q^2)A)`. The last two have its inverse.
Thus the complete product is the identity. No q passes through A.
The checker also uses a noncommuting matrix A and all four phase
eigenvalues as an exact control.

For (3), A must be the same transported `B q_R` in all four calls,
on the same row partition and with the same q_P. The exponent
change from 1 to 3 is a selected q_P^2 translation. The identity
does not prove those entrance conditions or the reader equality.
In particular, four identical semantic transforms on the same
block give only their fourth power; this is not a new productive
full-transform supplier by itself.

## The common-q alternative

The separately frozen phase-coded triple has endpoint

```text
(-F25 q Y0, F25 q X0)
```

on arbitrary physical inputs. Its source is
`native-escape-20261017/phase-coded-triple-20261020/FREEZE.json`,
digest
`0ee32fe22f42cffce2a9673f0dc95496a4b4bb8b11a534f77a11f5fe9c7aeb4b`.
The current proof and complete phase replay are inherited here.

Each q_p has odd norm in dimension 25 and is not the characteristic
vector. An orthogonal basis can start with q_p. Therefore
`F25 q_p`, up to its exact monomial frame factors, is a rank-24
native operator. This interpretation has target mass `224*24=5376`.
The actual profile is

```text
4176 H1 + 192 H2 + 144 H3 + 48 H8.
```

It has exactly that mass. If this word is used as an H24 supplier,
then for every 0<b<1 and every child rank r<24,

```text
r^(1-b) > r / 24^b.
```

The normalized child moment is therefore strictly greater than one.
Relabeling the word as an H24 supplier does not give a positive-b
saving. It can still be useful as a coded H25 operation if a proved
caller consumes the missing q factor.

## A safe output conversion and the open contract

For an actual root reader H, a standalone removal of `K(H)` can use
the existing 112 data fields:

```text
apply q to all 112 fields;
apply C(-H), with its 216 scalar ADDs;
apply Q to all 112 fields.
```

This gives the exact inverse code on arbitrary data. It has 224
rank-one line operations and 2,048 scalar primitives, before line
side maps and whole-stream address costs. No clean accumulator is
used. This is a safe upper bound, not an optimum or a strict saving.

A useful positive recursive construction must instead bind all of:

1. the two-sided operation (7), or an equivalent code update;
2. the gathered-axis code in (6) at every child entrance;
3. the code on every borrowed output, with its actual next owner;
4. the multi-digit description and its scalar/address cost;
5. a raw outer output or a priced final conversion.

The closed upper algebra removes an operator-product problem. It
does not remove these physical access and hosting conditions.

## A same-block inverse companion

There is also a positive two-type construction with an explicit
scope. Suppose a reversible supplier has the complete endpoint
`S=C F`, with the identity on every borrowed field. Suppose

```text
C=W^-1 L W,     WF=FW,     LZ=ZL,
J=W^-1 Z W is monomial,
Z F^-1 Z=(-i)^e F.
```

Here F is the full transform on e selected axes. Z is the sign on
those axes. Then J commutes with C, and

```text
i^e J S^-1 J^-1 = F C^-1.                          (9)
```

Thus the forward word has type `I -> C`, and its transformed reverse
has type `C -> I`, with positive semantic F in both cases. The
second word after the first gives F^2. The equality holds on every
input, including arbitrary borrowed values.

For the upper code K(H0), take `W=q`, `L=C(H0)`, and the common
all-axes sign Z. The root reader is a scalar port map, so it commutes
with Z. On an odd line p, at tensor width f,

```text
Q_p Z q_p = (-i)^f X_p Z.
```

Therefore J has one translation, one address sign, and a known
scalar phase on each coded field. It has no new native factor.
Every inverse native kernel in the reversed word can use
`C_axis^-1=X_axis C_axis`; its translation must be included in the
wrapper. This retains the native profile. Scalar inverses, address
passes, and the two J wrappers still have their own costs.

Equation (9) is a complete endpoint statement only for a supplier
that has the stated S endpoint and borrowed-field contract. The
208-line coded terminal gives such a candidate after its explicit
bank exchange. It already has mass 5,600. This lemma does not turn
that mass into a strict saving, and it does not apply without a new
derivation to the cheaper code Khat.

For two different gathered blocks, the join contains `C_V^-1 C_U`.
It cancels only when the two transported codes agree. Equation (6)
is the actual condition at that join. Thus (9) gives a useful
same-block type pair, not a complete recursive reuse theorem.

## Verification

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/coherent-port/recursive-code-interface-20261020/check_interface.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/coherent-port/recursive-code-interface-20261020/check_interface.py
```

The checker pins every input. It reads actual source matrices but
imports no source interpreter. It checks the 16 centre planes,
noncommuting upper-code identities, the exact four-line column,
the same-block control, the fresh-row-digit controls, the failed
one-copy polynomial, and the repaired four-code identity.
It does not repeat the native word, global phase, or owner reviews.
