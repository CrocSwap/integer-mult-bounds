# Validation and handoff

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Platform: macOS arm64. Python versions: CPython 3.14.7 and 3.11.14.
No third-party Python dependencies. Assignment seed: 39.

## Executed checks

| Check | Result |
|---|---|
| `python3 -I -B research/complex-coefficient-rescaling/verify.py` | PASS; 10,338 incremental real primitives saved; 1,015 blocks; both 716-column projections |
| `python3 -I -O -B research/complex-coefficient-rescaling/verify.py` | Same receipt; validation does not depend on assertions |
| `python3.11 -I -B research/complex-coefficient-rescaling/verify.py` | Same receipt |
| `python3.11 -I -O -B research/complex-coefficient-rescaling/verify.py` | Same receipt |
| `python3 -I -B research/complex-coefficient-rescaling/test_verify.py` | Nine tests pass, including all 343 signed triples |
| `python3.11 -I -O -B research/complex-coefficient-rescaling/test_verify.py` | Same nine tests pass |
| `ruff check research/complex-coefficient-rescaling` | PASS after import/style corrections |
| `make selected-record-check` | PASS; selected κ remains `51110230636731/31250000000000000` |
| Local Markdown links and `git diff --cached --check` | PASS |

The primary verifier checks 591 distinct add/scale cases used by the actual
JP8 programs. Unchanged macros then use their checked rational semantics in
the complete scalar projection; changed blocks execute their literal primitive
instructions. A separately implemented checker verifies every block using
scalar basis propagation, including arbitrary incoming W. Both exact positive
prefix maxima match the original selected contract.

The independent segmentation DP evaluates 18,925 forward and 5,909 backward
candidate blocks. It matches the chosen spans and costs, and records the 49
nonprofitable transitions. The full census and block hashes are in
`EXPECTED.json`; each block is reproduced from its source event interval.

The tests reject an omitted profitable block, a correct-endpoint extra clear,
an early-ended helper, a changed source payload and an altered receipt. A
minimal source tree relocated into a path with spaces accepts gzip files
recompressed at another level/time and then rejects a changed decompressed
event. Eleven primary mathematical/interface controls and four further
independent semantic controls are recorded in the main receipt.

One scoped AI reviewer checked the mathematics and implementation and authored
`crosscheck.py`. The reviewer independently corroborated the 10,338 incremental
saving and found no mathematical blocker. This is not independent human review.

## Coordination and limits

The initial full open-PR snapshot contained 551 PRs through #732. The final
intermediate snapshot contained 553 through #734, and the immediate
pre-submission snapshot contained 556 through #737; #696, #722 and #723 retained
their pinned heads. #734's body, head and changed-file inventory were inspected and its
distinct per-macro signed-Horner contribution was credited in the README.
GitHub reported no pinned coordination issue at either check, so the claim is
local. No separate reservation issue was opened. #738 arrived during submission;
its distinct Gaussian copy-floor result was checked for overlap. The single
submission is [PR #739](https://github.com/CrocSwap/integer-mult-bounds/pull/739).

Only this research package is changed. No selected supplier, production
emitter, global invoice, frontier pointer or `upstream/` file is modified.
The full `make verify` target regenerates many unrelated historical and current
packages, so it was not run for this isolated research addition. The cold
supplier rebuild, global physical admission, Linux CI and Lean were not run or
claimed. Integrating the block-level private-work contract into the production
emitter remains future work. All inherited uniform/physical/analytic assumptions
remain as stated in the README and the selected construction's maintainer review.
