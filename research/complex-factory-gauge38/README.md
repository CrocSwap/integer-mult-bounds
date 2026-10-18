# Two coupled factory scales save 224 primitives per orientation

**Follow-up: PR922 and PR924 compose.** The [combined construction](COMPOSITION.md)
uses **32 macros and 73 PR696 primitives** per real-component block, versus
77 for either PR alone. Complete raw replay saves **448 primitives per
orientation against baseline**, or **224 beyond either PR**. Use
`python3 -I -B research/complex-factory-gauge38/compose_pr922.py` to reproduce.
The standalone result and its original certificate below remain unchanged.

**Finite complex-supplier construction and scoped exact optimization result;
No new κ.** Delaying two doublings together turns two nonunit additions into
unit additions in Alluri's retained PR681 factory circuit. Neither move alone
improves the cost. The changed circuit keeps 34 scalar macros and saves four
operations per real component under Sagar Thakrar's PR696 lowering.

Fresh reconstruction and inverse cleanup propagate the improvement through
all fourteen historical raw-factory blocks:

| Complete raw scalar program | PR681 + PR696 baseline | This candidate | Saved |
| --- | ---: | ---: | ---: |
| Forward, both real components | 123,768 | 123,544 | 224 |
| Backward / inverse-transpose, both real components | 123,784 | 123,560 | 224 |

The macro count, helper inventory, recursive profile, adapter allowance,
positive prefix bounds and two-bit fractional grid are unchanged. The
corresponding conservative local PR696 recount decreases by 224. This is not a
practical runtime measurement, a selected-provider integration, or a larger
exponent. The selected conditional κ remains **0.001661634653669567**.

## Reproduce

From the repository root, standard-library Python 3.11+:

```sh
python3 -I -B research/complex-factory-gauge38/verify.py
```

Expected final line:

```text
PASS_COMPLEX_FACTORY_GAUGE38 baseline=81 budget=77 class_optimum=67 controls=46 blocks=14 saved=224,224 local_bill_delta=-224 no_new_kappa
```

This command checks source pins, exact integer primal/dual certificates, four
local orientations, 46 rejection controls, the actual raw constructor and all
fourteen physical windows. It executes unchanged native auditors and replays
six complete primitive streams on all 716 logical plus nine arbitrary private
input columns. It compares the deterministic result with `EXPECTED.json`.
Outputs use a temporary directory; `--out NEW_DIRECTORY` retains generated
words, local programs and logs and refuses to overwrite an existing directory.
Inherited subprocesses run with assertions enabled even under an optimized
parent. Gzip source pins cover decompressed payloads.

`--local-only` checks just the local certificate and controls; it is explicitly
not a full replay. `--write PATH` is a receipt-development option, not normal
verification. Packaging checks are:

```sh
python3 -I -B research/complex-factory-gauge38/test_package.py
```

The optional `nominate.py` requires NumPy and SciPy. It reruns the LP and one
20-second-bounded MILP, checks the rounded witnesses exactly, prints a
nomination, and never changes the committed certificate. Normal verification
does not require or trust a solver.

## Why joint moves, and why two cost measures?

The shipped replacement changes only original gates 16, 22, 26 and 30:
doublings on registers 0 and 1 move to just before original gates 31 and 32;
coefficients 2 and -1/2 become 1 and -1. All other gates retain their positions
relative to each other. See `CERTIFICATE.json` and the [proof](PROOF.md).

| Circuit | Macros per block | Original Horner | PR696 |
| --- | ---: | ---: | ---: |
| Retained predecessor | 34 | 128 | 81 |
| Only register 0's doubling moved | 34 | 128 | 81 |
| Only register 1's doubling moved | 34 | 128 | 81 |
| Both moved, shipped candidate | 34 | 126 | 77 |
| Unconstrained gauge-class optimum, accounting control | 38 | 123 | 67 |

An exact integer circulation certifies the last row's optimality among all
integer dyadic wire gauges on this fixed ordered-addition topology, with both
original negations and per-addition PR696 work clearing retained. Its graph
has 57 vertices, 92 edges, and matching primal/dual tension 9. This is an
unbounded class-specific proof, not a finite unsuccessful search. It does not
prove 77 optimal under the macro budget or prove unrestricted circuit optimality.

The 67-primitive circuit is a deliberately retained accounting control: all
scalar identities pass, but its additional scale macros increase the generic
adapter allowance. Its full local PR696 recount is **46,474,329,328 worse**.
The useful 77-primitive circuit preserves the macro budget and avoids that cost.
Both results are checked, rather than selecting the smallest scalar headline.

## Scope, sources and credit

Exact starting commit: `f567884aeb8851b6e794af1184119a3bfbe1e631`, fetched from
both upstream and fork main. OS seed **38** assigned the complex track. Overlap guided the
diagonal-rescaling choice; the highlighted physical seed block `38 mod 14 = 10` has support
`(1,3,5,7)`. Shared-template equality, not extrapolation from that block, is
used for the other thirteen. `CLAIM.json` records three candidates, the local
claim, and the evidence-driven macro-budget revision. No pinned coordination
issue existed; no API publication was attempted.

`SOURCE-PINS.json` pins every consumed predecessor/checker/input and records:

- **Alluri / @alluri-ritual, PR681**, `fdc2e4f3c6825530b02143b30deab5de10209479`:
  the 34-gate circuit, all-block constructor observer and exact native replay.
- **Sagar Thakrar / @thakrarsagar, PR696**,
  `5a3f983715027c4fd83f50bc9001d4b18463bed1`: accepted copy/unit primitive lowering.
- **Jeremy Kothe / @jeremykothe2, PR622**,
  `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`: raw K-triangle constructor.
- **Chafik Boukhalfa / @chafreaky, PR626**,
  `660de893d27bb7abd1d5b01b1640207528a5c851`: retained source/checker packaging.

Credit also belongs to icekylinx's factory/emitter lineage, DreamingOfClouds'
native/gauge work, Dugongue's coordinate-total work, Rohan Arun's recurrence
correction, eumemic, and the predecessor notices read in place. The PR681/696
composition and its complete primitive totals were already integrated in
`supplier-circuit-consolidation`; they are the comparator, not new results here.

PR681's bounded Gaussian synthesis and strictly improving single-scale pass
are not repeated. This adds coupled wire rescaling, an exact gauge-class
certificate, and a complete local-cost comparison. PR750's one-scale CK
cleanup search, PR769/860's coefficient-work reuse, PR837/882's within-macro
lowering and PR883's X4 target preconditions concern different objects/classes.
Their pending savings are not added to ours. PR802's independent PR681 replay
is credited as corroborating predecessor evidence; its code is not consumed.
See `OVERLAP.json` for the scoped metadata refresh and its limitations.

Concurrent **PR922 by @CubeJerry**, observed at
`efd5643c0016b6c6dac26e9ed7dee8a75295ff2a`, appeared during final verification.
It reports a 32-macro factory obtained by three-register contractions and the
same 224 marginal PR696 primitive saving. This contribution retains a different
34-macro word, proves the two single moves are neutral, supplies the unbounded
fixed-topology gauge certificate and the adverse complete-cost control, and
replays the entire PR696 primitive streams including arbitrary private inputs.
PR922's topology changes lie outside the gauge-class optimum proved here.
The original standalone run did not import or replay PR922. The subsequent
[composition follow-up](COMPOSITION.md), requested by @CubeJerry, retains its
pinned circuit and freshly replays both contributions and their combination.
It establishes additive savings for those exact heads; no priority or
standalone superiority claim is made.

Full source construction, local scalar/frame/wrapper checks and new primitive
replays are completed. Later provider transport, global hosting/invoice and
outer-assembly integration remain undone. Uniform compiler, realization,
precision/tape and analytic hypotheses remain inherited. No selected record,
generator, `upstream/` file or global artifact is modified.

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance in
research, implementation, mathematical reasoning, verification and writing.
All new files are Apache-2.0. No independent human or delegated-agent review
is claimed; finite replay is not a formal multiplication theorem proof.
