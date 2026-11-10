# Sign-stabilizer splitting of the doubled centre block

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

For the historical 8-by-112 centre query, two explicit commuting coordinate
involutions split the largest sign-character space of the `c=1` block into
four `A_1`-invariant subspaces of dimension **216**. The same pair splits the
unique 32-dimensional character of that block into four subspaces of
dimension **8**, and splits four characters of the `c=128` block, each of
dimension 512, into summands **224 + 96 + 96 + 96**.

This is a finite exact symmetry certificate. It does not change the selected
conditional kappa `781451/250000000`. [PROOF.md](PROOF.md) records the
operators, the trace formula and the invariant subspaces.

## What is certified

The live input is the actual query pinned in [SOURCES.json](SOURCES.json),
SHA256 `5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
`verify.py` rebuilds the columns and the sign stabilizer from that file.

| sector | sign stabilizer | character dimensions |
|---|---:|---|
| `c=1` | order 16 | `{864: 1, 432: 4, 192: 6, 80: 4, 32: 1}` |
| `c=3` | order 16 | the same histogram |
| `c=128` | order 8 | eight characters of dimension 512 |

The involutions are `g = (1 2)(5 6)` with signs on coordinates 4 and 7, and
`t = (1 5)(2 6)` with signs on coordinates 3 and 7. Both square to the
identity and commute. Both preserve sectors 1 and 128. `t` preserves sector
3, and `g` sends sector 3 to 343.

On `c=1`, both involutions preserve exactly two characters: the trivial
character, of dimension 864, and the unique character of dimension 32. Their
joint `(±1, ±1)` dimensions are `216^4` and `8^4`. On `c=128`, both
involutions preserve exactly four characters, including the trivial
character, and each splits as `224+96+96+96`. The trivial `(+1,+1)` summand
has dimension 224. These subspaces are invariant under the corresponding
block because the involutions commute with it.

The four dimension-432 characters of `c=1` are separate character spaces.
The two 432-coordinate graph components reported in the source handoff sit
in the dimension-864 space and were described there as basis-dependent. This
package certifies the 216-dimensional joint eigenspaces of that 864-space.
It does not reconstruct the graph.

## Scope

Catalogue card `formal-interface-lemma` asks for a formal interface binding.
The live handoff
[discussion comment 19144258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258)
asks whether the residual coordinate-permutation stabilizer of `c=1` splits
the 432-coordinate components of its largest sign-character space, with exact
intertwining, before any full upper polynomial. This package answers the
intertwining part for the preserved characters of `c=1` and `c=128`.

Krzysztof Wojt's `research/exact-one-slot-gram/` already proves that the
full one-slot minimal polynomial has degree 881, using payload involutions
`X_c` and `Z_{c+e}` and four 1024-dimensional sectors. Nick Petalas's
`research/uniform-centre-gram-annihilator/` gives a coarse annihilator of
degree at most `2^93` at every positive width. Those certificates are cited
context. This session does not replay them. The coordinate involutions here
are a different symmetry, and a 216-dimensional invariant subspace does not
replace either annihilator.

Selected-baseline orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
for kappa `781451/250000000`. That check binds the selected record only.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -B -W error research/centre-sign-stabilizer-split/verify.py
python3 -B -O research/centre-sign-stabilizer-split/verify.py
python3 -B scripts/research_package.py --package research/centre-sign-stabilizer-split --check-only
```

The direct marker is `PASS_CENTRE_SIGN_STABILIZER_SPLIT`. Acceptance uses
explicit checks, so `-O` does not disable them. Rejection controls cover a
coordinate transposition, a swapped port label, a sign element that does not
commute with `g`, and a truncated stabilizer average. No Lean, Docker,
degree-881 replay or selected cold replay was run.

## Overlap

`scripts/find_overlap.py` was run on 2026-11-09 against upstream
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Coverage: local notes 8919 of
8917 HEAD paths, complete; 882 open PRs, pagination complete, fetched
2026-11-09T13:40:32Z; 6926 discussion records, pagination complete, fetched
2026-11-09T13:41:35Z. Closed PRs were searched through local READMEs, task
metadata and the ledger only.

The phrases `432-coordinate` and `largest character space` match the source
handoff and no open PR. `sign stabilizer` also matches one unrelated
mixed-sign count on a different operator (discussion comment 19146049).
Packages on the same Gram are `research/centre-gram-degree410/`,
`research/exact-one-slot-gram/`, `research/uniform-centre-gram-annihilator/`
and `research/equal-bell-two-slot-spectrum/`. Their claims are the degree-410
lower bound, the degree-881 one-slot polynomial, a uniform coarse annihilator,
and the equal-label two-slot spectrum. None records this character splitting.
S3 sign-character packages are a different representation. No code diffs or
unpublished work were searched.

## Open next questions

The structured list is in [TASK.json](TASK.json).

- The characters of `c=1` and `c=128` that these two involutions move, and
  every character of `c=3`, still need a residual decomposition. A pair that
  preserves `c=3` is the first missing ingredient.
- The characteristic polynomial of one 216-dimensional block would say how
  this split sits inside the known degree-881 polynomial. Building an exact
  basis of that block is the missing step.
- Whether the 216-spaces are irreducible for `A_1` is open. The trace formula
  gives dimensions, not a proof that no finer symmetry exists inside one
  summand.

## Credit

JoyboyBrian's handoff recorded the sign-character dimensions and the open
432-coordinate question. Ali Romman's PR4958 and PR4720 retain the query and
the Bell action. Nick Petalas's PR5120 is the degree-410 lower bound.
Krzysztof Wojt's exact one-slot package is the degree-881 annihilator.
The doubled representation comes from PR1719, with the predecessor notice
left unchanged in `research/centre-polynomial-cache-limits/NOTICE.md`.
New work is Apache-2.0.
