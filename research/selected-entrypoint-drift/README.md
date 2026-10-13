# Public restatements of the selected result drift from its record

**Research consolidation and tooling; no new κ.** No certificate, construction,
selected record or frontier changes. Base `9a16422bf8d0ebd3342c1156c33cb5703c6cb02a`.
Sprint track 95–99 (consolidation), assignment seed 98.

## Discrepancy

[`certificates/selected-result.json`](../../certificates/selected-result.json)
selects PR890 with PR589, κ = 1661957774647029/10^18 = 0.001661957774647029,
reviewed in [community-frontier890-review.md](../../docs/research/community-frontier890-review.md)
and reproduced by `make frontier890-verify`. README.md and current-status.md
agree. At the base commit, three other public entry points did not:

| File | Statement at base | Selected record |
|---|---|---|
| `CITATION.cff` | "The selected checkpoint is PR626 with PR543"; κ = 51110230636731/31250000000000000 = 0.001635527380375392 | PR890 with PR589; κ = 0.001661957774647029 |
| `CONTRIBUTING.md` | current maintainer review `community-frontier741-review.md`; cold replay "currently `make frontier741-verify`" | `community-frontier890-review.md`; `make frontier890-verify` |
| `CONTRIBUTORS.md` | "Current reviewed composition: #799 with #589, κ=0.001661634653669567" | #890 with #589, κ=0.001661957774647029 |

`CITATION.cff` is what GitHub's "Cite this repository" and citation tools
read. It was two selections stale and credited the PR543 bit supplier rather
than PR589 on PR555. A contributor following `CONTRIBUTING.md` would replay
#741, not the selected construction.

## The drift is recurrent

[`history.py`](history.py) applies the same binder, unchanged, to every one of
the 17 commits that changed the selected record, plus the base. It reads each
commit's files from git objects. Twelve of the 17 selection commits left at
least one restatement contradicting the record committed alongside it.

| Commit | Selected | κ | Contradicting restatements |
|---|---|---|---|
| `9a16422b` (base) | #890 | 0.001661957774647029 | CITATION.cff (PR, κ), CONTRIBUTING.md (review, replay), CONTRIBUTORS.md (PR, κ) |
| `3b83e4f1` | #890 | 0.001661957774647029 | CITATION.cff (PR, κ), CONTRIBUTING.md (review, replay), CONTRIBUTORS.md (PR, κ) |
| `d6dfd8f2` | #799 | 0.001661634653669567 | CITATION.cff (PR, κ), CONTRIBUTING.md (review, replay) |
| `c290b7b9` | #741 | 0.001661202643272239 | CITATION.cff (PR, κ) |
| `2cdd93d0` | #741 | 0.001661202643272239 | CITATION.cff (PR, κ) |
| `5c5567d1` | #626 | 0.001635527380375392 | CONTRIBUTING.md (review) |
| `2e9ed969` | #617 | 0.001635183729255778 | CONTRIBUTING.md (review) |
| `1db1fbe6` | #596 | 0.0016127213726553 | CONTRIBUTING.md (review) |
| `7f6ccd7e` | #588 | 0.001602278921983212 | CONTRIBUTING.md (review) |
| `270c2458` | #588 | 0.001602278921983212 | CONTRIBUTING.md (review) |
| `1c1e42f0` | #535 | 0.001584931111785787 | CITATION.cff (κ), CONTRIBUTING.md (review) |
| `a1e7d848` | #531 | 0.001517760977820331 | CITATION.cff (κ), CONTRIBUTING.md (review) |
| `91e29e7b` | gen4 | 0.000723571590007464 | CITATION.cff (κ), current-status.md (replay) |
| `27d82ebe`, `d697aaa7`, `86b30e03`, `e2a02cac`, `6aed8701` | #186 – #144 | — | none |

By file: CONTRIBUTING.md 9, CITATION.cff 7, CONTRIBUTORS.md 1,
current-status.md 1, README.md 0. Every contradiction above was inspected
against the commit's text; [`HISTORY.json`](HISTORY.json) records each
non-matching field. From `a1e7d848` through `5c5567d1`, CONTRIBUTING.md
pointed to `community-pr279-review.md`. Its older wording also named
`make gen4-bank-verify` as the "selected incremental target"; the binder
does not anchor on that phrase, so the table does not count it. At `91e29e7b`,
current-status.md still presented #186 and `make entrance-bank-verify`
after the gen4 record was selected.

"No anchor" is not agreement. Older wording often lacks the phrases the binder
uses (for example, CITATION.cff did not name a checkpoint PR before `7f6ccd7e`).
Those cells are reported as `missing` in HISTORY.json and are not counted
above. An earlier version of this replay misread README's `6.6188…\times10^{-4}`
form as a contradiction; the parser now handles it and a test covers it.

## Change

- `CITATION.cff`: checkpoint, κ, abstract lineage, release label and credits
  now follow the selected record, README and the #890 review. The version and
  date follow the existing `community-<audit>-<date>` pattern. The maintainer
  should confirm them; they cannot be derived from the record.
- `CONTRIBUTING.md`: current review and cold-replay pointers.
- `CONTRIBUTORS.md`: the headline names #890. The existing cumulative table is
  labelled as the SW4 and X4 rounds through #799, which it describes. No credit
  text was removed.
- [`scripts/verify_selected_entrypoints.py`](../../scripts/verify_selected_entrypoints.py)
  binds every restatement to the record. It complements
  `scripts/verify_selected_result.py`, which binds the record to its
  certificate and proof files.
- [`tests/test_selected_entrypoints.py`](../../tests/test_selected_entrypoints.py)
  is discovered by `make verify-tests`. No Makefile or workflow changes.

The binder checks 18 fields:

| Entry point | Fields bound to the record |
|---|---|
| README.md, first `## ` section | exact `\kappa=\frac{…}{…}`, its printed decimal, review link |
| current-status.md, first `# ` section | bold κ decimal, first `` `make …` ``, review and receipt links |
| CONTRIBUTORS.md, headline | "Current reviewed composition: #N", its κ, review link |
| CONTRIBUTING.md | `[current maintainer review](…)`, "currently `` `make …` ``" |
| CITATION.cff | "selected checkpoint is PRN", each `kappa = A/B = D` |
| selected-result.json | decimal equals κ exactly; `reproduce` is a Makefile target; `previous_record` κ equals `previous_kappa` |

The primary PR is not a field of the record. The binder derives it as the
unique `reviewed_dependency_heads` entry whose head equals
`audited_source_head`. This holds for every selection since #531. Decimals
are compared exactly as rationals, so a rounded decimal fails. A missing anchor
or file fails like a contradiction.

## Reproduce

From the repository root, Python 3.11+ standard library only:

```sh
python3 -I -B scripts/verify_selected_entrypoints.py
```

Expected: `PASS 18 selected-result restatements agree with certificates/selected-result.json: kappa 1661957774647029/1000000000000000000`.
On the base tree (`--root` pointing at a checkout of `9a16422b`), the same
command exits 1 with `FAIL 8 of 18`: eight non-matching fields in the three
files above. Further commands:

```sh
python3 -m unittest discover -s tests -p test_selected_entrypoints.py -v
python3 -I -B research/selected-entrypoint-drift/history.py --check
```

The history replay requires a non-shallow clone. It is pinned to the 17
selection commits and the base. It reruns the current binder, so changing the
binder requires regenerating `HISTORY.json` with `--write`.

## Negative controls

Seven tests run on a temporary copy of the entry points. They show:

- each stale base value is rejected with exactly the expected fields: the #626
  CITATION κ and PR, the #741 CONTRIBUTING review and replay, and the #799
  CONTRIBUTORS headline;
- a decimal rounded in its last digit, or a changed numerator, is rejected;
  an equal decimal with a trailing zero is accepted;
- `10^{18}` denominators and `\times10^{-k}` decimals parse, and a wrong
  exponent is rejected;
- a removed anchor or deleted file fails as `missing`;
- a stale status-page replay command is rejected;
- three record defects are each rejected: an undefined replay target, a
  `previous_kappa` that differs from its checkpoint, and an underivable
  primary PR caused by two heads equal to `audited_source_head`.

## Scope and open questions

The binder checks metadata consistency only. It does not replay, review or
certify the construction or κ. It also does not decide which result should
be selected: the record is treated as authoritative. Prose credit lists are not
mechanically checked. Fields that cannot be derived from the record, such as
the CITATION version and date, are not checked.

The binder anchors on current wording. Rewording an anchor makes the test fail
until the binder is updated. This is deliberate, because a silently skipped
anchor would allow the same drift. The maintainer may also call the binder from
`selected-record-check`. That was not done here, so that frontier replays do
not depend on documentation text.

Left unchanged and noted for the maintainer:

- `make verify` invokes `frontier741-verify`, not the selected
  `frontier890-verify`. This may be intentional for cost; CONTRIBUTING.md
  separately asks for the selected cold replay.
- The "Remaining priorities" list in `docs/research/pr-ledger.md` names
  October 12 items. The ledger's coverage of selected source PRs is the
  subject of navinor's open #867 and is not repeated here.

## Credit and disclosure

This work builds on Douglas Colkitt's `scripts/verify_selected_result.py` and
the maintainer's selection records and reviews. It is related to Mihir
Srivastava's #841, which binds primary-proof pointers to verified digests,
and to navinor's #867, which maps ledger coverage of selected source PRs.
Construction credit for the selected result is as recorded in the
[#890 review](../../docs/research/community-frontier890-review.md) and
[CONTRIBUTORS.md](../../CONTRIBUTORS.md).

Prepared by Ian Libânio with substantial AI assistance (Claude Opus 5.5,
Anthropic, via Claude Code). Apache-2.0. This is not independent human review.
