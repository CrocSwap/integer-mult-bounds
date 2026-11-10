# Consecutive paired-star rank at g=31, q=26

**Status: proof, for one schedule family. No new kappa.**

Selected frontier, unchanged:
`781451/250000000 = 0.003125804`
in `certificates/selected-result.json` at base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Scope and evidence

The assigned question is the unconstructed paired-star profile `g=31`, `q=26`:
five thin maps of rank 26, block size `d=52`, with full projectors that need
not commute. Discussion #5593 and `research/coupled31-chronology` leave that
profile open. Open PRs #6922 and #6940 are `g=3`, `d=2` finite censuses.
They say the `g=3` result does not lift, and this package does not use them
as evidence.

[PROOF.md](PROOF.md) proves the following. On the paired-star contract, if
the two halves of every stage are adjacent and no thin map sits between
those halves, the endpoint requires total thin rank at least `q g`. At
`g=31`, `q=26` that lower bound is **806**. Five rank-26 maps supply at most
**130**. This schedule family has no endpoint, whether or not the projectors
commute and whether or not the off-diagonal block `B` is zero.

The argument is an identity in the projector algebra plus a square-free
monomial count. The registered checker reduces those identities. It does not
enumerate call orders, field elements, or projectors at `q=26`. There is no
finite census of this profile and no heuristic search in the evidence.

Schedules that place a thin map between the two halves, or that nest or
cross stage intervals, are outside the proof. Unrestricted nonexistence of
the profile is not a result of this package. The same algebra is uniform in
`g` and `q`; the certified consequence is `g=31`, `q=26` only. The `g=13`,
`q=8` profile is a different assignment and is not reported here.

The older chronological floor `5q >= 4q+20` still holds and still passes at
`q=26`. The commuting-projector theorem still requires `ceil(31/2)=16` thin
maps of unrestricted rank. Neither of those statements is replaced.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/g31-q26-consecutive-rank --check-only
python3.12 scripts/research_package.py --package research/g31-q26-consecutive-rank
```

Direct replay:

```sh
python3 -B research/g31-q26-consecutive-rank/verify.py
```

The passing marker is `PASS_G31_Q26_CONSECUTIVE_RANK` with
`lower_total_rank=806` and `profile_total_rank=130`. The checker also drops
the relation `AB+BA=B` and requires that broken algebra to miss the local
stage factor. Small leaf counts `g=1,2,3,4` rerun the same scalar identity.
They are not a projector census.

Source pins are in [SOURCES.json](SOURCES.json). The catalogue card and the
selected record are provenance. The coupled-star proof and commuting note
are pinned at the same base commit. Full Git history is required to resolve
those blobs.

## Open next questions

1. Can a thin map placed between the two halves of a stage bring the total
   thin rank of a legal `g=31`, `q=26` word down to `5q=130`?
   The scalar prefix used above stops as soon as one stage is open, so the
   monomial cover does not apply. A useful first step is the core-to-leaf
   coefficient of that internal gap in the eigenbasis of its projector, with
   the off-diagonal blocks free. No such identity is proved here, and the
   `g=3` censuses do not answer it.

2. Can nested or crossing stage intervals, with projectors that do not
   commute, meet the endpoint with five rank-26 maps?
   Adjacency is what replaces each stage by `D I` and `D T`. A useful first
   step is the pure-product obstruction for one crossed pair and one nested
   pair in that same projector algebra, before any `q=26` search. No witness
   and no all-order proof for those intervals is supplied.

## Credit

The paired-star contract, the chronological rank floor, and the commuting
map-count are from PR #5747 (Ali Romman), including PR #5673, PR #5631, and
PR #5617. Cinna Davis supplied the controller/simplex lineage those packages
retain. Open PRs #6922 and #6940 record the separate `g=3` finite censuses.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
