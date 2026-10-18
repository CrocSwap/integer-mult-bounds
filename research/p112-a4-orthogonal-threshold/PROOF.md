# The sharp five-endpoint support threshold is twenty-eight

Let K have characteristic zero. Let P be the 112 E8 root lines outside
an orthogonal eight-root frame F. With rational root representatives r_t,
let C be the evaluation code `{(<r_t,h>)_t : h in K^8}`.

**Theorem.** Suppose `a_1,...,a_k,q_0,...,q_4` are collectively independent
vectors in `K^112`. Let S be the union of the a_j supports. If `|S|<=28`
and every q_i has support at most twenty, their span T satisfies
`dim(T intersect C)<=3`. The common-support threshold 28 is sharp for this
arbitrary-support contract: the witness below has `|S|=29` and intersection
dimension four.

PR3211 proved the same conclusion at support26. The new step keeps the
orthogonality of the puncture instead of bounding eight arbitrary deletions.
The proof adapts PR3207's A5 variance argument to five endpoints. The new
support29 witness realizes the boundary with independent pieces.

## Geometric dependencies

We use the retained E8/P112 model of PR3211, with its earlier geometry in
`research/p112-ten-piece-simplex/geometry.py`. The replay authenticates and
executes that unchanged source, reconstructing all roots and simple-root
coordinates. It checks evaluation injectivity, all 960 simple reflections,
the six-node parabolic maximum 36, seven-node counts
`42,28,22,14,16,23,37,63`, and all 7,140 root planes.

The standard real Weyl-chamber theorem then gives minimum nonzero live
support 53 and classifies every direction of live support strictly below
70 as a scalar root direction. The field-extension argument is the one
in PR3211: rational perpendicular roots of a K-valued direction of support
below 70 have rank at most seven. Rank at most six would give a generic real normal with
the same perpendicular roots, contradicting the parabolic bound of 36
when at least 43 live roots are perpendicular. Thus their rational kernel
is one-dimensional, and the direction is a K-scalar multiple of its
rational generator. The Weyl-chamber theorem remains a written dependency.

Three root lines in a plane form A2 when a third line exists. Its coefficients
have ratio plus or minus one in norm-two root coordinates. The rational
plane statement extends to K by an invertible rational coordinate minor.
It follows, as in PR3211, that five affinely independent vertices whose
edges are root directions form one common nonzero scalar multiple of an
A4 root simplex `0,v_1,...,v_4`, where `<v_i,v_j>=1+delta_ij`.

Every such A4 star is Weyl-equivalent. The replay verifies this by successive
extension orbits of sizes `240,56,27,16`, under reflections perpendicular
to the already chosen prefix. Those reflections fix that prefix pointwise.
Retaining every subgroup orbit covers every extension; each inventory is
one orbit. Evaluating one representative therefore proves the complete
120-root cost spectrum, with cost defined below:

```
cost 0: 10 lines
cost 1: 50 lines
cost 2: 60 lines
total cost: 170.
```

The orbit check and spectrum are reimplemented here, with PR3211 credited
for the argument. No binary flat-capacity census is needed by this
arbitrary-support theorem. Neither this proof nor its replay admits a supplier.

## Orthogonality limits the frame cost to thirteen

Normalize roots to squared norm two. For a root r, put

```
x_i=<r,v_i>,  v_0=0,
k(r)=5-max_z #{i:x_i=z},
V(r)=sum_i (x_i-mean(x))^2=(1/5)sum_{i<j}(x_i-x_j)^2.
```

All five x_i are integers. If k=1, at least four pairs are unequal, so
`V>=4/5`. If k=2, every equality class has at most three members. The
partition 3+2 minimizes unequal pairs at six, so `V>=6/5`. These lower
bounds use only integrality and equality-class sizes. The complete spectrum
above ensures no root coordinate has cost above two.

Any orthogonal eight-root frame satisfies `sum_F rr^T=2I`. The A4 Gram
matrix gives `sum_i ||v_i||^2=8` and `||sum_i v_i||^2=20`. Consequently

```
sum_F V(r)=2*(8-20/5)=8.
```

Let c_j count cost-j roots in F. The variance bounds imply

```
8 >= (4/5)c_1+(6/5)c_2,
c_0+c_1+c_2=8,
3c_0+c_1>=4.
```

Thus `2c_0+c_1>=3`. Indeed, if c_0>=2 the left side is at least four;
if c_0=1 then c_1>=1; if c_0=0 then c_1>=4. The total frame cost is
therefore

```
c_1+2c_2=16-2c_0-c_1<=13.
```

Moving the simplex by a Weyl transformation moves F to another orthogonal
frame, so the estimate applies to the original fixed puncture. A common
nonzero K-scalar changes no equality classes. The real variance calculation
therefore bounds exactly the same support counts over K.

After the frame and at most s common live coordinates are removed, the
remaining cost is at least `170-13-2s=157-2s`. At s=28 this is 101.
The earlier arbitrary-puncture estimate gives only `170-16-56=98` there.

## Quotient normalization proves shortening

Assume `D=T intersect C` has dimension at least four. Then `Q=T/D` has
dimension at most k+1. The images of all k small pieces and any one endpoint
are independent: a nonzero relation would give a nonzero codeword supported
on at most `28+20=48<53` coordinates. Collective independence of the original
pieces excludes a zero combination. Hence `dim Q=k+1` and `dim D=4`.

Modulo the small images, all five endpoint images are nonzero in one
dimension. Rescale them to agree there, preserving supports and independence.
For suitable small-piece combinations s_i, define

```
c_0=0,  c_i=q_i-q_0-s_i in D, i=1,...,4.
```

The four c_i are independent by their unit coefficients on the independent
q_1,...,q_4. Injective evaluation supplies independent directions h_i.
Every edge has support at most `28+20+20=68<70`, so all are root directions.
The preceding plane argument gives the A4 simplex.

Outside S, endpoint values equal the five vertex evaluations plus one
common coordinate shift. At coordinate t, at least k(r_t) endpoints are
nonzero, whatever shift is used. Thus their total support is at least
`157-2*28=101`, exceeding their total allowance `5*20=100`. This contradiction
proves the theorem. It also covers fewer than 28 common coordinates.

## An actual support29 counterexample

Use geometry.py's doubled representatives r_t of squared norm eight, in the
original fixed P112 order. The doubled directions in WITNESS.json are

```
h_1=(1, 1, 1,-1, 1, 1,-1, 1)
h_2=(2, 0, 2, 0, 0, 0, 0, 0)
h_3=(1,-1, 1, 1, 1, 1,-1, 1)
h_4=(2, 0, 0, 0, 2, 0, 0, 0).
```

They have diagonal Gram entries eight and off-diagonal entries four.
Put `c_0=0`, `c_i(t)=<r_t,h_i>/4`, and take the 29 cuts in WITNESS.json.
At every coordinate choose z_t to be the most frequent of the five c_i
values, breaking ties by the smaller value. Define four small pieces and
five endpoints by

```
a_i(t)=c_i(t) on S and zero elsewhere,
q_i(t)=0 on S and c_i(t)-z_t elsewhere.
```

The primary checker reconstructs all literal sparse endpoint coefficients.
The small supports have union S. The endpoint support sizes are
`20,19,20,20,20`, totaling 99. The actual fixed frame has cost thirteen;
the 29 cuts each have cost two. Thus the support-sum bound 99 is attained.
At twenty-nine cuts the proof's strict inequality fails because the actual
independent-piece counterexample exists, not merely because a relaxation fails.

The rational checker verifies ranks `rank(a)=4`, `rank(q)=5`, `rank(T)=9`,
`rank(C)=8`, `rank(T+C)=13`. Moreover `c_i=q_i-q_0+a_i` gives four independent
codewords in T. Therefore `dim(T intersect C)=9+8-13=4`.
A separate checker reconstructs roots through lattice membership, reads the
literal endpoints, checks these relations and nonzero minors modulo 101.
The modular ranks give rational lower bounds only. The four independent
exact relations give the matching upper bound `rank(T+C)<=9+8-4=13`.
No modular zero is used to assert a rational upper bound. All identities and
nonzero rational minors survive extension to any characteristic-zero field.

## Scope and credit

This improves PR3211's general five-endpoint threshold from 26 to the sharp
value 28. PR3211 retains its two historical profile exclusions. We count no
additional TWOSIDE profile as newly excluded. Original binary support-rank
constraints are stronger than this arbitrary-support contract; the counterexample
is not asserted to satisfy them. Full C5, `C(P112)>=64`, physical suppliers
and kappa remain separate obligations. The selected result is unchanged.

Credit Nick Petalas/PR3211 for five-endpoint normalization and the A4 spectrum,
PR3207 for the Parseval method, PR3205/3203/3188/3176 for the support and
geometry lineage, and DreamingOfClouds/PR3154 for TWOSIDE. The retained decoder
lineage includes joaqcoo. SOURCES.json records exact public heads and source
pins. New work is Apache-2.0 and used substantial automated assistance in
construction, exact checks and internal review. Human and proof-kernel review
are separate from this finite evidence.
