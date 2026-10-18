# Independent source review: JP8 cleanup coefficient fanout

This review concerns only the selected JP8 provider's final FULL-frame cleanup
at base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. It supports a finite
primitive-lowering experiment: retain one coefficient-work value across a
contiguous run of additions with the same source and absolute coefficient.
It does not certify a new supplier, global invoice, or exponent.

## Pinned object and sources

The inspected [canonical word](../community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/CANONICAL-WORD.json.gz)
has compressed SHA-256
`7a3fec1022d3b2b1bd986302a327735ec521d17b043f4a5acb96253a56f6193c`
and decompressed-byte SHA-256
`fb4a8d14ed2a8048698bea6ae16f86163a1aa6c80f2eb622222eee5cdbce9b3b`.
Direct inspection gives `v=112`, `R=492`, and 716 arbitrary data/helper
columns. Its final cleanup contains 9,006 gates: 8,894 additions and 112
scales. Every cleanup gate has frame identifier 1 and touches only registers
whose final frame is 1. The separate 120-gate early cleanup is outside scope.
The inherited [local receipt](../community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/INDEPENDENT-LOCAL-REPLAY.json)
and [primitive receipt](../community-k492-audit/pr626/replay/mixed-global/base/providers/jp8/LOCAL-CHECKS.json)
bind this word and its original local programs.

The primary code inspected is pinned by
[SELECTED-SOURCE.json](../community-k492-audit/SELECTED-SOURCE.json#L1521-L1525):

| Source in `research/complex-k492-owner-repair/code/` | SHA-256 |
| --- | --- |
| `hpe_audit_and_transport.py` | `c9a05ff291016b870b4fc925b317abd9c3a604c73ffc8920dfdbbeb475e20aa3` |
| `hpe_audit_local.py` | `6bd9a1e279c9c9e4f3767d9f82e537b559292906feb2ddab02f380fb6523a810` |
| `hpe_emit_local.py` | `7e4a6fbc38c8228157b6311457d1496bf460291393043932d2c365f004f77805` |
| `invoice_allcold.py` | `141bd2fd58bbfb5b8d0fc8f56f61c45586d5608a5af3487c6b883dd987f998ec` |

## Obligations inherited from the actual checker

1. **Both orientations retain chronological order.** A backward elementary
   addition swaps source and target and negates its coefficient; a scale is
   reciprocated. The emitter does not reverse the gate list. For chronological
   matrices `G1,...,Gk`, the total map is `Gk ... G1`; applying the duals in
   the same order gives `(Gk ... G1)^(-T)`. Run discovery must therefore be
   performed separately after dualization. A forward common-source fanout
   generally becomes a backward common-target accumulation, which is not the
   same optimization. [Emitter, lines 31-39](../complex-k492-owner-repair/code/hpe_emit_local.py#L31-L39).

2. **FULL cleanup has fixed boundaries.** It follows final climbs and exit
   adapters and precedes all post residual wrappers. Only final-frame-1
   registers can occur in it. A block must stop at any phase, climb, adapter,
   wrapper, scale, or mismatching addition; it must not absorb an early-tail
   operation. The independent auditor checks actual frames and wrapper order.
   [Emitter, lines 111-122](../complex-k492-owner-repair/code/hpe_emit_local.py#L111-L122);
   [auditor, lines 35-78](../complex-k492-owner-repair/code/hpe_audit_local.py#L35-L78).

3. **All arbitrary dirt is restored.** The inherited endpoint check retains
   all 716 independent input columns, including every helper, and requires
   private center work to vanish. Its forward target is `T += D`; backward
   is `D -= T`; other live rows are identities. Testing only clean helper
   inputs or final target rows would weaken this obligation.
   [Auditor, lines 101-117](../complex-k492-owner-repair/code/hpe_audit_local.py#L101-L117).

4. **Primitive counts and scratch restoration require a new receipt.** The
   inherited lowering clears and rebuilds coefficient work for every scalar
   addition, and its receipt explicitly claims clearing after every macro.
   Reusing work across a block changes that lowering even when the entire
   scalar event list is unchanged. An unchanged inherited receipt establishes
   the original scalar interface, not the proposed reduced primitive count.
   [Emitter, lines 40-50 and 152-154](../complex-k492-owner-repair/code/hpe_emit_local.py#L40-L50);
   [invoice, lines 95-134](../complex-k492-owner-repair/code/invoice_allcold.py#L95-L134).

## Exact block argument and cost

Write a nonzero reduced dyadic magnitude as `q = a / 2^b`, with positive
integer `a` and nonnegative integer `b`. A permissible block contains, in
original order,

```
x[t_i] += epsilon_i * q * x[s],  i = 1,...,m,
```

where each `epsilon_i` is `+1` or `-1`, every `t_i != s`, and the source,
magnitude, and FULL frame agree. Repeated targets are allowed. The source is
unchanged throughout the block because no target is the source.

Clear the existing private coefficient stream `W`, form `a*x[s]` using the
inherited binary Horner operations, halve it `b` times, perform the `m`
signed accumulations in their original order, and clear `W`. Thus every live
row has exactly the original map for arbitrary input values, and `W` is zero
on exit even if its incoming value was arbitrary. No source access is free:
each `1` bit still incurs its addition from `x[s]`. No extra private stream,
copy, frame change, restoration call, or recursive child is introduced.
This argument uses the same primitive convention as the
[inherited Horner recount](../complex-k492-owner-repair/code/invoice_allcold.py#L101-L122).

Let `H = (bit_length(a)-1) + popcount(a) + b`. Per real component the old
cost is `m*(H+3)` and the shared-preparation cost is `H+m+2`. The exact
saving is `(m-1)*(H+2)`. Complex-register costs count both real components,
as the inherited invoice does. A singleton saves zero. Unit coefficients
can remain excluded from this experiment without affecting the argument.

The inherited prefix bound maintains a nonnegative row envelope `N`, and
includes the coefficient-work peak `a*N[s]` as well as every updated target
envelope. The optimized block uses exactly the same target updates in the
same order. Its source envelope stays fixed, and its sole preparation is
identical to the first original preparation. Retaining `W` introduces no
larger magnitude than that already attained by this first preparation.
Consequently the maximum inherited envelope over the block is unchanged.
This is a maximum-over-prefixes statement, not pointwise equality of scratch
contents at every original macro boundary.
[Auditor, lines 79-99](../complex-k492-owner-repair/code/hpe_audit_local.py#L79-L99);
[invoice, lines 101-123](../complex-k492-owner-repair/code/invoice_allcold.py#L101-L123).

The retained receipts charge 192 payload bits and report 64 forward / 101
backward prefix bits. A new checker should recompute the exact rational
envelopes and compare them to the original records, rather than merely
reuse these reported bit counts.

## Three targeted negative controls

1. **Illegal sharing:** change one member's source, or include an operation
   writing the supposed common source. Block validation must reject the
   change. If validation is deliberately bypassed, independent primitive
   replay against the original macro map must detect stale coefficient work.
2. **Wrong arithmetic:** reverse one signed accumulation or omit one halving
   in a genuine non-unit block. Exact arbitrary-input replay must reject the
   altered live map. This checks the newly shared primitive implementation,
   not only its metadata or a predicted operation count.
3. **Missing restoration:** remove a block's final `clear W`. All live output
   rows can still match, so the checker must separately reject nonzero private
   output. Starting `W` as an independent input column also makes omission of
   its initial clear observable.

Controls should be exercised in each orientation with an eligible block.
If an orientation has no eligible block, report that coverage explicitly.
Changing only a canonical cleanup gate's metadata frame is not a useful
control: the inherited emitter hardcodes frame 1 when emitting cleanup;
changing the actual emitted event frame would be meaningful.
[Emitter, lines 116-120](../complex-k492-owner-repair/code/hpe_emit_local.py#L116-L120).

## Scope and attribution

This is a source review and algebraic lowering argument. A finite replay
of the optimized artifact is not a formal proof of the full multiplication
theorem. The all-size, compiler, hosting, precision, analytic, and global
assembly assumptions remain inherited; no change to them is established.
Existing source attribution is retained in the
[package notice](../complex-k492-owner-repair/NOTICE.md), including icekylinx,
DreamingOfClouds, jeremykothe2, chafreaky, and predecessor research agents.
This review was prepared for @ellipsi2 with substantial OpenAI Codex
assistance. Apache-2.0.

## Implementation review and independent receipt check

A second review inspected `verify.py` and independently reconstructed the
recorded runs directly from the pinned canonical cleanup, without importing
the verifier's grouping or pricing functions. Every recorded forward run and
its closed-form primitive counts matched: **999 runs, 3,022 scalar additions,
and 19,688 saved real-component primitives**. Independent same-order
dualization found **zero eligible backward runs**. These observations
corroborate `EXPECTED.json`; they do not expand its finite scope.

The scoped review identified two useful endpoint-neutral controls for
`a += 3*s; b += 3*s`: a signed scratch excursion reaching `6*abs(s)` before
returning to `3*abs(s)`, and a temporary doubling/restoration of live target
`a`. The current [checker](verify.py) takes absolute scale factors in its
symbolic norm pass and permits clear/scale primitives only on `W`. Independent
reproduction confirms that the exact controls are rejected, respectively,
with `coefficient prefix envelope exceeded` and
`fanout may only clear or scale coefficient work`. All ten arithmetic controls
pass. No unresolved implementation defect was found in this scoped review.

The [README](README.md) matches the reviewed evidence: changed blocks receive
explicit primitive replay; unchanged macros retain exact rational semantics;
the backward orientation has no shared block; production-emitter integration
and global invoice reconstruction remain outside the contribution. A separate
check of the receipt also confirms 36 coefficient magnitudes, run lengths
2 through 13, and a 7.65379% reduction in the full forward primitive count.
