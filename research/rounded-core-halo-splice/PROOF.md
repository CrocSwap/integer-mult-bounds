# A rounded core/halo splice on one immutable reference

Prepared for @CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.

## Claim and precise change

This is a new numerical composition theorem at the open boundary of Jose
Manuel's `rational-unitary-fft/CORE-PROOF.md`. That predecessor supplies a
rounded, all-input finite-core inverse contract against a *single rational
reference*. The present theorem consumes that contract, retains its error
at every output, and obtains a complete cyclic inverse approximation by
pre-copying sparse inputs and replacing discarded outputs. It also gives a
tensor error and an integer-recovery substitution rule.

The new halo polynomial is the direct row-gap Neumann polynomial below,
not the normal-equation polynomial in #4100 `HALO.md`. Thus this is a
proposed, explicitly described alternative sparse correction, not a claim
that an unchanged existing implementation already computes it. Its purpose
is to close a numerical composition implication, not optimize an exponent.
No global coefficient-generation, physical compiler or multiplier premise
is discharged. In particular, the predecessor core contract is an explicit
input theorem, not independently accepted here from its finite receipt.

## 1. Domain and common input state

All coordinate lengths, bandwidths and cutoffs N_i,L_i,W_i,A_i,J_i are
integers, with N_i,L_i,A_i,J_i positive and W_i nonnegative.
For each axis i, let its period N_i be a multiple of L_i, with at least two
cores. All indices and matrix paths below use canonical cyclic coordinates.
Let H_i=I-E_i be a fixed real rational matrix, with cyclic bandwidth W_i,
and ||E_i||_infinity <= rho_i < 1. Put delta_i=1-rho_i and K_i=1/delta_i.
Zeros, holes, phase boundaries and the period cut are entries/coordinates
of this same H_i. No translation-invariance assumption is made.

Use ||x||_* = max_j (|Re x_j|+|Im x_j|). Real matrix absolute row sums
bound this norm. The proofs also apply with arbitrary additional RHS or
spectator coordinates, since the norm takes their maximum.

Choose J_i>=1 and b_i=(J_i-1)W_i. Partition each axis into ordinary cores
C of L_i consecutive coordinates; let A_i>b_i and L_i>4A_i. A row is kept
only when its local coordinate lies in [A_i,L_i-A_i). Its distance to the
core complement is then greater than b_i. At least W_i coordinates lie
outside each core, so its principal section is an ordinary window as
required by the predecessor. Require this last condition explicitly if
W_i is not already below A_i.

Choose a power of two a_i>=K_i. The exact normalized target is
B_i=H_i^-1/a_i. Its infinity norm is at most one. All numerical core
calls must be funded for the same declared input radius R>=1, and must
refer to exactly H_i[C,C]. A nonlinear routine C_i,C is admitted if, on
every incoming-grid vector z with ||z||_*<=R, it satisfies

    ||C_i,C(z)-H_i[C,C]^-1 z||_* <= epsilon_i.          (1)

The grid preservation and domain hypotheses of the actual core routine
are part of (1); they are not inferred from a matrix condition number.
The subsequent division by a_i is an exact dyadic shift, with its extra
fractional bits retained. If an implementation truncates that shift,
its error must be added to epsilon_i/a_i.

For the actual cited core theorem, epsilon_i=2^(-t_i-1). Its hypotheses
include the certified gap of its fixed narrow reference, funded raw-child
accuracy at its amplified radius, an ordinary window and its common grid.
Its proof accounts for the actual interior, sparse and boundary calls.
We reuse that statement; the verifier here does not rerun those circuits.

## 2. Local polynomial and inverse tails in the caller norm

Define P_i=sum_{j=0}^{J_i-1} E_i^j and tau_i=K_i rho_i^J_i. Neumann
convergence gives

    ||H_i^-1||_infinity <= K_i,
    ||P_i||_infinity <= K_i,
    ||P_i-H_i^-1||_infinity <= tau_i.                 (2)

Every principal section E_C has the same row-sum bound. Its polynomial
P_C and inverse H_C^-1 obey (2) with the same constants. Multiplication
paths contributing to E^j move at most jW_i in cyclic distance. A kept
row cannot leave C in at most J_i-1 steps. Therefore, after zero extension,

    row_r(P_C)=row_r(P_i)                            (3)

exactly. This concerns paths of the fixed reference, not paths of the
rounded core program. A core circuit can have global internal dependence
inside C; equation (1) pays its entire output error. Equations (2)-(3)
give the kept-row operator comparison

    ||row_r(H_C^-1 R_C-H_i^-1)||_1 <= 2 tau_i.        (4)

There is no factor for the number of cores or the length N_i. A block
diagonal collection of section inverses has norm at most K_i. Replacing
rows is bounded row by row in infinity norm, rather than by summing the
norms of all output masks.

## 3. Correct read/write chronology

For one axis, the numerical splice is the following transaction.

1. From the incoming array x, copy every input required by the discarded
   output rows' P_i evaluation, preserving its destination and cyclic
   coordinate. These copies contain the **pre-core** values.
2. Execute each complete core inverse on its core, normalize by a_i and
   retain only the kept outputs. The discarded locations may temporarily
   contain arbitrary core outputs.
3. Compute each discarded output from the saved input copies using the
   appropriate absolute-coordinate row of P_i/a_i. Return each output
   exactly once, then erase copies and work.

Here P_i is the polynomial of the global fixed E_i. Form its coefficients
globally or in a sufficiently large local dependency neighborhood first,
then restrict those already-formed rows to the copied rectangle. This is
not permission to replace P_i by the polynomial of E_i restricted to that
rectangle: boundary paths of those two polynomials can differ. The finite
verifier uses entries of the globally formed P_i for every halo axis.

The conceptual common x is not a required extra dense copy: all sparse
inputs are gathered before any dense core mutation, and the core circuits
can then overwrite their own data. Source ownership, tape moves and the
cost of the copied volume remain paid implementation obligations.

For g axes at once, a kept output lies in the Cartesian product of all
core interiors. The discarded outputs are partitioned by their first
boundary axis and side, exactly as in `halo-copy-enumeration`. On each
such rectangle save its expansion by b_i on every axis before modifying
the dense array. The row of the tensor product of the P_i depends only
on those saved coordinates. Periodic lifts and destination keys are
essential; sparse source addresses are not required to be unique.

Reading the already transformed core array in step 3 does not compute
P_i x. The negative control in the verifier demonstrates this failure;
it is not dismissed as a small local rounding error.

## 4. Rounded halo rows and one-axis bound

Let m_i=min(N_i,2b_i+1). Round each real coefficient of P_i/a_i toward
zero to a dyadic grid h_c,i. Accumulate its products with the saved
incoming data exactly on the product grid, then round each completed
real and imaginary output component toward zero to grid h_d,i. This
explicit elementary evaluation has, for ||x||_*<=R, error at most

    eta_i = m_i h_c,i R + 2 h_d,i.                    (5)

The first term is the absolute row sum of coefficient errors times R;
the second is the two final component errors. Intermediate product sums
have magnitude at most R, since inward rounding cannot increase the
absolute row sum and ||P_i/a_i||_infinity<=1. Products of dyadic inputs
and coefficients and their finite sums need their combined fractional
width plus O(log m_i) accumulator bits. No exact rational inverse is
used on the online data by this halo evaluator.

For a one-axis splice against B_i, (1), (4), and (5) imply

    error <= max(epsilon_i/a_i + 2 tau_i R/a_i,
                 eta_i + tau_i R/a_i).               (6)

This holds for nonlinear rounded core routines and all their allowed
inputs. It does not assume a linear error operator or zero discarded
core error. Each output uses exactly one branch, hence the maximum.

## 5. Tensor splice and domain induction

Suppose g>=1, incoming radius R0>=1, and all core calls are admitted for
R=2R0. Set c_i=epsilon_i/a_i and assume sum_i c_i<=R0. Within a complete
core box execute the normalized core stages axis by axis, preserving the
incoming grids required at each stage. The exact section maps are
contractions. Induction gives, after k stages,

    error relative to their exact tensor product <= sum_{i<=k} c_i,
    actual input/output radius <= R0+sum_{i<=k} c_i <= 2R0.  (7)

Thus the all-input contract (1) applies at the *actual rounded state*;
there is no appeal to invertibility of rounding or to an ideal radius
for the actual state. Direct sums over cores do not increase this bound.

For a kept tensor row, telescope the tensor product of zero-extended
section inverse rows and full inverse rows. Each normalized row has
l1 norm at most one, and (4) bounds its difference. Consequently the
kept-output error relative to the global tensor B=bigotimes_i B_i is

    E_keep <= sum_i c_i + 2R0 sum_i tau_i/a_i.          (8)

For discarded outputs apply P=bigotimes_i(P_i/a_i) on their saved
rectangles. Sequential axis evaluation with inward-rounded coefficient
rows has norm at most one before each final truncation, and the final
truncation cannot increase ||.||_*. Thus every actual halo state has
radius <=R0; using R0 in (5) is valid. Axis errors add, and tensor
telescoping of (2) gives

    E_halo <= sum_i eta_i + R0 sum_i tau_i/a_i.         (9)

The complete output, including all periods, holes and faces, satisfies

    ||output-Bx||_* <= max(E_keep,E_halo).             (10)

No exponential factor 2^g for face copies, number-of-core factor,
dimension-to-norm conversion or internal-core locality assumption
appears in (10). Copied volume and numerical error are different ledgers.
The complete rectangle tensor evaluation must keep all intermediate
coordinates required by later axes, as an ordinary full tensor product
on the expanded rectangle; premature row cropping is not licensed.

## 6. Quantified precision and source parameters

For requested total error zeta>0, one sufficient allocation is

    sum_i c_i <= zeta/4,
    R0 sum_i tau_i/a_i <= zeta/4,
    sum_i eta_i <= zeta/2,
    sum_i c_i <= R0.                                 (11)

Equations (8)-(10) then give error <=3zeta/4<zeta. For 0<rho_i<1 use
rho_i^J <= exp(-delta_i J); since K_i/a_i<=1, it suffices to take

    J_i >= delta_i^-1 log(4gR0/zeta).                 (12)

For rho_i=0 take J_i=1 and the tail is zero. Equation (12) is an
allocation inequality, not an instruction to approximate logs without
certification: rational powers rho_i^J give an exact acceptance check.
Coefficient/data precisions may be chosen from
m_i h_c,i R0<=zeta/(4g) and 2h_d,i<=zeta/(4g).

At #4100's row gap delta>=1/(16p^2), W<p and integer p>=2, the explicit
choice J=16p^4 gives tau/a<=exp(-p^2) and b<16p^5. For p>=2, 16p^5<p^48. Thus every b-expanded half-open input
interval is contained in the same interval expanded by the source A=p^48;
Cartesian products preserve that containment, including cyclic lifts.
The source core side L>=p^400 still exceeds 4A. Use a=2^ceil(log2(16p^2)); its inverse is an exact
dyadic shift. For g=p^beta, beta<1, R0<=2^(Cp) and zeta=2^(-C'p),
the tail requirement holds eventually, with C,C' fixed. Taking requested
core t=O(p+log g) and halo coefficient/data widths O(p+log p+log g)
is sufficient. The existing core's own preparation, gate coefficients,
temporaries and physical delivery are still governed by its contract.

The g exact shifts add sum_i log2(a_i) fractional bits to a preserved
incoming grid. With the displayed a_i this is O(g log p)=o(p), not zero.
Undoing all normalizers multiplies by A_total=product_i a_i and can
amplify an error by that same factor. It must be included in L_s or
L_rec in Section 7. The eventual O(p) width statement survives this
o(p)-bit increase; it does not authorize dropping the scale numerically.
If the exact shifts are folded into already paid output writes or
existing group diagonals they need no additional dense traversal.
Otherwise their traversals must be charged. This proof does not assert
the old complete execution tariff for an implementation that introduces
one new dense scan per axis.

The replacement P needs only a polynomial-size local neighborhood for
each row. Given the required absolute-coordinate reference entries, computing one
local row/neighborhood of exact rational coefficients by finitely many
matrix products is polynomial in p, reference coefficient bit size and
coordinate bit size. This is a per-neighborhood offline observation. It
does not price generating every distinct global row, obtaining its
reference entries, a uniform global page service or physical setup. The old conservative sparse
copy-volume allowance continues to contain the smaller dependency set;
its enumeration and physical costs are not re-proved here.

## 7. Exact integer recovery: what the splice supplies

For this section only, use the usual complex-modulus supremum norm
||x||_C=max_j |x_j|. The preceding splice bound transfers because
||x||_C<=||x||_*. A normalized complex Fourier transform is a
contraction in ||.||_C; it need not be a contraction in ||.||_*.
Let a completed source transform have exact contraction U in ||.||_C.
Suppose replacing a narrow inverse stage by this splice contributes at
most L_s E_splice after the known exact suffix and scalar compensation,
and all other paid errors total e_other. Then its completed error is
e=e_other+L_s E_splice. A suffix bound L_s must be supplied; it cannot
be discarded because the inner inverse was normalized.

For the three-transform convolution, assume the exact forward outputs
have radius at most r, each implemented transform has error <=e on
all *actual* inputs used, and the rounded pointwise multiplication has
error <=v. If the two forward errors are <=e, the product error is
at most 2re+e^2+v. The exact final transform is a contraction, so the
returned normalized convolution error is at most

    (2r+1)e+e^2+v.                                   (13)

For integer recovery scale L_rec and exact real integer coefficients,

    L_rec ((2r+1)e+e^2+v) < 1/2                       (14)

suffices for unique nearest-integer recovery. The no-cyclic-wrap condition,
CRT/Fourier identity, final call domain and exact L_rec remain separate
premises. In the conventions of `certified-gaussian-recovery`,
L_rec=S_total^2*2^(2b+4), including both S_total factors. This is a
substitution rule for a complete budget, not a claim to have instantiated
that budget for the selected recursive supplier.

## Open next questions

Bind pre-copy, core mutation and unique-return chronology to one actual
physical tensor caller with production-admitted shared-reference pages.
The first test should inspect every saved value before dense mutation,
including a periodic corner and a hole. Global page production, the
actual caller's L_s, and the complete fixed-tape cost remain blockers.

Independently review the retained all-input core contract at its pinned
source and replay its actual circuits. This package's exact tests check
the new composition identity and failure modes; they do not certify that
predecessor implementation or the all-size Gaussian gap.

Credit Cinna Davis/#4100 for the Gaussian core/halo plan; Jose Manuel/
jmbarrancoml/#4205 (retained via #4253) for rounded finite-core execution;
Nick Petalas/#4217 for polynomial locality and its factor-two correction;
the `halo-copy-enumeration` authors for sparse destination semantics;
Mason Hale/#2313 for certified Gaussian-to-integer recovery; Vlado
Vojdanovski/#1673, Jeremy Kothe/IdeaOuter/#1758, Chafik Boukhalfa/#1786
and the retained Harvey--van der Hoeven analytic lineage. Classical
Neumann convergence and tensor telescoping are not claimed as inventions.
