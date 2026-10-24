# Independent review of the signed coefficient annex

The coefficient theorem and its stated gauge pass this bounded review.
The result is complete for the fixed signed 48-port family and the
specified selected set. It does not supply a native schedule or a
complete supplier price. It gives no complete kappa improvement.

The reviewed annex is
`packages/reciprocal-native-responses/annexes/signed-rank-eight-coefficients`.
`REVIEW.json` binds its final manifest and proposed body. All 13 frozen
inputs match the campaign originals. Both unchanged checkers passed in
normal and optimized Python from a new temporary copy. The producer
proof, historical independent proof, matrix-source note, and both
executed checkers were read. This review includes the mathematical
argument below, rather than only the historical status or fresh receipts.

## Full-unit classification

The actual matrices satisfy KK^T=12I8, G^T=G, G^2=I48, det G=1, and
GK^T=K^T Lambda, with the fixed alternating signs in Lambda. For
D=diag(beta_v), these identities give

    E=G-K^T Lambda D K = G(I-K^T D K),
    det E=product_v (1-12 beta_v),
    E^-1=G+K^T Lambda diag(beta_v/(1-12 beta_v)) K.

These formulas follow directly from the matrix identities and retain
factor order. They need no additional component-projector assumption.
For a dyadic beta, 1-12 beta cannot vanish, since 1/12 is not dyadic.

Put R=Z[1/2] and s_v=1-12 beta_v. A product in R can be a unit only
when each factor is a unit. The determinant and inverse formulas prove
that E is a unit over R exactly when every s_v is a unit. The units of
R are the signed integer powers of two. Reduction modulo three is
defined on R and gives s_v=1 modulo three. It selects precisely

    s_v=(-2)^n_v,
    beta_v=(1-(-2)^n_v)/12, n_v in Z.

Conversely, these coefficients are dyadic for every integer exponent.
Inversion sends n_v to -n_v. This proves the infinite classification;
the finite exponent ranges in the checkers are controls only.

## Principal blocks and the count

The selected physical set is S=[0,7,15,36,42,46,79,89]. The actual
minor has det K_S=-4 and G_SS=0. Thus the selected block L has
det L=16 product beta_v. Jacobi's complementary principal-minor
identity, applied to the displayed inverse, gives the same determinant
for H on the other 40 centre ports. This remains valid when a beta
is zero, because the full dyadic response is still invertible over Q.

Consequently the two principal blocks are units over R exactly when
each beta_v is a unit. Intersect this condition with the full-unit
classification. For positive n, the odd numerator 1-(-2)^n must have
absolute value three. For negative n=-m, clearing 2^m gives the same
test for 2^m-(-1)^m. These equations give only n=-2,-1,1,2. At n=0,
beta is zero. The four coefficients are 1/16,1/8,1/4,-1/4.

Different parameter vectors give different matrices: multiplication
of K^T Lambda diag(delta) K=0 by K on the left and K^T on the right
gives 144 Lambda diag(delta)=0. There are therefore exactly 4^8=65536
distinct 48-port responses under the full-unit and both-principal-unit
conditions. This finite 48-port family is closed under inversion.

The conditions cannot be dropped. Uniform beta=1/2 has both principal
units but full determinant 5^8, which is not a dyadic unit. Uniform
beta=3/4 gives a full unit but nonunit principal blocks. Both cases
are checked. The eight centre rows and the rank of the correction
do not give a native-child count or native-cost lower bound.

## Gauge, interface, and orthogonality

In the stated order, the six factors on existing ordinary data give

    t_final=-K_T^T B(K_T t_initial+K_R0 r_initial),
    r_final=G_R0 r_initial-K_R0^T B(K_T t_initial+K_R0 r_initial),
    B=diag(alpha_v beta_v).

These expressions equal H on all inputs. The two additions are shears;
K_T, G_R0, and B are dyadic units under the stated condition. Reversing
the six factors therefore gives H^-1. No initial zero or extra centre
field is used. This proves an existing-data factorization, not a
concrete elementary-word price for every coefficient vector.

The ordered interface factors give det A=det L/det H=1 on the 48-port
part. The fixed 64-port complement has square 4I and determinant 2^64.
Its inverse belongs to the ordinary part of the full interface, which
therefore has determinant 2^-64. The full 112-port response inverse
uses one quarter of the fixed complement. Closure under inversion of
the 48-port coefficient family does not keep that complement unchanged.

Finally, E is symmetric and

    E^2=I+K^T diag(12 beta_v^2-2 beta_v) K.

Multiplication by K and K^T makes E^2=I equivalent to beta_v=0 or 1/6
for every v. Only zero is dyadic. Thus G is the only dyadic orthogonal
member of this fixed family. This statement does not exclude another
matching or reciprocal family, including the later E=P R family.

## Checks and publication boundary

The producer checks six full 112-port inverse examples and enumerates
all 65536 coefficient tuples through the proved determinant formulas.
The historical independent checker imports no producer code. It uses
integer Bareiss elimination after row-denominator clearing, nine
matrix cases, and a separate eight-step recurrence for the full
determinant distribution. It checks the six-step gauge and reverse
on all 40 columns in eight cases, both ordered interface inverse
products, and the fixed 64-port complement. It also checks the
distinction between full and principal units. These finite tests
support the source matrices; the written proof establishes completeness.

`COMMANDS.json` records the actual command. `REPLAY.json` and
`cold-replay/` retain all four receipts and logs. The runner used one
child process at a time, with `-I -B` and then also `-O`. All four
receipts match their exact frozen bytes. No normalization was used.
The runner and source manifest match the final annex. The scripts
use only the standard library and input paths derived from their
copied locations. No runtime compiler or producer module is imported.

The final package check covers every manifest entry, the exact file
inventory, new wrapper links, the proposed body, and preservation of
the earlier parent and original-J annex files. The predecessor notices
match the already reviewed parent copies. No new remote notice
verification is claimed. The older bipartite native packet is retained
as matrix source and historical context; its emitter and native word
were not rerun or adopted for the new coefficients.

Native query access, scatter placement, all native phases and helper
returns, routed composition, terminal decoding, recursive hosting,
precision, and a complete supplier invoice remain open. No result is
admitted to the current selected construction by this review. Final
commit-pinned GitHub links, rendered Markdown, and published readback
remain the coordinator's checks. This review makes no Git or publication
change. OpenAI Codex performed this review under the user's direction;
the retained notices give predecessor credit and the assistance record.
