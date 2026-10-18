# An effective depth bound for the rounded stride solver

This research argument extends PR846 at head
4bdb3e755ea7118170a7a34764df955880dec282. The original source is retained
unchanged in vendor/pr846/stride.py. Its clean scratch and sequential-tape model
remain unchanged. No borrowed-array, bit-reversible or kappa claim.

Let beta=2^-g, g>=1, and let u=2^-W with W>=2g+8. Assume every input
coefficient has modulus at most 1-beta. Add one exact zero test at each
recursion level: when every coefficient is zero, return the data rounded
once. This solves that level exactly up to one rounding. Count the test as
one full coefficient scan and head return; traffic is at most 44L records instead of
the original conservative 40L.

For the early-terminated solver, the number K of non-base levels is bounded independently of L by

    D(g,W)=2g+ceil(log2 W)+4.

Consequently 4(K+1)u<=beta follows from W>=2g+8. This removes the original
p>=log2(log2 L+2) admission condition, after imposing this sufficient local
working-precision condition instead.

## Decay of the rounded closure coefficients

Write rho for the maximum coefficient modulus at a level. Every chain has
at least two coefficients. Its product is initialized with the first exact
coefficient and then rounded after each multiplication. For chain length
ell>=2, its magnitude is bounded by

    rho^ell+u*(1+rho+...+rho^(ell-2)) <= rho^2+u/(1-rho).

Thus a scalar majorant for the next maximum is rho^2+u/(1-rho).

First suppose beta<=m=1-rho<=1/2. Since u<=beta^2/16<=m^2/16,

    1-rho_next >= m(2-m)-u/m >= (23/16)m > sqrt(2)m.

Within at most 2g levels, the margin therefore reaches 1/2, unless recursion
has already terminated. While rho<=1/2, the majorant is rho^2+2u.
This stays below 1/2, and two further levels give rho<=1/4 (W>=10 is more
than sufficient for these elementary inequalities).

While rho>2sqrt(u), the same majorant satisfies rho_next<=3rho^2/2.
For t=2rho, this implies t_next<=t^2, starting from t<=1/2. After at most
ceil(log2 W) additional levels, rho<=2sqrt(u): otherwise repeated squaring
would give rho<=2^(-2^j-1)<=u/2, a contradiction.

One more level gives rho<=6u. At the following level the first multiplication
in every chain has modulus at most 36u^2<u/2. Each component therefore rounds
exactly to zero. Subsequent products in the chain remain exactly zero. All
closure coefficients at that next level are zero, so the new base case
terminates. Adding the four stage counts gives D(g,W).

All inequalities concern complex modulus and use only the nearest-grid
rounding error <=u. They do not assume real positive coefficients, a common
phase, a common chain length or a dyadic initial coefficient. Exact zero in
the final step uses the componentwise nearest rounding rule, not just a
continuous norm upper bound. The strict threshold avoids tie ambiguity.

## Exact equivalence with the unchanged solver

At any level where all coefficients are exactly zero, the unchanged solver
also returns the data rounded once, regardless of its remaining structural
recursion. For stride zero this is its explicit division by one. Otherwise,
pass A copies a chain-start datum or rounds a later datum; every chain
product and every recursive coefficient remains zero. Its finite structural
recursion is well-defined, and pass C returns rnd(x_i+0*seed)=rnd(x_i) at
every coordinate. Reversal commutes with this pointwise rounding.

Thus replacing the whole zero-coefficient subtree by the new base case
preserves the exact rounded output. This is an algebraic identity for the
instruction sequence, not an estimate and not an inference from finite tests.
It applies separately at every zero subtree. Consequently the unchanged
PR846 solver and the truncated solver have exactly identical outputs.

The accuracy proof may analyze the truncated solver while executing the
original unchanged solver. The latter retains its original 40L traffic
bound: no zero scan is required at runtime. The optionally early-terminated
version uses at most 44L records including the extra coefficient scans and
head returns. Its effective nonzero depth is bounded by D; the unchanged
implementation's structural depth may still depend on L.

## Admission and inherited error proof

For W>=2g+8, ceil(log2 W)<=W-1 and 2g<=W-8, hence

    4(D+1)<=8W-16.

Also W-g>=ceil(W/2)+4 and 2^ceil(W/2)>=W for W>=4, so

    2^(W-g)>=16W>4(D+1).

This proves 4(K+1)u<=beta, and u<=beta/3 is automatic. PR846's margin,
weighted-data and shared-suffix error arguments now apply through at most
D levels. The new terminal system has exact solution x; rounding it once
has error at most u, matching the old terminal bound. Therefore the stated all-length error bound holds for both implementations,
with K equal to the truncated depth, or conservatively min(D,1/beta) in its
geometric error factor. The original structural depth is not used for admission.

The algebraic source/input restoration properties are unchanged: this is
still a clean-tape solver with the input unmodified. The optional early-exit check adds at most 2 sum L_k<=4L coefficient records
to the original 40L traffic bound. Executing the unchanged implementation
needs no extra scan and retains 40L.
Any full-kernel composition must use a working precision satisfying both
its existing error target and W>=2g+8. That added local condition is O(g)
and preserves the previous polynomial-in-r precision order.

## Cubic precision for the full kernel at arbitrary strides

This section combines the local result above with PR862's retained
common-operator argument. The target is the same prime-power kernel
P(U), with U=tau Z_L^w and |tau|=1, as in PR846. All inverse factors use
this one operator. Different noncommuting shifts are outside the argument.

A stride solve on input norm at most X has error at most

    (u/beta^2)(5+4X/beta)+u.

After the outer scalar or inner unit rotation and its rounding, its error
is at most 7(X+1)u/beta^3 for beta<=1/2. This is exactly the local bound
required by PR862. Its proof only needs stable factors and that bound;
it does not require the neighboring-stride implementation.

Let n=r-1, let Q=(1/r) product(z-rho_j), and suppose

    ||Q||_1<=M, ||Q(U)^-1||<=H,
    B=max(1,2^n M H).

The complementary-factor/Mahler argument in the retained PR862 proof
bounds every inverse prefix and contiguous inverse subproduct by B.
Starting with r x, ||x||<=D, the maximum prefix execution error E obeys

    E <= t(r B D+E+1),  t=7nB beta^-3 u.

For t<1 this yields E<=t(rBD+1)/(1-t). This does not repeatedly multiply
the worst reciprocal root margin at every factor.

For prime-power r>=3 and p,m>=0, retain the source preparation hypotheses
and put

    ell=ceil(log2 r), c=ceil(log2(r-1)), phi=EulerPhi(r),
    d=1+2ell+r(r-1)phi, a0=2d+r+2,
    g=d+ell+2r+2, beta=2^-g, h=a0+2r,
    e=max(d+1,a0+1,p+2a0+m+3),
    b=max((r-1)ell,e+r+3).

PR628/862's charged approximate factorization and coefficient verification
supply prepared roots with stable margin beta, ||Q||_1<=2^r,
||Q(U)^-1||<=2^(a0+1), and source-scaled kernel perturbation at most
2^(-p-2) for D<=2^m. Thus B<=2^h. These are certified premises, not
conclusions drawn merely from a numerical root list.

Choose

    J=c+2h+3g+ell+m+5, W=p+J+2.

This W exceeds 2g+8, so the stride admission holds for every L and every
stride. Moreover n<=2^c and 7<=2^3 imply

    t <= 2^(c+h+3+3g-W) <= 1/2,
    rBD+1 <= 2^(ell+h+m+1),
    E <= 2t(rBD+1) <= 2^(J-W)=2^(-p-2).

Adding the independently charged kernel preparation perturbation gives
error at most 2^(-p-1), within the target 2^-p. Approximate phase oracles
still need their separately charged perturbation and access budget.

A sufficient integer guard for data/state magnitudes is

    G=m+ell+h+g+8.

Indeed each factor input is bounded by rBD+E. PR846's weighted-data
invariant bounds recursive data and closure values by O(rBD/beta);
its corresponding recursive rounding error is at most one under the
chosen W (h>=g). Chain values, products, scalar application and division
fit this guard. Exact arithmetic accumulators and numerator/denominator
products may use a constant-factor wider representation, as usual.

Using phi<=r, ell<=r and c<=r gives the explicit cubic bounds

    W <= p+m+9r^3, G <= m+6r^3, b <= p+m+6r^3.

The exact nonnegative remainders in t=r-3 are

| Bound | Remainder after removing p and m as appropriate |
| --- | --- |
| 9r^3 minus the working overhead | 65t+25t^2+2t^3 |
| 6r^3 minus the integer guard overhead | 51+85t+30t^2+3t^3 |
| 6r^3 minus the factor-precision overhead | 43+67t+22t^2+2t^3 |

For the final row, the alternative (r-1)ell<=r^2 also fits the cap.
`cubic.py` checks these coefficient identities and exact exponent
inequalities; it does not infer an all-size bound from sampled radices.

If the incoming data have fractional width w, define the word scale
A=max(p,w)+2m+16r^3. With a supplied exact rational phase of representation
size B_tau, the one-kernel bill is

    soft-O(r^3(p+m+r^3))
    + O(rL) M(A+B_tau)
    + O(rL(A+B_tau)).

The terms are factor preparation/coefficient verification, rounded
execution, and sequential tape traffic. Here M is the cost of the charged
integer arithmetic; the Python reference is not a measured implementation
of asymptotically fast multiplication or factorization. Longer initial
coefficient/phase descriptions retain their actual input-reading cost.
Execution uses the inherited clean scratch tapes and O(L) data records;
there is no borrowed-array or bit-reversible realization claim.

The original solver retains its 40L traffic bound per stable factor.
Exact inner rotations and scalar applications add their inherited O(L)
work. The optional zero-truncated solver has at most 44L per factor.
Neither bound has a sorting factor or a precision admission depending
on L. Transform-level layout, phase collection, normalization, common
labels and the multiplication reduction remain separate.

## Evidence and attribution

The checks compare 423 array cases exactly between the unchanged and
truncated solver, with independent geometric oracles for the short cases.
They include non-dyadic margins and four deeper arrays through L=5741.
Ninety scalar coefficient paths test exact extinction for gaps through
2^-256; they are not huge-array executions.

All 300 original PR846 kernel cases pass using the uniform effective-depth
admission, with exact output equivalence and their original residual/dense
checks. An additional 64 executions at the actual cubic W cover radices
3/4/5/7, every stride at lengths 1/2/5, two unit phases, and arbitrary odd
lowest working bits. Roots are rounded to no more than the stated
preparation budget. Every common-operator hypothesis and the independent
kernel perturbation are checked before using the cubic budget.

The source lineage is PR846 (Rohan Guliani), PR764 (Charles Bethin), PR628
and PR862 (Chafik Boukhalfa), and PR621 (Ali Romman), together with their
retained classical references. This argument and its exact integration
checks do not claim independent human peer review or formal verification.
No new kappa is claimed.
