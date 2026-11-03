# Source-reference intake for research overlap

A dedicated `scripts/find_source_overlap.py` CLI accepts reference queries
and filters PR bodies by author and creation date. This makes an account's recent work
on a proposed source visible directly in the fetched body corpus. Missing
filter metadata produces an explicit error, so an old cache cannot silently
hide a possible lead.

Claim type: workflow tooling with behavioral regression evidence. This
contribution was produced by Nick Petalas. No mathematical bound, kappa
improvement or predecessor-result verification is claimed.

## Use

From the repository root:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/find_source_overlap.py \
  --reference 6537 --pr-author petalas --created-since 2026-10-27 \
  --include-closed --cache /tmp/source-overlap.json
```

Use the actual source number, login and UTC cutoff. `--reference` is
repeatable and applies identifier boundaries to numeric terms. Hashes and
decimal substrings cannot displace a real reference. Positional terms retain
their literal search semantics. The date filter uses creation, not update,
and includes the cutoff day's midnight UTC.

The dedicated intake CLI searches PR titles and bodies only. Closed/merged
bodies require `--include-closed`, with separate coverage and timestamps.
Local notes and Discussions are excluded. The existing `scripts/find_overlap.py`
remains byte-identical to the PR base; its functions are imported without
mutation. A filtered online query refreshes legacy PR metadata. An offline
cache missing the requested fields fails with an explanation.
`--pr-author` takes a login, rather than `@me` or a search expression.

## Evidence and reproduction

Eleven new regression groups cover identifier noise and spelling, literal
queries, inclusive dates and author case, optional closed bodies, legacy
offline errors, invalid metadata, creation/update separation, selective
online refresh and invalid CLI input. The existing 37 overlap groups also
pass. The registered replay runs all 48 groups in normal and optimized
Python, without network access.

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/source-reference-intake
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/source-reference-intake/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/source-reference-intake --check-source-history
```

Expected: `Ran 48 tests`, `OK`, `PASS_SOURCE_REFERENCE_INTAKE` and the
registered package PASS. [VALIDATION.json](VALIDATION.json) is generated
evidence bound to the tested script/test hashes. Default replay writes
nothing persistent. `verify.py --write NEW_PATH` records a fresh execution
and refuses to overwrite an existing path.

The dedicated CLI's offline query over the retained 587-open-PR snapshot,
fetched at 2026-11-03T14:10:56.715135+00:00, returned PR6571 as a source-6537 lead.
This only establishes the tool's retrieval behavior on that snapshot.
Neither its mathematics nor the source's result was evaluated. The eleven
synthetic regression groups make the behavior reproducible offline.

## Limits

Reference text is an overlap lead, not evidence of semantic novelty or
duplication. Work can share a model without citing its source. Current
claims, package questions and merged work still need inspection. Queries
do not provide an atomic server snapshot or a seven-day policy decision.
No selected frontier or frozen research package changes.

## Open next questions

Could a separately scoped provenance index also surface uncited package
reuse? First compare exact package-path references in PR bodies with a
complete changed-path inventory. Missing citations, renamed packages and
semantic equivalence remain blockers; they must not become automatic
novelty claims.

## Implementation and credit

The new filters traverse finite cached PR lists and validate dates before
comparing them. Unknown author/date values fail explicitly. The dedicated
CLI reuses the existing normalizer, identifier matcher, atomic cache writer
and PR deduplication functions. Its own PR-only cache refresh retains author
and creation metadata and preserves older evidence on failed publication.
The existing CLI and every other research package remain untouched.

Power of Ten rule 3 deviation: the Python cache/search command
allocates lists and dictionaries at runtime. The new pass adds linear
storage in the existing validated PR corpus size. A fixed-capacity service
port would require a separately declared corpus-size contract. Rule 9
deviation: unittest dispatch and mocks use their fixed test callbacks.
The replay runs one fixed subprocess with a 90-second timeout. Warning-strict
normal/optimized execution, AST compilation and the full affected suite
provide diagnostics; Ruff is unavailable in the prescribed environment.

Douglas Colkitt's overlap helper and its credited repository contributors
retain their attribution. Existing identifier matching and cache/pagination
machinery are reused. The new dedicated query and metadata filters, regression
fixtures and integration notes were produced by Nick Petalas. Apache-2.0.
Independent human review is unclaimed.

## CI compatibility repair

At head `e55541991331d578d88660dcbb34af60506a534d`, the initial hosted run
passed this package and four other jobs, but the historical overlap-path-index
replay failed with `source blob provenance mismatch: scripts/find_overlap.py`.
The shared-file edit in this PR caused that job to be selected. The correction
restores the exact PR-base helper bytes and moves the feature to the dedicated
CLI. The historical package and its source pins are unchanged. A regression
checks that the new CLI does not mutate imported legacy functions or record
shapes. New hosted confirmation remains pending.
