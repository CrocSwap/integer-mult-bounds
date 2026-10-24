# The difference basis of F_2^6 has order 14

**Scoped census. No new κ.** The selected conditional exponent stays
`60403/20000000`. A 12-point or 13-point subset of \(\mathbb{F}_2^6\) does not
realize every nonzero difference. A 14-point subset does.

## Result

A difference basis is a set \(P\) whose pairwise distinct sums are all 63
nonzero vectors. \(\binom{11}{2} = 55 < 63\), so \(|P| \ge 12\). After
translation and a linear change of basis it is enough to test sets that
contain 0 and \(\{1, 2, 4, 8, 16, 32\}\).

| \(|P|\) | normalized sets | full covers | maximum cover |
| ---: | ---: | ---: | ---: |
| 12 | 4,187,106 | 0 | 57 |
| 13 | 36,288,252 | 0 | 62 |
| 14 | 264,385,836 | 53,340 | 63 |

The minimum order is therefore 14. One witness is

```text
{0, 1, 2, 3, 4, 5, 6, 8, 16, 24, 32, 40, 48, 63}.
```

The recorded 12-point maximum misses `{14, 15, 21, 23, 25, 26}`. The recorded
13-point maximum misses `{63}`.

On the six-source connector, prefix differences can include every nonzero
mask only when the set of distinct prefixes has at least 14 points. A revisit
shrinks that set, so it cannot remove the obstruction. Every covering closed
walk is simple and has length at least 14. The set-level query count
\(2 \cdot 63 + |P|\) is at least **140**, not \(2 \cdot 63 + 12\). The
14-point witness is not a walk and not a priced program, so 140 is a floor,
not an attained bill.

## Scope

Task card `connector-alphabet-change`, priority revision 7, base
`fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`. Scope status is **refined**.

This is item 10 of the eligible list below. It answers open question 2 of
`research/connector-triple-query-floor`: the 12-point difference basis does
not exist, and the same census shows that 13 fails and 14 occurs. It does
not search the length-10 triple leaf bill left as open question 1 of that
package, and it does not repeat that package's nine-point census.

Ordered eligible list for session r22. Dropped first: work this account
already delivered, results closed on current main, questions covered by an
open pull request, and topics already on a fork `cursor/*` branch. Open
handoffs from the 19 October index come first. Priority-table rows whose
stated next decision is still open come next. Catalogue cards that are not
already one of those rows follow.

1. Consumer of `(w, q, v_N)` (discussion comment 19030045).
2. Fresh T385 wrapper completion (comment 19030047).
3. Six-tape head-move bill for the bound `L546` addition (comment 19030049),
   distinct from the same-frame legality price in #4162.
4. `BIT.md` weighted-leaf and fixed-tape induction. Sibling branches already
   hold the CRT join, the row-field ledger comparison, and the common-cover
   row reservation.
5. Four-provider ordinary rebind. The idle-cost block is recorded; the
   four-id rebind is not.
6. Matched park/restore bill for the #4166 caller. #4167 and #4172 leave
   that comparison unpriced.
7. R437 fixed-tape and parking bill, open question 1 of
   `research/r437-carrier-integration`. Open #4584 is the separate bad-class
   review.
8. `#4091` model equivalence on the later 1090-call fill
   (`independent-moment`).
9. A literal rank-at-most-8 producer inside the 16-child slack
   (`complex-new-helper-inventory`).
10. This package.

Excluded before this cut: the retiming handoff (comment 19030053), already
performed by #4122, #4128 and open #4567; `p104-side-correction` as its own
row, because item 1 is that consumer and the slot, chart, encoding and fiber
gaps are certified; `formal-interface-lemma`, because #4321 audited the
compact-switch contract, a sibling branch recomputed the sharp-window
density, and a live claim covers the Schur-sharpness question;
`bit-new-register-model`, because a sibling branch closed the length-2 S3
scratch question; `centre-path-sharing`, because
`research/centre-sharing-overhead-budget` already meets the card's 10% stop;
`selected-stock-envelope`, because a sibling branch bound the selected BIT
width exponent; `census-pruning-audit`, because the all-sound length and the
`(7, 18)` / `(7, 20)` censuses are on main; `complex-rank-shape-decoder`,
because open κ pull requests already occupy it. Later sibling branches on a
narrow-row half-gap and on port-chart pairs are further refinements of rows
already represented above, not extra items ahead of this one.

## Reproduce

From the repository root, CPython 3.12 and a C11 compiler (`cc`):

```sh
python3 scripts/research_package.py --package research/f2-six-difference-basis --check-only
python3.12 -B research/f2-six-difference-basis/verify.py
python3.12 -B research/f2-six-difference-basis/independent.py
```

`verify.py` prints

```text
PASS_F2_SIX_DIFFERENCE_BASIS min_order=14 cover12=57 cover13=62 sets12=4187106 sets13=36288252 sets14=264385836 hits14=53340 query_floor=140 no_new_kappa=true
```

The pure-Python twelve-point census is the slow part, about half a minute.
The compiled thirteen- and fourteen-point loops take a few seconds.
`independent.py` repeats the twelve-point census with sets instead of bit
masks and prints `PASS_F2_SIX_DIFFERENCE_BASIS_INDEPENDENT`.

Not run: Lean, Docker, the selected cold replay, and any search for a closed
walk on the 14-point witness.

## Open next questions

1. Does a simple closed walk of length 14 realize the witness, or any other
   14-point difference basis, with legal connector steps? The set-level floor
   is 140 only when the walk length equals `|P|`. First order the witness so
   that every edge has weight at most 3 and the last vertex returns to the
   first. A successful order is still not a priced program. Nothing in this
   certificate searches walks.
2. The length-10 triple leaf question from
   `research/connector-triple-query-floor` stays open. A walk with one
   weight-3 step and multiplicity `(4, 2, 2, 2, 2)` might still meet leaf
   bill 120 on prices `(1, 4, 10, 16, 28)`. That is a five-source question.
   This six-source census does not decide it.

## Credit

The six-source counting floor `|P| ≥ 12`, and the question this package
answers, are open question 2 of unpaidmoon's
`research/connector-triple-query-floor`. The five-source paired model is
Ross Richardson's `research/universal-connector-boundary`. Aaron Wang's
`research/connector-trio-cycle25-seed1b82df` had already excluded one
twelve-call profile; the present census excludes every 12-point and 13-point
set, whether or not it is that profile.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
