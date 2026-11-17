# Independent recount of the PR #7630 word, paid and target invoices

**No new κ. No frontier change. No supplier admission.** This package is an
independent finite audit of one open candidate,
[PR #7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630) at exact
head `6026e87d1cac03eb5bd2aa8524a8f5891dd9934e` (conditional
κ = 0.0036667343458, DreamingOfClouds). It applies the method of
[PR #7628](https://github.com/CrocSwap/integer-mult-bounds/pull/7628) to a
word that also changes the productive target histogram.

## Why this check adds coverage

The generic replay of #7630 builds `data/invoice-new.json` as the #7623 invoice
plus a declared per-call delta, for the paid side and for the helper targets.
This package binds both sides of that delta to the emitted word bytes with
separate counts that run in about two seconds. `verify.py` imports no
constructor, application or pricing engine from the PR. No audit of #7630 or of
its parent #7623 was found among the open PRs on 2026-11-17.

## Result

All statements are about the four pinned files in `inputs/pr7630/`. Their bytes
equal the blobs at the PR head (see [SOURCES.json](SOURCES.json)). The #7623
word bytes also equal the word published in #7623.

1. **Header.** The two words have equal headers except `initial`. Exactly two
   fields change: `initial[457]` 3 → 281 and `initial[461]` 3 → 285.
2. **Chart chronology.** Each field is followed through the complete program of
   both words (77,277 and 208,738 events). Each MOVE starts at the current
   chart of its field. Each ADD, COPY and SCALE acts at the chart where its
   operands are. Each INIT creates a dead owned field and each CLEAR removes a
   live owned field at its current chart. The public fields end at the `final`
   charts.
3. **Paid recount.** Rank law: `rank(a->b) = dim(A+B) - dim(A∩B)` over GF(2)
   for the frame spans A and B. In both words each MOVE joins two nested frames
   and has a positive rank. Let `H(word)` be the MOVE rank histogram. Then,
   exactly:

   `paid(invoice) = 17 · H(word) + K`

   with the same word-independent caller histogram

   `K = {1:384, 8:656, 9:32, 16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:208}`

   for #7623 and for #7630. This `K` also equals the one of the #7612 recount.
   The recounted native delta per call is
   `H(7630) - H(7623) = {1:-2, 2:-3, 3:-5, 5:+1, 6:+2}` (6,257 to 6,250 MOVEs).
   Paid positions are 110,145 and 110,026.
4. **Target recount.** For each helper field (every public field that is not a
   main, with the main set as the PR defines it) the target rank is
   `rank(final frame) - rank(initial frame)`. Then, exactly:

   `targets(invoice) = 17 · T(word) + K_T`

   with the same `K_T = {9:416, 17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 137:208}`
   for both words. The recounted helper delta per call is
   `T(7630) - T(7623) = {6:+2, 9:-2}`. Target positions stay 22,461. The rank
   surplus stays 1,424.
5. **Moment signs.** A separate 256-bit integer interval engine (logarithms from
   an `atanh` recurrence, exponentials from a Taylor series, both with explicit
   remainder bounds) evaluates `M(κ) = Σ (T_r - P_r) r^(1-κ)`. The #7630
   invoice is positive at the claim `0.0036667343458`, at the #7627 value
   `0.003665731276` and at the #7623 value `0.0036624027915`. It is negative at
   `0.0036667343459`. The #7623 invoice is positive at its own value, negative
   at `0.0036624027916` and negative at the #7630 claim. An upper bound of
   `dM/dκ` on `[0, 0.00376669]` is negative for both invoices (about
   -3.794e5 for #7630), so each crossing is unique on that interval.
6. **Tent test.** The change in `Σ (T_r - P_r) f(r)` is zero or positive for
   every `f(r) = min(r, a)`, a = 1 to 137, and positive for some a. Every
   increasing concave `f` with `f(0) = 0` is a non-negative combination of
   these tents on the integer ranks, so the #7630 profile is no worse for any
   such tariff. The PR states this as "uniformly better".
7. **Controls.** Ten semantic mutations reject: a growth-only rank law, one more
   paid unit, the old word with the new invoice, the old helper targets with
   the new invoice, an undone rebirth of field 457, an ADD at the wrong chart,
   a MOVE to another chart, a changed frame, the #7623 invoice at the claim,
   and a point above the bracket.

## What this does not establish

- The histograms `K` and `K_T` are measured from the invoices. This package does
  not derive them from the #7113 caller.
- The main set is the PR's own definition (`live`, `live + 112`, and the hosted
  `X2` and `Y2` fields). It is not derived from the physical caller.
- The exact rational replay of the hub re-settle, the changed CLEAR contents and
  the 5-smooth coefficient grid are not recounted.
- The ordinary bill is not recounted. The PR states 786,433,632 for #7623 and
  867,014,040 for #7630, below 10^9. The word grows from 77,277 to 208,738
  events, so about 133 million of the allowance remain.
- No physical map, Clifford identity, native or signed application, compiler,
  precision, tape or outer predicate is replayed.
- The five framework assumptions and the premises that #7630 inherits from
  #7620 remain as the PR states them. A correct count and a correct root are not
  a supplier admission.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/research_package.py --package research/pr7630-independent-recount --check-only
python3 scripts/research_package.py --package research/pr7630-independent-recount
```

Direct run:

```sh
python3 -I -B research/pr7630-independent-recount/verify.py
```

Environment of the recorded run: CPython 3.13.9, Windows 11, about 2 s, with
the registered argv run directly. The package runner requires Python 3.12 for
the replay step, and this machine has no Python 3.12. **The Python 3.12 runner
replay is not run.** Canonical main at the start and before submission:
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, checked
2026-11-17 UTC.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Recount the ordinary bill of the #7630 word with the formula the PR names.
   Blocker: that formula lives in a repository script that this audit did not
   read.
2. Derive the paid and target caller histograms from the #7113 signed caller
   definition. Blocker: the reconstruction lives in the dedicated application
   stages, which this session did not read.

## Credit

The audited construction, word, invoices and claim are by DreamingOfClouds
(#7630, #7623), on the P104 lineage of SYLforge (#7620), Clear1nsight,
Ali Romman, Hao Yan, ToikY, Rohan Arun and their predecessors. The recursive
invoice schema and the pricing tools belong to their authors. The vendored
files keep their Apache-2.0 license. The task card `independent-moment` and the
package tooling are by Douglas Colkitt.

This audit was prepared by fluorine with substantial Anthropic Claude
(Claude Code) assistance. New work is Apache-2.0. No independent human review
of this audit exists yet.
