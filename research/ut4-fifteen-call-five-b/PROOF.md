# Complete 15-call five-b exclusion and the beta <= 3 min(alpha, gamma) price cone

In the formal group-algebra register model over `R = F2[UT4(F2)]`, no fifteen-call
word with five `b` calls realizes `diag([z], [uz], I_rest)` on any finite number
`r >= 2` of arbitrary restored dirty roles. Every fifteen-call word therefore has
`n_b >= 6`, and every word with `n_b = 5` requires at least eleven outer (`a`/`c`)
calls (`n_a + n_c >= 11`, total length `L >= 16`). Consequently, the direct
fourteen-call `(4, 6, 4)` word is globally optimal on the expanded nonnegative
letter-price cone `beta <= 3 min(alpha, gamma)`, and at `(alpha, beta, gamma) = (1, 3, 1)`
cost `25` is impossible and `26` is the exact minimum.

This package resolves the explicit 15-call `(1, 3, 1)` handoff formulated by
Gareth Davidson (`@bitplane`) in [PR #2314](https://github.com/CrocSwap/integer-mult-bounds/pull/2314)
(`research/ut4-mixed-weighted-boundary`) and [PR #2343](https://github.com/CrocSwap/integer-mult-bounds/pull/2343)
(`research/register-pairing-compression`), building on Nick Petalas's (`@petalas`)
[PR #2175](https://github.com/CrocSwap/integer-mult-bounds/pull/2175)
(`research/ut4-mixed-central-middle`). The quotient, span-excess, and profile-screen
infrastructure retains its full predecessor attribution to Gareth Davidson (PR #2027,
PR #2314, PR #2343), Nick Petalas (PR #2175), ToikY (PR #1662, PR #1680),
CinnaDavis / `1337isnot1337` (PR #1541), and Aaron Wang / `@navinor` (PR #1690).

## 1. Formal model and inherited premises

Let `G = UT4(F2)` and `R = F2[G]` with elementary generators and target elements

```
a = I + E12,   b = I + E23,   c = I + E34,
u = I + E13,   z = I + E14.
```

On any finite number `r >= 2` of scalar roles `E = H direct-sum K` (`dim H = 2`
active roles and `dim K = r - 2` dirty roles), each paid call has the form
`D_N(g) = I + ([g] + 1) N` with `g in {a, b, c}` and `N = x y^T` a nonzero binary
rank-one matrix over `F2`. Both idempotent (`y^T x = 1`) and nilpotent (`y^T x = 0`)
couplings are permitted. Every occurrence of a generator call, including restoration,
is charged; invertible `GL_r(F2)` basis changes are free and normalized into the
couplings so that the target endpoint is `W = diag([z], [uz], I_K)` in `Mat_r(R)`.

We use the retained 17-dimensional quotient algebra

```
Q = F2<A, B, C> / (A^2, B^2, C^2, AC - CA, all monomials of degree >= 4),
```

under the unital homomorphism `a, b, c |-> 1 + A, 1 + B, 1 + C`. In `Q`,

```
[u] |-> 1 + AB + BA + ABA + BAB,
[z] |-> 1 + ABC + ACB + BAC + CBA.
```

Writing `P = diag(1, 1, 0, ...)` and `S = diag(0, 1, 0, ...)`, the image of
`diag([z], [uz], I_K)` in `Mat_r(Q)` has coefficient `I_r` at `1`, `S` at
`AB, BA, ABA, BAB`, `P` at `ABC, ACB, BAC, CBA`, and `0` on the remaining eight
basis monomials `A, B, C, AC, BC, CB, BCB, CBC`.

For each label `g in {a, b, c}`, let `X_g = span{x_j : g_j = g} <= E` and
`Y_g = span{y_j^T : g_j = g} <= E*`. By the retained span-containment and
mixed-middle rank inequalities (PR #2027, PR #2175, PR #2314, PR #2343), every
realizing word of length `L = n_a + n_b + n_c` on any finite `r >= 2` satisfies:

1. `H <= X_g` and `H* <= Y_g` for all `g in {a, b, c}` (so `dim X_g = 2 + e_g^x`
   and `dim Y_g = 2 + e_g^y` with integer excesses `e_g^x, e_g^y >= 0`);
2. `n_a >= 4 + e_a^x + e_a^y`, `n_c >= 4 + e_c^x + e_c^y`, and
   `n_b >= 5 + e_b^x + e_b^y`;
3. `sum_{g in {a,b,c}} (e_g^x + e_g^y) <= L - 13`;
4. By PR #2175 and PR #2314, no word of length `L <= 14` with `n_b = 5` exists on
   any finite number of roles `r >= 2` (splits `(4, 5, 4)`, `(5, 5, 4)`, and `(4, 5, 5)`
   are completely excluded).
5. By PR #2343, any 15-call word with `n_b = 5` has count split `(6, 5, 4)`,
   `(5, 5, 5)`, or `(4, 5, 6)`, satisfies `e_b^x = e_b^y = 0` (so every `b` call
   is supported exclusively on `H x H`), and compresses via dirty-pairing
   factorization `W' = diag(I_H, F) W diag(I_H, G)` to at most `r <= 3` roles
   with exact letter counts `(n_a, n_b, n_c)` preserved (since deleting any
   zero-projected factor would yield a five-`b` word of length `<= 14`,
   contradicting premise 4).

## 2. Two-role compression for (6, 5, 4) and (4, 5, 6)

**Lemma 1 (Nilpotent same-label dirty compression).** *Every realizing word with
count split `(6, 5, 4)` or `(4, 5, 6)` on any finite number `r >= 2` of restored
dirty roles projects directly onto the two active roles `H` (`r = 2`) with all
fifteen couplings remaining nonzero rank-one `2 x 2` matrices.*

*Proof.* Consider `(6, 5, 4)` (the case `(4, 5, 6)` follows identically by
interchanging `a` and `c`). From `n_b = 5 >= 5 + e_b^x + e_b^y` and
`n_c = 4 >= 4 + e_c^x + e_c^y`, we have

```
e_b^x = e_b^y = e_c^x = e_c^y = 0.
```

Thus `X_b = X_c = H` and `Y_b = Y_c = H*`, so every `b` call and every `c` call
has zero dirty column component (`u_j = 0`) and zero dirty row component (`v_j = 0`).
Only `a` calls can have nonzero `u_j` or `v_j`.

Expand the full product `W = prod_{j=1..15} (I + lambda_j x_j y_j^T)` in `Mat_r(R)`,
where `lambda_j = [g_j] + 1 in R`. For any nonempty index subsequence `i_1 < ... < i_s`,
the corresponding product term is

```
lambda_{i_1} ... lambda_{i_s} x_{i_1} (y_{i_1}^T x_{i_2}) ... (y_{i_{s-1}}^T x_{i_s}) y_{i_s}^T.
```

Write `x_j = (tilde_x_j, u_j)` and `y_j^T = (tilde_y_j^T, v_j)` with respect to
`E = H direct-sum K`. Each interior scalar contraction splits over `F2` as

```
y_{i_m}^T x_{i_{m+1}} = tilde_y_{i_m}^T tilde_x_{i_{m+1}} + v_{i_m}(u_{i_{m+1}}).
```

Whenever `v_{i_m}(u_{i_{m+1}}) != 0`, both `v_{i_m}` and `u_{i_{m+1}}` must be
nonzero, which forces both factors `i_m` and `i_{m+1}` to be `a` calls. Then
`lambda_{i_m} = lambda_{i_{m+1}} = [a] + 1`. Because `a^2 = I` in `UT4(F2)`,
`([a] + 1)^2 = [a^2] + 1 = 0` in the full group algebra `R = F2[UT4(F2)]`, so the
ordered coefficient product `lambda_{i_1} ... lambda_{i_s}` contains the adjacent
square `([a] + 1)^2 = 0` and vanishes identically in `R`.

Consequently, replacing every `x_j, y_j` by its active projection `tilde_x_j, tilde_y_j`
leaves every surviving interior contraction and the entire upper-left `2 x 2`
active block `P W P^T = diag([z], [uz])` unchanged in `Mat_2(R)`. No projected
coupling `tilde_N_j = tilde_x_j tilde_y_j^T` can vanish, because deleting an
identity factor would produce a two-role realizing word of length `<= 14` with
`n_b = 5`, which is impossible by PR #2175 and PR #2314. []

## 3. Three-role structure for (5, 5, 5)

For `(5, 5, 5)`, `n_b = 5` forces `e_b^x = e_b^y = 0`, while `n_a = 5` and `n_c = 5`
give `e_a^x + e_a^y <= 1` and `e_c^x + e_c^y <= 1`.

- If `e_a^x + e_c^x = 0`, then `u_j = 0` for all 15 factors (`P N_j = N_j`).
- If `e_a^y + e_c^y = 0`, then `v_j = 0` for all 15 factors (`N_j P = N_j`).
- If `e_a^x + e_a^y = 0` or `e_c^x + e_c^y = 0`, only one outer label has dirty
  support, and Lemma 1 applies.

In all those cases, active-corner projection compresses the word directly to two
roles (`r = 2`). The only remaining excess profiles are the two opposite-orientation
three-role cases (`E = H direct-sum K` with `dim K = 1`):

- **Case I (`(e_a^x, e_a^y, e_c^x, e_c^y) = (1, 0, 0, 1)`):** `v_a = 0`,
  `u_b = v_b = 0`, `u_c = 0`. In `3 x 3` block form on `H direct-sum K`:
  ```
  N_a = [ tilde_N_a     0 ],   N_b = [ N_b  0 ],   N_c = [ tilde_N_c  x_c d_c ]
        [ d_a y_a^T     0 ]          [  0   0 ]          [     0         0    ]
  ```
  with `tilde_N_a = x_a y_a^T`, `tilde_N_c = x_c y_c^T`, `d_a, d_c in F2`.
- **Case II (`(e_a^x, e_a^y, e_c^x, e_c^y) = (0, 1, 1, 0)`):** `u_a = 0`,
  `u_b = v_b = 0`, `v_c = 0`, the transpose block pattern:
  ```
  N_a = [ tilde_N_a  x_a d_a ],   N_b = [ N_b  0 ],   N_c = [ tilde_N_c     0 ]
        [     0         0    ]          [  0   0 ]          [ d_c y_c^T     0 ]
  ```

**Lemma 2 (Exact 3-role quotient equations for `(5, 5, 5)`).** *In `Mat_3(Q)`, any
realizing `(5, 5, 5)` word in Case I or Case II satisfies the following exact
necessary conditions:*

1. **Active-block decoupling outside `{AC, ACB, BAC}`:** *Every interior dirty
   contraction `v_{i_m}(u_{i_{m+1}}) != 0` requires `(g_{i_m}, g_{i_{m+1}}) = (c, a)`
   in Case I and `(a, c)` in Case II. Thus any subsequence contributing a dirty
   interior contraction has adjacent `A` and `C` in its quotient monomial, which
   can only belong to `{AC, ACB, BAC}` in `Q` (since `A^2 = C^2 = ACA = CAC = 0`
   and degree `>= 4` vanishes). All 14 remaining basis monomials of `Q` (`1, A, B, C,
   AB, BA, BC, CB, ABA, ABC, BAB, BCB, CBA, CBC`) on `W_HH` are identical to the
   two-role quotient of the projected word `(tilde_N_a, N_b, tilde_N_c)`.*
2. **Active rank-sum and compatible profile restriction:** *On `W_HH`, the first-degree
   equations give `sum tilde_N_a = sum N_b = sum tilde_N_c = 0`. Every `a` or `c`
   call has `rank(tilde_N) in {0, 1}` (with `tilde_N = 0` only when the call is a
   pure-dirty rank-one coupling `e_K y^T` or `x e_K^T`). Because the 14 non-adjacent-`{A,C}`
   equations on `W_HH` match the 2-role quotient, the active prefix sums
   `tilde_P_a, tilde_P_c in Mat_2(F2)^5` at the five `b` calls must belong to the
   exact `5,664` compatible `(5, 5, 5)` profile pairs. In particular, every
   compatible profile `P` has `sum_{g=0..5} rank(P_{g+1} + P_g) >= 4`, so at most
   one `a` call has `tilde_N_a = 0` and at most one `c` call has `tilde_N_c = 0`.*
3. **Homogeneous off-diagonal `(K, H)` and `(H, K)` equations:** *No subsequence
   of degree `<= 3` starting at `K` and ending at `H` (or starting at `H` and
   ending at `K`) can visit `K` twice without containing `ACA = 0`, `CAC = 0`, or
   degree `>= 4`. Hence `W_KH` and `W_HK` receive zero dirty interior contractions.
   Letting `r_{a,j} = sum_{t < b_j} d_{a,t} y_{a,t}^T` and `q_{c,j} = sum_{t > b_j} x_{c,t} d_{c,t}`
   in Case I (with `sum d_a y_a^T = 0` and `sum x_c d_c = 0` from `W_KH|_A = 0`
   and `W_HK|_C = 0`), the off-diagonal blocks `W_KH = 0` and `W_HK = 0` enforce:*
   - *Case I:*
     ```
     sum_{j=1..5} r_{a,j} N_{b,j} = 0               (W_KH at AB),
     sum_{j=1..5} r_{a,j} N_{b,j} tilde_P_{a,j} = 0 (W_KH at ABA),
     sum_{j=1..5} r_{a,j} N_{b,j} tilde_P_{c,j} = 0 (W_KH at ABC),
     sum_{j=1..5} N_{b,j} q_{c,j} = 0               (W_HK at BC),
     sum_{j=1..5} tilde_P_{c,j} N_{b,j} q_{c,j} = 0 (W_HK at CBC),
     sum_{j=1..5} tilde_P_{a,j} N_{b,j} q_{c,j} = 0 (W_HK at CBA).
     ```
   - *Case II (transpose orientation, with `q_{a,j} = sum_{t < b_j} x_{a,t} d_{a,t}`
     and `r_{c,j} = sum_{t > b_j} d_{c,t} y_{c,t}^T`):*
     ```
     sum_{j=1..5} N_{b,j} q_{a,j} = 0               (W_HK at BA),
     sum_{j=1..5} tilde_P_{a,j} N_{b,j} q_{a,j} = 0 (W_HK at ABA),
     sum_{j=1..5} tilde_P_{c,j} N_{b,j} q_{a,j} = 0 (W_HK at CBA),
     sum_{j=1..5} r_{c,j} N_{b,j} = 0               (W_KH at CB),
     sum_{j=1..5} r_{c,j} N_{b,j} tilde_P_{c,j} = 0 (W_KH at CBC),
     sum_{j=1..5} r_{c,j} N_{b,j} tilde_P_{a,j} = 0 (W_KH at ABC).
     ```
4. **Cross-role correction on `W_HH` at `{AC, ACB, BAC}`:** *On `W_HH`, the
   coefficients of `AC`, `ACB`, and `BAC` equal their two-role active values
   plus the rank-one dirty contractions across ordered pairs `(c_i < a_k)` in
   Case I (where `CA = AC` in `Q` contributes `x_{c,i} d_{c,i} d_{a,k} y_{a,k}^T`)
   or ordered pairs `(a_i < c_k)` in Case II (contributing `x_{a,i} d_{a,i} d_{c,k} y_{c,k}^T`),
   multiplied on the right by `N_{b,j}` for `j > max(i, k)` in `ACB` and on the
   left by `N_{b,j}` for `j < min(i, k)` in `BAC`.*

## 4. Profile rank-sum characterization and complete censuses

**Lemma 3 (5-gap profile rank-sum characterization).** *Let `P = (P_1, ..., P_5) in Mat_2(F2)^5`
be a 5-gap prefix profile with gap increments `S_g = P_{g+1} + P_g` for `g = 0, ..., 5`
(`P_0 = P_6 = 0`). Each `S_g in Mat_2(F2)` has rank `r_g in {0, 1, 2}` (`1` matrix
of rank `0`, `9` of rank `1`, and `6` of rank `2`), and can be written as a sum
of `k_g` nonzero rank-one matrices in `COUPLINGS` if and only if `k_g >= r_g` and
`(r_g, k_g) != (0, 1)`. Consequently, `P` is realizable by `n in {4, 5, 6}` nonzero
rank-one couplings distributed across the six gaps if and only if*

```
sum_{g=0..5} rank(S_g) <= n.
```

*(Even slack is absorbed by paired calls `R + R = 0`. Odd slack at least
three is absorbed by a zero-sum triple of distinct rank-one matrices sharing
one nonzero column, followed by pairs. For slack one, the minimal decomposition
contains a rank-one summand because the rank sum is `n-1 >= 3`; split that
summand into two distinct rank-one matrices sharing its column.)*

Across all `16^5 = 1,048,576` profiles in `Mat_2(F2)^5`, the exact rank-sum
distribution `sum_{g=0..5} rank(S_g) in {0, ..., 12}` is

```
[1, 0, 135, 720, 8865, 37800, 127149, 234360, 291690, 216720, 102240, 25920, 2976],
```

giving the complete two-role outer inventories:

| Outer calls `n` | Zero-sum sequences | Gap placements `C(n+5, n)` | Total realizations | Distinct profiles (`sum rank <= n`) |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 441 | 126 | 55,566 | 9,721 |
| 5 | 3,600 | 252 | 907,200 | 47,521 |
| 6 | 33,489 | 462 | 15,471,918 | 174,670 |

### 4.1 Complete two-role quotient censuses

For all `3,600` zero-sum five-`b` middle sequences, `census.py` evaluates every
realizable `a` and `c` prefix profile, filters by the exact necessary single-side
equations (`AB, BA, ABA, BAB` for `a` and `CB, BC, CBC, BCB` for `c`) and transported
`ABC = CBA = P` key compatibility, and then expands every realization and within-gap
interleaving across all six gaps to test `AC = 0`, `ACB = P`, and `BAC = P`:

| Split `(n_a, n_b, n_c)` | `a` / `c` profile passes | Key pairs | Profile pairs | Expanded words | First fail `AC` | First fail `ACB` | `Q` survivors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `(4, 5, 4)` (retained PR #2175) | 89,052 / 1,201,320 | 68 | 152 | 5,536 | 1,480 | 4,056 | 0 |
| `(5, 5, 4)` (retained PR #2314) | 236,224 / 1,201,320 | 144 | 944 | 211,968 | 125,636 | 86,332 | 0 |
| `(4, 5, 5)` (retained PR #2314) | 89,052 / 2,899,368 | 136 | 912 | 209,920 | 117,308 | 92,612 | 0 |
| `(6, 5, 4)` (**new**) | 542,428 / 1,201,320 | 312 | 3,376 | 6,049,824 | 3,729,888 | 2,319,936 | **0** |
| `(5, 5, 5)` (**new**, 2-role) | 236,224 / 2,899,368 | 288 | 5,664 | 8,655,168 | 5,508,044 | 3,147,124 | **0** |
| `(4, 5, 6)` (**new**) | 89,052 / 5,883,552 | 312 | 3,280 | 5,874,848 | 3,496,252 | 2,378,596 | **0** |

All `20,579,840` new 15-call two-role candidate words are rejected at `AC` or `ACB`.
By Lemma 1, this completely excludes `(6, 5, 4)` and `(4, 5, 6)` across all
finite dirty workspaces `r >= 2`, and excludes all two-role and common-orientation
`(5, 5, 5)` words.

### 4.2 Complete three-role quotient censuses for `(5, 5, 5)`

For each of the `5,664` compatible `(5, 5, 5)` active profile pairs `(N_b, tilde_P_a, tilde_P_c)`
and for each opposite-orientation mode (Case I and Case II), `census.py` enumerates
every dirty prefix profile `(r_1, ..., r_5)` and `(q_1, ..., q_5)` realized by
 five `a` calls and five `c` calls (including pure-dirty calls with `tilde_N = 0`
and requiring at least one nonzero dirty bit on each side so `e^x = 1` and `e^y = 1`),
applies the exact homogeneous off-diagonal equations `W_KH = 0` and `W_HK = 0` from
Lemma 2(3), and then evaluates `W_HH` on `AC, ACB, BAC` across every gap split and
within-gap interleaving:

| Three-role `(5, 5, 5)` mode | Active profile pairs | Dirty profile pairs passing `W_KH = W_HK = 0` | Weighted profile completions | First fail `W_HH[AC]` | First fail `W_HH[ACB]` | `Mat_3(Q)` survivors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Case I (`e_a^x = e_c^y = 1`) | 5,664 | 17,864 | 42,447,616 | 25,294,720 | 17,152,896 | **0** |
| Case II (`e_a^y = e_c^x = 1`) | 5,664 | 17,864 | 42,447,616 | 25,294,720 | 17,152,896 | **0** |

All `84,895,232` weighted profile completions covering the opposite-orientation
three-role `(5, 5, 5)` cases fail on `W_HH`
at `AC` or `ACB`. Together with the two-role census, this excludes `(5, 5, 5)`
across all finite dirty workspaces `r >= 2`.

## 5. Main theorem and weighted price consequences

**Theorem.** *In the formal rank-one group-algebra model over `F2[UT4(F2)]` for
`diag([z], [uz], I_rest)` on any finite number `r >= 2` of restored dirty roles:*

1. *No 15-call word has `n_b = 5`: the count splits `(6, 5, 4)`, `(5, 5, 5)`, and
   `(4, 5, 6)` are all impossible.*
2. *Every 15-call word satisfies `n_b >= 6`, and every word with `n_b = 5` (of any
   total length `L` and on any finite number of roles `r >= 2`) satisfies
   `n_a + n_c >= 11` and `L >= 16`.*
3. *For every nonnegative real letter-price triple `(alpha, beta, gamma) in R_{>= 0}^3`,
   every realizing word has weighted cost at least*
   ```
   min(4 alpha + 6 beta + 4 gamma,
       4 alpha + 5 beta + 4 gamma + 3 min(alpha, gamma)).
   ```
4. *Whenever `beta <= 3 min(alpha, gamma)`, the direct 14-call `(4, 6, 4)` word
   (`abcbabcb` on `z` and `acbabc` on `uz`) attains this lower bound and is
   therefore globally optimal across all word lengths `L` and all finite role
   counts `r >= 2`. In particular, at `(alpha, beta, gamma) = (1, 3, 1)`, cost `25`
   is impossible and `26` is the exact minimum.*

*Proof.* Every realizing word satisfies `n_a >= 4`, `n_b >= 5`, `n_c >= 4`. If
`n_b = 5` and `n_a + n_c <= 10`, then `L = n_a + 5 + n_c <= 15`. Length `<= 14` is
excluded by PR #2175 and PR #2314, and length `15` (`(6, 5, 4)`, `(5, 5, 5)`,
`(4, 5, 6)`) is excluded by Lemmas 1–3 and the complete censuses in Section 4.
Thus `n_b = 5` implies `n_a + n_c >= 11` (`L >= 16`).

For any `(alpha, beta, gamma) in R_{>= 0}^3`, a word with `n_b >= 6` costs at least
`4 alpha + 6 beta + 4 gamma`, while a word with `n_b = 5` has `n_a - 4 >= 0`,
`n_c - 4 >= 0`, and `(n_a - 4) + (n_c - 4) >= 3`, so it costs at least
`4 alpha + 5 beta + 4 gamma + 3 min(alpha, gamma)`. Comparing the two branches yields
`4 alpha + 6 beta + 4 gamma <= 4 alpha + 5 beta + 4 gamma + 3 min(alpha, gamma)` if
and only if `beta <= 3 min(alpha, gamma)`. At `(1, 3, 1)`, both branches equal `26`,
which is attained by the direct `(4, 6, 4)` word. []

## 6. Scope and limitations

This result is a scoped formal register-model theorem and computer-assisted
necessary-quotient exclusion over `F2[UT4(F2)]`. It does not claim:

- optimality outside the cone `beta <= 3 min(alpha, gamma)` (for instance at
  `(alpha, beta, gamma) = (1, 4, 1)`, where the direct `(4, 6, 4)` word costs `32`
  and the lower envelope is `31` via `L = 16` five-`b` candidates `(7, 5, 4)`,
  `(6, 5, 5)`, `(5, 5, 6)`, `(4, 5, 7)`),
- a native bit-operation supplier, compiler lowering, or `kappa` bound change.


### Maintainer clarification of census counts

The three-role `words` totals count weighted completions of the admitted dirty
prefix profiles. `get_dirty_profs` requires that each profile *has* a realization
with a nonzero dirty bit. The subsequent joint gap DP does not retain that
nonzero-bit flag, so it can also count realizations with an entirely clean side
when the same prefix profile permits them. Thus these totals are a conservative
superset, not exact counts of words with both excesses equal to one. This does
not weaken the exclusion: every required opposite-orientation word is included,
and every counted completion is rejected.

The maintainer's source-bound replay reproduces the original counts and checks
the finite coverage cutoffs: every compatible active profile has rank sum at
least four, forcing at most three calls of either label in any one gap; every
admitted joint gap uses at most four calls. It also detects 6,288 admitted dirty
profile pairs with a zero prefix profile on at least one side across the two
modes. These are profile-pair counts, not word counts. The exact receipt and
instrumentation are retained in `research/community-efficient1700-audit`.
