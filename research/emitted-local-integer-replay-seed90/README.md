# Faster emitted local replay, seed 90

An opt-in port accelerates the complete emitted local audit used in the selected PR1094 lineage, preserving both full orientations and all 25 inherited negative controls. It combines shared-denominator sparse integer rows with independent JSON mutation-fixture copies. These techniques are credited prior work: this package applies them to the distinct `hpe_audit_local.py` workload, leaving selected sources and commands unchanged.

Three alternating fresh-process pairs on Windows/CPython 3.14.5 measured a **2.33x median total process speedup** (2.41x inside the complete audit, 2.46x audit CPU). The full-audit paired wall ratios were 2.409, 2.393 and 2.440. Each timed run includes both orientations, all 25 mutations, input reads and output serialization; archive preparation is excluded. These are local measurements, not a general speed guarantee.

The source-bound default verifier checks all 704 arbitrary input columns, every one of 39386 scalar prefixes, the full receipt and stdout, all 27 pass/rejection outcomes, and all 31 original assertion ASTs. It also runs 441 arithmetic cases, COPY isolation and seven extra controls, including faulty engines that omit ADDs or private clearing. Prefix bounds remain 52 bits forward and 68 backward; the complete paid frame profile and wrapper contract are unchanged.

From repository root:

```text
python -I -B research/emitted-local-integer-replay-seed90/verify.py
python -I -O -B research/emitted-local-integer-replay-seed90/verify.py
```

Expected:

```text
PASS_EMITTED_LOCAL_INTEGER_S90 columns=704 orientations=2 retained_controls=25 extra_controls=7 scalar_prefixes=39386
```

To use the opt-in adapter on a directory containing `CANONICAL-WORD.json.gz` and `LOCAL-PROGRAMS.json.gz`:

```text
python -I -B research/emitted-local-integer-replay-seed90/run.py INPUT_DIRECTORY
```

It writes the same `INDEPENDENT-LOCAL-REPLAY.json` as the retained source. `--engine reference` runs the original source with assertions active. The validated workload is the exact archived selected R480 input; other words are not included in the measured coverage. Default verification prepares that input in an automatically cleaned package-local temporary directory.

`CERTIFICATE.json` is deterministic mathematical evidence. `BENCHMARK.json` separately stores three alternating fresh-process pairs, complete output hashes, wall/CPU samples, environment and implementation hashes. `--benchmark` repeats the timing experiment; `--write` explicitly regenerates the certificate. See VALIDATION.md for measured timings and limits.

No full cold-chain or native replay, hosted CI, selected replacement, general deepcopy replacement, multiplication speedup, or new kappa is claimed. Frame terminology is inherited from the retained local checker; this package does not prove a new physical/Clifford realization theorem. Source, scope and exact invariant are in PROOF.md.

Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0. Wronskode, Sagar Thakrar and the original checker authors are credited in NOTICE.md and OVERLAP.md.
