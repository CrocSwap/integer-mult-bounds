# Mathematical argument and scope

## Claim

Conditional on every written proof interface in PR #104 (`854ba7dca98651eab2050402384e1a7784534f0a`,
`notes/stopped-product-*.tex`), this package certifies two finite refinements:

1. **Complex-only refinement (holding PR #104's `h = 23` bit producer and
   `actual_bit_saving = 803380799/10^13` fixed)**:
   $$\kappa_{\text{complex-only}} = \frac{16065034230003}{200000000000000000} = 8.0325171150015 \times 10^{-5}.$$
2. **Joint regenerated bit + complex refinement (regenerating both the `h = 23`
   positive-label bit producer and the `h = 24` rational-center complex producer
   from source through the unmodified C++ matchers)**:
   $$\kappa_{\text{joint}} = \frac{3520093170589}{40000000000000000} = 8.8002329264725 \times 10^{-5}.$$

No new analytic theorem, product-ring factorization lemma, or recursive tape
interface is introduced; all scalar support identities, frame-nesting rules,
matching legality checks, and assembly inequalities are verified by the
inherited code.

## 1. Staggered dual-paired leave-one-out strips

Given $n$ summands $v_0, \dots, v_{n-1}$ with pairwise disjoint supports, the
leave-one-out outputs are $\text{out}_i = \text{prefix}[i] + \text{suffix}[i+1]$
for $0 \le i < n$. In standard sequential `ExclusionCircuit.vector(..., two=False)`,
neither `prefix` nor `suffix` shares operands between consecutive steps, leaving
all internal chain additions unmatched unless they accidentally share a leaf
with an endpoint output.

In `block_vector(values)`:
- For odd $i = 2k+1$, we form $p_k = v_{2k} + v_{2k+1}$ and set
  $\text{prefix}[2k+2] = \text{prefix}[2k] + p_k$, while for even $i = 2k$ we
  keep $\text{prefix}[2k+1] = \text{prefix}[2k] + v_{2k}$.
- For odd $i = 2k+1 < n - 1$, we form the **staggered** pair
  $q_k = v_{2k+1} + v_{2k+2}$ and set
  $\text{suffix}[2k+1] = q_k + \text{suffix}[2k+3]$, while for even $i = 2k$ we
  keep $\text{suffix}[2k] = v_{2k} + \text{suffix}[2k+1]$.
- When $n \ge 3$ and $v_0 = 0$, we strip the leading zero and recurse on
  $v_1, \dots, v_{n-1}$, returning $(\text{total}, [\text{total}] + \text{one}_{\text{nz}})$.

Because the pairing parity in `suffix` is shifted by one index relative to
`prefix`, every internal node participates in a legal carrier match:
1. $\text{prefix}[2k+1] = \text{prefix}[2k] + v_{2k}$ and
   $\text{prefix}[2k+2] = \text{prefix}[2k] + p_k$ share $\text{prefix}[2k]$
   with nested cover/support.
2. $\text{suffix}[2k+2] = v_{2k+2} + \text{suffix}[2k+3]$ and
   $\text{suffix}[2k+1] = q_k + \text{suffix}[2k+3]$ share $\text{suffix}[2k+3]$
   with nested cover/support.
3. Each prefix pair $p_k = v_{2k} + v_{2k+1}$ shares $v_{2k}$ with
   $\text{suffix}[2k] = v_{2k} + \text{suffix}[2k+1]$ (whose support/cover
   contains $\{v_{2k}, v_{2k+1}\}$).
4. Each suffix pair $q_k = v_{2k+1} + v_{2k+2}$ shares $v_{2k+2}$ with
   $\text{prefix}[2k+3] = \text{prefix}[2k+2] + v_{2k+2}$ (whose support/cover
   contains $\{v_{2k+1}, v_{2k+2}\}$).

## 2. `h = 24` rational-center complex producer (`R = 39,040`)

In `research/staggered-rational-centers/producer.py`:
- `StaggeredPairedTriple` subclasses `PairedTriple` with base threshold 2 in
  `block`, reverse-folded linear sums `rtotal` in `block`, `coarse`, and
  `coeff`, `block_vector` in `block` and recursive `vector(..., two=False)`
  (`len(values) < 11`), and odd-step suffix pairing at the top-level
  `two[u,v]` strip (`len(values) == 11`). Keeping every `suffix[i]` ($0 \le i < 10$)
  in `two[u,v]` ensures that when `complex.py` iterates over the reversed
  non-mate coordinates `((i ^ 1) in (a,b), -i)`, all ten even prefix totals
  `pre[2], pre[4], ..., pre[20]` hit `lookup[s]` without allocating duplicate
  gates.
- For each pair star `(a,b)` over the $22$ remaining coordinates $w_0, \dots, w_{21}$:
  - `suf` is built in two-step pairs `suf[j+1] = add(w[j+1], suf[j+2])` and
    `suf[j] = add(add(w[j], w[j+1]), suf[j+2])`.
  - For same-group pairs `(a ^ 1) == b` (which are skipped by `two[u,v]`), `pre`
    is paired at odd `idx_w < 20`, reusing `add(w[idx_w-1], w[idx_w])` via
    `lookup`.
  - Endpoint outputs at $j \in \{19, 21\}$ share `q20 = add(pre[19], w[20])` via
    `node(19) = add(q20, w[21])` and `node(21) = add(q20, w[19])`.
  - At $j = 20$ and same-group even $j \ge 4$, `node` uses the shifted pair-bridge
    `add(pre[j-2], add(add(w[j-2], w[j-1]), suf[j+1]))`.
  - When `(a ^ 1) != b` and $2 \le j < 18$ with `i // 2 < a // 2` or
    `(j // 2) % 2 == 0`, `node` uses the leave-one-pair-out bridge
    `add(add(pre[jj], suf[jj+2]), w[jj ^ (1 - (j & 1))])` ($jj = j \mathbin{\&} -2$).

All assertions in `complex.py` (disjoint ordinary additions, exact target
supports, exact rational center scatter with fixed odd divisor 21, and
nondegenerate nested binary frames) and in `match_complex_general.cpp` pass
unchanged. The resulting $h = 24, d = 24$ producer has $c = 48,958$,
$q = 8,120$, $\text{matched} = 18,038$, $R = 39,040$, $\ell = 552$, and
$\sum_r r H'[r] = 24 R + 2\ell = 938,064$, certifying complex saving
$b = 8801801147 / 10^{14}$ (with $b + 10^{-14}$ rejected).

## 3. `h = 23` positive-label bit producer (`R = 34,014`) and assembly bounds

In `research/staggered-rational-centers/bit_producer.py`, applying
`StaggeredDualPaired` and alternating pair ordering `alternating_points` to the
$h = 23$ retained-total bit producer and running the unmodified
`match_exported_dag.cpp`, `positive.py`, and `match_positive_dag.cpp` yields
$\text{orig}[\text{"matched"}] = \text{pos}[\text{"matched"}] = 10,541$,
$c = 39,219$, $q = 5,336$, $R = 34,014$, $\ell = 506$, and
$\sum_r r H[r] = 23 R + 2\ell = 783,334$. Under `stopped_product_network.coarse_moment`,
this certifies coarse bit saving $\text{COARSE} = 8926632362 / 10^{14}$ (with
$\text{COARSE} + 10^{-14}$ rejected) and stopped bit saving
$$\text{AB}_{\text{joint}} = (1 - 10^{-3})\,\text{COARSE} + 10^{-3}\,\text{OLD} = \frac{4460775859819}{50000000000000000} = 8.921551719638 \times 10^{-5}.$$

Evaluating `structured_bulk_assembly.assembly` with $\beta = 10^{-6}$ gives:
- **Complex-only certificate** (using PR #104's pinned `stopped-product-bit-axis.json`
  and $\text{AB} = 803380799 / 10^{13}$):
  $a = \min(\text{AB}, (1-\beta)b - 10^{-10}) = 803380799 / 10^{13}$, certifying
  $\kappa_{\text{complex-only}} = 16065034230003 / 200000000000000000 = 8.0325171150015 \times 10^{-5}$
  (with $\kappa_{\text{complex-only}} + 10^{-18}$ rejected).
- **Joint certificate** (using both regenerated producers):
  $a_{\text{joint}} = \min(\text{AB}_{\text{joint}}, (1-\beta)b - 10^{-10}) = (1-\beta)b - 10^{-10} = 8801782345198853 / 10^{20}$,
  certifying $\kappa_{\text{joint}} = 3520093170589 / 40000000000000000 = 8.8002329264725 \times 10^{-5}$
  (with $\kappa_{\text{joint}} + 10^{-18}$ rejected).
