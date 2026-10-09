# Physical word and conditional transfer

The source pins are Swapnil Jain's `741e7aa078392553815df7926ee17ac5e25a8c38`
and icekylinx's PR104 `948ce1510df750f4c18b96bdaef436a86f8bf834`.
The complex producer is Rohan Arun's PR113 `0eee4d507092a96bde88de703f07574ba17401a8`,
combining PR111's cyclic strip sums with PR108's dual-suffix identity credited
to PR55. Avi Eisenberg's PR110 supplies the closely related full-frame
deferred-readout comparison. This witness selects partial subframes instead.
The proof below changes their finite implementations while retaining their
analytic, ordered-affine streaming, restored-row, exact-recovery, and fixed-tape
interfaces. The round-seven stage-two complement reversal is an explicit
source premise. This document does not turn those premises into machine proofs.

## Complex word

For the all-disjoint h=24 producer, let `L` be its actual matched invertible
addition/copy word and `J` its signed rational output scatter. The retained
centers are `A_i=sum_{T not containing i} X_T`; `sum A_i=21 sum X_T`.
The central scatter `sum A_i/21 - sum_{i in S} A_i/2`, plus half the disjoint
sum and minus half the intersection-two sum, equals `X_S`. Thus `J L V=I`
on fresh input contributions. Write `C=J L` for the complete adjoint readout
matrix, including its cancellations over Q. The old-scratch correction is
exactly `-C a_0`, on arbitrary dirty scratch `a_0`.

Reconstruct the matched physical roles, not just the abstract DAG. A closure
under the recorded per-role event precedence computes all retained centers
first; disjoint events commute. It includes carrier anti-dependencies and preserves every role's full incident-event order, including read/read frame dependencies. The repaired retained closure has 32,488 events. All 209,340 event accesses and both retained and ordinary root-read boundaries preserve the original nested paths; an earlier scalar-only split order had 2,948 uncharged descents and was rejected.
For every selected role u, the closure and input injection leave its value
unchanged, so a delayed read still returns `a_0[u]`. Direct reads for the other
roles run at frame zero. Retained-center scatter also runs at zero. The
selected direct reads then run along the checked target frame chains, followed
by the remaining forward word and its side scatters. The reverse addition/copy
word and inverse injection restore scratch exactly. Algebraically, the net
target increment remains

`J L(a_0+V x)-C a_0 = x`.

The reconstruction checks actual carrier links and ordering. The exact signed
adjoint has 11,678,073 nonzero slot-target coefficients per invocation; after
multiplication by 42 they are integers of absolute value at most 42. Each
selected subframe sigma_u is contained in its first owner frame and in every
target hyperplane receiving a nonzero adjoint coefficient. All these subframes
and every target-chain residual are nondegenerate. Alternating subframes and
residuals use PR104's general inverse-Gram phase and its paid Gauss normal form.

For a tensor auxiliary role, let H be its h-dimensional frame inside the
full m=h^2 space F. Define `q_U(x)=wt(P_U x) mod 4`, using its orthogonal
projector over F2, and `C_U=H_F diag(i^q_U) H_F`. This definition includes
alternating nondegenerate U. Orthogonal sums give `q_{U directsum V}=q_U+q_V`.
All C operators commute. For sigma contained in H, put

`G=(F orthogonal-minus H) directsum sigma`.

In stage one, choose source phase `+q_sigma` and sink phase `q_F+q_sigma`.
Let B be the role's first owner frame, a subspace of H of rank b. The first
residual becomes `q_{B orthogonal-minus sigma}` and the last becomes
`q_G`; their ranks are `b-dim sigma` and `m-h+dim sigma`. The completed
route is still `q_F`. In stage two choose source phase `-q_sigma` and sink
phase `q_F-q_sigma`; the initial complement residual is again `q_G` and the
final sigma-complement frame equals the sink. These are positive residuals.
No extra phase or recursive child is discarded.

For a partial sigma of dimension d inside a first frame of rank b, replace
one internal rank-b child by rank b-d, and one auxiliary rank-(m-h) child by
rank m-h+d, per invocation and stage. Split each affected target's rank-(h-1)
front into its actual nested chain differences. These substitutions preserve
the rank mass exactly. The complete complex histogram has 40 positive bins,
`m=576`, `W=164065440`, total rank `94499831360`, and maximum child 572.
It includes `N=4096576` rank-one endpoint copies, `2N` rank-529 data macros,
and all `4N` rank-23 data fronts before their selected chain replacements.
The copied-center transition adjustment is internal: 24 rank-24 transitions
become rank one, while the rank-23 copied transforms remain.

The exact rational moment is less than one at
`a_c=5893637/62500000000`, with upward-enclosure gap exceeding `1.5e-13`.

## Whole-projector bit word

Every frozen nonzero bit edge is a partial swap of a proper rational
idempotent P. Nested projector differences, complements, and the data tensor
residuals are idempotents. Include the complete finite list from both stages
when selecting the common rational basis. For each rank-r P, its required
leading-minor polynomial is not identically zero, since P is similar to
`diag(I_r,0)`. A finite product is nonzero on irreducible GL_m. Rational
enumeration therefore selects one common basis with all required minors
nonzero. Choose an odd address prime after excluding its finitely many bad
denominators and pivots. This affects addresses, while payload XOR remains F2.

Give the second bank opposite atom order throughout the word. PR104's full
involution factorization, with lower triangular intrabank factors and a lower
cross-bank shear, converts every proper rank-r edge to one contiguous reversed
child of width r*f. The fixed factors use O(f) paid atom passes. Zero-rank
edges need no call; no full-rank child occurs. This global interpretation and
common-basis choice commute with the source's scalar word and preserve its
completed endpoints. They do not justify omitting any physical gate.

The complete bit histogram has 46 bins, `m=529`, `W=108516254`, total rank
`57403754177`, and maximum child 528. It contains each auxiliary edge of rank
`m-h+f_u`, all slot, target and input chain differences, all copied centers,
`2N` data residuals of rank 484, and `N=3136441` rank-one endpoint copies.
It preserves the source deficit `W*m-s=1344189`.

The stopped recurrence, normalized by volume, is

`T(n,w) <= sum_r (n_r/W) T(r floor(n/m),w) + C n + C w^(1-a_old)`.

The exact moment at `a*=15513/125000000` and the positive rank deficit yield
`T(n,w) <= A n + B n^(1-a*) w^(1-a_old)`, uniformly in n,w. Set
`w=ceil(e^(1/1000))`. The paid two-call outer wrapper converts the completed
reversed operation to ordinary interchange once outside recursion; remainders
use the old ordinary interface. Thus the ordinary saving is

`a_b=(999/1000)a*+(1/1000)(384599/10^10)=1240183559/10^13`.

The adapter saving `1/1000` exceeds a_b, as required. Binary/radix-q padding,
complete spectators, borrowing, and restored rows use PR104's stated contract.

## Exact grid, paid toll, and simultaneous rows

The changed complex scalar coefficients have only odd divisor 21. Use one
common exact grid `2^-P 21^-K`, with `K=G(D+1)` for maximum unfinished-call
depth D. Completed children have Gaussian-dyadic coefficients on arbitrary
dirty inputs; they do not increase the existing odd denominator exponent.
Only unfinished local programs contribute new odd factors. Scale once at the
outer boundary, never round or rescale at child returns, and unscale only
after the completed Gaussian-dyadic endpoint. The additional O(log d) bits
and boundary work fit the retained linear record and positive-power bounds.

Charge 16 primitive scalar operations for each signed adjoint term of magnitude
at most 42, including fixed multiplication, sign, and exact division by 42.
Keep the predecessor scalar allowance as an overestimate for the other gates.
The total group bound is

`G=2019773888+2*2024*11678073*16=758385205952`.

Recompute `E=64(W+m+G+1)^3`, the literal charge, `B=s+E`, and `C0=32mB^2`.
The exact certificate checks the literal charge below E and
`2B(m-maxchild)>s+E`; these imply the completed-child height induction
`A(e)<=2Be` and retained linear precision exponent `C1=1`.

The simultaneous reserve is the product of coarse bit, complex and old
ordinary leaf stocks. Their exact halving factors are 367, 100 and 9, and
wire bit lengths are 27, 28 and 28. The coefficient is

`367*27+100*28+9*28=12961`.

Use `p^27000` complete preceding rows. The degree gap is
`27000-(51/25)*12961=13989/25>0`. All copies and outer wrappers reuse
restored rows. The corresponding suffix requirement is eventual for every
fixed epsilon below one. Larger absolute constants change the threshold,
not the stated exponent.

## Conditional assembly and certificate scope

Use the retained semantic/bulk assembly with `beta=10^-6`, `eta=10^-8` and
bit parameter weakened to `(1-beta)a_c-10^-10`. The exact checker recomputes
all 47 constraints and seven output margins after substituting the new finite
constants. Their minimum exceeds `942802139/10^13` strictly.
Consequently, under the source premises listed above,

`T(n)=O(n (log n)^(1-kappa))`, `kappa=942802139/10^13`.

The Lean kernel certificate checks the supplied histogram inequalities and
signed rational parameter arithmetic without axioms. The real analytic
logarithm/exponential enclosure lemmas, algorithmic word transfer, and retained
all-size analytic and machine interfaces remain separate mathematical claims.
Successful kernel arithmetic does not establish an unconditional theorem.
