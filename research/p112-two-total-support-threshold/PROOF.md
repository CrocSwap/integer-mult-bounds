# Exact support thresholds for the fixed P112 coordinate readers

## Contract and statement

Use the P112 coordinate matrix `X` and binary labels/duals from
`research/p112-single-lift/reference-geometry.json`. Write `x_j` for its
eight columns, `S_j = supp(x_j)`, and

    beta(d,s) = rank_F2 (v_i dot l_t)_(i in supp(d), t in supp(s)).

The pinned geometry has `|S_j|=56` and `beta(x_j,x_j)=8`. For any set of
ports `T`, let `b_j(T)=beta(x_j, 1_(S_j\T) x_j)`: only the source columns in
`S_j\T` are retained. Then the exact thresholds for `b_j(T) <= 8-d`,
`d=1,...,8`, are, **for every** `j`, respectively

    w_d = (24,36,44,48,52,54,55,56).

In particular, deleting at most 23 sites from a coordinate source cannot
lower its COPY rank. At 24 sites, all 63 first-drop sets for each reader
are enumerated. Across the eight readers there are 476 distinct sets:
448 belong to one reader, and 28 belong to two, exactly one common set for
each pair of readers. None belongs to three. The smallest port set which can
lower three coordinate ranks simultaneously has size 40. The three-reader
statement is about a *freely chosen deletion set*, not the attainable cost
of a two-total factorization.

For the exact ten-term identity considered by Philipp / @mightyOil,

    XX^T = XT^T + DZ^T,       D=XA,       T=X-ZA^T,

let `T_source = supp(z_1) union supp(z_2)`. Any retained source `t_j`
agrees with `x_j` outside `T_source`; it may also have additional nonzero
positions. Adding source columns cannot decrease binary rank, so

    beta(x_j,t_j) >= b_j(T_source).

Consequently `|T_source| <= 23` forces all eight retained costs to remain
eight, and the two added costs are nonnegative. The complete separate-total
COPY sum is at least 64, for **arbitrary complex coefficients**, without
assuming independence or a particular coefficient support. The added-term
argument below extends this no-saving range to `|T_source| <= 43`, using
the predecessor's rank-one/off-column theorem. More generally,
`|T_source| < w_d` prevents a rank drop of `d` in any retained term. If
`|T_source| < 40`, fewer than three retained terms can drop at all. These
are necessary support restrictions; no floor is claimed beyond the
`|T_source|<=43` corollary.

## Why the finite enumeration proves the thresholds

For fixed `j`, put `V_j = span_F2{v_i : i in S_j}`. The source-bound
geometry gives `dim V_j=8`. Define the linear evaluation map

    E_j : V_j -> F2^(S_j),     q -> (q dot l_t)_(t in S_j).

Its image `C_j` has dimension eight, since `beta(x_j,x_j)=8`. For deleted
ports `T`, the nullity of evaluation on `S_j\T` is `8-b_j(T)`.
Thus `b_j(T)<=8-d` exactly when a `d`-dimensional subspace `U` of `C_j`
has its coordinate support contained in `T`. The minimum possible size
of `T` is the `d`-th generalized support weight of `C_j`.

`verify.py` constructs eight independent evaluation words from the actual
duals and labels, then enumerates every subspace of `F2^8` once by its
unique reduced row echelon basis. For each pivot set it allows exactly the
entries right of a pivot and outside all pivot columns to vary. The number
of enumerated spaces by dimension is

    255, 10795, 97155, 200787, 97155, 10795, 255, 1.

The support of a subspace is the bitwise union of its basis words, because
all combinations vanish at a coordinate exactly when all basis words do.
The minimum over all spaces gives `w_d`. The verifier checks these counts,
all eight weight sequences, each explicit minimizing witness, and that
removing any single port from such a witness restores at least one rank
unit using a **direct restricted-pairing rank** calculation. It also
reconstructs the geometry from the pinned root generator and checks every
Gram and binary pairing entry; no floating-point or finite-field proxy for
complex matrix rank is used.

Each `C_j` has one zero word and nonzero weight distribution
`24^63, 28^128, 32^63, 56^1`. For the cross-reader statement, the
verifier maps all 63 weight-24 words for each reader back to the common
112-port index set and compares them exactly. To exclude a triple below
40, it considers all 254 nonzero words of weight below 40 for each reader.
For every reader triple, it forms all pair unions of size below 40 and
checks that none can be enlarged by a third word while staying below 40.
An explicit union of three weight-24 words has size 40, and direct
restricted-pairing ranks confirm all three drops. This does not assume the
three deletions can be produced by two source columns.

## Added-total charge and the 43-port floor

The preceding argument controls only retained terms. To price added terms
in the predecessor's remaining full-rank case, `verify.py` also replays an
exact 511-functional census independently of the predecessor checker. For
each nonzero nine-bit `q`, it computes the rational rank of `X[I_q,:]`,
where `I_q={i:q dot v_i=1}`. Exactly 503 matrices have rank eight. The
other eight have rank seven, with one coordinate-axis kernel each. None
of the 112 distinct live source labels equals an exceptional `q`.

Let `d=Xa` be a nonzero added reader with arbitrary complex coefficients.
If the span of its active dual labels had dimension below eight, two
independent binary functionals `q_1,q_2` would annihilate every active
dual, and so would `q_1+q_2`. Each of these three nonzero `q` places
`a` in the kernel of `X[I_q,:]`. A full-rank `X[I_q,:]` forces `a=0`;
otherwise all three are exceptional, and the census shows the eight
exceptional kernels are distinct coordinate axes, so again `a=0`.
Thus its dual span has dimension at least eight. Further,
every live source label is visible to `d`: an invisible label would be
an exceptional `q`, but no source label is exceptional. Rational and
complex ranks agree for these integer matrices, so complex cancellation
does not invalidate the argument.

For a nonzero source `z` with `m` distinct live support sites, let
`r=beta(d,z)`. Evaluation on the reader's dual span has a kernel of
dimension at most one in the nine-bit label space. The `m` distinct source
labels all lie in the preimage of an `r`-dimensional image space, which
contains at most `2^(r+1)` labels. The visibility fact also gives `r>=1`.
Therefore

    beta(d,z) >= min {r>=1 : m <= 2^(r+1)}.                (A)

This is the rank-nullity support bound of Hanson Sun / @bbMisk's PR1432
(there sharpened to `m <= 2^(r+1)-1` because labels are nonzero), applied
to an arbitrary nonzero on-column reader. The 511-functional census is
Mihir Srivastava's #845 premise (503 full-rank functionals, eight
coordinate kernels), recomputed independently here. The weaker form (A)
already suffices through union 43.

Now assume the exact two-total factorization has both `A` and `Z` of
complex rank two. Both added reader and source columns are nonzero. If
their source support sizes are `m_1,m_2`, their union `M` satisfies
`m_1+m_2>=M`. The verifier minimizes the sum of (A) over all positive
`m_1,m_2<=M` with this constraint, for every `M=1,...,43`. For `M<24`
the retained rank loss is zero. For `24<=M<36`, each reader loses at most
one rank unit and fewer than three readers can drop, so total loss is at
most two; the added bill is at least five. For `36<=M<40`, each reader
loses at most two units and still fewer than three readers can drop, so
total loss is at most four; the added bill is at least five.

For `40<=M<44`, each reader loses at most two rank units, since its third
generalized weight is 44. The complete cross-reader cut census shows at
most four readers can drop: every union of four nonzero cut words below 44
is one of exactly 42 sets of size 40, and every fifth reader's cut needs at
least four further ports. Also, the original coordinate supports meet
pairwise in exactly 24 ports. Two readers each losing two rank units would
need a union of at least `36+36-24=48` ports, so at most one of the four
can lose two. Total retained loss is at most five, while the added bill is
at least six. The full-rank case therefore has COPY sum **strictly above
64** throughout `M<=43`.

Philipp / @mightyOil's predecessor theorem already proves COPY sum at
least 64 if either added matrix has rank at most one, either reader leaves
`col_C(X)`, or the coordinate coefficient supports are disjoint. Combining
that result with this full-rank on-column screen proves the no-saving
corollary for **every exact two-total factorization retaining the eight
coordinate readers with source union at most 43**, regardless of complex
coefficients. The new part is the bounded-support argument; the theorem
does not independently re-prove the predecessor's complementary cases.

## Sharp two-total rank-drop fixture

For readers 0 and 1, the common 24-port minimum cut is ports `0..23`.
Let `C` be that set and let `x_0|C`, `x_1|C` be the two coordinate vectors
restricted to it. Set

    a_0 = (1,1),       a_1 = (1,-1),       a_j=(0,0) for j>=2,
    z_1 = (x_0|C + x_1|C)/2,
    z_2 = (x_0|C - x_1|C)/2.

The two `A` columns overlap on both coordinates and have complex rank two.
The sources are nonzero on disjoint twelve-port halves, so `Z` also has
rank two. `D=XA` and `T=X-ZA^T` make the complete 112-by-112 identity exact.
The retained COPY ranks are `(7,7,8,8,8,8,8,8)`; both added terms cost
seven, for **total 76**. Removing port 0 from both sources restores all
retained costs to eight (total 78). The verifier checks every matrix entry
and all ten restricted pairing ranks. This proves the 24-site rank-drop
threshold is attained *inside* the predecessor's remaining rank-two,
overlapping-coefficient case; it is not a cheaper decoder.

## Limits and predecessor credit

This result does not bound arbitrary large source unions, certify a
ten-term COPY optimum, or price frames, preparation, restoration, hosting,
recursive children or an all-size supplier. `beta` is the inherited
separate-total pairing-rank charge under DreamingOfClouds' PR446/PR717
model. A different delivery architecture could have a different bill.

Philipp / @mightyOil established the predecessor rank-one, off-column and
disjoint-coordinate-support reductions. The single-lift floor is due to
Mihir Srivastava (#845) and its complex extension to @woklerx (#998).
The P112 coordinate geometry and cost descend from DreamingOfClouds and
Joel Pulikkan / GamingPuzzled, with earlier E8 work cited by those packages.
The first weight `w_1=24` is @commdata2338's PR1375 erasure distance of
a coordinate support (`research/p112-two-coordinate-small-rectangle/`).
This note adds the higher weights `w_2..w_8`, the cross-reader cut
thresholds, and their combination with the added-term charge in the
predecessor's remaining two-total case. PR669 (the-missionary-company)
computes generalized weights of signed proper-star codes, a different
code. Prepared for Josie Elliston by OpenAI Codex (offline session 17);
reviewed, corrected and published by Claude (Anthropic, session 19).
Substantial AI assistance. Apache-2.0; no independent human review or
full multiplication theorem.
