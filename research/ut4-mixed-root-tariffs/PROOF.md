# Sharp tariffs for heterogeneous noncentral UT4 commutator targets

This is a written uniform theorem in an explicit formal model, supported by
exact finite algebra checks. It is not a proof-assistant theorem or a supplier
implementation. The quotient and rank methods are predecessor methods; the
delta is the mixed target domain and the simultaneous sharp tariff below.

## Model and statement

All scalars and ranks in this note are over F2. Set

```
G = UT4(F2), R = F2[G],
a=I+E12, b=I+E23, c=I+E34,
u=I+E13=abab, v=I+E24=bcbc, z=I+E14=abcbabcb.
```

The three roots u,v,z commute and are involutions. A target on r scalar roles is

```
T = diag([u^s_i v^t_i z^h_i] : i=1,...,r),
```

where s_i,t_i,h_i are binary. Identity roles include every borrowed dirty role.
Equality is in the full matrix algebra Mat_r(R), on every arbitrary input.
In particular, an extra role's output must equal its input, and its initial
value cannot contaminate any target output.

A paid factor is D_N(g)=I+([g]+1)N, with g in {a,b,c} and N=xy^T a nonzero
binary rank-one matrix. Both idempotent and nilpotent N are allowed. Since
g^2=1, every factor is an involution regardless of N^2. Any interleaved scalar
GL_r(F2) operation is optimistically free. Conjugate it into the adjacent
couplings and collect scalar operations at one end. Augmentation [g]->1 sends
the factors and T to identity, so the remaining scalar operation must be I.
Thus it suffices to study products of the normalized paid factors.

Every paid occurrence, including undo, is counted. There are no free address
maps, initialized roles, COPY, ERASE, higher-rank unit calls or unpaid inverses.
The direct construction below needs no scalar mixing or extra roles. Physical
realization and its costs are separate obligations; a formal unit price is
not an implemented recursive child price.

Let S,T0,H be the sets of indices with s_i,t_i,h_i equal to one. Every such
formal word, for any finite r and any length, satisfies

```
n_a >= 2 |S union H|,
n_b >= 2 |S union T0 union H|,
n_c >= 2 |T0 union H|.                                  (1)
```

If no role is a pure central target, equivalently H is contained in S union T0,
these three bounds are attained simultaneously. Therefore nonnegative uniform
letter prices alpha,beta,gamma have exact optimum

```
2 alpha |S union H| + 2 beta |S union T0 union H|
                         + 2 gamma |T0 union H|.        (2)
```

The union cardinalities are ordinary integers. For pure-central roles, (1) is
only necessary; no sharpness or optimum is claimed here. The central family
has stronger predecessor results in PR1662/1680/1690/1816.

## Fixed algebra lemma and source of the coefficient constraints

Use the predecessor degree-three quotient

```
Q = F2<A,B,C> / (A^2,B^2,C^2, AC-CA, all monomials of degree >=4).
```

We write its generators in lower case in code. Its 17 monomial basis elements
are

```
1,a,b,c,ab,ac,ba,bc,cb,aba,abc,acb,bab,bac,bcb,cba,cbc.
```

Multiplication concatenates words, commutes ca to ac, kills squares, and kills
degree at least four. The only overlaps of commuting with square reduction
in these degrees, caa and cca, reduce to zero in either order. The checker
also verifies every one of the 17^3 basis associativity equations.

There is a homomorphism G -> Q^* sending a,b,c to 1+a,1+b,1+c. We use an exact
finite lemma for this fixed group, not an assumption about all presentations.
Write an upper-triangular group matrix's six entries as (A,B,C,D,E,F) at
12,23,34,13,24,14. Its normal form is

```
a^A b^B c^C u^(D+AB) v^(E+BC) z^(F+AE).
```

The primary program substitutes the quotient images in this normal form and
checks all 64^2 products against the explicit group law. The separate program
uses literal four-by-four matrix multiplication and a BFS to construct the
images. It constructs Q instead from all 40 words of length at most three,
reduces the full two-sided relation space by binary elimination (rank23),
and independently checks all 4,096 products and 4,913 associativity equations.
The two complete group-map transcripts agree. This finite algebra lemma is a
premise of the uniform proof; it does not enumerate role counts or word lengths.

The images of the three roots are

```
u -> 1+ab+ba+aba+bab,
v -> 1+bc+cb+bcb+cbc,
z -> 1+abc+acb+bac+cba.
```

Every nonconstant term here has degree at least two, so their pairwise products
vanish in Q. Consequently the image of u^s v^t z^h is one plus the sum of the
three indicated nonconstant parts, weighted by s,t,h. This observation is the
central-twist contribution missing from a second-degree-only calculation.

## Both spans of each label must carry the required target spaces

Write U=diag(s_i), V=diag(t_i), Z=diag(h_i). In the Q-image of a word with the
desired endpoint, the first-degree coefficients of a,b,c are zero. The
coefficients of ab and ba equal U; bc and cb equal V; and abc,acb,bac,cba
equal Z. Other cubic coefficients are not needed for this lower bound.

For each label g, collect its coupling columns x_j in X_g and rows y_j^T in
Y_g. The zero first-order coefficient says

```
X_g Y_g = sum_(g calls) x_j y_j^T = 0.
```

Therefore im(Y_g) is contained in ker(X_g), giving

```
n_g >= rank X_g + rank Y_g.                             (3)
```

Expansion preserves chronological scalar order: a chosen subsequence
j1<...<jk contributes N_j1 ... N_jk. Its image lies in the image of its first
coupling and its row space in the row space of its last coupling.

For label a, coefficient ab begins with a and coefficient abc begins with a.
Hence im U+im Z is contained in im X_a. Coefficients ba and cba end with a,
so row U+row Z is contained in row Y_a. Both dimensions are |S union H|.
Equation (3) gives the first inequality of (1).

For c, use cb and cba for columns and bc and abc for rows. These give
|T0 union H| for both ranks, proving the third inequality.

For b, coefficients ba and bc give im U+im V. The coefficient bac also has
im Z: its two word representatives bac and bca both begin with b, since a
and c commute in Q. Thus all its summands start with a b-coupling. Similarly
acb has representatives acb and cab, both ending with b. Together with ab
and cb this gives row U+row V+row Z. The column and row dimensions both equal
|S union T0 union H|. Equation (3) proves the middle inequality.

No call is charged twice by adding separate lower bounds on that label. The
same column space and the same row space contain the relevant unions. Both
are required: three nonzero couplings with columns (e1,e2,e1+e2) and identical
row e1^T sum to zero, yet the column rank is two and row rank only one.
Column rank two alone would not imply four calls.

The argument also holds after a common scalar conjugation of the entire
endpoint. The designated restored complement is then expressed in that basis;
this is not a claim that a conjugation mixing active and dirty coordinates
preserves each original coordinate's output boundary.

## Simultaneous attainment and why the pure central case is separate

These literal address words have the indicated full group products and counts:

| Target | Word | a | b | c |
|---|---|---:|---:|---:|
| identity | empty | 0 | 0 | 0 |
| u | abab | 2 | 2 | 0 |
| v | bcbc | 0 | 2 | 2 |
| uv | abacbc | 2 | 2 | 2 |
| uz | acbabc | 2 | 2 | 2 |
| vz | abcbac | 2 | 2 | 2 |
| uvz | acbacb | 2 | 2 | 2 |

Use the coordinate projector E_ii for every letter of the i-th target's word,
and concatenate across roles. A coordinate factor is exactly [g] on its
designated role and identity elsewhere. Thus these are full formal identities,
including arbitrary dirty roles, not conclusions inferred from Q. Each row
of the table attains (1) separately in every label; summing proves (2).

The same-role uv six-call possibility already appears as a boundary control in
Adam Gall's PR1935; it is not claimed as a new word. That predecessor's
disjoint u/v tariff is recovered when H is empty and S,T0 are disjoint.
When they overlap, middle calls are charged on the union, not twice.
Central twists force the third-order spaces and may add an outer-letter bill.

The pure central z has the direct eight-call word abcbabcb, whereas (1) alone
gives six. It is deliberately excluded from the sharp family. PR1662 proves
eight for one target even with dirty workspace by a stronger middle quotient;
this note does not reprove or extend that result. Mixed families that include
pure-central roles require additional analysis to decide their exact tariff.

## Evidence and limits

The checkers agree on all 20,440 ordered two-role words through length three
over the 27-label/coupling alphabet, including nilpotents. This tests coefficient
expansion and span implications, not arbitrary-length optimality by search.
There are 399 diagonal attaining fixtures (all seven-label tuples of lengths
one through three, each with one extra role), and three common-conjugate
fixtures through eight roles. Full formal products agree with separately
implemented faithful regular operators on 99,264 basis columns.

A nonzero formal error ([z]+1)([a]+1) on a dirty role is killed by Q but changes
every one of that role's 64 basis columns. It is a diagnostic operator, not an
asserted legal paid-word counterexample. A two-call noncoordinate nilpotent
loop checks a legal transient dirty interaction and its complete restoration.
Forty single-call deletions fail, including the central control. Changed-rank,
alphabet, order, receipt, source and optimization controls are separate tests.

All-workspace and all-length conclusions come from the written span argument
and the fixed-group algebra lemma, not extrapolation from finite fixtures.
No rational-frame translation, physical compiler, hosting, precision/tape,
all-size realization, selected cold replay or outer multiplication theorem is
provided. The selected record and every frozen predecessor remain unchanged.
