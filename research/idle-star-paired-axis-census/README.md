# Paired idle-axis transfers do not repair the T740 star profile

**Scoped negative result; no new κ or admitted supplier.** PR #3184 claims a conditional κ of `0.001730189061233850760095…` from redistributing idle rank-48 axes. PR #3187 supplies an exact physical-operator counterexample to its first committed one-stream move. This package checks the most direct symmetry repair: move the same residual axis on both channels of a child pair, so the phase on that pair is scalar, then transfer it to another pair.

## Result

Using the authenticated PR3148 T740 fill (`SHA256 8f4d6965…e00`), we checked all 112 port recipes for owner replica zero. A candidate moves an axis present in both residual children 8 and 10 to both children 12 and 13, or makes the reverse transfer. It must be orthogonal to every original axis of both destination children, including hosted axes, so the move changes child ranks rather than replacing a nonorthogonal destination direction.

The exact eight-stream replay found:

- **2,688** eligible forward transfers; all 2,688 change the physical operator at the moved axis character.
- **2,688** eligible reverse transfers; all 2,688 change the physical operator at the moved axis character. Each of the 112 recipes has 24 candidates in each direction.
- A 147-mode baseline control passes for port 0, and the zero-character identity passes for all ports. The complete fill journal and payload authenticate, and a mutated journal preimage is rejected.

For a concrete witness, port 0 and axis 7 change six entries of the exact Gaussian-integer matrix. For example, entry `(0,0)` changes from `[0,-1]` to `[1,0]`. `RESULT.json` contains the full before/after matrices and per-port counts.

This also rejects every simultaneous nonempty set of transfers **within this restricted class**. Axes eligible in one direction are orthogonal to the complete destination basis; each source residual basis is orthonormal. Thus all selected axes, in both directions, are pairwise orthogonal. At the character equal to any one selected axis, every other moved phase is inactive, leaving the same one-transfer counterexample.

This does not cover matched swaps that remove a nonorthogonal destination axis, longer cycles, other child/time pairs, nonzero replicas, or all operator-preserving assignments. It claims no general obstruction. The selected record and frontier are unchanged.

## Reproduce

From the repository root:

```sh
python3 scripts/research_package.py --package research/idle-star-paired-axis-census --check-only
python3.12 scripts/research_package.py --package research/idle-star-paired-axis-census
```

The verifier independently implements the exact eight-stream Gaussian-integer replay. Live main inputs are pinned in `SOURCES.json`; the retained fill, journal and provider table are checked against the SHA256 and Git-blob IDs recorded from PR3148. The original PR3133 notice and credits are retained under `vendor/`.

## Open next questions

See the structured tasks in [TASK.json](TASK.json). The nearest continuation is to enumerate matched swaps or short cycles in the 48-by-48 cross-Gram graph and test whether they can create net rank imbalance without changing the full stream operator. A different child/time pair needs its own exact insertion-to-insertion intertwiner and source-bound replay.

## Credit

The physical-stream criterion and the first exact PR3184 counterexample are due to Nick Petalas in [PR #3187](https://github.com/CrocSwap/integer-mult-bounds/pull/3187). The T740 fill and 145-row exchange journal are from Jeremy Diviney’s [PR #3148](https://github.com/CrocSwap/integer-mult-bounds/pull/3148); the underlying fill/provider notice and credits are retained unchanged from PR3133 in `vendor/`. The challenged profile claim is Rohan Arun’s [PR #3184](https://github.com/CrocSwap/integer-mult-bounds/pull/3184). Recipe, template, plan and dispatch retain their PR2979/selected-supplier lineage. This package adds an independently written exact replay and an exhaustive, source-bound census of one paired rank-changing transfer family. Prepared by OpenAI Codex with substantial AI assistance; no independent human or proof-assistant review is claimed. New work is Apache-2.0.
