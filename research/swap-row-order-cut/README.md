# Address spectators never help coordinate swaps

**Scoped formal-model theorem with exact finite checks. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

In the formal model of [PR #4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939),
`t` coordinate-SWAP targets cost **exactly `3t` paid calls**. This holds for
every address dimension `n ≥ 2` and every register count `R ≥ t`. Free
scalar mixing and any number of restored dirty registers are allowed.

For `t = 3` the minimum is nine, so spectator coordinates cannot reach the
eight-call `(3,3,2)` row budget. This answers #4939 open question 1.

The same cut reproves #4939's two-swap theorem without its projection step,
and it reduces to PR1989's inversion cut at `n = 2`.

## Model

The model is #4939's, unchanged. Work in `M_R(F2[GL_n(F2)])`.

- **Paid call.** A paid call is `D_N(g) = I_R + ([g] + [I_n]) N`, with
  `g = I_n + E_ij` (`i ≠ j`) and `N = u v^T`, `v^T u = 1`. Each call costs one.
- **Free maps.** Scalar `GL_R(F2)` maps are free.
- **Target.** The target is `T = diag([s], …, [s], [I_n], …, [I_n])`, with `t`
  copies of `[s]`, where `s` swaps address coordinates 0 and 1.
- **Equality.** Equality is formal and holds on arbitrary inputs. Extra
  registers are dirty and individually restored.

## Proof

**1. A representation and a cut.** Let `G = GL_n(F2)` act on itself by left
multiplication, and use the regular representation `ρ` on `F2^G ⊗ F2^R`.

- Left multiplication by `I + E_ij` adds row `j` to row `i` of `x`.
- Left multiplication by `s` swaps rows 0 and 1 of `x`.

Fix a linear order `<` on the `N = 2^n − 1` nonzero vectors of `F2^n`. Put

```text
A = { x in G : row0(x) < row1(x) },    X+ = A ⊗ F2^R,  X− = A^c ⊗ F2^R,
q(M) = rank M[X−, X+].
```

From `(UV)[−,+] = U[−,+] V[+,+] + U[−,−] V[−,+]` we get
`q(UV) ≤ q(U) + q(V)`.

For a permutation `g` put `out(g) = |{x ∈ A : g x ∉ A}|`. Then:

- **Paid call.** `ρ(D_N(g))[−,+] = P_g[A^c, A] ⊗ N` is a partial permutation
  tensored with a rank-one matrix, so `q = out(g)`.
- **Free maps.** A free scalar map has `q = 0`.
- **Target.** The target has `q = t · out(s)`. Restored registers contribute
  nothing.

**2. Counting `out`.** Write `L` for the set of lines `{a, b, a+b}`. There are
`|L| = N(N−1)/6` of them, and `|A| = c · 3|L|`, where `c` is the number of
completions of an independent row pair to an element of `G`.

- **The swap.** `s` maps `(r0, r1)` to `(r1, r0)`, so every element of `A`
  leaves: `out(s) = |A| = 3c|L|`.
- **Spectator-row writes.** A CNOT with `i ≥ 2` fixes rows 0 and 1:
  `out = 0`.
- **Active CNOTs.** Take `CNOT(0,1)`, which maps `(a, b)` to `(a+b, b)`, or
  `CNOT(1,0)`, which maps it to `(a, a+b)`. Sort each line as `x < y < z`.
  Of its three increasing pairs, exactly one leaves `A` under each map: `(x,y)`
  under `CNOT(0,1)` and `(y,z)` under `CNOT(1,0)`. So for **every** order,
  `out = c|L| = |A|/3`.
- **Spectator reads** (`i ∈ {0,1}`, `j ≥ 2`). Given rows 0 and 1 equal to
  `(a, b)`, row `j` is uniform over the vectors outside `span(a, b)`. Indeed,
  any two such vectors `u, u'` are exchanged by some `h` fixing `a` and `b`,
  and `x ↦ x h` permutes the completions. So `a + r_j` is uniform over the
  `N − 3` nonzero vectors off the line of `(a, b)`. Let line positions be
  `p_x < p_y < p_z`, with positions numbered `0, …, N−1`. Summing over each
  line's increasing pairs gives

  ```text
  out(CNOT(0,j)) (N−3)/c = Σ_lines (3N − 4 − p_y − 2 p_z),
  out(CNOT(1,j)) (N−3)/c = Σ_lines (2 p_x + p_y − 1).
  ```

**3. Average over all orders.** Under a uniformly random order, each line
occupies a uniformly random 3-subset of positions. For a random 3-subset of
`{0, …, N−1}`, `E[p_y + 2p_z] = 2N − 1` and `E[2p_x + p_y] = N − 2`. So
both spectator-read counts average exactly to `c|L| = |A|/3`.

Take `Q = Σ_orders q_order`. This is still subadditive. Every paid call has
`Q = (#orders) c|L|` exactly, by step 2 for the active and spectator-row
CNOTs and by this average for the spectator reads. The target has
`Q = (#orders) · 3 c|L| · t`. Hence

```text
calls · (#orders) c|L|  ≥  (#orders) 3c|L| t,   so   calls ≥ 3t.
```

The same averaging shows that some single order already works. Both
spectator conditions are equivalent to `Σ_lines (p_z − p_x) ≥ (N+1)|L|/2`,
and the average over orders meets this with equality.

**4. Attainment.** On each target register `r`, apply `a, b, a`, with
`a = I + E_01` and `b = I + E_10`, using projector `E_rr`. Since `aba = s`,
these `3t` calls give `T` and fix every other role.

At `n = 2` there are no spectators, the regular representation is that of
`S3`, and step 2 is PR1989's inversion count. For `n ≥ 3` a CNOT moves
`2^{n−1}` of the nonzero vectors, which is why #4939 needed its projection.
The row-pair cut needs no projection and has no limit on spectator writes.

## Evidence

`verify.py` uses only the standard library and exact integer or `Fraction`
arithmetic. It runs in about one second.

- **Regular-representation cut counts** for `GL_2` (all 6 orders),
  `GL_3` (all 5,040 orders) and `GL_4` (eight orders, including Gray and
  natural order; 20,160 group elements). Each check confirms that the swap
  cuts all of `A`, that the active CNOTs cut exactly `|A|/3` and that
  spectator-row CNOTs cut nothing. It also confirms that spectator reads match
  the line formula and the spread criterion. For `n = 2, 3`, the all-order
  sums equal `(#orders)|A|/3` exactly.
- **Spread identities** `E[p_z − p_x] = (N+1)/2`, `E[p_y + 2p_z] = 2N − 1`
  and `E[2p_x + p_y] = N − 2`, over all 3-subsets for `N ≤ 63`.
- **The crossing-rank lemma** on actual paid factors: GL_3, `R = 2`, every
  CNOT, the swap and every projector (42 cases).
- **200 random subadditivity checks.**
- **Attaining formal words** for `(n, t, R) = (2,3,3), (3,3,4), (4,2,3)`.

Mutating the active-CNOT count, the all-order sum, the swap count or the
attaining word makes the verifier fail.

The cut was found by column generation over subsets of the GL_3 regular
representation, using scipy/HiGHS in a scratch environment. The LP optimum
over permutation cuts is exactly 3 per swap. That search is not part of the
package; the proof above does not depend on it. Earlier, a separate formal
meet-in-the-middle search ([review on #4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939#issuecomment-6356540020))
found no two-swap word of length 5 or less at `(n,R) = (3,2), (4,2), (5,2)`.

## Scope

Card `bit-new-register-model`, scope **changed** (see `TASK.json`). This is
a negative formal-model screen. It does not satisfy the card's native
construction gate.

The result holds for the swap of one fixed coordinate pair on every target
register. Mixed targets, other permutations, other tariffs and native
realizations are not covered. No supplier, hosting, precision or recursive
profile is supplied.

Base: canonical main `cef4b52f2a59009865bf8eabde1be3f159063703`, priority
revision 7. The `find_overlap.py` search for "three swaps" found PR1541
(three swaps at `n = 2`), the four-swap and label-saturation notes, and the
GL2 corollary (`3t` at `n = 2`). None treats `n ≥ 3` beyond #4939's `t = 2`.
That is a search result, not a novelty proof.
Claim: [#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19137331).

## Reproduce

```sh
python3.12 -B research/swap-row-order-cut/verify.py
python3.12 -B scripts/research_package.py --package research/swap-row-order-cut
```

## Open next questions

1. **Mixed swap targets.** Does the row-order cut extend to swaps of
   different coordinate pairs on different registers, or to coordinate
   3-cycles? *First step:* at `n = 3`, compute the best permutation cut for
   swaps of `(0,1)` and `(1,2)` on two registers by the same column-generation
   LP, and compare it with the six-call word. *Blocked by:* nothing.

## Credit

- Mihir Srivastava (@mihir-s-05), #4939, for the spectator model, the row
  budget and the open question.
- commdata2338, PR1414/PR1495, for the two-coordinate obstruction and the
  spectator certificate.
- Ross Richardson, PR1989, and the GL2 corollary, for the cut method and the
  `3t` theorem at `n = 2`.
- PR1541, for three swaps at `n = 2`.
- Gareth Davidson/PR1333, for the alphabet and the normalization.

Their notes keep their earlier credit.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review and no formal-kernel
acceptance are claimed.
