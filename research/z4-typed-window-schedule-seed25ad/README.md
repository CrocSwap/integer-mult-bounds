# The ERASE-deferral window question of the fused z4 typed-echo pair

**KB1b: a legal realization of the pair exists; the ERASE deferral is not
necessary for any whole-construction saving.** PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2464 priced the fused z4
typed-echo pair (112 primitives / 232 reads / 16,080 travel row steps saved
per fused pair) and stopped on exactly one obligation: the fused pair defers
the first wrapper's ERASE across the second call's window (its exact k=2
witness: 24 dirty work rows at block-2 entry), while the pinned contract
(`research/split-centres-global/proofs/PR386-BIT-GEOMETRY.txt`, "COPY/ERASE
windows remain sequential and immutable") delivers totals per call. This
package constructs, at the smallest falsifying instance (the k=2 pair, all 56
basis columns = every dirty state), schedules of the same pair with **per-call
sequential immutable windows and per-call totals delivery** that keep a
positive saving under the full priced budget: **384 records per pair on the
pinned literal window reading and 304 with one bounded, priced typed-window
extension, against the priced 608-record baseline**. The deferral is not the
saving vehicle: at equal window width it buys 0 records at k=2 typed (128
descriptor bits of call-record bookkeeping) and is 32 records *worse* at k=2
literal.

Agent: **Aaron Wang**, with help from opencode (substantial AI assistance; no
independent human review). Task card: [TASK.json](TASK.json) (card
`centre-path-sharing`, scope changed to the assigned kappa-blocker KB1b
request; see the recorded reason). Claim:
[discussion comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18951711).

## What is actually at stake

The typed echo composes children `C_i(D,W) = (D + R_i W, P W)` with the
order-four intertwiner `R_i P = Q R_i`; a complete root echo maps
`(D, X, W) -> (D + sum R_i X, X, W)` for arbitrary dirty `D`, `X`, `W`. The
wrapper copies the source into the work rows (`W += X`, the COPY window) and
removes it after the body (`W -= X`, the ERASE window). PR 2464's fusion wraps
both calls of a pair in one window, deferring the first call's ERASE past the
second call's window; the pinned contract keeps one window per call,
sequential and immutable, with the call's totals delivered at its end.

The question is not whether the *word* is legal — the joint word is an exact
map (reproduced here). The question is whether any schedule that keeps the
contract can keep a saving. This package answers yes, and then shows that the
fusion's own saving decomposes into artifacts.

## Schedules of the k=2 pair (smallest falsifying instance)

Declared family: words over the pinned PR #1391 alphabet built from the
certified child words, per-octet work-frame words `P^u`, and window COPY/ERASE
records (one independent source row per work row); each call region is a
sandwich `COPY + body + ERASE + literal inverse(body)`. Two sandwiches =
per-call windows (legal); one sandwich spanning both calls = the ERASE
deferral (PR 2464's fusion). Every schedule below is checked as an exact
integer map on all 56 basis columns with its literal inverse, and the legal
ones additionally check that the state at call a's region end equals call a's
complete echo map exactly (per-call totals delivery, temporary restored).

| schedule | windows | primitives | reads | travel (row steps) | descriptor bits | storage |
|---|---|---:|---:|---:|---:|---:|
| PR 2464 two separate calls (priced baseline) | per-call, 24 rows | 608 | 1,168 | 53,024 | 9,984 | 4,088 |
| PR 2464 fused pair (the deferral) | one window, 24 rows | 496 | 936 | 36,944 | 8,064 | 4,088 |
| **legal, literal windows** | per-call, 8 rows | **384** | 736 | 32,512 | 6,400 | 4,088 |
| **legal, typed windows (extension)** | per-call, 8 rows | **304** | 584 | 26,128 | 5,120 | 4,088 |
| deferral, typed windows (equal width) | one window, 16 rows | 304 | 584 | 26,128 | 4,992 | 4,088 |
| deferral, literal windows (equal width) | one window, 16 rows | 416 | 792 | 35,488 | 6,784 | 4,088 |

Saving of the legal schedules against the priced 608-record baseline (the
full priced budget of PR 2464's declared tape model, one machine for all
schedules): **224 primitives / 432 reads / 20,512 travel row steps / 3,584
descriptor bits** (literal windows), **304 / 584 / 26,896 / 4,864** (typed
windows); storage is unchanged in every schedule. This is a positive saving
on every charged quantity of the whole-construction budget with the contract
intact.

Three ingredients, each exact:

1. **Window row selection.** The k=2 calls read disjoint work octets (call a
   reads octet 0, call b octet 1), so each call's window only needs its own 8
   rows. The 24-row wrapper copies two octets of source rows that a one-block
   call never reads. PR 2464's 48-record "wrapper fusion saving" is exactly
   this over-copy on both sides; at equal window width it vanishes.
2. **Typed windows (the one bounded contract extension, priced).** The ERASE
   need only remove the copied content *as the typed frame carries it*: at
   the call's end the work rows hold `P^s`-rotated content, and the ERASE's
   source rows are relabelled by `P^s` (a signed/permuted source list; `P` is
   an unsigned permutation, so the records are ordinary ADDs). This absorbs
   the boundary frame restoration entirely. Cost of the extension: **0 extra
   records, 0 extra descriptor bits**; the literal fallback (frame restored
   before a row-aligned ERASE) costs **+80 records per k=2 pair** in
   frame-restoration words.
3. **Per-call sandwiches.** Each call is `COPY + body + ERASE +
   inverse(body)`, so its totals are final in `D` and its temporary is
   restored at its own region end — the contract's per-call delivery, checked
   exactly.

**Witness at block-2 entry** (call b's entry state), both PR 2464's dirty-row
measure and the X-carrying-row measure (work rows carrying un-erased source
content):

| schedule | X-carrying rows | dirty rows |
|---|---:|---:|
| PR 2464 fused pair | 24 | 24 |
| deferral, typed/literal (row-minimal window) | 16 | 24 |
| legal per-call (typed and literal) | **0** | **0** |

The named "24 dirty work rows" witness is a window-width artifact: with
per-call windows the first call's ERASE has run and the temporary is restored
*before* the second call opens, so nothing is deferred.

## What the deferral actually buys

At equal window width and equal alphabet, the residual fusion saving is:

- **k=2 typed: 0 records** (128 descriptor bits: one 128-bit call record for
  the fused call instead of two). The calls' windows are on disjoint octets;
  the deferral shares nothing.
- **k=2 literal: −32 records** (the deferral is *more* expensive; see
  RESULT.json).
- **k=5+5 persistent pair (the bounded pivot), typed windows: exactly
  `2d = 48` window records** per pair, where `d = 24`: the two calls' windows
  share all three work octets, so per-call windows must erase and re-copy the
  same 24 source rows at the call boundary while one window pays them once.
  This matches a scoped record lower bound: inside the X-reading window
  family (one independent source row installed per work row), each call pays
  at least `2d` window records, so per-call windows pay at least `4d` per
  pair and a single window at least `2d`; the gap `2d = 48` is exactly the
  measured window-record residual. The **net** k=5+5 saving is reader-family
  dependent: `+48` records for phase-indexed readers (1,456 separate against
  1,408 fused) and `-56` records for fixed readers (1,616 separate against
  1,672 fused), because the fused fixed-reader body pays 264 per-octet
  frame-word records against the two separate calls' 160, a 104-record
  fusion penalty that more than absorbs the 48 shared-window records. The 48
  window records are the one fusion saving that needs the deferral (or an
  ownership-transfer rule), and they are the exact content of the demotion.

Pivot prices (k=5+5 persistent pair, same priced model):

| schedule | primitives | reads | travel | descriptor bits |
|---|---:|---:|---:|---:|
| PR 2464 two separate calls (priced baseline) | 2,016 | 3,856 | 150,688 | 32,512 |
| PR 2464 fused pair (the deferral) | 1,904 | 3,624 | 134,608 | 30,592 |
| legal per-call, typed windows, fixed readers | 1,616 | 3,096 | 139,888 | 26,112 |
| legal per-call, typed windows, phase-indexed readers | 1,456 | 2,792 | 127,120 | 23,552 |
| legal per-call, literal windows | 1,984 | 3,776 | 173,632 | 32,000 |
| deferral, typed, phase-indexed readers | 1,408 | 2,696 | 122,944 | 22,656 |

The phase-indexed reader family is `research/z4-distinct-source-seed55`'s
declared child-contract change (`C_(i,t)(D,W) = (D + Q^(-t) R_i W, P W)`); the
fixed-reader rows use only PR #1391's certified children plus per-octet frame
words, with the exact per-octet gap programs recorded in RESULT.json. The
deferral's 48-record window residual is the same `2d` window row-sharing in
both families; the net saving follows the reader family (`+48` phase-indexed,
`-56` fixed).

## The 144-primitive saving decomposes too

`research/z4-distinct-source-seed55` (Cinna Davis) composes two five-child
calls on distinct source banks and reports 1,696 separate vs 1,552 joint,
saving 144. Recomputing its published boundary recurrence exactly gives
`g(5) = 60`, `g(10) = 48`, and the saving is `2 g(5) - g(10) = 72` per
direction, `x2 = 144`: pure **boundary endpoint restoration**, not window
lifetime (its handoff already closes and reopens the windows at the
boundary). With typed windows both sides reach 1,456 and the saving is 0. So
the 144 needs neither the deferral nor fusion; it is the same endpoint
freedom the typed windows give both sides for free.

## Hosted ledgers and `a < D/E`

The legal realization keeps per-call windows, hence one centre path per call:
the hosted ledger keeps `n_8 = 1,152`, i.e. the selected histogram, and the
moment is the selected one. Exact rational enclosures (independent atanh/
Taylor engine, no import of the retained pricing engines), host `m = 73`,
`W = 14,336`, `N = 144`:

| ledger | D | `a < D/E` |
|---|---:|---:|
| selected baseline (the admitted realization) | 5,120 | 0.0016805907097543218 |
| shared ledger (widened-window variant) | 9,728 | 0.003203836729943888 |

The baseline `D/E` matches the published
0.001680590709754321699421 to its printing precision (control), and a control
enforces that `D/E` is only a screen (the exact moment at `D/E` exceeds 1
strictly). The saving that survives is scalar, so the demotion "scalar-only"
is **exact for the moment ledger and only for it**: moving `n_8` (the shared
ledger, and the +3.4536% bit-limited figure of
`research/centre-sharing-overhead-budget`) still requires the widened-window
/ common-sink contract change — consistent with
https://github.com/CrocSwap/integer-mult-bounds/pull/2500's finding that the
typed contract alone does not imply fewer recursive children.

## Scope, limits, and what is not claimed

The minimality statements are scoped: the gap programs are exact optima
inside the declared family (per-octet frame words, fixed or phase-indexed
certified children, sandwich windows); the window lower bound is scoped to
X-reading window records. This is not a lower bound for arbitrary ADD/NEG
programs, not a host admission, not a native or hosted emission, not an
all-size/compiler or analytic result, and not a multiplication theorem. The
prefix row-L1 peaks (precision proxy) are 4 for the legal k=2 schedules vs 10
for PR 2464's fused word, and 16/21 for the pivot's separate/joint
phase-indexed words; the carry's precision envelope is
https://github.com/CrocSwap/integer-mult-bounds/pull/2502's object, not
settled here. The selected record is unchanged; no kappa claim.

## Reproduce

Python 3.12+ standard library and `git`, from the repository root:

```sh
python3 -B research/z4-typed-window-schedule-seed25ad/verify.py
python3 scripts/research_package.py --package research/z4-typed-window-schedule-seed25ad --check-only
```

Expected final line:

```text
PASS_Z4_TYPED_WINDOW_SCHEDULE kb1b legal_literal=384 legal_typed=304 baseline=608 joint=496 witness_x=24_deferred_vs_0_legal pivot_residual=48 controls=73 no_new_kappa
```

`--write` regenerates [RESULT.json](RESULT.json); the default run recomputes
and rejects drift. The engine re-checks the pinned PR #1391 emitter and
certificate hashes before importing the word emitter; all other arithmetic
(window content maps, schedules, gap programs, invoices, tape prices, ledger
enclosures) is implemented independently in this package. 73 controls cover
the pinned invoice reproductions (608/496/1008/2016/1904), the intertwiner
identities, every schedule's exact map and literal inverse, per-call delivery
at the boundary, the 24/16/0 witness rows, four window mutants (wrong
relabeling, wrong frame power, omitted ERASE, deferral breaking per-call
delivery), the priced savings and residuals, the pivot gap programs and
prices, the `2d` window lower bound, the seed55 recurrence and its 144
decomposition, both coverage identities, the published `D/E`, the
`D/E`-is-not-acceptance control, and storage invariance.

## Open next questions

- **Does any named selected supplier admit typed (frame-relabelled) COPY/ERASE
  windows, and at what charge?** This settles the scalar side: typed windows
  remove every boundary frame restoration from the typed echo and make
  per-call windows as cheap as the deferring fusion at k=2. First step:
  inspect one retained supplier's window definition for whether window source
  rows may be scheduled in the typed frame, and price the relabeling
  (records, descriptor bits, live families). Blocked by the same named gap as
  PR 2464's: no named host child exposes the order-four intertwiner
  `R P = Q R`.
- **When two calls' windows share rows (the persistent pair), can the forced
  erase-and-re-copy of identical content transfer between sequential windows
  at zero record cost?** That `2d`-per-pair item is the only fusion saving
  left once windows are typed; it is exactly what the ERASE deferral buys.
  First step: ask the contract owner whether a temporary's erased-and-recopied
  content may pass between sequential windows, and price the alternative (48
  window records per pair at `d = 24`) against the widened window's extra live
  families. Blocked by the pinned sentence ("windows remain sequential and
  immutable"; each call's temporary erased within that call).

## Credit and scope

Mechanism and certified child family: **PR #1391** and **PR #1410** (Cinna
Davis with OpenAI Codex assistance), extending Ross Richardson's PR #1287 and
Sagar Thakrar's PR #1227; the phase-indexed reader family and the distinct-
source composition are `research/z4-distinct-source-seed55` (Cinna Davis).
The priced whole-construction model, the shared-centre ledgers, the `a < D/E`
diagnostic framing and the named obstruction are **PR #2464**'s (this task's
direct predecessor). The sharp overhead budgets are
`research/centre-sharing-overhead-budget` (rtyu193-rgb); the moment enclosure
technique and the published `D/E` are `research/selected-suppliers-de-diagnostic`
(Navinor) and the pricing model is Douglas Colkitt's
`research/complex-local-word-ceiling`; the immutable-window sentence is the
bit-geometry artifact `PR386-BIT-GEOMETRY.txt` in
[PR 386](https://github.com/CrocSwap/integer-mult-bounds/pull/386) by Zhihao Chen
(jacklightChen, with OpenAI Codex assistance), whose local E8 bit word is Dylan
Crow's from [PR 370](https://github.com/CrocSwap/integer-mult-bounds/pull/370)
(with Anthropic Claude assistance), pinned in
`research/split-centres-global`. Adjacent same-day work is distinguished, not
overlapped: PR #2500 (typed contract vs recursive children), PR #2491 and PR
#2543 (unitary paired cycles for the full dirty reader), PR #2502 (carry
error envelopes).

New package material is Apache-2.0. Prepared by **Aaron Wang** with help from
opencode (substantial AI assistance in derivation, implementation, checking
and prose); no independent human review or proof-assistant formalization is
claimed. The selected record, upstream files and predecessor packages are
unchanged.
