# Replication removes the eight-replica rank restriction

## Local word and frozen transformations

Start with eumemic's byte-identical PR #436 R740 word. Expand each grouped ADD
into its ordered primitive ADDs and apply 57 frozen frame changes. The ordered
scalar operands are unchanged. For every changed gate, the PR #417 retimer
checks its integer source-support lower bound and both neighboring register
frames in the joint configuration. All frames remain nested.

Apply a 114-pivot shared-donor response kernel with 103 donor slots and total
entrance rank 138. Each pivot p has an entrance E contained in its first frame
and every donor's first frame, and response(p) = XOR response(donors). Start p
at E, remove its frame-zero target correction, and add it to those donors at E
before A and again at FULL after C. Pivots and donors are disjoint; each donor
uses one entrance. The exact local replay checks all 980 independent columns,
including all helper dirt, and integer source-span legality. Frozen input,
intermediate and output hashes bind both transformations.

The PR #417 kernel code is retained unchanged. A separate adaptation keeps its
local checks and replaces only its eight-replica rank congruence with

```
T * (8R - entrance_rank) = 0 mod 64.
```

After the kernel, transplant the two frozen PR #441 joint B-frame stages: 112
paired-gate changes and 42 window changes, with 126 net changed B frames. The
original witnesses remain byte-identical and pinned. Their frame choices are
independently checked against the new word's joint feasible intervals, integer
source supports and complete arbitrary-dirt replay; input/output hashes are
recomputed for this composition. Every scalar ADD and its position is retained.

The complete selected word has local paid profile
`{1:2530, 2:1008, 3:280, 4:347, 5:118, 7:14, 8:9}`. The forward and reflected emitted
streams have the same profile, restore arbitrary input columns and erase each
private copy. The initial 57-frame retiming and PR #440 selection supplied a search
starting point; this selection retains two additional rank-one pivots.

## Why 32 replicas are admissible

The compressed nine-stage identity is an identity for one data-replica index.
Its four data pairs, alternating local calls, nine paired bridges and terminal
exchange do not refer to any other replica's data. Repeating that schedule for
four groups of eight replicas therefore gives a direct sum of the original
identities. The local eight-dimensional frames, 64-dimensional ambient form,
42-dimensional largest child, cover class and port maps are unchanged.

Banking changes only the embeddings of helper residuals. The local theorem holds
for arbitrary independent helper dirt. Assigning every helper residual an
injective isometry into a disjoint bank interval preserves this theorem. The
same proof applies when those intervals belong to different replica groups:
no data owner is shared across groups, and each stage's helper intervals are a
partition of its entire bank coordinate space. The emitter and independent
audit enumerate all 288 calls and all 213,120 helper owner assignments, check
every data owner formula, and reject cross-group data aliasing, omission of a
replica group and an incorrect replica count. They also replay the one-replica
nine-stage identity on 7,620 unbanked scalar columns, which is the repeated
block identity, not a claim to replay 32 separate enlarged matrices.

Here `8R - entrance_rank = 5782`. Eight replicas would require 722.75 banks;
32 replicas require exactly 2,891 banks. Thus 32 is the least positive multiple
of eight satisfying the exact bank equation. No incomplete bank is counted and
no padding calls or unused bank coordinates are introduced. Merely repeating a
fixed eight-replica word scales its profile and stock equally and gives no
rate improvement; the gain comes from admitting the stronger untrimmed kernel.

## Residual routes and accounting

Every distinct entrance has a stored integer matrix N with N N^T = 4I. Its
first dim(E) rows span exactly E, checked against every root of E. The remaining
rows give an isometry of E-perp to a coordinate block. For these 16 entrances,
N/2 is a coordinate permutation, reduced to identity with at most seven swaps.
Extending it by identity on 56 exterior coordinates and permuting coordinates
places the residual into its assigned interval. This is an explicit isometry
for I_64/2 at every inherited odd address prime. Reversal has the same residual
projector I-P_E; the common exterior window cancels from the endpoint difference.

Per stage, the exact bank partition is:

- 424 banks with widths `(7,7,7,7,7,7,7,7,8)`;
- 16 banks with sixteen width-four blocks;
- 2,451 banks with eight width-eight blocks.

Each coordinate is used exactly once. The independent audit checks all intervals,
frame IDs, orthogonal matrices and elementary route factors. It rejects reused
slots, wrong frames, altered bases, missing route factors and omitted calls.
The 32 replicas use `8*120*32 = 30,720` data families. Hence live stock is
`30,720 + 9*2,891 = 56,739`, with nine sequential private-centre reserves giving
physical stock 56,748. The paid profile is 288 times the local profile plus
23,040 rank-seven idle children and 15,360 each of ranks 14, 28 and 42.
Its rank deficit is `64*56,739 - paid_rank_mass = 9,984 = 32*312`.
No rank mass, idle move, copied centre or bridge is omitted.

## Finite and analytic gates

The finite invoice is recomputed with T=32, the larger live/physical stock, all
288 local calls, replicated bridges and copy episodes, and explicit residual
routes. It charges 144 additional elementary route factors per helper routing,
covering seven local swaps and 64 coordinate swaps. The prefix bound comes from
the emitted forward and reflected programs. Independent replicas act on separate
data and disjoint residual coordinates; sequential private copies are erased,
so replication does not multiply the per-coordinate coefficient-growth bound.
The invoice nevertheless charges every emitted operation and route.

Both rational moment engines must certify the bit lower endpoint
`0.001140121438872176364117`, including the inherited 10^-16 bad-branch allowance.
The maximum child still satisfies `2*42^2 < 64^2`. The newly computed two-level
coefficient must fit the retained 512-bit budget and row coefficient 18,355.
With the cited PR #433 complex rate, six ordinary bootstrap levels and all 47
strict outer inequalities give conditional
`kappa = 1138823042306561 / 1000000000000000000 = 0.001138823042306561`.
The adjacent 10^-18 grid point and invalid outer parameters must be rejected.
These are release-verifier requirements, not substitutes for its receipts.

The original all-size compiler, correlated dirty-bank, compressed-window,
restored-work, tape/common-grid, precision and analytic assumptions remain.
The complex supplier and its mutable-basis interface are cited from PR #433;
this package does not rerun its Gaussian phases or prove an unconditional theorem.
