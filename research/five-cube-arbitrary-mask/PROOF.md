# An arbitrary common Boolean mask does not lower the five-cube copy floor

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.

This is a written structural proof with exact finite checks. It is not a
proof-assistant formalization, a physical decoder, or a new multiplication bound.

## Statement and predecessor boundary

Use the 32 ports `x in F2^5`, parity `p(x)`, and the rational Gram

```
G[x,y] = 2(4-d(x,y))(2-d(x,y)),   d(x,y) = HammingDistance(x,y).
B[x,y] = 1 + p(x) + p(y)                          over F2.
E = 1+p,  O = p.
```

For **any Boolean function** `h : F2^5 -> F2`, let
`C_h = span_F2{E,O,h}`. Consider any finite list of factors `f_t,g_t in C_h`
whose binary outer products sum to B on **every** port pair. Terms may repeat,
cancel, or have zero cost. Discard a term if an evaluated factor is zero. Set

```
C_total = sum_t rank_Q G[supp(f_t), supp(g_t)].
```

**Theorem.** `C_total >= 32`, with equality attained by the two parity totals
`B = E E^T + O O^T`. There is no degree restriction on h and no term-count cap.

The attaining value and parity witness are credited to PR1046 and its lineage.
PR1222 establishes this floor for all common quadratic-mask codes using a
finite orbit/graph certificate. PR1177 allows arbitrary masks but at most three
terms. Here the new coverage is arbitrary Boolean degree **and** arbitrary
finite term count in a common one-mask code. This does not extend PR1046's
separate theorem for the entire six-dimensional affine code, nor PR1222's
rank-cap tradeoff, nor the two-mask result in PR1482.

## 1. The two parity bases

For each subset S of the five coordinates with `|S| <= 2`, set
`chi_S(x)=(-1)^(sum_{i in S} x_i)`. The 16-component real vector
`v_x=(chi_S(x))_S` has Gram G. Indeed, writing `z=5-2d`,

```
sum_{|S|<=2} chi_S(x) chi_S(y)
  = 1 + z + (z*z-5)/2 = 16-12d+2d*d = G[x,y].
```

Distinct ports of the same parity have distance two or four, so their Gram
entry is zero; the diagonal is 16. Thus the 16 even vectors divided by four
and the 16 odd vectors divided by four are two orthonormal bases of R^16.
The positive global scale does not affect any restricted rank. Since G is
rational, its ranks over Q and R agree. Decoder equality remains over F2.

We will prove a more general lemma for two real orthonormal bases in R^n.
The only special five-cube fact needed is the parity-basis property above.

## 2. Two binary partitions of two orthonormal bases

Call the two bases E and O, and split each by h into cells `E_0,E_1` and
`O_0,O_1`. Let `X_i=span_R E_i`, `Y_j=span_R O_j`. Then

```
R^n = X_0 orthogonal-sum X_1 = Y_0 orthogonal-sum Y_1.
```

There is an orthogonal decomposition into:

* `d_ij = dim(X_i intersect Y_j)` one-dimensional components of type `(i,j)`;
* `g` two-dimensional components, each containing one direction from each of
  the four cells, with basis vectors
  `e_0=(1,0), e_1=(0,1), o_0=(c,s), o_1=(-s,c)`, where
  `c,s>0` and `c*c+s*s=1`.

In particular, `sum_ij d_ij + 2g = n`. Rotating the bases **within each cell**
and changing signs puts them in this form. This is the usual two-projection
decomposition; the following argument supplies it here rather than assuming
that a finite collection of angles establishes it.

Let P,Q be the orthogonal projections onto X_0,Y_0. On X_0, the real symmetric
operator PQP has an orthonormal eigenbasis and eigenvalues in [0,1]. Eigenvalue
one gives `X_0 intersect Y_0`; eigenvalue zero gives `X_0 intersect Y_1`.
For a unit eigenvector u with `0<lambda<1`, define

```
w = (Q u - lambda*u) / sqrt(lambda*(1-lambda)).
```

Then w lies in X_1, has norm one, and

```
Q u = lambda*u + sqrt(lambda*(1-lambda))*w,
Q w = sqrt(lambda*(1-lambda))*u + (1-lambda)*w.
```

Different orthonormal u's give orthonormal w's, and their planes are mutually
orthogonal. The Y_0 and Y_1 directions in this plane have the displayed form
with `c=sqrt(lambda)`, `s=sqrt(1-lambda)`. The remaining orthogonal complement
lies in X_1 and is Q-invariant, so it splits into `X_1 intersect Y_0` and
`X_1 intersect Y_1`. This accounts for every dimension, including empty cells,
repeated eigenvalues and endpoint angles. Endpoint angles are one-dimensional
components, not generic planes.

## 3. Why this is a legitimate rank reduction

Every form in `span_F2{E,O,h}` is constant on each of the four cells. Its
support therefore contains either the whole cell or none of it. Invertible
real changes of basis within a cell multiply any selected row/column block
by invertible matrices and preserve its real rank. After those changes and
permutations, each restricted Gram is block diagonal along the components
above. Its rank is the **sum** of the component ranks.

We do **not** apply these real basis changes to the binary decoder matrix.
That would conflate two fields. Instead, the original all-pairs identity
implies the same binary equation for every pair of nonempty cell types,
because all factors and B are constant on those types. Every cell used by a
component is nonempty. Those cell equations are all the binary reasoning below
uses; no rational transformation of an F2 identity is asserted.

## 4. Each component pays twice its dimension

On a one-dimensional component `(i,j)`, the two labels, from E_i and O_j,
are parallel. A term has pairing rank one exactly when both its reader and
source restrictions on these two cell types are nonzero; otherwise its rank
is zero. The binary target on these two types is I_2: equal-parity pairs are
one and opposite-parity pairs zero. A sum of fewer than two nonzero rank-one
binary outer products cannot equal I_2. Therefore each such component costs
at least **two**, without any restriction on the total number of terms.

On a generic plane all four cell types are present. Their coefficient
evaluation rows, in the basis `(E,O,h)`, are

```
E_0: (1,0,0),  E_1: (1,0,1),
O_0: (0,1,0),  O_1: (0,1,1).
```

Every nonzero form selects either two or all four labels. Any two distinct
labels on this plane are linearly independent: the six determinants are
`1,s,c,-c,s,c*c+s*s`. Consequently every active term has restricted Gram rank
**two**. This uses ordinary real inner products and full rank of both selected
label matrices. The binary target on the four cell types is `J_2 direct-sum J_2`,
of rank two, so at least two active terms are needed. Each generic plane
therefore costs at least **four**.

Sum the term costs over components and exchange the two finite sums:

```
C_total >= 2*sum_ij d_ij + 4*g = 2*n.
```

This proves the general two-basis lemma. The original parity totals have ranks
n and n, and always attain it. At n=16 this gives the claimed sharp 32 floor.
Degenerate masks `h in span{E,O}` are included: generic planes then cannot
occur, and the one-dimensional argument still applies.

## 5. Exact rank formula and a finite certificate for the lower bound

For nonzero coefficient vectors a,b in F2^3 define
`v_a(p,h)=a_E*(1-p)+a_O*p+a_h*h` over F2 and

```
epsilon_ij(a) = 1 if (v_a(0,i),v_a(1,j)) != (0,0), else 0.
c(a,b) = sum_ij d_ij*epsilon_ij(a)*epsilon_ij(b) + 2*g.
```

The component analysis proves that c(a,b) is the **exact** rational pairing
rank on the cube. If a nonzero coefficient represents the zero function,
then g=0 and all its relevant epsilon values vanish, as required.

The multiplicities require no numerical eigensolver. With Q the orthogonal
cross-basis matrix, `A_i` its E_i row set and `B_j` its O_j column set,

```
d_ij = |A_i| - rank_R Q[A_i,B_(1-j)],
g = |A_0| - d_00 - d_01.
```

An independent computation uses
`d_ij=dim X_i + dim Y_j - dim(X_i+Y_j)` on the Walsh vectors instead.

For an explicit finite lower-bound certificate, encode a coefficient sum by
`M in F2^(3x3)` (512 states). Adding term (a,b) toggles `a b^T`. For each
one-dimensional type put `V_ij=[(1,0,i);(0,1,j)]` and set

```
phi_ij(M) = rank_F2(V_ij M V_ij^T),
phi_generic(M) = 2*rank_F2 M.
```

Rank subadditivity proves that the absolute potential change across any term
edge is at most its component cost. The target is `M_B=diag(1,1,0)`, where
the potentials are two and four. Both checkers independently verify every
edge for all five component types: `5*512*49 = 125440` inequalities. Thus a
weighted sum of these five potentials certifies the floor for any nonnegative
multiplicities. The proof does not require that a shortest-path search succeeds.

When the evaluation code has rank two, coefficient representations of B need
not equal M_B. The all-pairs identity nevertheless forces
`V_ij M V_ij^T=I_2` on every type with d_ij>0, and g=0. The same potential
argument therefore gives 2n for **every** valid representation, not just the
chosen coefficient lift. The component proof in section 4 avoids this issue
entirely. The verifier also checks all such degenerate lifts.

## 6. What the finite checks establish

The primary checker uses integer elimination with gcd normalization. The
separate checker reconstructs G from Walsh characters and uses Fraction
elimination, with no imports from the primary or predecessor code. Both
compute every ordered term rank for 324 explicitly specified mask fixtures:
all 256 Boolean functions of the seed-selected coordinates `(0,1,4)`, all
squarefree monomials in five coordinates, the two parity masks, and 42 seeded
truth tables, with duplicate masks removed. Degrees zero through five and the
zero mask are present. This is **not** an exhaustive 2^32-mask search.

They also check the full binary parity witness, the orthogonal-basis identity,
the component potentials, endpoint/empty-cell cases and deliberate failures.
Universal coverage comes from sections 1-4; the fixtures corroborate the
implementation and the exact rank formula. No independent human review is
claimed; both implementations share the same AI-assisted author.

## 7. Conditional budget and exclusions

Under PR1046's retained additive per-total copy pricing and stage ledger, for
`v=32` and `s>=3`, even granting all other expenses zero,

```
D <= (s-1)*32 - s*C_total <= -32.
```

Source access, gathers, helpers, arithmetic, frame changes, restoration,
recursive children, idle work, precision and hosting contribute only additional
nonnegative expense in that stated relaxation. Thus this mechanism cannot
produce a positive deficit in that ledger. It gives no new kappa; improving
the other supplier or outer assembly cannot repair this local negative budget.

The theorem does not cover different reader/source mask codes, two independent
extra masks, arbitrary functions of the cell bits, masked-only identities,
interactive or nonlinear data messages, changed copying/stage accounting, or
Grams without the two real orthogonal bases. Port-mask nonlinearity is allowed;
the communicated messages remain linear XOR sums of data. The proof's general
two-basis lemma applies beyond this cube only after its hypotheses are proved.
No physical source-access/frame realization or selected-supplier admission is
provided. All-size/compiler, mutable-source, whole-call hosting, precision/tape,
bit H1-H5 and analytic transfer remain outside this contribution.
