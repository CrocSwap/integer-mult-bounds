# Scoped algebra and literal realization

All matrices here are over the rationals. R is 8 by 112, K and P are 112 by 8,
RK=14I, RP=I, and only the eight rows A of P are nonzero. Define
J=I-KR, U=K-12P and F=I-UR. Since RU=2I,

F^2 = I - 2UR + U(RU)R = I,
RF = R - (RU)R = -R,
JF = F - KRF = I - UR + KR = I + 12PR.

U is injective because RU=2I, and R is surjective; hence F-I has rank exactly
eight. F acts by minus one on im(U) and by plus one on ker(R). The target
residual 12PR is supported on A. It is not a vanishing residual.

## Serial implementation

Let r_k be row k of R and u_k column k of U. Each source subword clears C0,
computes C0=r_k(source), scatters source -= u_k C0, and clears C0 again.
For distinct k,l, r_l u_k = 0, so earlier scatters do not change a later query.
The product of these eight rank-one source updates is exactly I-UR=F.
The source remains in its boundary frame during this operation. The existing
C0 field is sufficient; no extra borrowed helper is introduced.

## Complete backward and forward words

The retained corrected local core has backward map
(x,y,h,c)->(x-Jy,y,h,0) and forward map (x,y,h,c)->(x,y+Jx,h,0).
These are reconstructed from the actual literal programs and checked on all
columns, including arbitrary dirty helper inputs.

Backward: first add 12PRy to x on the eight rows A. Then apply F to y.
The clean-J core produces x+12PRy-JFy=x-y, with source Fy.

Forward: run the clean-J core, then apply F to x. Subtract 12PR(Fx) from y
on A. Since RF=-R, this correction is +12PRx. The target becomes
 y+Jx+12PRx = y+(I-KR+12PR)x = y+Fx.

The added rank-one line repairs implement the needed boundary frame changes
on A. Their signs/phases and Gaussian action are verified separately. No
claim that this separate check establishes the complete routed native word
is made. In particular, it does not license scalar mixing between unequal
physical charts or free source decoding between invocations.

## Relation to PR1862

For PR1862's supported P and disjoint selected logger L, let Q=R-L and
Z=K-13P. Its order-six preparation is G=I+ZQ-PR. The broader source family
G+ZB includes B=-2Q-L. Then
G+ZB = I-ZR-PR = I-(K-12P)R = F.
The condition LG=R of the fixed full-query logger is dropped. The known
family and target-support idea are inherited; the specialization and its
current instances are the contribution here.

## Why this is not a new supplier bound

F^2=I permits cancellation only when the same linear coordinates and chart
are used. Each native stage routes different ports through different cover
permutations. An interposed routing operator T need not commute with F;
FTF is not generally T. A global decoder and its paid implementation must
therefore be established before replacing centre costs in any moment invoice.
All claims in this package stop at the stated local interface.


## Alternative: source-restored reflection shears

Negate the target corrections and omit the source preparation. The backward
map is (x-Jy-12PRy,y)=(x-Fy,y), and the forward map is
(x,y+Jx+12PRx)=(x,y+Fx). Helpers and private fields retain their endpoints.
No source reflection now remains to restore. The price is a changed transfer
operator: these are F-shears, not identity-shears. Their exact local rank
profiles equal the first interface's profiles, and the scalar allowance falls
to 208,310 real primitives per coordinate per call.

For one common F with F squared equal to I, the usual three-shear sequence
has matrix [[0,-F],[F,0]]. The complete inherited nine-call/bridge word can
therefore be corrected by applying F on every bank on the constant-cover
restriction. Actual stages use distinct routed charts; this same-chart
calculation does not prove closure there. A route-induced content probe fails
for the unmodified constant-cover correction (retained as an exploratory
local diagnostic, not supplied as a full native counterexample here).
