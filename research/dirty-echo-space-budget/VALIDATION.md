# Validation receipt

Validated locally on macOS arm64 on 2026-10-13. Base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

## Completed checks

| Check | Result |
|---|---|
| Complete certificate replay, Python 3.14.7, ordinary isolated mode | Passed |
| Complete certificate replay, Python 3.11.15, isolated optimized mode | Passed |
| Relocated package with spaces in its path, outside any Git checkout | Passed |
| Source bytes, missing inventory entry and wrong source commit controls | All rejected |
| Wrong optimum, boolean-for-integer and float-for-integer certificate controls | All rejected |
| Existing output overwrite control | Rejected; original bytes preserved |
| All 13 vendored files compared with their exact Git blobs | Passed |
| `make selected-record-check` | Passed |
| Python syntax, local document links and patch whitespace | Passed |
| Original `upstream/`, selected record, current status and review ledger | Unchanged |

The reproducible core command is:

```sh
python3 -I -O -B research/dirty-echo-space-budget/verify.py
```

Expected:
`PASS_DIRTY_ECHO_SPACE_BUDGET: n=50, arrays=6, leaves=2752->2304`.
The complete evidence is compared as canonical JSON, preserving the distinction
between integer, boolean and floating-point fields.

The relocation and artifact controls are separately reproducible:

```sh
python3 -I -O -B research/dirty-echo-space-budget/test_package.py
```

Expected: `PASS_DIRTY_ECHO_PACKAGE: relocated replay and 7 artifact rejection controls`.

Every certificate field matches across the supported tested runtimes.
SHA-256 of EXPECTED.json:
`917e6eb0d2fc85efc06235ee36c033d41949c2b05378f1f55d525b4f72858e40`.

## Mathematical and implementation coverage

- All 576 `(n,s)` cells with `1<=n<=64`, `0<=s<=8`: 255 feasible plans and
  321 explicit infeasible cells. Every feasible plan is expanded and checked.
- Independent enumeration of all 5,440 ordered trees through eight leaves,
  with 72 exact optimum comparisons. All 1,161 trees through seven leaves
  additionally receive symbolic word checks.
- 2,904 signed free-noncommutative identities and inverse round trips, including
  all feasible table plans and 36 explicit equality-family constructions.
- 1,530 nonlinear square/floor modular round trips, covering 2,182,380 executed
  leaves, with arbitrary source/target/dirt and an unused spectator array.
- 18 mathematical instruction mutants; 24 public-interface rejections before
  mutation, plus argument, malformed-plan and infeasibility controls.
- 186 complete rounded compositions and their inverses across 31 plan/budget
  pairs, mixed inner/outer factors, cycle lengths 1/3/5 and both orientations.
  Exact rational dense references, actual factor multiplicities and phase-read
  counts agree; every complete error bound is at most `2^-96`.
- Five rounded-interface controls, including declared phase aliases,
  insufficient precision and a later invalid coefficient. The latter does
  not promise rollback after earlier completed leaves.
- Nine comparisons against PR758's actual pinned all-arity optimizer and
  emitted words, including all three 50-factor results. This checks uniform
  prices and symbolic endpoints, not the full PR or its weighted claims.

These finite checks support the implementation. The general lower bound and
equality family use the written induction in PROOF.md. They are not a formal
verification of the full multiplication theorem. Generic rounded fixtures do
not supply prime-power coefficient preparation or a physical supplier.

## Broader repository check and environment boundary

One `make verify` run used an isolated checkout of the exact base with this
research directory added, avoiding regeneration in the contribution checkout.
It completed `verify-community`, `verify-producers`, `verify-partial-gauge`,
`verify-three-stage-cover`, `verify-paired-cube`, `verify-recycled-bit` and
`verify-entrance-banks`. After 560.319 seconds it stopped at `gen4-bank-verify`:

```text
ModuleNotFoundError: No module named 'sympy'
```

The selected frontier cold replay and later full-suite groups were not reached.
No full repository suite or supplier cold-replay pass is claimed. The new
package uses only the standard library; SymPy is an inherited repository
environment dependency. The expensive global suite was not relaunched.

A preliminary run on Apple's Python 3.9.6 exposed the pinned PR628 verifier's
`sys.set_int_max_str_digits` dependency. The documented minimum and early CLI
guard are therefore Python 3.11. Vendored source bytes were preserved.

The GitHub push initially rejected an optional CI workflow because the OAuth
token lacks `workflow` scope. That unsubmitted file was removed before
publication; the research package and its executable checks are unchanged.
No remote CI, Linux, Lean or independent human-review pass is claimed here.

Separate Codex workers checked the recurrence/proof, exhaustive and symbolic
evidence, rounded execution and the final implementation. Their review caught
the reference generator's `O((s+1)N)` dispatch charge, now explicit in PROOF.md.
This is substantial AI assistance, not independent human peer review.
