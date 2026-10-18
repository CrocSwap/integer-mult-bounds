# Seven-source singleton connectors: f(7) = 24

**The minimum universal restored seven-source singleton word has 24 steps.**
This matches Douglas Colkitt's existing Gray-cycle construction from
[PR1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185).
The new work excludes every shorter word, including both the repeated-prefix
and simple-cycle cases at length 22. It answers the length-22 question left
open by Nicholas Stone's corrected census in [PR2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973).

The result is a finite computational proof in Ross Richardson's
[PR943 interface](../universal-connector-boundary/README.md): immutable
sources, an arbitrary dirty connector, singleton source additions, paired
readouts, and eventual restoration. It is not an unrestricted query optimum,
a physical implementation, a new supplier, or a multiplication-exponent claim.

The proof uses a published covering-code bound and a published finite
classification as mathematical premises. It does not rerun their original
classification searches or claim proof-assistant verification.

## 1. Prefix covers and the minimum set size

For a length-L source word w, start at q_0=0 and flip its named coordinate at
each step. Restoration means q_L=0. The credited paired-readout criterion is

```text
w is universal iff P+P = F2^7, where P={q_0,...,q_(L-1)}.
```

Choose a in P and translate P to Q=P+a, which contains zero. Use the distinct
nonzero members of Q as columns of H. Then

```text
{H e : weight(e) <= 2} = Q+Q = P+P.
```

A full cover makes H rank seven and ker(H) a codimension-seven binary linear
code of covering radius at most two. A set of at most nineteen points would
supply at most eighteen columns. Its radius cannot be zero or one, since there
are at most nineteen zero/one-column syndromes, fewer than 128.

[Struik, *Covering Codes*, Bound 3.13, printed pp. 42–43](https://pure.tue.nl/ws/portalfiles/portal/2274131/425174.pdf#page=55)
states ell(7,2)=19, also recorded in the
[1994 journal paper](https://doi.org/10.1109/18.333857).
Thus **every cover has at least twenty points**. The source credits an earlier
Ytrehus proof; this application does not claim a new coding bound. DMP's
Table 1 independently records ell(6,2,1)=19, the smallest size of a minimal
1-saturating set in PG(6,2); any 1-saturating set contains a minimal one, so
the twenty-point floor rests on two published sources.

**Corollary.** No 17-, 18- or 19-point subset of F2^7 is a difference cover.
This settles the set-level 17/18-point cover questions pursued in PR2773,
PR2870, PR2911, PR2933 and PR2961, including their remaining (12,6), (11,7)
and (9,9) classes, directly from the literature. No further class search is
needed for f(7).

## 2. Every minimum cover needs at least 24 walk steps

Davydov, Marcugini and Pambianco's
[complete classification](https://arxiv.org/pdf/1802.04214v1), section 2,
Table 1 and Table 6, lists exactly five minimal 19-point 1-saturating sets
in PG(6,2). Translating any 20-point cover to contain zero and deleting zero
gives one of these sets up to GL(7,2): it is minimal by section 1. Consequently
every 20-point cover is an affine image of one of the five augmented examples.

For each example, an exact hyperplane cut partitions it into A and B with:

- sizes 4 and 16, and affine ranks 2 and 6;
- disjoint nonzero internal direction sets A+A and B+B;
- exactly one unordered pair for every cross direction a+b.

Both Python implementations check these properties. Their cut normals are
67, 126, 64, 64 and 61 in the published coordinates. The properties are affine
invariant, so classification transfers them to every minimum cover.

For a nonempty finite X, a graph using directions D and having c components
satisfies affine_rank(X) <= rank(D)+c-1. Choose one root per component:
edge directions generate differences within each component, while differences
between roots contribute at most c-1 further dimensions.

Partition any seven directions into a internal-A, b internal-B and t cross
directions. The two internal graphs have at least 3-a and 7-b components.
Each cross direction contributes only one edge, so the entire graph has at
least 10-(a+b+t)=3 components. This does not require direction independence.

A cyclic walk containing this cover T needs at least three positions outside
T to separate visits to those components. Therefore L >= |T|+3=23. Restored
singleton words have even length, giving **L >= 24**. Positions are counted
with multiplicity. In particular, no 22-step word can contain a minimum cover.
A 20-step word has exactly twenty positions, so its prefix set would be a
20-point cover visited with no outside positions; the same argument excludes
it. Hence **f(7) >= 22 follows from sections 1-2 alone**, with no word census.
It uses neither the PR2542/PR2634/PR2691 censuses, whose pruning PR2973 reports
as unsound, nor PR2973's corrected census.

## 3. The entire 21-prefix case is excluded

The only remaining shorter length is 22. Suppose it has exactly 21 distinct
prefixes. Rotate its unique repeated vertex to zero. Removing zero gives a
minimal 20-column 1-saturating set: otherwise a 20-point cover would remain,
contradicting section 2. DMP's complete size-20 classification has 36 classes,
also transcribed in [table6.json](table6.json).

The walk multigraph has degree four at zero and degree two elsewhere. Its
seven directions form a basis. The functional equal to one on every direction
splits the vertices into ten even and eleven odd points. Both checkers examine
all 402 weight-eleven characters across the 36 classes.

A preliminary removable-point/component screen excludes twenty classes. It
retains sixteen classes and 234 character cases. For each, there are exactly
two structural possibilities:

1. All edges are simple. Each basis direction needs at least two pair
   representations. The induced support graph needs degree at least four at
   zero and at least two everywhere else.
2. An edge 0–v is doubled. The other endpoint exhausts its degree, and removing
   it leaves a simple 20-cycle. There are eleven possible odd leaves. Select
   v as a mandatory direction; each other direction needs two representations
   among the remaining twenty points. The mandatory direction can have no
   ordinary-cycle edge or can also occur on that cycle. Every remaining vertex
   needs support degree at least two.

Both checkers exhaust all **234 characters and 2,808 structural branches**.
There are **zero independent support bases**, even before solving for edges.
The primary implementation uses binary include/exclude decisions and span
closure. The independent implementation uses combination branches at deficient
vertices and Gaussian elimination; it omits graph-connectivity pruning.

The branch rules preserve all completions. Dependent directions cannot enter
a basis, and degree deficits force enough incident directions. The combination
search partitions completions by their first required incident directions,
leaving larger directions available. Once degree bounds hold, matroid
augmentation completes a partial independent set whenever the union has rank
seven. Planted positive controls cover both graph types, including a pendant
with no ordinary edge in its mandatory direction.

Thus a 22-step candidate must have **22 distinct prefixes: a simple cycle**.
The two implementations also independently check the correspondence, geometry,
character calculations and 32,640 small direction graphs.

## 4. Only two simple-cycle multiplicity patterns remain

Deleting a source coordinate projects a universal word to a universal word on
six sources. The exact known value f(6)=16 therefore bounds each multiplicity
by 22-16=6. Deleting two coordinates and using f(5)=12 bounds their sum by ten.
All seven multiplicities are even by restoration and positive because an
unused coordinate confines P+P to a hyperplane, leaving exactly

```text
A: (6,4,4,2,2,2,2)
B: (4,4,4,4,2,2,2).
```

The cycle checker freshly replays the small censuses underlying those credited
PR943/PR1185 lower bounds, without trusting stored PASS receipts:

| Sources / length | Canonical words | Maximum coverage |
| --- | ---: | ---: |
| 5 / 10 | 945 | 31 / 32 |
| 6 / 12 | 10,395 | 49 / 64 |
| 6 / 14 | 945,945 | 59 / 64 |

It also checks the length-12 five-source and length-16 six-source constructions.

## 5. Complete small-path searches exclude A and B

In pattern A, project onto its four twice-used coordinates. The low word has
eight steps with counts (2,2,2,2); the remaining high coordinates have counts
(6,4,4). There are 105 canonical low words, 26 universal ones, and five orbits
under cyclic rotation, reversal and coordinate permutation.

In pattern B, project onto one four-use coordinate together with the three
twice-used coordinates. The ten-step low word has counts (4,2,2,2), with its
four-use coordinate distinguished. The other three coordinates have counts
(4,4,4). There are 18,900 raw low words, 3,150 canonical rooted words, 1,310
universal rooted words and **77 dihedral orbits**. A separate Python enumeration
independently agrees on all 77 orbit memberships. These are necessary projected
covers, not an assumption that linear maps preserve cube edges. Full-word
rotation and reversal, followed by low-only coordinate relabeling and a
translation of the start state, preserve the high multiplicities. Hence the
projected dihedral representatives suffice for the complete word search.

Between consecutive low steps, the high state follows a simple path in Q3.
The complete table has **106 normalized path types**, identified by vertex
set, endpoint and the three coordinate counts. Translation gives 848 choices.
Replacing a path by its stored representative preserves every relevant field.

The checker enumerates every gap vector summing to fourteen high steps for A
or twelve for B. Each gap is at most seven. It then solves the finite path
constraints:

- neighboring endpoints agree cyclically;
- coordinate totals match the target;
- blocks at the same low vertex have disjoint high masks;
- for every low difference, the union of high sumsets is all of F2^3.

These conditions are exact. They reconstruct a simple restored word, and all
128 required differences are tested. Pruning only removes candidates lacking
binary support, candidates outside possible count totals, or candidates missing
a difference even after taking optimistic unions of all remaining choices.
The parity-capacity test counts possible pairs separately by high parity,
including pairs between repeated low blocks. The source explains each rule.

All five A orbits and all 77 B orbits must exhaust with zero witnesses. Resource
limits produce an incomplete result and a failing replay. Positive controls use
actual universal simple 24-cycles in two ways: with every block fixed to its
true path, which checks propagation, and through the full gap enumeration,
capacity test, start domains and branching from the low orbit alone, which
must rediscover a universal word for each pattern. Negative controls include
noncovering simple 22-cycles and universal words with repeated prefixes.
The rediscovery receipt must have more search nodes than capacity survivors:
each survivor creates one root call, so the excess certifies recursive branching.
Both patterns share a sixty-second control budget; the registered replay remains
serial and bounded, with incomplete or over-budget runs failing closed.
The pattern A exclusion is corroborated by an independent Python port and
solver checks; the pattern B exhaustion rests on this single native
implementation, each of whose pruning rules is a stated necessary condition.

Consequently neither A nor B admits a simple universal 22-cycle. Combined
with sections 1–4 and the credited 24-step upper construction, **f(7)=24**.

## Reproduction and evidence limits

From the repository root, with Python 3.12 and a C++17 compiler (Clang or GCC):

```sh
python3.12 -I -B scripts/research_package.py --package research/connector-covering-code
```

[VERIFY.json](VERIFY.json) registers the two Python implementations in ordinary
and optimized mode, plus the native cycle replay. Compilation and execution
are serial; temporary build files are removed. There are no Python package or
solver dependencies for the registered proof replay. The compiler environment
and exact run results are recorded in [TASK.json](TASK.json). All 82 orbits
also exhausted with the per-candidate conditional coverage pruning disabled:
22,594,820 gap vectors and 157,402,440 search nodes, with zero witnesses.

An independently implemented Z3 model provides additional checks; solver
timeouts are never counted as exclusions. For pattern B it returns three UNSAT
and 74 timeouts, so it is not a second complete B proof. It is not a default
dependency.
The original published coding/classification searches, proof-assistant checking,
hosted CI and human peer review remain outside the completed verification.

## Open next questions

1. Can a shorter proof replace the finite support and path searches, or remove
   the dependence on the published 19/20-column classification?
2. How does the optimum change under a specified, fully charged extension of
   the singleton alphabet? This theorem does not cover DUO or TRIO calls.
3. What can these reductions say about eight sources? No eight-source bound
   beyond credited predecessor work is claimed here.

## Attribution and related work

Prepared by **conorholds**, with substantial OpenAI Codex assistance in
mathematics, implementation, independent checking and writing, including
GPT-6.1 SOL agents at xHigh reasoning. A later independent audit, the
resulting fixes and the full-enumeration control used Anthropic Claude
(Fable 5.1) agents. New work is Apache-2.0. Separate AI reviews are not
independent human review.

Struik's bound credits Ytrehus; DMP own the published classification and all
41 transcribed representatives. Ross Richardson/PR943 supplies the exact dirty-
connector model and five-source result. Douglas Colkitt/PR1185 supplies the
six-source result and the retained seven-source upper construction.
Aaron Wang's PR2542, PR2634, PR2773, PR2870, PR2911, PR2933 and PR2961 and
Nicholas Stone's PR2691 investigated the smaller-cover and length-20 questions;
these historical censuses are not retained here as established exclusions.
Nicholas Stone's [PR2973](https://github.com/CrocSwap/integer-mult-bounds/pull/2973) then reported that the
PR2542/PR2634/PR2691 word censuses applied an unsound bit-0 collision budget,
supplied a corrected length-20 census giving 22 <= f(7) <= 24, and left
length 22 as its first open question. Tekalign's [PR2984](https://github.com/CrocSwap/integer-mult-bounds/pull/2984) and
Nick Petalas's [PR3005](https://github.com/CrocSwap/integer-mult-bounds/pull/3005) replay that corrected census and also
leave length 22 open. Aaron Wang's KB3h claim
([Discussion 1166, comment 18976193](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18976193))
was [released](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18980743)
as [PR3023](https://github.com/CrocSwap/integer-mult-bounds/pull/3023), which excludes
the (12,6) A-vanish (5,1) class and leaves the (4,2)/(3,3) and other splits open.
The API records the release at 2026-10-16T18:38:30Z. This proof
answers PR2973's open question and makes the remaining cover classes
unnecessary through the section 1 corollary; it relies on none of those
censuses or class searches. Exact source heads and literature locators are in
[SOURCES.json](SOURCES.json).
