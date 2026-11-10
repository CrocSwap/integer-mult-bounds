# Cursor meter for one R437 parent blank-return

**Partial certificate. No new κ.** The selected conditional exponent stays
`781451/250000000`.

## Result

On the success path of `packet_engine.py`, a completed packet is erased by
`rewind` followed by `Tape.clear`, starting from the trailing blank. For a
payload of `n` symbols that call has meter

```text
reads = 3n + 4,   writes = n,   moves = 3n + 6.
```

The parent geometry in `research/r437-carrier-integration/PHYSICAL.md` is one
payload of length

```text
n = 9475 * 12 * 3^128 = 972 * 9475 * 3^124.
```

The same call on that length is the parent blank-return invoice. The factor
`3^124` is the 124 omitted atom coordinates inside the gap. The opening
rewind, the blanking scan and the closing rewind each step across every
payload cell, so those coordinates are crossed three times. They are not
skipped.

The write count is exactly the one-visit lower bound from
`research/r437-parent-spectator-blank`. The move count is strictly larger.
The same call on the executed 972-bit fibre has moves `2922`, which does not
pay the parent.

The argument is in [PROOF.md](PROOF.md). `verify.py` runs the pinned
`records.Tape` on every length through 48, on the 972-bit fibre, and on the
two miniature parents `9475 * 12 * 3^k` for `k = 0, 1`. It does not allocate
the `3^128` parent.

## What stays open

`changed.clear()` and `local.clear()` still depend on where `action` leaves
the head. Gather, routing, parking, checkpointing and table setup are not
priced. One tape of length `n` is the predecessor's payload model; `9475`
separate tapes would add extra sentinel walks and are not this call. No
supplier and no new exponent is claimed.

## Task and overlap

- Task: `r437-carrier-integration`, scope **refined**.
- Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
- Selected record SHA-256 `9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa`.

Session r85, item 8 of the ordered eligible list. The 19 October handoffs
(discussion comments 19030045, 19030047, 19030049, and 19030053) are already
delivered or closed. Later handoffs whose canonical artifact is an open pull
request, including the H25 requests and the 2026-11-02 audits of #6348
through #6361, are excluded. The revision-8 next-decision table then supplies
six rows, naming `p104-side-correction`, `coverage-law-change` and
`bit-helper-contract`. Catalogue cards not named by those rows follow, in
catalogue order. Item 8 is `r437-carrier-integration`.

The card's reverse coefficient, child-constructor tapes, SOURCE87 fibre
multiplicity and payload-ratio lower bound are already delivered by this
account (#4147, #4160, #5277, #5276). This package answers open question 1 of
`research/r437-parent-spectator-blank`: the exact fixed-tape visit count,
including cursor motion across the 124 omitted coordinates. It does not
rederive the coefficient or rerun the pooled compiler.

Checked on 2026-11-02: no open pull request states this `3n+6` move count.
The merged predecessor #5276 stops at the payload ratio.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B scripts/research_selected_baseline.py
python3 -B research/r437-parent-blank-cursor/verify.py
python3 -B research/r437-parent-blank-cursor/test_verify.py
python3 -B scripts/research_package.py --package research/r437-parent-blank-cursor
```

`verify.py` prints `PASS_R437_PARENT_BLANK_CURSOR` with `writes` equal to the
parent payload and `moves = 3 * writes + 6`. `test_verify.py` prints
`PASS_R437_PARENT_BLANK_CURSOR_CONTROLS`.

Not run: `physical.py`, the pooled compiler, Lean, Docker, and
`make frontier6030-verify`. The universal statement for every `n` is the
control-flow count in `PROOF.md`; the checker executes the machine on the
lengths named above.

## Open next questions

1. Where does `action` leave the head of `changed` and `local` before their
   `clear` calls? Those blank-returns are not the success-path `current`
   call priced here. First step: one source-bound postcondition for `action`
   on a fibre of length `n`. Blocker: `action` is outside this package.
2. Can one of `G`, `C` or `F` in `BILL.md` be instantiated on both arms
   without setting the others to zero? A blank-return meter still does not
   sign the whole C/D inequality. First step: pin one tariff. Blocker: those
   tariffs are not inputs here.

## Credit

The parent extents, the constants `9475` and `972`, and the statement that a
one-visit lower bound is not the machine invoice are Chris R / Clear1nsight,
`research/r437-carrier-integration` and the open question in
`research/r437-parent-spectator-blank` (unpaidmoon #5276). The tape operations
are the retained predecessor `records.Tape` loaded by the selected physical
caller. The carrier lineage remains ai-nanachi / PR #3647, Ali Romman /
PR #1043, and Sagar Thakrar / PR #3700 and PR #2423.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
