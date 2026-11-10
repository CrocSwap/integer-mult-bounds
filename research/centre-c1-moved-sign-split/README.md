# Moved c=1 sign characters

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the residual signed-permutation stabilizer of sector `c = 1` has order **3072**. On each sign character moved by the predecessor involutions `g` and `t`, that finite group splits the character. The finest splits certified here come from one explicit order-4 permutation: complex dimensions `144 + 84 + 120 + 84` on each 432-dimensional character, `48 + 48 + 48 + 48` on each 192-dimensional character, and `32 + 12 + 24 + 12` on each 80-dimensional character.

This is an exhaustive finite census with exact intertwining identities. It does not change the selected conditional kappa `781451/250000000`. [PROOF.md](PROOF.md) records the stabilizer, the eigenvalue tables, and the centralizer obstruction.

## What is certified

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

`g = (1 2)(5 6)` with signs on coordinates 4 and 7, and `t = (1 5)(2 6)` with signs on coordinates 3 and 7, preserve exactly the trivial character and the unique 32-dimensional character of `c = 1`. The moved characters are four of dimension 432, six of dimension 192, and four of dimension 80. The same pair still sends sector 3 to 343 under `g`, so it is not used on the `c = 3` block.

Inside the order-3072 stabilizer, the preserving elements of one character of each moved dimension were enumerated. Their orders are 1, 2, 3, 4, and 6, and the eigenvalue multiplicities are the tables in [PROOF.md](PROOF.md). Involution traces give the real splits `264 + 168`, `96 + 96`, `120 + 72`, and `56 + 24`. The order-4 permutation `s = (0 4 3 7)(5 6)`, with all signs `+1`, realizes the finer complex splits above, and conjugation inside the stabilizer carries those splits onto every moved character of the same dimension.

On each character preserved by `s`, the 64 residual permutations that preserve the character and commute with `s` act by scalar fourth roots of unity on every complex eigenspace of `s`. That is a scoped obstruction for this centralizer. It is not an irreducibility theorem for a non-commuting element.

PR #6944 already splits the two characters `g` and `t` preserve, including the four 216-dimensional summands of the trivial character. This package starts from the characters those involutions move.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal caller binding. The open clause in [discussion comment 19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258), restricted to the `c = 1` characters that `g` and `t` move, asks which residual signed permutations split those characters. The answer is the census above.

Krzysztof Wojt's `research/exact-one-slot-gram/` remains the degree-881 one-slot certificate. These subspaces do not replace it. Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/centre-c1-moved-sign-split/verify.py
python3 -I -B -O -W error research/centre-c1-moved-sign-split/verify.py
python3 -B scripts/research_package.py --package research/centre-c1-moved-sign-split --check-only
```

The direct marker is `PASS_C1_MOVED_SIGN_SPLIT`. Acceptance uses explicit checks, so `-O` does not disable them. Rejection controls cover a coordinate transposition, a swapped port label, a truncated sign stabilizer, and the 224 sign patterns on `s` that lie outside the stabilizer. No Lean, Docker, degree-881 replay, or selected cold replay was run. Both direct modes passed on CPython 3.12.3.

## Overlap

`scripts/find_overlap.py --refresh` was run on 2026-11-10 against upstream `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Coverage: local notes 8919 of 8917 HEAD paths, complete; 895 open PRs, pagination complete, fetched 2026-11-10T02:30:38Z; 6941 discussion records, pagination complete, fetched 2026-11-10T02:31:38Z.

The phrases `432-coordinate` and `sign stabilizer` match the source handoff, discussion comment 19492873, and open PR #6944. That PR certifies the preserved-character split. The phrases for this moved-character question match no other open PR. Closed PRs were searched through local READMEs, task metadata, and the ledger only. No code diffs were searched.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Can one element of the `c = 1` stabilizer that preserves a moved 192-character, and does not commute with `s`, meet a 48-dimensional eigenspace of `s` in a smaller `A_1`-invariant subspace? The centralizer acts by scalars, so any finer split has to come from outside it. The trace formula does not list a basis.
- What is the characteristic polynomial of one of those 48-dimensional eigenspaces? It would place this split inside the known degree-881 polynomial. Building one exact basis is the missing step. This is separate from the 216-dimensional block in PR #6944.
- Which residual signed permutations split the `c = 3` characters? `g` sends sector 3 to 343, so the stabilizer certified here does not act on that block.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions and the open decomposition question. The preserved-character split and the operators `g` and `t` are the census behind discussion comment 19492873 and PR #6944, by unpaidmoon. Ali Romman's PR4958 and PR4720 retain the query and the Bell action. Nick Petalas's PR5120 is the degree-410 lower bound. Krzysztof Wojt's PR5168 is the degree-881 one-slot annihilator. The doubled representation comes from PR1719. New work is Apache-2.0.
