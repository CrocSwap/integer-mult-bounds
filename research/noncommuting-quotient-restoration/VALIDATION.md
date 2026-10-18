# Validation receipt

Observed on Windows with standard-library-only CPython **3.12.14** (bundled
runtime) and **3.14.6** (Anaconda). No dependency installation or predecessor
execution was required.

The Python 3.12 registered replay passed both declared commands and ended with
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. Its nine optimized
test groups passed in 2.376 seconds on this host. The same certificate passed
the Python 3.14 normal replay; the optimized 3.14 replay used to generate it
also passed. Timings concern verification only and are not a multiplication
benchmark.

```
python3.12 -B scripts/research_package.py --package research/noncommuting-quotient-restoration
python3.14 -I -B research/noncommuting-quotient-restoration/verify.py
```

Exact coverage: six group actions and 36 group laws; all 729 ternary readers;
46,656 normalized endpoint-correct boundary schedules including entrance
operations; five checkpoint policies at three positive price pairs; twelve
root cases with 624 forward/inverse basis columns and twelve rational dirty
probes; a two-child pilot and all six typed forward prefixes. Both complete
primary root words and every planned checkpoint witness are retained.

Twelve semantic/word controls detect missing output correction, invalid
reader admission, noncommuting order changes, missing source restoration,
missing batch inverse, a forward batch substituted for its inverse, wrong
workspace/output observers, an incomplete permutation, aliased ports, wrong
sign and an unreserved port. The public emitter rejects a non-equivariant
reader and the complete echo rejects a nonrestoring correction sequence.
Nine test groups also exercise noncommuting F, exact inverse on arbitrary
dirty source/workspace/output, seven invalid configurations, source-byte and
false-commit corruption, relocation and an on-disk unpaid-NEG receipt.
Windows temporary tests used the workspace-local `session-test-tmp` directory;
the optional `IMB_TEST_TMPDIR` variable permits this without changing replay
semantics. CI may use its ordinary temporary directory.

Selected-binding orientation returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`,
with the complex supplier binding. The assigned first-step source-binding
check and the universal connector positive control both passed; the latter
returned `pairings=945 max_coverage=31 queries=74 leaves=182`. These are
orientation controls, not new scientific results or selected cold replay.

Discovery base was fresh main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Submission refresh found main `680967accfd4311f3241dc154e1f434869747b43`;
AGENTS.md, autoresearch.md, CONTRIBUTING.md, the task catalogue, selected
record and registered replay script are identical at those two commits.
The branch retains its discovery base and adds only this package. No frozen
source package, selected record, shared script, upstream input or ledger is
changed.

Entry overlap covered 847 open PRs (drafts included) and 98 Discussion
body/comment/reply records. Final refresh covered **718 open PRs** at
2026-10-14 03:00:43 UTC and **218 Discussion records** at 03:01:17 UTC, with
complete pagination of both. The helper's offline warnings refer to reuse
of these freshly fetched snapshots. Exact coverage, terms, relevant heads and
limits are in OVERLAP.json. Concurrent Hanson Sun / bbMisk PR1488 at
`13d780ea51248ddd51901cd546b9f59adc76eb43` was read and credited. Its faithful
two-dimensional output differs from the sign quotient and kernel observers
here; its code and numerical claims were not independently replayed.

The local metadata was written from the documented schema because fetching
the pinned notes created the package directory before the optional generator
ran. The generator refused to overwrite it; the completed manual metadata
subsequently passed the standard provenance and replay checks. An initial
human-readable overlap print hit Windows cp1252 encoding; the complete JSON
report was rerun with `PYTHONUTF8=1`. Neither issue affected mathematical
acceptance.

The default intended session budget was about 60 minutes. Recorded entry and
submission UTC times span a longer session; no compliance with that intended
time budget is claimed. Mathematical computation stayed within the explicit
finite domain and short replay bounds.

Unrun: selected supplier cold replay, Linux/hosted CI, human review, proof
assistant formalization, actual supplier/owner/frame admission, rounded
precision and recovery, bit-level fixed-tape implementation, all-size compiler
and analytic transfer. Written exact identities and restricted boundary proofs
are distinguished from finite implementation evidence. No new κ is claimed.
