# Optimal 66-grade sign extraction in 68 complete executions

For 66 nonzero grades, the exact minimum is **68 complete executions** when
extracting arbitrary diagonal blocks by an equally weighted average of
grade-sign conjugations. Yiyang's [PR #5037](https://github.com/CrocSwap/integer-mult-bounds/pull/5037)
uses a 128-run Walsh wrapper at this grade count. The new wrapper saves 60
complete executions. This is a scoped algebraic proof with an exact finite
sign certificate, not a new kappa or a complete multiplication theorem.

[PROOF.md](PROOF.md) proves the lower bound by rank and three-column sign
divisibility, and attains it using the classical Paley order-68 Hadamard
matrix. Paley's construction is credited, not claimed as new. Each execution
uses the same complete program with signed input and output. Only original
independent inputs receive productive credit.

The average includes a factor 1/68, which is not dyadic. The proof establishes
that the common-grid integer accumulator is exactly divisible by 68. A binary
shift and exact integer division by 17 recover the result on the same dyadic
grid. The verifier includes a bit-by-bit signed divider. Seven extra accumulator
bits suffice, as for 128-run Walsh averaging. Copying, signs, accumulation and
division remain additional work; a lower total runtime is not established.

## Evidence and scope

The standalone standard-library verifier constructs every sign and checks
2,346 upper-triangular entries of the full 68-column Gram matrix. It executes
28 dense/triangular real-component fixtures with unequal grade dimensions,
covering 1,712 output components. These real-component checks also apply
separately to both components of Gaussian dyadic data. A separate six-coordinate
variable-denominator execution checks exact dyadic recovery. The binary divider
passes 8,201 signed exact-division fixtures, and 11 corruption/domain controls
reject. These are finite corroboration; the universal conclusion is the proof.

The contract fixes equal positive weights and sign-only conjugations that
extract every possible off-diagonal block. Unequal weights, arbitrary complex
phases, independently chosen input/output maps and special sparsity in a
particular program can change the problem. No optimality is asserted there.
This wrapper is applied once at the root. Native shears, recursive matching,
rounded arithmetic, physical implementation, row stock, BIT and outer admission
are not supplied or replayed here. The selected frontier is unchanged.

The original card is `complex-rank-shape-decoder`; [TASK.json](TASK.json)
records the changed scope to this extraction side result and the stop rule.
The scientific base is `81e9bd69e4a5b00ba9c713a1620e36d576d5522e`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the predecessor extraction note,
README, selected record and original card as Git provenance. No predecessor
executable or live input is needed. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142748)
records the target and bounded overlap checks.

## Reproduce

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/grade-sign-extraction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/grade-sign-extraction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/grade-sign-extraction --check-source-history
```

Substitute the local interpreter path on another host. Expected direct output
contains `PASS_GRADE_SIGN_EXTRACTION`, `runs: 68`, `literal_cases: 28` and
`signed_exact_divisions: 8201`. Registered replay runs both normal and optimized
Python with warnings as errors. The verifier writes no files and has no imports
from predecessor packages.

All verifier loops have fixed finite bounds. The largest literal operator is
102 by 102, with 68 executions; the binary divider has a 512-bit evidence cap.
The functions are under 60 lines and failures raise explicit exceptions, so
optimized Python retains every check. Power-of-Ten rule 3 has a managed-runtime
deviation: Python allocates objects during execution. Fixed matrix, integer and
execution capacities bound the live mathematical data; garbage collector and
interpreter allocation are not inspected. Rule 10 uses warning-strict normal
and optimized replay plus AST parsing; no separate static analyzer is required
by this package. A native port would need its own allocation and diagnostic
policy. No physical runtime measurement is inferred from verifier timings.

## Open next questions

- Bind one actual graded native program to the complete root extraction
  contract. Start with a literal source/exit-matched caller from #5037 and its
  same-grade Gaussian blocks. Coherent native shears and recursive matching
  remain blockers; another sign design does not discharge them.
- Price this 68-run wrapper and the 128-run Walsh wrapper at that completed
  physical caller. Include all signed copies, workspace reuse, accumulation
  and exact division by 17. A complete ownership, grid and movement contract
  is required before the count improvement can imply a complete cost gain.

## Credit

This contribution was produced by Nick Petalas. Credit Yiyang / Lyy-iiis
#5037 for the bounded-lane and root-only extraction setting, Dillon / #4623
for border recovery, Cao Yifan / #4610 for the native-word context, Jacob Alan
Sussman and the finite-precompiler contributors, and the retained native,
helper, semantic precision and outer lineage. The classical Paley/Hadamard
construction and sign orthogonality retain their credit. No literature-priority
claim is made for those methods. Predecessor files and notices are unchanged.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
