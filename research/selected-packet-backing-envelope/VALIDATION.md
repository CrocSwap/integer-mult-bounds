# Validation and limits

Checks on 2026-10-16, Linux x86_64, standard-library Python only (CPython 3.12.13 and 3.14.4):

```sh
python3.12 -B scripts/research_package.py --package research/selected-packet-backing-envelope --check-only
python3.12 -B scripts/research_package.py --package research/selected-packet-backing-envelope
python3 -I -O -B research/selected-packet-backing-envelope/verify.py
python3 -I -O -B research/selected-packet-backing-envelope/independent.py
python3 -I -O -B research/selected-packet-backing-envelope/test_verify.py
```

The registered Python 3.12 run passed all three commands. The Python 3.14.4
optimized primary receipt exactly matches [RESULT.json](RESULT.json).
A relocated, Git-free copy with every existing file mode set to read-only
passed all three optimized commands; all 34 then-existing file hashes were
unchanged. That copy preceded this validation document. Mutation tests operate
only on separate temporary copies and make their targeted copied files writable.
Directories in the relocation test were writable; no read-only-filesystem or
hostile-runtime sandbox guarantee is claimed.

The primary suite passed 99 cases, 106,227 observed samples and 693 each
prefix-return/copy-completion cuts. Observation counts are corroboration, not
an exhaustive claim about arbitrary interpreter states. Exact source reasoning
in PROOF.md covers unobserved transitions. Ninety cases use a synthetic action
with explicit total private backing `F+1+S`; nine use actual small sign actions
and certify only the caller cohort and output, not all native private arrays.
The records/layouts are synthetic and do not certify selected GL64 admission.

The independent integer-identity ledger passed 5,040 parameter cases,
10,080 schedules and 2,278,920 modeled cuts. It imports neither primary nor
predecessor verifier. Controls exhibit 1,800 prefix-only undercounts,
5,040 cases where `M+A` strictly overstates the exact modeled maximum, and
1,680 early-only scratch cases where the uniform action upper bound is not
attained. `M+A` remains a conservative bound; it is rejected only as an exact
maximum. This finite symbolic model corroborates the all-parameter written
proof and is not a second native execution or formal proof kernel.

Ten focused tests pass in normal and optimized Python. They include positive
source fixtures; prefix-only and copy-only underestimates; omitted preflight
backing; unpriced private scratch; invalid/Boolean domains; typed receipt,
manifest/source and preload defects; and a literal packet-engine counterexample
to endpoint-only borrowed-buffer restoration. The last control deliberately
grows the borrowed local backing by 100 cells then restores it before return.
Its endpoint is correct while its interior violates the stronger storage premise.
It is not a defect in the unchanged native action.

All 23 exported source/notice/license entries were independently compared with
`git cat-file blob` at their SNAPSHOTS.json blobs and match byte-for-byte.
The source loader authenticates the manifest and bytes before compiling them,
and rejects preloaded source module names. The original selected record and
research catalogue are historical provenance; the scope map is also provenance,
not a live mathematical input. All runtime proof-relevant exports are inside
the package and trigger its replay. Source integrity is not proof correctness.

The selected baseline command `python3 -B scripts/research_baseline.py` passed
its source-binding/arithmetic-only check. No full selected cold replay was run:
this addition neither changes nor admits a supplier. No physical tape compiler,
failure cleanup, recursive reserve, full native action backing bound, total
caller reserve, human review or new kappa is claimed.

## Freshness and coordination

The branch began at canonical main `c7df0bb890cae0cc393cdd32dad19c3facc80992`.
The submission checkpoint at 06:51:16 UTC fetched
`a7fc79c0cd63d6aa48df753069fc49eabda79dc3`. AGENTS.md, autoresearch.md,
priority revision 5, selected record, family status and caller/storage map
are byte-identical between those commits. Scientific provenance remains the
initial base and exact predecessor heads; no frozen inputs were repinned.
PR2697 and PR2874 heads were reread unchanged before submission.

The final overlap scan reports complete metadata pagination for 491 open PRs
at 06:47:30 UTC, 2,088 closed/merged PRs at 06:48:23 UTC and 1,526 Discussion
records at 06:48:03 UTC, with no warnings. These snapshots are not atomic and
exclude arbitrary code diffs and unpublished work. Direct latest comments in
Discussion #2319 distinguish this claim from PR2877's sign-traffic audit and
the physical-wrapper investigation. Exact search coverage is retained in
TASK.json. No novelty guarantee follows from an overlap scan.
