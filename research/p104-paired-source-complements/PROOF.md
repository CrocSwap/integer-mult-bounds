# Source complements weighted by the actual integer flow

This extends [#8029's coordinate-moment proof](https://github.com/ToikY/integer-mult-bounds/blob/c3837013dd7e2c50f6c3065c8f99d52a33b617bb/research/p104-paired-delayed-cover/weighted/moment/PROOF.md) at the same physical binary carrier. It uses the primary [integer flow](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md) and its [ambient-cap generalization](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md). The upper and lower bounds below refer to physical, signed rank histograms at [#8027](https://github.com/CrocSwap/integer-mult-bounds/pull/8027). All logarithms are natural except where a base is written.

## Strict separation closer to the raw crossing

Write `v=768`, `J=15^v`, `K=16^v`, `m=134^v`, `H=299610000000000`, `C=0.003890115286593`, and `t=1−C`. Let `P_s` and `T_s` be the one-letter paid and productive masses at exponent `s`, using the complete rank multiplicities. A raw paid tuple has product rank `R`. Each `R>J` is split as `floor(R/J)` disjoint full slabs of rank `J` plus at most one remainder, by the inherited `credited_trim.py` contract. Productive tuples less than `K` become owned zero specializations. Retain the paid operations and all ordinary allocation, restoration and routing charges. The rank `K` is actually attained by 512 factors of rank 8 and 256 of rank 64. Both ranks occur in the authenticated productive law.

With `u=1/5`, put `α=P_t/T_t`, `γ=P_(t+u)/(15^u T_t)`, `δ=16^u T_(t−u)/T_t`, and `ρ=γ/α`. The normalized full paid mass plus discarded productive mass is bounded above by `α^v+2γ^v+δ^v<1`. The independent predecessor engine also certifies the trial using `1/(1+v(1−α))` in place of `α^v`. Let `Q` be the completed paid `t`-mass and `W` the retained productive `t`-mass. Then `P_t^v≤Q<W≤T_t^v`, and the split uplift is at most `2ρ^v P_t^v`. These statements use the signed 36-call word, including the caller contribution. The directed crossing engine gives a positive lower margin at `C`, strictly below the left endpoint of its checked raw bracket. An extra rank-one payment makes its upper margin negative.

## The actual complement measure

At integer top rank `n≥m`, write `n/m=K^(G+f)` with integer `G≥0` and `0≤f<1`. Use the integral flow's chronological parent path multiplier `ρ_path` and product of productive factors `c(a)`. The family of deepest classes, with one degree-zero point each, emits all `(G+1)`-tuples of completed paid labels and no other exits. Its unnormalized `t`-mass is `E=Q^(G+1)`. Let `S` be the unnormalized source `t`-mass, and `S_0` its root part. Cancellation at matched integral jobs gives `S≥E`. The same divisor normalizes all source and exit counts to the per-source-array recurrence.

For `A(n)=(1+log(n)/(h log 2))^p`, set `F(n)=n^t A(n)` on positive ranks and `F(0)=0`. For a source of rank `s≤n`, monotonicity of `A` and concavity of the power give

```
F(n)−F(n−s) ≥ A(n)·s^t · t(s/n)^C.
```

Let `η=t m^(−C)`. The dimensionless capacity to average in the actual source law is `(m s/n)^C`. This replaces the predecessor's pointwise lower bound of one.

### Root sources

A retained root index has `c(a)≥K^G`, and it exposes every target `k` with the same root-column multiplier and the full target multiplicity. Its capacity averaged over the productive `t`-law is at least

```
K^((1−f)C) · E_retained[(k/K)^C] ≥ 3.23 · K^((1−f)C).
```

The second inequality follows by conditioning the raw productive law on `k≥K`, which increases this increasing expectation. Before restriction it equals `(T_1/(16^C T_t))^v`.

There is also a bound on the root share. The retained root indices `a` range over exactly the multiset of sequences of `G` productive labels whose product is at most `K^(G+f)`, grouped by their commutative index. Their exact multiplicity is the multinomial count with the given physical target multiplicities. With `u_0=1/100`, Markov's inequality applied to the inverse product gives

```
S_0/S ≤ min(1, S_0/E)
      ≤ min(1, ((T_t/P_t)^v)^(G+1) · D^G · K^(u_0 f)),
D = (16^u_0 T_(t−u_0)/T_t)^v.
```

Conditioning on `k≥K` decreases the expectation of `(K/k)^u_0`, so the unconditioned raw law supplies `D` as an upper bound. The increase factor `(T_t/P_t)^v D` is strictly below one. The root share bound at `G=10,f=1` therefore also covers every larger height. At `G=0`, all sources are root sources.

### Deeper sources

Fix the parent prefix, the child index `b`, and target grade `k`. Set `U=n/(m ρ_path c(b))`. The parent index `b+e_k` was truncated precisely when `U<k`. Such a missing parent leaves exactly the available child target slots as sources, one group per paid position with rank `r≤U`. The Pascal allocation gives equal multiplicity for each paid position in that group, apart from the paid-position multiplicities already in the inventory. All source ranks have the common form `s=ρ_path c(b) k r`. Consequently the group's average capacity is

```
(k/U)^C · E_completed[r^C | r≤U].
```

Only nonempty groups need a bound. It is greater than 210 in all four regions below. Boundary equalities satisfy at least one of the stated adjacent tests. Write `q=log(U)/log(J)`.

- For `q≤0.35`, use `r≥1,k≥K`. Then `(k/U)^C≥(K/J^0.35)^C>233`.
- For `0.35≤q≤0.59`, at least `0.99` of the eligible completed mass has `r≥J^0.24`. The directed proof uses the anchor `[0.28,0.35]` for `log(R)/log(J)` under the raw tilt `0.45`.
- For `0.59≤q≤0.82`, at least `0.99` has `r≥J^0.47`. The corresponding anchor is `[0.49,0.59]` under raw tilt `0.8`. In both middle regions the factor from the good mass alone is at least `0.99 (K/J^0.35)^C>210`.
- For `q≥0.82`, the prefix contains all unsplit tuples below `J^0.82`. Their `r^C`-weighted mass is the raw rank mass at exponent `t+C=1`. A fresh `+0.1` Chernoff tilt bounds the discarded fraction under that law by `(P_1.1/(15^0.082 P_1))^v`. The denominator is bounded by the entire completed `Q`, including all uplift. Since `k/U>1`, the group's capacity is at least `(P_1/P_t)^v (1−(P_1.1/(15^0.082 P_1))^v)/(1+2ρ^v)>210`.

For the middle-region calculation, let `[a,b]` be the anchor, `l<a` the bad cut, `q_1<1` the region's upper endpoint and `ν<t` the raw tilt. Chebyshev's inequality at `ν` gives a positive lower anchor probability `p_ν` using the exact one-letter mean and variance divided by `v`. Under the actual tilt `t`, the anchor has relative mass at least `M=(P_ν/P_t)^v J^((t−ν)a) p_ν`. The ratio of raw mass below `J^l` to that anchor is at most `J^((t−ν)(l−a))/p_ν`. Every high parent emits only one possible eligible sub-`J` remainder. Each such remainder has `t`-weight at most `(J^q_1/R)^t` times its parent's weight. Using `Pr_t(R>J)≤ρ^v`, the ratio of **all** eligible split remainder mass to the anchor is at most `ρ^v J^(t(q_1−1))/M`. The sum of these two ratios is strictly below `0.01` in each region. This argument uses the paid label's actual split geometry, including its full `t`-weight at a truncated source.

For `G>0`, take a lower root capacity `a_0`, a deeper capacity 210, and the upper bound `σ` on `S_0/S`. The capacity per unit total source mass is at least `210−max(0,210−a_0)σ`. Multiplying by `η` and then using `S≥E` gives a certified budget in units of exit `t`-mass. At `G=0` apply the root capacity by itself.

## Exit moments and the all-size induction

One raw letter has log contribution `Y=log(r)/log(J)` under the actual paid `t`-law. The exponential generating polynomial of its first `p` moments has coefficient `E[Y^j]/j!`. Raising that polynomial to power `v` gives the raw tuple coefficients through degree `p`. The verifier uses positive truncated convolution and checks against `A B'=v B A'` for `B=A^v`. Every degree `1≤j≤p` of the completed log-rank moment is at most the raw moment plus `2ρ^v`. Indeed, if `R>J`, its original normalized log exceeds 1 and every child's log is at most 1, so the moment numerator grows at most by the **positive** split uplift. The completed denominator grows weakly. The zeroth moment is exactly 1.

For the average of `g+1` completed labels, power the resulting upper moment polynomial to `g+1` and rescale its degree-`p` coefficient. The checker computes a separate directed norm `ℓ_g` for each `0≤g≤10`. For more labels the norm of the average is no greater than `ℓ_10`: the full average is the mean of its subaverages with eleven entries, and Jensen's inequality bounds its `p`th moment by the common eleven-entry moment. All independence here concerns weighted products of exact finite paid labels or raw tensor coordinates.

Put `a=h log 2/log J`, `b=(h log 2+log m)/log J`, and `β=log K/log J`. Minkowski's inequality at height `G` bounds the exit cost divided by `A(n)E` by

```
[(a+(G+1) ℓ_G)/(b+β(G+f))]^p.
```

Use `p=23,h=1300`. For `G=0,...,9`, cover `[0,1)` by 32 equal rational cells. In each cell use its lower endpoint in the exit denominator and its upper endpoint for both the lower root capacity and upper root share. All 320 strict comparisons pass. The smallest relative margin occurs in height 7, last cell, where the exit bound is below `1.386e−6` and the complement budget exceeds `1.420e−6`. For `G≥10` use `f=0` in the exit denominator, `ℓ_10` in the numerator, `f=1` in the root factor, and the uniform root-share upper at height 10. The fractional-linear expression attains its supremum at height 10 or infinity. Both strict comparisons pass. The infinite-height exit upper is below `5.582e−5`, with complement capacity greater than `9.235e−5`. Without the averaged source estimate the old per-source `η` is below `4.399e−7`, and fails the corresponding infinite-height test.

The ordinary base follows from `(1+log_2(m)/h)^p>m^C` by the concavity of `log(1+x/h)` on `0≤x≤log_2(m)`. The base at rank one is equality. Zero complements are covered by `F(0)=0`. Every recursive rank is smaller than `n`, and the weighted source budget dominates the normalized sum of exit costs. Strong integer induction proves the required uniform majorant for every top rank.

## Terminal debit and complete signed price

At the fixed binary `H`, exact integer arithmetic gives `h^23·2^868≤(H+h)^23<h^23·2^869`. The inequality remains strict at higher log-widths for debit `869/H`: its exponential growth rate exceeds the logarithmic derivative because `869(H+h)>2H·23` and `log 2>1/2`. The original same-prime fallback satisfies the #8029 bound with separate debit `1/(H·2^38)` for the same stock and fixed physical catalogue. Both suppliers use the same literal operators, setup and precision controls as the paired construction. None of the shape or tensor parameters is enlarged to obtain the higher trial.

The covered BIT value is `C−869/H−1/(H·2^38)`. Each of the four restored ordinary stages funds `(249·covered+previous)/250` and charges one additional tick after flooring to `10^−15`. The outer gate deducts eight signed ticks at `10^−14`, with seven ticks from claim to test. These are evaluated as exact fractions and separately by the signed supplier engine. The signed replay prices all 36 BIT and 48 rational calls, checks both source crossings and rejects corrupted paid ranks and invalid BIT caps. This is a higher conditional complete application for the pinned construction with the same five premises. The raw fixed-word BIT upper endpoint still bounds the scope of a proof-only extension based on a strictly separated trial of this raw law.
