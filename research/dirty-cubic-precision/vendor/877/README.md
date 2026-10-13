# Quartic precision for balanced dirty commutators

**Mathematical audit / improved sufficient local precision bound; no new κ.**
The balanced dirty-array inverse in
[#628](https://github.com/CrocSwap/integer-mult-bounds/pull/628) admits
**O(p+d+r⁴)** word size, improving its published **O(p+d+r⁵)** sufficient
bound. Here r is the radix, p the requested accuracy, and `2^d` bounds every
initial source, target and dirty array. Retain a finer initial input grid if
one is supplied. The dispatcher, leaf operations, number of calls and
borrowed arrays are unchanged.

The old proof bounds growth across every leaf call. This audit instead bounds
ideal prefixes and their inverses using the restored structure of complete
recursive children, then propagates the actual nonlinear leaf errors through
those linear maps. The full proof and complete inherited bill are in
[PROOF.md](PROOF.md).

For n factors, set `C=1+K`, where each ideal factor has norm at most K:

```text
E(1)=1; E(n)=n+max(floor(n/2)+E(ceil(n/2)), ceil(n/2)+E(floor(n/2))),
E(n)<=4n-3; B=C^E(n).
```

Every ideal prefix and inverse prefix has norm at most B, so every interval
of the ideal word has norm at most `B²`. With N complete leaf calls and
per-leaf error `a u (||source||+1)`, the resulting execution error is at most
`2 N B² a u (B D+1)`, provided `N B² a u<=1/2`. This covers arbitrary initial
dirt and target-dependent trajectories without assuming rounded leaves are
linear. Exact dirty restoration still uses the predecessor's deterministic
inverse contract and nonaliased read-only phases.

## Exact budget comparison

At `p=128`, `d=20`, using PR628's inherited root-gap exponent:

| Radix | Old guard after crediting #663's exact leaf count | New prefix guard |
|---|---:|---:|
| 4 | 680 | 1,341 |
| 9 | 31,106 | 32,514 |
| 16 | 461,599 | 266,372 |
| 64 | 516,978,511 | 73,245,212 |
| 256 | 544,452,103,903 | 19,177,910,612 |

These are conservative **sufficient fractional-bit budgets**, not measured
minimum precision, speedups or useful hardware word sizes. The earlier bound
is better at small radices; either valid bound may be used. For radix 64 the
new budget improves even the exact-count baseline, beyond the earlier
reduction of PR628's `4n²` allowance. Its 63 factors still execute **4,000**
leaves and use six arbitrary dirty arrays. Their prefix exponent is 188.

The complete neighboring-layout cost becomes
`soft-O((L r²+r³)(p+d+r⁴))` under the unchanged preparation and arithmetic
assumptions. All three leaf passes, validation/source access, inverse calls,
`ceil(log2 n)` borrowed arrays, clean scalar arithmetic, indexing, descriptors,
phase access and arbitrary-stride routing remain charged.

## Reproduce

Python 3.11+, standard library, no network or Git required, read-only by default:

```sh
python3 -B -I research/dirty-prefix-precision/verify.py
python3 -B -I research/dirty-prefix-precision/test_precision.py
```

Expected main marker:

```text
PASS_DIRTY_PREFIX_PRECISION budgets=1740 prefix_traces=18 rounded_generic=48 rounded_kernels=40 controls=10 kappa=unchanged
```

[EXPECTED.json](EXPECTED.json) contains the deterministic receipt. An explicit
`--write /new/path.json` reconstructs it and refuses an existing destination.
The [validation record](VALIDATION.md) describes executed commands and package
controls.

- **10,000** factor counts check the resource majorants and #663's count formula.
  The independently emitted positive/negative words match the immutable #628
  dispatcher for n=1..64: **128 words, 191,342 instructions**.
- **18** dense integer traces with noncommuting 2×2 factors check every prefix
  and inverse prefix: **11,142 boundaries**. Separate rational Gauss-Jordan
  inversion checks 66 selected prefixes. All **5,104** nonempty contiguous
  subwords in the fixtures through eight factors are also built directly and
  compared with their prefix/inverse-prefix products.
- **1,740** exact integer budgets cover all 116 prime-power radices from 3
  through 512, five target precisions and three initial magnitude bounds.
  Both the original and exact-call-count baselines are recorded.
- **48** generic and **40** actual kernel executions use the unchanged #628
  rounded leaves. All ten pinned kernel certificates are checked, with dense
  expanded-polynomial solves, nonzero initial dirt, both cycle orientations,
  and cycle lengths one and three. Every executed leaf restores its source;
  all 6,304 leaf boundaries satisfy the new magnitude bound. Every complete
  inverse cancels exactly. All 88 executions have nonzero rounding error
  bounded by the new execution budget. Kernel tests also charge coefficient
  perturbation and prove total error at most `2^-128`.
- Ten controls reject altered budget obligations, omitted restore, wrong
  inverse order and using the final operator norm as a prefix bound. Four
  tests exercise exact logarithm boundaries, finer input grids, the feedback
  threshold and eight additional nonlinear-error executions.

The finite domains and seed **63** are fixed in [CLAIM.json](CLAIM.json).
The all-n and all-cycle-length conclusions rest on the written proof and
inherited leaf/preparation theorems, rather than an extrapolation from tests.

## Scope, provenance and credit

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`; selected #799 remains at
κ=`1661634653669567/10^18`. The subject is the separate local #628 primitive,
head `0768f97d06c623b8211e651543c66135796b62bf`. Its consumed files and notice
are vendored verbatim and verified by SHA256 and Git blob identity in
[SOURCES.json](SOURCES.json). Original documentation is retained as historical
source, including its superseded sufficient precision estimate.

Credit **Chafik Boukhalfa (@chafreaky)** for #628's rounded leaves and dirty
composition, **0xkilgore** for #663's exact count and nonlinear restoration
audit, and **androolloyd** for #673's multiway echo and phase-alias repair.
The declared contract here requires phase arrays distinct from every mutable
array; this audit does not claim to fix the known alias defect in vendored
#628. The original notices credit Ali Romman's #621 kernel and its sources.

Related #689/#730/#744 optimize or audit other echo trees and call counts;
#714 uses one clean root checkpoint; #846 studies arbitrary strides.
Chafik's concurrent **#862** obtains cubic precision with owned widened words
and reserved low zero bits. That differs from the arbitrary-dirty-array
contract preserved here. None of those pending packages is imported.

General multiway or unbalanced trees, variable leaf precision, common-label
or Clifford compilation, reversible-bit realization, physical ownership,
full-transform accounting and the multiplication reduction are outside this
result. Factor preparation algorithms and fast fixed-precision arithmetic
remain inherited hypotheses, not newly implemented software. No selected
artifact or `upstream/` file changes. No full theorem formalization or
literature-priority claim is made.

Prepared for **Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance**. Apache-2.0; predecessor notice retained. All new code and the
proof were written by one AI agent; separate arithmetic methods are not
independent human review.
