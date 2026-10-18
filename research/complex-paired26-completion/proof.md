# Exact minimum 62 for the fixed 26-puncture paired normal

**Date:** 2026-10-14. **License:** Apache-2.0. **Prepared for:** Andrey Mas.

## 1. Result and exact scope

**Theorem.** Use precisely the 120 root-line representatives, fixed puncture set,
ordinary-transpose all-pairs identity, and separate actual-support COPY charges
specified below. Among all exact eight-term decoders over **C** whose designated
first normal pair is

```
a = (1,-1,-1,-1,1,1,-1,1)/2,
b = (0,0,0,0,0,0,-2,2),
```

the least complete separate COPY cost is **62**, attained by a rational decoder
with charges **(6,8,8,8,8,8,8,8)**.

There is also a complete equality classification. Up to permutations of the
seven residual terms and their paired nonzero complex rescalings, while keeping
the designated first pair exactly unchanged, there are **256 optimal
completions**. They are described in Section 9.

A sharper branch statement is useful: any completion with a residual A-normal
whose live support has label dimension below nine costs at least **67**; this
branch bound is attained by a separate rational witness.

These are results for **one fixed puncture and one fixed ordered pair**, not an
optimization over all 26-puncture sets. The exact minimum assertion does not
assume the real root-flat classification F6. It does not replace arbitrary
complex paired normals independently by real support representatives. No
Hermitian inner product, positive complex norm, physical supplier, preparation,
hosting, cross-term sharing, ninth term, masked identity, kappa, or frontier
claim is involved.

The puncture, designated cost-six pair, and previous 69-cost completion belong
to **woklerx's PR1020**, not to this investigation. The new contributions here
are the fixed-live-set kernel inventory, its residual dual-compatibility
consequence, the sharp minimum 62, and the classification of equality cases.
The annihilator-kernel method itself follows the credited predecessor work;
see ATTRIBUTION.md.

## 2. Model, indexing, and verified finite geometry

Generate doubled roots v in Z^8 in two families: vectors with two entries in
{−2,2} and all other entries zero, and vectors in {−1,1}^8 with an even number
of minus signs. In each unoriented pair retain the lexicographically larger
vector, and sort. The resulting indices are 0 through 119. Put r_i=v_i/2.
Every r_i has ordinary square 2.

Delete on both sides exactly

```
P = [0,23,24,25,26,34,35,36,37,48,60,61,62,63,66,67,
     72,73,76,77,78,79,82,83,88,89].
```

Let L be the 94 remaining indices in increasing order, and let R have rows r_i
for i in L. The label pairing, including the unit coordinate, is

    N_ij = (1 + (v_i dot v_j)/4) mod 2.

The quotient label space has dimension nine. More concretely, take the first
nine independent **pairing rows** in the specified greedy scan. Their indices
are

    J_label = [0,1,2,3,6,12,20,30,42].

Define ell_i=(N_i,j) for j in J_label. Both checkers reproduce this basis.
The primary verifier checks rank_F2(N)=9 with bitset and dense elimination,
checks that H=N[J_label,J_label] is invertible, and checks

    N_ij = ell_i H^(-1) ell_j^T

on all 14,400 ordered pairs of the full 120-line geometry. Thus these coordinates
carry an explicitly verified nondegenerate bilinear form beta. The live
pairing also has rank nine.

The live doubled-root minor using rows

    [1,2,3,6,12,20,30,42]

and all eight columns has determinant **−256**. Consequently the same true-root
minor has determinant **−1**, and R has rank eight over Q and C. This is a
direct minor certificate; no F6 classification or norm argument is needed.

For any nonzero z in C^8 define

    S(z) = {i in L : r_i dot z != 0},
    W(z) = span_F2{ell_i : i in S(z)},
    d(z) = dim_F2 W(z).

Supports here are the actual nonzero supports, not supersets, masks from a
proposed factorization, or supports after cancellation between terms. Normals
may point along punctured root directions: a normal is a vector in C^8, not an
additional port. This does not restore a deleted row.

For paired normals x,y the charge is exactly

    q(x,y) = rank_F2 N[S(x),S(y)]
           = rank beta restricted to W(x) x W(y).

Nondegeneracy gives the elementary bound

    q(x,y) >= d(x)+d(y)-9.                         (2.1)

Indeed the kernel of W(x) -> W(y)* is W(x) intersect W(y)^perp, of dimension
at most 9−d(y). In particular, if d(x)=9, the charge is **exactly d(y)**.
The same statement holds with the two sides interchanged.

## 3. Normal form for every arbitrary-complex eight-term decoder

Suppose D,T in C^(94 x 8) satisfy D T^T=2 R R^T on every ordered entry.
Because R is injective as a map C^8 -> C^94 and R^T is surjective, R R^T has
rank eight. Therefore D and T each have rank eight. The column space of
D T^T equals the column space of D and also equals the column space of R.
Transposing the identity gives the corresponding statement for T.

It follows that there are unique invertible A,B in C^(8 x 8) with

    D=RA,  T=RB.

A left inverse of R and its transposed right inverse give

    A B^T = 2I,
    B = 2 A^(-T),
    A^T B = 2I.                                  (3.1)

No inversion of R^T R is used. All transposes are ordinary transposes.
Writing paired columns as a_k,b_k, with k=0,...,7, (3.1) says

    a_j dot b_k = 2 delta_jk.

Both column lists are bases. With a_0=a and b_0=b fixed, a dot b=2, and

    a_k in b^perp,  b_k in a^perp,  k=1,...,7.     (3.2)

These are necessary constraints on all admissible arbitrary-complex
completions, not a restriction imposed for the construction.

## 4. An exact finite reduction for support-dimension drops

For each of the **511 nonzero** lambda in (F2^9)* form an integer matrix Z_lambda
whose rows are precisely the doubled roots v_i for which

    i in L and lambda(ell_i)=1.

For every z in C^8,

    lambda annihilates W(z)
    iff v_i dot z=0 for all rows of Z_lambda
    iff z belongs to ker_C Z_lambda.              (4.1)

Thus a nonzero normal has d(z)<=8 if and only if it belongs to at least one
of these 511 complex kernels. This proves completeness of the finite
reduction; it is not sampling directions in C^8.

Every Z_lambda is rational. A nonzero integer minor remains nonzero over C.
For a rank-eight record, the certificate gives an 8-by-8 nonzero minor. For a
rank-seven record it gives a 7-by-7 nonzero minor and a nonzero real root
vector annihilating **every** row. These establish exact rank, and in the latter
case establish the entire kernel as one complex line C r_j. No conclusion
about complex normals is drawn from their ordinary squares.

The primary verifier selects candidate independent rows by fraction-free
elimination and validates their minors using a separate Bareiss determinant
implementation with checked exact divisions. The additional audit.py imports
no primary-verifier code and instead eliminates each actual violation matrix
using normalized rational arithmetic. Both methods agree on all 511 matrices.

## 5. Complete kernel inventory for this fixed live set

There are **482 rank-eight matrices** and **29 rank-seven matrices**. The latter
have **27 distinct kernel lines**, exactly the root directions indexed by

    P union {30}.

Only r_0 has support dimension seven. All the other 26 reduced directions
have support dimension eight. Every nonzero complex normal not on one of
these lines has support dimension nine.

Here is the complete reduced-direction inventory. Lambda values use the
nine-bit coordinates of Section 2; the full 511 records and their exact minor
witnesses are in certificate.json.

| Root index | Label dimension | Live support size | Nonzero annihilator functionals |
|---:|---:|---:|:---|
| 0 | 7 | 31 | 1, 140, 141 |
| 23 | 8 | 43 | 121 |
| 24 | 8 | 42 | 117 |
| 25 | 8 | 43 | 118 |
| 26 | 8 | 42 | 122 |
| 30 | 8 | 33 | 12 |
| 34 | 8 | 43 | 244 |
| 35 | 8 | 42 | 248 |
| 36 | 8 | 43 | 251 |
| 37 | 8 | 42 | 247 |
| 48 | 8 | 43 | 286 |
| 60 | 8 | 42 | 382 |
| 61 | 8 | 43 | 370 |
| 62 | 8 | 42 | 355 |
| 63 | 8 | 43 | 367 |
| 66 | 8 | 43 | 334 |
| 67 | 8 | 42 | 322 |
| 72 | 8 | 42 | 336 |
| 73 | 8 | 43 | 348 |
| 76 | 8 | 42 | 499 |
| 77 | 8 | 43 | 511 |
| 78 | 8 | 42 | 494 |
| 79 | 8 | 43 | 482 |
| 82 | 8 | 43 | 451 |
| 83 | 8 | 42 | 463 |
| 88 | 8 | 42 | 477 |
| 89 | 8 | 43 | 465 |

The three functionals 1,140,141 are the three nonzero vectors of the
2-dimensional annihilator of W(r_0). Each remaining reduced direction has
one nonzero annihilator. In particular, this table accounts for all 29
rank-seven matrices, and not merely for 27 sampled roots.

## 6. What the fixed pair permits on the seven residual terms

Intersecting the complete reduced-direction list with the two exact
perpendicular spaces in (3.2) gives

    {reduced A directions in b^perp} = {r_30},

    {reduced B directions in a^perp}
      = {r_23,r_25,r_30,r_34,r_36,r_61,r_63,
         r_66,r_73,r_77,r_79,r_82,r_89}.            (6.1)

All 13 directions on the second line have support dimension eight. The unique
seven-dimensional-support direction r_0 does not belong to a^perp, so it
cannot occur in a residual B column. It cannot occur in a residual A column
either. These exclusions hold for all nonzero complex scalings of the lines.

Set

    c = r_30 = (0,1,-1,0,0,0,0,0).

In the displayed order of the 13 B candidates, the true-root dot products
c dot r_j are

    (-1,-1,2,1,1,-1,-1,-1,-1,1,1,1,1).

**None is zero.** This is the small compatibility fact that rules out the
optimistic but unattainable extra one-unit saving on the A side.

Since A is a basis, at most one of its seven residual columns can be a
multiple of c. All other residual A columns have label dimension nine.
For reference the directly checked pairing costs q(c,r_j) on the 13
candidates are seven for j=30 and eight for every other j.

## 7. Universal lower bound and the sharp exceptional branch

There are two cases, exhausting all arbitrary-complex completions.

**Case I: no residual A column is reduced.** All seven have label dimension
nine. Every residual B column has dimension at least eight by (6.1), so
its paired charge is at least eight by (2.1), or directly by the exact
full-space statement following it. Including the fixed cost-six term,

    total >= 6+7*8 = 62.                          (7.1)

**Case II: one residual A column is reduced.** Suppose a_j is a nonzero
multiple of c. For the six other residual indices k, duality forces
b_k perpendicular to c as well as to a. None of the 13 reduced B lines
in (6.1) is perpendicular to c. Hence every such b_k has label dimension
nine. The corresponding a_k also has dimension nine, since A is a basis
and c is its only possible reduced residual direction. These six terms
therefore each cost nine.

The remaining pair has d(a_j)=8 and d(b_j)>=8, hence costs at least seven.
Consequently

    total >= 6+6*9+7 = 67.                        (7.2)

Combining (7.1) and (7.2) proves the universal lower bound 62. In particular,
counting reduced normals independently on the two sides would only give
an optimistic 61; the additional reduction on the A side actually forces
six residual B sides to become full-dimensional.

The branch bound 67 is sharp: the supplied branch witness has first pair a,b,
second pair c,c, and charges (6,7,9,9,9,9,9,9). Its complete matrices, all
actual supports, and all-pairs checks are in certificate.json. This is an
additional checked boundary example, not an assumption in the lower bound.

## 8. Explicit attaining 62-cost decoder

Choose B columns

    (b, r_23, r_25, r_30, r_61, r_63, r_66, r_73)

and put A=2 B^(-T). Below are the matrices as **rows**, with paired normals
as **columns**.

A:

```
[1/2, 0, 0, 2, 1, 1, 1, 1]
[-1/2, 1, 1, 2, 0, 0, 0, 0]
[-1/2, 1, 1, 0, 0, 0, 0, 0]
[-1/2, 0, 0, 0, -1, -1, 1, 1]
[1/2, 0, 0, 0, -1, 1, -1, 1]
[1/2, 0, 0, 0, 1, -1, -1, 1]
[-1/2, -1, 1, 0, 0, 0, 0, 0]
[1/2, -1, 1, 0, 0, 0, 0, 0]
```

B:

```
[0, 0, 0, 0, 1/2, 1/2, 1/2, 1/2]
[0, 0, 0, 1, -1/2, -1/2, -1/2, -1/2]
[0, 1, 1, -1, 1/2, 1/2, 1/2, 1/2]
[0, 0, 0, 0, -1/2, -1/2, 1/2, 1/2]
[0, 0, 0, 0, -1/2, 1/2, -1/2, 1/2]
[0, 0, 0, 0, 1/2, -1/2, -1/2, 1/2]
[-2, -1, 0, 0, 1/2, 1/2, -1/2, 1/2]
[2, 0, 1, 0, -1/2, -1/2, 1/2, -1/2]
```

The first columns are exactly a and b, not just proportional copies.
The verifier checks both A B^T=2I and A^T B=2I. With D=RA and T=RB it
independently checks all **8,836** ordered identity entries, including all
**4,572 zero-right-hand-side entries**; no identity is tested only on
required or unmasked pairs.

The term accounting is:

| Term | D support size | T support size | D label dim. | T label dim. | COPY |
|---:|---:|---:|---:|---:|---:|
| 0 | 43 | 31 | 8 | 7 | 6 |
| 1 | 73 | 43 | 9 | 8 | 8 |
| 2 | 73 | 43 | 9 | 8 | 8 |
| 3 | 45 | 33 | 9 | 8 | 8 |
| 4 | 73 | 43 | 9 | 8 | 8 |
| 5 | 73 | 43 | 9 | 8 | 8 |
| 6 | 73 | 43 | 9 | 8 | 8 |
| 7 | 73 | 43 | 9 | 8 | 8 |

Each charge is computed directly from the actual N submatrix, with both
bitset and literal dense F2 elimination in the primary verifier. The complete
sum is 62, with COPY/port ratio 62/94=31/47 in this copy-only contract.
No transfer to another cost model is asserted.

Before computing this result the verifier reproduces the supplied PR1020
69-cost matrices unchanged, including both normal identities, all 8,836
ordered entries, actual supports, and charges (6,9,9,9,9,9,9,9). The separate
audit also replays that predecessor example. This is a new replay of the
transcribed input, not a claim to have executed the predecessor program.

## 9. All equality cases: 256 gauge classes

A 62-cost decoder cannot be in Case II. In Case I every residual charge is
exactly the dimension of its B support. Therefore equality holds if and only
if all seven residual B columns are independent complex multiples of seven
directions from the 13-element set in (6.1).

Conversely, choose any seven independent directions from that set. They
span a^perp. Since a dot b=2, adjoining b makes an invertible B. Setting
A=2 B^(-T) gives first A column exactly a. If a residual A column were a
multiple of c, six other chosen B directions would have to be perpendicular
to c, contradicting Section 6. Thus all residual A supports are
nine-dimensional and all seven remaining charges are exactly eight.

This is also the legitimate complex-to-rational reduction for **optimal
completions**. Write b_k=mu_k r_j, mu_k in C nonzero. The paired gauge change

    a_k -> mu_k a_k,  b_k -> mu_k^(-1) b_k

sets b_k=r_j while preserving the full identity and its paired term. It
leaves the designated first pair unchanged. After this change A is the
rational dual of the chosen rational B. This uses simultaneous duality,
not separate real representatives with matching supports.

There is a short exact count of the possible unordered B direction sets.
The 13 directions consist of c and six pairs (x_j,x_j+c), with pairs of
root indices

    (23,34), (25,36), (61,77),
    (63,79), (66,82), (73,89).

Every addition is literal in the specified oriented root representatives.
The vectors c,x_1,...,x_6 are independent in a^perp. For example, the
integer column matrix

    [2b, v_30, v_23, v_25, v_61, v_63, v_66, v_73]

has determinant **1024**, so the corresponding matrix of true normals has
determinant 4. Modulo Cc, the six images of the x_j form a basis.

An independent set of seven directions either contains c and chooses one
vector from each of the six pairs, or omits c and chooses both vectors
from one pair and one vector from each of the other five pairs. These
patterns are sufficient: in the second pattern the doubled pair recovers
c by subtraction. They are necessary because omitting both members of
any pair loses its independent quotient coordinate. Hence the number is

    2^6 + 6*2^5 = 64+192 = 256.

As a second exact finite check, the primary verifier evaluates all
binomial(13,7)=1,716 integer determinants. There are 1,460 zero determinants,
124 equal to −1024, and 132 equal to +1024 in the fixed sorted-column
convention. The 256 nonzero cases agree as a set with the structural formula.
The separate audit instead checks rational ranks of all 1,716 seven-subsets.
The certificate lists all 256 unordered root sets.

No omitted generic complex family can produce another optimum: Sections 4–7
force every optimal B normal onto this finite list before the basis count
is applied. This is a justified finite reduction of the optimum, not an
exhaustive search over numerical complex coefficients.

## 10. Complex and failure-mode controls

The controls are part of the default replay and also execute under Python -O;
there are no assert statements used as verification gates.

**A valid isotropic decoder.** Starting with the 62-cost matrices, make the
residual shear, using pre-shear columns,

    A[:,1] -> A[:,1] + i A[:,2],
    B[:,2] -> B[:,2] - i B[:,1].

This is a paired inverse-transpose change and leaves the designated pair
unchanged. The old A columns 1 and 2 are orthogonal, each of ordinary square
four. Their displayed complex combination is nonzero and has ordinary
square zero. The verifier represents all entries as rational real/imaginary
parts, checks all 8,836 complex ordered entries exactly, and obtains charges
(6,8,9,8,8,8,8,8), total 63. Thus isotropic normals are explicitly admitted.
This is a control, not a second minimum claim.

**Conjugate transpose is wrong.** On this valid complex example, using a
conjugate transpose gives 4−4i rather than 4 at live positions (0,0), namely
root indices (1,1). The mismatch is checked exactly.

**Preserving separate supports does not preserve duality.** Independently
replace the two changed complex columns by the real columns

    A[:,1] + 2 A[:,2],
    B[:,2] - 3 B[:,1].

All sixteen actual column supports agree with those of the complex example,
as checked over Q. Nevertheless the resulting A B^T is

    2I - A[:,2] B[:,1]^T,

with the columns on the right taken from the original 62-cost decoder.
It is not 2I. The normal-form verifier rejects it. This directly tests the
real-representative compatibility pitfall identified in the assignment.

There are additionally fourteen rejection controls: wrong dual scaling,
wrong transpose in the inverse, singular basis, an untracked gauge change
of the fixed pair, a 61-unit undercharge, deletion of an actual support
entry, an altered all-pairs decoder, a ninth zero term, omission of the unit
label, omission of functional 286, a false rank claim, a wrong kernel line,
a forged determinant, and alteration of the puncture. Removing the unit
label changes the ambient binary rank to eight and is explicitly rejected.

## 11. Reproducibility and exact boundaries of the evidence

Run the commands in README.md. The primary checker rebuilds the geometry,
reproduces the baseline first, recomputes all rank witnesses and supports,
checks the new examples and controls, and compares the entire regenerated
certificate to the delivered one. --write-certificate is the explicit
regeneration mode; normal replay does not rewrite the certificate.

The included separate audit uses a different rational-elimination route and
does not import the primary verifier. Both implementations were written in
the same ChatGPT investigation; their agreement is **not** an independent
human or separately authored mathematical review. This is a written proof
with exact machine-checked finite premises, not a Lean or other kernel proof.

Entrywise decoder checks cover the three rational examples and one exact
Gaussian-rational example, 8,836 entries each. They do not separately expand
all 256 optimal examples entry by entry; validity of that entire family
follows from the proven normal-form and support arguments. All 1,716 candidate
root subsets are independently rank/determinant checked.

There is no unresolved lower/upper gap within the stated fixed-pair problem.
Outside it, this package does not classify other punctures, optimize over
other designated pairs, price physical implementation, or assert any
multiplication exponent. No external posting or claim renewal was performed.

The exact upstream heads, Git blobs and SHA-256 pins are retained in
SOURCES.json. After the original research session, Codex authenticated these
bytes against the pinned Git objects and checked the transcribed PR1020 data.
REPLAY.json records that later local verification separately from the original
research-session executions. The mathematics and both checkers are
self-contained and do not require an upstream checkout.
