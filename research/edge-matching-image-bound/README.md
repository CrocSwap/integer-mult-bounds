# Edge matching bounds for binary projector images

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

For binary rank-one idempotents with nonzero off-diagonal patterns,
let k be the pattern dimension and nu the maximum matching size of
the matrix-unit edge graph. The joint-image dimension n satisfies
`2n<=3k+nu`. A nonzero irreducible image satisfies `2n<=3k+nu-1`.

The total bound `floor((3k+nu)/2)` is attained for every `k>=1` and
`0<=nu<=k`. The universal total maximum is `2k`. The universal
irreducible maximum is `2k-1`, attained at every `k>=1`.

Read [PROOF.md](PROOF.md) for the full argument, [RESULT.json](RESULT.json)
for the exact finite evidence, [CREDITS.md](CREDITS.md) for source roles
and [TASK.json](TASK.json) for the scope and family decision. The proof
allows arbitrary collections. The sharp examples are complete pools.

This extends the disjoint-relation method of
[PR #7690](https://github.com/CrocSwap/integer-mult-bounds/pull/7690)
to spaces that contain matrix units. It gives linear all-k bounds.
The earlier edge-quotient bound and three-dimensional sharp example
in [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782)
remain prior work. Their graph-sensitive bound can be smaller for a
specified graph. Use both bounds where their hypotheses hold.

## Reproduce

Use CPython 3.12 with its standard library, from the repository root.

```sh
python3.12 -I -W error -B research/edge-matching-image-bound/verify.py
python3.12 -I -W error -B -O research/edge-matching-image-bound/verify.py
python3.12 -B scripts/research_package.py --package research/edge-matching-image-bound
```

Expected markers are `PASS_EDGE_MATCHING_IMAGE_BOUND` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier compares all computed
results with the committed receipt and writes no file.

It checks 224036 image-basis collections, all 2825 pattern spaces at
width three, 65 total attaining families and eight irreducible families.
The latter two sets cover 20917 nonzero patterns. Separate raw scans
and pattern lifts agree on complete pools at width three. The tests
include extra-edge and coordinate-projector controls. All claims at
unbounded width rest on the written proof.

## Limits

There is no claim of a sharp irreducible bound for every fixed (k,nu),
or of total sharpness for a specified edge graph. Coordinate projectors
are excluded. No paid BIT word, native operator, complete invoice or
new kappa is supplied. The selected frontier and all five assumptions
remain unchanged. Independent human and formal-kernel review are
unclaimed. Selected cold replay, full predecessor package replays,
Lean and Docker are not part of this package's checks.

## Open next questions

Can the attaining irreducible family support a legal paid word with
target rank above paid rank? First state the operation alphabet,
relation lattice, endpoint basis, all counted roles and native interface.
The existing five-dimensional word obstruction in PR #6782 must be
compared before any larger-core word search.
