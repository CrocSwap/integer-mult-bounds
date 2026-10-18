# Exact widths of every P104 survivor projection

**Status:** scoped mathematical extension / independently checkable finite certificate; **no new κ**. This builds on the *conditional* delivery interface and terminal-read theorem of [PR #1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125) (Ali Romman). It is **not** a new decoder, supplier, frame schedule, all-size theorem, or claim that PR #1125 is already merged.

## 1. Frozen finite object

Write the 8 vertices of the three-dimensional Boolean cube as integer labels `0,...,7`, where two vertices are adjacent iff their XOR has Hamming weight one. Represent vertex subsets by 8-bit masks. The exact 104-term support family `F` is the 12 edges, 24 induced 3-vertex trees, 32 induced 4-vertex trees, 24 induced 5-vertex trees, and 12 complements of edges. The explicit 104 masks agree with the pinned `cube_supports` array in PR #1125, at blob `9a2cd574df48361579167e39aa6198f39059f70c`. `generate.py` reconstructs them *independently* by cube edge enumeration, induced connectivity and tree edge counts, rather than importing the predecessor's checker.

For any nonempty surviving term set `K`, define

    F_K = {S ∩ K : S ∈ F, S ∩ K != ∅},

with duplicates removed. Order `F_K` by inclusion and denote its width by `w(K)`, the largest antichain size. There are 255 nonempty `K`. The degenerate empty `K` has width zero.

## 2. Orbit reduction is exact

Every cube automorphism has the form `v -> permute_coordinates(v) XOR t`, where the coordinate permutation has six choices and `t` has eight, giving 48 distinct permutations. The checker exhaustively verifies each permutation maps **the entire original family** `F` onto itself. Therefore for every `S` and `K`,

    p(S ∩ K) = p(S) ∩ p(K),

and hence the posets `F_K` and `F_{p(K)}` are isomorphic, with identical widths. All 255 nonempty `K` split into exactly **21** cube-automorphism orbits, explicitly listed in `CERTIFICATE.json`. No orientation or geometric equivalence is assumed without finite verification.

## 3. Dual width witnesses

For each of the 21 orbit representatives, `CERTIFICATE.json` contains:

- an antichain of exactly `w` distinct members, giving `width >= w`;
- a partition of **every** member of the projected support poset into `w` strictly increasing chains, giving `width <= w`.

Both certificates are checked by `verify.py` without importing `generate.py`, solving optimization problems, or trusting recorded width values. Every member is accounted for once and every asserted inclusion is recomputed bitwise. Since an antichain meets each chain in at most one point, the two finite witnesses prove equality. Symmetry transports the proof to all 255 nonempty survivor sets.

The resulting **complete width census** is:

| Erased terms q | Remaining | Number of K | Exact widths (number of K) |
|---:|---:|---:|---|
| 0 | 8 | 1 | 32 (1) |
| 1 | 7 | 8 | 26 (8) |
| 2 | 6 | 28 | 18 (24), 20 (4) |
| 3 | 5 | 56 | 10 (56) |
| 4 | 4 | 70 | 6 (70) |
| 5 | 3 | 56 | 3 (56) |
| 6 | 2 | 28 | 2 (28) |
| 7 | 1 | 8 | 1 (8) |
| 8 | 0 | 1 | 0, trivial degenerate case |

For exactly two erased terms, **width 20 occurs iff the erased pair comprises opposite vertices of the cube**, i.e. their XOR equals `7`. The other 24 pairs have width 18. The six-vertex cases belong to three distinct automorphism orbits, though only two width values occur.

## 4. Consequences for the inherited delivery theorem

PR #1125's terminal-read theorem, with its full assumptions and endpoint / carrier / payment definitions, states:

    L >= q + 2 max(0, width(F_K) - P_K),

where `q` distinct terms lose their survivor, `P_K` counts continuous term-preserving paths assigned to surviving terms, and `L` is excess paid frame-move rank. This contribution does **not** reprove the physical/scheduling premises of that theorem. Substituting the now-exact widths yields additional conditional obstructions for every `q = 2,...,7`.

In particular, for **two erased terms**:

    L >= 2 + 2 max(0, 18 - P_K)              (non-opposite erased pair)
    L >= 2 + 2 max(0, 20 - P_K)              (opposite erased pair).

If `P` counts all delivery paths, and every erased term has at least one path, then `P_K <= P - 2`. Thus

    L >= 2 + 2 max(0, 20 - P)               (non-opposite pair)
    L >= 2 + 2 max(0, 22 - P)               (opposite pair).

For example, **P <= 18** forces **L >= 6** for non-opposite pairs and **L >= 10** for opposite pairs, provided exactly two terms are erased. These bounds improve the previously used generic `L >= q = 2` for this scoped path budget. They are necessary conditions, not constructs of any legal schedule. For `q >= 3`, substitute the row-specific widths in the same inequality. All transformations retain the original separate source, restoration, finite-invoice and analytic assumptions.

## 5. What was and was not established

- **Proved by finite witnesses:** the complete 255-case projection width table in the frozen 104-support cube model.
- **Conditional corollaries:** sharpened rank/path lower bounds assuming PR #1125's terminal-read theorem and *its precise interface*, rather than an arbitrary mixing or changed-COPY decoder.
- **Not claimed:** a new conditional exponent, a direct correction to an accepted frontier, a proof of all 7,168 geometrically labeled decoders independent of PR #1125's support-uniformity assertion, an unrestricted impossibility theorem, or a complete integer multiplication algorithm.

An optional SciPy sparse-matching oracle independently repeats all 255 cases and checks the opposite-pair condition. The 21 antichain/chain-cover certificates are exact finite proofs of these poset widths; they are not a formal proof of the physical terminal-read theorem. `verify.py` also exercises ten adversarial corruptions and rejects all ten. The full P104 path-price obligation for new constructions remains open.
