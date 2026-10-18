# PR1 source and credit retention receipt

**Research consolidation; no new kappa.** All eleven changed paths of Aurel Prosz
(Paureel)'s [#1](https://github.com/CrocSwap/integer-mult-bounds/pull/1)
(`bfb168a5611c9eb219d04cf7d551edf1517ecd78`, "Refine paired parameters and
derive the fixed-exponent supremum") are authenticated at that exact head against
live GitHub blob identities and disposed exactly at base
`d8e0f83f00191df62174b641e9fff055c357f641`, with a hunk-exact added-line
survival analysis and an audit of the existing `historical-credit-retained`
receipt (`research/overnight-pr-review-20261009/dispositions.json` record 1).
PR1's content is **not retained** at base; its credit **is retained** and its
authors verified against live GitHub metadata.

## Verdict

1. **Content: not integrated, zero substantive surviving lines.** Of PR1's
   2,050 added lines, exactly nine occur as lines of the corresponding file at
   base, and all nine are blank lines or `$$` display-math delimiters. The six
   new artifacts (1,968 lines: the paired-tuned certificate, the tuned-parameter
   document, the `h50-paired-tuned` patch and its three scripts/tests) are
   absent at base, and none has a byte-identical copy anywhere in the base tree
   (their git blob SHA-1 values are absent from the exact 81,016-path
   `git ls-tree -r` enumeration). The five shared files
   (`CITATION.cff`, `Makefile`, `NOTICE`, `README.md`, `docs/reproducibility.md`)
   are present but differ from their PR1 head versions. The claimed value
   `kappa = 1.7523184e-18` survives only inside claim-metadata records (an exact
   `git grep -l 1.7523184` enumeration finds six queue/leaderboard snapshots;
   observation recorded here, not replayed by `verify.py`).
2. **Credit: retained and verified.** `CONTRIBUTORS.md` carries the row
   "Aurel Prosz (Paureel) | #1 | Parameter refinement and a scoped
   fixed-exponent supremum"; `NOTICE` mentions Aurel Prosz/Paureel seven times;
   `README.md` credits "Aurel Prosz (Paureel) and Swapnil Jain"; 191 tracked
   files mention Paureel/Aurel Prosz (exact `git grep -l` enumeration, pinned).
   Live ground truth at 2026-10-16: `gh pr view 1 --json author,title` reports
   author login `Paureel` and the title recorded here; the head is unchanged
   since the 2026-10-09 inventory (`fetched_head == snapshot_head == head`,
   `head_changed: false`).
3. **The one dropped attribution is a documented convention, not silent loss.**
   PR1 added a `family-names: Prosz / given-names: Aurel` author entry to
   `CITATION.cff`; that entry does not survive. Base `CITATION.cff` states
   "Project-level authorship identifies the maintainer, not sole authorship of
   the mathematical result" and lists only the maintainer, while the individual
   credit lives in `CONTRIBUTORS.md`/`NOTICE`/`README.md` as in verdict 2. No
   repair is proposed here.

Per the card's acceptance gate: complete integration is empty (the PR1 head is
not an ancestor of the baseline), partial retention is exactly the nine
non-substantive lines above, and the reviewed head is unchanged. This receipt
makes no autonomous closure: the ledger keeps PR1 `partially_reviewed` with
`integration_location: []`.

## Exact sources and coverage

| Role | Commit and path |
|---|---|
| PR1 head | `bfb168a5611c9eb219d04cf7d551edf1517ecd78` (live, unchanged since 2026-10-09) |
| Base commit | `d8e0f83f00191df62174b641e9fff055c357f641` |
| Live REST record | `inputs/pr1-files-api.json` (path, blob SHA-1, status, additions/deletions, patch per file) |
| Vendored head bytes | `inputs/PR1-HEAD/` (eleven files; each recomputed git blob SHA-1 equals its REST identity) |
| Base-tree enumeration | `inputs/head-tree.txt` (exact `git ls-tree -r`, 81,016 paths) |
| Credit enumeration | `inputs/credit-mentions.txt` (exact `git grep -l`, 191 tracked files) |
| Review records | `research/overnight-pr-review-20261009/dispositions.json` record 1 and `source-inventory.json` entry 1 |

Per-path disposition at base (head SHA-256 and base SHA-256 are in
[RESULT.json](RESULT.json)):

| PR1 path | status | added | surviving | base state |
|---|---|---:|---:|---|
| CITATION.cff | modified | 5 | 0 | present, differs |
| Makefile | modified | 3 | 0 | present, differs |
| NOTICE | modified | 5 | 1 (blank line) | present, differs |
| README.md | modified | 52 | 8 (blank lines and `$$`) | present, differs |
| certificates/paired-tuned-parameters.json | added | 190 | 0 | absent |
| docs/paired-tuned-parameters.md | added | 372 | 0 | absent |
| docs/reproducibility.md | modified | 10 | 0 | present, differs |
| patches/h50-paired-tuned.patch | added | 898 | 0 | absent |
| scripts/make_tuned_paired_patch.py | added | 99 | 0 | absent |
| scripts/tune_paired_parameters.py | added | 236 | 0 | absent |
| tests/test_tuned_paired_parameters.py | added | 180 | 0 | absent |

The hunk-exact parser's added-line count equals the REST `additions` field for
every one of the eleven files (including 898 for the patch file, where a naive
`+`-prefix scan undercounts seven in-diff `+++` content lines).

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/pr1-retention-receipt
```

Expected output includes:

```text
PASS_PR1_RETENTION_RECEIPT paths=11 added=2050 surviving=9 substantive_surviving=0 copies_in_base_tree=0 credit_files=191
Ran 13 tests
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/pr1-retention-receipt outcome=completed
```

The direct `python3 -I -O -B research/pr1-retention-receipt/verify.py` command
needs neither Git nor network access: it reads only this package and the nine
immutable repository inputs listed in [VERIFY.json](VERIFY.json). To recollect
the live evidence (network and Git required), run
`python3 -I -B research/pr1-retention-receipt/collect.py`. Live author and head
metadata are re-checked with `gh pr view 1 --json author,title,headRefOid`.

## Task and overlap

Assigned by `scripts/choose_research_task.py` without rerolling (OS-random seed
`e8e1a0db1495c32197a3b4cf86a76225`, track `consolidation`, task
`overlap-receipt`, scope key `757723e3fd38f20fa774`, priority revision 6),
scope **unchanged**, refined to one small named PR set: PR1's eleven paths and
their credit rows. PR1 is one member of the named
"partially_reviewed starting-snapshot PRs with empty `integration_location`"
family not yet closed by `research/pr99-retention-seed99`,
`research/pr148-source-retention`, `research/pr203-retention-receipt` or
`research/pr211-retention-receipt`. Live board check at entry (discussions 1317
and 1166, nested replies included) found no claim on PR1's receipt object; the
narrow OR-mode overlap search matched only PR1 itself, seven credit mentions and
the ledger row. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18984023)
was posted before package implementation.

## Open next questions

- **Do PR1's six distinctive artifacts feed any retained downstream package
  under another name?** This matters because a downstream embedding without
  naming PR1 would justify an `integration_location` entry instead of the empty
  list. First step: a content-similarity search over retained research trees,
  beyond the exact-byte search done here. Blocked by: adapted-content reuse is
  invisible to exact hashing, and what counts as adoption needs maintainer
  guidance.
- **Does the fixed-exponent supremum claim survive the later two-stage topology
  and endpoint-copy work?** This matters for whether PR1's mathematical content
  still adds anything. First step: compare PR1's supremum proof with the PR29
  lineage it is said to feed and state the precise surviving statement. Blocked
  by: it is a mathematical review outside this source-and-credit receipt.

## Credit

Aurel Prosz ([Paureel](https://github.com/Paureel)) supplied PR1's paired
parameter refinement and scoped fixed-exponent supremum; the original
construction and manuscript attribution is Douglas Colkitt's, and the downstream
two-stage topology, copied-center and endpoint lineage is credited in `NOTICE`
to Zhihao Chen, Swapnil Jain, Rohan Arun, eumemic and the retained predecessors
named there. The 2026-10-09 overnight review (record 1) and the maintainer
ledger are the audited predecessor receipts; `research/pr148-source-retention`,
`research/pr99-retention-seed99`, `research/pr203-retention-receipt` and
`research/pr211-retention-receipt` (steph4n) established the receipt pattern
this package follows.

Prepared by **Aaron Wang**, with help from opencode (substantial AI assistance;
no model named; no independent human review claimed). Apache-2.0. Predecessor
licenses and notices remain in force.
