# Splitting one arbitrary helper return on the #7682 banked word

Under the five assumptions listed below, the signed sixteen-call construction gives **κ ≥ 0.0037266288**. This is **0.0000005264099 above the directed upper bound 0.0037261023901** for the complete #7682 invoice. The new raw crossing lies between 0.0037266288769 and 0.0037266288770. The independently directed check gives a positive target-minus-paid margin exceeding 0.00002721547 at the claimed lower bound. [Signed caller and compiler](CALLER.md) · [Independent interval check](price_crosscheck.py)

The parent is the 6,142-edge graph from PR #7682 at `1b4a4d6f9370b8c93b3f769a6229a9111ef3940e`. Its decompressed SHA-256 is `1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150`. The changed word uses the same sixteen chronological native invocations. It changes one rank-nine helper return per invocation into two independently owned returns. The old owner goes from chart 3 to 595. A fresh input at 595 goes to chart 127.

The canonical changed graph has SHA-256 `d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b`. Of the paid source forms, 340 change through the boundary input transformation and ten change through the suffix injections. Two of the 340, at keys 94756 and 97405, belong to the predecessor's fifteen pivot certificates. The full rational replay checks their values under the new boundary transformation, checks the surviving observations in all fifteen certificates, and verifies independence from the fresh input. It also executes the separately constructed adjoint operator. [Canonical constructor](construct.py) · [Exact operator checks](operator.py)

## The arbitrary-input identity

Work in normalized coordinates on the 615 ordinary helper roles with common entrance chart 3 and common exit chart 127. Write $x$ for their vector. Each coordinate can itself be a full array. On the parent, all 615 outputs equal their own inputs in these coordinates. The 400 main roles and the two separately accounted helpers 325 and 1087 lie outside the change.

Let `r = 281`. On the parent, eight stored arrivals at chart 595 give a linear functional `ell(x)`. Ten later paid departures from the same chart have rational injection coefficients. Adding those coefficients times one arbitrary array `t` changes the complete old output vector by `v t`. The extension of `v` is zero on all roles outside the group. The exact coefficients give `ell(v) = 1` and `ell[r] = -1/2`. The prefix arrivals have all been produced by schedule position 995. The first changed departure is at position 1473. No injection can affect a prefix read. The field names and coefficients are in the [edit witness](EDIT.json).

At chart 3 denote the external inputs by `u`. Express the internal old inputs in that common chart by

```text
x[j] = u[j] + v[j] u[r]                         for j different from r
x[r] = v[r] u[r] - sum(ell[j] u[j] / ell[r] for j different from r).
```

Taking `ell` gives exactly `u[r]`. The inverse recovers `u[j] = x[j] - v[j] ell(x)` for every other role. Thus this encoding is invertible for arbitrary arrays, including when `v[r] = 0`. No zero input to the old helper group is required.

Return the eight-arrival combination to the old owner at chart 595. Supply an independently initialized external array `g` to the new owner 1501 at that chart. In the ten designated source rows add the indicated multiple of `g - ell(x)`, using the unchanged prefix values. Linearity gives the old exit fields

```text
y = x + v (g - u[r]).
```

Consequently `ell(y) = g`, and `y[j] - v[j] ell(y) = u[j]` for every other helper. All other public roles see the original result. This proves the two independent returns, preserves the later reads that determine the main result, and identifies the early output for arbitrary values of every other field. Same-chart linear combinations are folded into individual bank rows and charged there. The finite graph determines which stored copies they read and when. The early output has its own backing through the enclosing caller's return.

## Physical meaning and productive price

For native chart $U$, a normalized array $z$ represents the physical field $T_U z$. The two complete helper maps are $T_{595}T_3^{-1}$ and $T_{127}T_{595}^{-1}$. The rank differences are 1 and 8. The replaced map $T_{127}T_3^{-1}$ has rank 9. The ordered intermediate basis is `[52]`. Both new ordered maps already occur among the parent’s paid native edges. The signed main wrappers use forward native invocations. Their action on main inputs and outputs leaves the independent helper fields alone. The whole-job adapters, spectators, complete native phases and both entrance and exit conversions belong to the physical application.

Write $H_r(k)=r^{1-k}$ for the weight of a rank-$r$ recursive job in the raw signed invoice. All existing paid edges remain. For the sixteen calls the increase in target weight is exactly

```text
16 (H_1(k) + H_8(k) - H_9(k)).
```

The linear rank mass at $k=0$ stays fixed. For $0<k<1$, strict concavity gives positive credit. Certifying a particular $k$ also requires directed margins against the complete caller, its funded compiler and all outer inequalities. An extra charge of one rank-one job already exceeds the projected surplus at the round's initial test point. The unchanged number of paid jobs therefore matters to the claim.

## Complete application

The actual signed caller retains 101,824 paid placements and has 21,168 productive targets, comprising 3,536 root fields and 17,632 fresh stage-specific helpers. All 12,800 main phase contacts are checked. The selected BIT floor is 0.00376669. Both compiler runs use carrier power 1,920, height 14,558,800,000,000,000,000 and written log power 2,287. The 54 strict and four functional predicates pass on the changed count, with minimum margin $10^{-15}$. The external return adds one native owner in each call, including its two conversions and both ordinary maps. [Literal signed application](caller.py) · [Directed funding and outer checks](price.py)

The physical test checks all 8,738,317 nonzero basis products on the child, including 166,789 whose reduced coefficient denominator contains seven. A safe native scaling uses the odd factor 2,083,725 and 18 binary fractional bits. It covers each scalar product and addition before any cancellation, with native scale removed on complete native return. Removing the full factor of $7^3$ produces a nonzero remainder at the actual coefficient $-40/21$. The complete 16-stage bound allows 336 binary debt bits and 588 magnitude bits per unfinished context, giving $c=1176$ and a 14,083-bit depth guard at the checked height. A native invocation uses 9,151 numeric homes and four independent guarded streams. The staged caller includes 55,136 complete-array conversions. [Common-root, movement and backing proof](PHYSICAL.md) · [Executable ordinary checks](physical.py)

The native phase checker verifies the old and new ordered maps and checks both complete directions on all 512 columns. A distinct physical replay executes all 6,142 paid operations in four cases, two independently seeded input arrays at each of two primes. A wrong sign at slot 102698 alters 83 output roles including fresh role 1501, while preserving the earlier role 281 return. A phase error at prefix slot 95743 instead changes 46 roles, including 281. An independent cut check writes the early public output on its actual owner and confirms that no later operation needs its old input home. [Exact phases](native.py) · [Physical execution](dense.py) · [Independent cut and price review](review/README.md)

## Scope and provenance

The comparison uses the same selected framework assumptions for native operations at all column multiplicities, owned allocation and erasure, uniform compiler closure, fixed-tape movement and precision, and analytic recovery. The checked finite graph, caller and ordinary resource obligations specialize them to this word. The selected maintainer review sets out the common-root arithmetic, finite-template substitution and final recovery. The separate review of #5599 gives the earlier arbitrary-input split argument and the all-forward treatment of signed main wrappers. [Selected application review](../../docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md) · [Earlier split review](../../docs/research/pr-intake-evidence/pr5599-completion/PROOF-REVIEW.md)

Ali Romman supplied the helper-subspace mechanism and the fifteen banked pivots. SYLforge and DreamingOfClouds supplied the preceding caller and native word. The specific chart 595 cut, its exact source and suffix coefficients, its materialized application on the #7682 graph and its complete comparison are this contribution. See the [attribution notice](NOTICE) for the inherited tools and construction.
