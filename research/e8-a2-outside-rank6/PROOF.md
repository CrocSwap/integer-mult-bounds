# Sharp outside-span A2 rank-six joint capacity

Use the declared leading-one root labels R in F2^9 from PR3288. Let A
be any 27-root projective fiber of an A2 root plane and W=span(A).
For a binary linear space V with dim V<=6 and V not contained in W, put
m=|R intersect V| and j=|A intersect V|.

**Theorem.** The existing upper bound m+j<=30 is sharp. For every A,
exactly 1080 spaces V attain equality on full E8. Write U=V intersect W.
Equality holds precisely when dim U=5, its leading-one affine four-section
has nondegenerate polar form and signed quadratic sum -4, U avoids the
unique root p in (R intersect W) minus A, and the other affine four-section
of V also has signed sum -4. Each of the 216 eligible U has five such
outside extensions. On the fixed P112, equality requires additionally
that all 20 roots in V avoid the deleted frame. For the committed canonical
A, exactly 144 spaces do so, including the displayed witness below.
Thus 30 is also the sharp uniform bound for the actual fixed P112.
The number 144 is asserted only for this canonical fiber. The P112 score
counts both intersections with the live root set, using A intersect P112.

This settles sharpness and outside equality, which PR3288 left unclaimed.
PR3262 owns the earlier joint 32 bound; PR3288 supplies its analytic proof
and contained-space equality 27. None of those results is relabelled here.

## Exact model and inherited premises

The source geometry assigns (1,c mod2) to each E8 root line, where c is
its integral simple-root coordinate vector. The leading coordinate is
the low bit in the executable representation. On the residue eight-space
E, the norm quadratic form q has nondegenerate polar form B, precisely
120 value-one points and signed sum +16. PR3288's finite configuration
binding gives an affine six-space H, the leading-one section of W, with
nondegenerate restricted polar form and signed sum +8. Its value-one
set is A union {p}, so it has 28 roots.

The exact PR3288 proof and canonical fixture bytes are retained in vendor.
Their commit, paths, Git blobs and SHA256 are in SOURCES.json. This package
inherits the universal 3360-fiber model-binding conclusion. It does not
rerun that complete predecessor census. Its direct replay authenticates
the geometry, reconstructs all root labels, binds the canonical fixture to
an actual A2 fiber, and checks H's sign and nondegeneracy. The general
argument below applies to every configuration with these inherited facts.

The signed restriction lemma from PR3288 says that an affine k-section
with polar radical of dimension t has signed sum zero or magnitude
2^((k+t)/2). If k+t is the whole ambient dimension and the sum is nonzero,
its sign is the positive ambient sign. Consequently the global rank-six
capacity is 20. Inside H, an affine four-section has at most ten roots;
ten occurs exactly at nondegenerate polar rank four with signed sum -4.
The degenerate rank-two case gives at most eight, and rank zero is
excluded by the radical dimension bound.

## Equality reduces to two affine four-sections

If dim V<=5, the global support bound 12 and j<=12 already give m+j<=24.
If dim V=6, being outside W forces dim U<=5. For dim U<=4 its leading-one
section has at most eight points, so m+j<=20+8=28. Equality 30 therefore
forces dim U=5, j=10 and m=20.

Let J be U's affine four-section and L its direction space. Since
j=10, J has ten roots, its polar form is nondegenerate, its signed sum
is -4 and p is absent. The affine five-section of V splits as J and one
parallel affine four-section J'. Nondegeneracy of B on L makes the signed
sum on every parallel section have magnitude four. Each contains either
six or ten roots. Hence m=20 holds exactly when J' also has ten roots.
This proves the stated necessary and sufficient equality conditions.

For an actual support subset T spanning V, equality in
|T|+|T intersect A| additionally requires T=R intersect V. The proof
does not assume that an arbitrary scalar piece fills its binary closure.

## Count 216 eligible intersections

The six-dimensional symplectic direction space of H has 336 nondegenerate
four-subspaces L. Indeed taking orthogonal complements identifies these
with nondegenerate two-planes. There are 63 choices of a nonzero first
vector and 32 choices of a second vector pairing to one. Each plane has
six ordered symplectic bases, giving 63*32/6=336.

For each L the four affine cosets in H have signed sums +4 or -4.
Their total is +8. Exactly one coset has sum -4 and the other three have
sum +4. Thus each L supplies exactly one ten-root section J.

Exactly 120 of these 336 sections contain p. To count them without an
incidence-transitivity assumption, take p as origin and put
q_p(x)=f(p+x)+f(p), where f is the quadratic function on H and f(p)=1.
Then q_p has signed sum -8. The sum on p+L is -4 exactly when q_p on L
has sum +4. By orthogonal factorization this is equivalent to q_p on
K=L-perp having sum -2. Such a two-plane is anisotropic: each of its
three nonzero vectors has q_p=1.

There are 36 vectors x with q_p(x)=1. For each, the hyperplane B(x,y)=1
has 32 points and signed sum -8, so exactly 20 choices of y have q_p(y)=1.
For clarity, character orthogonality gives that signed sum as
[-8-(-1)^q_p(x)*(-8)]/2=-8. Such x,y span an anisotropic plane because
q_p(x+y)=q_p(x)+q_p(y)+B(x,y)=1. Dividing its six ordered bases gives
36*20/6=120 planes. Therefore 336-120=216 sections J avoid p.

## Count five extensions per intersection

Fix one eligible L and J. All 16 cosets of L in E have signed sums +4
or -4, because L is nondegenerate. Their total is +16, so ten cosets
have sum +4 and six have sum -4. Among the four cosets lying in H only
J has sum -4. There are therefore exactly five negative cosets outside H.

Each such coset J' yields a distinct affine five-space J union J' and
thus a distinct binary six-space V extending U outside W. Conversely every
outside six-space extending U arises from one of the twelve cosets outside
H. This proves five equality extensions for each eligible U. Their
intersections U are unique, so the total is 216*5=1080 for every A.

This count is analytic. The canonical finite census of 2667 intersections
and twelve extensions each corroborates it on 32004 spaces. Spaces with
smaller intersection or smaller dimension cannot attain 30 by the earlier
argument; they need no additional census.

## Fixed P112 attainment and limits

One attaining six-space has binary basis

```
64, 32, 17, 8, 4, 3
```

Its full E8 root closure consists of these 20 labels, all present in P112:

```
3,11,17,21,25,29,39,47,49,53,57,61,71,79,103,111,113,117,121,125
```

Exactly ten are in the canonical A2 fiber:

```
3,17,29,47,49,61,79,111,113,125
```

Both enumerations check rank six, that V is outside W, its exact root
closure, the ten-label fiber intersection and actual frame avoidance.
For any A, the fixed-P112 equality spaces are precisely the 1080 full-E8
equality spaces whose root closures avoid the frame. No equal count for
other A is claimed. The canonical count 144 is finite evidence.

Attainment of a support inequality supplies no simultaneous compatible
pieces, rational scalar factors, shortening threshold, historical caller
exclusion, decoder floor, physical program, restored workspace, complete
consumer, supplier or kappa result. The global 12/20 and universal A2
configuration premises remain inherited. Lean, Docker, the old large
flat censuses and the selected cold replay are unrun.

Credit Nick Petalas/PR3288/3280/3269/3262, David Arias's quadratic model,
DreamingOfClouds/PR3154 and the retained E8/P112 lineage including joaqcoo.
New material is Apache-2.0. Internal computational review is separate
from independent human or proof-kernel approval.
