# Finite kernel certificate for the cyclic partial h24 witness

This bundle uses the selected portable arithmetic receipt and its 46-bin bit
and 40-bin complex histograms. It has no external Python imports and reads
only the bundled `inputs/` files by default. Reproduce with:

```sh
python3 generate.py
lean KernelNew.lean
```

The bit atom saving is `15513/125000000`. The complex saving is
`5893637/62500000000`; the assembled κ is `942802139/10000000000000`.
The complex profile has `m=576`, `W=164065440`, rank sum `94499831360`,
and maximum child width 572. At grid scale `10^30`, the strict moment deficits
are `6553956019943600618329002097382` (bit) and
`14928275267260630367060679744` (complex).

The generator checks source hashes, rank sums, all 47 exact assembly slacks,
and seven margins against `inputs/assembly.json`. `KernelNew.lean` checks
finite atanh24/log and exp8 upper grids, their domain guards, and signed
assembly arithmetic via `by decide +kernel`. `lean.log` records that all
three named theorems have no axioms.

The analytic interpretation of the upper enclosures, the physical-event
histogram semantics, and the all-size circuit theorem are outside this finite
Lean certificate.
