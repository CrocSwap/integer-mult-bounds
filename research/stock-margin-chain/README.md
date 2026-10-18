# Stock-margin chain: every remaining cutoff pair lands in the previous stopped range

**Stock-interface audit; no new κ.** For the frozen selected bootstrap receipt this
note completes the cutoff-pair arithmetic begun by the native stage-2 handoff
([discussion comment 18949652](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18949652))
and the native stage-3 audit ([PR #2931](https://github.com/CrocSwap/integer-mult-bounds/pull/2931),
`research/stage3-stock-margin`). It adds the ten remaining pairs — native stages
4–7 and the whole conservative branch, stages 2–7 — and reproduces the two
published native integers as positive controls.

```sh
python3 -B research/stock-margin-chain/verify.py
```

Expected:

```text
PASS_STOCK_MARGIN_CHAIN native_stages=2-7 conservative_stages=2-7 new_pairs=10 published_controls=2 min_margin=2851485324488315 coefficient=unresolved headroom_guard=17 native_s=67018507072324140916999892981492927675859083/40000000000000000000000000000000000000000000000 conservative_s=1675462673946628390002997324537326053371609997/1000000000000000000000000000000000000000000000000
```

Python 3.10+. The only input is the recorded receipt
`research/selected-bootstrap-stock-audit/RESULT.json`, bound below by SHA-256.
No supplier replay, no coefficient choice and no selected-frontier change.

## The boundary lemma

For one branch, let `s = 1 - stock_gap` be the branch's fixed saving (uniform
across its seven recorded stages), and let `L_1 < ... < L_7` be the recorded
cutoffs in `RESULT.json`. For every `j = 2..7`,

```text
floor(s*L_j - L_{j-1}) > 0.
```

Every width `w >= e^s` with `e >= 2^{L_j}` therefore satisfies
`w >= 2^{L_{j-1} + margin_j}` with `margin_j = floor(s*L_j - L_{j-1}) > 0`, so
that call sits in stage `j-1`'s stopped range. The routing room for the hoisted
reading is `floor((1-s)*L_{j-1})`.

| branch | stage j | `floor(s*L_j - L_{j-1})` | `floor((1-s)*L_{j-1})` | status |
| --- | --- | --- | --- | --- |
| native | 2 | 2851485324488315 | 4777557234646 | published control |
| native | 3 | 1015784602045963452130 | 1701909188404384116 | published control |
| native | 4 | 361852943409004062662957360 | 606271101174941147673746 | new |
| native | 5 | 128902872114845343680818492656976 | 215971951161791423920760764122 | new |
| native | 6 | 45919069451025819974017753079498485812 | 76935687018952933071573623067467882 | new |
| native | 7 | 16357749867431357886201881301751734180286423 | 27406799379443943425326695785974298689751 | new |
| conservative | 2 | 2851485349075174 | 4777557267681 | new |
| conservative | 3 | 1015784614274199324771 | 1701909205985694510 | new |
| conservative | 4 | 361852949001065216196285881 | 606271109508797681506267 | new |
| conservative | 5 | 128902874547204377208495156774925 | 215971954868265831114423996024 | new |
| conservative | 6 | 45919070474352818766043006228287526563 | 76935688602102847428409756325327327 | new |
| conservative | 7 | 16357750287845003715345973449256621277195623 | 27406800037024020153662277717993715829414 | new |

The native stage-2 integer `2851485324488315` is the one published by the
stage-2 handoff, and `1015784602045963452130` is PR #2931's stage-3 integer; both
are recomputed here from the receipt rather than copied. The conservative branch
had no published cutoff-pair margin before this note.

## What this does and does not establish

- It establishes only the stopped-range membership of each stage's `w >= e^s`
  calls, one cutoff pair at a time, for both recorded branches.
- It does **not** choose a stock coefficient. Every `actual_stock_coefficient`
  in the receipt remains null. The internal reading `σ = 8194` of the first-stage
  BIT envelope and the guard `⌈log2(8*8194)⌉ = 17 ≤ H_j` are inherited
  comparisons, exactly as in the stage-3 audit; the guard is not an envelope.
  (The separate reserve-composition audit uses PR2120's refined coefficient 6748
  with guard 16; this note reproduces neither refinement and claims neither.)
- It does **not** bind the routing-width lemma `W_j` to source. The hoisted
  reading needs routing calls to `A_{j-1}` to have width `≤ c_R·w` with
  `log2(c_R) ≤ floor((1-s)*L_{j-1})`; the receipt has the cutoff arithmetic, not
  that sentence.
- It does **not** treat the complex `m=73` supplier, hosting or precision. The
  BIT producer (PR589, `m=64`, maximum child rank 42) supplies the fourteen
  recorded cutoffs; the selected complex supplier is a separate open obligation.

## Source boundary

The recorded cutoffs, gaps and headrooms are the fourteen-stage receipt audited
by `research/selected-bootstrap-stock-audit` from frozen PR1087's
`code/assemble.py` recurrence (`L_j = max(ceil(36/delta_j^2), ceil(1032/delta_j))`),
and this package reads that receipt rather than the assembler. The receipt bytes
are fixed by SHA-256 `f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917`
and the check fails on any drift, a stored coefficient, a changed cutoff or a
non-uniform gap. Controls include reusing `L_{j-1}` in place of `L_j` (must stay
negative at every stage), applying the other branch's saving to these cutoffs
(must not reproduce the same floors) and a tampered receipt (must be rejected).

## Reproduce

From the repository root:

```sh
python3 -B research/stock-margin-chain/verify.py
python3 scripts/research_package.py --package research/stock-margin-chain --check-only
python3.12 scripts/research_package.py --package research/stock-margin-chain
```

## Open next questions

1. **Bind `W_j` to source at the later stages.** The routing room is smallest at
   stage 2 of each branch (`4777557234646` native, `4777557267681`
   conservative); a source sentence bounding the width of a stage-`j` routing
   call to `A_{j-1}` by a factor whose log2 is at most that room would separate
   the external-factor-1 reading from the hoisted reading at every stage. The
   first step is to match the retained PR185/PR387 cover-row text with such a
   factor; it is blocked here because the receipt contains cutoff arithmetic,
   not that sentence.
2. **Find the analogous cutoff sequence for the complex `m=73` supplier.** The
   complex side binds the selected κ, and the stock audit records no
   `m=73`-shaped per-stage receipt. The first step is to locate the selected
   complex assembler's own per-stage cutoffs and check whether the same
   `floor(s·L_j − L_{j-1})` membership can be stated for them; it is blocked by
   the missing recorded cutoffs (the audit states the selected coefficient is
   uncomputed).
3. **Recompute `L_j` from the frozen PR1087 assembler instead of the receipt.**
   This package treats `RESULT.json` as its audited input; the stock audit
   already binds the formula. A separate host-side re-derivation would extend
   byte-level coverage from the receipt to the assembler, but would not change
   the membership result. The first step is to rerun the audit's formula path
   against `upstream1087.tar.gz`; the blocker is that this package deliberately
   does not vendor or execute that assembler.

## Credit and limits

The native stage-2 envelope, its internal/hoisted split and the `W_2` framing
are [@philippeVV](https://github.com/philippeVV)'s handoff
comment; the native stage-3 cutoff pair and routing room are Riquelme Soares's
([@hevlyo](https://github.com/hevlyo)) PR #2931 and its package. The receipt,
the fourteen cutoffs and headrooms are the selected stock audit
(`research/selected-bootstrap-stock-audit`) on Josie Elliston's PR1956/PR1965
work. The first-stage BIT envelopes are Adam Gall's and Nick Petalas's; the
selected BIT supplier is DreamingOfClouds's PR589 on eumemic's base, with
Rohan Arun's PR1094 assembly and Jeremy Kothe's PR1087 assembler retaining
construction credit. This package only extends the recorded margin arithmetic
to the pairs those predecessors left open.

No independent human review, supplier replay, selected cold replay or formal
kernel result is claimed. New work is Apache-2.0; retained predecessors keep
their attribution. Prepared by Kumagi ([@kumagi](https://github.com/kumagi))
with substantial AI assistance (DeepSeek V4.1 Flash in the OpenCode harness),
including a separate exact-arithmetic recomputation and mutation controls.
