# Cubic precision with arbitrary dirty arrays

For PR628's balanced prime-power cyclic inverse, sufficient complete word
size is

    max(p, incoming_grid_bits) + O(m + r^3),

where every initial array has norm at most 2^m. The dispatcher, rounded
leaves, quadratic leaf count, and logarithmic number of borrowed dirty
arrays are unchanged. **No reserved zero bits or clean length-L array are
required. No new kappa is claimed.**

The new [proof](PROOF.md) shows that every ideal prefix and inverse prefix
is a sum of ordered products with no repeated factor occurrence. PR862's
common-isometry complementary-factor bound therefore controls these dirty
prefixes. PR877's variation-of-constants argument then bounds the nonlinear
rounding errors. The same exact restoration and inverse-word identities
from PR628 remain in force.

At radix 64, target p=128 and initial magnitude bound 2^20:

| Sufficient bound | Fractional bits | Leaf calls | Dirty arrays |
|---|---:|---:|---:|
| PR877 quartic budget | 73,245,212 | 4,000 | 6 |
| This cubic budget | 1,162,553 | 4,000 | 6 |

These are conservative proof budgets, not minimum precision, measurements,
or a runtime benchmark. The current formulas need not dominate every older
formula at small radices. Finer incoming grids must always be retained.
The preparation bound is also cubic, using PR862's full-inverse estimate.

## Reproduce

Standard-library Python 3.11 or later, from any working directory:

```sh
python3 -I -O -B research/dirty-cubic-precision/verify.py
python3 -I -O -B research/dirty-cubic-precision/test_package.py
```

The mathematical replay checks the manifest and source pins before running
and compares every generated mathematical field with [EXPECTED.json](EXPECTED.json).
It writes no package files. Expected final marker:

```text
PASS_DIRTY_CUBIC_PRECISION budgets=5220 symbolic=142 rounded=80 kappa=unchanged
```

- 5,220 exact integer budgets, with a separate recurrence/inequality checker.
- 142 free noncommuting polynomial traces through 256 factors, checking
  652,654 leaf boundaries in both signs for prefix and inverse prefix.
- 128 independently generated words compared with the frozen dispatcher.
- 18 dense matrix traces, 66 separate Gauss-Jordan inverse checks, and
  5,104 directly reconstructed interval propagators.
- 80 actual rounded kernel runs on all ten pinned fixtures, lengths
  1, 2, 3 and 8, both directions and signed initial dirt. Every real and
  imaginary input component has an odd numerator on the chosen working
  grid, including every borrowed word: no unused low-zero-bit assumption
  can explain their restoration. Every run has nonzero rounding error,
  bounded against a dense exact oracle, and checks true-kernel perturbation,
  exact source/dirty restoration and exact cancellation by the inverse word.
- Thirteen mathematical controls and separate package-binding controls.

The `--bindings-only` option checks only source/package integrity; it does
not run or certify the mathematics. `--write NEW_PATH` is an authoring mode
that creates a new complete receipt without overwriting an existing file.
The default mode requires the committed manifest and receipt.

## Scope and predecessors

All factors must use the same immutable unit-weighted permutation U and
one direction. All mutable arrays and phase storage must be distinct.
The proof does not infer subset bounds for unrelated noncommuting shifts.
All leaf passes, validation, source access, restoration, scalar arithmetic,
preparation and routing remain paid; long phase descriptions or phase
oracle access add their own costs. The neighboring-layout bound is

    soft-O((L r^2+r^3)(max(p, incoming_grid_bits)+m+r^3)).

This remains a local classical arithmetic theorem under the inherited
analytic, leaf and supplied-preparation hypotheses. It supplies no
bit-reversible compiler, common-label/Clifford word, physical owner layout,
full-transform recurrence, multiplication reduction or practical speedup.
Finite checks support the written all-size proof; they are not a formal
verification or independent human review.

Twenty-two predecessor files are retained unchanged with exact Git heads,
Git object identifiers and SHA256 hashes in [SOURCES.json](SOURCES.json).
PR628 supplies the dispatcher, leaves and fixtures; PR877 supplies the
retained prefix/perturbation argument, comparison budget, independent word
and dense-check engines; PR862 supplies the subset-inverse and cubic
preparation arguments. Historical relative links inside retained documents
refer to their original layouts. [NOTICE.md](NOTICE.md) records attribution
and substantial OpenAI Codex assistance. Selected construction files and
`upstream/` are unchanged.
