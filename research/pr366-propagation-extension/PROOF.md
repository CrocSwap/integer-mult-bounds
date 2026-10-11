# Finite propagation argument and dependencies

The complete manifest of `pr364-kernel-extension` is pinned to
`6f86aaaf6d926283c7a623d18f66ab8fd9339d1536eccc162c82607f867850fb`.
The default verifier runs that parent from scratch, preserving its PR364,
PR366 and earlier source pins, structural checks, physical checks, negative
controls and exact pricing. Its portable receipt and the input word,
state and frame hashes must equal the committed parent certificate.

The input records hash is
`7b4bb2f0944d422699501ccb9a9d1cdde5b8fbe8a7877b16ee844a73f7b92139`.
Each frozen stage identifies exact input record indices, scalar incidences
and replacement integer bases. There are four connected groups: three
pairs and one predecessor triangle followed by a fourth gate. Their
register sets are pairwise disjoint. The first two pairs are applied in
separate stages; the remaining four-gate and two-gate groups are applied
together in the third stage. Every stage is checked as a complete word.

In each group, the later frame contracts from dimension 15 to 14. Its
preceding shared-register frame must contract from 13 to 12 to retain the
required inclusion. In the triangle, that contraction propagates across
all three earlier gates. These frames need not be equal. This is recursive
predecessor propagation using the existing meet rule.

Applying each of the four later gates alone creates exactly one failed
rational MOVE containment; these are recorded negative controls. Applying
each complete frozen stage must pass chronological nesting, endpoint
frames, COPY/ERASE lifecycle, exact frame/annihilator data, nondegeneracy
under the inherited bilinear form, actual integer source-span containment
and formal F2 operator replay. The signed scalar instruction projection,
including COPY/ERASE operations, equals the original projection exactly.
These checks are stronger than a dimension-only test: inclusion is checked
over the rationals, and source supports are obtained from integer replay.

The successive records hashes are:

1. `e1cb90cd9e8ea698223b47b79894eeb0c630cb880706049dd463c1cd030aba52`
2. `ea64cf5dbab663058131182772025a2fd5514211fed89973420d4818d84c42c2`
3. `b0fd6cfb9a976e07c3860a5fddd34962504db31163d5346f96fc5e7c6624fdb0`

The unchanged endpoint maps preserve the parent's exact residual census
and banking witness. The public verifier nevertheless reconstructs all
100-replica banks, checks every block occurs exactly once, and recomputes
stock: 131846 banks per stage, literal stock 1043230 and normalized stock
208646. The independent native checker verifies physical ownership,
lifetimes, all 11930 columns and its bridge-omission controls. The final
payload prefix bound stays 93 bits.

The local histogram delta is {1:-3, 2:-5, 3:+4, 4:+1, 9:+3, 10:-3}.
Its weighted rank sum is zero; its changed distribution yields the gain.
Both rational engines price the complete final histogram, retaining the
10^-16 fallback density and 32m² rank-one fallback calls for each paid
child. Adjacent coarse endpoints on the 10^-24 grid have strict opposite
moment signs. Eight finite ordinary-bootstrap steps use the same
inherited transfer as PR369. The balanced outer assembly at eta=10^-24
and beta=10^-9 checks all 47 strict inequalities and rejects the next
10^-27 saving grid point. The exact admitted saving is
804946219504150552042557 / 1000000000000000000000000000.

The result retains every conditional interface listed in the parent's
PROOF.md. In particular, exact finite frames, payload columns and aggregate
banking do not establish a new native downstream chart/route admission or
complete finite invoice. All-size compilation, prime supply, analytic
transfer, precision/recovery and related interfaces remain conditional.
No unconditional theorem or new Lean kernel proof follows from this receipt.
