# The seven separated A2 sites transfer to the frozen PR3945 words

**Negative for the paid profile. No new κ.** The selected record is not edited.

On both frozen PR3945 words, the seven separated A2 sites occur at the published indices, and contracting them removes seven forward ADDs and five cleanup ADDs without changing the recursive frame histogram.

## Scope and evidence

Chooser seed `05f92898273de33149bc662a2b87104d` drew `scalar-to-moment`. The consecutive A1858 climb is a separate package. This note answers the other open question of [PR #4019](https://github.com/CrocSwap/integer-mult-bounds/pull/4019): the seven separated sites were certified only on the older PR3734 providers, and no PR3945 applicability was claimed.

The seven index triples and their removed positions are that witness:

| Section | Indices | Removed position |
|---|---|---|
| B | 4, 53, 54 | 0 |
| B | 7, 49, 50 | 0 |
| restore | 20, 21, 36 | 2 |
| restore | 22, 23, 38 | 2 |
| restore | 26, 27, 51 | 2 |
| restore | 30, 31, 62 | 2 |
| restore | 32, 33, 73 | 2 |

On each of the four frozen words, every triple lies inside one warp segment, the three ADDs share a frame, every intervening event misses their three registers, and deleting the published position and reversing the other two preserves the rational map. The B warp cuts are remapped after the two deleted B gates. Cleanup is rederived.

Both PR3734 words keep `{1:2440,2:725,3:224,4:102,5:20,8:8}`. Both PR3945 words keep `{1:2482,2:712,3:218,4:109,5:20,8:8}`. Each word loses exactly two B ADDs, five restore ADDs and five cleanup ADDs. Forgetting the warp remap fails frame containment. Removing a different gate of the same triple fails the rational map.

The PR3734 half reproduces the published seven-forward / five-cleanup saving. The new statement is the same saving, and the same absence of a histogram change, on the two PR3945 words. No predecessor verifier is imported.

## What this does not establish

No paid frame transition is removed. Native operators, owners, precision, stock and tape are not priced. This is not a search for further separated sites. The selected record stays the pinned `certificates/selected-result.json` (κ = `60403/20000000`); `make frontier4470-verify` was not run.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/separated-a2-pr3945-transfer/verify.py
python3.12 -B scripts/research_package.py --package research/separated-a2-pr3945-transfer
```

Expected first line: `PASS_SEPARATED_A2_PR3945_TRANSFER words=4 sites=7 forward_add_delta=-7 cleanup_add_delta=-5 histograms=unchanged`.

Input pins are in [SOURCES.json](SOURCES.json). Base commit `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`.

## Open next questions

Can a different graph remove a positive-dimension climb, rather than another scalar ADD? These seven sites, like the consecutive A1858 block, leave every rank count unchanged. Name one boundary whose frame dimension actually drops, and price that edited word, before another separated scan. No such boundary is identified here.

## Credit

ToikY, PR #4019, published the seven sites, the disjointness argument and the PR3734 saving, and left later-word applicability open. Chris R / Clear1nsight, PR #3998, supplied the A2 identity those sites extend. Dataisfire's PR3734 words and Dugongue's PR3945 words are the frozen inputs, as vendored by PR #4152. The frame contract follows the BORROW-WORD reading used by Arham Tahir's coupled-carrier audit. Riquelme Soares (@hevlyo), with substantial AI assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
