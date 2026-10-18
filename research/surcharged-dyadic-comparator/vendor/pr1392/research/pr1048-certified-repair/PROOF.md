# Certified comparison at a reference root

The pipeline is fixed at m=64, W=28416, with n_r=288 p_r+idle_r.
Let N=sum n_r and lambda=32 m^2/10^16=2/152587890625. Its residual is

    F_n(a) = sum_r n_r r (m/r)^a + lambda N m^a - mW.

All counts must be nonnegative integers, ranks must lie in 1..m, and N>0.
F is continuous and strictly increasing: each first-sum term is nondecreasing,
and the positive surcharge is strictly increasing because m>1. F tends to
infinity. The exact rational test F(0)<0 therefore proves existence and
uniqueness of a positive root. These requirements are checked for every priced
candidate. A failure is explicitly unresolved under the positive-root contract.

For unchanged idle profile, m, W and replication factor, subtracting residuals
gives the identity, valid at every real a,

    F_candidate(a)-F_reference(a) = 288 m^a J_delta(a),
    J_delta(a) = sum_r delta_p[r] r^(1-a) + lambda sum_r delta_p[r].

At the actual reference root c, F_reference(c)=0 and 288 m^c>0. Thus
J_delta(c)<0 implies the candidate root is strictly larger, while
J_delta(c)>=0 implies it is no larger. This is a reference-root comparison;
ordering profiles at an arbitrary fixed exponent is not justified.

The implementation first reuses woklerx's PR1182 bisection, with flemhhh's
original interval oracle. It explicitly rechecks both final signs:
F_reference(L)<0<F_reference(U). It retains a wider certified bracket if a
finite precision budget cannot refine it; no initial certified bracket means
no comparison. Monotonicity proves L<c<U. It then encloses J_delta over the
whole interval [L,U], rather than substituting a shipped lower endpoint.

For each r>1 and a in [L,U], monotonicity gives

    r / exp(U ln r) <= r^(1-a) <= r / exp(L ln r).

The retained log series gives rational lower and upper bounds for ln r. The
retained positive exponential Taylor series gives rational lower and upper
bounds for exp(x); its entire input interval is explicitly checked in [0,1].
Reciprocal endpoints are reversed, then rounded outward to a denominator of
10^48. For a negative delta coefficient, multiplication reverses the interval
endpoints again. The surcharge term is exact, including its sign. Consequently
an upper bound below zero certifies BETTER; a lower bound at least zero
certifies WORSE_OR_EQUAL; all other cases are UNRESOLVED. Identical profiles
give an exact zero identity and equal roots. Distinct-profile ties need not be
decidable by this interval method and are not assumed absent.

For the retained log routine, ln x is range-reduced into powers of two,
3/2, and a residual in [1,3/2), then evaluated with the positive atanh series.
Its remainder bound is conservative (the code adds an extra factor of two).
The exponential remainder uses the geometric majorant for the first omitted
term. No acceptance decision uses floating point. The independent checker
uses separately implemented enclosing arithmetic and direct residual signs.

# What this proves

Pricing validates an arithmetic comparison of declared profiles. It does not
prove that an abstract profile is realizable, that moving an operation is
legal, or that a nominated move set is complete. Coverage requires its own
finite domain and exact word/profile reconstruction. Equal price or equal
profile does not imply equal future move neighborhoods. Register-disjoint
pruning requires legality and certified one-move non-improvement hypotheses;
none follows merely from the additive objective. No unrestricted two-move
exhaustion or new multiplication bound is claimed.
