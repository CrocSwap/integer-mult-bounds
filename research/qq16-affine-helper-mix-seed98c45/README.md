# QQ16 mixed affine helper obstruction

**Scoped negative result; no supplier or kappa claim.** One added 8-coordinate
affine helper `H + B0 X_U + M B2 X_U + c` cannot restore all original
selected inputs under the fixed QQ16 `F0/B1` pair and retained schedule, for
any rational 8x8 mixer `M`. The proof converts the exact three-query rank
bound from PR #2104 into an all-mixer kernel bound. The helper and every
operation needed to implement or restore it are granted free, yet the
observations remain noninjective.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/qq16-affine-helper-mix-seed98c45/verify.py
python3 scripts/research_package.py --package research/qq16-affine-helper-mix-seed98c45 --check-only
```

Expected direct result: `PASS_QQ16_AFFINE_HELPER_MIX cases=4 positives=4 controls=3 no_new_kappa`.
Expected metadata result: `PASS_PACKAGE_METADATA_AND_PINS (not a mathematical acceptance check)`.
Registered replay uses Python 3.12; hosted CI is the runtime check if that
interpreter is unavailable locally.

The exact route lemma is pinned to PR #2104 head
`4bdc574da394a39f955e8cf4637075649c43a632`, `PROOF.md` SHA-256
`9c2ad4600d65dd3354db4bae5ac78d13fedf2da6e500224fafaeed596846c887`.
Its source-specific verifier ran locally on Python 3.14 against the exact
base. At the last successful status check at 19:52Z, that PR was open with
hosted checks pending; the later refresh hit the GitHub API rate limit, so
current hosted status is unverified. Full argument and scope limits are in
[PROOF.md](PROOF.md); original source and selected witness remain unchanged.

## Attribution and limits

Credit Ali Romman and PR #1969 for the QQ16 maps and selected witness; Cinna
Davis PR #2104 for the source-bound three-query rank result; Cinna Davis PR
#2079 for the B2-only observation this result extends. Adam Gall PR #2093 and
#2086 address related but different observation/logger cases. Prepared with
substantial OpenAI Codex assistance. No independent human or formal-kernel
review is claimed.

## Open next questions

- **Can a second independent ordinary-to-selected record restore injectivity?**
  The row-count cap used here would no longer apply. Specify the second source
  and compute the joint kernel before native synthesis.
- **Can one changed ordinary-tail map retain the erased selected value?**
  Derive its inverse and observations before expanding the controller.
