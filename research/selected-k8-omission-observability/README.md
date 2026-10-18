# Selected k8 scalar omissions: the dirty-helper observation boundary

**Independent exact finite audit; no current acceptance bug and no new kappa.**
For the complex R480 k8 word selected at main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`, every one of **19,669** single
scalar-event omissions changes the complete map. Nevertheless, forward
target-only observation misses **7,184**, and even observing both data banks
misses **6,489**. Testing with initially zero helpers misses **8,977**, even
when every output is inspected. **188 faults evade both shortcuts.**

Two such faults are actually submitted to the unchanged selected local auditor.
The original passes; both mutants reject at its **all-column endpoint**
predicate, before frame/profile checks. This corroborates a current acceptance
dependency rather than reporting the historical owner timing-only omission as
a new defect. No frozen inputs or selected-frontier files are changed.

## Exact result

The raw scalar program has 704 registers: source data `0..111`, target data
`112..223`, and arbitrary dirty helpers `224..703`. It contains 18,962 ADDs
and 707 SCALEs, including 7,208 independently reconstructed compensation ADDs.
These are rational scalar events, **not native-lowered instruction counts**.

| Single-omission class | Forward | Inverse transpose |
| --- | ---: | ---: |
| Nonzero complete-map defects | 19,669 | 19,669 |
| Target outputs unchanged for every input | 7,184 | 8,977 |
| Both data banks unchanged for every input | 6,489 | 8,977 |
| All outputs unchanged whenever helpers start zero | 8,977 | 6,489 |
| All outputs unchanged on source-only inputs | 9,169 | 6,489 |
| Both data-invisible and clean-helper-invisible | 188 | 188 |

The target bank in the inverse-transpose orientation is `0..111`; its source
bank is `112..223`. Counts overlap and must not be added. The complete per-section
counts, exact factor-stream hashes, representative witnesses and source-checker
results are in [EXPECTED.json](EXPECTED.json).

For example, omit `A[3]`, the ADD `r311 -= r498` (scalar event 7,403,
zero-based). For **every** initial state the only changed output is
`r311 += initial_r498`. Thus both data banks are exactly unchanged, and all
outputs agree on every clean-helper input. A dirty basis input `e498` exposes
the failure: the expected output is `e498`, but the mutant also has `r311=1`.
In the inverse-transpose orientation the defect is instead
`r498 -= initial_r311`.

A separate late control omits `cleanup[541]` (scalar event 13,427). Its only
forward defect is `r680 += initial_r686`; the dual defect is
`r686 -= initial_r680`. Both tests use valid JSON, valid dyadic ADDs, valid
registers and the original helper inventory, rather than malformed syntax.
Removing the cleanup entry also updates subsequent early-cleanup indices;
the verifier proves that this changes exactly the intended scalar event.

Actual unchanged-auditor outcomes:

```text
original: PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES
          checked_columns=704, exit_code=0
omit A[3]: RuntimeError: all-column endpoint failure (False, [311]), exit_code=1
omit cleanup[541]: RuntimeError: all-column endpoint failure (False, [680]), exit_code=1
```

## Independent method and proof

Write the full map around a chosen event as `M = S G P`, where `P` is its
prefix and `S` its suffix. Omitting the event gives `M' = S P`.
For `G = I + c e_d e_s^T` (an ADD),

```text
M' - M = -c (S e_d) (e_s^T P).
```

For scaling register `d` by `c`, replace `-c` by `1-c` and `s` by `d`.
All source gates are invertible and all selected scales are nonidentity, so
every defect is nonzero and rank one. Exact output invisibility is equivalent
to the corresponding restriction of `S e_d` being zero; clean-helper
invisibility is equivalent to the data restriction of `e_s^T P` being zero.
This is an equality over the rationals and hence also over complex inputs,
not a numerical tolerance or random-probe argument.

The verifier independently reconstructs compensation from the raw dirty-helper
target response and builds the actual early/full cleanup order. It computes
sparse rational prefix **rows** and reverse suffix **columns**, retaining exact
cancellation rather than propagating support unions. Their full endpoint
matrices must agree and equal the prescribed data shear with every other
register restored. The second orientation replaces every ADD by its negative
transpose and every scale by its reciprocal, in the same event order.

All 39,338 omission positions across both orientations are classified by these
exact factors. Representative basis-input mutants are also executed literally.
The package does **not** claim to have separately run 39,338 complete 704-column
mutant programs. Six tests include an independent literal full-matrix oracle
for all 125 length-three words over a five-operation rational alphabet, in both
orientations (750 omission cases), exact cancellation, identity scales,
inverse-transpose semantics, invalid endpoint/gate rejection and source drift.

## Source to checker to current caller

All listed code and mathematical inputs are SHA-256/Git-blob pinned in
[SOURCES.json](SOURCES.json). The copied word's decompressed hash
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`
is checked against the actual selected `SLOT-PINS-k8.json`, not merely its
historical filename. The selected source manifest independently binds that
pin file, the slot driver and the scalar auditor.

1. `research/gauge44-slots/independent/audit_local.py:89-112` constructs the
   complete scalar program and compares all 704 formal columns in both
   orientations. `require` remains active under optimized Python.
2. `research/gauge44-slots/construction/slots/verify_slots.py:109-111` invokes
   that auditor as `audit-local`; its subprocess must exit zero and its receipt
   must have the exact success status. Native checks are separately required
   earlier in the same caller. They are not replaced by this audit.
3. `scripts/verify_frontier1042.py:79-82` requires that slot replay and passes its
   resulting locals to T16 admission.
4. `scripts/verify_frontier1094.py:60-85` either performs the complete baseline1042
   replay or permits only the published reviewed receipt, checking stage/source/
   log/artifact bindings before passing those same slot locals to PR1094.

This is a pinned source trace, **not an executed full cold caller replay**.
The two controls execute the complete unchanged standalone scalar auditor,
with its optional `--main` parent-interface check omitted to isolate the
scalar obligation. No AST-extracted predicate or mock is substituted. The
full frozen-word content pin would reject the mutant earlier; the experiment
purposefully reaches the semantic defense without changing any production pin.

## Reproduce

Standard-library CPython 3.12, from the repository root:

```sh
python3.12 -I -O -B research/selected-k8-omission-observability/verify.py
python3.12 -I -O -B research/selected-k8-omission-observability/test_verify.py
python3.12 -B scripts/research_package.py --package research/selected-k8-omission-observability
```

The verifier compares the complete deterministic receipt and prints
`PASS_SELECTED_K8_OMISSION_OBSERVABILITY`. Normal replay creates only temporary
source-control files, which are removed on exit. `--write /absolute/new.json`
records a fresh receipt and refuses occupied paths. No third-party libraries,
compiler, optimizer or network access is needed.

The research experiment on macOS arm64 CPython 3.12.12 completed in 2.54 seconds,
including both exact censuses and the original/two mutated source-checker runs.
Runtime is environment-specific, not a speedup claim.
The final registered replay on the same interpreter passed source/provenance
metadata validation, the isolated optimized direct audit and all six tests in
3.02 seconds total, with `PASS_REGISTERED_RESEARCH_PACKAGE`. The command used
locally was `uv run --python 3.12 --no-project scripts/research_package.py
--package research/selected-k8-omission-observability`. Full selected cold replay,
native compiler builds, hosted CI and Lean were not run.

## Overlap, credit and limitations

The [parent coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884)
is advisory. The helper's initial snapshot covered all 539 open PRs including
drafts at 2026-10-14 13:09:44 UTC and 524 discussion records at 13:10:59 UTC;
subsequent cached exact-phrase queries used 540 PRs fetched at 13:15:09 UTC.
Both reported complete pagination. Queries included the assigned card,
`k8 omission`, `complex omission`, `complex fault`, `selected fault`, `k8 fault`,
and adjacent owner/phase/cone obligations. No matching exact phrase hit is a
novelty certificate. Closed work is covered only through local notes/ledger;
code diffs and arbitrary nested source files are not exhaustively searched.
Before publication, a cached exact-scope recheck covered 543 open PRs fetched
at 2026-10-14 13:23:53 UTC and 529 discussions fetched at 13:25:07 UTC, both
with complete pagination; it returned only this local package. The cache can
miss later changes. Targeted live queries confirmed the four heads below
unchanged (PR1017/1102/1433 merged, PR1583 open).
Full bodies and heads of the closest predecessors were read:

- [PR1017](https://github.com/CrocSwap/integer-mult-bounds/pull/1017),
  `b66839f4707e4580524b0f4031d4edc1be939e27`: woklerx's historical R439 Boolean
  single-ADD atlas. Its prefix/suffix fault method and target-invisible
  restoration warning precede this contribution. Here the object is the
  selected complex k8 word, rational ADD/SCALE primitives, both orientations,
  and the data-observation/clean-helper intersection.
- [PR1102](https://github.com/CrocSwap/integer-mult-bounds/pull/1102),
  `6b34051c6cb4b9b68f83383909583a6ba0dab0a9`: optimal two-input testing for that
  Boolean word; no optimal test-suite claim is made here.
- [PR1433](https://github.com/CrocSwap/integer-mult-bounds/pull/1433),
  `71a8cb20bda047ffd110b7efb3f611769cba3cc3`: Sagar Thakrar's packed literal
  Boolean mutant replay; no packed acceleration or all-mutant full-map replay
  is claimed here.
- [PR1583](https://github.com/CrocSwap/integer-mult-bounds/pull/1583),
  `04516881142961cdf97a828fbbc63d72e232a148`: Arham Tahir's selected helper-endpoint
  rigidity audit changes frames while preserving both scalar maps. Here the
  scalar maps themselves are invalid despite restricted observations passing.

Credit Rohan Arun's PR1094 placement (`0fc329d0bec93ca7cd288eaea1295172e8789810`),
Jeremy Kothe's k8/leaver/slot lineage and PR1087
(`589d1cedf5ef5f231182f4ec86408616311a8af0`), Hao Yan's T16 controller,
icekylinx's independent scalar checker, Josie Elliston's PR1091 word pin,
Sagar Thakrar's PR1049 source, and the retained native, frame and bit-supplier
lineages. No claim of invention of the rank-one perturbation identity is made.

This covers only one omitted scalar ADD/SCALE in the fixed program. It does not
establish multi-fault detection, syndrome uniqueness, native phase correctness,
copy/erase or frame legality, owner geometry, physical correlated-helper
realization, precision/tape bounds, compiler injectivity, analytic transfer or
a complete multiplication theorem. Frozen evidence and the selected profile
and kappa remain unchanged.

Prepared for **Adam Gall** with substantial **OpenAI Codex assistance** in
research, implementation, experiments and writing. Apache-2.0. No independent
human-review claim.

## Open next questions

A small fixed rational probe set might diagnose every single omission without
running all formal columns. First collect the exact prefix covectors already
hashed here, seek a probe outside their kernels, and literally replay every
mutant on it. Any coefficient-height/runtime benefit must be demonstrated;
the Boolean two-probe lower bound from PR1102 does not automatically transfer
to rational inputs. Such a diagnostic must not replace complete admission or
claim multiple-fault guarantees. The structured question is in [TASK.json](TASK.json).
