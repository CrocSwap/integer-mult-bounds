# Exact 35-digit endpoint extension of the T740 release

This scoped package tests one exact question: does the unchanged T740 six-skip construction admit the next 35-decimal-grid endpoint above the open PR #3115 claim? The latest public point used here is the exact claim `0.001729737950064278551242895823 - 10^-52 - 10^-76` in [PR #3115](https://github.com/CrocSwap/integer-mult-bounds/pull/3115), head `400bc83669f86917f69b6249cd0356d3a913293c`.

For profile `{1:16376940, 2:4741920, 3:1594737, 4:719280, 5:137085, 8:53280, 48:281903}` at `T=740`, the credited root engine brackets the root in

```text
[1729737950064278551242895823817348847577393 / 10^45,
 864868975032139275621447911908674423788697 / (5*10^44)].
```

The next candidate endpoint is the lower 35-digit grid point

```text
C35 = 86486897503213927562144791190867 / (5*10^34)
    = 0.00172973795006427855124289582381734.
κ35 = C35 - 10^-57 - 10^-81.
```

Both retained exact rational moment engines must show `M(C35)<1<M(C35+10^-35)`, and both must reject the unpaid rank-1 and rank-48 child controls. Relative to PR #3115's `C30 - 10^-52 - 10^-76`, the exact κ gain is `40867/(5*10^34) + 10^-52 + 10^-76 - 10^-57 - 10^-81`, slightly above `8.1734e-31`. This is a finer endpoint for the same paid mechanism; it does not claim a structural improvement or new supplier mechanism.

The κ claim is admissible only if the complete unmodified T740 baseline and the complete changed strict supplier/outer release pass. The replay must retain every inherited admission predicate, all 63 positive outer rows, all 17 rejection controls, and the authenticated identical native receipt. A root-only check is not a release.

## Open next questions

- Can the weighted diagonal rank-batching screen in [open PR #3116](https://github.com/CrocSwap/integer-mult-bounds/pull/3116) be turned into a fully charged endpoint with a materially higher κ? Its local ceiling is not a constructed claim; the first step is to exhibit and invoice a physical endpoint, including the separate bit supplier.
- Which changed paid producer/consumer boundary can lower the local profile enough to exceed the fixed-word ceiling materially? Start with the live normal-7 B-phase/later-A handoff; price the full supplier bill before expanding the construction.
