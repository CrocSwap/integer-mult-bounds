# A configuration-relative time/space tradeoff for fast lifting

**Conditional recursive-interface construction.** The fast batched lifting core
can use clean workspace within a logarithmic factor of its input size while
retaining subquadratic dependence on rank. The key is to build its checkpoint
tree from the ratio of runtime to complete configuration size, **T/S**, so the
payload N does not acquire an extra power.

With the same source assumptions as Jose Manuel's PR3109 and the complete-state
space binding in PR3122, `N=2^n`, `n=Theta(r)` and component width `W=Theta(r)`:

| Implementation choice | Time, excluding N | Additional clean space, excluding N |
| --- | --- | --- |
| PR3109 whole history | `r^(1199003/600000)` | `r^(1197203/600000)` |
| PR3122 two-level checkpoint | same time power | `r^(1797203/1200000)` |
| This fixed-height H family | same time power, H-dependent constants | `r^(1+(997/1000)(599/600)/(H+1))` |
| This fixed-radix, variable-height point | `r^(2399003/1200000)` | `r log(r+2)` |

The last row trades some time saving for space: the time power increases from
about **1.998338** to **1.999169**, still below two. Its proof uses the enormous
fixed radix **`2^1200`**, with correspondingly enormous constants and crossover
sizes. It is an asymptotic existence result, not a practical performance claim.
The full formulas retain mutable compilation F; the displayed powers fix the
inherited compiler. No new kappa or selected supplier is claimed.

This is an application of **Bennett's classical multilevel checkpointing**, not
a new reversible-simulation theorem. [PROOF.md](PROOF.md) supplies the complete
source-relative recurrence, an explicit sequential bank layout, copied state,
head/control work, routing, cleanup, short groups and narrow-residue charges.
The exact nonlinear map, literal inverse, four-call consumer and error bound
remain unchanged. Owned work is clean; arbitrary dirty helpers do not acquire
this capacity for free.

## The reusable insight

A unit-step checkpoint tree has depth proportional to log T. Here both T and S
contain the large payload N. Stop subdivision when a leaf's time fits S and the
depth becomes `ceil(log_b(max(1,T/S)))`, independent of a common scaling of T and
S. With `alpha=log_b(2b-1)-1`, the complete bounds are

```
time  = O_b((T+S) max(1,T/S)^alpha log(2+T/S))
space = O_b(S log(2+T/S)).
```

The time logarithm pays a simple router that returns to the checkpoint-bank
origin. It includes entry/cleanup scans as well as computation copies. The
source configuration envelope is essential: substituting S=T would remove the
useful improvement. A runtime bound alone cannot establish this result.

## Executed evidence

[RESULT.json](RESULT.json) contains:

- 3,360 exhaustive source/dirty-target cases, including noninjective overwrites,
  empty intervals, two radices and heights zero through three.
- 32,125 exact integer invoice cases, checking balanced subdivisions, fixed-height
  root selection, relative-height selection, full routing and allocated payload.
- 20 same-input Gaussian controller executions in both orientations, compared
  with the frozen PR3122 two-level controller and an independent stage oracle.
- 24 backend calls inside three unchanged nonlinear forward/inverse macro pairs.
- Controls for missing cleanup at three depths, corrupted history, wrong segment
  offsets, aliasing, unordered projections, invalid plans and omitted scan travel.

The primary finite hierarchy is binary (OS seed 24) and uses configuration-scale
leaves. On the same rank-three, eight-entry, 16-bit Gaussian program, there are
30,464 overwrite gates and 518 configuration-payload bits:

| Executed schedule | Allocated checkpoint/active/history payload | Forward gates | Reported payload work |
| --- | ---: | ---: | ---: |
| Full trace | 30,982 bits | 30,464 | 62,220 |
| PR3122 two-level schedule | 7,952 bits | 57,120 | 163,188 |
| New binary height 5 (curve point) | 4,060 bits | 231,336 | 2,988,696 |
| New binary height 6 (relative plan) | 4,102 bits | 347,004 | 9,767,552 |

The new relative plan uses about **48.4% less payload workspace** than the
predecessor's two-level schedule, with much more recomputation and bank movement.
Height 5 happens to use less payload than height 6 on this finite instance; the
relative rule is an asymptotic bound, not a finite optimum. The receipt includes
the complete curves and separate copy, reverse, zero-scan and routing counts.

These are logical payload and between-slot-distance invoices, not Python RAM,
wall-time measurements or literal physical transition counts. Control headers,
immutable program storage and constant-cost scan/rewind lowering are not included
in the finite payload columns; the written theorem prices them separately.
Both schedules retain the same 518-bit source adapter and 256-bit dirty target.
The small Gaussian circuit is a semantic fixture, not the fast physical C machine.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/lifting-relative-history
```

Expected markers: `PASS_LIFTING_RELATIVE_HISTORY`,
`PASS_LIFTING_RELATIVE_HISTORY_EXPORT_CONTROLS`, and the generic package pass.
Direct `verify.py --emit` prints the deterministic receipt; `--suite controller`,
`plans`, `exponents`, `gaussian`, `macros` or `controls` runs a bounded subset.
The export check replays under `-O` in a read-only Git-free tree and rejects live
source drift, a changed archive, missing input declaration and typed-receipt
corruption. It does not rely on assertions surviving optimization.

Exact base: **`997e6a9ca7b4f95d50e366f61412fd640d72a88a`**.
[SOURCES.json](SOURCES.json) pins all live inputs and the unchanged PR3122 archive
members by SHA256 and Git blob. No source archive is extracted or modified.
Local Python modules and authenticated predecessor bytes are compiled directly.
The generic metadata checker additionally validates provenance through Git;
direct replay needs only this package and the declared inputs.

[TASK.json](TASK.json) records the seed, changed card scope, three candidates,
expansion decision and completed domains. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18988775)
keeps this work separate from the dense-wrapper/collector investigation.

## Open next questions

1. Lower complete-state snapshots and the encoded control stack into the actual
   fast C interpreter. First bind one resumable segment's full state and local
   head layout. The inherited source/compiler refinement needs independent review;
   this prototype does not replace it.
2. Choose a finite resource point for an actual caller, including scratch ownership,
   control bits, source/target banks and recomputation. First compare its complete
   budget across several small radices/heights. Clean-stock production and wrapper/
   collector integration remain open; an asymptotic reserve is not a supplier bill.

## Credit

Prepared by **Tekalign**, with substantial **OpenAI Codex** assistance in
mathematics, implementation, verification and writing; Apache-2.0. No independent
human or formal-kernel review is claimed.

Credit C. H. Bennett's [1973 reversible simulation](https://doi.org/10.1147/rd.176.0525)
and [1989 tradeoff](https://doi.org/10.1137/0218053). Jose Manuel (`jmbarrancoml`)
supplied [PR3109](https://github.com/CrocSwap/integer-mult-bounds/pull/3109), head
`15eac811648182bdac7254a91fd9b841b1414ebc`, and the retained PR2287/2250/2899 source
framework. [PR3122](https://github.com/CrocSwap/integer-mult-bounds/pull/3122), head
`bd06efe0c53280c585d0f3b2f21c52d036f40902`, supplies the complete-configuration
binding, segment simulator and Gaussian fixture; it remains pending independent
review. Its archive retains full predecessor attribution. Credit Ross Richardson's
PR3072 protected evaluator, PR3033/3025, Douglas Colkitt, Nick Petalas, David Arias,
and all contributors/notices in the inherited lineage. Sources, upstream/ and the
selected conditional frontier `0.001672660197076918` are unchanged.
