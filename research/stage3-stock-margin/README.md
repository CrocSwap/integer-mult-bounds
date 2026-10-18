# Native stage 3 lands in stage 2's stopped range

**Stock-interface audit; no new kappa.** The native stage-2 envelope is already
stated, conditionally, in the handoff
[discussion comment 18949652](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18949652).
This note takes the next cutoff pair that comment leaves open. It does not
choose a stock coefficient.

```sh
python3 -B research/stage3-stock-margin/verify.py
```

Expected:

```text
PASS_STAGE3_STOCK_MARGIN stage=3 margin=1015784602045963452130 routing_room=1701909188404384116 coefficient=unresolved stage2_margin_reproduced=true
```

Python 3.10+. The input is the recorded native receipt in
`research/selected-bootstrap-stock-audit/RESULT.json`. No supplier replay.

## The boundary lemma

For the selected native receipt, s*L3 - L2 > 1015784602045963452130. Every width w >= e^s with e >= 2^L3 therefore satisfies w > 2^(L2 + 1015784602045963452130), so that call sits in stage 2's stopped range. This does not choose between an external factor of 1 and a hoisted routing factor.

Here `s = 1 - stock_gap` is the same positive rational at all seven native
stages, `L2 = 1704765459304159860` and `L3 = 607288590542446415285737`.
The same function of the receipt reproduces the published stage-2 integer
`floor(s*L2 - L1) = 2851485324488315`. Replacing `L3` by `L2` makes the
difference negative, so the inequality uses the later cutoff.

The stage-2 handoff's internal reading keeps the coefficient at 8194 when the
previous stage is a completed leaf with external factor 1. Its hoisted reading
needs a bound on routing width. The analogous room at this stage is
`floor((1-s)*L2) = 1701909188404384116`: a routing call of width at most
`c_R*w` with `log2(c_R)` at most that integer would stay inside the previous
stopped range only under a source statement this receipt does not contain.
The historical increment 57,604 and the allowance 252 are not added.

If the coefficient were 8194, `ceil(log2(8*8194)) = 17`, and the recorded
stage-3 headroom is `2337861697120`. That comparison is only the fit guard.
The stored coefficient remains null.

## Open next questions

Which source sentence bounds the width of a stage-3 routing call to the
previous stopped algorithm? The stage-2 handoff already isolates that kind
of bound as W2. The first step is to match the retained cover-row text with
a factor `c_R` whose log is at most `1701909188404384116`. It is blocked
here because this receipt only has the cutoff arithmetic, not that sentence.

## Credit and limits

The stage-2 conditional envelope and its internal/hoisted split are the
handoff above. The receipt and headrooms are the selected stock audit.
The first-stage BIT envelopes are Adam Gall's and Nick Petalas's. This
package only moves one cutoff pair forward.

No selected certificate or kappa changes. The selected baseline was not
rerun in this sparse checkout. Stages 4 through 7, the complex `m=73`
supplier, hosting and precision stay open.

Prepared by Riquelme Soares (@hevlyo) with substantial AI assistance.
Apache-2.0. No independent human peer review is asserted.
