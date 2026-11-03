# Line-span(7) query does not beat its zero-frame scatter

**No new κ.** Selected conditional κ stays `781451/250000000`. Discussion #1166
comment
[19143427](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19143427)
already stopped one triangular continuation of Rohan Arun's draft PR #1525 at
`90d39a5603c7fbfd8d8d957e9732d9b6ebd6317f`, and left the evidence in local paths.
This package replays that scatter identity from the pinned bytes and checks the
constructor fact the handoff left open: `model.move` rejects a descent from
`span(7)` to the zero frame.

## Result

Puncture 0 builds `q = (c61 + c63 + c31 + c256) / 2`. On the pinned word, the
copied query is the line `span(7)`. The retained cut is 176 zero-frame centre
ADDs, 22 from each of the eight centres. The triangular substitution

- column 61 becomes twice itself,
- columns 63, 31 and 256 each lose column 61,

reproduces every original scatter linear form. Each of the 112 outputs is a
vector on the 704 roles. This check does not replay section B. The corrected
matrix has 230 nonzero ADD entries, exactly 54 more. Those 54 split by support:
column 63 overlaps column 61 in 8 rows and cancels 4 of them (`+10`), while
columns 31 and 256 are disjoint from column 61 (`+22` each). JoyboyBrian's
handoff already recorded the 230-versus-176 census. The overlap split is checked
here.

All 62 dirty columns of `q` already appear in those original outputs. A final
map that equals the original scatter therefore keeps every one of them. A final
map that zeroes any of them does not deliver the original target outputs.

The PR1060 constructor `move` admits a change only when the old frame is
contained in the new one. `contained((7,), ())` is false, so that constructor
rejects moving the query register from `span(7)` to the zero frame. The handoff
priced the same conversion if a paid rank-1 copy is granted instead, and the
profiles it named are `{1: 4, 8: 1}` and `{1: 5, 8: 1}`. For every positive
integer power tariff those two multisets differ by exactly 1. The same strict
increase holds for every tariff that gives rank 1 a positive price and prices
no other rank differently. The 54 extra ADDs are further nonnegative scalar
cost on this matrix.

## What this does not show

This does not price a scatter that consumes the line-7 query directly, a
different correction matrix, whole-call owners, precision, tape, compiler, or
outer admission. It does not replay section B and it does not change the
selected frontier. The handoff's local scripts remain unpublished; these checks
recompute the scatter identity from the pinned word and centre seed.

## Reproduction

Python 3.12, standard library only:

```sh
python3 -B research/p111-line7-query-price/verify.py
python3 -B scripts/research_package.py --package research/p111-line7-query-price
```

Expected first line: `PASS_P111_LINE7_QUERY_PRICE delta_adds 54 dirty_visible 62 line_to_zero_move False NO_NEW_KAPPA`.

The word SHA-256 is `e8e6e78ff7422275c38324499e1f33fb2ecd30de9503aef2b8f1ee80d8c4df8e`.
Failure controls inside the verifier: omitting the three partner corrections
changes an output, and the containment test rejects the line-to-zero move.

## Open next questions

1. Can a continuation whose 22 query receivers stay at `span(7)` until their
   original final frames are restored beat `{1: 4, 8: 1}` after every restoration
   copy is charged? The scalar cut does not record those final frames.
2. Is there a correction other than this triangular substitution that preserves
   the 112 output forms with no extra rank-1 child and fewer than 230 ADDs?

## Credit

Word, centre seed and query formula: Rohan Arun, PR #1525, with the retained
PR1297 / PR1134 / PR1060 lineage in that package's NOTICE. The triangular
relation, the 230-versus-176 census, and the conditional `{1: 4, 8: 1}` to
`{1: 5, 8: 1}` bill are JoyboyBrian's, comment 19143427; that note labelled its
checker local-only. Frame containment is the test in PR1060 `model.py`
(`contained`). This replay and the support split were prepared by unpaidmoon
with substantial Cursor Grok assistance. Apache-2.0.
