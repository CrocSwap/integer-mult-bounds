# One reflected D6 anchor pair keeps the transported support set

**Exhaustive finite census of one simple reflection. No new κ.**
The selected conditional exponent stays `781451/250000000`. Reflect the
pinned D6 anchors by one simple E8 root, rebuild the 30-line complement,
and transport it by every coordinate permutation that carries the image
pair back to the pinned pair. Every such transport reproduces the partner
supports whose SHA256 is
`23a7b374a6bc62bc2aca47843d52a01fa8e791ed3a98085133829d816c5094e8`.

## Result

The pinned anchors and the pinned 30 lines are the D6 slice in
[research/d6-punctured-frame-code/ROOTS.json](../d6-punctured-frame-code/ROOTS.json).
The anchors are `(2, 2, 0, 0, 0, 0, 0, 0)` and `(2, -2, 0, 0, 0, 0, 0, 0)`.
Their line-list SHA256 is
`bd3d7efd8a94a7d0a6a7339cfd95805bb6907f3951ff67e9669b317655869538`.
The partner-support SHA256 above is recomputed from that line list. The
original bit-lane census is not rerun.

The simple system is the eight roots in
[research/p112-a3-six-flat/geometry.py](../p112-a3-six-flat/geometry.py).
Each has norm 8, and each simple reflection permutes the 120 E8 lines.
In this basis every line has integer coordinates of one sign. The eight
lines whose coordinates are a single `±1` are exactly these simple roots,
and each simple root is the corresponding basis vector. The Gram matrix
divided by 4 is the Cartan matrix of E8: node 3 is the branch, with arms
of lengths 1, 2 and 4.

In that order, simple roots 1 and 2 are the pinned anchor lines, and roots
4, 5, 6 and 7 are orthogonal to both anchors. Those six reflections fix
the unordered pair. Simple root 0,

```text
(1, -1, -1, -1, -1, -1, -1, 1)
```

fixes the first anchor and sends the second to
`(1, -1, 1, 1, 1, 1, 1, -1)`. That image has absolute coordinates
`1,1,1,1,1,1,1,1`. Each pinned anchor has absolute coordinates
`2,2,0,0,0,0,0,0`. A signed coordinate permutation preserves the multiset
of absolute values, so none carries this image pair onto the pinned pair.
The same conclusion for unsigned permutations is the census below: 0 of
the `8! = 40320` coordinate permutations carry it. This package does not
build that spinor complement's frame code.

The first simple root that moves the pair and admits a coordinate
permutation is index 3,

```text
α = (0, -2, 2, 0, 0, 0, 0, 0).
```

With `A = (2, 2, 0, 0, 0, 0, 0, 0)` and `B = (2, -2, 0, 0, 0, 0, 0, 0)`,

```text
A · α = -4,    s_α(A) = A + α = (2, 0, 2, 0, 0, 0, 0, 0),
B · α = 4,     s_α(B) = B - α = (2, 0, -2, 0, 0, 0, 0, 0).
```

The images are orthogonal E8 lines, and they are a different unordered
pair. Keeping `B` fixed destroys orthogonality: `s_α(A) · B = 4`. The
orthogonal pair tested here is the joint image.

| Simple index | Pair moves | Carrying permutations |
|---:|:---:|---:|
| 0 | yes | 0 |
| 1 | no | 1440 |
| 2 | no | 1440 |
| 3 | yes | 1440 |
| 4 | no | 1440 |
| 5 | no | 1440 |
| 6 | no | 1440 |
| 7 | no | 1440 |

`itertools.permutations(range(8))` yields each coordinate permutation once,
in lexicographic order, and the verifier counts `8 · 40320` visits. A
permutation `σ` acts by `(P_σ v)_i = v_{σ(i)}`. For root 3, `P_σ` carries
the image pair to the pinned pair if and only if `{σ(0), σ(1)} = {0, 2}`.
There are `2! · 6! = 1440` such permutations, and the census finds exactly
those. The lexicographically first is

```text
σ = (0, 2, 1, 3, 4, 5, 6, 7),
```

the transposition of axes 1 and 2. It satisfies `P_σ(s_α(A)) = A` and
`P_σ(s_α(B)) = B`. The identity does not carry the image pair.

The 30 lines orthogonal to both image anchors are the coordinate lines
`±2e_i ± 2e_j` on axes `1, 3, 4, 5, 6, 7`. No spinor line is orthogonal to
both images: the two anchor equations would force a zero coordinate. This
line list is also the image of the pinned 30 lines under `s_α`. Its
SHA256, of the JSON array with no extra spaces, is
`bcc5dc15f642aca7bdcc1249d2588869b6510aa8e08cde8688fe340c665435b5`,
distinct from the pinned line-list hash.

Two of these lines are orthogonal exactly when their supports are equal or
disjoint. That comparison was made for all 435 pairs. The orthogonal
6-frames are the both-sign lifts of the 15 perfect matchings of the six
axes. An increasing-clique search, finished under its state cap, returns
that same set of 15 frames. Every line lies in 3 frames, and the sum of
the frame rows is the all-one word.

The partner supports are the 15 masks of the two sign lines on one edge.
On this reflected list they are

```text
3, 24, 36, 768, 1152, 2112, 98304, 147456, 270336, 528384,
50331648, 75497472, 138412032, 270532608, 537919488
```

Every vector in `F_2^30` of weight 0, 1 or 2 was tested against the 15
frame parities: `1 + 30 + 435 = 466` vectors. The vectors that pass are
zero and these 15 masks. The incidence matrix of the 15 frames has F2
rank 10, so the code has dimension 20. That rank is Gaussian elimination
on these 15 rows. It is not a walk of the `2^20` codewords.

For every one of the 1440 carrying permutations, the image of each
reflected line lands in the pinned line list, the induced index map is a
bijection, and the transported partner masks are exactly the 15 integers
above. Their SHA256, of `json.dumps` of that sorted list, is the recorded
hash. The lexicographic permutation induces the identity index map. At
least one other carrying permutation moves indices and still reproduces
the same set. Removing the first mask changes the hash. Clearing its top
bit produces a weight-1 word outside the screened set, and the mask of
lines 0 and 2 is a weight-2 word outside the set.

## Scope

Task card `replay-runtime`, priority revision 8, base
`17469fff78c22941280f04d39dc5a1faee09c840`. Scope status is **refined**.

The card asks for a new measured speedup that keeps coverage. The
revision-8 verification row instead says that faster output is not the same
coverage until checked. Merged PR #6959 checked one pinned D6 pair and
left this reflection open. This package is that comparison for simple root
3, the first root in the pinned simple system that moves the pair and is
carried back by a coordinate permutation. Width 30, weight bound 2, one
reflected anchor pair.

The selected record's κ is `781451/250000000`. The priority note on this
base still quotes the older displayed value `0.00310045` from PR #5599.
This package uses the selected record and leaves it unchanged.

Ordered overlap check on 2026-11-10, after fetching upstream `main` at
`17469fff78c22941280f04d39dc5a1faee09c840`. `scripts/find_overlap.py
--refresh --include-closed` read 339 open pull requests, including drafts
(fetched `2026-11-10T09:50:29Z`, pagination complete), 6175 closed pull
requests (fetched `2026-11-10T09:52:16Z`), 7007 discussion records
(fetched `2026-11-10T09:51:28Z`, pagination complete), and 10180 local
notes at that head, with a complete local inventory. The matches were the
pinned D6 package, this package, merged PR #6959, and discussion comment
19507177. The earlier records state this question and do not reflect an
anchor.

This census has two finite domains, both enumerated completely. The first
is the set of coordinate permutations of eight axes, for each of the eight
simple roots: `8! = 40320` tuples, each visited once. The second is the
set of vectors of weight at most 2 on the reflected code: 466 vectors,
each tested against the frame rows. The clique search is the complete set
of increasing 6-cliques, because every index triple `i < j < k` and every
later 3-subset of the common neighborhood is visited, and the search
finishes under the cap. The absolute-value mismatch for simple root 0 is
a proof that no signed coordinate permutation carries that image onto the
pinned pair. It is scoped to monomial signed permutations. It is not a
statement about the rest of the Weyl group.

This is not a census of the 3780 orthogonal anchor pairs, not a frame-code
check of the spinor image, and not a proof that the bit-lane iterator is
correct on the reflected basis. The original D6 equality of #6959, the
P112 equality of #7007, and the E6 equality of #6948 are separate results.
A failed search was not used.

## Reproduce

Python 3.12 and the standard library, from the repository root. The
permutation census and the 466-vector screen finish in a few seconds.

```sh
python3 -B scripts/research_package.py --package research/d6-reflected-anchor-pair --check-only
python3 -I -B research/d6-reflected-anchor-pair/verify.py
python3 -I -O -B research/d6-reflected-anchor-pair/verify.py
python3 -B scripts/research_package.py --package research/d6-reflected-anchor-pair
```

The direct verifier prints

```text
PASS_D6_REFLECTED_ANCHOR_PAIR simple=3 permutations=1440 width=30 frames=15 dimension=20 supports=15 vectors=466 hash_match=true spinor_coordinate_permutations=0 engine=false no_new_kappa=true
```

Outside this run: `low_weight_words`, the `2^20` Gray walk, the half-split
of the pinned kernel, `research/e7-intersection-counters/engine.py`, the
E6 and P112 censuses, the spinor complement's frames, any non-simple
root, Lean, Docker, and `scripts/research_selected_baseline.py` as a
scientific replay. The selected record is provenance only.

## Open next questions

1. Does the image pair of simple root 0 have the same weight-at-most-2
   set equality on its own 30-line complement? No coordinate permutation
   carries that pair to the pinned anchors, so the hash comparison above
   does not apply. The complement was not built. First list the E8 lines
   orthogonal to `(2, 2, 0, 0, 0, 0, 0, 0)` and
   `(1, -1, 1, 1, 1, 1, 1, -1)`, and screen all 466 vectors of weight at
   most 2 against that frame code.
2. Does one coordinate root outside this simple system induce the same
   transported equality? The root `(0, 2, 0, -2, 0, 0, 0, 0)` is an E8
   line, it is not one of the eight simple roots, and its image is a
   different orthogonal pair. Those three facts are checked. The
   coordinate-permutation transport of that image is not run. First
   compare its transported partner supports with the hash above.

## Credit

The pinned D6 lines, the partner-support hash, and the open question are
the merged record in PR #6959,
`research/d6-punctured-frame-code`, discussion comment 19507177. The
simple system is the one fixed in `research/p112-a3-six-flat/geometry.py`,
from Nick Petalas's PR3161/PR3162 lineage. The coordinate D6 lines match
the `D(6)` construction used by that earlier package. This comparison
does not rerun Ali Romman's bit-lane iterator from PR #5729.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
