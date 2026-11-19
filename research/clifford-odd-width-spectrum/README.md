# Exact Clifford spectrum at every odd width

For the full four-qubit Gaussian-dyadic Clifford alphabet, this package
proves the exact Gram spectral endpoints for every odd width `f >= 13`.
Two explicit degree-eight polynomials give both endpoints. Their blocks
swap with `f mod 8`. The exact Gram condition number approaches one
with leading error `408 * 2^(-(f-1)/2)`.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json), and [CREDITS.md](CREDITS.md).
The certificate includes all 81 spectral polynomials, 318 strict order
proofs on full rational intervals and two positive-endpoint proofs.
The infinite-width conclusion follows from those interval proofs.

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-odd-width-spectrum
```

Both modes print this prefix, followed by elapsed seconds:

```text
PASS_CLIFFORD_ODD_WIDTH_SPECTRUM 81 blocks 318 order proofs 2 positive endpoints
```

The unchanged threshold checker runs. Exact multiplicity and orbit
checks cover 35 odd widths. Literal one-qubit checks cover all four
odd residue classes and four complete Gram matrices. The ordinary
character projection is a retained mathematical input. Its full source
archive is not re-extracted here.

No physical decoder, new kappa, even-width endpoint classification,
independent human acceptance or formal-kernel proof is claimed. The
selected frontier and all five framework assumptions remain unchanged.

## Open next questions

Construct and price a decoder for one exact caller, including precision,
routing, owned-state recovery and stock. The algebraic inverse bound
does not supply these costs.

Derive the exact even-width endpoints from the quadratic-form
stabilizers. Do not insert an even width into the odd-sector formula.
