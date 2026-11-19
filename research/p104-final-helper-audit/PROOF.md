# Exact final helper return and pulse weights

This is a scoped audit of the final split in
[PR #7781](https://github.com/CrocSwap/integer-mult-bounds/pull/7781).
It confirms the rational public map and determines all valid weights on
the three fixed pulse sends. It gives no new kappa and no complete supplier
admission. The source is
[the exact final journal](https://github.com/Clear1nsight/integer-mult-bounds/blob/913fb6febe28cc3ccad1c16de8e45b8bce0da063/research/p104-subdivided-helper-births/complex/FINAL-BIRTH.json).

## Boundary and exact reconstruction

The old helper has role 1164, label 1307, and charts 3 to 517.
The split returns that input at chart 232. A new independent input at
chart 232 has role 1278, label 1531, and returns at chart 517.
Every other owner keeps its source and return chart. The 5,714 paid MOVEs
are identical. The chart spans satisfy strict inclusions
`3 < 232 < 517`, with dimensions that differ by four on each side.
Here the inequality denotes subspace inclusion, not integer order.

The deposited WORD is the carrier before the overlay. The checker applies
the retained overlay and checks its published digest. It then constructs
the split from the stated equations, recovers the old graph in reverse,
and compares both canonical objects with the journal:

| Graph | SHA-256 |
| --- | --- |
| Before final split | `6eba6bb65015df98cf103ce6d12fdd982ba4dcd24a69000bcc58e05477b17c19` |
| After final split | `03ef8f6cc9ebb7394b5c7f8da70d44df965659ae4ff361bbc8d32c7a12121445` |

Let h=1164, j=1166 and f=1278. The source and return direction is
`d = -2 e_h - 8 e_j`. Write p for the full source covector in the journal.
Its h coordinate is 3030720, its j coordinate is zero, and
`p d = -6061440`. If u has zero h coordinate, the source substitution is

```text
u' = u + d (x - p u)/(p d).
```

The inverse substitution is explicit: recover x as `p u'`; recover u_j
as `u'_j - 4 u'_h`; retain every other coordinate except the removed
h coordinate. Thus this input change is invertible on the old public
inputs. The local readout at chart 232 equals x.

Let z denote the terminal rows after the source substitution and pulse,
but before the final terminal edit. The return covector is `-e_j`.
The new f row is `-z_j`, and the new j row is `z_j - 4 z_h`.
Their inverse is

```text
z_j = -new_f,
z_h = -(new_f + new_j)/4.
```

After this terminal inverse, remove the pulse at each of the three sends.
Then apply the inverse source substitution. The recovered graph has the
exact pre-split digest above. The 48 changed rows also match the journal's
complete delta digest. As a cross-check, the retained source split routine
maps this recovered graph back to the same final rows and chart lists.

## Arbitrary inputs and the adjoint

The checker expands every graph row as a rational form in independent
public inputs. It uses integer numerators and one reduced denominator per
row. It checks local chart access and acyclic dependencies before each
expansion. It compares the old 1278-square map and new 1279-square map
with the exact prescribed main blocks and independent helper identities.
It separately reverses all graph edges and all paid routes, exchanges
input and output charts, and expands that adjoint. The result is the
transpose of the prescribed map.

These checks cover 4,904,966 coefficient positions and perform 46,466,187
scalar coefficient products. These are verification counts, not physical
gate or work counts. The full new public operator has rank 1279: each
helper block is the identity and each main block is invertible.

## Complete pulse-weight error law

The pulse sends, in order, are 92740, 98411 and 98796. Their source
coefficients are -5, -2 and -2. The return normalization is eight.
Let C be the local calibration form after the source substitution, and
let y be the fresh input. The exact calibration is

```text
C = -u_j - (x - p u)/757680.
```

The checker verifies this identity on all public input coefficients.
It also checks that each individual pulse has zero response on both C
and the old-input readout. Thus each pulse can vary without changing
either local probe. The common excitation is `y-C`.

Define R_i as the final output response to an additive pulse of the
stated coefficient divided by eight at send i. The full columns are in
RESULT.json. Their sum is `e_f`. Their rows at outputs 17, 38 and f are

```text
         92740   98411   98796
17        -5/2       0     5/2
38         5/2    -5/2       0
1278         0     1/2     1/2
```

This minor has determinant 25/4. The three response columns are linearly
independent over the rationals.

Keep the source substitution, terminal edit and three send locations
fixed. Multiply their complete pulse additions by arbitrary rational
weights lambda_i. Linearity and the probe identities give the full error

```text
error = (y-C) sum_i (lambda_i-1) R_i.
```

The form `y-C` is nonzero because y is independent and C has zero y
coefficient. Therefore the full public map is correct if and only if
all three weights are one. This is an exact classification within this
three-send family. It does not optimize different send locations, new
local forms, added paid transfers or another graph.

If only the fresh-input terms are weighted, the same law holds with y
in place of `y-C`. All old input columns stay unchanged. All eight
include-or-omit subsets are checked. Omitting all three gives exactly
`-y e_f`. Every nonempty proper subset also introduces a wrong old-owner
output coefficient. Twelve direct rational controls check the complete
pulse law on four input assignments, including old and fresh inputs.

## Signed ranks and limits

The split replaces one rank-eight productive target with two rank-four
targets. The native paid rank histogram is identical. Under the retained
48-call multiplicity, its contribution to the signed margin is

```text
48 (2 * 4^(1-kappa) - 8^(1-kappa)).
```

This is positive for `0 < kappa < 1`, because
`2 * 4^t > 8^t` for `0 < t < 1`. The calculation is a local signed-rank
delta. It does not reprice the increased ordinary work or establish a
new finite bound.

The overlay is retained source code; the final constructor, inverse,
adjoint and pulse controls are source-aware checks. The exact row
expander comes from the separately published audit in
[PR #7777](https://github.com/CrocSwap/integer-mult-bounds/pull/7777).
This is computational and algebraic corroboration, not independent human
or proof-kernel acceptance. The earlier fourteen births, full physical
word, caller stream, binary service, ordinary costs, stock and compiler
are not replayed here. The five inherited assumptions remain.

## Open next questions

Does the complete finite application preserve this exact owner boundary
with its stated ordinary allowance? Inspect the published application
and its owner and cost obligations. This audit supplies the exact scalar
map and local rank delta for that review; it does not discharge it.
