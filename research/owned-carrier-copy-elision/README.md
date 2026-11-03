# Remove one owned copy from the current native word

This contribution is produced by Nick Petalas. Claim type: scoped scalar-program
construction with exact finite equivalence. No new kappa or selected-frontier
change.

In DreamingOfClouds's [PR6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621)
at `c51a142bb94c6d46ebee9a48c3f71cde8022da91`, the first lifetime of owned
carrier 774 holds only one quarter of retained carrier 785. Both consumers
can read 785 directly with coefficient `1/4`. This removes four scalar events
and one owned lifetime. Under the source's exact scalar tariff, the complete
allowance decreases by eight units, from 137,866 to 137,858.

The native-call sequence and productive boundary are identical. Paid rank
histograms, productive moments, peak owned storage and allocated register
inventory are unchanged. This is an improvement to the scalar implementation,
with no recursive exponent gain. The [proof](PROOF.md) gives the exact six
source events, the arbitrary-input argument and the complete local bill.

## Reproduction

From the worktree root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/owned-carrier-copy-elision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/owned-carrier-copy-elision/verify.py
```

The registered hook runs normal and optimized Python. Each command prints a
generated JSON receipt with `PASS_OWNED_CARRIER_COPY_ELISION`, input/package
hashes and the constructed program hash. It writes no files. The constructor
is the complete new word: call `transform(read_word())` in this package's
module to obtain it without generating a second committed data copy.

Checks cover every one of the 638,401 rational coefficient positions of the
complete program maps, the same independent modular all-column comparison,
frame/ownership legality, the scalar/lifetime delta, identical native jobs,
and six semantic rejection controls. The source result is a premise; its
endpoint, native operators, compiler, caller price and selected cold replay
are not audited or re-certified. No physical runtime speedup is measured.

`WORD.json.gz` is retained unchanged as data. [SOURCE.json](SOURCE.json) records
the source commit, original archive URL, Git blob, SHA256 and nested member
hashes. Normal replay checks the retained bytes locally; it does not contact
GitHub or authenticate the external publication. After downloading the pinned
`archive_url` into an external scratch directory, this optional command
checks the complete original-byte extraction chain without extracting or
executing predecessor code:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/owned-carrier-copy-elision/verify.py --source-archive /path/to/source.tar
```

The local source-archive equality check, normal/optimized direct runs and both
registered checks were run before publication. Committed-byte/history checks
are recorded in the PR. Hosted CI remains separate. All five inherited
framework assumptions remain; independent human and formal proof-kernel
review are unclaimed.

## Open next questions

Can a future paid transport be shared while preserving every intermediate
reader and the public boundary? Name one overlapping carrier pair and a common
future transport, then supply the causal consumer and restoration bill before
a wider search. No such paid-prefix construction is supplied or reserved here.
The present result stops at the first scalar improvement. [TASK.json](TASK.json)
records the changed scope and the original card.

## Credit and coordination

DreamingOfClouds supplies PR6621's native word. Credit Ali Romman's PR6529,
PR6545 and PR6551, Rohan Arun / PR6399 and PR6417, Erwan L. / PR6453 and the
retained native/helper/compiler lineage. Copy elision and constant propagation
are classical techniques. The new contribution is this exact changed word,
the arbitrary-input proof and the complete eight-unit allowance reduction.
The original credit notice is retained unchanged in [SOURCE-NOTICE](SOURCE-NOTICE).

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375269)
records the original carrier-sharing attempt and the earlier route stopped
for overlap with recent account work. This result does not revive that route.
Live open PRs, claims, current main READMEs and merged general/object searches
were checked. The cached snapshot covered 572 open PRs and 6,636 Discussion
records; its sparse local corpus omitted 8,797 notes. Separate Git searches
covered main's README bytes. Unpublished work and arbitrary historical diffs
remain overlap limits.

## Verifier bounds

All loops are bounded by the frozen 18,561-event input and 799 roles/columns.
No recursion, predecessor executable imports, network access or output files
are used. Every function is below 60 physical lines. Runtime guards remain
enabled under optimized Python, and warnings are errors in both registered
commands.

Python's managed allocation and rational arithmetic are the Power of Ten
rule-3 deviation. Sparse rows have at most 799 coefficients; each dense matrix
has 638,401 entries, with two modular matrices live for comparison. The input
is hash-bound and its decoded size is capped at 3 MiB. Each command has a
120-second timeout. A future input expansion must revisit these bounds.
No static type checker is a package dependency. No shared analysis or CI
configuration is changed.
