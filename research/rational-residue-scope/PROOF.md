# Representation and restoration boundaries

## 1. The exact algebraic interface

Let `S` be the rational numbers whose reduced denominator is odd, and let
`M=2^w`, `w>=1`. Define

```text
phi(a/b) = a * b^(-1) mod M,  gcd(b,2)=1.
```

Every such b is a unit modulo M. If `a/b=c/d`, then `ad=bc`; multiplying that
identity by the two unit inverses proves that phi is independent of the
representation. Common denominators directly prove preservation of addition,
subtraction and multiplication. Thus phi is a ring homomorphism from S to
`Z/MZ`. This is the standard localization property, also stated in the
[Stacks Project, Proposition 10.9.3](https://stacks.math.columbia.edu/tag/00CP).
No new algebraic result is claimed for it.

An L-by-L matrix over S induces an additive map on `(Z/MZ)^L` by entrywise phi.
Its matrix need not be invertible: a leaf is the shear
`target += sign * A source`, whose inverse negates the sign. The credited
PR1057 borrowing induction therefore applies unchanged to every ordered
binary/ternary tree and arbitrary dirty residue arrays. No commutation of
matrix factors is required. The resulting map is the reduction of the exact
rational product; all other data rows restore, including borrowed ancestor
ports. Equality of residues gives equality of their stored w-bit patterns.

This general additive-group scope already belongs to PR1057. PR1159 implements
the integer-factor special case. Here only coefficient preparation and the
source-bound interpretation are extended; its actual dense backend is unchanged.

## 2. Integer recovery and its limits

Suppose the external source x and initial output y are integer vectors with
norm bounds X,Y. Let `P=A_(n-1)...A_0`, and require that `P x` is integral on
the admitted source domain. A sufficient stronger admission is that every
entry of P is an integer; that is what this package's generic checker tests.
Let `K_i=||A_i||_infinity` and `R=Y+X product(K_i)`. If

```text
2^(w-1) > max(X,R),
```

then both source and completed output have unique signed representatives.
The residue endpoint decodes to exactly `y + sign*P x`. Dirty helpers require
no small norm or coarse-lattice promise; they start as arbitrary w-bit patterns
and return unchanged. Internal boundaries are residues, with no signed decoding.
The actual supplied x,y must meet the declared X,Y bounds; the code checks them.

Three missing hypotheses have different failure modes.

- A reduced even denominator cannot be inverted modulo `2^w`: for instance
  `2z=1` has no solution. There is no unital ring map sending 1/2 into this ring.
  Restricted source lattices or a different modulus need another contract and
  implementation. A raw denominator may cancel: `2/6=1/3` is a valid unit case.
- Small absolute rational magnitude does not imply integer recoverability.
  `1/3 mod16=11`, which signed-decodes to `-5`. Integrality or another proved
  reconstruction interface is indispensable.
- Omitting the signed guard can wrap an integral endpoint. Its X term is also
  necessary for unchanged-input representation when a zero factor makes the
  output small. Equality at the stated strict cap is rejected.

The tested family has `A_i = 3^(e_i) U_i`, where the U_i are PR1159's integer
matrices and `e_i=-1,+1` alternately for 52 factors. Since their sum is zero,
P is exactly the original integer product. All norms are `2*3^(e_i)`, so
their product is `2^52`. The same endpoint radius as PR1159 admits w=56.

## 3. What the numerator comparison establishes

PR1135 Section 7 uses a common denominator `q^D`, where D is the largest formal
factor degree at any prefix of the literal word. Its source routine gives
D=65 here, larger than the root's 52 factors. That construction is sufficient;
it does not claim `q^D` is the minimum for concrete cancelling coefficients.
Its endpoint lower bound for repeated coprime scalar p/q factors explicitly
excludes denominator-cancelling kernels.

An independent Fraction matrix interpreter computes every actual prefix on
all ten integer input columns. The lcm of all entry denominators is nine in
each direction. It is sufficient for common integer numerators at every
prefix. It is necessary because the reduced coefficient `-2584/9` occurs.
In particular denominator three fails on that literal basis input. This is
a finite statement about this program and these matrices, not a family-wide
bound or an arbitrary representation lower bound.

For each prefix row with coefficients c_j and initial magnitude bounds B_j,
the triangle inequality gives `|row| <= sum_j |c_j| B_j`. Use B_j=7 for source
and output coordinates and `2^55` for dirty coordinates. Initial rows are also
included. The largest forward bound is
`865889932777058898029788786`; multiplying by nine yields
`7793009394993530082268099074`, which fits 94 signed bits under the conservative
`1+bit_length` rule. The reverse bound also fits 94. Multiplying the same
bounds by `3^65` gives 194 sufficient bits. Neither result is a width minimum.

These count numerator data only. A numerator implementation additionally pays
for embedding the original data, products, sums, exact divisions, private
work and any precision extensions. Exact division can be performed after a
complete matrix dot product when needed; per-term divisibility is not assumed.
The residue implementation avoids scaling the data by either denominator,
but pays coefficient preparation and the modular kernel's reductions. No
total runtime or total-storage dominance is inferred from the data widths.

## 4. Literal coefficient preparation and cost

For the priced preparer, original signed numerator descriptors fit w+2 bits
and reduced positive denominators lie below `2^w`. Descriptors outside this
range are rejected by that implementation. The algebraic statement permits
larger heights, but would require separately paid reading/reduction and
workspace. Input normalization and validation are also separate costs.

For each distinct denominator q, start u=1. The update
`u <- u(2-qu) mod2^w` squares the error `1-qu`. Hence its correct low-bit count
doubles from one and `ceil(log2 w)` iterations suffice. Each iteration performs
two products, three reductions, a subtraction and a move. Four startup clears,
the denominator read, oddness check, setting one, a final multiply/reduce/check,
the inverse write and four closing clears are explicit. With t iterations,
one denominator costs `15+7t` commands. An independent bit-at-a-time inverse
checks the resulting coefficients.

For every coefficient a/b, the program reads a and b, reduces a, reads the
prepared inverse, multiplies, reduces, writes the coefficient, and clears all
four work registers. It uses 11 commands per coefficient plus four startup
clears. Thus r distinct denominators and E coefficients cost

```text
P_setup = r*(15+7 ceil(log2 w)) + 4 + 11E.
```

Here r=2, E=208 and w=56, giving 2,406 commands. The private capacities are
`a:w+1 unsigned`, `c:w unsigned`, `v:w+2 signed`, `p:2w unsigned`, as in PR1159.
Products of two residues fit p, reduced accumulators fit a, and `2-p_reduced`
fits v. They are cleared on exit. The inverse and coefficient tables are owned
prepared storage, not promised-restored arbitrary dirty inputs.

The external layout is: five data arrays, residue coefficients, inverse table,
then fixed-width original numerator/denominator descriptors. Each source read
and table write has an explicit bit position and field width. The head returns
to zero after each inverse and coefficient. Independent itinerary summation
checks all 836 accesses and the bit-action/head-motion bill. Private arithmetic
movement is part of each primitive's cost, not included again in that external
itinerary. Variable-width packed payload bits are reported only diagnostically;
the charged descriptor storage uses fixed three-bit numerator and two-bit
denominator fields for this instance.

The actual full conditional cost is

```text
C_admission_and_normalization
+ C_original_input_and_output_conversion
+ sum over every counted setup and kernel primitive of its width-aware cost
+ C_external_source_and_table_routing
+ C_program_and_preparation_control
+ C_physical_adapter.
```

None of these terms is set to zero. The emitted kernel has 52,292 primitive
commands; setup plus kernel has 54,698. Their explicit field-access costs are
separate from arithmetic costs and control annotations. If generic product
integrality is checked online, the 416 exact rational products, 416 additions,
height/normalization work, norm checks and temporary product matrices are
additional preprocessing. The four-private-register bound applies to setup
and the kernel, not to arbitrary rational certificate verification. The fixed
scaling family has its own symbolic integrality proof, without claiming free
certification for arbitrary input factors.

## 5. Rounded interfaces remain different

PR1135's no-wrap, nearest-rounded map is not phi. A binary echo with ideal
factors `1/3` then `3` has integral ideal product one. Replacing the first leaf
by nearest rounding gives target increment `3*nearest(x/3)`, which is zero
at x=1 rather than one. An integral ideal endpoint therefore does not justify
silently substituting rounded implementations.

At the actual nested PR1057 boundary `(0,((1,2),3))`, let factor 2 be
`nearest(4z/3)` and all other factors be identity. The pinned PR1135 rounding
and literal word send `[-2,-2,0,-2,-2]` to `[-2,-5,0,-1,-2]`: a dirty helper
changes. This is an exact algebraic boundary witness, not a replay of PR985's
complete physical leaf implementation. It corroborates, rather than repairs,
PR1135's scoped translation obstruction.

Changed moduli, nonintegral rational reconstruction, restricted source grids,
rounded or irrational leaves, and actual supplier/compiler/hosting admission
remain open interfaces. The comparison does not alter any selected bound or
establish the full multiplication theorem.
