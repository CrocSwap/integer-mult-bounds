# Witness spec tools

Describe a witness declaratively and get a complete, generic verifier for it. You no longer copy and hand-edit a
package `verify.py`. This tooling makes no kappa claim of its own.

There are two entry points:

- `spec.py generate` takes your `WITNESS.json`, builds everything from it and writes `EXPECTED.json`.
  `spec.py check` validates both files and every pin that can be checked without a replay.
- `verify.py` verifies a package from scratch: it builds from `WITNESS.json` and compares against `EXPECTED.json`.

Python 3.11+, standard library only. Run with assertions enabled (no `-O`).

## Two files, one rule

| file | holds | used for |
|---|---|---|
| `WITNESS.json` | **inputs only**: pinned sources, `geometry`, provider build chains (typed steps naming recipes), `dispatch` and `call_order`, and PLAN/OWNERS/recipes referenced by hash | the verifier **builds** from it |
| `EXPECTED.json` | **expected values only**: built word hashes, control counts, per-provider artifacts, programs and profiles, global profile and counts, kappa | the verifier only **compares** against it |

**Rule: no value in `EXPECTED.json` may feed a computation.** Every expected value is recomputed independently
from the inputs, and only then compared. A mismatch stops the run with `SPEC MISMATCH <key>` or
`BUILD PIN MISMATCH <key>`. A wrong `EXPECTED.json` can only make verification fail. That includes the moment
endpoints: they are re-certified, not read. `EXPECTED.json` also records the hash of the `WITNESS.json` it was
generated from.

The inputs are checked too:
- the package and source MANIFESTs, PLAN, OWNERS and every recipe must match their hashes;
- `dispatch` must equal PLAN's;
- `geometry` (`v`, `h`, `helpers`, `centres`, `stages`, `replicas`, `cold_helpers`) is asserted against every built
  word, plan and receipt.

What is trusted:
- the pinned source packages;
- the conditional assumptions inherited by the admission scripts in `code/`. These are PR582's scripts unchanged,
  except that shape constants come from `geometry` and moment endpoints are always re-certified;
- the fixed accounting model in `assemble.py`/`invoice_allcold.py`: the 73-column recurrence, the compiler and
  finite bounds, and the parent dedicated-bank envelope.

## Provider build steps

Each provider is a base word (`{"kind": "source_file", "file": "NAME:rel"}` or `{"kind": "frozen558_promoted"}`) plus
a chain of typed steps. Step types are allowlisted. Each runs an unchanged constructor from a pinned source,
followed by its paired omission or negative-control audit:

| type | constructor and audit |
|---|---|
| `cold_kernel` | PR568 `build_cold_kernel.py` + `audit_kernel_controls.py` |
| `multicut`, `greedy_kernels` | PR568 `build_multicut_kernels.py` + `audit_multicold_controls.py` |
| `promote` | PR569 `build_entrance_promotions.py` + an independent frame-only transfer check with 4 controls |
| `joint_prefix` | PR575 `build_joint_prefix.py` + all-kernel, rank-five and literal-prefix/coverage audits (`variant`, `kernel_recipes`) |
| `frozen558_scalar_audits` | inherited static44 and rank-five audits; the word is unchanged |

Neither file contains scripts or commands.

## Defining a new witness

1. Make a package directory `PKG/` containing:
   - `data/PLAN.json` and `data/OWNERS.json.gz`, from your owner/dispatch solver;
   - any recipes you reference as `pkg:data/recipes/...`.
2. Write `WITNESS.json`. Copy `examples/pr582/WITNESS.json`, then edit:
   - `name`, `geometry` and `gain_baseline_kappa` (the reference the reported gain is computed against);
   - `build.sources`: one must be named `multicold` (the PR568 package, which carries the frozen PR558 replay and
     the vendored local pipeline);
   - `build.providers`: base and steps.

   You may omit `data`, `dispatch`, `call_order` and the `*_sha256` hashes of recipes; `generate` fills them in
   from the files.
3. Generate:
   ```
   python3 spec.py generate --package PKG --witness WITNESS.json --work /tmp/gen --out-dir PKG/data --source multicold=DIR ...
   ```
   This runs one full discovery replay: every provider word is built, every check runs, and nothing is compared.
   Each recomputed value is then copied into `PKG/data/EXPECTED.json`.
4. Check, then verify strictly from scratch:
   ```
   python3 spec.py check --package PKG --source ...
   python3 verify.py --package PKG --work /tmp/verify --source ...
   ```
   `verify.py` prints `RESULT.json` and writes `RECEIPT.json`, which holds the hash of every stage log and artifact.
   If the package has a `MANIFEST.json`, regenerate it after step 3.

Sources default to `PKG/../<dir>`: for example, `research/complex-multicold` next to `research/<your package>`.
`--source NAME=DIR` overrides that location.

## Worked example: PR582

`examples/pr582/WITNESS.json` declares PR582 (`research/complex-571-free4f`, commit 747ec97) as three provider build
chains over pinned sources:

- `ck`: PR571's prefix word → `greedy_kernels` (twelve multi-cut kernels);
- `atm3`: the same word → `promote` (forty entrance promotions) → `greedy_kernels`;
- `jp8`: the frozen558 promoted word → `cold_kernel` → `multicut` → `frozen558_scalar_audits` → `joint_prefix`
  (PR575's plain joint prefix).

```
PKG=REPO_AT_PR582/research/complex-571-free4f
SRC="--source multicold=.../complex-multicold --source structural_gain=.../structural-gain \
     --source larger_gain=.../larger-gain --source joint_prefix=.../complex-joint-prefix"
python3 spec.py generate --package $PKG --witness examples/pr582/WITNESS.json --work /tmp/g --out-dir /tmp/pr582 $SRC
python3 spec.py check --package $PKG --witness /tmp/pr582/WITNESS.json --expected /tmp/pr582/EXPECTED.json $SRC
python3 verify.py --package $PKG --witness /tmp/pr582/WITNESS.json --expected /tmp/pr582/EXPECTED.json --work /tmp/v $SRC
# kappa 0.001601486955392486
```

The generated `EXPECTED.json` equals the expected values in PR582's published `data/SPEC.json`, with one
difference: the hash of `SCALAR-FRAME-AUDIT.json` is no longer listed. That file records seconds and was never
compared.

## Tests

```
python3 tests/run_tests.py --checkout REPO_AT_PR582 --work /tmp/t $SRC
```

End to end, starting from `examples/pr582/WITNESS.json` alone, with no prebuilt words and no reused locals, the test:
1. generates `EXPECTED.json`;
2. checks that it matches PR582's published values;
3. runs `spec.py check`;
4. runs a strict `verify.py` from scratch, which must reproduce kappa 0.001601486955392486 exactly.

It then runs four mutations. Each must make `verify.py` fail at a named check:

| mutation | expected failure |
|---|---|
| one expected global profile count | `SPEC MISMATCH global.global_profile` |
| one dispatch entry | `PLAN dispatch differs from witness dispatch` |
| one owner role in `OWNERS.json.gz`, hash re-pinned | the controller emitter rejects it |
| one kernel coefficient in a recipe, hash re-pinned | the PR568 constructor rejects it |

The mutation runs reuse the strict run's frozen558 replay and localized providers (`--reuse-baseline` and
`--reuse-local`, which are development flags). They still rebuild every provider word. The whole suite takes about
30 minutes on three cores.

## Not included

- Searching for witnesses: owner MILP and solvers, kernel/width screens and `propose.py` orchestration are
  separate tools. This directory only describes and checks witnesses.
- New step types (demotions, PR571 prefix composition). To add one, write a method in `verify.py` that runs a
  pinned constructor and its audit, then list it in `STEP_TYPES`.
- Probe builds that discover a new recipe's own output hash. Recipes must already carry their final
  `output_content_sha256`.
- Byte-for-byte replay of a retained local directory.
- A spec-driven accounting model or parent envelope in `assemble.py`/`invoice_allcold.py`. These describe the fixed
  model, not the witness.
