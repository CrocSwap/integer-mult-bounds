# Sharp radial budgets for finite Gaussian iterate identities

**Scoped all-input optimum; no new kappa.** Fix a positive integer m.
A total Gaussian-pair map can preserve exact sum, stay within Euclidean
error one of the positive half-transform, and satisfy `F^m=id` exactly
when four divides m. In that case, let R be the first odd integer at
least five that does not divide m. The sharp forward outward slack is

```text
sqrt((R^2+2R+3)/2) - sqrt((R^2+1)/2).
```

The proof gives a global bijection with an explicit inverse. It attains
the same bound for absolute radial change and inverse outward slack.
The map has Gaussian-unit covariance; the lower bound assumes no symmetry.
The requirement is the iterate identity, not that m be the least period.

Examples: m=4 retains the known `sqrt(19)-sqrt(13)` optimum. At m=20,
the optimum is `sqrt(33)-5`; at m=140, it is `sqrt(51)-sqrt(41)`.
Finite iterate budgets approach `1/sqrt(2)` as their compatible odd
ring periods increase. No finite iterate attains that limit.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[verify.py](verify.py) and [CREDITS.md](CREDITS.md).

The lower bound isolates the first incompatible ring between two
invariant finite squares. The upper map uses directed cycles on allowed
single rings and shifted pairs of annuli outside that radius. If three
does not divide m, the two central rings need a separate paired case.
The code has a local point rule and does not store an unbounded table.

## Reproduce

Use CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/gaussian-finite-iterate-optimum
```

Both registered normal and optimized commands print:

```text
PASS_GAUSSIAN_FINITE_ITERATE_OPTIMUM
1024 iterate budgets; 23 complete grids; 41032 half-grid points
2424 lower-boundary edges; 19208 full Gaussian inputs; all controls pass
```

The complete grid checks compare the local map with a separate arc
generator, follow every cycle, verify the stated iterate identity,
check both colors and inverses, and attain each exact bound. Twenty
distinct critical cutoffs from five through 61 have complete lower-
boundary checks. The Gaussian inputs include every component parity
and eight iterate choices. All comparisons use integers and certified
square-root intervals. The proof establishes the all-input and all-m
claims; these finite domains corroborate them.

Controls reject omission of the central paired case, a single map on
the first incompatible ring, and reuse of the old fourth-power budget
at m=20. The zero-sum fiber forces divisibility by four. No finite
attaining cycle is treated as a complete global construction on its own.

## Scope and credit

CubeJerry/Jerry Chen supplied the half-grid and annular map in
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570).
Ali Romman's [PR #7699](https://github.com/CrocSwap/integer-mult-bounds/pull/7699)
supplied the forced ring classification, no-finite-order optimum and
fourth-power-only lower bound. Those results are prior work. This
package supplies the first-incompatible-ring formula and an attaining
global map for every prescribed iterate identity. The source roles,
exact pins, reused routines and retained geometric credit are in CREDITS.md.

The selected kappa remains `0.00363005817`, with all five assumptions.
No native tariff, physical provider, tensor caller, scratch restoration
or complete recursive invoice is supplied. Inverse by conjugation and
row/column tensor commutation are not claimed. Full predecessor suites,
selected cold replay, native/physical replay, Lean, Docker, independent
human and formal-kernel review were not run. This is author-checked work;
the adapted checker is not an independent source review.

## Open next questions

The theorem specifies an iterate identity. If an actual caller needs
exact least period m, identify that caller and the period requirement
before further construction. The present map can have a smaller period.
Its local point rule also needs a complete physical cost and restoration
contract before native use. Exact local identities do not provide tensor
commutation or supplier admission. No follow-up is reserved.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0.
