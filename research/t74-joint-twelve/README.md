# Joint twelve-source recovery: conditional κ ≈ 0.001717141586348426338109

This changes the four older lifted-source assignments together with Mason Hale's eight assignments (PR2696), then composes Philippe Van Velzen's six pre-life hostings and refit (PR2679) with Jeremy Kothe's invocation order and allocation (PR2673). All eight central children remain rank eight. The complete native profile improves on Marius-Paul Dumitrean's PR2733 by `2664*(H8-H7-H1)`. The gain in conditional κ is approximately 0.05834%; it is incremental, not a measured runtime speedup or an unconditional multiplication theorem.

Exact base: `c22e42de697334df85337e005864773cdc2bc98b`.
The rational κ is in `CLAIM.json`: take `0.001717141586348426338109 - 10^-46 - 10^-70`. Larger κ is better in `O(n (log n)^(1-κ))`. No selected frontier is edited.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -B research/t74-joint-twelve/verify.py
```

Expected: `PASS_JOINT_TWELVE_FINITE_REPLAY`, 276390 owner roles, six rejected algebra mutations and one rejected owner mutation. This checks complete arbitrary-input symbolic words, actual frame charges, cleanup, deterministic full owner placement and an exact rational adjacent root bracket. It does not stand in for native/supplier admission.

The optional registered hook runs this plus the generic packing ceiling:

```sh
python3.12 -B scripts/research_package.py --package research/t74-joint-twelve
```

For full release, install `requirements.txt` in a dedicated Python environment, then use a fresh external output directory:

```sh
python3 -B research/t74-joint-twelve/full_replay.py --work /tmp/FRESH-joint-twelve
```

The default authenticates 491 files from pinned PR2679, applies the changed-files-only overlay, generates fresh native providers and retained-parent admission, and runs the original complete supplier/outer verifier. It requires network access and substantially more time. `--source /path/to/pr2679/research/gmx-t74-borrow43-handoff` uses an exact local copy; every file is still authenticated. `--prepared-native-cache PATH` is explicit source-bound reuse and must match every published cache hash. Execution coverage and reuse are in `EVIDENCE.json`; do not infer that every option was run.

To regenerate both complete words from source:

```sh
python3 -B research/t74-joint-twelve/generate.py --source /path/to/pr2679/research/gmx-t74-borrow43-handoff --out /tmp/FRESH-joint-words
```

Expected: `PASS_REGENERATED_JOINT_TWELVE_BOTH_WORDS`. This first positively reconstructs both original PR2462 words, then checks semantic equality of every field of both final words. Compression bytes are not used to judge regenerated mathematical equality.

## Construction and cost

See `PROOF.md` for the changed recovery contract. There are 415 helpers and 72 private buffers per call, live66304, physical66801 = 66304+415+8+72+2, dimension73. All source accesses, recoveries, initial corrections, frame changes, inverse cleanup, pre-life hosting, recursive children and idle remainders are included in the actual words and placement.

Local profile: `{1:2366,2:646,3:297,4:120,5:26,8:8}`.
Complete profile: `{1:1593072,2:430236,3:204396,4:79920,5:22532,8:5328,32:1,48:26558}`; rank mass4816512.
The exact moment root lies strictly between `.001717141586348426338109` and `.001717141586348426338110`. The strict supplier and modern outer release both pass. The retained bit supplier remains nonbinding under the inherited assembly/outer assumptions.

The generic coverage-law ceiling is about `.001750373331784`, realized fraction `.9810144814068302`, computed using the pinned `ceiling.ceiling()` implementation. This is not a sharp lattice bound or proof of optimality. The experiment constructed one deterministic assignment in both providers; no exhaustive search claim is made. Retained assignment seed2 is provenance, not a claim of an independent random search.

## Verification and controls

Both changed native providers passed native generation, ledgers, local replay, wrappers and phases freshly. The complete strict supplier and modern outer release passed with authenticated native/retained-parent reuse. Receipts are under `evidence/`; `REUSE-PINS.json` binds every reused file. The independent implementation propagates symbolic noncommuting operator words and separately checks geometry/cleanup. Reversing or deleting anticipatory corrections and reversing a source recovery are rejected for both providers. An out-of-bin owner mutation is rejected. The candidate endpoint rejects PR2733's inferior profile.

`DERIVATIVE-CODE.patch` exposes checker changes for review. No rejection test is removed: the intermediate-centre-step mutant is generalized to an actual incomplete descent when there is no intermediate step. Lowfour mutants select actual corrected targets, source33 writes and recovery gates instead of stale hardcoded indices. Runtime target/profile/refit pins are updated to the changed word. Alias653 position metadata is regenerated from the actual warp; its checker is unchanged. The full release reruns these controls. Failed initial runs that exposed these stale assumptions are recorded in `EVIDENCE.json`.

The overlay is about1.5MB, not a copied predecessor tree. Compressed certificates carry the complete witnesses; their generators and readable checker patch are included. `SOURCE-FILES.json`, `OVERLAY-PINS.json`, `INPUT-PINS.json` and `GENERATOR-PINS.json` authenticate their respective sources. `SOURCES.json` pins main-line provenance and external dependency heads.

## Scope and inherited obligations

Finite exact admission is conditional evidence, not formal proof of the complete multiplication theorem. All-size compiler/machine realization, common labels and source access, physical hosting/routing, precision/fixed-tape contracts, exact recovery and analytic transfer, recurrence, bit-supplier and modern outer obligations remain inherited. No new discharge of those universal obligations is claimed. The selected accepted result and this pending derivative are distinct.

This deliberately changes the old-four recovery paths held fixed by PR2720. It does not contradict that scoped cut obstruction. PR2733 independently supplied the concentrated/pre-life composition; a previous local duplicate of it was not submitted. PR2745 subsequently refined that same profile's outer numerical precision by about6e-25; the present change improves the actual native profile. Latest live overlap coverage and limits are in `FRESHNESS.json`.

## Open next questions

- Can another changed source/consumer contract improve the actual word beyond this profile? First price all recoveries, frames, source accesses and buffers; the fixed-old-path obstruction cannot simply be ignored.
- Can a sharp fixed-inventory packing certificate close the remaining gap to the generic coverage-law ceiling? First derive the new inventory's dual/lattice constraints. The reported generic ceiling does not establish a packing opportunity.
- Can one inherited all-size realization or precision obligation be independently discharged? Select its exact hypotheses from the pinned review; finite replay is not that proof.

Prepared by Tekalign (@tekuuu) with substantial OpenAI Codex assistance in construction, code, independent algorithms, checking and documentation. No independent human review claimed. See `SOURCE-NOTICE` for predecessor credits and retained notices. New work Apache-2.0.
