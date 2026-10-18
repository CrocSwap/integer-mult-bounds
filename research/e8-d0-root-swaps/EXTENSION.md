# A cost-seven extension and a C1 subcase

Prepared by **conorholds** with substantial OpenAI Codex assistance.
Use the characteristic-zero model, labels, binary weight and cost in
[PROOF.md](PROOF.md). This note strengthens its restricted root-only filter
and closes one precise subcase of DreamingOfClouds'
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154),
`checks/CONJG2/NOTES.md` Section 2 and `checks/CONJ-G/NOTES.md` Section 0.
It does not close C1 in full. The registered replay regenerates the finite
geometry below in two coordinate models: [extension_check.py](extension_check.py)
checks the new cost-seven data and fixtures; the primary geometry checkers
retain the norm-six, A2 and full-root-remainder tables from PROOF.md.
The C1 decoder consequences assume PR3154's d=0 rigid shape, corrected
ledger identity `cost(D') = sum_j w(A_j) - n_c`, pivot rebate
`epsilon_k in {0,1}`, and N8 (at most eight corrections with distinct
corrected frame indices). This package does not validate that broader
reduction. The geometric Theorems C and E have their own stated hypotheses.

## 1. Root-only filter at cost seven

**Theorem C.** Let U be a subspace of K^P with dimension at least two and
cost(U) at most seven. If h is nonzero and

    w(p_h|P + tau) <= 8,       tau in U,

then h is proportional to an E8 root, possibly a frame root.

In particular, applying C with U=T in PR3154's d=0 rigid shape resolves
CONJG2 Section 2(ii) for every minimum correction cost kappa<=7: no
weight-eight high member has a nonroot D7/E6-type normal. This is independent
of the actual low-basis total Sigma. It makes no assertion for kappa=8 or
about the remaining invoice and coefficient obligations.

Choose a minimum-weight basis q_1,...,q_a, with weights w_j and total k<=7.
Every w_j is positive, a>=2, and hence every w_j<=6. The cap bounds in
PROOF.md imply that the union B of their supports has at most 21 points:
the largest permitted profile is (6,1). Its binary label rank is at most k.
Choose a binary hyperplane H containing the corrected support. Then

    D = Off_P(h) minus H is contained in B,
    |D| <= 21,  rank(D) <= 7,  |Off_P(h)| <= 64+21 = 85.

Thus at least 27 full E8 root lines are perpendicular to h. The parabolic
argument of PROOF.md Section 4, including its transfer of rational support
patterns to any characteristic-zero field, applies at threshold 27. The
same six proper types qualify: D6, E6, A7, E6+A1, D7 and E7. As before,
their possible nonroot normals reduce to norm-four, norm-six and primitive
norm-eight directions, A2 normal planes, and orthogonal-root normal planes.

The old tables exclude the norm-six and A2 families by deletion cardinality
at least 24. Their full-E8 Off sizes are respectively 83 and 84, so
restriction to P cannot add any Off-85 rows for either family. Raising the
Off cutoff from 84 to 85 adds exactly these rows:

| Family | Off size | Minimum deletion | Number |
|---|---:|---:|---:|
| Primitive norm-eight directions | 85 | 25 | 3,584 |
| Orthogonal-root normal planes | 85 | 25 | 448 |

The earlier rows of these two families also have minimum deletion at least
24. For all 1,080 norm-four directions and all 511 binary hyperplanes,
the complete inventory with deletion size at most 21 is:

| Deletion size | Binary rank | Number of normal/hyperplane pairs |
|---:|---:|---:|
| 12 | 7 | 56 |
| 13 | 8 | 896 |
| 14 | 8 | 128 |

Only the first row could meet the correction budget. Its 56 normals are
exactly the lines f_i+f_j and f_i-f_j for distinct frame vectors. For each,
D consists of six disjoint pairs of root labels with a common nonzero XOR.
The union of any two pairs is a four-element binary circuit: the total XOR
is zero, distinct labels exclude two-element dependencies, and their common
first coordinate 1 excludes odd dependencies. These circuits connect every
element of D. Consequently its rank-seven binary matroid is connected:
every nontrivial bipartition D=A union A' satisfies

    rank(A) + rank(A') >= 8.

This follows directly from the circuit definition of matroid connectedness;
alternatively, a rank-additive partition splits the two spans into a direct
sum, so every circuit would lie wholly in one part, contradicting the
pair-union circuits. Both coordinate implementations check the six-pair
certificate for all 56 configurations. An additional private independent
probe checked all 4,094 nontrivial subsets of each configuration.

Here is the coefficient-independent covering step, which allows arbitrary
overlap of correction supports. Assign each point of D to one basis member
whose support contains it, producing parts D_j. If there is only one
nonempty part, that basis member has weight at least seven and another
positive-weight member exists, contradicting k<=7. Otherwise select one
nonempty proper part D_i. Connectedness and rank subadditivity give

    8 <= rank(D_i) + rank(D minus D_i)
      <= sum_j rank(D_j) <= sum_j w_j <= 7,

again a contradiction. This excludes the last nonroot case and proves C.

## 2. Two sharp boundary examples

The dimension hypothesis in C is essential. In ordinary norm-two root
coordinates take

    h = (1,1,1,1,0,0,0,0),
    H = {labels r : 1+(h,r) = 0 modulo 2},
    tau(r) = -p_h(r) outside H, and 0 inside H, on P.

Its twelve nonzero entries have label rank seven, so U=span(tau) has
dimension one and cost seven. The corrected support has weight eight and
h is nonroot. Every deleted coordinate is essential, and this H contains
no frame labels. The registered check records literal coefficients and an
eight-label basis of the corrected support. There are no eligible exact
root swaps in this fixture; it does not contradict Theorem A or C7.

Nor can the cost bound be raised to eight, even for carrying members. Take

    h = (1,1,1,0,1,0,0,0),     u = e3+e5,
    D = {r in P : |(h,r)|=2},
    q0 = -p_h on D minus {u}, and zero elsewhere,
    U = span(q0, delta_u),     tau = q0-2 delta_u.

Here |D|=13, rank(D)=8, rank(D minus {u})=7, and U has profile (7,1).
The corrected support has weight eight and its actual label span contains
four frame labels, those for e3+e4, e3-e4, e5+e6 and e5-e6. The minimum
cost is exactly eight: it is at most eight by the displayed basis, while
the union of supports has binary rank eight, a lower bound on every basis
weight sum. This is a boundary example for the
root-only lemma, not a complete decoder or a counterexample to C1.

## 3. Four corrected weight-eight root directions

Retain the d=0 rigid basis shape in PR3154 CONJG2 Section 2. There is a
low basis F_T of T, dim(T) in {2,3}, and eight high members
q_l=p_{h_l}+tau_l of weights eight or nine. Their h_l form a basis of K^8.
The row functional dual to h_l is denoted mu_l. A corrected high member
has mu_l proportional to some frame functional f_j, and its support-label
span contains that frame label z_j. The frame indices of corrected members
are distinct, as in the source's normalization/Lemma D.

Suppose cost(T)<=7. Theorem C forces every **weight-eight** high direction
to be a root. No claim about weight-nine directions is needed. A frame-root
direction cannot be corrected: every tau in T has support contained in
the union B of the chosen basis supports, of size at most 21. Hence the
56-point P support of its codeword
retains its rank-eight span W_j after at most 21 deletions, since the full
root-remainder minimum deletion is 24. Thus a corrected support of rank
eight has span W_j, which contains no frame labels.

For m corrected weight-eight members their nonframe root directions r_i
therefore have distinct matched frame indices j_i, with

    (r_i,f_j_i) != 0,       (r_i,f_j_s) = 0 for s != i.

Every nonframe E8 root has exactly four nonzero frame pairings, all +/-1:
the squared pairings sum to four. Any two such four-element incidence
supports have even intersection, since their inner product is one half
the signed sum on the intersection and is integral.

If m>=6, each root would have to use its own matched index and at least
three of at most two unmatched indices, impossible. If m=5, each must use
all three unmatched indices, so two incidence supports intersect in three
places, also impossible. Hence m<=4. The finite check supplies a sharp
four-index matching. The exclusion of frame roots is necessary: allowing
them admits eight private matched indices.

## 4. A complete C1 subcase, with one unit of slack

**Corollary D.** In the preceding d=0 shape, suppose the actual low basis
has total weight

    Sigma = sum_{q in F_T} w(q) = 7.

Then the corrected one-sided invoice is at least 65, and the pivot invoice
in PR3154's Conjecture G is at least 64.

Indeed cost(T)<=7 and dim(T)>=2. Let n_T count corrected low members,
n_8 corrected weight-eight high members, c_9 all weight-nine high members,
and c_9,corr their corrected subset. A low member carrying an excluded
frame label has weight at least three: a binary span of rank at most two
contains no first-coordinate-one label other than its generating root
labels. Thus n_T<=2. Section 3 gives n_8<=4, while c_9,corr<=c_9, so

    n_c = n_T+n_8+c_9,corr <= 6+c_9.

The exact source invoice is the raw weight minus one for each corrected
member; its possible pivot rebate epsilon_k is either zero or one. Hence

    corrected invoice >= 64+Sigma+c_9-n_c >= 65,
    pivot invoice     >= 65-epsilon_k >= 64.

The same proof also covers actual Sigma=8 if cost(T)<=7: the corrected
invoice is then at least 66 and the pivot invoice at least 65. The support
bound uses a minimum basis of T, while n_T<=2 uses the actual basis total;
these are distinct quantities. No such conclusion is claimed for cost(T)=8.

This settles every pivot choice in the stated Sigma=7 subcase. It uses
neither F1 nor the unfinished T_v coefficient step, and it does not assume
an actual-swap conversion on the P112 remainder at union size 21.

## 5. A sharp F1 support threshold

The F1 condition in PR3154 CONJ-G Section 1 asks whether vanishing on
O_v forces the normal direction to be v; write O_v for its O_{l_v}.
The source does not explicitly define O_v in its prose. Its identity
`Off(c_v) intersect O_v = {v}` together with
`N(v) = Off(c_v) minus {v} = P minus O_v`
([CONJ-G notes, lines 21 and 39](https://github.com/CrocSwap/integer-mult-bounds/blob/708f0ad8928c383de8294aea3c126e9461d2066d/research/p112-reduction-to-conjectures/checks/CONJ-G/NOTES.md#L21),
[f1.py, lines 2 and 10-12](https://github.com/CrocSwap/integer-mult-bounds/blob/708f0ad8928c383de8294aea3c126e9461d2066d/research/p112-reduction-to-conjectures/checks/CONJ-G/f1.py#L2))
determines the set used here. Since `Off(c_v) = {r in P : (r,v)!=0}`,
for a nonframe root v it is

    O_v = {r in P : (r,v)=0} union {v}.

This set has 60 elements; its complement in P has 52, matching the source
checker's assertions. The registered replay constructs and checks it afresh.

**Theorem E.** If h is nonzero, |supp(tau)|<=24, and p_h|P+tau vanishes
on O_v, then h is proportional to v. The number 24 is sharp.

The cancellation condition gives

    |Off_P(h)| <= 52+24 = 76.

Thus at least 120-(76+8)=36 full root lines are perpendicular to h. Exactly four
proper parabolic types qualify: E7, D7, E6+A1 and E6, with respectively
63, 42, 37 and 36 root lines. The same support-pattern/field argument as
in PROOF.md reduces h to root directions, norm-four or norm-six directions,
or a generic A2 normal plane. Norm-six directions have Off_P at least 77
and generic A2 planes at least 78, so both are excluded by cardinality.
The check also enumerates norm-six directions with Off_P=77 to establish
the sharp boundary below.

The two coordinate implementations regenerate the following minima for
the required cancellation support Off_P(h) intersect O_v:

| Direction | Minimum support | Coverage |
|---|---:|---|
| Root other than v, including frame roots | 26 | All 112 pivots and 119 other root lines |
| Norm four | 30 | All 112 pivots and 1,080 normal lines |
| Norm six with Off_P<=77 | 25 | All 112 pivots and 2,688 normal lines |

Every direction except v therefore needs more than 24 cancellations.
This proves E for any characteristic-zero field. The registered fixture
records the nonroot norm-six normal h=(0,0,0,1,-2,0,-1,0), pivot
v=(0,0,0,1,0,0,1,0), and all 25 literal coefficients
tau=-p_h on Off_P(h) intersect O_v. Their corrected word vanishes on O_v,
so replacing 24 by 25 would be false. This is an actual failure of the F1
extension, not a decoder counterexample.

This tau has weight seven. Choose the unit delta_u at the first listed
nonzero coordinate u. The other 24 coordinates still have binary rank
seven. Therefore U=span(tau,delta_u) has dimension two and exact cost eight:
every vector outside the unit line retains those 24 nonzero coordinates
and has weight at least seven; every basis pays at least 7+1. The same g
violates unrestricted F1 in this (7,1) correction space. This does not
construct an admissible complete C1 decoder or its high basis. In this
fixture (h,v)=0, so the extra nonzero evaluation condition in CONJ-G
Section 2 case (A) is absent; pivot-aware replacements remain possible.

As a consequence, F1 holds for every tau in a correction space of dimension
at least two and cost at most seven (support union at most 21). It also
holds for every correction space of dimension three and cost at most eight:
the cap table bounds its union support by 22, attained by profile (6,1,1).
Thus the entire F1 step for C1's d=0, dim(T)=3 rigid branch is discharged.
This does not settle its other swap/carrier or coefficient conditions. For
dim(T)=2 and cost eight, profile (7,1) can have support 37; no complete F1
claim is made for that remaining case.

## 6. The cost-eight (7,1) invoice branch

**Theorem F.** In the d=0 rigid shape of Section 3, suppose the actual
low-basis total is eight and T admits a minimum basis with weights (7,1).
Then the corrected invoice is at least 65 and the pivot invoice at least 64.
This includes the minimum profile of the F1 counterexample in Section 5;
it does not require the false unrestricted F1 implication there.

Let delta_u generate the unit line in a minimum (7,1) basis. Every vector
of T outside that line has weight at least seven: a vector of smaller
weight together with delta_u would contradict cost(T)=8. Therefore an
actual basis of total eight also has profile (7,1). At most one low member
can be corrected, because a unit cannot carry an excluded frame label.
The full support B of T has at most 36+1=37 coordinates by the cap table.

Suppose the corrected invoice were at most 64. Its raw value is 72+c_9,
and normalization gives n_c<=8. Hence c_9=0 and n_c=8: all eight high
members have weight eight and at least seven of them are corrected. Let J
be their distinct matched frame indices. If |J|=8, each high direction is
its own frame direction. If |J|=7, let k be the unused frame index. Duality
forces each corrected high direction with matched index j to lie in
span(f_j,f_k), with nonzero f_j coefficient.

The Off_P patterns in this plane are exhausted by f_j, f_j+f_k, f_j-f_k,
and a generic f_j+2f_k. Indeed nonframe-root frame pairings are 0 or +/-1,
so the only cancellation ratios with both coefficients nonzero are +/-1.
This classification holds over every characteristic-zero field.

For each of the 56 ordered frame pairs and each of the 255 binary
hyperplanes H containing z_j, the registered check forms

    D = Off_P(h) minus H.

For each of the three nonframe strata, all 14,280 cases have rank(D)=8
and no coloops: removing any one label still leaves rank eight. But any
correction in a (7,1) space has the form alpha*a+beta*delta_u for a
weight-seven word a. Cancellation outside H requires
`D subset supp(alpha*a+beta*delta_u) subset supp(a) union {u}`.
Thus D minus {u} has rank at most seven, a contradiction. Only the frame
stratum can survive. Its genuine survivors are retained as positive controls;
the proof does not exclude
frame directions using this rank test.

There are therefore at least seven corrected high members whose normal
directions are their own distinct frame directions. Each frame codeword's
56 nonzero P coordinates span W_j, which contains no frame labels. A
corrected member's hyperplane H contains z_j and differs from W_j, so
at least 24 of those original coordinates must be canceled, by the full
root-remainder bound. Every canceled coordinate lies in B.

Every nonframe root has nonzero pairing with exactly four frame vectors.
Summing the necessary cancellations over the seven corrected frames gives

    7*24 = 168 <= sum_{r in B} number of selected frames nonorthogonal to r
                <= 4*|B| <= 4*37 = 148,

impossible. The corrected invoice, an integer, is at least 65; subtracting
the possible unit pivot rebate leaves at least 64.

Both coordinate models check all plane patterns and hyperplanes. The fast
no-coloop test performs binary elimination while retaining dependence
masks: its nullspace-basis supports cover every point exactly when there
is no coloop. Selected cases are compared directly with every one-point
deletion rank; a separate private implementation independently checked every one-point
deletion in all 42,840 nonframe cases. Frame positive controls are retained
by the registered check.

This closes only the minimum (7,1) profile at actual total eight. Minimum
profiles (6,2), (5,3), (4,4), other dimensions and the other C1 cases require
separate arguments. Section 5's component counterexample remains valid;
the aggregate invoice obstruction excludes the full decoder branch.

**Residual F1 corollary.** The entire F1 obligation in PR3154 CONJG2
Section 2(iii) is discharged for surviving d=0 rigid-shape candidates with
corrected invoice at most 64. The source reduction gives kappa=cost(T)
<=Sigma<=8. If kappa<=7, the support union is at most 21. If kappa=8 and
dim(T)=3, it is at most 22. At kappa=8 and dim(T)=2, the complete minimum
profiles are (7,1), (6,2), (5,3) and (4,4). The first forces actual Sigma=8
and is excluded by F; the other three have union caps 22, 16 and 16.
Every remaining case therefore satisfies E. This is a proof for the
surviving low-invoice candidates, not an unrestricted F1 statement about
the eliminated (7,1) spaces. The other C1 inequalities and coefficient
obligations remain open.

## 7. What remains open and what Lean checks

C7 is proved in PROOF.md. Under the inherited rigid-shape assumptions,
Theorem C settles CONJG2 Section 2(ii) for kappa<=7. The exact C1 invoice
cases of Corollary D and Theorem F, and the residual F1 obligation from E/F,
are discharged here. Other C1 cases and C2-C6 remain outside this package's
closure claim. In particular the
cost-eight carrying example prevents simply extrapolating Theorem C.
Other basis totals and C1's coefficient/pivot conditions require further
arguments; the new lemma is not a complete L120 or multiplication proof.

Two Lean files check separate parts of Theorem A, with actual coefficient
witnesses: [RootSwapOneExceptional.lean](formal/RootSwapOneExceptional.lean)
proves the generating-family rank bound under explicit pairing hypotheses
when every member except a distinguished one has root-support rank at most
label-support rank; [RootSwapQuartet.lean](formal/RootSwapQuartet.lean) proves the
low-overlap two-quartet/singleton case.
[RootSwapConnectedCover.lean](formal/RootSwapConnectedCover.lean) additionally
proves Section 1's generic rank-cover contradiction, with actual label-span
ranks and overlapping supports, assuming the connectedness inequality.
All three were compiled with the
repository's Lean/mathlib v4.21.0 pins, with no warnings, sorry, custom
axioms or unsafe declarations. Their printed axioms are only propext,
Classical.choice and Quot.sound.

These are partial formalizations: the E8/label instantiation and
characteristic-zero rank bridges, exceptional-support classification,
two-factor lemma, high-overlap quartet bound, finite geometry and final
greedy C7 assembly remain written proofs and executable finite checks.
Theorems C/E/F and Corollary D are not complete Lean formalizations.
