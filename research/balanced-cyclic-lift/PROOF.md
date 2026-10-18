# A determinant-balanced real cyclic leaf

Wentao Li, with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and changed mechanism

Let L>=1, let d in {-1,1}, and let b_i be exact real rational numbers with
|b_i|<=1/2. Define C by (Cv)_i=b_i v_(i-d mod L), and B=(I-C)^(-1).
All payload values lie on one grid u Z, u=2^(-w). Source x and target y are
length-L arrays. A length-L array z and a scalar h are borrowed with arbitrary
initial values. All four storage objects are distinct. The source is read-only.

The result adds an approximation to an **ordered** product B_n ... B_1 x,
and restores z, h and x exactly. Exact rational coefficient preparation and
ordinary clean scalar arithmetic are charged. This is a real, half-stable,
indexed reference contract; it does not instantiate PR628's full complex
prime-power factorization, a supplier word, or a fixed-tape implementation.

PR628's additive leaf restores its source and cannot be composed in place.
Its dirty product therefore uses nested additive commutators. This contribution
changes the leaf: it realizes the **enlarged** map diag(B,det(I-C)) by integer
lifts. A single scalar absorbs the nonunit determinant. The enlarged leaf can
be composed in place, then uncomputed. No clean checkpoint is assumed.

## Exact factorization for every cycle length

List cyclic positions in direction d as 0,...,L-1, renaming indices only in this
argument. Put a_j=b_(position j), p_j=a_0...a_j,
delta=1-p_(L-1), and t=1/delta. Since |a_j|<=1/2,

    1/2 <= delta <= 3/2,    2/3 <= t <= 2.

The equations for B are v_0-a_0 v_(L-1)=x_0 and
v_j-a_j v_(j-1)=x_j for j>=1. Consecutive row eliminations leave

    v_j - p_j v_(L-1) = z_j       (0<=j<L-1),
    delta v_(L-1) = z_(L-1),
    z_0=x_0, z_j=x_j+a_j z_(j-1).

Each row elimination has determinant one, so det(I-C)=delta. For L=1 there
are no causal or return additions and the sole equation is delta v_0=x_0.

In place, first execute z_j += a_j z_(j-1), j=1,...,L-1. Next scale the pair
(z_(L-1),h) by (t,delta). Finally execute z_j += p_j z_(L-1), j=0,...,L-2.
The exact rational result is (Bz,delta h), including for nonzero initial h.

The pair scale is four ordinary shears. With U(c) sending z to z+c h and
L(c) sending h to h+c z, its chronological word is

    L(-t), U(delta-1), L(1), U(t-1).

Indeed U(t-1)L(1)U(delta-1)L(-t)=diag(t,delta), since t delta=1.
Every factor therefore consists of 2L+2 shears: L-1 causal, four pair, and
L-1 return shears. This proof is uniform in L and in position-dependent signed
coefficients. Factor commutativity is never used.

## Rounded shears and exact restoration

Replace a shear q += c r by q += RN(c r/u) u, where RN is nearest integer
rounding with ties away from zero. Its exact inverse subtracts **the same**
rounded value. The source r does not change during that shear. Every shear is
thus a bijection on the two-coordinate integer grid. Reverse the word and
subtract its increments to obtain the exact inverse, for every initial value.

Directly overwriting the pivot by RN(t q/u)u would not suffice. For the legal
L=1 coefficient a=-1/2, t=2/3, integers 1 and 2 both round to 1. That loses
information. The borrowed scalar and the four-shear pair avoid this collision.
Neither clearing that scalar nor assuming it starts at zero is permitted.

## Length-independent error with exact coefficients

One rounded shear introduces error at most u/2. The causal pass's error at
position j obeys e_j<=e_(j-1)/2+u/2, hence e_j<=u.

For the pair alone, let its three possible rounding errors be r_1,r_2,r_4,
each at most u/2 in absolute value; L(1) is an exact grid addition. Starting
from exact pair inputs, the errors after U(delta-1) are

    e_z=(delta-1)r_1+r_2,    e_h=r_1.

After L(1), |e_h|<=5u/4 and |e_z|<=3u/4. After the final U(t-1),
|e_z|<=3u/4+5u/4+u/2=5u/2. The exact pair's final map is diagonal, so the
causal pivot error adds at most t u<=2u to the final pivot and **zero** to
the final helper. Therefore the pivot error is at most 9u/2, and the helper
error is at most 5u/4. Each other return coordinate has error at most

    u + |p_j|(9u/2) + u/2 <= 15u/4,

because |p_j|<=1/2. The rounded factor Khat satisfies

    ||Khat(v)-K(v)||_infinity <= 5u,
    K=diag(B,delta),             ||K||_infinity <= 2.

The norm bound uses the convergent Neumann series for B: ||C||<=1/2, so
||B||<=2, while delta<=3/2. The rounding bound depends on neither L nor the
initial dirt magnitude. Its **exact coefficient** hypothesis matters: rounding
coefficient tables without a separate perturbation budget is not allowed.

For n factors, let F=Khat_n ... Khat_1 and K=K_n ... K_1. Starting at the
same input, accumulated error obeys E_0=0, E_j<=2E_(j-1)+5u. Thus

    ||F(v)-Kv|| <= 5(2^n-1)u.

This is a proof of the stated error bound; the finite dense comparisons below
are regression evidence for the implementation, not its all-length proof.

## Two evaluations of the composed bijection

Execute the following, where pi projects away the helper scalar:

    (z,h) <- F(z,h);          y -= pi(z,h);
    (z,h) <- F^-1(z,h);
    z += x;
    (z,h) <- F(z,h);          y += pi(z,h);
    (z,h) <- F^-1(z,h);
    z -= x.

Each inverse is the exact inverse integer instruction word. The source and
borrowed storage are restored exactly. The net increment is

    pi(F((z,h)+(x,0))-F(z,h)).

The ideal enlarged product is diag(B_n...B_1,delta_n...delta_1); its difference
is exactly (B_n...B_1 x,0). The increment error is therefore at most

    10(2^n-1)u.

Choosing w=p+n+4 ensures absolute error <2^(-p). Actual rounding may make
the increment depend on initial dirt inside this error allowance. The replay
records all 25 small dirt states for a concrete one-factor example; it does
not claim exact dirt independence. A negative call uses the same calculations
and opposite target additions. Since the target is never a computational
source and the borrowed inputs are restored, this cancels the increment exactly.

## Complete cost recurrence and early cost screen

The cost unit differs from PR628's **additive** factor leaf. For n=55 its pinned
dispatcher uses 3,232 additive leaf calls and six dirty arrays. Here there are
220 executions of an **in-place stabilized factor**, one dirty array and one
dirty scalar. These counts are not a benchmark or an equal-price comparison.

Let P_i be the paid preparation cost of factor i, including validation,
L prefix products, delta, t, and the coefficient table. Let R_i price all
factor routing/returns and coefficient/source reads. Let A(Q,Hc) price the
nearest rational product with a Q-bit grid integer and a coefficient of Hc
bits, including multiplication, division, rounding, the destination addition
and writing the result.
Let J(Q) price an exact grid addition. If original coefficients have at most
H numerator/denominator bits, prepared coefficients have at most LH+O(1)
bits. One stabilized factor execution has complete arithmetic price

    C_i = (L-1) A(Q,H) + (L+2) A(Q,LH+O(1)) + J(Q) + R_i.

The three nonunit pair shears account for the +3 inside L+2; the unit shear
is J(Q). Even zero coefficients remain in this conservative bill. For the
ordered pipeline, C(empty)=0 and C(prefix+i)=C(prefix)+C_i. Its inverse has
the same conservative price. The whole additive interface costs

    T = sum_i P_i + 4 sum_i C_i
        + 4L J(Q) + R_source_target + V_admission.

The last four length-L passes are two source translations and two target
scatters. R_source_target prices their source reads, storage access and returns;
V_admission covers all input/grid/alias/coefficient checks. No recursive child,
closure scale, copy, inverse, helper restoration or table access is omitted.
At the indexed word level each shear uses two payload reads and one write, so
R_i includes 3(2L+2) payload accesses and 2L+2 coefficient reads per execution,
plus loop/indexing and any required returns. The four copy/scatter passes add
12L payload accesses. Writes already included in A or J may be omitted from R
to avoid double counting; they cannot be omitted from both. This reference's
word-access bill is explicit; a tape layout requires its own realization.
The reference records exactly 8n(L+1)+4L coordinate updates: **2,660** for
n=55,L=5. It does not charge a hidden n-factor recursive cancellation tree.

If initial physical magnitudes are at most D, factor endpoints satisfy
M_j<=2^j(M_0+5u), and M_0<=2D in either forward evaluation. A conservative
prefix bound uses a pivot bounded by 2M after the causal pass and a helper
bounded by M. The four pair prefixes have bounds 5M, 5M, 19M/2 and 14M;
their cumulative rounding deviations are at most 17u/2. The return pass
has smaller bounds. Thus every intermediate is at most 32(M+u).
Inverse executions exactly
retrace those states. Including target scatters, 2^(n+8)(D+u) bounds all mutable
payload magnitudes. For u<=1, Q=w+n+11+ceil(log2(D+1)) signed bits suffice.
Ordinary scalar multiplication/division workspace is additionally paid.

**The coefficient expense remains material.** An exact dyadic input can have
prefix denominators of length proportional to L. A fully stored coefficient
table occupies O(nL^2 H) bits; borrowed payload occupies (L+1)Q bits. With
schoolbook integer multiplication/division, A is bounded by O((Q+LH)^2), and
the complete arithmetic bound is

    sum_i P_i + O(nL(Q+LH)^2) + all routing/access/admission costs.

This does not inherit PR628's length-independent *coefficient word size* or
its fast approximate preparation. Truncating the tables, extending to complex
roots, scaling factors, translating arbitrary strides, and mapping all roles
of a transform require separate paid constructions. Source and helper words
also need a legal physical lifetime. Those are limitations of this result.

The favorable count does not establish a κ improvement: no narrower recursive
child, complete common-label word, replacement invoice or owner schedule is
provided. The selected #626/#543 profiles remain exactly the base profiles.
The bounded experiment therefore stops at this explicit interface construction
and its fully exposed coefficient/layout expense.

## Exact evidence and completed coverage

`verify.py` builds I-C independently and uses dense rational Gauss-Jordan
elimination. Exhaustive coefficients {-1/2,-1/4,0,1/4,1/2} through L=4 in both
orientations give 1,560 factors and 7,420 complete enlarged-operator columns.
Each factor is rounded on three initial dirty states, including 220-bit dirt:
4,680 cases, with exact inverse restoration. The observed maximum factor error
is 51/31 grid units, below the proved bound 5.

315 product executions cover n in {1,2,3,5,8,16,55}, L in {1,2,3,5,8}, grid
bits {0,16,80}, and three dirty magnitudes. Coefficients include signed eighths
and vary by position; orientations vary by factor. The generator is fixed at
`random.Random(55)`, and the seed-selected n=55,L=5 coefficients are retained
literally in the certificate. All outputs meet the dense-reference bound and
restore source/helper/data. Negative calls cancel exactly. The n55 fixture's
observed error is below 36 grid units; its 80-bit grid gives error <36*2^-80.

The 25 mathematical/admission controls include every single-shear omission in
one nonzero-coefficient factor, a noncommuting order witness, the pivot collision,
missing restoration, aliases, unstable/nonrational coefficients, invalid direction,
empty/mismatched factors and a Boolean sign. The original PR628 dispatcher is
extracted from its pinned source and executed with a counting leaf stub through
128 factors. This checks its call counts only; its numerical leaf is not replayed.

Source pins and predecessor credits are in SOURCES.json and NOTICE.md. No solver,
numerical search, optimality claim, proof assistant or new selected certificate
is used. The finite package does not discharge the multiplication theorem's
compiler, physical, precision/tape or analytic obligations.
