# Independent review of the direct clean pair

Both direct native words pass. All 209 distinct physical kernels pass
all 512 exact spatial columns, including global phase. The complete
words pass all 640 arbitrary input columns and preserve all 416
outside fields. No material defect was found.

Each word costs 2912 real scalar primitives. Its native profile is
\(96H_1+128H_8+96H_9\), with 320 children and mass 1984. The native
side-map upper bound is 448. There is no boundary adapter or new
field. This is a local result. It does not close a routed caller or
construct a recursive helper host.

## Inputs and independent method

The producer is
[SIMPLE-CLEAN-NATIVE.md](../../new-core-transfer-20261017/low-displacement-20261020/simple-clean-native-20261020/SIMPLE-CLEAN-NATIVE.md).
Its freeze SHA-256 is
`1e08caf1376ffb3a74eac87200e6165c969a08d71d5c028a7c8940093f830089`.
The decompressed payload has SHA-256
`1bdddb7955d0ada6dabcf150fce0a568cd336a846f51be3324c081f10dd374c7`.

The source ports and row code are bound to the frozen clean exchange,
with decompressed SHA-256
`b0432322c28ad3a03af8da550a0b7c7df048c7ff5a0664acc7f78efffcffd083`,
and to the controller's row-capture payload, with SHA-256
`4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7`.
The earlier independent
[clean-exchange review](../clean-centre-exchange-review-20261020/REVIEW.md)
has freeze
`6cd34040ecd7d832f1bae3d44c5a7b97dcc11022d843e48007c5474cc4f3701d`.

The new checker imports only the pinned independent arithmetic
helper. It imports no producer module, Clifford compiler, or Pauli
interpreter. The physical check uses explicit Gaussian-integer
matrix coefficients. The content check uses reverse coefficient
columns and a separate forward-prefix pass.

The two prior providers have the same consumed ports and row code.
The new packet has one direct pair that applies to those common
inputs. It does not retain either provider's old native path.

## Exact physical kernel check

On one nine-bit alphabet define

\[
C_v=\frac{(1+i)I+(1-i)X_v}{2},\qquad
F_9=\prod_{j=0}^{8}C_{2^j}.
\]

Write
\[
b_r(t)=(1+i)^{r-|t|}(1-i)^{|t|}.
\]
Then the exact kernel of \(F_9\) at displacement \(t\) is
\(b_9(t)/2^9\). If \(q_p=C_{v_p}^{-1}\), the exact kernel of
\(F_9q_p\) is

\[
\frac{(1-i)b_9(t)+(1+i)b_9(t\mathbin{\mathrm{xor}}v_p)}{2^{10}}.
\]

The exact kernel of \(q_p\) is \((1-i)/2\) at displacement zero
and \((1+i)/2\) at displacement \(v_p\). These formulas include
the scalar phase.

For each serialized native recipe, the checker evaluates the right
and left monomial maps as full address and Z4 phase tables. It then
uses \(b_r(t)/2^r\) for the native rank-r child. For every input
column, it compares every nonzero coefficient with the independent
kernel above. It also checks the complete support, the address
permutations, and every monomial record field. Cross multiplication
uses integers only.

The checks cover:

| Kernel class | Distinct kernels | Columns per kernel |
| --- | ---: | ---: |
| \(F_9\) | 1 | 512 |
| \(F_9q_p\) | 112 | 512 |
| \(q_p\) on ordinary targets | 96 | 512 |

In total this is 107008 spatial columns and 15040512 nonzero exact
coefficients. The rank-eight kernels have support 256 in every
column; the rank-nine kernel has support 512; the negative-line
kernels have support two. The direct FULL recipe has identity
left and right maps.

The checker also verifies every literal physical frame. Each
line-to-FULL kernel maps the actual positive \(C_{v_p}\) input
to \(F_9\). Each ordinary exit kernel maps \(F_9\) to
\(F_9q_p\). This is an operator check, not an inference from a
frame name. Since all \(X_v\) commute, \(F_9q_p=q_pF_9\).

## Complete forward word

Let P be the actual sixteen selected ports and U the other 96
ports. Write

\[
C(a,u)=(a+Bu,u),\qquad L=[I,B].
\]

The checker verifies that the source code has identity ordinary
rows and identity selected columns. Thus \(C=I+e_PB\), with
\(B_P=0\). It independently replays the complete scalar C word
and verifies its price 1760.

The input types are
\[
X=Q(a,u),\qquad Y_P=Q_Pz,\qquad Y_U=v.
\]

The exact chronology is:

1. Apply \(F_9q_p\) on all 112 X fields.
2. Apply \(F_9q_p\) on all sixteen selected Y fields.
3. Apply \(F_9\) on all 96 ordinary Y fields.
4. Add each ordinary X field to its Y partner, at common FULL.
5. Apply \(q_p\) on each ordinary Y field.
6. Apply C on common-FULL X.
7. Apply the signed rotation on each selected X/Y pair.

The last rotation consists of

```text
Y += X;
X -= Y;
Y += X.
```

It maps \((a+Bu,z)\) to \((-z,a+Bu)\). Each operand is FULL
at its actual event. The ordinary target has already become
\(F_9q_U(v+u)\) and is not used by the later code or rotations.
The full content map is therefore

\[
F_{\rm simple}(a,u,z,v)=(-z,\ u,\ a+Bu,\ v+u).
\]

The checker constructs this event list independently from the
pinned row code and the displayed chronology. It requires exact
equality with the serialized list and stage ranges.

## Complete selected-conjugate inverse-adjoint

Let M be the forward content matrix. Let

\[
A_{\rm in}=\operatorname{diag}(Q,Q_P,I_U),\qquad
A_{\rm out}=\operatorname{diag}(F_9,F_9,F_9q_U),
\]

where the first entry acts on all X and the last two act on selected
and ordinary Y. Both are unitary. The exact physical forward map is
\(W=A_{\rm out}MA_{\rm in}^{-1}\). Hence

\[
W^{-*}=A_{\rm out}M^{-T}A_{\rm in}^{-1}.
\]

Every native kernel is unitary, so its inverse-adjoint is the same
exact kernel, with the same scalar phase. For a scalar ADD, the
inverse-adjoint exchanges source and target and negates the real
coefficient. For a scale, it takes the reciprocal coefficient.
The operation \(W\mapsto W^{-*}\) preserves the chronological
instruction order.

Let S exchange the two physical fields at each selected port.
The selected input operators are the same Q on both banks. The
selected output operators are the same FULL on both banks.
Thus S commutes with both complete boundary operators.
Conjugating every instruction by S only renames its field labels.
The intervening S factors cancel. No runtime swaps are required.

The checker constructs every inverse-adjoint instruction in the
original order and applies S to each target and source. It checks
the full serialized list, wire permutation, and endpoint arrays.
It also checks every intermediate scalar frame after this change.

Direct inversion gives

\[
M^{-1}(a,u,z,v)=(z-Bu,\ u,\ -a,\ v-u).
\]

Transposing and applying the selected permutation on both sides
gives

\[
B_{\rm custom}(a,u,z,v)
=(z,\ u-B^Tz-v,\ -a,\ v).
\]

The checker constructs this formula independently. It compares it
with the complete literal replay and with \(SM^{-T}S\). Both
content inverse orders pass for both words.

All 640 inputs are independent. The 416 outside fields remain
identity output rows and have zero influence on the 224 data
outputs. No helper is assumed zero. No helper progress is claimed.

## Tensor scope

The phase checks above prove exact one-alphabet operator identities.
For width f, take the tensor power of each complete monomial map
and child operator. Equality is preserved by tensor power. This
gives the same field transition for every f.

Each scalar ADD uses two fields with the same current physical
type. Thus it acts on their contents with the stated coefficient
at every width. The two native words and their scalar instructions
therefore have the proved content maps at every width.

This argument does not substitute \(X_v^{\otimes f}\) into a
one-bit polynomial for \(C_v\). Such a substitution would in
general give the wrong operator. The construction uses the full
tensor power of the exact kernel and its complete wrappers.

## Full local invoice and bounds

| Part | Scalar primitives | Native calls |
| --- | ---: | --- |
| X and selected-Y progress | 0 | 128 H8 |
| Ordinary-Y FULL progress | 0 | 96 H9 |
| Ordinary self ADDs | 768 | 0 |
| Ordinary negative-line exits | 0 | 96 H1 |
| Complete C code | 1760 | 0 |
| Sixteen signed rotations | 384 | 0 |
| Total | 2912 | 320 |

The inverse-adjoint word has the same price. All 96 H9 calls have
identity wrappers. The other 224 calls retain two wrappers each,
so the side-map upper bound is 448. There are no boundary adapters,
new fields, private zero fields, or odd divisions.

The scalar-prefix content row-sum peak is 22 for Fsimple and four
for Bcustom. Both have additional binary denominator height one.
These are exact ideal content bounds at scalar-event boundaries.
They exclude child internals, rounding, and recursive precision.

Deleting an ordinary self ADD or a reader ADD fails the independent
endpoint check in both words. Normal and optimized checks give
identical receipts. The reproduction record checks every consumed
file hash again.

The higher native mass 1984 must be compared using the complete
profile above, not only the scalar count. The different 320-child
profile must not be replaced by the older 1520-child profile.
No complete kappa claim follows from this local invoice.

## Reproduction and credit

From this review directory run:

```text
python3 -B check.py --out normal
python3 -O -B check.py --out optimized
```

Both runs must print
`PASS_INDEPENDENT_DIRECT_SIMPLE_CLEAN_NATIVE`.
The receipts and input manifests must be byte equal.

The new-core-transfer lane supplied the direct construction and
its native recipes. The controller lane supplied the row code.
The earlier clean-exchange work supplied the selected rotation
and its physical input and output types. This lane supplied the
independent full spatial-column checks and complete word review.
AI agents prepared these local research records.

No PR, push, commit, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
