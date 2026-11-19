# Exact four-qubit spectrum in the Bell sector

For every width f>=14 with f=2 modulo 4, the full normalized Clifford
Gram spectrum has 127 irreducible blocks. The minimum and maximum are
H(-t) and H(t), where t=2^(-(f-2)/2) and PROOF.md gives H explicitly.
Each endpoint has eigenspace dimension 14,400. This gives sharp
condition and recovery constants. No new kappa follows.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).
Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-bell-sector-spectrum
```

Both modes print this prefix and elapsed seconds:

```text
PASS_CLIFFORD_BELL_SECTOR_SPECTRUM 127 blocks 251 order proofs 1143 restriction identities
```

The checker runs the unchanged stabilizer and threshold source suites.
It checks 40 source pins, all polynomial coefficients through two
formulas, interval certificates, complete moment identities, 22 width
checks, four literal one-qubit Gram spectra and six negative controls.
The full ordinary table archive is not re-extracted. No full four-qubit
Gram, Lean, physical decoder or complete caller invoice is supplied.
All five assumptions and the selected frontier remain unchanged.

## Open next questions

Determine the other even central sector, f=0 modulo 4. Its inertia
modules differ from the Bell modules used here.

Construct and price a physical decoder for one specified caller. Include
native preparation, precision, routing, owned recovery and stock costs.
