# Attribution and scope

Contributor: merramil, with substantial OpenAI Codex assistance. Apache-2.0.

`baseline.py` is an exact, unmodified copy of
`scripts/experiments/single_intersection.py` at
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, SHA256
`08ddae46e5621a5b4c525b504e67ae655abe9b49461d894feaa7abc89a51847d`.
It was introduced in Douglas R. Colkitt's historical research preservation
commit `d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`. The benchmark retains it
only as a pinned comparison implementation, under the repository's Apache-2.0
license. All original construction, rank-screen, and orbit-proof credit remains
with that work and its cited mathematical sources.

The closest concurrent tooling PRs inspected were #707 (Bareiss determinant
prefixes for selected R420 frames) and #756 (balanced-Fano meet-in-the-middle
replay). Neither supplies code or a dependency here; this contribution packs
the historical single-intersection binary Gram matrix.

See [the engineering note](../../docs/research/single-intersection-packing.md)
for the equivalence argument and verification scope. No new multiplication
exponent, broader negative result, or full theorem verification is claimed.
