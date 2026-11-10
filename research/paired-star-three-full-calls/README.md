# Three or more full calls miss the three-leaf paired star

**No new kappa.** Over F_2, with block size 2 and three paired leaves, a stage
that uses three or more nonzero T-commuting full-call projectors misses the
paired-star pure endpoint. The obstruction is the determinant of the pure
word. It holds for every call order and every finite list of constant thin
maps. Exactly two thin maps of total rank 6 or 7 are included, and none exist
under this call hypothesis. The selected frontier stays
781451/250000000.

The argument, the census counts, and the limits are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed query
demand removes real work. This package changes one hypothesis of the PR #5747
paired-star contract: the number of full calls in a stage. The field stays
F_2, and the thin-map question stays at exactly two maps. It is not a caller,
a native bill, or a change of kappa. Source commits, Git blobs and SHA256 pins
are in [SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance.

`current-priorities.md` at this base still prints the older decimal 0.00310045.
The live selected record is 781451/250000000. This package uses that record
and edits neither file.

The pure comparison is exact in F_2[x]. The machine census is exhaustive on a
finite domain:

- 256 commutant pairs, of which 26 are projectors and 25 are nonzero.
- All 625 ordered pairs of nonzero projectors: 24 meet I + x E, and those 24
  are the complementary resolutions.
- All 15,625 ordered triples: none meet I + x E.
- Every longer list: each nonzero projector has (1 + x)-valuation at least 2,
  so four or more calls have valuation at least 8, against a target valuation
  of 4. That step is a uniform inequality, not a truncated search.

A failed or partial search is not what this record claims. The triple domain
was multiplied in full, and the longer lists are covered by the same checked
valuation.

Overlap was refreshed against open upstream PRs and discussions at
2026-11-10T02:09:51Z (`python3 scripts/find_overlap.py --refresh`). The nearest
records are PR #5747 (the contract and the rank floor), PR #6922 (one thin
map; it leaves three or more full calls open), and the two-call rank-8 census
on fork branch `cursor/paired-star-two-thin-rank-b55f`. The three-FULL sentence
in `research/two-full-central-obstruction` belongs to a different central-word
model.

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-three-full-calls
```

The registered replay runs the verifier twice, once with `-O`. Both print
`PASS_PAIRED_STAR_THREE_FULL_CALLS`. The checks raise, so `-O` does not strip
them. Directly:

```sh
python3 -B research/paired-star-three-full-calls/verify.py
```

## Open next questions

- With one unsplit full call E_j on each stage, do two constant F_2 thin maps
  of total rank 6 or 7 meet the endpoint at g=3, d=2? The determinant allows
  this call count. The first step is to place the three factors I + x_j E_j
  and solve the two-gap equation. Nothing external blocks that calculation.
- Can a stage factor that is not a T-commuting projector have (1 + x)-valuation
  1, so three factors can total the target valuation 4? The first step is one
  explicit triple of 4-by-4 matrices whose product is I + x I_4. Nothing
  external blocks that example; it changes the call shape used here.

Three or more thin maps under the two-call contract, and block entries outside
F_2, stay separate questions. This g=3, d=2 identity does not lift to the
unconstructed profiles g=13, q=8 and g=31, q=26.

## Credit

The paired-star contract, the local form, and the rank floor are from PR #5747
(Ali Romman), including PR #5673, PR #5631, and PR #5617. The two-call census
that left the three-or-more full-call clause open is
`cursor/paired-star-two-thin-rank-b55f` at
`9888af91b9f9e6dc55efd4172858a7d6093d484b`. The one-map census is PR #6922.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Independent
human review and a proof-assistant proof are unclaimed.
