# Exact least period for Gaussian-pair rounding

**Scoped proof.** An exact-sum Gaussian-pair rounder with Euclidean pair
error at most one can have finite global least period `m` exactly when
`4` divides `m`. Its sharp forward outward slack at that least period is
`sqrt((R^2+2R+3)/2) - sqrt((R^2+1)/2)`, where `R` is the least odd
integer at least five that does not divide `m`. The same construction
attains that bound for absolute radial change and inverse outward slack.

The finite iterate theorem supplies the lower bound and a map whose
period divides `m`. The new construction joins `m/4` four-cycles on
consecutive rings in the sum-one fiber into one cycle of length `m`.
The switches alternate between opposite sides of the rings so each
changed edge still has error one. Moving the switches far enough
toward a corner keeps the new edges below the radial bound.
For instance, period eight attains `sqrt(19)-sqrt(13)`.
[Proof](PROOF.md)

## Reproduce

Run from the repository root. The local checks used CPython 3.12.15
and only the standard library.

```sh
pkg=research/gaussian-rounder-exact-period
python3.12 -B scripts/research_package.py --package "$pkg"
python3.12 -B scripts/check_research_commit.py --package "$pkg" --check-source-history
python3.12 -I -W error -B "$pkg/verify.py"
python3.12 -I -W error -O -B "$pkg/verify.py"
```

Both verifier modes print `PASS_GAUSSIAN_ROUNDER_EXACT_PERIOD`.
They check 20 orbits through period 13,860, including 16,940 Gaussian
edges and 8,430 switched successors. The four controls omit part or
all of the splice, reuse a source, or move the splice near the axis.
The written proof covers arbitrary admissible periods. The verifier
checks only the new construction on its stated fixtures.

The contribution is a local precision result. Physical
implementation, caller pricing and any change to the conditional
multiplication bound remain open. The predecessor theorem is a cited
premise. Its suite, the selected cold replay, Lean and Docker were
unrun. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Which physical caller, if any, needs a prescribed least period?
Identify one caller and its row and address schedule. That would
give a concrete setting for pricing the local splice predicate,
coordinate arithmetic and workspace restoration.

## Credit

This contribution was produced by Nick Petalas. Ali Romman's
finite iterate optimum supplies the lower bound and the starting
permutation. Jerry Chen's annular matching supplies the geometric
construction it uses. Ali Romman's ring classification supplies
the lower-bound framework, and his exact-sum contract supplies the
Gaussian transform. [#7714 at ba5e006](https://github.com/aliromman/integer-mult-bounds/tree/ba5e006ed70119b23d6ef9e2e8627e43a3f4f18b/research/gaussian-finite-iterate-optimum),
[#7570 at 053c42c](https://github.com/CubeJerry/integer-mult-bounds/tree/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding),
[#7699](https://github.com/CrocSwap/integer-mult-bounds/pull/7699),
[#6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509).

Apache-2.0. [Task](TASK.json) · [Source provenance](SOURCES.json) ·
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19718444)
