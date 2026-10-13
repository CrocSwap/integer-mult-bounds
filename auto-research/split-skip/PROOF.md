# Split-pair skip-prefix networks with paid clones

The exact finite witness supports the conditional bound

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=\frac{4598878089}{10^{14}}=0.00004598878089>2^{-15}.
\]

This improves PR #54's claimed saving `4529040672/10^14` by approximately
**1.5419914%**, and PR #53's by **2.2394590%**. These compare asymptotic
exponent savings, not measured multiplication speed. The next dyadic saving
`2^-14` is not reached. The PR #54 comparison is pinned at
`7210de7d0f9ccaeb64c3f60f188419e02be08d95`; this branch starts from PR #53 at
`3ffd4021995c959ac02d12920e0279ae97dd03c7`.

By submission time, PR #58 at `bc2f7ed4c20dc18898305ab17165c0c995cbb804`
claimed the stronger saving `4.75073569e-5` using a joint frame compiler.
This contribution is a separate grouping/order improvement over the pinned
PR #54 construction. It does not claim the strongest current exponent.

## Construction

The ambient dimensions remain `(23,25)`, both local bases remain `I+J`, and
the copied centers, paid endpoint corrections, reversed data corners and
complex network are inherited unchanged. The new search changes recursive
partitions, summand orders and selected legal carrier uses. It then composes
PR #54's paid whole-chain clones with that changed graph.

At selected levels, replace one ordinary two-point group by two singleton
groups. For dimension 23, the split choices by recursion depth are first,
last, middle. For dimension 25 they are first, middle, middle. Other groups
remain ordinary consecutive pairs. This creates additional coarse work but
removes the nonzero strip work for the singleton groups. Crucially, physical
role count, rather than number of scalar additions, governs the bound.

The pinned total and strip permutations in `config-23.json` and
`config-25.json` further improve legal reuse. Numerical search is merely a
way to choose these finite inputs. The reconstruction verifies each input
exactly; neither optimality of the matching nor global search optimality is
claimed. The exact recurrence objective was also used after role-count search.

Finally, 186 and 165 paid clones recompute existing sums from disjoint
operands with unchanged original envelopes and replace whole continuation
chains. Every added gate and resulting role is included in the reconstructed
DAG and complete cost profile. This is PR #54's mechanism, not a new free
copying rule.

| Construction | h23 additions | h23 roles | h25 additions | h25 roles | W |
|---|---:|---:|---:|---:|---:|
| PR #53 | 40,329 | 32,946 | 53,475 | 43,409 | 160,799,739 |
| PR #54 | 40,582 | 32,693 | 53,828 | 43,056 | 159,592,676 |
| New grouping and orders, before clones | 40,915 | 32,283 | 54,193 | 42,421 | 157,525,091 |
| New grouping and orders, with paid clones | 41,101 | 32,097 | 54,358 | 42,256 | 156,805,076 |

The final matched carrier counts are 14,340 and 19,027. The output-use counts
are 5,336 and 6,925. Both satisfy `R = additions + output uses - matches`.

## Why singleton groups preserve the scalar identity

For a set of vertices S, define F(S) as the sum of its vertex weights plus
all edge weights with both endpoints in S. Partition the vertices into
nonempty groups of size one or two. A coarse vertex carries the original
vertex weights in its group and its internal edge, if any. A coarse edge
carries every edge between the corresponding groups. These quantities
partition the terms of F without cancellation or overlap.

The recursive coarse circuit therefore supplies
`outside[i] = F(V minus G_i)` and
`far[i,j] = F(V minus (G_i union G_j))`.
For a removed vertex a in G_i, its strip for excluded group j contains the
weights of `G_i minus {a}` and edges from those remaining vertices to groups
other than i and j. There is no omitted internal edge, since at most one
vertex remains in G_i.

For vertices a and b in distinct groups, the desired leave-two-out sum is
the disjoint sum of `far[i,j]`, the two appropriate strips and the edges
between `G_i minus {a}` and `G_j minus {b}`. For two vertices in the same
group, the group has exactly two elements and deleting them leaves precisely
`outside[i]`. The analogous one-vertex formula is `outside[i] + sums[a]`.
Singleton groups make the associated strip and cross terms zero, so the
same code and identities apply.

At every nonbase level the selected partitions retain an unsplit pair, hence
the number of groups is strictly smaller than the number of points. The
recursion terminates. All group sizes and contraction are checked explicitly.
Changing summand order preserves disjoint supports. Exact reconstruction
checks the complete global triple-source coefficient vector of every output,
not random numerical samples.

## Paid clones and physical realization

The unchanged PR #54 replay checks every pinned clone against its actual
parent graph and matching: disjoint exact source partition, identical
core/cover envelope, two distinct unused provider capacities, causal
placement, and replacement of one complete continuation chain. Source and
output graph hashes must agree. The reconstructed graph includes all newly
added gates and is checked again from its exact global source supports.

The generic cancellation-free graph construction does not require different
nodes to have different supports. Every clone remains in the same common-point
positive envelope. The final graph therefore enters the same original-envelope
compiler as any other legal addition DAG. The final carrier matching is
replayed independently for actual operand use, envelope inclusion, causal
order and donor/use uniqueness. The complete physical timeline and every
dirty-scratch basis direction are checked in both orientations. No scalar
identity or equal-value observation is used to identify storage slots for free.

## Complete finite accounting

The selected networks have

- `m = 575`, `N = 4,073,300`, `W = 156,805,076`;
- weighted local loss `L = 2,226,400`;
- total child rank `W*m - N + L = 90,161,071,800`;
- unchanged deficit `N-L = 1,846,900`, maximum child width 529.

For every data pair the contiguous data profile is nine singletons plus
blocks 21, 17 and 481. Every one of the N endpoint-copy corrections remains.
The full fixed local profiles retain the paid copied-center transforms;
only the h full center cleanup calls on each axis are replaced by h rank-one
complements. The same deterministic prime and minor bounds apply because
all frames retain the original core/cover family in dimensions 23 and 25.

All 4,073,300 data pairs are accounted for. The ten failures of the primary
modular nonvanishing test are recovered by exact rational elimination;
they are not discarded. The unchanged complex graph retains its scalar
charge in the semantic error constant and its saving `717/10^7`.

## Exact recurrence and assembly

Let n_t be the complete child multiplicity at width t. The exact bit saving is

\[
a_b=\frac{4599089596}{10^{14}}=0.00004599089596.
\]

`witness.py` proves
`sum_t n_t (t/m)^(1-a_b) / W < 1`
with rational logarithm and exponential enclosures. A rigorous lower bound
excludes `a_b + 10^-14` for this same finite profile. The complete PR #53 and
PR #54 child lists fail at the new saving; comparisons use their own widths.

The inherited balanced assembly checks all 47 strict constraints, all seven
final margins, product row stock, semantic constants and eventual arithmetic
cutoffs. The displayed kappa lies strictly below the controlling margin;
its next `10^-14` grid point is excluded. These are scoped grid exclusions,
not optimality claims over other networks.

`independent_arithmetic.py` imports no candidate checker. It reconstructs
the child list from the two raw role/profile records, uses a separate
80-term atanh logarithm enclosure and degree-nine exponential enclosure,
and recomputes all seven final margins. Its moment gap exceeds `1.15e-15`
and its final absorption gap exceeds `4.62e-15`.

## Reproduction and review boundary

Run from the repository root with Python 3.11+ and a C++17 compiler:

```
python3 research/split-skip/producer.py --work-dir build/split-skip --output build/split-skip-receipt.json
python3 research/split-skip/witness.py
python3 research/split-skip/independent_arithmetic.py
python3 -m unittest discover -s tests -p 'test_split_skip.py' -v
```

The producer command performs the full physical reconstruction; arithmetic
checks alone do not replace it. SciPy was used for discovery and is not
needed to check the pinned witness. `SOURCE.json` pins the new finite inputs
and inherited verification sources; `producer-receipt.json` and
`validation.json` record completed checks.

The original OpenAI multiplication framework, generic residual compiler,
fixed finite-alphabet multitape recursion, analytic recovery, semantic
precision, routing, bulk resampling, eligible prime/setup conditions and
eventual thresholds remain inherited proof dependencies. This continuation is outside the maintainer's published release reviews. This continuation adds
finite evidence and a written conditional argument, not a full formal proof,
independent human peer review or an unconditional multiplication theorem.

## Attribution

New here: the singleton/pair partition search, its application to the
skip-prefix producer, summand-order and finite-moment refinements, and the
verified composition with paid clones. Prepared with substantial OpenAI
Codex assistance at the user's request.

Avi Eisenberg / ikeboy with Anthropic Claude assistance supplied PR #53's
skip-prefix strips. Chafik Boukhalfa with OpenAI Codex assistance supplied
PR #43/#46/#48 and PR #54's original-envelope paid-clone specialization.
RaD / hipotures supplied the source-partition/whole-chain cloning idea in
PR #51, alternating producer work and analytic/routing contributions.
Rohan Arun supplied PR #44's weighted-matching work, with its stated
Anthropic Claude assistance, and earlier reversed/fixed geometry work.

Retain all earlier credits: icekylinx's paired producers, batching and copied
centers; Dominik Scholz's fixed bases and dimensions; James Chang's reversed
geometry; Zhihao Chen's ternary and two-stage/interface contributions; Aurel
Prosz / Paureel, Swapnil Jain, eumemic, Bortlesboat, dleen, Douglas Colkitt,
OpenAI, David Harvey and Joris van der Hoeven, and all retained source notices.
Apache-2.0 and predecessor-specific licenses remain in force.
