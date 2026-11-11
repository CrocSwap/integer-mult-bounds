# Cancellation adds a three-block signature

This is a scoped algebraic proof. It answers Open next question 1 of
SHIN09-git's [#6708](https://github.com/CrocSwap/integer-mult-bounds/pull/6708).
The new proof and construction were produced by Nick Petalas. Apache-2.0.

## 1. The signature and the generic model

Partition the rows of an invertible square matrix P into nonempty blocks.
Message j has source mask consisting of the blocks on which column j of P
is nonzero. Its reader mask consists of the blocks on which row j of
P inverse is nonzero. This is the source/reader convention of #6708,
Gonzalo Mier's #3990/#3997 and Nick Petalas's #6691.

A generic support matrix has one separate algebraically independent
indeterminate in each allowed entry, zero elsewhere. Invertibility and
inverse supports are taken over the rational-function field. The generic
census is the union of signatures over all such structurally invertible
supports, not just the support of one selected numerical witness.

**Result.** On three blocks of two rows there is an integer unimodular P
whose source masks are all ABC and whose reader masks are

    BC, BC, AC, AC, AB, AB.

The same matrices realize the same signature over every field. No generic
support matrix has that signature, over any coefficient field. In fact,
for b >= 2 blocks and arbitrary positive block sizes, if every generic
source mask is full then at least b reader masks are full. This generic
lower bound is sharp.

The counterexample settles the stated six-port existence question. It
does not enumerate all three-block signatures or price a decoder.

## 2. A field-uniform integer witness

All displayed blocks are two by two. Put

    T = [ 0 -1 ]      T^2 + T + I = 0,      det T = 1.
        [ 1 -1 ]

Define the two six-by-six integer matrices

        [ 0 I I ]                [  T^2 -T^2 -T ]
    B = [ I 0 I ],           P = [  -T    T -T ].
        [ I T 0 ]                [ -T^2  -T  T ]

Direct block multiplication using T^2 + T + I = 0 gives

    P B = B P = I_6.

For example the first block row of P B is
(-T^2-T, T^2-T^2, T^2-T^2) = (I,0,0).
The remaining block rows follow by the same identity. Both matrices
therefore have integer inverses and are unimodular. This establishes the
identity over every field, including characteristic two; no division by
two is used.

Every block of P is one of T, -T, T^2, -T^2 and is invertible over every
field. Every column of P consequently has a nonzero restriction to each
of the three row blocks. The diagonal blocks of B are zero and every
off-diagonal block is I or T, also invertible. Each row in block A of B
therefore reads exactly B and C, and likewise for the other blocks.
This proves the claimed signature over every field.

## 3. Generic inverse supports from a determinant matching

Here is the classical matching/path description, with conventions fixed
to avoid transposing source and reader masks.

Choose a determinant matching of a structurally invertible generic
matrix. Write r(j) for the row matched to column j. Relabel column j by
r(j), so the matched entries become diagonal in a matrix Q. On the row
vertices put a directed edge i -> r(j) for every supported P[i,j].

**Path fact.** The generic inverse entry P inverse[j,i] is nonzero if and
only if i is reachable from r(j) in this directed graph, allowing the
length-zero path.

To prove this, first use Q. A simple path from u to v supplies a matching
in Q with row v and column u removed: use the path's edges and the
diagonal matching at the other vertices. Conversely any matching of that
minor, together with the removed row/column, decomposes into a directed
path from u to v and disjoint cycles. Thus the corresponding cofactor
has a determinant matching exactly when the path exists. Each supported
entry is a distinct indeterminate, so different matchings have different
monomials. They cannot cancel, even in characteristic two. A cofactor is
therefore nonzero exactly in this case. Undoing the column relabeling
gives the stated convention for P inverse. The u=v case uses the
diagonal matching in the principal minor.

This uses the standard structural determinant/cofactor matching method;
it is not a new matching theorem. The new use is the block-mask bound
below.

## 4. The generic full-reader floor and its sharpness

Suppose every source mask of P contains all b blocks. Take a source
strongly connected component C of the directed graph above, meaning one
with no edge into it from another component. Such a component exists
because the component graph is a finite directed acyclic graph.

For any column j with r(j) in C, every block supplies a supported entry
P[i,j]. Each such entry gives an edge i -> r(j). The source property
forces i into C. Thus C meets every block and has at least b vertices.

For each vertex r(j) in C, strong connectivity gives a path to every
vertex of C. By the path fact, row j of P inverse has a nonzero entry in
each block. The distinct vertices of C correspond to distinct messages.
At least |C| >= b messages therefore have full reader masks. This proves
the bound for every structurally invertible support, irrespective of the
matching chosen.

For sharpness choose one representative row in each block. Support every
entry of those b rows, and support only the diagonal entry of each other
row. There is a diagonal matching. The representatives form one source
strongly connected component; they reach every row. Every other vertex
has only its self-loop. The path fact gives full reader masks exactly
at the b representatives. All columns have full source masks. Because
b >= 2, the other rows' singleton reader masks are not full. The lower
bound is attained for all positive block sizes.

For the six-port witness b=3, but no reader mask is full. Hence its
signature is absent from the union over all generic support matrices.
Merely noting cancellation in its own entry support would not prove
this stronger exclusion; the universal bound does.

## 5. Scope and finite corroboration

The all-field conclusion and the exclusion of all six-port generic
supports use the proof above. The verifier independently inverts the
integer matrices, checks both products and signatures, and specializes
to F2, F3, F5, F7 and F11. It checks every full-source support for block
sizes (1,1,1), (2,1,1) and (2,2,1), comparing literal cofactor matchings
with graph reachability. It also checks the sharp six-port generic
example and the generic signature of the actual witness support.
These are finite corroborations, not an exhaustive six-port census.

The predecessor's two-block classification is a cited result, not
replayed or audited. Its theorem remains within its two-block scope.
The new result shows why its generic-signature equality cannot simply
be extended to three blocks. No paid physical preparation, restoration,
delivery, native word, supplier, kappa or multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
