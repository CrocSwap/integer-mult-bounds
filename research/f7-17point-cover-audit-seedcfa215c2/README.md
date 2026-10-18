# KB3c — 17-point cover audit: PR 2542's "no 17-point set covers F2^7" against its own lemma table

**Set-level finite result: the audited claim is established for four of the six
counting-feasible 17-point splits. The splits `(10,7)/(7,10)` are excluded
exactly; the splits `(11,6)/(6,11)` are reduced to two explicit surviving
rows. No new kappa.**

[PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) (Aaron
Wang) excludes length 18 for seven-source singleton universal words, proving
`f(7) >= 20`. Its "Why length 18 collapses" section asserts, in bold, **"No
17-point set covers `F2^7`"** — but its machine-checked `lemma_a_table` /
`lemma_a_by_multiset` contradiction is computed only for the parity splits
`(9,8)/(8,9)`, and its certificate records `size17_splits = {"9_8": false,
"8_9": false}` only. The counting-feasible 17-point splits `(|E|,|O|)` with
`|E|+|O| = 17` are exactly `(9,8),(8,9),(10,7),(7,10),(11,6),(6,11)`, and the
four non-`(9,8)` rows survive the identity as written
(`lemma_a_table(7, 10, 7)` is feasible: upper 3 versus need 3; PR 2634's
`test_lemma_rows_survive_at_L20` already pins this).

This package audits the claim against that table:

> **1. The pair-representation identity is extended to all six rows with a
> sharp collision-multiplicity constraint** (`sum_o C(r_o, 2) = 2 sum_x A_x
> B_x`, odd excess `sum_o (r_o - 1) = s*t - 64`), machine-checked and
> independently re-derived. `(9,8)/(8,9)` are re-killed (best 1, need 4); the
> `(10,7)` profiles force `c` in `{3, 4, 5, 6, 8}`; `(11,6)` collapses to one
> row class `(e_ex, b_ex, c) = (e, 6-e, 1)` with `shared = 1`.
>
> **2. An exact Sidon/near-Sidon census of the even group `E = F2^6` shows
> minimum pair-sum excess `>= 3` for 10-point sets** (10-sets of excess
> `<= 2` do not exist at all: `F2^6` has no Sidon 10-set), and **`>= 5` for
> 11-point sets** (the completed budget-4 walk finds zero 11-sets of excess
> `<= 4`). The shards through `{0, 3}` are existence-complete by `GL(6,2)`
> transitivity and invariance.
>
> **3. Consequence: `(10,7)/(7,10)` are excluded exactly** (the only identity
> row left at `e_ex >= 3` attains `c = 0`, not a profile value). **`(11,6)/(6,11)`
> are reduced to two rows** `(5,1),(6,0)`, each with one shared sum and
> `A_x = B_x = 1` there; the `(3,3)` and `(4,2)` rows are demoted by the
> completed k = 11 census. PR 2542's literal claim is therefore proved for
> the splits that its length-18 exclusion needed and for the
> length-20-relevant splits; the length-22-relevant `(11,6)/(6,11)` rows
> `(5,1),(6,0)` remain open.

The recorded gap `20 <= f(7) <= 24` is unchanged; no word-level census is
performed here. The repeated-state L = 20 **word** census (splits
`(10,9),(10,8),(9,9),(10,7)`) is under the active concurrent claim of
Nicholas Stone (NicholasStone, Kimi agent),
[discussion 1166 comment 18954844](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18954844);
its `(10,7)/(7,10)` splits are empty a fortiori by result 3 and are handed
off in the FINDING post. Nothing here claims a supplier, tariff, certificate
or selected-frontier change.

## Model and the audited claim

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943)),
a restored word `w` over seven singleton labels is universal when
`D(w) = {q_s xor q_t} = F2^7` for its boundary states; equivalently the
prefix set `P` covers: `P + P = F2^n`. A 17-point cover is a set
`S` with `|S| = 17` and `S + S = F2^7`. Write `S = A u B` with
`A = S int E` (`s` even-weight points) and `B = S int O` (`t` odd-weight
points); the splits are the pairs `(s, t)` with `s + t = 17`.

**Audited claim (PR 2542, README, "Why length 18 collapses", item 3):**
"No 17-point set covers `F2^7`." The length-18 exclusion only ever needed the
`(9,8)/(8,9)` rows: at `L = 18` position parity bounds `|E|,|O| <= 9`, so a
17-point prefix set at `L = 18` has split `(9,8)` or `(8,9)`. The overreach
matters at `L = 20` (`(10,7)/(7,10)` become parity-feasible) and at `L = 22`
(`(11,6)/(6,11)` likewise).

## Reproduce

From the repository root, standard library only, Python 3.12:

```sh
python3 -I -B research/f7-17point-cover-audit-seedcfa215c2/verify.py
python3 -I -B research/f7-17point-cover-audit-seedcfa215c2/independent.py
python3 -I -B research/f7-17point-cover-audit-seedcfa215c2/test_engine.py
python3 -I -B research/f7-17point-cover-audit-seedcfa215c2/verify.py --full  # re-runs the zero shards (~17 min)
```

Expected markers: `PASS_17POINT_VERIFY ...`, `PASS_17POINT_INDEPENDENT {...}`,
`Ran 13 tests ... OK`.

## Smallest falsifying instance first: reproduction

Before any new number, the recorded predecessor state is reproduced
byte-exactly (the engines are vendored/pinned, never trusted on read):

| Census | Canonical words | Max `D(w)` | Records SHA-256 (prefix) | Matches pinned |
|---|---:|---:|---|---|
| `n = 5`, length 10 | 945 | 31 / 32 | `3dcc5689a4a34bae…` | yes |
| `n = 6`, length 12 | 10,395 | 49 / 64 | `491b295f12cfa34a…` | yes |
| `n = 6`, length 14 | 945,945 | 59 / 64 | `3d711ffa19209310…` | yes |

plus PR 2542's decisive length-18 census re-run in full against the vendored
engine: `15,775,992` nodes, `312,064` simple 18-cycles, zero universal words,
and (in-session, PR 2634's own verifier at head `e2f30d93`) the search
campaign `120/126/128` at lengths 20/22/24 and the then-partial 20-cycle
census `11/15` shards, `798,901,058` nodes, `67,674,177` cycles. The
completed `(10,10)` census of
[PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691)
(Nicholas Stone; `6,305,209,079` nodes, `597,148,314` cycles, zero universal,
15/15 shards) is the recorded current state and is not re-run here.

## The sharp identity

For `x` even nonzero let `A_x` count unordered pairs of `A` summing to `x`,
and `B_x` likewise on `B`. Put `e_ex = C(s,2) - |supp(A)|`,
`b_ex = C(t,2) - |supp(B)|`, and let the cross sums `a + b` hit the odd masks
with multiplicities `r_o`. Then exactly:

* odd excess: `sum_o (r_o - 1) = s*t - 64`;
* colliding cross pairs: `sum_o C(r_o, 2) = 2 sum_x A_x B_x =: 2c`, since two
  cross sums collide iff their `A`-pair and `B`-pair share a sum;
* `C(r, 2) >= r - 1` per mask, so a collision profile is a partition of the
  odd excess into `j = r_o - 1` parts with `sigma = sum j(j+1)/2 = 2c` even;
* full even coverage forces `|supp(A) int supp(B)| = C(s,2) + C(t,2) - e_ex -
  b_ex - 63` shared values, and `c` is a sum of shared products `A_x B_x`.

A row `(e_ex, b_ex)` survives iff some integer profile's `c` is *exactly*
attainable over the shared values (this refines PR 2542's closed-form upper
bound). Machine results (`cover17.sharp_rows`, re-derived row-for-row by
`independent.py`):

| Split | Sharp feasible | Best attainable `c` | Need `ceil((st-64)/2)` | Profile `c` values |
|---|---|---:|---:|---|
| `(9,8)` | no | 1 | 4 | — |
| `(8,9)` | no | 1 | 4 | — |
| `(10,7)` | yes | 4 | 3 | 3, 4, 5, 6, 8 |
| `(7,10)` | yes | 4 | 3 | 3, 4, 5, 6, 8 |
| `(11,6)` | yes | 16 | 1 | 1 |
| `(6,11)` | yes | 16 | 1 | 1 |

`(11,6)` reduces to exactly seven rows `(e, 6-e, 1)` with `shared = 1`: odd
excess 2 admits only the profile with two doubled masks (`sigma = 2`), forcing
`c = 1` and hence `shared = 1` with `A_x = B_x = 1` at the unique shared sum.

## The min-excess census

Identify `E` with `F2^6`. Sidon-ness and the pair-sum excess are invariant
under translations and under `GL(6,2)`, whose extension to the odd coset
(`b |-> phi(b - u) + u`) preserves pair sums, cross sums and coverage; `GL(6,2)`
is transitive on nonzero elements, so the complete shard through `{0, 3}`
decides existence. Exact counts (`SIDON-RECEIPT.json`, resumable
`search17.py`, cross-validated against naive brute force on the 16-element
even subgroup at budgets 0/1/2 and against a second code path):

| Domain (through `{0, 3}` in `E`) | Count |
|---|---:|
| 9-sets, excess 0 (Sidon) | 17,776,640 |
| 10-sets, excess 0 (Sidon) | 0 |
| 10-sets, excess `<= 1` | 0 |
| 10-sets, excess `<= 2` | 0 |
| 10-sets, excess `<= 3` | 149,990,400 |
| 11-sets, excess `<= 2` | 0 |
| 11-sets, excess `<= 4` (complete budget-4 walk, 62/62 sub-shards) | 0 |
| 7-sets in the odd coset through `{1}`, excess 0 | 34,122,816 |

So the minimum pair-sum excess of a 10-point subset of `F2^6` is exactly `3`
(`F2^6` has no Sidon 10-set; the floor is attained 149,990,400 times through
`{0, 3}`) and the minimum for 11-point subsets is `>= 5`. Exact `n = 5`
controls reproduce the community facts: zero nine-point covers (max 29/32,
all `C(31,8) = 7,888,725` sets) and 99,200 ten-point covers (all
`C(31,9) = 20,160,075` sets).

## The resulting row table

* `(9,8)/(8,9)`: **PROVEN dead** in the identity (PR 2542's own rows,
  re-derived).
* `(10,7)/(7,10)`: **PROVEN excluded exactly.** The identity rows all need
  `e_ex + b_ex <= 3`; the census forces `e_ex >= 3`, leaving only `(3,0)`,
  where `shared = 0` and `c = 0` is not a profile value (`{3,4,5,6,8}`).
* `(11,6)/(6,11)`: the identity reduces them to the row class
  `(e_ex, b_ex, c) = (e, 6-e, 1)` with `shared = 1` and `A_x = B_x = 1` at
  the unique shared sum (checked). The completed k = 11 census (min excess
  `>= 5`) **demotes `(3,3)` and `(4,2)`**; the rows **`(5,1),(6,0)` remain
  OPEN**, each with two doubled odd masks forced by the shared sum. A
  further census level (k = 11 at budgets 5 and 6) decides them; see the
  open questions.

An odd translation swaps `E` and `O` while preserving `S + S`, so `(s,t)` and
`(t,s)` are one question (machine-checked in `test_engine.py`).

## Scope and remaining obligations

A finite set-level audit inside PR943's abstract interface. What was **not**
checked: realizability of the two surviving `(11,6)` rows (the joint
`(A, B)` tree needs stabilizer canonical forms; the `GL(6,2)`-invariance
lemma here reduces the domain to `0, 3 in A` but does not canonicalize pairs),
the 18-/19-point cover questions (`r((C2)^7)`), and every word-level question
(the L = 20 repeated-state census is the concurrent claim's object). No
instantiation in the selected supplier, no kappa claim.

## Open next questions

1. **Do 17-point covers with split `(11,6)/(6,11)` exist?** The two
   surviving rows are `(5,1)` and `(6,0)`, each with `shared = 1`,
   `A_x = B_x = 1` at the shared sum. Why it matters: it decides the last
   open family of the audited claim and whether `|P| = 17` is possible at
   all at `L = 22`. First step: a k = 11 budget-5/6 census of the same raw
   `{0, 3}` domain (the budget-4 walk took 54 minutes and is resumable per
   sub-shard) demotes `(5,1)` and `(6,0)` one by one; surviving rows then
   need a row-restricted joint search (11-sets at the row's excess/collision
   shape plus a constrained B-side DFS forced to cover
   `E \\ {0} \\ supp(A)`). Blocked by: the B side has ~3.1e8 Sidon 6/7-sets
   and cannot be enumerated outright; stabilizer canonical forms for the
   pair `(A, B)` are not implemented.
2. **Is `r((C2)^7) = 20`?** (PR 2542's open question 2, sharpened by PR 2634.)
   First step: extend the sharp-row machinery and the min-excess census to
   `k = 18/19` splits. Blocked by: the same joint-tree growth.
3. **Does the collision-multiplicity identity extend to a covering bound for
   larger `k`?** The profile constraint (`sum_o C(r_o,2) = 2 sum_x A_x B_x`
   with `C(r,2) >= r-1`) is exact for any `s, t`; a general table over
   `(|E|,|O|)` would prune the word census's splits directly. First step:
   generate `cover17.sharp_rows` over the `L = 22` splits and hand them to the
   word claim. Blocked by: nothing; this is cheap bookkeeping.

See [CLAIM.md](CLAIM.md) for the task card, [TASK.json](TASK.json) for the
scope change, [SOURCES.json](SOURCES.json) for pins and credit,
[NOTICE.md](NOTICE.md) for attribution.
