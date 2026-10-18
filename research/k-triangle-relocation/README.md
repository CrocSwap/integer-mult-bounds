# K-triangle single-read relocation census

Research note and scoped negative result. No new κ.

All 841 distinct single-read relocations of one pinned K-triangle fail to improve
its raw paid profile. Exactly 708 violate a target hyperplane. The other 133
preserve all terminal frames and the profile `{1: 48, 2: 6}`.

The result concerns the negative `(6,7)` triangle in PR622's raw 492-helper word.
It does not concern the final, optimized CK or JP8 providers. Both exact frame
engines and the arbitrary-input scalar checks reproduce the certificate.

## Reproduce

Run from the repository root with Python 3.11 or later:

```sh
python3 research/k-triangle-relocation/verify.py
```

Expected output:

```text
PASS: 841 distinct relocations; 708 illegal; 133 unchanged profiles; two exact engines; six controls.
```

The command uses only the standard library. It checks four source hashes,
rebuilds the raw word in a temporary directory, and compares every certificate
field. It does not change the source files or use cached supplier outputs.
The generated word uses a canonical JSON hash, independent of gzip headers.
The command rejects `-O`, because the pinned constructor requires assertions.

`EXPECTED.json` records each permutation, the moved indices, and its outcome.
Each rejection supplies the first failing event, target register, and a binary
vector outside that target's hyperplane. Each legal case records its profile.
`SOURCE.json` pins the base, source files, assignment seed, and source PR.

## Domain and stopping rule

The operating system supplied seed 27, which selects the complex-supplier track.
The rule `27 % 4 = 3` selects triangle index 3 in `TRI-SCHEDULE.json`.
Its 30 additions occupy the half-open interval `B[178:208]` in the raw word.

For each pair `i != j`, remove read `i` and insert it at final position `j`.
There are 870 ordered index pairs. Adjacent swaps each occur twice, leaving
841 distinct permutations. The census visits every permutation once and stops.
It uses no random search, solver timeout, or floating-point objective.

Each read uses the smallest frame containing its source and target frames.
The prefix, suffix, coefficients, registers, helper allocation, and cleanup stay
fixed. The search changes only the order within this one window.

## Exact checks and cost accounting

One engine uses binary row elimination. The other stores each subspace as its
complete set of binary vectors. Neither imports the supplier's frame checker.
They independently replay the prefix, all candidate windows, and the raw profile.
The engines share traversal and certificate code.

The six source frames start at dimension two. Each target starts at dimension
zero. The 133 legal schedules have identical terminal frames on all 716 registers.
Their window pays 48 rank-one climbs and six rank-two climbs: total rank mass 60.
Source climbs contribute 24 units; target climbs contribute 36 units.

The independent full replay includes every source and helper climb, the eight
centre scatters, and the terminal climbs. It matches the constructor's profile:

```json
{"1":2024,"2":760,"3":300,"4":168,"5":168,"6":44,"8":8}
```

Its total rank mass is 6284. The suffix begins with exactly the same frames for
every legal candidate. Therefore its cost and the final restoration cost stay
unchanged. The changed additions only write targets and only read non-targets.
The cleanup contains inverses of non-target writes, so it also stays unchanged.
No extra helper, source access, copy, frame change, restoration, or child is free.

The scalar checker starts with twelve independent indeterminates, one per touched
register. It compares exact rational maps for every legal permutation. This
covers arbitrary dirty values. The window leaves the other 704 registers unchanged.
Thus the unchanged prefix and suffix give equal complete scalar maps, including
all helper columns. This establishes equality with the baseline, not a new proof
that the full supplier satisfies all its interfaces.

Identical histograms give identical sums `sum(H[r] * r**p)` for every real `p`.
There is no raw moment gain to offer the assembly or bit supplier.
This does not exclude new optimizations after porting a changed schedule.

## Negative controls

The command checks six failure modes:

- Doubling one coefficient changes the exact scalar map.
- Removing one read changes the exact scalar map.
- Replacing the last read with the first changes the exact scalar map.
- A recorded illegal relocation fails the target-cap check.
- Disabling that check accepts the same illegal relocation.
- Ignoring source climbs undercharges the window by 24 rank units.

## Scope and dependencies

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR622 source head: `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
The source package lives in `research/complex-k492-owner-repair` on this base.
The selected record remains #626/#622/#623 with #543, at conditional
κ = `0.001635527380375392`.

This is a complete census of one finite neighborhood. It is not an impossibility
theorem for all 30-read permutations, deliberate frame promotions, other
triangles, gauge changes, cold endpoints, or final provider schedules.
It does not rebuild the selected suppliers or claim formal verification.
The existing `frame_regroup` step already improves profiles through deliberate
frame promotions. Those changes lie outside this census's minimal-join rule.
See the K-triangle section of `complex-k492-owner-repair/PROOF-NOTE.md`.

All inherited all-size compiler, common-label/mutable-source realization,
whole-call hosting, normalized residual, precision/tape, exact recovery,
analytic-transfer, and bit-supplier assumptions remain unchanged.

## Prior work and attribution

Jeremy Kothe's #622 supplies AtomScout's K-triangle constructor and schedule.
The constructor retains icekylinx's #531 architecture and Dugongue's #514 scalar
helpers, with their attribution.
Chafik Boukhalfa's #626 supplies the selected package used here. Their predecessor
notices, including DreamingOfClouds' and other contributors' work, remain intact.

Concurrent #646, by Jeremy Diviney, studies eight signed-root triangles and a
480-helper construction. Concurrent #651, by Sreekanth Nair, studies target hosting
and face-register sharing. This note studies a different, fixed 30-read window
without changing triangle count or sharing rules. Neither pending PR supplies
code or an assumed mathematical result here. `CLAIM.md` records the scope check.

The final check also reads #681, Alluri's coordinate-total circuit resynthesis,
and #683, Douglas Colkitt's partial K/M bypass result. Both study different
changes to the raw word. Neither supplies a dependency for this census.

Charles Bethin prepared this contribution with substantial OpenAI Codex assistance
in research, implementation, verification, and writing. The new files use the
repository's Apache-2.0 license.
