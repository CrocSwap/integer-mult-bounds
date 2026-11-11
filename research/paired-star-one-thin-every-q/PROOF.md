# One constant thin map misses the three-leaf paired star for every q

**Evidence class: proof.** The argument is an identity in the polynomial ring.
It is not an exhaustive census, not a search over q, and not a claim that a
failed search rules a word out. Selected κ stays 781451/250000000.

The F_2 census in PR #6922 is not an input. It remains a finite statement at
block size 2. The proof below covers every port count at once.

## Hypotheses

The field F has characteristic 2. There are g = 3 leaves and q ≥ 1 coupled
ports. The core and each leaf have dimension d = 2q. Stage j acts on the core
and leaf j. On that plane

```text
E_j = diag(I, I),    T_j = [[I, I], [I, I]].
```

A legal pair on the stage uses one matrix B and complementary halves A, A':

```text
A^2 = A,   rank A = q,   A' = I + A,
AB + BA = B,
P  = [[A+B, B], [B, A+B]],     R  = [[A, A], [A, A]],
P' = [[A'+B, B], [B, A'+B]],   R' = [[A', A'], [A', A']].
```

These are the local matrices of PR #5747, embedded by zero off the core and
leaf j. The same formulae with the two halves exchanged are allowed. Each
stage contributes exactly these two full calls, in either internal order.
Calls of different stages may be interleaved. Projectors of different stages
are not assumed to commute, so B may be nonzero.

A full call is (I + (D_j+1) P)(I + e R) in F[e, D_0, D_1, D_2] / (e^2). The
three stage variables are independent. A thin call is I + e Z with Z a
constant d(g+1) matrix over F. The word contains exactly one thin call, in
any of the seven gaps. The endpoint is

```text
(I + e) (I + x_0 E_0)(I + x_1 E_1)(I + x_2 E_2),    x_j = D_j + 1.
```

## Theorem

No such word exists. Every successful word on this contract therefore uses
at least two constant thin maps. The adjacent word in
`research/coupled31-chronology/COMMUTING.md` meets the endpoint with exactly
two thin maps for every q ≥ 1. An interleaved schedule does not lower that
count at g = 3.

## Proof

### 1. Evaluating at all D_j = 1 forces Z

Set every D_j = 1, so every x_j = 0. Each full factor collapses to I + e R
or I + e R', and the thin factor is I + e Z. In the dual numbers,
(I + e M)(I + e N) = I + e (M + N). The product is I + e times the sum of
the six query matrices and Z, in any order.

The endpoint collapses to I + e. Therefore

```text
(R + R')_0 + (R + R')_1 + (R + R')_2 + Z = I.
```

On one stage, A + A' = I, so R + R' = T_j. The B blocks do not appear in R.
Hence Z = I + T_0 + T_1 + T_2. Call this constant matrix K. In blocks, with
the core first,

```text
K = [[0, I, I, I],
     [I, 0, 0, 0],
     [I, 0, 0, 0],
     [I, 0, 0, 0]].
```

The three leaf columns are equal: each is I in the core and 0 on every leaf.
The three leaf rows are equal for the same reason. Explicitly, on a vector
(c, l_0, l_1, l_2),

```text
K(c, l_0, l_1, l_2) = (l_0 + l_1 + l_2, c, c, c).
```

The image is {(s, v, v, v) : s, v in F^d}, so rank K = 2d = 4q.

Zero thin maps are the same evaluation with Z = 0. Then sum_j T_j = I. The
core-to-leaf block of T_j is I, so this fails before any order is chosen.

### 2. A necessary coefficient in one stage variable

The identity of section 1 is necessary, but it is not the contradiction.
Keep Z = K and pass to the quotient in which x_1 = x_2 = 0 and x_0^2 = 0.
A polynomial identity survives in every quotient.

In that quotient the endpoint is (I + e)(I + x_0 E_0). Its pure part and its
coefficient of e are the same matrix, I + x_0 E_0. That matrix equals its
own inverse because x_0^2 = 0 and E_0^2 = E_0, so the normalized coefficient
is I on either side. The same holds with the three stages relabeled.

Write a general state as (I + e S) U. For a legal half, all four blocks of
P R and of R P equal A: each B term appears twice and cancels, and A^2 = A.
Thus P R = R P = R and [P, R] = 0. A full call of stage 0 has gate
G = I + x_0 P. In the quotient G^{-1} = G. The call updates

```text
S  |->  S + R + x_0 [P, S].
```

A call with x = 0, including the thin call, adds its matrix and does not
produce an x_0 term. The constant term of the final S is the sum of every
emission. Section 1 already forces that sum to be I. The coefficient of
x_0 must vanish, so

```text
sum_{i in stage 0} [P_i, sum of emissions strictly before i] = 0.
```

[P, I] = 0 and [P_i, R_i] = 0, and the sum of all emissions is I, so the
prefix commutator equals the commutator against the emissions strictly
after i. The same relation holds for each stage.

### 3. B cancels, and K does not distinguish leaves

Let M be the sum of the emissions after a stage-0 call, and let k be a
different leaf. The columns of P outside {core, leaf 0} are zero, so M P
contributes nothing to column k. The remaining product is

```text
(PM)_{core, k} = (A+B) M_{core, k} + B M_{0, k},
(PM)_{0, k}    = B M_{core, k} + (A+B) M_{0, k}.
```

Adding those two block rows cancels B:

```text
A (M_{core, k} + M_{0, k}).
```

A later full call of stage k, with half-projection A_kl, contributes A_kl
to M_{core, k} and 0 to M_{0, k}. A later full call of any other stage has
a zero column k. The later thin map, if it is later, contributes K, and

```text
K_{core, k} + K_{0, k} = I.
```

That sum is I for both foreign leaves. Summing the stage-0 calls therefore
gives matrices, independent of which foreign leaf was read,

```text
S_{0k} = C,
```

where S_{0k} is the sum of A_i A_kl over stage-0 halves i that precede a
stage-k half, and C is the sum of those stage-0 halves that precede Z.
Both foreign leaves produce the same C, so S_{01} = S_{02}.

### 4. The half-projections annihilate their prefix

Fix one stage-0 half A. The two halves of stage k are orthogonal and sum
to I, so the sum Later of the stage-k halves after this call and the sum
Earlier of those before it satisfy Later = I + Earlier. Orthogonality
inside stage 0 kills the other stage-0 half, and

```text
A S_{0k} = A Later = A + A Earlier.
```

S_{01} = S_{02} therefore gives A Earlier_1 = A Earlier_2. The earlier
stage-0 half is annihilated by A. For the total prefix S of the three
stages in the induced order,

```text
A S = 0
```

at this call. Every half of every stage satisfies the same relation: the
labels 0, 1, 2 were arbitrary.

### 5. The determinant contradicts that relation

Let x be a new central indeterminate, not one of the x_j. Whenever A S = 0
and A^2 = A,

```text
(I + x A)(I + x S) = I + x (A + S).
```

Start from S = 0 and apply the six halves in their induced order. The
product of the six factors I + x A equals I + x S_final. Each stage's
halves sum to I, so S_final = I + I + I = I and the product equals
(1 + x) I.

On the other hand each half is idempotent of rank q. Its minimal
polynomial divides t(t + 1), a product of distinct linear factors, so A is
diagonalizable over F. In an eigenbasis

```text
det(I + x A) = (1 + x)^q
```

in F[x]. Two halves per stage and three stages give

```text
det(product) = (1 + x)^{3d}.
```

The matrix (1 + x) I has determinant (1 + x)^d. These polynomials differ
for every d > 0: in characteristic 2,

```text
(1 + x)^{3d} = (1 + x^2)^d (1 + x)^d,
```

and (1 + x^2)^d = 1 only for d = 0. This contradiction does not depend on
q, on B, or on the gap that contains Z.

The same comparison is the one-sided argument of PR #5673, applied to the
single matrix K. The step that is not in that argument is section 1: one
constant thin map is forced to be K, so the three leaf columns agree.

## The published rank floor sees the same gap

`research/coupled31-chronology/PROOF.md` proves, under these paired
hypotheses, that a successful word has thin-rank sum at least

```text
2d + 2 ceil((g - 2) / 3) = 4q + 2.
```

Section 1 forces the single thin map to be K, of rank 4q. The inequality
4q < 4q + 2 is the same obstruction, read off the floor. The determinant
argument above does not rely on the induction that proves the floor.

## Corollary, still inside the star contract

The same chain applies to every g ≥ 3 and every block dimension d > 0, for
an arbitrary orthogonal resolution of each E_j rather than only a legal
pair. Evaluating at all D_j = 1 still forces the single thin map to be
K = I + sum_j T_j, because the queries on stage j still sum to T_j. Every
leaf column of that K is I in the core and 0 on the leaves, so any three
leaves have identical columns.

On those three leaves the block calculation is unchanged. A full call of a
stage other than the selected stage and the selected column has a zero
column there, so it does not appear in S_jk. The determinant product uses
only the induced order of the three selected stages, whose projections
resolve I three times. The polynomials (1 + x)^{3d} and (1 + x)^d still
differ.

Thus one constant thin map is impossible for every g ≥ 3. At g = 4 the only
positive count below ceil(g/2) = 2 is one map, so an interleaved schedule
does not beat the adjacent count there either. At g = 2 the obstruction
does not start: there are not three leaves, and the word in COMMUTING.md
meets the endpoint with one thin map.

This corollary is the same identity on a subset of leaves. It is not a
statement about five thin maps, and it is not a statement about g = 13 or
g = 31.

## What the registered checker locks

`verify.py` is not a search. It checks the following, and raises unless
they hold.

- The selected record is still κ = 781451/250000000.
- For g in {3, 4, 5} and q in {1, 2, 8}, the matrix K has rank 2d and
  identical leaf columns of the shape above. A matrix with one flipped
  entry is rejected.
- For q = 1 and q = 2, with a nonzero B whose stage projectors do not
  commute, the summed commutator row equals A(M_core + M_leaf) on probes,
  on K, and on the other stage queries. On K that block equals A for both
  foreign leaves.
- det(I + x A) = (1 + x)^q for both halves at q = 1 and q = 2, by the
  full permutation expansion in characteristic 2 (2 terms at q = 1, 24
  terms at q = 2). The bitmasks (1 + x)^{3d} and (1 + x)^d differ for
  d in {2, 4, 16, 52}.
- If A S = 0, the two-factor telescope holds on an explicit pair. One
  complementary stage multiplies to (1 + x) I; the scalar (1 + x)^3 is not
  1 + x.
- The adjacent two-map word equals the endpoint as a polynomial, for
  (g, q) in {(2, 1), (3, 1), (3, 2)}, both with B = 0 and with the nonzero
  exchange B. Deleting one of the g = 3 maps misses the endpoint.
- The forced matrix K misses the endpoint on all seven gaps of the adjacent
  g = 3, q = 1 schedule, for both choices of B, and on one interleaved
  order at q = 1 and at q = 2. Those words are controls. They are not the
  set of all orders.
- At the point D = (1, 1, 1), the adjacent word with Z = K matches and the
  word with Z = 0 does not.

The general identity is the argument above. The finite words are there so
a wrong gate formula cannot hide inside the writeup.

## What this does not say

- It does not change κ. It does not price a caller, a tape, or a native lift.
- It does not bound two or more thin maps, except by importing the known
  two-map word as a matching upper bound at g = 3. The F_2 rank-8 census,
  the three-map F_2 word, and the partial F_4 and F_8 records stay where
  they are.
- It does not decide an interleaved word with five thin maps at g = 13 or
  g = 31. One map is a different count.
- A thin factor whose matrix depends on the D_j is outside the contract.
  The evaluation step uses that Z is constant.
- The g ≥ 3 corollary is still the star contract: orthogonal resolutions,
  the query R = P T, constant thin maps, and this endpoint. It is not an
  unrestricted nonexistence theorem.
