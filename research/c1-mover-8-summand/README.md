# c=1 movers miss the 8-dimensional dihedral summand

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

No element of the `c=1` stabilizer that moves the trivial-character `(+1,+1)`
216-space preserves the 8-dimensional dihedral isotypic summand inside that
space. For every one of the 2304 movers, the image of the summand misses the
216-space entirely. No new kappa. The selected conditional kappa stays
`781451/250000000`.

## Scope and evidence

Catalogue card `formal-interface-lemma`, scope changed. The card asks for a
formal caller binding. The assigned question is open question 1 of
[PR #7022](https://github.com/CrocSwap/integer-mult-bounds/pull/7022): does
any `c=1` stabilizer element that moves the 216-space preserve the
8-dimensional dihedral isotypic summand and act non-scalarly on it?

The answer is no. The stabilizer has order 3072. Exactly 768 elements
preserve the 216-space, and 2304 move it. None of the movers preserves the
summand. The proof, the named mover `(0 3)(5 6)`, and the hypotheses are in
[PROOF.md](PROOF.md). Source pins are in [SOURCES.json](SOURCES.json). The
selected record and the task catalogue are historical provenance.

Evidence class: exhaustive finite census of a finite set of order 3072, plus
an exact rank computation over `Q` for each mover. The completeness argument
is the decomposition of the hyperoctahedral group into 30 left cosets of the
line-preserving subgroup of order 344064. This is not a heuristic or
incomplete search. It is not an unrestricted nonexistence claim about
operators outside this stabilizer.

The 768 preservers of the 216-space all preserve the summand and act by `±I`,
with 384 elements of each sign. That agrees with the linear-character
prediction in PR #7008 and with the placement, in PR #7022, of the
outside-normalizer preservers among those 768 elements. It is a control on
the membership test. It is not a new normalizer census, and it is not the
answer to the mover question.

PR #7023 already proved that this summand is reducible under `A_1`. This
package rebuilds the projector only to name the subspace. It does not
recompute that characteristic polynomial. The different 8-dimensional joint
space of PR #7019 meets the 216-space only at zero and is not this summand.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-mover-8-summand/verify.py
python3 -B -O research/c1-mover-8-summand/verify.py
python3 -B scripts/research_package.py --package research/c1-mover-8-summand --check-only
```

The marker is `PASS_C1_MOVER_8_SUMMAND`. Acceptance uses explicit checks, so
`-O` does not skip an element or a rejection control.

Not run: Lean, Docker, the degree-881 replay, any characteristic polynomial,
and the selected cold replay. Selected-baseline orientation is source-binding
only.

## Overlap

`scripts/find_overlap.py --refresh` was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10180,
HEAD paths 10178, complete; 339 open PRs, pagination complete, fetched
2026-11-10T10:22:32Z; 7013 discussion records, pagination complete, fetched
2026-11-10T10:23:39Z. The phrases `8-dimensional dihedral`, `moves the 216`,
and `isotypic summand` match PR #7008, PR #7022, and PR #7023, which ask or
narrow this question, and PR #7019, which states that its 8-dimensional joint
space is a different subspace. No open PR reports the action of a mover on
this summand. Closed PRs were searched through local READMEs, task metadata,
and the ledger only. No code diffs.

## Open next questions

See [TASK.json](TASK.json).

- For the named mover `(0 3)(5 6)`, does `g` or `t` act by a scalar on the
  image of the summand? The image misses the `(+1,+1)` space, and this
  package does not test the other three joint signs. This is not the
  basis-transport question of PR #7019, which uses a different 8-dimensional
  space.
- Does any element of the line-preserving group outside the `c=1` stabilizer
  preserve this summand and act non-scalarly? The census stops at sector
  `c=1`.

## Credit

JoyboyBrian recorded the sign-character dimensions. PR #6944 split the
trivial `c=1` character into 216-dimensional blocks. PR #6964 pinned the
basis of one 216-space. PR #7008 computed the dihedral image and the
multiplicity-8 character. PR #7022 enumerated the stabilizer action on the
216-space and left the mover question open. PR #7023 built the basis of the
summand used here and proved reducibility under `A_1`. Ali Romman's PR #4958
and PR #4720 retain the query and the Bell action. Krzysztof Wojt's
`research/exact-one-slot-gram/` supplies the 13 generators. The doubled
representation comes from PR #1719. New work is Apache-2.0.
