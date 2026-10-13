# Required evidence coverage for public frontier replay

Tooling integration; no new kappa or mathematical construction.

[Lucas's PR838](https://github.com/CrocSwap/integer-mult-bounds/pull/838), at
`2a50020bb9564229874cbfbdc112e17b235bacfc`, identified a receipt-coverage gap:
the PR741 composition checker accepts an unrelated successful stage in place
of a required stage, or an omitted artifact when its receipt entry is omitted
too. Its existing checks validate the hashes of listed evidence, but do not
require the producer's complete inventory. PR799 uses that checker for ancestry.

The public `make frontier741-verify` and `make frontier799-verify` commands and
both frontier CI workflows now use `scripts/verify_frontier_replay.py`. It
requires the frozen PR741 producer's 22 ordered stages, all 44 artifact paths,
and agreement between the receipt and `STAGES.json`, then applies every
historical composition check, including file/log hashes and path containment.
The inventory comes from the producer and retained complete run, not the
candidate receipt. A regression checks agreement with the producer's 34 fixed
outputs and its ten local outputs.

The entrypoint checks reused ancestry before starting a supplier. After a cold
run it checks ancestry again, before writing the public completion record.
The implementation delegates construction to the existing scripts; it does not
copy or change their mathematics, source packages, selected records or proof
hashes. Existing historical script entrypoints retain their historical checks.

## Commands and output layout

```sh
python3 -B -m unittest discover -s tests -p 'test_frontier_replay_coverage.py' -v
make frontier799-verify
```

For an explicit output directory, which must be fresh and outside the repository:

```sh
python3 -B scripts/verify_frontier_replay.py --frontier 799 --work /tmp/frontier-run
```

`/tmp/frontier-run/replay/` contains the historical script's logs and output.
Only `/tmp/frontier-run/RESULT.json` marks successful completion of the public
entrypoint. It retains the historical result fields and adds receipt coverage
counts. Expected final output for the base selection:

```text
PASS_COMPLETE_REPLAY_RECEIPT_COVERAGE 0.001661634653669567
```

To reuse a complete PR741 run, add `--ancestor /path/to/pr741`. That directory
must contain `bit/` and `complex/`; for output from this new entrypoint, use its
`replay/` subdirectory. Incomplete reuse is rejected before creating the output
directory. Construction failure or failed postflight coverage leaves no public
top-level `RESULT.json`; diagnostic files may remain in `replay/`.

## Scope and attribution

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The source contract is
`research/complex-sw4-frame8/verify.py` and its retained complete archive
`research/community-queue-20261013/pr741-fresh-replay.tar.gz` at that commit.
Changing that producer's coverage requires reviewing this contract and tests.

Validation on Linux CPython 3.12.15 in a network-disabled, read-only Docker
container: all 11 new tests pass, the existing PR741/PR799 binding suites pass,
and the selected-record integrity check passes with its original hashes. Tests
physically delete each of the 44 artifacts and reproduce historical acceptance
of representative coherently rehashed omissions. Publication tests substitute
only the expensive subprocess boundary and validate real archived evidence;
they are not fresh native construction runs. A fresh full cold replay and
hosted CI are not claimed as locally completed; the updated workflows perform
the full cold replay when run.

This closes omission acceptance in the public entrypoint. It does not
authenticate a fabricated log, establish that an arbitrary receipt records
an actual execution, or replace mathematical certificate replay. It does not
audit all PR799 evidence or prove the full multiplication theorem. Inherited
realization, all-size, hosting, precision/tape and analytic assumptions remain.

Credit Lucas (@ljste) for PR838's finding and supplemental coverage predicate;
Douglas Colkitt for the composition checkers and retained replays; Chafik
Boukhalfa for PR741; and DreamingOfClouds and eumemic for PR589/PR555 and their
retained predecessors. Production integration and regression tests by
Chinmay (@chinmayarvind23), with substantial OpenAI Codex assistance, under
Apache-2.0. This is a follow-up to PR838, not an independent discovery.

## Integrated entrypoint

PR865 independently extends this PR847 design with version-pinned contracts,
selected-result/log checks and package controls. Standard Make/CI commands use
`verify_frontier_complete.py`, including Adem Vessell's PR851 bridge-ID checks
in an external adapter. This PR847 implementation and regression tests remain
available and credited. The historical pinned bindings remain unchanged.
