# Joint funding of helper restrictions and owned-history caches

## 1. Result and exact scope

This is a necessary-budget obstruction for one source and one retained moment
criterion. It is not a multiplication lower bound, a new supplier, an attained
value of kappa, or a discharge of a foundational assumption.

The canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`. The native
word is the exact unselected #7481 word at
`89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`, with compressed SHA256
`acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
The complete retained #7113 caller has **17**, not 18, native invocations.
Its exact input and invoice bytes are pinned in SOURCES.json.

Let `f_k(r)=r^(1-k)` for positive ranks and `f_k(0)=0`. Let

    M(k) = sum_r (T_r-P_r) f_k(r)

be the exact complete #7481 signed moment. We allow the following changes to
each native invocation, with their most favorable possible accounting:

1. Restrict the 1,101 autonomous helper inputs, independently of all 400 main
   inputs. A retained set I of original helper coordinates must remain jointly
   arbitrary. Every other original helper target is fully debited at its old
   rank price. Newly decoded target types receive no original-coordinate credit.
2. Delete any original MOVE whose normalized value is identically zero on the
   promised input domain. All other original scalar contacts, frames, target
   labels and chronological values retain their original meanings on that domain.
3. Replace an owned MOVE by its exact target value using only the original
   strictly earlier history at its destination coframe. We grant the entire
   history, unlimited storage, arbitrary deterministic processing, free helper
   preparation, and free owned retirement. No imported observation or changed
   producer history is included. Pooling equal-span frame aliases only enlarges
   this information grant; it does not identify their physical operators.

The fine theorem allows arbitrary finite arrays `V=F^D`, `D>=1`, over
`F=R` or `C`, and arbitrary homogeneous **block-linear** helper promises
`ker U`. Their matrices may mix entries and need not commute. Original
normalized source maps remain the same rational scalar maps tensored with
`Id_V`. Sections2–6 first give the scalar derivation; BLOCK-LIFT.md proves
that every necessary-debit and composition bound survives arbitrary blocks.
No fractional physical jobs or newly decoded target credits are introduced.

The same fine bound holds for a main-independent C1 real helper submanifold
with a retained-coordinate submersion somewhere, or for a complex helper
submanifold with that property. A single common tangent preserves the finite
set of exact zero/cache dependencies without differentiating their decoders.
It also holds for any real-semialgebraic helper promise whose retained
projection contains a nonempty Euclidean open set: a regular stratum supplies
the required tangent. Complex arrays may be realified because the actual
normalized source coefficients are rational-real. The detailed reductions,
classical primary references and excluded discrete/nonregular cases are in
`extensions/TANGENT-PROOF.md`, `extensions/SEMIALGEBRAIC-PROOF.md`, and
`extensions/SCOPE-COUNTEREXAMPLES.md`.

**Fine theorem.** For `0<=k<=.01`, the net native saving of any such modification
is at most

    F(k) = f_k(5) + f_k(3) + 2 f_k(1) - 2 f_k(4).

Consequently the complete optimistic moment is at most `M(k)+17F(k)`. At
`k=.0038` this upper bound is less than `-25.25810999183538`. This upper
envelope is strictly decreasing on `[0,.01]` and has its unique zero in

    (0.0037347911502843961, 0.0037347911502843965).

This is a ceiling for the stated strategy and criterion, not a feasible
exponent. In particular, no strict positive moment is possible from
`k=.003734792` through `.01` in the fine model.

**Coarse theorem.** For `.01<=k<=1`, the same failure follows even for an
arbitrary nonempty main-independent helper promise surjective onto I,
including nonlinear and operator-valued preparations. Its net native saving
is at most 72, and exact interval bounds prove `M(k)+17*72<0` throughout that
whole interval. The fine linear/regularity hypotheses are not needed here.

The all-input source contract is essential. Scalar information separators
apply on the rational/complex normalized domain, and on digital input domains
that contain the stated exact input differences. No restriction on main inputs
may remove those directions. Neither theorem claims a result about a special
caller promise that abandons this arbitrary-main contract.

## 2. Source facts and the information obligation

Fresh exact replay of the 76,475 native instructions gives 6,279 MOVEs. Exactly
468 have nonzero helper-only normalized rows; the other 5,811 have a nonzero
main coefficient and cannot vanish on a nonempty main-independent helper
promise. The 468 helper rows have rank 463 and nullity five. For every such
row e and each helper coordinate h in its support,

    paid_rank(e) <= original_helper_target_rank(h).

The maximum paid rank among these rows is eight. Helper target ranks are
between one and nine. Rank prices are bound to actual independent frame bases
and nested entrance/exit or MOVE pairs; absolute dimension difference is used
only after that geometry is checked.

There are 47 owned MOVEs. For 33, an exact earlier-history separator can be
chosen entirely on the 400 main coordinates. Fix any permitted helper
assignment and vary mains in this separator direction. The two runs have
identical earlier histories but different target values. Therefore no
deterministic function of those histories can replace the MOVE, even with an
arbitrary helper promise. This is an indistinguishability argument, not a
restriction of providers to linear arithmetic.

Only these fourteen events remain possible after helper restriction:

    30581 30593 35152 35448 35452 36346 36358
    39875 39884 41646 42487 42500 44253 45656.

Their paid ranks sum to 32. Their unrestricted earlier histories still miss
their targets. For each such event E, let c_E be its scalar target row, P_E
the span of its original strict history, and H the helper-coordinate row space.
Define

    L_E = (P_E + span(c_E)) intersect H.

On a linear domain `all_mains x ker U`, exact deterministic recovery of c_E
from the observations P_E is equivalent to

    c_E in P_E + U.

Indeed, deterministic recovery requires c_E to vanish on the kernel of the
observation map restricted to the linear domain. The annihilator identity for
that kernel gives the displayed row-space condition. Conversely the condition
supplies a scalar linear recovery formula. This implication is not valid for
arbitrary nonlinear helper promises, which is why a nonlinear promise needs the separate common-tangent
reduction rather than a direct row-space inference.

An enabled cache therefore supplies a necessary relation
`u_E=c_E-p_E` in `U intersect L_E`. If `c_E` is not already in `P_E+Z`, this
relation lies outside Z. All source rows and histories in this argument are
reconstructed from the native bytes, rather than accepted from author tables.

## 3. Original-coordinate funding

For a row space V on the helper coordinates, define beta_f(V) as the minimum
sum of original target prices over a coordinate-column basis for V. This is
a lower bound on lost productive credit, not a cost of preparing V.

Let J be the fully debited helper coordinates, the complement of retained I.
Surjectivity of the promised helper domain onto I forces restriction `V -> J`
to be injective whenever all rows of V vanish on that domain. Otherwise a
nonzero relation supported only on I would vanish on every retained input,
contradicting joint arbitrariness. Thus J contains a column basis for V and
its lost target price is at least beta_f(V). This reasoning does not require
the helper promise itself to be linear.

Two elementary consequences will be used repeatedly.

**Independent-row funding.** Suppose rows z_e are independent and every
nonzero column h in row e has target rank at least its paid rank r_e. A
nonzero determinant minor has a nonzero permutation term. That term matches
each row to a distinct supported column. For any increasing f, the basis
price is at least `sum_e f(r_e)`.

**Basis extension.** If Z is contained in W, every column basis for W contains
a column basis for Z. In particular, `beta_f(W)>=beta_f(Z)`. If W has rank
`rank(Z)+1` and every nonzero column of W has target rank at least a, then

    beta_f(W) >= beta_f(Z) + f(a).

The support hypothesis concerns the entire enlarged space, not only its
newly appended row. Additional constraints cannot reduce these lower bounds.

For scalar constraints the price beta_f is computed exactly from prefix ranks.
Let C_a contain all helper columns with target rank at most a. The ordinary
linear-matroid exchange argument gives

    beta_f(V) = sum_(a=1)^9
        [rank(V restricted C_a)-rank(V restricted C_(a-1))] f(a).

All prefix ranks are exact rational ranks. A modular lower rank alone has the
wrong direction for certifying a minimum-price lower bound.

## 4. Why the local bills compose

The fourteen L_E spaces have total basis-row count 99 and joint rank 96.
Adjoin their basis rows to the 468 zero-MOVE rows. The resulting 567 labeled
row occurrences have exact rank 525 and nullity 42. Fundamental-circuit
components, coarsened to keep each entire L_E together, give a direct sum of
418 row spaces. Eleven contain caches: ten genuinely mixed groups and the
cache-only group 41646. Their ranks sum to 101. The 407 zero-only groups have
rank sum 424: 403 singletons, three five-row/rank-four groups, and one
eleven-row/rank-nine group.

Choose the actual deleted zero rows and one necessary witness for every
actual cache. Their spans V_g within these groups still form a direct sum.
Take any nonzero global column-basis determinant for their union. A Laplace
expansion by row groups has a nonzero term partitioning the selected columns
into local column bases. Therefore

    beta_f(direct_sum_g V_g) >= sum_g beta_f(V_g).

This is an inequality; equality is not asserted. It remains valid when the
groups' column supports overlap. It also remains valid when U has additional
cross-group constraints, since the selected direct sum is a subspace of U.
This is the step that prevents spending the same sacrificed helper target
separately in several attractive local modifications.

The zero-only groups have no positive gain for `0<=k<=.01`. Their independent
subsets are funded by support matching. All 31 dependent subset cases in the
four nonsingleton groups satisfy the exact rational inequality

    6 * minimum_linear_column_basis_price >= 11 * paid_rank_sum.

For ranks at most nine and `0<=k<=1/4`, `f_k(r)>=(6/11)r`; the integer control
`9*6^4<11^4` proves the endpoint. Also `f_k(r)<=r`. Thus the dependent subsets
are funded as well. The compact certificate is checked from source rows;
the previous global helper-funding package receives explicit predecessor credit.

## 5. Necessary debit for newly enabled caches

Fix one cache-containing group and a subset S of its zero-MOVE occurrences.
Write Z=span(S) and let A(S) be the caches already satisfying `c_E in P_E+Z`.
Credit all caches in A(S), even if an actual proposal would not use them.
Let N be the subset of other caches it additionally enables. There are at most
two cache sites in each group.

For `N` empty, the optimistic gain is

    sum_(e in S) f(r_e) + sum_(E in A(S)) f(r_E) - beta_f(Z).

For every E in N, the actual constraint space must contain
`Z+span(u_E)` for some `u_E in L_E outside Z`. Define

    gamma_E = min_(u in L_E outside Z) beta_f(Z+span(u)).

The actual debit is at least `max_(E in N) gamma_E`. We charge that maximum
and grant all A(S) and N cache benefits. We do not assert that one row realizes
several caches, or that the independent minimum debits are simultaneously
attainable. Each is a necessary condition, so their maximum remains valid.

The generic appended-row formula computes gamma_E. For any column set C,
the largest rank after appending one row from L_E is

    min(rank(Z restricted C)+1,
        rank((Z+L_E) restricted C)).

Whenever the rank can increase, the coefficient tuples that fail to increase
it form a proper linear subspace. Finitely many such sets cannot cover the
coefficient space over an infinite field. A generic rational row attains all
the prefix maxima simultaneously. Every special row outside Z has the same
full rank and no larger prefix ranks, hence no cheaper column basis. The
greedy prefix formula therefore gives gamma_E exactly. No bounded-height
physical preparation follows from this algebraic minimum.

Taking the maximum over all S and all N covers every actual proposal. In
particular, choose S to be its complete set of zero deletions. A relaxed row
that happens to create additional zero rows does not receive silent extra
credit; those rows are covered in their proper S case.

## 6. Local bounds and their finite certificates

| Cache sites | Zero rows in group | Native gain upper bound on `[0,.01]` |
| --- | ---: | --- |
| 35152, 45656 | 14 | 0 |
| 42487 | 6 | 0 |
| 35448, 35452 | 6 | 0 |
| 30593 | 4 | 0 |
| 36358 | 4 | 0 |
| 30581 | 1 | 0 |
| 36346 | 1 | 0 |
| 39875, 39884 | 1 | `f(5)+f(1)-f(6)` |
| 44253 | 1 | 0 |
| 42500 | 1 | `f(1)+f(3)-f(4)` |
| 41646 | 0 | `f(6)-f(4)` |

The largest group's fourteen zero rows are independent and supported only on
target ranks at least four. Cache35152 is outside their full quotient span.
Cache45656 is enabled by S exactly when S includes events45659,45661,45663
and58936. An exact quotient identity proves sufficiency; omitting each required
event from the full set proves necessity. Three of those required zero rows
are disjoint rank-four target units, each with paid rank one. Consequently
the already-enabled cache case is bounded by `4f(1)-3f(4)<0`.

If45656 is new, its entire L space and Z have support of target rank at least
four. Basis extension charges at least f(4) beyond beta(Z), even if both
caches are granted, giving `f(1)+f(2)-f(4)<0`. If only35152 is new, support
rank at least three charges f(3) for credit f(2), worsening the previous case.
These statements cover arbitrary constraint dimension. The original full
16,384-subset exploration is corroboration; the compact proof checks the
rank, support, quotient identity and four omission certificates directly.

In both six-zero groups, the zero rows are independent and no cache is in
the full zero-row quotient span. For42487, the entire relevant support has
rank at least four, which pays its rank-four cache credit. In the pair,
L35448 has support minimum three and L35452 minimum four, while all zero
supports have minimum four. Low-only, high-only and both-new cases have
bounds `f(2)-f(3)`, `f(1)-f(4)` and `f(1)+f(2)-f(4)` respectively. These are
nonpositive throughout the interval. The elementary inequality
`4^(99/100)>3`, certified by `4^99>3^100`, supplies the only near-linear
price comparison beyond monotonicity. Independent enumeration checked all
128 subsets and384 new-cache-set cases.

The remaining eight groups have only43 zero-row subsets in total. Exact
prefix ranks and the individual-gamma rule give89 cases. For each case a
recorded necessary-debit profile lies below the displayed ceiling throughout
`[0,.01]`. The interval check proves this, including ties at zero, by bounding
the derivative of the profile difference. If d(0) is its exact integer value
and B is a directed upper bound on d' throughout the interval, then

    d(k) <= d(0) + .01 * max(0,B) <= 0.

The three nonzero upper profiles telescope to F(k). No profile in this table
is asserted to have a physical realization or free preparation.

## 7. Complete moment and directed arithmetic

The complete native and caller inventories are reconstructed from the pinned
word and caller and compared with the pinned invoice. They contain22,461
productive fields and110,519 paid jobs, with linear-rank surplus1,424.
Each native modification repeats seventeen times; all other caller costs
are retained. Extra source acquisition, copying, restoration, recursive
children, ordinary work, precision and storage have been granted free, so
they cannot rescue a negative upper moment.

The numerical certificate bounds logarithms using the positive atanh series
after range reduction to `[1,2]`, with an explicit geometric tail. It bounds
`exp(-x)` using the signed Taylor remainder: odd degree35 is a lower bound,
even degree36 an upper bound for every `x>=0`. Every rounding is outward in
exact rational arithmetic. Derivative bounds use
`d f_k(r)/dk = -log(r) f_k(r)` and interval endpoints with the correct signs.
An independent checker brackets powers at `.0038` through the integer identity
`f(r)^5000=r^4981`; decimal values merely seed brackets whose inequalities
are then certified by integer exponentiation.

The fine envelope has derivative at most `-362106.78529987` on `[0,.01]`.
Its exact signs at the two stated rational crossing endpoints are opposite.
At `.0038`, its value is below `-25.25810999183538`; the required unmodified
net native saving exceeds3.48481964025734, whereas F(.0038) is below1.999049.
These are inequalities for the retained complete moment, not a new recurrence.

## 8. Coarse exclusion without linear helper promises

Let S be any set of zero-MOVE rows, and choose an independent row basis B
of S. Nullity is monotone under taking row subsets, so

    |S|-|B| <= 468-463 = 5.

The lost original helper targets fund all rows in B by the matching argument,
even for nonlinear or array-operator promises. The remaining at most five
occurrences can earn at most `5 f_k(8)<=40` for `0<=k<=1`. The33 main-only
information separators remain valid for every helper assignment. Grant all
fourteen remaining caches, without charging any further target loss or
physical expense; their credit is at most32. Thus the native gain is at most72.

It remains to verify the entire interval, not merely its endpoints. For each
closed rational interval `[a,b]` in the certificate, monotonicity in k gives
an upper bound on `M(k)+1224` by using upper `f_a(r)` for positive signed
invoice coefficients and lower `f_b(r)` for negative coefficients. The thirteen
certificate intervals meet exactly, begin at `.01`, and end at1. Their endpoints
have denominator1000; integer-power comparisons certify every endpoint price,
with decimal arithmetic used only to seed a candidate bracket. Every upper
bound is negative; the least negative is below `-170.4827884543`. This proves
the assertion throughout `[.01,1]`. Exact endpoint values alone would not
have sufficed.

## 9. What remains open

Changed producer histories can supply information absent from P_E. New
productive interfaces can change the target-debit rule. Main-dependent
promises can invalidate the main-only separators. Below `.01`, discrete
exact-grid or nonregular promises without an eligible common tangent remain
outside the fine theorem. Nonzero public-MOVE caches are also outside the
owned-cache budget. Those are explicit changes of hypothesis, not conclusions
of this proof. All five selected assumptions remain: native all-columns,
owned erasure, compiler closure, precision/tape, and analytic recovery.

The source and signed caller retain Clear1nsight's #7481 and Rohan Arun's
#7113 lineage and all predecessor notices. The earlier Jerry Chen / @CubeJerry
helper-funding and owned-history packages supply prior scoped results; this
package adds their joint cost allocation and the fine/coarse envelopes.
Classical linear algebra, matroid exchange, determinant expansion and Taylor
remainder arguments are not claimed as new. Substantial OpenAI assistance
covered research, separate implementations, adversarial review and packaging.
Independent evidence here is not independent human or proof-kernel acceptance.
