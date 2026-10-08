# A searched-order variant of PR #49's exclusion graphs

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{4125007391}{10^{14}}=4.125007391\times10^{-5}>2^{-15}.$$

This is **0.02773% above PR #49** (`4123863984/10^14`). The bit saving is
`825035511/2\cdot10^{13}` `= 4.125177555\times10^{-5}`.

## Idea

PR #49 pinned a greedy climb over the adjacent-swap bits of PR #48's `total()`
and `vector()` orders, and its own scope note disclaims global optimality of that
search. This variant runs a **complete single-bit-flip descent** from the same
pinned bits: every decision bit (1584 at h=23, 1900 at h=25) is flipped,
evaluated end to end, and the best strict improvement accepted; the pass then
repeats until no single flip improves.

The objective matters. A flip can add matched carriers and add more additions at
the same time, so maximising matched carriers is *not* the same as minimising the
role count `R = c + q - matched`. Because `W = 2N + sum_h (N // v_h) * R_h` holds
the child list fixed, `R` is the quantity that moves the role volume and hence
the exponent, so the descent minimises `R` directly, with matched carriers and
the log-weight as tie-breaks.

| | PR #49 | This |
|---|---:|---:|
| h=23 roles R (matched) | 36,382 (6,077) | **36,341 (6,153)** |
| h=25 roles R (matched) | 48,255 (7,809) | **48,247 (7,825)** |
| Width W | 177,284,805 | **177,176,337** |
| bit saving | 4124034054/10^14 | **825035511/2\cdot10^13** |
| kappa | 4123863984/10^14 | **4125007391/10^14** |

Everything else is PR #48/#49, unchanged: RaD's point order and original-envelope
labels, both fixed I+J bases, copied centers, paid endpoint corrections, reversed
data corners with exact recovery of all ten fallbacks, the complex layer and the
balanced assembly.

## Checks

- `witness.py` derives the bit saving and kappa from the searched rows and their
  certified profiles (a grid search instead of pinned constants) and checks the
  47 assembly constraints, the seven margins, the rejection of the next bit and
  kappa grid points, and the exclusion of **nine** earlier networks at the new
  saving - including PR #49's own - which is what makes the improvement strict.
- `producer.py` replays both dimensions with PR #43's independent checkers
  (imported unchanged): scalar identity, dense global-bitset audit, the pinned
  matching read back by `profiles.cpp` with every edge asserted admissible, an
  independent recount of every matched use, and the complete physical timeline
  and dirty basis in both orientations. CRT disagreements are zero.
- `make ordered-descent-verify` runs both.

## Scope and limits

This is a **single-bit local optimum** of the order space, not a global one, and
the descent was still finding improvements when it was stopped (`R` had reached
36,336 and 48,239 in the unfinished next passes), so the reported numbers are a
lower bound on what this search reaches. No global optimality is claimed for the
matcher beyond the pinned max-weight maximum matchings; the inherited PR #48
dependencies and the analytic hypotheses are unchanged and remain conditional.

## Reproduce

```sh
make ordered-descent-producer   # full independent replay (needs a C++17 compiler)
make ordered-descent-check      # exact witness and focused tests
```

The search harness itself (bit-vector descent with the role-count objective) is
not shipped; the searched bit vectors, producer rows, certified profiles,
matchings, witness and certificate are.

## Attribution

Base graphs, orders, matching objective and composition: PR #48 (Chafik
Boukhalfa) and PR #49 (Rohan Arun with Anthropic Claude assistance), themselves
building on RaD / hipotures PR #41, icekylinx, James Chang, Dominik Scholz,
Zhihao Chen, Aurel Prosz / Paureel, Swapnil Jain, eumemic, Douglas Colkitt,
OpenAI and Harvey-van der Hoeven. The searched-order descent, the role-count
objective and this run were produced by @maxime-fleury with AI assistance.
