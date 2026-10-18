# Sharp common-cut threshold for three rank-five pieces

Use the actual P112 roots and leading-one nine-bit labels in the pinned
`geometry.py`. Let K be any characteristic-zero field, and let
`C = {(r_t dot h)_t : h in K^8}`. For one common set S of live coordinates,
write pi for deletion of S. The binary support rank of a piece is the F2
rank of the labels at its nonzero residual coordinates.

**Theorem.** If `|S| <= 47` and each of three arbitrary pieces has residual
binary support rank at most five, then

```
dim_K(pi(C) intersect span_K(pi(q_1), pi(q_2), pi(q_3))) <= 1.
```

The threshold is sharp. At 48 there are three rational pieces, each with
support size12 and binary support rank5, whose span contains two independent
restricted codewords. Coefficients are arbitrary; pieces may be dependent.
This is a shortening theorem, not a complete decoder or multiplication result.

## Sources and separate obligations

The retained PR3266 proof and receipt supply the D6/A2 normalization framework,
Weyl action on labels, full D6 fiber sizes33,33,12,12 and small-fiber capacity8.
Its theorem stops at46. PR3269 supplies an analytic global rank-five capacity12
on the exact full120 labels. The separately developed A2 joint-incidence proof
and receipt are retained with their exact source commit in SOURCES.json.
Scientific commit `129eba68a1ae082ea65dffcfd93a1305165113e1` supplies the new
bound20 used below, replacing PR3257's bound21.
These are pending research dependencies, not selected supplier admissions.

The standard real Weyl-chamber theorem remains a mathematical premise. A
root-spanned subspace, after a Weyl transformation, has its roots generated
by a subset of simple roots. The code checks the finite face inventory and
normal-plane statements used here; it does not formalize that theorem.
The inherited Weyl transitivity and label-linearity argument transports the
canonical D6 fiber calculation, including arbitrary transformed frames.

## Normalize any two restricted codewords

Suppose the displayed intersection has dimension at least two. Lift two
independent restricted codewords to h,k, and let U be the full live union of
their supports. Every coordinate in U outside S belongs to a residual piece.
Global capacity12 gives

```
|U| <= |S| + 3*12 <= 83.
```

At least29 live root lines are perpendicular to both h,k. Their rational
span has rank at most six, because rational matrix rank is unchanged over a
characteristic-zero extension and h,k are independent. A parabolic of rank
at most five has at most20 lines. The complete six-node face inventory has
only D6 with30 lines and E6 with36 lines above the new cutoff29. Therefore
the perpendicular roots span rank six and h,k span the scalar extension of
its rational normal plane. This is D6's orthogonal-root plane or E6's A2 plane.
No ordering of K is assumed.

In the A2 case the live union has size at least78, so
`N = |U minus S| >= 31`. Express the two restricted codewords by a fixed
2-by-3 coefficient matrix in the three pieces. A singleton site, where
exactly one piece is nonzero, has evaluation direction given by that piece's
coefficient column. Its singleton labels lie in one projective A2 fiber.
A zero coefficient column admits no singleton in U.

Let m_i count piece i's incidences in U outside S, and l_i its singleton
sites there. The retained A2 theorem gives `m_i+l_i <=20`: the full-root
intersection with its rank-five ambient span bounds m_i, and intersection
with its singleton fiber bounds l_i. The one-root fibers also satisfy this
bound, using12+1. At each nonsingleton coordinate there are at least two
incidences. Thus

```
62 <= 2*N <= sum_i(m_i+l_i) <= 60,
```

which is impossible. Supports or cancellations outside U only consume capacity.

## D6 near-equality forces eleven singleton labels

The exact orthogonal-plane inventory shows that a D6 live union at most83
has size exactly82. Each of its two full33-root axis fibers loses four
mutually orthogonal frame roots; neither12-root diagonal fiber loses a root.
Consequently `N >=82-47=35`. Write M for the sum of the three support sizes
outside S, so `35 <= N <= M <=36`.

If M=35, all three supports are disjoint, have sizes11,12,12, and every
site is singleton. If M=36, all supports have size12 and there is at most
one excess incidence over the union. Each piece therefore has at least11
singleton sites. Incidences outside U can only reduce these allowances: more
formally apply these same inequalities to m_i, whose sum is at most M.
Hence in every case each piece has at least11 singleton sites in U outside S.

Each singleton set lies in one projective D6 fiber. The smaller fibers have
capacity8, so only the two axis fibers can occur. The following new finite
lemma upgrades singleton concentration to concentration of the whole piece.

**Eleven-label closure lemma.** Every rank-at-most-five set of at least11
labels in a full33-root D6 axis fiber lies in a twelve-root five-space whose
full E8 root intersection consists of those twelve axis labels.

For each canonical axis, the complete97,155 five-space enumeration has no
intersection of size11 and exactly120 intersections of size12. Every such
intersection spans five dimensions and its full120-root closure has size12,
all in that axis. Any eleven leading-one labels have binary rank at least
five: a four-space has only eight leading-one vectors. Thus their span is
already the five-space on extension, proving the lemma. Since the entire
piece has binary rank at most five, it lies in this same full-root closure.
It is consequently wholly contained in its singleton axis fiber.

## Punctured near-maxima have pair union at most22

A closure may include one removed frame root. It would be incorrect to check
only twelve-element supports that avoid the puncture. The replay checks all
120 mutually orthogonal four-root punctures in each canonical axis, including
closures meeting the puncture in one root.

For every puncture, the120 twelve-root closures leave exactly60 distinct
live intersections of size at least11: twelve have size12 and48 have size11.
Every pair of these live intersections has union at most22. The12/12 case
recovers PR3266's minimum intersection2. The12/11 cases have minimum
intersection4. Two11-element sets have union at most22 without another bound.
Any actual piece with at least11 singleton labels is a subset of one of these
near-maximal live intersections, so the same pair-union bound applies to it.

Three pieces in two axis fibers force two pieces in the same fiber. Their
union has size at most22; the third has size at most12. Thus their total
union is at most34, contradicting N>=35. This finishes the theorem.

The primary enumeration is complete by unique reverse-echelon annihilators.
The second implementation enumerates all474,672 five-label subsets of the
two full axis fibers, performs separate elimination, and recovers exactly
the same240 closures. It independently checks the rational witness equations
and support ranks. This is finite computational evidence and written proof,
not proof-kernel or independent human verification.

## An actual rational counterexample at48

WITNESS.json stores two orthogonal root directions a,b, one48-coordinate cut
and all112 coefficients of each piece, scaled by two to keep them integral.
The directions in the pinned root order are

```
a = (0,0,0,0,0,2,-2,0)
b = (0,2,-2,0,0,0,0,0).
```

Their live union has size82. In a's axis choose two surviving twelve-root
rank-five supports A,B with intersection2. In b's axis choose another such
support D. Their union has size34. Delete precisely the remaining48 roots
of the codeword union. Let q_1 equal c_a on A minus B, and c_a/2 on A cap B;
let q_2 equal c_a on B minus A and c_a/2 on A cap B. Let q_3 equal c_b on D.
All other entries are zero. Then on the retained coordinates

```
q_1 + q_2 = pi(c_a),   q_3 = pi(c_b).
```

Both codewords are nonzero and independent because their retained supports
lie in distinct axes. The verifier checks every retained coordinate, the
three exact binary ranks, the48 distinct cuts and a nonzero2-by-2 evaluation
minor. This disproves the uniform statement at48 and makes47 sharp.

## Limits and next questions

No literal TWOSIDE caller is inferred. The theorem requires one common cut,
the declared leading-one labels, three residual ranks at most five, and
characteristic zero. No full C5, complete decoder floor, native realization,
physical bill, restoration/consumer implementation, supplier admission,
all-size multiplication theorem or kappa improvement is claimed.

The narrow family decision is to finish this explicitly missing boundary and
stop. No new construction round follows. Global capacity12, A2 incidence20
and the Weyl argument remain attributed dependencies with the evidence status
above. Selected cold replay, Lean, Docker and full supplier verification are
unrun. Credit Nick Petalas/PR3249/3257/3266/3269, DreamingOfClouds/PR3154 and
the retained E8/P112 lineage including joaqcoo. No predecessor is modified.
