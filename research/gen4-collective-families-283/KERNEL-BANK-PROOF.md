> This is an intermediate-stage proof/review. Final endpoint-aware quantities and exponent are in README.md and PROOF.md.

# Dirty-input kernel condensation and complete 120-replica banks

This note proves the finite algebraic transformations used by the kernel and bank stages. The starting circuit is the pinned generation-four construction from [PR276](https://github.com/CrocSwap/integer-mult-bounds/pull/276), at commit `d428ab0462b9dfd3131ab4e89999f0adcd6173dd`. Sixteen explicitly selected terminal sinks are applied first. The kernel selection is then rebound to that actual circuit; its gains are not added to gains measured on another circuit.

The result of this stage has 741 kernel pivots, total entrance dimension 1552, 19914 physical registers, and 16394 helper roles. Five of the original 746 kernel rows conflict with removed sink helpers and are excluded. The original cut 520031 becomes cut 519967 after the sink transformation. All geometric, response and lifetime checks use the rewritten circuit.

Later retiming stages may alter the paid child histogram while preserving the scalar map and endpoints. Such stages need their own exact checks, followed by fresh final pricing. The theorem below and the complete bank allocation remain the kernel stage's sufficient justification; no exponent is inferred by adding estimated gains.

## 1. A universal identity for arbitrary dirty inputs

Work over the binary field. Register values may be single bits or vectors of bits of any common length. Separate the participating helpers, indexed by a set H, from all remaining registers X. Let the original word consist of a prefix L followed by a suffix S, and write its endpoint map as

    T = S L = diag(T_X, I_H).

Thus the original circuit restores every participating helper and its final data output is independent of their initial contents. No helper is assumed initially zero. Because the participating helpers are not modified before the selected cut, the prefix has block form

    L = [ A  C ]
        [ 0  I ].

Partition H into pivot coordinates P and donor coordinates D. For every pivot p choose coefficients a_dp in the binary field, supported on D, satisfying the full response relation

    C_p + sum_d a_dp C_d = 0.                         (1)

The finite witness uses coefficients zero or one. Define N on helper coordinates by

    N e_p = sum_d a_dp e_d,     N e_d = 0,

and define Q = I + N. Since no pivot is a donor, N squared is zero. Hence Q is invertible, with inverse I - N; over the binary field the signs coincide. Extend Q by the identity on X and call the resulting register map U.

Delete the original initial compensation reads from pivot helpers. Each participating helper has remained equal to its own initial value throughout the prefix, so deleting these reads changes only the corresponding columns of C. The modified prefix is

    L_0 = [ A  C Pi_D ],
          [ 0     I  ]

where Pi_D retains donor coordinates and kills pivot coordinates. Equation (1) says exactly that C Q = C Pi_D. Direct block multiplication therefore gives

    U L_0 = L U.

Execute U at the cut, retain the original suffix, and finally execute U inverse. The complete new endpoint map is

    U inverse S U L_0
      = U inverse S L U
      = U inverse T U
      = T.                                          (2)

The last equality follows from T = diag(T_X, I_H). This proves correctness for every initial input, including arbitrary dirty helper values and arbitrary correlations among them. The argument does not need an assumed decoder, an unproved response oracle, or an invertibility hypothesis on A.

Each nonzero a_dp becomes the paid gate `donor_d += pivot_p`; the final inverse subtracts the same pivot at the full helper frame. These shear gates commute even when several pivots share a donor, because a destination is never a pivot source. All final helper values, including shared donors, are restored by (2).

For this application, prefix helper influence outside the target registers is exactly the corresponding identity column. Thus the matrix C in (1) is checked by the complete target response, rather than by a hash or a sample of target coordinates.

### What is actually checked

The transform checks that every participating helper starts at the zero address frame and ends at the full frame; before its cut it is never modified or involved in COPY/ERASE and is read only by permitted zero-frame compensation reads into targets. An independent prefix program recomputes the actual binary response at every selected cut. In this checkpoint it checks 1304160 target-kernel equalities and 39993262 non-target identity bits for 1612 distinct participating helpers.

The emitted word is separately replayed on every one of the 19914 formal input coordinates, forward and inverse, with the actual temporary row used for each COPY. It must implement the specified endpoint map, not merely preserve a response rank. Deliberately omitting the entire entrance shear layer or its inverse must produce nonzero incorrect output columns; the transform rejects vacuous controls.

## 2. Address geometry is a separate exact obligation

The binary identities above concern bit values. They are not assertions that the same cancellation holds over the integers. Integer ADD signs are retained in the physical transcript for inverse operations, signed coefficient bounds, and costs.

Address frames live in a different layer. They are rational subspaces of a 24-dimensional address space with nonsingular symmetric form

    G = I - J/9.

A selected entrance E has a full-row-rank basis matrix U_E. Its Gram matrix U_E G U_E^t must be nonsingular. Define its orthogonal projector and residual projector by

    sigma_E = U_E^t (U_E G U_E^t) inverse U_E G,
    P_E = I - sigma_E.

Let V_E be a basis of the nullspace of U_E G, and let

    B_E = [ V_E^t | U_E^t ].

Nondegeneracy gives a direct sum of E and its G-orthogonal complement. Consequently B_E is invertible and

    B_E inverse P_E B_E = diag(I_(24-dim E), 0_(dim E)).   (3)

The chart checker constructs these matrices and verifies both inverse products, the orthogonality equations, and (3) using exact rational arithmetic. It does not infer a valid chart from the dimension alone. Each elimination pivot and emitted coefficient is guarded by an explicit numerator and denominator bound. The retained odd address prime is larger than these guarded nonzero factors, so the rational charts transport to that prime field. This odd-prime address calculation is distinct from the binary data calculation.

### Legal chronological execution

Each entrance E must be contained in the actual first required frame of its pivot and every donor. Pivots begin in their admitted entrance frames. Donors retain their original entrance and move through the required frames before the shear gates. For a donor shared by several relations, the required frames must form a containment chain in chronological order. At one common cut, comparable frames are ordered by increasing dimension and then pivot identifier.

An independent checker follows every physical instruction. It checks exact containment with arbitrary-precision integers, matching frame states at each ADD, each positive-rank MOVE charge, the actual source of each COPY, its immutable lifetime, matching ERASE, final frames, and exclusion of source-owned or forbidden donor roles. It also rejects fresh frame identifiers that collide with inherited ones. The 24 COPY/ERASE pairs remain explicit operations, not uncharged assumptions.

The raw movement-rank saving telescopes to dim(E) per pivot. For this sink-rewritten baseline, the checked raw rank mass decreases from 425358 to 423806, a decrease of 1552. This identity alone is not an exponent bound: different child-rank histograms with the same total rank can have different recurrence moments.

## 3. Conditional donor costs and the search method

For search only, write psi(r) = (r/120)^(1-a), with psi(0)=0. Suppose a donor's original first-use rank is r and its selected nested entrance dimensions are

    0 = d_0 <= d_1 <= ... <= d_k <= r.

Its actual recursive contribution along this chain is

    sum_i psi(d_i - d_(i-1)) + psi(r - d_k).

This is charged once for the donor. Charging a complete new entrance independently for every relation would overcount shared work. The new search keeps circuits that worsen the moment when used alone if their incremental cost is beneficial after existing donor frames are installed. It also chooses information sets that prioritize already installed donor directions.

These floating-point scores nominate candidates only. The frozen witness contains explicit relations and frames; it does not require trusting the search or its objective. Final counts come from the emitted word, and final moment inequalities use rational interval bounds. No global optimality claim is made.

## 4. A complete bank construction for 120 replicas

A helper with entrance dimension d has residual rank r = 24-d by (3). Run 120 disjoint replicas, with banks of width 120. Every residual block must occupy exactly one slot; no overlapping scratch or missing helper is permitted.

The sunk baseline has 266 residual-rank-three helpers, 2200 residual-rank-four helpers, and 13928 initially full residual-rank-24 helpers. The kernel stage changes 741 of the last family. The unchanged and changed blocks can be assigned as follows.

* Forty rank-three blocks fill a bank. Across all replicas the 266 helpers require 798 such banks.
* For each changed helper of residual rank r, use 30 banks. Each bank holds four of that helper's rank-r replica blocks and 30-r rank-four filler blocks. Its width is 4r + 4(30-r) = 120. All 120 replicas of the helper are used exactly once.
* There are initially 264000 rank-four replica blocks. The preceding mixed banks consume 179940; the remaining 84060 fill 2802 banks of thirty rank-four blocks each.
* The 13187 remaining full-rank helpers use 24 banks each, five rank-24 blocks per bank.

The resulting bank count per stage is 342318. Including the inherited data stock, the five-stage literal stock is

    844800 + 5 * 342318 = 2556390.

The normalized stock used in the recurrence is 511278. The general count is the baseline bank count minus the total entrance dimension; here that subtraction is exactly 1552.

The allocation checker enumerates all 9836400 stage/replica/helper assignments and checks every occupied address coordinate for collisions and gaps. It also checks each distinct bank pattern on all endpoint coordinates: its block swaps compose to the full bank exchange, both forward and inverse. Omitting or repeating one block must leave exactly the expected nonzero endpoint discrepancy. The largest block index is 40 in the rank-three pattern; this index is not confused with the width or the number of banks.

The one-replica five-stage circuit is independently checked on its complete formal columns. Disjoint replica namespaces then give its 120-fold direct sum. This extension is an elementary disjoint-coordinate construction; it is not a claim that the global column checker separately enumerated all 120 copies. The allocation checker does enumerate their actual bank assignments.

For this kernel checkpoint, the exact chart audit covers all 741 new frames, with maximum measured chart factor count 312. The finite invoice retains its explicitly larger normalizer allowance and charges the resulting routing and selector operations. It does not treat changing the replication constant or adding banks as free.

## 5. Counts, prime arithmetic, and exact pricing

Let h_r be the actual number of rank-r children in the local emitted word. The normalized five-stage profile uses

    H_r = 120 h_r + 48 * 1760 * indicator(r in {4,23,46,50}).

The literal profile is five times this normalized profile. Its checked deficit is 528000. All scalar additions, coefficient-expanded additions, COPY ranks, stage bridges, routing, normalizers, selectors and fallback children are counted from the actual composed word and admitted stock.

The finite arithmetic stage uses the address prime 2^127-1, verifies the associated Lucas-Lehmer computation, and retains the complete rare-child fallback term. It bounds the recurrence moment by two independent rational interval engines. It accepts the chosen coarse endpoint and rejects the adjacent finer-grid endpoint, propagates the supplied ordinary-leaf recurrence through eight finite levels, and checks all 47 strict outer assembly constraints and seven reported margins. No floating-point search score is used as proof of these inequalities.

Before any later retiming, the fully audited sixteen-sink/741-kernel checkpoint has conditional

    kappa = 724251636106082822039023 / 10^27.

This is a checkpoint value, not a promise that a subsequently edited transcript has the same price. The package's final result must be read from the fresh receipt for its final word, and compared with the public baseline under the same retained interfaces.

The finite coefficient is the coefficient counted for this explicit construction. It is not a replacement for an unknown larger constant in an inherited all-size theorem. When such a larger constant is required, it must enter the stated cutoff formula; the finite invoice does not silently set it equal to the smaller counted coefficient.

## 6. Frozen evidence and reproduction

The frozen kernel witness supplies each pivot, its complete donor support, the actual cut, and an exact rational basis of the entrance frame. The sink witness and its old-to-new role map are separate explicit inputs. Physical compatibility filenames containing `249` are retained by the tools, but they refer to the pinned generation-four or sink-rewritten export supplied as the baseline argument; they do not identify the historical PR249 word.

A complete replay performs these dependent steps:

1. Regenerate the pinned PR276 generation-four physical export.
2. Apply the sixteen selected sinks, checking their complete physical word and emitting the new role map and actual cut.
3. Rebind the kernel witness to that map, explicitly dropping the five conflicting rows.
4. Run the kernel transform on that sink-rewritten baseline, obtaining the literal word, frames, initial states and replay receipt.
5. Run independent prefix and chronological legality checks, exact chart and complete bank checks, and complete five-stage formal-column checks.
6. Apply any separately declared retiming stages with their own source-bound checks, then repeat every affected final-word audit.
7. Recompute the literal finite invoice and exact assembly price, checking the pinned input and output hashes.

The kernel-stage command interface is:

    kernel-transform BASELINE_EXPORT KERNEL_SELECTION OUTPUT_DIRECTORY

The output directory must exist before using the inherited emitter. The independent prefix and legality checkers take `BASELINE_EXPORT`, the emitted directory, and a receipt destination. The bank checker additionally takes the emitted initial-state and new-frame files. The final verifier orchestrates these commands and hash checks; the discovery search is not part of the trusted replay.

## Scope

This is a finite, explicitly checkable construction and a conditional exponent improvement within the public framework. The inherited all-size compiler, common weighted charts, restored-row interfaces, selectors and routing, prime/precision/recovery mechanisms, complex supplier and analytic assembly assumptions retain their original status. The finite identities, inventory and exact arithmetic above do not prove those separate general interfaces. No unconditional integer-multiplication theorem, practical runtime improvement, or Lean certificate is claimed.
