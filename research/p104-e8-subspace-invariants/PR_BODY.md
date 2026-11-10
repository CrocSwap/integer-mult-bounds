Title: Prove E8 subspace invariants of the P104 ports: saturation depth, port counts per dimension, and a star law for bicliques (no κ)

No κ claim. This adds a registered research package for the card `p104-side-correction`. It states four exact facts about the 104 ports of P104 and the 120 ports of full E8 (all 9-bit vectors of weight 3 or 7), inside `F2^9`.

**Result.**

1. **Saturation depth.** No subspace of dimension 5 or more has all its odd vectors among the ports, for any subset of the 120 E8 lines. The saturated subspaces of dimension 1..4 number 104, 5356, 17958, 3441 (P104) and 120, 7140, 32130, 11475 (P120).
2. **Ports per dimension.** The maximum number of ports in a subspace of dimension e = 1..7 is 1, 2, 4, 8, 12, 20, 36, the same for P104 and P120. They differ only from e = 8 on (60 and 64).
3. **Star law.** The maximum of N(V)·N(V⊥) over subspaces V is 48 at every dimension for P104, and 56 or 48 for P120. In both cases it is the degree of the port graph (edge = dot product 0), so no subspace biclique is larger than one port's star, and covering the 2496 (P104) or 3360 (P120) edges by such bicliques needs at least 52 or 60 of them.
4. **Flag rectangles.** For g ⊂ A of dimensions d−1 and d, the best rectangle ports(g) × ports(A⊥) has mass 32 at every level d = 2..8 of P120 except 36 at d = 5. For P104 it is 30, 32, 32, 36, 32, 32, 30.

**Proof sketch.** The quadratic form `q(x) = C(wt x, 2) mod 2` has radical the all-ones vector and descends to a plus-type form on `F2^8` whose 120 nonsingular points are the ports (odd representatives). If an affine 4-flat `u + W` of odd vectors were all nonsingular, then `q|W` equals `B(u, ·)`, forcing `W` totally isotropic of dimension 4, with a totally singular kernel `W0` of dimension 3; reducing modulo `W0` gives a hyperbolic plane in which `u` would have to be singular, a contradiction. The counts in 2 to 4 come from enumerating every subspace of dimension at most 4, with duality covering the rest.

**Checks.** A standard-library script recomputes the form facts, all subspace counts, the saturated counts, the maximum ports per dimension, the degrees, the star-law and flag tables for both sets from the port list and from coordinates, in about 6 seconds. An independent unpruned implementation gave identical tables.

**Scope.** The statements are about the port sets only. Items 2 to 4 are exhaustive computations, not closed formulas; the pattern 2^(e−2) + 4 for e = 4..7 is observed, not proved. No word is constructed and nothing is priced; open questions are in the package.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
