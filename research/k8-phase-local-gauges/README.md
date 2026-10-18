# Exact zero-at-boundary gauges on the selected k8 word

**Finite scalar construction, boundary-price comparison and scoped optimum;
no new kappa.** Concurrent Sagar Thakrar [PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259)
already supplies varying helper gauges and the integer-clipping/shortest-path
mechanism, independently rediscovered here. This package adds a stricter
interface: return the gauge to zero before **every non-scalar event**, including
recursive children and residual wrappers. It prices that restriction exactly,
checks all 477 eligible helpers including wrapped helpers, and admits the
materialized words to the retained local scalar/frame/wrapper checker. Original
SCALEs remain in place. No priority or novel shortest-path mechanism is claimed.

The zero-boundary contract needs no commutation of a nonzero gauge through a
recursive child or wrapper. Replaying PR1259's 32 unrestricted helper minima
agrees exactly. For L276, imposing all boundary resets costs **4 primitives per
complex call**: its unrestricted saving 344 becomes 340. L427 likewise pays 4,
while L359 pays zero. [BOUNDARY-COMPARISON.json](BOUNDARY-COMPARISON.json) records
the full 16-helper comparison and four corruption/coverage controls.

Among the **240 wrapped helpers**, the exact best reset schedule is L652, saving
**72 primitives per complex call**. Its complete forward/backward words are also
materialized, literally replayed and admitted by the retained local frame/wrapper
checker. This demonstrates a helper interface excluded by PR1259's unwrapped domain.

On the source-bound PR1094/PR1042 k8 word, the exact best single-helper schedule
is L427, with 22 new SCALE macros in each orientation. It saves **522 real scalar
primitives per complex call** (261 per real/imaginary component), compared with
PR1161's 332 for one constant whole-word gauge.

Adding one such schedule to the *fixed* PR1214 L251/L427 two-helper witness picks
L359, with 28 new SCALE macros. It saves another **518 primitives**, for a total
**1,094** against the selected word. Both the original and composed programs
restore arbitrary helper dirt, preserve every non-scalar event and the paid
recursive profile, and pass the retained emitted scalar/frame/wrapper checker.

| Complete complex call, both components | Forward | Backward |
| --- | ---: | ---: |
| Selected original | 149,002 | 149,018 |
| One phase-local helper, L427 | 148,480 | 148,496 |
| PR1214's fixed two-helper baseline | 148,426 | 148,442 |
| PR1214 plus phase-local L359 | **147,908** | **147,924** |

The inherited engine names the one-component count `real_primitives` and twice
that count `complex_primitives`; this table reports the latter, i.e. actual real
primitive operations for both components. Positive local prefix envelopes remain
52/68 bits under the unchanged 192-bit allowance.

## Exact scope and evidence

The domain is all 477 non-center helpers not incident with COPY/CLEAR, one helper
at a time, both orientations, arbitrary integer gauge exponents and arbitrary
changes within scalar runs, resetting to zero at every non-scalar event. Original
ADD topology, frames and SCALEs remain fixed. A clipping proof in [PROOF.md](PROOF.md)
reduces all integer exponents to a finite interval; the replay is not a finite
cutoff presented as an unbounded search. This class and the whole-word constant
gauge class differ: the latter may remain nonzero across non-scalar events.

The composed claim fixes PR1214's two-helper witness and optimizes **one extra
phase-local helper**. It is not a global three-helper or all-helper optimum.
In this comparison, the added gauge is zero at each boundary **relative to the
fixed PR1214 word**; PR1214's two constant gauges and their inherited transfer
assumptions remain. It does not make those predecessor gauges zero at boundaries.
No native C++ compiler, complete hosting/invoice, outer moment, selected cold
replay, CI or Lean result is claimed. The unchanged emitted Python frame/wrapper
checker is a local check, distinct from those obligations. All-size/compiler,
realization, hosting, precision/tape, analytic and bit assumptions remain.

- Main DP: 95,490 vertices per orientation on the selected word; 94,261 on PR1214.
- Separate distance-transform DP uses literal PR696 lowerer lengths on a padded
  domain: all **1,908** census minima, plus both wrapped-witness minima, agree exactly.
- Independently reconstructed unrestricted minima agree with all **32** values
  in the pinned PR1259 certificate; exact boundary premiums distinguish the classes.
- Literal lowered replay: **445,342 primitives** across six candidate words,
  all **713** initial columns, including initially dirty coefficient work.
- Original macro replay separately checks all 712 data/helper/center columns.
- Unchanged source-pinned frame/wrapper checker: three versions, both orientations,
  all **25 inherited mutation controls** rejected for each version.
- Ten package test groups include 258 exhaustive tiny shortest-path instances,
  unit-discount, domain-expansion, missing-scale, wrong-orientation pricing,
  nonzero-boundary and source-corruption controls. Checks also pass with `-O`.

The new schedules and all per-helper minima are in `CERTIFICATE.json`; complete
programs are deterministically reconstructed and bound by canonical JSON hashes.
No compressed generated container hash is used as an equality oracle.

## Reproduce

Python standard library only, from the repository root:

```sh
python3 -I -B research/k8-phase-local-gauges/reproduce.py
```

That bounded driver runs the five scoped checks below and ends with
`PASS_COMPLETE_K8_PHASE_LOCAL_GAUGES`:

```sh
python3 -I -B research/k8-phase-local-gauges/verify.py
python3 -I -B research/k8-phase-local-gauges/independent.py
python3 -I -B research/k8-phase-local-gauges/comparison.py
python3 -I -O -B research/k8-phase-local-gauges/test_package.py
python3 -I -B research/k8-phase-local-gauges/frame_replay.py
```

Expected markers: `PASS_K8_PHASE_LOCAL_GAUGES`,
`PASS_INDEPENDENT_PHASE_GAUGES`, ten tests `OK`, and three
`PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY` receipts with 25 controls.
The source-pinned historical frame checker uses assertions; its subprocess always
runs without `-O`, even if the driver is invoked with `-O`.

## Provenance, overlap and credit

Base **dadfea6e8a78ff6ba901705f87532a71c6f5bbb8**; OS-random seed **26**, original
20–39 complex-supplier track. [CLAIM.json](CLAIM.json) records three candidates
and the stopping rule. This is a scalar side contribution; unchanged recursive
profiles cannot improve the binding moment or the selected kappa.

PR1161 `d210969d3158a1e6c505e41f67dd84e555c88564` by @woklerx provides the retained
source loader, one-helper conjugation, exact macro replay, unit-discount pricing
and envelope engine, vendored unchanged with its notices. PR1214
`26162c56ec9c50a80e49949f36d4dd9a137a76a6` by Hanson Sun (@bbMisk) supplies the fixed
two-helper comparator; its original certificate is pinned, and its complete
invoice is independently reconstructed. Their constant-gauge optima are credited,
not claimed as new proofs here. PR1170 consolidates existing stage SCALEs, whereas
this package retains them; no composition with that pending result is claimed.

Sagar Thakrar's concurrent PR1259 at
`61367611154266a982fe25e1a6243a8aad77227d` (previous head
`10f4aaed33d79f76ebdebc974e201b1baad8b8aa`) is the closest mechanism overlap.
It checks 16 cold/FULL unwrapped helpers and permits nonzero gauges across
non-scalar events under the inherited homogeneous-transfer contract. Its original
certificate is pinned unchanged; this package replays its 32 minima before pricing
the added reset restriction. Philipp / @mightyOil's concurrent PR1263 at
`5fbaca13028846bddbb001e8e07addc2ab8e5816` uses many constant gauges and has the
larger scalar saving 13,000. This package does **not** claim a best scalar bill
across these classes, or composition with PR1263. Its specific contribution is
the zero-boundary contract, exact restriction price and local admission evidence.

Sagar Thakrar's PR696 supplies the literal lowerer. The emitted frame checker is
the retained PR514/433 local replay, following icekylinx; source bytes are pinned.
The selected construction is Rohan Arun's PR1094 packing on Jeremy Kothe's k8/T16
word and the retained Hao Yan/icekylinx, Chafik Boukhalfa, BRoute, NewBArch and
earlier supplier lineage, as documented in the frozen maintainer review.

At selection, live open PR bodies (up to the 1,000-result request), current
discussions and the local ledger/negative-result descriptions were inspected.
Nearest initial scopes were PR1161, PR1214, PR1170, PR1119 and PR1186. The final
refresh and coordinator review identified overlapping PR1259; the contribution
was reframed around the distinct boundary contract and exact comparison above.
No pinned sprint issue was present; the local
claim was recorded. Existing source packages, selection and `upstream/` are unchanged.

Prepared for **Philipp / @mightyOil**, with substantial **OpenAI Codex
(GPT-6 Astra)** assistance in mathematics, implementation and writing. The two
algorithms are separately implemented but both AI-assisted; no independent human
review or formal multiplication theorem is claimed. New work: Apache-2.0.

## Open next questions

1. **Admit the composed word to the full native/hosted compiler.** This would
   determine whether the finite scalar saving translates to a complete invoice.
   First step: replace only the emitted local streams in an isolated pinned k8
   replay and regenerate all downstream binds. Blocker: that complete admission
   and its precision/global accounting are not supplied here.
2. **Joint phase-local schedules on two interacting helpers.** The present exact
   DP is one-dimensional; two simultaneous gauges can interact on a shared ADD.
   First step: choose one run containing L359/L427 and price the exact 2D transition
   problem, including both helpers' scales. Blocker: a complete unbounded-domain
   reduction and full-word reconstruction must precede any global-optimum claim.
