# Odd division in the full Clifford decoder

The exact canonical four-qubit Clifford decoder cannot use only
Gaussian-dyadic coefficients at any odd width f>=13 or any Bell-sector
width f>=14 with f=2 modulo 4. One explicit eigenvalue forces odd
numerators M. A common odd decoder denominator D must satisfy M|D^2.
At widths 13 and 14, D must be a multiple of 498015 and 30378915.
These divisors need not suffice. No new kappa follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
Use Python 3.12 with the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-odd-division-obstruction
```

Both commands print this prefix and elapsed seconds:

```text
PASS_CLIFFORD_ODD_DIVISION_OBSTRUCTION 89 widths; two infinite-width certificates; 6 rejecting controls;
```

The checker authenticates eight source files, expands two exact
polynomial certificates, checks the symbolic valuation gaps, and
corroborates 89 widths. It also computes a complete literal one-qubit
Gram inverse and verifies both inverse products. A separate example
shows why this theorem does not exclude every noise-free left inverse.
The full predecessor suites are not rerun. No physical decoder, full
four-qubit inverse, Lean or complete caller price is supplied.
All five assumptions and the selected frontier remain unchanged.

## Open next questions

Determine sufficient common denominators for the complete canonical
inverse. The necessary divisor from one spectral block is not enough.

Determine whether a different Gaussian-dyadic left inverse exists.
The saturated column module, not only the Gram spectrum, controls it.
