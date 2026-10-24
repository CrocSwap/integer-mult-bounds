# A dyadic capture with 56 active phase fields

The actual rank-sixteen response admits a dyadic involution C with
rank(C-I)=16. The coded response K=C E C is supported within the
actual q+R phase classes, where R=span(30,45,75,384).

In a class-preserving pair basis, C acts on only 56 fields and is
identity on the other 56. The capture and its inverse use no odd
division, owned field, or native child inside a common scalar frame.
Their literal cost is 4044 old real scalar units in each direction.

In the rank-four carried frame W_R, the phase-class reduction gives
an exact factorization of Q C Q^-1 with 112 rank-one phase calls.
This is a conditional factorization count. This packet does not
emit the physical phase recipes or admit the carried frame in a
complete supplier. The current W45 exit is a different frame.

## Actual response and phase classes

The source response is E=H^-1 E_mode H. H is the frozen physical
pair code. E_mode is the direct sum of eight signed six-mode blocks
and eight signed eight-mode blocks I-dd^T.

The actual labels form fourteen q+R classes, each of size eight.
H preserves these classes. Every six-mode block meets three classes
in two ports each. Every eight-mode block meets four classes in two
ports each. The checker verifies these statements from the pinned
source labels and signs.

Choose the first class of each group in numeric coset order. The
pair order follows the source group's port order. Write its two
ports as p and t. All formulas below use the actual signs d_i.

## Six-mode block

Define vectors a and b by

```text
a_p=2d_p,   a_t=0,
b_p=3d_p,   b_t=-d_t,
```

with all other entries zero. Set

```text
u=a-d,
v=(d-b)/4,
S=I+u v^T.
```

Then

```text
v^T d=1,      v^T u=-2,
S d=a,        b^T S=d^T,
b^T a=6.
```

The second identity gives S^2=I. All entries are dyadic and
det(S)=-1. Thus S is a unit over Z[1/2]. It follows that

```text
S(I-dd^T)S = I-ab^T.
```

The changed part is wholly inside the chosen phase-class pair.
On that pair it is

```text
[-5, 2 d_p d_t]
[ 0,         1].
```

The centre information remains available as the within-class
functional b^T(Sx)=d^T x. It is not asserted to be one original
physical field.

## Eight-mode block

Let e equal d on the chosen pair and zero elsewhere. Put

```text
u=2e-d,
v=-u/4,
S=I+u v^T.
```

Now u^T u=8, so v^T u=-2 and S^2=I. Also S d=2e. Hence

```text
S(I-dd^T)S = I-4ee^T.
```

This changed part is also confined to the chosen phase-class pair.
It has eigenvalues -7 and 1 on that pair. Again S is a dyadic unit
with determinant -1.

## Active pair coordinates

For each same-class pair use the signed rotation coordinates

```text
s = d_p x_p+d_t x_t,
t = -d_p x_p+d_t x_t.
```

This convention makes t the negative signed difference. The pair
matrix is a dyadic unit. Let P be the direct sum of all 56 pair
matrices.

For a six-mode group, P S P^-1 reads and changes only the chosen
pair's difference and the other two pairs' sums. In that order,

```text
u_reduced = (-2,-2,-2),
v_reduced = (1/2,1/4,1/4),
S_reduced = I+u_reduced v_reduced^T.
```

The chosen pair's sum is passive. Each other difference is passive.
For an eight-mode group, only the four sums are active, with

```text
u_reduced = (1,-1,-1,-1),
v_reduced = (-1/2,1/2,1/2,1/2).
```

All four differences are passive. The total number of active fields
is 8*3+8*4=56. Each global phase class contains four active fields.
The exact active role list is in the payload.

Put T=P H. Both P and H preserve the global phase classes. The
complete physical code is

```text
C = H^-1 S H
  = T^-1 S_reduced T,
C^-1=C.
```

The physical response K=C E C remains supported within the global
phase classes because H preserves them. The complete capture has
rank(C-I)=16 and determinant 1.

## Literal scalar word

The reduced blocks have an in-place word with no extra field.
For any of the reduced vectors u and v, choose its first active
field p. Let R perform

```text
x_i -= (u_i/u_p)x_p      for all other active i.
```

Then R u=u_p e_p, and

```text
R S_reduced R^-1
  = I+u_p e_p(v^T R^-1).
```

Only its p-th row changes. Its p-th diagonal entry is -1, and
its other entries in that row are u_p v_i. Apply R, multiply
x_p by -1, add u_p v_i x_i into x_p, and apply R^-1.

The six-mode reduced word has four unit ADDs, two half ADDs,
and one sign SCALE. It costs 4*8+2*10+2=54 old real units.
The eight-mode reduced word has six unit ADDs, three half ADDs,
and one sign SCALE. It costs 6*8+3*10+2=80.

The complete word executes H, P, the reduced code, P^-1, and
H^-1. Its exact invoice is

| Part | Old real scalar units |
| --- | ---: |
| H | 470 |
| P | 1016 |
| Reduced code | 1072 |
| Complete capture | 4044 |
| Literal inverse capture | 4044 |

All event coefficients are dyadic. Every SCALE is a signed power
of two. There are no fixed odd multiplication or division events.
Both complete words have maximum prefix row one-norm 10 and
maximum binary denominator height three.

The checker verifies all 640 output rows. It leaves the other
528 fields arbitrary and unchanged. It also verifies C^2=I,
the exact conjugation of the actual response, and rank(C-I)=16.
No zero-input, helper, or restoration premise is used.

The class-supported additive maps

```text
(X,Y) -> (X,Y+KX),
(X,Y) -> (X-KY,Y)
```

each have a complete 1544-unit scalar ADD word. These are different
from applying K in place on one bank. The source E is symmetric,
so encoding both banks by the same C gives these two maps. The
second response is -K, not -K^T. A transpose-dual interface is a
separate choice.

K itself has determinant 35^8. Its inverse requires the old
response's factors five and seven. This packet does not claim a
dyadic in-place implementation of K^-1.

## Phase factorization and limits

Work in the rank-four frame W_R and write Q' for W_R Q W_R^-1.
Choose one global anchor phase D_g in each class. Define

```text
A_i=Q'_i D_g^-1.
```

All A_i are monomial in this frame. The anchor phases have Fourier
rank one. These are consequences of the frozen common-gauge
geometry: q_i+q_anchor lies in R, whereas each anchor is odd and
therefore is not in the even space R.

Let D repeat the anchor on every field in its class. Then Q'=A D.
Since T preserves classes,

```text
Q' C Q'^-1
 = A T^-1 [D_active S_reduced D_active^-1 direct-sum I] T A^-1.
```

There are exactly 56 inverse anchor calls and 56 forward anchor
calls. Both alignment passes have at most 112 monomial maps.
Each native rank-one factor can require its two side maps; the
corresponding upper bound is 224 side maps. The scalar word keeps
its full 4044-unit invoice.

No phase is dropped in this identity. The anchor and alignment
operators retain their ordered definitions at every tensor width.
This packet emits their directions and the pinned W circuit, but
does not emit their monomial or native phase recipes. Those
recipes, legal caller access, and recursive child costs must be
checked before this factorization becomes a native caller word.

The inverse capture has the same active set and the same alignment.
Negative conjugation uses inverse anchors and the corresponding
inverse alignments. These are monomial here because all original
directional phases commute. The statement need not hold for a
general noncommuting phase family without that extra premise.

For a transported inverse code Q' C^-1 Q', retain the right factor
Q'^2. It can be composed into the first alignment only as an
explicit declared monomial map. It is not an omitted free factor.

Since K preserves classes, D K=K D and

```text
Q' K Q'^-1 = A K A^-1.
```

Its additive use is therefore native-free in this frame, with the
scalar and monomial maps still charged.

The current changed supplier uses the rank-one W45 exit. It does
not supply W_R for free. The complete four-pair compression of one
actual orthonormal eight-clique already requires a rank-four common
gauge: its four disjoint pair-difference vectors are independent.
The reviewed common-gauge theorem therefore gives rank at least
four for a gauge that makes all four ratios monomial. This is a
limit of this pair compression, not a general decoder lower bound.

Preparing or removing W_R, changing native endpoints, routed code
matching, source access, helper progress, terminal output, and the
full recursive cost remain separate. No complete supplier or
kappa improvement is claimed.

## Evidence and credit

Run with one CPU from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-dyadic-capture-20261020/emit_capture.py --out NEW_DIRECTORY
python3 -O work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/phase-class-dyadic-capture-20261020/emit_capture.py --out ANOTHER_NEW_DIRECTORY
```

The required status is `PASS_DYADIC_PHASE_CLASS_CAPTURE`.
Both payloads and both receipts must have identical bytes.
Only `verified-normal` and `verified-optimized` are final evidence.
Earlier directories retain the prior difference orientation or a
run made before the explicit source-symmetry check.

The source pins bind the actual rank-sixteen response, cyclic pair
geometry, and common-root gauge. This construction uses the
coordinator's phase-class reduction, the bridge capture work, and
the campaign's pair-code and gauge results. The asymmetric
six-mode involution and selected-difference reduction were derived
in this lane. This is a producer packet; distinct review remains
required. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
