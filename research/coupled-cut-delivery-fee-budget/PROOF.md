# Exact recursive fee budget for a hypothetical coupled cut delivery

Prepared for ToikY with substantial source-aware OpenAI Codex assistance.
Apache-2.0. This is a fixed selected-invoice relaxation, not a native transport,
new selected saving or resolution of a framework assumption.

## 1. Changed hypothesis, retained source bill

zxv's PR6083 explicitly excludes grouped delivery from its negative theorem.
It keeps the selected PR6030 invoice, grants at most two new binary helper
splits per added eligible coordinate per LOCAL, and charges at least one new
positive-rank job PER COORDINATE globally. Its <.773-per-coordinate bound rules
out that contract. Nothing here contradicts it or reclaims its interval proof
or pure-cut census as new work.

We instead make the following OPTIMISTIC hypotheses, with no implementation
claimed. In each of the18 LOCAL invocations at the selected source bill, permit
up to four additional binary splits of its helper targets. A split replaces
one positive integer rank h by a and h-a, 1≤a<h; descendants may also split.
All original helper ranks are at most9. Keep every other productive target and
every existing paid job. Hypothetically share ONE new rank-one recursive job
globally across all18 invocations, as the price of delivering enough eligibility
to permit these splits. All other new recursive fees may be recorded separately
as a nonnegative raw-moment debit.

In the PR6083 interpretation, four opportunities correspond to d=2 new eligible
directions PER LOCAL cut under its at-most2d split contract. Merely delivering
two scalar values somewhere globally does not supply36 cut-coordinate
availabilities, their timing or lifetime. Reuse/delivery across all18 LOCALs is
GRANTED by this relaxation. Neither that sharing, actual eligibility of the
chosen rank9 helpers, nor a native chart/endpoint is supplied. The scalar
module quotient rank d and a paid native job's recursive rank are distinct;
we assume no inequality equating them.

The source is the exact6030 RESULT with SHA25684fcbe2a…1924ad. It supplies18
forward calls,385 rank9 helpers PER LOCAL and no helper above9. The verifier
reconstructs the complete targets as18 times the local helper histogram plus
the physical caller's main-target histogram. It reconstructs paid jobs as18
times the local paid histogram, all whole-idle jobs, and104·15 rank-one query
jobs. The resulting13444 targets,66834 paid jobs and rank-mass surplus760 are
retained source invoice data, not a new word/census/native replay.

## 2. Sharp binary-split credit, including descendants

Fix any exponent0<p<1 and write f(x)=x^p. The gain from splitting rank h is

    f(a)+f(h-a)-f(h).

The unit increments f(j+1)-f(j) strictly decrease with j. Transferring one
unit from a part at least two larger than the other to the smaller part
therefore strictly increases their sum. The maximum split of h is balanced:

    D_h=f(floor(h/2))+f(ceil(h/2))-f(h).

Moreover D_h strictly increases for integer h≥2. For h=2v to2v+1 its increase
is the increment of f from v tov+1 minus that from2v to2v+1, which is positive.
For2v+1 to2v+2 it is the same earlier increment minus that from2v+1 to2v+2,
also positive. Consequently every split of a rank at most9 earns at most

    delta_9 = 4^p+5^p-9^p,

with equality only for rank9 split as4+5, in either ordering. This quantity is
positive by strict concavity and f(0)=0.

All descendants still have rank at most9. Along any forest of binary splits,
the total target credit telescopes to the sum of its individual split gains.
Thus a LOCAL with s≤4 split events has credit at most s·delta_9 even when new
descendants may be split. The bound is attained IN THIS HISTOGRAM RELAXATION
by splitting s distinct original rank9 helpers into4+5. There are385 such
roots, so inventory does not constrain s≤4. In particular the exact maximum
with up to four events is4·delta_9, not the loose generic2d·9(2^k-1) envelope.

This attainer is a formal target-histogram edit. It is not proof that two
eligible coordinates produce those particular four independent physical
targets, or that their native normalization/restoration is free.

## 3. Complete raw-moment ceiling and ticket counting

Now fix the selected k0=781451/250000000 and p=1-k0. Let the unchanged complete
source target and paid histograms be T_r and P_r, and put

    M = sum_r (T_r-P_r) r^p.

For uniform s additional splits per LOCAL, the sharp optimistic extra credit
is18s·delta_9. The formal target changes are+18s at ranks4 and5 and-18s at9;
their rank mass is unchanged. If J is the TOTAL added recursive raw-moment
debit globally, the largest possible edited moment is

    F_(18s)-J,             F_t=M+t·delta_9.

For nonuniform counts s_i∈{0,...,4}, t=sum_i s_i can be any integer0..72,
and the same exact optimum F_t applies. Distribute t among eighteen bins of
capacity4 and use distinct rank9 roots at each LOCAL. No cut or physical word
is constructed by this allocation.

Positive raw funding requires STRICTLY J<F_t. Therefore F_t is the supremum
of the allowable total extra recursive debit, not an inclusive fee cap. If the
one proposed rank-one job is already charged, the remaining strict allowance
is F_t-1. These units are exactly the raw recursive tariff r^(1-k0). They are
NOT scalar ADD counts, tape time, precision storage or a flat physical fee.
No conversion to those costs is supplied.

The fixed rational certificate in verify.py is required to establish:

    M>0,
    F_36<1<F_54,
    F_72<2^p,
    F_72<2.

The first two strict separations identify THREE as the minimum uniform splits
per LOCAL capable of funding a rank-one job in the relaxation. That is54 split
events globally, not three global events. Two per LOCAL cannot fund it, even
under the optimistic assumptions. Under the at-most2d-splits-per-LOCAL contract
with the SAME coordinate budget d at every cut, this makes d≥2 necessary;
it does NOT make d=2 sufficient for physical delivery. This is not a claim
that every cut needs two coordinates when different d_i may be allocated.

The actual minimum TOTAL split count in the relaxation is independently
derived from the complete moment, rather than assumed equal to54:

    t_min = floor((1-M)/delta_9)+1.

The strict inequality matters even if the ratio is an integer. The verifier
finds the least integer t in0..72 with a certified F_t>1 and certifies
F_(t-1)<1. Actual numerical t_min and all rational endpoints belong to the
generated RESULT, not an unexecuted guess in this proof.

The last two separations show that EVEN THE FOUR-SPLIT optimum cannot pay one
rank-two job or two rank-one jobs. Since p>0, every positive integer rank at
least2 costs at least2^p, and each positive-rank job costs at least1. Hence,
among hypotheses demanding at least one new positive-rank job, this relaxation
permits ONLY one global rank-one job and has no room for another positive-rank
recursive job. Other recursive debits must fit the remaining strict fractional
allowance; physical/nonrecursive costs and productive-carrier changes require
a separate model. With no extra job the positive split credit remains available
arithmetically, but a free existing trajectory is itself an unprovided physical
hypothesis.

These are exact full-profile budget distinctions, not a new kappa or an assertion
that a positive raw moment passes the original native/compiler/outer gates.

## 4. Exact rational enclosure method and required evidence

The new implementation imports no predecessor verifier, source word, native
engine or helper census. It reads only the exact selected RESULT and two
retained6083 prose bodies, authenticating their fixed sizes/SHA256 before any
calculation. This is code-disjoint implementation, but source-aware:6083 also
uses the classical log series, whose credit is retained. It is not a blind or
independent human re-audit of its theorem.

For1≤q≤2 and z=(q-1)/(q+1), the nonnegative atanh series gives

    log(q)=2 sum_(j≥0) z^(2j+1)/(2j+1).

After64 terms its tail is bounded above by

    2 z^129 / (129(1-z^2)).

Range reduction r=2^e q supplies log(r) from that interval and the same
rigorous log2 interval. Bounds are rounded outward to the dyadic grid2^-192.
For x=k0 log(r), the code checks0≤x<1/50. Alternating Taylor sums of exp(-x)
through odd degree33 and even degree32 give lower and upper bounds, since
successive term magnitudes decrease. Because exp(-x) decreases, evaluate the
lower polynomial at the upper x endpoint and the upper polynomial at the
lower endpoint. Multiplying by r and rounding outward encloses r^p.
Every operation is exact Fraction/integer arithmetic, with signed interval
coefficients reversing endpoints correctly. No float/Decimal or sampled
transcendental routine supplies a sign.

The finite implementation checks all36 integer split choices1≤a<h≤9 at k0,
with balanced rank9 equality and strict domination otherwise. The written
argument in section2—not this finite check—covers all0<p<1 and arbitrary
split forests. It separately forms complete edited histograms and compares
their direct interval repricing to the factored M+18s·delta_9-1 expression.
The numerical specialization is publishable only with a completed receipt
whose strict gates above pass; execution status and observed resource use
are recorded separately. No pass is inferred merely from source-code presence.

Controls include the failed two-ticket, rank-two and second-rank-one budgets,
with actual rational negative witnesses; omission of an old paid call rejected
by complete-profile reconstruction; insufficient rank9 inventory; and strict
Boolean-count/duplicate/float/nonfinite JSON guards. Another control corrupts
the retained baseline target profile by adding rank4/rank5 credits without a
rank9 debit, and rejects through baseline target-profile reconstruction. It
does not mutate the new attainer constructor; that constructor's debit and
rank-mass guard are inspected separately. The first generated
packet must be preserved before any correction. --emit prints a computed packet to
stdout without writing RESULT; default mode recomputes everything and compares
the entire typed canonical packet with retained RESULT. External receipts bind
package bytes, avoiding a self-referential RESULT hash inside its own packet.

## 5. Limits and credit

No native grouped delivery, cut eligibility, chart/phase, timing, lifetime,
arbitrary dirty restoration, cross18 installation or complete physical invoice
is constructed. All are explicit unknowns, not free realized operations. The
original all-five-assumption/actual-helper acceptance gate remains unmet.
Changed prefixes, productive carriers, extra credits, multiple cuts, a new BIT
cap or more than four splits per LOCAL are outside this result. Neither the
6083 exclusion nor this optimistic countermodel is a universal P104 barrier.
No source scientific program or selected cold replay is executed by verify.py.

Credit zxv6083 for the separate-coordinate interval exclusion, explicit coupled
delivery opening and declared target-count caveat; zxv6064 and Ali Romman5615
for the fixed-cut module capacity framework; DreamingOfClouds6030/5907 and the
cumulative P104 word/invoice; Matarener5994 for the earlier census (NOT rerun);
Nick Petalas6033 for the distinct fixed-rung carrier-price boundary; all retained
source authors and notices. Concavity, balanced partitions, discrete marginal
increments, atanh/Taylor bounds and interval arithmetic are classical. Substantial
OpenAI Codex implementation/proof/source-aware review assistance is disclosed;
no independent human, Lean/kernel, supplier, frontier/adoption or merge claim.
