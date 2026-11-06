# Independent review: two exponent relations at arbitrary scalar width

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. This is an independent written mathematical review, not external
human review or proof-kernel verification. No second copy of the author's
finite census was run for this review.

Reviewed objects:

- `research/bit-two-relation-any-registers/PROOF.md`, Sections 1–7.
- David Govea's CrocSwap/integer-mult-bounds#720, canonical base
  `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
  `research/three-register-no-target-flag/README.md`, especially Sections 1–4.

The new theorem is precisely about binary rank-one idempotent scalar calls
over the formal group algebra of a finitely generated torsion-free exponent
group, with at most two independent integer relations and an exact diagonal
monomial endpoint. It does not concern arbitrary scalar fields, torsion
relations, address changes between calls, or finite-address coincidence.

## Review conclusion

I find the new arbitrary-width reduction valid. The common-J argument extends
to every odd core size, the two-pattern image classification is exhaustive
without an ambient-width bound, and original repeated or identity target
labels can be recovered. The exact inherited #720 lemma has the needed
torsion-free, at-most-two-relation scope; it has no frame-rank, target-rank,
invertibility, flag or target-distinctness hypothesis.

The conclusion remains a written theorem depending on that named inherited
three-register result. This review did not rerun #720's finite classification
or its unrelated address-dimension-three search. It also does not newly verify
every older low-span result cited for the historical eight-call summary.

## 1. Saturation and the cube lift

Because the finitely generated exponent group H is torsion-free, the exact
sequence from Z^k splits. Thus the mod-two linear relation space is exactly
L/2L, rather than a larger kernel created by torsion. First-order off-diagonal
coefficient vectors therefore span at most rank(L) directions.

Every universal product entry is multilinear in the individual call variables:
each call contributes either its constant matrix part or one occurrence of its
own variable. Consequently a collision between two contributing exponent
monomials has a relation vector in {-1,0,1}^k. Saturating the rational span of
all such cube relations cannot introduce a new equality between subset sums,
and removes none. If that span has rank at most one, the resulting torsion-free
lift preserves all coefficient fibers. Each endpoint monomial has at least
one subset representative, so the lifted diagonal endpoint is well defined
as well; repeated or identity target values remain consistent. The returned
disjoint subsets map back to the original exponents.

If two independent cube relations exist, the claimed saturated basis argument
is sound. Independent mod-two reductions give an odd 2-by-2 minor, necessarily
plus or minus one because its absolute value is at most two. Coincident
nonzero reductions give two integral half-sums with disjoint nonempty support
and a unit minor. Their membership in L uses saturation, equivalently
torsion-freeness of H. Since rank(L) is at most two, either basis spans all
of L integrally.

In the pattern-span-two case, a coordinate projector has zero pattern, hence
both basis-relation coefficients there are zero modulo two. Cube-valued
coefficients make them zero as integers. This proves the direct sum
H=H_S plus Z^T and justifies removing coordinate calls before applying a
noncoordinate invariant-image argument. Without this step, the claimed
common image would not in general be invariant under arbitrary coordinate
projectors.

## 2. Arbitrary odd common-J cores

A cyclic rank-one binary idempotent has an odd support intersection of size
s at least three. Its off-diagonal graph gives upper-triangular tails around
an all-ones J_s core. Coordinate projectors preserve that block order.
The diagonal endpoint outside the core is already the disjoint product of
the corresponding coordinate calls, and the core relation lattice embeds
into the original lattice by zero extension.

The following points make the degree-two argument valid rather than a
first-order heuristic:

1. The universal first-order off-diagonal expression is a multiple of the
   constant matrix `(J_s)_off`. Quotienting that matrix direction kills the
   entire first-order expression before any Laurent substitution. Therefore
   quadratic terms introduced by nonlinear substitutions into a surviving
   universal linear term cannot interfere: no such term survives.
2. The associated graded augmentation ring of F2[H] is the polynomial ring
   Sym(H/2H). After eliminating the nonzero J-sum relation L_J, at most one
   further linear relation M remains. A nonzero homogeneous quadratic that
   vanishes in the quotient is therefore divisible by M.
3. For the star matrices K_i, an equation sum(a_i K_i)=lambda J_off means
   a_i+a_j=lambda for every distinct i,j. A triangle forces lambda=0;
   then all a_i are equal. Thus the only star relation, even after this
   matrix quotient, is their total sum. This works for every s at least
   three, not just s=3.

Eliminating the last J variable leaves independent proper J-prefix forms
P_1,...,P_(h-1). Every remaining quadratic q_i+q_s is bilinear between J
variables X and coordinate-call variables Y. If a nonzero bilinear
polynomial factors into two linear forms, its pure X and pure Y degree-two
parts must vanish. Since a polynomial ring over F2 is a domain, one factor
must be purely X and the other purely Y. Its coefficient matrix has rank one.
All its nonzero columns are therefore the same prefix P_j; distinct proper
prefixes are independent and cannot lie on one binary line.

The common-divisor condition synchronizes the gap across all coordinates.
If q_s is nonzero, its own columns occur in every q_i+q_s, so their rank-one
prefix must agree. If q_s is zero, different nonzero q_i have disjoint
Y-variable supports; they cannot share a nonzero Y divisor. Their common
divisor is consequently the same X prefix. If just one quadratic is
nonzero, its own rank-one condition is enough. If all these quadratics are
identically zero before the final relation M, disjoint Y supports force all
q_i to vanish identically and there are no internal coordinate calls.

This reduces the word to U(b) D U(c) after removing exterior invertible
diagonal factors. If either b or c equals one, an off-diagonal equation
forces the other to equal one. Otherwise subtracting two columns in a third
row gives `(b-1)(d_j-d_k)=0`. The Laurent domain and s at least three force
D=dI. Since J_s is idempotent for odd s, the remaining word is d U(bc),
whose off-diagonal equations force bc=1. Its endpoint is exactly the one
obtained by deleting all J calls. No word-length or core-size enumeration
is used in this conclusion.

The phrase "all quadratics vanish" should consistently mean universal
vanishing after L_J has been eliminated and before imposing M; vanishing
modulo M alone would not imply the absence of internal coordinate calls.
The current argument uses the former meaning.

## 3. The joint-image classification is exhaustive

I checked all structural cases independently of the finite 4- and 5-register
data.

Two distinct lifts of one nonzero off-diagonal pattern differ by a nonzero
diagonal matrix of rank at most two and trace zero. It therefore has exactly
two supported diagonal entries. Rank equality forces both images and both
covectors into those two coordinates. The binary 2-by-2 rank-one idempotents
give exactly the two stated lifts of a single edge; other realized nonzero
patterns have one lift.

A two-dimensional pattern plane has only three nonzero elements. With no
edge ambiguity there are at most three projectors, giving image dimension
at most three. With exactly one edge and all three patterns realized,
write the other lifts as M,N and M+N=E_ab+D. Rank subadditivity bounds the
diagonal support of D by three, and trace parity makes it zero or two.

- If D=0 and the two image vectors are independent, rank(M+N)=1 forces
  their covectors equal and their image sum to e_a. Adding e_a,e_b thus
  still spans at most three dimensions. Dependent images are easier.
- If D has support {c,d}, disjointness from {a,b} would produce three
  independent columns, contrary to rank at most two. Its principal
  {c,d} minor has determinant one, so rank(M+N)=2 and its image equals
  the joint image of M,N. All image vectors then lie in the union of
  at most three coordinate positions.

With two edges and their sum realized, the latter has only two off-diagonal
entries. Its support intersection cannot have cyclic size at least three,
which would already create six edges. For intersection size one, the tail
sizes satisfy a+b+ab=2, forcing (2,0) or (0,2). Thus the two edges share a
row or a column and all lifts are supported on three coordinates.

If only two edge patterns are realized, their four lifts span their
endpoints. The only image-dimension-four case has four distinct endpoints.
Those disjoint edges are simultaneously coordinate upper triangular, and
their sum is unrealizable by the preceding two-edge count. This proves the
claimed exception and rules out an unexamined high-width case. The sharp
pool span(E_01,E_23) also prevents incorrectly strengthening the bound to
three without the triangular exception.

## 4. Independent target-label argument

The author's invariant-eigenspace decomposition is valid: monomial
independence applied to a constant vector in V separates each distinct
target exponent's coordinate projection. Repeated target values require
grouping equal monomials, which the proof does.

There is a stronger direct argument in this setting. Because every N_j has
image in V, a telescoping product identity gives

    (D-I)(F2^W tensor R) contained in V tensor R.

For original target label i with projected exponent h_i not zero,
`(D-I)e_i=([h_i]-1)e_i`. Its image in the constant-vector quotient by V
can vanish only if e_i lies in V: apply a binary linear functional nonzero
on that quotient vector and use `[h_i]-1 != 0`. Consequently every original
nonzero-target coordinate axis lies in V, and

    V = span{e_i: h_i != 0} direct-sum (V intersect E_0).

Choose those original nonzero target axes themselves in the restricted
basis, followed by a basis of the zero-target intersection. This retains
every nonzero target label directly, even when its exponent is repeated.
All quotient target labels have zero exponent. Each restricted projector
is still rank one and idempotent because its nonzero image vector lies in
V and is fixed. Applying the inherited three-register lemma is therefore
legitimate after padding if necessary. Any subsets assigned to artificial
zero-target basis vectors can simply be discarded; their sums are zero.

Finally, projecting onto a free coordinate-call generator leaves only its
original coordinate projector. Formal monomial equality assigns that
generator to exactly its original target label with coefficient one,
and coefficient zero to all others. Reattaching these calls preserves
disjointness and reconstructs the full exponent by the exact direct sum.
No free scalar-basis transformation has been asserted as a physical gate.

## 5. Quantifiers and consequences

Every argument above is independent of W and k. The only finite width used
as an inherited mathematical theorem is at most three, reached by an
analytic image reduction. The disjoint-edge exception is solved directly
by triangular diagonals rather than by the 4,964-plane census. Thus the
finite 4- and 5-register checks corroborate the new structural lemma; they
do not carry the arbitrary-width quantifier.

For rational matrix exponents the group map is additive over the rationals,
while scalar projectors remain binary. Rational address entries are not
reduced modulo two. Disjoint subset assignment and ordinary matrix-rank
subadditivity give total target rank no larger than total paid frame rank.
In particular, three invertible 3-by-3 targets require at least nine total
rank-one calls whenever the frame-relation rank is at most two, regardless
of additional diagonal monomial helper outputs.

This proves no kappa improvement, physical supplier admission, recursive
cost model or unrestricted lower bound for three or more frame relations.
The historical remaining span-five case uses the separately cited earlier
low-span results as well as this theorem; it is not a new assertion that a
span-five construction exists.

## Author response and final proof pin

The requested distinction between universal quadratic vanishing and vanishing
modulo M is now explicit in PROOF.md. This clarifies the reviewed argument.
Final proof SHA256: `ad05bccffaf0fe11120312d8514146e5433d7032bbc65bd9d57974e06a6c3f82`.
