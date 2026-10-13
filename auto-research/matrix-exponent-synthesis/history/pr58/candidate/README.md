# Exact parameter refinement of pinned PR58

This changes the certified numerical parameters, with the PR58 graph, words,
profiles, and inherited algorithm left unchanged:

    kappa = 59384196136667 / 1250000000000000000

It is strictly above PR58's published `475073569/10^13` and the scoped limit
computed with its old bit saving. The backoff is explicitly `h=10^-18`.
This is a small numerical-witness refinement, not a new multiplication graph,
matrix tensor-rank result, practical speedup, or unconditional theorem.

The fresh check recomputes the rational moment enclosure, all 47 strict
assembly inequalities and seven margins, and the eventual-bound arithmetic.
The unchanged physical construction's validation is inherited from PR58;
its producer, XOR words, dirty bases, CPP/CRT and data sweep were **not rerun**
for this refinement. Separate Lean artifacts establish their stated arithmetic
scope; this Python checker does not claim to compile or verify those artifacts.

Python 3.11+ standard library and Git suffice:

```sh
git clone https://github.com/chafreaky/integer-mult-bounds.git upstream
git -C upstream checkout --detach bc2f7ed4c20dc18898305ab17165c0c995cbb804
python3 verify_refinement.py --upstream upstream
```

Git HEAD, the exact source certificate, and the two arithmetic implementations
are hash-checked before evaluation. This needs the explicit external pinned
checkout; no external dependency download or inherited construction replay is
performed. `arithmetic.json` contains the exact new witness and source hashes.

At the fine search grid, failure of the next **upper enclosure** to certify a
point is not a proof that the actual network cannot satisfy that point. No
global optimality or strongest-ever claim is made. The cited predecessor is
[PR58](https://github.com/CrocSwap/integer-mult-bounds/pull/58), composed by
Chafik Boukhalfa from Rohan Gupta's dual-suffix graphs and Eumemic's joint frame
compiler, with all notices and predecessor credit retained.
