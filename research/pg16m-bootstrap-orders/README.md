# Bootstrap orders on PG(2,16)−M: independent checks, an exact merge-family optimum, and a bounded search

**Status: search result plus an exact optimum inside one structured family. No new bound on Boot, no κ claim.**
Author-checked; one separate AI review agent tried to break it (below); no human review. Base: canonical `main` at `1b8ec21e`.

Predecessor and source of the question: Philippe Van Velzen (philippeVV), `limits-1` at
`ed21d6245f8ce1a62e21205be7bedc24271dd772` (`research/complex-budget-law/limits-1/bootstrap/`, expXL) and
`limits-2` at `ae0cd3ed609ad3a8956aa070ee9ec40ff79a600a`, Discussion #2278. Those packages are author-checked and not
reviewed; nothing here re-derives their theorems.

## Question

Γ = PG(2,16)−M has 546 vertices, degree 16, E = 4368 and local half-rate MDS codes (k = 8). limits-1 reports
Boot(Γ) ∈ [772, 784], where 772 = dim C of the Hermitian Singer code (imported) and 784 is the Singer cyclic order.
Under the limits-1 bootstrap corollary, an order of cost 772 with a feasible back-arc flow would make that code
schedulable; a certified Boot > 772 would show it is not.

Scope note: dim C/E = 772/4368 = 0.1767 is below the κ ≥ 0.1 threshold 0.1930 at girth 6, and limits-1 already lists
PG(2,16)−M as excluded. So q = 16 is a test instance for the Hermitian bit-side route (the κ-relevant instance is
PG(2,64)−M at s = 0.2154). Either outcome here is evidence about that route, not a κ change.

## Definitions used (checked against `limits-1/bootstrap/README.md` and `xl/check_order.py`)

- An **order** σ is a permutation of the 546 vertices. j_v = number of neighbours of v earlier in σ.
- **cost(σ)** = Σ_v (8 − j_v)⁺ = ½ Σ_v |j_v − 8| = ½ × (total ascent of the prefix-cut profile).
  **Boot(Γ)** = min over σ of cost(σ).
- **Flow feasibility** (the `boot3` rule): every v with j_v > 8 sends j_v − 8 back arcs, one per edge, to earlier
  neighbours u with j_u < 8, and each such u receives exactly 8 − j_u. σ gives a schedule iff this transportation
  problem is feasible.
- **Split identity** (limits-1, re-checked here at every prefix of every recorded order): for any prefix S of σ,
  cost(σ) = ½|∂S| + Σ_{v∈S}(j_v − 8)⁺ + Σ_{v∉S}(ℓ_v − 8)⁺, with ℓ_v = later neighbours outside S. The two sums can be
  minimised separately, so **Boot = min_S [½|∂S| + P(G[S]) + P(G[V∖S])]**, where P(H) is the least excess of H over
  8-degeneracy. Cost 772 therefore needs a cut profile with total ascent exactly 1544.

## Results

| Item | Result | Grade |
|---|---|---|
| Graph identity | `graph16_59.txt` is the Singer incidence graph of PG(2,16) with difference set D′ ∪ {59} minus the invariant matching point i — line i+59. Rebuilt byte for byte from 17 integers; ord784 is the alternating cyclic order with multiplier 118 and line offset 81 | measured |
| Independent checker | Separate implementation (scipy Dinic, and stdlib Dinic in `verify.py`) agrees with `check_order.py` on ord784 (784, max cut 1568, flow 784/784), its reversal, a two-swap (789, flow 785/789, infeasible) and 3 random orders; both reject duplicate or missing vertices. `check_order.py` accepts a degree-preserving rewired graph that contains a 4-cycle; this checker rejects it | measured |
| Lower bound | 751 (Laplacian λ₂ = 11 at the size-273 prefix). Reproduces limits-1. No bound above 751 was certified | measured |
| Cut-width ceiling | limits-1's `o3_52` order has max prefix cut 1544, so max_t min_{\|S\|=t} \|∂S\|/2 ≤ 772: bisection, spectral and cut-width bounds cannot certify Boot > 772. (The total ascent of the profile is also a function of the cuts and equals 2·cost, so this is a statement about cut-width-type bounds, not every cut functional.) | measured |
| **Exact merge-family optimum** | Over all 144 × 144 × 273 = **5,660,928** families "points P_{m_p i}, lines L_{m_l l + c}, any interleaving", the exact DP minimum is **784**. Only m_p = m_l ∈ {118, 155 = −118} with c ∈ {81, 199, 236} attain it. Next values: 785 (4 families), 786 (2), 787 (4) | measured (exact within the family) |
| Bounded search | No order below 784. Best non-cyclic order: **785 (max prefix cut 1570, flow 567/785, infeasible)**. Ledger below | search result, not a bound |

### Search ledger (exact cost in the loop; all runs on one 8-core desktop)

| Method | Budget | Best |
|---|---|---|
| Partition annealing, objective ½\|∂S\| + peel(G[S]) + peel(G[V∖S]) (= exact cost of a built order), from the 784 peak split | 8 runs × 0.2M and 8 × 3M moves | 784 (never below) |
| Same, from random splits | 8 × 0.2M, 8 × 3M, 16 × 4M, 16 × 8M moves | 785 |
| Beam search over prefix sets, value = exact cost of a greedy-peel completion | width 64 / 24 candidates × 8 seeds; width 512 / 32 × 8 seeds | 797 |
| Exact-cost insertion annealing (window 40–60) on the best non-cyclic orders | 8 × 60M, 8 × 600M, 8 × 600M and 8 × 200M moves | 785 (polish never improved a 785 order) |
| Exact merge DP (above) | 5.66M families, about 27 min on 8 cores | 784 |

Every recorded cost is ≥ 772, which is consistent with the imported dim C ≤ Boot.

**On the "untried method".** The session brief asked for MCTS or learned-value beam search over prefix orders. The
split identity shows that the cost-to-go from a prefix set S is exactly P(G[V∖S]). The beam therefore scores states by
a direct upper bound on that quantity (a min-degree peel), which is also an exact rollout cost. A learned value would
fit the same quantity, so none was trained. MCTS and RL were not run.

## Limits

- Not a bound. A failed finite search is a statement about the searched domain only.
- The merge DP is exact only inside the two-sequence cyclic merge family. Orders that interleave more than two
  sequences, or that are not cyclic on either side, are outside it.
- dim C = 772 and the bootstrap theorem/corollary are imported from limits-1 (author-checked, not reviewed).
- Peel penalties are greedy; P(G[S]) can be smaller than the peel value. The annealers optimise an upper bound.

## Open next questions

1. **Certified Boot > 772.** Why: only this closes q = 16. First step: lower-bound P(G[S]) by the density excess
   max_{K⊆S}(e(K) − 8|K|) (a max-flow computation) and test whether ½|∂S| + D(S) + D(V∖S) ≥ 773 can hold on every
   split with |∂S| ≤ 1544. Blocked by: the outer minimum over S is still a partition problem; it needs branch and bound.
2. **Three or more interleaved cyclic sequences.** Why: the two-sequence family is now closed at 784. First step:
   exact DP over merges of the cosets of the order-3 or order-7 subgroup of Z₂₇₃ (about 274³ states per family).
   Blocked by: the family count grows quickly; restrict to the native multiplier first.
3. **PG(2,64)−M.** Why: that is the κ-relevant instance. First step: the merge DP for the native Singer multiplier
   only (N = 4161, about 1.7 × 10⁷ states per family). Blocked by: the graph file and the dimension check for that matching.

These questions are mirrored in `TASK.json`.

## Reproduce

Registered replay (stdlib, Python 3.12, about 20 s):

```sh
python3 scripts/research_package.py --package research/pg16m-bootstrap-orders --check-only
python3.12 scripts/research_package.py --package research/pg16m-bootstrap-orders
```

`verify.py` rebuilds the graph and ord784 and checks their pinned SHA256 values, re-evaluates every order in
`RESULT.json` (cost, max cut, Dinic flow), replays the exact merge DP in pure Python on 47 recorded families (all 6
optima, the reversed-multiplier family and 40 random ones), and runs 4 corrupted-input controls plus the two-swap flow
control. The ½Σ|j − 8|, cut-ascent and split-identity checks hold by algebra on any 16-regular graph; they are sanity
checks on the implementation, not evidence about the orders.

What the registered replay does **not** cover: the global merge-DP minimum of 784 over all 5,660,928 families. That
rests on the numba sweep (`search/merge_dp.py`). The review agent independently re-implemented the DP from the limits-1
graph file and reproduced it on two full slices: the diagonal m_p = m_l (39,312 families; counts 784:6, 785:4, 786:2,
787:4, 788:2, 789:8, identical to `RESULT.json`) and the row m_p = 118 (39,312 families; 784 only at m_l = 118), plus
300 random families (minimum 855). It did not rerun the full sweep.

Search tools (not part of the registered replay; numpy, scipy, numba): `search/merge_dp.py` (full sweep),
`search/sa_part.py`, `search/beam.py`, `search/polish.py`, `search/indep_check.py`, `search/controls.py`,
`search/spectral.py`, with shared kernels in `search/core.py`. Run them from `search/` with `graph16_59.txt` copied there.

## Credit

Question, definitions, the 784 order, `o3_52`, the cost identities and dim C: Philippe Van Velzen (limits-1, limits-2).
This package: Sudarsh Chaturvedi, with substantial assistance from Claude (Anthropic) for code, search and drafting.
New work is Apache-2.0.
