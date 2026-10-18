# R420 phase-A quad 13: 19 XORs become 12

**Finite circuit improvement; no new kappa claim.** A replacement for one
six-register phase-A quad in eumemic's PR543 R420 supplier reduces its circuit
from **19 to 12 binary XOR gates**. Rebuilding the required literal reverse
cleanup saves seven more: **26,916 to 26,902 native scalar ADDs** in total.
The exact forward integer transfer matrix is unchanged. The reversed
nonnegative transfer matrix decreases entrywise. All 660 symbolic input columns,
including 420 arbitrary dirty helpers, satisfy the original endpoint contract.

No helper, COPY, frame, register, child or restoration step is omitted. Every
register follows the same ordered frame path. The local paid histogram remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, with rank mass **5112**. Consequently this
result supplies no improved recursive moment or integer-multiplication exponent.
The selected result is unchanged.

## Reproduce

From the repository root, using Python 3.10+ and only its standard library:

```sh
python3 -B research/r420-quad13/verify.py
```

Expected final line:

```text
PASS_R420_QUAD13 gates=19->12 native_adds=26916->26902 columns=660 rank_mass=5112 controls=8
```

This checks source pins, reconstructs the improved word from `WITNESS.json`,
compares exact matrices and `CERTIFICATE.json`, replays the predecessor's
E8/frame/dirty-column/interface audit, enumerates all 64 local Boolean inputs,
and independently interprets the actual exported native records with set-valued
symbolic columns and MOVE/COPY/ERASE lifecycle checks. Eight corruptions must be
rejected, including a correct F2 endpoint with invalid literal cleanup and an
F2-neutral pair that increases the positive cost matrix.

Use `--output /absolute/new/directory` to retain both reconstructed words and
record packages; the output directory must not already exist. With no output
argument, scratch files are temporary. `--write-certificate` explicitly rebuilds
only this package's certificate. The verifier's acceptance checks remain active
under optimized Python.

The bounded nomination is separately reproducible:

```sh
python3 -B research/r420-quad13/search.py
```

Expected: `PASS_QUAD13_SEARCH seed=13 attempts=100000 gates=19->12`.

## Exact object and cost

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected record at that base consumes PR543 at
`2065fe4f72a914d907f1046603f5a36f17018535` in the PR626 assembly at
`660de893d27bb7abd1d5b01b1640207528a5c851`, with conditional
`kappa=51110230636731/31250000000000000`.

The object is zero-based quad 13, frame 315, A gates `[873,892)`, on ordered
registers `[267,347,349,376,467,491]`. The six local indices in `WITNESS.json`
refer to this list. `SOURCES.json` pins source bytes and Git blobs at the base;
the word, independent auditor and exporter are the three execution inputs.
The remaining pins identify contextual provenance at the base, not dependencies
on future versions of the selected certificate.

| Component | Original | Replacement |
|---|---:|---:|
| Quad gates at frame 315 | 19 | 12 |
| Corresponding cleanup gates at full frame | 19 | 12 |
| A gates (multi-source gates counted once) | 2064 | 2057 |
| C gates (multi-source gates counted once) | 2661 | 2654 |
| Native ADDs (one per source operand) | 26916 | 26902 |
| Helpers / retained COPYs | 420 / 9 | 420 / 9 |
| Paid rank mass | 5112 | 5112 |

All other phases, retained totals, decoder scatter, source access, boundary
frames and recursive rank charges are unchanged. The complete restoration is
regenerated, not treated as free. See `PROOF.md` for the substitution argument.

## Search, overlap and limitations

OS seed **13** selected the bit-supplier track and quad `13 mod 60`. A seeded
search attempts 100 runs of 1,000 local rewrites. Each rewrite replaces three
gates by at most two with the same F2 map and no increase in either positive
transfer matrix; commuting neighboring transvections exposes other windows.
The first run ends at 14 gates, the second at 12, and the remaining 98 do not
improve it. This covers those **100,000 attempted rewrites**, not all six-wire
circuits. No minimum gate count or impossibility theorem is claimed.

Concurrent PR670 and PR674 shorten phase-B blocks 3 and 5; this package changes
a distinct phase-A quad and depends on neither. Their composition with this
replacement is not tested. PR661's fixed-order phase-B moment bound explicitly
excludes circuit resynthesis. PR620's decoder floors concern a different expense
and are not reopened. `CLAIM.md` records the candidates and coordination checks.

The submission refresh through PR690 also found Mikhail R. Gadelha's PR686
(frame-zero D sharing) and Ali Romman's PR688 (composition and hosted replay of
PR670/674). Neither changes this phase-A quad. They are distinct concurrent
contributions; this package does not import their circuits or claim their
downstream verification coverage.

The checked result stops at the complete native word. The multistage C++ formal
columns, hosted supplier invoice, global moment engines, outer assembly,
repository-wide `make verify`, Lean and remote CI were not run. This isolated
research addition does not alter the selected construction or its inputs;
integration into an accepted supplier requires its usual complete replay.
The inherited all-size compiler, common-label/mutable-basis realization,
whole-call hosting, precision, tape, exact-recovery and analytic assumptions
remain. Finite replay is not a formal proof of the multiplication theorem.

## Credit and license

Prepared for **@mtpsl** with substantial **OpenAI Codex** assistance in choosing
the circuit, writing the search, mathematical argument, checker and handoff.
No independent human review is claimed. New files are Apache-2.0 under the
repository's LICENSE.

This builds on **eumemic's PR543/493** circuit, D4 partition and interleaved
scalar-interface checker; **Dylan Crow's PR370** E8 word format, decoder and
record exporter; **DreamingOfClouds' PR503/510** retained totals and nine-stage
pricing; **Zhihao Chen's PR425** interface argument; and the realization and
accounting lineage retained in
[`research/e8-bit-r420/NOTICE.md`](../e8-bit-r420/NOTICE.md), including Jacob
Sussman, icekylinx, chafreaky and DaysSky. The selected consuming composition
credits Chafik Boukhalfa's PR626 allocation, Jeremy Kothe's construction and
dispatch work, Rohan Arun's recurrence correction, and their cited predecessors.
This package claims only the new quad replacement and its evidence.
