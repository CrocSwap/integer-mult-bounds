# A sharp bound on mixed-precision agreement density

This contribution is produced by Nick Petalas.

For an affine source lattice x=x0+Bz and a rational rounded-linear reader A,
let H be the finite fractional-part image of 2^w AB. Put g=v-w>0 and let
H[2^g] be its subgroup killed by 2^g. The fraction rho of complete parameter
residues on which coarse and fine increments agree satisfies

```text
rho <= 1 / |H[2^g]|.
```

If H has dyadic invariant factors 2^e_i, this becomes

```text
rho <= 2^(-sum_i min(g,e_i)).
```

The bound is attained by coordinate-aligned lattices for every exponent list
and precision gap. For example, three independent order-eight factors and a
two-bit precision gap permit agreement on at most 1/64 of all parameter
residues, and this fraction is attainable. Correlated output coordinates must
be priced through the actual residue group, rather than their number.

This is a **scoped proof with finite corroboration**. [PROOF.md](PROOF.md)
gives the all-dimensional argument, including affine offsets, independence of
the common denominator, natural density and sharpness. The new step is a
finite-subgroup packing bound. The existing universal agreement criterion and
its finite numbers are not claimed as new results.

## Scope and predecessors

woklerx's [PR #1848](https://github.com/CrocSwap/integer-mult-bounds/pull/1848)
proves the affine-lattice universal-cancellation criterion and supplies the
half-open safe-cell geometry. Its canonical-main README is pinned as
historical provenance in [SOURCES.json](SOURCES.json), not imported or replayed.
Credit also woklerx's #1451 product-grid inverse boundary, Gareth Davidson's
dirty-prefix precision discipline, Chafik Boukhalfa's #628 rounded leaf and
Ali Romman's retained kernel lineage. No predecessor executable is run.
The group counting and packing ingredients are elementary; no mathematical
literature-priority claim is intended.

The task changes the uniform-transfer-audit card from auditing a caller of
#4100 to a quantitative precision-interface theorem. The selected metadata
positive control passed. This side result quantifies a failure mode when
precision changes on correlated inputs. It does not establish a new runtime
policy or improve a supplier invoice.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-rounding-agreement-density
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dyadic-rounding-agreement-density/verify.py
```

The registered normal and optimized commands each check:

- 93 distinct two-generator subgroups in (Z/mZ)^2 for m=2,3,4,6,8.
- 60,192 complete offset/gap cases and 599,712 literal point probes, including
  half-grid offset ties and precision gaps one through four. There are 12,423
  tight cases and 47,769 strict cases in this declared census.
- 16,000 comparisons with an independent Fraction rounding oracle.
- 336 sharp coordinate examples, with 6,840 scalar probes, through dimension
  three and cyclic exponents one through four.
- 1,168 complete-period/fiber cases and 780 arbitrary-dirty restoration cases.
- Eight semantic controls for tie direction, full-group versus torsion size,
  correlated coordinates, fixed-embedding strictness and excluded domains.

Each check uses explicit exceptions and remains active with `-O`. The finite
census corroborates the written proof; it does not replace it. The verifier
prints all counts and SHA256 hashes of the six package files. An optional
`--receipt /absolute/path/outside/package.json` writes that generated record
and refuses to overwrite a file. `--check-receipt` recomputes it and compares
canonical bytes. No receipt is handwritten or committed.

## Limitations

The fraction is uniform over a complete parameter period, or natural density
in expanding integer parameter boxes. A bounded box or a chosen distribution
may concentrate entirely on safe inputs. The bound may be strict for a fixed
embedding, even if its invariant factors agree with a sharp example. Odd-order
groups can make the torsion bound uninformative.

Restoration requires unchanged source data and exact addition/subtraction of
the separately rounded increments. Internally rounded nonlinear leaves,
aliasing, overflow, saturation, modular targets, adaptive precision policies
and reachable-state contracts are outside this proof. Physical movement,
precision storage, compiler admission and the complete multiplication theorem
remain separate obligations. No new kappa or selected-frontier change is
claimed. Independent human and formal proof-kernel review are unclaimed.

The bounded verifier has no recursion, network access, third-party dependency
or runtime source import. Its largest ambient group has 64 points and its
subgroup discovery tests 4,096 generator pairs. Python allocates managed
objects during loops; this is a bounded-memory deviation from fixed allocation.
All iteration ranges are fixed in the source. Functions stay below 60 lines.

## Open next questions

1. Determine the exact maximum agreement density for one fixed embedded group
   as the offset varies. Start with H generated by (1/4,1/2), where zero offset
   is strictly below the present bound. The obstacle is simultaneous circular
   coordinate constraints. This would sharpen policy-specific frequency bounds.
2. Bind a complete-period distribution to an actual rounded-linear caller.
   Start by proving the exact affine source domain and its update closure.
   Internally rounded leaves and nonuniform source selection remain blockers.

The structured versions are in [TASK.json](TASK.json). Research stops at the
first sharp bound; these follow-ups are not part of this contribution.
