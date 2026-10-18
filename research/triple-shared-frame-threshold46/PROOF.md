# A sharp ten-coordinate threshold for triple shared nodes

## Model and claim

Use the historical parity-side interface from `docs/research/parity-side.md`
and the one-node model of ArnavSwiggy's PR920. A label is a three-subset of
an h-coordinate ground set, also viewed as its incidence vector over F2.
Take distinct source labels s1,s2 and distinct target labels t1,t2 such that:

1. Both pairs are degenerate: |s1 intersect s2|=|t1 intersect t2|=1.
2. All four cross intersections have even size.
3. The 2x2 rational matrix K(s,t)=Re(i^|s intersect t|) has rank one.
4. E=span_F2(s1,s2) and T=span_F2(t1,t2) intersect only in zero.

These are necessary conditions for a single scalar shared sum with a
nondegenerate separating frame E subset U subset T-perp. The common factor
1/2 in the actual side kernel does not affect rank. Both endpoint pairs
being degenerate is essential to this theorem.

**Classification.** Under conditions1--4, the union of the two target triples
is disjoint from the union of the two source triples. Conversely, any two
degenerate triple pairs on disjoint coordinate supports satisfy1--4.
Consequently h>=10 is necessary. For every such rectangle at every h>=10,
there is a legal dimension-four shared frame with orthonormal residuals at
all four incident edges. The threshold is therefore sharp in this model.

The new result is the all-dimension support classification, necessary
ten-coordinate bound and exact count. PR920 already supplied the h10 positive
fixture and a distinct h8 fixture for general norm-one labels; neither
positive witness is claimed as new.

## Four possible target support types

Coordinate permutations let us write

    s1={c,a,b},  s2={c,d,e},  O=all other coordinates.

The five displayed coordinates are distinct. A target triple even-orthogonal
to both sources has exactly one of these four forms:

| Type | Target support | Column (K(s1,t),K(s2,t)) |
| --- | --- | --- |
| A | three elements of O | (+1,+1) |
| B | {a,b,o}, o in O | (-1,+1) |
| C | {d,e,o}, o in O | (+1,-1) |
| D | {c,x,y}, x in {a,b}, y in {d,e} | (-1,-1) |

To see completeness, if c belongs to the target, even intersections force
one additional element from each of the two disjoint pairs, giving D. If c
does not belong, the target contains either zero or two elements of each
pair. Its size three permits exactly A, B or C.

Scalar rank one requires proportional columns. Thus the two targets lie
either in the A/D group or in the B/C group.

- Two A targets have their entire support in O and are allowed exactly when
  their mutual intersection has size one.
- An A and a D target are disjoint, so their pair is not degenerate.
- Two distinct D targets intersect in one coordinate exactly when both x
  and y differ. Their vector sum is r={a,b,d,e}=s1+s2, so E intersect T
  contains the nonzero vector r.
- Two distinct B targets, or two distinct C targets, intersect in two
  coordinates and are not a degenerate pair.
- A B and a C target intersect in one coordinate exactly when they use the
  same o. Their vector sum is again r, giving the same common-span
  obstruction.

Only A/A remains. Its two triples with intersection one require five
coordinates in O, disjoint from the five source coordinates. This proves
necessity. Disjoint supports make all four scalar entries +1, make the
binary spans disjoint, and give the converse immediately. In particular,
even cross intersections alone cannot replace the signed rank-one test.

## Exact counting

There are 15*C(h,5) unordered source pairs intersecting in one coordinate:
choose their union of size five, the common coordinate in five ways, and a
partition of the other four coordinates into two unordered pairs in three
ways. For each fixed source pair the classification gives exactly

    15*C(h-5,5)

unordered target pairs, taking this to be zero for h<10. Source and target
sides are distinguished. The total number of rectangles is therefore

    225*C(h,5)*C(h-5,5).

At h=10 there are 15 for a fixed source pair and 56,700 over all labeled source
pairs. This formula is proved for all h, not extrapolated from the census.

## Legal frame and incident residuals

In the canonical coordinates s1=7={0,1,2}, s2=25={0,3,4}, use the
predecessor's frame

    U=span(7,25,4,16)=span(3,4,9,16).

Equivalently U is the orthogonal complement of v=11={0,1,3} inside the first
five-coordinate standard space. Since v has norm one, U is nondegenerate of
dimension four. It contains both sources. Every admissible target is
supported outside those five coordinates, so lies in U-perp.

For a nondegenerate binary space W, its characteristic vector w_W represents
the linear functional x -> x dot x. For a norm-one label z in W, the residual
W intersect z-perp is alternating exactly when w_W=z. This is the criterion
already proved in PR920. Here w_U=31 xor 11=20, of weight two, and
w_(U-perp)=(2^h-1) xor 20, of weight h-2. Neither can equal an incident
triple when h>=10. The four residuals are nondegenerate and nonalternating,
hence have orthonormal bases over F2. The main verifier explicitly constructs
all four bases for all 15 canonical h10 target pairs.

The frame and residual argument is invariant under coordinate permutation.
It proves existence for every classified rectangle. It neither selects a
globally compatible labeling for a larger DAG nor accounts for the costs
of a physical supplier.

## Evidence and boundaries

The main finite check exhausts canonical target pairs at h=5,...,12 using
bit masks. A separate set-based engine exhausts every labeled source pair
and every compatible target pair at h=5,...,10, using Fraction determinants
for scalar rank. It checks 6,930 source pairs and 615,060 eligible rectangles.
These finite checks support the written all-dimension classification;
they are not its replacement.

The h8 general norm-one positive control passes: its labels include vectors
of weight one, so it is outside the triple theorem. The old h6 example with
only one degenerate pair also remains legal. Relaxing scalar rank one,
common-span disjointness, or either degeneracy condition changes the class.
No arbitrary-label, multi-node, phase-conversion, Clifford-transport or
current selected-supplier exclusion follows. No paid cost, helper saving,
runtime gain or kappa improvement is claimed.
