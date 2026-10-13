# Positive frames and paid clones on skip-prefix graphs

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{4548671376}{10^{14}}=4.548671376\times10^{-5}>2^{-15}.$$

This is **0.4334% above PR #54** (`141532521/(3125·10^9)`) and **1.1233% above
PR #53** (`4498144/10^11`). The bit saving is `4548878290/10^14`, and
W = 159,509,439 (PR #53: 160,799,739; PR #54: 159,592,676).

## Construction

This construction combines two previously proposed changes:

1. **PR #53 (Avi Eisenberg): skip-prefix strips.** The scalar DAG is
   unchanged.
2. **PR #51 (hipotures / RaD): backward-positive labels and paid whole-chain
   clones.** On the skip-prefix DAG we compute envelope carriers
   (`match_exported_dag`) and PR #51's enlarged signed positive labels
   (`scripts/partial_swap/positive.py`). Then we run PR #51's clone search
   (`positive_clone_search`, limit 4, policy `late`) with its rank-node
   matcher until no clone remains. Two rounds each:

   | | Before | After |
   |---|---:|---:|
   | h=23 roles | 32,946 | 32,693 (230 + 23 clones) |
   | h=25 roles | 43,409 | 43,009 (375 + 25 clones) |

   PR #51's alternative-partition stage finds nothing further.
3. **PR #44's numerically weighted carrier matching**, run under the positive-frame
   adjacency.

PR #54 independently applied paid clones to PR #53 with original-envelope
frames. The enlarged frames admit more clones and carriers here.

The geometry is unchanged: both fixed bases I+J, as in PR #53. So PR #53's
complete data-corner certificate (all 4,073,300 pairs, with exact recovery
of the fallbacks) and the rest of its pipeline carry over unchanged.

## Checks

- **`build.py`** reproduces everything from scratch in about a minute:
  - rebuilds both DAGs, labels and clone rounds, and asserts the pinned
    digests (`pins.json`)
  - profiles the pinned matchings
  - runs **PR #51's independent compiler** `check_compiled_witness` (scalar
    identity, rational frame containment, physical role compiler, rank
    timeline), which passes at both h
- **Profiles** come from `tools/cprof.cpp`, which builds frame projectors in
  the basis `L=I+cJ` from a closed form, mod three primes, with PR #51's
  max-corner pivot rule. It reproduces **PR #53's certified I+J profiles
  exactly** (c=1, original-envelope labels) and **PR #51's certified
  negative-basis profiles exactly**, at both h.
- **`witness.py`**:
  - exact moment at the new bit saving
  - all 47 constraints and seven margins
  - the next bit-saving and κ grid points are rejected
  - PR #53's and PR #54's child lists are excluded by exact lower bounds

```sh
make positive-skip-verify
```

**Full `make verify` passed** at research commit `bcb33f4fde2d07b11f0eee98f089e506dfc24e2f`: **211 tests**, four focused tests, fresh DAG/label/clone rebuilding and compiler checks, inherited producer and complete data-geometry replay, and **18 historical patch checks**. See [validation.json](validation.json). Separately, PR #51's exact Boost-based profiler in `fixed` mode reproduced both pinned `blocks` arrays exactly: 85,355 matrices and 10 primes at h23; 113,893 matrices and 11 primes at h25. See [exact-recertification.json](exact-recertification.json) for complete profiler outputs, source hash and comparisons. These finite checks leave the inherited general analytic and physical interfaces subject to mathematical review.

Weighted matching is a numerical discovery procedure; the pinned output is
checked exactly. No exact weighted-matching optimality or global optimality
claim is made.

## Attribution

Avi Eisenberg (PR #53 skip-prefix strips). hipotures / RaD (PR #51 positive
labels, clone search, rank-node matcher, compiler checker and profiler,
copied in `pr51/` under Apache-2.0). Chafik Boukhalfa (PR #43/#46/#48/#54).
icekylinx, James Chang, Dominik Scholz, Zhihao Chen, Aurel Prosz / Paureel,
Swapnil Jain, eumemic, Douglas Colkitt, OpenAI, Harvey–van der Hoeven and
all retained predecessors. Composition, weighted matching and certificate by
Rohan Arun with Anthropic Claude assistance.

OpenAI Codex independently replayed the local build, exact profile
recertification and full repository verification.
