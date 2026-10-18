# Complete 15-call five-b exclusion and the beta <= 3 min(alpha, gamma) price cone

No fifteen-call word with five `b` calls realizes `diag([z], [uz], I_rest)` in
`F2[UT4(F2)]` on any finite number `r >= 2` of arbitrary restored dirty registers.
All three 15-call five-`b` count splits `(6, 5, 4)`, `(5, 5, 5)`, and `(4, 5, 6)`
explicitly handed off by Gareth Davidson (`@bitplane`) in
[PR #2314](https://github.com/CrocSwap/integer-mult-bounds/pull/2314) and
[PR #2343](https://github.com/CrocSwap/integer-mult-bounds/pull/2343) are excluded.

Consequently, every 15-call word has `n_b >= 6`, and every word with `n_b = 5`
requires at least eleven outer (`a`/`c`) calls (`n_a + n_c >= 11`, total length
`L >= 16`). For nonnegative per-letter prices `(alpha, beta, gamma)`, the direct
fourteen-call `(4, 6, 4)` word is globally optimal throughout **`beta <= 3 min(alpha, gamma)`**,
with exact price `4 alpha + 6 beta + 4 gamma`. At `(alpha, beta, gamma) = (1, 3, 1)`,
cost `25` is impossible and `26` is the exact minimum. This is a formal register-model
theorem and does not provide a native bit supplier or improve `kappa`.

## Model and evidence

Work in the full group algebra `R = F2[UT4(F2)]` with adjacent generators
`a = I + E12`, `b = I + E23`, `c = I + E34` and targets `u = I + E13`, `z = I + E14`.
Each paid call is `I + ([g] + 1) x y^T` with `g in {a, b, c}` and `x y^T` a nonzero
binary rank-one coupling over `F2` (idempotent or nilpotent). Every occurrence,
including restoration, is charged; invertible `GL_r(F2)` mixing is normalized into
the couplings. Extra roles start arbitrary dirty and must be restored to identity
without contaminating the active outputs.

[PROOF.md](PROOF.md) proves the uniform arbitrary-workspace reductions:

1. **Two-role compression for `(6, 5, 4)` and `(4, 5, 6)` (Lemma 1):** Because
   `n_b = 5` forces `e_b^x = e_b^y = 0` and `n_c = 4` (or `n_a = 4`) forces
   `e_c^x = e_c^y = 0` (or `e_a^x = e_a^y = 0`), only one outer generator label
   can have dirty row or column support. Any interior dirty contraction
   `v_{i_m}(u_{i_{m+1}}) != 0` therefore occurs between two calls of the same
   generator label, which vanishes identically in `R` by `([a] + 1)^2 = ([c] + 1)^2 = 0`.
   Active-corner projection preserves the `2 x 2` active block over `R`, and
   predecessor exclusions at length `<= 14` prevent any projected factor from
   vanishing.
2. **Three-role active-plus-dirty decomposition for `(5, 5, 5)` (Lemma 2):**
   All common-orientation excess profiles compress to two roles. The only remaining
   15-call five-`b` excess profiles are the two opposite-orientation three-role
   cases (`Case I`: `(e_a^x, e_a^y, e_c^x, e_c^y) = (1, 0, 0, 1)`, and `Case II`:
   `(0, 1, 1, 0)`). In `Mat_3(Q)`, the 14 basis monomials without adjacent `{A, C}`
   decouple completely from the dirty role on `W_HH` (restricting the active projections
   to the exact `5,664` compatible `(5, 5, 5)` profile pairs), the off-diagonal
   blocks `W_KH = 0` and `W_HK = 0` have zero interior dirty contractions (yielding
   exact homogeneous linear equations on the dirty prefix profiles), and `W_HH` on
   `AC, ACB, BAC` receives only the rank-one cross-role contraction.
3. **Complete 5-gap rank-sum profile characterization (Lemma 3):** A 5-gap prefix
   profile `P in Mat_2(F2)^5` with gap increments `S_g = P_{g+1} + P_g` is realizable
   by `n in {4, 5, 6}` nonzero rank-one couplings if and only if
   `sum_{g=0..5} rank(S_g) <= n`, yielding `9,721`, `47,521`, and `174,670` profiles
   (`55,566`, `907,200`, and `15,471,918` realizations).

### Complete two-role quotient censuses

| Split `(a, b, c)` | `a` / `c` profile passes | Key pairs | Profile pairs | Expanded words | First fail `AC` | First fail `ACB` | `Q` survivors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `(4, 5, 4)`, retained PR #2175 control | 89,052 / 1,201,320 | 68 | 152 | 5,536 | 1,480 | 4,056 | 0 |
| `(5, 5, 4)`, retained PR #2314 control | 236,224 / 1,201,320 | 144 | 944 | 211,968 | 125,636 | 86,332 | 0 |
| `(4, 5, 5)`, retained PR #2314 control | 89,052 / 2,899,368 | 136 | 912 | 209,920 | 117,308 | 92,612 | 0 |
| `(6, 5, 4)`, **new** | 542,428 / 1,201,320 | 312 | 3,376 | 6,049,824 | 3,729,888 | 2,319,936 | **0** |
| `(5, 5, 5)`, **new** (2-role) | 236,224 / 2,899,368 | 288 | 5,664 | 8,655,168 | 5,508,044 | 3,147,124 | **0** |
| `(4, 5, 6)`, **new** | 89,052 / 5,883,552 | 312 | 3,280 | 5,874,848 | 3,496,252 | 2,378,596 | **0** |

The three retained predecessor controls reproduce their exact counts and transcript
digests from PR #2175 and PR #2314. The new two-role total is **20,579,840 expanded
words**, with zero survivors.

### Complete three-role `(5, 5, 5)` quotient censuses

| Three-role `(5, 5, 5)` mode | Active profile pairs | Dirty profile pairs (`W_KH = W_HK = 0`) | Weighted profile completions | First fail `W_HH[AC]` | First fail `W_HH[ACB]` | `Mat_3(Q)` survivors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Case I (`e_a^x = e_c^y = 1`) | 5,664 | 17,864 | 42,447,616 | 25,294,720 | 17,152,896 | **0** |
| Case II (`e_a^y = e_c^x = 1`) | 5,664 | 17,864 | 42,447,616 | 25,294,720 | 17,152,896 | **0** |

The new three-role total is **84,895,232 weighted profile completions**, with zero survivors.

The separate [controls.py](controls.py) script checks:

- all 4,096 literal `4 x 4` binary group products in `UT4(F2)` and all 20,440 words
  of length `<= 3` against an independent subsequence-sum quotient oracle;
- the complete `16^5 = 1,048,576` profile rank-sum histogram and exact agreement
  with the explicit 4-call (`55,566` realizations, `9,721` profiles) and 5-call
  (`907,200` realizations, `47,521` profiles) gap catalogues;
- planted 15-call two-role word reconstruction and quotient evaluation across
  `(6, 5, 4)`, `(5, 5, 5)`, and `(4, 5, 6)`;
- 50 same-label nilpotent dirty-compression pairs in `Mat_3(F2[UT4(F2)])` (confirming
  Lemma 1 when both dirty rows and dirty columns are present on the same outer
  generator label) and detection of a cross-label dirty contraction;
- an independent 3-role subsequence-sum quotient oracle `quotient_3role` in `Mat_3(Q)`
  on planted 15-call three-role `(5, 5, 5)` words for both Case I and Case II, plus
  perturbation negative controls where violating a single dirty bit breaks `W_KH = 0`
  or `W_HK = 0`;
- all 28 span-rank profiles at `L <= 15` and 216 weighted price grid points,
  including the `(1, 3, 1)` boundary minimum `26` and the outside-cone `(1, 4, 1)`
  negative control (`31 < 32`).

## Scope of the price result

For all nonnegative letter prices `(alpha, beta, gamma)`, every word satisfies the
necessary lower bound

```
min(4 alpha + 6 beta + 4 gamma,
    4 alpha + 5 beta + 4 gamma + 3 min(alpha, gamma)).
```

The first branch is attained by the direct 14-call `(4, 6, 4)` word and is the
minimum whenever `beta <= 3 min(alpha, gamma)`. The second branch is a relaxed
count bound (`n_b = 5` implies `n_a + n_c >= 11`); whether any word with `n_b = 5`
exists at `L >= 16` remains open.

## Reproduce

From the repository root (standard library only):

```sh
python3.12 -I -B scripts/research_package.py --package research/ut4-fifteen-call-five-b
# Direct commands:
python3 -I -O -B research/ut4-fifteen-call-five-b/verify.py
python3 -I -O -B research/ut4-fifteen-call-five-b/controls.py
```

Both commands complete in under 10 seconds total. `verify.py --write-result`
regenerates [RESULT.json](RESULT.json).

## Open next questions

1. Does any realizing word with `n_b = 5` exist at all in `F2[UT4(F2)]`, or is
   `n_b >= 6` an unconditional structural invariant of `diag([z], [uz], I_rest)`
   for every word length `L` and workspace size `r`?
2. At `L = 16` with `n_b = 5` (`(7, 5, 4)`, `(6, 5, 5)`, `(5, 5, 6)`, `(4, 5, 7)`),
   the pairing bound from PR #2343 still restricts any realizing word to at most
   `r <= 2 + floor((16 - 13) / 2) = 3` roles, and Lemma 1 compresses `(7, 5, 4)`
   and `(4, 5, 7)` directly to `r = 2` roles. Can an algebraic invariant in `Q`
   explain why `AC = 0` and `ACB = I_2` are incompatible with the 14 non-adjacent-`{A,C}`
   equations whenever `n_b = 5`, without requiring a separate census at each outer
   length `n_a + n_c`?

## Credit

Prepared by `steph4n-gh` with AI assistance (Antigravity). Apache-2.0.

Full predecessor credit to Gareth Davidson (`@bitplane`, PR #2027, PR #2314, PR #2343)
for the mixed-root tariffs, 14-call weighted boundary, register-pairing compression,
and explicit 15-call `(1, 3, 1)` handoff; Nick Petalas (`@petalas`, PR #2175) for
the mixed-middle rank inequality, 13-call `(4, 5, 4)` census, and retained verifier
library; ToikY (PR #1662, PR #1680) and CinnaDavis / `1337isnot1337` (PR #1541)
for the degree-3 quotient and span-orientation compression; and Aaron Wang
(`@navinor`, PR #1690) for the gap-profile screening method.


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
