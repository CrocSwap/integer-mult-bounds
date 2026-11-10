# Two F_2 thin maps need total rank 8 on the three-leaf paired star

**No new kappa.** Over F_2, with block size 2 and three paired leaves, one
thin map does not meet the paired-star endpoint, and every two-map word
has total thin rank at least 8. The commuting control still meets the
endpoint with ranks 4 and 4, so the bound is sharp for this contract. The
chronological floor at this size is 6. The selected frontier is unchanged.

The statement, the specialization argument, and the limits are in
[PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
caller or query demand removes real work. This package answers the
two-map rank question left open by the one-thin census on the paired-star
contract of PR #5747. It is not a caller, a native bill, or a change of
kappa. Source commits, Git blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance.

The census screens all 12 orthogonal resolutions and all 720 orders
(1,244,160 words), including the 96 ordered resolution pairs whose A
factors do not commute. It specializes at two GF(256) points. Any legal
constant solution would lie in the affine spaces that were searched. The
branch-and-bound prunes only branches whose already-fixed rows have rank
sum at least 8, so a rank sum of 6 or 7 cannot be skipped. The polynomial
control is separate from that search: deleting one thin map, or moving it
into the other odd gap, misses the endpoint.

## Reproduce

Python 3.12 and gcc with OpenMP. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-two-thin-rank
```

The registered replay is split into stage-0 resolutions 0..5 and 6..11 so
each command stays inside the package runner's time cap. Both halves are
required. Each prints `PASS_PAIRED_STAR_TWO_THIN_RANK`. Together they
screen 1244160 orders, with 159984 pure hits, 568752 consistent gap
pairs, `min_rank_sum` 8, and `one_agree` 0. The second command uses
`python3 -O -B`; the checks raise, so `-O` does not strip them.

## Open next questions

- Can three or more thin maps meet total rank 6 or 7 on this same g=3,
  d=2, F_2 contract? The two-map bound is now 8, and the chronological
  floor is still 6, so a three-map word is the remaining way to test that
  floor at this size.
- Does a two-map word of total rank 6 or 7 appear once block entries may
  lie outside F_2, or once a stage may use three or more full calls?
  Either would pass this census without reaching g=13.
- Do the unconstructed profiles g=13, q=8 (five rank-8 maps) and g=31,
  q=26 (five rank-q maps) exist with noncommuting projectors? This g=3
  result does not lift. Commuting projectors remain impossible for those
  map counts.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including the predecessor statements in
PR #5673, PR #5631, and PR #5617. The two-map control is the construction
in `research/coupled31-chronology/COMMUTING.md`, specialized to g=3 and
q=1. The one-map field screen was first recorded in the open census
PR #6922 and is re-checked here. Prepared by unpaidmoon with substantial
Cursor Grok assistance. Independent human review and a proof-assistant
proof are unclaimed.
