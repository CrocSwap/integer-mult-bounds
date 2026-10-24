# New centre Gram spectrum at two doubled slots

**Exact equal-label classification; no new kappa.** The full equal-Bell
subspace at width two has minimal-polynomial degree **255**. Its spectrum
adds **212 degrees** to the inherited one-slot degree-881 polynomial.
Every width at least two therefore has minimal-polynomial degree **at least
1093**; every defined nonconstant affine scalar-polynomial inverse needs
degree **at least 1092**. This is not a full width-two upper bound.

The [proof](PROOF.md) reduces the 2^30-dimensional equal-label subspace to
8-by-8 signed root sums and proves the six-representative cover. The
[receipt](RESULT.json) contains exact polynomials, coverage counts and hashes.
The [implementation](spectrum.py) checks all 190239 compressed matrix pairs,
with an independent literal port-sum/symbolic determinant check for all
886 distinct characteristic polynomials. A concrete new eigenvalue is **8**
for A_2, at c=1, u=0, v=2 and the second root coordinate. It is absent from A_1.

This answers the equal-label part of Krzysztof Wojt's
[PR5168](https://github.com/CrocSwap/integer-mult-bounds/pull/5168) higher-width
handoff in [Discussion5142](https://github.com/CrocSwap/integer-mult-bounds/discussions/5142#discussioncomment-19154307).
The predecessor's full one-slot theorem is inherited, not independently
reproved. Its exact certificate and source model are authenticated. Nick
Petalas's PR5120 and Ali Romman's PR4958/PR4720 retain their roles; see the
proof and unchanged predecessor notice for the complete source lineage.

## Reproduce

Use Python 3.12, `numpy==2.4.1` and `sympy==1.14.0`, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/equal-bell-two-slot-spectrum
```

The runner performs normal and optimized checks. Direct, Git-free commands:

```sh
python3.12 -I -W error -B research/equal-bell-two-slot-spectrum/verify.py
python3.12 -I -O -W error -B research/equal-bell-two-slot-spectrum/verify.py
```

Expected marker: `PASS_EQUAL_BELL_TWO_SLOT_SPECTRUM`. The receipt is compared
with exact JSON types. `--write` creates a new receipt exclusively and cannot
overwrite one. Normal replay makes no files. The source digest is checked
before execution. The verifier uses no floating-point spectral decisions
and no FLINT dependency. Candidate discovery used python-flint 0.8.0 in a
separate temporary environment; the complete clean verifier recomputes the
polynomials without it.

The scope is one exact finite spectral classification with a written
all-positive-higher-width implication. No independent human or kernel review
is claimed. No native physical decoder, storage, movement, precision, dirty
restoration or complete supplier is priced. The current source-bound baseline
passes on selected #4610; that metadata check is separate from this historical
query. No selected frontier or multiplication exponent changes.

## Open next questions

1. Classify the unequal outer-label blocks (c,d), c!=d. The equal-label Bell
   transform no longer diagonalizes all payload factors. Start with their
   exact commutator structure and retain the root coefficient once. A full
   width-two upper polynomial remains unknown.
2. Determine whether a scalar-polynomial decoder is useful after all physical
   costs, or provide a different decoder with explicit source/target and dirty
   restoration contracts. This algebraic degree result supplies neither one.

Prepared by Ali Romman with substantial OpenAI Codex assistance, Apache-2.0.
