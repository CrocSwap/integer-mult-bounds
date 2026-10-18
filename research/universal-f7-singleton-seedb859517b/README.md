# Seven-source singleton universal path: `f(7) >= 20`

**Recursive-interface finite result: the sharp singleton `f(7)` gap narrows
from `18 <= f(7) <= 24` to `20 <= f(7) <= 24`. No new kappa.**

In the PR943 prefix-walk model
([Ross Richardson's `research/universal-connector-boundary`](https://github.com/CrocSwap/integer-mult-bounds/pull/943)),
a restored source word `w` over `n` singleton labels is *universal* when paired
output readouts realize every binary row mask, `D(w) = {q_s xor q_t} = F2^n`,
and `f(n)` is the minimum length of a universal word. The pinned record from
[Douglas Colkitt's six-source package](https://github.com/CrocSwap/integer-mult-bounds/pull/1185)
is `f(5) = 12`, `f(6) = 16` and `18 <= f(7) <= 24`, with `f(7)` explicitly open
("neither 18, 20 nor 22 is excluded, and 24 is attained"). This package removes
18 from the gap in the singleton alphabet:

> **No universal seven-source word of length 18 exists. Hence `f(7) >= 20`.**

The DUO pair-source alphabet
([https://github.com/CrocSwap/integer-mult-bounds/pull/2396](https://github.com/CrocSwap/integer-mult-bounds/pull/2396),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2156](https://github.com/CrocSwap/integer-mult-bounds/pull/2156))
and the 63-mask weight-1/2/3 sparse family
([https://github.com/CrocSwap/integer-mult-bounds/pull/2229](https://github.com/CrocSwap/integer-mult-bounds/pull/2229),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2236](https://github.com/CrocSwap/integer-mult-bounds/pull/2236),
[https://github.com/CrocSwap/integer-mult-bounds/pull/2397](https://github.com/CrocSwap/integer-mult-bounds/pull/2397))
are different alphabets or different mask families; nothing here touches them.

## Reproduce

From the repository root, standard library only, Python 3.12:

```sh
python3 -I -B research/universal-f7-singleton-seedb859517b/verify.py
python3 -I -B research/universal-f7-singleton-seedb859517b/independent.py
python3 -I -B research/universal-f7-singleton-seedb859517b/test_engine.py
```

Expected markers:

```text
PASS_F7_SINGLETON_GAP_VERIFY f(7) >= 20 (length 18 excluded) cycles=312064 universal_words=0 nodes=15775992
PASS_F7_INDEPENDENT {...}
Ran 22 tests ... OK
```

The decisive census itself is `search.py` (about 15 minutes including the
reproduction tiers; resumable from `CERTIFICATE-PROGRESS.json`, one checkpoint
per shard):

```sh
python3 -I -B -u research/universal-f7-singleton-seedb859517b/search.py
# PASS_F7_SINGLETON_GAP f(7)>=20 L18-excluded
```

## Smallest falsifying instance first: reproduction

Before any new number, the engine rebuilds the pinned
[`research/universal-connector-six-source/EXPECTED.json`](https://github.com/CrocSwap/integer-mult-bounds/blob/main/research/universal-connector-six-source/EXPECTED.json)
byte-for-byte, including records SHA-256:

| Census | Canonical words | Max `|D(w)|` | Records SHA-256 (prefix) | Matches pinned |
|---|---:|---:|---|---|
| `n = 5`, length 10 | 945 | 31 / 32 | `3dcc5689a4a34bae…` | yes |
| `n = 6`, length 12 | 10,395 | 49 / 64 | `491b295f12cfa34a…` | yes |
| `n = 6`, length 14 | 945,945 | 59 / 64 | `3d711ffa19209310…` | yes |

It also reproduces the counting lower bounds `10, 14, 18` for `n = 5, 6, 7`
and the Gray constructions of lengths `12, 16, 24`. The pinned record is
`f(5) = 12` (the assignment placeholder "f(5)=16" was corrected by reading the
pinned package, as instructed).

## Why length 18 collapses to a census of simple 18-cycles

Let `P` be the set of prefix parity states of a length-`L` word (`0 in P`),
`E` the even-weight elements and `O` the odd-weight ones. Universality is
exactly `P + P = F2^n`, and weight parity splits the pair sums: odd masks come
only from `E + O`, even masks only from `E + E` and `O + O`.

1. **Position parity.** At `L = 18` the walk has 9 even and 9 odd boundary
   positions (the closing state repeats the start), so `|E|, |O| <= 9`.
2. **Counting.** Full coverage needs `|E||O| >= 64` and
   `C(|E|,2) + C(|O|,2) >= 63`. This already excludes `L <= 16` and every
   split with `|P| <= 16` at `L = 18`.
3. **Lemma A (pair-representation identity).** Write `A_x` for the number of
   unordered pairs of `E` summing to `x`, `B_x` likewise on `O`, and
   `e_ex = C(|E|,2) - |supp(A)|`, `b_ex` similarly. Full odd coverage with
   `|E||O|` pairs forces `sum_x A_x B_x >= ceil((|E||O| - 64)/2)`, while full
   even coverage forces `|supp(A) int supp(B)| = C(|E|,2) + C(|O|,2) - e_ex -
   b_ex - 63` and hence `sum_x A_x B_x <= |S| + e_ex + b_ex + e_ex*b_ex`. For
   the 17-point splits `(9,8)` and `(8,9)` these bounds are `>= 4` against
   `<= 1`: contradictory. **No 17-point set covers `F2^7`.** (The same lemma,
   applied at `n = 5`, explains the community census fact that no nine-point
   set of `F2^5` covers, maximum 29, without enumeration.)
4. So `|P| = 18`, the split is `(9,9)`, and the 18 boundary states are
   distinct: **every universal 18-word would be a simple 18-cycle** through 18
   vertices of the 7-cube, with both sides Sidon-ish (`e_ex + b_ex <= 9`).

The identity rows are machine-checked (`lemma_a_table`) and independently
re-derived by an explicit collision-multiset enumeration
(`independent.py`: `best_sum_AB=1 need=4` for `(9,8)`/`(8,9)`).

## The decisive census

`engine.cyclic_census(7, 18, budget=9, simple=True)` enumerates every
restricted-growth direction word of length 18 (complete under coordinate
relabeling, a hypercube automorphism) with the proved-necessary prunes above:
multiplicity room, self-avoidance, and the pair-representation collision
budget. Sharded by depth-3 prefix (the five shards partition the tree; leaf
counts agree with an unsharded run to the last leaf):

```text
nodes=15,775,992  simple 18-cycles=312,064  universal words=0
```

Zero universal words: length 18 is excluded, so `f(7) >= 20`.

## Controls and non-vacuity

* The cyclic census's leaf set at `n = 5`, length 10 and `n = 6`, length 12 is
  **exactly** the pinned canonical word set (set equality, not just counts).
* Zero universal words at `n = 5`, length 10 and `n = 6`, length 14,
  reproducing `f(5) = 12` and `f(6) = 16` from the other side.
* Planted hits: the census does find universal words at `n = 5`, length 12 and
  `n = 6`, length 16 (the known values), and each found word is re-checked by
  `word_is_universal`.
* The set-level engine cross-checks against brute force at `n = 5`: all
  C(31,9) = 20,160,075 ten-point sets give 99,200 covers, and the independent
  `(E,O)` joint search finds exactly the same 99,200; none of them is
  cycle-realisable, re-confirming `f(5) = 12` at the set level. The
  7,888,725-set nine-point census reproduces the community result (maximum 29,
  zero covers).
* `independent.py` re-checks coverage with the dual predicate (`m` covered iff
  `(P xor m)` meets `P`), realizes cycles with subset dynamic programming
  instead of DFS, and re-derives the lemma rows without the closed-form bound.

## Scope and remaining obligations

A finite exclusion inside PR943's abstract interface. It does not instantiate
that interface in the selected supplier and claims no kappa, supplier or
selected-frontier change. The gap is now `20 <= f(7) <= 24`: the remaining
question is whether a universal seven-source word of length 20 or 22 exists,
or whether the Gray bound 24 is sharp. Common-label/mutable-source
realization, frames, owner admission, full-row charging, compiler integration
and precision remain as PR943 lists them.

## Open next questions

1. **Does a universal length-20 or length-22 seven-source singleton word
   exist?** Why it matters: it would lower the singleton bound `f(7) <= 24`
   and the all-127-row batch bill. First step: run
   `cyclic_census(7, 20, simple=False, budget=None)`-style enumeration with
   the split identity rows for `L = 20` (`(10,8)`, `(10,9)`, `(10,10)`,
   `(9,9)`) computed by `lemma_a_table`, starting with the tightest split.
   Blocked by: at `L = 20` the identity no longer forces a simple walk or a
   unique split, so the SAW and budget prunes must be derived per split, and
   the word count grows well past the length-18 tree.
2. **Do 18-point covers of `F2^7` exist at all?** This package proves none is
   cycle-realisable; the set-level question is the restricted addition basis
   value `r((C2)^7)` (the community records `r((C2)^6) = 14` after Gavrylkiv).
   First step: shard `joint_covers(7, [(9, 9)])` by the least element and
   enumerate the Sidon 9-set pairs under the shared-support identity
   (`|S| = 9 - e_ex - b_ex`, `sum A_x B_x >= 9`). Blocked by: the raw joint
   tree exceeds a single session (the unsharded DFS stalls in the odd-side
   fill); orbit reduction under the 5,040 coordinate permutations is needed.

See [CLAIM.md](CLAIM.md) for the task card, [TASK.json](TASK.json) for the
scope change and budget, [SOURCES.json](SOURCES.json) for pins and concurrent
scopes, [NOTICE.md](NOTICE.md) for attribution.
