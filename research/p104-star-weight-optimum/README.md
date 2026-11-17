# The weighted star program of #6933 is exactly optimal at 5/6 on P104

**Claim type:** scoped written proof with an exact rational certificate.
**No kappa, no word, no supplier.** No selected-frontier change.

This package answers the optimization question that
[#6933](https://github.com/CrocSwap/integer-mult-bounds/pull/6933) leaves open.
Its Theorem 3 proves, for weights `a` on an orthogonal 8-set `K` of P104
satisfying

```text
(W1)  a_c + a_d <= 1          for every edge cd of the edge graph Gamma(K),
(W2)  a_c (d_c - 2) <= 2      for every c in K,
```

the rank bound `j/k >= (E - mu)/(mu + rho)` with `mu = sum_c (1 + a_c)` and
`rho = sum_edges (1 - a_c - a_d)`. #6933 evaluates this at weights taken from a
grid and states that it makes no claim that they are optimal. It is not an
audit of that theorem: the theorem, its constraints and its type census are
cited premises. The new statement is the exact optimum of the weight program and
its equality case.

## Result

Write `f(a) = (E - mu)/(mu + rho)`. For P104 and every orthogonal 8-set `K`:

```text
for every admissible a:                 f(a) <= 5/6,
and 5/6 is attained, exactly when       K has type (E; d) = (22; 5,5,5,5,6,6,6,6)
                                        and a_c = 1/2 for every c in K.
```

The proof is a multiplier identity, not a search. With `w_c = 5 d_c - 11`, the
uniform multiplier `14/5` on every edge and `mu_c = ((11/5) d_c - 11)/(d_c - 2)`
on each vertex, the coefficient identity

```text
sum_{e ni c} 14/5 + mu_c (d_c - 2) = 5 d_c - 11
```

holds exactly at every vertex, so

```text
sum_c (5 d_c - 11) a_c <= (14/5) E + 2 sum_c mu_c <= 88 - E,
```

which is precisely `f(a) <= 5/6`. Equality forces every edge of `Gamma(K)` tight,
every degree-6 cap tight, `E = 22`, and no degree-7 vertex. Then `a_c = 1/2` at
degree 6, and every degree-5 vertex has a degree-6 neighbour (it has five
neighbours but only three other degree-5 vertices), so `a_c = 1/2` there too.

Two consequences matter for the next contributor.

1. **No reweighting can raise `53/6`.** The star inequality of #6933 cannot be
   improved by choosing better weights, on any orthogonal 8-set of P104: `5/6`
   is its exact ceiling, and the maximizer is rigid.
2. **The floor 9 needs a different inequality, which is what #7114 found.** That
   PR replaces the edge inequality by `k <= g_T(c) + g_T(d) + min(Y_c, Y_d)` and
   reaches `j >= k` with no weights. The present result explains why the weight
   route was closed: it is a post-mortem on the weight program, not a competing
   value. Where #7114 is available it supersedes the value 9; where the weight
   program is reused, this fixes its ceiling.

## Evidence

`verify.py` recomputes everything from the P104 port vectors, with exact rational
arithmetic and no floating point decisions:

- the 104 ports, the 1728 orthogonal 8-sets, the orthonormal basis `K + v` with
  `v` the all-ones vector plus `sum(K)`, the parity identity `|A(t)| + eps = 1`,
  and simplicity of `Gamma(K)` (`960 / 384 / 384` sets of the three types);
- the three recorded values `5/6`, `101/126`, `3/4` at #6933's own weights;
- the multiplier coefficient identity, and the cost inequality
  `(19/5) E + 2 sum_c mu_c <= 88` with maximum exactly `88` on the principal
  type;
- `f <= 5/6` on 20,401 feasible weight vectors (corners of the cap box and
  repaired random draws) over all 1728 sets, with equality only at `a = 1/2` on
  the principal type;
- the rigidity lemma on all 960 principal-type sets;
- controls: a weight vector violating (W2) gives `99/115 > 5/6`, a mutated
  multiplier `13/5` breaks the coefficient identity, and a mutated census count
  is detected.

## Reproduce

```sh
python3.12 -I -B research/p104-star-weight-optimum/verify.py
```

The run takes about 5 s and ends with `PASS_P104_STAR_WEIGHT_OPTIMUM`. Standard
library only.

## Limitations

- P104 only. The same certificate fails on P112 and P120 because their edge
  counts already exceed the budget `88 - E`; their star values `1` are not
  re-derived here and no optimality claim is made for them.
- The result is about the weight program of Theorem 3. It does not bound
  `w(P104; F)` and it does not re-derive the rank inequality itself.
- The census, the constraints and the ratio formula are cited from #6933; only
  the optimum and its equality case are new.
- No human or proof-kernel review. No construction, no physical decoder, no
  kappa.

## Open next questions

1. **P112 and P120.** Is the star value `1` the exact optimum of the same weight
   program on those systems, and is the maximizing set rigid? The certificate
   here is specific to `E = 21, 22` with degrees in `{5, 6}`; a different
   multiplier pattern would be needed.
2. **Degree-7 vertices.** The cost budget is exhausted exactly on the principal
   type. A mixed certificate that uses the degree-7 vertices' stronger (W2) caps
   in a non-uniform way could in principle beat `5/6` on the `E = 22; 5,5,5,5,5,6,6,7`
   type; the uniform certificate here cannot, and the recorded value there is
   `101/126`.
3. **Sharpness of #7114's edge inequality.** Its `min(Y_c, Y_d)` step is the one
   that now carries the floor. An equality analysis of that inequality would
   decide whether `j >= k` is itself rigid, in the same way this package settles
   the weight program.

## Credit

The orthogonal-8-set setting, Theorem 3, constraints (W1) and (W2), the type
census and the recorded values are DreamingOfClouds's
[#6933](https://github.com/CrocSwap/integer-mult-bounds/pull/6933), with its
retained Bukh–Cox, Haemers and Blasiak lineage. #7114 (DreamingOfClouds) is the
sharper edge inequality that reaches 9, cited here as the successor route. The
exact optimum, the multiplier certificate, the equality case and the verifier
were produced by Nick Petalas. Apache-2.0.
