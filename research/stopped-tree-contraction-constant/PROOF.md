# A contraction bound for lower-order recursion tolls

This scoped written proof was produced by Nick Petalas. Apache-2.0.
The critical moment inequality and physical node premises cited below are
inherited, not reverified here. The new result is a smaller sufficient
uniform cost coefficient under those premises.

## Weighted-tree lemma

Consider a finite rooted tree. Node u has width e_u>0 and volume v_u>=0.
The root has width h and volume V. Every internal width exceeds s>0,
every leaf width is at most s, and each child c satisfies

    e_c <= rho e_u,       0<rho<1,
    sum_c (v_c/v_u)(e_c/e_u)^beta <= 1,       beta>0.

Zero-volume nodes can be deleted. For every delta>0,

    sum_internal_u v_u e_u^(beta-delta)
      <= V h^beta s^(-delta) / (1-rho^delta).                 (1)

Also, the leaf potential satisfies

    sum_leaf_u v_u e_u^beta <= V h^beta.                       (2)

If 0<delta<=1, concavity at one gives the rational relaxation

    1/(1-rho^delta) <= 1/[delta(1-rho)].                       (3)

To prove these statements, put p_(u,c)=(v_c/v_u)(e_c/e_u)^beta.
These nonnegative conditional weights sum to at most one. Complete each
sum to one by adding a terminating outcome with no further toll. A node's
reach probability is

    P_u = (v_u/V)(e_u/h)^beta.

This follows by telescoping along its path. It is valid even when total
child volume exceeds parent volume. Unnormalized volume is not a probability.

Take any realized finite path with internal widths e_0,...,e_l. Strict
contraction implies e_j>=rho^(-(l-j))e_l. Therefore

    sum_(j=0)^l e_j^(-delta)
      <= e_l^(-delta) sum_(k=0)^l rho^(k delta)
      <= s^(-delta)/(1-rho^delta).

An empty internal path has sum zero. Taking expectations and substituting
P_u proves (1). The total probability of reaching genuine leaves is at most
one, which proves (2). Finally, x^delta is concave for 0<delta<=1, so
rho^delta<=1+delta(rho-1). This proves (3). These arguments do not require
equal depths, equal volumes, a stationary branching rule or monotonicity of
the recursion cost.

For integer widths at least one, strict contraction bounds the depth by a
finite function of h and rho. More generally, stopping below s also bounds
depth by the least d with rho^d h<=s. Thus the argument applies to the stopped
recursion below without an infinite-path interchange.

## Application to the cited stopped complex recursion

JoyboyBrian's PR4965 supplies the following contract for Cinna Davis's
PR4100 mixed recursion, using the PR4088 histogram. All of its node,
leaf, placement and additivity premises N, L, P, A remain assumptions here.
They include actual whole-child volume, local node tariffs, and eventual
restoration. No physical implementation is constructed in this package.

The fixed parameters are

    b  = .001730979115670792472760579929302792893760378764,
    a2 = .001733394791695384296,
    q  = b-10^(-28),       eta=10^(-32),
    beta=1-b,             delta=a2-b,            rho=48/73.

Write mu_x=sum_r (H_r/W)(r/73)^x. The inherited critical moment premise
is mu_beta<=1. In particular, no new enclosure of this moment or of the
predecessor's near-critical moment mu_tau is claimed.

An internal node of integer width e>s>=73 has f=floor(e/73), children of
width r f for r<=48 and total volume (H_r/W)v for each r. Consequently

    r f <= rho e,
    sum_child (v_c/v)(e_c/e)^beta <= mu_beta <= 1.

The integer remainder e-73f is at most 72. Because 1-a2>199/200 and
74^199>=72^200, every internal e>=74 satisfies 72<=e^(1-a2).
Its node and remainder costs are therefore at most

    c_N Lambda v e^(1-a2) + 72 c_L v
      <= (c_N Lambda+c_L) v e^(beta-delta).

Here Lambda>=1 is the inherited polylogarithmic factor. Equations (1) and
(3), and s^(-delta)<=1, bound all internal costs by

    Lambda(c_N+c_L) V h^beta * 73/[25(a2-b)].                  (4)

This denominator uses the toll exponent gap a2-b, rather than a moment gap
at an exponent arbitrarily close to beta. Exact rational arithmetic gives

    73/[25(a2-b)]
      = 730000000000000000000000000000000000000000000000
        /603919006147955809855017674301776559905309
      < 1,209,000.                                           (5)

At a leaf, e=e^beta e^b<=s^b e^beta, since b>0. Equation (2) bounds all
leaf costs by c_L V s^b h^beta. In particular the complete tree costs at most

    V h^beta [1,209,000 Lambda(c_N+c_L)+c_L s^b].              (6)

For the source's s=max(73,h^eta), s^b<=73^b h^(eta b).
Exact rational comparisons give beta<1-q, beta+eta b<1-q, and
1-a2<1-q. Adding root placement c_P Lambda V(h^(1-a2)+1), every h>=1
therefore obeys

    layer <= V Lambda h^(1-q)
      [1,209,000(c_N+c_L)+73^b c_L+2c_P].                     (7)

This includes a root that is already a leaf. The leaf and placement terms
are the same as in PR4965. Its adapter/remainder coefficient is
1/(1-mu_tau), reported there above 7e27. Equation (7) replaces it by
1,209,000, without recomputing or disputing that earlier certificate.
This is a smaller sufficient theoretical constant, not a runtime measurement,
an optimal constant, a new exponent or a reduced physical implementation bill.

## Evidence and scope

The universal proof is the argument above. The exact verifier builds new
finite trees, rather than replaying predecessor source instances. Its floor
trees include exactly critical and subcritical moments, unequal widths,
total child volume above parent volume and roots that are leaves. Literal
path expansion agrees with a separately evaluated bottom-up recurrence.
Rational-square trees exercise delta=1/2 and the exact and relaxed
contraction denominators. Failure controls demonstrate why a positive toll
gap, a critical moment bound and genuine contraction are needed.

The source's critical moment inequality is a cited mathematical dependency.
None of N, L, P, A, actual packet/chart realization, local suspension,
native/all-column identities, compiler closure, dirty restoration, storage,
precision/tape or analytic integer recovery is discharged. No selected
supplier or complete multiplication theorem follows. Independent human and
formal proof-kernel review are unclaimed.

Credit Brian / JoyboyBrian for PR4965's recurrence and old cost theorem;
Cinna Davis for PR4100 and PR4088's construction and histogram; Jose Manuel
/ jmbarrancoml for PR4178's height context; Matarener for PR4424's cover/stock
analysis; unpaidmoon for PR4375's whole-child versus factorwise distinction;
and the retained native/compiler/outer lineage. Weighted path probabilities,
geometric summation and concavity are classical. No global literature
priority is claimed for the lemma. The contribution is its explicit
quantitative application (7) to this retained contract.
