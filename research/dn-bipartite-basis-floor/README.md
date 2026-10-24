# Bipartite basis changes cannot improve a paired Dn puncture

For any graph G, retain both root lines e_i+e_j and e_i-e_j on each
edge. Change the coordinate Gram factor basis by M=I+N, where N has
arbitrary rational entries with rows in A and columns in its disjoint
complement D. Entries in the opposite direction are zero.
Even after jointly optimizing every admissible directed binary pairing,
the exact minimum COPY cost is

    2|E(G)| = number of live root lines.

This is a **scoped mathematical proof with finite exact corroboration**.
It answers the elementary-shear step in ywz65's [PR2536](https://github.com/CrocSwap/integer-mult-bounds/pull/2536)
Open next question 1 and also covers any number of shears across the
same fixed split. It permits asymmetric pairings and paired edge
deletions. No new kappa, physical supplier or complete multiplication
theorem is claimed.

## Proof and research decision

[PROOF.md](PROOF.md) proves that every factor term keeps a coordinate
factor on one side. Its other factor has at least one nonzero sign root
on every incident edge. Those surviving roots force an identity minor
whose size is the coordinate's graph degree. One fixed symmetric
pairing, consisting of an all-ones block on each opposite-sign pair,
attains every degree bound at once.

The first D5 fixture retains edges 01, 02, 04, 12, 23, 34 and uses
M=I+E_01. Its term prices at the attaining pairing are 3,2,3,2,2, totaling
12 for 12 live roots. This is a basis-changing fixture, rather than a
replay of the coordinate-basis census.

Stop tuning single shears or repeated shears across a fixed split for
this paired-root family. A different basis pattern or another stated
premise is needed to reopen this route. This is a local obstruction;
the physical producer, consumer, restoration and complete bill remain
unpriced. It supplies no family expansion or selected-frontier change.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/dn-bipartite-basis-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/dn-bipartite-basis-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dn-bipartite-basis-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dn-bipartite-basis-floor --check-source-history
```

The direct verifier reports `PASS_DN_BIPARTITE_BASIS_FLOOR`. Default
replay reads committed files and writes nothing. `--output /new/path`
generates a receipt and refuses to overwrite an existing file.
[RESULT.json](RESULT.json) records generated counts and SHA256 hashes of
all six proof, code and metadata files. It contains no hand-written run
receipt.

The finite corroboration checks 439 literal rational Gram factorizations,
15,451 pairing bills and 55,490 actual forced identity minors. It exhausts all seven
nonempty paired graphs on three vertices, every coordinate split,
every cross coefficient in {-1,0,1}, and every fitting directed pairing.
A separate two-edge matching checks all 4096 fitting directed pairings
for each of two specified changed bases. This includes all directed
entries between disjoint edges, which the coordinate-only bill ignores.
Exact rational fixtures also cover full and paired-deleted graphs in
dimensions four through eight, with seven deterministic pairings each.
Those larger fixtures are samples, not complete basis or pairing censuses.

Binary elimination and a separately implemented cardinality-of-span
oracle agree throughout the complete small cases. Boundary controls
distinguish required nonorthogonality zeros, diagonal ones, sign-pair
survival, characteristic two and the rank-one price of an all-ones mate
block. Invalid geometry, split and coefficient inputs reject.

## Limits and implementation notes

The written proof supplies all-size coverage. The executable checker
uses only its fixed finite case table. Arbitrary changing-split shear
products, general bases, single-sign punctures, extra terms and factors
outside the root code are outside scope. Physical frames, storage,
precision, native calls, compiler and outer recovery are unrun. Independent
human and formal proof-kernel review are unclaimed.

Power of Ten deviations: CPython and Fraction allocate dynamically.
Fixture dimensions are fixed to 2..8, root counts to at most 56, and the
complete pairing census to at most 12 free bits. The independent span
oracle admits at most eight rows and hence at most 256 span elements.
Every loop has a finite case-table or explicit collection bound. There
is no recursion, dynamic code, imported predecessor executable, network
or subprocess in the verifier. Functions fit within 60 lines; explicit
checks remain active under optimization. Warning-strict normal and
optimized Python are the interpreted-code diagnostics. No shared tool
or build configuration is changed.

## Open next questions

1. Can a product of two shears with changing coordinate splits lower
   the optimized cost of one paired D5 graph? Start with a literal exact
   factorization and optimize one common fitting pairing across all
   terms. The blocker is that a term may lose its coordinate anchor;
   the identity minors above then need not survive.
2. Which single-sign deletions allow a useful basis-dependent gain over
   the fixed-coordinate value 2e? Start with one explicit puncture and
   a complete factorization, retaining the same pairing at every term.
   The theorem here uses both signs to prevent total cancellation; a
   cheaper isolated factor is insufficient evidence of a decoder gain.

The structured questions in [TASK.json](TASK.json) include their
relevance, first steps and blockers. Neither question starts another
construction or search campaign here.

## Credit and sources

This package was produced by Nick Petalas. New material is Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

ywz65 supplied PR2536's exact coordinate-pairing spectrum and open basis
question. Aaron Wang / navinor supplied [PR2272](https://github.com/CrocSwap/integer-mult-bounds/pull/2272)
and [PR2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518)'s
root conventions and finite screens. DreamingOfClouds supplied
[PR2125](https://github.com/CrocSwap/integer-mult-bounds/pull/2125) and
[PR2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277)'s model
and dense/root-code lineage. ywz65's [PR2719](https://github.com/CrocSwap/integer-mult-bounds/pull/2719)
allows all root-code term counts on full Dn with a fixed dense pairing;
it is cited context and does not settle this variable-pairing puncture
question. Those results and all retained predecessor credit are unchanged.
No predecessor executable or mathematical census is replayed here.

DreamingOfClouds's open [PR3045](https://github.com/CrocSwap/integer-mult-bounds/pull/3045)
already gives the full D4 square-root-code floor 12 for arbitrary fitting
pairings and arbitrary bases. That full-D4 subcase is not new here. Its
D6 general-basis/global-pairing question remains open; this package
settles only the coordinate-anchored bipartite basis family, including
paired punctures in every dimension. The companion open
[PR2832](https://github.com/CrocSwap/integer-mult-bounds/pull/2832)
records broader decoder and batching reductions; it does not claim this
paired-puncture basis theorem.

[SOURCES.json](SOURCES.json) pins the predecessor texts as historical
provenance at canonical main a5df48c55ea806d7952b65acc9c76d878ff09b13,
priority revision 7. The card is explicitly changed from a physical
rank-shape construction to this original algebraic obstruction. The
first experiment follows PR2536's suggested single-shear example. The
historical fixed-invoice ceiling is outside this changed model and is
not an acceptance test for it. The selected metadata orientation passes;
no selected cold replay is claimed.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144833)
records the question. Live PRs, recent account contributions, handoffs,
active Discussions, distinctive main-tree/merged searches and local
reservations were checked. The cached snapshot covered 331 open PRs
and 4340 Discussion records at 11:38..11:39 UTC on October 23, 2026.
Only 166 of 6918 HEAD notes were materialized for that cached search;
the relevant predecessors and all-main distinctive-term searches
supplement it. Arbitrary historical diffs and unpublished work remain
coverage limits, so search absence is not a novelty certificate.
