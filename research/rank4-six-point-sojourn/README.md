# Exclude the six-point rank-four sojourn at length 30

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration.

A universal closed eight-source binary singleton word of length 30 cannot
have a multiplicity-two source whose rank-four sojourn visits exactly six
distinct projected states. Such a layer requires at least 32 complementary
states and therefore at least 38 prefix slots. This closes the separate
size-six case explicitly left open in unpaidmoon's
[PR #7093](https://github.com/CrocSwap/integer-mult-bounds/pull/7093), head
`94b36d4649b5d29829959409acbc1906ef0b4379`.

The new step is an affine-plane coset argument applied in each quotient
fiber. Three translates can cover an elementary binary group only when the
other set has at least half the group. Six points in F_2^4 therefore need
at least four translating points per fiber. Eight fibers require 32 points.
[PROOF.md](PROOF.md) gives the self-contained argument and an attaining
cross-layer set cover. That cover is not a universal word.

## Evidence and reproduction

CPython 3.12, standard library only, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/rank4-six-point-sojourn/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/rank4-six-point-sojourn/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rank4-six-point-sojourn
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rank4-six-point-sojourn --check-source-history
```

The verifier enumerates all 8,008 six-sets and 560 triples in F_2^4,
checking 4,484,480 sumsets. A separate literal-set check covers all 8,008
six-sets against a normalized triple. The full and normalized cardinality
histograms must agree under affine symmetry. Explicit fixtures check the
32+6 sharp cross-layer cover, its failed same-layer condition, and four
boundary controls. The generated JSON receipt includes every package-file
SHA256 and the marker `PASS_RANK4_SIX_POINT_SOJOURN`. No receipt is committed
or hand-authored. No predecessor executable is imported or replayed.

The code has fixed finite domains, no recursion, no subprocesses and no
runtime file writes. Python allocates managed objects during enumeration;
the largest retained census collection has 560 triples, and all individual
sumsets have at most 128 elements. Functions stay below 60 lines. Explicit
exceptions keep proof checks active under optimization. The registered
warning-strict normal and optimized commands provide the local diagnostics.

## Scope, sources and credit

The connector-alphabet-change card is explicitly changed to this algebraic
side result within the existing alphabet. It removes one live candidate
boundary; it supplies no changed operation or complete supplier bill.
The card's old 945-pairing replay is outside this new question. The working
example here is the six-point layer and its three-point translation test.

Credit unpaidmoon #7093 for the separate size-six question and its rank-four
setting, #7015 and #6943 for the sojourn split and preceding exclusions;
Ross Richardson #943 for the singleton model and prefix criterion; Douglas
Colkitt #1185, conorholds #3058, Nick Petalas #5234, and Nicholas Stone #5430
for the retained eight-source lineage. Their bounds and constructions are
cited rather than reverified. This proof neither uses nor extends #7321's
adjacent-pair degree argument. Main sources are pinned in SOURCES.json;
the pending question source is identified by URL and exact head in TASK.json
and this document, with no runtime dependence on its unmerged Git objects.

The selected record remains unchanged. No new f(8) bound, physical schedule,
native/stock/precision/caller admission or multiplication theorem is claimed.
No Lean, Docker, selected cold replay or proof-kernel check was run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Does a universal length-30 word survive the remaining rank-four sizes and
the higher-rank cases? First search one rank-four layer with 17 complementary
points, using #7093's existing constraints and excluding size six by this
proof. This matters because a word would lower the length-32 upper bound.
The coupled same-layer cover and legal chronological walk remain blockers.
No further search or tighter boundary is part of this contribution.
