# No facet or ridge of the mode zonotope has a depth gap

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped finite theorem with an exact certificate; no κ.** This continues the
mode-fiber rounding-radius thread: #6312 (R ≥ 1), #6320 (R = 1 is a zonotope-filling
question) and #6333 (R ≤ 3/2). It upgrades the sampled check posted on
[#6333](https://github.com/CrocSwap/integer-mult-bounds/pull/6333#issuecomment-6701730365)
to **every** facet.

R = 1 holds if and only if every point of 2L in the interior of Z = Σ[−1,1]m_i is a
sign sum Σ±m_i. Just inside a facet with normal θ, a sign sum must lie at a depth
of the form 2·(a subset sum of the off-facet values |⟨m_i,θ⟩|). A missing subset
sum would leave a whole wide lattice layer without sign sums, the most direct
counterexample to R = 1.

**Theorem.** Z has 422,224 facet hyperplanes in 41 symmetry orbits. For every
one of them, the off-facet values (divided by their gcd g ∈ {1,2}) have gap-free
subset sums, with smallest value 1 and no greedy jump. So no facet carries a
depth obstruction.

**Method.**
1. Up to sign, the 112 rows are all sign patterns on the 14 weight-four words
   of H8. The facet set is therefore invariant under Aut(H8) (order 1344)
   combined with all coordinate sign flips.
2. [ORBITS.json](ORBITS.json) lists one representative per orbit.
3. verify.py proves the list complete by exact closure under ridge adjacency.
   For each representative it enumerates every rank-6 flat and every hyperplane
   through it, and checks each lies in a listed orbit. The facet–ridge graph
   is connected.

A control direction that is not a facet, (5,3,0,…,0), does have a gap, so the
property is not automatic.

**Ridges.** For each of the 21,589 rank-6 flats of the representatives, the
rows are projected onto the 2-D normal plane of the flat. Up to symmetry, these
flats cover every ridge. In each case, every lattice point strictly inside the
projected zonogon is a projected sign sum. So no two-dimensional shadow along a
ridge obstructs R = 1 either. A bitset dynamic program performs the test. It is
cross-checked against a set-based recomputation and against a toy zonogon with
known holes. See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/mode-fiber-facet-depth/verify.py facets
python3.12 -I -W error -B research/mode-fiber-facet-depth/verify.py ridges
python3.12 -I -O -W error -B research/mode-fiber-facet-depth/verify.py facets
python3.12 -I -O -W error -B research/mode-fiber-facet-depth/verify.py ridges
python3.12 -B scripts/research_package.py --package research/mode-fiber-facet-depth
```

The facets part takes about 80 s locally and the ridges part about 3 minutes;
the registered timeouts are 200 s and 400 s. The orbits were found by a breadth-first search
from one facet, which took about 40 minutes with an unoptimized script. The
committed verifier only checks the certificate.

## Limitations

This rules out obstructions visible in facet (1-D) and ridge (2-D) shadows only.
It does **not** prove R = 1. Shadows along faces of codimension 3 to 8 remain
unchecked; codimension 8 is the full question. 1 ≤ R ≤ 3/2 is unchanged. Exact-mode contract only. No physical
rounder, κ, frontier or assumption change. No independent human or proof-kernel
review is claimed.

## Open next questions

1. **Codimension 3.** Run the same filling test on 3-D shadows along rank-5
   flats. First step: take the rank-5 flats inside the 21,589 rank-6 flats and
   use a 3-D bitset. Expect a much larger flat count and more cost per flat.
2. **A proof of R = 1.** Can the facet-level greedy property (smallest value g,
   no jumps) be propagated to all faces, giving an inductive filling argument?

## Credit

Nick Petalas's #6312 defines R and proves R ≥ 1. Dillon Amburgey's PR4933
supplies M. The finite reduction (#6320) and the R ≤ 3/2 bound (#6333) are
earlier apoursh contributions. Facet–ridge connectivity of polytopes and the
extended Hamming code are classical.
