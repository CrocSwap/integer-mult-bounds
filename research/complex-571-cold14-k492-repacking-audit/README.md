# Contributor evidence: PR622 owner repacking

This directory records a repacking of PR622 at `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`. The source package is the sibling `complex-571-cold14-k492`. This is contributor validation awaiting independent review, with all inherited conditional assumptions retained.

`PREDECESSOR-RESULT.json` and `PREDECESSOR-RECEIPT.json` record an independent fresh 64-stage replay of unchanged PR622. The new witness's result, receipt, raw stage logs and validation record are retained separately. `SOURCE-REVIEW.json` checks every unchanged inherited file, including all verifier code, atom inputs, recipes and source contracts. `EXPORT-CONTROLS.json` records exact nomination reproduction and five rejection controls. `SHA256SUMS.json` binds every retained file in this directory except itself.

## Verification scope

The new package is admitted by its unchanged default-SPEC verifier, with every provider rebuilt from pinned sources and no reused baseline or provider outputs. Both exact moment engines and the strict outer assembly are checked. The package's `OWNER-REPACKING.md` gives the commands and immutable dependencies.

`SHARED-MAKE-VERIFY.log.gz` retains the passing full repository suite, including 84 isolated test modules, the gen4 checkpoint and historical patch checks. **That broad run used the earlier PR617 repacking worktree**, identified in `SHARED-REGRESSION-SCOPE.json`; it was not rerun on this PR622 worktree. All tracked Makefile, scripts, tests and other shared infrastructure files are identical between the two base commits. The only inherited differences are the standalone b3 and k492 packages, which those entrypoints do not invoke. The new k492 package has its separate fresh replay, including the inherited generalized-R and R504 checks. This explicit split avoids claiming tests ran on a checkout where they did not.

## Search reproduction

The portable reconstruction route is the package's standard-library `tools/replay_repacking.py`, using its recorded simultaneous moves and the pinned original PR622 data. The final exporter compares PLAN bytes and decompressed owner content; a regenerated gzip stream need not have identical container bytes across platforms.

`search/` contains the as-run discovery scripts, settings/results and the successful intermediate map. Intermediate PLAN files are compressed as `PLAN.json.gz`; decompress them before using a retained directory as `--data` or `--candidate`.

```sh
python3 anneal_owner_pair_swaps.py --data /path/to/pr622/data \
  --out /tmp/pairs0 --trials 3000000 --seed 0 --temperature 1
python3 minimize_owner_profile_delta.py --base /path/to/pr622/data \
  --candidate /tmp/pairs0 --out /tmp/minimal --seconds 60
```

The annealer sometimes exchanges two helpers from each owner simultaneously. Every proposal preserves whole helpers, capacity, windows and family uniqueness. Floating entropy guides discovery, not admission. The minimizer uses OR-Tools 9.15.6755 to choose each changed helper's original or proposed owner while preserving the global spare-rank profile. The timed solve reduces 11,626 changed placements to 5,027; a subsequent optimum is only over those retained choices, not all physical owner maps. The final nomination recipe records the selected map independently of solver timing.

A three-million-trial single-helper search and a ten-million-trial pair-search continuation found no additional gain; their summaries are retained. The exploratory scripts are not used by the verifier. All mandatory admission checks are in the unchanged source package.

Prepared by Jeremy Diviney with OpenAI Codex assistance, on Python 3.12.3 / Linux x86_64. Supplier and verifier construction credit remains with jeremykothe2, DreamingOfClouds and the predecessors named in the package NOTICE. No K-triangle construction or verifier generalization is attributed to this owner repacking.
