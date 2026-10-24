# Uniform direct consumer for the narrow periodic Gaussian Reference

This package binds the actual narrow `Reference` family to the retained
variable-gap cyclic direct solver. It supports every source parameter tuple
that passes the explicit positive-gap and analytic-error gates. It retains
all periodic and cross-cell coefficients, every hole and arbitrary signed
complex inputs. Source generation remains paid.

The [proof](PROOF.md) gives an original-coordinate error theorem. It separates
analytic Reference error, downward coefficient rounding, the rounded direct
solve and final output rounding. Each term has one quarter of the target.
The gap is rounded down adaptively to a power of two; there is no fixed
16-bit floor. A source with an unfunded analytic error is rejected.

For source size n, excess e, target period N=n+e and retained halfwidth w,
the consumer uses at most 4nw^2 factor products and 8nw products per complex
solve, plus O(N+n) input/output scans and grid conversion. Source formation,
its potentially large rational weights, retained caches and factor storage
are explicit additional costs. The selected block is cyclic in source
coordinates. Hole coordinates are copied exactly on the boundary grid.

Run with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/periodic-gaussian-uniform-solve
```

Both registered isolated, warning-strict modes must end with
`PASS_PERIODIC_GAUSSIAN_UNIFORM_SOLVE`. `RESULT.json` contains the exact
finite evidence. Direct `verify.py --write-result` regenerates it;
`verify.py --small` runs the two small source cases and rejection controls.
The normal command writes no package files.

This extends the one-source direct result in
[PR #5260](https://github.com/CrocSwap/integer-mult-bounds/pull/5260) by binding
the all-size solver from
[PR #5284](https://github.com/CrocSwap/integer-mult-bounds/pull/5284) to the
unchanged source and arbitrary hole geometry. It does not prove that a given
production policy funds the gates. It is a host-array consumer, not a native
tape implementation or a complete multiplication theorem. Kappa and the
selected frontier remain unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Credit Jose Manuel for the Reference; JoyboyBrian for the periodic recurrence
and weighted-power bound; Dugongue and Ryanson Jonathan for the prior
band/Woodbury scope; and their retained source notices. `SOURCES.json` pins
the live source inputs and the byte-exact solver retained in branch history.
The full credit and limits are in PROOF.md.

## Open next questions

Pin one production caller policy and fund all four terms with its actual
source size, excess, Gaussian width, truncation radii, target and input bound.
Then pay the original coefficient generation together with ordered physical
delivery, retained factors and restoration. The local arithmetic result does
not supply that bit-cost or tape proof. Independent acceptance of the
inherited analytic and interval contracts also remains separate.
