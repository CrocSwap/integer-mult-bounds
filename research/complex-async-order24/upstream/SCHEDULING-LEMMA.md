# Sufficient asynchronous whole-owner scheduling lemma

This is a mathematical composition proof, not Lean certification. It applies to the complete-call interfaces already retained by PR496. It does not permit splitting a residual across physical owners or stopping before dirty workspace restoration.

Let physical families be mutually independent vector spaces. A local invocation is an explicitly implemented finite word whose COMPLETE endpoint factors as its intended data operation on one replica and one prescribed residual operator on each distinct helper owner; all private workspace and borrowed spectator coordinates are restored. A pending idle child on a family factors into commuting coordinate residuals on disjoint coordinate blocks and its complementary remainder.

A finite schedule is sufficient if:

1. For each data replica it preserves the order of all of that replica's data operations, including bridges and recipe phases.
2. Every helper use occurs inside the pending child's interval on the OWNER replica's timeline, and that owner is not an active data family in the invocation.
3. Pending coordinate blocks allocated to different uses are disjoint; all blocks and the one complementary remainder cover the original pending child exactly.
4. Every complete invocation has distinct physical helper owners and finishes its entry wrappers, scalar body, cleanup, exit wrappers and full cover sweep before the next invocation. It restores spectators even when later calls will use those coordinates actively.
5. All allocated residuals and the remainder finish before the owner replica's next operation that depends on completion of that pending child.

Then the schedule has exactly the same complete endpoint as the original controller. Proof: replace each completed local invocation by its established block-diagonal endpoint. This is valid on arbitrary dirty input, hence remains valid after any preceding invocation. On each family, data operations occur in their original order. Between two consecutive such operations, the only newly ordered factors are residuals on disjoint coordinate blocks; they commute, and their product with the remainder is the original pending child. Regroup these factors inside each family interval. Their product is unchanged, so the overall controller endpoint is unchanged. No operation is commuted through an unfinished scalar body, and no independent-dirt claim is inferred merely from a logical alias. The full-cover right-translation bijection and actual owner maps remain premises of each complete invocation.

Replica lockstep is therefore unnecessary for this sufficient composition argument. The construction still needs an explicit schedule, owner injection, full maps, interval checks, and paid profile.

## Prefix bill

The old synchronized prefix bound cannot be copied without checking its batching premise. If nine bridge rounds become as many as seventy-two ordered bridge sweeps, a safe logarithmic envelope should count those sweeps individually, alongside the seventy-two complete local sweeps, exact local transient norm, and conversion from entry sup norm to full-family L2. Enlarging the finite coefficient allowance is allowed if the outer assembly pays it. Alternatively an independent argument can retain a tighter norm bound by tracking disjoint active replicas. This is an invoice issue, not an extra recursive child count.

## Structural source

OpenAI FourierCircuit/WordScheduling.lean gives fixed-support scheduling and substitution identities. The proof above uses the same support-sensitive mechanism, with completed normalized invocations as its indivisible units. SparseShear's whole-call-index constructions reinforce why physical supports, not just abstract row dimensions, must remain explicit.
