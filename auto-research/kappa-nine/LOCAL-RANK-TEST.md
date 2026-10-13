# Local rank tests: a compatibility obstruction, not a new exponent

**The unrestricted dimension-15 problem remains open. All 103 branch
representatives retained by the previous pass remain open.** This pass
tests the uniform mode-2 and mode-3 cases from `LOCAL-ELIMINATION.md`.

Two results are established:

1. Both cases pass every pairwise restricted-rank inequality with explicit
   abstract rank profiles. Those inequalities alone do not close either
   case.
2. In uniform mode 3, at least three of the seven anchored two-dimensional
   blocks must have some allowed Y-label factor restriction of rank zero
   or two. The candidate in which all such restrictions have rank one is
   impossible, as are repairs confined to one or two blocks.

No covariance or symmetric form is assumed in the second statement.
It is a necessary condition within uniform mode 3, not a rejection of
that entire case or of the other 102 surviving representatives.

## What the rank inequalities do and do not test

For a directed edge T,U, let D be the intersection of the allowed column
support of B_T and row support of A_U. Annihilation implies

    rank(B_T restricted to D) + rank(A_U restricted to D) <= dim D.

The audit supplies abstract row/column-space profiles satisfying this
inequality on all graph edges, total factor rank two, and the elementary
sum-of-product-ranks condition for B_T A_T=I_2. The profiles are ordinary
rational rank-two subspace patterns: positive integer labels describe
distinct lines in an individual factor's internal two-space, and -1
denotes the full two-space.

For mode 3, use distinct lines on all allowed blocks. For mode 2, use a
seven-coloring of the Y-label subgraph to choose one exceptional line in
each Y factor, with its other blocks and remainder sharing a common
line. A short backtracking routine finds and exactly checks the coloring.

These are **rank-relaxation witnesses**, not factor matrices satisfying
normalization and annihilation. In particular, the inequalities cannot
check whether the necessary lines in different factors can be aligned
consistently. The next argument detects precisely such an inconsistency.

## The rank-one alignment obstruction

In uniform mode 3 the 42 Y labels have no remainder coordinate. Each has
support in three anchored two-planes. Call an anchored block *regular*
if every allowed A and B restriction of the 18 Y labels supported there
has rank exactly one.

Fix a regular block E. Among its 18 labels, take the edges for which E
is the sole common allowed block. This graph has 54 edges and is
connected and bipartite. The certificate supplies the graph, its two
colors, and a spanning tree for each of the seven choices of E.

Let U_T be the image line of A_T restricted to E and K_T the kernel line
of B_T restricted to E. For an edge T,U in this graph,

    B_T|_E A_U|_E = 0   implies   U_U = K_T.

The reverse directed edge gives U_T=K_U. Connectivity and bipartiteness
therefore force two lines L_0,L_1 such that

    U_T=L_color(T),    K_T=L_(1-color(T)).

The two lines must be distinct. Indeed, each of six relevant three-label
cliques fills its six-dimensional coordinate support, so the sum of its
projectors restricts to I_2 on E. If L_0=L_1, all the corresponding
A_T B_T block images would lie in one line, making that identity
impossible. This step uses rank, not positivity or an inner product.

Consequently, for any two labels supported on a regular E:

- opposite colors force B_T|_E A_U|_E=0;
- equal colors force this product to be nonzero.

Now take two members of a Y_j three-label clique. Their common support
consists of the three anchor blocks associated with ground point j.
The certificate checks that their colors agree on exactly one of those
blocks and disagree on the other two. If all three blocks were regular,
the full product B_T A_U would therefore have one nonzero summand and
two zero summands. It could not vanish, contradicting their adjacency.

This argument applies for each of the seven values of j. Thus the set of
nonregular blocks must intersect each of the seven three-block support
sets. Exhaustive enumeration of the 128 block subsets gives minimum
size **three**, with seven minimum sets. Equivalently, a candidate must
have at least three anchored blocks each containing some allowed Y
restriction of rank zero or two. This does not prescribe how many such
restrictions occur or their ranks elsewhere.

## Controls and interpretation

The isolated 18-label problem on each individual block really is
feasible. The audit constructs rank-one rational factors using two
coordinate lines, with coefficients 1 or 1/2, and verifies all its local
zero products and all six saturated-clique sum identities. All seven
isolated controls pass. The obstruction requires compatibility across
three different blocks; it is not a disguised local inconsistency.

The combinatorial replay checks the spanning trees, colorings, actual
support intersections, the seven contradictory-edge patterns, and the
minimum hitting-set count. Three focused tests also check both abstract
rank profiles and reject deliberately corrupted profiles and colorings.

This is useful pruning, but it is not a reason to increase a blind solver
budget. The next bounded test should admit mixed ranks 0,1,2 in uniform
mode 3 and propagate the line identifications only where rank one is
actually present. Start with the seven minimal three-block exception
patterns; label that restriction explicitly, since a valid construction
could need four or more exceptional blocks. Keep the broader 103-case
problem open throughout.

## Reproduction

    python3 research/kappa-nine/local_rank_test.py --output /tmp/local-rank-test.json
    python3 -m unittest discover -s research/kappa-nine -p test_local_rank.py -v

The scripts use only the Python standard library. The exact checks run
in well under a second here. Previous receipts, published artifacts and
the selected multiplication witness remain unchanged.
