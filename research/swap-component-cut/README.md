# Mixed transposition targets cost three calls each

**Scoped formal-model theorem, exact finite minima and a census. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

The model is the formal `M_R(F2[GL_n(F2)])` model of
[#4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939). Each
target register `r` carries the row transposition `τ_r` of some coordinate
pair `{a_r, b_r}`, and different registers may use different pairs. Build
the **target graph** on the coordinates: it has one edge `{a_r, b_r}` per
target.

1. **Theorem.** Suppose every connected component of the target graph has at
   most three vertices. Then the `t` targets cost **exactly `3t` paid calls**.
   This holds for every `n ≥ 2` and `R ≥ t`, with free scalar mixing and
   restored dirty registers. It answers [#4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950)'s
   open question for these targets: mixed swaps such as `(0,1)` on one
   register and `(1,2)` on another cost 6, with nothing shared.
2. **Exact minima at `n = 3`, `R = 2`.**
   - `diag([s01],[s12])` costs exactly 6.
   - A coordinate 3-cycle costs exactly 6, even with a dirty register.
   - For **every** pair `(g, h)` in `GL_3(F2)^2`, `diag([g],[h])` costs at
     least `min(ℓ(g)+ℓ(h), 6)`, where `ℓ` is the CNOT word length. So the
     cost is additive whenever `ℓ(g)+ℓ(h) ≤ 6`.
3. **Limits of the method.** Cuts built from the relative order of the rows
   (order patterns) do not reach every target, by exact LP over all subsets:
   - for a 3-cycle at `n = 3` they certify only 3 of the 6 calls;
   - at `n = 4` they certify `8.33` for the 3-edge path and `8.14` for the
     3-edge star. Both round up to the true 9, but no clean cut exists there.

## Proof of the theorem

Use the regular representation of `G = GL_n(F2)`, as in #4950. For a cut
`A ⊆ G` let `out(g) = |{x ∈ A : g x ∉ A}|`. The crossing rank
`q(M) = rank M[A^c ⊗ F2^R, A ⊗ F2^R]` is subadditive, and it gives:

- `out(g)` for a paid call;
- 0 for a free scalar map;
- `Σ_r out(τ_r)` for the target.

Fix a linear order on the nonzero vectors, and sum every cut below over all
orders. A CNOT writing row `i` replaces `r_i` by `w = r_i + r_j`, a vector
distinct from all rows. Averaged over orders, the relative order of
`r_0, …, r_{n−1}, w` is uniform. So only exchangeability of a few random
items matters. Write `u = |G|/6` per order.

- **Pair cut** on `{a, b}`: `A = {r_a < r_b}`.
  - A CNOT writing `a` or `b` leaves with probability `P(r_a < r_b < w) = 1/6`,
    which is `u`.
  - A CNOT writing any other row costs 0.
  - The transposition of `a` and `b` moves all of `A` out: `3u`.
- **Triple parity cut** on `{a, b, c}`: `A` is the set of `x` whose rows
  `a, b, c` appear in an even-sign relative order.
  - Over the 24 orders of `{r_a, r_b, r_c, w}`, a CNOT writing `a` starts in
    `A` and flips parity in exactly 4, which is `u`. The same holds for `b`
    and `c`.
  - CNOTs writing other rows cost 0.
  - Each of the three transpositions inside the triple flips parity: `3u`.

Give each component of the target graph one cut. A single edge, with any
multiplicity, gets its pair cut. A 2-path or a triangle gets the parity cut
of its three vertices. Components have disjoint vertex sets, so:

- each CNOT writes a row in at most one component, which bounds every paid
  call by `u`;
- each target contributes `3u` to its own component's cut.

Hence `calls · u ≥ 3t · u`. Each transposition takes three CNOTs on its own
register, so `3t` is attained.

A single pair cut fails on a 2-path: `τ_{12}` contributes only `u` to the
pair cut `{0 < 1}`. That is why the parity cut is needed. The parity cut
works only for three rows. For four rows, a reinsertion flips parity with
probability `2/5` rather than `1/3`.

## Evidence

`verify.py`, exact, about three seconds, checks:

- both exchangeability lemmas, over all 6 and all 24 relative orders;
- the averaged cut counts in the `GL_3` regular representation over all
  5,040 orders, for every CNOT and transposition under the pair and parity
  cuts;
- formal minima by meet-in-the-middle with a 26,551-element forward ball:
  `s01+s12` has no word of length at most 5 and has one of length 6, and the
  same holds for the 3-cycle;
- the nine-call word for the 3-edge path at `n = 4`, `R = 3`.

`census.py`, exact, about 20 seconds, checks all 28,211 pairs at `n = 3`,
`R = 2`: none has a formal word shorter than `min(ℓ(g)+ℓ(h), 6)`.

The LP figures in item 3 come from an exact enumeration of all 64 pattern
subsets at `n = 3`, and from column generation with MILP pricing at `n = 4`.
Both ran on scipy/HiGHS in a scratch environment. They are not part of the
package, and the theorem does not use them.

## Scope

Card `bit-new-register-model`, scope **changed** (see `TASK.json`). This is a
negative formal-model screen, not a native construction.

The theorem does **not** cover target components with four or more
vertices, cycles of three or more coordinates in one register, other group
elements, or other tariffs. The census covers only `n = 3` with at most two
registers.

Base: canonical main `cef4b52f2a59009865bf8eabde1be3f159063703`, priority
revision 7. This builds on pending #4950 and pending #4939. The overlap
search is the one recorded for #4950. No other `n ≥ 3` mixed-target work
was found, which is not a novelty proof.

## Reproduce

```sh
python3.12 -B research/swap-component-cut/verify.py
python3.12 -B research/swap-component-cut/census.py
python3.12 -B scripts/research_package.py --package research/swap-component-cut
```

## Open next questions

1. **Are costs additive across several targets that are not transpositions in
   small components?** Examples are two 3-cycles on two registers, or a
   3-edge transposition path or star. A *single* target is settled: pending
   [#4974](https://github.com/CrocSwap/integer-mult-bounds/pull/4974)'s
   support lemma shows that one target `[g]` costs at least the CNOT word
   length `ℓ_{GL_n}(g)`. With the trivial one-register word, this makes the
   cost exactly `ℓ_{GL_n}(g)`. In particular a 3-cycle costs 6 for every `n`
   and `R`. Support bounds only the largest single target, though. For several
   targets, order-pattern cuts are not tight: 3 of 6 for a 3-cycle at
   `n = 3`, and 8.33 and 8.14 of 9 for the 3-edge path and star at `n = 4`. A
   scratch column-generation run over all permutation cuts stopped at 3.51
   for the 3-cycle; it is not certified optimal. *First step:* run the exact
   formal search for `diag([c3],[c3])` at `n = 3`, `R = 2`, up to length 11,
   or find a cut that combines with the support argument. *Blocked by:*
   nothing.

## Credit

- Mihir Srivastava, #4939, for the spectator model.
- PR1989 and the GL2 corollary, for the cut method.
- commdata2338, PR1414/PR1495.
- PR1541.
- Gareth Davidson/PR1333.

Their notes keep their earlier credit.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review and no formal-kernel
acceptance are claimed.
