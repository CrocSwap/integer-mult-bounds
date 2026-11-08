# One thin map misses the three-leaf F_2 paired star

**No new kappa.** Over F_2, with block size 2 and three paired leaves, one
thin map does not meet the paired-star endpoint. Every legal orthogonal
resolution is included: nonzero off-diagonal blocks and noncommuting stage
projectors, and every order of the six full calls. Two thin maps of ranks
4 and 4 still meet the endpoint. The selected frontier is unchanged.

This is the smallest paired test of the escape left open by
[PR #5747](https://github.com/CrocSwap/integer-mult-bounds/pull/5747).
Commuting full projectors already need at least `ceil(g / 2)` thin maps.
At g=3 that count is 2, and the rank floor is 6, so one map of rank at
least 6 was not already ruled out. The census closes that F_2 case only.
The g=13, q=8 and g=31, q=26 five-map profiles stay open.

The statement, the gate identity, and the limits are in [PROOF.md](PROOF.md).

## Reproduce

Python 3.12 and numpy 1.26.4. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/paired-star-one-thin-gap
```

Expected status: `PASS_PAIRED_STAR_ONE_THIN_GAP`, with
`screened_orders` equal to 1244160 and `one_thin_witness` null.
The same command under `python3 -O -B` is registered and must pass; the
checks raise, so they are not stripped by `-O`.

The run specializes every word at two points of GF(256). A constant
candidate would be replayed in the polynomial ring. The two-map commuting
word is an exact positive control, and deleting one of its thin maps
misses the endpoint. A separate formula lock compares the field arithmetic
with the polynomial word at every gap of one noncommuting order.

## Open next questions

- Can two thin maps meet total rank 6 or 7 at this same g=3, d=2, F_2
  contract? The control uses total rank 8, and the chronological floor is
  6. A sharp example would test the floor at the smallest paired size.
- Does one thin map appear once block entries may lie in a larger
  characteristic-two field, or once a stage may use three or more full
  calls? Either would be a route around this census without reaching
  g=13.
- Do the unconstructed profiles g=13, q=8 (five rank-8 maps) and g=31,
  q=26 (five rank-q maps) exist with noncommuting projectors? This g=3
  result does not lift. Commuting projectors remain impossible for those
  map counts.

## Credit

The paired-star contract, the rank floor, and the commuting map-count are
from PR #5747 (Ali Romman), including the predecessor statements in
PR #5673, PR #5631, and PR #5617. The two-map control is the construction
in `research/coupled31-chronology/COMMUTING.md`, specialized to g=3 and
q=1. Prepared by unpaidmoon with substantial Cursor Grok assistance.
Independent human review and a proof-assistant proof are unclaimed.
