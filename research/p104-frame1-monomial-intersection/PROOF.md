# Frame 1 hosted, and its overlap with the recorded forty

No new κ. The selected record stays `781451/250000000`. This note hosts frame 1
of the odd-character P104 window by a product of root-line letters, charges
every monomial of degree at least 2, and intersects that set with the 40
monomials recorded for frame 0. It does not host frames 2 through 12 and it
does not compare a histogram with the selected profile.

## 1. Hypotheses

Ports and the odd graph are those of PR #6933. Two distinct ports are adjacent
when the parity of their bitwise-and popcount is 1. Frame 1 of the #7014
witness, vendored at `data/frames.json`, is the ordered 8-tuple

```text
13, 26, 131, 148, 262, 273, 392, 415.
```

A **letter** is a root-line functional `λ_i(j) = (<r_i, r_j> + 1) mod 2` on the
120 root lines. A **word** is a product of letters. The product is evaluated in
`F_2`, so the value is 1 only when every factor is 1. The word **hosts** the
frame-indicator row when, on all 120 lines, the product equals 1 on these eight
lines and equals 0 on the other 112. Restriction to the 104 P104 lines is then
the indicator of this frame.

Labels use the inherited simple-root chart. If `B` is the doubled simple-root
basis, the label of a root `r` is its coordinate vector in `B`, reduced mod 2,
with a ninth coordinate 1. The symmetric form `S9` is the Cartan matrix of `B`
on the first eight coordinates and 1 on the ninth diagonal entry. The chart is
used because `S9(u_i, u_j) = (<r_i, r_j> + 1) mod 2` holds for every pair of
the 120 lines. That identity is checked exhaustively on all 14,400 pairs. It is
the same chart as in PR #7031.

Square-free monomials are written in `x0, ..., x7`. The relation `x_i^2 = x_i`
is used throughout, so every function `F_2^8 → F_2` has one algebraic normal
form. Every affine function is idempotent in this ring: cross terms have
coefficient 2.

The recorded forty are the degree-at-least-2 monomials of the frame-0
polynomial proved in PR #7031,

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7).
```

The variables in the four factors are disjoint, so the square-free expansion
has `2 · 4 · 2 · 3 = 48` monomials and no cancellation. Eight have degree at
most 1. The other 40 are the recorded charge. This note does not rerun the
frame-0 census. It locks the expansion by the ANF hash recorded with that
proof, `26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a`,
computed on the comma-joined sorted integer exponents.

## 2. The word

**Theorem.** Under the hypotheses above, frame 1 is hosted by a product of
root-line letters. The admissible letters are exactly the eight frame letters.
The hosting products are exactly the 149 subsets of those letters whose linear
parts span a fixed 4-dimensional space: none of length less than 4, then 56,
56, 28, 8, and 1 products of lengths 4 through 8. Every one of those 149
products equals the same function

```text
(1 + x1 + x3)(1 + x0 + x1 + x4)(1 + x1 + x2 + x5 + x6)(1 + x0 + x1 + x5 + x7).
```

The square-free support has 120 monomials. The degree counts are 1, 8, 27, 47,
and 37 in degrees 0 through 4. The 111 monomials of degree at least 2 are the
new charges for this row. Exactly 31 of them lie in the recorded 40. The other
80 are the additional charge once those 40 are already paid. Nine of the
recorded 40 do not occur in this polynomial. The joint degree-at-least-2
support of the two words has 120 monomials.

One hosting word, the lexicographically first length-4 subset in the frame
order, is the product of the letters of ports `13, 26, 131, 262`.

The pairing matrix on the eight frame lines is the all-ones matrix and has
`F_2`-rank 1. That copy-cost is a different unit and is not added to the
monomial bill.

## 3. The eight letters

Write

```text
p = x1 + x3,
q = x0 + x1 + x4,
r = x1 + x2 + x5 + x6,
s = x0 + x1 + x5 + x7,
```

and `P = 1 + p`, `Q = 1 + q`, `R = 1 + r`, `S = 1 + s`. The coefficient matrix
of `(p, q, r, s)` has columns `x3, x4, x2, x7` equal to the four standard basis
vectors, so these four forms are linearly independent. Their common zero `Z` has
16 points, and `PQRS` is the indicator of `Z`.

The Cartan matrix mod 2, in the simple-root order, is

```text
0 0 1 0 0 0 0 0
0 0 0 1 0 0 0 0
1 0 0 1 0 0 0 0
0 1 1 0 1 0 0 0
0 0 0 1 0 1 0 0
0 0 0 0 1 0 1 0
0 0 0 0 0 1 0 1
0 0 0 0 0 0 1 0
```

Each frame root solves uniquely against the simple basis. The odd coordinates,
which are the eight-bit labels, and the Cartan sums of those rows are:

| Port | Odd coordinates | Sum of those Cartan rows |
|---:|---|---|
| 13 | 1, 3, 4, 5 | `x1 + x2 + x5 + x6` |
| 26 | 0, 4, 7 | `x2 + x3 + x5 + x6` |
| 131 | 0, 1, 3, 6 | `x1 + x3 + x4 + x5 + x7` |
| 148 | 5, 6, 7 | `x4 + x5 + x7` |
| 262 | 1, 2, 3, 4, 5, 6 | `x0 + x1 + x2 + x3 + x6 + x7` |
| 273 | 0, 2, 4, 6, 7 | `x0 + x2 + x6 + x7` |
| 392 | 0, 1, 2, 3 | `x0 + x1 + x4` |
| 415 | 2, 5, 7 | `x0 + x3 + x4` |

The ninth label bit is 1, so the chart letter is 1 plus that linear form. In
the basis `(p, q, r, s)` the eight linear parts are

```text
r,  p + r,  p + q + s,  q + s,  p + r + s,  r + s,  q,  p + q.
```

Each has q-coefficient different from r-coefficient, and the eight tuples are
distinct. The set of vectors in `F_2^4` with that coefficient condition has
size 8, so these are all of them. Call that affine hyperplane `H`, and call
`W = {q-coefficient = r-coefficient}` the complementary linear hyperplane.

The coordinate solves are eight invertible rational systems. `verify.py`
recomputes them and rejects a non-integral coordinate. The row sums above are
the letters once those bits are known.

## 4. Which products host the row

**Factor restriction.** A product equals 1 at a line only if every factor does.
Every root in this model has sum of squares 8, so the normalized dot of a root
with itself is 2 and every letter equals 1 on its own line. The 28 pairs of
distinct frame roots are orthogonal, which is checked pair by pair, so each
frame letter equals 1 on all eight frame lines. Thus every frame letter is
admissible.

A letter outside the frame fails the same test. The eight frame labels span a
4-dimensional space `U`. Enumerating the orthogonal of `U` inside `F_2^8`
returns 16 vectors. Exactly eight of those vectors are eight-bit root-line
labels, and they are the frame labels. A root
label is annihilated by every form in `V = span{p, q, r, s}` exactly when it is
orthogonal to `U`, because the eight linear parts span `V` and each chart letter
is `1 + B(label, ·)`. The orthogonal census and the direct test of all 120
letters agree: the admissible letters are the frame letters. Repetition does
not create a new `F_2` value, since every letter is idempotent. The nonempty
subsets of the eight letters therefore exhaust the hosting candidates.

**Spanning criterion.** For a subset of these letters, the product equals 1
exactly where every selected linear part vanishes. That common zero is `Z` if
and only if the selected vectors span `V`. The product is then the indicator of
`Z`, which is `PQRS`. If the vectors do not span `V`, the common zero has size
at least 32, so the product is a different function.

**Length count.** This is a count of spanning subsets of `H` inside `F_2^4`.

- No subset of size at most 3 spans a 4-dimensional space.
- `F_2^4` has 15 linear hyperplanes, one for each nonzero linear equation. One
  of them is `W`, which misses `H`. Each of the other 14 meets `W` in a
  2-dimensional subspace and therefore meets `H` in `8 - 4 = 4` points. Those
  four points are a coset of that 2-dimensional subspace, so they span a
  3-dimensional space and do not span `F_2^4`.
- The 14 four-point sets are distinct. If two distinct hyperplanes met `H` in
  the same four points `S`, then `S` would equal their intersection, a linear
  subspace. That subspace contains 0, and `H` does not.
- There are `C(8, 4) = 70` four-subsets, so 56 of them span `F_2^4`.
- A subset that does not span lies in some linear hyperplane. Inside `H` that
  hyperplane contributes only four points. Every subset of size at least 5
  therefore spans. The counts are `C(8, 5) = 56`, `C(8, 6) = 28`,
  `C(8, 7) = 8`, and `C(8, 8) = 1`.

So the hosting products are 56 of length 4 and every subset of length at least
5. There are 149 of them, and each equals `PQRS` as a function on `F_2^8`.

The lexicographically first length-4 mask, with bit `i` selecting the `i`-th
frame port, is `0b10111`, the ports `13, 26, 131, 262`. Their letters are
`R`, `1 + P + R`, `P + Q + S`, and `P + R + S`. The first two multiply to `PR`:

```text
R(1 + P + R) = R(1 + P) + R^2 = R + PR + R = PR.
```

The last two multiply to `P + PR + PQ + QR + QS + SR + S`. Multiplying on the
left by `PR` cancels every term except `PQRS`. This is the same polynomial.
The spanning argument already covers the other 148 hosting products.

`verify.py` evaluates all 255 nonempty pairing products on the 120 lines and
checks that the successful masks are exactly the spanning subsets, and that
each of those expansions equals `PQRS`. That loop is a complete pass over a
domain of size 255. It corroborates the identification of the letters. It is
not a sample.

## 5. The flat meets the root lines in the frame

`PQRS` equals 1 on a chart point exactly on `Z`. Evaluating it on the 120
root-line labels returns exactly the eight frame labels. The domain of that
check is the full set of 120 lines. On root lines the function is therefore the
frame indicator. The eight ports lie in the P104 window, so the same statement
holds after restriction to the 104 lines.

The support of the function on the whole chart is the 16-point flat `Z`, not
the indicator of eight points inside `F_2^8`.

## 6. The bill

Boolean multiplication of the four factors, reduced by `x_i^2 = x_i`, produces
120 monomials. The Möbius transform of the indicator of `Z` produces the same
set. The degree counts are

```text
degree 0: 1,  degree 1: 8,  degree 2: 27,  degree 3: 47,  degree 4: 37.
```

The degree-1 monomials are `x0, x1, x2, x3, x4, x5, x6, x7`. The other 111
monomials are the new charges. Their ANF hash, on the comma-joined sorted
exponents, is `df38586c54c752c2881df43e80653a9abffbaf5e49b9d76282919d3cf3c79765`.
The full 120-monomial hash is
`b2af6c2893e8104e3c9f54ce4db48f30f692c99f11ca877d81252ae5c36c0acd`.

`Q`, `R`, and `S` do not use `x3`, while `P = (1 + x1) + x3`. The monomials
that contain `x3` are therefore `x3` times the monomials of `QRS`, disjoint
from the rest. Fifty-one of the 111 new monomials contain `x3`. The recorded
polynomial does not use `x3`, so all 51 lie outside the recorded 40 and inside
the additional charge.

Of the 111 new monomials, the intersection with the recorded 40 has size 31,
degrees 16, 13, and 2 in degrees 2, 3, and 4. Hash
`2f7b63759f9780a1ae332df1ebbb987027c880cad97896fb39ebcb92194cc65b`.

```text
x0*x1 x0*x2 x0*x4 x0*x5 x1*x5 x0*x1*x5 x2*x5 x0*x2*x5 x4*x5 x0*x4*x5
x0*x6 x1*x6 x0*x1*x6 x4*x6 x0*x4*x6 x5*x6 x0*x5*x6 x1*x5*x6 x0*x1*x5*x6 x4*x5*x6
x0*x7 x1*x7 x0*x1*x7 x2*x7 x0*x2*x7 x4*x7 x5*x7 x0*x5*x7 x1*x5*x7 x0*x1*x5*x7 x4*x5*x7
```

The additional bill is the other 80, degrees 11, 34, and 35. Hash
`219f34e8bd473ae9927d0b6cb7d94c4b6de2b4c93f6b9c4c3b8355fdad4b13cb`.
Twenty-nine of them are free of `x3`; the other 51 contain `x3`.

```text
x1*x2 x0*x1*x2 x0*x3 x1*x3 x0*x1*x3 x2*x3 x0*x2*x3 x1*x2*x3
x1*x4 x0*x1*x4 x2*x4 x0*x2*x4 x1*x2*x4 x0*x1*x2*x4 x3*x4 x0*x3*x4
x1*x3*x4 x0*x1*x3*x4 x2*x3*x4 x0*x2*x3*x4 x1*x2*x3*x4 x1*x2*x5 x0*x1*x2*x5
x3*x5 x0*x3*x5 x1*x3*x5 x0*x1*x3*x5 x2*x3*x5 x0*x2*x3*x5 x1*x2*x3*x5
x1*x4*x5 x0*x1*x4*x5 x2*x4*x5 x1*x2*x4*x5 x3*x4*x5 x0*x3*x4*x5 x2*x3*x4*x5
x3*x6 x0*x3*x6 x1*x3*x6 x1*x4*x6 x0*x1*x4*x6 x3*x4*x6 x0*x3*x4*x6 x1*x3*x4*x6
x3*x5*x6 x0*x3*x5*x6 x1*x3*x5*x6 x1*x4*x5*x6 x3*x4*x5*x6
x1*x2*x7 x0*x1*x2*x7 x3*x7 x0*x3*x7 x1*x3*x7 x0*x1*x3*x7 x2*x3*x7 x0*x2*x3*x7 x1*x2*x3*x7
x1*x4*x7 x2*x4*x7 x1*x2*x4*x7 x3*x4*x7 x1*x3*x4*x7 x2*x3*x4*x7
x3*x5*x7 x0*x3*x5*x7 x1*x3*x5*x7 x1*x4*x5*x7 x3*x4*x5*x7
x6*x7 x0*x6*x7 x1*x6*x7 x0*x1*x6*x7 x3*x6*x7 x0*x3*x6*x7 x1*x3*x6*x7 x4*x6*x7 x1*x4*x6*x7 x3*x4*x6*x7
```

Nine recorded monomials are absent from frame 1, degrees 1, 4, and 4. Hash
`5ca7559ebd00485c0852a0f65479f721997ae1c8aaac9bbc2e4083a29da2c7bf`.

```text
x2*x6 x0*x2*x6 x2*x5*x6 x0*x2*x5*x6 x0*x4*x5*x6 x0*x4*x7 x2*x5*x7 x0*x2*x5*x7 x0*x4*x5*x7
```

The joint degree-at-least-2 support is the union of the 111 and these nine, so
it has size `111 + 9 = 120`. That count equals the number of monomials of the
frame-1 polynomial, and the two sets are different: the polynomial also
contains the constant and the eight degree-1 monomials, and it omits these
nine. The arithmetic identity `31 + 80 = 111` and `40 + 80 = 120` is the whole
comparison of the two charges.

## 7. Evidence class

The hosting classification, the length count, the equality of every spanning
product with `PQRS`, and the four-letter multiplication for ports
`13, 26, 131, 262` are proofs under the hypotheses in §1. The independence of
`p, q, r, s` and the idempotence used in the multiplication are part of those
proofs.

The following are exhaustive finite censuses. Each domain is finite, every
element is tested, and the domain is the one named here.

- The chart identity, on all 14,400 pairs of root lines.
- Pairwise orthogonality and the odd-graph condition, on all 28 pairs of frame
  ports.
- The eight coordinate solves and the Cartan row sums.
- The admissible-letter test on all 120 lines, together with the 16-vector
  orthogonal of the frame-label span.
- The agreement of all 255 subset products with the spanning prediction.
- The boolean expansion of `PQRS`, cross-checked by the Möbius transform of the
  indicator of `Z` on all 256 chart points, and the evaluation of that function
  on all 120 root-line labels.
- The comparison of the resulting degree-at-least-2 set with the 40 monomials
  of the recorded closed form.

These checks are not a heuristic and not an incomplete search inside this
alphabet. A failed search is not what is claimed. The length count is not being
inferred from a sample of words.

## 8. What the bill does not decide

The factor restriction uses products of root-line letters. A sum of such
products, a coordinate change, or a circuit that is not a product can be a
different hosting. This note gives no lower bound for those larger alphabets.
The 80 additional monomials are the exact remainder inside the product alphabet
and this chart, after the recorded 40 are paid. They are not a count of
Clifford routes, Gaussian children, or selected-invoice primitives.

The selected frontier stays `781451/250000000`. Sharing 31 monomials makes the
algebraic union of these two rows smaller than the sum of the separate new
charges. That union is not a signed histogram, and frames 2 through 12 are not
expanded. The rank-1 pairing matrix is not part of the monomial bill.

Frame partition: unpaidmoon, PR #7014. The recorded forty and the frame-0
closed form: PR #7031. Ports and the odd-graph window: PR #6933. Prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
