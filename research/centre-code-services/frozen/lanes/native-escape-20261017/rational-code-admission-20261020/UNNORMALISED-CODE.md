# A dyadic capture for the actual rank-thirty response

The actual rank-thirty factorization admits a capture that has no odd
division. It stores the unnormalised centre value Va in thirty existing
data fields. The other eighty-two fields retain a complement. The
centre response and its inverse preserve the image of this capture.
Thus a valid capture, centre action, and decode chain needs no odd root
scale. Its binary precision and each physical view still have a cost.

This packet also gives the full test for a dyadic middle operation to
preserve this code. There are eleven congruences modulo three and
eleven modulo five. The test applies to a whole-state matrix, including
arbitrary borrowed roles. It does not establish that the actual native
interstage operations pass the test.

## Sources and exact code

Use the actual U and V in the rank-thirty response:

```text
new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json
SHA256 5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c
```

The response is E=I+UV, with U of size 112 by 30. The chosen row
minor and the normalised code come from:

```text
coherent-port/section-entry-20261020/SECTION.json
SHA256 23568099ea426947015eca86f7d86742a4758f33327e725b047441daab7c8bd7
```

Let A be its thirty selected physical slots, in the source order:

```text
0,27,9,61,11,63,20,46,37,110,41,106,76,87,78,99,
5,3,24,23,1,8,29,26,4,18,19,39,6,31.
```

Let O be the other eighty-two slots. The matrix U_A has determinant
-1/256 and an integral inverse. Put B0=VU and G0=I+B0. The full B0 is
the direct sum of eight blocks

```text
B = [-4  1]
    [ 2 -2]
```

and fourteen scalars: eleven -5 and three -3. The scalar -3 entries
have centre indices 25, 26, and 27. All indices start at zero.

Write R0=Z[i,1/2]. Define the code Csum on arbitrary data a by

```text
c = V a,
r = a_O - U_O U_A^-1 a_A.
```

Store c_j in physical slot A[j] and r in O. All coefficients of Csum
are in R0. Its inverse on arbitrary rational code coordinates is

```text
w   = c - V_O r,
u   = B0^-1 w,
a_A = U_A u,
a_O = r + U_O u.
```

To verify the two inverse orders, set u0=U_A^-1 a_A. Then
a=Uu0+(0,r), so c=B0u0+V_O r. Conversely, the displayed inverse
gives that same c and r. This also proves that every input coordinate
is retained.

If C0 is the source's normalised code, then

```text
Csum = diag(B0,I_O) C0.
```

The following block program forms Csum in place:

```text
a_A = U_A^-1 a_A
a_O -= U_O a_A
a_A = B0 a_A
a_A += V_O a_O.
```

The first two lines are the same as in C0. In the source's
B0/gather/B0^-1 lowering of the final additive map, Csum omits the
last B0^-1. Therefore that lowering saves 204 old real scalar units
and 22 real divisions by three plus 22 by five at capture. This is a
relative local price. This packet does not supply the complete
elementary capture word or its address-map invoice.

## Centre action and exact decode

The matrices B0 and G0 commute. It follows from the source code
identity that

```text
Csum E Csum^-1 = H = diag(G0,I_O).
```

Both G0 and G0^-1 are dyadic. The eight large G0 blocks are
[[-3,1],[2,-1]], each of determinant one. The other blocks are
eleven -4 and three -2. In particular,

```text
E^-1 = I - U G0^-1 V
```

is dyadic as well. Thus H and H^-1 both preserve
Lambda=Csum R0^112.

For a valid encoded input Csum a, the decoder's w is
B0 U_A^-1 a_A. The constant B0^-1 word in CENTRE-CONSTANTS.md
therefore receives a valid B0-code. Every odd division in that word
is exact on each input column. An encode, H or H^-1, decode chain
does not need a common odd factor in the original data. A binary
guard must still cover all intermediate dyadic coefficients.

This statement requires the full valid-code premise. It does not
allow an exact division on an unrelated centre value, a rounded
division on an arbitrary borrowed field, or an unproved partial
native endpoint.

## The complete image test

For a dyadic candidate code coordinate z=(c,r), set w=c-V_O r.
The inverse above gives

```text
z is in Lambda  if and only if  w is in B0 R0^30.
```

For one large block,

```text
B^-1 = [-1/3  -1/6]
       [-1/3  -2/3].
```

Hence B^-1 w is dyadic if and only if w0-w1 is zero modulo three.
Each scalar -3 gives one further congruence modulo three. Each
scalar -5 gives one congruence modulo five. There are no further
odd denominators and no higher prime powers.

Let P map z to c-V_O r. Let N3 have the eight rows
e_(2j)-e_(2j+1), for 0<=j<8, and the three rows e25,e26,e27.
Let N5 have the eleven coordinate rows for the -5 blocks. Define

```text
L3 = N3 P,               L5 = N5 P.
```

The exact image criterion is

```text
Lambda = {z in R0^112 : L3 z = 0 mod3 and L5 z = 0 mod5}.
```

Each Lp has an integral right inverse supported on selected centre
slots. For a difference row, use its even centre coordinate. For a
coordinate row, use that coordinate. The eleven rows are therefore
independent over both residue rings. The result does not treat
R0/5R0 as a field; that ring is a product of two fields.

The Chinese remainder theorem gives the full quotient:

```text
R0^112 / Lambda = (R0/3R0)^11 direct-sum (R0/5R0)^11.
```

The equality denotes an isomorphism induced by (L3,L5). In
particular, these congruences are sufficient as well as necessary.

## The full dyadic middle algebra

Let M be a matrix over R0 on these 112 fields. Then

```text
M Lambda is contained in Lambda
```

if and only if, for p=3 and p=5,

```text
ker(Lp modp) is contained in ker(Lp M modp).
```

Equivalently, there must be a matrix Sp over R0/pR0 such that

```text
Lp M = Sp Lp modp.
```

For sufficiency, apply these identities to the two zero syndromes.
For necessity, take a vector in ker Lp. The Chinese remainder
theorem lifts it to a dyadic vector with the required residue at p
and zero residue at the other odd prime. This lift is in Lambda.
The preservation premise then gives Lp M=0 on ker Lp. Since Lp has
a right inverse, a map that vanishes on its kernel factors through
Lp. This proof is valid over the split residue ring at five.

This criterion describes the full algebra of dyadic operations that
preserve this code. It is not restricted to operations that commute
with B0 or E. For the actual H and H^-1 the stronger identities hold:

```text
Lp H = Lp,               Lp H^-1 = Lp modp.
```

The checker verifies both identities. A dyadic unit need not satisfy
them. As a negative control, doubling the selected physical field
A[0] gives a nonzero mod3 syndrome on an actual capture column.

Extend Csum by identity on every other role. Extend L3 and L5 by
zero columns on those roles. The same theorem then applies to the
whole state, with arbitrary borrowed inputs. A middle map can mix
these roles only when its complete matrix passes the criterion.
There is no assumption that borrowed data are zero.

## Routed codes and limits

If Pleft and Pright are dyadic units, the image of
Pleft Csum Pright is Pleft Lambda. The right unit does not change
the image. A full image test is Lp Pleft^-1. This gives a formal
transport rule for the congruence interface. It does not make
Pleft, its inverse, or a physical frame transition free.

For the source's Q with Q^4=I, Csum Q^2 is a dyadic entry code.
At a common advance FQ^-1 under the source's stated commutation
hypotheses, the transported code is Q^-1 Csum Q^-1. The encoded
response remains diag(Q_A^-1 G0 Q_A,I_O). The eight large blocks
still need their actual pair-phase intertwiners. The code-image
test does not supply them.

No native F/B controller, helper endpoint, cross-bank transition,
or terminal raw decode is admitted by this packet. These must
establish the exact whole-state map and either preserve the code
or pay for a new representation. There is no complete kappa claim.

## Verification and credit

Run with fresh output directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_unnormalised_code.py --out /tmp/unnormalised-normal
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/rational-code-admission-20261020/check_unnormalised_code.py --out /tmp/unnormalised-optimized
```

Expected status: PASS_ACTUAL_UNNORMALISED_RANK30_CODE. The two output
files must be byte-identical. The checks cover all 112 input columns,
both inverse orders, the complete B0 block form, both centre
actions, both quotient actions, and the negative control.

The new-core lane supplied the actual rank-thirty factors. The
coherent-port lane supplied the actual minor, the normalised square
code, and its phase transport. The constant-code packet supplied
the exact B0 word and its valid-code division proof. This addendum
supplies the unnormalised capture and its complete dyadic
code-preservation test. OpenAI Codex assisted the proof and checks.
No publication is authorised. Before any future PR description,
read /Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
