# A translated dyadic escape for the actual reader

This scoped constructive proof is produced by Nick Petalas. Apache-2.0.
It uses the actual factors of Ali Romman's PR5646 as supplied inputs.
Their source identities and native application are cited premises, not new
verification claims. Indices below are zero based.

## Algebra and changed basis

Let R = Q[C2^9]. Write tau_g for the group element indexed by the nine-bit
integer g, so tau_g tau_h = tau_(g xor h). The ring is commutative. In any
representation by nine commuting involutions, tau_g acts as the corresponding
translation. The argument therefore holds in the source's positive-width
tensor representations, with arbitrary payloads and arbitrary dirty banks.

The supplied scatter J is 112 by 30, the supplied gather L is 30 by 112,
and L J = 0 over R. A scatter entry at port p initially has group element
tau_(q_p). L is the supplied inverse-Walsh translation kernel after PR5646's
ten constant dyadic basis operations.

Put A = I_30 + 2 tau_258 E_(4,1). Since 4 differs from 1, E_(4,1)^2 = 0.
Thus A^(-1) = I_30 - 2 tau_258 E_(4,1), over the dyadic subring as well.
Define

    L' = A L,        J' = J A^(-1).

Only two factor vectors change:

    L'_4 = L_4 + 2 tau_258 L_1,
    J'_1 = J_1 - 2 tau_258 J_4.

The other rows of L and columns of J are identical. Matrix multiplication
proves J'L' = JL and L'J' = A(LJ)A^(-1) = 0. This is an elementary basis
over the translation ring. It is outside the constant-coefficient dyadic
row-ADD alphabet whose local optimum PR5646 proved. The basis itself is
compiled into the two factors; there is no runtime A or A^(-1) pass.

## Complete arbitrary-input endpoint

On data x and a dirty bank z, execute these four cross-bank shears:

    z += L' x
    x += J' z
    z -= L' x
    x -= J' z

After the first scatter, x is x_0 + J'z_0 + J'L'x_0. The second gather
returns z exactly to z_0 because L'J' = 0. The last scatter therefore returns

    x = (I + J'L') x_0 = (I + JL) x_0,        z = z_0.

Every initial bank value is arbitrary. No zero assumption, fresh centre,
COPY, CLEAR or additional Gaussian call is used. These statements concern
the recoder's cross-bank word; the supplied native section still requires
its own thirty-field bank and its original implementation contract.

## Enumerated coefficient and routing invoice

The exact reconstruction and enumeration in verify.py gives:

| Quantity | PR5646 factors | Translated factors |
|---|---:|---:|
| Scatter coefficients | 208 | 220 |
| Gather coefficients | 9968 | 9940 |
| Four-shear coefficient ADDs | 20352 | 20320 |
| Nonidentity translation applications | 20352 | 20320 |
| Axis-translation units | 92036 | 91924 |
| Common denominator | 960 | 960 |
| Largest absolute coefficient | 1 | 9/8 |
| Scatter infinity norm, absolute coefficient sums | 9/4 | 43/16 |
| Gather infinity norm, absolute coefficient sums | 1036/15 | 72 |

Each factor occurs twice. The support saving is therefore
2 times (28 removed gather coefficients minus 12 added scatter coefficients),
which equals 32 ADDs. The earlier rational construction PR5919 costs 20344
ADDs with denominator 1200. Its published count is cited context; its new
basis operation and scientific suite are not replayed here.

Every shift is explicitly charged. An axis-translation unit means one
specified axis involution in a direct decomposition of tau_g; its price is
popcount(g). The checker enumerates all coefficients in both passes. It
returns these histograms for weights zero through nine:

    old: [0, 844, 0, 7108, 0, 8750, 0, 3366, 0, 284]
    new: [0, 852, 0, 7048, 0, 8776, 0, 3374, 0, 270]

Thus a backend charging every translation as its axis-by-axis decomposition
saves 112 such units as well as 32 coefficient ADDs. If that backend must
restore the source layout after every ADD, two route passes cost respectively
184072 and 183848 units. This is a declared routing invoice, not a bound on
physical tape work. The new shifts must still be installed and priced in
an actual caller. Coefficient multiplication is not free.

The denominator adds no odd factor. The numerator bound at denominator 960
rises from 960 to 1080, and the factor norm bounds rise as shown. A complete
arithmetic or precision price may therefore offset the support saving.

For example a conservative explicit prefix/suffix bound is

    B = ((1 + 72)(1 + 43/16))^2 = (4307/16)^2.

On the stacked coordinate infinity norm, a gather or any partial coefficient
pass has norm at most 73; a scatter or any partial coefficient pass has norm
at most 59/16. Every prefix and suffix uses at most two of each. The same
bound covers the reversed signed inverse. This bound is uniform in payload
volume. It does not prove an arithmetic-interior or fixed-tape implementation.

## Evidence and limits

The checker compares every coefficient of the two changed columns' product,
including the 4608 nonzero baseline coefficients and possible new positions.
It checks all untouched factor vectors and the literal inverse basis.
An exact integer-scaled implementation executes both full four-shear words
on one dense 512-address payload and one arbitrary nonzero dirty bank.
It compares all 57344 data coordinates and all 15360 bank coordinates and
counts executed coefficient instructions. Four algebraic corruption controls
and two invalid-shift controls reject. The algebraic argument above covers
arbitrary inputs and every representation; this finite payload is corroboration.

The result is one explicit coefficient-support improvement. It proves no
basis optimum, full physical runtime saving, paid recursive-moment gain,
new kappa, admitted supplier, selected-frontier change or complete
multiplication theorem. Source native correctness, thirty-field section
storage, rational arithmetic interiors, routing/tape realization, whole-caller
precision, all-size compilation and outer use retain their separate obligations.
