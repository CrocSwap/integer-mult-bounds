# At most 23 distinct adjacent pairs in a length-28 universal word

**Scoped written proof with exhaustive finite corroboration and an explicit sharp
example. No new kappa.** Selected kappa stays `363005817/100000000000`
(0.00363005817).

Consider a closed cyclic word of length 28 over the eight coordinate directions
of `F_2^8`, with letter multiplicities `(4,4,4,4,4,4,2,2)`, the profile that
[#5234](https://github.com/CrocSwap/integer-mult-bounds/pull/5234) shows is
necessary at length 28. This package proves:

> **Theorem.** Let `D(w)` be the number of distinct unordered pairs
> `{w_t, w_{t+1}}` of cyclically consecutive letters. Then `D(w) <= 23`, and
> 23 is attained.

Equivalently, at least 5 of the 28 adjacent-pair slots repeat an earlier
unordered pair. A two-letter arc contributes the sum `e_i + e_j`, so at least
5 of the 28 weight-2 basis sums cannot be produced by a two-letter arc and must
come from arcs of even length at least 4.

The proof is a degree count on a graph attached to the word. Each occurrence of
a letter participates in exactly two adjacent pairs, so the number of distinct
partners of a letter is at most twice its multiplicity; the two letters of
multiplicity 2 have at most four partners out of seven and therefore each miss
at least three edges of `K_8`. Their missing sets can share at most the single
edge between them, so at least five edges are missing and at most
`28 - 5 = 23` distinct pairs remain. Sharpness is an explicit loop-free
multigraph with degree sequence `(8,8,8,8,8,8,4,4)` on 28 edges, 23 of them
distinct, whose Euler circuit realizes the profile.

A consequence excludes the most natural construction: a word whose 28 adjacent
pairs are all distinct would have every letter count equal to `7/2`. Thus no
Euler circuit of `K_8` (or of any simple graph with 28 distinct pairs) is a
length-28 word with the required profile, and a census that enumerates such
circuits is provably incomplete.

## Scope

The result is a combinatorial constraint on the input word. It does not
construct a universal length-28 word, does not prove one impossible, and does
not change `28 <= f(8) <= 32`. The question it constrains is Open next question
1 of `research/length28-sojourn-rank` (#6966), which asks whether a universal
length-28 word exists with every multiplicity-2 arc using at least four other
sources.

Priority card `connector-alphabet-change`, priority revision 8. Scope status:
**changed**; the card asks for one new connector operation, while this package
keeps the singleton alphabet and adds a necessary condition on the word.
Base commit `e54523517d0f03e58352e647c403a5af3e525a57`.

## Result in detail

Write `m_i` for the number of occurrences of letter `i` and `mult(i,j)` for the
number of slots whose unordered pair is `{i,j}`. Let `G` be the simple graph on
the eight letters with `{i,j}` an edge when `mult(i,j) > 0`.

1. **Incidence identity.** `2 m_i = sum_{j != i} mult(i,j) + 2 loops_i`.
2. **Degree bound.** `deg_G(i) <= min(2 m_i, 7)`.
3. **Complement count.** The two letters with `m_i = 2` have `deg_G <= 4`, so
   each misses at least three edges of `K_8`. Two such missing sets share at
   most the edge joining the two letters, so at least 5 of the 28 edges are
   missing.
4. **Sharpness.** The word `0107547156453236250432413021` is closed, has counts
   `(4,4,4,4,4,4,2,2)`, and has exactly 23 distinct adjacent pairs.

The bound is tight as a statement about the profile. It is not tight for
universality: the exhibited word has only 156 distinct arc sums, so it is not
universal.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
python3 -W error -I -B research/length28-adjacent-pair-degree-obstruction/verify.py
python3 -W error -I -O -B research/length28-adjacent-pair-degree-obstruction/verify.py
python3 -B scripts/research_package.py --package research/length28-adjacent-pair-degree-obstruction
```

Expected marker:

```text
PASS_LENGTH28_ADJACENCY_DEGREE words=484417 D_max=23 sharp_D=23
```

The verifier exhaustively checks the lemma on 484,417 closed words over at most
five letters, checks the complement arithmetic, rebuilds the sharp multigraph
and its Euler circuit, and confirms the all-distinct arithmetic. It runs in
about 1.5 seconds.

## Evidence status

The written proof is the argument above. The verifier corroborates the finite
claims exactly; it is not a proof kernel. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

1. Does a universal length-28 word exist at all? The present bound leaves the
   five weight-2 sums to longer arcs; a census can now restrict to words with at
   most 23 distinct adjacent pairs, but no exclusion follows.
2. Can the same degree count be sharpened with length-3 or length-4 arc
   constraints? The count uses only length-2 arcs, and the sharp example shows
   the length-2 budget alone cannot exclude the profile.
3. Does the arc-rank constraint of `research/length28-sojourn-rank` combine with
   the 23-pair bound to exclude the rank-4 arcs it leaves open?

## Credit

Ross Richardson, #943, for the singleton model and the prefix criterion.
conorholds, #3058, for `f(7) = 24` and the eight-source question. Nick Petalas,
#5234, for the length-28 floor and the multiplicity profile used as the premise.
unpaidmoon, #6966, for the arc-rank constraint and for posing the sharpness
question this package constrains. The degree count, the sharp multigraph and the
verifier are new work.

## Overlap

The search covered open and merged PR titles and bodies for `length-28`,
`4,4,4,4,4,4,2,2`, `adjacent pair`, `Euler circuit` and `difference basis`, and
the live handoff thread. No earlier package states a bound on the number of
distinct adjacent pairs. #5234 and #6966 bound arcs by rank, not by adjacency
degree; #5430 and #6497 fix one projection. No match is a novelty certificate.
