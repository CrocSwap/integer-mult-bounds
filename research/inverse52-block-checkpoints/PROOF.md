# Clean sampler blocks with exact history and gate counts

## Contract and result

Use the exact finite-window sampler from the retained PR #7773. Its inputs
are `0<=a,b<52`, in two six-bit words, and L resident coin bits. The circuit
returns the ordered source label and first stopping depth if it completes
by coin L. Otherwise it returns label zero, completion zero and depth L+1.
The deterministic pair `(0,0)` has label zero, completion one and depth zero.
For arbitrary initial output bits the full contract is

```text
(a,b,coins,out,0_work) -> (a,b,coins,out XOR result,0_work).
```

The new circuit keeps this contract and every ordered coin path. It uses

```text
clean work bits = 559 + 51*ceil(2*sqrt(L)).
```

Its gate count remains linear in L. All parameters and resident coins stay
unchanged. Their `12+L` input wires and the `3+bit_length(L+1)` output wires
are excluded from clean work and must still be supplied. Thus this is a
reduction in additional clean work, not a sublinear total-space claim.

The construction applies classical reversible checkpointing. It is not a
new general simulation theorem. It supplies a complete Boolean gate list
for this particular sampler, including exact stopping depth, partial blocks,
copies and cleanup. No new kappa or physical sampler admission follows.

## Block schedule

Choose an integer block length B with `1<=B<=L`. Put `K=ceil(L/B)` and
`q=L-(K-1)*B`. There are K blocks. Put the short block of length q
first and use length B for all later blocks. The last block has length B.
Each sampler state has 51 bits. Allocate K checkpoint states
and B reusable local states, all initially zero, plus the source's 559
temporary bits. Checkpoint zero contains the prepared state at time zero.

For every block except the last, run its draw oracles into the local states.
Copy the final local state into the next zero checkpoint with 51 CNOTs.
Reverse the draw oracles to clear all local states. Keep the checkpoint.
This is a clean XOR oracle for the block endpoint. Its input checkpoint
stays unchanged. The same oracle can later clear its output checkpoint.

For the last block, run its B draw oracles and copy the final completion and
masked label to the external output. No final checkpoint copy is needed.
Reverse this local computation. Then visit the earlier blocks in reverse
order: recompute each block, XOR its endpoint into its retained checkpoint,
and reverse its local computation. This clears each checkpoint before its
predecessor is cleared. Finally reverse preparation.

Every state needed for cleanup is present at the time of use. Every local
and temporary field returns to zero. External output wires never control a
gate. The schedule therefore gives the stated XOR oracle even if those
output wires initially contain arbitrary bits.

## Exact first stopping depth

Let `s_t` be the completion bit at time t. These bits are monotone. The
source's exact formula is

```text
depth = (L+1) XOR XOR_(t=0)^L [(t XOR (t+1))*s_t].
```

During each nonfinal block, accumulate the terms for its start state and
its local states except the endpoint into the output depth word. Its endpoint
is the start of the next block and is counted there. During the final block,
include all B+1 states, including time L. Every time from zero through L
is counted exactly once. No depth term is repeated during checkpoint
cleanup. The proof of the source formula therefore applies without retaining
all L+1 states at once. In particular, it preserves the first stopping
depth even when later coins are read during recomputation.

The constant word and the increment masks use exactly `2*(L+1)` gates.
Completion and the two masked label bits add one CNOT and two Toffolis.
The source's exact censoring masses remain
`Pr(label i and completed)=floor(2^L*w_i/2704)/2^L`, with
`w=((52-a)(52-b),(52-a)b,a(52-b),ab)`. The censoring probability is at most
`3/2^L`. This statement requires independent fair coins conditional on a,b.
The circuit identity itself holds for every resident coin string.

## Complete Boolean bill

Let r be the last block length, which is B in the new schedule. There are
`D=4*L-2*r` clean draw-oracle uses: four per coin in a nonfinal
block and two per coin in the last block. Preparation runs twice. Each
nonfinal checkpoint is copied twice. Put `p=popcount(L+1)`. The exact counts
from the emitted gates are

```text
X       = 260 + 90*D + p
CNOT    = 2449 + 717*D + 102*(K-1) + 2*L - p
Toffoli = 934 + 170*D
total   = 3643 + 977*D + 102*(K-1) + 2*L
work    = 559 + 51*(B+K).
```

For `B=L`, K=1 and r=L. These formulas recover the original complete
history bill: `3643+1956*L` gates and `610+51*L` clean bits. This is also
an executed positive control. The source preparation and draw oracles are
unchanged; all extra work comes from checkpoint copies and recomputation.

| L | B | K | Final block | New clean bits | Original clean bits | New gates | Original gates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 2 | 2 | 2 | 763 | 814 | 15,477 | 11,467 |
| 16 | 4 | 4 | 4 | 967 | 1,426 | 58,693 | 34,939 |
| 64 | 8 | 8 | 8 | 1,375 | 3,874 | 238,965 | 128,827 |
| 127 | 13 | 10 | 13 | 1,732 | 7,087 | 475,729 | 252,055 |

These are logical gate and wire counts, not elapsed-time or physical-memory
measurements. No coin delivery, owner extraction or tape scan is omitted
from a claimed physical bill: no such physical bill is claimed.

## Optimal block choice within this architecture

Allow any partition of L into K positive block lengths, with maximum B.
The least possible sum `S=B+K` is `ceil(2*sqrt(L))`. Indeed `B*K>=L`
implies `B+K>=2*sqrt(L)`. Conversely, the balanced integers with sum S
have product `floor(S^2/4)>=L`. Taking `K=ceil(L/B)`, one short block
and K-1 full blocks attains the lower bound. This proves the clean-work
formula for this architecture, including unequal block lengths.

For fixed B and K, the gate count is least when the last block has the
maximum length B: those coins use two draw-oracle calls instead of four.
Move a longest block to the end to attain that bound. Among choices with minimum
work S, put `K=S-B`. The feasible B values satisfy `B*(S-B)>=L`. With
the last block full, the gate count is a constant minus `2056*B`. Thus
the largest feasible B uniquely minimizes gates as a function of B. Different
nonfinal block partitions can share that bill. The selected short-first
partition attains it, with

```text
S = ceil(2*sqrt(L))
B = floor((S+sqrt(S*S-4*L))/2).
```

Integer square roots implement these expressions exactly. The checker
compares the selection with all 524,800 maximum-block choices for
`1<=L<=1024`, and with all 65,535 ordered partitions for `1<=L<=16`.
The written argument proves the all-L claim. This optimum concerns only
the stated one-level architecture with K retained checkpoints and B local
states. It is not a lower bound for arbitrary reversible circuits, deeper
checkpoint schedules or a different memory-reuse discipline.

## Evidence and remaining work

All 32 retained files are pinned by Git blob and SHA-256. The unchanged
source arithmetic checks cover all 2,704 parameter pairs and all 2,704
residue doublings. Whole-circuit forward and reverse checks inspect every
input, coin, output, checkpoint and temporary bit in 940,486 cases:

- All coin strings for all 2,704 pairs at L=1,3,4,8.
- All stopping prefixes with both constant suffixes and all live prefixes
  for all pairs at L=16. This is not all length-16 coin strings.
- The same prefix coverage for 16 named pairs at L=31 and L=64.
- All length-8 strings for those 16 pairs at block lengths 1,2,3,5,8.

The certificate names each pair and domain. Scalar gate replay provides
a separate execution check. Dirty-output lanes pass. Omitting checkpoint
cleanup or omitting a block-boundary depth term fails. Generated counts
agree with the formulas at 14 lengths through 127, including the complete
history positive control.

The complete predecessor periodic-edge and historical circuit suites are
not rerun. Their source proofs and receipts remain pinned. The finite
checks support the composition proof; they do not enumerate all L or all
long coin strings. Full unbounded sampling, censored continuation, fresh
coin delivery, owner extraction, tape movement, clean-stock funding and
actual caller installation remain open. Discarding or restarting censored
draws does not generally preserve the intended distribution.

No selected cold replay, Lean, Docker, independent human or formal-kernel
acceptance is claimed. The selected frontier and all five assumptions stay
unchanged. The next useful task is a caller that explicitly handles censoring
and pays for physical access and stock.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
