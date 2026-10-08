# RaD producers with fixed bases and copied reversed corners

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{4099494519}{10^{14}}=4.099494519\times10^{-5}>2^{-15}.$$

This composes **RaD / hipotures's alternating producers from
[PR #41](https://github.com/CrocSwap/integer-mult-bounds/pull/41)** with the
explicit fixed bases and copied reversed corners from
[PR #40](https://github.com/CrocSwap/integer-mult-bounds/pull/40).
It improves the conditional exponent saving by **1.6193275%** over PR #41's
stronger alternating candidate, `4.034168124e-5`. This is a comparison of
conditional asymptotic bounds, not measured multiplication speed.

The changed producer graphs and point order are RaD's work. This contribution
recomputes their complete original-envelope local profiles in both fixed
bases, verifies the actual carrier schedules independently, and proves the
composition with our existing common-basis geometry. RaD also reports separate
fixed-basis investigations; no priority or global optimality claim is made.

## Why the composition works

Both bases are `I+J`, with ordered dimensions `(23,25)`. The changed addition
trees retain exactly the same triple inputs and terminal centers. Consequently
the actual data matrices and controlled coordinate orders are unchanged, so
PR #40's complete certificate for **4,073,300 source pairs** and
**191,445,100 nonzero prefixes** applies. The data profile remains
`9 singletons + [21,17,481]`. The [general proof](proof.txt) explains the
unchanged geometry and the transfer of arbitrary local matrices by nonzero
diagonal row and column scalings.

The local matrices do change with the producer. We therefore regenerate the
actual original-envelope carrier assignment and compute its **entire** local
profile at five certified primes. There are **68,186** profiled matrices at
h23 and **91,732** at h25, with no prime disagreements. The inherited exact
rank-four minor bound certifies rational zero ranks; agreement of a few primes
alone would not suffice. Fresh label checks establish that the new additions
have the core sizes and denominators required by that bound.

The independent schedule checks verify actual event-slot paths, protected
outputs, all source coefficients and retained centers. Complete dirty-basis controls at both actual dimensions supplement the
general reversible schedule argument. See the
[review evidence](review/). These original envelopes differ from the positive
label frames also supplied by PR #41; equal role totals do not permit their
histograms to be interchanged.

Exactly h full-width identity cleanup calls become h rank-one complements in
each copied profile. Every rank-(h-1) copied transform remains paid. Both full
local contributions replace their generic counterparts once. No auxiliary
block or copy saving is counted twice.

## Complete costs and exact arithmetic

| Quantity | Value |
|---|---:|
| Original carrier roles, h23 / h25 | 36,685 / 48,479 |
| Matched event slots, h23 / h25 | 5,749 / 7,565 |
| Data banks N | 4,073,300 |
| Ambient dimension m | 575 |
| Width W | 178,378,409 |
| Copied loss L | 2,226,400 |
| Total rank Wm-N+L | 102,565,738,275 |
| Distinct child widths / maximum child | 26 / 529 |

All N endpoint corrections remain paid. The bit saving is
`819932517/20000000000000 = 4.099662585e-5`. The complex construction remains
PR #36's `(28,28)` mixed-center-19 witness with saving `717/10^7`.
Exact rational logarithm and exponential enclosures certify both moments,
all **47 strict assembly conditions**, seven margins and eventual cutoff
comparisons. The semantic precision includes the scalar gate count, with
`C1=1` and row stock `p^2000`. All normalizations use the changed width W.

The strongest of the four checked producer combinations is selected:

| h23 / h25 producer | Conditional kappa |
|---|---:|
| association / association | 4.020046773e-5 |
| association / alternating | 4.059827972e-5 |
| alternating / association | 4.058936056e-5 |
| alternating / alternating | **4.099494519e-5** |

This finite comparison does not establish an optimum over other graphs,
carrier assignments, bases or dimensions.

## Sources, reproduction and validation

The parent is PR #40 at `e3bf3ab0cb1ec48588e279b31a97e7a49c72f99e`.
RaD source fixtures are pinned to PR #41 at
`d9c96297d455053b795ee58ba108d5cf892e1c04` and its immutable checkpoint
`7e488e6b25dc1713c1f41baaf1cefbf677507cf3`. The later PR #41 head
`03bde70c0c2a453f1ceae20c619b602841405467` adds only a PR body document.
Pinned graph hashes, source hashes, fixtures and reproduction code are local;
no sibling checkout or network fetch is required.

```sh
make rad-fixed-reversed-check
make rad-fixed-reversed-producer
make verify
```

Python 3.11 or newer and a C++ compiler are required. The focused patch applies
to the pinned parent. Inherited manuscripts are unchanged.

**Validation status: fresh producer/profile and independent schedule checks,
exact geometry compatibility and arithmetic, and 12 focused tests pass. A full
repository rerun for this contribution is pending.** Earlier validation receipts apply
only to their own pinned commits. The draft PR will be marked ready after a
successful full rerun and a published validation receipt.

The analytic recovery, eligible prime/native tables, eventual setup constants,
sequential fixed-tape routing and bulk interfaces, and all-size dirty-state
transfer remain inherited proof dependencies. These finite checks and the
written composition argument do not constitute formal verification or
independent expert acceptance of the full multiplication theorem.

## Attribution

Rohan Arun, with substantial OpenAI Codex assistance, supplies the fixed-profile
composition, independent checks and integration. **RaD / hipotures** supplies
the changed producer graphs, alternating point policy and preceding assembly
work. Credit **icekylinx** for fixed projectors and copied centers, **James
Chang** for reversed geometry, **Dominik Scholz** for fixed-basis/dimension
refinements, **Zhihao Chen**, **Aurel Prosz / Paureel**, **Swapnil Jain**,
**eumemic**, **Douglas Colkitt**, **OpenAI**, **Harvey–van der Hoeven**, and all
retained predecessor authors, licenses and AI-assistance notices.
