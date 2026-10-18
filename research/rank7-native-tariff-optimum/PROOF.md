# Exact native-tariff optimum

## Model

There are two registers. An ADD sends one register to itself plus a nonzero
dyadic rational multiple of the other. A SCALE multiplies one register by
`q = ±2^k`, with integer `k`. No scratch register, COPY, CLEAR, swap, compiler
fusion or change of frame is allowed in this block model.

The cost is exactly the one-real-component bound in the pinned inherited
`bw_emit.py::primitive_bound`. For a reduced ADD coefficient `a/b`, with
nonzero integer `a` and positive power-of-two `b`, it is

```text
A(a/b) = 3 + floor(log2 |a|) + popcount(|a|) + log2 b.
S(±2^k) = |k| + [the sign is negative].
```

Every nonzero ADD costs at least 4. Every nonidentity SCALE costs at least 1.
An identity SCALE costs zero and may be deleted. A zero-coefficient ADD may
also be deleted; it cannot help a minimum. Costs are additive in this model.
They are compiler upper-bound units, not a lower bound on arbitrary physical
implementations of the same map.

## Construction

The four gates are

```text
y -= x
x += y
x = -x
y = -y
```

After the first two gates the registers are `(y, y-x)`. After the negations
they are `(-y, x-y)`. Thus the matrix on arbitrary dirty inputs is

```text
M = [[0,-1], [1,-1]],     det(M) = 1.
```

Its cost is `4 + 4 + 1 + 1 = 10`. Reversing the gates and inverting each
coefficient gives the inverse matrix `[[ -1,1 ],[ -1,0 ]]`, also with cost 10.
Both ADDs are invertible elementary row operations; neither negation creates
or erases state.

## Lower bound for every finite word

A word with no ADDs is diagonal. A word with one ADD, surrounded by arbitrary
SCALEs, is triangular. Neither can have two nonzero off-diagonal entries.
Every word realizing M or its inverse therefore contains at least two ADDs.

Three or more ADDs cost at least 12. It remains to consider exactly two.
If all SCALEs are identities, delete them. Two ADDs in the same direction
have both diagonal entries equal to one. Two ADDs in opposite directions
have at least one diagonal entry equal to one. Neither target has a unit
diagonal entry, so a nonidentity SCALE is necessary.

ADD determinants are one. The product of SCALE coefficients must therefore
be one. A total SCALE cost of one would consist, after deleting identities,
of exactly one SCALE with coefficient `-1`, `2` or `1/2`. None has determinant
one. Thus the SCALE cost is at least two. The total cost is at least
`2*4 + 2 = 10`, attained by the construction above. This proves the exact
minimum for both target matrices at every finite word length.

`lower_bound` checks the decisive hypotheses. Tests show that a unit diagonal
permits an eight-unit two-ADD word, determinant minus one permits a nine-unit
word, and dropping both off-diagonal requirements permits a two-unit diagonal
word. These are controls on the proof's scope, not exceptions to its claim.

As a separate finite check, `bounded_exclusions` enumerates all two-ADD cores
costing less than ten after removing identity SCALEs. The four cost-4 ADDs
and eight cost-5 ADDs yield 80 unscaled words below ten. Six possible
cost-1 SCALEs, on either register, inserted at each of three positions between
cost-4 ADDs yield another 288 words. None of the 368 maps equals either target.
Words with at most one ADD and words with at least three are excluded by the
preceding analytic argument. The enumeration corroborates, rather than
replaces, that argument.

## Source application and complete tariff delta

PR3042's original block has four unit-coefficient ADDs and costs 16.
PR3056's shortest three-ADD block has coefficients `1,-1,2` and costs 13.
All three maps are exactly M. The literal native transport/emitter is run on
all three complete words, for both source providers and both orientations.

The same frame is used by every gate and no frame transition changes.
On the actual common invertible-frame contract, conjugating a register-vector
map by that common frame preserves the 2x2 matrix equality. Other registers
are unchanged. This package does not assert the optional `Q[P]/(P²-P)`
extension from PR3056. If ADDs were projected by `P=0` but SCALEs remained
ordinary negations, the new word would negate both registers instead of being
identity. That different projected contract requires its own proof.

The cleanup generator reverses the changed forward body, inverts each scalar
operation and injectively substitutes the existing private buffers. The
changed inverse block acts on register 22 and private buffer 934. The full
restore equality holds on all 704 original dirty columns, and fresh native
transport/emission checks all 632 retained columns in each orientation.

In both restore and inverse cleanup the one-component cost falls by six
against PR3042, or three against PR3056. The emitter charges both real
components of every Gaussian scalar macro. Thus the complete per-word,
per-orientation reductions are

```text
versus PR3042: 2 components * 2 blocks * 6 = 24
versus PR3056: 2 components * 2 blocks * 3 = 12.
```

Every other emitted scalar, climb, centre event, wrapper, warp, allocation and
free operation is unchanged. The independent emitted-rank recount confirms
zero recursive-profile delta. Hence the source-bound recursive moment and
conditional κ do not improve. Physical instruction expansion, precision,
movement, supplier admission and outer transfer remain separate obligations.
