# The c=1 ++ 216-space is reducible under A_1

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, the trivial sign character of the
`c=1` block has dimension 864 and splits into four joint eigenspaces of
dimension 216 under the involutions `g` and `t` from PR #6944. The
centralizer of `{g,t}` in the signed-permutation stabilizer of `c=1` has
order 16, and every one of those elements acts by `±I` on each 216-space.
That exhaustive count does not prove irreducibility.

The normalizer is larger. Its image on the trivial-character `(+1,+1)` space
is the dihedral group of order 12, with rational isotypic dimensions
**8**, **80**, and **128**. Those subspaces are invariant under `A_1`. The
216-dimensional summand is reducible. An explicit involution `u=(4 7)(5 6)`
already cuts it, and the other three 216-spaces, as 72+144.

No new kappa. The selected conditional kappa stays `781451/250000000`.
[PROOF.md](PROOF.md) records the operators, the census, and the character
inner products.

## What is certified

The live input is the query pinned in [SOURCES.json](SOURCES.json), SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.

| object | order or dimension |
|---|---:|
| line-preserving signed permutations | 344064 |
| index in the hyperoctahedral group | 30 |
| stabilizer of `c=1` | 3072 |
| centralizer of `{g,t}` | 16, all traces `±216` |
| normalizer of `{g,t}` | 96 |
| image on the `(+1,+1)` space | dihedral of order 12 |
| rational isotypic dimensions | 8, 80, 128 |

The same census shows that each of the other three joint spaces has a
rational `A_1`-invariant subspace of dimension 72. Only the `(+1,+1)` space
carries the full dihedral image, and only that space is given the
8-dimensional summand.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live question, left open by
[PR #6944](https://github.com/CrocSwap/integer-mult-bounds/pull/6944)
and by
[discussion comment 19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258),
is whether one 216-dimensional summand is irreducible under `A_1`.

This package answers that question for the trivial-character `(+1,+1)`
summand: it is reducible. The characteristic polynomial of the 216-space is
not computed. The absence of a third involution in the centralizer is
certified by a complete count, and that count is not used as an
irreducibility proof.

Krzysztof Wojt's `research/exact-one-slot-gram/` supplies the 13 generators
whose closure is proved here to be the full line-preserving signed-permutation
group, and it supplies the degree-881 one-slot annihilator. This session does
not replay that annihilator. Selected-baseline orientation returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` for kappa `781451/250000000`.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/centre-216-normalizer-split/verify.py
python3 -B -O research/centre-216-normalizer-split/verify.py
python3 -B scripts/research_package.py --package research/centre-216-normalizer-split --check-only
```

The direct marker is `PASS_CENTRE_216_NORMALIZER_SPLIT`. Acceptance uses
explicit checks, so `-O` does not disable them. Rejection controls cover a
coordinate transposition, the incomplete swap of coordinates 4 and 7, a
swapped port label, and a sign symmetry that does not commute with `g`.
No Lean, Docker, degree-881 replay, characteristic polynomial, or selected
cold replay was run.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-10 against upstream
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Coverage: local notes 8917 of
8917 HEAD paths, complete; 895 open PRs, pagination complete, fetched
2026-11-10T02:25:52Z; 6934 discussion records, pagination complete, fetched
2026-11-10T02:27:02Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only.

The phrase `216-dimensional` matches open PR #6944, whose head
`26ceb7a0b4e04d4377a31aaa849dcb13e06e4cbc` is the sign-character split into
216-dimensional blocks. That PR leaves irreducibility of one summand open
and does not compute this normalizer action. A search for `irreducible under`
also hits #6944 and unrelated normalizer or joint-eigenspace notes on other
operators.

The fork branch `cursor/a1-joint-216-charpoly-0702` at
`306f791048636c7dc91c83ecb8ae6e730908042c` computes the characteristic
polynomial of this same 216-space and records that `x` and `x-2` both divide
it. That shows reducibility without exhibiting a subspace or searching a
centralizer. This package does not read those coefficients, does not rebuild
that matrix, and does not identify the 8-dimensional symmetry summand with a
factor of that polynomial. The 8-dimensional joint eigenspace inside the
32-dimensional sign character, left open there, is a different space.
No code diffs of upstream PRs were searched.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- Whether the 8-dimensional isotypic summand is irreducible under `A_1`.
  The character inner product gives its dimension and does not list a basis.
  A missing further involution would not decide the question. The
  characteristic polynomial of the parent 216-space was not computed here.
- Whether a signed permutation in the `c=1` stabilizer, outside the
  normalizer of `{g,t}`, preserves that 8-dimensional summand and acts
  non-scalarly. The centralizer census does not answer this.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions and the open
432-coordinate question. PR #6944 split the trivial `c=1` character into
216-dimensional joint spaces and left irreducibility open. Ali Romman's
PR4958 and PR4720 retain the query and the Bell action. Krzysztof Wojt's
`research/exact-one-slot-gram/` is the degree-881 annihilator and the source
of the 13 signed-permutation generators. Nick Petalas's PR5120 is the
degree-410 lower bound. The doubled representation comes from PR1719.
New work is Apache-2.0.
