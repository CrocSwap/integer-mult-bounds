# Sharp joint-choice bound: the ten rank-six patterns cover at most 99 diagonals

PR1347 supplies ten rank-six atoms with copy bill 60 meeting each P112 orthogonal frame at least eight times, but its chosen supports leave 21 diagonals uncovered. It explicitly warns that retaining one support representative per frame-hit pattern may lose useful diagonal coverage. This package resolves that question for its **ten published term patterns**: allowing any cost-seven C/N root-star parent, arbitrary joint support trims of cost at most six, and extra frame hits, **at most 99 of 112 diagonals can be covered**. At least 13 remain impossible.

The additional result is the **joint-choice optimum of 99**, not priority for the representative census or its union bound. Concurrent [PR1402](https://github.com/CrocSwap/integer-mult-bounds/pull/1402), inspected at head `e5917254b781e9f327436ac682baab1c93941aed`, independently gives the same four tagged maximal representatives per original pattern, two distinct diagonal supports, and their 102-diagonal union. Our complete multiple-choice calculation shows that selecting one representative for each of the ten terms necessarily loses at least three more diagonals: 13 are missing simultaneously, although only ten are absent from the union of every alternative. An explicit support choice attaining 99 is in CERTIFICATE.json. This is a support obstruction, not a coefficient decoder or supplier.

The independently written scan reconstructs all 1260 frames, all 57600 tagged parent pairs, 7616 cost-seven parents and 967232 maximal one-axis rank-six slices. No retained representative has a strict superset of an original pattern's frame hits. All 903 distinct final union states of the ten binary choices are tested. The domain changes PR1347's representative choice, not its general frame-capacity theorem. Ten terms with different frame patterns, mixed ranks, other parents or punctures remain outside this result.

## Proof

Let a parent pairing matrix M have F2-rank 7. Factor M=XY with X of column rank 7 and Y of row rank 7. If restricting rows and columns gives rank at most 6, at least one restricted factor loses rank: left and right inverses would otherwise certify rank 7 for the product. When rows lose rank, their X-vectors lie in the kernel of a nonzero functional. The corresponding nonzero word in the full parent column code vanishes on all retained rows. Expanding the rows to its whole zero set and restoring all columns therefore dominates the joint trim. The other case is the transpose. All 127 nonzero codewords are enumerated for every parent; every maximal slice has rank 6 in this geometry. The argument includes arbitrary joint restrictions of cost below six.

Expansion only adds frame hits and diagonal support. A replacement for term k must hit all frames hit by original term k, but may hit more. The scan retains every maximal slice satisfying that inclusion. Transposition preserves frame hits and the diagonal intersection, so column-side cuts add no diagonal choices. Exact candidate enumeration and dynamic union enumeration prove the maximum 99. A missing diagonal cannot be repaired by coefficients: all rank-one contributions there are zero while the target diagonal is 4. Cost-zero odd rectangles also have zero diagonal entries.

The theorem retains a **per-term** frame-hit requirement. Letting one term lose hits while another repays them is outside it. No complete invoice is supplied: every other physical charge is optimistically zero for this necessary test, and no new kappa, native, all-size or supplier result is claimed.

## Reproduce

Python 3.12+, standard library, from the repository root:

```
python -I -B research/p112-rank6-cover-representatives/scan.py
python -I -O -B research/p112-rank6-cover-representatives/scan.py
python scripts/research_package.py --package research/p112-rank6-cover-representatives
```

Expected: `PASS_RANK6_REPRESENTATIVES ... max_diagonals=99 unavoidable_missing=13`.
Every replay compares the complete generated receipt. Controls reject the original false diagonal-coverage inference, the repaired-all-diagonals inference and an untrimmed parent priced at six. The best tuple is a positive rank-six support control. `--write` regenerates the receipt.

## Open next questions

Can ten rank-six terms cover every diagonal and every frame demand when frame hits may transfer between terms? Start by letting one original term lose hits and requiring the other nine to repay those deficits. Even a favorable support witness would still require exact complex coefficients and a complete physical invoice. Representative substitution alone cannot be the repair.

## Sources and credit

The cover and root order are copied byte-for-byte from Cinna Davis (@1337isnot1337), PR1347 at 64fd5f9e91961dedc16118fcc7ad71ee82efe28f; DEPENDENCY.json records paths, Git blobs and SHA256. Apache-2.0. Its source lineage retains Navinor PR1226, David Arias PR1236, Hanson Sun PR1242, Cinna Davis PR1323, DreamingOfClouds PR717 and themilkman216 PR968. PR1402's concurrent complete representative census and union obstruction are credited above; it was identified during the final overlap refresh after this independent computation. No PR1402 executable or certificate is imported. This package adds the sharp one-choice-per-term optimum and the written domination proof for arbitrary joint restrictions of rank at most six. New scan and proof prepared for woklerx with substantial OpenAI Codex assistance; no independent human review claimed.
