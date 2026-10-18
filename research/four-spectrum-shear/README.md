# Spectrum-sensitive minimum for three independent same-phase transfers

**Scoped lower-bound theorem with exact canonical checks; no new kappa.**

Three independent transfers `y_j += (C-I)x_j`, with all sources and arbitrary
dirty workspace restored, have these minimum call counts:

| Character spectrum of C | Minimum C/C^-1 calls |
|---|---:|
| {1,i} | 4 |
| {1,i,-1,-i} | 6 |

The alphabet permits arbitrary constant invertible complex role mixing and
any number of restored dirty roles. It permits only the same C or C^-1 as
character-dependent gates. Additional phase functions, free C^2/Pauli/address
gates and clean-input workspace are outside the theorem. This does not establish
an unrestricted multiplier circuit bound, heterogeneous child moment optimum,
supplier admission, or a new multiplication exponent.

[PROOF.md](PROOF.md) gives the arbitrary-dimension case split. It reduces a
hypothetical four-call word to phase-direction span three or four. The former
forces two canonical alternating loops whose simultaneous constant-transfer
images have ranks one and two; Laurent interpolation excludes the latter.
The ordinary six-call construction attains the lower bound.

The binary four-call words use 32 Gaussian role ADDs, or 76 signed real ADDs
per array entry with unit real coefficients. The full-spectrum six-call word
uses six signed role ADDs. These are call/array-operation counts, not a measured
runtime comparison or a complete fixed-tape invoice.

## Reproduce

Python 3.10+ and its standard library suffice, from any working directory:

```sh
python3 -I -B research/four-spectrum-shear/verify.py
```

Expected: `PASS_FOUR_SPECTRUM_SHEAR minimum=6 binary_minimum=4 controls=7 no_new_kappa`.

The program independently reconstructs the two canonical transfer matrices
using closed coefficient formulas and literal matrix products, performs rational
elimination after realification, verifies complete kernel bases and image ranks,
checks all four root values and every dirty input column, and rejects seven
corrupted words/receipts. Positive scope controls retain the valid binary
four-call contract and a four-call rank-two full-spectrum transfer.

Regenerate the committed mathematical certificate to a fresh output path:

```sh
python3 -I -B research/four-spectrum-shear/verify.py --regenerate /tmp/four-spectrum-certificate.json
python3 -I -B research/four-spectrum-shear/verify.py --certificate /tmp/four-spectrum-certificate.json
```

Every ordinary replay compares the committed certificate with deterministic
regeneration. `--receipt PATH` records source hashes and verification details.
Regeneration refuses an existing output. The proof is not machine-formalized;
finite checks are not a formal verification of all complex mixing matrices or
the multiplication theorem.

## Attribution and context

Prepared by Richard Hoekstra with substantial OpenAI Codex assistance in
mathematics, implementation, checks and prose. New material is Apache-2.0.
No independent human review or literature-priority claim.

PR1235 studies individually calibrated endpoint gauges without role mixing.
This package allows arbitrary constant role mixing but restricts paid calls to
one common phase function. PR836's unitary/nonunitary formal-group diagnostics,
PR800's fixed Clifford-word valuations, PR720's abelian three-register bit
theorem and PR990's private ADDRESS-query batch have different alphabets or
endpoints; their theorems are not imported. See NOTICE.md for links and credit.
No selected record, supplier, frozen package or repository framework is changed.

## Open next questions

1. Does the intermediate spectrum {1,i,-1} admit four calls? Case 1's four-root
   interpolation does not settle it. Start with its degree-three vanishing
   polynomial and phase-direction span four; a finite candidate failure alone
   would not be a universal exclusion.
2. Can explicitly paid additional character-dependent gates lower the call
   count? Specify and charge those gates first; their admission changes the
   fixed-projector normalization used in this proof.
