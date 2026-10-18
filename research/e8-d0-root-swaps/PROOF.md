# A root-swap rank bound and the remaining d=0 kernel case

This is a characteristic-zero theorem in the one-sided E8 lift model of
[PR2816](https://github.com/CrocSwap/integer-mult-bounds/pull/2816).
It closes the `d=0`, `ker(rho) intersect S != 0` branch listed as open in
[PR3074](https://github.com/CrocSwap/integer-mult-bounds/pull/3074).
The subsequent [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
names this same obligation C7; its other reductions are not premises here.
It does not prove L120 for the other branches, the two-sided decoder floor,
a supplier construction, or a multiplication-exponent improvement.

The proof separates a uniform, coefficient-preserving rank argument from
finite geometric inputs. The latter are recomputed by two implementations.
Exact predecessor versions and their roles are recorded in `SOURCES.json`.

## 1. Model and statements

Let Lambda be the even unimodular E8 lattice, with roots of squared norm 2.
Let E be its 120 unoriented root lines, with one root r_t chosen on each line.
Put V = Lambda/2Lambda, Q(x) = (x,x)/2 mod 2, and

    label(t) = (1, r_t mod 2) in F2 direct-sum V.
    beta((a,x),(b,y)) = ab + (x,y) mod 2.

Signs do not change labels or any support in this note. The 120 root classes
are exactly Q^{-1}(1). For distinct root lines,

    beta(label(s),label(t)) = 0 iff (r_s,r_t) != 0;
    beta(label(t),label(t)) = 1.

Fix the orthogonal frame F consisting of e1+e2, e3+e4, e5+e6, e7+e8,
e1-e2, e3-e4, e5-e6, e7-e8, in that order. This is the frame in PR2816.
Choose these displayed roots as the representatives on the frame lines.
Write P = E minus F, and rho for restriction from E to P.
For a vector v with coefficients in a characteristic-zero field K define

    w(v) = rank_F2 {label(t): v(t) != 0}, with w(0) = 0;
    cost(L) = min over K-bases B of L of sum_{b in B} w(b).

The code C_E is {p_h : h in K^8}, where p_h(t) = (r_t,h).
Its restriction is C_P. Each code has dimension eight. Real ranks of sets
of roots equal their ranks over K, because the root coordinates are rational.

A root t is **swap-eligible for L** if there is tau in L such that

    tau(t) != 0,
    supp(tau) subset {t} union {s: (r_s,r_t) != 0}.

The root t itself is permitted in this support condition. All *other*
orthogonal coordinates must vanish. Denote the eligible root set by R(L).

**Theorem A (weighted root-swap bound).** For every K-subspace L of K^E,

    rank_K {r_t: t in R(L)} <= cost(L).

**Theorem B (the d=0 kernel branch).** Let S contain C_E. Set

    T = (rho S)_{<=7},
    d = dim_K(C_P intersect T),
    Z = ker(rho) intersect S.

Here a subscript <=7 means the span of all vectors of weight at most seven,
not the set of such vectors. If d=0 and Z is nonzero, then cost(S) >= 72.
The bound is sharp in this branch: S=C_E+span(delta_f), for any frame root f,
has a basis delta_f, p_f-2delta_f and seven other frame codewords, of weights
1, 8 and seven times 9. Its restricted code is C_P, so d=0, and its kernel
contains delta_f.

## 2. A two-factor lemma, with its field scope made explicit

We use [PR1590, Lemma A](https://github.com/CrocSwap/integer-mult-bounds/pull/1590).
Its published proof is stated over Q. The same proof works over any field:
arbitrarily order the finite set of ratio values appearing below. No order
compatible with field addition or multiplication is needed.

Let M = p1 q1^T + p2 q2^T have nonzero diagonal on a finite index set I.
Let B be a binary matrix with diagonal one, such that B_st=1 for s!=t
implies M_st=0. Put R_j=supp(pj), A_j=supp(qj), and
r_j=rank_F2 B[R_j,A_j]. Then r_1+r_2 >= |I|.

For completeness, put D_j=R_j intersect A_j, X=D_1 intersect D_2, and
P_j=D_j minus X. Every index belongs to D_1 union D_2. A private index
in P_j supplies a unit row or unit column in B[R_j,A_j], because its
other-factor diagonal product is zero. Peeling these pivots leaves a block
containing B[X,X], so r_j >= |P_j| + rank B[X,X].

On X all four factors are nonzero. Set alpha(t)=p1(t)/p2(t) and
eta(t)=-q2(t)/q1(t). Then M_ts=0 iff alpha(t)=eta(s), while
alpha(t)!=eta(t). Choose any total order on the finite union of these
values and partition X into alpha<eta and alpha>eta. On either part,
the equality alpha(t)=eta(s) for B_ts=1 gives a strict order in one
direction. Ordering by alpha on the first part and eta on the second
makes the corresponding principal block unit triangular. Thus
rank B[X,X] >= max(|X_<|,|X_>|) >= |X|/2. Summing proves the assertion.
Zero factors include the one-factor case.

In particular, if dim L<=2, take any finite eligible set I and choose its
actual witnesses tau_t in L. Normalize tau_t(t)=1, and form M_st=tau_t(s)
for s,t in I. Its diagonal is one and its entries on orthogonal pairs vanish.
With B_st=beta(label(s),label(t)), write tau_t=c1(t)b1+c2(t)b2
using at most two basis vectors b1,b2 of L, padding with a zero factor
when needed. In the lemma's notation p_j(s)=b_j(s) and q_j(t)=c_j(t).
Each r_j is at most w(b_j): every row of its binary block is obtained
from the corresponding root label by the same linear map. Hence

    |I| <= w(b1)+w(b2).

This uses the same coefficient space L for every witness. Replacing L by
all vectors supported on its union support would not justify this step.

## 3. Proof of Theorem A

Write k=cost(L). If k>=8 the conclusion follows from the ambient root rank
eight. Suppose k<=7 and choose a minimizing basis q1,...,qa.
Call a basis member exceptional when

    rank_K {r_t: t in supp(qj)} > w(qj).

**At most one exceptional member.** Let O be the K-span of the supports of
all other members, viewed as root vectors. Then
dim O <= sum of their weights. An eligible root outside O has a witness
whose exceptional coefficient is nonzero; outside O that witness is a
nonzero multiple of the same exceptional vector q. Consequently any two
eligible roots outside O are nonorthogonal: evaluating one witness at
the other's coordinate gives a nonzero value. Their labels are beta-
orthonormal, hence independent over F2. Their number is at most w(q).
Therefore rank R(L) <= dim O+w(q) <= k. With no exceptional member the
union-of-spans bound gives the result directly.

**The smallest exceptional member.** A weight-one or weight-two support
has at most one or two roots, respectively. A weight-three support has
at most four roots, since all labels have first coordinate one. If its
real rank exceeds three, it consists of four independent roots r1,...,r4
whose labels sum to zero. Thus every signed half-sum

    v_epsilon = (epsilon1 r1 + ... + epsilon4 r4)/2

belongs to Lambda. Independence makes all sixteen half-sums nonzero.
Every one therefore has squared norm at least two. Their average squared
norm is exactly two. All sixteen norms equal two; expanding these
identities and taking the pairwise sign coefficients gives (ri,rj)=0
for i!=j. A weight-three exceptional support is an orthogonal quartet.
This is a lattice argument, independent of the correction coefficients.

**Two or more exceptional members.** Each costs at least three. With k<=7
there are at most two, and the only basis profiles containing two are
(3,3), (4,3), and (3,3,1). The first two have dim L=2 and are covered by
Section 2. In the last case let A and B be the two orthogonal quartets;
the weight-one member is a multiple of one coordinate unit delta_u.

If |A intersect B|>=2, the whole union support has at most 4+4-2+1=7
roots, so its rank is at most k=7. Otherwise suppose t!=u is eligible.
Its witness uses a quartet containing t with nonzero coefficient. Among its
three other roots, at most one lies in the other quartet
and at most one is u. At least one coordinate therefore remains nonzero
and orthogonal to t, a contradiction. This also covers t in A intersect B:
either nonzero quartet coefficient leaves such a coordinate. Thus only u
can be eligible. These cases exhaust all profiles and prove Theorem A.

## 4. Geometric inputs and the root-only reduction

The following finite E8 facts are recomputed from two coordinate models;
they are not read from predecessor PASS receipts.

1. Every nonzero p_h in C_E has weight nine. Equivalently, for each of the
   511 binary label hyperplanes, its root complement has real rank eight.
2. Maximum numbers of root lines in label flats of dimensions 1,...,8 are
   bounded by (1,2,4,8,12,20,36,64). The uniform proof below gives all eight;
   the finite checks cover dimensions 1,...,7 and directly enumerate all
   511 label hyperplanes to check the dimension-eight cap of 64 in both models.
3. For each root r, its 56 nonself nonorthogonal root lines span the
   binary hyperplane W_r=label(r)^{perp_beta}. Every nonzero binary
   character on this remainder has support at least 24.

The first two facts agree with the retained E8/P112 code facts of PR2816
and the full-E8 cap calculation in PR2985. The distinction between full
E8 caps and P112 caps matters here.

Here is also a short proof of the full cap bounds. The quadratic Gauss sum
of Q on V is 16. A label w-flat either misses first-coordinate-one entirely,
or meets it in an affine (w-1)-flat A=x0+U of V. In the latter case Fourier
summation gives

    sum_{x in A} (-1)^Q(x)
      = 16/|U^perp| sum_{y in U^perp} (-1)^(Q(y)+(x0,y)).

A quadratic function with zero constant term on an n-dimensional binary
space has Gauss sum either zero, positive 2^n when its polar rank is zero,
or plus/minus 2^(n-r/2) with even polar rank r>=2. Its negative sum is
therefore no smaller than -2^(n-1). For w=5,6,7 this bounds the displayed
sum below by -8, giving at most 12,20,36 nonsingular points in A.
For w<=4 use the trivial bound 2^(w-1). For w=8 the dual dimension is
one, where the sum cannot be negative, giving at most 64 points.

**Root-only lemma.** If a correction space U in K^P has cost(U)<=6 and
w(p_h|P+tau)<=8 for some tau in U and nonzero h, then h is proportional
to one of the 120 E8 roots, including the eight frame directions.

Choose a minimum basis of U. The cap bounds give union support size<=20
and union label rank<=6. A hyperplane H containing the corrected support
therefore has

    |Off_P(h)| <= 64+20=84,
    Off_P(h) minus H subset supp(tau),
    rank_F2 labels(Off_P(h) minus H) <= 6.

Completeness uses the parabolic root-intersection argument of PR2816 C3,
not the RRC census. The roots perpendicular to h contain at least 28
nonframe lines. Every root intersection with a real subspace is Weyl-
conjugate to a standard parabolic subsystem: take a generic real normal
whose vanishing roots are precisely that intersection, and use its Weyl
point stabilizer. Among the 256 standard parabolics, ranks<=5 have at
most 20 root lines. The qualifying proper types are exactly

| rank | subsystem | root lines | normal object |
|---:|---|---:|---|
| 7 | E7 | 63 | a root line |
| 7 | D7 | 42 | a primitive norm-four line |
| 7 | E6+A1 | 37 | a norm-six line |
| 7 | A7 | 28 | a primitive norm-eight line |
| 6 | E6 | 36 | an A2 normal plane |
| 6 | D6 | 30 | an orthogonal-root normal plane |

The rank-seven normal norms follow from the fundamental-weight calculation.
The rank-six normal planes contain respectively three and two root lines.
Generic members of each plane have one common support; exceptional members
have a larger perpendicular subsystem and are in the rank-seven cases.

The independently regenerated deletion profiles below consider every
binary hyperplane H and keep all normal objects with |Off_P(h)|<=84.

| family | total objects | (Off size, minimum deletion size, objects) |
|---|---:|---|
| norm four | 1080 | (70,14,128), (73,13,896), (76,12,56) |
| norm six | 3360 | (77,25,2688), (79,24,448), (80,24,224) |
| primitive norm eight | 8640 | (84,28,1024) |
| A2 normal planes | 1120 | (78,26,896), (80,24,224) |
| orthogonal-root normal planes | 3780 | (82,26,448), (84,24,2688) |

Every norm-four deletion of size at most twenty has label rank at least seven;
the other families require at least 24 deleted lines. Neither can be supplied
by U. Only root directions remain. The norm-four rank test is essential: its deletion
cardinalities alone are insufficient.

This argument covers every characteristic-zero field because all the
filter's hypotheses are zero-pattern conditions: they use only which
rational root rows vanish, and the resulting fixed binary supports and ranks.
For any such pattern realized by h over K, let V_Q be the rational kernel
of its zero rows. Each designated nonzero row is nonzero on V_Q; otherwise
it would vanish on V_Q tensor K, which contains h. A finite union of proper
rational hyperplanes cannot cover V_Q, so a rational point realizes exactly
the same zero and nonzero rows. The normal-family and normal-plane tests
therefore apply to it with unchanged hypotheses. Once this rational
representative is forced to a root line,
its zero rows span that root's rank-seven perpendicular system. The original
K-vector has the same zero rows, hence belongs to the same one-dimensional
K-root line. No positivity of the coefficients of h is assumed.

The parabolic inventory also shows that every proper root intersection has
at most 63 lines. Thus every nonzero word in C_P has at least 112-63=49
nonzero coordinates, whereas a weight-at-most-seven support has at most 36.
Consequently (C_P)_{<=7}=0. This supplies the d=0 assertion for the sharp
examples in Section 1 without importing a predecessor codeword census.

## 5. From feasible directions to actual root swaps

Suppose cost(L)=k<=7 and L contains a nonzero vector supported on F.
Restriction removes at least one positive-weight basis member: choosing
independent restricted basis images gives

    cost(rho L) <= k - dim(ker(rho) intersect L) <= 6.

If dim L>=2, a minimum basis has at least two positive weight parts, each
at most six. The cap table shows its full union support has size<=21,
maximized by the partition 6+1. If dim L=1, the nonzero kernel forces
L to be supported on the eight frame coordinates, so the bound still holds.

Let p_h+ell have full weight<=8 for ell in L and h!=0. The root-only lemma
applied after restriction makes h a root direction. Scale h to a root r.
The 56 nonself nonorthogonal coordinates of p_r, after removing supp(L),
still span W_r: fewer than 24 deletions cannot reduce their rank. Any
hyperplane containing supp(p_r+ell) is consequently W_r itself.
Choose r to be the fixed representative r_t of its root line. Its own root
coordinate and every coordinate orthogonal to r lie outside W_r. Thus
ell(r_t)=-2, and ell vanishes at all other orthogonal coordinates. Choosing
the opposite normal representative instead gives +2 at that coordinate;
rescaling the witness leaves exact-swap eligibility unchanged.
It is an actual root-swap witness. Conversely any such witness, after
scaling its own coordinate to -2, gives a vector supported in W_r.

Therefore the span of all feasible h directions has dimension
rank R(L)<=k by Theorem A. The strict full remainder bound 24>21 is why
the P112 remainder's smaller deletion threshold is not enough here.

## 6. Proof of Theorem B and exact downstream scope

Suppose, to obtain a contradiction, that cost(S)<=71. Put L=S_{<=7}.
Since rho L is contained in T and C_P intersect T=0, and rho is injective
on C_E, we have C_E intersect L=0. Thus S/L has dimension at least eight.
A greedy minimum basis of S consists of a minimum basis of L and
at least eight members of weight eight or nine. Nine such members would
already cost 72. There are exactly eight, their code directions are
independent, S=C_E direct-sum L, and k=cost(L)<=7.
Here greedy basis selection uses the nested spans S_{<=j}: at each weight,
extend an independent set to a basis of that span. Any basis must contain
at least dim S-dim S_{<=j} members above weight j, so this construction
minimizes the total weight and justifies the simultaneous basis choice.

Also T=rho L: T contains rho L, and any additional element of T would,
after subtracting its rho L part, give a nonzero element of C_P intersect T.
Writing a kernel vector as c+ell in C_E direct-sum L similarly shows
Z=ker(rho) intersect L. In particular L has the nonzero frame-supported
vector required by Section 5.

If t of the eight high basis members have weight eight, the cost is

    k + 8t + 9(8-t) = 72+k-t.

Cost<=71 forces t>=k+1 independent feasible code directions. Section 5
and Theorem A bound their span by k. This contradiction proves Theorem B.

PR3074 originally lists this kernel branch separately from the 38 open d>=4
rows, seven prior-only rows and seven conditional E6-slack rows. The newer
PR3154 claims further ledger closures and retains the kernel case as C7,
alongside C6 (DEG2) on the one-sided track. Its CONJECTURES.md and
checks/L120D0/NOTES.md Section 4 use the same definitions as Theorem B.
The theorem here removes C7 directly. No other PR3154 closure is imported or
independently validated here; C1-C6 and a complete L120 proof remain outside
this result.

## 7. Credit and evidence boundary

DreamingOfClouds' PR2816 supplies the one-sided lift model, weight/peeling
framework and parabolic reduction; PR2862 supplies the predecessor
carrier argument for restricted cost at most three; PR2985 supplies full
E8 cap context; PR3074 states the open kernel branch and padding implication.
PR3095 clarifies the field scope and normalization boundary. PR1590's
two-factor lemma is reused, with the finite-order field clarification above.
PR3154 and Discussion3156 provide the latest C7 statement and handoff.
Classical E8 lattice, quadratic-space and root-system facts retain their
original mathematical status; no new general lattice theorem is claimed.

The new work is Theorem A's shared-coefficient argument, its application
through the full remainder and restricted normal filters, and the completed
kernel-branch implication. Prepared by conorholds with substantial OpenAI
Codex assistance, including GPT-6.1 SOL agents at xHigh reasoning.
Finite replays support the stated inputs and controls. They are not a
proof-assistant certification or independent human review.
