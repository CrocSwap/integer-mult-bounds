# All extremal irreducible edge pools have one form

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

Let a binary noncoordinate rank-one-idempotent collection have pattern
dimension `k>=2` and irreducible joint-image dimension `2k-1`.
It must be the complete pool. Its pattern space contains exactly
`k-1` disjoint matrix-unit edges. The pool consists of their two lifts
each, plus one link with fixed old-coordinate factors and arbitrary
fresh factors a,b with `a dot b=1`.

Every such family works. Each restricted action is isomorphic to the
first `2k-2` coordinate projectors plus the all-one matrix of size
`2k-1`. This parameterization is not a count of coordinate-permutation
orbits, and the basis change is not declared physically free.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [CREDITS.md](CREDITS.md)
and [TASK.json](TASK.json). The proof uses the all-width matching bound
in [PR #7692](https://github.com/CrocSwap/integer-mult-bounds/pull/7692).
It extends the prior k=3 two-edge restricted normal form in
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782).
That special case remains prior work.

## Reproduce

Use CPython 3.12 and its standard library, from the repository root.

```sh
python3.12 -I -W error -B research/edge-extremal-pool-classification/verify.py
python3.12 -I -W error -B -O research/edge-extremal-pool-classification/verify.py
python3.12 -B scripts/research_package.py --package research/edge-extremal-pool-classification
```

Expected markers are `PASS_EDGE_EXTREMAL_POOL_CLASSIFICATION` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier writes no file and
compares its complete result with the committed receipt.

It checks all 2825 pattern spaces at width three, all 4164 directed
unit graphs at widths two through four, and 30702 complete link spaces
across seven stated domains. Their 49 irreducible survivors have the
claimed form; all negatives have checked invariant certificates.
The tests include 352 pools with extra members and 24 wider forms
through width 19. A separate all-vector test checks the small
irreducibility algorithm and every positive link-domain survivor.

## Limits

The matching theorem is a pinned mathematical dependency. The finite
census does not cover every ambient embedding. Forced completeness
fails at k=1; that boundary and the irreducibility premise have explicit
negative controls. No paid BIT word, native implementation, complete
invoice or new kappa is supplied. The selected frontier and its five
assumptions remain unchanged. Independent human and formal-kernel
review are unclaimed. Full predecessor package replays, selected cold
replay, Lean and Docker are not included.

## Open next questions

Can the unique extremal action support a legal paid word with target
rank above paid rank at larger k? First compare the five-core word
obstruction in [PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782).
Specify the alphabet, relation lattice, endpoint coordinates, counted
roles and native interface. A scalar normal form does not supply these.
