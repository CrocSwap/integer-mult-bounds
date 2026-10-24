# Complex component blocks and the clean unitary map

This note gives the algebra used by the independent native review.
The review receipt must bind the actual word before this note can
support a claim about that word.

Let a complex field have real components `(r,i)`. For a Gaussian
dyadic matrix `M`, let `R(M)` be its real matrix in the interleaved
component order. The identities are

```text
R(MN) = R(M) R(N),
R(M*) = R(M)^T.
```

These identities hold for rectangular matrices of compatible sizes.
They follow by expansion of complex multiplication.

## A complete Gaussian ADD

For distinct fields `t` and `s`, the operation `t += (a+ib)s` has
the following real instructions. Omit an instruction with coefficient
zero.

```text
r_t += a r_s
r_t -= b i_s
i_t += b r_s
i_t += a i_s
```

The source field is unchanged. Thus the complete block has the stated
Gaussian ADD matrix. This argument does not apply to a same-field
complex scale. Such a scale needs its own invertible real word.

Let `T` be the common complex frame on all fields in one block.
A complex matrix on the field index commutes with `T` on the spatial
index. Thus a complete real word for `R(M)` can be used between two
common-frame boundaries. This holds at every spatial width and for
every complex input.

An individual real instruction need not commute with `T`. The word
must keep all instructions of the block contiguous. No native child,
map, or frame change can occur inside the block. Only its two
boundaries have the stated complex frame.

The cost is the sum of the real instructions. For the Gaussian ADD,
it is twice the real ADD cost of `a` plus twice the real ADD cost of
`b`. Zero terms have zero cost. A prefix bound inside the block
refers to its physical input components. It is not a claim that
each prefix has the common complex frame.

## The chronological inverse-adjoint

For a real ADD `t += c s`, the inverse-transpose instruction is
`s -= c t`. For a nonzero real scale `t *= c`, it is `t /= c`.
Apply these rules in the original chronological order.

For the complete Gaussian ADD above, the four resulting instructions
give `s -= conjugate(a+ib)t`. Therefore the real inverse-transpose
is the complex inverse-adjoint at the block boundaries.

For a complete unitary code `C`, the same rule gives `C^{-*}=C`.
The new real word need not be equal to the old real word. Its
complete matrix is equal. The field list and the component labels
must both be changed if the caller renames fields.

Each native frame change is unitary. Its inverse-adjoint is the
same exact operator, including its scalar phase. Hence its recipe
and its chronological position stay the same in the dual word.

## The clean local map

Let `P` be the selected-coordinate projection and let `R=I-P`.
Let `S` exchange the two banks on the selected coordinates only.
Set `D=I-2P`. If the native ordinary response is `RC`, the source
code is `C`, and the selected rotations are `(x,y) -> (-y,x)`,
then the complete content map is

```text
F_C = S N_C,

N_C = [ C    0 ]
      [ RC   D ].
```

Equivalently,

```text
X' = R C x - P y,
Y' = C x + R y.
```

This formula retains every arbitrary selected input in `-P y`.
It uses no zero field.

When `C` is unitary,

```text
N_C^-1 = [ C*   0 ]
         [ -R   D ],

N_C^{-*} = [ C   -R ]
           [ 0    D ].
```

Both formulas follow by block multiplication, using `D R=R`
and `D^2=I`. No commutation of `C` with `P` or `R` is used.
The selected-bank conjugate of the inverse-adjoint is

```text
B_C = S F_C^{-*} S = N_C^{-*} S.
```

If `x=(a,u)` and `y=(z,v)` in selected and ordinary coordinates,
put `w=C(z,u)`. Then

```text
X'_P=w_P,  X'_R=w_R-v,
Y'_P=-a,   Y'_R=v.
```

This is the map that the full native replay must check. The forward
and backward maps act as the identity on the other 416 complex
fields.

The physical boundary adds the stated source line, FULL, and ordinary
hole frames. The review must bind those frames and all endpoint
adapters separately. These equations do not admit a routed caller,
recursive child host, or terminal decoder by themselves.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
