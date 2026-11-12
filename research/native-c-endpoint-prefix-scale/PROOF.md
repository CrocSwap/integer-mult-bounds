# Sharp scale for endpoint-integral native C tensors

This proof was produced by Nick Petalas. Apache-2.0.

Put `O=Z[i]`, `pi=1+i`, and

```text
C = [[1+i,1-i],[1-i,1+i]]/2
  = pi^-1 [[i,1],[1,i]].
```

For `f>=1`, let `C_a` apply C on binary address bit a, and set
`F=C_0 ... C_(f-1)`. Let `C_S=product_(a in S) C_a`. Distinct axes
commute. The endpoint-promised input domain is

```text
L_f = {x in O^(2^f) : F x in O^(2^f)}.
```

Both the input and final output are exact Gaussian integers. No assumption
about intermediate integrality is made. Arbitrary signs, imaginary parts
and independent spectator fibres are allowed.

## Theorem

For every `S subset {0,...,f-1}`, put `j=|S|` and `d=min(j,f-j)`.
The least nonnegative integer e such that

```text
pi^e C_S L_f is contained in O^(2^f)
```

is exactly `d`. The least nonnegative integer s such that
`2^s C_S L_f` is integral is exactly `ceil(d/2)`.

Consequently the least common Gaussian scale for every partial axis product
is `pi^floor(f/2)`, and the least common binary scale is

```text
2^ceil(floor(f/2)/2).
```

The same common scales are minimal for the prefixes of any single fixed
axis ordering. They suffice for every ordering simultaneously. Minimality
is over all inputs in `L_f`, rather than for each individual input.

## Upper bound from the two endpoints

Direct multiplication gives

```text
pi C       = [[i,1],[1,i]],
pi C^-1    = [[1,i],[i,1]],
C^2        = [[0,1],[1,0]],
C (1,1)^T  = (1,1)^T.
```

In particular, `pi C` and `pi C^-1` are Gaussian integral. If `x in L_f`
and `y=F x`, then

```text
C_S x is in pi^-j O^(2^f),
C_S x = C_(S complement)^-1 y is in pi^-(f-j) O^(2^f).
```

For nonnegative a,b, the two fractional modules are nested and their
intersection is `pi^-min(a,b) O^(2^f)`. This proves the bound d, using
only the two endpoint promises. Since `pi^2=2i`, multiplying by
`2^ceil(d/2)` clears those denominators.

## Matching input at every cut

Pair d distinct axes in S with d distinct axes outside S. On each pair
use the integer array

```text
v = e_00 + e_11.
```

On every unpaired axis use `u=e_0+e_1`. Let x be their tensor product,
with factors placed on the specified axes. This has only zero/one real
entries and zero imaginary parts.

The complete transform fixes u and sends each v to `e_01+e_10`.
Indeed C is symmetric and `C^2` is the bit swap, so this identity follows
by multiplying the displayed two-by-two matrices. Thus both x and F x
are Gaussian integral, and x belongs to `L_f`.

At the chosen cut, exactly one axis in each pair has been transformed.
Its four entries, in address order, are

```text
(C tensor I) v = pi^-1 (i,1,1,i).
```

The same identity holds with the pair's axes exchanged. The unpaired u
factors remain fixed. Every coordinate of `C_S x` is therefore a Gaussian
unit times `pi^-d`. A Gaussian unit is not divisible by pi. Hence no
smaller exponent e can clear the Gaussian denominator.

Multiplication by `2^s` increases pi divisibility by exactly `2s`, because
`2=-i pi^2`. The same example is integral after that multiplication if
and only if `2s>=d`. This proves the binary lower bound. At a middle cut
of any fixed ordering, `d=floor(f/2)`, proving both common-scale minima.

## Arithmetic interface consequence

Suppose a supplied array x and its intended `F x` are Gaussian integral.
Scale the input by the theorem's common binary factor, apply the ordinary
axis sequence, then divide the completed output by the same factor.
Every axis output is integral, and the final division is exact. The
returned mathematical output is exactly `F x`.

This statement is an arithmetic composition. It supplies neither a
literal scaling program nor a signed-range bound. An implementation must
still pay both conversions, preserve ownership, allocate sufficient
intermediate signed width and scratch, and admit its actual producer's
endpoint promise. The argument applies independently to every spectator
fibre of the positive rank-one native leaf, so it covers arbitrary f in
the stated tensor model without asserting physical implementation.

## Relation to earlier work and scope

Jerry Chen / CubeJerry's PR7429 defines this positive C tensor at selected
MOVE24472 and requires every axis output to be integral and fit the signed
width. Its f=2 example already distinguishes final and intermediate
integrality. That distinction and the machine implementation are credited
premises, not new findings or replay targets here.

Jose Manuel / jmbarrancoml's PR3091 supplies the physical axis method and
retains Alejandro Zarzuelo Urdiales's sharp `ceil(f/2)` binary reserve for
arbitrary inputs. The new bound uses the additional *integral final
output* premise, so it does not replace that unrestricted-input reserve.

Clear1nsight's PR3382 characterizes the integral entrance on which every
partial coordinate product is already integral. That maximal exactness
lattice is an established result. The proof here does not reconstruct
or use its characterization. The new result is the exact scalar needed
to move the larger endpoint-promised domain into every partial-product
integrality domain, with a matching input at every cut.

No denominator theorem for arbitrary Clifford words, intervening
noncommuting maps, nonintegral final outputs or rounded trajectories is
asserted. The statement concerns exactly the commuting coordinate C
tensors defined above. All five selected framework assumptions remain.
