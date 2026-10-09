# Staggered dual-paired rational-center and bit producers on PR104 / PR107

Under **all of PR104's inherited and newly proposed interfaces** (building on
commit `854ba7dca98651eab2050402384e1a7784534f0a` from PR #104 and commit
`fc7e8ce7abb1d12f01b2406a61a77286ba613437` from PR #107), this finite
refinement certifies two exact rational bounds:

1. **Complex-only refinement (with PR104's `h = 23` bit producer and
   `actual_bit_saving = 803380799/10^13` held fixed)**:
   $$\kappa_{\text{complex-only}} = \frac{16065034230003}{200000000000000000} = 8.0325171150015 \times 10^{-5}$$
   (**+3.05022% above PR104**'s $7.79476 \times 10^{-5}$ and **+3.00195% above PR107**'s $7.798412662809 \times 10^{-5}$), saturating PR104's stopped bit ceiling $a = \text{AB}_{\text{PR104}} = 8.03380799 \times 10^{-5}$.
2. **Joint regenerated bit + complex refinement (regenerating both the `h = 23`
   positive-label bit producer and the `h = 24` rational-center complex producer
   from source through the unmodified C++ matchers)**:
   $$\kappa_{\text{joint}} = \frac{3520093170589}{40000000000000000} = 8.8002329264725 \times 10^{-5}$$
   (**+12.8993% above PR104** and **+12.8465% above PR107**).

## Mathematical and circuit refinements

1. **Staggered dual-paired leave-one-out strips (`block_vector`)**:
   In a leave-one-out strip over $n$ disjoint summands $v_0, \dots, v_{n-1}$,
   pairing even steps $p_k = v_{2k} + v_{2k+1}$ in `prefix`
   (`prefix[2k+2] = add(prefix[2k], p_k)`) and **staggered** odd steps
   $q_k = v_{2k+1} + v_{2k+2}$ in `suffix`
   (`suffix[2k+1] = add(q_k, suffix[2k+3])`) ensures that every odd-step prefix
   matches into the next even-step prefix (sharing `prefix[2k]`), every
   even-step suffix matches into the preceding odd-step suffix (sharing
   `suffix[2k+3]`), every prefix pair $p_k$ matches into `suffix[2k]` (sharing
   $v_{2k}$), and every suffix pair $q_k$ matches into `prefix[2k+3]` (sharing
   $v_{2k+2}$).
2. **`h = 24` rational-center complex producer (`producer.py` -> `producer.json`)**:
   Combining `StaggeredPairedTriple` (staggered dual-paired `block_vector` at
   recursive levels, odd-step suffix pairing at the top-level `two[u,v]` strip so
   all 10 group suffixes remain in `lookup` for `pre[2k]`, and reverse-folded
   block/coarse/coefficient aggregations) with pair-star synthesis (retained
   reverse group order `((i ^ 1) in (a,b), -i)` from PR #107, paired-step suffix,
   shared endpoint node `q20 = add(pre[19], w[20])`, shifted pair-bridge at
   `j = 20` and same-group even `j >= 4`, and leave-one-pair-out bridge
   `add(add(pre[jj], suf[jj+2]), w[jj ^ (1 - (j & 1))])` when
   `(a ^ 1) != b and 2 <= j < 18 and (i // 2 < a // 2 or (j // 2) % 2 == 0)`)
   reduces the `h = 24, d = 24` complex role count from **44,918 to 39,040**
   (**5,878 roles reclaimed**, `c = 48,958`, `q = 8,120`, `matched = 18,038`)
   and lifts the complex saving from $7.796061114 \times 10^{-5}$ (PR #104) and
   $7.799647191 \times 10^{-5}$ (PR #107) to
   $$b = \frac{8801801147}{10^{14}} = 8.801801147 \times 10^{-5}.$$
3. **`h = 23` positive-label bit producer (`bit_producer.py` -> `bit-axis.json`)**:
   Applying `StaggeredDualPaired` and alternating pair ordering to the $h = 23$
   retained-total bit producer and running the unmodified C++ matchers
   `match_exported_dag.cpp`, `positive.py`, and `match_positive_dag.cpp` yields
   exact matching equality `orig["matched"] == matched["matched"] == 10,541`
   (up from `1,324`), reducing `R` from **38,776 to 34,014** (**4,762 roles
   reclaimed**, `c = 39,219`, `q = 5,336`) and lifting the coarse bit saving to
   $$\text{COARSE} = \frac{8926632362}{10^{14}} = 8.926632362 \times 10^{-5}, \qquad \text{AB} = \frac{4460775859819}{50000000000000000} = 8.921551719638 \times 10^{-5}.$$

## Verification

```sh
python3 research/staggered-rational-centers/verify.py
python3 research/staggered-rational-centers/test_controls.py
python3 research/reversed-rational-centers/verify.py
```

The verifier checks all pinned predecessor hashes, reproduces PR #104's and
PR #107's certificates, compiles the unmodified C++ matchers
(`match_complex_general.cpp`, `match_exported_dag.cpp`, `match_positive_dag.cpp`),
regenerates the PR #104, PR #107, and selected `h = 24` complex producers plus
the selected `h = 23` positive-label bit producer from source, verifies every
histogram entry and rank identity, and checks all 47 strict constraints, 7
margins, and 4 next-grid exclusions across both the complex-only and joint
certificates. Ten adversarial controls in `test_controls.py` reject unpaid
cleanup, omitted retained loss, reuse of parent histograms, and next-grid
exponents.

## Scope and attribution

As in PR #104 and PR #107, **the opposite-bank factorization, stopped atom
streaming, ordinary leaf conversion, common odd-denominator grid, and recursive
tape transfer interfaces in PR #104 remain written proof dependencies, not
independently established theorems here**. See [proof.md](proof.md).

Credit icekylinx for PR #104 and its stopped product-ring/rational-center
construction; Rohan Arun for PR #107 and its reversed pair-star ordering;
Zhihao Chen for the semantic/bulk assembly; RaD/hipotures for its analytic
interfaces; Aurel Prosz/Paureel and the credited two-stage contributors;
eumemic and the retained paired-circuit contributors; Douglas Colkitt, OpenAI,
David Harvey, Joris van der Hoeven, and all predecessors credited in `NOTICE`,
`CONTRIBUTORS.md`, and `SOURCES.json`. Prepared by Thomas Marchand with Google
Antigravity assistance, under Apache-2.0.
