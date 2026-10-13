# Exact parameter refinement of the stacked PR62 witness

The unchanged stacked PR62 construction supports the freshly checked witness

    kappa = 25508460085039 / 500000000000000000

This exceeds the published stacked `5101691/10^11` and its old scoped limit.
The new bit saving is `102039046058023/2e18`, with explicit `h=10^-18`.
This is a numerical parameter refinement, not a new graph, compiler,
tensor-rank result, practical speedup, or unconditional theorem.

Fresh checks cover the rational moment enclosure, 47 strict assembly
inequalities, seven margins and eventual bounds. Source hashes are checked
before evaluation. The main and stacked PR62 constructions' reported focused
validation is inherited. Their graph, physical words, dirty bases, CPP/CRT
profiles and data geometry were **not rerun for this refinement**. The all-size
framed-word, residual, tape and analytic interfaces remain conditional.
Separate Lean receipts state their arithmetic scope; this Python script does
not compile or verify those files.

Requirements: Python 3.11+ standard library, Git and the external pinned source:

```sh
git clone https://github.com/ikeboy/integer-mult-bounds.git upstream
git -C upstream checkout --detach ad0f25ff7b23cff7f08ad237c2254e6ecf74257e
python3 verify_refinement.py --upstream upstream
```

`arithmetic.json` contains the exact witness and source hashes.
`arithmetic-verification.json` records the executed fresh result. No dependency
downloads or inherited physical replay occur. At a fine grid, an upper-bound
failure to certify the next point is not actual infeasibility or optimality.

The predecessor is [PR62](https://github.com/CrocSwap/integer-mult-bounds/pull/62),
Avi Eisenberg's pair-assembly construction and its stack with Eumemic's joint
frame compiler. All retained author, license and assistance notices remain.
