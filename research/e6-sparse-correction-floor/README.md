# Every sparse two-coordinate E6 correction costs at least 39

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written invoice proof with exact finite corroboration.
For Cinna Davis / 1337isnot1337's fixed PR2240 one-extra rank-one E6
factorization and its fully charged Theorem C tariff, every nonzero rational
correction direction supported on at most two coordinates costs at least 39,
for every nonzero rational lambda. A two-coordinate direction that excludes
coordinate two costs at least 40. Attainment is unclaimed.

The [proof](PROOF.md) gives the support-sensitive moment bound, valid for every
positive power q and every genuine seven-term member:

```text
sum charged_rank^q >= (s+1) 5^q + (5-s+epsilon) 6^q + (1-epsilon) 7^q,
C >= 42-s-epsilon,
s = support size of a,   epsilon = 1 if a_2 is nonzero, otherwise 0.
```

This strengthens PR2277's general root-code floor 36 on this sparse family.
To match the original six-term cost 37, a genuine seven-term correction must
touch at least four coordinates, including coordinate two when it touches exactly four. To reach
36 requires at least five, including coordinate two when exactly five.
These are new necessary support gates, not sufficient conditions or decoders.

The lower profile is sharp in the abstract relaxation that retains only fixed
term ranks and the five-unit charge floor. No E6 decoder is claimed to attain
that abstract profile. The exact minimum on the rational two-parameter plane
remains open.

## Evidence and reproduction

The standalone verifier enumerates every nonempty coordinate support and all
12,285 declared abstract invoices. Each of the 63 support minima equals the
new formula. It also checks 240 new rational coefficient fixtures across all
coordinate pairs, five invalid supports and the ordinary, exceptional and
full-support boundaries. It imports no predecessor executable and does not
replay the predecessor's census or recompute its six published pairing ranks.
Four scientific source mutations and one source-byte corruption were also
rejected locally in both normal and optimized modes. Every run generates a
receipt hashing all six package files and its pinned
source certificate. No receipt is handwritten or committed.

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -B research/e6-sparse-correction-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -X dev -W error -B research/e6-sparse-correction-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e6-sparse-correction-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e6-sparse-correction-floor --check-source-history
```

Another CPython 3.12 installation can replace the absolute interpreter path.
The direct marker is PASS_E6_SPARSE_CORRECTION_FLOOR. Normal and optimized
commands are read-only. A standalone export must retain the declared source
certificate at its repository-relative path; direct replay then needs no Git.
The metadata and committed-byte commands need repository history.

## Sources and scope

Cinna Davis / 1337isnot1337's [PR2240](https://github.com/CrocSwap/integer-mult-bounds/pull/2240),
head c8a2b37056e766715c457f56e2dd8172f5bdbccd, supplies the fixed
factorization, dense pairing, ranks (6,7,6,6,6,6), tariff and finite-alphabet
screen. Those mathematical inputs are cited, not audited or independently
re-certified. Its PR1590/root-unit lineage retains credit. PR2247 changes the
base by shears. DreamingOfClouds's PR2277 supplies the broader root-code floor
36, already excluding cost 35. The new gate is stronger on this sparse fixed
base, and leaves those results intact.

Scientific base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priorities revision 8, selected PR6030. [SOURCES.json](SOURCES.json) binds the
source certificate as a live input and the source question as provenance.
[TASK.json](TASK.json) records the change from the complex-rank-shape-decoder
card to this scoped obstruction. Its supplier acceptance gate is not claimed.
The current selected metadata control passed; its scientific replay was not run.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371202)
identifies the E6 target and its narrowed scope.
Live open/account PRs, active Discussions, reservations, main/merged rational
and support-sensitive searches were checked. The overlap snapshot covered
522 open PRs and 6,534 Discussion records; omitted sparse notes, unpublished
work and arbitrary historical diffs remain limits. No global novelty claim is
made.

No raw-rank bound, exact decoder minimum, physical supplier, new kappa,
selected-frontier change or complete multiplication theorem is claimed.
Native realization, ownership/restoration, routing, precision/tape, stock,
compiler and outer costs remain separate. All five selected framework
assumptions remain. Selected cold replay, Lean, Docker, independent human and
formal proof-kernel review were not run or claimed.

## Engineering bounds

All loops have fixed finite bounds: 63 supports, at most 3^7 invoice choices,
seven ranks, six coordinates and 240 rational fixtures. There is no recursion,
dynamic code evaluation or external executable import. Each function is under
60 lines and explicit invariant checks survive optimized execution.

Power-of-Ten rule 3 has a managed-runtime deviation. Python integers, Fractions
and temporary lists allocate during arithmetic. The fixed domains bound live
records to one seven-rank invoice or six-by-six coefficient matrix, plus the
source certificate, capped at 64 KiB. Any future general-input interface needs
a new resource bound. Warning-strict normal/optimized runs, AST inspection,
source corruption and scientific mutation controls are the applicable checks.
No repository-wide analyzer configuration changes are needed for this package.

## Open next questions

1. Determine whether a genuine fixed-base correction attains the support-only
   floor at support four or five. Start by checking simultaneous pairing-rank
   compatibility at an explicit rational direction. The abstract invoice does
   not supply that compatibility or a decoder.
2. Determine the exact minimum on a=e_1+t e_2. Start with the support-change
   arrangement in rational t and lambda. The present floor 39 is not claimed
   attained; a universal two-parameter classification is unrun.
3. Identify a changed base or a complete physical consumer that makes a lower
   algebraic invoice useful. Start with its full paid contract. Frames,
   restoration and native/outer costs are unresolved.
