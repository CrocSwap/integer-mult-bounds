# Conditional spectator terminal product

This annex adds an exact terminal factorization for complete portwise layer
endpoints. For one fixed spectator bit z, both slices contain arbitrary data.
Suppose each complete layer has endpoint

```text
T_j = [[0,Q_j],[Q_j^-1,0]],
Q_j^2 = X_vj,     Q_j^4 = I,
```

where the Q_j commute and act on the active coordinates identically on both
z slices. Then the ordered product is `Q_all M`,
where `Q_all=prod_j Q_j` and M is one explicit affine address map.
The identity holds for every positive layer count and all stated tensor
widths. For disjoint orthonormal native layer directions, its inverse uses
one gathered C_D call, with D equal to the total number of layer directions,
plus the stated gather, sign, unit-scale, and affine maps. Every cost remains
due. No new zero field is required by the operator identity.

The [complete proof](frozen/lanes/coherent-port/SPECTATOR-TERMINAL-PRODUCT.md),
[mandatory phase qualification](frozen/lanes/coherent-port/SPECTATOR-TERMINAL-CONJUGATION.md),
and [independent product-order receipt](frozen/lanes/schur-selection/spectator/TERMINAL-PRODUCT-REVIEW.json)
define the claim. [SOURCES.json](SOURCES.json) pins every retained input.
This is a conditional terminal theorem. It gives no complete kappa or
supplier improvement and makes no claim of applicability to the current
selected construction.

## Exact order

For m layers, put `epsilon_j=(-1)^(m-j)`, let V be the binary sum of all
v_j, and let V_minus sum those v_j with negative epsilon_j. Let S exchange
the two spectator slices. Then

```text
T_m ... T_1 = diag(U,U^-1) S^m = Q_all M,
U = prod_j Q_j^epsilon_j,
M = X_Vminus diag(I,X_V) S^m,
M^-1 = S^m diag(I,X_V) X_Vminus,
(T_m ... T_1)^-1 = M^-1 Q_all^-1.
```

The inverse order matters when m is odd. The native inverse identity retains
the exact factor `(-i)^D` and both sign passes. A gather must meet the actual
complete-row, chunk, guard, volume, and depth contracts before a C_D child
is admitted. The theorem does not supply those contracts or their price.

## Phase and current-twiddle boundary

If S_j is a monomial on layer j's active coordinates and is identity on z
and all other layers, the conjugated product is
`S_all (T_m ... T_1) S_all^-1`. Its inverse is
`S_all M^-1 Q_all^-1 S_all^-1`. These wrappers still have execution costs.
A phase that depends on z need not commute with another T factor, even if
it leaves the z address fixed.

The actual conversion `H0=b S C S`, with `b=(1-i)/2`, has the required
layer-local S. But a returned native code E_j appears as
`(S_j E_j S_j^-1) H0_j`, before the current outer twiddle. That DIF twiddle
depends on the new branch and unprocessed bits. It cannot be absorbed in
the layer-local conjugation. An application must prove a complete-round
portwise endpoint after the twiddle, implement an exact typed encoded
twiddle, or return the raw H0 layer.

The exact [layer source](sources/upstream/upstream/build/sections/05-layers.tex)
is retained. Its SHA-256 is
`20cfc8d12099d4e4ed9e3e7eeb6162edd9b6e0e076f24693364cd24377252594`.
It is the blob consumed by the addendum at historical commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It also equals the already
retained parent-package source at
`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`.

The unchanged paired controller is not an application. Its endpoint mixes
data and modes. Reshaping two replicas as spectator slices preserves that
map. The retained [controller proof](frozen/lanes/encoded-controller/ORIGINAL-PAIRED-CONTROLLER.md)
and [separate review](frozen/lanes/coherent-port/ORIGINAL-PAIRED-CONTROLLER-PROOF-REVIEW.md)
give the conditional 2912 witness against mode-only restoration in the
stated source word. The source rows and route-distinctness checks remain
inherited premises. This annex does not rerun that controller or its route
reconstruction. A changed controller or mixed terminal remains outside that
negative result.

## Reproduce

Use Python 3.11 or later and its standard library. Use a new output directory
outside this annex, with an existing parent directory and at least 3 GiB free.
From this annex directory, run:

```text
python3 -I -B replay.py --out /tmp/spectator-terminal-annex
```

The runner executes both unchanged checkers normally and with `python -O`,
one process at a time. It makes a private copy for each run and removes that
copy's expected output before execution. Every newly written receipt must
equal the frozen receipt byte for byte. The normal and optimized receipts
must also match. The final line is:

```text
PASS_SPECTATOR_TERMINAL_ANNEX
```

The producer checks all 112 actual labels, one through six layers, 1,344
slice columns, and 28,224 nonzero kernel entries. It rejects 672 omitted
controlled translations and 672 wrong inverse orders. The separate checker
uses independent formal fourth-root generators for 64 cases, with one
through 32 layers and both slices. The general conclusions depend on the
written proof, not extrapolation from those finite cases.

No checker source was adapted. The runner changes no frozen input. It does
not run the accepted parent package's suite. It does not establish a full
layer endpoint, native gather admission, owner schedule, complete finite or
recursive cost, precision, integer recovery, or a supplier. The addendum's
written phase argument is a review obligation separate from the two finite
checkers. The source [notice](NOTICE.md) retains credit and license terms.
