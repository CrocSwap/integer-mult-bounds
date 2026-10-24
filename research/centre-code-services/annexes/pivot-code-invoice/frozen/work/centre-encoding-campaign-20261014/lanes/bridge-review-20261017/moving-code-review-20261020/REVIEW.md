# Independent review of the moving centre code

The new reader removes the phase-dependent inverse from the entry
section. It applies to both actual response families. In particular,
the actual rank16 response has a valid entry code although all eight
of its old small phase blocks are singular at character 2.

The complete entry swaps below are exact array programs with paid
scalar operations and translations. The square codes on the existing
112 fields are also checked. The rank16 square code makes the encoded
response diagonal on sixteen actual carriers. None of these statements
implements the final output decode or the complete productive caller.

## Independent source checks

`CHECKS.json` pins every input. The checker imports no producer code.
It uses exact rational arithmetic and verifies:

- E=I+UV and both orders of the actual E inverse for both families;
- B=VU, an independent rational inverse of B, and D0 U=I;
- the full inverse identity E^-1=I-U(I+B)^-1 V;
- complete literal B and B^-1 words on arbitrary inputs;
- every input field of both complete entry swaps, with translation
  labels retained on every coefficient;
- restoration of every field after two complete entry swaps;
- the actual rank30 minor and normalized square code;
- both literal rank16 pivot-code directions, both inverse orders,
  and the full 112-column diagonal response.

The rank30 inverse minor is computed independently. Its determinant is
-1/256 and its inverse is integral. The rank16 code is the actual
unnormalized pivot code from the native source packet. It is a
different scalar conjugator from the normalized section code.

The current checker does not repeat the native phase and wrapper
verification. It uses the already reviewed phase identity Q_p^2=X_qp
and its consequence Q_p^4=I. The 112 directions are compared directly
with the pinned stage-zero DATA views.

## General section theorem

Let E=I+UV and suppose B=VU is invertible. Put D0=B^-1 V. Then D0 U=I.
Let Q be the diagonal matrix of exact line phases and put L=Q^2.
Assume L^2=I. Set

```text
J_in = L U,                 D_in = D0 L.
```

Their product is D_in J_in=I. This requires no inverse of VLU.
On arbitrary arrays a and z, the word

```text
a += J_in z
z -= D_in a
a += J_in z
z = -z
```

has endpoint

```text
((I-J_in D_in)a+J_in z, D_in a).
```

The second line reads the updated a. Direct substitution proves that
the endpoint is an involution. A single use stores the old arbitrary z
inside the data section. It does not restore or clear z.

Write S0 for the same swap with section U and reader D0. Then

```text
S_in = diag(L,I) S0 diag(L,I).
```

The two translation passes can therefore be placed outside the whole
constant scalar word. They need 224 field-map calls for n=112.
There is no need for separate translation passes around each shear.

Suppose the data advance is A=FQ^-1 and the centre advance is F.
The common F must commute with the scalar maps and the port phases.
Then

```text
J_out = A J_in F^-1 = Q U,
D_out = F D_in A^-1 = B^-1 V Q^-1.
```

Thus the desired response has exactly the form

```text
Q E Q^-1 = I+J_out B D_out.
```

It fixes ker(D_out) and acts by H=I+B on the section coordinates.
The transported swap satisfies

```text
diag(A,F) S_in = S_out diag(A,F),
S_out diag(Q E Q^-1,I) S_out = diag(I,H).
```

These identities include every arbitrary data and centre value.
The proof does not supply a productive centre bank or its advance.

If E is invertible, H is invertible as well. The formula

```text
H^-1 = I - V E^-1 U
```

proves both inverse orders over a coefficient ring. It does not require
an inference from injectivity over a field.

## Actual constant matrices

For rank30, B has eight blocks

```text
[-4  1]
[ 2 -2]
```

and eleven scalars -5 and three scalars -3. Its inverse has common
denominator 30. H has eight blocks [[-3,1],[2,-1]], eleven scalars -4,
and three scalars -2. H and H^-1 are dyadic, and det(H)=2^25.

For rank16,

```text
B = diag(-6 I8,-8 I8),       H = diag(-5 I8,-7 I8).
```

B^-1 has common denominator 24. The reader therefore needs the odd
prime 3. H^-1 has common denominator 35. Its use introduces separate
requirements at 5 and 7.

For each of the eight actual rank16 small cliques, character 2 gives
four positive and four negative translation signs. Its old phase
block is zero. The new constant reader is therefore a strict escape
from that particular inverse condition. This is not a lower bound
against other readers or native constructions.

## Explicit complete entry words

The middle constant shear is implemented as

```text
z <- B z
z -= V a
z <- B^-1 z.
```

Its endpoint is z-D0a on arbitrary a and z. In-place inverse access is
not treated as an additive oracle.

The rank30 large-block word uses the short factor from the
native-escape lane:

```text
y -= x
x *= 3
x -= y
y *= 2
x = -x
y = -y.
```

The output is (-4x_old+y_old,2x_old-2y_old). Reverse every operation
and invert it to obtain B^-1. The small blocks use one signed
fixed-odd scale each. Rank16 uses only independent field scales.

The checker emits the complete entry programs. Its sparse interpreter
retains each pair (original input field, uniform translation). Since
distinct translations give distinct array addresses at positive
width, this checks every input column of the physical array map.
The group identity then gives every tensor width.

| Complete entry swap | Dyadic real primitives | Translation maps | Complex odd multiplications | Complex odd divisions |
| --- | ---: | ---: | --- | --- |
| Rank30 | 5,076 | 224 | 11 by 3; 11 by 5 | 11 by 3; 11 by 5 |
| Rank16 | 4,448 | 224 | 8 by 3 | 8 by 3 |

The dyadic price includes both U shears, both B directions, the V
gather, and the final signs. It uses the inherited ADD tariff. Signs
and one-bit scales each cost two real primitives. The odd scans are
separate and each complex scan acts on two real records.

There is no new native child or additional owned array. The section
swap does require its declared independent z bank: thirty fields in
one case and sixteen in the other. This count must not be confused
with the square code, which uses only the 112 data fields.

For both complete words the largest stored row sum at an opcode
boundary is 12. Rank30 prefixes have at most one new factor 3 and
one new factor 5 in a coefficient denominator. Rank16 prefixes have
at most one new factor 3. These are exact local prefix statements.
They are not a complete bound for bit-level ADD temporaries or for
arbitrarily many recursive uses.

The common root grid must admit each division on all arbitrary input
streams. Map compilation, coefficient width, carry storage, root
conversion, descriptor work, and recursive grid height remain
separate costs. No finite scan or map cost is included in the dyadic
primitive column.

## The square code and the actual rank16 pivot code

For a unit row minor U_P, let R be the complementary rows. The
normalized square code is

```text
c = D0 a,
b = a_R-U_R U_P^-1 a_P.
```

Its inverse is t=c-(D0)_R b, followed by
a_P=U_P t and a_R=U_R t+b. It conjugates E to diag(H,I_R).
The actual rank30 code has this form, with the supplied thirty
carriers. Both inverse orders and the exact conjugation are checked.

A more general statement is needed for the actual rank16 pivot
word. Let any scalar unit C satisfy

```text
C E C^-1 = K.
```

Then entry C L transports through A to q C q, where q=Q^-1, and

```text
(q C q)(Q E q)(Q C^-1 Q) = q K Q.
```

Only adjacent equal-port phase factors cancel. No phase is moved
through C. If K is diagonal, q K Q=K.

The rank16 literal pivot code satisfies this identity with K equal
to -5 on eight actual pivot fields, -7 on eight more, and 1 on the
other 96 fields. Its input and inverse words were independently
replayed on all 112 columns. Thus the response in this output code
uses sixteen scalar multiplications. The code is not required to
equal the normalized D0 code.

## Reuse and the caller boundary

With fixed Q and common advances F_s Q^-1, the code cycle is

```text
C L -> q C q -> L C -> Q C Q -> C L.
```

Every F_s must commute with C and Q. Two advances reach a code
with only scalar and translation factors; four return the entry
code. A following advance F_- Q returns q C q directly to C L.
The F operators need not be equal if each commutation condition
holds. Interleaved operations need their own typed endpoint checks.

For a diagonal routed operator diag(F_p), the precise scalar-code
test is

```text
[diag(F_p),C]_(p,r) = C_(p,r) (F_p-F_r).
```

Thus a nonzero code edge needs equal actual advances or a proved
intertwiner. Nominal labels do not establish this operator identity.

The actual native caller takes physical inputs (a,b)=(Qx,y) and
returns (F x',Fq y'). Its forward and backward logical responses
are y'=y+Ex and x'=x-E^T y. Therefore the physical maps are

```text
diag(Fq,Fq) [[I,0],[E q,I]],
diag(Fq,Fq) [[I,-Q E^T],[0,I]].
```

The extra odd phase in each cross-bank map remains. Diagonalizing E
does not by itself admit these complete calls. A final raw decode
also needs Q C^-1 Q, not the cheap scalar inverse alone.

The root moving-code theorem is valid with these boundaries. Its
rank16 primitive gives an encoded endpoint, not a raw endpoint.
The complete supplier must still bind the actual routed chronology,
all cross-bank operations, code transitions, borrowed restoration,
productive child hosting, and the final decode.

## Reproduction, credit, and status

Run `python3 -I -B check_moving_code.py` and
`python3 -O -I -B check_moving_code.py`. Both must print
`PASS_INDEPENDENT_MOVING_CODE` and produce identical files.

The coherent-port lane supplied the corrected reader and the
rank30 square code. The new-core-transfer lane supplied both actual
responses and the rank16 pivot code. The native-escape lane supplied
the short B block word and fixed-odd contracts. The root supplied
the reuse-cycle statement. This review independently checks their
matrix claims and emits complete paid entry swaps. It uses AI
assistance. No PR, publication, or kappa improvement is claimed.
