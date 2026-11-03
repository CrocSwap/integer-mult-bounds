# Exact rounding radius for signed-permutation frame groups

This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

**Scoped written proof with exact finite corroboration; no new kappa.**
For every d>=1 and unimodular integer matrix P, let G=P B_d P^-1, where
B_d is the full signed-permutation group, and let L be the largest absolute
row sum of P. Among every G-equivariant function from the complete refined
integer grid to the integer grid, the exact least uniform infinity-norm
rounding error is

    R_m(P) = floor(m/2) L / m,        m>=2.

On all real inputs it is L/2. Output grid spacing delta multiplies these
radii by delta. One rule attains every optimum and fixes integer inputs:

    q_P(x) = P nearest_odd(P^-1 x),

where scalar nearest rounding sends half ties away from zero. The proof
uses a point stabilizer to force every possible equivariant output onto a
primitive integer line. It covers arbitrary coupled nonlinear rounders.
See [PROOF.md](PROOF.md) for the full statement and argument.

This answers the signed-permutation conjugacy class of Krzysztof Wojt's
[PR5122 larger-finite-group question](https://github.com/CrocSwap/integer-mult-bounds/pull/5122).
For the sheared dihedral example P=[[1,2],[0,1]], the exact radius is 3/2
on the half-grid and on real inputs, and 1 on the third-grid. PR5122 already
gives these lower values for a reflection subgroup. The new result attains
them for all eight frames simultaneously and proves the general P,d formula.
Nick Petalas's [PR5079](https://github.com/CrocSwap/integer-mult-bounds/pull/5079)
provides the finite-group existence context and the dihedral example.
Neither predecessor executable is imported, replayed or audited.

## Evidence

The all-input and all-dimension conclusions rest on the written proof.
The standard-library verifier supplies exact finite corroboration:

- All 104 two-by-two unimodular matrices with entries in [-2,2], at every
  denominator m=2,...,9 and every transformed residue pair in {0,...,m-1}^2:
  29,536 points and 236,288 literal simultaneous equivariance comparisons.
- A separately implemented integer oracle constructs the eight physical
  frames, tests point stabilizers, and optimizes every displayed orbit by
  complete integer-box enumeration. Across these points and 832 explicit
  attaining orbits it enumerates 99,264 candidate outputs. It imports no
  radius formula, quantizer, inverse routine or predecessor executable.
- Eight further frames in dimensions 1,...,8, with 680 rational data points,
  5,440 sign/swap generator checks and 140 witness-stabilizer checks.
- Five semantic controls distinguish an understated radius, the odd-grid
  correction, an incompatible stabilizer choice, rounding in physical
  coordinates, and an actual nonodd-tie mutation. Fifteen malformed input
  cases reject; a 257-bit integer input is fixed exactly.

The receipt is computed at execution time and binds every package source
by SHA256. It is never handwritten. The verifier writes no files by default;
`--receipt /absolute/new/path.json` exclusively creates an external receipt.

## Reproduce

From the repository root, with CPython 3.12 and no additional dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/signed-permutation-frame-radius/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/signed-permutation-frame-radius/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/signed-permutation-frame-radius
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/signed-permutation-frame-radius --check-source-history
```

Another CPython 3.12 executable may replace the local path. Expected markers
are `PASS_SIGNED_PERMUTATION_FRAME_RADIUS`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Both registered checks run the complete
finite domain, separately with normal and optimized Python, with 180-second
limits. Local CPython is 3.12.15 on macOS arm64. Hosted execution is recorded
separately in the PR body; it is not independent mathematical acceptance.

## Scope and implementation limits

The `uniform-transfer-audit` card is explicitly changed to this precision
side theorem. A current supplier is not shown to reach a maximizing orbit.
There is no paid rounding/restoration circuit, native implementation, physical
tape invoice, stock bound, supplier admission, new kappa or selected-frontier
change. The five selected framework assumptions remain. No selected cold
replay, Lean or Docker run is claimed. Other finite integer representations,
restricted reachable domains, frame-dependent rules, changing grids and
magnitude-relative errors require separate arguments.

The executable frame boundary allows dimensions 1,...,8, integer entries of
at most 16 bits, rational point numerators/denominators of at most 4,096 bits,
and grid denominators at most 65,536. Its trusted frame/inverse pair comes
from `rounding.matrix`. The proof has no such operational size limits.
The independent oracle is a private two-dimensional fixture checker with
denominator at most 11, scaled incumbent radius at most 128 and at most
129 choices per output coordinate. Every loop has a finite input or fixture
bound; all functions are under sixty lines. Python exact integers and
Fractions allocate dynamically; bounded dimensions, coefficient/data bit
lengths and streaming census hashes bound live data. This is the managed
runtime deviation from preallocated steady-state memory. The nonodd-tie
mutation replaces one known local callable inside try/finally; there is no
dynamic evaluation or unbounded dispatch. Explicit exceptions keep the
contracts active under optimization; warning-strict execution and AST
parsing check all new Python sources. These checks do not certify physical
arithmetic complexity.

## Open next questions

Structured versions are in [TASK.json](TASK.json).

- Does an actual carried reader reach the explicit maximizing point or its
  orbit? Pin its frame and full dirty-input image, then decide membership.
  Actual reachability and the complete paid rounding/restoration bill are
  missing; the full-grid radius alone does not price a supplier.
- What is the exact radius outside the signed-permutation conjugacy class?
  Start with one explicit finite integral representation and its stabilizer
  sublattices. This proof supplies no general finite-group radius algorithm.

## Provenance and credit

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected conditional kappa `0.003125804`. [SOURCES.json](SOURCES.json) binds
predecessor context as historical provenance; there are no external runtime
inputs. The source question is PR5122, head
`dab8cc5917fbc76564367a973bd6cd1ed5a22ee3`, Open next question 2. PR5079's
exact head is `43f558c1b8fc14fb0ed33a4512fbc976beea6b0f`.

Credit Krzysztof Wojt for the reflection optima and released question;
Nick Petalas for the earlier existence classification; Sricharan Vagvala
(PR1631), woklerx (PR1892), Sagar Thakrar (PR1537), Ross Richardson (PR1287)
and the retained output-frame/dirty-echo lineage for their context. Scalar
rounding, change of basis, signed permutations and invariant subspaces are
classical. The new contribution is the simultaneous exact radius theorem,
its attaining rule and the finite corroboration; no general literature
priority is claimed. Predecessor credit lines and source bytes are unchanged.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370162)
records the scope. Live handoffs, local reservations, 505 open PRs, 6,496
Discussion records, main README searches and merged/all-state object searches
were checked. Sparse local notes, arbitrary historical diffs, unpublished
work and later changes remain coverage limits.
