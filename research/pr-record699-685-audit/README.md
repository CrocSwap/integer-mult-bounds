# Independent finite replay: PR #699 and PR #685

**Audit by Rohan Guliani (@Rohansguliani), with substantial AI assistance through Mux (OpenAI GPT-6 Astra and Claude Opus 5.5).** This audit and its replay tools are under the repository's Apache-2.0 license. It credits the submissions audited and their recorded source lineage. It does not claim a new multiplication bound.

## Verdict

Both submitted conditional κ values reproduce exactly from fresh constructions, and an independent checker that imports no repository code confirms them. No mathematical, owner-map or arithmetic error was found.

| PR | Author | Reviewed head | Source base / first parent | κ (confirmed) | Complex b | Bit c |
|---|---|---|---|---:|---:|---:|
| [#699](https://github.com/CrocSwap/integer-mult-bounds/pull/699) | Jeremy Kothe (jeremykothe2) | `03e8d7ca494a083e5053cd6b1228f66b98414479` | `66849e1475c930fd7732b1a0067ffee7e1e95f60` | `0.001660666354374641` | `0.001663428754540205730067` | `0.001733427039589844234749` |
| [#685](https://github.com/CrocSwap/integer-mult-bounds/pull/685) | Chafik Boukhalfa (chafreaky) | `5fc2a0c4e10558f09f03a8e42559dcf8e381e57e` | `17ce0c79b7b51c2634b439ea5a2b754f09909693` | `0.001660339298410333` | `0.001663100609709845015347` | `0.001733427039589844234749` |

Both records are complex-bound. Their global profiles are

* #699: `{1: 183457, 2: 24624, 3: 31537, 4: 13392, 5: 4032, 8: 576, 44: 1, 48: 2396}`
* #685: `{1: 185185, 2: 23472, 3: 30961, 4: 13968, 5: 4032, 8: 576, 44: 1, 48: 2396}`

with `m = 73`, `live = 7168` and complex deficit 2560.

After review, #699 gained commit `f042731cb332359166e8215839f9a3da28c46c5b`. It changes only the package `README.md` (PLAN/OWNERS are now described as verifier inputs, which resolves the one documentation mismatch this audit reported in [a comment](https://github.com/CrocSwap/integer-mult-bounds/pull/699#issuecomment-6138514968)) and the matching `MANIFEST.json` entry. The replay stays pinned to the reviewed head `03e8d7c`.

## What was replayed

* **#699, the package's own pipeline at `03e8d7c`:** manifest, base and no-triangle construction, layered NP/P6N words, four promotions, the SW4 B-read exchange, native/local/wrapper/phase replay, the independent exact local audit (forward and dual endpoints), `verify_global.py` (strict global admission: `PASS_GAUGE44_NATIVE_EXACT_GLOBAL_ASSEMBLY 0.001660666354374641`) and `independent/price_profile.py` (two exact engines and 47 outer constraints; next-grid, zero-η, zero-β and unit-β controls rejected).
* **#685, the package's own `verify.sh` at `5fc2a0c`:** all 20 stages, including strict global admission, the independent literal-map moment and the two-engine outer-47 check, ending `PASS 0.001660339298410333` (909 s).
* **`independent_check.py`** imports no repository code. For each PR it does the following:
  * Recounts the paid rank profile and residual widths from the raw gates and GF(2) frames, enumerating the subspaces directly.
  * Replays the native scalar programs as exact rational maps on all 728 columns and checks the Horner primitive invoices.
  * Checks the literal `OWNERS.json.gz` (72 × 504 roles: unique helpers and families per call, window capacity, compact non-overlapping footprints) and rebuilds the global profile from it.
  * Brackets complex b and bit c with its own rational log/exp enclosures, strictly within 10⁻²⁴.
  * Recomputes κ as the floored 10⁻¹⁸ grid point of the closed-form bootstrap.
  
  It also checks the following:
  * SW4 leaves the end-of-B rational map unchanged on all 728 input columns, keeps the width inventory, and moves the paid ranks by `{1: −24, 2: +16, 3: +8, 4: −8}`.
  * #699 and #685 occupy the same 36,288 physical owner slots.
  
  Negative controls are rejected: complex b shifted by ±2·10⁻²⁴, κ raised by 10⁻¹⁸, and one owner offset moved by 1.
* **PR #589 bit supplier, standalone:** `research/e8-bit-p111-tuned/tune/verify.sh` (the merged #589 tree, `9d66bbc5`) with Boost headers, which includes the C++ legality/column checkers. It reproduces bit c `1733427039589844234749/10^24`, profile `{1: 381024, 2: 400416, 3: 22752, 4: 26880, 5: 29376, 6: 17376, 7: 26784, 42: 288}` and live 28416. These equal the `nine` record in both PRs' `PR589-EXPECTED.json`, which is byte-identical (blob `e293ddc5`) to the merged file.

## Reproduction

From this repository at or after base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, run this with `git`, `tar`, network access to GitHub, `python3` ≥ 3.11 and a Python that has `numpy` for #685's phase compiler:

```sh
PYTHON=/path/to/python-with-numpy bash research/pr-record699-685-audit/replay.sh /tmp/rohan-record699-685-replay
```

The script fetches the two PR refs and requires each reviewed head to be one of their ancestors. It also checks both parent commits. It builds a separate shared clone with worktrees at the pinned heads, reconstructs PR635's pinned source for #699, runs both packages' pipelines, and then runs `independent_check.py`. The receipt is written to `<out>/INDEPENDENT-AUDIT.json`. The calling checkout is not modified. The #589 standalone replay is separate: run `BOOST_INCLUDE=… PYTHON=… bash research/e8-bit-p111-tuned/tune/verify.sh <new dir>`.

Tested on Linux with Python 3.13.7 and GCC 15.2.0. The full command finished with exit code 0 in 71 minutes and printed `PASS independent finite checks` for both PRs.

## Credit

#699 builds on #685's owner assignment, Jeremy Kothe's #659/#676 construction line, icekylinx's #645 gauge44 package, PR635's local compiler/auditors and eumemic's merged #589 bit supplier. #685 builds on #664's promotions, #659's 504-helper no-triangle word, PR635's local/compiler interfaces and #589. The packages keep the earlier contributor credits and notices, and this report does not replace them.

## Limits

This is a finite replay. It does not prove the inherited all-size compilation, whole-call hosting, precision/tape, mutable-source or analytic-transfer assumptions, and it is not a formal verification of the multiplication theorem. It makes no packing-optimality claim for either owner assignment. #699's committed `evidence/` files come from an earlier construction (R = 492) and are not the SW4 artifacts. This replay regenerated and checked the SW4 artifacts and did not use those files as evidence.
