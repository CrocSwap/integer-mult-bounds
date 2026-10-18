# Why the paired-cube decoder does not extend to 4-dimensional (hyper)cubes (no new κ)

A scoping note on the port dimension of the paired-cube bit word. **No κ is claimed, and nothing existing changes.**

## The identity being generalized

The paired-cube bit word (`research/paired-cube-bit/LEMMA.md`) computes the mod-2 decoder identity

    x_T = sum_{c in T} star(c) + sum_{|S cap T| = 1} x_S        (mod 2),

over **ports**: triples taking one coordinate from each of three distinct coordinate pairs.
- `star(c)` is the sum of `x_S` over all ports containing coordinate `c`. These are the shared center sums.
- The overlap-1 sums are what the cube's local circuits, modules and partner pairs compute.

A natural question is whether moving to k-dimensional cubes, with ports taking one coordinate from each of k pairs, gives a larger deficit. The source count grows like 2^k·C(p,k), while the center loss grows like p².

## Result

Consider the star family of decoders for k-ports:

    x_T = sum_{0<l<k} a_l sum_{L <= T, |L| = l} star_L  +  sum_{0<j<k} b_j sum_{|S cap T| = j} x_S     (mod 2),

with `star_L` the sum of `x_S` over the ports containing the l-set `L`. Coefficients `a_l, b_j` are in F2. The global sum (`l = 0`) and the disjoint class (`j = 0`) are excluded, because together they give only the trivial "everything minus the rest" decoder.

**A decoder of this form exists if and only if k is not a power of two.** In particular, there is none for **k = 4**.

*Proof.* The coefficient of `x_S` in the right-hand side depends only on `j = |S cap T|`. It equals `sum_l a_l C(j,l) + b_j`, where `b_j` is present only for `0 < j < k`.
- For `0 < j < k`, choosing `b_j` makes it 0.
- For `j = 0` it is 0 automatically.
- For `S = T` (`j = k`) it is `sum_{0<l<k} a_l C(k,l)`. This can be 1 exactly when some `C(k,l)` with `0 < l < k` is odd.

By Lucas' theorem, every such `C(k,l)` is even iff `k` is a power of two. ∎

| k | Example | Decoder |
|---|---|---|
| 3 | paired cubes (today) | yes, e.g. level-1 stars plus overlap-1 corrections (the lemma above) |
| **4** | **hypercubes** | **no**: `C(4,1), C(4,2), C(4,3)` are all even |
| 5 | | yes, e.g. level-1 stars plus overlap-1 and overlap-3 corrections |
| 6 | | yes, needs level-2 stars (`C(6,2) = 15`) |
| 8, 16, … | | no |

## Check

```sh
python3 -B research/hypercube-decoder-parity/check.py      # standard library, under one second
```

For `(k, p) = (3,6), (4,6), (5,7), (6,7)`, the script tests every coefficient vector `(a, b)` against every column of every port. It confirms that valid decoders exist exactly when `k` is not a power of two, with 2, 0, 8 and 16 decoders respectively. It also confirms that the k = 3 solutions include the paired-cube identity.

## Scope

- The note concerns decoders built from stars and overlap-class corrections. That is the family the paired-cube construction uses, and the one whose terms local circuits and shared center sums can compute.
- It is not an impossibility proof for every decoder over 4-dimensional ports.
- It says nothing yet about whether k = 5 or k = 6 would beat k = 3. That would need new local circuits, partner pairs, caps and a full construction, and those decoders also need correction terms at more overlap sizes.

Credits: icekylinx (#144, paired cubes) and eumemic (paired-cube bit word and its lemma). Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance; Apache-2.0.
