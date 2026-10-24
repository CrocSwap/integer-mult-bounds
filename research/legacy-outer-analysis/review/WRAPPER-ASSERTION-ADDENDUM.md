# Child assertion control

The wrapper fix passes independent review. This addendum covers only
verify.py. The mathematical proofs and frozen check inputs are unchanged.

An isolated parent process ignores PYTHONOPTIMIZE for its own flags.
However, that variable remains in os.environ. A child started with only
`-B` would use it and could disable its assertions. The wrapper now copies
the environment, removes PYTHONOPTIMIZE, and passes that environment to
each of the six child calls. The parent's explicit optimized-mode refusal
is unchanged.

I inspected the fix and ran check_child_assertions.py with the exact
package wrapper. The test starts an isolated parent with
`PYTHONOPTIMIZE=1`. It replaces each mathematical child with a short
assertion-state probe while keeping the production command flags,
working directory, environment, timeout, and result handling. Each of
the six probes reported assertions enabled, optimize level zero, and no
PYTHONOPTIMIZE variable.

The negative control removes only the environment cleanup from an
in-memory copy of the wrapper source. The first child then reports
optimize level one and fails with ASSERTIONS_DISABLED. The production
wrapper rejects that nonzero exit. Neither control changes package files.

The commands ran from the project root:

```sh
env PYTHONOPTIMIZE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 -I -B \
  work/project-final-cleanup-20261022/reviews/outer-analysis/check_child_assertions.py \
  work/project-final-cleanup-20261022/legacy-audit/packages/legacy-outer-analysis \
  work/project-final-cleanup-20261022/reviews/outer-analysis/wrapper-assertion-positive

env PYTHONOPTIMIZE=1 /opt/homebrew/opt/python@3.14/bin/python3.14 -I -B \
  work/project-final-cleanup-20261022/reviews/outer-analysis/check_child_assertions.py \
  work/project-final-cleanup-20261022/legacy-audit/packages/legacy-outer-analysis \
  work/project-final-cleanup-20261022/reviews/outer-analysis/wrapper-assertion-negative \
  --omit-cleanup
```

Both controls exited zero with PASS_WRAPPER_ASSERTION_CONTROL. These are
instrumented wrapper controls, not new mathematical replays. In particular,
the wrapper's success line in the positive control is not evidence of a
second six-check mathematical run. The original successful mathematical
replay remains in fresh-run/. No heavy check was repeated for this review.

The corrected wrapper has SHA-256
`7e04578997d2f9f48e3723ca91c301a92585cdc63cd2499d5fb9414dc124ee88`.
The two JSON receipts contain each dispatched command and actual child
result. CHECKED-FILES-AFTER.json and REVIEW-STATUS.json bind the current
files. No material review finding remains.

The package owner then ran all six mathematical checks again with
PYTHONOPTIMIZE=1 and an isolated parent. I checked all 18 saved evidence
hashes, the six successful exits, the wrapper and source-manifest hashes,
and the RUN.json contents. The five mathematical JSON receipts and the
Newton output match my original independent replay after exclusion of
timing, memory, free-space, and output-path fields. This is a check of the
owner's new replay evidence, not a claim that I ran that replay. The result
is in FINAL-PACKAGE-RECEIPT-CHECK.json.

The final CHECKED-FILES-AFTER.json covers all package files except the
top-level review/ and publication-review/ directories. Those directories
contain copies of review metadata. They are excluded to prevent a manifest
from binding an old copy of itself. The mathematical files, driver,
documentation, source manifests, and all replay evidence are included.

Prepared by the independent OpenAI Codex review agent. This is not human
review or formal proof verification.
