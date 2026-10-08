# Hill-climbed producers with optimal carrier matching

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{4105106623}{10^{14}}=4.105106623\times10^{-5}>2^{-15}.$$

This is **0.10918% above PR #46** (`82012589/(2·10^12)`), 0.10918% above PR #44
and 0.13690% above PR #42. The bit saving is `4105275149/10^14`.

## Idea

PR #44 showed that, for a fixed scalar graph, the best carrier matching is an
exact max-weight maximum matching. The bigger lever is the **number of
roles** `R = c + q − matched`. Each removed role is worth far more than any
reshuffling of profiles.

The summand order inside RaD's `total()` calls decides which additions share
nested envelopes, so it decides how many carriers can be matched. Starting
from PR #44's descending order, we pin a vector of adjacent-swap bits
(`bits-{h}.json`) and climb greedily: flip 1–5 bits, rebuild the graph,
solve the optimal matching, and keep the change if the exact bit moment
improves.

| | PR #44 / #46 | This |
|---|---:|---:|
| h=23 roles R (matched) | 36,685 (5,749) | **36,656 (5,778)**, 23 swaps |
| h=25 roles R (matched) | 48,479 (7,565) | **48,398 (7,696)**, 192 swaps |
| Width W | 178,378,409 | smaller |

Unchanged from PR #46:
- RaD's alternating point order and pairing
- original-envelope labels
- both fixed I+J bases
- copied centers and every paid endpoint correction
- reversed data corners, including #46's exact rational recovery of all ten
  fallbacks
- the PR #36 complex layer and the balanced assembly

## Checks

- `producer.py` replays both dimensions with PR #43/#46's own checkers,
  imported unchanged:
  - scalar identity
  - dense global-bitset audit
  - independent recount of every matched use
  - the complete physical timeline and dirty basis in both orientations

  The profiler reads the pinned matching and asserts that every edge is
  admissible. CRT disagreements are zero.
- `witness.py`:
  - exact moment at the new bit saving
  - all 47 constraints and seven margins
  - the next bit-saving and κ grid points are rejected
  - the PR #40–#46 child lists are excluded at the new bit saving by exact
    lower bounds
- `optimize_matching.py` regenerates the pinned links. It needs scipy and is
  not part of `make verify`.

```sh
make climbed-producers-verify
```

A greedy climb over finite swap vectors is a search, not a claim of global
optimality.

**Validation status:** the focused producer replay, the exact certificate and
5 tests pass. A full `make verify` has not been run yet. On Linux/GCC, use
`CXX="c++ -include algorithm"`.

## Attribution

Chafik Boukhalfa (PR #43/#46: composition, checkers, exact data recovery).
RaD / hipotures (PR #41 graphs and point order). icekylinx, James Chang,
Dominik Scholz, Zhihao Chen, Aurel Prosz / Paureel, Swapnil Jain, eumemic,
Douglas Colkitt, OpenAI, Harvey–van der Hoeven, and all retained
predecessors. Optimal matching (PR #44), climbed orders and certificate by
Rohan Arun with Anthropic Claude assistance.
