# Verification record

Base: canonical CrocSwap main `1ec1119972c9aefe42525172d07b332fcff81cb4`,
task catalogue revision 7. The selected-result record was resolved before work:
the selected bound remains κ = .0030217758 and its inherited assumptions.
This package changes no selected source, certificate or shared code.

Environment: macOS 26.5.1 arm64, CPython 3.12.8, standard library only.
Run from the repository root in the isolated `codex/qq16-caller-lifetime`
worktree. Scientific replay was serial. The successful original caller
calibration had a 240-second wall limit and sampled descendant-RSS limit of
1 GiB (0.5-second sampling); it completed in 130.369 seconds with sampled peak
59,504 KiB. See RESOURCE.json. Sampling is a resource guard, not a mathematical
space bound. The three rejecting runtime controls ran serially with individual
90-second subprocess timeouts and completed successfully; no RSS receipt was
recorded for those short rejecting runs.

Executed, all passing:

```sh
python3.12 -I -B research/qq16-restoration-root-closure/calibrate.py --output /tmp/qq16-lifetime-calibration.json
python3.12 -I -B research/qq16-restoration-root-closure/verify.py --runtime-controls --output /tmp/qq16-contract-controls.json
python3.12 -I -O -B research/qq16-restoration-root-closure/verify.py
python3.12 -B scripts/research_package.py --package research/qq16-restoration-root-closure --check-only
```

These are the manifest's verification commands, executed individually to
retain receipts. Do not rerun the original caller merely to repeat the same
evidence under a different wrapper. RESULT.json and CONTRACT.json retain their
deterministic receipts. The optimized run checks source contracts and four
source mutations; a second optimized full physical calibration was not run.
No Lean, Docker, unrelated historical suite or selected cold replay was run.
The original frozen loader's whole-repository authentication was not run;
the component adapter authenticates the exact archived runtime instead.

The written proof was cross-checked by an assisted source-audit worker with
shared context. This is not independent human or proof-kernel acceptance.

## Overlap and freshness

The live overlap helper refreshed 347 open PR bodies and 4,682 Discussion
records with complete reported pagination at 2026-10-23 21:58 UTC. Its sparse
local-note search covered zero of 7,267 tracked top-level notes: absence of
local matches carries no novelty implication. Relevant package sources and
the current Discussion 4744 lifecycle handoff were read separately. The
restoration constructor still names whole-caller retention as an open
obligation. The concurrent numerical constructor work is a distinct scope.

Pending source pins:

* [#5362](https://github.com/CrocSwap/integer-mult-bounds/pull/5362):
  `a9e5ab880bc006aa9366fc1d037ba4ad86132dd8`; constructor and proof exported
  verbatim with hashes in SOURCE-EXPORTS.json.
* [#5330](https://github.com/CrocSwap/integer-mult-bounds/pull/5330):
  `08057adb207d487cd782736e5912bf9296b17180`, merged at inspection.
* [#5371](https://github.com/CrocSwap/integer-mult-bounds/pull/5371):
  `3da48976b1518719dc2b5eb1afb16a398adec615`; inspected for overlap only,
  no theorem or replay dependency.

Full publication source-history checking requires a non-shallow clone and is
unavailable in this shallow checkout. Byte provenance, direct base ancestry
and commit-export checks are separate checks; none implies complete history.
The package only pins main's available base, and retains pending source bytes
locally rather than requiring a foreign pending commit in ancestry.
