# One tensor axis is at most two section errors at ceiling 9

**Claim type:** a telescoping identity with an explicit one-axis norm bound.
**No new κ.** The per-axis norm bounds stay hypotheses. The selected record
remains `23/10000`.

## Question

#4506 bounds the scalar monomial

```text
2 g (9 p^2 + p^6 exp(-p^2))^{g-1} p^6 exp(-p^2)
```

and asks whether one axis of the tensor difference is at most two section
errors. The ceiling in that question is `9 p^2`.

## Lemma

Let `g ≥ 1`, and let `B_i` and `C_i` be bounded operators on Hilbert spaces.
Write `ε = p^6 exp(-p^2)` for an integer `p ≥ 2`. Suppose that for every axis

```text
||B_i|| ≤ 9 p^2,
||C_i|| ≤ 9 p^2 + ε,
||B_i - C_i|| < 2 ε,
```

and that `||X ⊗ Y|| = ||X|| ||Y||`. Then

```text
⊗_i B_i - ⊗_i C_i = sum_{k=1}^g T_k,
```

where

```text
T_k = (⊗_{i<k} B_i) ⊗ (B_k - C_k) ⊗ (⊗_{i>k} C_i),
```

an empty product being the identity. Every slice satisfies

```text
||T_k|| < 2 (9 p^2 + ε)^{g-1} ε,
```

and the triangle inequality gives

```text
||⊗_i B_i - ⊗_i C_i|| < 2 g (9 p^2 + ε)^{g-1} ε.
```

The factor 2 is the sum of two section errors on the active axis. HALO's
`2g` rectangles are a volume partition, not this factor. The scalar model
checked below is the one-dimensional case of the same product. The gate that
puts the right-hand side below `2^{-C p}` is #4506; it is not re-proved here.

## Proof

For `g = 1` the identity is `B_1 - C_1 = T_1`. If it holds for `g - 1` factors,
then

```text
(⊗_{i<g} B_i) ⊗ B_g - (⊗_{i<g} C_i) ⊗ C_g
  = (⊗_{i<g} B_i) ⊗ (B_g - C_g)
    + ((⊗_{i<g} B_i) - (⊗_{i<g} C_i)) ⊗ C_g.
```

The second sum expands by the inductive hypothesis, and its slices are the
slices `T_k` for `k < g`. The first sum is `T_g`.

The norm hypothesis multiplies across a pure tensor, so

```text
||T_k|| = (∏_{i<k} ||B_i||) · ||B_k - C_k|| · (∏_{i>k} ||C_i||)
  < (9 p^2)^{k-1} (9 p^2 + ε)^{g-k} · 2 ε.
```

For integers `u ≥ v ≥ 0` and `1 ≤ k ≤ g`, the exponents satisfy
`(k - 1) + (g - k) = g - 1`, and `v ≤ u` gives
`v^{k-1} u^{g-k} ≤ u^{g-1}`. Apply this with `v = 9 p^2` and
`u = 9 p^2 + ε`. Each slice is strictly smaller than `2 u^{g-1} ε`. Adding
the `g` slices preserves the strict inequality.

The cap `||B_i - C_i|| < 2 ε` is the sum of two strict section errors. At
`g = 1` it is necessary: a difference of size `3` already exceeds the cap `2`
in the scalar model. The executable check uses the integer caps `9`, `10`
and `2` in place of `9 p^2`, `9 p^2 + ε` and `2 ε`. The displayed factors
are `8, 7, 6` and `7, 9, 5`.

## Not covered

- A proof that any axis inverse, approximant, or section error meets the
  three norm hypotheses.
- The comparison of the monomial with `2^{-C p}`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-axis --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-tensor-nine-axis
```

Base `bbde3b0bedb8f7ce17159dfbe913b7e3e5194bab`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T02:50:31Z. It had
moved from `2a13eb18` by archive intake and merged packages. The selected
κ and priority revision were unchanged, and the HALO sentences used here
were still present.

Overlap snapshot: open PRs fetched 2026-10-22T02:50:59Z (293 records) and
discussions fetched 2026-10-22T02:51:39Z (3382 records). A search for
`ceiling 9`, `caps 9`, `9 p^2 + epsilon` and `two section errors` returned
this draft, #4506, which leaves the axis open, #4488, which is the same
telescope at ceiling `10 p^2`, and an unrelated format ceiling. A search miss
is not a novelty certificate. #4506 is the scalar monomial. HALO is the
tensor sentence.

## Open next questions

1. **Does one axis meet the three norm hypotheses at ceiling `9 p^2`?** The
   telescope uses `||B_i|| ≤ 9 p^2`, `||C_i|| ≤ 9 p^2 + ε`, and
   `||B_i - C_i|| < 2 ε`. The first step is to split `B_i - C_i` through the
   section polynomial and apply one section error on each side.

## Credit

- The telescoping shape at ceiling `10 p^2` is #4488.
- The scalar monomial with coefficient 9 is #4506.
- The section error `p^6 exp(-p^2)` is the within-cell bound of #4452.
- HALO's sentence `These 2g sets are disjoint rectangles.` is a volume
  partition. The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
