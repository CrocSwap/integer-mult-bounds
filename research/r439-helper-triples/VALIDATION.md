# Validation receipt and limits

Research base: `007664306fff84fbb1c9a1b4053b69f439764034`.
Assignment seed: 12. Local run date: 2026-10-13 UTC / 2026-10-14 Melbourne.

The initial complete receipt was generated with:

```sh
BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -I -B research/r439-helper-triples/verify.py --record --output /private/tmp/r439-helper-triples-verification-seed12-v2
```

Environment: CPython 3.14.6, macOS 26.5.2 arm64, Apple clang 17.0.0
(`clang-1700.6.4.2`), Boost 1.87 headers. The Boost path is local build
configuration, not a required fixed path. No network is needed for replay.

`EXPECTED.json` records the complete deterministic receipt. It includes:

- 168 independently enumerated GL(3,2) maps and 1,008 distance edges;
- 1,774,080 independently rescored choices with an identical census digest;
- 155 guarded complete words and 3,688,220 literal positive instructions;
- 40 accepted replacements, 115 exact guard rejections, 780 conflicts;
- 661 separate arbitrary input columns, four words, both D directions;
- ten local control categories and a charged cancelling-pair control;
- unchanged owning E8/frame/endpoint checks on all four words;
- original, PR915 and candidate native legality plus 5/9/11-stage replays,
  covering 883/1,327/1,549 columns per word and 144 rejected omitted bridges;
- unchanged rank mass 5,129, all paid rank counts, nine COPY/ERASE pairs,
  and every register's MOVE path;
- exact source-bound 104-bit local and 192-bit nine-stage inequalities.

The ordinary verification command was then rerun into a fresh directory,
without `--record`, and passed exact comparison of the full committed receipt:

```sh
BOOST_INCLUDE=/private/tmp/boost_1_87_0 python3 -I -B research/r439-helper-triples/verify.py --output /private/tmp/r439-helper-triples-final-seed12
```

Final status: `PASS_R439_HELPER_TRIPLES_FINITE`. This fresh run rebuilt all
four C++ binaries and reran the complete checks listed above. Both the
certificate and regenerated gzip payload compare canonically and completely.

The independent census and group check passed on the first implementation
run; its reporting layer then tried to serialize byte-valued boundary columns
as JSON and raised TypeError. That comparison was changed to direct byte
equality. The completed fresh run above passes every stage. This was a
verifier implementation error, not a circuit counterexample or failed search.

`make selected-record-check` passes for PR890 at the exact base. Repository
wide `make verify`, complete cold supplier reconstruction, whole-hosted
adoption, outer assembly and Lean multiplication formalization were not run:
this isolated research package changes none of their inputs or selected
artifacts. The native checks are scoped evidence, not substitutes for those
remaining admission obligations. Hosted CI status is separate from these
local checks and is reported in the PR.

The open queue was refreshed through PR962 before packaging. PR941's
disjoint-pair result and PR952's phase-A synthesis remain distinct. Main
still matched the exact base at that refresh. No coordination issue was
pinned; the claim and final result are recorded locally in CLAIM.json.
