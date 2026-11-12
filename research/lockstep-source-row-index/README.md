# Index every replicated compiler source row using polynomially many chronological states

**Scoped constructive compiler result; no new kappa.** Every fresh source
of a separated finite mixed-target flow now has an exact contiguous row
index, with an inverse that recovers its occurrence. Counting shares only
subtree statistics; distinct chronological occurrences and physical rows
retain their identities.

The [preceding occurrence codec](https://github.com/CubeJerry/integer-mult-bounds/tree/91246e5131152ccb1f64a969c36706360861f821/research/pascal-occurrence-codec)
resolved a productive field to a symbolic source or owned-bank name. Its
first open question was to rank fresh source names into physical row intervals.
This package closes that logical indexing question and connects its source
names to integers `0,...,a*S_N-1` for the actual replication count a. Owned
banks are excluded from productive row credit.

## Exact theorem

Let G be the finite flow height, d the number of distinct target ranks,
and q the number of distinct paid ranks. A class's source-subtree count
depends only on depth, paid-rank product and the **last paid rank**. The
number of such states is at most

`R=1+q*binom(G+q-1,q)`.

The required target multiindices number `M=binom(G+d,d)`. Both are
polynomial in G for fixed finite rank alphabets. The algorithm enumerates
neither every paid path nor all unit occurrences of a multiindex. Its
rank/unrank query follows one chronological path and skips whole intervals.

[PROOF.md](PROOF.md) gives the exact source-count recurrence, inverse proof,
bit sizes, deterministic sorted-table setup/query costs, and a separately
charged conservative serialized-table simulation. The declared
source order is depth-first class preorder, lexicographic unit multiindex,
unit ordinal and native role order. This canonical numbering can differ
from the literal audit's incidental numeric IDs; it leaves job chronology
and owner identity unchanged.

Two details are essential:

* Equal paid ranks may share cached counts, but their actual occurrence
  multiplicities and positions remain in every source interval.
* The last rank cannot be dropped from the state: at one exact fixture,
  equal depth and dilation have local source counts 1 and 0 depending on
  that last rank.

## Evidence and reproduction

After placing this directory at `research/lockstep-source-row-index/`, run:

```sh
python3 -I -W error -B research/lockstep-source-row-index/verify.py
python3 -I -W error -O -B research/lockstep-source-row-index/verify.py
```

Both standard-library Python 3.12 commands print
`PASS_CONTIGUOUS_SOURCE_INDEX`; the local outputs agree exactly.

The literal predecessor oracle supplies 102 complete small flows, with
555 classes, 1,005 native units and 1,431 fresh sources. Every fresh source
is checked against its exact sorted literal rank and inverse, including
replica 0 and replica 2 in a three-replica row interval. Fourteen controls reject
lost paid multiplicities, out-of-range indices, a wrong namespace, owned
bank credit, a matched role masquerading as a source, omitted last-rank
state, invalid occurrence ordinals and physical merging of equal-statistic
sibling classes, as well as absent, unordered, duplicate and uninitialized
state-table entries.

A separate height-64 fixture indexes

`20,857,390,061,882,631,902,013,162,838,873,341,952` source rows

using **4,161** states and **2,145** target multiindices. Its complete class
tree has more than `5*10^30` classes and is not enumerated. Five interval
positions round-trip. A different counting method independently corroborates
every one of those 4,161 state totals: it counts ordered target words by their
product, then obtains fresh inputs by subtracting incoming parent-unit counts.
This alternative uses the same inherited flow theorem, rather than an
independent proof kernel.

An independent peer review found that the original hash-based state tables
did not support their advertised worst-case work bound. The repaired
algorithm uses sorted/deduplicated level lists, one shared sorted key vector
and binary-search count tables; target profiles use a list. The verifier
includes a fixed rule with paid ranks proportional to Python's integer hash
modulus: at height 8 its **3,961** states collide within every depth, yet all
counts and its source-row inverse pass. The proof retains the explicit
counterexample and correction rather than treating hash behavior as an
average-case premise.

The retained literal oracle and the preceding codec are copied byte-for-byte
under `inputs/` and authenticated before use. Their source commits, Git blobs
and SHA256 values are in [SOURCES.json](SOURCES.json). An explicit adapter
sets the literal oracle's ambient cap; its matching and source computation
remain unchanged. Verification is source-aware, not a blind experiment.

## Significance and limits

The result supplies concrete integers for the productive source inputs of
the finite compiler, which previously had only symbolic occurrence names.
For fixed native rank alphabets, the metadata construction has polynomial
arithmetic/comparison work in the flow height and input bit sizes. A separate
serialized-table construction also has an explicit conservative polynomial
fixed-tape bound, including metadata scans and head return. This does not imply a
practical construction at the selected astronomical compiler parameters.

The selected conditional value remains **0.00363005817**, and all five
selected assumptions remain. A row integer does not provide constant-time
payload access. The full selected product/paid-owner manifest, grouped source
complements, smaller-rank substitutions, owned-bank allocation and all actual
native, precision and fixed-tape costs remain separate obligations. No
complete multiplier, new supplier, human review or formal-kernel acceptance
is claimed.

This is a source-indexing successor to the published codec, with independent
base `e54523517d0f03e58352e647c403a5af3e525a57`. The source proof/code,
#4691 live-role executor, and #6878 occurrence-layout work were checked for
overlap. Targeted all-state PR searches for source rank/unrank/compiler,
source indexing and subtree/Pascal did not locate this construction; those
bounded searches do not establish universal priority.

## Open next questions

1. **Integrate source rank groups with complement batches.** Supply exact
   index/rank maps for one source-rank bucket and its complementary program.
   The present numbering covers all sources in chronological order; it does
   not execute grouping or the associated physical permutation.
2. **Bind the real selected product manifest.** Emit the actual role and
   paid-owner lists for a smaller complete product, then use both codecs on
   that source. The final 1920-fold template is still unmaterialized.
3. **Price one actual row dispatcher.** Lower the integer indices to a
   declared tape representation and account for access, head return,
   preservation, copies and erasure. Offline indexing supplies no zero-cost
   field lookup or native endpoint.

## Credit

Prepared for **Jerry Chen / @CubeJerry**, with substantial OpenAI assistance.
The preceding codec and its root's separate AI review retain their exact
publication and evidence. Jacob Alan Sussman supplies the integer Pascal/
lockstep flow; zxv supplies the finite compiler and literal audit; Mark /
Matarener supplies the live-role executor; @CubeJerry and retained geometry
contributors supply #6878's occurrence routes. The reused files retain their
original headers. Apache-2.0; see [NOTICE.md](NOTICE.md).

## Separate independent reviews

[REVIEW.md](REVIEW.md) preserves the initial collision finding and its repaired disposition. A different worker reviewed metadata access and serialized-tape costs in [COST-MODEL-REVIEW.md](COST-MODEL-REVIEW.md). Run `python3 -I -W error -B independent_check.py .` from this directory for the separate ordered-word oracle: 16 cases, 314 sources, all 1,570 replicated rows and four collision-family controls. Its final receipt is [INDEPENDENT-RESULT.json](INDEPENDENT-RESULT.json).
