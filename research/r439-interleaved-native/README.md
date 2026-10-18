# Native replay of the R439 interleaved COPY window

**PR2407's exact interleaved stream passes the unchanged native legality and
5/9/11-stage column engines.** This closes its finite native-replay handoff,
not physical supplier admission. The construction and its six-ADD saving belong
to Ross Richardson's [PR2407](https://github.com/CrocSwap/integer-mult-bounds/pull/2407).
No new circuit, optimum or kappa is claimed.

The column-0 COPY stays open across all **303 target-undo ADDs and ten taps**.
The copied helper and private slot are not written during that interval. The
native lifetime checker accepts it. Moving the last tap from cut 182 to the
opening preserves instruction counts, frame paths and COPY endpoints, but all
three native column engines reject the changed map.

## Result and coverage

Both the 94-scatter-ADD split and the 88-scatter-ADD interleaving pass. The
candidate has 13,990 records: 11,061 ADDs, 2,911 MOVEs, nine COPYs and nine ERASEs.
Its paid rank mass remains 5,129, with one live copied slot.

| Stages | Formal columns | Candidate scalar ADDs | Bridge ADDs | Omitted-bridge controls |
|---:|---:|---:|---:|---:|
| 5 | 883 | 55,305 | 666 | 6 rejected |
| 9 | 1,327 | 99,549 | 1,998 | 18 rejected |
| 11 | 1,549 | 121,671 | 2,664 | 24 rejected |

The complete native receipts, including every stage and bridge control, are in
[NATIVE.json](NATIVE.json). The finite source replay, full record/metadata hashes,
exact COPY window and inherited invoice are in [REPLAY.json](REPLAY.json).
The candidate's positive envelopes are `F=25717`, `B=5026856`: 95 local bits and
181 bits in the inherited nine-stage scalar bound, below the 104/192 caps.
These are not a general physical precision theorem.

| Changed stream | Native legality | Native columns, all three sizes |
|---|---|---|
| Last nonzero-cut tap moved to COPY opening | Passes | Endpoint rejected |
| One deferred undo omitted | Passes | Endpoint rejected |
| ERASE moved before the taps | Lifetime rejected | Inactive temporary rejected |
| Two ADD phase labels exchanged | Passes | Passes |

The last row is a **coverage boundary**, not a semantic counterexample. Native
engines ignore ADD phase labels. The count-preserving exchange keeps the map and
invoice unchanged but fails the wrapper's full expected RAW6 binding. Phase
provenance therefore comes from that binding, not the native engines.

## Reproduce

Use Linux, Python 3.12 and a Git checkout containing the base commit below.
The registered command needs only Python's standard library and Git:

```sh
python3.12 -B scripts/research_package.py --package research/r439-interleaved-native
```

It prints `PASS_R439_INTERLEAVED_PYTHON_ONLY` and explicitly does **not** execute
native checks. To compile and run the complete native replay, install a C++17
compiler and Boost headers, then run:

```sh
python3.12 -I -O -B research/r439-interleaved-native/verify.py --native
```

Expected final marker:

```text
PASS_R439_INTERLEAVED_NATIVE split94=11067 interleaved88=11061 controls=4 receipts_match
```

`CXX` selects the compiler; `BOOST_INCLUDE` selects a non-system Boost include
root. Temporary files use Python's `tempfile` defaults, including `TMPDIR` when
set. Local checks used CPython 3.12.13, g++ 15.2.0 and Boost 1.90. Native replay is
separate from the generic Python-only CI hook. Hosted CI is not claimed here.

Ordinary execution requires the committed receipts and compares them exactly.
Only explicit `--write` regenerates receipts. Native execution removes only
elapsed time and the temporary input path from comparison, replacing the latter
with the full consumed-stream SHA256. All other native receipt fields remain.
No optimizer or network request is a replay dependency. Native compilation and
execution have per-process timeouts recorded in [VERIFY.json](VERIFY.json).

## Source binding and scope

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
[SOURCES.json](SOURCES.json) pins live inputs and historical catalogue/selected
provenance. [PREDECESSOR.json](PREDECESSOR.json) pins four consumed PR2407 files
at `4944211cee666eb8631b990cb0f33cfa68666485`, retained unchanged in
[pr2407-source.tar.gz](pr2407-source.tar.gz). The archive exists to run the exact
source verifier, not to replace it with another mathematical implementation.

The wrapper checks all pins before loading predecessor code, runs its original
CLI and fixed RESULT, then reconstructs and stages the exact record stream.
It checks staging preserves the full bytes and frame/state metadata. Crucially,
it feeds the interleaved RAW6 to the native engines rather than re-exporting the
non-interleaved JSON word. The candidate RAW6 SHA256 is
`856873eac7d6d9d737e83a28c321b6e760ee183d9648bd98e80761b8d4dc9aba`.

This is a changed scope from the drawn `bit-helper-contract` card: it takes the
explicit [Discussion2401 native handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2401#discussioncomment-18944522)
rather than reopening covered H2/K lemmas. The selected record and frozen
predecessor packages are unchanged. The exact task and next question are in
[TASK.json](TASK.json).

The Python mathematics and native engines are reused with attribution; this
is a new source-bound execution, not a separately derived mathematical checker.
It does not discharge whole-call hosting, projector routing, recursive scratch,
all-size/compiler/common-label realization, precision/tape, analytic transfer,
replacement-interface adoption or the full multiplication theorem. The bit
primitive is not the selected bottleneck, and the paid recursive profile is
unchanged.

## Open next questions

Can this stream satisfy the complete physical COPY and hosting contract? First
bind its exact COPY window, target undo and taps to the physical routing and
recursive-scratch invoice. Stop if that interface cannot preserve the snapshot
while executing the target work. The finite native result removes one execution
uncertainty; it does not supply those missing physical and all-size arguments.

## Credit and disclosure

Ross Richardson supplies PR2407's interleaved construction, witness and source
verifier. Gareth Davidson's [PR2373](https://github.com/CrocSwap/integer-mult-bounds/pull/2373),
head `b52f87f5355ad9f02ca4ac4395117655ac1b19c7`, supplies the native-harness
precedent for a different, non-interleaved word. Sagar Thakrar supplies PR1062
and PR2115's deferred basis and split; Charles Bethin supplies PR2279's
split-ideal optimum; Sricharan Vagvala supplies PR2356's interleaving model.

Retained lineage includes Gareth Davidson's PR915 basis; commdata2338, Scott
Woolsey Biggart and Sagar Thakrar's target-basis work; Sricharan Vagvala's helper
stars; Aaron Wang's B circuits; Ross Richardson's frame circuit;
DreamingOfClouds' PR589 on eumemic's PR555; and the interface, exporter and native
checker work of Zhihao Chen, eumemic, woklerx, Arham Tahir, Dylan Crow and DaysSky.
See the pinned carrier-skeleton LICENSE and NOTICE for its source notices.

Prepared by starship-s with substantial Hermes (`gpt-6-astra-900k`) and Codex
(`gpt-6-astra`, max) assistance in source inspection, implementation and
verification. No independent human review is claimed. Apache-2.0.
