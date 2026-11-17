# Independent recount of the PR #7631 and #7633 words and invoices

**No new κ. No frontier change. No supplier admission.** This package is an
independent finite audit of two successive open candidates by Clear1nsight:
[PR #7631](https://github.com/CrocSwap/integer-mult-bounds/pull/7631) at exact
head `2f1cc8c0f8c281afd2f99aeeeae6153e269f4721` (conditional κ ≥ 0.003666272802)
and [PR #7633](https://github.com/CrocSwap/integer-mult-bounds/pull/7633) at
exact head `8b885be4a553dea375303808fdfff52ed0d71019` (conditional
κ ≥ 0.003667193194322). The #7633 source word is byte-equal to the #7631
candidate word, so one package covers both links. It applies the method of
[PR #7628](https://github.com/CrocSwap/integer-mult-bounds/pull/7628) and
[PR #7635](https://github.com/CrocSwap/integer-mult-bounds/pull/7635).

## Why this check adds coverage

Each PR ships a complete paid and target invoice for its word, but the invoice
is the previous invoice plus a declared change. This package binds both sides of
each change to the word bytes with separate counts that run in about two
seconds. `verify.py` imports no constructor, application or pricing engine from
the PRs. No audit of #7631 or #7633 was found among the open PRs on 2026-11-17.

## Result

All statements are about the six pinned files in `inputs/pr7633/`. Their bytes
equal the blobs at the PR heads (see [SOURCES.json](SOURCES.json)). The #7631
candidate word and invoice equal the #7633 source word and invoice, byte for
byte.

1. **Digests.** The canonical JSON digests of the #7631 candidate word
   (`1ea66c26…`) and of the #7633 word (`4961e5e9…`) equal the two digests that
   the #7633 README states.
2. **Chart chronology.** Each field is followed through the complete program of
   all three words (77,373, 77,393 and 77,598 events). Each MOVE starts at the
   current chart of its field. Each ADD, COPY and SCALE acts at the chart where
   its operands are. Each INIT creates a dead owned field and each CLEAR removes
   a live owned field at its current chart. The public fields end at the `final`
   charts.
3. **Paid recount.** Rank law: `rank(a->b) = dim(A+B) - dim(A∩B)` over GF(2).
   In all words each MOVE joins two nested frames and has a positive rank. With
   `H(word)` the MOVE rank histogram, exactly `paid(invoice) = 17 · H(word) + K`
   with the same `K = {1:384, 8:656, 9:32, 16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:208}`
   for all three words. This `K` equals the one of the #7612 and #7630
   recounts.

   | link | native MOVE change per call | MOVEs | paid positions |
   |---|---|---|---|
   | #7631 | `{2:-1, 3:-1, 5:+1}` | 6,251 to 6,250 | 110,043 to 110,026 |
   | #7633 | `{3:-1}` | 6,250 to 6,249 | 110,026 to 110,009 |
4. **Target recount.** For each helper field (every public field that is not a
   main, with the main set as #7630 defines it) the target rank is
   `rank(final frame) - rank(initial frame)`. Exactly
   `targets(invoice) = 17 · T(word) + K_T`, with the same
   `K_T = {9:416, 17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 137:208}`
   for all three words. The #7631 link changes no helper target. The #7633 link
   changes `initial[457]` from 3 to 281 and no other initial chart. Its helper
   change per call is `{6:+1, 9:-1}`. Target positions stay 22,461 and the rank
   surplus stays 1,424.
5. **Moment signs.** A separate 256-bit integer interval engine evaluates
   `M(κ) = Σ (T_r - P_r) r^(1-κ)`. Its signs agree with the PRs at 14 points:
   each candidate is positive at its claim and at its raw lower bracket, and
   negative at its raw upper bracket (the brackets are 10^-34 wide). The #7633
   invoice is also positive at its tested point `0.00366719319432207` and at the
   #7631 claim. Each older invoice is negative at the newer claim. The #7627
   value `0.003665731276` is positive for the #7631 source and for #7631. The
   upper bounds of `dM/dκ` on `[0, 0.00376669]` are negative for all three
   invoices. For #7631 and #7633 they are `-379433.91241361655` and
   `-379338.0672489424`. These equal the values in the #7633 price file to all
   printed digits, so the two engines agree.
6. **Tent test.** For each link the change in the moment is zero or positive for
   every tariff `min(r, a)` and positive for some a. So each step is no worse
   for any increasing concave tariff with `f(0) = 0`.
7. **Controls.** Eighteen semantic mutations reject (eight for #7631 and ten for
   #7633): a growth-only rank law, one more paid unit, the old word with the new
   invoice, the old helper targets with the new invoice, an undone rebirth of
   field 457, an ADD at the wrong chart, a MOVE to another chart, a changed
   frame, the old invoice at the new claim, and a point above the bracket.

## What this does not establish

- #7633 depends on a common whole-private-extent supplier U that the PR states
  is not implemented, and on its own cold replay, which is open. This audit does
  not touch either one.
- `K` and `K_T` are measured from the invoices. They are not derived from the
  #7113 caller.
- The main set is the definition of #7630. It is not derived from the physical
  caller.
- The ordinary bill is not recounted. The #7633 matched-ordinary record gives
  791,355,340 for its source and 791,537,376 for its candidate, so this step
  adds 182,036. About 208 million of the 10^9 allowance remain.
- The 205 candidate CLEAR certificates, the exact rational replay, the native
  and physical checks, the signed catalogue and the precision premises are not
  replayed.
- Earlier links of the chain (#7625, #7626, #7627) are not recounted. The #7631
  source word is bound to its invoice here, but not to the #7627 word.
- The five framework assumptions remain as the PRs state them. A correct count
  is not a supplier admission.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/research_package.py --package research/pr7633-independent-recount --check-only
python3 scripts/research_package.py --package research/pr7633-independent-recount
python3 -I -B research/pr7633-independent-recount/verify.py
```

Environment of the recorded run: CPython 3.13.9, Windows 11, about 2 s, with
the registered argv run directly. The package runner requires Python 3.12 for
the replay step, and this machine has no Python 3.12. **The Python 3.12 runner
replay is not run.** Canonical main at the start and before submission:
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, checked
2026-11-17 UTC.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Recount the ordinary bills with the formula the PRs name. Blocker: that
   formula lives in repository scripts that this audit did not read.
2. Implement or refute the common supplier U of #7633. Blocker: it needs the
   #7113 caller and is outside a count audit.
3. Add the earlier links of the chain (#7625, #7626, #7627) to `verify.py`.

## Credit

The audited constructions, words, invoices and claims are by Clear1nsight
(#7631, #7633), on the role-457 mechanism of DreamingOfClouds (#7630), the
work of SYLforge (#7624, #7620) and the P104 lineage of Ali Romman, Hao Yan,
ToikY, Rohan Arun and their predecessors. The recursive invoice schema and the
pricing tools belong to their authors. The vendored files keep their Apache-2.0
license. The task card `independent-moment` and the package tooling are by
Douglas Colkitt.

This audit was prepared by fluorine with substantial Anthropic Claude
(Claude Code) assistance. New work is Apache-2.0. No independent human review
of this audit exists yet.
