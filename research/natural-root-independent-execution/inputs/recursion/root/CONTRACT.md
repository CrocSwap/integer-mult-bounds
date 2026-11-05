# Natural root descriptor contract

Preserve the sealed all-depth core unchanged as `inputs/core/`. The new
program supplies only physical positive canonical binary T,R_body,w,
readonly unary d and the complete payload. It is not supplied A0,R0 or H.
Compile-time parameters L,q,N remain fixed as in the retained source.

The retained physical width prefix produces H=q^(N²(w−1)). The added root
prefix then delivers A0=T*(L*H)^d and R0=H*R_body, with all three descriptors
at the exact body origins required by the old node entry. It uses one fixed
27-tape table for the L4/q3/N1 instance, two more tapes than the 25-tape core.
The extra tapes hold readonly T and R_body. All old scratch/return roles are
reused and physically retired before entering the old core.

The algorithm copies T into the owned root-A field, constructs a dummy L*H
descriptor by the existing finite-carry constant-L multiplier, and uses the
unchanged shape producer's H*R product to deliver root R. For each physical
unary depth mark it applies that same H*R product to the current A and then
multiplies by L. It restores the unary depth head. No executed instruction
performs host powers, multiplication, division or descriptor decoding.

Linking changes only the old H-generated-to-entry jump and old final halt:
the former enters the appended root prefix; the latter enters owned A/R
cleanup. Every other old instruction remains identical, including the whole
recursive node, CALL/RETURN, grant production and protected output protocol.
After the core returns, generated root A/R are erased; original T,R_body,w,
depth and payload are preserved. Generated descriptors earn no credit.

The root-prefix bill is O_template(V0), not O(d*V0): with g=L*H>=2,
the intermediate A_k=T*g^k grow geometrically, so their sum is O(A_d),
H times their sum is O(A_d), and d*g<=A_d for d>=1. This also charges the
repeated dummy-LH conversions and every actual copy/retirement. The written
proof must include d=0, original descriptor lengths, w/H generation and
visited physical backing. The existing core's occurrence-sum time and
geometric active-chain space remain separate charged terms.

This closes one actual root-shape input premise. It does not generate
numerical ancestor weights, root padding T, w or d from the integer input,
or an ordinary BIT/Gaussian leaf. No kappa or complete production claim.
