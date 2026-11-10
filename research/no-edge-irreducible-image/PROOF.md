# Irreducible joint image of a no-edge pattern pool

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. This is a written, all-width linear-algebra proof, accompanied by
finite exact checks. **No new κ.** The selected frontier stays
`781451/250000000`.

## 1. Statement

Work over the field F2. For a matrix N, write off(N) for the matrix obtained
by deleting its diagonal. Let P be a linear space of zero-diagonal W-by-W
matrices, and define the complete noncoordinate pool

    C(P) = {N = x y^T : y^T x = 1, off(N) in P, off(N) != 0}.

The condition y^T x = 1 makes N a rank-one idempotent. Put

    V(P) = sum_{N in C(P)} im(N),

and let e(P) be the number of matrix units E_ab, a != b, contained in P.
Coordinate projectors E_aa are excluded. The pool acts on V = V(P). A subspace
W ⊆ V is invariant when N(W) ⊆ W for every N in C(P). The action is
**reducible** when some subspace 0 < W < V is invariant, and **irreducible**
otherwise. Equivalently, the common kernel of all covectors is invariant, a
line spanned by one image is invariant when every other covector kills that
image, and a hyperplane ker(φ) ∩ V is invariant when every pool image except
the image belonging to φ lies in the hyperplane and φ itself kills the
hyperplane.

**Theorem.** If dim P ≤ 3 and e(P) = 0, then either dim V(P) ≤ 3, or
dim V(P) = 4 and the action on V(P) is reducible. The bound 3 is sharp: for
every ambient width there is a complete no-edge pool, with three-dimensional
pattern space, whose joint image is three-dimensional and irreducible.

The total-image bound dim V ≤ 4 is Theorem 1 of #6838. It is cited as a
finished input and is not reproved. The new statement is the irreducible
bound. #6838's attaining four-dimensional pool is reducible, and #6838 left
open whether an irreducible four-dimensional example exists. This note answers
that question: it does not, and 3 is sharp.

## 2. Inherited ingredients

**Fiber lemma (#5921).** A realized nonzero off-diagonal pattern has exactly
one binary rank-one idempotent lift, except a matrix unit E_ab, which has the
two lifts e_a(e_a+e_b)^T and (e_a+e_b)e_b^T. In particular, when e(P) = 0,
distinct pool projectors have distinct nonzero patterns. The short proof is
recorded in #5921 and again in #6838; it is not repeated here.

**Total-image bound (#6838).** If dim P ≤ 3 and e(P) = 0, then dim V(P) ≤ 4.
The same bound holds for the span of the covectors. The proof is the
five-point argument: five independent images would force two pattern triples
sharing one pattern, and the shared projector would be coordinate.

**Five-point lemma (#6838, Lemma 4).** Any five distinct nonzero vectors of
F2^3 contain two three-element zero-sum subsets meeting in exactly one
element. Any six or seven nonzero vectors therefore contain a three-element
zero-sum as well. A four-point set with no three-element zero-sum is the
complement of a line; there are exactly seven such sets, one for each line.
Each is the set of nonzero vectors of F2^3 outside a two-dimensional subspace,
and the sum of its four vectors is zero. The verifier enumerates all
four-point subsets.

A zero-sum of patterns makes the corresponding sum of projectors diagonal,
because the off-diagonal parts cancel. Over F2 every diagonal matrix D
satisfies D^2 = D.

## 3. Independent triples

Throughout this section, N_i = x_i y_i^T for i = 1, 2, 3, the images
x_1, x_2, x_3 are linearly independent, each y_i · x_i = 1, and
N_1+N_2+N_3 is diagonal. Write U for the three-dimensional span of the
images and X for the isomorphism F2^3 → U sending the standard basis vector
ε_i to x_i.

**Support lemma.** For each ambient coordinate b, let m(b) in F2^3 be the
vector with m(b)_i = y_i(b). The b-th column of the diagonal sum is
X m(b), so X m(b) is either 0 or e_b. Injectivity of X forces m(b) = 0
whenever e_b is not in U. Whenever e_b is in U, m(b) is either 0 or the
unique vector μ(b) = X^{-1} e_b. The coordinates b with m(b) ≠ 0 therefore
form a set A, the corresponding basis vectors e_b are independent, and

    y_i = sum_{b in A} μ(b)_i e_b,        |A| ≤ 3.

**Parity.** Summing the diagonal pairings gives

    sum_i y_i · x_i = sum_b e_b · (X m(b)) = |A|  (mod 2),

since the b-term equals 1 exactly for b in A. Idempotence makes each summand
1, and 1+1+1 = 1, so |A| is odd. Thus |A| is 1 or 3. The empty set would make
every covector zero.

**The case |A| = 1.** Some coordinate, which we call 0, has μ(0) with all
three components equal to 1; otherwise one covector would vanish. Every
covector equals e_0, and every image has bit 0. The three off-diagonal
patterns lie in column 0. Their column vectors a, b, a+b are nonzero,
sum to zero, and each has weight at least 2: a weight-1 column would be a
matrix unit, and a zero column would be a coordinate projector. The pattern
span is {u e_0^T : u in T} for T = span(a, b). Every nonzero vector of T has
weight at least 2. This is the **column triple** below.

**The case |A| = 3.** The three basis vectors e_b lie in U, so after renaming
coordinates U is the coordinate space on {0, 1, 2}. The matrix X, with those
images as columns, lies in GL(3, 2), and the coordinate matrix of the three
covectors is X^{-1}. The sum of the three projectors is X X^{-1} = I on U, so
the three patterns sum to zero.

**Normal-form classification.** Let x_1, x_2, x_3 be the columns of a matrix
in GL(3, 2) and let y_1, y_2, y_3 be the rows of the inverse. The pattern of
x y^T has weight wt(x) wt(y) − d, where d is the number of coordinates at
which both vectors are 1. The pairing y · x = 1 forces d odd. No-edge
requires each of the three pattern weights to be at least 2. The verifier
enumerates all 168 elements of GL(3, 2). Exactly 18 matrices meet the bound,
every one of them has column weights 2, 2 and 3, and the covectors are the
dual basis described next. In particular the enumeration is what excludes a
weight-1 column; the rest of the identification is by hand.

F2^3 has a unique weight-3 vector o and exactly three weight-2 vectors, and
those three sum to zero, so they are dependent. An invertible matrix therefore
cannot have three weight-2 columns. Combined with the enumeration, every
survivor has columns o and two distinct weight-2 vectors.

The dual basis of any such triple is forced, and it meets the weight bound.
Any two distinct weight-2 vectors p and q pair to 1, each pairs to 0 with o,
and o pairs to 1 with itself. Hence the covector of p is q, the covector of
q is p, and the covector of o is o. Each weight-2 pattern then has weight
2·2 − 1 = 3, and the weight-3 pattern has weight 3·3 − 3 = 6. All three are
at least 2, they sum to zero, and none is zero, so they are the three nonzero
vectors of a two-dimensional pattern space with no matrix unit. There are 3
choices for which column is o and 3·2 choices for the ordered pair of
weight-2 columns, hence exactly these 18 matrices. A coordinate permutation
identifies every such triple with

    u = e_1+e_2,    v = e_0+e_2,    o = e_0+e_1+e_2,

    N_u = u v^T,    N_v = v u^T,    N_o = o o^T.

Call this the **normal-form triple**. Its pattern space Q is two-dimensional
and contains no matrix unit. The three covectors are a basis of the dual of
U = span(e_0, e_1, e_2).

**Summary.** An independent-image zero-sum triple in a no-edge pool is either
a column triple or a normal-form triple.

## 4. Pools with no independent triple

Let S be the set of realized patterns, viewed as nonzero vectors of a
three-dimensional coordinate space for P. If dim P ≤ 2, then |S| ≤ 3 and
dim V ≤ 3. Assume dim P = 3.

A three-element zero-sum in S is a **line**. If some line has
three-dimensional image span, Section 3 supplies a column triple or a
normal-form triple; those pools are treated in Sections 6 and 7. This section
handles pools in which every line has image span at most 2, and the separate
four-pattern cap.

**Four patterns and no line.** Such a set is one of the seven four-point
complements of a line, so its vectors sum to zero and no three sum to zero.
The four projectors therefore have diagonal sum D. If dim V ≤ 3 there is
nothing to prove. If dim V = 4, the four images are a basis of V. In that
basis the matrix G of D has entries G_ki = y_k · x_i and satisfies G^2 = G,
because D^2 = D. The diagonal entries are 1. A rank-4 idempotent endomorphism
is the identity, since an idempotent acts as the identity on its image. Thus
either rank G < 4, in which case the covectors have a nonzero common kernel,
or G = I. In the identity case y_k · x_i = δ_ki, so each line span(x_i) is
invariant: the i-th projector maps into that line and every other projector
kills x_i. Either way the action is reducible.

**Five or more patterns, every line of image rank at most 2.** At least one
line exists. For five patterns, the five-point lemma supplies two lines
covering all five patterns and meeting in one pattern. The two image planes
both contain that shared nonzero image, so their sum has dimension at most
2+2−1 = 3.

For six or seven patterns, suppose the images span a four-dimensional space.
Four independent images cannot contain a line, so their four patterns form a
cap, and the omitted point of a six-pattern set lies on the complementary
line. Label the cap

    c_1 = e_1,  c_2 = e_2,  c_3 = e_3,  c_4 = e_1+e_2+e_3

with independent images f_1, f_2, f_3, f_4, and label the complementary line

    m_12 = e_1+e_2,  m_13 = e_1+e_3,  m_23 = e_2+e_3.

If seven patterns are realized, the line through c_1, c_2, m_12 forces the
image of m_12 into span(f_1, f_2). The line through c_4, m_12, c_3 is the
triple {c_4, m_12, c_3}, so that same image also lies in span(f_4, f_3). The
two planes meet only at zero, so the image is zero, which is impossible. If
only six patterns are realized, the omitted pattern is one of the three
points on the complementary line. The two lines above avoid m_13 and m_23.
Omitting m_12 instead is the same configuration after swapping the labels of
c_1, c_2 with c_3, c_4, which preserves the cap and the independence of the
four images. In every case one remaining complement image is forced into two
planes that meet only at zero. This contradiction shows dim V ≤ 3.

## 5. Column triples inside a four-dimensional image

Let a column triple sit in C(P), with common covector e_0 and pattern space

    Q = {u e_0^T : u in T},

where T is a two-dimensional space of vectors supported off coordinate 0 and
T contains no weight-1 vector. The three images span the three-dimensional
space span(e_0) + T. The pool's pattern space has dimension at most 3. If it
equals Q, there are no further projectors and dim V = 3. For a
four-dimensional joint image, P = Q ⊕ span(ρ) for some pattern ρ outside Q,
and e(P) = 0.

Every pattern in the coset ρ+Q has the same entries outside column 0, because
elements of Q touch only column 0. If those shared entries are all zero, every
pattern in P is a single column-0 matrix. No such matrix is a matrix unit, so
each has a unique lift, necessarily of the form (e_0+w) e_0^T. Every covector
equals e_0 and the common kernel has codimension 1. The action is reducible.

Now suppose some column b ≠ 0 of ρ is nonzero. Call its off-diagonal part c.
Every projector in the odd coset has off-diagonal column b equal to c. For
N = x y^T that means y(b) = 1 and x(a) = c_a for every a ≠ b. All odd
projectors therefore share every image bit except possibly bit b: there are
at most two possible odd images.

For each coordinate c ≠ 0 the off-diagonal column c of an odd pattern is
independent of the Q-component, hence is the same for every odd projector.
If a candidate image is nonzero off coordinate c, the shared column forces a
single value of y(c). Thus y(c) can vary only when every candidate image that
actually occurs is supported at c alone. Column b is nonzero, so the pinned
part of each candidate is nonzero, and a nonzero vector is supported at one
coordinate for at most one choice of c. Bit b itself is already fixed:
y(b) = 1. The only remaining free bit is coordinate 0, whose column varies
inside the coset of T. Every odd covector therefore lies in one coset of a
coordinate space of dimension at most 2, whether one candidate image occurs
or both. Those covectors span at most three dimensions. The column triple
contributes only e_0, which is already in that span. On a four-dimensional
image the covectors have a nonzero common kernel, and that kernel is
invariant. The action is reducible.

Even projectors realize patterns in Q, so by the fiber lemma they are the
original three and contribute only e_0.

## 6. Normal-form triples inside a four-dimensional image

Let a normal-form triple sit in C(P), with pattern space Q as in Section 3.
Its images span the coordinate space U on {0, 1, 2}. If P = Q, then
dim V = 3. For dim V = 4 one has P = Q ⊕ span(ρ) with e(P) = 0, and every
image lies in a space V = U ⊕ span(z) for a single nonzero vector z supported
off {0, 1, 2}. Write S for the support of z. Patterns in Q are supported
inside the coordinate block U. Patterns in the odd coset ρ+Q all share the
same entries outside that block.

Write an odd projector as N = x y^T with x = x_U + β z, β in {0, 1}, and
write η for the restriction of y to U. For each coordinate t in S, the shared
outside blocks give the rank-one identities

    (row t inside U) = x(t) η,      (column t inside U) = y(t) x_U.

A projector with β = 1 has x(t) = 1 for every t in S, so every such projector
has the same inside covector η, and the shared row block equals η. In
particular η is independent of which β = 1 projector is under discussion. If
no β = 1 projector exists, every image lies in U and dim V ≤ 3. Assume one
exists. Idempotence reads η · x_U + y · z = 1.

**Vanishing inside covector.** Suppose η = 0. Idempotence forces y · z = 1.
On V, every such covector is the functional ψ which vanishes on U and takes
the value 1 on z; extra coordinates off V do not change the action on V. This
functional kills every image in U, including the normal-form images and every
odd image with β = 0. Every β = 1 image pairs with it to 1, and the column
identity makes those images share a single inside part, so they determine one
line of V not contained in U. The hyperplane H = ker(ψ) ∩ V = U is invariant:
the normal-form projectors preserve U, every β = 0 image lies in U, and every
β = 1 projector has covector ψ and therefore kills U. The action is reducible.

**Nonzero inside covector, every odd covector kills z.** Then η ≠ 0 and every
odd projector has y · z = 0. The normal-form covectors are supported on U, so
they kill z as well. The line span(z) lies in the common kernel. The action
is reducible.

**Nonzero inside covector, and y · z = 1 for some odd projector.** Idempotence
gives η · x_U = 0. Some t in S has y(t) = 1, so the shared column at t pins
x_U. Every odd projector with y · z = 1 has this same image vector
x = x_U + z and the same action on V.

If η ≠ 0, a β = 0 odd projector would have zero outside rows, hence could
exist only for η = 0. Thus every odd image is of the form above, except in
the one-coordinate situation treated at the end of this section. For the
generic situation, consider the three normal-form covectors φ in {v, u, o}.
Each kills z. If any one of them kills x_U, it kills the odd image. That
covector is dual to one normal-form image and kills the other two, so its
hyperplane meets V in an invariant subspace of dimension 3: the projector
belonging to the covector kills the hyperplane, and every other pool image
lies in the hyperplane. The action is reducible.

If none of the three kills x_U, then each pairs to 1 with x_U. The three
covectors are a basis of the dual of U, so there is exactly one such vector,
namely the sum ξ of the three normal-form images. The inside part of the odd
covector satisfies η · ξ = 0. The three normal-form images form a basis of U,
so the pairings of η against them cannot all be 1: that would give
η · ξ = 1. Some normal-form image x_* is therefore killed by η, hence by the
odd covector. The other two normal-form covectors kill x_* as well, because
the gram matrix of the triple is the identity. The line span(x_*) is
invariant. The action is reducible.

**One outside coordinate, mixed parities.** The only configuration not covered
by the two preceding paragraphs is |S| = 1, where the outside block does not
by itself force every odd projector to share the bit y(t). Let z = e_t. The
shared column says that a projector with y(t) = 0 contributes the zero column,
while a projector with y(t) = 1 contributes its inside image. For both to
occur when η ≠ 0, the pinned inside image is zero. Odd projectors then have
one of the two shapes

    x = e_t,            y|V = η + ψ,
    x = x_E + e_t,      y|V = η,       η · x_E = 1,

where ψ(e_t) = 1 and ψ vanishes on U. Every covector in this list kills e_t
except the projectors of the first shape, and those have image e_t. The
normal-form covectors kill e_t. The line span(e_t) is invariant.

If only the first shape occurs, then x_U = 0, so every normal-form covector
kills the odd image and the earlier hyperplane argument applies. If only the
second shape occurs, every odd covector kills e_t and the line is again the
common kernel. The action is reducible in every subcase.

## 7. Assembly

Assume dim P ≤ 3 and e(P) = 0. By the #6838 bound, dim V ≤ 4. If
dim V ≤ 3, the stated alternative holds. Suppose dim V = 4.

If S contains no line, then |S| ≤ 4. The case |S| ≤ 3 cannot span a
four-dimensional space. The case |S| = 4 with no line is the cap in Section
4, which is reducible. If every line has image rank at most 2 and |S| ≥ 5,
Section 4 gives dim V ≤ 3, a contradiction. Hence some line has
three-dimensional image span. Section 3 says that line is a column triple or
a normal-form triple. Sections 5 and 6 say that a four-dimensional pool
containing either triple is reducible.

## 8. Sharpness at dimension 3

On coordinates {0, 1, 2, 3} define

    N_0 = e_0 (e_0+e_1+e_2)^T,     pattern E_01+E_02,
    N_1 = e_1 (e_0+e_1+e_3)^T,     pattern E_10+E_13,
    N_2 = e_2 (e_0+e_2+e_3)^T,     pattern E_20+E_23.

Let P be the span of these three patterns. A general element is

    α(E_01+E_02) + β(E_10+E_13) + γ(E_20+E_23).

The six positions are distinct, so the weight is twice the number of nonzero
coefficients among α, β, γ. No nonzero element has weight 1, and the three
patterns are independent, so dim P = 3 and e(P) = 0.

Both factors of any realizable projector are supported on {0, 1, 2, 3}. Row
t ≥ 4 of every matrix in P is zero, so a factor x with x(t) = 1 forces y to
vanish off t. Column t is likewise zero, so y(t) = 1 then forces x to vanish
off t. The resulting projector is coordinate and its pattern is zero,
contradicting membership in C(P). Thus y(t) = 0 as well.

Inside {0, 1, 2, 3} the same entrywise constraints leave only the three
projectors above. Write x = (x_0, x_1, x_2, x_3) and likewise for y, with
y · x = 1. Vanishing of the three forbidden entries in row 3 forces
x_3 y_0 = x_3 y_1 = x_3 y_2 = 0. If x_3 = 1, then y = y_3 e_3, the idempotence
condition gives y_3 = 1, and the absent column-3 entry in row 0 forces
x_0 = 0. The surviving pattern is x_1 E_13 + x_2 E_23. Membership in P forces
the paired entries E_10 and E_20 to carry the same coefficients, which are
zero because y_0 = 0, so x_1 = x_2 = 0 and the pattern is zero. Hence
x_3 = 0, and then y_3 x_0 = 0 together with the three pairing identities

    x_0 y_1 = x_0 y_2,    x_1 y_0 = x_1 y_3,    x_2 y_0 = x_2 y_3,

and the two further zeros x_1 y_2 = x_2 y_1 = 0. If x_0 = 1, the idempotence
condition and those zeros force x_1 = x_2 = 0, y_0 = y_1 = y_2 = 1 and
y_3 = 0, which is N_0. If x_0 = 0 and x_1 = 1, they force x_2 = 0,
y_1 = y_0 = y_3 = 1 and y_2 = 0, which is N_1. The symmetric subcase is N_2.
The remaining subcase x_0 = x_1 = x_2 = 0 contradicts idempotence. The pool is
exactly {N_0, N_1, N_2} at every ambient width.

The images span V = span(e_0, e_1, e_2). On coordinates (a, b, c) of V,

    N_0(a, b, c) = e_0 if a+b+c = 1, else 0,
    N_1(a, b, c) = e_1 if a+b = 1, else 0,
    N_2(a, b, c) = e_2 if a+c = 1, else 0.

No line is invariant. A nonzero vector with a+b+c = 1 is sent by N_0 to e_0,
so the line would be span(e_0); but N_1(e_0) = e_1. A nonzero vector with
a+b+c = 0 that meets N_1 or N_2 is sent to e_1 or e_2, both of which have
coordinate sum 1. If it meets neither, then a+b = a+c = 0, so b = c = a, and
the sum-zero condition forces a = b = c = 0.

No plane is invariant. The four hyperplanes of the dual of F2^3 may be cut
out by a+b+c, by b, by c, and by b+c. They fail on (1, 0, 1), (1, 0, 0),
(1, 0, 0) and (0, 1, 1) respectively: each witness is sent outside the
hyperplane. The verifier repeats the subspace enumeration. The action is
therefore irreducible, and the irreducible bound 3 is attained.

The same three patterns show that the bound is specific to irreducibility.
#6838 already attains total dimension 4 with a reducible no-edge pool, the
even-parity construction recalled in the verifier as a negative control.

## 9. What this does not claim

The selected κ and its five framework assumptions are unchanged. This note
does not produce a rational-address word, a native primitive, a supplier
admission, or a multiplication identity. It does not extend the bound to
pattern dimension 4. The parity construction of #6838, moved up one
dimension, has total joint image 5 and shows that a four-dimensional pattern
space is outside the argument. Applying the bound to a concrete three-relation
word still requires the relation, cube-span, and coordinate-call hypotheses
of #6777 and #6782; those hypotheses are not reproved here.

## Open next questions

The packaged questions are the word-level accounting after a valid split, and
the irreducible bound in pattern dimension 4. Both are stated with a first
step in `TASK.json`.
