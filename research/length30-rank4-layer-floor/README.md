# Rank 4 cannot use a 16-point layer at length 30

**Scoped proof, with an exhaustive finite census. No new κ.** Selected κ
stays `781451/250000000`. The gap `28 <= f(8) <= 32` is unchanged. This does
not decide whether a universal length-30 word exists.

In the restored binary singleton model, a universal closed word of length 30
cannot have a multiplicity-2 sojourn of rank 4 with exactly 16 distinct
layer-0 projections. Inside the stated window of 8 to 14 layer-1
projections, every such sojourn therefore has at least 17 layer-0
projections and at most 13 layer-1 projections. The 14-point layer-1
boundary is empty. The same pair and fiber inequalities also admit one
case outside that window, `|Q1| = 6` with `|Q0| = 24`. That case is not
censused.

## Scope

The question is open question 1 of
[#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015): whether a
universal length-30 word exists when every multiplicity-2 sojourn has rank at
least 4, with at least 16, 15 and 12 layer-0 projections at ranks 4, 5 and 6.
This package takes the stated first step at rank 4. It fixes one
multiplicity-2 source whose open sojourn has rank 4 and whose layer-1
projection has between 8 and 14 points, and it censuses the complementary
layer of size exactly 16. That layer is the cardinality boundary of the
window. The census is empty, so every surviving complementary layer has at
least 17 points.

Card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**. The card asks for one new connector operation. The alphabet stays
the published singleton alphabet. The new fact is the rank-4 size restriction
above. Base commit `17469fff78c22941280f04d39dc5a1faee09c840`.

The argument is in [PROOF.md](PROOF.md). The sixteen-point nonexistence is a
proof. Its finite step is an exhaustive census of the `120^7` normalized
two-point fiber tuples, with a prune whose soundness is written there. It is
not a heuristic search, and it is not a proof that no universal length-30
word exists.

## Evidence and reproduction

CPython 3.12 and gcc, standard library, from the repository root:

```sh
python3 -B research/length30-rank4-layer-floor/verify.py
python3 -O -B research/length30-rank4-layer-floor/verify.py
python3 -B scripts/research_package.py --package research/length30-rank4-layer-floor
python3 -B scripts/check_research_commit.py --package research/length30-rank4-layer-floor
```

Expected marker:

```text
PASS_LENGTH30_RANK4_LAYER16 solutions=0 nodes=57685490 branch1_nodes=515051 layer0_floor=17 layer1_ceiling=13 witness_coverage=255
```

The verifier checks the pair and fiber window, constructs a basis for each of
the 15 nonzero differences, recomputes one branch of the fiber tree in
Python, and compiles `layer16_census.c`. The C search scores the same branch
and then the full normalized tree. A fixed eight-fiber fixture partitions the
odd quotient directions and misses the even ones. The coverage-255 witness,
a swapped failure control, the normalized rank-4 layers of that witness, and
the length-32 Gray concatenation are checked. Checks raise on failure, so
`-O` does not disable them.

Not run: the seventeen-point fiber census, ranks 5 and 6, length 28, a SAT
encoding of the remaining words, a proof assistant, Lean, Docker, the
selected cold replay, and `f(7) = 24`. The source-history preflight was not
run: this checkout is shallow, and that preflight requires full Git history.
The byte preflight without `--check-source-history` is the command above.

## Overlap

Upstream main was fetched at session start and was
`17469fff78c22941280f04d39dc5a1faee09c840`. Open-PR search for a length-30
rank-4 layer census found [#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015)
and no package that decides this boundary. [#7015](https://github.com/CrocSwap/integer-mult-bounds/pull/7015)
blocks rank 3 and leaves rank at least 4 open; its first open question is
the question narrowed here. [#6943](https://github.com/CrocSwap/integer-mult-bounds/pull/6943)
is the rank-at-most-2, bent, and 4+4 predecessor. [#6966](https://github.com/CrocSwap/integer-mult-bounds/pull/6966)
is the length-28 arc floor and is not used. No match is a novelty certificate.

## Open next questions

1. Does a universal length-30 word exist when every rank-4 multiplicity-2
   sojourn has at least 17 layer-0 projections, layer-1 size 6 or 8 through
   13, and ranks 5 and 6 keep the floors 15 and 12? A yes answer would lower
   the published upper bound on `f(8)` from 32 to 30. The coverage-255
   witness still meets the tightened floor and misses only mask 131. First
   step: census one rank-4 layer of size 17, whose only fiber shape on the
   8-to-13 side is one triple and seven pairs, or search one complementary
   arc in that range. The size-6 layer is a separate necessary case with
   `|Q0| = 24` and was not part of the 8-to-14 search. Blocker: at size 17
   each direction has 18 sums available against 16 targets, so the exact
   packing used here stops. Length 28 is a different question.

## Credit

Ross Richardson, #943, for the singleton model and prefix criterion. Douglas
Colkitt, #1185, for the length-32 Gray upper construction checked here as a
positive control. conorholds, #3058, for `f(7) = 24` and the eight-source
question; that theorem is not used. Nick Petalas, #5234 and discussion
comment 19377982, for the deletion floor and the length-30 handoff. Nicholas
Stone, #5430, for the fixed-projection lift obstruction, which this split
does not reuse. Upstream pull request 6943 for the rank-at-most-2
obstruction, the bent lower bound, the 4+4 argument, and the coverage-255
witness. Open pull request 7015 for the rank-3 blockage and for the rank-4
window whose sixteen-point boundary is settled here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0. Independent human and proof-kernel review are unclaimed.
