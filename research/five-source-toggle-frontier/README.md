# Five sources: no toggle alphabet beats the DUO point (72 queries, 74 additions)

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration. No new κ, no supplier, no
selected-frontier change.** It answers the open question of
[PR3321](https://github.com/CrocSwap/integer-mult-bounds/pull/3321)
(`research/quint-toggle-connector`): can two all-five toggle calls (Q5), or a mixed
Q5/DUO/TRIO alphabet, give a new priced point on the five-source, 31-output connector
batch?

## Setting

The interface is that of `research/universal-connector-boundary` (PR943): five read-only
sources, one arbitrarily dirty connector `z`, 31 dirty output rows, readouts
`A_m: y_m += A_m z`. Here **every nonempty source subset `S` is available as one complete
call** `T_S: z += sum_{j in S} B_j x_j`, charged one dispatch plus `|S|` source additions,
with no surcharge (the same favorable ledger as PR3321). Readouts stay singleton calls.
A schedule has `Q` dispatches and `A` elementary additions; its price is `oQ + pA` with
`o >= 0`, `p > 0`. The singleton witness is `(Q, A) = (74, 74)` and the DUO witness of
[PR1531](https://github.com/CrocSwap/integer-mult-bounds/pull/1531) is `(72, 74)`.

## Result

**Theorem 1.** For any set of toggle calls, used any number of times, every correct
schedule has `Q >= 72` and `A >= 74`. The DUO word attains both bounds at once, so the
minimum price is `72o + 74p` for every `o >= 0`, `p > 0`, and `(72, 74)` is the only
Pareto point. No mixture and no number of Q5 calls can improve it.

**Theorem 2.** Every correct schedule that contains a weight-5 call has `A >= 78`, so its
price is at least `72o + 78p`, which is the DUO price plus `4p`. The bound is attained by
a word with one Q5, two DUOs and seven singletons (10 calls, 16 additions, `(72, 78)`).

Consequences for PR3321's question:

* One Q5 with singleton calls has no favorable point (PR3321). With DUO calls also
  available, a Q5-containing schedule at `(72, 78)` **does** beat the singleton witness
  `(74, 74)`, exactly when `o > 2p`. So a mixed alphabet creates a new priced point
  relative to singletons plus Q5.
* It never beats the DUO point. For every `o >= 0`, `p > 0` the DUO schedule is cheaper
  than any Q5-containing schedule by at least `4p`. Two or more Q5 calls give `A >= 80`.
* In the ledger that adds a surcharge `sigma` to each multi-source call, the DUO word has
  two such calls and prices `72o + 74p + 2 sigma`, against `74o + 74p` for singletons. It
  wins exactly when `sigma < o`. The Q5 witness has three multi-source calls and is
  dominated at every `sigma >= 0`.

## Proof

*Reduction (PR943, specialized to identity maps with one-bit rows).* Let `q_t` be the
parity vector of the sources added after `t` calls. A schedule must restore `z`, so the
word of toggle vectors is a closed walk in `F_2^5`: `T` steps, `q_T = 0`, `W` total weight
(`W` is even). A row `m` read `r_m` times at boundaries `t_1..t_r` receives
`r_m A_m z_initial + A_m sum_i q_{t_i} . (B x)`, so correctness for dirty `z` forces `r_m`
even and `sum_i q_{t_i} = m`. Hence `r_m >= 2`, and `r_m = 2` only if `m = q_s XOR q_t`
for two boundaries. Let `D` be the set of nonzero differences of the prefix points and
`u = 31 - |D|`. Rows outside `D` need at least four readouts, so
`R >= 62 + 2u`, `Q = T + R`, `A = W + R`.

*Lemma 1 (support).* `T + 2u >= 10`, with equality only if `T = 10`, the ten prefix
points are distinct and `u = 0`. Let `s` be the number of distinct prefix points, so
`T >= s` and `31 - u <= C(s, 2)`. No set of at most nine points of `F_2^5` has
`P + P = F_2^5` (counting for `s <= 8`; an exhaustive search for `s = 9`, below), so
`s <= 9` forces `u >= 1`. The values of `s + 2 u_min(s)` are 14 at `s = 8`, 11 at `s = 9`,
10 at `s = 10` and `s` beyond. This extends the full-coverage bound of
[PR4137](https://github.com/CrocSwap/integer-mult-bounds/pull/4137) to words that repair
missing rows with extra readouts. So `Q >= T + 62 + 2u >= 72`.

*Lemma 2 (expansion).* Replace each call `T_S` by `|S|` consecutive singleton calls. The
result is a closed singleton word `w'` of length `W` whose boundaries include those of the
original, so `u(w') <= u(w)`. For a closed singleton word of length `L`,
`L + 2u >= 12`: a missing source leaves 16 rows uncovered; otherwise `L >= 10`; `L = 10`
means every source twice, and none of the 945 pairing words covers all 32 masks (best 31),
so `u >= 1`; `L >= 12` is immediate. Hence `A >= W + 62 + 2u(w) >= 74`.

*Theorem 1.* Lemmas 1 and 2 give `Q >= 72` and `A >= 74`. The DUO word below attains
`(72, 74)`, which proves the price statement. Equality in `Q` forces `T = 10` and full
coverage.

*Theorem 2.* Let a word have `k >= 1` weight-5 steps, so `W >= T + 4k`. With
`T + 2u >= 10`, `A >= W + 62 + 2u >= 72 + 4k`: this gives `A >= 80` for `k >= 2`.
For `k = 1` the same chain gives 76, and the cases below close the gap to 78.

* `T >= 11`: `W >= T + 4 >= 15` and `W` is even, so `W >= 16`, `A >= 78`.
* `T <= 9`: `u >= 1`, `W >= 14` at `T = 9`, `A >= 14 + 62 + 2 = 78`; smaller `T` leaves
  more rows uncovered (`u >= 3` at `T = 8`, giving `A >= 80`).
* `T = 10`: `W >= 16` gives 78. If `W = 14`, the other nine steps are singletons. Rotating
  the closed word puts Q5 last, and closure makes every singleton count odd, so the counts
  are `(5,1,1,1,1)` or `(3,3,1,1,1)`. The census below runs all 115,920 such words: at
  most 27 of 31 differences, so `u >= 4` and `A >= 14 + 62 + 8 = 84`.

The word `[1, 2, 1, 4, 2, 1, 8, 24, 10, 31]` (masks; 24 = `{3,4}`, 10 = `{1,3}`, 31 = Q5) has
ten distinct prefix points covering `F_2^5`, `W = 16`, so `(72, 78)`. It was found by an
exhaustive depth-first search over closed words with one Q5; the verifier replays it.

## Evidence

All counts are recomputed from the integers by `verify.py` (standard library; about 14 s):

* **Cover numbers.** An exhaustive search with an exact waste cut finds no nine-point
  cover; the affine-basis normal form (every cover contains an affine basis) agrees; the
  same search finds 99,200 ten-point covers containing 0, the number recorded by
  `research/duo-toggle-connector`, and the normal form finds 80.
* **Pairing census.** 945 length-ten singleton words; the coverage histogram equals the one
  recorded by PR943 (`31` is the maximum, 22 words); minimum missing rows `u = 1`.
* **One weight-5 step.** 115,920 words; maximum 27 distinct nonzero differences.
* **Witnesses.** Both words build explicit 72-call schedules (62 readouts, rows at their
  first boundary pair). Each is replayed twice: symbolically for arbitrary operators
  (`z` and each row as formal combinations of `z_0` and `B_j x_j`) and concretely with
  random binary maps and dirty data (150 trials each). The singleton 74-call word and
  PR943's ten-call word with a four-readout repair pass the same replays as positive
  controls; the ten-call word misses exactly mask 21, as PR943 states.
* **Tables and sanity.** The `T + 2u` table, the case checks for Theorem 2 over `T <= 40`,
  30,000 random closed words over all 31 toggles and a 6,000-step hill climb from the DUO
  word, all above the floors (`Q >= 72`, `A >= 74`, `A >= 78` with a Q5).
* **Controls.** Dropped operations, a wrong row, an unclosed word, a truncated concrete
  schedule, a four-step word claimed to reach 72, and a zero toggle are all rejected.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/five-source-toggle-frontier/verify.py
python3.12 -I -O -W error -B research/five-source-toggle-frontier/verify.py
python3.12 -B scripts/research_package.py --package research/five-source-toggle-frontier
```

Expected first line:
`PASS_FIVE_SOURCE_TOGGLE_FRONTIER nine_point_covers=0 ten_point_covers=99200 ...
weight5_witness=(72,78) no_new_kappa`.

## Limitations

* The price model is the favorable ledger of PR3321: a multi-source call costs one
  dispatch plus its additions, with no frame, routing or implementation surcharge. A real
  surcharge only raises every schedule that uses such a call. No physical call, compiler
  or supplier is established, and nothing here changes κ.
* The model is the binary-linear five-source, 31-row interface with singleton readouts. It
  excludes joint readouts, extra connectors, mutable sources, frame changes and other
  source counts. The all-alphabet claim is for source-side toggles only.
* The reduction to prefix differences is inherited from PR943 (necessity by the
  identity-map specialization). The proofs are written, with finite exhaustive components
  under the stated reductions. No proof assistant was run; independent human and formal
  proof-kernel review are unclaimed.
* Weights 3 and 4 are not given an analogue of Theorem 2 here.

## Open next questions

1. What is the exact minimum price among schedules that contain a weight-3 or weight-4
   call? The expansion argument gives `A >= 74` there; existing packages bound single
   TRIO and arity-four cases separately (`research/atomic-trio-connector`, the open
   PR3909). A rerun of the depth-first search used for the Q5 witness, with one TRIO or
   one weight-4 call and extra weight 2 to 6, would give the attained value. Nothing
   blocks it.
2. Does the same single-point collapse hold for every alphabet at six sources? The open
   [PR2249](https://github.com/CrocSwap/integer-mult-bounds/pull/2249) reports
   `r((C2)^6) = 14` and the singleton minimum `f(6) = 16`, which would give `Q >= 140` and
   `A >= 142`, attained by the six-source DUO word it cites. Rerunning the argument here with
   those two invariants, and then a uniform statement for `n <= 6` from the least cover size
   and the least singleton walk, is the next step.
3. Can a readout-side alphabet (joint outputs) move the 62-readout floor, which is 62 of
   the 72 queries? Toggle-side extensions cannot: Theorem 1 closes them.

## Credit

Interface, singleton minimum 12 and the 945-pairing census: Ross Richardson, PR943
(`research/universal-connector-boundary`). The DUO word and the ten-point cover count: navinor,
PR1531 (`research/duo-toggle-connector`). The support bound for steps of weight 1 to 5 at
full coverage: unpaidmoon, PR4137 (`research/connector-triple-query-floor`). The Q5 model,
the one-Q5 census and the question answered here: 1337isnot1337 (Cinna Davis), PR3321
(`research/quint-toggle-connector`). All were used as cited inputs and recomputed as
controls; none was audited. New here: the partial-coverage form of the support bound, the
expansion bound `A >= 74` for every alphabet, the single-point frontier, the weight-5
floor 78 and its attaining word.
