# A nonconstant chirp for the dirty cyclic inverse

This research construction adds the quadratic diagonal
`D_j=exp(2 pi i a j^2/m)` to PR985's dirty arbitrary-stride solver. The leaf
adds an approximation to `(I-b D Z^w D^-1)^-1 x` to a dirty target. It
restores the source exactly, needs no extra data array, and uses a constant
number of clean arithmetic registers. A negative call is its exact grid
inverse. The complete factor interface uses the original logarithmic
borrowed-array budget and pays only four phase passes for the whole word.

The site coefficients are nonconstant. For `L=8, a=-3, m=16, w=3`, the
shift-edge phase residues are `11,9,7,5,3,1,15,13`. The family includes the
retained single-axis transform chirp `exp(-pi i s j^2/t)` by taking even
`L=t`, `a=-s`, and `m=2t`.

`chirp.py` generates each coefficient from exact integer residues with a
rounded Machin/Taylor evaluator. It implements each rotation with three
reversible real shears and an exact quarter-turn. There is no clean phase
array, cached table, or free phase lookup. Both forward and inverse maps
have a conservative error bound that includes the initial dirty values.
See [PROOF.md](PROOF.md) for the full coefficient, precision, workspace,
restoration, and tape bill.

The phase layer costs `O((L+1)P)` scalar steps, where `P=W+O(log W)` and `W`
is the complete working precision. It does not retain an `O(L)` scalar
count or PR479's fast exponential bound. The data movement stays linear:
`4160L` record moves per leaf is a conservative bound on the two physical
data tapes. A complete word uses its charged PR985 routing plus four phase
passes. Scalar work tapes and descriptor access are also paid in the proof.

Run with Python 3.11 or later and the standard library:

```sh
python3 -I -O -B research/dirty-stride-phases/verify.py
python3 -I -O -B research/dirty-stride-phases/test_package.py
```

The first command checks 910 phase cases, 263 rounded leaf executions,
20 complete generic factor words, two retained radix-four kernel cases,
four larger movement fixtures, and invalid-input controls. All 263 leaf
cases have a nonzero error against the independent ideal interval oracle.
The inputs include odd lowest grid bits and dirty values through `2^80`.
The two retained kernels pay both factor error and execution error to the
128-bit target. The second command checks source mutations and package
relocation. `VALIDATION.json` records the completed checks and their limits.

The oracle uses full-angle rational intervals, direct quadratic residues,
finite geometric sums, and exact dense polynomial elimination. It does
not call the production phase or inverse solver. These are separate
computational paths, not independent human review or a formal theorem.
The exact deterministic receipt is [EXPECTED.json](EXPECTED.json).
`--write /absolute/new/receipt.json` writes a new receipt without overwrite.

Base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
PR985 dependency: `9df42a99dd8497b6e7d46cd2507bb89071372640`.
[Source pins](SOURCE.json) and [attribution](NOTICE.md) keep the predecessor
sources and substantial AI-assistance disclosure explicit.

No new kappa is claimed. The selected frontier and `upstream/` are unchanged.
Arbitrary supplied phase arrays, multi-axis tensor streams, variable
coefficient magnitudes, full-transform composition, fast phase evaluation,
common-label compilation, physical supplier hosting, and the multiplication
reduction remain outside this construction.
