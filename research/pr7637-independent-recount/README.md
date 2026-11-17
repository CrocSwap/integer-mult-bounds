# Independent recount of the PR #7637 word and invoices

**No new κ. No frontier change. No supplier admission.** This package is an
independent finite audit of the open candidate
[PR #7637](https://github.com/CrocSwap/integer-mult-bounds/pull/7637) by
SYLforge at exact head `32e3853b2250f1971932919cbbc01348cd8245be`
(conditional κ ≥ 0.0037, the portable 233-CLEAR composition). It compares the
#7637 word and invoice with the open
[PR #7633](https://github.com/CrocSwap/integer-mult-bounds/pull/7633) word and
invoice at head `8b885be4a553dea375303808fdfff52ed0d71019`. It applies the
method of [PR #7628](https://github.com/CrocSwap/integer-mult-bounds/pull/7628),
[#7635](https://github.com/CrocSwap/integer-mult-bounds/pull/7635),
[#7638](https://github.com/CrocSwap/integer-mult-bounds/pull/7638) and
[#7639](https://github.com/CrocSwap/integer-mult-bounds/pull/7639).

## Why this check adds coverage

#7637 ships its word and its complete invoice only inside the packed data
archive `data/inputs.tar.gz`, and its checks reuse earlier author receipts. This
package takes the two objects out of the archive, binds the paid and target
invoice of the claim to the word bytes, and checks the moment signs with a
separate engine. It runs in about one second. `verify.py` imports no
constructor, application or pricing engine from #7637. No audit of #7637 was
found among the open PRs on 2026-11-17.

## Result

All statements are about the four pinned files in `inputs/pr7637/`. The #7633
files equal the blobs at the #7633 head. The #7637 files are objects of the
archive at the #7637 head, and their SHA-256 equal the manifest entries (see
[SOURCES.json](SOURCES.json)).

1. **Digests and census.** The canonical JSON digest of the #7637 word equals
   the one that its README states (`8ab3d9db…`). So does the digest of the #7633
   word (`4961e5e9…`). The #7637 word has 78,596 events: 68,049 ADD, 3,890
   SCALE, 6,191 MOVE, 233 INIT and 233 CLEAR. At most 50 owned fields are live
   at one time, and 52 owned labels are used.
2. **Header.** The two words are equal except `program`. No initial chart
   changes, and `initial[457]` is 281 in both.
3. **Chart chronology.** Each field is followed through the complete program of
   both words (77,598 and 78,596 events). Each MOVE starts at the current chart
   of its field. Each ADD, COPY and SCALE acts at the chart where its operands
   are. Each INIT creates a dead owned field and each CLEAR removes a live owned
   field at its current chart. The public fields end at the `final` charts.
4. **Paid recount.** Rank law: `rank(a->b) = dim(A+B) - dim(A∩B)` over GF(2).
   In both words each MOVE joins two nested frames and has a positive rank. With
   `H(word)` the MOVE rank histogram, exactly `paid(invoice) = 17 · H(word) + K`
   with the same `K = {1:384, 8:656, 9:32, 16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:208}`
   for both words. This `K` equals the one of the #7612, #7630, #7631, #7633 and
   #7636 recounts. The native MOVE change per call is
   `{1:-13, 2:-46, 3:-7, 4:-40, 5:+4, 6:+43, 8:+1}`. The MOVE count goes from
   6,249 to 6,191 and the total rank of the change is zero. Paid positions go
   from 110,009 to 109,023, which is 17 · 58 fewer.
5. **Target recount.** For each helper field (every public field that is not a
   main, with the main set as #7630 defines it) the target rank is
   `rank(final frame) - rank(initial frame)`. Exactly
   `targets(invoice) = 17 · T(word) + K_T`, with the same
   `K_T = {9:416, 17:416, 25:416, 33:416, 41:416, 49:416, 57:416, 65:416, 73:208, 137:208}`
   for both words. The helper change per call is empty. Target positions stay
   22,461 and the rank surplus stays 1,424.
6. **Moment signs.** A separate 256-bit integer interval engine evaluates
   `M(κ) = Σ (T_r - P_r) r^(1-κ)`. The #7637 invoice is positive at the claim
   `0.0037`, at the #7636 claim `0.0036807241001` and at the #7633 value
   `0.003667193194322`. It is negative at the bit cap `0.00376669`. The PR does
   not state a crossing. This audit measures one between `0.00370007` (positive)
   and `0.00370008` (negative), so the claim is about `7.7 · 10^-8` below it.
   The #7633 invoice is positive at its tested point `0.00366719319432207` and
   negative at `0.0036672` and at the #7637 claim. The upper bounds of `dM/dκ`
   on `[0, 0.00376669]` are negative for both invoices. For #7633 it is
   `-379338.0672489424`, equal to the value of the #7633 recount. For #7637 it
   is `-375918.531…`. So each crossing is unique on the interval.
7. **Tent test.** The change in the moment is zero or positive for every tariff
   `min(r, a)` and positive for some a. So #7637 is no worse than #7633 for every
   increasing concave tariff with `f(0) = 0`.
8. **Controls.** Ten semantic mutations reject: a growth-only rank law, one more
   paid unit, the old word with the new invoice, a dropped MOVE, a changed
   initial chart, an ADD at the wrong chart, a MOVE to another chart, a changed
   frame, the old invoice at the new claim and a point above the crossing.

## What this does not establish

- #7637 states that no admitted common supplier exists and that its changed
  entrance, whole-extent reset, residual domain and cost obligations are open.
  This audit does not touch them.
- `K` and `K_T` are measured from the invoices. They are not derived from the
  #7113 caller.
- The main set is the definition of #7630. It is not derived from the physical
  caller.
- The ordinary bill and the PR tariff (4,000 ordinary units per lifetime pair,
  32 scalar services per INIT or CLEAR, coefficient 2^20 per service) are not
  recounted. The 10^9 allowance is not checked.
- The 233 recoverability certificates, the scalar audit, the exact rational
  replay, the native route, the signed route, the precision and tape checks and
  the external #7334 archive are not replayed.
- The recount compares the #7637 word with the #7633 word, because they share
  headers and initial charts. It does not check the construction that the PR
  describes (the H5B base and the E1 and E4 edits).
- The five framework assumptions remain as #7637 states them. A correct count is
  not a supplier admission.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/research_package.py --package research/pr7637-independent-recount --check-only
python3 scripts/research_package.py --package research/pr7637-independent-recount
python3 -I -B research/pr7637-independent-recount/verify.py
```

Environment of the recorded run: CPython 3.13.9, Windows 11, about 1 s, with
the registered argv run directly. The package runner requires Python 3.12 for
the replay step, and this machine has no Python 3.12. **The Python 3.12 runner
replay is not run.** Canonical main at the start and before submission:
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, checked
2026-11-17 UTC.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Recount the ordinary bill and the PR tariff with the formula that #7633
   names. Blocker: that formula lives in repository scripts that this audit did
   not read.
2. Show that a common supplier covers all 233 lifetimes and the changed
   entrance. Blocker: it needs the #7113 caller and is outside a count audit.
3. Replay the reconstruction, native and signed routes on a Python 3.12 runner
   with the pinned #7334 archive.

## Credit

The audited construction, word, invoice and claim are by SYLforge (#7637), on
the work of SYLforge (H5B, #7616, #7620), DreamingOfClouds (#7630, #7636),
Clear1nsight (#7631, #7633, #7626), Ali Romman (#7605), Rohan Arun (#7113,
#7334), Hao Yan, ToikY and their predecessors. The vendored files keep their
Apache-2.0 license. The task card `independent-moment` and the package tooling
are by Douglas Colkitt.

This audit was prepared by fluorine with substantial Anthropic Claude
(Claude Code) assistance. New work is Apache-2.0. No independent human review
of this audit exists yet.
