# Three F_2 thin maps meet total rank 6 on the three-leaf paired star

**No new kappa.** Over F_2, with block size 2 and three paired leaves,
there is a word with three thin maps of ranks 2, 2 and 2. The
chronological floor at this size is 6, so that floor is attained once
three maps are allowed. Every two-map word still has total rank at least
8, and the commuting control still meets the endpoint with ranks 4 and 4.
The selected frontier is unchanged.

The word and the multiplication check are in [PROOF.md](PROOF.md).

## Scope and evidence

Original card: `joint-query-controller`. The card asks whether a changed
caller or query demand removes real work. This package answers the
three-or-more-map question left open by the two-map rank-8 census on the
paired-star contract of PR #5747. It is not a caller, a native bill, or a
change of kappa. Source commits, Git blobs and SHA256 pins are in
[SOURCES.json](SOURCES.json). The selected record and catalogue are
historical provenance.

The witness uses exactly two full calls in each stage and constant F_2
entries. Stages 0 and 1 share the resolution with A-bits `0001` and
B-bits `0010`. Stage 2 uses A-bits `0011` and B-bits `0000`, whose A
factor does not commute with the first. The chronological order is
`4, 2, 3, 0, 1, 5`. The three nonzero maps are in gaps 1, 3 and 5, each
of rank 2. Deleting any one misses the endpoint. This is one identity,
not a classification of every schedule.

## Reproduce

Python 3.12. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-three-thin-rank
```

The registered replay runs `verify.py` twice, the second time under
`python3 -O -B`. Both print `PASS_PAIRED_STAR_THREE_THIN_RANK`. The
checks raise, so `-O` does not strip them. No native compiler is required.

## Open next questions

- Does a two-map word of total rank 6 or 7 exist at g=3, d=2 once block
  entries may lie outside F_2? Both the two-map rank-8 census and this
  witness are F_2 statements.
- Can a stage with three or more full calls, together with thin maps,
  meet total thin rank 6 or 7? Open PR #6956 claims that three or more
  nonzero T-commuting projectors already fail the pure determinant. This
  package does not review that claim and uses exactly two full calls per
  stage.
- Do the unconstructed profiles g=13, q=8 with five rank-8 maps, and
  g=31, q=26 with five rank-q maps, exist when full projectors need not
  commute? This g=3 word does not lift. Commuting projectors remain
  impossible for those map counts.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including the predecessor statements in
PR #5673, PR #5631, and PR #5617. The one-map obstruction is open PR
#6922. The two-map rank-8 bound is open PR #6940. The rank-8 control is
the construction in `research/coupled31-chronology/COMMUTING.md`,
specialized to g=3 and q=1. Prepared by unpaidmoon with substantial
Cursor Grok assistance. Independent human review and a proof-assistant
proof are unclaimed.
