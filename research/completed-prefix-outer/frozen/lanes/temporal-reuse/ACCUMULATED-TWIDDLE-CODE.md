# A complete-round code need not have a one-child terminal decoder

## Exact result

Assume that each complete native layer has the stable, portwise left
code

```
T = [[0,Q],[Q^-1,0]],   Q = C_q^tensor(f).
```

The two slices can be two replicas or one fixed physical spectator bit.
They contain arbitrary input. This assumption is more favourable than
an endpoint with changing port labels or a dense data code.

Even under this assumption, the actual synthetic FFT twiddles prevent
the accumulated code from being only a product of disjoint Q factors.
For the actual port `q=11`, two length-four DIF rounds give a terminal
decoder with ten nonzero entries in every row. Two entries have absolute
value `1/2`; eight have absolute value `1/4`. Thus this decoder is not
one native C tensor between monomial maps.

The independent integer-Gaussian checker verifies all 256 formal complex
coefficient inputs of this example, or 512 real input columns. It keeps
the polynomial fourth root separate from the Gaussian unit i. It
verifies the ordinary DIF transform against its Fourier entries, both
complete unitary rescalings, and all 256 coefficient decoder rows. No
producer checker is imported.

This does not exclude a decoder with several native children, a new
endpoint, a different outer transform, or a different recursive layout.
It invalidates the direct use of the disjoint-layer product theorem for
this accumulated FFT code.

## The side of the H0 conversion

Use the actual source conventions

```
C = ((1+i)I+(1-i)X)/2,
S = diag(1,i),
H0 = ((1-i)/2) S C S.
```

Let `C_all` be the tensor product on all current bits and let `S_all`
be the corresponding diagonal phase. T commutes with `C_all`, because
its Q factors and its line-square translations are functions of
commuting translations. Converting a native endpoint `C_all T` gives

```
H0_encoded = E H0,       E = S_all T S_all^-1.
```

The actual current twiddle J follows the butterfly. The implemented
round is therefore `J E H0`. It is not `E J H0`. Codes on distinct bit
offsets commute with later raw butterflies, but this fact does not move
E past its own current twiddle.

The small check retains this order exactly. The ordinary butterfly is
rescaled to a unitary matrix for the finite matrix calculation. The two
complete words have the same scalar rescaling, so it cancels in the
terminal decoder `U_raw U_code^-1`. In the three-axis, two-round example,
each source word is one eighth of the unitary rescaling used in the
checker. No normalization is omitted from the decoder.

## A parity invariant for the complete word

This invariant applies to any odd nonzero port q, not only to the small
example. Let `Z_q` multiply a current address by
`(-1)^(q dot x)`, and let `w` be the Hamming weight of q. Direct Pauli
conjugation gives

```
C_all Z_q C_all^-1 = (-i)^w X_q Z_q,
C_q Z_q C_q^-1 = -i X_q Z_q,
C_q^-1 Z_q C_q = i X_q Z_q.
```

Because w is odd, each of `C_all C_q` and `C_all C_q^-1`
conjugates `Z_q` to `Z_q` or `-Z_q`. The two signs are opposite.
The S phases commute with `Z_q`. Hence the encoded butterfly maps each
q-parity subspace to a single q-parity subspace. It does not mix the two
subspaces.

For the actual weights three and seven, the plus-Q branch preserves
the parity and the minus-Q branch flips it. In the two-slice T word,
the exact class update is

```
z_out = z_in+1,
p_out = p_in+1-z_in              (mod 2).
```

For a general odd weight there is one further fixed parity offset.
This does not change the subspace conclusion. For f tensor columns the
same rule holds for each of the f parity bits, with the same slice bit.

Every twiddle is diagonal in the address bits, with a unit polynomial
coefficient. It preserves these parity subspaces. Later rounds act on
different bit offsets. Therefore a complete stable-port encoded word
permutes the joint parity classes for all completed offsets and the
slice bit. Each block is invertible.

Suppose there are l complete bit rounds and f tensor columns. There
are `2^(f*l)` parity classes for each fixed slice. The ordinary raw FFT
has a nonzero unit entry from every input address to every output
address in that slice, up to its common dyadic normalization. For any
output row, its restriction to each parity block is a nonzero row.
Right multiplication by an invertible block cannot make that row zero.
Consequently the required terminal decoder has a nonzero entry in
each of these `2^(f*l)` input parity classes.

This is a full-word statement. It does not assume that separate
per-round decoder words are used.

## Exact two-round example

The selected port list begins with `q=11`, supported on source axes
0, 1, and 3. The other six local axes factor out of the residual. It is
therefore enough to use three length-four axes and one arbitrary slice
bit, which gives 128 record addresses. Two polynomial coefficient
positions give 256 complex coefficient inputs.

Write each length-four address as `x_low+2*x_high`. In the first DIF
round, apply the three high-bit H0 factors and then their output code
`S T S^-1`. Apply the actual twiddle

```
theta^(-sum_j b_high,j * x_low,j).
```

Then apply the three low-bit H0 factors and their output code. The
length-two twiddle is the identity. The corresponding uncoded word has
entries proportional to

```
theta^(-sum_j x_j * reverse_2(y_j)).
```

This calibration also fixes the DIF bit order. The polynomial fourth
root is `theta=y^(r/2)` and satisfies `theta^2=-1`. It is not identified
with the Gaussian unit i used in the native C kernel. On each pair of
coefficient positions separated by r/2, multiplication by theta is the
signed permutation `(a,b)->(-b,a)`. Thus the two-position check applies
to every such coefficient pair for any even record length r.

The checker uses pairs of integers for every Gaussian number. The
unitary ordinary word has denominator 8; the encoded word has
denominator 32. Their decoder has denominator 256. Its first scalar
coefficient row has the following nonzero real numerators. Bits 0
through 5 give the three addresses, bit 6 gives the slice, and bit 7
gives the coefficient position:

```
0:128, 21:-128, 42:-64, 47:64, 59:64,
62:64, 171:-64, 174:-64, 186:-64, 191:64.
```

Every row has the same support and magnitude counts. With both twiddles
removed, the same checker gives four entries of equal magnitude in
every decoder row. That control isolates the effect of the actual
twiddle.

## Why one native tensor is insufficient

A native tensor of total rank r has exactly `2^r` nonzero entries per
complex address row. Each coefficient is a common power of `(1+i)`
times a Gaussian unit. On the real coefficient tape, the row support
is `2^r` when r is even and `2^(r+1)` when r is odd. Either count is a
power of two. The native frame adapters are monomial, so they do not
change the row support count.

The example's coefficient matrix is real. Each scalar coefficient row
has exactly ten nonzero entries,
at ten distinct input record addresses. Left and right monomial maps
cannot turn this support count into a power of two. This rejects one
native C tensor between such maps, even if the maps permute scalar
coefficient addresses. It does not reject a sum or a product with
additional native children.

## Consequence for a terminal pass program

In a program of complete comparable-volume stream passes, a monomial,
COPY, SCALE, or CLEAR does not increase the number of input dependencies
of one output entry. A binary pointwise ADD can at most double that
number at one dependency depth. The complete parity lower bound
therefore requires at least `f*l` ADD depths for a terminal decoder in
this grammar.

If each such pass scans volume comparable to V, this costs
`Omega(V*f*l)`. On the common rounds of the selected outer layout,
`f=Theta(d/73)` and `l=Theta(p/d)`, so the bound is `Omega(Vp)`.
It does not fit a positive saving below Vp.

This cost statement does not apply to a recursive native child as if
that child were one free ADD pass. It does not cover varying-volume
subcalls, a new packed algorithm, or a different code that mixes the
parity classes before the terminal point.

## Evidence and remaining obligations

The packet is `check_accumulated_twiddle_code.py` and
`ACCUMULATED-TWIDDLE-CODE.json`. The receipt pins the actual port list
and the current selected-bit layer and transform sources. Run:

```
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/check_accumulated_twiddle_code.py
```

Expected status:

```
PASS_EXACT_ACCUMULATED_TWIDDLE_CODE
```

The all-size statements still assume a fixed port label, a common
physical slice convention, and the stated complete-layer T endpoint.
They do not infer those premises from a local centre identity. A
changing role assignment or a different encoded endpoint needs a new
proof. The opposite transform and any new decoder construction remain
separate tasks.

The coherent-port lane supplied the conditional disjoint-layer product
identity. This packet checks why that identity alone does not give the
terminal code of the actual twiddled word. OpenAI Codex assisted this
work under the user's direction. No human review is claimed.
