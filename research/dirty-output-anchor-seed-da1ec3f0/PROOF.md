# Dirty-anchor product fanout

Work over an abelian group of exponent two, in particular over bit vectors with XOR. Let `p` and each `t_i` be values computed by complete XOR children from read-only inputs that are disjoint from all target rows. Let `A_0,...,A_(q-1)` be arbitrary, independent dirty output rows. Each child toggles only its designated target and leaves its inputs and other rows unchanged.

For the output map

```text
A_i' = A_i XOR p XOR t_i,       0 <= i < q,
```

where every `t_i` is a private value from its own complete child, use this schedule:

```text
for i = 1,...,q-1:  A_i ^= A_0
child:               A_0 ^= p
for i = 1,...,q-1:  A_i ^= A_0
for i = 0,...,q-1:  A_i ^= t_i
```

Write the entry values as `a_i`. After the first fanout, `A_i=a_i XOR a_0` for `i>0`. After the common child, `A_0=a_0 XOR p`. The second fanout gives

```text
A_i = a_i XOR a_0 XOR a_0 XOR p = a_i XOR p,
```

for every `i>0`; `A_0` also equals `a_0 XOR p`. The private calls then produce the specified output map. This proof places no restriction on any dirty output value or on `p` and `t_i`.

## Complete local invoice

The direct implementation calls the common child once per output and then the private child once per output: `2q` complete children. The dirty-anchor implementation uses one common child, `q` private children, and two full-width affine fanout waves:

```text
children:          q + 1
affine row ADDs:   2(q - 1)
bit XORs at width w: 2w(q - 1)
clean helpers:     0
child uncomputes:  0
input copies:      0
frame changes:     0
```

The exact net saving under a complete child price `mu` and a complete width-`w` ADD price `alpha(w)` is

```text
2q*mu - ((q+1)*mu + 2(q-1)*alpha(w))
= (q-1)*(mu - 2*alpha(w)).
```

This schedule reduces the recursive-child count whenever `q>1`. The fully charged local implementation is cheaper exactly when `mu>2*alpha(w)`. No child/ADD price ratio is guessed here. If the child is a recursive multiplication whose charged cost grows faster than width, the two affine waves form a lower-order linear term; this asymptotic observation does not identify a physical provider or a finite base-case threshold.

## Minimum number of dirty-row ADDs with one common child

Restrict the interface to the `q` target rows, row ADDs `A_i ^= A_j` with `i != j`, and exactly one common-product child that toggles one target row `k`. No extra helper, COPY, CLEAR, or second common-product child is allowed. Any private child calls use independent read-only source symbols; they may be interleaved, but they do not change the target-linear map or the coefficient of `p`. Let `U` be the product of all row-ADD matrices before the common child and `V` the product after it. Because every target entry is arbitrary and must be preserved apart from the requested common-product translation, `VU=I`. The coefficient of `p` at the endpoint is `V e_k`, which must be the all-ones vector `1`.

Each row ADD changes the Hamming weight of a target-coefficient vector by at most one. Therefore any word realizing `V e_k=1` needs at least `q-1` row ADDs after the child. Also `U=V^{-1}` implies `U 1=e_k`; taking the all-ones vector through the pre-child ADD word reduces its weight from `q` to `1`, requiring at least `q-1` further row ADDs. The total is at least `2(q-1)`, attained by the two fanout waves above.

This is a lower bound only for the named row-ADD alphabet and single-child boundary. It does not cover temporary rows, COPY/CLEAR, additional shared children, or alternative whole-register linear primitives.

For `q=112`, the direct bill is 224 rank-one child calls; the dirty-anchor bill is 113 child calls and 222 complete row ADDs. At scalar width one that is 222 XORs. For eight hypothetical 112-port blocks, the rank-one profile would fall from 2,412 to 1,524, while 1,776 scalar XORs remain explicit. The rank-only ceiling screen is therefore reported separately from the additive term.

## Reversibility

Each child is an XOR oracle, hence self-inverse with its inputs fixed. Every affine fanout is a CNOT-style XOR and is also self-inverse. The complete inverse first reverses all private children, then applies the second fanout wave, the common child, and the first fanout wave. It restores every original arbitrary target and leaves all source inputs unchanged. There is no private state to clear.

The package's exhaustive tests treat each product result as an arbitrary width-`w` value. This verifies the interface identity for all child outputs, rather than relying on a particular multiplication truth table. The written proof covers all `q`; the tests exhaust every state through `q=5` at the listed widths and reject four malformed schedules.
