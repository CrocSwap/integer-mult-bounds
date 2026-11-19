# Joint denominator-13 decisions use fewer expected fair bits

For every fixed pair of nonzero residue probabilities $a/13,b/13$, an explicit
finite-state sampler produces **two independent** Bernoulli decisions with
optimal expected fair-bit count strictly below $7/2$. Two separate exact
standalone samplers require expected count at least four. When both probabilities
are $1/13$, the joint expected count is below $9/4$, saving more than 43.75% of
the standalone expected draws.

Each parameter pair has exactly 312 internal control states and 624 binary
transitions. Including its four output labels, every target fits nine bits;
a packed transition table uses 5,616 bits, or 702 bytes, per parameter pair.
The implementation generates one table at a time rather than storing all 144.

This is a finite exact sampling construction and an expected-bit optimum,
not a physical inverse, worst-case latency bound, reversible cleanup protocol,
supplier or new κ. It deliberately changes the **standalone-call** hypothesis
of [PR #6068](https://github.com/CrocSwap/integer-mult-bounds/pull/6068).
The underlying dyadic decision-graph method is classical; the contribution is
this small complete denominator-13 catalogue, exact means and resource ledger.

## Contract and source relevance

The denominator-13 inverse in
[PR #5069](https://github.com/CrocSwap/integer-mult-bounds/pull/5069) motivates
rounding probabilities with this denominator. Both probabilities must be known
**before** this sampler consumes any bits. Their intended decisions are
independent. A second probability that depends on the first rounded result
cannot be substituted into this batch without a new contract.

No actual native caller is asserted to provide the required residue pair or
batching window. The retained deterministic inverse is not alleged defective.
The stochastic prefix of
[Nick Petalas](https://github.com/petalas)'s
[PR #6026](https://github.com/CrocSwap/integer-mult-bounds/pull/6026) supplies a
related arithmetic context, but its adaptive updates are not automatically
batchable, and its native/caller error analysis is not extended here.

## Exact joint decision graph

In output order 00, 01, 10, 11, set the integer weights

$$
(w_0,w_1,w_2,w_3)
=((13-a)(13-b),(13-a)b,a(13-b),ab).
$$

Their sum is 169. Dividing by 169 gives exactly the product law, hence the
required independent marginals. Write the binary digits of each probability
as $d_{i,k}$ at depth $k\geq1$. Define

$$
n_k=2^k-\sum_{i=0}^3\lfloor2^k w_i/169\rfloor.
$$

This is the number of unfinished binary prefixes after depth $k$. At the root,
$n_0=1$. At the next depth, double every unfinished node, label the first
$d_{i,k}$ available children with output $i$, and retain the rest as unfinished.
Each digit is zero or one, and

$$
n_k=2n_{k-1}-\sum_i d_{i,k}.
$$

Thus this rule never overfills a level. An executable version stores the
unfinished-node index $j$: after drawing one bit $u$, set $j\leftarrow2j+u$,
then subtract the four probability digits in output order. The first subtraction
making $j$ negative returns that output; otherwise the remaining $j$ is the
next unfinished-node index. All four digits come from exact residue doubling
modulo 169.

By induction, the completed output-$i$ prefixes at depth $k$ number exactly
$\lfloor2^k w_i/169\rfloor$. Since $1\leq n_k\leq3$, unfinished probability
is at most $3/2^k$, tending to zero. The resulting output law is therefore
exactly $w_i/169$, not an approximation from finite samples.

## Finite periodic controller and exact expected cost

The order of two modulo 169 is 156; replay checks this with exact integer
powers. Every weight is coprime to 13, so its residue sequence is periodic
with that period. The digits and unfinished-node counts repeat. There are
exactly 312 internal phase/node pairs for every one of the 144 residue pairs;
this finite count is checked exhaustively. Two transitions per state give the
624-entry table. No growing arithmetic precision is needed to represent the
sampler's logical control state, although its random tape and stopping length
have no finite worst-case bound.

The exact expected draw count is

$$
E[T]=\frac{\sum_{k=0}^{155} n_k2^{-k}}{1-2^{-156}}.
$$

For $(a,b)=(1,1)$ this is

$$
E[T]=\frac{9960277917013927549978}{4649714690825496825793}<\frac94.
$$

The exact finite catalogue certifies $2<E[T]<7/2$ for all 144 nonzero residue
pairs. These numerical bounds and state counts are finite certificates; the
construction, law and expected-cost formula have the preceding written proof.
No floating-point logarithms or Monte Carlo estimates are used.

## Optimality and the changed standalone hypothesis

For any exact fair-bit decision tree with these four output probabilities,
completed output-$i$ mass after $k$ bits is an integer multiple of $2^{-k}$
and cannot exceed $w_i/169$. Its completed prefix count is therefore at most
$\lfloor2^k w_i/169\rfloor$. Its unfinished probability is at least $n_k/2^k$.
Summing these tail bounds proves that its expected draw count is at least the
displayed formula. This sampler saturates every depth bound, so it is optimal
for the stated fixed joint law, with no free initial random state.

A standalone non-dyadic Bernoulli sampler must leave at least one fair prefix
unfinished at every depth, giving expectation at least two. Separate calls
without a shared entropy reservoir therefore require at least four draws in
expectation. The joint four-outcome tree changes that boundary; it preserves
independence of the **decisions**, without requiring separately executed
sampling trees. Reusing a single sampled flag for both decisions would have
the right marginals but the wrong joint law and is rejected by a control.

The sampler still has a positive unfinished probability at every finite depth.
It chooses the unbounded-stopping option in #6068's tradeoff, not an escape
from that worst-case theorem. A finite control table is not a finite draw cap.

## Costs and unproved physical obligations

The logical sampler performs one table transition per consumed fair bit, then
returns one two-bit outcome. Per-configuration packed table storage is 702
bytes and control needs nine bits including output labels. Selecting or building
the table from actual data residues, table access, random-bit movement, output
storage, stopping-record retention and reversible cleanup are additional costs.
The returned decisions are correlated with the consumed tape, so that tape is
not automatically a fresh reusable random resource.

No source-bound physical batching window, all-column primitive, deterministic
tariff, compiler or outer error budget is supplied. The expected bit reduction
must not be read as a runtime speedup or an admitted exponent improvement.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/paired-residue-sampler
python3.12 -B scripts/check_research_commit.py --package research/paired-residue-sampler
```

The standard-library verifier constructs every table, checks the complete
outcome-prefix counts for two full 156-step periods, independently enumerates
36,864 literal eight-bit tapes, certifies the exact expected counts and resource
bounds, and rejects corrupted output labels and false independence/latency
claims. Normal and optimized modes write no package files. Universal probability
and optimality come from the written depth-count argument, not the literal tapes.

Canonical main was refreshed on 2026-10-28 UTC at
721c03822c421b7f7fcbb2598993b947c4d88419, priority 8. The navigation-only repair
from [PR #6050](https://github.com/CrocSwap/integer-mult-bounds/pull/6050) is
included. The optional full-history check is unavailable in this shallow checkout;
source pins use its reachable base. No selected/native cold replay, independent
human review or formal-kernel acceptance is claimed. Frozen sources stay unchanged.

## Significance for researchers

The standalone two-draw lower bound is not a per-scalar amortized limit. A small
joint interface can reduce expected randomness while preserving the exact
independent rounding law. This supplies a concrete batching target and exposes
the next obligation: an actual nonadaptive residue pair and a full hosting and
cleanup bill, rather than free entropy or a claimed bounded-time sampler.

## Open next questions

Does one actual inverse-service stage expose two residue probabilities before
either output is consumed? First bind that data-dependence and timing boundary,
then price table selection, access and random-tape cleanup. No such caller is
instantiated here.

Can the table be shared or parameterized across residue pairs with less total
physical control cost? Start with two configurations and an explicit dispatcher
that preserves the joint law. A lower expected bit count alone does not fund it.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
The dyadic distribution-generation tree and depth-count optimality argument are
classical and not claimed as new. [JoyboyBrian](https://github.com/JoyboyBrian)'s
#5069/#5037 lineage supplies the inverse context;
[Nick Petalas](https://github.com/petalas)'s #6026 supplies the stochastic-prefix
context. Their sources and attribution remain unchanged. Apache-2.0.
