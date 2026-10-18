# Complete T74 native replay with exact sparse state evaluation

**Tooling improvement; no new κ.** This opt-in runner applies the existing
PR1029 sparse evaluator and PR662 exact gate tables to the current T74
Clifford wrappers and phase lowering. It runs the complete five-stage native
pipeline, including the unchanged independent warp-recipe checker. No previous
native result is reused. The benchmark compares the original and accelerated
runners on the same PR2751 base word; both provider words are replayed in CI.

The contribution is integration, coverage-preserving comparison and reproducible
complete-native benchmarking. The sparse evaluator and gate tables are copied
unchanged from their credited predecessors. Older U8 fast runners do not include
this T74 warp-aware pipeline. PR2329 concerns a different multicold production
checker; it is not a dependency of this package.

## Result and scope

Three alternating pairs measured **3.57× faster complete native replay**,
with median **306.7s → 85.9s** (72.0% less wall time). These are Python 3.12.14 /
numpy 2.2.6 measurements on this shared Linux host, specific to this fixture.

| Stage | Original median (s) | Sparse median (s) |
|---|---:|---:|
| native | 1.20 | 1.19 |
| ledgers | 1.44 | 1.41 |
| local-replay | 38.21 | 37.70 |
| wrappers | 5.76 | 2.15 |
| phases | 259.39 | 43.40 |

`phases` includes unchanged independent warp-recipe verification. Stage medians
do not necessarily sum to the median total. Every sample and stage is retained
in `evidence/BENCHMARK.json`. Every sample uses a fresh subprocess and
fresh output directory. There is no saved-result cache. In-process caches hold
only exact, immutable gate tables, with the predecessor's bounded cache sizes.

The five stages are transport, ledgers, independent local replay, wrappers, and
phase lowering followed by independent warp-recipe verification. The last audit
checks 166 warp classes on all 512 columns, including global phase, and retains
all thirteen recipe mutations. All other original native checks remain enabled.
The full paid supplier, physical hosting and outer inequalities are **outside
this benchmark**. This is neither a whole-project speedup nor a faster integer
multiplication algorithm. The selected certificate remains unchanged.

`compare.py` reads every field in all eleven native artifacts. It removes only
the two documented top-level elapsed-time fields. Before normalizing compressed
container hashes to decompressed hashes, it verifies the actual container
bindings. Recipe hashes remain hashes of the original serialized bytes. A changed
control list, a missing file, an invalid binding or a different recipe fails.
`EXPECTED.json` records the complete normalized reference digest and exact recipe
hash for each provider; original receipt hashes trace to PR2751's `REUSE-PINS.json`.

`stage.py` substitutes only `Op.zero_state` inside a fresh process, then executes
the pinned wrappers or phase script unchanged. Tableaux, lowering, rank checks,
off-support checks, denominators and global-phase comparisons remain. The
independent numpy warp checker is a separate unchanged process. The retained
`SPARSE-PROOF.md` proves the predecessor's evaluator equivalence; its compiler
integration section describes PR1029, whereas this package uses the explicit
process-local substitution above.

The current exact algebra's original dense evaluator is also compared with the
sparse evaluator for dimensions 1–5, twelve length-20 circuits per dimension, both
adjoints, and every input basis column (1,488 comparisons, deterministic seed 2).
This finite check supplements the predecessor's proof; it is not a formal proof
of the complete multiplication theorem.

## Reproduce

From repository root, in a Python 3.12 environment with `numpy==2.2.6`:

```sh
python3.12 scripts/research_package.py --package research/t74-native-fast
```

Expected: `PASS_T74_NATIVE_FAST_REFERENCE_AND_CONTROLS base` and `extra`, then
`PASS_REGISTERED_RESEARCH_PACKAGE`. Each provider starts a fresh complete native
replay; the extra run uses a Git-free package copy in a path with spaces.
The base run also exercises 18 boundary controls: source digest/inventory/
symlink changes, altered benchmark fixture, optimized Python, output reuse, singular warp and incorrect
paid profile in both engines, actual emitted recipe mutations, and changed
receipt coverage/bindings. Source drift is rejected before any vendored import.
A failed stage cannot produce the runner's success receipt.

To use the runner on another word under the **same pinned native source version**:

```sh
python3.12 -I -B research/t74-native-fast/run_native.py WORD.json.gz /tmp/t74-fresh
```

The output directory must not exist. Add `--engine reference` to invoke the
unchanged original driver. This standalone command needs no Git or network;
its sources are authenticated and copied into the output directory before use.
Logs, `COMMANDS.json`, the original native artifacts, and `RESULT.json` are kept.
It does not authenticate an arbitrary input as a known construction; it checks
that input through the native pipeline. The fixture verifier above additionally
requires exact fixture and reference-output pins.

To repeat the controlled benchmark (several minutes per reference run):

```sh
python3.12 -I -B research/t74-native-fast/benchmark.py --pairs 3 --provider base --work /tmp/t74-benchmark-fresh
```

Expected: `PASS_COMPLETE_T74_NATIVE_BENCHMARK` and three
`PASS_ALL_NATIVE_OUTPUTS_IDENTICAL` comparisons. Order alternates
reference/sparse, sparse/reference, reference/sparse. OS caches are not flushed;
this shared-host timing is descriptive, with no timing threshold in CI.

## Sources and coverage boundary

Scientific base: `2d3af1ba7e28b74248b47381768e5b116078ba1c`, priority revision 5.
Submission parent after canonical sync: `936fac15b1b1b59dc5285c713a77f9f3c07b2906`.
The relevant dependencies and selected record are unchanged; see `FRESHNESS.json`.
The exact source closure and fixture hashes are in `PINS.json`. File-by-file
origins, dependency heads and transformations are in `SOURCE-PROVENANCE.json`.
The native closure is PR2679 at `2e2cf56521df8a2b816b2689144765ee00b69a24`
with PR2751's published native-audit overlay at
`4cfbb0cc8314d7fb4e8e754545a49a42eb590a69`. Its bytes are unchanged here,
including the repaired incomplete-centre negative control. Existing frozen
packages and `upstream/` are untouched.

The runner supports this specific closure, not arbitrary future native versions.
There is no result-cache invalidation problem: every invocation recomputes the
native evidence. Changing a vendored dependency requires an explicit source pin
update, new before/after comparison and review. Generic package CI reruns both
providers whenever this package changes. Main-line documentation pins are
historical provenance, not admission of pending PR2751.

Inherited all-size/compiler, source-access, hosting, precision/tape, recovery and
analytic obligations remain with the original construction. Exact finite replay
does not discharge them. Source hashes protect against accidental drift; they
are not a security boundary against someone editing both code and its pins.

## Open next questions

The next measured bottlenecks are the independent local replay and all-column
warp matrices. Profile them before choosing an exact representation change;
preserve arbitrary-input, both-orientation and phase-sensitive coverage.
A separate maintainer decision could adopt this entry point for future T74
construction work after independent replay and source-inventory review. This
package makes no automatic migration. Structured first steps and blockers are
in `TASK.json`.

## Credit

Prepared by Tekalign (@tekuuu), with substantial OpenAI Codex assistance in
profiling, integration, verification, review and documentation. No independent
human review is claimed. Apache-2.0; see `LICENSE` and retained notices.

- Charles Bethin (@cbethin), PR662: exact bounded gate tables.
- Ali Romman (@aliromman), PR1029: exact sparse state propagation and its proof.
- Sagar Thakrar (@thakrarsagar), PR1041: prior complete U8 phase benchmarking
  and parallel runner; the present runner does not use its parallelization.
- Victor Li (@VictorLiwentao), PR2329: related pending production integration
  for the multicold helper checker, independently useful overlap.
- Cinna Davis (@1337isnot1337), PR2226: anticipatory dirty borrowing and exact
  warp operators; Rohan Arun and the native lineage: T74 native realization.
- Philippe Van Velzen, PR2679: pre-life hosts, refit/alias and source snapshot;
  PR2751 by Tekalign supplies the current two provider words and audit overlay.
  Jeremy Kothe, zxv, Mason Hale, Marius-Paul Dumitrean, icekylinx,
  DreamingOfClouds and the remaining predecessor contributions are retained in
  `NATIVE-LINEAGE-NOTICE` and the native source notices.
