# Irreducible image-basis collections

An irreducible collection of n binary rank-one idempotents with independent
images satisfies `2n <= 3k-1`, where k is the dimension of its nonzero
off-diagonal pattern span and that span contains no matrix unit.

Equality, for `n>1`, forces an even number d of disjoint normal-form triples
and one fresh-factor hub link, with `n=3d+1` and `k=2d+1`. Every such family
is a complete pool and attains equality. In particular, a seven-projector
irreducible collection with seven-dimensional image and pattern dimension
at most five must have the known two-block form.

Read [PROOF.md](PROOF.md) for the proof and source credit,
[RESULT.json](RESULT.json) for exact fixtures and checks, and
[TASK.json](TASK.json) for the task boundary. This answers the
minimum-cardinality case of the open structural question in
[PR #7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281).
The construction of the two blocks and the classification after those blocks
are fixed are prior work. The new step forces the blocks.

With CPython 3.12 and its standard library, from the repository root:

```sh
python3.12 -I -W error -B research/no-edge-image-basis-bound/verify.py
python3.12 -I -W error -B -O research/no-edge-image-basis-bound/verify.py
python3.12 -B scripts/research_package.py --package research/no-edge-image-basis-bound
```

Expected markers:

```text
PASS_NO_EDGE_IMAGE_BASIS_BOUND
PASS_REGISTERED_RESEARCH_PACKAGE
```

The verifier checks all 168 three-dimensional bases, all 26199 nonzero
patterns in nine equality fixtures, exact diagonal sectors and irreducibility.
Direct vector-orbit checks cover the seven-dimensional fixtures. Exhaustive
small idempotent scans check the four-trial lift method. Reducible, matrix-unit
and odd-block controls check the required hypotheses. The all-width proof
uses the complete finite three-coordinate classification lemma.

No new kappa, paid BIT word, native operator or complete invoice is supplied.
The selected frontier and all five assumptions remain unchanged. Larger
pools with dependent images are outside this result. Predecessor scientific
replays, the selected cold replay, Lean and Docker were not run. Independent
human and formal-kernel review are unclaimed.

## Open next questions

Can an irreducible complete pool of pattern dimension five and image dimension
seven lack an irreducible image-basis subcollection? First check the incidence
and common kernels of those subcollections. A proof of existence would extend
the classification; the current theorem does not provide it.

Prepared by Ali Romman with substantial OpenAI Codex assistance. New work is
Apache-2.0. See [CREDITS.md](CREDITS.md) for predecessor sources.
