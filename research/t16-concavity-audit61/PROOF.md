# What the frozen T16 improvements do and do not imply

This audits the four source-bound owner maps reviewed together in
`docs/research/community-batch1047-review.md`: PR1022, PR1028, PR1031 and PR1042.
Their local seven-slot k8 supplier, widths, 144-call order and pending-child
windows agree. This is a comparison of those maps, not a claim about all T16
maps, later proposals, or global optimality.

## Reconstructing the residuals

For each group g=(owner replica, child, port), read capacity C_g from the
frozen PLAN and its complete helper slices from OWNERS. The main verifier
checks whole widths, per-call helper/family uniqueness, declared window
membership, disjoint slices and exact prefix occupation. It computes
r_g=C_g-sum(widths in g), retaining zeros. All four vectors have 32,256 entries
and sum 237,024. Their paid global profiles minus these nonzero residuals are
the same 144 copies of the local profile. Thus differences of global profile
costs equal differences of residual costs.

These checks bind the comparison to the actual owners. They do not replace
the upstream reconstruction of physical windows, charts, scalar semantics,
controller invoice, precision, exact moment roots or all-size interfaces.

## The classical majorization criterion

For equal-length, equal-sum nonnegative integer vectors with entries at most
48, new majorizes old exactly when

    sum_new max(r-k,0) - sum_old max(r-k,0) >= 0

for k=0,...,48. Checking integer thresholds suffices because the difference
is linear between successive integers, zero above 48, and fixed by the equal
sum below zero. This is the classical stop-loss formulation of majorization,
already used in the inherited `hosting/PROOF.md`; it is not a new theorem.
Equivalently the sorted descending prefix sums of new dominate those of old.
The independent verifier uses that second formulation on expanded vectors.

A majorizing vector has a weakly smaller sum for every concave function.
The equal-length condition includes the zero residuals; deleting them changes
the comparison domain. For an explicit witness, phi_k(r)=min(r,k) is concave,
and its new-minus-old sum is the negative stop-loss difference at k, since
min(r,k)=r-max(r-k,0) and total ranks agree.

Of the six chronological pairs, only PR1028 -> PR1031 has the stated
majorization: two residuals of rank 1 become ranks 0 and 2. Its stop-loss
improvement is 1 at k=1 and zero at all other integer thresholds. The other
five pairs have both negative and positive stop-loss differences. Therefore
neither member dominates the other for all concave costs. Every pair's full
49-threshold vector and explicit concave witnesses are in CERTIFICATE.json.

## A reversal inside the actual power-cost family

The selected PR1031 -> PR1042 difference is

    delta = {0:-3, 3:+11, 7:-7, 16:-2, 48:+1}.

The total count and total rank differences are zero. At k=3 the stop-loss
difference is -9; at k=16 it is +32. Hence min(r,3) costs 9 more in PR1042,
while min(r,16) costs 32 less. This already excludes universal concave
improvement, but the actual moment-cost family has a stronger direct control.

For 0<b<1 let phi_b(r)=73^b*r^(1-b)-r, with phi_b(0)=0, exactly as in the
inherited hosting proof. Equal rank sums cancel the linear term. The sign of
the new-minus-old total cost is therefore the sign of

    D_b = 11*3^(1-b) - 7*7^(1-b) - 2*16^(1-b) + 48^(1-b).

At b=1/2 this is 15*sqrt(3)-7*sqrt(7)-8 < 0. At b=3/4 it is
13*3^(1/4)-7*7^(1/4)-4 > 0. Thus the same chosen map improves one member of
the actual strictly concave cost family and worsens another. Continuity gives
at least one zero in (1/2,3/4); neither uniqueness nor its location is claimed.

The signs are exact: for q=2 or 4 and S=10^12, compute the integer l with
l^q <= r*S^q < (l+1)^q. This brackets r^(1/q) in [l/S,(l+1)/S], tightening
to equality for perfect powers. Signed summation reverses interval endpoints
for negative coefficients. The certificate records rational bounds that
strictly exclude zero. A separate implementation bisects Fraction intervals
60 times and proves the same 12 signs for all six pairs, without importing the
primary verifier or any audited implementation.

## Consequence and limits

PR1042's reviewed selected small-exponent certificate and kappa ordering are
unchanged. A strict inequality at that admitted exponent is entirely
compatible with a reversal at much larger b. The inherited greedy exchange
proof guarantees all-concave improvements for the specific capacity-greedy
updates satisfying its hypotheses. It does not imply that different joint
LNS repacks, such as these four frozen maps, are ordered for all concave costs.
Neither the selected review nor this audit requires that stronger property.
This result corroborates the review's treatment of the maps as feasible
witnesses and makes the limit of exponent-independent comparison concrete.
