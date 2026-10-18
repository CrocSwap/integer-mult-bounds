# Conditional local native-format theorem

## Contract and source interpretation

Work on complex fields indexed by F2^9. Let u,v0,v1,v2,v3 have independent
real and imaginary integer components in [-L,L-1], L=2^(P-1), P>=3. Put
v=(v0-v1+v2-v3)/2. The fields are local normalized inputs; no claim of their
independent realizability at every globally aliased owner is needed for the
sufficient bound. Necessity refers to this independent local input box.

The actual forward A13 ADD in each pinned reconstructed provider is
126 -= 83/2 at frame F=[45]. Its preceding source warp uses E=[382] and
G columns [1,2,4,16,392,128,162,68,401]. The target climbs from frame zero.
An exact reduced-word scalar prefix derives u=initial83 and the stated v,
with v0,v1,v2,v3=initial126,initial127,initial164,initial165.

The physical entrance assertion is source=T_E u, target=v. Connecting the
complete physical prefix to this assertion inherits the native common-frame
conjugation theorem and adapter contracts. The scalar prefix replay alone is
not a physical execution. This package checks the local transformations
after that entrance assertion, with the Gaussian operator conventions below.

## Native operators

For a basis index x, a square-root translation C(q,+1) sends a field z to

```text
((1+i) z[x] + (1-i) z[x xor q]) / 2.
```

Its inverse reverses i. P(G) permutes indices by G, and D(Q,a) multiplies by
the associated Z/4 quadratic phase. Canonical T_U uses the retained ordered
basis extension and circuit K_U^-1, C(e0),...,C(e[r-1]), K_U. The first listed
gate acts first. These are the retained PR2226 and exact Clifford conventions.

For G above, K=K_G is P(G) then D(I+G^-T G^-1). The quadratic rows are
[264,32,64,281,264,386,68,288,441] and their diagonal coefficients are
[0,0,0,1,0,0,1,0,1]. The physical warp is

```text
W = T_F K T_E^-1.
```

Independent sparse rational and packed-integer evaluations on all 512 columns
show that W has one unit Gaussian entry in each row and column. Therefore W
is a component permutation with signs and real/imaginary exchanges. Its phase
counts are 144 of +1,112 of -1,128 of +i,128 of -i. It differs from K.
Associativity and invertibility give W T_E=T_F K, with no omitted phase.
The source becomes S=T_F K u. The target climb gives V=T_F v, and linearity
of the half-ADD gives V-S/2=T_F(v-Ku/2). The source stays unchanged by that ADD.

## Sharp range and grid

For a real row with positive coefficient sum A and negative absolute
coefficient sum B, its exact minimum and maximum on the signed input box are

```text
minimum = -L A - (L-1) B
maximum = (L-1) A + L B.
```

Each expanded real row of S has four coefficients ±1/2. Their positive and
negative sums are (3/2,1/2) or its reverse. Both types occur. Thus the global
range is ±(2L-1/2). Every expanded real row of V has sixteen coefficients
±1/4, eight of each sign. Its exact range is ±(4L-2). The v-fields and u-field
are disjoint. Each final row therefore has coefficient sums (9/4,11/4) or
the reverse, yielding the exact global range ±(5L-9/4).

All local endpoints have quarter-integer components. The target with only
v0's real coordinate zero set to 1 has V_real[0]=1/4, so two fractional bits
are necessary. The final output also retains that value when u=0.
Because S has half-integer components, its quarter-grid encoding 4S is even.
This proves the divisibility required by the encoded half-ADD.

On that grid the final range is ±(20L-9). Width P+5 has signed magnitude
limit 32L, so it suffices. Width P+4 has positive maximum 16L-1.
For P>=3, L>=4 and 20L-9>16L-1, so the smaller width fails.
The assignments in RESULT.json attain both final extrema. At P=3, the maximum
is 71/4 and its encoding 71 exceeds the seven-bit maximum 63.

The scalar-only local endpoint has norm 5/2, grid one and width P+3. Adding
the native conversion costs one fractional and one magnitude bit in this
local comparison. This does not refute the complete scalar-stream 77-bit
theorem, which explicitly omits native conversions; nor does it establish
a global native bound by adding two to that theorem's width.

The argument also applies to atoms on a common input grid 2^-d, after scaling
all values by 2^-d. The output then uses d+2 fractional bits in P+5 signed
bits, when P measures the signed integer encoding of each original atom.

## Internal arithmetic and local bit caller

The retained circuit expansion of W has two C gates. Before its first C,
components are signed permutations of T_E u and have absolute value at most
2L-1/2. Before its second C they are signed permutations of u and have
absolute value at most L. Before the target's C they are signed permutations
of v and have absolute value at most 2L-1. A C numerator is a signed sum of
four real components. Every partial sum therefore has absolute value at most
8L-2 on the source path and 8L-4 on the target path. On the quarter grid,
these are strictly below 32L. Thus P+5 bits also suffice for those partial sums.
The receipt separately checks every gate endpoint and whole C numerator.

This is capacity for evaluating the specified arithmetic, not a reversible
native bit circuit, its temporary-field ownership or a charge for its movement.
The monomial W can itself be represented by a signed permutation; realizing
that permutation physically remains a separate cost.

For the one half-ADD, PR3080's explicit read-only Boolean circuit applies at
W=P+5 with 4S even. Its uniform proof is inherited, and this package executes
the literal circuit on both source-bound extremal assignments at P=64. It
returns each source and all 68 carries; W=68 rejects the exact endpoint.
The generated 69-bit circuit has 541 gates. Sequential execution over 1,024
real components gives 553,984 gates and permits one reusable 68-bit carry bank.
Its production, routing, source/target exclusivity and all non-ADD costs are
unknown here. Partial Boolean states are modular, so their signed ranges are
not interpreted as intermediate real arithmetic.

## Consumer and admission limits

The quarter-grid target bits are live output. Discarding them after A13 loses
information on the displayed basis input. An inverse half-ADD followed by the
inverse target conversion would return v exactly, but the actual supplier has
intervening consumers; this statement grants no early erasure there.

There is no claim about the actual dual entrance expression, approximate
recursive outputs, complete physical prefix, global precision, all-size
compiler, physical ownership, supplier/outer admission or multiplication
exponent. No selected record is changed. The next useful obligation is the
concrete producer/consumer composition with its complete charged invoice.
