# Conditional A-stage native capacity

## Contract

Let the 632 initial normalized complex fields have integer real and imaginary
components in `[-L,L-1]`, with `L=2^(P-1)` and `P>=3`. Execute the pinned
zero-frame scalar prelude, including its logical monomial warps, exactly.
Write its resulting normalized rows as `b_r`.

**Adapter endpoint hypothesis.** At entrance to A, physical register r is
`T_start[r] b_r` forward, or `conjugate(T_start[r]) b_r` in the inverse-transpose
orientation. The residual adapters' implementation, interiors and cost are not
proved here. The prelude rows specify the required entrance values, rather than
assuming that every A entrance value is independently integral.

A logical warp is the retained Gaussian monomial `K_G`, or its inverse, forward;
it is the conjugated monomial in the inverse-transpose orientation. These
operators permute real/imaginary input components with signs. Both preserve
integer grids and symmetric component bounds. The emitted dual scalars swap
ADD ports and negate their coefficients, and invert scale factors, exactly as
in the pinned emitter.

The claimed capacity covers A-stage frame/warp circuit operands and endpoints,
scalar endpoints and exact ADD increments, the sum of target and increment,
and the specified C numerator arithmetic below. It also covers the explicit
zero-frame prelude scalar endpoints and increments. It excludes arithmetic
used to manufacture a scalar increment, residual adapters, centres and later
phases, recursive approximation and error accumulation. A sufficient capacity
is not an optimal-width theorem or a complete physical implementation.

## Canonical frames and the paired bound

The first listed gate acts first. For a rank-r frame, the retained exact circuit
is `adjoint(K_U) + [C(e0),...,C(e[r-1])] + K_U`. Both K circuits are Gaussian
monomials. Rank zero is identity, and full rank uses the Fourier shortcut.
The replay validates independent frame rows and this gate shape for all 1,124
frames in each canonical word, and invertibility of every declared warp matrix.

After k distinct C factors, a coefficient is a product of k factors
`(1+i)/2` or `(1-i)/2`. Distinct axes give distinct input coordinates.
For even k, a coefficient has one nonzero real or imaginary part of absolute
value `2^(-k/2)`. For odd k, both parts have absolute value `2^(-(k+1)/2)`.
Consequently every real-component row has

```
E_k = ceil(k/2) fractional bits
M_k = 2^ceil(k/2) real row l1 norm.
```

Monomial phases and permutations at either end preserve these facts for
all rows, including prefixes of the canonical frame circuit. Conjugation
preserves both quantities. For the backward interpretation the frame is
`T_U^(-transpose) = conjugate(T_U)`, since T_U is unitary. It is generally
neither T_U nor its adjoint. This distinction matters even at frame `[45]`.

For a conversion, use the explicit execution list

```
adjoint(frame(old)) + logical_monomial + frame(new).
```

For a climb the logical monomial is identity. Applied to the actual entrance
`frame(old) u`, each inverse prefix cancels a suffix of that same frame
operator. Intermediate values are therefore prefixes of the old frame on u,
then prefixes of the new frame on the monomial image of u. This argument
uses the correlated entrance identity; it does not replace intermediate
values by independent inputs. It also holds after conjugating the complete
list for the backward orientation. This is a chosen exact arithmetic
realization; its native instruction, access and storage cost is not priced.

## Pair-first C arithmetic

For sign s, write the two current complex inputs as `a+ib,c+id`. Form

```
real left  = a - s*b       real right = c + s*d
imag left  = b + s*a       imag right = d - s*c
real numerator = real left + real right
imag numerator = imag left + imag right
```

Then divide the two numerators by two. The capacity includes the four inputs,
the four pair values, both complete numerators and the outputs. It assumes this
pair-first order, rather than arbitrary four-term summation order.

For forward C number k, the pair expressions each have norm `M_k` on the
normalized input coordinates; the full numerator has norm `2M_k`. Thus the
maximum is `2^(ceil(k/2)+1)`. The maximum grid depth of the inputs and partial
numerators before division is `E_(k-1)`.

For inverse C removing factor k, denote its original pre-C inputs by
`A+iB,C+iD`, with original C sign t. The inverse sign is `-t`. Substitution
in the four pair expressions gives

```
A+tD, A-tD, B-tC, B+tC,
```

whose two final sums are `2A,2B`. The two last-axis input supports are disjoint,
so every pair and complete numerator has norm `2M_(k-1)`. Including the current
operands, the maximum remains `2^(floor(k/2)+1)`, with maximum grid depth E_k.
Conjugating changes t to -t and preserves these conclusions. The maximum over
all steps in a rank-r inverse or forward circuit occurs at its largest rank.
`numerators.py` enumerates these exact component rows for ranks 1 through 9,
both directions and both signs, independently of the supplier row propagation.

If the completed C output lies on the common grid `2^-D`, its encoded numerator
is twice an integer on that grid. Therefore division by two is exact on this
fixed grid. The output grid bounds below include every C endpoint. No rounding
or destructive loss of a fractional bit is permitted.

## Substituting the actual normalized rows

A normalized register row is `sum q_(v,w) K_w x_v`, with reduced formal warp
words w and rational dyadic q. Let d be its maximum coefficient denominator
depth, and N the sum of absolute q. Substitution of actual Gaussian monomials
shows its components have grid `2^-d` and absolute value at most `L*N`.
Formal atoms need not be independent for these sufficient bounds. Actual
coincidences may cause further cancellations.

A frame prefix adds E_k to the coefficient depth and multiplies this bound by
M_k. Native C pair-first arithmetic multiplies N by the preceding subsection's
factor. An ADD increment is propagated as the exact row `q*source`; the final
row is combined and reduced. We also include the conservative temporary bound
`N_target + abs(q)*N_source` in the common frame. Constructing the increment
itself, such as computing `7*source/8`, requires its own lowering contract.

The replay checks chronological old/new frames, common-frame ADD operands,
all prelude and A scalar rows and warps, and stops immediately before centres.
There are 5,964 prelude scalars, 72 prelude warps, 4,028 A scalars, 24 A warps
and 1,020 A climbs per orientation and provider. The A source list has 4,052
entries, including its 24 warps. A separate integer engine, with fixed
denominator `2^32`, reproduces the digest of every changed normalized row.
All divisions in that engine check their remainders.

## Capacity and comparison

The resulting exact rational **upper envelopes** are the same in both providers:

| Bound constructed here | Forward D | Forward B | Backward D | Backward B |
|---|---:|---:|---:|---:|
| One charge per C | 8 | 78336 | 11 | 9856 |
| Paired frame, generic partials | 5 | 9792 | 7 | 1536 |
| Paired frame, pair-first C | 5 | 4896 | 7 | 934 |

B means every covered real value has absolute value at most `L*B`.
The first control charges a denominator factor two and norm factor two for
every C, plus generic four-term numerator bounds. The middle control changes
only the frame bound. The last row also uses the proved pair-first partial
arithmetic. All use the same source rows and covered events; these controls
are not claimed to be upstream production allocations.

On a common fractional grid D, require the **strict** signed inequality

```
L * B * 2^D < 2^(W-1).
```

This reserves the positive signed limit. A Gaussian phase may negate the
allowed normalized input -L to +L; equality at the positive limit would be
unsafe. For every P>=3 the separate sufficient widths are

| Bound | Forward width | Backward width | Common D | Common width |
|---|---:|---:|---:|---:|
| One charge per C | P+25 | P+25 | 11 | P+28 |
| Paired frame, generic partials | P+19 | P+18 | 7 | P+21 |
| Paired frame, pair-first C | P+18 | P+17 | 7 | P+20 |

At P=64 the final result is 82 bits forward, 81 backward, or an 84-bit common
layout, eight fewer than the 92-bit common control. This is a reduction in a
proved sufficient capacity bound under the stated scope, not a measured
physical storage or runtime saving. The exact normalized exit still needs
three fractional bits, so the guards cannot simply be cleared at A's end.

No multiplication exponent, recursive child profile, supplier admission,
selected frontier or complete physical invoice follows from this theorem.
