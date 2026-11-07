# No facet of the mode zonotope has a depth gap

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
property is not automatic. See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/mode-fiber-facet-depth/verify.py
python3.12 -I -O -W error -B research/mode-fiber-facet-depth/verify.py
python3.12 -B scripts/research_package.py --package research/mode-fiber-facet-depth
```

Each run prints `PASS_MODE_FIBER_FACET_DEPTH` in about 80 s locally; the
registered timeout is 600 s. The orbits were found by a breadth-first search
from one facet, which took about 40 minutes with an unoptimized script. The
committed verifier only checks the certificate.

## Limitations

This rules out single-facet depth obstructions only. It does **not** prove R = 1.
Faces of codimension ≥ 2 and obstructions invisible to every linear shadow remain
open, and 1 ≤ R ≤ 3/2 is unchanged. Exact-mode contract only. No physical
rounder, κ, frontier or assumption change. No independent human or proof-kernel
review is claimed.

## Open next questions

1. **Codimension-2 faces.** For each ridge, do the two-dimensional depth vectors
   of the forced rows cover every lattice point of 2L near the ridge that lies
   inside Z? First step: start from the 41 facet orbits and their ridge lists.
   The (5,3,0,…) shadow gap shows that single shadows can fail there, so the
   test must use the actual 2-D cone.
2. **A proof of R = 1.** Can the facet-level greedy property (smallest value g,
   no jumps) be propagated to all faces, giving an inductive filling argument?

## Credit

Nick Petalas's #6312 defines R and proves R ≥ 1. Dillon Amburgey's PR4933
supplies M. The finite reduction (#6320) and the R ≤ 3/2 bound (#6333) are
earlier apoursh contributions. Facet–ridge connectivity of polytopes and the
extended Hamming code are classical.
