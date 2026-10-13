# Exact local elimination in the unrestricted dimension-15 problem

**Outcome: 43 of 146 branch representatives are excluded; 103 remain
open. No new geometry or multiplication exponent is established.**

This continues `NONCOVARIANT-FOLLOWUP.md`. Unlike the earlier shared-scalar
screen, this reduction imposes no covariance, additive labels or common
form. It uses the legitimate fixed-Fano coordinate gauge of the
unrestricted problem. Graph automorphisms identify equivalent cases;
individual solutions need not respect those automorphisms.

## The single leftover coordinate gives an exact finite case split

Write the ambient space as seven anchored two-planes E_0,...,E_6 and a
one-dimensional remainder L. A variable projector is P_T=A_T B_T with
B_T A_T=I_2. Adjacency to an anchor deletes the corresponding coordinates
from both factors.

The 77 non-anchor labels fall into fourteen support classes, paired in
seven groups indexed by a ground point j of the fixed seven-point Fano
plane. In each group:

- Five labels X_j have support in four anchor planes plus L.
- Six labels Y_j have support in the complementary three planes plus L.
- Every X_j label is adjacent to every Y_j label.

These seven complete bipartite graphs account for precisely the 210 edges
whose only common allowed coordinate is L. This is checked by direct
enumeration of all 1,890 graph edges.

Let a_X mean the collection of remainder rows of A_T over X_j, and b_X
the collection of remainder columns of B_T; define a_Y,b_Y similarly.
The cross equations are products of a column and a row over a field.
Consequently they are equivalent to

    (b_X=0 or a_Y=0) and (b_Y=0 or a_X=0).

The four resulting modes are:

| Mode | Forced zeros |
|---|---|
| 0 | a_X=a_Y=0 |
| 1 | b_X=b_Y=0 |
| 2 | a_X=b_X=0 |
| 3 | a_Y=b_Y=0 |

The modes may overlap; this is an exhaustive cover, not a disjoint
classification of representations. There are 4^7=16,384 mode patterns.
The 168 permutations preserving the fixed Fano plane, together with
global transposition P_T -> P_T^T, reduce this cover to **146 orbits**.
Transposition exchanges modes 0 and 1 and fixes modes 2 and 3.

The one-dimensional remainder is essential. With two remainder
coordinates, nonzero factors can multiply to zero, so this split must
not be used to exclude the valid dimension-16 control.

## Coordinate spans and saturated clique identities

For a clique K of q labels, the images of its rank-two projectors form a
direct sum of dimension 2q. Their dual row spaces do too. Thus either
factor support union must have dimension at least 2q.

If the image support union is a coordinate space D of dimension exactly
2q, the sum Q_K of the projectors has image D and acts as identity on D.
The analogous statement for a saturated dual support gives the same
identity on the D-by-D block. Neither argument requires orthogonality
or positivity.

This has two exact consequences:

1. A common neighbor's dual factor must vanish on a saturated image
   union; the transposed rule applies to saturated dual unions.
2. In each anchored two-plane contained in a saturated union, the sum
   of the corresponding diagonal block traces is two.

All **80,859 nonempty cliques** are enumerated, with sizes 1 through 7.
Coordinate-span propagation alone makes no further deletions and excludes
none of the 146 representatives. The diagonal identities are stronger.

For each projector and anchored two-plane use a variable equal to half
the block trace. Use half the scalar remainder entry for the eighth
variable. A deleted row or column forces that variable to zero. Saturated
cliques impose sums equal to one; trace(P_T)=2 imposes a sum of the eight
variables equal to one. Variables are unrestricted signed rationals.

Exact rational elimination gives:

| Test | Representatives excluded |
|---|---:|
| Saturated-clique diagonal equations | 41 |
| Additional trace coupling | 2 |
| Remaining after both | 103 |

The excluded orbits cover 3,824 of the 16,384 mode patterns. This is a
count of branch descriptions, not a proportion of potential solutions.

## Independent evidence and its limits

Each exclusion records a rational linear combination of necessary
equations with zero variable coefficients and nonzero right-hand side.
`verify_local_support.py` reconstructs the equations from the graph and
branch supports, checks clique saturation, and sums the certificate
without running Gaussian elimination. All **43 contradictions replay**.

For each surviving representative, the artifact also supplies a rational
assignment satisfying every tested diagonal and trace equation. The
independent replay checks all clique constraints and all traces for all
**103 assignments**. These assignments are solutions only to the linear
relaxation; they do not claim to be idempotent matrices or valid labels.

Four focused tests check the 210-edge partition, the exhaustive Boolean
case split, the orbit cover, every rejection certificate, and rejection
of a deliberately corrupted certificate.

## Next bounded experiment

Further diagonal elimination using these same saturated-clique and trace
equations cannot exclude the surviving branches: explicit rational
solutions are saved. The next useful step is to add local rank conditions
that those equations omit.

In particular, 378 of the non-anchor edges originally share exactly one
anchored two-plane and L. On such a three-dimensional intersection,

    B_T|_D A_U|_D = 0

implies

    rank(B_T|_D) + rank(A_U|_D) <= 3.

Both factors have rank at most two, so at least one restriction must have
rank at most one. Branch-specific zero patterns can reduce the shared
support further. This offers small determinantal subproblems inside the
103 remaining branches. A failed bounded search in those subproblems
still would not be an unrestricted impossibility proof.

Start with the two uniform survivors (all mode 2 and all mode 3), which
give especially explicit fixed clique-sum identities. Treat them as
diagnostics, not as representative of every remaining case. The existing
dimension-16 exact control should remain in every algebra/checker pass.

## Reproduction

    python3 research/kappa-nine/local_support_elimination.py --output /tmp/local-support.json
    python3 research/kappa-nine/verify_local_support.py /tmp/local-support.json
    python3 -m unittest discover -s research/kappa-nine -p test_local_support.py -v

All three commands use the Python standard library. The full elimination
run took about 83 seconds in this environment. Existing publication
artifacts, earlier receipts, and the selected multiplication witness were
left unchanged.
