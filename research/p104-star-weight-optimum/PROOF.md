# Exact optimum of the weighted star program on P104

## 0. Setting and cited premises

Let `V` be the 104-port set P104 of [vector port systems], a set of 104 vectors of
`F_2^9` of weight `3 mod 4`; two distinct ports are adjacent when their dot
product is `1` and orthogonal when it is `0`.

Fix an orthogonal 8-set `K` of `V` (eight pairwise orthogonal ports) and put
`v = 1 + sum(K)`, the all-ones vector plus the sum of `K` in `F_2^9`. Then
`dot(v, c) = 0` for `c` in `K` and `dot(v, v) = 1`, so `K` together with `v` is
an orthonormal basis of `F_2^9`. Every port `t` is therefore

```text
t = sum_{c in A(t)} c + eps(t) v,     A(t) = {c in K : dot(t,c) = 1},  eps(t) = dot(t,v),
```

with `|A(t)| + eps(t) = 1` mod 2. A port outside `K` is an **edge port** if
`|A(t)| = 2`. Distinct edge ports have distinct pairs `A(t)`, so the **edge
graph** `Gamma(K)`, with vertex set `K` and one edge per edge port, is simple.
Write `E` for the number of edge ports, `d_c` for the degree of `c` in
`Gamma(K)`, and `m = |E(Gamma(K))| = E` (simplicity).

These facts, and the type census used in Lemma 4, are Theorem 3 and its
structural section in [the predecessor package](../p104-port-window-haemers/THEOREM.md)
(#6933, DreamingOfClouds). They are cited premises. `verify.py` recomputes the
census so that the certificate below is self-contained, but the mathematics of
this package begins at Lemma 1.

**Theorem 3 of #6933 (cited).** Let `a_c >= 0` be weights on `K` with

```text
(W1)  a_c + a_d <= 1                     for every edge cd of Gamma(K),
(W2)  a_c (d_c - 2) <= 2                 for every c in K.
```

Put

```text
mu  = sum_{c in K} (1 + a_c),
rho = sum_{cd in E(Gamma(K))} (1 - a_c - a_d).
```

Then for every field `F`, every `k` and every `k`-block pattern `B` on `V`,
writing `rank B = 8k + j`,

```text
j/k >= (E - mu) / (mu + rho).
```

The right-hand side is a function `f(a)`. #6933 evaluates `f` at weights from a
grid and states that it makes no claim that they are optimal. The theorem below
computes the exact supremum of `f` over the whole admissible set, and its
equality case.

## 1. Two identities

**Lemma 1.** With `A = sum_c a_c` and `D = sum_c d_c a_c`,

```text
mu = 8 + A,          rho = E - D,          mu + rho = 8 + A + E - D.
```

*Proof.* `mu = sum_c (1 + a_c) = 8 + A`. Every edge of `Gamma(K)` contributes
`1 - a_c - a_d`, so summing over the `E` edges counts each `a_c` exactly `d_c`
times: `rho = E - sum_c d_c a_c = E - D`. ∎

Note `mu + rho = mu + rho >= 8 > 0`, so `f` is defined and no sign case arises.

**Lemma 2.** `f(a) <= 5/6` if and only if `5D - 11A <= 88 - E`.

*Proof.* Since `mu + rho > 0`,

```text
f <= 5/6  <=>  6 (E - 8 - A) <= 5 (8 + A + E - D)
          <=>  6E - 48 - 6A <= 40 + 5A + 5E - 5D
          <=>  E - 88 <= 11A - 5D
          <=>  5D - 11A <= 88 - E.                                  ∎
```

## 2. The multiplier certificate

**Lemma 3.** Let `lambda = 14/5` and, for each `c` in `K`,

```text
mu_c = ( (11/5) d_c - 11 ) / (d_c - 2).
```

For `d_c >= 5` the number `mu_c` is nonnegative, and for every `c`

```text
d_c lambda + mu_c (d_c - 2) = 5 d_c - 11.        (identity)
```

Consequently, for every `a` satisfying (W1) and (W2),

```text
5D - 11A <= (14/5) E + 2 sum_c mu_c.
```

*Proof.* `d_c lambda + mu_c(d_c - 2) = (14/5) d_c + (11/5) d_c - 11 = 5 d_c - 11`.
Then

```text
5D - 11A = sum_c (5 d_c - 11) a_c
         = sum_c a_c [ d_c lambda + mu_c (d_c - 2) ]
         = lambda sum_{cd in E(Gamma)} (a_c + a_d) + sum_c mu_c (d_c - 2) a_c
         <= lambda E + 2 sum_c mu_c,
```

because every edge contributes `a_c + a_d` once, (W1) bounds each of the `E`
edge terms by `1`, and (W2) bounds each vertex term by `2 mu_c >= 0`. ∎

**Lemma 4 (cost on the three P104 types).** The quantity

```text
(14/5) E + 2 sum_c mu_c  =  (19/5) E + 2 sum_c mu_c
```

satisfies

| type `(E; d_c)` | `sum_c mu_c` | cost | `88 - E` |
| --- | ---: | ---: | ---: |
| `(22; 5,5,5,5,6,6,6,6)` | `11/5` | `88` | `66` |
| `(22; 5,5,5,5,5,6,6,7)` | `99/50` | `4378/50` | `66` |
| `(21; 5,5,5,5,5,5,6,6)` | `11/10` | `82` | `67` |

So in every case `(14/5)E + 2 sum_c mu_c <= 88 - E`.

*Proof.* `mu_5 = ((11/5)·5 - 11)/3 = 0`, `mu_6 = (66/5 - 11)/4 = 11/20`, and
`mu_7 = (77/5 - 11)/5 = 22/25`. Sum over the multiplicities of each type and add
`(14/5)E = (14/5)·22` or `(14/5)·21`. The first row gives
`308/5 + 2·11/5 = 330/5 = 66`; the second `308/5 + 2·99/50 = 4378/50 <= 66`; the
third `294/5 + 2·11/10 = 82 <= 67`. The three types are the complete census of
orthogonal 8-sets of P104. ∎

## 3. The theorem

**Theorem.** For every orthogonal 8-set `K` of P104 and every weight vector `a`
satisfying (W1) and (W2),

```text
f(a) = (E - mu)/(mu + rho) <= 5/6.
```

Moreover `f(a) = 5/6` holds exactly when `K` has type `(22; 5,5,5,5,6,6,6,6)`
and `a_c = 1/2` for every `c` in `K`.

*Proof.* Lemma 3 and Lemma 4 give `5D - 11A <= 88 - E`, which is `f(a) <= 5/6`
by Lemma 2. This proves the bound.

For the equality case, `f(a) = 5/6` forces equality in every link of the chain.

1. *Cost equality.* `(14/5)E + 2 sum_c mu_c = 88 - E`. By Lemma 4 the cost is
   `88` only for `E = 22` with `sum_c mu_c = 11/5`. Since `mu_c = 0` at degree 5,
   `mu_c = 11/20` at degree 6 and `mu_c = 22/25` at degree 7, the only multiset of
   eight degrees with `sum_c mu_c = 11/5 = 4 · 11/20` is `(5,5,5,5,6,6,6,6)`.
2. *Vertex equalities.* `lambda = 14/5 > 0`, so every one of the `E` edge terms
   must be tight: `a_c + a_d = 1` for every edge `cd`. And `mu_c > 0` at every
   degree-6 vertex, so `(d_c - 2) a_c = 2`, i.e. `a_c = 1/2` at every degree-6
   vertex.
3. *Degree 5.* A degree-5 vertex has five neighbours but only three other
   degree-5 vertices, so it has a neighbour `d` with `d_d = 6`. Then
   `a_c = 1 - a_d = 1/2`.

Conversely, `a_c = 1/2` for all `c` is admissible: (W1) gives `1/2 + 1/2 = 1`, and
(W2) gives `(1/2)·3 = 3/2 <= 2` at degree 5 and `(1/2)·4 = 2 <= 2` at degree 6.
For the principal type it yields `mu = 8 + 4 = 12`, `rho = 22 - 22 = 0`, hence
`f = 10/12 = 5/6`. ∎

## 4. Corollaries

**Corollary 1.** No choice of weights satisfying (W1) and (W2) makes Theorem 3 of
#6933 exceed `j/k >= 5/6` on any orthogonal 8-set of P104. Since the bound
`rank B >= 53k/6` is exactly this inequality, no reweighting raises the floor
`53/6`. The maximizer is unique, so the weight program has no second regime to
explore.

**Corollary 2.** Any strict improvement of the star route must change an
inequality that is not a weight: a sharper edge or star inequality. This is what
[#7114](https://github.com/CrocSwap/integer-mult-bounds/pull/7114) does with
`k <= g_T(c) + g_T(d) + min(Y_c, Y_d)`, reaching `j >= k` and the floor `9`. The
present theorem is the post-mortem on the weight program; it does not compete
with that value and does not bound `w(P104; F)`.

## 5. What is not claimed

The rank inequality of #6933 is not re-derived, only cited. The type census is
recomputed as an input to Lemma 4 but is #6933's result. No statement is made
about P112 or P120, where the certificate's cost budget already fails at the
edge count. No field, block pattern, decoder, native word, supplier, kappa or
selected-frontier change is claimed. No human or proof-kernel review.
