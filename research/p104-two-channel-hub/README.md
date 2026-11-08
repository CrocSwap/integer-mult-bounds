# No two-channel S09 hub on the frozen serial schedule of PR #6824

**Exact scoped obstruction; no new κ.** On the reconstructed native word of
[PR #6824](https://github.com/CrocSwap/integer-mult-bounds/pull/6824), every
asynchronous collection/delivery pairing in the model below has rank at most
one. A two-channel hub needs `C D = I₂`, so none exists in this model, even if
all eligible access subdivisions, scalar operations and buffers are free.

The census covers all **77 helper boundary groups**. Thirty groups have at
least two helpers and target grade at least two. Their **4,296 critical cuts**
have pairing ranks `{0: 4292, 1: 4}`. The other groups are excluded by their
size or lack of a strict intermediate dimension. The source has 772 arbitrary
public inputs, 29 arbitrary dirty-owned input axes, 18,622 events and 1,095
stored frames. All 801 axes are retained in both histories.

The old scalar program and serial event order stay fixed. Every nested MOVE
may be subdivided at **any intermediate frame**, and its moving helper can
serve as a pivot there. A residency lemma reduces the common block frame to
the stored catalogue: inside one old MOVE only that role can visit a new
frame, so two old pivots require a stationary pivot already at a stored frame.
Collection and injection may use arbitrarily many earlier/later contacts.
Two old helper pivots must actually share the common frame at the cut, and
both rows and columns must have support in one common-boundary helper group.
This is the S09 retained-difference-buffer model. There are no extra old-role
relocations or free retags. Retimed/overlapping queries, transported or
substituted buffer pivots, changed source scalar contacts and altered helper
boundaries are outside the theorem. A new frame alone cannot evade it; new
frames with a changed pivot meeting can. Atlas C02 remains open generally.

## Reproduce

```sh
python3 -I -W error -B research/p104-two-channel-hub/verify.py
python3 -I -O -W error -B research/p104-two-channel-hub/verify.py
```

The standard-library verifier checks the source payload, literal scalar and
frame/ownership execution, all endpoint columns, all boundary groups, every
critical cut and the entire receipt. It prints
`PASS_P104_FROZEN_TWO_CHANNEL_OBSTRUCTION`. Normal replay is read-only;
`--emit` explicitly regenerates `RESULT.json`.

[PROOF.md](PROOF.md) proves the finite reduction and rank implication.
[RESULT.json](RESULT.json) lists every cut, pivot set, pure-space dimensions
and pairing rank, plus a complete rank-one matrix. [SOURCES.json](SOURCES.json)
pins the upstream reconstruction and digest. [SEARCH-NOTES.md](SEARCH-NOTES.md)
separates retiming discovery from the exact theorem.

Controls detect a genuine two-channel identity example, a pivot available
only inside a paid query, a nonzero two-by-two minor, dirty contamination and
cancellation that really recovers a pure direction. There is no native-phase,
caller, compiler, BIT or selected-result replay here. No new physical word is
claimed. Selected conditional κ = 0.003125804 and the five framework
assumptions are unchanged.

## Open next questions

1. Can query retiming create a profitable block? Start with exact rational
   C,D and charge the union of actual query edits, pivot access, boundary bases,
   buffer clears, completion fields and peak stock. The experimental screen
   is not an exclusion of retimings or larger blocks.
2. Can a new frame with a changed pivot meeting supply another direction?
   First give its binary basis and at least two real pivot arrivals, including
   the retiming or extra relocation required by the residency lemma.
3. Can a changed source contact or transported buffer evade the bound? Give
   its new chronology and all-input contract before reusing source histories.

## Credit

Ali Romman's PR #5786 supplies asynchronous hubs; ToikY's PR #5800 supplies
the complete temporal/dirty-axis contract and nonzero retained-buffer audit.
Atlas PR #5803 supplies S09, and PR #5806 retains composition obligations.
Credit Matarener's `p104-helper-split-exhaustion` for its earlier common-cut
census on PR #5907, and Ali Romman's `p104-fixed-contact-ceiling` and
`p104-paid-meeting-splits` for their different fixed-contact and paid-meeting
questions. The new result is this current-word asynchronous block certificate,
not a new general linear-algebra theorem.

DreamingOfClouds supplies PR #6824; @CubeJerry supplies PR #6805. Retain
the #6702, #6726, native, controller, compiler, analytic and BIT lineage in
[NOTICE](NOTICE). Prepared for @CubeJerry with substantial OpenAI Codex
assistance in a coordinated multi-agent investigation. Apache-2.0.
