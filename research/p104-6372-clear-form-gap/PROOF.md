# The PR6372 rank margin does not discharge two forward CLEAR forms

## Object

The candidate is the literal word in PR6372 at head
`b556600ffe14be72406b03a47c661f3c7f1aff06`, file
`research/p104-contact-block-contraction/WORD.json.gz`, Git blob
`0af79e58172f85c302c35b193205c0b185b09393`, SHA256
`e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491`.
The comparison word is that package's frozen PR6353 input, Git blob
`03ea7690285d4cda72815f962d5710ab96e08490`, SHA256
`0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928`.
Both bytes are copied into this package. PR6372's commit is not an ancestor
of the branch, so the verifier authenticates those bytes directly.

The scalar projection gives each of the 770 public coordinates its own
initial basis functional and gives every owned coordinate the zero functional
at `INIT`. `ADD`, `COPY` and `SCALE` use their literal dyadic coefficients.
`MOVE` changes only the frame label. `CLEAR` records the functional and then
drops the coordinate. This is the same projection used to state PR6372's
local rank margin; it is not a native phase or owned-erasure proof.

## Proposition

Let `f` be the public functional discarded by owned role 779 at its lifetime
from event 12998 to CLEAR event 17756, frame 127. Let `g` be the functional
discarded by role 780 from event 12999 to CLEAR event 17755, frame 127.
Then both supports have size 97, every coefficient lies in `{±1, ±2, 4}`,
the two forms agree on their 93 common coordinates, and

```text
f - g = 2(e_27 - e_57 + e_87 - e_92 + e_228 + e_230 - e_232 - e_234).
```

The source word has neither of these CLEAR indices. Relative to that source,
the candidate's MOVE multiset changes only by replacing the two transports
`(224, 1091→127)` and `(227, 1091→127)` with `(224, 1091→245)` and
`(227, 1091→245)`. Frames 3, 1091, 245 and 127 have dimensions 0, 4, 8 and 9,
nested in that order, so the declared nested-rank image of this replacement
is the paid change `2H_4 - 2H_5` and the productive change `2H_8 - 2H_9`.

That rank expression does not contain `f` or `g`. Both forms are nonzero, so
the expression is not a discharge of these two forward CLEARs.

## Proof

`verify.py` replays both literal programs. It checks the MOVE symmetric
difference, the four frame dimensions and the resulting rank counters before
reading the CLEAR rows. It then rebuilds `f` and `g` from the candidate
program and compares `f - g` with the eight-term form above. A one-coefficient
mutation of `f` is required to change that difference, so the comparison is
not a vacuous success. The canonical row hashes agree with the support-97
receipts published by the PR6376 endpoint audit:

```text
779  02ce1aeb475900c8075ad512ad444960a7766f940f489825a56374a3c3d85f39
780  b949deff3f5c36b3465df10cbb1e38c0731284f0c0a72897fcacac5f54e83193
```

The replay visits every event of both words. It is a finite exact identity
on these pinned programs, not a sample and not an analytic closure.

The rank margin is a function of the two replaced MOVE records and the four
frame dimensions only. The CLEAR events do not appear in that multiset, and
neither functional is the zero row. Therefore no evaluation of
`2(H_8 - H_9) - 2(H_4 - H_5)`, including the 19-copy extension claimed in
PR6372, cancels `f` or `g`. PR6372 already says a forward CLEAR may discard a
nonzero functional and that the inherited owned-erasure assumption remains.
This identity makes the two discarded forms explicit and shows they are
distinct from the eleven dual-preparation zero rows, which are a different
lifetime claim.

## What this does not prove

It does not decide whether the retained owned-erasure contract permits these
discards. The selected assumption `owned_erasure` still says only that owned
streams obey the retained allocation, erasure and ownership contracts.
Selected κ remains `781451/250000000`. There is no new conditional κ, no
native column or phase check, no 19-copy caller recount, and no transfer to
PR6375, whose six further helper edits leave this word.
