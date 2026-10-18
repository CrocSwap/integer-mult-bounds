# An all-pair-count screen for the current P104 forward and dual

Scoped conditional obstruction. No supplier admission or new kappa.

The pinned PR2458 forward and PR2712 physical dual cannot meet the selected
saving in the paired-chain coverage model below, for **any integer pair count
`p >= 1`**, even with 416 rank units forgiven per dual and the other 102 forward
corrections supplied free. Any finite number of fully paid auxiliary banks
also fails. The selected frontier and predecessor files are unchanged.

This extends Jose Manuel / `jmbarrancoml`'s
[four-pair Discussion calculation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566).
It is not another local fusion or endpoint-rank result. The new step covers
all pair counts with the actual changing width `m=16p+9`, rather than
extrapolating the four-pair width 73.

## Exact contract and evidence

Fix these local positive-child profiles, independently recounted from the
retained transport events using exact binary elimination:

| Rank | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Rank mass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| PR2458 forward F | 1216 | 74 | 86 | 104 | 48 | 42 | 68 | 8 | 3070 |
| PR2712 dual D | 1498 | 60 | 74 | 92 | 58 | 56 | 92 | 8 | 3542 |
| Optimistic dual D* | 1082 | 60 | 74 | 92 | 58 | 56 | 92 | 8 | 3126 |

Exact source heads:

- PR2458, Ross Richardson (`RossRichardson`), `3170afd2fc13a990bfe28f5ab6421bcda4ffd0f6`.
- PR2712, ywz65, `afa5d6649460dcdb93489babd74f0ee9d01a4911`.

`PREDECESSORS.json` binds the retained data and original README notices to
SHA256 and original Git blobs. `SOURCES.json` binds live inputs and historical
assignment provenance. No predecessor Python is imported or executed. The
checker also recounts net endpoint progress as 2312 original plus 702 added
forward units and 3014 dual units. Crediting those units to global coverage
is conditional. Native correctness and complete forward/dual boundaries
remain inherited, not newly verified here. The forward count combines the original PR1972 word retained
by PR1991 with PR2458's two insertion lists; this is an invoice recount, not a
new chronology or native proof.

The conditional consumer has, per replica:

- `p+1` forward calls, `p` dual calls, `m=16p+9` and `W=208p` live data families.
- One unpaid coordinate per live data family.
- At most `C=104*8+104*8+150*9=3014` units of persistent endpoint progress per
  call. We grant that entire amount to every call, including descending paths
  and the discounted dual, without requiring an actual compatible owner map.
- With `B_aux>=0` fully paid auxiliary banks, residual coverage at least
  `I_B=max(0,(m-1)W+m*B_aux-(2p+1)C)`. Without banks write `I=I_0`.
  We grant residual children rank `m`, above the retained halving guard.
- Every other obligation free, including missing forward corrections, scalar
  and monomial work, allocation, movement, precision and restoration overhead.

The template formulas come from Dominik Scholz's retained `larger-gain` model
and the explicitly conditional P104 substitution in
[`p104-terminal-correction-floor`](../p104-terminal-correction-floor/README.md).
This is not a claim that its coverage law, inventory or owner windows have
been realized for these nonmonotone words. A consumer with extra unpaid
coordinates, different coverage, different call multiplicities, shared work
that changes the profiles, or different endpoint progress is outside the
result. Costs cannot simply be removed while retaining endpoint credit from
a different contract.

## Proof

Write `a0=836330098538459/500000000000000000`, the selected kappa. Testing at
this smaller value favors the candidate: the retained transfer requires a
primitive saving strictly larger than kappa, and each child cost is
nondecreasing in the saving.

For `0<q=1-a<1` and integer `0<=delta<=r`,

```
r^q - (r-delta)^q <= delta.
```

Each unit increment of the concave function `r^q` is at most its first
increment, one. Thus deleting 416 H1 children grants at least as much moment
benefit as deleting any 416 integer rank units from one dual's children.
This includes deleting whole children. It does not cover arbitrary circuit
resynthesis, noninteger ranks or more than 416 forgiven units. This discount
argument and the four-pair starting calculation belong to Jose Manuel.

Let `n_r(p)=(p+1)F_r+pD*_r`. The optimistic normalized moment is

```
M_p,B(a) = [sum_r n_r(p)*(r/m)^(1-a) + I_B/m] / (W+B_aux).
```

For `p=1` without banks, clamp the negative residual formula to zero. The
paid mass alone exceeds `mW` by `2*3070+3126-25*208=4066`. With arbitrary
banks, use `I_B >= (m-1)W+m*B_aux-(2p+1)C` directly. It gives paid-plus-idle
mass at least `m*(W+B_aux)+56-40p`, a strict **16-unit** excess at `p=1`.
Since `(r/m)^(1-a)>=r/m`, this rejects every nonnegative saving. The stronger
4066-unit zero-bank margin must not be reused unchanged after adding banks.

For `p>=2`, `I=3328*(p-2)^2+8948*(p-2)+1570>=0`. The zero-bank
paid-plus-idle mass is

```
sum_r n_r(p)*r + I = mW + 56 - 40p.
```

Use `exp(x)>=1+x` to get

```
M_p,0(a0) >= 1 + [56-40p + a0*L_p] / (mW),
L_p = sum_r n_r(p)*r*log(m/r).
```

The executable uses only rational lower bounds for these logarithms. For
`x>=1`, put `t=(x-1)/(x+1)`. Integrating the finite geometric series for
`1/(1-t^2)` gives

```
log(x) >= 2*sum_{j=0}^{127} t^(2j+1)/(2j+1).
```

It rounds this sum down to six decimal places. No floating-point sign decision
or numerical root enters acceptance.

For each of `p=2,3,4,5,6,7`, substituting these bounds makes the excess
numerator strictly greater than **46**. For every `p>=8`, `m>=137`, so use the
single fixed table of lower bounds for `log(137/r)`. It gives

```
56-40p+a0*L_p >= A*p+B,
A > 2/3,  B > 76.
```

The exact certified values are
`A=6793028173440143209107/10000000000000000000000` and
`B=19117566126860375528272583/250000000000000000000000`.
They prove the entire infinite tail, not a sampled large-p range.
Consequently `M_p,0(a0)>1` for every positive integer p, and the same holds
at any required primitive saving `a>=a0` below one.

For `p>=2`, nonnegative `I` gives `I_B=I+m*B_aux`. The same positive
excess numerator is therefore divided by `m*(W+B_aux)`, rather than `mW`.
It remains strictly positive for every finite `B_aux`. The clamped `p=1`
case was handled separately above. Banks receive no unpaid-coordinate
credit; granting that credit changes the contract.

## Reproduce

Standard-library Python 3.12 or later, from the repository root:

```sh
python3 -I -B research/p104-all-pair-consumer-budget/verify.py
python3 -I -O -B research/p104-all-pair-consumer-budget/test_verify.py
python3 scripts/research_package.py --package research/p104-all-pair-consumer-budget
```

Expected marker: `PASS_P104_ALL_PAIR_CONSUMER_BUDGET all_p>=1 finite=6 tail_from=8 no_new_kappa`.
The normal verifier is read-only and compares its complete recomputed receipt
with `RESULT.json`. Only explicit `--write` replaces that receipt.
Tests exercise the credited p=4 profile as a positive fixture, lower-saving
non-rejection, wrong mass/rank/nesting, duplicate JSON keys, source and receipt
corruption, optimized Git-free replay and equivalent gzip recompression.
A separate set-span census checks all 3584 transport occurrences without
using the primary elimination routine.

Local validation passes on CPython 3.12.15 through the registered hook and
CPython 3.13.5 with optimized execution. All 11 package tests pass. The 70
research-workflow tests pass with two skips. Ruff `E,F,I,UP,B` diagnostics
pass. No hosted-CI or independent human review is claimed.

## Expansion decision and limitations

Pause extensions that only change pair count, repack idle coverage or add
fully paid banks to these exact profiles under this exact consumer. Local
native and fusion contributions remain useful. Reopen with a source-bound
changed profile or consumer and a new complete coverage/cost ledger.

This does not bound every P104 decoder, interleaved correction, changed
producer/consumer or multiplication algorithm. No native cold replay,
all-size proof, physical owner/routing construction, precision/tape admission,
selected-supplier replay or formal-kernel check is claimed.

Python allocates managed integers and fractions during this bounded check.
JSON payloads are capped at 2 MB; each word has at most 6000 events, each frame
uses at most 18 nine-bit vectors, and each logarithm uses exactly 128 terms.
The all-p proof uses six base cases and one tail, not an unbounded loop.
Source JSON contains varying event shapes, so its parsed representation is
dynamic; rank/frame and source bindings validate the proof-relevant boundary.

## Open next questions

Can a changed P104 consumer provide enough additional unpaid-coordinate or
endpoint-progress credit without repaying it in restoration? First write its
actual boundary and replace `I` above with a justified coverage law. The
blocker is a compatible physical consumer, not another optimizer seed.

Can a changed complete local profile escape this screen? First recount both
directions, including all missing corrections, then replace F and D in the
same optimistic screen. The current words correct only two forward rows;
finishing the other rows at unchanged cost was merely a favorable assumption.

## Credit

Jose Manuel / `jmbarrancoml` supplied the p=4 screen and 416-unit discount
argument in Discussion2619. ywz65 supplied PR2458's native binding, PR2497 and
PR2586's physical-dual lineage, and PR2712's retiming. commdata2338 supplied
PR2662's endpoint fusion; Nick Petalas supplied PR2550's complementary-frame
method. Ross Richardson / PR2445 supplied the two-target correction.

Retain Chafik Boukhalfa / PR1991, Rohan Arun / PR1972, Adam Gall / PR1940,
Josie Elliston / PR1071, Ali Romman / PR1125 and PR1862, icekylinx and the
retained geometry/compiler lineage. Dominik Scholz supplied the larger-gain
stage template; Sagar Thakrar / PR1012 supplied the coverage context; Douglas
Colkitt supplied the selected-word ceiling context. Original notices remain
in the retained predecessor READMEs. The selected construction's complete
attribution remains in its selected review.

New all-p theorem, checker and tests by Nick Petalas. Apache-2.0.
