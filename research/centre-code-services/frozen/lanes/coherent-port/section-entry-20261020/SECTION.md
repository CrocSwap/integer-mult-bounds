# An entry code for the actual rank-thirty response

The actual factorization E=I+UV admits an invertible code on the existing
112 data fields. It exposes thirty correction coordinates and retains
the other eighty-two coordinates. It needs no additional data family.
The selected minor has determinant -1/256 and an integral inverse.

A translation at entry selects the correct phase orientation. After a
positive Q-to-FULL advance, the correction Q E Q^-1 acts only on the
thirty encoded coordinates. Fourteen of those actions are scalar.
The other sixteen form eight two-field actions with the same
isotropic line difference 45.

These are exact algebra and interface results. They do not give a
complete coded native F/B call or a raw terminal decoder. The precise
remaining code transitions are stated below.

## Inputs and notation

The pinned response is
`new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json`,
SHA256
`5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c`.
It supplies U with 112 rows and 30 columns and V with 30 rows.

Write Q=diag(C_qp) for the physical port lines and L=Q^2. For every
tensor width, Q^4=I and L is a fieldwise uniform translation. Put

```text
B0 = VU,                 D0 = B0^-1 V,
H  = I+B0.
```

For the actual factors, B0 consists of eight blocks

```text
[ -4   1 ]
[  2  -2 ]
```

and fourteen scalar blocks: eleven -5 and three -3. Thus B0 is
invertible. The block determinants are six. The corresponding H
blocks are [[-3,1],[2,-1]], -4, and -2. H and H^-1 are dyadic.
B0^-1 can have factors three and five in its denominator.

The constant-word compiler and its price belong to the
`native-escape-20261017/rational-code-admission-20261020` packet.
This packet verifies the matrices but does not replace that compiler.

## An arbitrary-state section exchange

Set

```text
J = L U,                 D = D0 L.
```

Then DJ=D0 U=I. For a data bank a and an independent thirty-field bank z,
the map

```text
S(a,z) = ((I-JD)a+Jz, Da)
```

is an involution. One ordered implementation is

```text
a += Jz
z -= Da                  using the updated a
a += Jz                  using the updated z
z *= -1
```

Both inputs are arbitrary. One application transfers the old z into
the data. It does not restore z. A second matched application restores
both banks.

The two L factors can be placed outside a constant scalar section
exchange:

```text
S = diag(L,I) S_(U,D0) diag(L,I).
```

Thus the entry maps use translations and scalar operations. This
does not make their execution cost zero. An additive D0 service on an
arbitrary centre bank can use B0, a V gather, and B0^-1. Its scalar,
odd-division, and stream costs must be charged.

Under the physical advance diag(F Q^-1,F), where F is common to both
banks and commutes with the displayed port operators, the section
becomes

```text
J_out = Q U,             D_out = B0^-1 V Q^-1.
```

This is the required orientation:

```text
Q E Q^-1 = I + J_out B0 D_out.
```

In the output section coordinates this action is identity on the
data complement and H on the centre bank. A thirty-field productive
cohort and its advance F are not supplied by the factorization.

## A square code on the existing data

Use these thirty physical carrier slots, in the stated order:

```text
0,27,9,61,11,63,20,46,37,110,41,106,76,87,78,99,
5,3,24,23,1,8,29,26,4,18,19,39,6,31.
```

Call this set A and its complement B. The rows U_A form a unit with
determinant -1/256. Its inverse has integer entries. Store centre
coordinate j in physical slot A[j]. Define the square code C0 by

```text
c = D0 a,
r = a_B - U_B U_A^-1 a_A.
```

Here C0 is a matrix name. It does not denote the private scratch field
called C0 in older source packets. The inverse is

```text
u   = c - (D0)_B r,
a_A = U_A u,
a_B = r + U_B u.
```

Both inverse orders hold on every input. The following block updates
give C0 in place:

```text
a_A = U_A^-1 a_A
a_B -= U_B a_A
a_A += (D0)_B a_B
```

The final additive map must retain the current arbitrary a_A. It can
be lowered as B0 on a_A, then a V_B gather, then B0^-1 on a_A.
The full code preserves all 112 input coordinates. It makes

```text
C0 E C0^-1 = diag(H,I_B).
```

The checker verifies the ordered block updates and both inverse
orders on all 112 columns. It does not emit an elementary scalar
word or claim its scan cost.

## Exact code transport

Use the entry code

```text
C_in = C0 L.
```

This differs from the square code built directly from J,D only by
the free translation L_B on the complement coordinates.

For an all-data advance A_plus=F Q^-1, assume F is common to all
fields and commutes with C0 and Q. The transported code is

```text
C_out = A_plus C_in A_plus^-1 = Q^-1 C0 Q^-1.
```

Let M=Q E Q^-1. Then

```text
C_out M C_out^-1 = diag(Q_A^-1 H Q_A,I_B).
```

The selected carrier phases remain. The statement is not
C_out M C_out^-1=diag(H,I_B) unless H commutes with Q_A.

For the chosen A, its first sixteen slots are eight complete physical
pairs from the pinned cyclic source. Every pair has q_p+q_r=45.
Assign one two-coordinate H block to each pair. On such a pair the
transported block is

```text
[ -3                  C_qp^-1 C_qr ]
[  2 C_qr^-1 C_qp                 -1 ].
```

It can use two ordered off-diagonal ADDs and two sign changes.
The common isotropic gauge from
`coherent-port/isotropic-pair-gauge-20261018/GAUGE.md` makes each of
these ADD views monomial. That theorem does not make the gauge
entrance or exit free. Without an inherited gauge, two rank-one
line passes on the sixteen fields give a conservative 32-rank
implementation. The fourteen scalar blocks commute with their
carrier phases and need no native phase conversion.

For the rank-sixteen alternative response, H is diagonal. The same
transport equation then leaves a scalar centre action. Its actual
minor and native capture are separate work in the new-core lane.

With fixed C0 and Q, repeated positive advances transport the code
through

```text
C0 L -> Q^-1 C0 Q^-1 -> L C0 -> Q C0 Q -> C0 L.
```

Every even boundary has only scalar and translation factors. A
negative advance FQ returns the first odd code to C0 L. These
identities need the stated common-F condition. They do not by
themselves bind a stage-dependent routed code.

## Actual native caller and remaining work

The literal source at
`new-core-transfer-20261017/low-displacement-20261020/native-normal-v2/NATIVE-PROGRAM.json.gz`
has decompressed SHA256
`e387b082422f085efc8122497cdda0b5211a86b0418af4b9fdbc1da15ac71558`.
It has two 112-field data banks. Its other 416 fields are arbitrary
and unchanged. It forms no thirty-field centre cohort.

Its physical input is (a,b)=(Qx,y). Therefore its complete physical
maps, before any new code, have the form

```text
forward  = diag(Fq,Fq) [ I       0 ]
                      [ E q     I ],

backward = diag(Fq,Fq) [ I   -Q E^T ]
                      [ 0       I ],
```

where q=Q^-1. Thus both data banks have the same diagonal advance,
but the cross-bank maps also contain an odd Q factor. A common
square code on both banks does not remove that factor merely
because it diagonalizes E.

At a raw output, the inverse code is

```text
C_out^-1 = Q C0^-1 Q.
```

For two stages with different constant or routed codes, the proposed
transition is

```text
C_in,t C_out,s^-1 = C0,t Q^-1 C0,s^-1 Q.
```

These are phase-coded data maps. No free implementation is supplied
here. A complete caller must admit the cross-bank maps, the code
transitions, the final raw output, all native child interfaces, and
the scalar and finite-precision costs. The entry code alone does
not improve the complete kappa bound.

## Why the earlier reader choice does not close the same section

The other valid section uses T=V L U and D=T^-1 V at entry. After
positive progress its reader is T^-1 VQ. The required terminal reader
is VQ^-1. The latter does not factor through the former.

At the actual character chi=92, the matrix formed by stacking V and
V diag((-1)^(chi dot q_p)) has rank sixty. The payload gives a
sixty-column minor with a nonzero determinant modulo 1000003.
Since V has rank thirty, the restriction of VQ^-1 to ker(VQ) has
rank thirty. This is an exact counterexample to a centre-only
action for that reader choice. It does not apply to the shifted
reader D0 L used above.

The character can be extended by zero columns. The counterexample
therefore persists at every positive tensor width. It is not a
native-child lower bound.

## Checks and scope

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/coherent-port/section-entry-20261020/check_section.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/coherent-port/section-entry-20261020/check_section.py
```

Expected output is `PASS_EXACT_RANK30_ENTRY_SECTION`. The two JSON
outputs must be byte-identical. The source packets are hash checked
and are not changed. The checker tests the exact matrices and the
constant block program. The phase transport equations are general
proofs; a new routed native circuit is not emitted.

The root supplied the section and code-transport task. The new-core
lane supplied U,V and the native source. The native-escape lane
supplied the one-reader section word and the constant-matrix
compiler. This lane selected the actual minor, checked the square
code, selected the shifted reader, and stated the remaining physical
interfaces. AI assistance was used.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
