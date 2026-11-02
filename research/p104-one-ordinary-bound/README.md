# One ordinary-work bound for the PR6353 supplier

**Audit; no new κ.** Selected kappa stays `781451/250000000`.

## Scope and evidence

Original card: `joint-query-controller`. The scope is **changed**. The card
asks whether a new query demand removes work. This package does not change
the caller or the supplier. It checks one source-specific funding inequality
left after the stage-1 LOCAL contact.

The stage-1 contact on all 104 ports is already recorded on fork branch
`cursor/p104-6353-stage1-local-contact-7c18`. [PR #6359](https://github.com/CrocSwap/integer-mult-bounds/pull/6359)
already recounts the recursive paid and productive invoice and leaves ordinary
funding open. [PR #6360](https://github.com/CrocSwap/integer-mult-bounds/pull/6360)
and [PR #6361](https://github.com/CrocSwap/integer-mult-bounds/pull/6361) cover
width-one frame-1094 matrices and the formal Laurent endpoint. The handoff is
[discussion 1166, comment 19344846](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19344846).

The supplier word is the PR6353 file at `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`,
vendored at `sources/pr6353-WORD.json.gz`. Its SHA256 is
`0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928`.
A session regeneration of that commit's constructor, on the pinned source
word, reproduced those payload bytes. The registered replay hashes the
vendored file and does not rerun the constructor.

Two charge walks agree. Relative to the pinned source word, the local paid
histogram changes by `14 H1 - 4 H2 - 3 H3 + 4 H4 - 5 H5`, and the productive
histogram changes by `H5 + 8 H8 - 9 H9`. The scalar allowance moves from
127088 to 128694. Paid calls move from 3450 to 3456. Nine extra owned
openings, one each on labels 770 through 778, move the lifetime count from
32 to 41. Peak storage stays 13.

The declared local route allowance is then 5368000. Added to the scalar
allowance, the local ordinary total is **5496694, strictly below 10^7**.
The declared complete raw expression, evaluated at the pinned caller’s 353
events, is **194902768, strictly below 10^9**. Substituting the supplier
program length 17657 produces 256089712, a different number that is still
below 10^9. The published raw figure is the caller-sized expression.

Details, the formula and the limits are in [PROOF.md](PROOF.md).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/p104-one-ordinary-bound --check-only
python3 -B scripts/research_package.py --package research/p104-one-ordinary-bound
```

A direct run also accepts `-O`. The checks raise `ValueError`.

```sh
python3 -B research/p104-one-ordinary-bound/verify.py
```

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. Check the compiler threshold and the 54 outer predicates at the same
   PR6353 head. This ordinary-work slack does not discharge them.
2. Bind LOCAL stages 2 through 19. Stage 1 is already on the fork branch
   named above, and one stage does not transfer.

## Credit

The supplier word, the ordinary-work formula and the nine output contractions
are Ali Romman’s, with the retained Cinna Davis / P104 native-channel lineage,
DreamingOfClouds for the PR6349 ports, and the PR6348 caller. The recursive
invoice recount is ToikY, PR6359. The stage-1 contact recount is the parallel
fork branch above. New charge walk and funding check: unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0.
