# Every T1 endpoint pair has a monotone chain

**Proof, checked on the finite endpoint domain. No new κ.** In the
unchanged unsigned dirty connector, every endpoint pair of the multiset
`(6,6,6,7,7,7)` is joined by a floor word whose diagonal sum stays that
multiset at every index `s = 4,...,18`. There are 2400 such pairs. The
120 pairs with equal masks were already constructed in PR #7042. The
other 2280 pairs, those whose masks differ, are constructed here. The
named symmetry class `M_4 = {0,1,2}`, `D = 3`, `M_18 = {3,4,5}` is one
of them.

The selected conditional κ remains `781451/250000000` in
`certificates/selected-result.json`.

## Interface, unchanged

A floor word on `k = 6` sources in characteristic `c = 6` has length 36
and calls each source exactly six times. `q_t` counts the first `t`
letters, so `q_0 = 0`, `q_36 = (6,6,6,6,6,6)`, and each step adds one
basis vector. Counts stay in `{0,...,6}`. This is the interface of
PR4231/PR4248, as used by PR6141, PR6955, PR7029 and PR7042. Write

```text
S(s) = q_s + q_{39-s}.
```

The one-step identity, for `s = 4,...,17`, is

```text
S(s+1) = S(s) + e_{w_s} - e_{w_{38-s}}.
```

`S(s)` realizes the multiset `(6,6,6,7,7,7)` when three coordinates are
7 and the other three are 6. The mask is the set of coordinates equal
to 7. A step stays inside the multiset exactly when it is a pure slide
`w_s = w_{38-s}`, or it replaces one mask source by one source outside
the mask. PR7029 calls this multiset type T1: it is the only
separation-3 family with no coordinate equal to 12.

## Endpoint domain

The two endpoint lemmas are those of PR7042. They are re-enumerated
here so the transport statement does not depend on an external census.

**Lemma 1.** If `S(18)` is a permutation of `(6,6,6,7,7,7)`, then
`q_18 = (3,3,3,3,3,3)` and the bridge `w_18 w_19 w_20` is a permutation
of the three mask sources. There are 20 masks.

**Lemma 2.** If `S(4)` is a permutation of `(6,6,6,7,7,7)` and `D = w_35`,
the length-4 prefix is determined by the mask `M_4` and `D`.

- Type A, `D ∉ M_4`. Then `q_4` is 1 on `M_4 ∪ {D}` and 0 elsewhere.
  There are 60 pairs.
- Type B, `D ∈ M_4`. Then `q_4` is 2 at `D`, 1 on `M_4 \ {D}`, and 0
  elsewhere. There are 60 pairs.

An **endpoint pair** is a triple `(M_4, D, M_18)` from these two
domains. There are `120 · 20 = 2400` pairs, of which 120 have
`M_4 = M_18` and 2280 do not. `verify.py` visits every candidate row
in the lemma-1 table and every sum-4 vector with every final letter,
and these are the only survivors.

## Budget identity

Fix an endpoint pair. The letters outside the middle are the length-4
prefix, the bridge, and the final letter `D`. The 14 early letters
`w_4,...,w_17` and the 14 late letters `w_21,...,w_34` must make up the
remaining calls. Their budgets are

```text
E_j = 3 - q_4[j],
L_j = 3 - 1_{j in M_18} - 1_{j = D}.
```

Both are nonnegative, and each sums to 14. In either type,
`q_4[j] - 1_{j = D}` is 1 on `M_4` and 0 off `M_4`, so

```text
L_j - E_j = 1_{j in M_4} - 1_{j in M_18}.
```

Write `X = M_4 \ M_18` and `Y = M_18 \ M_4`. Then `L_j - E_j` is `+1` on
`X`, `-1` on `Y`, and `0` elsewhere. In particular `|X| = |Y|`.

## Construction

Order `X = (x_0,...,x_{t-1})` and `Y = (y_0,...,y_{t-1})` increasingly,
where `t = |X|`. The 14 paired steps `(a_i, b_i)`, with
`a_i = w_{4+i}` and `b_i = w_{34-i}`, are

1. the `t` swaps `(y_k, x_k)`,
2. then, for each source `j` from 0 through 5, exactly
   `E_j - 1_{j in Y}` slides `(j, j)`.

The slide quota equals `L_j - 1_{j in X}`, so it is a nonnegative
integer, and the early and late letters meet `E` and `L`. The prefix is
the increasing list `M_4 ∪ {D}` in type A, and `D, D` followed by the
increasing list `M_4 \ {D}` in type B. The bridge is the increasing list
`M_18`. The final letter is `D`.

For `M_4 = {0,1,2}`, `D = 3` and `M_18 = {3,4,5}` the word is

```text
012334500112234455345554432211002103
```

## Proof

The prefix realizes `q_4`, and `q_35 = (6,6,6,6,6,6) - e_D`. The same
arithmetic as Lemma 2 gives `S(4)` the mask `M_4`. The early budget is
`E_j = 3 - q_4[j]`, so `q_18` is identically 3. The bridge then gives
`S(18)` the mask `M_18`. Every source is called

```text
q_4[j] + E_j + 1_{j in M_18} + L_j + 1_{j = D} = 6
```

times, so the word is a floor word.

The mask starts at `M_4`, which contains every source in `X` and none
in `Y`. The `k`-th swap takes `b = x_k`, still in the mask, and
`a = y_k`, still outside it. Those two sets are disjoint, so the step
is a legal T1 exchange: it removes `x_k` and adds `y_k`. After all `t`
swaps the mask is `(M_4 \ X) ∪ Y = M_18`. Each later step is a slide,
which does not change `S`. Every intermediate sum is therefore the
multiset `(6,6,6,7,7,7)`, and the masks at the two ends are the masks
of the endpoint pair.

This argument does not depend on `M_4` and `M_18` being equal. It is a
proof for every one of the 2400 pairs, not a sample. The program builds
each word and checks the floor-word count, the fifteen diagonal sums,
and the two endpoint masks. The domain loops are exhaustive: every
4-row assignment and every sum-4 vector is visited.

## Scope

The result says that type T1 imposes no further diagonal obstruction
beyond Lemmas 1 and 2. A chain for this one multiset is not a
classification of the families that contain a 12, and it is not a human
proof of the six-source depth-two exclusion. PR7029 still excludes this
multiset under the weight-3 shape at `(0, 9)`, because that shape needs
a coordinate 6 in `q_9` while Lemma 1 forces every coordinate of `q_18`
to be 3. No supplier, consumer, or selected frontier changes. No DRAT
certificate is emitted.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -W error -B research/six-source-c6-unequal-mask-transport/verify.py
python3.12 -I -O -W error -B research/six-source-c6-unequal-mask-transport/verify.py
python3.12 -B scripts/research_package.py --package research/six-source-c6-unequal-mask-transport --check-only
```

The marker is

```text
PASS_SIX_SOURCE_C6_UNEQUAL_MASK_TRANSPORT splits18=20 splits4=120 pairs=2400 unequal=2280 equal=120 controls=4
```

The two domain loops and all 2400 words are the census. The marker's
`controls=4` counts the predecessor moving word
`012340011223344555014555443322110023`, the pinned named word, one
floor word whose first exit lies outside the start mask, and one word
with seven calls of a source. Failures raise `SystemExit`. Optimized
mode cannot silence them. No Lean, Docker, or solver replay was run.

## Open next questions

1. Which endpoint pairs of separation-3 type T2, the multiset
   `(0,6,7,7,7,12)`, are joined by a monotone chain on `s = 4,...,18`?
   *Why it matters:* T1 is the only separation-3 family with no
   coordinate 12, and a 12 is fixed by every legal weight-3 step. A T2
   obstruction would be a diagonal constraint that this transport does
   not see. A complete yes would mean the frozen 12 and the three mask
   coordinates can be moved independently inside that family. Either
   answer stays short of the unrestricted c=6 exclusion. *First step:*
   fix the frozen 12 at source 5, take start mask `{0,1,2}` and end
   mask `{0,1,3}`, and decide whether one explicit word keeps
   `(0,6,7,7,7,12)` at every `s = 4,...,18`. *Blocked by:* the exchange
   used above replaces a 6 by a 7. It is not a legal step once a
   coordinate is 12. This package does not build a T2 word.

## Credit

The depth-two interface and the weight identity are Nick Petalas's
(PR4231, PR4248, PR6107), with the Ross Richardson PR934/PR943 lineage.
JosieElliston's PR6141 records the c=6 solver verdict. PR6955 classifies
the empty centre. PR7029, head
`8fe9a44a114efd4d3718208fd8f7c592fd03af62`, isolates type T1 as the
family with no frozen 12. PR7042, head
`807149a85d185b8272aa1fda43ba6d8d7c541cfe`, classifies the two endpoint
domains, realizes every equal-mask pair, gives one unequal example, and
asks which unequal pairs are joined. The six-family census and the
price of the mask at `(0, 9)` are not re-proved. The upstream finding
that records the open question is
[discussion comment 19514157](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514157).

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
