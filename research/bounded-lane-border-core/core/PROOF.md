# A fixed-width lane boundary and a closed inverse-pair core

Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
SPDX-License-Identifier: Apache-2.0

Status: exact operator lemma and priced local native specialization. This is
not a completed native recursive supplier or a new multiplication bound.

## 1. The finite lane algebra

Let V be any vector space over a field. Fix L >= 1 and order the L copies of
V by lane indices 0,...,L-1. Let A_L be the algebra of block lower-triangular
operators whose L diagonal blocks are equal. The common diagonal a_0 need
not commute with the strictly lower blocks. Write

    S(v_0,...,v_{L-1}) = (0,v_0,...,v_{L-2}),
    R(v_0,...,v_{L-1}) = (v_1,...,v_{L-1},0),
    P_0(v_0,...,v_{L-1}) = (v_0,0,...,0).

These matrices describe a circuit using role permutations and explicitly
owned terminal fields; S and R are not being introduced as free destructive
primitives. Their literal implementation is given below.

For A in A_L with common diagonal a_0 define

    T(A) = S A R + a_0 P_0.

Here a_0 P_0 applies a_0 only on lane 0. Equivalently, T(A) is block diagonal
between lane 0 and lanes 1,...,L-1: it has a_0 on the first block and the
leading (L-1)-lane principal compression of A on the other block.

**Lemma 1.** T is a unital algebra homomorphism, and

    T(A) S = S A.

**Proof.** Leading principal compression is multiplicative for lower
triangular matrices. The common diagonal of AC is a_0 c_0, in that order,
so both blocks of T(AC) equal the corresponding blocks of T(A)T(C).
The identity is preserved. Finally S annihilates the last lane, and lower
triangularity implies S A P_last=0. Thus
T(A)S = S A R S = S A(I-P_last)=S A. No Toeplitz assumption is used.

Invertible A in A_L has inverse B=A^-1 in A_L, with common diagonal
b_0=a_0^-1. In particular T(A)T(B)=T(B)T(A)=I.

## 2. The compensated boundary core

For an actual inverse pair AB=BA=I, the two-shear identity is

    M(A,B) = U(A) L(-B) [[I,-I],[I,0]]
           = [[A,0],[I-B,B]],

where U(A)=[[I,A],[0,I]] and L(-B)=[[I,0],[-B,I]]. Its actual inverse is

    M(A,B)^-1 = [[B,0],[B-I,A]].

Define the boundary-repaired maps

    E(A,B) = [[A,0],[S(I-B),T(B)]],
    F(A,B) = [[B,0],[S(B-I),T(A)]].

They arise by sandwiching M and its actual inverse between diag(I,S) and
diag(I,R), then adding respectively b_0 P_0 and a_0 P_0 to the bottom-right
block. The boundary call is the **exact common diagonal** b_0 or a_0; it does
not require the whole boundary column B P_0 or A P_0.

**Theorem 2.** E and F are actual two-sided inverses. After putting all
roles in lane order, both belong to A_L, now with payload V direct-sum V.
Their common diagonal blocks are diag(a_0,b_0) and diag(b_0,a_0).

**Proof.** The diagonal blocks of EF are AB=I and T(B)T(A)=I. Its lower
left block is

    S(I-B)B + T(B)S(B-I)
      = S(B-B^2) + S B(B-I) = 0.

The lower left block of FE is

    S(B-I)A + T(A)S(I-B)
      = S(I-A) + S A(I-B) = 0.

All strictly lower lane terms remain strictly lower. The factor S in each
cross-role block raises the lane by one. Thus the common diagonal contains
only the claimed two independent diagonal operators.

The theorem is valid for noncommuting physical payload blocks. It does not
assert that passing an arbitrary full native word and its inverse supplies
the required shear pair U(A),L(-B). That is a separate caller obligation.

## 3. Filtration and repeated core composition

Give a block in lane row i and column j grade i-j. For a lower-triangular
A write A=sum A_l, 0<=l<=L-1. Every A_l and B_l appears linearly in the
endpoint expression. For positive l,

    T(B)_l = S B_l R,

which has the same grade l despite the temporary reverse shift. The
cross-role block S(I-B) at grade l uses only B_(l-1), with a constant
identity contribution when l=1. Consequently endpoint output grade never
uses a child component of higher grade. The same statement holds for F.

This is a fixed filtration height L-1. It is not the assertion that every
raw gate preserves the grade: R lowers it temporarily. The exact inverse
identity cancels the offending upper-right block before the endpoint is
interpreted. Repeated use of this core algebra does not increase the number
of grades, but a complete supplier still has to bind its role inventories,
physical tensor axes, source/exits, and all native intermediate relations.

## 4. Literal finite boundary implementation

At the ideal native specialization, let q be the canonical central Gaussian
and d=D1 D2 the product of the two fresh disjoint eight-axis Gaussian
factors. Every native invocation has its own full set of arbitrary helper
inputs. The two-full endpoint on one main pair is d M(q,q^-1).

For each of the 112 main role pairs, take arbitrary X_0,...,X_(L-1) and
Y_0,...,Y_(L-1), and one owned initially zero terminal field Z.

1. Rotate the Y fields and Z so the L query inputs are
   Y_1,...,Y_(L-1),0 and Z holds the original Y_0.
2. Run the L two-full units on (X_j, query-Y_j), retaining all 2L native
   helper sets. These are full native programs, with their ordinary owned
   centers restored at completion.
3. Apply the full rank-17 Gaussian d q^-1 to Z. This is charged explicitly.
4. Route Z into external Y_0, route query output j into external Y_(j+1)
   for j<L-1, and place the unused terminal query output into the owned Z.
5. Clear Z explicitly after its native unit has completed. It has no
   independent productive output credit. Its initialization, permutation,
   movement, and clearing are scalar/storage costs of the fixed program.

All original arbitrary inputs are retained. The endpoint is

    X'_j = d q X_j,
    Y'_0 = d q^-1 Y_0,
    Y'_j = d q^-1 Y_j + d(I-q^-1)X_(j-1),  j>=1.

The inverse endpoint is diag(d^-1,d^-1) F(q,q^-1). It can use the actual
inverse core in the same boundary construction, the corresponding d^-1
fresh-axis wrapper, and an explicitly charged rank-17 boundary Gaussian
d^-1 q on Y_0. The Gaussian inverse orientations differ by the retained
Pauli corrections; the full native binding must price those charts. The
inverse is not obtained by attempting to reverse the owned CLEAR operation.
Exact inverse equality here concerns the completed linear maps; a rounded
same-realization implementation needs its own proof.

For the general A_L lemma, the lane-coupled core is one program M(A,B), not
L independent scalar-q calls. The shift/owned-field construction is the
same, provided that this actual core and its inverse are available with
their declared costs. The ideal native specialization above proves only
the local endpoint and boundary invoice.

## 5. Paid boundary invoice

The pinned round-three two-full split invoice is

    target T = {4:56, 7:14, 8:94, 9:652, 17:224},
    paid   P = {1:4656, 2:920, 3:1386}.

At the ideal local native specialization, the L-lane construction retains
exactly L*T productive target jobs. Its full local paid profile is L*P plus
112 rank-17 boundary Gaussians. Splitting
those on disjoint axes into rank-one jobs gives

    P_L = {1:4656*L+1904, 2:920*L, 3:1386*L}.

This explicitly pays for every otherwise missing Y_0. The raw rank surplus
is 96L-1904. At candidate exponent reduction C=17/5000=.0034, the moment
margin is

    L * (sum_k T[k] k^(1-C) - sum_r P[r] r^(1-C)) - 1904.

The bracketed term is about 28.6560369624. Therefore L=67 is the least
integer lane count making this particular exact local invoice positive;
L=66 fails. The verifier certifies both signs with rational log/exp
enclosures rather than accepting rounded root digits. L=67 uses 112
terminal owned fields and 67 copies of every retained helper inventory.

The scalar passes, storage, row-stock constants, and semantic precision
have not been folded into a completed outer multiplication tariff. In
particular the boundary must supply an exact common-diagonal Gaussian;
replacing its rank-one leaves by arbitrary graded child maps does not by
itself meet that requirement. A recursive implementation or a corrected
graded endpoint identity is still required. This positive local moment is
a screening result, not a bound claim.

## 6. The remaining native obstruction is precise

The proof requires exact upper-right cancellation AB-I=0 inside M. An
arbitrary graded approximation to a native word, even if its full inverse
is available, need not be U(A) or L(-A^-1) on the main ports. A positive
grade upper-right residue H=S before the exterior boundary produces

    H R = S R = I-P_0,

a nonzero grade-zero residue. Thus lower-triangular child outputs and
whole-word inverse coherence by themselves do not establish this caller.
This is a rejection control for an incorrect inference, not a universal
impossibility claim. Proving a coherent native shear/frame representation,
or charging its correction, is the concrete next obligation.

## 7. Preferred variant: omit the boundary target honestly

There is a distinct contract that does not request an exact boundary
Gaussian at all. Keep L productive X fields, but only the L-1 productive
Y fields labelled Y_1,...,Y_(L-1). There is no Y_0 input or output in this
contract. The final query Y_L is owned, initialized to zero, and cleared
after its completed unit. Every retained arbitrary input is still used
exactly once; no supplied input is silently discarded.

Let P project onto the leading L-1 lanes and J embed those lanes. Define

    C(A)=P A J.

For lower-triangular A,B, C is multiplicative and C(A)P=PA. The literal
program runs the L cores on (X_j,Y_(j+1)), with Y_L=0, retaining X_j and
the first L-1 query-Y outputs. Its endpoint and actual inverse are

    E_minus = [[A, 0], [P(I-B), C(B)]],
    F_minus = [[B, 0], [P(B-I), C(A)]].

The inverse proof is the proof of Theorem 2 with T,S replaced by C,P.
The lower block of E_minus F_minus is

    P(I-B)B + C(B)P(B-I) = P(B-B^2)+PB(B-I)=0,

and the other product is analogous. At the ideal native specialization,
all L X outputs and L-1 Y outputs have the intended full rank-17 Gaussian
diagonal. All 2L native helper sets are retained. Each main pair has one
terminal owned field; it receives no productive target credit.

Assign grade j to X_j, and grade j to external Y_j for j>=1. The row of
P(I-B) corresponding to Y_j is the old lane row j-1; therefore every
nonzero cross-role block raises the grade at least one. The endpoints
have fixed grade span L-1. Lane 0 has only the X payload; other lanes have
both X and Y payloads. Thus this variant is a filtered inverse-pair lemma
on a nonuniform graded module, rather than closure in the equal-payload
algebra A_L of Section 1.

More generally, on F=direct_sum_(h=0)^H F_h, use P onto F_0,...,F_(H-1)
and grade its Y copy one level higher. The same proof works even if the
diagonal blocks differ. Output grade-h dimension becomes d_h+d_(h-1),
with d_(-1)=0. Repeated formal use preserves H, but its grade dimensions
obey a Pascal recurrence and can grow polynomially with depth. The omitted
Y payload at each use is the current highest-grade payload d_H, not a
fixed fraction 1/L after arbitrary repeated use. With fixed H and a
nonzero lowest grade, the highest grade eventually dominates the total
payload under this bare Pascal iteration. Thus the one-shot invoice below
cannot be iterated unchanged. This is not yet a fixed-role finite native
compiler; per-grade paid/target balance, source/exits, physical embedding,
storage, and costs remain separate obligations.

The exact local invoice now is

    target = L*T - 112 rank-17 jobs,
    paid   = L*P.

This charges the entire missing boundary by lost productive credit. It
does not contain the 1904 boundary calls from Section 5. The raw rank
surplus is still 96L-1904, but the concave moment cost of omitting the
targets is smaller than paying 1904 rank-one jobs. At C=.0034,

    margin = L * base_margin - 112 * 17^(1-C).

The exact interval checker proves L=65 gives a negative margin, while
L=66 gives a margin in [5.551473221217,5.551473223332]. Thus 66 is the
minimum lane count for this particular no-boundary-provider local invoice.
The corresponding L=66 target and paid profiles are

    target = {4:3696,7:924,8:6204,9:43032,17:14672},
    paid   = {1:307296,2:60720,3:91476}.

This removes the exact-boundary-provider obligation of Section 5. It does
not remove the coherent native shear obligation of Section 6, and it does
not establish the nonuniform graded-module matching required by recursion.

## Open next questions

- Bind the actual all-column round-three word to coherent shears over this
  lane algebra, including helper ports, owned centers, and frame changes.
- Bind every Pascal source, exit, complement, and field adapter to the same
  fixed filtration, without reclassifying owned fields as productive data.
- Substitute the actual scalar/precision/stock constants into the retained
  finite compiler and ordinary recursion. For Section 5, price the exact
  boundary Gaussian implementations. For Section 7, instead bind the
  nonuniform graded-module interface and its role inventory.
- Compare the same-cost inverse recipe with deterministic rounded execution;
  endpoint algebra alone does not establish rounded inverse coherence.

Attribution: the native paid profile and helper interface are Cao Yifan's
round-three PR4610 lineage; the two-full border and its inverse-pair caveat
are the predecessor Yiyang/Codex packages; the finite mixed-target compiler
is Jacob Alan Sussman's Theorem1G lineage, as pinned by this repository.
