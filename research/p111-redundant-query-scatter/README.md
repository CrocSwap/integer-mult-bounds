# Sharp support obstruction for the retained P111 line-7 query

This contribution was produced by Nick Petalas. Claim type: scoped proof
with exact finite corroboration. No new kappa is claimed.

For the PR1525 puncture-0 scatter, retain all eight independent original
centre readouts and add `q=(c61+c63+c31+c256)/2`. Among every rational
direct-scatter matrix preserving the original map, the unique minimum has
176 nonzero coefficients and ignores q. If q must be used, the exact minimum
is 177. Exactly eight matrices attain that constrained minimum, one for each
receiver in `(112,113,115,119,152,153,179,183)`.

The new result closes a favorable direct-matrix relaxation of Open next
question 2 in [unpaidmoon's PR6640](https://github.com/CrocSwap/integer-mult-bounds/pull/6640).
The original eight readouts remain available, so this is a changed contract
from substituting q for one centre. It is an obstruction over all rational
coefficients, rather than a failed finite search. The predecessor's 176-entry
scatter is the baseline input, not a new count claimed here.

The [proof](PROOF.md) characterizes every exact correction. On each row a,
the query coefficient t forces subtraction of t/2 from each of the four
query-centre coefficients. Every source row omits at least two of these
centres. A nonzero t therefore creates at least two new terms, cancels at
most two, and adds its own term. This proves the strict penalty and the
unique unrestricted optimum. Eight equal-pair rows attain penalty one.

This prices direct coefficients only. General ADD circuits may share
intermediates and have a smaller operation count. A ninth readout also has
acquisition, frame, lifetime and restoration costs that are not priced here.
This result supplies neither a physical scatter nor a complete paid invoice.

## Evidence and reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p111-redundant-query-scatter/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/p111-redundant-query-scatter/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p111-redundant-query-scatter
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p111-redundant-query-scatter --check-source-history
```

Another CPython 3.12 interpreter may replace the absolute local path.
Direct replay prints `PASS_P111_REDUNDANT_QUERY_SCATTER` in a fresh JSON
receipt bound to all twelve package files. It writes nothing. Registered
normal and optimized checks run the same complete domain with explicit
guards that remain enabled under `-O`.

The primary checker constructs one attaining matrix and compares all eight
formal centre coefficients of every output. It classifies all 112 rows.
The separate [support oracle](oracle.py) enumerates all 512 readout subsets
for each row, for 57,344 cases, and uses integer elimination over Q rather
than the cancellation-frequency formula. It checks both unrestricted
support and a genuinely nonzero query coefficient.

Eight centre-basis fixtures use arbitrary nonzero rational dirty targets;
the literal ADD interpreter checks the exact endpoint, unchanged readouts
and reverse restoration. Six controls reject changed query/correction
coefficients, a missing query centre, a false equal-cost claim and invalid
target/denominator inputs. A dense-row positive control reduces four terms
to one and confirms that the two-zero premise is essential. The written
identity gives arbitrary dirty-input coverage; these fixtures corroborate
its implementation.

## Sources, credit and overlap

Rohan Arun / rohanarun's [PR1525](https://github.com/CrocSwap/integer-mult-bounds/pull/1525),
head `90d39a5603c7fbfd8d8d957e9732d9b6ebd6317f`, supplies the query and
word. Four source files, including both unchanged predecessor notices, are
retained under `inputs/`. [ORIGINS.json](ORIGINS.json) records their original
paths, Git blobs and SHA256 values. They were first retained at commit
`34ffd44f2d6257e9c2bcfd01970b5fce61113ab2`; [SOURCES.json](SOURCES.json)
pins these ancestor bytes. No unmerged foreign Git object is required.
The checker uses only the source `cut`, centre order and query terms. It
does not execute or validate the predecessor's native, dirty-query or
whole-word verifier.

Credit unpaidmoon for the question and frozen-interface price screen, and
JoyboyBrian for the earlier triangular identity in Discussion1166 comment
19143427. Credit PR1297/1134/1060 and the retained Rohan Arun, Ali Romman,
DreamingOfClouds, eumemic, geometry, supplier and controller lineage.
Sparse linear representation and rational elimination are classical.
Independent human and formal proof-kernel review are unclaimed.

Related open work at the overlap checkpoint:

- PR6640 studies the eight-readout substitution and its physical price.
  This theorem optimizes a different, redundant nine-readout direct matrix.
- PR1525 supplies the underlying query and leaves a physical continuation
  open. This local obstruction does not settle that larger question.
- PR1900 constructs five plane queries on the P111 boundary. That changes
  both factors and is outside this single retained-query model.
- PR3045 and PR2832 concern fitting-matrix decoder rank floors and global
  decoder reductions. Neither is a direct coefficient-support objective
  for the fixed centre query here.

The live overlap cache covered 613 open PRs and 6,708 Discussion records.
Its sparse local scan covered 127 of 8,917 note paths; main-branch README
searches supplemented it. Closed PR and recent account searches were also
used. This is a stated search scope, not proof of literature novelty.

The joint-query-controller card is refined to this algebraic relaxation.
The pinned catalogue is revision 8 at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The selected record identifies
PR6030; historical priority prose retains an older checkpoint. The selected
frontier is unchanged.

## Limits and implementation constraints

The theorem requires the same exact output map for all independent centre
values and all 112 original cut rows. Omitting a punctured or unused output
changes the consumer contract. Restricted-value inputs, shared intermediate arithmetic, changed
bases, other queries and a changed consumer remain outside scope. Native
frames, query acquisition, independent dirty-state compensation, physical
mixing, owner lifetimes, complete restoration costs, precision/tape,
compiler closure and a complete supplier invoice remain unproved. The five
framework assumptions remain. No selected cold replay, Lean or Docker run
is claimed.

The new checker has no recursion, network access or subprocesses. Every loop
uses a finite bound: 112 rows, eight centre coordinates, nine readouts,
512 support subsets, at most four cancellation candidates and at most
1,024 source cut events. Elimination has at most ten rows and eight columns.
Compressed/file reads are capped at one MiB and expanded word bytes at two
MiB. Functions fit within 60 physical lines. Warning-strict normal and
optimized commands are the available diagnostics; no new static-analysis
dependency is added.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and containers during the bounded one-shot replay. Fixed runtime allocation
is not available. The finite domains and byte limits above bound live
resources; context managers close files on success and failure. A fixed
allocation implementation would need a separate runtime if required.
Rule 9 deviation: the rejection helper dispatches only six statically named
local control calls. Each has a fixed fixture, and unexpected exceptions
propagate. All six rejection paths run in both registered modes.

## Open next questions

Can shared intermediate arithmetic exploit this query after its actual
acquisition, frame and restoration costs are charged? A useful first step
is one explicit chronological shared-accumulator scatter with the same eight
centres and q, followed by a complete price for its readouts and temporaries.
A physical nine-readout caller and legal lifetime/restoration contract are
the blockers. No wider construction search is reserved here.

New work is Apache-2.0. Source notices are retained unchanged.
