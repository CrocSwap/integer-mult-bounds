# Independent recount of the PR #7612 word, paid invoice and moment signs

**No new κ. No frontier change. No supplier admission.** This package is an
independent finite audit of one open candidate,
[PR #7612](https://github.com/CrocSwap/integer-mult-bounds/pull/7612) at exact
head `e814828ee5b869c9468282d57ba28c364b07d130` (conditional κ = 0.003652740309,
Clear1nsight). The author requested independent review in the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19626233).

## Why this check adds coverage

The four-command generic replay of #7612 does not count the candidate invoice
from the candidate word. `build.py` builds `data/invoice-new.json` as the #7611
invoice plus the declared delta `{1:-34, 2:+34, 3:-17, 4:-17, 5:+17}`. Only the
two dedicated application stages (about 20 minutes, 2 GiB) reconstruct the
complete invoice. This package binds the declared paid histogram to the word
bytes with a separate count that runs in about one second. `verify.py` imports
no constructor, application or pricing engine from the PR.

## Result

All statements are about the four pinned files in `inputs/pr7612/`. Their bytes
equal the blobs at the PR head (see [SOURCES.json](SOURCES.json)).

1. **Edit recount.** A diff that does not use the PR's index literals finds
   exactly one dropped event (index 41074, `MOVE 329 373->618`) and four
   substitutions (indices 41073, 41075, 41166, 42110). All of them act on fields
   134 and 329. The word headers are equal. Scalar content of the edited ADD is
   equal. The incident ranks change from `{1,1,3,4}` to `{2,2,5}`.
2. **Chart chronology.** Each field is followed through the complete program of
   both words (76,668 and 76,667 events). Each MOVE starts at the current chart
   of its field. Each ADD, COPY and SCALE acts at the chart where its operands
   are. Each INIT creates a dead owned field and each CLEAR removes a live owned
   field at its current chart. The public fields end at the `final` charts.
3. **Paid recount.** Rank law: `rank(a->b) = dim(A+B) - dim(A∩B)` over GF(2)
   for the frame spans A and B. In both words each MOVE joins two nested frames
   and has a positive rank. Let `H(word)` be the MOVE rank histogram (public and
   owned MOVEs together). Then, exactly:

   `paid(invoice) = 17 · H(word) + K`

   with the same word-independent caller histogram

   `K = {1:384, 8:656, 9:32, 16:416, 24:416, 32:416, 40:416, 48:416, 56:416, 64:208}`

   for #7611 and for #7612. The recounted native delta is
   `H(7612) - H(7611) = {1:-2, 2:+2, 3:-1, 4:-1, 5:+1}`. Paid positions are
   110,281 and 110,264. The two invoices state equal targets (22,461 positions,
   rank surplus 1,424).
4. **Moment signs.** A separate 256-bit integer interval engine (logarithms from
   an `atanh` recurrence, exponentials from a Taylor series, both with explicit
   remainder bounds) evaluates `M(κ) = Σ (T_r - P_r) r^(1-κ)`. The signs agree
   with the PR at seven points: the candidate is positive at the claim, at the
   tested point `0.003652740309007`, at the stated lower bracket and at the
   #7611 raw upper. The candidate is negative at the stated upper bracket. The
   #7611 invoice is negative at the claim and at its raw upper. An upper bound
   of `dM/dκ` on `[0, 0.00376669]` is negative for both invoices (about
   -3.8086e5 for #7612), so each crossing is unique on that interval.
5. **Controls.** Nine semantic mutations reject: a growth-only rank law, one
   more paid unit, the old word with the new invoice, the ADD at the old contact
   chart, the dropped MOVE restored, a wrong restoration chart, a changed frame
   373, the #7611 invoice at the claim, and a point above the bracket.

**Local-only supplement.** `verify.py --lineage` reads the #7604, #7605 and
#7608 words and invoices from the PR head tree in local Git objects. The same
`K` holds for all three. This mode skips when the PR head object is absent. It
is not part of the registered command.

## What this does not establish

- The histogram `K` is measured from the invoices. This package does not derive
  it from the #7113 caller.
- The target histogram is not recounted. The package only checks that the edit
  leaves headers, owned MOVEs, INIT and CLEAR events unchanged and that both
  invoices state equal targets.
- No physical map, Clifford identity, native or signed application, compiler,
  precision, tape, ordinary bound or outer predicate is replayed.
- The five framework assumptions and the CLEAR44 service premise of #7608/#7611
  remain as stated in the PR.
- A correct count and a correct root are not a supplier admission.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/research_package.py --package research/pr7612-independent-invoice-recount --check-only
python3 scripts/research_package.py --package research/pr7612-independent-invoice-recount
```

Direct run, with the optional lineage supplement:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git pull/7612/head
python3 -I -B research/pr7612-independent-invoice-recount/verify.py --lineage
```

Environment of the recorded run: CPython 3.13.9, Windows 11, about 1 s, with
the registered argv run directly, in normal and `-O` mode. The metadata and pin
check passed. The package runner requires Python 3.12 for the replay step, and
this machine has no Python 3.12. **The Python 3.12 runner replay is not run.**
Canonical main at the start and before submission:
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8,
checked 2026-11-16 UTC.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. Derive the caller histogram `K` from the #7113 signed caller definition.
   With that derivation, the complete paid invoice of each P104 successor word
   follows from the word bytes in about one second. First step: count the QUERY
   and IDLE charges by rank in the retained #7605 signed application. Blocker:
   that reconstruction lives in the dedicated application stages, which this
   session did not read.
2. Recount the productive target histogram from the word header and owner
   chronology. First step: apply the target rule of the reviewed #5599/#7000
   proof review to the `hosted` and `ports` fields. Blocker: the word file does
   not state the helper target semantics.

## Credit

The audited construction, word, invoices and claim are by Clear1nsight
(#7612, #7611), on the retained P104 lineage of Ali Romman (#7605),
DreamingOfClouds, SYLforge, Hao Yan, ToikY, Rohan Arun and their predecessors.
The recursive invoice schema and the pricing tools belong to their authors.
The vendored files keep their Apache-2.0 license. The task card
`independent-moment` and the package tooling are by Douglas Colkitt.

This audit was prepared by fluorine with substantial Anthropic Claude
(Claude Code) assistance. New work is Apache-2.0. No independent human review
of this audit exists yet.
