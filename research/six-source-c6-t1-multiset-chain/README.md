# Floor words that keep the multiset (6,6,6,7,7,7) on s=4..18

**Constructive witness, plus an exhaustive census of the endpoint splits.
No new κ.** In the unchanged unsigned dirty connector, one six-source
characteristic-6 floor word has diagonal sum `q_s + q_{39-s}` equal to a
permutation of `(6,6,6,7,7,7)` at every index `s = 4,...,18`. The same
statement holds for every constant mask: there are 120 such pure-slide
words, one for each 3-subset of sources and each choice of the final
letter. A second explicit word keeps the multiset while moving the mask
once.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36 and
calls each source exactly six times. `q_t` counts the first `t` letters, so
`q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one basis vector.
Counts stay in `{0,...,6}`. This is the interface of PR4231/PR4248, as used
by PR6141, by the centre classification in PR6955, and by the separation-3
classification in PR7029. Write

```text
S(s) = q_s + q_{39-s}.
```

The one-step identity, for `s = 4,...,17`, is

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{38-s}}.
```

`S(s)` realizes a **weight-3 mask** when every coordinate lies in
`{0,1,6,7,12}` and exactly three coordinates lie in `{1,7}`. The multiset
`(6,6,6,7,7,7)` is one such mask. Its three 7s are the mask coordinates.
PR7029 calls the separation-3 realization of this multiset type T1: it is
the only one of the six families with no coordinate equal to 12, and a
legal step that stays inside the multiset exchanges a 6 with a 7 or leaves
the vector fixed. This package uses that description and does not repeat
the six-family census.

## Endpoint splits

**Lemma 1.** If `S(18)` is a permutation of `(6,6,6,7,7,7)`, then
`q_18 = (3,3,3,3,3,3)` and the three coordinates equal to 7 are exactly the
three letters in positions 18, 19 and 20. There are 20 such count pairs.

**Proof.** Let `r = q_18` and let `δ = q_21 - q_18`. Then `δ_j ≥ 0`,
`∑ δ_j = 3`, `r_j + δ_j ≤ 6`, and `2 r_j + δ_j` is 6 or 7. The pairs
`(r, δ)` in that range are exactly

| `r` | `δ` | sum |
|---:|---:|---:|
| 2 | 2 | 6 |
| 2 | 3 | 7 |
| 3 | 0 | 6 |
| 3 | 1 | 7 |

A coordinate `(2, 3)` consumes all three bridge letters, so every other
`δ` is 0 and every other sum is even. That assignment has one 7. A
coordinate `(2, 2)` consumes two bridge letters and is itself a 6, so at
most one later coordinate has `δ = 1` and there is at most one 7. Every
surviving assignment is therefore three coordinates `(3, 1)` and three
coordinates `(3, 0)`. There are `C(6,3) = 20` of them.

The loop in `verify.py` visits all `4^6` assignments of these rows, keeps
those with early-count sum 18 and bridge sum 3, and finds these 20 pairs
and no others. The domain is complete for a floor word: each bridge
coordinate is an integer in `{0,1,2,3}` because the three bridge letters
are nonnegative and sum to 3, and the cap `r + δ ≤ 6` is the floor-word
cap.

**Lemma 2.** If `S(4)` is a permutation of `(6,6,6,7,7,7)`, the count pair
is one of two types. Let `D = w_35` and let `M = {j : S(4)_j = 7}`.

- Type A, `D ∉ M`. Then `q_4` is 1 on `M ∪ {D}` and 0 elsewhere. There are
  `6 · C(5,3) = 60` pairs.
- Type B, `D ∈ M`. Then `q_4` is 2 at `D`, 1 on `M \ {D}`, and 0 elsewhere.
  There are `6 · C(5,2) = 60` pairs.

**Proof.** A floor word has `q_35 = (6,6,6,6,6,6) - e_D`. For `j ≠ D`,
`S(4)_j = q_4[j] + 6` lies in `{6,7}` only for `q_4[j] ∈ {0,1}`. For `D`,
`S(4)_D = q_4[D] + 5` lies in `{6,7}` only for `q_4[D] ∈ {1,2}`.

If `q_4[D] = 1`, then `D` is a 6. The three 7s are three of the other five
coordinates, each with `q_4 = 1`, and the other two have `q_4 = 0`. The
coordinate sum is `1 + 3 = 4`. If `q_4[D] = 2`, then `D` is a 7 and exactly
two of the other five coordinates have `q_4 = 1`. The coordinate sum is
`2 + 2 = 4`.

`verify.py` visits every vector in `{0,...,6}^6` of sum 4 and every choice
of `D`. There are 126 such vectors and `126 · 6 = 756` pairs. Exactly 60
are type A, 60 are type B, and none has another shape. These 756 pairs are
the `(q_4, w_35)` domain. The census classifies that domain by this
multiset. It does not repeat the separation-3 family count.

## Constant-mask chains

**Proposition.** For every 3-subset `M` and every source `D` there is a
floor word whose sum `S(s)` equals 7 on `M` and 6 off `M` at every
`s = 4,...,18`. The 120 words below realize every endpoint pair in which
the mask at `s = 4` equals the mask at `s = 18`.

Let `Z` be the complement of `M`.

Type A, `D ∉ M`. The prefix is the four sources `M ∪ {D}` in increasing
order, one call each. The early block calls each source in `M ∪ {D}` twice,
in increasing order, then calls each source in `Z \ {D}` three times, in
increasing order. The bridge is `M` in increasing order. The late block is
the reverse of the early block. The final letter is `D`.

Type B, `D ∈ M`. Write `M \ {D} = {a, b}` with `a < b`. The prefix is
`D, D, a, b`. The early block is one `D`, then `a, a, b, b`, then three
calls to each source of `Z` in increasing order. The bridge, late block and
final letter are as in type A.

The early block has length `2 · 4 + 3 · 2 = 14` in type A and
`1 + 2 · 2 + 3 · 3 = 14` in type B. The word has length
`4 + 14 + 3 + 14 + 1 = 36`.

Each source is called six times. In type A a source in `M` contributes
`1 + 2 + 1 + 2`, the source `D` contributes `1 + 2 + 0 + 2 + 1`, and either
remaining source contributes `0 + 3 + 0 + 3`. In type B the source `D`
contributes `2 + 1 + 1 + 1 + 1`, either other source in `M` contributes
`1 + 2 + 1 + 2`, and each source in `Z` contributes `0 + 3 + 0 + 3`.

The resulting `q_18` is identically 3. In type A the four sources
`M ∪ {D}` go from 1 to 3 and the other two go from 0 to 3. In type B the
source `D` goes from 2 to 3, the other mask sources go from 1 to 3, and
`Z` goes from 0 to 3. The bridge then puts `q_21` at 4 on `M` and 3 off
`M`, so

```text
S(18) = 7 on M and 6 off M.
```

The same vector is `S(4)`. Indeed `q_35` is 5 at `D` and 6 elsewhere, and
the prefix counts of the two types are exactly the counts in Lemma 2.

For each `i = 0,...,13` the letter in position `4 + i` is the `i`-th early
letter, and the letter in position `34 - i` is the matching entry of the
reversed late block. Those two letters are equal, so each of the 14 steps
adds and subtracts the same basis vector. Therefore `S(s)` is constant on
`s = 4,...,18`.

One displayed type-A word, `M = {0,1,2}` and `D = 3`, is

```text
012300112233444555012555444332211003
```

`verify.py` checks all 120 words, 60 of each type, including this string.

## One chain whose mask moves

Equal endpoint masks are sufficient, and they are not necessary. The word

```text
012340011223344555014555443322110023
```

has mask `{0,1,2}` at `s = 4` and mask `{0,1,4}` at every
`s = 5,...,18`.

Read it as the prefix `0123`, the early block `4` followed by
`00112233444555`, the bridge `014`, the late block `55544332211002`, and
the final letter `3`. The early counts are `(2,2,2,2,3,3)` and the late
counts are `(2,2,3,2,2,3)`. Adding the prefix `(1,1,1,1,0,0)`, the bridge
`(1,1,0,0,1,0)` and the final letter `3` gives six calls of each source.
The length-18 prefix is identically 3, and the bridge is `{0,1,4}`, so

```text
S(18) = (7,7,6,6,7,6).
```

The length-4 prefix is `(1,1,1,1,0,0)` and `q_35 = (6,6,6,5,6,6)`, so

```text
S(4) = (7,7,7,6,6,6).
```

Position 4 holds 4 and position 34 holds 2, hence

```text
S(5) = S(4) + e_4 - e_2 = (7,7,6,6,7,6).
```

Positions `5,...,17` are `00112233444555`, and positions `33,...,21` are
that block reversed, so the other thirteen steps are pure slides. The sum
stays `(7,7,6,6,7,6)` through `s = 18`.

The move closure of the multiset allows this exchange of a 6 with a 7.
The two endpoint splits are different: `q_4 = (1,1,1,1,0,0)` with late
deficit at source 3, while `q_18` is identically 3 and the bridge is
`{0,1,4}`. The sum multiset does not determine the split.

## Scope of the claim

This is a constructive witness for the existence question, an explicit
construction for every constant-mask endpoint pair, and an exhaustive
finite census of the two endpoint domains in Lemmas 1 and 2. The census
domains are finite, the loops visit every element, and the counts match
the binomial closed forms above.

The witness shows that the diagonal chain for this multiset is nonempty.
PR7029 already shows that type T1 is incompatible with its hypothesis (H1),
the weight-3 shape at `(0, 9)`: that shape needs a coordinate 6 in `q_9`,
while Lemma 1 forces every coordinate of `q_18`, hence of `q_9`, to be 3.
The displayed constant word has `q_9 = (3,3,2,1,0,0)`. These words sit in
the case that theorem leaves open, and they give that case a positive
instance. The joint exclusion under (H1) and (H2) is unchanged.

The unrestricted six-source depth-two exclusion remains the solver verdict
of PR6141. A word that keeps this one multiset on `s = 4,...,18` is a
special case of the diagonal hypothesis (H2) in PR7029. It is not a
classification of every weight-3 shape on that diagonal, and it is not a
human proof of the depth-two statement. No DRAT certificate is emitted.
No supplier, consumer, or selected frontier changes.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-t1-multiset-chain/verify.py
python3.12 -I -O -W error -B research/six-source-c6-t1-multiset-chain/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-t1-multiset-chain --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_T1_MULTISET_CHAIN rows=4 splits18=20 splits4=120 domain4=756 constant_words=120 moving_mask_changes=1 controls=10
```

The ten controls check the local row table, both split censuses, all 120
constant-mask words, a late block copied in the early order, a block-layered
T1 slot that meets the multiset only at `s = 18`, the moving word, the
displayed `(0, 9)` sum, a word with seven calls of one source, and the
one-step identity on the moving word. Failures raise `SystemExit`.
Optimized mode cannot silence them. No Lean, Docker, or solver replay was
run.

## Open next questions

1. Which endpoint pairs with unequal masks are joined by a monotone chain
   of this multiset? *Why it matters:* every equal-mask pair is realized
   above, and one unequal pair is realized by the moving word, so existence
   is settled. The remaining question is the boundary of mask transport
   inside `(6,6,6,7,7,7)`. A missing pair would be an obstruction that uses
   neither the `(0, 9)` hypothesis nor a frozen 12. A complete yes would
   mean this multiset imposes no further diagonal obstruction beyond
   Lemmas 1 and 2. Either answer stays short of the unrestricted c=6
   exclusion. *First step:* search the finite `(r, f)` graph for one
   symmetry class, `M_4 = {0,1,2}`, `D = 3`, `M_18 = {3,4,5}`, where `r`
   is the number of early letters still to place and `f` is the number of
   late letters still to place. *Blocked by:* the constant-mask proof uses
   equal early and late budgets on each source, and those budgets differ
   as soon as the masks differ. This package does not search that graph.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR4231, PR4248, PR6107), with the Ross Richardson PR934/PR943 lineage.
JosieElliston's PR6141 records the c=6 solver verdict. PR6955 classifies
the empty centre and leaves the separation-3 slot open. PR7029, head
`8fe9a44a114efd4d3718208fd8f7c592fd03af62`, classifies that slot, isolates
type T1 as the family with no frozen 12, and asks the question answered
here. The six-family census and the price of the mask at `(0, 9)` are not
re-proved. Nick Petalas's handoff on 2026-11-03
([discussion comment 19384981](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19384981))
states the diagonal slot count. The upstream finding that records the open
question is
[discussion comment 19514157](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514157).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
