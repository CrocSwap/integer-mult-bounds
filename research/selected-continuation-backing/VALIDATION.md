# Local verification and review

Environment: macOS 27.0.1 arm64, CPython 3.12.15. Standard library only.
The configured Python 3.12 executable was
`/Users/nick/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`.
A separate optimized compatibility run used Homebrew CPython 3.14.8.

From the repository root:

```sh
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-continuation-backing --check-only
python3.12 -I -Werror -B scripts/research_package.py \
  --package research/selected-continuation-backing
python3.14 -I -O -Werror -B research/selected-continuation-backing/verify.py
python3.14 -I -O -Werror -B research/selected-continuation-backing/test_verify.py
python3.12 -I -Werror -B -m unittest discover -s tests -p 'test_research_*.py'
uvx ruff check research/selected-continuation-backing --select E4,E7,E9,F,I,UP,B,RUF
uvx ruff format --check research/selected-continuation-backing
```

Registered metadata/source-pin check passes. Normal and optimized registered
replays compare the complete typed RESULT.json; nine behavioral tests pass.
The research workflow suite passes 144 tests with seven platform-specific skips.
Scoped Ruff checks and formatting pass. No hosted-CI pass is claimed.

The initial arbitrary-warm fixture failed the reused predecessor's fresh-entry
backing assertion. The fixture adapter now explicitly permits the independent
warm-entry allowance while preserving the old live-symbol check and unchanged
runtime. A rejecting context entry also required explicit restoration of the
observers, since Python does not call `__exit__` when `__enter__` raises. Real
quota failure followed by a successful fresh replay tests that cleanup.

A separate internal reviewer derived the h+1 RETURN bound from the literal
source, checked partial pushes/reversal and sharpness, independently ran the
complete fixed receipt and the original eight tests on CPython 3.12.15, and
identified the warm-history and fixture-label qualifications now enforced.
The ninth test checks the latter: literal fixtures accept only binary modes,
R=3 and one call. Repeated and arbitrary-warm evidence uses the explicitly
synthetic step/preparation fixtures. This is internal review, not independent
human review or formal verification.

All new functions fit below 60 physical lines after standard formatting. The
new fixture loops have explicit domain bounds: six branch modes, depths 0..3
for the complete 524-history census, binary stress depths 4..6, two word regimes,
three literal fixtures, one/two evaluations and four entry extents <=1024.
The numerical and source tables are bounded predecessor fixtures. Existing
runtime loops and managed allocations retain their source contracts; no fixed
physical-heap implementation is inferred. The exact managed-runtime/source-
loading/observer deviations and compensating controls are in TASK.json.

Initial main was a7482490b4ca256db67d767a33fa6f7553060807. Submission refresh
found 3bee87dc2bbb012623ecece9df6b27c6d15706fb, with unchanged consumed
scientific inputs, priority revision 5, selected record and registered runner.
The changed current-status/review1900 navigation retains the frontier and
separates pending follow-ups. Complete refreshed metadata coverage at
11:38 through 11:39 UTC includes 495 open PRs, 2122 closed/merged PRs and 1601 Discussion
records, with no warning. Arbitrary diffs and unpublished work remain outside
that coverage. TASK.json preserves the exact timestamps and compatibility
comparison. Frozen inputs and the selected frontier are unchanged.

## Attention

Review capability: a separate read-only internal source/proof and verifier
review. Its concrete qualifications were incorporated. The local decision
trail records the failed warm test and metadata checks. No remaining blocking
flag was identified. The important scientific limits remain successful-call
premises, conditional grammar sharpness, B>A slack and the unjoined physical
reserve. No full selected supplier replay or formal-kernel proof was run.
