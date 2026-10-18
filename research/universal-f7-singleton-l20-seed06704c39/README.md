# KB3b — seven-source singleton `f(7)` continued: obstructions, cover dichotomy, resumable 20-cycle census

**Recursive-interface finite result: the `L = 19` question is closed exactly, the
two natural Gray-beating templates are closed by proved lemmas, and the
`L = 20` / `L = 22` word question is advanced to a reproducible search ceiling
plus a resumable census. No new kappa.**

In the PR943 prefix-walk model
([Ross Richardson, `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943)),
a restored source word `w` over seven singleton labels is *universal* when
paired readouts realize every mask, `D(w) = {q_s xor q_t} = F2^7`, and `f(n)` is
the minimum word length. The pinned record
([Douglas Colkitt, `research/universal-connector-six-source`](https://github.com/CrocSwap/integer-mult-bounds/pull/1185))
is `f(5) = 12`, `f(6) = 16`, `18 <= f(7) <= 24`; the predecessor of this
package removed 18
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542), `f(7) >= 20`),
so the recorded gap is `20 <= f(7) <= 24`, with the Gray bound 24 attained.

This package continues the question (kappa-blocker KB3b) and delivers:

> **1. Length 19 is closed exactly — but for a structural reason.** Every
> restored word has even length (all label counts are even and `>= 2`), so no
> odd length exists to census. The assignment's literal "exclude length 19" is
> discharged by PR943's restoration facts, and the census step-up from 18 is
> `L = 20`.
>
> **2. Two natural Gray-beating templates are impossible** (proved lemmas,
> machine spot-checked): the *disjoint product* family cannot beat 24 in even
> length, and the *square-detour / transversal* family has no realization at
> any length (its walk forces a connected transversal, which cannot cover).
>
> **3. Set covers of `F2^7` at 20 points exist** (explicit verified example
> below; set-ILS finds them in 14 of 30 restarts) — but every cover sampled
> (463 at `k = 20/22`) has isolated vertices in the hypercube, hence admits no
> closed walk at any length. Walk-shaped sets and covering sets look disjoint
> at `k <= 22`: this is quantified evidence, not an exclusion.
>
> **4. A deterministic search campaign with an `L = 24` non-vacuity control**
> tops out at `120/128` (length 20), `126/128` (length 22) and finds `128/128`
> at length 24 (control). Extended 600-restart runs confirm both ceilings.
> These are search failures, not exclusions.
>
> **5. A resumable restricted-growth simple-20-cycle census** (the `|P| = 20`,
> `(10,10)` split of `L = 20`, with PR 2542's proved-necessary prunes and the
> split-identity budget `e_ex + b_ex <= 27`) runs to the priced budget with
> exact per-shard node counts checkpointed in `CENSUS20-PROGRESS.json`.

The gap `20 <= f(7) <= 24` is unchanged; no supplier, tariff, certificate or
selected-frontier change is claimed. The DUO pair-source line
([https://github.com/CrocSwap/integer-mult-bounds/pull/2396](https://github.com/CrocSwap/integer-mult-bounds/pull/2396),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2156](https://github.com/CrocSwap/integer-mult-bounds/pull/2156))
and the sparse weight-1/2/3 family
([https://github.com/CrocSwap/integer-mult-bounds/pull/2229](https://github.com/CrocSwap/integer-mult-bounds/pull/2229),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2397](https://github.com/CrocSwap/integer-mult-bounds/pull/2397))
are distinct alphabets or mask families.

## Model (two equivalent forms)

PR943's: dirty `F2` arrays, complete calls `B_j: z += B_j x_j`, paired output
readouts; the boundary states `q_t` walk the hypercube from 0 and `D(w)` is the
set of pairwise XORs of the boundary states. Universality is `P + P = F2^n`
for the prefix set `P`. Equivalently — the form used by the search here —
`D(w)` is the set of XORs of *contiguous subwords* of `w` (interval XORs), plus
the empty block for the zero mask. Restored words have every label count even
and `>= 2`, so lengths are even and walks are closed.

## Reproduce

From the repository root, standard library only, Python 3.12:

```sh
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/verify.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/independent.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/test_engine.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/census20.py   # resumable
```

Expected markers: `PASS_F7_L20_VERIFY ...`, `PASS_F7_L20_INDEPENDENT {...}`,
`Ran 14 tests ... OK`, and `CENSUS20 COMPLETE|PARTIAL shards=... nodes=...`.
The deterministic search campaign is `search.py` (CI-sized); `search.py
--extended` runs the 600-restart session budget.

## Smallest falsifying instance first: reproduction

Before any new number, `verify.py` rebuilds the pinned
[`research/universal-connector-six-source/EXPECTED.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/main/research/universal-connector-six-source/EXPECTED.json)
byte-for-byte (histograms and records SHA-256 included):

| Census | Canonical words | Max `|D(w)|` | Records SHA-256 (prefix) | Matches pinned |
|---|---:|---:|---|---|
| `n = 5`, length 10 | 945 | 31 / 32 | `3dcc5689a4a34bae…` | yes |
| `n = 6`, length 12 | 10,395 | 49 / 64 | `491b295f12cfa34a…` | yes |
| `n = 6`, length 14 | 945,945 | 59 / 64 | `3d711ffa19209310…` | yes |

plus the counting lower bounds `10/14/18` and the Gray constructions
`12/16/24`. It then **fully re-runs PR 2542's decisive census** and reproduces
`15,775,992` nodes, `312,064` simple 18-cycles, zero universal words — the
predecessor engine is vendored byte-exact (SHA-256 pinned in `SOURCES.json`,
enforced by `test_engine.py`) and its numbers are not taken on trust.

## The exact obstructions

**Parity (closes length 19, and every odd length).** A restored word has each
label count even, so `|w|` is even; equivalently the cube is bipartite and a
closed walk has even length. `patterns(7, 19)` is empty and the test asserts
it. This is PR943's restoration fact, recorded here because the assignment's
option (a) asked for the length-19 exclusion literally.

**Square-detour / transversal template.** The most structured way to beat 24
is a subcycle through a 16-point set `R` in a half-space plus a 6-call detour
`[6, i, j, i, j, 6]` over a coordinate square `sq = span(e_i, e_j)`. Odd-mask
coverage then forces `|R|·|sq| = 64`, so `R` is a transversal of `sq`; write
`R = {t + g(t) : t in F2^4}`. Two induced-cube facts close it:

* `G[R]` has an edge between `t + g(t)` and `t' + g(t')` only when
  `t' = t + e_k` and `g(t) = g(t')` (a transversal has no two points in one
  `sq`-coset). So the components of `G[R]` are the components of the level
  sets of `g`. Any closed walk spanning `R` needs `G[R]` connected, i.e. `g`
  constant.
* But `g` constant makes `R + R` the 16-point plane `F2^4 x {q}`, missing 48
  of the 64 masks needed from within-layer sums.

So no word of this template is universal at any length. The two component
claims are machine spot-checked (`test_engine.py::TestTransversalLemma`).

## The cover / walk dichotomy at `k = 20` and `k = 22`

Set-ILS (`search.py::set_search`, steepest ascent over point swaps) finds
covering sets easily:

| `k` | covers found | first cover's induced degrees | closed walk? |
|---:|---:|---|---|
| 18 | 0 (max 118/128, 40 restarts) | — | — |
| 19 | 0 (max 124/128, 200 restarts) | — | — |
| 20 | 14 / 30 restarts | `[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,2,2,2,2,3]` | no (min degree 0) |
| 22 | 28 / 30 restarts | `[0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,2,2,2,3]` | no (min degree 0) |

The stored `cover20` (20 points, verified `|P + P| = 128` exactly) is the
deterministic first cover of the campaign. Every cover sampled at `k = 20/22`
(175 and 288 in the session sweeps, plus the campaign's) has an isolated
vertex, so no closed walk spans it at *any* length. Conversely the word-side
search below never reaches a cover. This is the `n = 5` dichotomy
(99,200 ten-point covers, none cycle-realisable, `f(5) = 12`) at `n = 7`, and
it is quantified evidence only: no lemma yet separates the two families.

## Search campaign (deterministic, with non-vacuity control)

`search.py` runs steepest-ascent ILS over restored words (transpositions,
segment reversals, kicks) and over sets, fixed seeds:

| Stage | Budget | Result |
|---|---|---|
| word `L = 24` (control) | 30 restarts | **128/128 found** (`[0,1,2,5,2,3,4,3,6,4,3,5,0,4,2,1,0,3,1,0,4,1,6,2]`) |
| word `L = 22` | 40 restarts | 126/128 (missing 2) |
| word `L = 20` | 40 restarts | 120/128 (missing 8) |
| extended `L = 22` | 600 restarts | 126/128 (confirmed) |
| extended `L = 20` | 600 restarts | 120/128 (confirmed) |

The control is the point: the same optimizer finds the known universal 24-word
(and a non-Gray one) in seconds, so the 126/120 ceilings are landscape, not
tool failure. The predecessor's annealer had already reported 126/128 at
length 22; the ceilings here agree and add the `L = 20` and control numbers.

## The resumable simple-20-cycle census

`census20.py` enumerates every canonical restored length-20 word with distinct
boundary states (a simple 20-cycle; `|P| = 20` forces the `(10,10)` split)
using PR 2542's proved-necessary prunes: multiplicity room, self-avoidance
(justified by `|P| = L` here) and the pair-representation collision budget
`e_ex + b_ex <= 27`. Shards are the Bell(4) = 15 restricted-growth depth-4
prefixes, exactly one per canonical word;
`CENSUS20-PROGRESS.json` checkpoints each subtree, so the census resumes and a
partial run still records exact node/leaf counts. **Status at submission
(2026-10-15): 11 of 15 shards complete, covering 798,901,058 nodes and
67,674,177 simple 20-cycles with zero universal words.** The small shards die
instantly on the self-avoidance prune (27 nodes total); the completed heavy
shard `0102` alone accounts for 798,901,031 nodes and 67,674,177 cycles. The
three remaining heavy subtrees (`0120`, `0121`, `0123`) are of the same order —
a capped probe of `0123` passes 5,000,000 nodes in 21.4 s (234,169 nodes/s) —
so completing the `(10,10)` exclusion needs several more hours of the same
exact enumeration, resumed from the checkpoint. No universal word appears in
the 67.7 million cycles checked so far.

Length-20 words with repeated boundary states (`|P|` in `{17, 18, 19}`) are
**not** covered by this census; the L = 20 split identity admits `(10,7)` /
`(7,10)` and `(10,8)` / `(8,10)` / `(9,9)` / `(10,9)` families, which need
multiset collision semantics with per-split budgets. That is the recorded open
remainder of option (a).

## Scope and remaining obligations

A finite study inside PR943's abstract interface; no instantiation in the
selected supplier and no kappa claim. What was **not** checked: the repeated-
state `L = 20` splits, the `L = 22` census splits, and any set-level exhaustive
enumeration (the joint tree needs orbit reduction, as PR 2542 records).
Common-label/mutable-source realization, frames, owner admission, full-row
charging, compiler integration and precision remain as PR943 lists them.

## Open next questions

1. **Does a universal `L = 20` or `L = 22` word with repeated boundary states
   exist, or is the Gray bound 24 sharp?** Why it matters: it settles
   `f(7) in {20, 22, 24}`. First step: extend `census20.py` to the repeated-
   state splits with per-split budgets from `lemma_a_table`, and the simple
   `(11,11)` split at `L = 22`. Blocked by: multiset collision semantics per
   split and tree growth past the simple-cycle census.
2. **Is `r((C2)^7) = 20`?** (PR 2542's open question 2 sharpened: 20-point
   covers exist, 19-point ones were not found in 200 restarts.) First step:
   shard the joint `(E, O)` enumeration for the `k = 19` splits or orbit-reduce
   under the 5,040 coordinate permutations. Blocked by: the raw joint tree.
3. **Are covers and walk-shape incompatible at `k <= 22`?** Every sampled
   cover has an isolated vertex. A proof would give `f(7) = 24` together with
   the `L = 22` exclusion. First step: constrained search maximizing `|P+P|`
   over cycle-shaped sets, or an autocorrelation obstruction for sets
   containing a Hamiltonian cycle. Blocked by: no structural lemma yet.

See [CLAIM.md](CLAIM.md) for the task card, [TASK.json](TASK.json) for the
scope change, [SOURCES.json](SOURCES.json) for pins and credit,
[NOTICE.md](NOTICE.md) for attribution.
