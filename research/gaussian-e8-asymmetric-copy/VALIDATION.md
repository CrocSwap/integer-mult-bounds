# Validation and limits

## Replays

The full command passes on macOS arm64 with Python 3.9.6 and Python 3.14.6:

```sh
python3 -B research/gaussian-e8-asymmetric-copy/verify.py
/opt/homebrew/bin/python3.14 -B research/gaussian-e8-asymmetric-copy/verify.py
```

Both runs rebuild the evidence and match the saved certificates exactly after JSON normalization.
The geometry replay takes about 12 seconds in the development environment.
The six-plane replay takes about 3 seconds.
These timings describe validation and make no performance claim.

## Completed coverage

- Generate all 240 doubled E8 roots and all 60 Gaussian line orbits.
- Enumerate all root flats through rank three.
- Check that each of the 1,770 line pairs belongs to exactly one rank-two flat.
- Check 480 ranks through independent rational realification.
- Inspect all 4,176 rectangles in representative planes of sizes two, three, and six.
- Enumerate all 4,120 corresponding partial-diagonal fitting matrices.

- Verify the exact cost-60 decoder of fifteen orthogonal frames.

The incidence and decoder checks add the following coverage:

- Verify all 60 six-plane incidence identities and their eight-line clique witnesses.
- Enumerate all 900 full-six-plane rectangle types and their complete binary kernel.
- Verify the 960 hyperplane types, rank 880, and all 80 independent kernel vectors.
- Verify the hyperplane coefficient identity and the feasible cost-820 example.

The root-flat census is:

| Rank | Number of lines in flat | Number of flats |
|---:|---:|---:|
| 1 | 1 | 60 |
| 2 | 2 | 360 |
| 2 | 3 | 320 |
| 2 | 6 | 30 |
| 3 | 4 | 960 |
| 3 | 6 | 480 |
| 3 | 15 | 60 |

The geometry replay also classifies all 1,124,250 unordered pairs of rank-three flats.
Exactly 51,090 pairs have pairing rank two.
This census covers full flats, not their arbitrary subsets.

## Negative controls and independent audit

The six-plane verifier rejects 60 witnesses with a removed index.
It also rejects 60 witnesses with an orthogonal replacement index.
Explicit Gaussian examples refute the stronger claim that low pairing rank implies low joint support dimension.
The command rejects optimized Python, which would disable assertions.

A separate audit reconstructs the roots and geometry without importing the package's geometry or verifier modules.
It uses integer Hermitian determinants for plane membership.
It checks the incidence witnesses and the hyperplane identity by direct binary elimination.

```sh
python3 -B research/gaussian-e8-asymmetric-copy/independent_audit.py
```

This independent command passes on Python 3.9.6.
The audit supports the finite certificates, not a formal verification of the multiplication theorem.

The written proof handles arbitrary numbers of planar and support-saturated totals.
The finite identities extend by linearity to all binary coefficients in their stated classes.
Repeated rectangle types do not weaken the bounds because their physical charges are nonnegative.

## Search and stopping rule

The initial asymmetric probe considers full six-line planes as reader and source supports.
Exact incidence identities settle that entire domain and extend it to arbitrary sources on one side.
The hyperplane probe includes all 900 ordered orthogonal-normal pairs and 60 equal-normal pairs.
The coefficient identity gives a cost floor before any supplier implementation.
The failed optimistic deficit ends these mechanisms at the mathematical stage.

A preliminary bounded mixed-integer diagnostic contributes no proof claim or numerical bound.
The committed results use exact finite identities and written rank arguments.
Partial supports and unrestricted mixtures remain open.

The final overlap check finds PR738's distinct general floor of 40.
This package does not replay or strengthen that general bound.
All new files stay within this research package.
The existing generators, selected certificates, and `upstream/` remain unchanged.
The unchanged repository-wide suite and selected supplier's cold replay do not run for this isolated research note.
