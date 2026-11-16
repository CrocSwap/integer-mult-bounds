# CONDITIONAL κ = 0.0036624027915 — 14 loan + stationary-snapshot instances on #7621, with the engine that finds them (premises: exactly #7620's, over 180 CLEARs)

**κ = 0.00366240279155398…, ×1.00025679 (+0.025679%) over our
[#7621](https://github.com/CrocSwap/integer-mult-bounds/pull/7621)** (κ 0.0036614625547). The official
`evaluate_recursive_power` bracket (256 bits) is [0.0036624027915, 0.0036624027916]; the claim 0.0036624027915 is
below the exact crossing 0.00366240279155398.

This PR ships the word **and the engine that produced it** (`engine/`), so anyone can run these incremental
passes on any P104 native word. The device is [SYLforge](https://github.com/CrocSwap/integer-mult-bounds/pull/7620)'s
(#7616, #7620); the engine finds, solves and exactly checks instances of it automatically.

> **Premises (inherited; one reading widens).** Conditional on exactly #7620's premises: its five framework
> assumptions (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`) and its
> fixed allocation of 17·68 = 1,156 owned banks. Its CLEAR reading now covers **180 CLEARs** (74 original + 106
> stationary), not 167: the 13 new CLEARs belong to 13 new stationary owned lifetimes of the commonest shape among #7620's own
> (INIT, one write, one read, dirty CLEAR, no MOVE; 82 of #7620's lifetimes have it), each with an exact CLEAR certificate
> under the rule of #7620's `verify_certificates` (data/clear-certificates.json). The word's rows, end charts, 47 owned MOVEs,
> peak 50, 68 labels, all 1,018 old owned observations and the old 167 CLEAR contents are #7621's. If #7620's premises
> are refused, this word is void with #7620 and #7621.

## Run it yourself

```sh
python3 engine/run_on.py WORD.json.gz [OUT_PREFIX]      # census -> greedy -> re-census, about 1 minute, one process, under 1 GB
python3 engine/run_on.py data/base-7621-word.json.gz /tmp/out   # reproduces this PR: /tmp/out_14.json.gz == data/word.json.gz
python3 -I -B check.py engine                            # the same, as a test (JSON-equal word and equal instance log)
python3 engine/control.py                                # controls on #7617 with #7620's instances as data
```
Python 3.12 and the standard library only; `pricekit.py`, `fastx.py`, `jl.py` and the #7113 caller are vendored in
`engine/`, and every path is relative to the script. Full notes are in [engine/ENGINE.md](engine/ENGINE.md).

**The move.** A register r drops an interior stop X from its path A→X→B. A partner p takes one extra stop: on side A
(all 14 here) p is the reader of r at X and inserts A before X. The work r would have done at X is carried by (i) a
loan through a carrier c, a public register whose path runs A→X→B consecutively, (ii) stationary owned snapshots
(INIT at X, one write, one read, dirty CLEAR) when r's X-writes must reach p, and (iii) a signed role swap between r and p, with
a settle at B. Natively each instance swaps one 3|1 hop merge for one 1+2 split.

**How the engine works.** `lb.py` indexes a word (register stays, ops, owned live intervals, projected-state checkpoints)
and solves a candidate exactly: the template coefficients that are unknown enter linearly, so a windowed replay (mod 2^61−1, 4-dim random
projection) is affine in them, is solved, rationalised and re-verified, and must reproduce the window-end state, every pre-existing
owned observation and every CLEAR content. `tpl.py` holds the templates and the legality-keeping slides. `run7621.py` takes an exact census of
both shapes ordered by the convexity gain of x ln x, tries instances greedily, accepts one only if `check.full` passes, the owned
peak stays ≤ 50 and the PRICEKIT κ rises, then re-censuses until a pass lands nothing. `control.py` rebuilds #7620's own instances
on #7617 (read as data): 39 of 44 shape instances rebuilt, 258@829 and 464@526 identical to SYLforge's (same carriers, same coefficients).

**Known blockers on this word (85-place re-census after the 14 landed).**

| reason | places | meaning |
|---|---|---|
| no solution | 20 | contamination reaches registers that never meet r at B |
| no free label (peak 50 binds) | 17 | owned peak 50 is full over the snapshot interval |
| no carrier | 17 | no register runs A→X→B |
| A window | 15 | the carrier leaves A before r or p arrive |
| slides | 10 | a slide partner is touched in between |
| write after read / read before p at X | 2 + 2 | side-A write-after-read; r read before p arrives at X |

**Next levers.** A second carrier, so a contaminated register can be settled where it meets a register holding ρ rather than r;
shared snapshots or a reorder of busy owned lifetimes to free peak-50 events; carriers that are not consecutive with in-transit
settles; census shapes with several sources or readers.

## The edits

73 deletions and 154 insertions on #7621's word (77,196 → 77,277 events; ADD +55, INIT +13, CLEAR +13;
[data/edits.json](data/edits.json), instances in [data/instances.json](data/instances.json)). Fourteen instances, all side A:

| r | X | p | carrier c |
|---|---|---|---|
| 382 | 438 | 553 | 1144 |
| 422 | 492 | 577 | 1182 |
| 392 | 455 | 562 | 1154 |
| 391 | 451 | 558 | 1153 |
| 390 | 453 | 560 | 1152 |
| 386 | 452 | 559 | 1148 |
| 374 | 433 | 548 | 1136 |
| 366 | 420 | 541 | 1128 |
| 364 | 419 | 540 | 1126 |
| 360 | 417 | 538 | 1122 |
| 359 | 413 | 534 | 1121 |
| 358 | 415 | 536 | 1120 |
| 356 | 416 | 537 | 1118 |
| 348 | 399 | 528 | 1110 |

In each, r's route loses X and p's route gains the chart before X; exactly these 28 registers change chains. Thirteen instances add a
snapshot (348@399 reroutes r's X-writes straight into p). 24 new MOVE pairs appear, all strictly nested; 14 leave the MOVE set.

## Price

Native paid delta per call {1:+1, 2:+13, 3:−28, 4:+13, 5:+1}; over 17 calls {1:+17, 2:+221, 3:−476, 4:+221, 5:+17}.
Paid positions 110,145 and rank surplus S = 1,424 are unchanged. Official tools (`price.py`): `compare_recursive_invoices` against #7621 gives
`uniformly_better`, strictly negative for r^(1−C); `evaluate_recursive_power` (256 bits) gives `new_cost_lower` at C = 0.0036624027915, 0.0036614625547 (#7621)
and 0.0036611026181 (#7620), `new_cost_higher` at C = 0.0036624027916.

Ordinary bill (17 calls, #7000 formula) 785,022,672 → 785,921,632 < 10^9; precision bit bounds 303 / 299 / 299 unchanged; common grid
2^25·1125 with 40 numerator bits unchanged; non-dyadic literal events 5,903 → 5,903. An independent read-only audit found the word sound relative to
#7620/#7621 (exact replay; official #7000 native engine with bad_inputs 0; strictification gate passed, γ 0.941467, δ 0.908157;
22/22 rejecting controls).

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-loan-snapshot-engine-on7621
```
`VERIFY.json` registers six commands: `core` (words, edit list, exact replay of both, owned data, observations, certificates, structure, invoice, κ),
`controls` (22 rejecting controls, 2 accepting), `columns1` and `columns2` (the affected-pair column tests), `price.py` and `engine` (the engine rerun on #7621's word).

**Affected pairs.** #7621's census is 846 pairs (the 837 pinned by #7620's runner, minus (719,127), plus 10). This word changes 28 more routes; the census
becomes **964 pairs** (+118: the old and new route pairs of the registers not already counted; none dropped; every new MOVE pair is inside).
`check.py` runs 512 forward and 512 adjoint Gaussian columns, signed Pauli action, absolute phase, exact ascent rank and a wrong-phase rejection
on all 964 (964 × 1,024 = 987,136 columns, in two halves of 482 pairs). Census files: `data/affected-pairs-7621.json`, `data/affected-pairs-loan.json`.

## Conditional premises and what is not rerun

The claim carries exactly #7620's premises (above), now over 180 CLEARs, and the signed #7113 caller and BIT premise of the base. This package
does not rerun #7620's full native/signed 17-stage application, catalogue, outer predicates or precision/tape counts (header, rows, grid and owned data
are unchanged); the audit ran the official #7000 native engines on the word. No upstream maintainer has reviewed the package.

## Credit

The device is SYLforge's ([#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616), [#7620](https://github.com/CrocSwap/integer-mult-bounds/pull/7620));
the base is our [#7621](https://github.com/CrocSwap/integer-mult-bounds/pull/7621), on [#7617](https://github.com/CrocSwap/integer-mult-bounds/pull/7617)
and [#7615](https://github.com/CrocSwap/integer-mult-bounds/pull/7615) (courier lineage). Signed caller: Rohan Arun's #7113. See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

**The premises.** A ruling on #7620's inherited assumptions and its CLEAR reading (`owned_erasure`, clear-form-gap Q1), now with 180 CLEARs, decides
#7620, #7621 and this word together. See [TASK.json](TASK.json).
