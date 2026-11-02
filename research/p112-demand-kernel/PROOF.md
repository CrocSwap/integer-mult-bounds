# An exact finite demand kernel

This scoped proof and finite certificate were produced by Nick Petalas.

## Fixed question and result

Use the ordered P112 roots and live vertices in Jeremy Diviney's PR1422
`GEOMETRY.json`. Its two saved layouts in `CANDIDATES.json` specify support
rectangles, not coefficient vectors. Traverse their terms in file order,
retaining the first occurrence of each ordered support pair. Then append the
eight coordinate rectangles, in punctured-frame order, again omitting exact
duplicates. There are 14 resulting rectangles `(L_k,R_k)`. Their literal
bitmasks and the eight coordinate indices are in `RESULT.json`.

For every nonempty orthogonal live-root clique Q, put

    H(Q) = {k : L_k meets Q and R_k meets Q},
    d(Q) = |Q|.

Let x be any vector of 14 nonnegative real numbers. The following systems
are equivalent:

    sum_(k in H(Q)) x_k >= d(Q), for every orthogonal clique Q;
    sum_(k in H(Q)) x_k >= d(Q), for the 280 saved witnesses Q.

The complete domain has 262,928 demands. Equal hit signatures leave 1,141
rows; pairwise dominance leaves the stated 280. Every retained row includes
its original clique witness. Every original demand has an explicit retained
dominator reconstructed by the verifier. The certificate records deterministic
hashes of the full clique, quotient and domination streams.

The all-x implication is a written elementary argument below. The numerical
instantiation is an exact finite certificate. Neither is a formal-kernel proof.

## Why these are necessary decoder demands

This is the rank-demand argument of PR1422, used as a premise and recalled
to specify the contract. The required masked decoder matrix on Q is a
nonsingular diagonal matrix, of rank |Q|. A rank-one factor supported on
`L_k x R_k` contributes zero unless both sides meet Q, and otherwise has rank
at most one. Consequently, an integer multiplicity vector for a decoder
must satisfy the first system. Independent whole-term transposes preserve
H(Q). A coefficient may vanish inside a cap; this can only strengthen the
actual-support screen beyond the cap screen studied here.

The real-valued system is a relaxation. A fractional x is not a physical
fraction of a call. The equivalence makes no claim that either system implies
the existence of coefficient vectors or a decoder.

## Equal-signature quotient

For each realized hit set H, define

    D(H) = max { |Q| : H(Q)=H }.

Choose the smallest integer root bitmask among the maximizing Q as witness.
All rows with that hit set have the same left-hand side. Their conjunction
is therefore exactly the single inequality `sum_(k in H) x_k >= D(H)`.
The maximum is over a finite nonempty class, so its witness is an actual
original demand. This proves equivalence of the complete and quotient systems.

## Nonnegative dominance

A row `(A,a)` dominates `(B,b)` when `A` is a subset of B and `a>=b`.
For nonnegative x,

    sum_(k in B) x_k >= sum_(k in A) x_k >= a >= b.

Thus the first row implies the second. This uses hit-set inclusion, not
inclusion between the vertex sets of two cliques. Vertex inclusion alone
does not compare these two sides of a rank inequality in the required direction.

The reduction orders quotient rows by decreasing demand, then increasing
hit-set size, then increasing integer hit mask. It retains a row unless
an already retained row dominates it. If one distinct row dominates another,
it occurs earlier in this order: either its demand is larger or its hit set
is strictly smaller at equal demand. Consequently a later row cannot dominate
an earlier retained one. The retained rows form a pairwise nondominated family.

Each discarded row has a retained dominator by the discard test itself.
Equivalently, the verifier reconstructs a retained dominator directly for
every quotient row. The displayed inequality proves that every retained-row
solution satisfies every quotient row. Conversely each retained row is an
original demand, so a solution of all original demands satisfies every retained
one. Together with the quotient argument this proves the asserted equivalence
for every nonnegative real x, including unbounded integer multiplicities.

This is not a minimum-cardinality or linear-program irredundancy theorem.
For example `x_1>=1`, `x_2>=1`, `x_1+x_2>=2` are pairwise nondominated but
the third follows from their sum. The verifier retains this control.

## Complete finite domain and evidence

The primary enumerator extends increasing vertex prefixes using intersections
of later-neighbor bitsets. Every extension is a clique. Every nonempty clique
has one increasing vertex list and is reached once, by induction on its length.
An independent implementation grows tuples by length and tests coordinate dot
products literally. The two complete sets must be equal. The source consists
of nonzero roots in eight dimensions, so mutually orthogonal sets have size
at most eight. Explicit node and storage budgets reject rather than truncate
a larger domain.

Every quotient maximum is computed from the complete domain. The verifier
checks the witness, hit signature and demand of each retained row, checks
pairwise nondominance, and checks the domination implication for each of the
262,928 original demands. The saved certificate is regenerated and compared
canonically. Binary multiplicities are exhausted in all 16,384 vectors, and
256 larger integer vectors give additional behavioral controls. These checks
corroborate the written all-x proof; they do not replace nonnegativity in it.

The checker also enumerates 3,456 toy multiplicity/profile pairs. Coordinate
caps give a positive control, while each coordinate omission and the two
source support layouts give negative controls. The latter are the source's
known fixtures, used to ensure the reduced screen retains their rejection;
their old costs and failure counts are not recomputed as a new deliverable.
Altered demands, false witnesses, absent dominators, negative or Boolean
multiplicities and wrong vector dimensions must reject. All checks use
explicit exceptions and remain active under optimized Python.

## Scope and credit

This answers PR1422 Open next question 2 for the specified cap alphabet.
Changing caps, adding a new rectangle or using actual trimmed supports requires
rebuilding the quotient. Repeated terms and independent whole-term transposes
are covered by multiplicities and the symmetric hit predicate. A zero-cost
rectangle cannot meet both sides of an orthogonal clique: the binary pairing
on that clique is all ones, so such a subrectangle would already have positive
pairing rank. No extra zero-cost term is silently counted as a useful hit.

Credit Jeremy Diviney for the question, complete-clique guard, geometry pin
and saved caps; Cinna Davis for PR1347/1323's support model and geometry;
Navinor, David Arias, Hanson Sun, DreamingOfClouds, themilkman216 and the
retained E8/label/decoder lineage. Quotienting equal inequalities and monotone
dominance are classical; no literature priority is claimed for them. This
contribution is the exact smaller system and its scope-preserving certificate.

No coefficients, complete COPY floor, physical/native supplier, signed-moment
gain, selected-frontier change or multiplication theorem is established.
The five selected framework assumptions, independent human review and formal
proof-kernel review remain open.
