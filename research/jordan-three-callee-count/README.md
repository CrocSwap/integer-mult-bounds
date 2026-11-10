# Exact regular J3 second-callee counts

For a first map P=J_3(lambda) over F_q, with lambda nonzero and lambda^2!=1,
the fixed ordinary wrapper has exactly

```text
q^4-q             optimal invertible second maps if lambda^2=-1,
q^4-q^2-q         optimal invertible second maps otherwise.
```

The first branch cannot occur in characteristic two. This is a scoped
algebraic proof with exact finite corroboration. It resolves the regular
three-dimensional case explicitly left open by Nicholas Stone's
[PR5556](https://github.com/CrocSwap/integer-mult-bounds/pull/5556).
No new kappa or selected-frontier change is claimed.

[PROOF.md](PROOF.md) proves the count and the complete determinant
distribution of Q=P+(P^2-I)S across all square-zero S. In dimension three,
every nonzero S has rank one. Counting its two annihilator constraints
reduces the determinant filter to the kernel dimension of
`(1+lambda^-2)N-lambda^-3 N^2`. That dimension is two in the exceptional
branch and one otherwise. The predecessor wrapper characterization and
its optimum are cited premises, not new audit deliverables.

Examples are 236 maps for either regular lambda over F4, 620 for
lambda=2 or 3 over F5, 2345 for every regular lambda over F7, and 6552
for either square root of -1 over F9. These are counts in the abstract
wrapper, without native implementation prices.

## Evidence and reproduction

The standalone standard-library verifier reports
`PASS_JORDAN_THREE_CALLEE_COUNT`. It computes:

- All 62,512 distinct square-zero parameters across fields of sizes
  2,3,4,5,7,8,9,11,13, with no duplicate projective representatives.
- All 519,494 literal second-map determinants in 38 regular field/lambda
  contexts and their complete determinant distributions.
- Independent complete enumeration of all 262,144 three-by-three matrices
  over F4 and all 1,953,125 over F5. The square-zero subsets contain 316
  and 745 matrices and equal the projective catalogues exactly.
- All six input columns of the literal ordinary wrapper for each of the
  1,712 accepted maps over F4 and F5, each attaining error rank three.
- Thirteen rejected malformed or mutated cases, plus explicit non-field,
  non-square-zero and invertible-but-suboptimal wrapper discriminators.

F4, F8 and F9 use polynomial-basis extension fields, with exhaustive field
axiom checks. They are not arithmetic modulo a composite integer. The
all-finite-field conclusion comes from the written proof. The enumeration
is finite corroboration and does not claim independent review.

From the worktree root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/jordan-three-callee-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/jordan-three-callee-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/jordan-three-callee-count
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/jordan-three-callee-count --check-source-history --check-modes
```

Another CPython 3.12 path may replace the interpreter prefix. Every run
emits a generated receipt binding the package files by SHA256 and writes
nothing. There is no handwritten receipt or expected-output hash oracle.
[VERIFY.json](VERIFY.json) registers normal and optimized checks with
180-second limits. Local warning-strict normal and optimized runs took
4.59 and 4.73 seconds on CPython 3.12.15, macOS arm64. Both registered
commands also pass through the package launcher. These are replay durations,
not performance-improvement measurements. [SOURCES.json](SOURCES.json) binds predecessor prose and
the source context as historical provenance, without runtime dependencies.

## Limitations

Resonant lambda^2=1, larger blocks, several coupled blocks and arbitrary
first maps are outside the theorem. Rank-optimal agreement does not mean
exact interchange on all inputs. Native coefficients, physical realization,
restoration, movement, precision, stock, compiler and complete supplier/outer
costs remain unpriced. The five selected framework assumptions remain.
No predecessor scientific suite, selected cold replay, Lean or Docker run
is part of this contribution. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Count the resonant J3 branch, starting with PR5228's noninvertible-A
  quotient characterization and separating characteristic two. This proof
  requires A invertible and cannot settle that branch.
- Choose two explicitly specified Jordan blocks and count their coupled
  square-zero parameters. Off-diagonal couplings and higher rank prevent
  naive multiplication of single-block counts.

These questions and their blockers are recorded in [TASK.json](TASK.json).
The first verified regular J3 count ended the search.

## Sources, overlap and credit

This contribution was produced by Nick Petalas. Apache-2.0. Credit Nicholas
Stone / [PR5556](https://github.com/CrocSwap/integer-mult-bounds/pull/5556),
head f87b6ac80fce79eb83c005d9b33d0a06597aeb50, for the question, filtered
Jordan method and rank-one suggestion; Nick Petalas /
[PR5228](https://github.com/CrocSwap/integer-mult-bounds/pull/5228) for the
all-first-map characterization; Jerry Chen / CubeJerry /
[PR2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950) for the
ordinary wrapper optimum; and the retained ordinary/native lineage.
Rank-nullity, rank-one determinants and finite-field fiber counting are
classical. No general literature-priority claim is made.

Base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8. The uniform-transfer-audit card is explicitly changed to this
algebraic side result; no selected assumption is discharged. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360811)
records the scope. Entry checking covered 352 open PRs, 6,254 Discussion
records and all 8,917 current note records, supplemented by main-tree,
merged-PR and recent-account searches. Unpublished work and arbitrary
historical diffs remain coverage limits. No open PR studying this regular
J3 count was identified; PR5556 and PR5228 are merged predecessors.

## Verification constraints

The verifier imports no predecessor code, uses no subprocesses or network,
and has no recursion. Its 22 functions are each at most 29 physical lines.
Field presentations are a fixed allowlist with q<=13; matrices have size
three or six. The largest parameter catalogue has 30,745 matrices, each
with nine field entries. The independent full-matrix scans stream at most
5^9 tuples and retain only the accepted square-zero subset. Explicit
exceptions enforce checks under optimized execution.

Managed allocation in CPython is a Power of Ten rule 3 deviation, bounded
by these fixed domains and the committed package size. The dataclass uses
standard bounded generated methods. The rejection helper's indirect calls
have five statically listed validation targets and synchronous lifetimes.
No variable-domain or fixed-allocation runtime claim is made. Warning-strict
normal/optimized execution and AST inspection provide available diagnostics;
no separate static analyzer or proof assistant is used.
