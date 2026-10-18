# Validation of the PR615 family ceiling and rounding refinement

The frozen core package is `../complex-pr615-ceiling`, manifest SHA-256 `d5ab97aa2e30ed078117f2444350482dcca8a9de82450f9dc1e0deb4346112e9`. The source is PR615 at `bf8a49a34350599763cced8592db81dc62c2c1c0`.

| Check | Result |
|---|---|
| Fresh macOS Python 3.14.8 replay | 42 stages, 271.526 seconds |
| Fresh Linux aarch64 Python 3.14.8 replay | 42 stages, 313.749 seconds |
| Reused baseline or local results | None on either platform |
| Primary receipt verification | All 43 artifact hashes and 42 stage-log hashes checked on each platform |
| Exact ceiling | 92 pattern/remainder cases; rational inequalities; no solver dependency |
| Independent pattern enumeration | All 915 integer multisets of the five widths up to capacity 48 |
| Malformed-input controls | Five rejected under `python -I -O`; valid control accepted before and after |
| Outer refinement | Seven bootstrap steps and 47 strict constraints in each native/conservative model; next fine tick and three invalid slack settings rejected |
| Cross-platform agreement | Ceiling and refinement certificates byte-identical; RESULT differs only in elapsed time |

`macos/` and `linux/` retain the primary receipt artifacts and raw stage logs, supplemental exact certificates, and baseline receipts. `CROSS-PLATFORM.json` records the comparison. `SOURCE-REVIEW.json` records byte identity of the primary verifier and the scope of inherited source changes. `SHA256SUMS.json` seals this directory; it excludes itself.

The only arithmetic change in the inherited runtime is the final outer output grid and its next-tick rejection, from `10^-18` to `10^-24`. The independent refinement checker proves that these are the only two source-expression changes in `assemble.py`. Source directory declarations point to the bundled pinned files; their content contracts are unchanged. New supplemental checkers do not replace the primary replay.

Run the additional independent enumeration and rejection audit after a fresh core replay:

```sh
python3 -B research/complex-pr615-ceiling-validation/audit_ceiling.py \
  --package research/complex-pr615-ceiling \
  --work /tmp/pr615-ceiling-fresh \
  --out /tmp/pr615-ceiling-controls
```

## Search provenance and scope

`fork-select/` records a four-branch fresh-context search starting from the verified PR615 witness. Three branches retained the seed; branch 4 supplied the finer output grid and was selected by exact certified κ. Parent grading verified source/receipt identities and ran a strict selected-candidate replay. Branch 3 supplied integrity checks of inherited full-replay evidence, not a new complete replay. The selected branch itself and this final package each received separate fresh full replays. Nominal branch horizons were 480 seconds, with actual recorded completion times and three concurrent workers followed by the fourth. This was not an equal-compute efficiency experiment.

The selected branch continued after receiving the parent's independently derived ceiling as a new input. No losing-branch ideas were transferred. Its first continuation admitted no improved construction. A subsequent cold-end nomination failed the compensation eligibility condition and was not promoted to a result. Further continuation work is outside this frozen package.

The refined conditional κ is `0.001626010676080313339567`; it is a rounding refinement of PR615, not a new multiplication construction. PR617 subsequently claimed the larger `0.001635183729255778` using changed suppliers, which are outside this ceiling. That external construction subsequently passed a separate independent fresh 42-stage macOS replay and literal-map/exact-moment check. Its evidence is not part of this package; no global frontier record or unrestricted optimality is claimed here.

The native moment and inherited outer conversion are hypotheses of the ceiling. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape/exact recovery, analytic transfer, and bit H1-H5 assumptions remain conditional. The result is neither an unconditional multiplication theorem nor a complete Lean proof. The ceiling does not apply after changing these suppliers, the owner geometry, or the proof interface.

The new files pass the scoped whitespace check. The broad added-file check reports inherited trailing whitespace or final blank lines in pinned source files; these bytes are intentionally preserved to retain their provenance hashes.
