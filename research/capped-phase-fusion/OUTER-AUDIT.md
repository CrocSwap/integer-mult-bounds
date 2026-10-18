# Phase-cell fusion: outer assembly audit

Historical uncapped assembly snapshot. Its prospective status and weaker numerical case below are retained as provenance. For the current capped/T74 theorem, mixed-width recurrence and completed outer review, use [phase_fusion_note.tex](phase_fusion_note.tex) and [the 14 October response](review20261014/REVIEW-RESPONSE.md). The current proof pays the complete depth-dependent product row stock and a polylogarithmic number of scans per group.

Status: assembly audit in progress. The exact arithmetic in this directory is a **conditional target**, not a replacement of the selected certificate. The remaining proof interfaces are recorded explicitly below.

## Conditional transfer statement

Assume the same finite bit/complex suppliers, common-label arithmetic compiler, semantic guard and all-size fixed-tape interfaces as the selected conditional PR1094 result. Also assume the new deferred-reservation, support-limited H supplier, shallow-circuit tensorization, and grouped sparse/core-halo lemmas below have their stated uniform implementations. Then the retained integer-multiplication reduction runs in

`O(n (log n)^(1-kappa))`,  `kappa=0.001672664764353193`.

Here p=Theta(log n) and the live scalar bit volume V=Theta(n). Global one-axis preprocessing is polynomial in the original axis sizes and p, hence `n^o(1)`. Table construction or page loading repeated per coarse block is charged to its superpolynomial `L^g` payload by the tensor/scan lemmas; it is included in the displayed V costs, rather than called one global preprocessing operation. Every cost row below is `O(V p^e polylog p)` with `1-e>kappa`. The minimum excess is greater than `10^-11`. Consequently every fixed logarithmic factor and each use of the unconditional quasi-linear short arithmetic kernel can be absorbed in a single positive fraction of that excess. Floors, rounded alpha, and dyadic L alter constants or logarithmic factors. All claims are eventual in p; one fixed finite prefix of inputs can use the retained elementary fallback. This statement becomes an admitted theorem only when the named implementation hypotheses receive the intended full review.

## Parameter convention

Let `a_bit=0.001733427039589844234749` and `b=0.001675462676808103522925` be the retained lower bounds certified by the selected PR1094 replay. For applying the older compact recurrence, lower the usable bit saving to `a_eff=(b+q)/2`; this keeps its historical convention `a_eff<b` while retaining a strict supplier margin. It does not claim a stronger bit supplier.

Use actual `alpha^2=O(log p)` as in the logarithmic diagonal-dominance audit. The symbol `r=10^-6` is only a spare upper-bound exponent: eventually `alpha^2<=p^r`. The narrow and broad Gaussian bandwidths are both `O(sqrt(p) polylog p)`. The group guard is conservatively bounded by `g p^r d`, although the actual logarithmic choice is better.

Write `d=p^epsilon`, `g=p^beta` (integer parts change constants), `L=Theta(p^8)` dyadic microbox side, and `A=Theta(p^3)` locality halo. The retained target axis lengths exceed every polynomial in p, and their logarithms are `Theta(p/d)`. Keep the retained near-one prime/dyadic capacity bound `T/S<2`.

## The exact dense-path objects

The inverse path must use the actual globally fixed rounded narrow matrix H from the retained phase-cell proof. Let C select the increasing nearest positions q_j and let E be its injection into the target grid. Define

`H_aug = E H C + (I-E C)`.

After simultaneously ordering selected positions first, this is exactly `H direct_sum I`. Thus its row gap, row norm, inverse bound and principal-window locality follow from those of H. Because q increments are one or two, its physical target-grid bandwidth is at most `2w+2`. A principal target-grid window contains a contiguous source interval plus identity hole coordinates. The inverse on the selected rows is exactly `E H^-1 C`. Multiplying its selected outputs by the retained `D_normalized/2^j` and setting its hole outputs to zero realizes compression, followed by an increasing q-image extraction.

The expansion path uses the square target-grid completion in `../gaussian_fast_ultra/FORWARD-SMALL-A-AUDIT.md`. The input is the one-pass q-image embedding with zero hole entries. Identity columns at holes make the completion invertible but contribute zero to the desired expansion. The principal non-hole phase blocks are two diagonal factors around a symmetric broad Gaussian Toeplitz matrix. Their finite inverses are polynomially bounded at `alpha^2=O(log p)` by the small-parameter bilateral LDU argument; their raw diagonal range is `O(d/alpha^2)`, below the common `O(alpha^2 d)` guard allowance. This is a different Gaussian matrix from the narrow H, and cannot be replaced by H without proof.

Normalize the completed augmented forward matrix by 4. The retained broad map has row norm below 2, so the identity-hole augmentation has row norm below 3; division by 4 is therefore a contraction on arbitrary inputs, including numerical error in hole coordinates. On the intended zero-hole subspace this introduces an additional factor 1/2 per axis relative to the former S/2 convention. Compensate by a single exact `2^D` output scale for D resampled axes, increasing the retained gamma by D. Since D=O(d)=o(p), this costs only O(d) extra bits and one O(V) shift scan. The exact Fourier/resampling identity is retained after that stated scale adjustment.

In both paths refine physical phase cells into dyadic interiors separated by O(wide-bandwidth) boundary groups. Preserve the original physical period cut. The refinement increases the boundary count by only `O(log d)` and keeps scalar Schur bandwidth O(wide-bandwidth). It uses exactly the original rounded coefficients and weights, with no local rerounding.

All target holes belong to the boundary: inside one original phase cell `q_j-j` is constant, so its selected target positions are consecutive. Hence each dyadic interior is an ordinary contiguous selected interval, not a masked Toeplitz matrix. Use the maximum broad/narrow physical bandwidth W in both directions and every separator. Using only the smaller narrow bandwidth for the forward partition would leave forbidden interior-to-interior edges.

## Five factors and the scope of the sparse union

For an interior/boundary partition M=[A B; C D], put `S=D-C A^-1 B`. The inverse and forward identities are respectively

```
M^-1 = diag(A^-1,I) E_-B diag(A,S^-1) E_-C diag(A^-1,I),
M    = diag(A,I) E_C diag(A^-1,S) E_B diag(A,I).
```

Here the two off-diagonal shears use **original** B and C, which are banded. Each sparse factor acts inside the union of the boundary slabs and the O(wide-bandwidth) neighboring interior slabs. That union is invariant during that sparse factor. A dense A or A^-1 stage can spread its support throughout an interior; the implementation gathers the sparse union afresh after each dense stage. It never assumes the union remains invariant across a dense stage.

There are a fixed number of dense tensor stages and sparse union stages per group. At a dense stage the generic circuit tensorizer supplies all g local circuits together, with cost `O(V g^(1-q) polylog p)`, plus its paid bit routing. Distinct cell origins and dyadic size classes change coefficient tables and switch controls but not the common routing schedule. Identity blocks use identity stages. No data-axis padding by a constant factor is permitted.

Each compiled H stage is invoked on the **whole complete tensor stream across all coarse labels**. It is not separately invoked inside one fixed coarse-label microbox. The H schedule selects the same local bit positions for every label and its completed operator preserves all coarse coordinates. The coefficient-dependent diagonal stages run between completed H calls and may scan one coarse block at a time. Thus a supplier may temporarily borrow complete high/coarse bits from the selected original dyadic axes and restore them before a diagonal is evaluated. This distinction is necessary: `log2 L` local bits alone are shorter than a `K=128G` compact neighborhood.

Every selected bit can have a complete K-bit neighborhood from its original axis, because the true axis bitlength is `Theta(p/d)` and eventually exceeds every fixed multiple of log p. The supplier's internal coordinate frames must be implemented by support-limited permutations involving only those g neighborhoods, its O(gG) reserved controls and O(log g) row roles. The union of these positions is O(g log p); the endpoint routing therefore costs `O(V g^(1-a_eff) polylog p)`, not a fresh `O(V p^(1-a_eff))` at every H call. The independent support audit must verify the actual compact frames, rather than inferring this charge solely from the final selected-bit support. The initial global microbox gather and final inverse gather may still use the separately paid full-address router.

## Target-grid cores avoid non-dyadic dense halo fields

The dense path uses only the dyadic L-sized target cores. It does not pad the retained `(L+2A)` target halo length to 2L on every axis. For compression, the row-Neumann locality proof is applied to `H_aug` (bandwidth at most `2w+2`); enlarging A by a fixed factor covers that bandwidth and the q-image conversion. Core outputs within a fixed multiple of A of any microbox boundary are repaired by separately gathered sparse halo rectangles. Outside those strips the principal-core inverse has the retained exponentially small row error. Expansion is banded after Gaussian truncation and has the same simpler core/halo split.

Partition exceptional outputs by the first exceptional axis and side. For halo thickness a fixed multiple of A, the exact rectangular-copy count is `O(V g A/L)` per group. Process only those copied rectangles by the retained sequential g-axis local algorithm, with temporary padding of its **current single field** removed after each operation. Its cost is bounded by

`O(V (g A/L) g [1+w^2/d] polylog p)` per group,

plus sparse sorting and metadata. This is negligible at L=Theta(p^8), even if the group-key length `K=O(g p/d)` and another fixed polynomial factor are charged. The original local contraction and tensor error argument applies to each rectangle, because all its inputs are original group inputs and unprocessed axes retain their supplied halos. Erroneous principal-core edge outputs are discarded, never recycled as purported global halo values.

The full source-to-q-image embedding and its inverse extraction preserve lexicographic order in each coordinate. Enumerating the target rectangle and testing all q-image predicates costs O(p) per p-bit coefficient record. They therefore take one O(V) pass, using the retained near-one volume bound. The same record accounting permits membership tests for the sparse union in one pass. Multiplication by a separable diagonal uses the tensorizer's nested prefix-product scan; it does not multiply g coefficients afresh for every scalar record.

## Remaining old outer rows

The main synthetic transform must use the deferred-reservation layer from `../radical_reduction_ultra/README.md`, including the support-limited global layout replacement. Its total cost is `O(V[p^(1-a_eff)+p*d^-q] polylog p)`. In particular, retaining the old per-top-axis bit moves or power-width reservation condition would reintroduce an invalid row. The common-layer recurrence may use any fixed stopping exponent `t_stop>0` with `(1-t_stop)b>a_eff` and `q<(1-t_stop)b`.

For each visited coarse block and group, all required local coefficient pages can instead be regenerated in polynomial time in p: there are g local windows of size at most L=Theta(p^8), their rational origins have O(p/d) bits, and the published local coefficient/Schur/circuit constructors are polynomial in that size and requested precision. Recover local phases and anchor gauges from these origins; do not form a raw uncentered global q² exponential on the data. The page contains O(p)-bit online coefficients. Its polynomial setup and sequential loading are amortized by the complete `L^g` payload, which eventually dominates every fixed power of p. This gives an explicit access method even when the coarse labels are permuted; no random global coefficient-table lookup is assumed.

Global chirps, twists, positive diagonal normalizations and exact scale factors are separable products. The prefix-product scan supplies their products in O(V polylog p), with completed scalar range `O(d alpha^2)=o(p)`. Packed polynomial products retain their saving epsilon. The finite supplier, exact common-label frame, whole-call hosting, semantic depth bound with C1=1, phase precision, prime packing and fixed-tape input/output assumptions are inherited unchanged. They are still conditional interfaces, as in the selected result.

## Cost ledger, with conservative wide bandwidth

Let `h_w=1/2` and `h_K=beta+1-epsilon`. Normalize all costs by V. Fixed logarithmic factors are absorbed by strict gaps.

| Component | power of p | reason |
|---|---:|---|
| main transform | `1-epsilon*q` | deferred reservations |
| constant global coordinate routing | `1-a_eff` | paid support/full router |
| dense Gaussian groups | `epsilon-q*beta` | `(d/g) g^(1-q)` |
| grouped bit routing | `epsilon-a_eff*beta` | same grouping, bit supplier |
| one/fixed group scans | `epsilon-beta` | d/g groups |
| boundary algebra | `(omega-1)*h_w` | batched w-column Strassen |
| sparse union, basic movement | `beta+h_w` | V g w overall |
| sparse union, conservative key surcharge | `beta+h_w+h_K` | full active-group keys |
| polynomial products | `1-epsilon` | retained short polynomial products |
| core-face corrections | `epsilon+beta+3-8+2` | old local maps on sparse copies, with a loose p² allowance |

Use the rational upper bound `omega<45/16`, checked by `7^16<2^45`. The target balances the first and third rows exactly before a fixed 10^-11 absorption backoff.

This ledger is accepted only after its circuit tensorizer, grouped sparse route, target-grid core/halo adapter, forward small-a inverse bound, and deferred-reservation interfaces have written proofs. Exact positive inequalities alone do not discharge those interfaces.
