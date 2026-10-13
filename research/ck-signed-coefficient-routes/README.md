# Signed coefficient reuse in the historical CK circuit

**Finite complex-supplier circuit construction, with exact bounded-class
verification. No new kappa.**

Allowing a subtracted source read between dyadic shifts saves **926 additional
real-component primitives in the forward CK program**, compared with positive
source reads on the same runs using the accepted PR696 copy-initialized reset.
There are 202 strictly improved transitions, all in full-frame cleanup.
**There is no additional backward saving under that stronger comparator.**

**Not admissible as-is.** The fused runs keep private work `W` live across
several target updates, whereas the inherited macro contract clears `W` after
every addition. The native frame/wrapper checker was not rerun, so the
physical layout has not been shown to tolerate the longer live range. The
forward program also needs one more fractional bit (4 versus 3); see
"Precision". This is a mechanism note for a superseded provider, not a
frontier or kappa contribution.

The object is the historical PR626/PR622 CK provider, not the current selected
PR799 X4 construction. Exact base:
`f567884aeb8851b6e794af1184119a3bfbe1e631`. At that base the accepted conditional
value is `1661634653669567/1000000000000000000`. This package does not change it.

## Reproduce

Python 3.10 or newer, standard library, offline, no writes:

```sh
python3 -I -B research/ck-signed-coefficient-routes/verify.py
```

Expected:

```text
PASS_CK_SIGNED_ROUTES orientations=2 columns=725 extra_saved=926,0 pairs=496 cases=1080288 controls=15 kappa=unchanged
```

The command executes both the Fraction-based full-column verifier and the
separate integer-only exhaustive checker. Portable-package tests:

```sh
python3 -I -B research/ck-signed-coefficient-routes/test_package.py
```

## Complete local scalar counts

Every entry counts both real components of the complete complex scalar program.
All preparatory source reads, shifts, target accumulations and final clears are
included. These are instruction counts, not runtime measurements.

| Lowering on the fixed macro/event stream | Forward | Backward |
|---|---:|---:|
| Original PR626 binary Horner | 224,938 | 224,986 |
| Accepted PR696 copy/unit lowering alone | 169,618 | 169,634 |
| Same-domain copy reset or power-only reuse | 147,856 | 113,930 |
| Same-domain copy reset or power/positive-read reuse | 146,332 | 113,018 |
| This signed-read construction | **145,406** | **113,018** |
| Increment from allowing subtraction | **926** | **0** |

Only the last difference is attributed to the new signed-read mechanism.
Other savings include predecessor copy initialization and work sharing, plus
this package's wider contiguous-run grouping. Comparator rows are separately
implemented on this domain, not claimed reproductions of PR769's differently
restricted runs or PR811's JP8 totals. No globally best CK cost or additive
saving with other pending work is claimed.

An initial screen used original clear-plus-leading-add resets and found extra
savings of 1,308 / 456. Copy-initialized reset, already accepted through PR696,
eliminates the backward increment and reduces the forward increment to 926.
All final code and certificates use this stronger reset.

## Construction and scoped proof

A macro has map `T <- T + q*S`, with private coefficient register `W`.
PR696 initializes `W <- S` by a paid copy, then uses binary Horner to prepare
`abs(q)*S`. Unit coefficients use a direct signed target update plus work clear.
Both accept arbitrary private input dirt.

Partition each literal event stream into maximal runs of consecutive nonunit
addition macros with exactly the same source and frame. Every intervening
non-scalar event, frame/source change or unit coefficient is a barrier. Each
target differs from the source. The source is therefore invariant throughout
the run, even if targets repeat. Copy-prepare the first coefficient. Each later
step begins with `W=a*S` and selects the cheapest of:

1. Copy-initialized binary-Horner reset to `b*S`, fully charged.
2. A power-only transition when `b/a=2^e`, at cost `abs(e)`.
3. `W <- 2^u*W; W <- W + epsilon*S; W <- 2^v*W`, where
   `b=2^v(2^u*a+epsilon)`, `epsilon` is -1 or +1, and `u,v` are in [-16,16].

The third cost is exactly `abs(u)+1+abs(v)`: each shift is a paid doubling or
halving, and the middle instruction is a paid source access and addition or
subtraction. Perform the original signed target update, then clear `W` at the
run end. No source is modified and no extra scratch, helper or child is added.

For `a=3/2, b=1/2`, `W <- W-S` costs one primitive, versus the two-instruction
copy reset `W <- S; W <- W/2`. The target accumulation and final clear are still
paid. Such a transition saves two real-component primitives.

Induction proves the original target values: the source stays fixed, every
transition ends at `W=b*S`, and target/sign order is retained. At a run boundary
the complete map agrees and `W=0`, for arbitrary original and private inputs.
Untouched events therefore compose with the changed runs. This is a linear
circuit identity over the rationals (separately over real and imaginary
components), not a sampled-input observation.

The constructor checks every `u` and sign and solves exactly for `v`; the
second, integer-only checker enumerates both exponents using integer shifts to clear
denominators. The 496 distinct ordered pairs produce **1,080,288** one-read
cases. Reset and all applicable power-only transitions are also checked. The
route table is complete, with lexicographic tie breaking. Minimum costs compose
within each fixed run because every route has the same prescribed coefficient
boundary. This is not unrestricted optimality: multiple reads, alternative
single-macro lowerings (including PR837), reordering, extra scratch and other
suppliers are excluded.

## Precision

The prefix envelope bounds only the high end. Signed routes can also halve odd
intermediates, e.g. 23/2 -> 15 passes through a work value with denominator 8.
The verifier now replays exact rows for both the original and the signed
lowering and records the deepest power-of-two denominator reached:

| | Original | Signed |
|---|---:|---:|
| Forward max fraction bits | 3 | **4** |
| Backward max fraction bits | 8 | 8 |

Eight forward work steps exceed the original depth. The second checker
recomputes the work-coefficient depth from the route table and agrees (4 / 2
for work only). No inherited fixed-point or rounding bound is checked here;
whether one extra low bit is free under the precision interface is open.

## Coverage, prefix and accounting

Forward: 957 runs / 5,053 additions (869 cleanup, 11 A, 69 B, 8 center runs).
Backward: 160 runs / 8,550 additions, all in zero-frame preconditioning.
All 27,256 events in each orientation are retained. The stopping rule is full
coverage of this domain; no conclusion about excluded classes is inferred.

The primitive replay checks all **716 logical plus nine arbitrary private
input columns**, restores 492 dirty helpers, clears eight private centers and
coefficient work, and compares each changed block with direct macro semantics.
Non-scalar events and paid child histograms are unchanged. The private-work
clearing boundary extends to the run boundary; it is **not** after every old
scalar macro. No child, wrapper or frame event lies inside a fused run.

Prefix growth is recomputed. Literal triangle envelopes treat subtraction as
addition and do not exploit work/source cancellation. Exact maxima and bit
counts are recorded in EXPECTED.json. The forward bound rises **40 -> 43 bits**
and the backward bound **62 -> 63 bits**; both remain strictly below the
inherited `2^192` allowance. The second, integer-only checker reconstructs all
primitives and positive envelopes, agreeing on complete digests and counts.

The inherited adapter/compiler reserve is **11,058,400,870,400**. Keeping that
reserve and all original frame/wrapper/helper/child charges gives a conditional
arithmetic substitution budget of **11,058,401,015,806**, versus
**11,058,401,095,386**, saving 79,580. This uses the orientation maximum, not the
sum. It includes predecessor savings and is **not** a refreshed global invoice
or admission of the new private-work interface. Recursive profiles are unchanged.

Fifteen controls, each required to fail with its stated reason, cover wrong subtraction, omitted initialization, halving,
target updates and clearing, illegal boundaries, aliases, underpricing and
endpoint-neutral excessive prefix growth. Omitting final clearing is also
rejected separately in all 1,117 actual runs. Package tests cover source,
circuit, certificate and invoice corruption, plus relocated optimized replay
and equivalent gzip recompression.

## Provenance and remaining obligations

[SOURCES.json](SOURCES.json) pins source Git objects and payload hashes,
including the preserved PR626 record, CK SPEC/programs, original invoice/emitter
and review. Gzip equality uses decompressed payloads; original Git blobs remain
provenance pins. Source heads: PR626 `660de893d27bb7abd1d5b01b1640207528a5c851`,
PR622 `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.

Credit **Sagar Thakrar / thakrarsagar (PR696)** for copy/unit lowering,
**ellipsi2 (PR722)** for equal-magnitude sharing, **Jeffrey Cox / namredips
(PR739)** for power-only continuation, **24kHandsome1201 (PR769)** for CK
dyadic ladders, and **Ryan Haines (PR811/830)** for positive one-read JP8 routes
and transposition. PR769/811 comparison heads are pinned in SOURCES.json; no
pending implementation is imported. This adds signed source reads on CK, not
priority for coefficient reuse, reset elimination or CK coverage. PR837's
bidirectional Horner and PR807/816's basis changes are distinct and not combined.

The supplier/interface lineage is due to **Jeremy Kothe, Chafik Boukhalfa,
icekylinx, DreamingOfClouds, Rohan Arun, eumemic**, and the predecessors retained
in the pinned original notice/review. Their construction, geometry, hosting,
interface and conditional-theorem credit is preserved.

Production integration of the extended work boundary, refreshed global
admission/invoice, all-size compiler, common-label/mutable-basis realization,
hosting, rounding/precision, tape and analytic transfer remain separate or
inherited obligations. The native frame checker and supplier cold rebuild
were not rerun. This checks the scalar projection and unchanged event stream,
not the complete multiplication theorem, and does not transport counts to X4.
See [VALIDATION.md](VALIDATION.md).

Prepared for **Joseph / AmazedBot (@amazedbot)** with substantial **OpenAI Codex
assistance** in research, implementation, proof analysis, verification and
writing; the precision check and stricter controls were added with
**Anthropic Claude** assistance. Both implementations were written by AI
agents and share one cost model and the same input data, so they guard against
coding slips rather than shared misreadings. No human or delegated-agent review
is claimed. New files are **Apache-2.0**.
