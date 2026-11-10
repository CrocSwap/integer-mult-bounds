# Exact paths and requested repositories in the proposed pin-edit guard

This completes the two source-reader repairs requested by the canonical intake
decision for [PR6319](https://github.com/CrocSwap/integer-mult-bounds/pull/6319),
reviewed head `b1cb8b91a7213d639da117a5ef3060afecd5058b`. The two failures were
already independently reproduced in that decision; they are not new discoveries
of this contribution. Main at `7c49fe32c55de02c2c873655c804b16e4c3fef0a` does
not yet contain the proposed script. This additive repair retains the original
guard and its six tests, with predecessor authorship intact.

## Repair

The original `blobs()` joins `revision:path` requests with LF for
`git cat-file --batch`. A valid filename containing LF becomes multiple
requests, so the old pinned bytes can appear absent and yield a false-clean
report. A pinner filename with LF can also desynchronize the response parser.

Ordinary requests retain the existing fast batch path. A request containing
CR or LF instead resolves its exact pathname through NUL-framed
`git --literal-pathspecs ls-tree -z --full-tree`. It checks the single returned
pathname and object ID, then reads a blob by that ASCII ID. Missing paths and
non-blob objects retain the old `None` behavior; unexpected Git failures
propagate rather than becoming clean reports. This uses no newer Git batching
option or new dependency.

The ordinary batch reader consumes each successful response's declared payload
and terminating newline before classifying its type. A directory that replaces
a pinning file is reported as removed, and the next response is still read at
its header. The committed-tree regression keeps a second stale pin after the
directory and requires exit 1 in both default and strict modes. Thanks to
[@antunishdPursuit](https://github.com/CrocSwap/integer-mult-bounds/pull/6357#issuecomment-6582649037)
for reproducing the false-clean report.

The original Git subprocesses inherit shell variables such as `GIT_DIR`, which
can select an unrelated clean repository despite `--root`. Every guard Git
read now uses the existing `research_package.git_source_env()` policy. This
removes inherited repository/index/object selectors and config injection while
preserving normal checkout and linked-worktree discovery. The parent process's
environment is unchanged. This adopts the shared policy; it is not a claim of
complete isolation from every Git configuration, executable or machine setting.

Pin classification, lowercase full SHA256 search, frozen-path prefixes and
default/advisory/`--strict` exit policy are unchanged. The guard remains a static
byte check, not mathematical replay, source admission or proof that an empty
report implies all frozen evidence is unchanged. Non-UTF8 paths, additional
digest formats and automatic gating of contribution PRs remain outside scope.

## Evidence and reproduction

The original script SHA256 is
`0b5ce60e4cfc0ddbfbc0c29c4dada278fa6e36dca913f643230edd9e753a404f`;
Git blob `36d06ea6b2435dc895f7b196fd526c063dcc7de5`. The six original tests
remain byte-identical, SHA256
`5e5aa240e16289a60417b41a553642fa2e43941729335a08d1b0a6a80a3a78f1`.
The exact intake decision is in `docs/research/pr-intake-decisions.json`,
blob `c39161eba92dfba20d053f820d2f87889dc3d4b3` at the base above.

With Python3.12 and Git, from the repository root:

```sh
python3.12 -I -W error -B tests/test_check_pinned_edits.py -v
python3.12 -I -O -W error -B tests/test_check_pinned_edits.py -v
python3.12 -I -W error -B tests/test_research_pinned_edits_paths.py -v
python3.12 -I -O -W error -B tests/test_research_pinned_edits_paths.py -v
```

The added suite constructs bare Git trees, so its LF/CRLF cases exercise stored
Git path bytes without depending on whether a host filesystem can create those
names. Expected pin rows and exit statuses come from explicit fixture
declarations, with separate blob-ID byte checks. It runs the actual CLI rather
than importing the guard. Cases include LF/CRLF/CR/Unicode names, literal glob
characters with a decoy, mixed ordinary and multiline requests, deleted targets,
stale/repinned/removed pinners, binary filtering, advisory/strict behavior, and
ambient repository/config redirection. It does not mock Git responses.
Deleting a referenced loose blob while retaining its tree entry also verifies
that a real failed blob read aborts instead of yielding a clean report.

The new filename matches the existing `test_research_*.py` CI discovery rule;
no workflow or automatic guard-gating policy is added. The predecessor source
is publicly reproducible at its exact head above. Before/after controls run the
same new tests against that byte-exact original in a private layout and against
the repaired candidate; the original fails the recorded source-reader cases.

## Open next questions

An independent reviewer should confirm that these exact changes resolve the
two intake obligations and preserve classification. Re-run the four commands
above, then compare the script with the pinned PR6319 source. Broader guard
admission and whether to run it automatically on real PR diffs remain maintainer
decisions. No PR is merged or closed and no selected or priority file changes.

## Credit

The original guard and six tests are Armin Pourshafeie / apoursh's work with
substantial Claude Code / Anthropic assistance. The intake review supplied both
counterexamples and the repair request. Arham Tahir's PR1595 and later exact-path
readers established newline-preserving source reads; Douglas Colkitt supplied
the source-pin/package design. The shared Git-source environment policy retains
its T74-2530 lineage. Sagar Thakrar and ywz65 supplied predecessor guards.
Existing source attribution is retained. New repairs and independent bare-object
regressions: ToikY with substantial OpenAI Codex assistance and bounded agents
for implementation, oracle tests and review. Apache-2.0.

Canonical coordination: [Discussion6356](https://github.com/CrocSwap/integer-mult-bounds/discussions/6356).
