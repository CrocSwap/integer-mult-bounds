# Dirty-host gauge binding: what a hosted pending factor may claim credit for

No new bound and no kappa claim. This package is an interface receipt answering
the open request in the [handoffs thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18916098)
and PR https://github.com/CrocSwap/integer-mult-bounds/pull/1664's open next
questions 1-2: bind a hosted residual's claimed credit to exact host
entry/exit gauges and to the history-span endpoint term `H_end`.

## Scope and evidence

Original card: `persistent-boundary`, **scope changed** (see
[TASK.json](TASK.json)). The drawn object (consecutive dirty-connector calls) is
covered by open concurrent PR
https://github.com/CrocSwap/integer-mult-bounds/pull/1739 and the adjacent-call
centre-fanout claim in
https://github.com/CrocSwap/integer-mult-bounds/discussions/1516 (posted
2026-10-14T11:11Z); this package instead keeps the card's method-2 shape — a
lower bound on the compulsory transitions of one proposed typed interface — and
applies it to the idle-axis hosted-residual interface
([research/idle-axis-hosting/PROOF.md](../idle-axis-hosting/PROOF.md)) in the
scalar common-frame transport model of PR 1664's PROOF.md sections 4-5.

Concretely, `verify.py` implements PR 1664's cut lemma `(C-down)`/`(C-up)` and a
crossing feasibility check exactly (rational arithmetic; entry rows are an
identity basis, so row equality covers arbitrary dirty inputs by linearity), and
audits one hosted residual: one invocation residual factor of width `w` hosted
on a block `S'` of an idle family's pending set `S`, moved from the invocation
to the idle child's advance.

**Finding 1 (operator gauges, exact; sufficient hypotheses).** The hosting move
leaves the complete operator unchanged whenever the moved factor is the
advance's own factor on `S'`, no touch of the host occurs strictly between the
residual application and the advance (more generally, every such touch commutes
with the moved factor), and hosted blocks are disjoint (order preserved). These
are the inherited hosting interface's sufficient legality hypotheses, not a
necessary condition for operator equality, and no necessity claim is proved
here for any class. Exact 3x3 counterexample over Q, kept as the regression
control `cancellation-equality-not-rejected` in `verify.py`: `R = I + E01`,
`T = I + E12`, `T^{-1} = I - E12`. Both `T` and `T^{-1}` fail to commute with
`R`, yet moving `R` across the consecutive touches `T, T^{-1}` preserves the
complete operator, `T^{-1} T R = R T^{-1} T = R`. Cancellation routes like this
one are not closed by this receipt. Each dropped hypothesis still has a
smallest counterexample as composed linear maps (3x3 shears): an escaping block
gives a different endpoint, a single out-of-window touch that does not commute
with the moved factor breaks the composition, and the exhibited overlapping
blocks are order-dependent. Those controls show the hypotheses cannot simply be
deleted; they do not establish necessity. The tiny cut examples below
(including the 156 restored-host regions) and the selected no-touch hosting
rule remain valid as they stand.

**Finding 2 (credit binding on the smallest complete instances).** With hosts
restored and the clean scatter `Y' = Y + S X` demanded at height 0 (PR 1664's
section 5.1 contract), the per-cut demand identity

`sum_j need_j = q*rank(S) + sum_alpha |a_alpha - b_alpha| = q*rank(S) + H_end`

holds exactly on **all 156 enumerated tiny regions** (every binary `t x m`
scatter matrix with `m,t <= 2`, `w <= 2`, and host motions `(a,b)` in
`{(1,0),(2,0),(2,1)}`). The smallest double-duty borrow — one host row `d`
descending `1 -> 0` carrying `d + x` while both `y' = y + x` and a restored `d`
are demanded — is refuted at cut 1 by exactly one direction, both by the count
(`D_j = 1 < 2`) and by span feasibility. So a hosted pending factor's
creditable mass is exactly its host's endpoint displacement `H_end`, and never
more: the scatter term `q*rank(S)` cannot be hosted away while hosts are
restored, and each useful pending factor is counted once. This instantiates PR
1664's "show that the claimed hosting credit is `H_end`" affirmatively for the
toy class, with the double-credit loop as the smallest refuted instance.

**Finding 3 (the only free route, and it is a contract change).** At zero extra
mass a host crossing may deliver a hosted direction **only** if the host's own
prescribed endpoint absorbs that direction and no separate target or restoration
demand survives. Dropping PR 1664's clean-scatter and restoration obligations is
exactly such an endpoint-contract change; it must be charged against the data
endpoint (a coordinate cannot be counted unpaid while left unadvanced there).
This is the precise accounting interface between "hosting credit" and "unpaid
coordinate", the quantity the coverage-law line (discussion
https://github.com/CrocSwap/integer-mult-bounds/discussions/1587) manipulates.

A pre-positioned copy of the host dirt below the cut earns no credit (the
restoration direction is already in `W_j^0`), instantiated as a machine check of
PR 1664's section 7 warning.

## What this does not establish

- Finding 1's operator-level hypotheses are sufficient only. A necessity claim
  would have to be restricted to a stated class and proved there; any such
  class must provably exclude cancellation examples such as the `T, T^{-1}`
  control above, which this receipt deliberately leaves open.
- No bank-tile physics: the replaced bank write/clear mass is not modeled; the
  claim "one bank tile of width `w` eliminated" is compared only through the
  credit shape `w*|a-b|` per host row.
- No wrappers, spectators or gauge charts: PR 1664's section 6 warning that
  "useful width" is not generally endpoint displacement (non-nested frames such
  as `span(e_1)` to `span(e_2)`) remains open here.
- No physical or production admission, no selected-word application, no
  selected rank-8/64 calculation, no kappa claim, no supplier/profile change.
  The whole-construction budget and the `a < D/E` diagnostic are not applicable
  to this interface receipt.
- Finite checks on toy regions do not certify the universal written statements
  of PR 1664 or idle-axis hosting.

## Reproduce

From the repository root (stdlib only):

```sh
python3.12 -B research/dirty-host-gauge-binding-seedea2e/verify.py
python3.12 scripts/research_package.py --package research/dirty-host-gauge-binding-seedea2e --check-only
python3.12 scripts/research_package.py --package research/dirty-host-gauge-binding-seedea2e
```

Expected first and last lines: `PASS_DIRTY_HOST_GAUGE_BINDING_BEGIN` and
`PASS_DIRTY_HOST_GAUGE_BINDING`, with the smallest falsifying instances run
first. Source pins are in [SOURCES.json](SOURCES.json); replay commands are in
[VERIFY.json](VERIFY.json).

## Open next questions

Structured versions are in [TASK.json](TASK.json).

1. **Bind the gauges on the pinned selected replay.** Check every hosted slot of
   the selected 480-helper word for `S' subset S`, in-window and pairwise
   disjoint blocks, then re-derive its credited residual count against
   `H_end`. It matters because it turns this toy receipt into a statement about
   the construction. First step: parse the hosted slots in
   `research/community-frontier1094-audit/selected-replay.tar.gz`'s
   `LOCAL-PROGRAMS.json.gz` and the per-stream pending sets. Blocked by: the
   slot/pending-set data definitions and separately claimed centre-phase work in
   https://github.com/CrocSwap/integer-mult-bounds/discussions/1516.
2. **Non-nested frame gauges.** Replace `|a-b|` by the supplied frame metric
   `d(L_A,L_B) = dim A + dim B - 2 dim(A meet B)` and decide the useful-width
   versus endpoint-displacement mismatch PR 1664 section 6 records. First step:
   the smallest toy with `A = span(e_1)`, `B = span(e_2)` (transition rank 2,
   equal heights). Blocked by: a concrete inherited wrapper/chart convention.
3. **Can a legal data endpoint actually absorb a hosted direction?** Finding 3
   says absorption is the only free route; whether any endpoint contract admits
   it without leaving a coordinate unadvanced is the coverage question. First
   step: test the plane-port endpoint's two unpaid coordinates (discussion
   https://github.com/CrocSwap/integer-mult-bounds/discussions/1587) for exactly
   this absorption. Blocked by: the open plane-port decoder contract.

## Credit

Prepared by **Aaron Wang**, with help from opencode. Substantial AI assistance is
disclosed in [TASK.json](TASK.json). New work is Apache-2.0.

Predecessors (read, not modified): Andrey Mas / an664's PR
https://github.com/CrocSwap/integer-mult-bounds/pull/1664
(`research/dirty-host-cutrank-audit/`, including its GPT-6 Pro review) and the
handoff https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18916098;
ctoh's dirty-host implication and branching-tree bound in
https://github.com/CrocSwap/integer-mult-bounds/discussions/1516; DaysSky's
`research/idle-axis-hosting`; and the lineage recorded in PR 1664's SOURCES.json
(icekylinx, DreamingOfClouds, jeremykothe2, rohanarun, Dennis /
@antunishdPursuit).
