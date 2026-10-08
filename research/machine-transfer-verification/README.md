# Formal transfer and finite-certificate checkpoint

This package makes the completed research after the first PR64 checkpoint
reviewable and reproducible. It contains exact finite certificates, reusable
Lean proofs, concrete tape primitives and the current proof boundary.
**The full uniform fixed-tape integer multiplication theorem remains unfinished.**

The strongest public finite candidate reproduced in this checkpoint is
[PR76](https://github.com/CrocSwap/integer-mult-bounds/pull/76), pinned at
`4b716171d4b3122d6b9db93f802751a41a209955`, with conditional
`kappa = 51738676045141 / 1000000000000000000 = 5.1738676045141e-5`.
Its supplied words, dirty-basis semantics, exact CRT profiles and assembly
arithmetic passed independent checks. Heuristic compiler regeneration was not
run for PR76. The latest **literal real-characteristic Lean instantiation** is
the earlier PR73 profile, with conditional `kappa = 5.1414646104194e-5`.
PR73's later withdrawal does not change its immutable certificate or theorem.
The PR76 result is not silently substituted into that Lean theorem.

The completed PR69/71 combination experiment has the finite conditional
witness `kappa = 51544825802029 / 1000000000000000000`
(`5.1544825802029e-5`), above PR73 and below PR76. Both changed axes were
compiled and checked, including fresh CRT profiles and complete dirty-basis
replay. Its exact arithmetic is independently recomputed by the offline check;
there is no literal Lean profile instantiation for this experiment.

## Review map

| Package | Completed result | Remaining boundary |
| --- | --- | --- |
| `next-proof/analytic` | Actual real log/exp enclosures and characteristic contraction for PR64 | Supplied finite profile and physical realization |
| `next-proof/framed`, `next-proof/rows` | Typed XOR/gauge semantics and exact row-index bijections | Complete generated trace and physical routing |
| `transfer-proof/recurrence` | Floor-child depth, recurrence and uniform state-cost transfer | Named physical implementation hypotheses |
| `transfer-proof/tapes` | Literal fixed-alphabet stack push/pop, clean scratch and restored heads | Recursive scheduler composition |
| `transfer-proof/framed` | Concrete modular address-gauge algebra | Instantiation with the complete selected tables |
| `full-transfer/outerrows` | All-positive-width row supply, padding below factor two and descriptor absorption | Physical gathering and descriptor routines |
| `full-transfer/localization` | Rational table localization, eligible odd primes, unit pivots and modular transport | Concrete complete tables and setup costs |
| `full-transfer/framed` | Tensor identities and complete ambient finite schedule/profile correspondence | External finite checker, inherited local pivots; no full generated Lean trace |
| `full-transfer/latest-analytic` | Actual PR73 real characteristic and conditional state-cost specialization | Full deterministic multiplier |
| `stream-transfer/counters` | Six-state head-local binary counter; exact first completion, head return and fixed-direction amortized cost | Payload/reset/dispatcher costs and integration into routing |
| `stream-transfer/audit` | PR76 supplied-word/CRT/bridge/arithmetic validation and source pins | Compiler discovery regeneration and literal Lean specialization |
| `stream-transfer/experiments` | Bounded balanced-coarse/split-graph experiment and exact comparisons | No claim to beat PR76 or establish a global optimum |

The counter bound is `4N + 2w` for N primitive calls in a **fixed direction**.
It does not cover arbitrary alternating increments and decrements, or include
the separate costs of payload emission, controller dispatch and counter reset.
Those costs must be included when proving a whole routing routine.

The integrated inventory has 27 unique modules and 298 theorem/lemma audits.
It includes the 13 earlier `DirtyWrapper` declarations and 12 `FramedXor`
helpers beyond the historical selected prints. Duplicate module copies are
checked byte-for-byte and compiled once. These counts describe audit coverage,
not independent new mathematical results. Only standard Lean foundational
axioms are permitted; sources contain no proof escapes or custom axioms.

## Reproduce from the repository root

Python 3.11 or newer, standard library only:

```sh
make machine-transfer-check
```

This validates the publication manifest, binds the PR64/68/73 literal Lean
profiles to their certificates, recomputes exact rational characteristic and
assembly inequalities for those profiles, PR76 and the completed combination,
and repeats the exact
counterexample to universal PR73-over-PR68 power dominance. It does **not**
rerun the Lean kernel, finite words, CRT profiler or compiler discovery.
It is included in `make verify-certificates` and hence `make verify`.

With the repository's existing Lean 4.21.0 and pinned Mathlib project ready:

```sh
make formal-machine-transfer-verify
# An already prepared compatible project can be selected explicitly:
make formal-machine-transfer-verify LAKE_PROJECT=/path/to/pinned/mathlib-project
```

The checker validates toolchain, dependency revision, source hashes and full
declaration coverage, then compiles all unique modules into a fresh temporary
directory and generates a kernel axiom-audit shim for each. It installs nothing
and writes reports under ignored `build/`. It also runs in the existing
historical formal CI job. Mathlib revision:
`308445d7985027f538e281e18df29ca16ede2ba3`.

Full finite replay commands require the exact public source checkouts named in
the individual packages. For example, using a local checkout containing PR76
at its pinned commit and unchanged checked-out files:

```sh
P=research/machine-transfer-verification
python3 -B "$P/stream-transfer/audit/independent_pr76.py" \
  --repo /path/to/pr76-checkout --output build/pr76-independent.json
```

That command replays both entire dirty-state bases, checks literal scatter,
rebuilds the complete paid profile from the supplied axis profiles, and checks
the exact arithmetic. Fresh C++ CRT profiling is a distinct upstream command
documented in `stream-transfer/audit/README.txt`; its saved receipt is included.
The full ambient checks and experimental producer/replay commands have their
own explicit source requirements. Checkers do not fetch or modify tracked
upstream sources; the CRT setup creates an ignored parent archive.

## Provenance and checkpoint handling

`publication-manifest.json` is the authoritative hash inventory for this
publication. Leaf theorem manifests, source pins and scientific receipts are
retained. Old aggregate archive manifests, bulky GitHub API dumps, compiler
binaries and build logs are omitted. Historical checkpoint JSON/READMEs record
their status at creation, including statements that a checkpoint was then
unpublished. Their old workspace examples are historical; use the portable
commands above or pass explicit `--lake-project`, `--upstream`/`--repo` and
`--output` arguments to the leaf checkers. The standalone legacy scatter helper
is used through its path-independent library function.

The manuscript is the completed full-transfer snapshot; current counter and
PR76 findings are documented in their package READMEs. No unfinished
`ClockReset` or integrated routing draft is included. One local source-path
metadata string in `selected-certificate.json` is normalized to the package
relative `pair-ranked-profile.json`; its mathematical fields are unchanged.
Pinned public PR68 and PR73 candidate bytes are preserved exactly.

Credit for the public constructions and refinements remains with their authors:
Avi Eisenberg's PR62 graph; eumemic's PR57 compiler and PR69 balanced coarse
sums; Chafik Boukhalfa's PR60 priority and PR71 anchored split construction;
Rohan Arun's PR65 scheduling and PR67 costs; Dominik Scholz's PR68 controls and
PR73 parameter refinement; Alejandro Zarzuelo Urdiales's PR70 exchanges; Thomas DiFiore's PR74 node
ordering; and Dominik Scholz's PR76 composition.
All earlier data, complex-layer, matching and assembly credits and notices
remain applicable. This independent verification, formalization and bounded
combination work used substantial OpenAI Codex assistance, including separate
agent reviews. New sources follow the repository's Apache-2.0 license.

Remaining decisive work is actual digit/row routing, complete table and ordered
child-plan instantiation, one fixed-tape recursive scheduler satisfying the
cost hypotheses, and the analytic resampling/precision/exact-recovery/setup
integration needed for the final multiplication theorem.
