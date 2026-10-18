# PR99 source retention through PR103

**Research consolidation; no new kappa.** All 46 files introduced by Divjot
Singh Manchanda's PR99 survive unchanged in Rohan Arun's incorporated PR103.
Both complete package trees are `6bebd79406bb2453ada2b7761aece13d3e53b694`.
The offline proof authenticates paths, modes, blob identities and the complete
original commit difference, rather than relying on a matching title or README.

At base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, the
[ledger](../../docs/research/pr-ledger.json) gives PR99 no integration location
and records only earlier source-inventory triage. PR103's retained README says
the whole PR99 package was vendored unchanged. This receipt establishes that
link and restores the missing individual credit in
[CONTRIBUTORS.md](../../CONTRIBUTORS.md). It does not change ledger dispositions
or convert source retention into mathematical approval. Live GitHub metadata
at entry already reported both PRs closed; no PR was closed by this work.

## Exact sources and coverage

| Role | Commit and path |
|---|---|
| PR99 source | `0622dcce6a897567e4eb6bdfedc7def66ab21346:research/nondegenerate-readout-saturation` |
| Original comparison parent | `56b66d58297deca1d7dd130247d720e960f77a37` |
| PR103 retained copy | `75ab1f70d146c21c7611ce0df9eb5f645f51ac0e:research/saturated-balanced/vendor/pr99` |
| Published source archive | `b91de239a64d24d8aee409a0f4ac3e00710ae5c1`, tag `archive/pr-reconciliation100-20261013` |

[SOURCE-PROOF.json](SOURCE-PROOF.json) contains 32 raw Git objects: four commits,
the necessary trees, and five evidence blobs. Its authenticated commit difference
is exactly 46 additions, zero modifications and zero deletions. PR103 is a direct
parent of the archive commit, whose identity and parent list are checked against
the retained archive receipt. The historical PR103 review is bound to its exact
head. Git content identity assumes collision resistance of Git SHA-1; it does
not authenticate signatures or establish authorship. The optional collector
also compares every original and retained file's bytes using Git directly.

The standalone checker imports no predecessor implementation. It reconciles
four authenticated saved reports: the baseline histogram, PR99's candidate and
frame-extension list, PR99's historical component-delta review, and PR103's
integrated histogram. The extension counts are six `12->13`, three `12->14`,
and thirteen `13->14`: 22 frames and 25 added dimensions. With `v=1771`, their
recorded merger accounting is

```text
3542 * [6*(H509-H507-2*H1) + 13*(H511-H509-2*H1)
        + 3*(H511-H507-4*H1)]
= -177100*H1 - 31878*H507 - 24794*H509 + 56672*H511.
```

Here `Hr` denotes one child of rank `r`. The independently subtracted saved
histograms give precisely this vector. Its rank-weighted mass is zero; both
profiles have recursive rank `57,403,754,177`, width `108,516,254` and `28,866`
auxiliary roles. PR103's complete saved histogram equals PR99's candidate.
The checker verifies these identities, not the legality of the original frame
extensions or a newly executed circuit. Full physical, native, moment, all-size,
compiler, routing, precision/recovery and analytic obligations remain inherited.
No full multiplication theorem or new selected-frontier replay is claimed.

## Reproduce

From the repository root, using Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/pr99-retention-seed99
```

This runs the read-only checker and 18 tests: one positive case and 17 failure
controls. Expected output includes:

```text
PASS_PR99_RETENTION_AND_SAVED_ACCOUNTING files=46 singleton_delta=-177100 mass_delta=0
Ran 18 tests
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/pr99-retention-seed99 outcome=completed
```

Controls cover missing files and trees, same-count path substitution, file modes,
corrupt commits and accounting blobs, missing archive ancestry, wrong review
heads, duplicate JSON/ranks/slots, a missing double extension, changed width,
omitted component charges, a mass-preserving wrong profile, and substitution of
the unsaturated histogram into PR103. Explicit checks also run under `python -O`.

The direct `python3 -I -O -B research/pr99-retention-seed99/verify.py` command
needs neither Git nor network access, only this package and the two immutable
review inputs listed in [VERIFY.json](VERIFY.json). The registered metadata
check additionally uses Git history for the provenance in [SOURCES.json](SOURCES.json).
[RESULT.json](RESULT.json) is compared against recomputation on every default run.

To recollect the proof from locally available pinned Git objects, run
`python3 -I -B research/pr99-retention-seed99/collect.py --output /tmp/pr99-proof.json`
and compare it with `SOURCE-PROOF.json`. The collector documents the fetches
needed if those objects are absent; it never fetches or runs archived code itself.

## Task and overlap

OS-random seed **99**, consolidation track; task `overlap-receipt`, refined to
PR99 through PR103. The seed selects the older PR99 object. PR279 source closure
and stale current-result routing were rejected as candidate tasks because
PR1190 and PR1232/1285 already address them. This receipt uses a similar Git
object authentication method to Adam Gall's PR1190, on a distinct source tree;
no code or proof data from that pending PR is imported. Rohan Arun's PR103 and
the maintainer reconciliation are the retention and review predecessors.
Full overlap-search coverage and limitations are recorded in [TASK.json](TASK.json).
The [coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18912011)
was posted before implementation. No search for a better circuit was performed.

## Open next questions

No further retention experiment is justified by this receipt: the complete
original change is accounted for. This does not settle whether every original
mathematical obligation has received sufficient review. That question remains
outside this source-retention result; neither the ledger's historical disposition
nor the selected frontier is changed.

## Credit

Divjot Singh Manchanda (@djsmanchanda) supplied PR99's nondegenerate readout
saturation. Rohan Arun (@rohanarun) supplied PR103's signed/balanced integration;
Zhihao Chen (@jacklightChen), Swapnil Jain and the original notices retain the
upstream mathematical and implementation credit. Douglas Colkitt and the
maintainer reconciliation retained the historical source and review records.
The original [UPSTREAM-NOTICE](UPSTREAM-NOTICE) is preserved byte for byte.

Prepared for Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in
source investigation, implementation, verification and writing. These checks
are independently implemented relative to the historical code, not independent
human peer review. New work is Apache-2.0; predecessor licenses remain in their
unchanged original package.
