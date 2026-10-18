# R420 compensation with disjoint target pairs

**Finite circuit improvement; no new kappa.** On eumemic's PR543 R420 word,
60 disjoint target pairs reduce the frame-zero D compensation from **19,922
to 16,672 binary XOR additions**. The complete local word drops from **26,916
to 23,666 additions**, a saving of 3,250, including preparation and restoration.
Every source and helper keeps its original value at the D boundary.

A small vertex-price certificate proves that **3,250 is optimal within this
disjoint target-pair substitution class**. This adds 100 saved additions beyond
concurrent [PR713](https://github.com/CrocSwap/integer-mult-bounds/pull/713),
which independently found a 3,150-addition saving. Neither result is a new
supplier exponent or a claim about arbitrary compensation circuits.

The complete physical frame paths, 420 helpers, nine retained copies and paid
rank mass 5,112 are unchanged. The reverse positive-prefix bound grows, so this
is not a free substitution into a previously certified hosted invoice.

| Local quantity | PR543 source | Target-pair word |
| --- | ---: | ---: |
| D binary additions | 19,922 | 16,672 |
| All binary additions | 26,916 | 23,666 |
| Forward positive-prefix bound | 144,651 | 144,651 |
| Reverse positive-prefix bound | 2,270,064 | 3,703,810 |
| Local native payload bits | 100 | 102 |
| Paid rank mass | 5,112 | 5,112 |

The local native payload expression is `64 F^3 B^2`. For the changed word it is
`2657306775507971405724759110400 < 2^104`. This is the inherited local payload
test used by the native cohort checker, not a new proof of global hosted
prefix bounds at nine or eleven stages.

## Reproduce

From the repository root, with Python 3.11 or later and its standard library:

```sh
python3 -B research/r420-target-pairs/verify.py
```

Expected output:

```text
PASS_R420_TARGET_PAIRS D=19922->16672 ADDs=26916->23666 saved=3250 columns=660 rank_mass=5112
```

`--report` prints the exact receipt, which must match `certificate.json`.
The recipe and pinned source reconstruct the entire changed word in memory;
its canonical JSON SHA-256 is
`814b845afa056f6bce4e566e87494d591c6776092772748b509aead2959e0bff`.
No generated word or changes to predecessor files are needed.

To also run the unchanged native exporter, legality checker and five-, nine-
and eleven-stage formal-column checkers, provide a C++17 compiler and Boost
headers. These are the predecessor checkers' existing dependencies.

```sh
BOOST_INCLUDE=/path/containing/boost python3 -B research/r420-target-pairs/verify.py --native
```

`CXX` selects the compiler. With system Boost headers, omit `BOOST_INCLUDE`.
Native checks cover 900, 1,380 and 1,620 formal columns, respectively, and 6,
18 and 24 omitted-bridge rejection controls. Two additional corruptions,
missing target restoration and an incorrect helper read, pass frame legality
but fail the formal-column checker at all three stage counts. The native
receipt also compares exact prefix bounds from an independent binary-record
parser against each C++ result. Temporary streams are removed after the run.

## The identity and its complete local cost

Let `K_a` and `K_b` be sets of helper indices in two original D rows. Addition
is over F2. The target inputs `u,v` and all helper contents `s` are arbitrary.
Write `A = K_a s`, `B = K_b s`. Replace the two direct helper sums by

```text
y_a += y_b
y_b += K_b s
y_a += (K_a symmetric_difference K_b) s
y_a += y_b
```

The successive target states are

```text
(u,v) -> (u+v,v) -> (u+v,v+B) -> (u+v+A+B,v+B) -> (u+A,v+B).
```

Thus the endpoint is exactly the original two-row operator. Helpers are only
read and never modified. There is no clean-register assumption. All operands
start and remain at frame zero throughout D, so there are no additional frame
changes, copies, source accesses or recursive children. Both target-to-target
additions are charged. The cost is `|K_b| + |K_a symmetric_difference K_b| + 2`,
instead of `|K_a| + |K_b|`. Disjoint target pairs cannot interfere. The final
recipe pairs all 120 targets.

The changed D has more multi-input rows, 240 instead of 120. Counts in this
note are binary additions, after expanding every source operand. Neither a
multi-input row nor a restored target mixing operation is charged for free.

## Explicit interface extension

The original PR543 checker rejects the changed word at
`H2_D_frame0_targets_from_helpers` and `K_equals_D`. H2 forbids target sources
in D, and the literal K extractor assumes each D source is a helper input.
`verify.py` requires these two rejections to occur. It does not patch the
predecessor or report that its original H1–H5 contract accepts the new D.

Replace only that syntactic D condition and literal extraction with the
following semantic condition, H2'. D executes first; every operand is a target
or helper at frame zero; D writes only targets; and its complete operator is
`(x,s,y) -> (x,s,y+Ks)`, with exactly the K of the original D. The independent
set-valued replay checks this on all 660 input columns. In particular, its
target-to-target endpoint block is the identity. H1's prohibition on target
feedback into sources or helpers is retained, even for F2-neutral feedback.

The original raw word `W0 = A, scatter, B` and cleanup C are unchanged.
The pinned source audit proves their finite decomposition as
`(z,y) -> (Uz,y+Jx+Ks)`, with `J=I`, and C restores z. Substituting a D with
the same complete operator therefore leaves the complete scalar map
`(x,s,y) -> (x,s,y+x)` unchanged. The existing exact frame/scalar replay also
checks the changed word directly on all 660 columns. Its remaining interface
hypotheses and conclusions pass. Every frame path is compared exactly, and
the retained-copy frames are checked at the actual scatter boundary.

This is a finite endpoint substitution and a written algebraic argument. It
does not formalize the all-size multiplication theorem or establish that a
downstream tool accepts H2'.

## Exact optimum in the disjoint-pair class

The domain consists of arbitrary disjoint target pairs, either orientation
for each pair, and unchanged D rows for any unpaired targets. Each pair uses
exactly the four-operation identity above with both mixing operations paid.
For distinct targets i,j, let

```text
w_ij = max(0, max(|K_i|, |K_j|) - |K_i symmetric_difference K_j| - 2).
```

This is the best nonnegative saving from that pair. In `matching-dual.json`,
`twice_vertex_prices` gives 120 integers q_i in target order 120 through 239.
The independent, integer-only checker verifies

```text
q_i >= 0                         for all 120 targets
q_i + q_j >= 2*w_ij              for all 7,140 unordered pairs
sum_i q_i = 6,500.
```

For any disjoint matching M, summing its edge inequalities gives
`2*sum_M w_ij <= sum_used q_i <= sum_all q_i = 6,500`. Thus no matching in
this class saves more than 3,250 additions. The 60-pair recipe has actual
oriented saving exactly 3,250, so it attains the upper bound. This proves the
restricted optimum without trusting a matching solver. It makes no claim
about larger target blocks, overlapping transformations or helper factoring.

The OS assignment seed was **13**. All `120 × 119 = 14,280` orientations were
scored; 4,544 had positive complete local savings. The original single seed-13
greedy pass saved 3,150. Concurrent PR713 reported that same saving before
submission, so one bounded pivot replaced greedy selection by a maximum-weight
matching nomination on the 3,280 positive undirected edges. NetworkX 3.5,
with seed-13 shuffled edge insertion, nominated the final matching. A separate
integer Hungarian assignment calculation produced the vertex prices and an
attaining matching independently. Neither solver is imported or required by
the shipped verifier. The exact frozen witness and feasible prices, rather
than a solver's success message, establish the result. The stopping rule was
one matching solve followed by the independent matching-bound certificate;
there was no search beyond this class.

## Controls

Nine negative controls reject removed initial mixing, removed final recovery,
a missing helper term, a nonzero D frame, target feedback into a helper,
F2-neutral feedback into a helper, source access at frame zero, an edit outside
D, and overlapping pairs. Every mutation must change the object and fail for
the expected reason. A positive F2-neutral target-pair control passes the
operator check but must pay two additional additions. A tenth negative
control lowers one vertex price and must fail an edge inequality. These are finite tests,
not impossibility proofs or a formal proof of the full theorem.

## Pins, predecessor credit and remaining work

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The selected certificate at that base identifies **#626 with #543**, with
conditional `kappa = 51110230636731/31250000000000000`, approximately
`0.001635527380375392`. See the
[selected review](../../docs/research/community-k492-review.md).
Historical numbers in the R420 README are not the current selected result.

The input is eumemic's [PR543](https://github.com/CrocSwap/integer-mult-bounds/pull/543),
source commit `2065fe4f72a914d907f1046603f5a36f17018535`. The two source pins in
`certificate.json` cover the decompressed word payload and the exact checker
bytes. `native.py` pins the six exporter, checker and header files it executes
from PR493's package. Gzip container bytes are deliberately not the identity.
PR493, #425 and the retained common-label interface supply the inherited
mutable-source and cleanup construction.

Dugongue's [PR476](https://github.com/CrocSwap/integer-mult-bounds/pull/476),
head `e850569c33ad1d5771e2f8b1c6dfe7a445396167` at inspection, uses this reversible
target-factoring identity in phase B. DreamingOfClouds' PR450 is earlier
target-mixing precedent. This note claims neither invention of the identity
nor those submissions' bounds.

Concurrent [PR686](https://github.com/CrocSwap/integer-mult-bounds/pull/686) and
[PR694](https://github.com/CrocSwap/integer-mult-bounds/pull/694) factor helper
columns in D and motivate a semantic D contract. Their inspected heads were
`23dcb610c2b156b76b9d599ea296c3cbde224b2d` and
`9732ac127dd4bef98a846aaa904c20b5a84e72c1`. This package instead factors target
rows, has no helper writes, imports no code from those pending PRs, and does
not combine their circuits. PR670/674/688 optimize phase-B blocks, and PR691
optimizes a phase-A quad. Those are separate scopes.

The pre-submission overlap refresh covered 534 open PRs. PR708 shares
phase-A decoder operands, while PR707/709 improve verification tooling. None
of those changes these target rows. Scott Woolsey Biggart's PR713 appeared
in the final refresh at head `1a19af5c5ddb6de9797a6d085e5df0b90ed6d58b` and
independently constructed 57 target pairs with saving 3,150. The original
version of this package corroborated that value. This final version adds the
60-pair circuit and a solver-independent 3,250 upper bound for the full
disjoint-pair class. It claims no priority for target-row factoring. No pinned
coordination issue existed, so [the sprint claim](CLAIM.md) is local.

The recursive profile is unchanged. No larger supplier exponent or kappa is
claimed. Hosted-parent regeneration, whole-owner accounting, finite invoices,
outer assembly and acceptance of H2' remain work for a future integration.
All-size compilation, common-label/mutable-basis realization, whole-call
hosting, normalized residual, precision/tape, exact recovery and analytic
transfer remain inherited assumptions. Local native payload checks do not
discharge them. No practical runtime speedup is claimed.

## Validation record

Local replay on 2026-10-13 used Python 3.14.8, macOS 26.5.2 arm64, Apple Clang
21.0.0 and Boost 1.92.0 headers. The standard-library verifier passed normally
and with `python3 -I -O -B`. The final native run also used `-I -O -B`; all
five-, nine- and eleven-stage checks and the two corruption controls passed.
Native records fall from 29,874 to 26,624, while 2,940 nested MOVEs, nine
COPY/ERASE pairs and the paid histogram remain unchanged.

Gzip recompression with a different timestamp passed the payload pin; changed
decompressed source bytes were rejected. An independent audit reconstructed
the frozen D map without importing this verifier and separately recovered all
672 frame dimensions and the paid histogram. `make selected-record-check`
passed. No selected-frontier, predecessor or upstream file is edited.

The repository-wide `make verify` target and selected cold supplier replay
were not run: this additive package changes neither selected supplier and
does not regenerate global artifacts. Linux execution, hosted-parent
reconstruction and outer assembly remain unchecked here. Native compiler and
Boost versions are environmental dependencies, not new repository dependencies.

Contributor: Sagar Thakrar, with substantial OpenAI Codex assistance in the
search, implementation, written argument and review. Independent delegated
checks corroborated the endpoint and paid profile. New material is Apache-2.0;
predecessor sources, notices and `upstream/` are unchanged.
