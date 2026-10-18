# Sufficient construction and scope of the exponent claim

## 1. The signed prefix identity

Fix a donor target j and a destination i, whose initial values are arbitrary, independent dirty inputs y_j and y_i. Assume the donor is unchanged and no modified destination is ever a donor for another rewrite. Let P_i and P_j be the exact sums of source values delivered to those targets before the chosen cut. Source values are indexed by physical register, write version, and the frame in which the delivery occurs.

For any rational q, replace the original destination prefix by these three operations:

1. At their common initial zero frame, set Y_i := Y_i - q Y_j.
2. Deliver P_i - q P_j to Y_i, cancelling equal versioned source/frame tokens.
3. At the common recovery frame, set Y_i := Y_i + q Y_j.

At the cut, the donor contains y_j + P_j. Therefore the new destination contains

    y_i - q y_j + P_i - q P_j + q (y_j + P_j) = y_i + P_i.

This equality holds for every initial source and helper value, not only clean inputs. The donor and all other roles are unchanged; subsequent operations therefore see exactly the original state. The retained centre scatter precedes this prefix and is included in the full replay. Its contribution to donor and destination is handled by the initial subtraction and final restoration, so it cancels by the same identity.

The 25 selected pairs have distinct destinations and distinct donors, with no role overlap. Their rewrites commute on their separate target pairs. The search supports a broader donor-star selection but the actual witness has fanout one; no shared-donor benefit is claimed. Six rational scales were screened, but the selected coefficients are only +1 and -1.

## 2. Legal frames and the exact saving

Cancellation is allowed only for equal source/register-version/frame tokens. We retain every old helper/source visit, even when its scalar delivery disappears. Every newly consecutive frame must be nested. Setup and recovery are literal scalar operations in a common frame; their primitive costs and endpoint adapters are included.

The actual local paid histogram changes by:

| Rank | Number of calls changed |
|---:|---:|
| 1 | -8 |
| 2 | -8 |
| 3 | -7 |
| 4 | -8 |
| 6 | -14 |
| 7 | +23 |

Both sides have total rank mass 161. For every exponent 0 < p < 1 and every removed rank r < 7, r^p > r * 7^(p-1). Summing gives a strict improvement of the child moment. Calls also decrease by 22 per invocation, so the fallback per-call toll decreases. There are 72 invocations; the global number of paid calls decreases by 1,584 relative to the R781 baseline. No rank mass or live stock is removed by this rewrite.

## 3. Dirty response, private workspace and phases

The exact full raw operator and retained totals agree with the baseline. The source/helper subword is unchanged. Consequently its literal old-response K and cleanup are still valid. The main compiler is extended to emit the new target-to-target adds, and both complete orientations are replayed over all 1,021 independent live columns (including 781 dirty helpers). Private registers must finish zero. The emitted local frame events and global owner maps are audited independently of the scalar equality.

Exact Clifford representatives, both directed child edges, and source/target endpoint adapters include Gaussian phases. A symplectic-label equality alone would not suffice. The global finite schedule uses the nine-stage recipe and explicit whole-bank slots, corrections, padding and cover owners; it is not inferred solely from a moment histogram.

## 4. Exact pricing and conditional assembly

The reconstructed complex profile has m=73, live stock 14,709, physical stock 15,500, rank mass 1,071,261 and deficit 2,496. Its coarse saving is bracketed by independent exact rational moment engines. The unchanged bit construction has certified coarse saving 255384852701747/250000000000000000. The complex side binds.

The outer assembly uses six fixed ordinary bootstrap levels, positive eta=beta=10^-18 and an explicit 10^-24 backoff, then the 47 strict inequalities. The final rational kappa is 125311832453733/125000000000000000. The bundled outer proof gives the finite cutoffs and required row/constant bounds. Floating-point discovery scores never establish this value.

The sufficient implication is: if the inherited all-size supplier, ordinary-call, workspace, precision and analytic contracts described in the outer proof hold, then the changed finite construction and exact outer inequalities give the stated conditional saving. This package checks its finite witnesses and inequalities. It does not supply those missing all-size contracts or claim an unconditional multiplication algorithm.

## 5. Rejected alternatives

The research notes retain bounded searches, exact algebraic extensions, and source-dual scalar witnesses. They contribute no extra priced saving. In particular clean-response quotienting must explicitly recompute dirty compensation; matching clean columns alone is insufficient. No failed bounded search proves a global optimality barrier.
