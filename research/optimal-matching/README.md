# Optimal carrier matching on RaD's fixed-basis graphs

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{2050314627}{5\cdot10^{13}}=4.100629254\times10^{-5}>2^{-15}.$$

This is **0.02681% above PR #43** (`409953/10^10`) and 0.02768% above PR #42
(`4099494519/10^14`). The bit saving is `4100797413/10^14 = 4.100797413e-5`,
against `4.09970639e-5`, the exact maximum certifiable for PR #43's own child
list. These compare conditional asymptotic exponents, not running times.

## The idea

PR #42 and PR #43 choose the carrier matching with Hopcroft–Karp; #42 uses
ascending donor order, #43 descending. Each returns *some* maximum matching.
All maximum matchings have the same cardinality, so they also share:

- role counts (36,685 at h=23, 48,479 at h=25)
- width `W`, `N`, `L`
- the total rank and the rank deficit

Only the fixed-basis block profile differs.

With the cardinality fixed, **the bit moment is linear in the chosen edges.**
In the profiler, a matched edge (donor `u` → use `w`, which carries value `y`
into target `t`) changes the frame-transition multiset by exactly

    +(u→t)  −(u→sink)  −(0→y)  −(y→t)      (self-loops omitted)

Every transition's lower-lower pivot profile, including PR #43's 3-prime
max-corner rule, depends only on its frame pair. So each admissible edge has a
fixed signed effect on the child-width multiset, and each removes exactly `h`
rank units (checked for every edge). The moment `Σ c_t t^τ / (W m^τ)` then
differs between maximum matchings only through the first-order term
`Σ c_t · t · ln t`.

We maximize that sum exactly over all maximum-cardinality matchings. This is
a bipartite assignment, with a private penalized dummy column per donor so
that cardinality comes first. The candidate edges are exactly the admissible
adjacency of `profiles.cpp`: causal order plus frame inclusion.

| | Donors | Uses | Admissible edges | Matched |
|---|---:|---:|---:|---:|
| h=23 | 6,609 | 6,171 | 10,406 | 5,749 |
| h=25 | 8,756 | 8,108 | 13,686 | 7,565 |

We also apply PR #43's descending (support size, bitmask) summand sort at
h=25, not only at h=23. With optimal matching, this choice helps; it keeps
R=48,479. At h=23 the DAG is byte-identical to PR #43's.

| h=23 graph | h=25 graph | Matching | Bit saving |
|---|---|---|---:|
| #43 | #43 | descending HK (#43) | 4.09970639e-5 |
| #43 | #43 | optimal | 4.10069931e-5 |
| #43 | descending sort | **optimal** | **4.10079741e-5** |

The matchings are pinned in `links-23.uses` and `links-25.uses`. They use the
same binary format PR #43 exports. `optimize_matching.py` regenerates them;
it needs scipy and is not part of `make verify`. The certificate needs only the
pinned links. Optimality over matchings for these finite graphs is not a
claim of global optimality.

## Checks

`producer.py` replays both dimensions with **PR #43's own independent
checkers**, imported unchanged:

- scalar identity
- dense global-bitset audit
- independent recount of every matched use
- the complete physical role timeline
- the dirty basis in both orientations (`original_timeline.check`)

It also profiles the pinned links with `profiles.cpp`. That file is unchanged
except that the matching is read from the pin, and each pinned edge is
asserted to lie in the admissible adjacency. All replayed JSON must equal the
pinned files, and CRT disagreements are zero.

`witness.py` reuses PR #43's data corners and geometry, with the ten
conservatively charged fallbacks unchanged. It also reuses the complex layer
and the balanced assembly. Then it checks:

- the exact moment at the new bit saving
- all 47 assembly constraints and seven margins
- that the next bit-saving and κ grid points are both rejected
- that the PR #40, #41, #42 and #43 child lists are excluded at the new bit
  saving by exact lower bounds

```sh
make optimal-matching-verify
make verify
```

On Linux/GCC the profiler is compiled with `-include algorithm`, because
`scripts/partial_swap/binary_io.hpp` uses `std::reverse`.

**Validation status:** draft. The focused producer replay and the exact
certificate pass. The full repository `make verify` is running and will be
recorded in `validation.json`.

## Attribution

Chafik Boukhalfa (PR #43: composition, descending matching, independent
checkers, balanced assembly reuse). RaD / hipotures (PR #41 graphs and point
order). icekylinx, James Chang, Dominik Scholz, Zhihao Chen, Aurel Prosz /
Paureel, Swapnil Jain, eumemic, Douglas Colkitt, OpenAI, Harvey–van der
Hoeven, and all retained predecessors. Optimal matching, h=25 order and
certificate by Rohan Arun with Anthropic Claude assistance.
