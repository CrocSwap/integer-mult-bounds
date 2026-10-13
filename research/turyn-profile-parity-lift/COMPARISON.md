# Exact relation to predecessor and concurrent work

## PR598: inherited mathematics and the new transfer

DominikScholz's [PR598](https://github.com/CrocSwap/integer-mult-bounds/pull/598),
incorporated snapshot `615ca6f06fdea0c50dbef733370c47349e25c555`, supplies the
Turyn geometry and these two distinct results:

1. On the **2,880-class existential glue quotient**, nine 24-cliques give
   rank at least 27d for asymmetric d-block fittings over every field of
   characteristic two. The general parity-projector proof is inherited.
   A recorded obstruction prevents automatically lifting its global cliques
   to consistently chosen actual ports.
2. On **actual ports within a profile**, a different 24-port finite search
   excludes symmetric standard-dot eight-bit labels over F₂. Explicit
   nine-bit profile labels give the upper bound. The predecessor expressly
   leaves asymmetric fitting outside that finite search's conclusion.

The new contribution consistently chooses **twenty actual ports per
profile** lifting the nine eight-class restrictions of the first result.
All clique edges are recomputed from literal integer coordinates. Applying
the inherited rank argument now proves the lower bound 9d for actual ports,
without symmetry, scalar-block, or F₂-only restrictions. The independently
rebuilt complete-profile upper fit makes the minimum exactly 9d for every
full canonical 7,680-port profile. The upper dimension nine and the general
parity principle themselves are not new claims.

The three separate lifts are not a lift of the global quotient certificate:
each chosen global 24-set has 98–150 missing cross-profile edges. Arbitrary
profile source/target spans need not be orthogonal. No unrestricted global
rank-27 obstruction, no exclusion of a global 25-dimensional fit, and no κ
improvement follows from this result.

The algebraic appendix is independent corroboration on the earlier different
24-port graph. It extends the preserved 57-variable-edge core to symmetric
fittings over all characteristic-two fields. It does not assert the new
asymmetric-block theorem for that particular core.

Consumed primary sources at the exact contribution base:

- [Quotient proof, including its asymmetric-block argument and nonliftability boundary](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/91a2094f2e022930069e8cfdc810a3ea1b81cd09/research/turyn-code-space/PROOF.txt)
- [Original actual-port/profile proof and its symmetry restriction](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/91a2094f2e022930069e8cfdc810a3ea1b81cd09/research/turyn-port-labels/PROOF.txt)
- [Original nine-clique quotient certificate](https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/91a2094f2e022930069e8cfdc810a3ea1b81cd09/research/turyn-code-space/evidence/PARITY-CERTIFICATE.json)

All consumed bytes are pinned in `SOURCES.json`; `SOURCE-AUDIT.json` also
records their exact base Git blobs. An earlier PR598-head query was rate-limited. The successful final query
at 15:25 UTC reverified its head as the same incorporated snapshot; the PR
is closed.

## PR898: distinct tooling, no code reused

[PR898](https://github.com/CrocSwap/integer-mult-bounds/pull/898), observed
head `521c86e7fd4d0fbd1ed4e0524aa26a1e45861477` in the successful 2026-10-13
14:32 UTC refresh, accelerates a **historical affine Leech-minor audit**
using exact byte lanes. It preserves that audit's existing finite results.
It supplies neither an actual Turyn profile parity lift nor the new
asymmetric-block lower bound. None of its implementation is imported or
executed here.

The 14:37 and final 15:25 UTC all-state searches returned only PR598 and
PR898 for “Turyn”.
A broader “fitting” search returned nine results, including PR954's different
fixed-star E8 puncture classification. These checks found no duplicate of
the actual-profile lift; the final recent-PR page reached PR971. Dated raw responses are retained in the standalone
handoff archive; discovery is not a claim of exhaustive literature priority.
