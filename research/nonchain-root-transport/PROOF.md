# Paid mixed transport across the chain bridge

CubeJerry, with substantial OpenAI GPT-6 Astra Pro assistance. Apache-2.0.
The normalized root, native profile and original caller are due to
DreamingOfClouds with Claude Opus 5.5, building on the contributors named in the
retained source headers. This note changes their stage supports and idle lines.

## 1. Scope and normalization

Fix the exact #6833 head `51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`
and its eighteen unit native stages. There are twenty fields
`A,f0,...,f8,h0,...,h8,E`, nine left queries, three thin bridge queries and nine
right queries. Write a normalized query as

\[
 T_k(S)=I+(S-1)x_ky_k,\qquad S^2=1,
\]

with the source's explicit integer columns and rows. The source sign Gram is
`y_i x_j = sign(i-j)`. Thus the complete query word is `S I`, as checked at both
roots of `S²-1`. The source normalization converts this final `S` to `Q^-1`.
Every coordinate containing `w` fresh stages therefore has target rank `8w+1`.
All fields are independent arbitrary inputs.

We retain all eighteen native calls and all three thin queries. The native
productive and paid histograms are read from the retained `pricing.py`; they
are not edited or inferred from a headline exponent. The price is eighteen
copies of that complete native bill plus 104 copies of every outer target,
thin-query debit and whole-idle debit. Ordinary basis work is not credited as
negative cost. No new multiplication exponent or compiler theorem is claimed.

## 2. Enlarged coordinate masks

For parameters `(p,q)`, add the last `q` right fields to left masks `L_p,...,L_8`,
and add the first `p` left fields to right masks `R_0,...,R_(8-q)`.
The original query columns and rows are unchanged. The two investigated masks
are `(4,4)` and, after its favorable bill lost, `(1,2)`.

Every enlarged mask still contains its query column and row and commutes with
that query's complete prefix. The verifier checks this exactly, entry by entry,
for the whole matrix, not on a distinguished input vector. Let `P_i` denote a
stage mask and `D_i` its independent formal stage multiplier. Since all `P_i`
are coordinate projectors, they commute with each other. Induction gives

\[
 \prod_{i\text{ in time}} [(I+(D_i-1)P_i)T_i]
 = S I\prod_i[I+(D_i-1)P_i].
\]

Here the displayed product convention is execution in time order, with later
operators on the left. At the induction step, commutation with the current
query prefix moves the new diagonal factor to the common right-hand product.
This proves the arbitrary-input diagonal identity for all independent stage
variables. It is not a numerical specialization of the `D_i`.

For `(1,2)`, the added fields are `h7,h8` on `L1,...,L8` and `f0` on
`R0,...,R6`. Relative to #6833, its exact per-port target change is

\[
 2[129]+[137]-2[73]-[65].
\]

Brackets denote one target or paid request at that rank, not a dimensionless
coefficient. The unchanged target ranks and their multiplicities remain in the
complete report.

## 3. Two actual mixed bridge carriers

Let `f=f0`, `u=h7`, and `v=h8`. Across the interval
`L1,...,L8`, all three thin queries, `R0,...,R6`, define

\[
\begin{array}{c|c|c}
 &\phi&\gamma\\\hline
1&f+v&2A^*-f^*-u^*+2v^*\\
2&-f+u&2A^*-f^*+v^*
\end{array}
\]

These are dual: `gamma_i phi_j = delta_ij`. For every actual query in the
interval, including each thin bridge query,

\[
 y_k\phi_i=0,\qquad\gamma_i x_k=0.
\]

Thus the two projectors `E_i=phi_i gamma_i` commute with every `T_k(S)` for both
values of `S`, and each lies inside every covered stage mask. They support two
legal whole idle jobs, each covering fifteen full stages and costing rank 120.
This is mixed left/right transport. It does not assume a free conjugator between
unrelated hub planes, and does not merely check the bridge at `S=-1`.

For comparison, the source left idle has column `f_j` and row `f_j* - 2A*`.
Its row pairs to 2 with every right native column, so that source line cannot
continue unchanged across the right arm. Enlarging the masks is essential to
the mixed construction above.

The remaining idle dimensions are filled as follows. Source left lines on
`f1,...,f7` retain their intervals of lengths 7 down to 1. The left remaining
line, on the eight-stage left interval, is

\[
 \phi_L=f+u+v,\quad\gamma_L=-2A^*+f^*+u^*-v^*.
\]

Source right lines on `h1,...,h6` retain intervals of lengths 1 through 6.
The right remaining line, on the seven-stage right interval, is

\[
 \phi_R=f+u+v,\quad\gamma_R=f^*+u^*-v^*.
\]

Finally, a separate one-stage idle at `R7` has column `v` and row `2A*+v*`.
The verifier checks unit duality and mutual dual orthogonality of every pair of
jobs overlapping any stage. At each full stage,

\[
 A_i=P_i-\sum_{j\text{ covering }i}E_j
\]

is an idempotent of rank two, fixing the native column and row. The explicit
ordinary basis uses columns `x_i`, `A_i e_A`, the idle columns and standard
coordinates outside `P_i`. Its inverse is integral; all entries in both matrices
have numerator bit length at most two. Thus this modified interface does not
hide a non-dyadic scalar or an unavailable basis map.

Whole idle factors can be grouped at the first covered stage: each commutes
with the intervening queries, masks, other covering idle projectors and the
resulting native active projectors. Expanding a whole factor into its individual
`D_i` factors therefore recovers the stage identity in section 2.

The complete construction has eighteen whole idle jobs. Its per-port idle
change is

\[
 2[120]+[8]-[64].
\]

There is no thin-query saving, retired field or surrendered native helper.

## 4. Uniform loss for this explicit construction

Subtracting its old bill, the per-port signed-moment change is

\[
 2\,129^t+137^t+64^t
 -2\,73^t-65^t-2\,120^t-8^t.
\]

The vector `(137,129,129,64,0,0)` majorizes
`(120,120,73,73,65,8)`: their prefix sums are respectively
`137,266,395,459,459,459` and `120,240,313,386,451,459`.
Both sums equal 459. Strict concavity of `x^t` gives a strict loss for every
`0<t<1`. More generally the non-strict loss holds for every concave tariff with
`f(0)=0`. This comparison includes the changed productive target credits;
it is not an idle-cost-only comparison.

At `C=0.0033718004755`, `t=1-C`, the complete eighteen-native-call gain lies in
`(-45.137633381995714,-45.137633381995712)`. The unchanged source gain lies in
`(-0.000000000734153,-0.000000000734151)`. Exact rational enclosures, rather than
floating-point root finding, establish these signs.

## 5. Optimistic bound for every interval idle schedule on the two masks

The explicit construction is not presumed optimal. Consider all fixed ordinary
rank-one idle projectors that are supported on every stage of a full-stage
interval, annihilate every actual query between its endpoints, and are mutually
dual-orthogonal whenever their intervals overlap. Fractional job counts and
simultaneously incompatible choices of different interval carrier spaces are
allowed in the relaxation below. This makes its paid bill favorable.

For an interval `I=[a,b]`, let `M` be the intersection of its coordinate masks.
Let `Y` contain all query rows between its endpoints, restricted to `M`, and
`X` contain all intervening query columns restricted to `M`. The primal idle
space is `ker Y`; the dual idle space is the annihilator of `im X`. The rank of
the pairing between these two spaces is exactly

\[
 c_I=|M|-\operatorname{rank}Y-\operatorname{rank}X+
              \operatorname{rank}(YX).
\]

Indeed `ker Y` has dimension `|M|-rank Y`; its pairing radical is
`ker Y intersect im X`, of dimension `rank X-rank(YX)`. This proves the formula
without treating nonzero primal and dual nullspaces as a dual idle line.

Every collection of jobs whose intervals contain `I` consists of independent
dual projectors in this common pairing space. Hence its size is at most `c_I`.
Let `z_J >= 0` count jobs on each of the 171 nonempty full-stage intervals.
Every legal schedule satisfies

\[
 \sum_{J\supseteq I}z_J\le c_I,\qquad
 \sum_{J\ni i}z_J=|P_i|-2.
\]

Minimize `sum_J z_J (8|J|)^t`. This charges every idle dimension and allows all
common carrier capacities, including carriers unrelated to the explicit source
lines. All 171 capacities are recomputed by exact rational Gaussian elimination.
For the original masks every interval crossing the bridge has capacity zero.
For `(1,2)`, the interval `L1` through `R6` has capacity exactly two; for `(4,4)`,
`L4` through `R4` has capacity exactly six.

The saved certificate contains rational LP dual variables `alpha_I <= 0` and
unrestricted `beta_i`. Replay checks every dual column

\[
 \sum_{I\subseteq J}\alpha_I+\sum_{i\in J}\beta_i
 \le (8|J|)^t.
\]

It then lower-bounds paid cost by `sum_I alpha_I c_I + sum_i beta_i(|P_i|-2)`.
The exact power enclosures use a finite rational atanh series for logarithms
and alternating Taylor bounds for `exp(-C log r)`; no solver is used in replay.
The complete gain upper bounds, including all native and outer credits, are

| Masks | Complete gain upper bound |
|---|---:|
| `(4,4)` | `-68.1289200947679` |
| `(1,2)` | `-36.7785606995188` |

The floating-point LP was used only to propose a dual certificate. Exact replay
checks its signs, all columns and the final strict negative bound. No optimality
or integrality assertion about the discovered primal solution is required.

## 6. Coverage limits

This resolves the two declared enlarged-mask transport targets before any broad
search. It is not a barrier for arbitrary masks, arbitrary non-shortest roots,
stage-dependent carrier lines or a factorization outside the interval/orthogonal
idle contract. The fixed query word, unchanged native source and the rank tariff
are explicit hypotheses. The source native all-column/owned-erasure proof,
compiler, precision tape and analytic recovery remain inherited assumptions;
this package does not independently rerun them. No selected or pending frontier
is changed.
