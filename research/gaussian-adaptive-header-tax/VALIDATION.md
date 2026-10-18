# Validation and coverage

Executed on Windows, 2026-10-15:

- Python 3.12.14 `-I -O -B verify.py --write RESULT.json`: full unchanged
  PR738 geometry plus new finite controls passed and produced the receipt.
- Python 3.12.14 registered package replay: passed. The first metadata attempt
  rejected an unsupported outcome spelling; it was corrected to the schema's
  `negative-result` before the successful scientific replay.
- Python 3.14.5 `-I -O -B verify.py` in a Git-free export containing only this
  package and its six declared inputs: passed with inherited PYTHONOPTIMIZE=2.
  The retained geometry still ran in an assertion-enabled child. Every file's
  SHA256 before/after matched, establishing read-only behavior for this run.
- The relocated entry point rejected a modified input source, an existing
  `--write` destination and an unknown option. Six scientific controls are
  recorded in RESULT.json and rerun by the default command.
- A separate Codex agent reviewed the full proof, including conditioning on
  the branch, varying payload counts, the full-span tariff, both entropy bounds
  and the expected/worst-case distinction; no remaining issue was reported.

The retained geometry check covers 2,579,856 unordered nonempty flat pairs.
New checks cover 4,096 adaptive inputs, 49,152 receiver observations and
2,621,440 conditional clique projections. The average illustrative invoice is
13, with realized costs 8, 12 and 16; the proved simplified floor is 26/3.
Finite examples do not replace the written all-width entropy proof. No hosted
CI, independent human review, native supplier or full selected cold replay is
claimed.

Initial source/selection base was0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2.
Before submission canonical main advanced to
b4560d9e7216f72b73c5aa940ac099c05e33ccf9, priority5. All changed guidance,
including the family expansion gate, was read. The branch was fast-forwarded;
the six scientific input blobs did not change. The contribution diff uses
b4560d9e as its base; SOURCES.json preserves historical scientific pins.

Overlap used the fully paginated 817-open-PR snapshot at16:31:22 UTC and the
1,239-Discussion-record snapshot at15:22:22 UTC, plus a fresh REST page of the
newest100 open PRs before submission. The Gaussian nonlinear fixed-support,
Hurwitz paid-header and PR2607 adaptive affine Eisenstein scopes were read.
No matching Gaussian prefix-payload/header-tax result was located. Discussion
freshness is bounded, and metadata search is not a novelty guarantee.

Claim and completion share the predecessor investigation:
https://github.com/CrocSwap/integer-mult-bounds/pull/888#issuecomment-6196956825

The final receipt comparator also rejects JSON Boolean/integer and float/integer
substitutions while accepting the unchanged parsed receipt. Scientific counts
and input bytes are unchanged by this type-preserving comparison.
