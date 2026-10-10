κ = 7.6817007781759e-4

# Composed stages on the p10 paired-cube word

This conditional finite construction certifies

`κ = 76817007781759 / 100000000000000000`.

It improves on PR315's `7.64230861320245e-4` by about **0.515%**, and on PR316's `7.65146115390441e-4` by about **0.395%**. The bit supplier binds. The unchanged PR315 complex supplier has certified saving `772714351296671/10^18`, including its complete bad-class fallback. These numbers are asymptotic exponent savings, not measured multiplication speeds.

The package vendors PR315 at `243899975d0fbe888d5deda399060885d609e0a1` unchanged, runs its complete verifier fresh, reconstructs its actual parity word, and then applies five pinned, freshly checked stages:

| Stage | Items | Change |
| --- | ---: | --- |
| Kernel condensation | 540 disjoint pairs | 540 new rank-one entrances; exact prefix response relations |
| Target prefix | 120 groups | local paid histogram change `{1:-120,16:-120,17:+120}` |
| Frame retiming | 480 ADDs | partner mixes move from rank 2 to rank 18; signed scalar order unchanged |
| Early restoration | 240 helpers | finish at rank 19; actual endpoint residuals decrease by 240 |
| Commuting reordering | 140 ADDs | independently checked crossed intervals; rebuilt nested MOVE paths |

The target and kernel transformations use exact F₂ relations. No signed-integer endpoint equivalence is asserted for those stages. The verifier replays the actual final signed coefficients, derives their cancellation-free row bounds, and charges their unit expansion. The retiming, restoration commutation and reordering have separate exact scalar arguments.

## Reproduce

Python 3.11+ with SymPy 1.14.0, a C++17 compiler, and Boost headers:

```sh
python3 -m pip install -r research/p10-composed-stages/requirements.txt
python3 -B research/p10-composed-stages/verify.py --output /tmp/p10-composed-proof --cxx g++ --boost-include /usr/include
```

Use a fresh output directory outside the package. No network access is needed. The root manifest pins the entire package, including the unchanged upstream manifest. Input hashes are checked before and after the full run.

## Final accounting

- Local word: **384,471 records**, **335,240 ADDs**, **337,160 unit-expanded additions**, 20 copied centres.
- Actual final word SHA256: `e6ad3590e6ad83a6df4f202adda6fe899ed0c60b20822f608db3de670468f61e`.
- Local positive-rank calls: **48,042**; local paid rank mass: **180,270**.
- Independent dirty helpers: **8,230**; local formal columns: **10,150**; global five-stage formal columns: **12,070**.
- Endpoint residual census: `{3:310,4:960,19:540,20:6420}`. Width 100, 60 replicas, **86,058 banks per stage**, no padding.
- Literal stock: **660,690**; normalized stock: **132,138**. All **2,469,000** role/replica/stage assignments are enumerated.
- Exact geometry: **390 new frames**, **3,752 changed projector charts**. New projector charts use at most 134 factors; the unchanged source has a 150-factor chart bound. The finite invoice conservatively pays a 787-factor normalizer.
- Literal five-stage paid children: **14,873,400**; rank mass **65,946,600**; deficit **122,400**. The normalized deficit is **24,480**.
- Bit coarse saving: `384380308527233/500000000000000000`.
- Two exact rational moment engines include the complete `10^-16` bad-class fallback. Three completed ordinary levels feed all **47 strict assembly constraints**; the next grid point is rejected.
- Selector calls: **389,017,013,400**. Full counted primitive coefficient: **25,350,779,320,984,001**, below `2^80`. The computed payload bound is 90 bits, below the retained 104-bit allowance.

The native finite invoice is recomputed from the binary word. Neither the stage selections nor this table supply its paid histogram. Changed endpoints are charged using `dim(final)-dim(initial)`; the final helper frame need not be FULL.

## Scope

This is a source-bound conditional finite construction under PR315's inherited all-size compiler, weighted charts, restored-row, selector, routing, prime-supply, precision/recovery, complex-symbolic and analytic-transfer interfaces. It is not a new unconditional integer-multiplication theorem, bit-side Lean proof, or runtime benchmark. PR315's unpinned local Lean run for its complex supplier is not rerun or claimed here. See `PROOF.md`, `NOTICE.md`, and the unchanged upstream documents in `vendor/pr315/`.
