# Spend the existing Gaussian normalizer once

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
**Conditional source-interface lemma; no new kappa.** Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. Actual boundary, predecessor work and the two scale policies

The current complete-Core / first-face bridge returns, on one actual original
field, a rounded approximation to

`B_j = tensor_(i in G_j) (H_i^-1 / 2^u_i)`,

where the real rational H_i are the same immutable augmented narrow References
on both sides of the splice. Put `U_j=sum_(i in G_j) u_i` and `U=sum_j U_j`.
The admitted real row-gap bound gives `||H_i^-1||_infinity<=1/delta_i`.
Because H_i is real, the same absolute row sums bound the component-l1
supremum norm. Consequently
`||B_j||_*<=product_(i in G_j)(2^-u_i/delta_i)<=1`.
The bridge's single final truncation is on the common component grid 2^-q.
Its exact source, whole-field radius and error contracts are retained at
[public commit 73d5adab](https://github.com/CubeJerry/integer-mult-bounds/tree/73d5adaba2b7dc662e86eb901e81369a3f73be9f/research/core-halo-source-bridge).
This package retains its unchanged allocation function and proof. The complete
Core numerical contract is the cited premise at
[6fb9ab77](https://github.com/CubeJerry/integer-mult-bounds/blob/6fb9ab776b7d0956b8bcc2d3cfde0f3034421630/research/complete-core-physical-join/NUMERICS.md).

The canonical `unconditional-batched-crt/PROOF.md`, under "Exact Gaussian and
source-transform identity", defines

`(Cv)_j=v_(q_j)`, `D_jj=exp(pi alpha^2 beta_j^2)`, `N=C T_gauss D`,
`P_s F_s = D N^-1 C P_t F_t S_gauss`.

It already normalizes **completed** S_gauss and D N^-1 C maps by dyadic powers
of p and restores their accumulated exponent gamma. The same package's
GAUSSIAN.md specifies a sufficient dyadic p^100 bound per completed axis and
combines normalizers within group diagonals. Its proof claims are provenance,
not accepted here as an unconditional multiplier. In particular, we retain
the source comparison H versus ideal N, coefficient preparation and physical
execution as premises.

Let K_j be the already-declared compression normalizer exponent for group j.
On the padded target grid let Dtilde_i equal the actual D diagonal at selected
addresses and equal 1 at holes. Final extraction C drops holes and has norm
at most one. Since the actual Reference has no coupling to a hole, extraction
of `Dtilde_i H_i^-1` is exactly the corresponding source rational compression
map. The separate replacement of this rational map by the ideal N map is
not proved here. The source's normalized rational target is

`G_j = 2^-K_j Dtilde_(G_j) tensor_(i in G_j) H_i^-1`.       (1)

This is a protocol on the complete padded target field: extraction is deferred
until after the groups. The exact extraction on an axis commutes with every
map acting only on another group's disjoint axes, so this preserves the
exact source factorization. We do not commute arbitrary rounded operations;
their actual all-input errors are controlled below. The inherited prime-product
admission `T/S<2` in GAUSSIAN.md bounds this padding volume. Physical adaptation
must still preserve the same original coordinates and pay the full padded
field. Without that admission retain T explicitly rather than identifying
its cost with the compressed source volume S.

There are two valid accounting policies:

* **Spend existing normalization.** Following B_j, apply
  `A_j=2^-(K_j-U_j) Dtilde_(G_j)`. Then `A_j B_j=G_j` and the existing
  final restoration `2^gamma` is unchanged. Require K_j>=U_j; a stronger
  condition below makes A_j a contraction on arbitrary hole errors too.
* **Add a new normalization.** Keep the old remaining diagonal
  `2^-K_j Dtilde_(G_j)`. The completed group is then `G_j/2^U_j`.
  To recover the same old target the final exponent must become `gamma+U`.

Adding U to gamma in the first policy is wrong; retaining gamma in the second
is wrong. These statements are exact identities, including all source holes.
The policy must be bound to the actual remaining coefficients and final
scale. Labels such as "normalized Core" cannot establish this binding.
The written theorem below uses the first policy. The second has the same
proof with its actual smaller remaining maps and final exponent gamma+U.

#6880 already gives one-group splice bounds and warns that recovery scales
must be paid. #5325 joins a different physical Tensor using its own 1/8
compression and gamma. The Gaussian normalization stream concerns powers of
(1-i)/2; the mixed-native audit concerns JSON commitments; sparse-dyadic
normalization concerns Bezout acquisition. None supplies this particular
source's remaining-diagonal contract or consumes its p^100 budget. We claim
that source-specific join and its exact admission rule, not a new generic
perturbation inequality, Gaussian identity or asymptotic p^100 argument.

## 2. The actual D bound leaves room for the bridge normalizer

Use the source family with p>=2 and `pi alpha^2<=5 log(16p)`; this upper bound
is an explicitly inherited eventual Gaussian admission. Original nearest
half-up rounding gives `|beta_j|<=1/2`. Therefore

`1<=D_jj<=exp(pi alpha^2/4)<=(16p)^(5/4)<=(16p)^2`.

Let `l=ceil(log2 p)`. A safe per-axis dyadic norm exponent is
`v_i=2l+8`. It covers the value 1 assigned to holes as well as all selected
diagonal entries. For a group put V_j=sum v_i. In the component-l1 supremum
norm used by the bridge,

`||A_j|| <= c_j := 2^(U_j+V_j-K_j)`.

Thus the exact finite admission `K_j>=U_j+V_j` makes both A_j and G_j
contractions. The bound holds on arbitrary numerical errors, including hole
errors, rather than only on an exact source-image subspace.

The source gap `delta_i>=1/(16p^2)` permits the least dyadic normalizer
`u_i=ceil(log2(delta_i^-1))<=2l+4`. The looser `u_i<=2l+5` also suffices.
Consequently the concrete choice `k_i=100l` has

`k_i-u_i-v_i >= 96l-13 > 0`, p>=2.                      (2)

This is one sufficient dyadic polynomial budget compatible with the source
p^100 prescription. A caller's actual smaller k_i must pass the finite
inequality; its name or asymptotic order is insufficient. A caller choosing
oversized a_i instead of the least dyadic must fund those actual exponents.
Equation (2) does not certify the numerical D coefficients or implement their
physical stream.

## 3. Actual rounded states, remaining error and explicit precision

Let m>=1 groups partition the actual inverse axes. Each bridge is admitted on
every incoming q-grid state of component-l1 radius at most R_b=2R_0, with
integer R_0>=1. Its same-reference global error bound is

`E_j=max( 2^(-t_j-U_j)+2^(1-q)+2 R_b Lambda_j,
          L_j(R_b) 2^-q + R_b Lambda_j )`,              (3)

where

`Lambda_j=sum_(i in G_j) (1-delta_i)^J_i/(2^u_i delta_i)`,
`L_j(R_b)=sum_(i in G_j) ((2W_i+1)R_b+2)/delta_i`.

This is the retained actual bridge allocation, including complex component
conversion, whole Core error and the final q-grid truncation. It applies at
the actual input of each group; a rounded bridge is not assumed linear or
Lipschitz. Its internal native radius must still include `R_b sqrt(T_j)` for
the full field of that call. With a common upper volume `T_j<=2^n_addr`, where
n_addr denotes the field's address width, the sufficient exponent is
`ceil(log2 R_b)+ceil(n_addr/2)`.

The actual remaining-diagonal implementation must return to the same q grid
and satisfy, on every actual input of radius at most R_w=3R_0,

`||Ahat_j(z)-A_j z||_* <= e_A,j`.                       (4)

This is a paid source/compiler/rounding obligation. It includes diagonal
coefficient error, products, copies, final grid conversion and any scale
operation. It is not inferred from (2). If Q_q is the final componentwise
toward-zero truncation and the preceding diagonal computation has error
e_D,j, then `e_A,j<=e_D,j+2^(1-q)`. No precision is silently preserved after
the remaining division.

Set `w_j=c_j E_j+e_A,j`, with c_j<=1. If

`sum_j w_j<=R_0`, `E_j<=R_0`,                          (5)

the actual completed-group states all remain within R_b. Indeed a group
input of radius at most `R_0+sum_(k<j) w_k` is in the bridge domain. The
bridge output has radius at most `R_b+E_j<=R_w`, so (4) applies to its actual
output. Compare that output first with A_j B_j applied to the same actual
input; the local defect is at most w_j. Then use the exact contraction G_j
to compare the actual input with the ideal predecessor. Induction gives

`r_j<=R_0+sum_(k<=j) w_k`, `e_j<=sum_(k<=j) w_k`.       (6)

The sharper recurrence is `e_j<=||G_j|| e_(j-1)+w_j`; (6) suffices without
assuming linearity of either rounded routine. Final extraction cannot
increase this norm. Exact final multiplication by 2^gamma therefore gives

`final compression contribution <=2^gamma sum_j w_j`.  (7)

All errors before this compression stage and after it remain separate. If
the remaining exact suffix has complex-supremum norm L_s, its contribution
is at most `L_s 2^gamma sum w_j` since complex modulus is bounded by the
component-l1 norm. A complex unit phase is not assumed to contract the
component-l1 norm. A caller returning to that norm must pay the appropriate
conversion. Integer recovery still needs the actual CRT/Fourier and product
scale from #6880/#2313; (7) is a substitution, not a full recovery theorem.

Here is a concrete simultaneous allocation for target 2^-tau in (7).
Require integer tau>=1 and gamma>=0; a larger exact suffix can be covered by
adding an integer bound on log2(max(1,L_s)) to tau. Put

`h=ceil(log2 m)`, `z=tau+gamma+h+1`, `eta=2^-z`.

For each group require

`t_j>=max(1,z+2-U_j)`,
`q>=max_i u_i`, `q>=z+ceil(log2(max(8,2 max_j L_j(R_b))))`,
`Lambda_j<=eta/(4R_b)`, `e_A,j<=eta`.                  (8)

Then the Core term and final rounding in the kept branch of (3) are each
at most eta/4, and its tail is at most eta/2. The halo coefficient term is
at most eta/2 and its tail at most eta/4. Hence E_j<=eta, w_j<=2eta, and

`sum w_j<=2m eta<=2^(-tau-gamma)<=1/2<=R_0`.

All actual-domain guards (5) and the final tolerance follow. One sufficient
axis-tail admission is
`(1-delta_i)^J_i/(2^u_i delta_i)<=eta/(4R_b |G_j|)`.
The exact rational powers give a finite acceptance check. If delta_i=1 the
tail is zero at J_i=1, without taking a logarithm of zero. W_i=0 and holes
remain ordinary source cases. Every inherited Core/halo geometry admission,
original coordinate binding and production-context certificate stays required.

Equation (8)'s q budget also leaves room for the final remaining-diagonal
truncation: `2^(1-q)<=eta/4`. It therefore suffices to obtain
`e_D,j<=3eta/4` before that truncation. This records a concrete still-open
diagonal error target rather than setting it to zero for free.

## 4. Global dimension and complete costs

The public Core's conservative family uses balanced group sizes between
g and 2g, `g=Theta(p^(39/40))`, and the actual number of axes
`d=Theta(p^epsilon)`, `epsilon=1-10^-30`. The canonical outer source gives
`n_addr=log2 T=Theta(p)`, `ell_original=Theta(p^(1-epsilon))`; these are explicit family
premises, not consequences of a finite fixture.
The source's own n denotes the integer input length, with V=Tp=Theta(n);
it is not the address-width symbol n_addr used here.

Under uniform `u_i=O(log p)`, `k_i=O(log p)`, both global totals obey

`U=O(d log p)=o(p)`, `gamma=O(d log p)=o(p)`.             (9)

The first-policy gamma also includes all preexisting expansion normalizers.
The second-policy exponent gamma+U has the same eventual order. A single
group's `U_j=o(p)` alone would not establish (9); the full d relation is
essential. We do not claim a contradiction for the canonical near-one
epsilon. The statement is asymptotic and can have a very large initial range.

For a quantitative interpretation, suppose a combined scale bound has the
explicit form `B p^(1-a) log2 p`, where a=1-epsilon>0 and B is a uniform
constant after some admitted p_0. Elementary maximization gives
`log2 p <= (2/a) p^(a/2)` for p>=1. To make this scale at most c p, it
suffices that

`p>=max(p_0,(2B/(a c))^(2/a))`.                        (10)

With a=10^-30 this sufficient onset is enormous. Neither the proof nor its
small controls claim practical production parameters at this onset.

Let `tau=O(p)`, `log R_0=O(p)`, `W_i=O(sqrt(p) polylog p)` and
`delta_i>=1/(16p^2)`. Then log L_j=O(p+log p+log g), log m=O(log p), and
(8) gives common q and all t_j of O(p). The fixed conservative choice
`J_i=16p^4` gives `(1-delta_i)^J_i<=exp(-p^2)` and meets the tail guards
eventually, including the total restored scale in (9). It retains
`b_i=(J_i-1)W_i<16p^5<p^48` once the source W_i<p admission holds.
The earlier source geometry `L>=p^400` and first-face containment remain.

The inherited Core formats then use their actual q, t_j and full radius
R_b sqrt(T_j); their proofs give P_j,w_j=O(p) under the same uniform source
height/prefix premises. Here the word width w_j is unrelated to the local
error notation of (5). The bridge codec retains its complete O(T_j F_j)
invoice, with

`F_j=d_record+w_native,j+(P_j-q)+(P_j+U_j-q)+1=O(p)`,

where `d_record=q+R_b.bit_length()+1` and `w_native,j` denotes the actual
native signed-carrier width. Thus its sum is O(V m), V=Theta(Tp) for a
common upper field volume T. A separate final exact scale or an unfused
remaining dyadic shift costs a full O(V) pass, or O(Vm) for one per group;
it is not free. Exact positive final shifts retain O(p) signed headroom.
Exact downward shifts must retain the extra fractional bits or charge their
rounding through (4). Old backing and every source/halo/callee owner remain.

All **diagonal numerical products**, coefficient tables, source formation,
validation and physical access retain their existing complete invoices. This
proof adds no per-record free scalar multiplication and provides no new
diagonal engine. Funding (4) at O(p) bits preserves a claimed existing tariff
only if its actual source contract supports that precision and cost. The
Core's full K-context setup and the halo archive bill remain; the new scale
ledger neither drops K nor creates a cache. A fixed number of global scalar
admission calculations per axis has polynomial descriptor cost; exact tail
checks may have polynomial(p) rational height and are setup, not online O(1).

## 5. Failure controls and exact remaining implication

The actual Reference._narrow returns identity whenever either address is a
hole. Thus a tensor coordinate consisting of holes is an exact eigenvector
of every H_i and its inverse with eigenvalue one. This is an admitted
all-input source direction, regardless of whether a particular outer prefix
reaches it. Its normalized bridge action is exactly multiplication by 2^-U_j.

Take two groups with U_1=U_2=8, caller K_j=U_j, remaining diagonal identity,
and a unit value on such a coordinate. At q=15, each individual shift fits
q>=u_i, but the sequential q-grid values are `2^-8` and then zero, because
`2^-16<2^-15`. Restoring by 2^16 still returns zero instead of one. At q=16
the unit survives exactly. This is a cumulative-grid erasure control for an
ideal exact hole action followed by the actual specified truncation; it is
not a native Gaussian execution or proof that a particular complete outer
caller reaches that input. Final C deletes this hole-supported direction:
the control concerns the **pre-extraction bridge interface**, and is not a
counterexample to the completed extracted compression output. It does not
prove a necessary q>=U condition for every final caller or reachable input.
It exposes why individual group shifts and an ideal-state radius check do
not certify the bridge's declared all-input global budget.

Taking the actual Reference source halfwidth w=0 would make its selected
off-diagonal entries vanish, but does not supply a stronger admitted example:
the unchanged constructor's `narrow_tail` starts with
`2/(1-exp(-2 pi alpha^2))>2` at w=0. Its certified `narrow_gap` is then
negative. The actual bridge demands a positive bound no larger than that
certificate. We therefore do not promote this structurally identity
zero-source-halfwidth reference to an admitted selected-coordinate or
final-output counterexample.

The independent checker also distinguishes omitted compensation from double
compensation, underfunded remaining diagonal norm, ideal-only wrapper radius,
missing wrapper truncation, source corruption, zero tails and the full-field
radius conversion. Exact finite recurrence cases corroborate the written
proof and the unchanged bridge allocation; they do not establish analytic
source or native execution premises.

The new implication is now explicit: an actual remaining-diagonal service
meeting (4), bound to the source's chosen K_j and the proper policy, plus the
already admitted bridge at (8), yields a complete normalized compression-group
contract on actual states and the final contribution (7). The source's
polynomial normalizer budget passes its exact norm gate. Its source-page,
rounded-diagonal and physical delivery obligations still need execution and
verification; this is not a complete Gaussian/Tensor/FFT or multiplication
theorem. All five foundational assumptions and the accepted kappa remain.
