# Signed permutations outside the {g,t} normalizer on the ++ 216-space

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the trivial sign character of the
`c=1` block splits into four joint spaces of dimension 216 under the
involutions `g` and `t`. PR #7008 proves that the normalizer of `{1,g,t,gt}`
in the `c=1` stabilizer has order 96 and that its image on the `(+1,+1)`
space is the dihedral group of order 12.

The setwise stabilizer of that 216-space is larger. It has order **768**.
Its kernel on the space has order 64, so its image in `GL(E)` still has
order **12** and equals the dihedral image of the normalizer. Inside the
3072-element `c=1` stabilizer, **560** elements lie outside the normalizer,
preserve the 216-space, and act non-scalarly. Each of those actions is one
of the twelve dihedral operators already induced by the normalizer.

One witness is the involution `w` with permutation `(4 7)(5 6)` and a single
minus sign on coordinate 1. It is the PR #7008 involution `u` multiplied by
the coordinate-1 sign. That sign acts by `+I` on the 216-space, so `w` and
`u` induce the same trace-72 operator. The sign does not normalize
`{1,g,t,gt}`, and neither does `w`.

No new kappa. The selected conditional kappa stays `781451/250000000`.
[PROOF.md](PROOF.md) separates the trace identities, the exhaustive census,
and the facts that are not claimed.

## What is certified

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

| object | count |
|---|---:|
| line-preserving signed permutations | 344064 |
| stabilizer of `c=1` | 3072 |
| group `M` cutting out the `(+1,+1)` space | 64 |
| dimension of that space | 216 |
| normalizer of `{1,g,t,gt}` | 96 |
| setwise stabilizer of the space | 768 |
| preservers outside the normalizer | 672 |
| of those, acting non-scalarly | 560 |
| image of either stabilizer in `GL(E)` | 12 |

Every projector correlation on the `c=1` stabilizer is `0` or `216`. The
trace histogram on the 768 preservers is

```text
216: 64,  -216: 64,  72: 192,  -72: 192,  24: 128,  -24: 128
```

## Evidence class

This is an exhaustive finite census of a finite set of order 3072, plus one
constructive witness. The completeness argument is the decomposition of the
hyperoctahedral group into 30 left cosets of the line-preserving subgroup.
It is not a heuristic search, and a failed search was not used as a
nonexistence proof. The non-scalar count is an existence result: 560 explicit
elements, one of which is stored in the verifier. The equality of images is
an order comparison inside that same census. Nothing here changes kappa.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The question answered here is whether any signed permutation in the `c=1`
stabilizer, outside the normalizer of `{g,t}`, preserves the
trivial-character `(+1,+1)` 216-space and acts non-scalarly on it. Open
question 2 of
[PR #7008](https://github.com/CrocSwap/integer-mult-bounds/pull/7008)
asks the analogous question for the 8-dimensional isotypic summand inside
that space. This package does not decide that 8-dimensional question and
does not decide whether the 8-dimensional summand is irreducible under
`A_1`.

Krzysztof Wojt's `research/exact-one-slot-gram/` supplies the 13 generators
and the degree-881 one-slot annihilator. This session does not replay that
annihilator. Selected-baseline orientation returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/c1-216-outside-normalizer/verify.py
python3 -B -O research/c1-216-outside-normalizer/verify.py
python3 -B scripts/research_package.py --package research/c1-216-outside-normalizer --check-only
```

The direct marker is `PASS_C1_216_OUTSIDE_NORMALIZER`. Acceptance uses
explicit checks, so `-O` does not disable them. Rejection controls cover a
coordinate transposition, the incomplete swap of coordinates 4 and 7, a
swapped port label, a projector sum that drops `g`, the normalizer element
`u` of trace 72, and the coordinate-1 sign that preserves the space but acts
by `+I`. No Lean, Docker, degree-881 replay, characteristic polynomial, or
selected cold replay was run. On the measured host the census takes about
35 seconds.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`17469fff78c22941280f04d39dc5a1faee09c840`. Coverage: local notes 10178 of
10178 HEAD paths, complete; 317 open PRs, pagination complete, fetched
2026-11-10T08:49:45Z; 6971 discussion records, pagination complete, fetched
2026-11-10T08:50:46Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only.

The phrases `216-dimensional summand`, `non-scalarly`, and `normalizer of`
match open PR #7008 and its finding
[discussion comment 19507672](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19507672).
That PR computes the normalizer image and leaves the outside-normalizer
question open. The same phrases match the local task notes for the `c=3`
split and the original sign-stabilizer split, which are different blocks.
No open PR body reports this 768-element stabilizer or the witness `w`.
Fork branches `cursor/a1-216-normalizer-split-d47f`,
`cursor/a1-joint-216-charpoly-0702`, and
`cursor/centre-sign-stabilizer-split-20de` are the normalizer split, the
degree-216 polynomial, and the original sign split. This search is not a
novelty certificate.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Does any `c=1` stabilizer element that moves the 216-space preserve the
  8-dimensional dihedral isotypic summand and act non-scalarly on it? Under
  the linear-character identification in PR #7008, every element that
  preserves the 216-space acts through the dihedral image and therefore by a
  scalar on that summand. A non-scalar action would have to move the ambient
  space. The trace on the 4096-dimensional block does not decide it.
- Irreducibility of that 8-dimensional summand under `A_1` remains open.
  This census does not build its basis.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions. PR #6944 split
the trivial `c=1` character into 216-dimensional blocks. PR #7008 computed
the normalizer and the dihedral image of order 12, and left the
outside-normalizer question open. Ali Romman's PR4958 and PR4720 retain the
query and the Bell action. Krzysztof Wojt's `research/exact-one-slot-gram/`
is the degree-881 annihilator and the source of the 13 generators. Nick
Petalas's PR5120 is the degree-410 lower bound. The doubled representation
comes from PR1719. New work is Apache-2.0.
