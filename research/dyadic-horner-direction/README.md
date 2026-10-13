# Bidirectional Horner for individual dyadic coefficients

**Finite complex-supplier circuit construction; no new κ.** Building a
fractional coefficient from its low digits can avoid the numerator doublings
followed by denominator halvings in conventional Horner lowering. This package
chooses the cheaper direction separately for each unchanged scalar macro.
It preserves clearing after every addition, including arbitrary incoming work.

The new saving, beyond copy/unit and forward signed-digit lowering, is **928
real primitives per CK orientation, 810 per JP8 orientation, and 312 per SW4
orientation**. SW4 was the #741 selected supplier at the starting base; CK and
JP8 belong to the preserved #626 checkpoint. These are circuit counts, not
runtime measurements. Earlier improvements receive separate columns:

| Program | Original | Copy/unit (#696) | Best forward binary/NAF | Bidirectional | New saving |
|---|---:|---:|---:|---:|---:|
| CK forward | 224,938 | 169,618 | 169,416 | 168,488 | 928 |
| CK backward | 224,986 | 169,634 | 169,432 | 168,504 | 928 |
| JP8 forward | 257,232 | 200,380 | 197,104 | 196,294 | 810 |
| JP8 backward | 257,280 | 200,396 | 197,120 | 196,310 | 810 |
| SW4 forward | 193,162 | 143,658 | 142,536 | 142,224 | 312 |
| SW4 backward | 193,210 | 143,674 | 142,552 | 142,240 | 312 |

The first two reference columns are inherited methods, freshly applied here
to the #741 scalar word as well as the checkpoint words. Forward NAF is the
credited #723/#787 mechanism. This package makes no claim of discovering those
savings. Cross-macro sharing or target/helper basis changes are not composed
into this table.

## Reproduce

Python 3.11+ and the standard library; offline, no writes by default:

```sh
python3 -B -I research/dyadic-horner-direction/verify.py
python3 -B -I research/dyadic-horner-direction/crosscheck.py
python3 -B -I research/dyadic-horner-direction/test_verify.py
```

Expected first two final lines:

```text
PASS_DYADIC_HORNER_DIRECTION programs=6 coefficients=962 extra_saved_per_orientation=928,810,312 controls=14 kappa=unchanged
PASS_INTEGER_HORNER_CROSSCHECK coefficients=962 grid_cases=13286 input_columns=3 costs_and_prefixes=exact
```

The last command runs eight tests. `verify.py --write /new/path.json`
reconstructs the receipt instead of comparing it, and refuses an existing
destination. The default command checks every committed proof-relevant field
in [EXPECTED.json](EXPECTED.json), including integer versus floating JSON
representations. [VALIDATION.md](VALIDATION.md) records executed checks.

## Construction and exact cost

Consider `t += q*s`, with distinct target, source and work. Write the nonzero
dyadic as `q = sign * a * 2^e`, with positive odd `a`. Let
`a = sum(d_i * 2^i, i=0..h)`, using binary or non-adjacent signed digits.
Then `d_0` is ±1. Initialize `w = s` by a charged copy. For increasing
`i=1..h`, halve `w`, then add `d_0*d_i*s` when `d_i` is nonzero. After step i,

```text
w = d_0 * (sum(d_j * 2^j, j=0..i)) / 2^i * s.
```

The assertion holds initially since `d_0^2=1`; a halving and the next signed
source addition establish the induction. Scale by `2^(h+e)` using charged
doublings or halvings. Accumulate `sign*d_0*w` into t, then clear w. The
result is exactly `(t+q*s, s, 0)` for arbitrary initial `(t,s,w)`. No other
register is touched. The sign correction is necessary: reverse NAF for 11/8
starts with -1, so its final accumulation subtracts work for a positive q.
Fourteen adverse controls include deleting that correction.

If the expansion has m nonzero digits, the reverse word costs

```text
1 copy + h halvings + (m-1) signed reads
       + |h+e| shifts + 1 target accumulation + 1 clear
  = 2 + h + m + |h+e| real primitives.
```

For a reduced positive numerator A and denominator `2^k`, forward Horner
with expansion height H and weight M costs `2+H+M+k`. For odd A this shows
why reverse processing can help: it substitutes `|H-k|` for k. For example,
3/2 uses `copy; halve; add source; add target; clear`, five primitives rather
than six under forward copy-Horner. Integral even numerators are reduced to
their odd part only for the reverse construction; their extracted exponent
is charged in the final scaling. Unit coefficients keep #696's two-gate
accumulation/clear circuit.

The four candidates are forward binary, forward NAF, reverse binary and
reverse NAF. The first shortest word in that order wins. Consequently this
finite menu cannot raise the scalar primitive count relative to the credited
forward baseline. No shortest-chain or general circuit optimality is claimed.
Every real-component gate is charged; the complex bill is twice that count.
No additional private register, logical helper, frame transition, wrapper or
recursive child is required. All emitted gates retain their macro's frame.

## Evidence and intermediate bounds

[verify.py](verify.py) executes every primitive in all six fixed programs,
using exact sparse rational rows. The #626 words have 716 arbitrary logical
inputs, including 492 dirty helpers. SW4 has 728, including 504 dirty helpers.
Each replay also starts all eight private centres and the coefficient stream
with nine independent arbitrary inputs. Every macro boundary agrees, every
logical endpoint agrees, every helper is restored and every private stream
is erased. The unchanged paid event histograms and original invoices agree
with their pinned SPECs.

The checker independently propagates positive triangle majorants through
every primitive; it does not borrow a receipt for the changed words. The new
forward/backward bounds are 40/62 bits for CK, 64/101 for JP8, and 55/72 for
SW4. All are below the inherited 192-bit local allowance. Exact rational
envelopes, operation histograms and framed stream digests are in the receipt.
Signed cancellation is never used to understate those majorants.

All 962 distinct coefficients receive arbitrary three-column checks for
**every** available candidate, not just the chosen one. Reverse words win on
36 distinct coefficients, appearing in 415 CK, 393 JP8 and 148 SW4 additions
per orientation. Some coefficient sets overlap. The 14 controls cover signs,
initialization, source integrity, halving, erasure, inadmissible coefficients,
aliasing, cost undercharging and an endpoint-neutral prefix excursion.

[crosscheck.py](crosscheck.py) uses dense integer vectors with binary
denominators instead of the primary rational-row interpreter. It derives
NAF height/weight from shifted bits of `3A` and A, independently of the
lowerer's modular digit recurrence, and checks the closed cost formulas.
It agrees on all receipt coefficients and the fixed 13,286-input grid
`q=±n/2^k`, `1<=n<=511`, `0<=k<=12`, including reducible inputs. This is a
completed finite crosscheck, not a universal optimality search. Both
implementations were written by one AI agent, not separate human reviewers.

## Pins, predecessors and scope

Exact base: **7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261**. Selected #741 head:
`e516b1463606840a15f80aac1995d64ce0092e89`. Historical #626 head:
`660de893d27bb7abd1d5b01b1640207528a5c851`, from #622 at
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
[SOURCES.json](SOURCES.json) binds both reviewed records to their manifests,
SPECs and consumed program payloads. SW4 inputs are read directly from the
committed maintainer replay archive without extraction or code execution.
Every consumed gzip member is compared after decompression. The original
archive container hash is retained as provenance; harmless repackaging is
accepted. This does not cold-rebuild the supplier construction chain.

During publication, main advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631` and selected #799 at
κ = 0.001661634653669567. The six programs here retain their #741/#626 scope;
no transport to #799 is claimed. The unchanged #741 record is now archived at
`certificates/checkpoints/frontier741.json`. The verifier accepts either
official location only with the same exact pinned bytes and manifest binding.
Its complete receipt also passes using the actual inputs from refreshed main.

Sagar Thakrar's **#696** copy/unit lowering at
`5a3f983715027c4fd83f50bc9001d4b18463bed1` is vendored verbatim with its notice.
Its Git blob is `a2c2889e5be41a0fc30d4dfa5dfcebb03d6d47f8`. Credit his
**#723** for forward signed digits, Chris Pagolu's **#734** for a bounded
forward-Horner class and **our #787** for the replay/NAF implementation
adapted here (`93ceb65cfbf339d7ca743614d4756a3af1440cd4`).

Sagar's **#751** uses reverse Horner to collect different sources at a shared
target across macros. This contribution reverses the digit direction *within
one coefficient macro* and retains its original clearing boundary. **#739,
#769 and #811** reuse coefficients across reads; **#793/#807/#816** alter
source, helper or target panels. Their savings are not assumed additive.
The submission refresh also inspected Ryan Haines's **#830**, which
transposes #811's cross-macro work into backward JP8 batches; that different
boundary contract and its savings are not combined here.
[CLAIM.json](CLAIM.json) records the inspected heads, three candidates, OS
seed **39**, finite scope and local claim in the absence of a sprint issue.

Credit icekylinx's primitive/emitter lineage, DreamingOfClouds, Jeremy Kothe,
Chafik Boukhalfa, Rohan Arun, eumemic and the retained contributors to #622,
#626 and the #741 chain. Their source and Apache-2.0 notices are retained.
Prepared for **Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance**. No independent human review is claimed.

This contribution does not change the selected κ. Production lowering,
global invoices/admission and any frontier promotion are separate work.
Native geometry, ordered phase/wrapper identities and global ownership are
inherited from the pinned construction; their expensive checks are not rerun
here. Uniform compilation, common-label/mutable-source realization, physical
hosting, recursive interfaces, precision/tape and analytic transfer remain
assumptions. This exact finite scalar replay is not a proof of the complete
multiplication theorem. No selected artifact or `upstream/` file is edited.
