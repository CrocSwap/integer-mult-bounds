# Identity, historical evidence, and source provenance

The new review branch starts at upstream
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`. Contribution commits use
`AI-assisted verification contributor <verification-contributor@example.invalid>`.
The human participant initiated and coordinated the AI-assisted effort; no
independent human derivation or checking of the mathematics is claimed.

## Limits of the earlier privacy cleanup

The previous public checkpoint is
`377012d9e1d350c29fc47669e82415249429f60c`. Its metadata rewrite replaced
personal Git author/committer fields and its later cleanup removed obsolete
commit citations from then-current files. That did not erase old objects:
unauthenticated checks still retrieved an old identifying commit through both
the fork and upstream repository URLs. Historical snapshots and diffs retain
references. No GitHub removal is claimed.

A private Support request was prepared but not submitted. Eligibility for
GitHub's [sensitive-data removal process](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
requires GitHub's assessment. Copies, clones, and other references may remain.
The public account and required upstream attribution are still visible.
No old identifying commit IDs or personal Git identity are repeated here.

## Current versus historical verification

The current fresh-build receipts are under `validation/`; their results are
reported in [VALIDATION.md](VALIDATION.md). Both directly match their current
manifests. The [Task B receipt](validation/task-b.json) records 52 fresh modules,
zero reuse, and 931 axiom reports including `SourceInvocation.actualContract`.
It fingerprints the installed external libraries used for this new compilation;
it does not authenticate the library bytes used by the historical build.

The old metadata-reanchoring helper and receipt were retired from this new
delivery. Their [historical record](https://github.com/cheesegrader/integer-mult-bounds/blob/377012d9e1d350c29fc47669e82415249429f60c/research/lean-external-review/validation/metadata-reanchor.json)
explains citation substitutions in older copies; it is not current proof
verification. Original Task A/B `replay-result.json` files remain unchanged as
historical context. In older regression receipts, original log hashes identify
pre-substitution bytes, not the published copies. No new claim relies on those
old log hashes or on the earlier missing external-library fingerprints.

Authored reproduction instructions use portable paths. Machine paths in raw
historical execution records describe those runs and are not prerequisites.
Required local sources and dependencies remain included; the supported delivery
uses one cumulative patch from the new upstream base.

## PR493 → PR472 → PR442 is provenance only

At PR493 commit `c3a9a436b84fe44fdc223a5784d84736d1c2d3c7`:

- The [README](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/README.md#L147-L152)
  explicitly lists “whole-call correlated-helper hosting (#442)” among inherited assumptions.
- The [NOTICE](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/NOTICE.md#L42-L48)
  names PR472 as the intermediary carrying PR442's `hosting_core.py`.
- The [source map](https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/SOURCE-pr472.json#L40-L43)
  pins that source file's Git blob.

The checked `hosting_core.py` bytes match at that PR493 commit, PR472
`259c68488b7aa8a14cf3fcae7fc499381c9bf729`, and PR442
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`: Git blob
`68b536daa9e6546c0aa046934bf840aaa3c3fde3`, SHA-256
`d8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3`.

This establishes the interface's source lineage. It does not transfer the
selected R747 invocation proof to a PR493 word, ownership map, coordinate
system, or schedule. The current merged-work comparison is in
[MERGED-OVERLAP.md](MERGED-OVERLAP.md); it supersedes the earlier overlap snapshot
for current integration context.
