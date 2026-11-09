# The actual reference error fits the existing compression budget

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
**Source-interface theorem, conditional on the named analytic and physical
contracts; no new kappa and no complete integer-recovery theorem.** Canonical
source: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. The missing boundary and the result

The public `core-group-scale-ledger` at
`76a84e1c4bfa4035e5ee85410dbfc4541f0da168` compares the actual Core/halo and
remaining diagonal with a tensor of inverses of fixed rational References H.
Its section 1 explicitly leaves replacement of H by the ideal periodic narrow
Gaussian N open. The actual remaining-diagonal service at
`b00d64b6204e83d468dde2db7480a2822e6940aa` supplies its local error contract,
but also leaves that comparison open. This package joins that specific
boundary, including the original q image, holes, final extraction C and the
already-declared restoration exponent gamma.

The result is stronger than a new generic inverse-perturbation bound. The
literal `Reference.for_cap` allocator funds the comparison at the **same**
Core target and external q grid used in the public ledger, provided its
declared radius covers the stated bridge input radius and the exact finite
normalization check (13) below holds. The concrete per-axis p^100 budget
satisfies that check. A constructor target copied from an unrelated caller,
or a radius below the incoming-radius contract, gets no such conclusion.

The proof uses existing Gaussian tail and row-norm theorems as explicit
premises. It does not establish the exact Gaussian/Fourier identity, the
expansion approximation, the supplier theorem, all physical context delivery,
or the final CRT/product/carry tolerance. It supplies the previously missing
reference-versus-ideal contribution for this compression stage.

## 2. Exact same-reference operators and source premises

For axis i, let S_i be its original source period, e_i its excess and
T_i=S_i+e_i its target period. Define

    theta_i=e_i/S_i, rho_i=T_i/S_i,
    phase_i(j)=floor(theta_i*j+1/2),
    q_i(j)=j+phase_i(j), beta_i(j)=theta_i*j-phase_i(j).

All maps below use these original coordinates and the original period cut.
The ideal source matrix is

    N_i[r,s] = sum_(ell in Z)
      exp(-pi*alpha_i^2*((rho_i*(s+ell*S_i)-q_i(r))^2-beta_i(s)^2)).  (1)

In particular N_i's diagonal contains the positive nonzero-period aliases.
The canonical Reference sets its narrow diagonal to exactly one. Deleting
those aliases from the definition of N_i would change the target and would
not implement the stated Gaussian source identity.

Embed N_i and H_i on the selected target coordinates q_i(j). Put the identity
on holes, with zero selected/hole couplings. This is precisely the augmented
narrow Reference convention. Let Dtilde_i be
`exp(pi*alpha_i^2*beta_i(j)^2)` at q_i(j) and 1 at holes. Let C select q_i(j).
After applying all groups, C is the tensor extraction. Operators on disjoint
axes commute with this exact extraction; no commutation of rounded routines
is assumed. The public ledger's deferred extraction preserves the same target.

Write epsilon_i for the actual rational `ref.errors["narrow"]` and delta_i
for the actual `ref.narrow_gap`. RAW-GAUSSIAN-PROOF sections 3--5 prove

    ||H_i-N_i||_infinity <= epsilon_i,
    ||H_i^-1||_infinity <= 1/delta_i,                         (2)

when delta_i>0. The first includes both omitted periodic aliases and every
retained coefficient error. Those theorems concern the actual deterministic
Reference rule, not a separately rounded matrix.

For the fine-theta family the source parameters obey

    p>=2, 1/(4p^2)<=theta_i<=1/p^2,
    pi*alpha_i^2>=4 log(16p),

and the complete unchanged `Reference.for_cap` is called with legal cuts.
The production-gap theorem at
`9a07c08c014259bb23c0a2b5844a1b67d91892f6` proves
`delta_i>1/(16p^2)` from this literal constructor. Its inherited interval
and row-gap premises are listed there; they are not discharged again.
It also proves the source allocation lower bound used in section 5.

Use the component-l1 supremum norm
`||x||_* = max_x (|Re x_x|+|Im x_x|)` on the full padded field. Every matrix
here is real. Its absolute row-sum bound therefore applies to this norm, and
Kronecker row sums multiply. Complex unit phases are outside this claim;
there is no free component-norm contraction for an unrelated suffix.

## 3. The ideal inverse uses the same literal certificate

The actual constructor computes rational upper endpoints a_i and b_i for
`exp(-2*pi*alpha_i^2*theta_i)` and `exp(-2*pi*alpha_i^2)`, then sets

    delta_i=1-a_i-5*b_i-epsilon_i.

The credited ideal row theorem bounds `||N_i-I||_infinity` by a_i+5*b_i,
including the aliases on the diagonal. Hence

    ||N_i-I||_infinity <= 1-delta_i-epsilon_i < 1,
    ||N_i^-1||_* <= 1/(delta_i+epsilon_i) <= 1/delta_i.      (3)

All quantities refer to one actual constructor. No unknown inverse bound
was used to construct epsilon_i or delta_i. The resolvent identity gives

    H_i^-1-N_i^-1 = H_i^-1 (N_i-H_i) N_i^-1,

so

    ||H_i^-1-N_i^-1||_*
      <= epsilon_i/[delta_i*(delta_i+epsilon_i)].            (4)

The separately credited ideal half-gap also gives `||N_i^-1||<=8p^2`;
therefore the simpler `128p^4 epsilon_i` is valid. We retain (4) in the
actual group invoice because its denominator matches the constructor and
the public normalizers. Identity holes contribute zero to (2) and (4).

## 4. Actual group diagonals and the complete exact comparison

Let nonempty disjoint groups G_j partition all d inverse axes. Retain the
public ledger's actual normalizer bits u_i, group totals U_j=sum u_i and
K_j, and bounds v_i with `||Dtilde_i||<=2^v_i`. Put V_j=sum v_i and

    c_j=2^(U_j+V_j-K_j),
    mu_j=2^(V_j-K_j) product_(i in G_j) delta_i^-1.

The actual admissions are `2^u_i*delta_i>=1` and `K_j>=U_j+V_j`; thus
`mu_j<=c_j<=1`. The exact normalized targets are

    G_H,j = 2^-K_j tensor_(i in G_j) (Dtilde_i H_i^-1),
    G_N,j = 2^-K_j tensor_(i in G_j) (Dtilde_i N_i^-1).      (5)

Both have norm at most mu_j. This proves their contractions from their
actual factors. It does not assert contraction of either numerical routine.
Nor does it require every individual axis to contract: a group can spend
its normalizer collectively.

Telescope (5) one tensor factor at a time, use (4), and bound the other
inverse factors by delta_i^-1. The common factors give

    ||G_H,j-G_N,j||_*
      <= xi_j := mu_j sum_(i in G_j)
                     epsilon_i/(delta_i+epsilon_i).         (6)

This is where the actual D factors and group scale are paid; dropping them
before forming the invoice would not prove the same assertion.

Let F_H=C G_H,m ... G_H,1 and F_N=C G_N,m ... G_N,1. A second telescope
uses the proved complete-group contractions and `||C||<=1`. On an original
input x of radius at most R_0,

    ||F_H x-F_N x||_* <= R_0 sum_j xi_j.                    (7)

The factor is R_0 because (7) compares two exact operators on their common
initial input. If instead a caller inserts (6) at an actual rounded
intermediate state, it must use that state's radius. We use the separate
physical-versus-H argument below and do not conflate these two comparisons.

## 5. The existing constructor radius pays the reference input radius

For every axis in G_j, call the unchanged constructor once, before any
numerical block request, at cap B_i and declared radius R_i. Require
`R_i>=2R_0`, target s_i>=t_j and legal original-period cuts. Larger radii
needed by actual dense interiors remain charged and must also be covered;
this theorem does not weaken their radius admission.

The production-gap source proof derives from the actual Gaussian.qbar

    Qstar_i>=2^21 alpha_i^2 p B_i,
    E_i=s_i+ceil(log2(8(R_i+1)Qstar_i^2)).

With alpha_i,B_i>=1 and R_i>=2R_0, this implies

    E_i >= s_i+46+ceil(log2(R_0 p^2)),
    R_0 epsilon_i <= 2^(-s_i-46)/p^2.                    (8)

These are inequalities for the constructor's existing allocation. We do not
replace E_i by a separately invented reference precision. Inserting
`delta_i>1/(16p^2)` into (6) yields

    R_0 xi_j <= mu_j |G_j| 2^(-t_j-42).                   (9)

The nominal radius in a source allocator is not free metadata: using R_i=1
at an arbitrarily large R_0 removes the cancellation in (8). Such a different
caller must retain its actual R_0/(R_i+1) factor or raise the target; it is
not admitted by the unchanged-allocation result.

## 6. The public diagonal service leaves the needed slack

Retain the exact source/geometry/tail/precision admissions of the public
group ledger. For desired final contribution 2^-tau it chooses

    h=ceil(log2 m), z=tau+gamma+h+1, eta=2^-z,
    t_j>=max(1,z+2-U_j),
    q>=max_i u_i,
    q>=z+ceil(log2(max(8,2 max_j L_j))),
    L_j=sum_(i in G_j) (((2W_i+1)2R_0+2)/delta_i),
    Lambda_j<=eta/(8R_0).                                (10)

Its actual nonlinear bridge has all-input defect E_j<=eta on radius 2R_0.
The actual source remaining-diagonal service, on radius 3R_0, proves

    e_A,j <= (3R_0+2)2^-q.                               (11)

This includes coefficient error, native product rounding and the proved
zero-drop external codec. Using that actual service is essential: a merely
postulated wrapper with allowance eta need not leave the following slack.

The literal delta_i lies in (0,1), and W_i>=0. Since each group is nonempty,
`L_j>=2R_0+2`. Equation (10) therefore gives

    e_A,j <= [(3R_0+2)/(4R_0+4)] eta <= 3eta/4.

The actual completed-group defect against G_H,j is consequently

    w_j=c_j E_j+e_A,j <= (c_j+3/4)eta <= 7eta/4.          (12)

The public actual-state induction remains valid, since this strengthens its
old bound w_j<=2eta. Its intermediate inputs are at most 2R_0 and bridge
outputs at most 3R_0; the new ideal comparison does not enlarge an actual
state or invoke a routine on an idealized state.

Because `2^-t_j<=eta*2^(U_j-2)`, (9) is at most eta/4 whenever

    mu_j |G_j| 2^U_j <= 2^42.                            (13)

This is an exact rational finite sufficient check on the actual descriptors.
A convenient stronger check, using mu_j<=c_j, is

    |G_j| 2^(2U_j+V_j-K_j) <= 2^42.                     (14)

Under (13), combine the physical-versus-H error sum from (12) with (7):

    ||actual extracted output-F_N x||_*
      <= sum_j w_j+R_0 sum_j xi_j
      <= 2m eta <= 2^(-tau-gamma).                       (15)

Exact restoration by 2^gamma gives at most 2^-tau. Gamma is unchanged:
the remaining coefficients are still `2^(U_j-K_j)Dtilde`, so each completed
group still implements (5), rather than adding a new inverse normalization.
No alias removal, input downcast or second restoration is hidden in (15).

Thus **the old precise t_j and q allocation suffices**, with the original
tau, when source targets s_i>=t_j, source radii R_i>=2R_0 and gate (13) are
bound to the same References. This is an allocation binding and proof, not
a mutation of an already frozen Reference. If a given frozen source fails
the binding, construct its replacement before any numerical consumer and
rebind every consumer; a source label alone does not repair it.

## 7. Source-first sufficient allocation and production cost

The normalizer bits u_i are determined after the actual Reference exists.
There is no need to guess them or solve a circular fixed-point condition.
Under the retained first scale policy, choose K_j and gamma independently
of the new Reference normalizer bits u_i; these are the preexisting completed
map normalizers and restoration. Choose m, tau, R_0, legal original descriptors
and source radii R_i first, and set

    s_i=max(1,z+2) for every i.                           (16)

Construct the immutable References at these targets. Their positive gaps
then determine the least dyadic u_i. The public ledger computes
`t_j=max(1,z+2-U_j)`, automatically no larger than s_i. A tighter choice may
exploit an independently established lower bound on U_j, but is unnecessary
for the complete asymptotic bill. Already frozen References whose actual
s_i cover t_j need no reconstruction.

For the conservative production family let l=ceil(log2 p). The established
eventual alpha estimate permits `v_i=2l+8`. The production-gap certificate
permits `u_i<=2l+4`, and the source's dyadic p^100 prescription can use
`k_i=100l`, K_j=sum k_i. Then

    2U_j+V_j-K_j <= (16-94l)|G_j| <= -78|G_j|.

For positive integers r, r<=2^r; hence the left side of (14) is at most
`r 2^-78r<=2^-77r<1<2^42`. This check is uniform in group size. The actual
remaining-diagonal coefficient guard, all native admissions and all
Core/halo geometry constraints remain separate inherited requirements.

For a finite small case without the eventual alpha upper bound, the valid
alternative `v_i=2alpha_i^2` follows from pi<4 and exp(1)<4. Apply (13)/(14)
with that actual bound; do not silently assign the eventual v_i to p=3.

With d=Theta(p^(1-10^-30)), balanced groups of size Theta(p^(39/40)),
gamma=O(d log p)=o(p), tau=O(p), and log R_i=O(p), (16) has s_i=O(p).
The production-gap source upper allocation gives E_i=O(p), entry/interval
grids O(p), w_i=O(sqrt(p/log p)) and
W_i=O(sqrt(p log p)+log p). The original positive-weight setup precision
remains O(p^2 log p+p); it is not an online scalar width. Actual descriptor
heights, canonical constructor AST work, coefficient preparation, tails,
comparisons and disposal remain charged.

The comparison proof constructs or scans no dense ideal N or inverse during
production. It adds O(d) rational descriptor checks, with polynomial bit
heights, to the already paid source setup. The main actual payload still has
full padded size T=product T_i. The inherited T/S<2 admission is needed to
compare its cost with the extracted source volume; otherwise retain T.
All full-volume Core/halo, routes, diagonal stock, coefficient scans, scalar
leaves, restored widths and backing costs remain those of the public packages.
None disappear when the mathematical target changes from H to N.

The source-first target (16) exceeds the minimum Core target by at most U_j
for that group. Since U_j=O(g log p)=o(p), it preserves the same O(p)
precision envelope. It can change actual width constants and must be used
when constructing those source objects; this is not a performance comparison
between two finite frozen experiments. The enormous legal-period and global
parameter onsets remain separate from the p>=2^200 sufficient alpha/precision
estimate in the production-gap package.

## 8. Prior work and the remaining ideal-analytic premise

PR #3851 already proves a resolvent comparison and normalized compression
error for its original ProductionPlan: theta about 1/d, gap 1/(8p),
P=32768p and D/2^(2alpha^2). PR #3935 composes those physical Tensor axes,
and #5325 gives their later recovery caller. Their comparison method is
credited; their numerical domain and coefficient cohort do not admit the
fine-theta Reference or the present public group normalizers. This package
does not repackage that older complete Tensor as a new theorem.

RAW-GAUSSIAN-PROOF supplies the global H-versus-N estimate and the actual
cap allocator. PR #4648 supplies the ideal half-gap budget, and the public
production-gap package binds positivity to that allocator. PR #6880 and
the public Core/halo bridge compare the rounded splice with the same H.
The public scale ledger and remaining-diagonal package supply the actual
state and wrapper contracts used in (10)--(12). The new work is the
source-first binding, the same-certificate ideal inverse, and the explicit
demonstration that the existing t/q allocation funds (15).

The weakest remaining analytic input at this boundary is now explicit:
the definition (1), prior global reference-error estimate (2), ideal row
majorant used in section 3, and interval producer theorems. Those analytic
statements are written prior theorems,
not independently formalized here. Outside this boundary one must still
join this ideal compression with the actual expansion and Fourier calls,
account for their incoming/suffix errors, and verify the exact final
CRT/convolution/restoration tolerance. No statement here removes the full
analytic_recovery assumption or any of the other four foundational premises.

## 9. Bounded verification boundary

The checker executes complete unchanged Reference.for_cap constructors;
its independent positive-series oracle uses original source offsets and an
infinite geometric tail. A full-period Neumann diagnostic is an exact
rational error certificate for its named small case, not a physical native
execution or a numerical proof of (15). The general arguments above prove
the quantified implication. Executed counts, controls, exact source pins
and receipts are recorded separately.

In the independent oracle, the full positive Taylor argument x is enclosed
by rational endpoints, without the canonical producer's range reduction or
squaring. Starting with term zero equal to one, each next term is multiplied
by the corresponding x endpoint, divided by its positive degree and rounded
outward on a fixed dyadic working grid. Induction encloses each positive
term and its partial sum. After degree n with x_upper<n+2, the remaining
positive tail is at most

    term_upper * x_upper/(n+1) / (1-x_upper/(n+2)).

Taking reciprocal endpoints encloses exp(-x). The implementation checks its
final interval width and stops within an explicit iteration cap; failure
rejects. For sufficiently large f it instead uses
`0<=exp(-pi f)<=2^-floor(3f)`, from pi>3 and exp(1)>2. No assertion of
irrational exact rounding participates in the oracle.

For every original row i, all |h|<=4 terms use j=(i+h) mod S and the original
beta_j. For |h|>4 the narrow inequality
`f>=alpha^2(h^2-|h|)` bounds the sum by the exact rational geometric series

    2*2^(-3 alpha^2*4*5)/(1-2^(-6 alpha^2*5)).

The tail includes every nonzero diagonal alias. Terms do not become zero
merely because their original source index has wrapped. The finite lower
matrix and its row-error bound therefore enclose the entire periodic N.

The two fixed-grid Neumann diagnostics are checked by their actual final
residuals, rather than assuming that an unrounded recurrence executed.
For any candidate v and matrix A with `||I-A||<=rho<1`,
`||v-A^-1 x||<=||x-Av||/(1-rho)`. For the ideal matrix, the residual also
includes the complete oracle row error times ||v||. The exact rational
Reference residual uses every source-produced nonzero entry. All vectors
are complex and every residual uses the component-l1 norm.

The named fixture has p=3, S=61, T=64, alpha=3, cap1, source radius2,
R_0=1, source target35, entry bits155, source cutoff3 and target cutoff23.
Its original holes are 11,32,53. All 4096 Reference entries and 549 independent
finite periodic terms are checked. Both Neumann diagnostics use the one named 64-component complex input x.
For that input, the certified difference of the two exact inverse outputs
is at most 2^-158; after the actual D ordering, normalization by 2^20 and
final extraction, the difference on that input is at most 2^-169. These two
figures are input-specific bounds, not measured inverse operator norms. The unchanged public budget yields
q41/Core target34 and a combined **conditional invoice** at most 2^-13 for
target2^-12. It is not an executed physical output-error measurement.
This small case uses v=2alpha^2=18 and K20. It is not the eventual p^100
family, and it does not admit complete Core geometry or the actual dense
native-radius contract. Its radius2 proves only the additional bridge-radius
binding in section 5. No larger physical obligation is inferred from it.
