# The 40 frame-0 monomials are not primitives of the selected invoice

No new κ. The selected record stays `781451/250000000`. This note answers the
naming step left open by PR #7031: whether the 40 charged monomials can be
named as primitives on the selected #6030 invoice. They cannot, under the
naming rules that invoice actually uses. The missing obligation is one total
map that those rules accept. This is not a comparison with the selected
profile, and it is not a claim that no future contract could name the
monomials.

## 1. The 40 monomials

PR #7031 charges the degree-at-least-2 terms of

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7)
```

in the square-free ring `F_2[x0,...,x7]/(x_i^2 = x_i)`. The four factors use
disjoint variables, so the expansion is the Cartesian product of the summands.
That domain has `2 · 4 · 2 · 3 = 48` elements, every product is distinct, and
there is no cancellation. The degrees are 1, 7, 17, 17, and 6 in degrees 0
through 4. The eight monomials of degree at most 1 are `1, x0, x1, x2, x4,
x5, x6, x7`. The other 40 are the charged monomials.

The SHA256 of the 48 sorted exponent integers, joined by commas, is

```text
26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a
```

which is the normal-form hash recorded by the #7031 verifier at head
`531ecca652dde63c6010cd6097cb55a994367ce7`. This note does not replay that
pull request's hosting census. It takes this polynomial as the charged object.

An exponent is the integer whose bit `i` is the factor `x_i`. The six
degree-4 exponents are `99, 101, 113, 163, 165, 177`, namely

```text
x0*x1*x5*x6, x0*x2*x5*x6, x0*x4*x5*x6,
x0*x1*x5*x7, x0*x2*x5*x7, x0*x4*x5*x7.
```

## 2. What the selected invoice calls a primitive

The selected record points at
`research/p104-helper470-twin-rung-removal/RESULT.json`. Its word has schema
`p104-accumulated-block-composition/2`. A recursive primitive on that invoice
is a pair `(side, rank)` produced by one of the following constructors, as
written in `local.py` `replay` and `pricing.py` `assemble`.

- A `MOVE` from frame `a` to frame `b` has local paid rank `|dim b - dim a|`,
  where the dimension is the length of the stored basis.
- A non-main public helper has local target rank `dim(final) - dim(initial)`.
- Eighteen forward `LOCAL` calls repeat both local histograms.
- Fifteen query shears add paid rank `1`, with count `104` each.
- For each idle length `L` in `{7, 8}` and each `j = 1, ..., L`, the assembly
  adds paid rank `8(j+1)` and target rank `1 + 8(j+1)`, with count `208`.
- One further target of rank `145` is added with count `208`.

Replaying every `MOVE` and every non-main helper of the selected word, then
applying this finite formula, reproduces `RESULT.json` `local.paid`,
`local.helpers`, `complete_cost.paid`, and `complete_cost.targets`. The paid
keys are

```text
1, 2, 3, 4, 5, 6, 7, 8, 16, 24, 32, 40, 48, 56, 64, 72.
```

The target keys are

```text
1, 2, 3, 4, 5, 6, 7, 8, 9, 17, 25, 33, 41, 49, 57, 65, 73, 145.
```

The ordinary names on the same word are the opcodes that occur: `ADD`,
`CLEAR`, `COPY`, `INIT`, `MOVE`, and `SCALE`. Each acts on a role index and,
for a scalar event, a dyadic coefficient. The assembly text and the replay
text do not mention a chart variable, a polynomial degree, or a monomial.

The native routine in `local.py` builds Clifford recipes from frame charts
and ports. It is not replayed here. Its inputs are those frames and ports,
not the 40 exponents, so it does not assign these monomials names either.

## 3. Readings that still do not name all 40

A naming, in the sense asked by #7031, would be a total function from the 40
exponents to this alphabet that the constructors above determine. The
readings that use only an integer or a string already attached to the
monomial fail.

**Exponent integer as a histogram key.** Of the 40 exponents, exactly three
are paid keys: `3, 5, 48`. Exactly seven are target keys: `3, 5, 17, 33, 49,
65, 145`. The union has eight exponents, so 32 exponents are keys of neither
side. The two exponents `3` and `5` are keys of both sides, so the integer
does not choose a unique primitive even in the collisions. All six degree-4
exponents lie in the 32. This is an exhaustive check of a 40-element set
against the two finite key sets.

**Printed name as an opcode.** None of the 40 strings `x0*x1`, ... equals
`ADD`, `CLEAR`, `COPY`, `INIT`, `MOVE`, or `SCALE`.

**Exponent integer as a selected port.** The word stores 104 ports, and the
local native check identifies the initial frame of each live line with the
singleton `[port]`. Exactly 14 of the 40 exponents occur in that port list:
`35, 37, 49, 69, 81, 98, 100, 112, 131, 133, 145, 161, 164, 176`. The other
26 do not. This reading does not name all 40.

**Degree as rank.** The degrees that occur are 2, 3, and 4, and each of those
integers is both a paid key and a target key. That numerical fact is not a
name. Neither constructor reads a degree. Calling these monomials `H_2`,
`H_3`, and `H_4` would be a new tariff. This note does not adopt that tariff
and does not claim that every future contract must reject it.

## 4. The chart is not the invoice coordinate system

The same integer can appear in both lists without being the same object.
The hosting word of #7031 uses ports `11, 21, 38, 140`. Their simple-root
labels, with the ninth coordinate set, are `282, 284, 270, 454`. None equals
its port, and none is one of the 40 exponents (every charged exponent is at
most `177`). The invoice frames are vectors in the port-space `F_2^9`. The
monomials are functions of the simple-root coordinates. An exponent that
happens to equal a port, or a frame basis vector, is not that port and not
that vector.

For the record, 34 of the 40 exponent integers occur somewhere in the stored
frame bases, and the six that do not are exactly the degree-4 exponents.
That census is not a naming: a basis vector is not a primitive of the
invoice, and the two coordinate systems are distinct.

## 5. The obstruction

Under the constructors in section 2, the selected invoice does not determine
a total function from these 40 exponents to its primitive alphabet. The
missing obligation is that function, together with a proof that an inherited
constructor, or a stated extension of one, sends each exponent to the image
it names. Until the function exists, these 40 monomials are not primitives
on the selected invoice.

No profile comparison is made. The other twelve frames are not expanded.
The selected κ is unchanged. This is not a proof that the monomials cannot
be named by a different contract, and it is not a proof that no function
into the alphabet exists. Many functions exist. None is fixed by the
invoice that was asked about.

## Evidence class

The expansion is an exhaustive census of a 48-element product, complete
because the factors are disjoint and every combination is enumerated. The
histogram identity is an exhaustive replay of the finite selected word plus
the finite assembly formula, matched to the selected receipt. The three
failed readings are exhaustive checks of the same 40 exponents against
finite sets. The refusal of the degree reading is the observation that the
constructor texts do not read a degree. Together this is a scoped proof and
an exhaustive finite census. It is not a heuristic and not an incomplete
search inside those readings.
