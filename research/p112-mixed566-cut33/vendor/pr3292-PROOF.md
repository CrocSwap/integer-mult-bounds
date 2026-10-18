# Analytic rank-six capacity after four D6 punctures

Let R be the full120 E8 root lines with the leading-one binary labels
`(1,c mod2)` in the pinned simple-root coordinates. For orthogonal root
lines a,b, let F be the33-line fiber with `r dot a !=0, r dot b=0`.
Let P consist of FOUR mutually orthogonal lines in F. For any ambient
binary linear space V of dimension at most six,

```
|(F minus P) intersect V| <=18.
```

The uniform bound is sharp. It is attained after every such puncture in
the canonical fiber, and an actual18-label support attains it in the
fixed P112 configuration. PR3267 already established18 by complete
six-space censuses. The new contribution is the analytic proof below,
including the exceptional-root case and an equality classification.
No shortening theorem or caller application is asserted.

## Exact finite model binding

The norm quadratic form on root residues is

```
q(x) = sum_i x_i + sum_(i<j) (s_i dot s_j)/4 * x_i*x_j mod2.
B(x,y) = q(x+y)+q(x)+q(y).
```

Here s_i are doubled simple roots. The norm identity follows by expanding
`||sum_i c_i*s_i||^2/8`. All root labels satisfy q=1.
The following properties are checked on one canonical ordered pair.

1. F consists of the exceptional line a and a32-line set T. The labels
   of T span a seven-space W. Their affine span H has dimension six;
   its direction space is L. The exceptional label is outside W.
2. T is exactly the q=1 locus in H. The polar restriction to L has rank
   four and radical D of dimension two. The affine derivative character
   `d -> q(o+d)+q(o)` on D is nonzero, for any origin o of H.
3. All120 orthogonal four-root subsets P of F lie in T. Each is an affine
   two-plane in H, with direction Q satisfying `Q intersect D={0}`.

The exceptional line cannot occur in a four-root orthogonal subset:
its inner product with every line of T is +4 or -4. The replay exhausts
all four-subsets of the32 bulk lines and checks the affine-plane and
transversality properties. These are finite structural premises, not
an enumeration of rank-six support spaces.

The eight simple reflections permute all120 roots and induce invertible
linear maps of their nine-bit labels. A bounded orbit calculation visits
all7560 ordered orthogonal pairs. Consequently the canonical binding
transports every fiber, puncture, binary rank and support intersection
in the theorem. This uses exact finite permutations and label maps,
not an unrun Weyl/chamber classification theorem.

## Five-dimensional affine sections of H

Write f for q restricted to H. Its radical D has a nonzero derivative
character. Let M be a hyperplane direction in L.

If D is contained in M, that character pairs the points in each affine
hyperplane with opposite f values. Each section has exactly16 ones.

If D is not contained in M, then `dim(M intersect D)=1`. The projection
of M onto the nondegenerate four-space L/D is onto, so the restricted
polar rank on M is four and its radical is `M intersect D`.
If the derivative on that radical is nonzero, the section is again
balanced. Otherwise f descends to a nondegenerate quadratic function
on the affine four-dimensional quotient. Its signed sum is +4 or -4,
so the original five-section has signed sum +8 or -8 and contains
12 or20 ones. Thus every affine hyperplane of H contains12,16 or20
points of T. Smaller sections may be extended to hyperplanes.

This character-sum fact follows by squaring the signed sum and grouping
pairs by their difference. For a nondegenerate quadratic function on
four variables the square is16, so its signed sum is +4 or -4.
For degenerate restrictions a nonzero radical character gives zero.
No historical global flat-capacity proof is needed here.

## A twenty-point section meets P at least twice

Let K be a hyperplane of H with20 ones. Its complementary hyperplane
K' has12, since T has32. Both have the same direction M. The restricted
radical E is the one-space `M intersect D`, and f is constant along E.
On K'/E the induced nondegenerate quadratic function has six ones
among16 points, hence positive signed sum +4.

Suppose K misses P. Then P is contained in K'. The direction Q of P
is disjoint from D, hence from E. Its image in K'/E is an affine
two-plane on which the quotient quadratic function is constantly one.
This is impossible for a nondegenerate four-dimensional quadratic
function of positive signed sum.

For completeness, if such an affine two-plane exists, its direction J
is totally isotropic and has dimension two. Thus `J=J-perp`. For a point
z of the plane, set `g(x)=f(z+x)+f(z)`. This function vanishes on J.
On every coset of J outside J, a nonzero polar character cancels the
signed sum. The total signed sum of g is therefore4. Translating back
and using f(z)=1 gives total signed sum -4 for f, a contradiction.

An affine hyperplane meets an affine two-plane in zero, two or four
points. The zero case is excluded, so K meets P in at least two.
It leaves at most18 roots after the puncture. Sections with at most16
ones already satisfy that bound.

## Arbitrary ambient support spaces and equality

If V is contained in W, its leading-one section is empty or has affine
dimension at most five inside H. Extend it to an affine hyperplane K.
The preceding argument gives at most18 surviving roots.

If V is not contained in W, `dim(V intersect W)<=5`. Its leading-one
section has affine dimension at most four and at most16 points. The
exceptional root can add at most one, giving17. This counts every
ambient V, including spaces not generated by fiber labels and spaces
containing the exceptional root.

Equality18 therefore forces V to be a six-space contained in W. Its
five-dimensional section has20 ones and meets P in exactly two.
Conversely those conditions give equality. For an actual subset of
labels with binary rank at most six, equality additionally means that
it contains all18 surviving points of that section. Arbitrary subsets
need not fill their binary closure to satisfy the upper bound.

The primary replay corroborates the proof with only127 hyperplanes of
W and their intersections with all120 punctures. It finds attainment
for every puncture. RESULT.json also stores an18-label support and
rank-six ambient basis on a literal fixed-P112 minimum-union D6 plane.
The separate checker reconstructs roots and labels by a different
rational elimination and enumerates all10795 six-spaces in the full
eight-dimensional fiber span, checking all120 punctures independently.
It does not rerun the896-fiber historical census.

## Limits and credit

Four orthogonal punctures are essential. Removing only two roots or
arbitrary nonorthogonal roots does not establish18. The controls retain
actual20-point sections under those changed hypotheses. Rank seven
also fails: W contains all28 surviving bulk labels.

This is written mathematics with exact finite structural binding and
internal computational review. It is not human or proof-kernel approval,
a new shortening threshold, literal caller, full C5, decoder floor,
physical supplier, restoration/consumer invoice or kappa result.
Selected cold replay, Lean, Docker and historical full censuses are unrun.

Credit Nick Petalas's PR3267 at
`008f042859a5183d1323228a68aa1038f8d7718a` for the original18 result and
finite dependency, David Arias's retained quadratic model, the
root-simplex/E8/P112 lineage including joaqcoo, and DreamingOfClouds/PR3154
for the reduction motivation. PR3267's proof/receipt bytes are retained
with exact source authentication and attribution. No predecessor proof
is a mathematical premise of the new capacity argument. Concurrent
A2 joint32 and mixed5/5/6 cut40 work has separate predicates and is not used.
