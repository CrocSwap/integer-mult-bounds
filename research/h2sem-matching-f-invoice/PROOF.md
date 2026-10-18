# Seed-7 matching dominates the published seed-42 H2-sem invoice

**Scoped priced invoice. No new κ.**

## Setup

Let `W` be the selected PR589 R439 word. PR848's helper-temp wrap for an
oriented helper pair `(a,b)` prepends `a ^= b`, rewrites every D row containing
`a` by symmetric difference with `b`, and appends the reverse restoration.
Positive oriented pairs are those with arithmetic source-read saving

`sum_{rows containing a} (1_{b in row} - 1_{b not in row}) - 2 > 0`.

An ADD-greedy matching shuffles the positive list with a fixed seed, sorts by
nonincreasing saving (stable), and takes a maximal disjoint subset.

## Published baseline (PR1805)

Seed `42` yields 205 pairs and saving 6,231. Under H2-sem the completed wrap
has whole-word ADD count 18,074, forward envelope `F = 75,381`, reverse
envelope `B = 1,196,402`, paid profile mass 5,129, and strict precision guards.

## Improved matching

Seed `7` yields 208 pairs and saving **6,245**. The completed wrap has

- ADD count **18,060** (14 better than seed-42),
- `F = 73,805` (1,576 lower),
- `B = 1,187,790` (8,612 lower),
- the same paid profile `{1:1323,…,7:19}` and rank mass 5,129,
- local/nine-stage bits 95/180 (still under 104/192).

The unordered pair sets share 150 pairs and differ elsewhere; the saving=65
champion pair `(277,434)` appears in both. Semantic matrix `N` equals the
baseline on all 661 formal columns; complete forward/reverse COPY/ERASE
boundaries equal the baseline endpoint. H2-sem shape conditions 1–2 hold;
syntactic H2 and `K_equals_D` fail exactly as on the seed-42 wrap.

## Why the endpoint holds

The wrap is chronologically `H; D0; H` with `H = H^{-1}` over F2, so the
composite equals the original D map on every F2 column (PR1194 / PR1805). Full
helper restoration is necessary: deleting a restore breaks the helper basis.
Equality of the 661 binary D columns therefore certifies the H2-sem boundary
for every F2-module stream under the common zero-frame reading.

## Search scope

Among ADD-greedy shuffles with seeds `0..255` and saving ≥ 6,200 (233 invoiced
matchings), seed-7 uniquely maximises ADD saving and, among savings ≥ 6,231,
minimises `F`. This bounds the stated search; it is not a theorem about every
matching.

## Limits

No kappa claim. No optimality outside ADD-greedy tie-breaks. Composition onto
the PR1062 star word is open #2033's object and is not attempted here.
