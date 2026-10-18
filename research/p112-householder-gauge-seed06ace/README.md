# P112 ten-term Householder gauge cost screen

**Scoped negative result for one exact witness orbit. No new `κ` or supplier admission.**

## Result

The P112 symmetric ten-term decoder witness from open PR1633 has exact per-term binary support ranks `(8,8,8,8,8,8,8,8,9,9)`, total 82. This package exhausts every rational Householder term gauge

```text
O_s = I - 2 s s^T / (s^T s),
s ∈ {-1,0,1}^10 \ {0}, modulo s ~ -s.
```

The domain has 29,524 reflections. All preserve the ordinary-transpose P112 identity, all ten terms remain active, and the support invoices form only nine histograms. Every histogram uses ranks 8 and 9; the minimum total stays 82. The best candidate is just a signed-column reflection and retains the predecessor's `(8^8,9^2)` profile.

To screen the result, the candidate decoder replaces the selected profile's eight rank-8 centre children by its ten priced terms. Even waiving every coefficient, frame, precision, hosting, storage, and restoration expense, its best exact ceiling is

```text
0.000834274164361244 ≤ a_cap ≤ 0.000834274164361245
```

The selected fixed-word ceiling is `0.001690054109089`; its 5% acceptance target is `0.00177455681454345`. The entire searched family misses the target before any extra charge, so this route stops here. This does not rule out a different P112 witness, an asymmetric two-sided decoder, other coefficient choices, or another support family.

`RESULT.json` records all nine histograms, their exact ceiling intervals, candidate counts, and the best normal. `verify.py` regenerates and compares that receipt. It rebuilds the 112 roots, checks the base witness on all 12,544 ordered root pairs, proves each Householder numerator orthogonal by exact integer arithmetic, directly checks the best transformed identity, computes support ranks over F2, and runs five positive/failure controls. The ceiling calculation uses the pinned exact-rational interval implementation.

## Provenance and overlap

- Cycle seed `06ace58bfc2b63b47b02129f729e35d4`, track `complex-mechanisms`, task `complex-rank-shape-decoder`, priority revision 3. The card is marked **changed** in [TASK.json](TASK.json): the diagonal rank-16 batching route overlaps open PRs #1779/#1817 and their child-contract follow-up; this package tests the separate open overcomplete-decoder question.
- Exact base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. The actual selected review, source manifest and assembly certificate are pinned in [SOURCES.json](SOURCES.json); the selected reproduction command is `make frontier1094-verify`. The selected frontier remains untouched.
- The witness is extracted from Hanson Sun's open PR1633, head `652264fa1f70820139b2730363a0056b7fadc689`, `research/decoder-excess-rank/RESULT.json`, pinned by both Git blob and SHA-256 in `WITNESS.json` and [SOURCES.json](SOURCES.json). PR1633 proves the rank-one residual normal form and explicitly leaves support-aware ten-term copy optimization open. Its witness invoice 82 and dense-gauge control 90 are reproduced here. PR1224 supplies the earlier projection equations; PR1077 and PR968 supply the E8/Gaussian decoder conventions.
- The full overlap refresh at 2026-10-14 13:27 UTC covered 543 open PRs and 529 Discussion records with complete pagination and no warnings. The bounded scope claim is [Discussion #1622 comment 18925227](https://github.com/CrocSwap/integer-mult-bounds/discussions/1622#discussioncomment-18925227). The result is limited to this witness and this finite gauge family.

## Reproduce

From the repository root:

```sh
python3 -B research/p112-householder-gauge-seed06ace/verify.py
python3 scripts/research_package.py --package research/p112-householder-gauge-seed06ace --check-only
python3.12 scripts/research_package.py --package research/p112-householder-gauge-seed06ace
```

The direct verifier and metadata/source-pin check pass under the local Python 3.14.7. Python 3.12 is unavailable locally, so the registered Python 3.12 replay remains for CI/reviewer confirmation. A metadata pass checks package structure and pins; it is not a mathematical acceptance check.

## Open next questions

Can an asymmetric two-sided ten-term P112 decoder outside this symmetric witness orbit reduce the 64-rank copy bill? This remains relevant because a lower exact support profile could change the selected centre children. A feasible first step is to search the original term coordinates under the rank-one residual equations in [TASK.json](TASK.json), charging every term support before applying the selected ceiling. The unrestricted coefficient/support space and the absence of a native frame and precision invoice are the blockers.

## Credit

The exact witness and rank-normal-form predecessor are Hanson Sun / PR1633; earlier decoder equations are joaqcoo / PR1224, with E8 and Gaussian arithmetic from woklerx / PR1077 and themilkman216 / PR968. Prepared by Cinna Davis with substantial OpenAI Codex assistance in scoping, exact finite search, support-rank computation, ceiling screening, verifier implementation, and writing. No subagents or independent human review are claimed. New material is Apache-2.0.
