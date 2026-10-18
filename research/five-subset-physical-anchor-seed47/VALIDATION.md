# Seed 47 physical-anchor validation

Research base: `c5108f0f68d482e5712a8e26a5978d47762dfc16`.
macOS arm64; CPython 3.12.14; standard library only, no network during replay.
All checks below were completed in this sprint. Hosted CI is separate.

## One-command full check

From the repository root:

```sh
python3.12 -I -O -B research/five-subset-physical-anchor-seed47/test_package.py
```

Final forward-only package output:

```text
PASS_PHYSICAL_OUTPUT_ANCHOR programs=7 ADDs=24->16 rank_mass=285->241 columns=6656 no_new_kappa
REPLAY_SECONDS verify.py=10.72
PASS_SEED47_INDEPENDENT_WALSH anchors=6 characters=512 columns=13 mass=285->241 adds=24->16 controls=13 no_new_kappa
REPLAY_SECONDS independent.py=4.526
PASS_SEED47_PHYSICAL_PACKAGE programs=7 columns=6656 controls=10 relocation=1 no_new_kappa
```

These individual replay timings describe this run, not a performance claim or
acceptance threshold. The command also runs relocation and corruption checks;
the entire command takes longer than the sum of these two timings.
The primary default replay separately passed without `-O`. The independent
default replay passed both normally and under `-O`; it imports no primary or
predecessor implementation. Saved artifacts remain unchanged by default checks.

## Coverage and controls

Seven programs: the frozen helper comparator and all six output anchors.
Both physical directions, all thirteen arbitrary input roles and all 512 array
addresses are covered. The primary spatial representation covers 6,656 complex
input columns through translation symmetry. The second implementation checks
all Walsh characters, actual address matrices, phases, child ranks and gauge
chronology. Written coverage arguments and the moment inequality are in PROOF.md.

Primary mathematical controls reject nine altered physical words, including
omitted compensation, missing Pauli shifts, wrong half-scales and omitted helper
boundary work. An old-helper error is invisible to clean-source-only checking
but is detected by complete dirty input coverage. The independent implementation
has thirteen controls. These counts describe distinct suites, not a sum of
independent proof obligations.

The package harness makes ten actual on-disk corruptions: missing birth,
singular address map, Boolean rank, wrong half-scale, duplicate JSON key,
undercharged receipt, changed retained source, duplicated source inventory,
changed independent checker, and missing independent receipt. Every intended
rejection occurs. Missing evidence is not silently regenerated. A minimal offline
export in a path containing spaces passes, and the original package hashes do
not change. This is finite evidence, not formal proof of integer multiplication.

An early bidirectional CHILD assumption was removed before publication. The
final literal forward streams and deterministically normalized inverse streams
use only forward CHILD calls. Their extra translations are explicitly charged:
forward 73 to 60; inverse 147 to 117. Both exact dirty endpoints still pass.

## Selected-source context and limits

`scripts/research_baseline.py` in the sparse research checkout could not run
because `research/complex-sw4-frame8` was not materialized. This was a checkout
limitation, not a failed mathematical baseline. The source-binding baseline
passed in the existing full seed17 checkout, whose head is
`8d17ec366d4e4e50d8f28fdb3f23cf9213417b7a`:

```text
PASS_RESEARCH_BASELINE_BINDINGS_ONLY
PASS_SELECTED_SOURCE_TREE_REUSE roots=13
```

All thirteen Git tree objects listed by the selected SELECTED-SOURCE.json
are identical between that full checkout and the research base. No cold circuit
replay is claimed. The full checkout also passed:

```sh
python3.12 -I -B scripts/verify_selected_result.py
python3.12 -I -B -m unittest discover -s tests -p 'test_selected*.py'
```

The selected-record guard passed and all 25 selected-result tests passed, with
no skips. Those four test/guard files match the research base. The selected
conditional kappa remains `836330098538459/500000000000000000`.

Upstream was refreshed to `adc34159e0d6dc3dd2af2bdba3f5ca7376ef957e` before
submission. All five consumed repository inputs, AGENTS.md, CONTRIBUTING.md,
current status and contribution-review index have identical Git blobs.
The revised autoresearch guidance and historical review-ledger changes were
read; they do not admit this finite caller or change its source inputs. No new
package-path collision exists. The branch remains based on the recorded commit.

Final overlap refresh at approximately 03:39 UTC read the newest twenty open
PR title/body records, the Discussion board's first page through Discussion1593,
and the pinned start-here post. PR1230 and PR1557 heads are unchanged at their
recorded pins. Earlier scoped five-subset and dirty-anchor queries were also
checked. No matching fixed-block physical-anchor scope was identified in this
bounded coverage. It does not establish repository-wide novelty.

Not run or established: selected cold replay, global decoder/caller adoption,
CHILD-internal implementation and hidden-state precision, monotone hosting,
tape routing, all-size analytic transfer, Linux, Lean or human peer review.
The full main bill remains noncontracting despite the finite improvement.
