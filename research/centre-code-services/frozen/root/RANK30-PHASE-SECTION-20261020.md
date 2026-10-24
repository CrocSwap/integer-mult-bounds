# A translation inverse for the rank-thirty response

The actual rank-thirty response has a useful property that correction
rank alone does not give. Its phase-dependent cross matrix is invertible
at every positive tensor width. Its inverse uses only simultaneous
translations and coefficients in Z[1/2,1/15]. Thus it gives an exact
section and an exact coordinate split with no new native transform.
The translation maps, scalar scans, storage, and boundary access still
require their full implementation cost.

The required terminal query is not supplied by this theorem. The section
uses the positive phase reader VQ. The current terminal needs VQ^-1.
The last section states this difference as an operator identity. The
later MOVING-CENTRE-CODE-20261020.md proof changes the reader and removes
this mismatch without using the translation inverse proved here.

## Pinned actual inputs

Use the matrices U and V in the rank-thirty response packet:

```text
../lanes/new-core-transfer-20261017/low-displacement-20261020/
run-normal/RESPONSE-PROGRAM.json
SHA256 5832788135e16c2427f8c746f251501621684a02ef88b0a14322056653dc2d7c
```

Here U has 112 rows and 30 columns, V has 30 rows and 112 columns,
and E-I=UV. The physical port order is the order in that packet.
Use the 112 directions q_p in the transfer list of:

```text
../lanes/history-encoding/independent-skeleton-20261018/
fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz
decompressed SHA256
b08cb4146f1aec241e027cd62c942f6eca4ddab3e97f000a9c0017575d36deb5
```

The rank-thirty matrix review and the complete native review are separate
dependencies. They check E-I=UV, the selected principal interface, both
native directions, every input role, and the native phases. This note
uses their actual U,V and q arrays. It does not infer a native circuit
from an arbitrary low-rank matrix.

## A general translation-section theorem

Let G be the additive group F2^d. On a field array at tensor width f,
let tau_g translate every tensor copy by the same g. Other coordinates
of the full supplier address are unchanged. Then

```text
tau_g tau_h = tau_(g+h),          tau_g^2 = I.
```

These are simultaneous translations. They are not f independent
translation choices. In particular, the group has 2^d elements at
every positive f.

Let U be an n by r scalar matrix and V an r by n scalar matrix. Put

```text
J = diag_p(tau_(q_p)) U,
T = V J,
T_chi = V diag_p((-1)^(chi dot q_p)) U.
```

Assume all 2^d matrices T_chi are invertible. For each character chi,
define the operator

```text
e_chi = 2^-d sum_g (-1)^(chi dot g) tau_g.
```

The character orthogonality identity gives

```text
e_chi e_psi = [chi=psi] e_chi,        sum_chi e_chi = I,
T = sum_chi T_chi e_chi.
```

Consequently

```text
T^-1 = sum_chi T_chi^-1 e_chi
     = sum_g K_g tau_g,
K_g = 2^-d sum_chi (-1)^(chi dot g) T_chi^-1.
```

Multiplication proves both inverse orders. The proof is an identity in
the finite group algebra, so it holds in every representation of this
translation group. In particular, it holds at every positive tensor
width and in the full supplier chart. There is no approximation.

There is also a useful direct Fourier description. At a frequency tuple
(chi_1,...,chi_f), the multiplier of tau_g is
(-1)^((chi_1+...+chi_f) dot g). Thus the matrix at that frequency is
T_(chi_1+...+chi_f). This gives the same all-width result. It does not
replace T by a tensor power of an r by r matrix.

If every T_chi^-1 has coefficients in Z[1/2,1/s], so does T^-1.
The averaging factor 2^-d adds no odd denominator. A valid implementation
can use the finite translation formula or a factored mode word. This
algebraic formula alone does not price an in-place implementation.

## Exact result for the actual thirty coordinates

For the actual U,V, take d=9 and r=30. The native line phases satisfy
Q_p^2=tau_(q_p), with the exact phase convention of the pinned native
word. Thus

```text
T = V Q^2 U.
```

Each T_chi is a direct sum of one 16 by 16 matrix and fourteen scalar
matrices. The first block comes from the eight reciprocal six-mode
responses after the actual signed pair code. The other blocks come
from eleven five-cliques and three three-cliques.

The adjacent checker constructs T_chi directly from the pinned U,V,q.
It inverts every large block by exact rational elimination, checks both
inverse orders, and checks every small block. There are 512 characters.
Its results are:

```text
all 512 large blocks are invertible;
all fourteen small blocks are nonzero at every character;
the least common denominator of the character inverse entries is 60;
the odd part of that common denominator is 15;
the largest character inverse row one-norm is 53/5.
```

It follows that each physical kernel coefficient has denominator
dividing 512*60=30720. In particular, the all-width inverse belongs to
Z[1/2,1/15][G]. The character row norm is not the array row norm.
Independent integer Walsh reconstruction gives 2712 nonzero kernel
coefficients, least common denominator 120, and exact array infinity
norm 88/5. Character inverse entries -1/3 and -1/5 prove that the odd
part 15 is necessary over the dyadic coefficient ring.

The exact inverse blocks are in:

```text
RANK30-PHASE-SECTION-BLOCKS-20261020.json.gz
decompressed SHA256
91b546da328fbf4a58b9fbf92c5851ec7a66402d3c2bcf7a52ce3e1533052bc8
```

The receipt is:

```text
RANK30-PHASE-SECTION-CHECKS-20261020.json
SHA256 04121bb27884df692fd13e042f9f7b8ab005982535a07f7c95e3b1de5dfcaee7
```

The independent inverse and kernel review is:

```text
../lanes/bridge-review-20261017/rank30-phase-section-review-20261020/
FREEZE.json
SHA256 ce66823499be95adcd980333c8e49c394fa9c0a08927d099c3bfc5fd57edf7d6
```

Normal and optimized Python runs give the same root bytes. The checks are
finite and exhaustive over the character group. The group-algebra proof
above is the step that extends them to every tensor width.

## Why odd cliques give a reusable family

Let one zero-diagonal rank-one response block be E=I+uv, on k ports.
The diagonal equations give u_p v_p=-1. Its scalar cross matrix is

```text
T_chi = -sum_p (-1)^(chi dot q_p).
```

If k is odd, this sum is odd and nonzero for every character, regardless
of relations among the directions. Therefore this phase section always
exists. Its inverse has odd denominator dividing the least common
multiple of 1,3,...,k. For k=3 and k=5 those bounds are 3 and 15.
Disjoint odd blocks retain this property, with the least common multiple
of their denominator bounds.

For comparison, suppose k is even and the directions are independent.
There is a character with k/2 positive signs and k/2 negative signs.
Its scalar cross matrix is zero. Hence this phase section does not exist.
The actual rank-sixteen candidate uses eight independent directions in
each of its eight small cliques, so it has this obstruction.

An invertible change of the r correction coordinates replaces a minimal
factorization U,V by U S,S^-1 V. It conjugates T. Such a coordinate
change cannot remove a singular character. This conclusion concerns this
phase section. It does not rule out a different centre code or decoder.

## Exact entry coordinates and arbitrary borrowed values

Set

```text
J = Q^2 U,       D = T^-1 V,       P = J D.
```

Then DJ=I and P^2=P. For arbitrary data a and arbitrary centre values z,
define

```text
S(a,z) = ((I-P)a+Jz, Da).
```

Direct substitution proves S^2=I. In particular, this operation does
not erase the arbitrary value of z. It places that value in the J
component of the data.

The following word has exactly that endpoint:

```text
a += J z
z -= D a
a += J z
z *= -1
```

The second line reads the updated a. It gives
z-D(a+Jz)=-Da. The third line then gives (I-P)a+Jz.
This proof includes every arbitrary input column.

The word has two J shears and one D shear. A standalone inverse of T
is not an additive D oracle. One safe in-place lowering of the middle
line is:

```text
z <- T z
z -= V a
z <- T^-1 z
```

This lowering must pay both T directions and their workspace. J needs
the actual simultaneous translations and scalar scatter. V is a scalar
gather only at its declared common frame. The section theorem supplies
none of these operations at an undeclared physical cut.

A square coordinate split can avoid thirty additional field families.
Choose r physical rows A for which U_A is invertible, and let B be the
remaining rows. Then J_A=diag_A(Q_p^2) U_A is invertible by scalar
arithmetic and translations. Define

```text
c = D a,
b = a_B-J_B J_A^-1 a_A.
```

The inverse is

```text
t = c-D_B b,
a_A = J_A t,
a_B = J_B t+b.
```

Indeed, a=Jt+(0,b), so Da=t+D_Bb. These are exact algebraic
identities on the existing data bank. Selecting and pricing an actual
minor, its translations, all prefix arithmetic, and its routed caller
are implementation obligations.

## The remaining terminal obstacle

In the logical positive-phase chart, QU is a section for VQ:

```text
(VQ)(QU)=T.
```

The current local terminal correction instead has the form

```text
Q(E-I)Q^-1 = (QU)(VQ^-1).
```

The desired reader is VQ^-1. It is not VQ. Moving the entry split
through a data advance FQ^-1 and a common centre advance F gives
section QU and normalized reader T^-1 VQ, when F commutes with the
translation algebra. This moves the section to the desired image.
It does not change its reader to VQ^-1.

For example, on the complementary subspace ker(VQ), the desired update
still requires VQ^-1 b. The section certificate does not show that this
quantity vanishes or that it can be formed cheaply. A useful supplier
must implement that reader, use a different transported input code, or
prove an actual productive word between the two declared codes.

Thus the theorem resolves exact invertibility, odd-denominator control,
and lossless coordinate splitting for this actual response. The next
construction must use those capabilities at a legal cut and complete
the terminal and recursive invoice.

## Credit and reproduction

The rank-two reciprocal response is in the root
RECIPROCAL-RANK-TWO-20261020.md proof and its addendum. The cyclic native
family, pair code, selected interface, and fourteen-clique cover are
credited in the response packet. The earlier eight-coordinate translation
inverse in the native-escape lane supplied the simultaneous-translation
method and the in-place mode implementation pattern. The coherent-port
lane supplied the lossless entry split; the native-escape lane shortened
the swap word and identified the cost of its additive D operation.
Independent review is recorded in a separate packet.

Run:

```text
python3 work/centre-encoding-campaign-20261014/root/check_rank30_phase_section_20261020.py
python3 -O work/centre-encoding-campaign-20261014/root/check_rank30_phase_section_20261020.py
```

The expected status is PASS_RANK30_PHASE_SECTION. The checker performs
no native cost, routed access, or complete supplier test.

OpenAI Codex assisted this work. No PR or publication is authorized.
Before any future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
