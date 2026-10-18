# Information flow through the fixed P104 joint flags

PR2981 supplies 208 explicit nested flags that realize both prescribed endpoint
covers. Those **fixed full flags cannot implement the missing `I-G/2` correction**
in the frozen X-only monotone common-chart model: only **323 of 4,992** required
source-to-target pairs have a directed information path. The other **4,669**
pairs are unreachable, even in the favorable relaxation below.

This answers a concrete part of [PR2981's dependency handoff][2981]. It corroborates
the predecessor's stated distinction between static geometry and a correction
program; it reports no defect in its correctly scoped certificate. The result
is specific to its published full flags, including the intermediate spaces.
Another basis extension or matching may change reachability. No new lifetime
floor, supplier, selected exponent or complete multiplication theorem is claimed.

## Exact model and support invariant

This checks added correction operations; the retained `G/2` channel is held
fixed. Use the original PR1972/1991 increasing X/Y paths. The 104 sources X are
immutable logical values, and Y are unread additive targets. New helper inputs
are arbitrary dirty values independent of X. A helper visits the ten prefix
spans of one of PR2981's nine-vector ordered bases, from ZERO to FULL.
Transport preserves its logical value in the new common chart. Scalar linear
mixing between helpers, reads from X and additions into Y require **equal
frames**. Inclusion or equal dimension alone does not make a scalar contact.
Original helper/private-query reads, source writes, target feedback,
source-dependent helper initialization and new frame transitions are excluded.
These are hypotheses of this X-only test, not restrictions on every P104 design.

Construct a directed graph as follows:

1. A node is a distinct frame occurring in a data path or helper flag. Merge all
   occurrences of the same frame, even at different times and in different roles.
2. Each consecutive helper prefix gives a forward edge. Duplicate edges are
   merged. There are 1,599 nodes and 1,625 distinct edges from 1,872 occurrences.
3. For source s, seed every frame in its X path with s. Grant every such snapshot
   freely and at any time. Propagate source sets along the forward helper edges.
4. A target may receive every source reaching any frame in its entire Y path.

This drops timing, bandwidth, register availability and dirty-restoration
requirements, all in favor of the proposed correction. Arbitrary interleavings and repeated
free mixing cannot repair nonreachability in this graph.

**Necessary condition.** Every source on which a helper's current logical value
depends belongs to the reachability set at its frame. Initially its arbitrary
dirty value has no X dependence. Transport follows a graph edge. A common-frame
linear operation can only combine the source supports already present at that
node; an X read adds one of the granted seeds. Induction through any permitted
program proves the invariant, regardless of cancellations or relay depth.
Target additions can therefore involve only the union over that target's
visited frames. The argument also follows by varying one X input while holding
all other source and dirty inputs fixed.

A missing required pair disproves the correction for these flags. A reachable
pair is merely permitted by this relaxation: no simultaneous schedule,
coefficient factorization, restoration or cost upper bound follows.

## Explicit cut and full finite result

With zero-based indices, the doubled ordered roots are

```text
X4: (0,0,0,0,2,0,0,-2)
Y0: (0,0,0,0,0,2,0,-2).
```

Their doubled dot product is 4, so the ordinary Gram entry is 1 and the required
correction coefficient is `C[0,4] = -1/2`. Every source snapshot for X4 lies in
a **22-node forward-closed set**, while every Y0 frame lies outside it. No helper
edge leaves the set. Thus the correction has zero X4 dependence at Y0, where
`-X4/2` is required. Composing it with the retained `G/2` channel leaves this
off-diagonal coefficient uncancelled.

[RESULT.json](RESULT.json) retains all 22 frames, the input roots and coefficient,
and the complete 104-by-104 required/reachable/missing relations. Each mask list
is indexed by target; source s is bit s of its hexadecimal integer. Each target
requires 48 sources, of which only two through six are reachable. The full
required-pair recount gives 323 reachable and 4,669 missing.

The primary checker reconstructs ordered roots from the standard E8 root
families, validates their label/target-frame binding, and propagates 104-bit
source sets in increasing frame dimension. The independent checker enumerates
the doubled E8 lattice directly, uses reduced binary row bases instead of span
bitmaps, and runs a separate BFS for each source. It imports neither the primary
checker nor predecessor implementations and compares every receipt field.
Both share the authenticated mathematical inputs and the written model. These
are two algorithms by the same assistant, not independent human review.
Earlier frame-contact/cut work by Adam Gall / PR2090 and Jeremy Diviney /
PR2113 already uses information-flow relaxations on the original channel.
This contribution applies that standard reasoning to PR2981's new fixed flags
and records their complete missing-pair relation and explicit cut.

## Reproduce and validation

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-flag-information-flow
```

Direct read-only checks work without Git or network:

```sh
python3 -I -O -Werror -B research/p104-flag-information-flow/verify.py
python3 -I -O -Werror -B research/p104-flag-information-flow/independent.py
python3 -I -O -Werror -B research/p104-flag-information-flow/test_verify.py
```

`verify.py --emit` prints the regenerated receipt. Default replay authenticates
four declared live inputs before interpretation, then compares the complete
typed receipt. [SOURCES.json](SOURCES.json) pins SHA256s and Git blobs.

Seven behavioral groups cover both actual CLIs; all 32 subgraphs of a small
five-edge example; positive two-hop relays; missing contacts and wrong direction;
equivalent basis spellings; a forged edge crossing the cut; dependent flags;
Boolean/integer confusion and duplicate keys; source and relation corruption;
and optimized Git-free read-only exports. Reversing all transport edges falsely
permits X4-to-Y0, demonstrating why their direction matters.

Local validation and exact commands are recorded in [TASK.json](TASK.json).
This package does not replay native identities, precision, physical owners or
tape movement, the complete caller or selected cold construction, or all-size
lifting. They are unnecessary for this support obstruction and remain separate
obligations for any changed candidate. Hosted CI and formal-kernel review are
not claimed.

## Open next questions

Can a **changed named flag collection** provide all required paths? First pin
one specific intermediate-frame or matching change, then run the support test,
including X4-to-Y0, before scalar synthesis. If it passes, attach chronological
acquisition/delivery times and prove coefficients, dirty restoration and the
complete physical/consumer bill. A favorable graph alone supplies none of those.
[TASK.json](TASK.json) records the relevance, first step and blockers.

Family decision: finish this named-witness calibration and stop. There is no
alternate-flag search, numeric lifetime-threshold refinement or construction
expansion in this contribution. The previously reported stronger program-level
lifetime floors are neither challenged nor re-proved here.

## Sources and credit

Started from current canonical main
`b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`, priority revision 5. Task picker nonce
`63ac7de32d4e8713ab250a621732276b`, complex-mechanisms / p104-side-correction,
refined to PR2981's explicitly missing information-flow implication.
[Canonical claim and status][claim].
Submission is rebased onto revision-6 main
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`. Its refreshed P104 card names this
same dependency gap. Original scientific/provenance pins are retained; the
selected record and four live inputs are unchanged.

Credit Nick Petalas / PR2981 (`3d24b92d8ba057b57cb2d480170ec407520e6882`) for
the full static flags and handoff, and PR2920 for the fixed covers. Retain
PR2953's distinct joint cheap-flag obstruction, Sudarsh Chaturvedi / PR2924's
reported lifetime-floor screen, Hiroki Kumazaki / PR2889/2353's monotone model,
ywz65 / PR2614's later-read-aware departures, Arham Tahir / PR2675/2682's
coupled budget, Sagar Thakrar's mixer handoff and Philippe Van Velzen's relay
work. The original inputs retain Rohan Arun / PR1972, Chafik Boukhalfa / PR1991,
Adam Gall / PR1940, Josie Elliston / PR1071, Ali Romman / PR1125 and their
geometry/native/compiler lineage. Their predecessor artifacts are unchanged.

Prepared for Arham Tahir with substantial OpenAI Codex assistance in reasoning,
implementation, verification and writing. No subagents, independent human review
or literature-priority guarantee. Apache-2.0. The new result is the source-bound
fixed-flag obstruction and reusable support test; graph reachability itself is
standard mathematics.

[2981]: https://github.com/CrocSwap/integer-mult-bounds/blob/3d24b92d8ba057b57cb2d480170ec407520e6882/research/p104-joint-unit-flags/README.md
[claim]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18977808
