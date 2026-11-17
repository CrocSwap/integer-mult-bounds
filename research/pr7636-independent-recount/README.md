# Independent recount of the PR #7636 word and invoices

**No new κ. No frontier change. No supplier admission.** This package is an
independent finite audit of the open candidate
[PR #7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636) by
DreamingOfClouds at exact head `7e68d8dd62d9a38c0f3c942262a7a85ca7125b75`
(conditional κ = 0.0036807241001, 22 swap-then-delete composites on the #7630
word). It applies the method of
[PR #7628](https://github.com/CrocSwap/integer-mult-bounds/pull/7628),
[PR #7635](https://github.com/CrocSwap/integer-mult-bounds/pull/7635) and
[PR #7638](https://github.com/CrocSwap/integer-mult-bounds/pull/7638).

## Why this check adds coverage

#7636 ships a complete paid and target invoice for its word. The invoice is the
#7630 invoice plus a declared change. This package binds that change to the word
bytes with separate counts that run in about two seconds. `verify.py` imports no
constructor, application or pricing engine from #7636. No audit of #7636 was
found among the open PRs on 2026-11-17.

## Result

All statements are about the four pinned files in `inputs/pr7636/`. Their bytes
equal the blobs at the PR head (see [SOURCES.json](SOURCES.json)). The base word
and base invoice equal the #7630 word and invoice, byte for byte.

1. **Header.** The two words are equal except `program`. No initial chart
   changes.
2. **Chart chronology.** Each field is followed through the complete program of
   both words (208,738 and 202,668 events). Each MOVE starts at the current
   chart of its field. Each ADD, COPY and SCALE acts at the chart where its
   operands are. Each INIT creates a dead owned field and each CLEAR removes a
   live owned field at its current chart. The public fields end at the `final`
   charts.
3. **Paid recount.** Rank law: `rank(a->b) = dim(A+B) - dim(A∩B)` over GF(2).
   In both words each MOVE joins two nested frames and has a positive rank. With
   `H(word)` the MOVE rank histogram, exactly `paid(invoice) = 17 · H(word) + K`
   with the same `K = {1:384, 8:656, 9:32, 16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:208}`
   for both words. This `K` equals the one of the #7612, #7630, #7631 and #7633
   recounts. The native MOVE change per call is
   `{2:-18, 3:-6, 4:-20, 6:+20, 7:+2}`. The MOVE count goes from 6,250 to 6,228
   and the total rank of the change is zero. Paid positions go from 110,026 to
   109,652, which is 17 · 22 fewer.
4. **Target recount.** For each helper field (every public field that is not a
   main, with the main set as #7630 defines it) the target rank is
   `rank(final frame) - rank(initial frame)`. Exactly
   `targets(invoice) = 17 · T(word) + K_T`, with the same
   `K_T = {9:416, 17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 137:208}`
   for both words. The helper change per call is empty. Target positions stay
   22,461 and the rank surplus stays 1,424.
5. **Moment signs.** A separate 256-bit integer interval engine evaluates
   `M(κ) = Σ (T_r - P_r) r^(1-κ)`. Its signs agree with the PR at ten points.
   The #7636 invoice is positive at the claim `0.0036807241001`, at the #7633
   value `0.003667193194322`, at the #7630 claim `0.0036667343458` and at the
   #7627 value `0.003665731276`. It is negative at the upper bracket
   `0.0036807241002`. It is positive at `c - 10^-30` and negative at
   `c + 10^-30`, with `c = 0.00368072410014727862067955898005` the crossing
   that the PR states. The #7630 invoice is positive at its own claim, negative
   just above it and negative at the #7636 claim. The ratio of the claim to
   the #7633 value is 1.00368972. The upper bounds of `dM/dκ` on
   `[0, 0.00376669]` are negative for both invoices (`-379386.789…` and
   `-377942.182…`), so each crossing is unique there.
6. **Tent test.** The change in the moment is zero or positive for every tariff
   `min(r, a)` and positive for some a. So #7636 is no worse than #7630 for
   every increasing concave tariff with `f(0) = 0`.
7. **Controls.** Ten semantic mutations reject: a growth-only rank law, one more
   paid unit, the old word with the new invoice, a dropped MOVE, a changed
   initial chart, an ADD at the wrong chart, a MOVE to another chart, a changed
   frame, the old invoice at the new claim and a point above the bracket.

## What this does not establish

- `K` and `K_T` are measured from the invoices. They are not derived from the
  #7113 caller.
- The main set is the definition of #7630. It is not derived from the physical
  caller.
- The 22 composites in `data/edits.json` are not applied to the #7630 word. This
  audit binds the finished word to the invoice. It does not check each edit
  against the swap law of #7634.
- The exact rational replay of the hub re-settle, the 180 CLEAR certificates
  (151 change) and the affected-pair census (1,023 pairs) are not recounted.
- The ordinary bill is not recounted. #7636 states 859,783,396 (from
  867,014,040 for #7630), below 10^9. About 140 million of the allowance remain.
- The native, physical, signed, compiler, precision, tape and outer checks are
  not replayed.
- The five framework assumptions and the premises that #7636 inherits from #7630
  and #7620 remain as stated. A correct count is not a supplier admission.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/research_package.py --package research/pr7636-independent-recount --check-only
python3 scripts/research_package.py --package research/pr7636-independent-recount
python3 -I -B research/pr7636-independent-recount/verify.py
```

Environment of the recorded run: CPython 3.13.9, Windows 11, about 2 s, with
the registered argv run directly. The package runner requires Python 3.12 for
the replay step, and this machine has no Python 3.12. **The Python 3.12 runner
replay is not run.** Canonical main at the start and before submission:
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, checked
2026-11-17 UTC.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Recount the ordinary bill with the formula the PR names. Blocker: that
   formula lives in repository scripts that this audit did not read.
2. Apply the 22 edits of `data/edits.json` to the #7630 word and compare with the
   #7636 word. Blocker: the coordinate convention needs a careful read.
3. Replay the 180 CLEAR certificates and the census on a Python 3.12 runner.

## Credit

The audited construction, word, invoices and claim are by DreamingOfClouds
(#7636, #7630, #7623), on the swap device of SYLforge (#7616, #7620) and the P104
lineage of Clear1nsight, Ali Romman, Hao Yan, ToikY, Rohan Arun and their
predecessors. The recursive invoice schema and the pricing tools belong to their
authors. The vendored files keep their Apache-2.0 license. The task card
`independent-moment` and the package tooling are by Douglas Colkitt.

This audit was prepared by fluorine with substantial Anthropic Claude
(Claude Code) assistance. New work is Apache-2.0. No independent human review
of this audit exists yet.
