# Simultaneous k8 helper gauges save 13,000 scalar primitives

**Finite scalar construction; no new kappa.** A simultaneous diagonal gauge on
218 of the 237 eligible helpers reduces the selected-at-base PR1094 k8 scalar
word by **13,000 primitives per complex invocation in each orientation**.
The paid recursive events are identical. This extends the one-coordinate
construction of @woklerx [PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161)
and the at-most-two-coordinate construction of Hanson Sun / @bbMisk
[PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214).
It is a local finite supplier candidate; native and complete hosted admission
remain open.

| Item | Forward | Backward |
|---|---:|---:|
| Original complex scalar primitives | 149,002 | 149,018 |
| New complex scalar primitives | 136,002 | 136,018 |
| Saving, including boundary work | 13,000 | 13,000 |
| Changed helper coordinates | 218 | 218 |
| Added boundary primitives, real component | 630 | 630 |
| Positive primitive-prefix ceiling, bits | 52 | 68 |
| Dyadic denominator depth, original → candidate | 22 → 24 | 26 → 26 |
| Retained local charged bits | 192 | 192 |
| Saving under the older Horner lowering | 7,504 | 7,504 |

The gauges in [GAUGES.json](GAUGES.json) are 1/2 or 1/4 forward and their inverses
backward. All original SCALEs, ADD operands and order, source access, COPYs,
clears, frames, residual wrappers and recursive events remain as given. There
are 436 added boundary SCALE macros, priced as 630 real primitives (1,260 complex
primitives); the interior saving is 14,260 complex primitives. No new helper,
frame change or recursive child is introduced. Sagar Thakrar's PR696 copy-init
lowerer charges coefficient workspace initialization and clearing, including
its unit-coefficient shortcut. This complete price is used throughout.

The exact base is `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. The accepted
conditional kappa at that base is `0.001672660197076918`; this contribution does
not change it. [SOURCES.json](SOURCES.json) records repository input hashes and
Git blobs; [PREDECESSORS.json](PREDECESSORS.json) records the exact external
heads and vendored source bytes. The archived PR1042 provider is authenticated
against the actual PR1094 provider before use.

## Why the transformation is exact

For each eligible helper h, let D multiply its entire register by 2^k_h. The
eligible set is exactly PR1214's cold-entry/FULL-exit, unwrapped, non-center
helpers with no incident COPY or clear. For an ADD `t += q*s`, use
`q' = q * 2^(k_t-k_s)`, taking k=0 off the eligible helpers. Each old SCALE
commutes with D. Other unchanged events act on individual registers or on
unscaled center registers, and hence commute with uniform scalar multiplication
of a helper's coordinates. No COPY/clear is incident with a changed helper.

Insert D after `zero_frame_precondition`, and D^-1 after the full cleanup,
before `done`. For original operators A_1,...,A_m in chronological order:

```text
D^-1 (D A_m D^-1) ... (D A_1 D^-1) D = A_m ... A_1.
```

This identity applies to arbitrary dirty helper inputs. It is not premised on
zero helpers. Both orientations are checked as separate literal words: forward
adds X into Y and backward subtracts Y from X, restoring all 480 helpers and
clearing the eight private centers. The reused exact PR1161 symbolic checker
includes **all 712 input columns**, including initial private-center dirt.
The new independent checker reconstructs by rational scale ratios, emits the
actual lowerer's primitive stream, checks six dirty-state fixtures (baseline
and candidate in each), and directly executes the positive primitive-majorant
recurrence. That recurrence agrees exactly with the full scalar invoice.
A separate conservative denominator-depth recurrence on every primitive records
22 to 24 forward and 26 to 26 backward, relative to integral dirty inputs;
this local grid check is not a new global precision admission.
Finite replay is supporting evidence, not a formal proof of multiplication.

## Search and its exact scope

This is a completed bounded search, not a global optimality claim. OS seed
**29** assigned the complex-supplier track under the donor's original mapping.
The three candidates were hosting/packing ceilings (already PR1240), existing
stage-SCALE consolidation (PR1170), and simultaneous gauges beyond PR1214's
explicit two-coordinate cutoff (chosen). The frozen current repository card
is retained as provenance in TASK.json, with the actual scope marked **changed**:
this is a scalar side result, not the card's requested new recursive inventory.

For a dyadic coefficient |q| = p*2^e with p positive odd, define
`f_p(x)=|x|-[p=1 and x=0]`. The joint real-component cost change is

```text
Delta(k) = 2 sum_h |k_h|
           + sum_ADDs (f_p(e+k_target-k_source)-f_p(e)).
```

Shared ADDs are counted **once**. Summing separate single-helper savings does
not price a simultaneous change; a control detects that error on this candidate.
All unchanged operations are also recounted by the complete invoice.

Discovery uses the forward word, four starts (first zero; three initialized
uniformly in {-2,-1,0,1,2} with Python's seeded Random(29)), and at most 50
shuffled coordinate sweeps per start. Each coordinate update minimizes exactly
over its integer breakpoints, with other coordinates fixed, and takes only a
strict cost decrease. The complete records, final assignments and stopping
sweeps are in CERTIFICATE.json. The first scope claim proposed a bounded
exponent box; inspecting the inherited one-coordinate formula allowed a safer
exact all-integer coordinate update at the same tiny runtime. This widens only
one-coordinate minimization, not the global search coverage.

With all other gauges fixed, a coordinate objective is
`2|x| + sum f_p(e' + sign*x)`. Between its integer breakpoints (zero and the
zeros of its ADD coefficients' valuations), the undiscounted part is affine;
unit discounts only lower breakpoint values. Outside the extremes, every
absolute-value term has outward slope, including the boundary charge. Therefore
a minimum over all integers occurs at a tested breakpoint. At termination no
single-coordinate integer change improves the frozen result. A separately
written checker enumerates every integer between the extreme breakpoints plus
one point on each outer tail: **2,036 evaluations per orientation**. This
certifies coordinate stationarity, not joint/global optimality. Backward uses
the negated forward gauges and is independently checked for the same property.

## Verification and limits

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 scripts/research_package.py --package research/k8-many-dyadic-seed29
```

Expected final marker:
`PASS_REGISTERED_RESEARCH_PACKAGE research/k8-many-dyadic-seed29 outcome=completed`.
The registered command runs the complete certificate, independent primitive
check and semantic/package controls. `python3 -I -O -B
research/k8-many-dyadic-seed29/test_package.py` is the direct portable command.
Certificate regeneration is deterministic; `verify.py --write` refuses to
overwrite an existing certificate. No compressed output or compiler cache is
required.

Controls omit entry and inverse scales, undo a changed ADD coefficient, reuse
forward entry scales incorrectly in the backward word, invalidate the allowed
helper interface, corrupt a gauge/receipt/source pin/source file and falsify a
saving. Dirty targets, helpers, centers and coefficient work are included.
A successful relocation check uses a path containing spaces and optimized
Python. Tests use ordinary checks and exceptions; `-O` does not disable them.

The exact recursive profile is unchanged, so the selected moment/kappa does not
improve. No global gauge optimum, composition with PR1170, native C++ replay,
hosting/controller reconstruction, cold selected-supplier replay, precision
reduction, remote CI success or independent human review is asserted. The
all-size/compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape and analytic assumptions remain inherited. The 52/68-bit positive
checks cover this local scalar word, not a revised global precision invoice.

## Open next questions

1. **Admit this word through a native supplier and its complete hosted invoice.**
   This would turn the finite scalar candidate into a checked supplier change.
   First port only the frozen GAUGES.json transformation into the source-bound
   emitter, rerun phase/native and controller controls, and compare all complete
   invoices. The blockers are that this package changes emitted scalar streams
   only and supplies no new native/compiler artifact.
2. **Does a coupled move improve the coordinate-stationary candidate?** Its
   global minimum is unknown. First evaluate exact two-coordinate breakpoint
   moves around this frozen vector, pricing shared ADDs once. A result requires
   fresh endpoints and invoice checks; no broad search is implied here.

## Credit and overlap

Prepared for **Philipp (@mightyOil)** with substantial **GPT-6 Astra / OpenAI
Codex** assistance in research, implementation, verification and writing.
The byte-identical PR1161 loader, transformation theory, source pins, symbolic
replay and invoice are retained with @woklerx's attribution and disclosure in
`vendor/pr1161/`. PR1214 supplies the 237-helper interface and motivates the
multi-coordinate extension; its claimed two-helper optimum is credited, not
reproved or contradicted here. Its exact head is
`26162c56ec9c50a80e49949f36d4dd9a137a76a6`; PR1161 is
`d210969d3158a1e6c505e41f67dd84e555c88564`.

Credit Sagar Thakrar's lowerer, icekylinx's scalar vocabulary, Jeremy Kothe's
k8/T16 supplier and leaver lineage, Rohan Arun's PR1094 packing, and Douglas
Colkitt's source-bound integration review. Retained notices name their further
predecessors. New work is Apache-2.0. No literature-priority claim is made.

The initial live scan read 853 open PR bodies and current discussions, including
PR1161/1214, stage consolidation PR1170, and the fixed-word ceiling PR1240.
[Discussion1258](https://github.com/CrocSwap/integer-mult-bounds/discussions/1258)
records the narrow claim. There was no pinned sprint issue. Broader old gauges,
coefficient-work batching, factor-source rescalings and the pending X54 mixed
providers have different interfaces; their savings are not silently composed.
The bounded overlap check is not a proof of novelty.

The final refresh covered 854 open PR bodies and 11 discussions. Sagar Thakrar's concurrent
[PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259), head
`10f4aaed33d79f76ebdebc974e201b1baad8b8aa`, changes one helper's gauge between
uses. Here each of 218 helpers has a constant gauge throughout the word; no
phase-varying result or combined saving from PR1259 is used. Its distinct
schedule-class contribution is acknowledged.
