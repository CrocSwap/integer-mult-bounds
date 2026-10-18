# A mixed-rank anchor closes one beta shape

All label spaces are over F2. Direction spans and piece coefficients are over
a characteristic-zero field K. Use the pinned doubled E8 roots r_t, the 112
nonframe lines, and the nine-bit labels ell(t). Define

```
Lambda(V) = {t : ell(t) is in V}
Off(h) = {t : r_t dot h != 0}.
```

## Finite theorem

Fix any two six-dimensional label spaces V1,V2 and let X be the union of their
live-line masks. For j in {4,6}, define H_j to consist of the nonzero projective
directions h for which some set D_h of at most twelve live lines satisfies

```
rank_F2 ell(Off(h) \ (X union D_h)) <= j.
```

If H_4 is nonempty, then dim_K span(H_6) <= 3. The bound is sharp for this
separate-deletion contract. It therefore also bounds any subfamily using one
common deletion set. Common-set attainment is not claimed.

This is an exact finite geometric result, not a supplier or multiplication
claim. Its proof uses the finite census and the standard E8 Weyl-chamber theorem.

## Direction completeness at support seventy-two

The retained flat enumerator covers all 788,035 three-dimensional annihilators
in F2^9. Their kernels are all six-flats. Every live six-flat mask has at most
twenty lines. Every live label is odd, so a rank-four label set has at most eight
lines: the first-coordinate functional cuts a four-dimensional space in at most
eight points.

Every H_6 direction consequently has support at most

```
20 + 20 + 12 + 20 = 72.
```

Thus at least forty of the 120 E8 root lines are perpendicular. The retained
geometry checks a simple system, positivity of all root coordinates in it, and
all 28 six-node parabolic enlargements. They have at most 36 root lines. In a
closed Weyl chamber, forty perpendicular lines therefore force a seven-node
face. The eight fundamental-ray perpendicular counts are

```
42, 28, 22, 14, 16, 23, 37, 63.
```

Only the 42 and 63 rays can qualify. Their projective reflection closure has
1,080 D7 normals and 120 E7/root normals. The P112 support histogram of this
whole closure is

```
53:112, 56:8, 70:128, 73:896, 76:56.
```

There are no supports 71 or 72. The predecessor's 248 directions at cutoff
seventy therefore remain complete at the new cutoff seventy-two. This gap is
explicitly recomputed in `mixed_direction_coverage`; it is not inferred from
having used the old catalogue. The same argument proves the nonzero P112 root
code distance is 53.

For general K, the rational span of the roots perpendicular to h has rank at
most seven. Rank at most six would give a generic real normal with at least
forty perpendicular roots of rank at most six, contrary to the parabolic cap.
Thus its rational kernel is a line, h is proportional to its rational generator,
and the real classification applies. Scalar extension preserves the ranks of
the resulting rational direction vectors. This also handles complex directions.

## Complete pair coverage and pruning

There are 776,805 distinct nonempty six-flat masks. Empty masks cannot admit an
H_6 direction: the other flat, residual flat and deletions cover at most 52
lines, below distance 53. Repeated masks do not change the question.

The retained twelve generators preserve binary-label relations. Their signed
Gram matrices are checked against every root pair, and the live roots span Q^8.
Hence the permutations are induced by invertible rational orthogonal maps.
They preserve both residual binary ranks and characteristic-zero direction
spans. Union-find gives 159 first-mask orbits. One first mask per orbit paired
with every second mask covers all pairs, giving 123,511,995 representative pairs.
No symmetry of rational rank is inferred from support permutations alone.

An anchor in H_4 has support at most 20+20+12+8=60, so only the 120 root normals
need be tested. Before the second flat is removed it has at most forty lines;
afterwards at most twenty. These are necessary cardinality inequalities. Every
remaining decision goes to the exact rank-four oracle. After finding one anchor
for a pair, the program tests every catalogue direction whose residual support
has at most 32 lines for membership in H_6. It does not replace the anchor's
rank-four requirement with rank six.

The completed census reports 987 anchor decisions, 832 anchor-positive pairs
and 2,146 rank-six oracle calls. Every positive pair has H_6 span at most three.
Python checks every recorded anchor answer, recomputes the complete H_6 list for
every positive pair, validates the literal cuts and computes rational rank.
All 159 orbit rows and coverage totals are required. `RESULT.json` retains them.

## Exact deletion oracles and sharpness

For a residual set S of at most twenty odd labels, rank-four retention after
p<=12 deletions is automatic when |S|<=p+4, by keeping any four points. If
|S|>p+8 it is impossible. Otherwise a successful retained set has at least five
points, so rank exactly four and a four-point basis. Four distinct odd labels
x,y,z,w are independent precisely when x XOR y XOR z != w. The odd points of
their span are those four points and their four triple XORs. Enumerating at most
C(20,4)=4,845 bases therefore decides the question exactly. Python independently
constructs full XOR spans instead of using the eight-point formula.

For rank six, retain PR3161/3162's dual-code oracle. If S has rank r>6, deletion
to rank six is equivalent to r-6 independent restricted character words with
support union of size at most twelve. Here r-6<=3. Enumerate the 511 ambient
nonzero characters and deduplicate restrictions. Three distinct words are
independent exactly when none is the XOR of the other two. Positive answers
carry cuts; Python checks negative answers and the complete direction list.

The native controls compare both oracles against exhaustive retained-subset
optima for all 4,096 subsets of a rank-nine twelve-point fixture at budgets
zero through twelve. The rank-four control additionally covers a twenty-point
fixture and its 210 one/two-point deletions. Its optimum table enumerates all
1,048,576 subsets. There are 109,239 decision comparisons in total.

The sharp fixture in `RESULT.json` has first mask
`(881632412340060325,35734196326400)` and second mask
`(4293210,52413606960)`, encoded as low/high 64-bit words. Its four qualifying
vectors are

```
(0,0,0,0,0,0,1,1)
(0,0,0,0,1,1,0,0)
(1,1,-1,1,1,-1,-1,-1)
(1,1,-1,1,1,-1,1,1).
```

Their rational span has dimension three. The second vector supplies the
rank-four anchor with the retained literal cut. All four rank-six directions
and their cuts are reconstructed and separately checked during replay.

## Application to the pinned TWOSIDE beta residue

Retain TWOSIDE's low-piece/fundamental-circuit hypotheses, stated explicitly
here. B is a linearly independent family of nine piece vectors. Each piece q_k
has support in a line set A_k whose binary label rank is its weight w_k. Set
T=span_K B and let C be the P112 root evaluation code. Assume dim(T intersect C)
is at least five, as in the `(b,t)=(5,4)` beta cell. These are inherited reduction
hypotheses, not consequences of the finite scan.

Consider the weight multiset

```
3,4,4,6,6,6,6,6,6.
```

Choose four pieces X0 with weights 3,4,6,6. Their support union has at most

```
4 + 8 + 20 + 20 = 52 < 53
```

lines. No nonzero combination of them is a codeword. Their images in
T/(T intersect C) are independent. That quotient has dimension at most four,
so they are a quotient basis and dim(T intersect C)=5.

For each of the five nonbasis pieces, subtract the unique combination of X0
with the same quotient image. The resulting five vectors c_y lie in C and are
independent: their B coordinates on the nonbasis pieces are distinct unit
vectors. Write c_y as the root evaluations of h_y. The evaluation map is
injective because the live roots span eight dimensions, so the h_y are five
independent directions.

Put the supports of the two weight-six X0 pieces in V1,V2. Let P be the union
of the other two X0 supports. It has at most 4+8=12 lines and is common to all
five c_y. Outside Lambda(V1) union Lambda(V2) union P, the support of c_y lies
in A_y. The remaining weights are 4,6,6,6,6. Thus all five directions belong to
H_6 and one belongs to H_4. The finite theorem gives span at most three, in
contradiction to independence.

This excludes exactly the named shape. Against the pinned historical PR3162
15-to-2 weight ledger, it leaves `2,5,5,5,6,6,6,6,6`. Concurrent PR3164 at
`857384079ab640a949fb7618b7909664d3e737e5` now reports both shapes excluded by a
different root-simplex argument. Our application corroborates one of its
exclusions; it is not a new unresolved-cell closure. Our finite theorem has no
nine-piece or root-simplex premise, so that theorem is a distinct result.
The preceding ledger and TWOSIDE reduction are inherited, not all replayed here.
In particular this is not a claim that all C5 cells, C1-C7, or C(P112)>=64 have
been proved.

## Controls that prevent an unjustified extension

The retained PR3162 rank-five witness checks that unstructured separate
twelve-deletion directions can span five. The rank-four anchor premise matters.

`CONTROL14.json` is a second exact witness: a rank-five anchor at deletion budget
fourteen coexists with five independent rank-six directions at that budget.
Its literal roots, masks and cuts are checked without the exploratory scanner.
Its cut union exceeds fourteen. It refutes that separate-set relaxation, not
the common-set conjecture or the remaining actual beta shape. Do not close the
remaining shape merely by changing four/twelve to five/fourteen in this theorem.
