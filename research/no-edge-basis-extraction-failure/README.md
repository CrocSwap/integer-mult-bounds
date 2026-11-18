# A complete pool can require more than an image basis

For every `n>=3`, this package gives a complete binary projector pool with
`n+1` members, joint-image dimension n and irreducible action. Its pattern
space has dimension `n+1`, minimum nonzero weight six and no matrix unit.
Both of its image-basis subcollections are reducible. The construction uses
width `3n` and permits zero padding.

Thus irreducibility of a complete pool does not imply the existence of an
irreducible image-basis subcollection. The excess of one projector is the
least possible for this failure. The proof includes a three-copy embedding
that preserves the exact complete pool of any binary matrix subspace.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), and
[TASK.json](TASK.json). The result marks a boundary of the image-basis theorem
in [PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686).
At image dimension seven, the new pattern dimension is eight. This does not
settle basis extraction at pattern dimension five.

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/no-edge-basis-extraction-failure/verify.py
python3.12 -I -W error -B -O research/no-edge-basis-extraction-failure/verify.py
python3.12 -B scripts/research_package.py --package research/no-edge-basis-extraction-failure
```

Expected markers:

```text
PASS_NO_EDGE_BASIS_EXTRACTION_FAILURE
PASS_REGISTERED_RESEARCH_PACKAGE
```

The verifier checks all 16358 nonzero patterns and all 16368 subsets for ten
family instances, `3<=n<=12`. Exact rank, incidence and invariant-subspace
witnesses pass. Direct orbit checks cover `3<=n<=8`. All 67 subspaces of
`M_2(F2)` check the exact replication lemma, and all 256 matrix pairs check
the algebra law. Even-copy and single-copy controls reject invalid variants.

No new kappa, paid BIT word, native operation or full invoice is supplied.
The selected frontier and all five assumptions remain unchanged. Predecessor
scientific replays, the selected cold replay, Lean and Docker were not run.
Independent human and formal-kernel review are unclaimed.

## Open next questions

Does pattern dimension five force basis extraction for an irreducible
seven-dimensional image? The counterexample has larger pattern dimension.
A proof must use the extra restriction instead of the false general premise.

Prepared by Ali Romman with substantial OpenAI Codex assistance. New work is
Apache-2.0. See [CREDITS.md](CREDITS.md) for source credit.
