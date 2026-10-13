# Validation and handoff

Verified on 2026-10-13 in the prepared Linux Codex Cloud environment:
CPython 3.12.14 and g++ 14.2.0. Python checkers use only the standard
library. The independent search also needs a C++17 compiler. No packages
were installed for this contribution.

From the repository root:

```sh
python3 -I -B research/prescribed-star-triples/verify.py
python3 -I -B research/prescribed-star-triples/run_independent.py
python3 -I -O -B research/prescribed-star-triples/test_package.py
make selected-record-check
```

All four commands passed. Actual output is retained in [evidence/](evidence/).
The primary result is 44,100 target triples, 18+19 symmetry orbits and
645,606 four-block partitions. It checks 3,060 literal surviving-source
columns, 740 one-port-restoration rejections and three other invalid-decoder
controls. Its complete deterministic receipt matches CERTIFICATE.json.

The independent optimizer completes **306,446,336** normalized coefficient
assignments across p=5,6, permitting all eight labels. Its separate orbit
canonicalization and binary row-space checks agree with the primary minima
and orbit sizes. It independently rejects 740 restored ports in those two
domains. Additional p=2,3,4 finite checks are recorded separately; all 224
prescribed triples at p=2,3 also pass an exhaustive deletion-mask comparison.
The p=3 empty-star control changes a target triangle from impossible to a
five-deletion decoder. This is a boundary control, not a classification of
the larger observation model at p=5,6.

The three packaging tests pass in isolated optimized Python. They reject
an underpriced exceptional receipt, preserve the absence of output after
failure, reject modified predecessor bytes, and reproduce byte-identical
receipts after relocation into a path containing spaces. Existing output
files are preserved. The independently implemented search also passed a
full optimized replay and rejection of corrupted receipts, existing output
paths and out-of-range parameters. C++ compilation with
`-std=c++17 -O2 -Wall -Wextra -pedantic` produced no warnings.

Separate AI-assisted adversarial review checked the uniform proof, the
connected-optimum qualification, all forest shapes and the empty-star
counterexample. Its separate scratch implementation checked bridge versus
binary-row recovery on all 4,096 retained p=3 graphs (24,576 retained-edge
comparisons), all three-target vertex-basis choices at p=5,6,7, and all
35 feasible primary witnesses against direct row-space recovery. Those
supplementary scratch checks and reviews are retained in the recovery
archive; the submitted theorem does not depend on unshipped scratch code.
Agent agreement is supporting evidence, not a proof.

## Sources, overlap and limits

Exact base is `91a2094f2e022930069e8cfdc810a3ea1b81cd09`.
The two retained PR669 proof texts are SHA256-pinned in SOURCES.json;
their Git blob IDs were also checked against GitHub's contents API at
head `7d526020fc368ce4157cd436995c2f4fcf683318`. No predecessor executable
code or solver is imported. The latest ledger has no scoped exact-head
review of that pending PR; attribution here does not imply its acceptance.
The needed argument is rederived in PROOF.md.

A follow-up compliance audit consulted the exact [contributor guide at
47481c8](https://github.com/CrocSwap/integer-mult-bounds/blob/47481c89fd30a43f8f882eb4b391e89c29273fd0/CONTRIBUTING.md).
It is byte-identical to the guide read at the base commit (SHA256
`1cae543effcabab91dab7f78423ee9283e60fb504f10848483d153331cd72bc4`).
The referenced [contribution-review index](../../docs/research/contribution-review.md)
was consulted during this follow-up, rather than before building on PR669.
It explicitly records historical triage through PR40, is not the current
queue, and contains no PR669 acceptance or conflicting prescribed-triple
finding. Source pins, attribution, mathematical scope, README/proof consistency,
negative controls, Apache-2.0 notices and substantial AI disclosure were
checked against the guide. No closure or integration of predecessor work
is implied by this audit.

The initial refresh inspected 721 open PRs through #931; a later after-check
snapshot at 2026-10-13 15:01 UTC inspected 715 through #962 and found no matching
classification. **That overlap conclusion is now superseded.** The user's
pre-opening refresh at 15:12 UTC found 702 open PRs through #966, following
seventeen merges. No pinned coordination issue or existing PR from our branch
was present. New PR963/964/965 concern different circuit or scalar-forest models. A final
delta read at 15:20 UTC reached PR970: PR967/969/970 concern circuit, scalar
compiler or provenance work; PR968 concerns complex frame-pair decoders. None
adds the same coefficient verification. Main and the inspected PR669/966 heads
remained unchanged.

Concurrent **PR966 by @woklerx**, opened at 15:07:03 UTC, head
`7eaf5665ac246310293fda06a3cf245fe72f6012`, states the same nonempty-star triple
classification for p>=3 and an exact p=2 boundary. **PR669 by Sam Sung** subsequently
expanded at `8f4600b41bf1f0f5d07f209e5d3950eb22ef5cad` to classify triples in both
star spaces and give a broader arbitrary-forest formula. Those statements
subsume our p>=5 theorem. The package is therefore presented as independent
verification, with no claim of a new classification or priority. Our original
retained PR669 texts remain byte-identical at its newer head.

The comparison inspected the actual proof, checker sources and retained receipts:

| Package and pinned version | Relevant independent finite coverage |
| --- | --- |
| PR966 at `7eaf5665` | RREF cut-subspace enumeration through p=5; its primary four-block census also covers p=6. |
| PR669 at `8f4600b` | Retained-graph checks at p=2,3 and independent coefficient optimization at p=4, for triples and quadruples. |
| PR971 at `b4cb9709` | Independent group-action inventory and literal witness audit through p=6; unrestricted RREF minimum comparison only at p=3,4. |
| This package | Unrestricted eight-label coefficient enumeration at p=5,6; p=6 alone checks 301,989,888 assignments, all 19 target orbits (18 feasible), 34,220 triples and 433 separate row-space restoration controls. |

At the user's request, PR971 by Eva Ayala (@ToikY), pinned at
`b4cb9709ac48e69002a25607e1ecc2ed8452d5b3`, was also inspected. Its actual
`audit.py`, `independent_check.py` and AUDIT.json restrict independent minimum
computation to p=3,4; at p=6 its scope is inventory and supplied-attainer checks.
It contributes explicit group actions and targetwise histogram-preserving
controls, which are credited rather than claimed here as new. This bounded
source/receipt review did not execute PR971's checker.

The additional p=6 coefficient coverage does not assume four blocks or import
any concurrent implementation. Its proof and primary census remain useful
cross-checks but are not new claims relative to those PRs. This review did not
execute the concurrent checkers or certify their broader empty-star/forest
statements. Our smaller-parameter cases remain finite boundary controls rather
than a newly claimed uniform extension.

Main advanced to `bbc600db2fc15007b7c914f4f2b2ed55fa909c87`, selecting PR942 with
conditional κ `1661960547713947/10^18`, source
`1960cfa919a0945d0ca4cb14ea96237000037903`. The current selected record and status
were consulted; the contributor guide and PR template remain unchanged. The
#799 and #890 contexts in SOURCES.json are earlier snapshots. No selected
supplier is a mathematical or executable dependency of this verification.

Only this research package is added. `upstream/`, the selected certificate,
existing generators and supplier artifacts are unchanged. The applicable
focused checks and selected-record integrity pass. The repository-wide
`make verify` suite **passed (exit 0)** in an isolated local clone at contribution
commit `70484032ff4ae960b19acc8e159622e7e6ac8bac`: all 18 sequential groups,
87 isolated test modules and 20 historical patch checks completed in
4,840.266 seconds. The [compact receipt](evidence/make-verify.json) records
the tested head, timestamps and full-log SHA256; the log is in the recovery
archive. This is a run on the original base, not current-main integration.
The later edits only add documentation, context metadata and evidence;
mathematical arguments, executable checkers, certificates and predecessor bytes
are unchanged; later provenance text credits the concurrent results.

The historical PR741 cold replay included in that suite also passed
`scripts/verify_replay_coverage.py --frontier 741`, pinned at main
`007664306fff84fbb1c9a1b4053b69f439764034`, using its existing output.
That pinned checker validates the
22-stage/44-artifact contract, bridge controls and original composition
bindings; its [receipt](evidence/current-main-741-coverage.json) reports
`PASS_COMPLETE_PR741_REPLAY_COVERAGE`. The historical driver, binder and
supplier packages are byte-identical at the original base and `0076643`.
This additional admission check did not rerun producers or validate PR890.
The #799, #890 and current #942 selected-supplier cold replays were not run
because this contribution changes no supplier construction.
Both checkers also passed isolated optimized replay from an export of the
staged Git blobs, launched outside the checkout. Staged whitespace checks
passed. No hosted CI, independent human review or proof-assistant verification
is claimed. Paid implementation, all-size/compiler, hosting, precision/tape
and analytic obligations remain outside this information-threshold result.

The next useful review is the completeness of the unrestricted coefficient
normalization and p=6 enumeration, together with its independent row-space
checks. Maintainers can assess whether to integrate this evidence alongside
PR966 or PR669. The broader empty-star and forest results in current PR669
are outside the verification claimed here.
