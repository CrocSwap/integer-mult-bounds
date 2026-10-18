# Fixed-option A-triple census on PR589's selected bit word

**Scoped negative result; no new κ.** This certificate exhausts the
**Cartesian product of three frozen individually legal PR1345 single-move
option lists** for one seed-selected A-section triple in the merged PR589
R439 word. It does **not** enumerate every jointly enabled frame or
commutation-dependent triple placement. It adds a fixed-option third-order
case beyond the single-transport and pair censuses in PR #1345.

## Result

The selected operations are A-operation indices 927, 928 and 930. They all
write register 325 at frame 282, from sources 256, 442 and 392. Let `D_i`
be the fixed `(slot, frame)` option list returned by the pinned PR1345 atlas
when operation `i` is moved individually in the unchanged word. The exact
sizes are `|D_927|=7`, `|D_928|=6`, and `|D_930|=5`. We enumerate the
**entire fixed product** `D_927 x D_928 x D_930`, all 210 tuples. Each is
inserted by the verifier's deterministic move order and tested for joint
chain nesting and full paid replay; this is a completeness claim only for
that enumerated product, not for all conceivable triple moves.

| Joint outcome | Assignments | Evidence |
|---|---:|---|
| Incompatible full register chain | 46 | Exact frame-nesting score rejects the combined placement; the full word replay also rejects it. |
| Same paid profile | 100 | Full 661-register replay passes; profile equals the original exactly. |
| Strictly higher moment cost | 64 | Full replay passes; every changed profile is `{1:1326, 2:1342, 3:78, 4:44, 5:102, 6:11, 7:19}`. |
| Improvement or unresolved case | 0 | Every assignment **within the fixed 210-tuple product** is classified. |

The unchanged selected profile is `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`.
The changed profile increases the rank-one count by three and reduces the
rank-three count by one. At PR589's exact bit saving
`1733427039589844234749/10^24`, the exact outward-rational interval for the
moment-cost increase is

`[89827377253997004816123267, 89827377253997004816123311] / 15625000000000000000000000000`

(approximately `0.005748952144255809`). The interval is strictly positive.
The exact moment increment for a profile-preserving word is zero.

The selected assembly remains complex-bound at
`κ = 836330098538459/500000000000000000`. This finite triple census changes no
supplier or exponent.

## Assignment and overlap

- Track: Bit supplier; OS-random seed 5; exact base
  `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Selected input: PR589 merged head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`,
  tuned word `v=111`, `R=439`, decoder constant 63.
- PR #1345 exhausts all legal single transports and same-section shared-register
  pairs. Its README explicitly leaves triples and larger shared-register sets
  open. PR #1382 covers A/B cross-section pairs and explicitly leaves triples
  open. This package evaluates one distinct same-section triple from the large
  A component.
- The screen also checked an eight-total decoder reduction against PR #1084 and
  the PR #968/#1077 decoder-floor lineage, and the active helper-468 later-cut
  claim in Discussion #1362. Those scopes were not repeated.
- The first seed-indexed triple had only slot choices at its original frames and
  could not alter the paid profile. One bounded pivot restricted the candidate
  pool to frame-sensitive triples. The resulting pool contains 200 tuples,
  ordered by `(option product, operation index triple)`; seed `5 mod 200` selects
  index 5, `(927,928,930)`.
- Exact source Git blobs and SHA256 pins are in `SOURCES.json`; PR #1345's exact
  atlas source is vendored under `vendor/pr1345/`.

## Reproduce

From the repository root, with Python 3.11 or later and the standard library:

```sh
python3 -I -B research/bit589-shared-register-triple-seed05/verify.py
```

Expected output:

```text
PASS_PR589_A_TRIPLE_TRANSPORT seed=5 ops=927,928,930 assignments=210 valid=164 ties=100 losses=64 incompatible=46 controls=3 no_new_kappa
```

The verifier rebuilds the pinned PR1345 **individual single-move** option
lists, checks the seed selection, scores all 210 tuples in their Cartesian
product, and replays every jointly nestable reconstructed word on all 661
registers. It also checks an all-home identity, a mutated source operand,
and an omitted ADD. It does not generate new options jointly enabled by
moving multiple gates, nor enumerate alternative commutation/reordering
schedules beyond its fixed insertion rule.

## Limits and credit

This result covers one triple **only within the frozen product of three
individually legal single-move option lists and the specified insertion
convention** in one A-section component of the fixed PR589 word. Jointly
enabled frame options, commutation-sensitive legal placements, alternative
insertions, and multi-move choices absent from these single-move lists have
**not** been enumerated; the 210-tuple result cannot rule out improvements
among them. It also does not exclude a different triple, four or more
simultaneous transports, A/B cross-section triples, gate-order changes,
structural rewrites, or a different bit circuit. The bit supplier's inherited H1-H5, compiler,
realization, hosting, precision/tape and analytic assumptions remain. The
finite census is not an optimality theorem for PR589 or a proof of the full
multiplication theorem.

## Open next questions

- **Question:** Does any other frame-sensitive triple of A operations sharing
  a register lower PR589's paid profile? **Why it matters:** This census covers
  one seed-selected tuple and cannot decide whether the triple move class has
  a useful profile change elsewhere. **First step:** apply the same exact
  chain-compatibility and full 661-register replay to the remaining eligible
  triples in the pinned PR1345 atlas, with an explicit bounded search budget.
  **Blocked by:** the joint option product and candidate count grow quickly;
  each surviving assignment still needs an exact paid replay.
- **Question:** Can a useful result compose triples that share an operation or
  use different target registers? **Why it matters:** Such interactions are
  outside both this fixed tuple and PR #1345's pair census. **First step:**
  define a disjoint or shared-operation move family and price its complete
  joint domain before enumerating. **Blocked by:** the current exact transport
  scorer does not establish that overlapping move combinations preserve the
  required gate multiset and full-chain nesting.

Credit DreamingOfClouds / PR589 for the selected bit word and the retained PR555
construction; credit @hypotures and the PR1345 atlas for the exact transport
domain and cost method; credit @1337isnot1337 / PR1382 for the disjoint
A/B-pair extension. Prepared by Cinna Davis with substantial OpenAI Codex
assistance for task selection, exact enumeration, verification and writing. No
independent human review or subagents are claimed. Apache-2.0.
