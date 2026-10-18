# PR #774 finite and formal coverage

The [review continuation](https://github.com/CrocSwap/integer-mult-bounds/pull/774#issuecomment-6160960125)
requests both finite and formal coverage of the constrained forest construction.
The reviewed construction is commit `50f8c366f27a9083e0655593a1be3d6810d1f053`,
whose complete diff from `66849e1475c930fd7732b1a0067ffee7e1e95f60` adds the
22 files below. The initial follow-up added CI and documentation. The later
upstream integration below adds verification and a credited written interface
argument; the construction, Lean proof, source hashes and frozen certificates
are unchanged.

## Coverage of the submitted package

| Files | Obligation and evidence |
| --- | --- |
| `construct.py`, `data/word.json.gz`, `data/recipe.json`, `data/optimum.json.gz`, `data/optimum-recipe.json` | `reproduce.py` rebuilds both words and recipes and compares canonical JSON. `verify.py` independently derives K from A/scatter/B, checks all 660 arbitrary-input columns and exact frame/COPY/ERASE paths, and checks all 7,140 non-tree cycle inequalities including seed-6 tie order. |
| `budget.py`, `data/budget.json` | Reconstruction compares the entire 724-state certificate. The independent `verify.cut_budget` recurrence returns 15,025 D XORs; literal replay attains this lower bound with cuts 5, 34, 39, 57, 78 and strict `64 F^3 B^2 < 2^104`. |
| `verify.py`, `test_verify.py`, `reproduce.py` | All 23 adversarial/positive tests pass, including wrong endpoints, pricing, provenance, source types, the 106-bit uncut failure and the cheaper out-of-class 15,023-XOR rewire. The CLI requires the selected circuit to attain the cut-class optimum. |
| `Forest.lean`, `lean-toolchain`, `data/lean-axioms.txt` | Lean 4.21.0 compiles the complete file. Its seven audited theorems cover linearity, reversal, ordered forest action and compensated injection for arbitrary helper/target inputs. Each reports only `propext` and `Quot.sound`; the fresh output matches the recorded axiom report. |
| `native.py`, `data/native-selected.json`, `data/native-unconstrained.json` | Fresh unchanged C++ checkers accept the original and selected circuits at 5/9/11 stages: 900/1,380/1,620 formal columns and 6/18/24 omitted-bridge controls. Missing restoration is frame-legal but fails every endpoint checker. The uncut calibration fails all three native 104-bit checks. Fresh receipts match the historical results after normalizing elapsed times and output-directory paths. |
| `PROOF.md` | The forest/dummy-root-tree bijection preserves cost including both target XORs. The cycle exchange argument proves the unconstrained minimum. The cut recurrence considers retain/cut for each child, conditioned on its retained ancestor; the fixed work-row forward lower bound plus an attaining literal replay certifies the restricted optimum. These are written arguments with exact finite checks, not Lean optimality theorems. |
| `SOURCES.json`, `CLAIM.json`, `VALIDATION.json`, `NOTICE.md`, `README.md` | All 14 pinned repository inputs match. The original validation is historical macOS evidence. Attribution, seed/search scope, concurrent #759 credit and the distinction between the unconstrained floor and the feasible cut optimum remain explicit. |

## Reproduction and execution status

Run from the repository root, using a fresh output directory outside it:

```sh
python3 -B research/r420-forest-cut-budget/reproduce.py --lean /path/to/lean-4.21.0/bin/lean
python3 -B research/r420-forest-cut-budget/native.py --out /fresh/selected --boost /path/containing/boost
python3 -B research/r420-forest-cut-budget/native.py --out /fresh/uncut --boost /path/containing/boost --candidate research/r420-forest-cut-budget/data/optimum.json.gz --recipe research/r420-forest-cut-budget/data/optimum-recipe.json --expect-prefix-rejection
```

The 2026-10-14 follow-up reran these checks locally on macOS arm64 with
Python 3.14.7, Apple clang 21.0.0, Boost 1.85.0 and Lean 4.21.0. The selected
record integrity check also passed. The
[CI workflow](../../.github/workflows/r420-forest-cut-budget.yml) requires
the same finite, formal and native coverage on Ubuntu 24.04 / Python 3.13,
with bounded runtimes, read-only permissions and retained revision/input
identities and receipts. A local pass does not establish a hosted Linux pass;
the Actions run for the checked revision supplies that evidence separately.

Hosted Linux coverage passed at `e1a23bbecf308368865d827febf185fc03a74546`:
[run 38681040914](https://github.com/anthonylei/integer-mult-bounds/actions/runs/38681040914).
All finite, Lean, native acceptance/rejection and unchanged-artifact steps
passed; the run retains its revision, file inventory, logs and receipts.

## Claim boundary

Lean proves the generic Boolean compensation identity and forest ordering.
It does not bind the concrete JSON word or prove MST/DP optimality, physical
frames, global invoices or multiplication. The executable checks supply the
concrete finite evidence. In particular, 15,025 is optimal only over cuts of
the fixed oriented seed-6 tree; the 15,023 rewire demonstrates the boundary.

Full changed-word hosted-parent/whole-owner reconstruction, maintained supplier
adoption of semantic D, global invoices and outer assembly remain open, as disclosed in
the original submission. Repository-wide verification and native replay of
the separate 15,023 scope-control word were not run. No new κ or completed
supplier admission follows from this coverage. This follow-up is Codex-assisted
verification and written review, not independent human peer review.

## Integration with refreshed upstream

Canonical `main` at `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` was merged
without conflicts in `ce12313f`. This brings in 1,817 upstream commits since
the scientific base `66849e1475c930fd7732b1a0067ffee7e1e95f60`. The original
R420 inputs and certificates remain the research baseline. The updated root
guidance has `priority_revision: 4`; the selected record is now #1094 with
PR589/555's R439 bit supplier, and the complex side binds the selected κ.
The selected record, manifest and review were read through its declared paths.
The pre-submission upstream check recorded at `2026-10-15T04:46:45Z` found the same canonical
head, selected record and priority revision.

The final live overlap search completed at `2026-10-15T04:47:26Z`, using
`target forest`, `cut budget`, `semantic D` and `H2-sem`: 527 open PRs,
1,022 discussion/comment/reply records and 1,537 local notes, with complete
remote pagination and no warnings. It searches titles/bodies/comments and
local notes, not arbitrary diffs, so it is not a novelty certificate. The
discussion start-here #1163 was read. Pending #794 at
`6be7364e0245c5a1c931cb1c43b3da991b755850` and #2191 at
`c368d1b1f59c28b7a837fd6d080bd57703266d2c`, plus discussion #1796's R439
hosted invoice, reinforce the distinction between a local identity, pricing
and supplier admission. Their changed circuits are not imported here.

| Upstream work | Decision for this PR |
| --- | --- |
| Oscar Fennell #759, `467b9da6fe130a12d0d6edda310cd6b0efd22a7e` | Retain the original credit for forest factoring and the 14,921 floor. Our additional result remains the 15,025 optimum over this fixed tree's budgeted cuts. |
| Scott Woolsey Biggart #733, `dfe84e09298abc5c5e0074afda59a821e10abfb4` | Its broader two-sided basis saves more ADDs. Preserve the narrower untouched-helper class and avoid an overall-record claim. |
| Gareth Davidson #915, `e9daefe320a0043000bd9746664ed02c3287d056` | R439 target compensation already exists. Defer a port until it answers a distinct precision or hosting question. |
| woklerx #1194, `2e39c98238f543d988f9efc1b076590a4b780dca`; Arham Tahir #1311, `a2875c1834b9c9ef42a84eda4890d5462cc98fa5` | Apply their chronological semantic-D bridge to the frozen R420 word. Document its conditional proof and execute the original checker on the actual and virtual words. |
| Aaron Wang #1782, `1cfe5e10ce38b04209699c1a6b0e62b87e21833f`; Wentao Li (@VictorLiwentao) #1805, `b34e0620bd92af49c9095e0eeb885f601fffd137` | Keep semantic admission, actual local price and full hosted adoption separate. Do not treat endpoint equality as an integer-prefix bound. |

The merge exposed one replay failure: `certificates/selected-result.json`
now contains #1094. `reproduce.check_source_pins` explicitly resolves that
historical input to `certificates/checkpoints/k492626.json`, whose SHA256 is
the original `b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53`.
No expected hash changes. Missing or corrupt checkpoints fail without a
fallback to the live selection. CI watches the actual checkpoint dependency.

| Added check | Coverage and limitation |
| --- | --- |
| `test_reproduce.py` (4 tests) | A newer live selection stays untouched; missing/corrupt historical checkpoints and changes to each of the other 13 pinned inputs fail. |
| `test_budget.py` (4 tests) | Independently reconstructs unsigned reverse-tail magnitudes and literally executes every cut assignment for 620 recorded states with at most eight descendant edges: 7,904 assignments, 44 infeasible states and 62 states requiring cuts. Checks minimum cost and attaining witnesses; rejects underpricing, false infeasibility and a nonattaining witness. It imports no recurrence and makes no exhaustive claim about the remaining 104 states. |
| `test_semantic_bridge.py` (6 tests) | Pins the original source/checker, reports the two exact legacy syntactic failures, checks the original-D splice, all 660 dirty boundary columns and frames, and unchanged complete paths/profile. Missing restoration, cancelling illegal frame changes and cancelling target feedback are rejected. This applies #1194/#1311; it does not formalize their bridge in Lean or rebuild hosting. |

All 37 tests run through the bounded reproduction command. The frozen
15,025-XOR word, 724-state certificate and Lean file remain unchanged. The
small exhaustive oracle supplements the two complete recurrences; it does
not replace their full fixed-tree optimality argument. See the README's
**Open next questions** for bounded follow-ups.

Post-merge verification passed on macOS arm64 with the same Python/Clang/
Boost/Lean versions listed above: combined reconstruction and all 37 tests,
seven Lean axiom reports, selected and uncut native modes at 5/9/11 stages,
`scripts/verify_selected_result.py`, `scripts/research_baseline.py`, Python
syntax, actionlint 1.7.12 and `git diff --check`. The baseline command checks
selected bindings/arithmetic only. Both new mathematical suites also pass
under Python `-O`, and an independent Codex read-through found no concrete
bugs. All original data, source hashes, claim, validation and Lean files were
compared byte-for-byte with the original submission. No current-frontier cold
replay or whole-repository suite was run: this PR does not change that supplier.
