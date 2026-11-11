# An irreducible no-edge image of dimension 7 at pattern dimension 5

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The fiber lemma is cited and not reproved. Everything else is proved here.

This is a written existence proof for one explicit pool. It is not a new κ.
The selected frontier stays `363005817/100000000000`. It is not an upper
bound on every pattern-dimension-5 pool, and it is not a census of those
pools. The 127-vector scan in `verify.py` checks this one image; it does
not search pattern spaces.

## 1. Statement

Work over F2. For a matrix N, write off(N) for N with its diagonal deleted.
For ambient width W, let P be a linear space of zero-diagonal W×W matrices
containing no matrix unit. The complete no-edge pool is

```text
C(P) = {x y^T : y·x = 1, off(x y^T) is a nonzero element of P}.
```

Every element is a rank-one idempotent. Coordinate projectors have zero
pattern, so they are not in C(P). Write V(P) for the span of the images of
C(P). The action is reducible when some subspace 0 < U < V(P) is invariant
under every pool projector.

**Theorem.** For every W ≥ 7 there is a 5-dimensional unit-free pattern
space whose complete pool has seven projectors, joint image of dimension 7,
and irreducible action.

Explicitly, on coordinates {0,1,2}, {3,4,5} and {6},

```text
(e0+e2)(e1+e2)^T,
(e1+e2)(e0+e2)^T,
(e0+e1+e2)(e0+e1+e2)^T,
(e3+e5)(e4+e5)^T,
(e4+e5)(e3+e5)^T,
(e3+e4+e5)(e3+e4+e5)^T,
(e2+e5+e6)(e2+e5+e6)^T.
```

Let z = e2+e5+e6 and let P be the span of the seven off-diagonal patterns,
padded by zero rows and columns when W > 7. Then C(P) is exactly these
seven projectors, dim V(P) = 7, and the action on V(P) is irreducible.

In particular, a complete no-edge pool of pattern dimension 5 need not have
total joint image at most 6, and its irreducible image can have dimension 7.
Both answers use this one pool. The argument uses completeness, the absence
of matrix units, and pattern dimension exactly 5 for this P. It does not
bound any other pattern space, and it does not price a word.

## 2. The seven patterns

Write A = {0,1,2} and B = {3,4,5}. The first three projectors are the
normal-form triple on A. Put

```text
u = e1+e2,  v = e0+e2,  o = e0+e1+e2.
```

Then v·u = 1 and o·o = 1, so u v^T, v u^T and o o^T are rank-one
idempotents. Their off-diagonal patterns are

```text
p_u = E10 + E12 + E20,
p_v = E01 + E02 + E21,
p_o = E01 + E02 + E10 + E12 + E20 + E21.
```

These have weights 3, 3 and 6. The first two are disjoint and their sum is
the third, so they are the three nonzero elements of a 2-dimensional space
Q_A supported on the off-diagonal positions of A. The same formulas shifted
by 3 give a 2-dimensional space Q_B on block B, with weights 3, 3 and 6.
The two blocks use disjoint positions, so H = Q_A ⊕ Q_B is 4-dimensional.

The seventh pattern comes from z = e2+e5+e6. This vector has weight 3, so
z·z = 1 and z z^T is a rank-one idempotent. Its off-diagonal pattern is

```text
p_* = E25 + E26 + E52 + E56 + E62 + E65.
```

It has weight 6. None of its six positions lies in an off-diagonal A-block
or B-block: each position meets coordinate 6 or crosses from A to B. Thus
p_* is outside H. Let P = H ⊕ span(p_*). Then dim P = 5.

A general element is q_A + q_B + λ p_* with q_A in Q_A, q_B in Q_B and
λ in F2. If λ = 0 and the element is nonzero, its weight is the sum of a
weight in {0,3,6} from each block, not both zero, hence at least 3. If
λ = 1, all six positions of p_* survive, because neither block meets them,
so the weight is at least 6. Every nonzero element has weight at least 3.
In particular P contains no matrix unit.

## 3. Support

Let x y^T be a pool element, so y·x = 1 and the pattern p = off(x y^T) lies
in P and is nonzero. Call p even when λ = 0 and odd when λ = 1.

Every matrix in P is zero in every row and every column indexed by
t ≥ 7. If x_t = 1, then y_j = p_tj = 0 for all j ≠ t, so y = e_t and
y·x = 1 forces y_t = 1. The pattern is then the off-diagonal part of row t,
which is zero, contradicting membership in the pool. Thus x_t = 0. If
y_t = 1, column t of the pattern is x with bit t cleared, hence x = e_t.
Combined with x_t = 0 this gives x = 0, which is impossible. Thus y_t = 0.
Both factors are supported on {0,1,2,3,4,5,6}.

The same reading applies to coordinate 6 when p is even: an even pattern
has zero row 6 and zero column 6, so x_6 = y_6 = 0 by the same two
sentences. An even pattern also has no cross entry between A and B.

## 4. The odd coset

Every odd pattern has λ = 1, so it contains all six positions of p_*. Those
entries are x_i y_j. Therefore

```text
x2 y6 = x6 y2 = x5 y6 = x6 y5 = x2 y5 = x5 y2 = 1,
```

and x_i y_6 = 0 for every i outside {2,5,6}, because every matrix in P has
zero column 6 outside rows 2 and 5. The first family gives
x2 = x5 = x6 = y2 = y5 = y6 = 1. The second gives x_i = 0 outside
{2,5,6}. Thus x = z. Row 6 of an odd pattern is zero outside columns 2 and
5, and x6 = 1, so y_j = 0 outside {2,5,6}. Thus y = z.

The projector is z z^T. Its pattern is exactly p_*, whose blocks inside A
and inside B are zero. An odd pattern with a nonzero block summand is
therefore not the pattern of this projector. It has no other candidate,
because the six entries already force the factors. The only odd pool element
is z z^T.

## 5. The even coset

Let p = q_A + q_B be even and nonzero, and let x y^T realize it. Section 3
puts both factors on A ∪ B, with no cross entry: x_a y_b = 0 and
x_b y_a = 0 for all a in A and b in B.

The internal A-pattern is the restriction of x y^T. If it is nonzero, some
x_a = y_a' = 1, so both the A-part of x and the A-part of y are nonzero.
From x_a = 1 and the cross equations, every B-bit of y is zero. From
y_a' = 1, every B-bit of x is zero. The internal B-pattern is then zero.
The symmetric argument says that a nonzero B-pattern forces the A-pattern
to vanish. A pattern with both blocks nonzero is unrealized.

So p lies in Q_A or in Q_B. Consider Q_A. Its three nonzero elements are
p_u, p_v and p_o, of weights 3, 3 and 6, and the three displayed projectors
realize them. None is a matrix unit. By the fiber lemma of #5921, a
realizable nonzero off-diagonal pattern that is not a matrix unit has
exactly one rank-one idempotent lift. Those three lifts are the first three
projectors, and the same holds for Q_B. There is no further even pool
element.

## 6. The pool and the image

Sections 4 and 5 account for every nonzero pattern in P. For every W ≥ 7,

```text
C(P) = the seven projectors in Section 1.
```

The first three images are u, v and o. Then u+o = e0, v+o = e1 and
u+v+o = e2, so they span the coordinate space L = span(e0,e1,e2). The next
three span R = span(e3,e4,e5) by the same sums. These two coordinate spaces
meet only at zero, and z is not in L ⊕ R because of e6. Therefore

```text
V(P) = L ⊕ R ⊕ span(e6),    dim V(P) = 7.
```

Section 7 shows that the block covectors span L* ⊕ R* and that ζ is nonzero
on e6, so the seven covectors span the dual of V(P). The common kernel is
zero. That is not yet irreducibility.

## 7. Irreducibility

Identify V(P) with F2^7 on the ordered coordinates
(e0,e1,e2,e3,e4,e5,e6). Write a vector as ℓ + r + γ e6 with ℓ in L and
r in R. The linking covector is ζ = e2* + e5* + e6*, so

```text
ζ(ℓ + r + γ e6) = ℓ2 + r5 + γ.
```

The three block-A covectors, in coordinates (e0,e1,e2), are the rows

```text
0 1 1
1 0 1
1 1 1.
```

Adding row 0 to row 1 produces (1,1,0); adding that to row 2 produces
(0,0,1); back-substitution produces the identity. They are a basis of L*.
The block-B covectors are the same matrix on (e3,e4,e5), hence a basis of
R*. Each block image meets z in one coordinate: u, v and o each meet z in
e2, and each B-image meets z in e5. Therefore ζ is 1 on all six block
images. The block covectors are the swapped copies u*, v*, o* and their
translates, so each block covector is likewise 1 on z. Also ζ(z) = 1.

Let U be a nonzero invariant subspace.

If some w in U has ζ(w) = 1, the linking projector sends w to z, so z is in
U. Every block covector is 1 on z, so every block projector sends z to its
image, and all six images lie in U. The three A-images span L and the three
B-images span R, so L ⊕ R is contained in U. Then e2 and e5 lie in U, and
z + e2 + e5 = e6 lies in U. Hence U = V(P).

If instead ζ vanishes on every vector of U, none of the six block images can
lie in U, because ζ is 1 on each of them. An invariant subspace that does not
contain a block image cannot be hit by that block's covector. All three
A-covectors therefore vanish on U. They span L*, so the L-component of every
vector in U is zero. The same holds for R. The relation ζ = 0 then forces the
e6-coordinate to vanish as well. Thus U = 0, contradicting the choice of U.

Every nonzero invariant subspace equals V(P). The action is irreducible.

Deleting the linking projector leaves the first six. Their covectors vanish
on the opposite block, and each block's projectors map into that block, so
L is a proper nonzero invariant subspace. The link is what makes the
seven-projector action irreducible. A single normal-form block is already
reducible for the same reason; the verifier uses the deleted pool, rather
than that smaller block, as the control.

## 8. The parity construction does not decide the question

The question asks about the parity construction one dimension above the
pattern-dimension-4 example. That construction is the even-weight column,
and it stays at total image 6.

Let S be the even-weight subspace of the coordinate space on {1,2,3,4,5,6}.
It is the kernel of the all-ones functional, so dim S = 5, and every nonzero
vector of S has weight at least 2. Let P_even be the 5-dimensional space of
matrices s e0^T with s in S. A nonzero element has weight at least 2, so
P_even contains no matrix unit.

A pool element x y^T has its only possible nonzero column in column 0. If
y_t = 1 for some t ≠ 0, column t of the pattern is zero, so x = e_t, and
column 0 is then 0 or e_t. The pattern is 0 or the matrix unit E_t0. Neither
lies in the pool. Thus y = e0 and x_0 = 1. The pattern is the vector x + e0
placed in column 0, so x = e0 + s for some nonzero s in S. These 31
projectors are exactly the pool, at every width at least 7. Their images
are e0 + s. Differences span S, and e0 is outside S, so the image has
dimension 6. Every covector is e0. The space S lies in the image and is
orthogonal to e0, so every projector sends S to 0. Thus S is a proper
nonzero invariant subspace. The parity pool is reducible and has total
image 6.

It therefore does not show that the total image can exceed 6, and it does
not show that an irreducible image can exceed 5. Section 1 is the pool that
decides both questions.

## 9. What this does not claim

The selected κ and its framework assumptions are unchanged. No rational
address, native word, supplier admission, or multiplication identity is
produced.

The theorem does not say that every complete no-edge pool of pattern
dimension 5 has joint image at most 7, and it does not say that 7 is the
only irreducible dimension above 5. The edge-quotient bound of #6782, in
the zero-edge case, still gives only dim V ≤ 2^5 − 1 = 31. A search through
one family of extensions is not a substitute for that upper bound, and none
is claimed here.

The 127 nonzero vectors of this image form a finite set. The verifier
closes every one under the seven projectors and finds that each closure is
all of V(P). That census matches Section 7; it is not a search over pattern
spaces. The width scans certify this pool and the parity pool only.

Question 2 of #7139, the coordinate classification of the dimension-6 pools
at pattern dimension 4, is not this result. Question 3 of #7139, paid-rank
accounting after a relation split, remains question 1 of #6921 and is not
answered here. The original card still asks for a new register alphabet;
that gate is unmet.

## Open next questions

1. **Is 7 an upper bound?** Does every complete no-edge pool of pattern
   dimension 5 have total joint image at most 7? The witness shows that 6
   is too small, and the zero-edge quotient bound is still 31. The missing
   step is to show that a unit-free one-dimensional extension of a
   dimension-6 pattern space adds at most one image dimension. This package
   does not prove that estimate.

2. **Is the dimension-7 pool unique up to coordinates?** Is every
   irreducible complete no-edge pool of pattern dimension 5 and joint-image
   dimension 7 a coordinate permutation of the seven projectors in Section
   1? The existence proof does not identify the pools. The first step is to
   match the two normal-form blocks and the linking vector. Nothing in
   Section 7 classifies other links.
