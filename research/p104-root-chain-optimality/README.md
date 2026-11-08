# Chain-nested root optimality: no root mask family beats chain(g|g) in D_root (no κ)

**No new κ.** This package states and checks a lower bound on the root cost `D_root` of a rank-one root in a stated family, and shows it is attained by the chain-nested root `chain(g|g)` (the 9|9 root of #6833 at `L = 18`). Nothing is built or priced.

## Setting

A root has `L` productive sites `0..L-1` and one all-field `A`. Every other field `F` has a mask, a set of sites, and a host site. For a family of non-`A` fields, with `f(x) = x ln x`,

```
D_root = f(8L+1) + sum over non-A fields F of [ f(8|M_F|+1) - sum over maximal runs r of idle sites in M_F of f(8 r) ],
```

where idle sites are the mask sites other than the host. This is the formula the #6833 root obeys; for `chain(9|9)` it gives `1418.8458829` per port (`L = 18`).

**Hypothesis H** (the setting of the hierarchical-root analysis, Theorem A there): characteristic not 2; ordinary bases independent of the data parameters; each parameter `D_k` occurs at its own site only, once; site `k` is a unit `Delta_k (I - 2 x_k y_k^T)` with `y_k x_k = 0` and `x_k, y_k` inside the mask `M_k`; the root is shortest (`L+1` queries). Under H the primed Gram matrix `g_ij(D) = y_i Lambda x_j` has `Z = I + 2L - G` of rank one with non-zero off-diagonals, so `g_ij g_ji = -1`, the Laurent units are monomials, and `g_{k,k+1}` carries `D_k^{-1}`; hence a field lies in every mask (the all-field `A`, rank `8L+1`). No pull request records this theorem; it is quoted from the source analysis. The chain construction itself is #6833.

Extra hypotheses used below:

* **R1** fields are coordinates, `Delta_k = D_k` on `M_k`; a field is not split.
* **R2** (`y` live on two coordinates): `y_i` is supported on `A` and the host of `i`. `x_j` is unrestricted on its mask. Section "Dropping R2" removes it.
* **R3** every non-`A` field hosts exactly one site. It is automatic when there are at least two thin queries (`n >= L+1` fields); see Scope for the one-doubleton case.

Masks may be taken to be intervals containing the host: a mask piece not adjacent to the host is useless, and adding a disconnected idle piece costs `f(8(n+r)+1) - f(8n+1) - f(8r) >= 0` by superadditivity of `f`.

## Theorem

Under H, R1, R2, R3, every family with `L = 2g` sites satisfies

```
D_root  >=  f(8L+1) + 2 * sum_{m=1..g} [ f(8m+1) - f(8m-8) ],
```

with equality for `chain(g|g)` and its outer-nested twin and for no other family. Unbalanced chains `chain(a|b)`, `a != b`, are strictly worse. At `L = 18` the bound is `1418.8458829` per port, equal to `chain(9|9)`.

## Proof

1. **Realizability is a sign factorisation (Lemma E).** Row `i` gives `S_ij = a_i alpha_j + b_i xi_{j,F_i}` for `j != i`, with `a_i = y_i A`, `alpha_j = x_j A`, and `xi_{j,F}` the component of `x_j` on `F`. For `j` in `F_i` the entry is a free unknown (the host is a singleton). For `j` outside `F_i`, `a_i alpha_j = sign(i-j) = +-1`; along every connected component of this pair graph `|a|`, `|alpha|` are constant and the signs factor as `p_i q_j`. Conversely, given signs set `a_i = p_i`, `alpha_j = q_j` and solve for `xi`. So a family of interval fields `F_i` is realizable iff there are signs `p_i, q_j` with `sign(i-j) = p_i q_j` for all `j` outside `F_i`. The least admissible `F_i` is the hull from the first `j < i` with `q_j != p_i` to the last `j > i` with `q_j = p_i`.
2. **Cost of one field.** For a host inside an interval of size `n` with idle runs `l + r = n-1`, the cost is `f(8n+1) - f(8l) - f(8r) >= f(8n+1) - f(8n-8) =: c(n)` since `f` is convex with `f(0) = 0` (superadditive); equality iff the host is at an end. `c` is increasing.
3. **Staircase.** Let `n_i` be the size of `F_i`. For every `t >= 0`, `#{i : n_i <= t} <= min(2t, L)`. (Fix `q_0 = +` by a global flip. Rows with label `-` need `lo = 0`, so `n_i >= i+1`. If `q_{L-1} = +`, rows with label `+` have `n_i >= L - min(i, z_-)` and at most `t` rows of each label are small. If `q_{L-1} = -`, rows with label `-` have `n_i >= L`; for label `+` with `u = z_-` the first `-` and `w` the last `+`, the admissible small indices number at most `2t-1-(w-u)`, or, if `u = w+1`, at most `t` on each side.) Hence the `k`-th smallest size is at least `ceil(k/2)`.
4. **Bound.** Summing `c` over sizes at least `1,1,2,2,...,g,g` gives the displayed bound. `chain(g|g)` has exactly these sizes with hosts at the inner ends, so it attains it. Strict inequality for unbalanced chains follows from convexity.

## Dropping R2

Allow `y_i` on any set of fields (dense `y`), `x` free on its masks, so that `S_ij = a_i alpha_j + sum_c b_ic xi_jc`. Idle sites become the mask minus the sites with a `y` component, so dense `y` only loses idle discount. All interval families with at least `L-1` non-`A` fields and cost at most the chain were enumerated and decided exactly by a Gröbner-basis computation over `Q` (the ideal containing 1 means unrealizable over `C`): `L = 4` (1365 families, 10 sign-consistent) and `L = 6` (1,677,563 families, 34 sign-consistent). Among families with at least `L` non-`A` fields, or in which every site has a `y` component on some field, only `chain` and the twin are realizable. So R2 can be dropped without gain at `L = 4, 6`; this is exhaustive checking, not a general-`L` proof.

## Scope (stated honestly)

* **Uncovered pivot (one loophole).** At `n = L` fields (exactly one thin query, `t = 1`) there are realizable families in which one site has `y_i = a_i A` only, with no live line besides `A`. They save `3.43957` at `L = 4` (a small-`L` artefact) and `0.43858` at `L = 4` and `L = 6`. This case is excluded when `t >= 2`, and by the non-degeneracy `b_i != 0` of the model. The saving at `L = 18` was not computed, and no word has been built or priced for these families; `check.py` recomputes the six savings from the stored families.
* **Doubleton hosts** (one field hosting two sites, possible only when `t = 1`): a relaxation keeping only the sign condition shows a spurious gain, but the exact decision finds no realizable family within the chain budget at `L = 4` (11 families, 4 sign-consistent), `L = 6` (3657 / 30) and `L = 8` (1,850,556 / 58). Reported counts; not reproduced by `check.py`, not proved for general `L`.
* **Escapes outside the theorem:** non-coordinate masks, bases that depend on `D`, non-shortest roots, units of rank above one, and dense `y` for `L > 6`. The theorem says the root has no further `D_root` lever inside H, given R2; any root gain must leave H or find a non-covered case above.
* The statement is for the model; that a legal word is a family of this kind is the H of the source analysis, quoted, not re-proved here.

## Exact checks (`check.py`, `verify.sh`, seconds)

Standard library only; `python3.12 -I -B check.py` (add `--quick` to stop the exhaustive enumeration at `L = 14`). It prints, for every even `L = 4..18`:

1. the bound, `chain(g|g)` and the twin, each computed from explicit fields and idle runs, and the sorted-size staircase sum, all equal (`L = 18`: `1418.8458829299`);
2. every unbalanced `chain(a|b)` strictly above the bound;
3. for all sign patterns `q` (`L <= 16`), the `k`-th smallest hull size is at least `ceil(k/2)`;
4. the exhaustive minimum over all `q in {+-}^L` with the best `p` per row (the non-`A` part is `697.2194902789` at `L = 18`), equal to the chain, with exactly two minimisers up to global sign (chain and twin);
5. the six uncovered-pivot savings above, and that those families appear as realizable in the stored decision logs.

It ends with `PASS_P104_ROOT_CHAIN_OPTIMALITY`. The directory `supp/` holds the supplementary decision logs (each line: saving versus chain, a realizable/unrealizable tag, the family as `(lo, hi, (sites with y))` triples) and the exhaustive minima for `L = 14..18`; the logs are read only for the presence check in item 5, and the Gröbner decisions themselves are not re-run by `check.py`.

## Open next questions

1. Is the uncovered-pivot saving (0.43858 at `L = 4, 6`) constant in `L`, and realizable with one thin query at `L = 18`?
2. Can R2 be dropped for all `L` by an obstruction proof rather than enumeration?
3. Do doubleton hosts at `t = 1` admit any realizable family within the chain budget for `L > 8`?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
