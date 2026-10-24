# A truncated-source envelope for the selected nested compiler

**Author-checked scoped proof; no new κ or physical admission.** For the unchanged selected #4470 product/completion/splitting rule and #4436 nested widths, let `H=64215200000000`, `N=2^H` and `K=ceil(log2 B_N)/H`. This package improves [Sagar Thakrar's #5026](https://github.com/CrocSwap/integer-mult-bounds/pull/5026) upper bound from `K/N < 3.639` to **`K/N < 3.070`**. Its inherited lower bound `K/N > 2.943` is unchanged, so the conditional bracket has ratio below `1.044`. The selected conditional κ remains `60403/20000000`.

The new ingredient is an eligibility-sensitive source census and a first-moment bound on its root and nonroot terms. It changes no batching, call, completion, split, complement or physical tariff. It does not optimize the outer cutoff. The general inequality is uniform at every integer rank `n>=M`; the numerical accumulated result applies at the selected `N` without constructing that integer.

## Source-bound definitions

Use the positive productive multiplicities `T_k`, paid multiplicities `P_r`, ambient rank `M=max k`, productive floor `L=min k>=2`, and `max r<M`. Write `W=sum T_k`, `T1=sum k T_k`, `P1=sum r P_r`, `x=n/M`, and `G=max{g:M L^g<=n}`. Define `c(a)=product k^a_k` and `u(a)=multinomial(|a|;a) product T_k^a_k`. A chronological paid path `sigma` has multiplier `rho_sigma`; repetitions are separate path positions, not rank mass.

The pinned #4436 implementation instantiates `u(a)` units at depth `d` precisely when `|a|=G-d` and `rho_sigma c(a)<=x`. Each unit has `T_k` target slots of rank `rho_sigma c(a)k`. Its Pascal matching rule consumes every child demand when the parent point exists; when it does not, the child slot receives a distinct new top source. The target-slot label consists of the chronological path, unit instance and target position. These labels remain distinct even when their ranks coincide. Aggregating labels by rank sums positive integer counts and never aliases source arrays.

## Exact truncated root and nonroot census

The root count is exactly

```text
R_n = W sum_{|a|=G, c(a)<=x} u(a).
```

For a nonroot depth `d=1,...,G`, let `sigma` be a paid path of length `d-1`, and let `r` be its next chronological paid position. The source count is exactly

```text
D_(n,d) = sum_sigma sum_r sum_{|a|=G-d} sum_k
          u(a) T_k [rho_sigma r c(a)<=x<rho_sigma c(a)k].
S_n = R_n + sum_(d=1..G) D_(n,d).
```

Here `sum_r` includes each paid position, with its full multiplicity. The first indicator is the actual child-unit eligibility condition. The second is the absence of the parent point `a+e_k`. If that point exists, the complete Pascal identity says its supply is `u(a+e_k)`, at least the eligible child demand, so no new source is created. If it is absent, every eligible demanded slot is a source. This proves the formula without assuming full layers or monotonicity.

Every counted source rank `s` satisfies `x<s<=n`. At the root, `s=c(a)k>=L^(G+1)>x`, and eligibility gives `s<=M c(a)<=n`. At a nonroot source, absence gives `rho_sigma c(a)k>x`; multiplying by `r>=1` gives `s=r rho_sigma c(a)k>x`, while child eligibility and `k<=M` give `s<=n`. The interval is strict at its lower end. This is the useful truncation constraint, not an additional assumed rule.

## Uniform weighted envelope, including every nonroot layer

Since each source has `s>x`, its unit count satisfies `1<s/x`. Sum over the exact census, then enlarge each eligible set only *after* introducing its rank weight. The full rank-weight sum of the root target slots is `T1^(G+1)`. At depth `d`, summing paid paths contributes `P1^d`, the remaining productive word contributes `T1^(G-d)`, and the final target slot contributes `T1`. Consequently, uniformly for every `n>=M`,

```text
S_n < (T1/x) sum_(d=0..G) P1^d T1^(G-d).                   (1)
```

This bound counts sources, not paid rank mass as paid calls. In particular, if `P1<=T1`,

```text
S_n < (G+1) T1^(G+1)/x
    <= (G+1) T1 (T1/L)^G.                                (2)
```

The second step uses `x>=L^G`. The old untruncated count scales with `(W+Q+1)^G`, where `Q` is paid call count; (2) instead scales with `(T1/L)^G`. Both root and missing-parent terms are included. No exact source count or height monotonicity is assumed, except the elementary monotonicity of `G(n)` itself.

## Fully charged selected application

The retained selected invoice gives raw productive count `W0=10928`, productive rank mass `T10=239886`, paid rank mass `P10=239134`, and ambient rank `145`. The fixed product power is `v=1024`, productive completion floor `L=21^v`, and paid split cutoff `J=20^v`. If `D` is the sum of all completion ranks, chronological product, completion and splitting give exactly

```text
T1 = T10^v + D,       P1 = P10^v + D,
0 <= D <= W0^v L,    T1-P1 = T10^v-P10^v > 0.
```

Each completion is paid on disjoint coordinates of its target, and splitting preserves its full rank mass. Thus `P1<T1<=U`, where `U=239886^1024+10928^1024*21^1024`. The condition needed by (2) is proved from the charged invoice, not inferred from a favorable uncharged profile. There is no need to materialize the product histogram.

Use the same exact integer height upper bound as #5026:

```text
h = floor((H-(bit_length(M)-1))/(bit_length(L)-1))
  = 14279564152,                 M=145^1024.
```

For every `M<=n<=N`, `G(n)<=h`. Since `U/L>=W>=1`, (2) implies

```text
log2 S_n < log2(h+1) + log2 U + h log2(U/L)
         < bit_length(h+1) + bit_length(U)
           + h (bit_length(U)-(bit_length(L)-1))
         = X = 197115103572543.
```

Only integers with tens of thousands of bits occur in this calculation. The previous `X` was `233670787813430`. Nested widths satisfy `B_n=B_(n-1)S_n` above the base and `B_n=1` below it, hence `log2 B_N < N X`. Because `NX` is an integer, `ceil(log2 B_N)<=NX`. Finally the exact comparison `1000X < 3070H` proves `K/N<3070/1000`. This upper sum does not replace `S_n` by a monotone interpolation. Every complement and exit batch continues using the original nested divisible width; complements are part of the program but create no extra factor in its defining `B_n=B_(n-1)S_n` recurrence.

## Discriminating finite fixtures

The actual selected invoice at reduced product power `v=1`, after the same completion and splitting, has these independently computed root and nonroot counts:

| n | G | Root | Nonroot | Total |
| ---: | ---: | ---: | ---: | ---: |
| 3044 | 0 | 10928 | 0 | 10928 |
| 3045 | 1 | 85150976 | 243240704 | 328391680 |
| 3046 | 1 | 85150976 | 243240704 | 328391680 |
| 63944 | 1 | 119421184 | 0 | 119421184 |
| 63945 | 2 | 663496404992 | 7221750536448 | 7885246941440 |
| 63946 | 2 | 663496404992 | 7221750536448 | 7885246941440 |

At `n=3045`, one missing-parent source has `d=1`, parent multiplier `1`, paid rank `20`, child column `1`, target rank `145`, source rank `2900` and multiplicity `1254400`. The child is eligible because `145*20<=3045`, but the parent point is absent because `145*145>3045`. Thus a root-only bound misses actual sources.

Inside the same height-one slab, increasing `n` from `3624` to `3625` increases the root count from `85150976` to `90046720` but reduces nonroot demand from `243240704` to `208492032`. The total falls from `328391680` to `298538752`. This directly rejects monotonicity of `S_n`.

The verifier independently computes weighted ordered-word sums and compares the entire source-rank spectrum with the pinned multivariate Pascal implementation on all six selected fixtures. Twelve tiny literal chronological replays also agree, including a paid/target overlap control. Distinct chronological copies are retained through multiplicities; no production product or huge-rank word is expanded. Six semantic controls reject omitted eligibility, omitted nonroot demand, source monotonicity, rank-mass/call confusion, omitted paid completion and omitted source complements. They use explicit exceptions and run under `-O`.

## Reproduction and evidence boundary

Python 3.12, standard library only, from repository root:

```sh
python3.12 -I -B research/selected-truncated-source-envelope/verify.py
python3.12 -I -O -B research/selected-truncated-source-envelope/verify.py
python3.12 scripts/research_package.py --package research/selected-truncated-source-envelope
```

Source spectra are compared in full during replay and retained as deterministic SHA256 receipts. The numerical and finite receipt is [RESULT.json](RESULT.json). Immutable inputs, hashes, original paths and commits are in [VENDOR.json](VENDOR.json) and [SOURCES.json](SOURCES.json). Pending #5026's exact relevant README is retained, as are the selected invoice/proof and #4436 flow implementation/proof. Direct verification is Git-free. `SOURCES.json` live-input pins resolve to the retained bytes in this contribution's own history; `VENDOR.json` separately records their original heads and paths, so a cached pending-predecessor Git object is not required. Provenance and source-history checks are separate from mathematical validation. On macOS arm64 with Python 3.12, registered normal and optimized replay passed in under one second, and a Git-free copied package passed under `-O`. Altering a retained source or the result receipt caused rejection. All package checks are author-checked; independent review and proof-kernel validation are not claimed.

This is a uniform source-count proof under the unchanged compiler and native hypotheses, supported by finite calibrations. It is not an emitted compiler, minimal width, physical row-depth admission, optimal coefficient, new outer cutoff, new κ, or a proof of the multiplication theorem. Native all-column, owned storage, routing, whole-job adapters, precision/tape, analytic, prime and recovery obligations remain inherited and unrun.

## Open next questions

1. Can a fractional moment or a sharper eligible-boundary law further reduce the interval between the inherited `2.943` lower and new `3.070` upper coefficients? First derive a uniform moment bound preserving the same nonroot absence indicator and all completion mass; a new histogram census or outer-root calculation alone does not answer it. No further expansion is needed for the present result.
2. Physical realization remains a separate handoff: bind this permitted mathematical width to the actual fixed-program stock/ownership/routing interface and its complete tariff. This package does not provide that implementation.

## Attribution

Prepared by JoyboyBrian with substantial OpenAI Codex (GPT-6 Astra) assistance. New material is Apache-2.0. Credit Sagar Thakrar (#5026 and its explicit truncated-source handoff); James Reed/jwr404 (#4972/#4970); Mark/Matarener (#4612 and stock audit); zxv (#4436 nested widths and flow, strictification and retained stock/native sources); Cinna Davis and zxv (#4440/#4470); Jacob Alan Sussman (Theorem 1G multinomial lockstep construction); Ryanson Jonathan (#4476); and mihir-s-05 (#4507/#4519). Retained files preserve their original notices and predecessor attribution. The canonical investigation is [Discussion #5061](https://github.com/CrocSwap/integer-mult-bounds/discussions/5061). Source/publication provenance is not scientific acceptance.
