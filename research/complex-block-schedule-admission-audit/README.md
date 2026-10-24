# Complete block cascade conditioning and admission audit

The literal cyclic matrices in hexapode's #4818, #4819 and #4826 have exact Euclidean condition number **3**, with norm **3/2** and inverse norm **2**. Their stated bounds 9/7, 8193/8191 and 9/7 respectively apply to loop closure factors, not the whole cascade. The corrected bound is still below 16; this finding does **not** make the observation systems singular or prove their proposed call counts impossible.

A second exact check exhibits the arbitrary-input failure of applying #4813's plus-swap-sector cancellation to a general bank. On input e_1 the output-coordinate-zero error is -(1+i)/4. A third check positively confirms #4826's residual identity at the literal 32-coordinate width, although its verifier computes the residual without asserting its monomial factorization. This preserves a valid algebraic starting point.

No new exponent saving is established. A rank computation on an observation matrix containing K does not produce a chronological paid-call realization of that matrix. The proposed complete unit still needs that realization, an all-input owner inventory, raw inverse transpose, all-width justification, finite work/precision bills, and compiler/outer transfer. See [PROOF.md](PROOF.md) and [HANDOFF.md](HANDOFF.md).

## Source and overlap scope

Canonical base: `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7. Exact audited heads:

| PR | Head | Coverage |
|---|---|---|
| #4813 | `f982ecc06826e7087e69b9468d3ff52589fd0822` | Native block-3 operators, sector misuse witness, assembly/accounting boundary |
| #4818 | `fd29d065bbe12f5be5af02fdf5a8b4d86dda3381` | Literal 48-square cyclic model and claimed bound |
| #4819 | `a7b42c2f8ffe5a18d305ca4dda5729d2f1d72ea8` | Literal 208-square cyclic model and claimed bound |
| #4826 | `d7b53d3992e658f0dd49d0207ba33bbc39272bac` | Literal 96-square cyclic model, residual identity, assembly/accounting boundary |

Five unchanged Python source files are retained in `inputs/`; their original paths, immutable URLs, Git blob IDs and SHA256 hashes are in ORIGINS.json. They are self-contained retained inputs, not dependencies on unmerged Git objects. SOURCES.json binds the task/selected provenance at canonical base. The verifier authenticates retained inputs before loading any code. It uses source matrix constructors plus an independent permutation-cycle action and exact integer/rational witnesses; it does not claim a wholly independent reconstruction of every source Clifford primitive.

Bounded live GitHub PR-body queries for `4826`, `4819 audit`, `4818 audit`, `4813 audit`, and `"condition" "cascade"` found these proposals and neighbouring #4828/#4835. All four proposal comment timelines were empty at inspection. #4828 (`299b6092a3a4f6c617dd509cda2d590932d8be1e`) proves sharp conditioning for #4743's **two-bank port** and explicitly excludes complete-cascade conditioning. #4835 concerns the address-algebra finite-test kernel. Neither is reproduced here. Unpublished work, exhaustive discussion coverage and novelty are not established; refresh these heads before publication. Root agents coordinate the ongoing Discussion/handoff check.

## Reproduction

```sh
python3 -I -B research/complex-block-schedule-admission-audit/verify.py
python3 -I -O -B research/complex-block-schedule-admission-audit/verify.py
python3 -B scripts/research_package.py --package research/complex-block-schedule-admission-audit
```

Expected: `PASS_COMPLEX_BLOCK_SCHEDULE_ADMISSION_AUDIT`. RESULT.json records exact witnesses. `--write-result` explicitly regenerates that receipt. Ordinary checks are read-only. `mutation_check.py` copies the package to a temporary Git-free directory, runs optimized Python with no tools on PATH, corrupts a retained source byte and then the scientific receipt in separate subprocesses, and requires both mutations to be rejected. Original package bytes remain untouched. Checks stay active under optimized Python. The predecessor constructors contain assertions; this audit's independent comparison and rejection predicates use explicit exceptions. No original complete native suite, Lean, full phase proof, compiler, hosted CI or independent human review is claimed.

## Open next questions

1. Emit one actual shared-register chronological word for #4813's five banks, starting with the first two overlapping ports. Identify which input to port two is still the original bank and charge every preservation/restoration operation. This is the smallest discriminating test of the alleged 14-call schedule.
2. For #4826, emit one actual three-call two-bank primitive realizing the stated rank-five K block, including dirty companion output, or replace the claimed interface. Dense insertion of K into an observation matrix is not that witness.
3. If a whole word is obtained, derive the full norm/rounding bill using the corrected factor 3 and all internal cuts, then price the complete recursive caller. Endpoint conditioning alone cannot fund a κ improvement.

Prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0. Credit hexapode for the audited packages; Dugongue #4743, Yiyang / Lyy-iiis #4710, lee-phys #4688 and Jacob Alan Sussman #4628 for their predecessor construction/bound work, retained by citation. Nick Petalas #4828 distinguishes the earlier complete-port conditioning problem. The permutation-cycle norm proof is elementary; no claim of a new general spectral method is made.
